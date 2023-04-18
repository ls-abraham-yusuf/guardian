# Helm chart values

## Env-lib integration

If a value from `env-lib` is required the "env-lib.get" template function should be used.
For example:
```yaml
someKey: '{{ include "env-lib.get" (list $ "databases.my-service.host") }}'
```

This template function call will return a value from the values file of `env-lib` user path `<environment_name>.databases.my-service.host`.
Here `<environment_name>` takes the value of `environment.name` value in the chart.


`environment.name` - should be set to `stg` by default.
The Value is set by vessel/deploy job based on the cluster the chart is deployed to (i.e. `stg`, `trial`, `prod`).
The value is set to `ephemeral` by Fleet when Fleet deploys the chart in ephemeral configuration.


## Environment variables

### Plain environment variables
`envVars.SOME_ENV_VAR_NAME` - the value of `SOME_ENV_VAR_NAME` for the application.
Some examples are:
`envVars.ENV_VAR_1`: "value" - set to a plain value
`envVars.ENV_VAR_2`: "{{ $.Values.someKey }}" - set to a value that is located in this file under key `someKey`
`envVars.ENV_VAR_3`: "{{ tpl $.Values.someKey $ }}" - set to a value returned by templating the string located in this file under key `someKey`.
`envVars.LSK_ENVIRONMENT`: '{{ include "env-lib.get" (list $ "lskEnvironment") }}' - will track the value of `lskEnvironment` defined in env-lib. Will change depending on the `environment.name`.
`envVars.SPRING_DATASOURCE_URL`: '{{ include "starter-lib.java-mysql-url" (list $ "someAlias") }}' - see `starter-lib.java-mysql-url` documentation.
`envVars.KAFKA_BROKERS`: '{{ include "starter-lib.kafka-brokers" $ }}' - a starter-lib helper over the env-lib values of kafka brokers. Return a comma separated list of kafka brokers in the current `environment.name`.
`envVars.SECURITY_OAUTH2_CLIENT_USER_AUTHORIZATION_URI`: '{{ include "starter-lib.nightswatchPublicUrl" $ }}' - constructs a public nightswatch url that is based on the `environment.name`.
`envVars.OAUTH_AUTHORIZE_URL`: '{{ include "starter-lib.nightswatch-public-url" $ }}/oauth/authorize' - you can append a static string to a value returned by a template like so.

You might see a value being set by some helper you do not know. The helper is defined in this repo. The docs will be located above the function definition.

### Secret variables
The chart is integrated with secrets vault [vault docs](https://docs.lsk.lightspeed.app/Onboarding/accounts/#vault).
By default, no secrets are fetched for your service.
Once at least one secret variable needs to be set a kubernetes Job called k8s-secret-fetcher will be created on each release.
The job will authenticate to the vault that corresponds to the current `environemnt.name` and fetch the corresponding secret.
A kubernetes Secret object will be created by the job and all the keys in the vault secret will be present in this secret.
The job is defined in `starter-lib/templates/_secret_fetcher.yaml`.

`secretVars.SHHH_VAR: {}` - sets the `SHHH_VAR` environment variable to the value defined in the secret in vault under the key `SHHH_VAR`.
Setting `secretVars.OTHER_ENVVAR.secretName` and `secretVars.OTHER_ENVVAR.secretKey` enables OTHER_ENVVAR to be set from some other kubernetes secret.
`secretName` - is the name of the target k8s secret, `secretKey` - in the key of the value in the target k8s secret.

### Generating Java database connection string

The following values are to be defined when a mysql url needs to be constructed.
The values are used by `starter-lib.java-mysql-url` template function, that constructs the mysql connection url.
These values should be set via `env-lib.get` by taking the database domain, port and schema name
from the environment config instead of setting the value directly.

`databases.someAlias.javaDriver` - the java driver to be used.
`databases.someAlias.host` - the database host.
`databases.someAlias.port` - the database port.
`databases.someAlias.schemaName` - the name of the schema.
`databases.someAlias.queryArgs` - the query args like so :`?useSSL=false`.

Example:
```yaml
databases:
  primary:
    javaDriver: "jdbc:mariadb"
    host: `{{ include "env-lib.get" (list $ "databases.my-service.host") }}`
    port: `{{ include "env-lib.get" (list $ "databases.my-service.port") }}`
    schemaName: `{{ include "env-lib.get" (list $ "databases.my-service.dbName") }}`
    queryArgs: "?someArg=yes"
```

Given the values are set as above the call `{{ include "starter-lib.java-mysql-url" (list $ "someAlias") }}` returns:
`jdbc:mariadb://some-db-domain:some-port/some-shema-name?someArg=yes`.

## Init containers

The chart is integrated with [kubernetes init containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/).
One common use case for init containers is to run kafka-init service to create kafka topics with specific configs.
The example shows us how to enable such init container.
```yaml
initContainers:
   00-kafka-init: # naming helps define the order of execution of init containers
     enabled: true # allows disabling kafka init in upper environments where topics are expected to be present
     image:
       name: kafka-init # the docker image name for the init container
       pullPolicy: Always # pull this image always, even if it is present
       tag: '{{ include "env-lib.get" (list $ "kafkaInit.tag") }}' # this tag of the kafka init to use
       registry: '{{ include "env-lib.get" (list $ "kafkaInit.registry") }}' # which artifactory registry to pull the image from
     envVars: {} # Refer to container env vars for syntax
     secretVars: {} # Refer to container secret vars for syntax
     volumeMounts: {} # allows setting up volume mounts for the init container, this way the init container can create a file, or mount a config map

```

## Ports, Services and Ingress

`containerPorts` key allows aliasing a port exposed by the container to a name. [Kubernetes documentation](https://kubernetes.io/docs/concepts/services-networking/connect-applications-service/)
Example:
```yaml
containerPorts:
  - name: http # this is the alias of the port, keep it http unless you have to change it
    containerPort: 80 # set this port to the port the application inside the container uses
```

`service` key defines the kubernetes service object to be created. [Kubernetes documentation](https://kubernetes.io/docs/concepts/services-networking/service/).
For most use cases the following example is sufficient:
```yaml
service:
  type: ClusterIP
  annotations: {}
  ports:
    - port: 80 # do not change unless you need to
      targetPort: http # the alias used in containerPorts.[].name
      name: http # do not change unless you need to
```

This creates a Service resource of type ClusterIP that will load balance traffic coming to pods.
This creates a domain that typically matches your chart name (see starter-lib/templates/_service.yaml).
This domain is resolvable only inside the kubernetes cluster.

Once a service resource is enabled it is typical to require the service to be exposed outside the cluster and to be assigned a certain domain and domain aliases.
The domains are typically different for each of the environments.

To expose a service an ingress resource needs to be created.
Example below will make nginx route traffic from https://api.ikentoo.com/my-service-path into the first port defined in `service.ports`.
The `my-service-path` will be dropped from the request that the application will receive.
The service will also be reachable at https://services.ikentoo.com/my-service-path and https://other.ikentoo.com/my-service-path.

```yaml
ingress:
  enabled: true # enable the creation on the ingress object
  stickySessions: false
  configurationSnippet: "httpsWorkaround" # keep this value here
  annotations:
    kubernetes.io/ingress.class: nginx # any extra annotations to be set on the ingress object

  serverAlias: 'services.ikentoo.com,other.ikentoo.com'
  hosts:
    - host: 'api.ikentoo.com'
      paths: ["/my-service-path/"]
  tls: []
```

`enabled` (bool) key controls the creation of the ingress resource.
`annotations.some-annotation-key` - adds an annotation to the ingress resource allowing to control features of the ingress. [List of ingress annotations](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/)
`stickySessions` (bool) key makes the ingress add a request affinity cookie. The following is the approximate annotations that will be set. [more here](https://kubernetes.github.io/ingress-nginx/examples/affinity/cookie/).
```yaml
nginx.ingress.kubernetes.io/affinity: cookie
nginx.ingress.kubernetes.io/affinity-mode: persistent
nginx.ingress.kubernetes.io/session-cookie-name: "<chart-name>"
```

`configurationSnippet` sets the snippet name to be used for ingress configuration. Make sure it is set to "httpsWorkaround" for now. Uses `nginx.ingress.kubernetes.io/configuration-snippet` annotation.
`serverAlias` - a comma separated list of aliases under which the service lives.
`hosts` -  an array of objects with `host` and `paths` keys. The host is the main location of the application in format subdomain.domain.toplevel.
The `paths` array is a list of url paths to be routed to this application. [Read more here](https://kubernetes.github.io/ingress-nginx/user-guide/basic-usage/).

Ingress `hosts` and `serverAlias` must be configured with values gotten by `starter-lib.ingress-alias` and `starter-lib.ingress-host`.
Env-lib provides a concept of a "domain group". A domain group is a host and its aliases.
A domain group definition lives under `domains` keys in env-lib like so:
```yaml
domains:
  someGroup:
    ingressHost: 'api.stg.lightspeed.app'
    aliases:
      - api-staging.stg.lightspeed.app
      - api.stg.somedomain.com
  ...
  otherGoup:
    ingressHost: ...
    aliases:
      - other.domain.com
      ...
```
Then the call to `'{{ include "starter-lib.ingress-host" ( list $  "someGroup" ) }}'` returns `"api.stg.lightspeed.app"`
and `{{ include "starter-lib.ingress-alias" ( list $  "someGroup" ) }}` returns `"api-staging.stg.lightspeed.app,api.stg.somedomain.com"`.

## Probes
The pod's probes are defined by setting the following values (see also [kubernetes docs](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)):

Replace `readinessProbe` with `livenessProbe` or `startupProbe` to define the other probes.
Defining `readinessProbe` is required.

The following values are used to define a readiness probe.
`readinessProbe.enabled` - (true/false), required, allows enabling and disable the probe.
`readinessProbe.path` - a path to the healthcheck. Example "/management/health".
`readinessProbe.port` - the port alias from containerPorts.

The following values are optional.
Read more about the following values in the kubernetes documentation.
`readinessProbe.initialDelaySeconds`
`readinessProbe.periodSeconds`
`readinessProbe.failureThreshold`
`readinessProbe.successThreshold`
`readinessProbe.timeoutSeconds`

## Setting up Volumes
To set up volumes, these values can be used:
```yaml
volumes:
  00-working-volume:
    name: working-volume
    emptyDir: {}
volumeMounts:
  00-working-volume-mount:
    name: working-volume
    mountPath: /working-volume
```
The volumes defined here can also be used in the initContainer's volumeMounts.

## Remote Debug and JMX
The chart is aware of [docker-java](https://github.com/lightspeed-hospitality/docker-java).
Here is how one would enable remote debugging or jmxMonitoring.
kubectl access is required to forward the port to the local machine.
```yaml
java:
  jvmDebug:
    containerPort: 5005

  jmxMonitoring:
    containerPort: 9001
```

`terminationGracePeriodSeconds` - integer - the time between the container getting a SIGTERM and forcefully killed by kubernetes.
Your app should react to SIGTERM and terminate gracefully before terminationGracePeriodSeconds runs out.
`restartPolicy` - by default the pod will be recreated if it dies. This policy can be changed with this value.


## Service Account, AWS IRSA

A service account allows the pod to authenticate to kubernetes api.
It is however mainly used by the [IRSA](https://docs.aws.amazon.com/emr/latest/EMR-on-EKS-DevelopmentGuide/setting-up-enable-IAM.html) integration to authenticate to AWS services with the aws role definition defined with `serviceAccount.awsRole`.
`serviceAccount.awsRole` is integrated with env-lib and will look up the role by an alias under `awsRoles` key in env-lib values.
Disable service account if it is not used.
The example shows how to apply an aws role with role alias `my-role` to the application.

```yaml
serviceAccount:
  create: true
  awsRole: "my-role"
  annotations: {}
  name: ""
```


## Datadog integration

The chart comes with Datadog APM integration.
One can enable Datadog integration like so.

```yaml
apm:
  datadog:
    enabled: true
    environment: "" # empty means the kubernetes namespace name should be taken as the environment
    serviceMapping: ""
```
`apm.datadog.environment` - sets `DD_ENV`, the environment the APM will report to. Empty string means kubernetes namespace should be used and the environment. This is a good default.
`apm.datadog.serviceMapping` - sets `DD_SERVICE_MAPPING`.
- [Datadog docs](https://docs.datadoghq.com/tracing/setup_overview/setup/java/?tab=containers)

## Scheduling and Scaling

Kubernetes uses `Resource Requests` to schedule pods onto nodes so that the node has the available resources.
Ensure your service has CPU and Memory requests that cover the peak usage of your service.
You may start with higher values and adjust it based on the usage of the service.
Ephemeral environments should have smaller requests so that more pods could be crammed into one node.
CPU requests were not set in ephemeral, so that the scheduling is done only on memory request.
This is due to pods being evicted from nodes when the node runs out of memory.
When CPU usage on a node is high on the other hand the pods are only throttled.
512 Mi RAM for Java applications is a good value in ephemeral.

```yaml
resources:
  requests:
    memory: 512Mi
    cpu: 100m
```

Kubernetes' deployments can be updated using one of the 2 strategies: `RollingUpdate` or `Recreate`.
If a service can be run in multiple instances `RollingUpdate` strategy allows the application to be available during the upgrade.
`RollingUpdate` strategy can be configured with `maxSurge` and `maxUnavailable` values. See kubernetes documentation.
Otherwise, set `rollingUpdate: {}` to disable `RollingUpdate` and enable `Recreate`.

[How Rolling Update is Performed](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/)

[Update Strategies](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#strategy)

```yaml
rollingUpdate:
  maxSurge: "25%"
  maxUnavailable: "25%"
```


### Static scaling
`replicaCount` - defines the amount of pods of the service to start if HPA is not enabled.

### Autoscaling
If the count of pods of the application should be changed dynamically based on the load `HorizontalPodAutoscaler(HPA)` can be used.
`autoscaling.enabled` - bool - enables the creation of `HPA` resource.
[HPA docs](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

The following example shows how HPA can be configured in the chart.
Refer to kubernetes documentation for the description of the values.

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 4
  targetCPUUtilizationPercentage: 70
  # targetMemoryUtilizationPercentage: 80
```

### HA pod scheduling

Ensuring high availability of services requires us to ensure that the pods of the same application are not scheduled on the same node in case the node or the availability zone becomes unavailable.
Achieving this can be done in two ways:
1. using `anti-affinity` [Docs](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)
2. using `topologySpreadConstraints` [Docs](https://kubernetes.io/docs/concepts/workloads/pods/pod-topology-spread-constraints/).

The chart allows setting both. As `topologySpreadConstraints` are a newer feature we suggest enabling both.
Setting up `anti-affinity` and `topologySpreadConstraints` is error-prone, so the chart comes with pre-built presets for both.
This is how to use recommended anti-affinity. Refer to chart's source code in starter-lib to see what default preset entails. This is a good default.

```yaml
affinityPresets: ["default"]
```

All affinity presets can be disabled by setting `affinityPresets: []`.
Then `extraAffinity` key can be used to set specific affinity values.

TopologySpreadConstraints presets are set with:
```yaml
topologySpreadPresets: ["default"]
```
This is a good default.
Disable all presets by setting `topologySpreadPresets: []`.
`extraTopologySpreadConstraint` - can be used to set a specific topologySpreadConstraint.

`tolerations` - array - defines pods' tolerations. [Docs](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/).
Keep it an empty array unless tolerations are required.
```yaml
tolerations: []
```

### Pod Disruption Budget
`PodDisruptionBudget (PDB)` resource helps ensure that a certain count of pods is always in `ready` state, meaning service traffic.
Example of requiring at least one pod of the application to be up:
```yaml
pdb:
  minAvailable: 1
#  maxUnavailable: 1 # choose maxUnavailable or minAvailable
```
This is a good default, unless the application runs in a single pod. If so, then PDB should be disabled.

`pdb: null` - disables PDB.

## Security
Applications should not run as root and should operate on readonly filesystem.
The guide to achieving is located here [Rootless Services](https://docs.lsk.lightspeed.app/Tutorials/rootless-services/).
The following values are explained in the guide.
By default, pods are run as root and can edit the filesystem.
```yaml
podSecurityContext: {}
  # fsGroup: 2000

securityContext: {}
  # capabilities:
  #   drop:
  #   - ALL
  # readOnlyRootFilesystem: true
  # runAsNonRoot: true
  # runAsUser: 1000
```


## Docker images and naming
`nameOverride` - overrides what would otherwise be {Chart.Name} (deprecated).
`fullnameOverride` - overrides the fullname.

"starter-lib.fullname" will return `fullnameOverride` if set.
The default returns a value that is unique per namespace (cluster?) if release name and chart name together are unique.

`image.name` - the name of the docker image in the registry, by default - chart name is used
`image.pullPolicy` - default `IfNotPresent`, defines when the docker image needs to be pulled
`image.tag` - default `.Chart.AppVersion`, the docker tag to be pulled.
`image.registry`: do not override. The value is set based on the environment where the helm chart is to be deployed.


## Misc values

`podAnnotations` - dict - allows adding extra annotations to pods.


In case a headless service is required an extra `Service` resource for it can be created. [HeadlessService docs](https://kubernetes.io/docs/concepts/services-networking/service/#headless-services).
```yaml
headlessService: {}
#  enabled: false
#  type: ClusterIP
#  ports:
#    - port: 5701
#      targetPort: hazelcast
#      name: hazelcast
```

`hostAliases` - json string array - the domains that should not be resolvable by the application. Used in ephemeral and upper envs to ensure no calls to other envs are made.
Set it like so in all environments:
```yaml
hostAliases: '{{- include "starter-lib.blocked-domains" $ }}'
```
