# guardian

<p align="center">
  <a href="#development">Development</a> •
  <a href="#architecture--documentation">Documentation</a> •
  <a href="#how-to-contribute">Contribute</a> •
  <a href="#support--feedback">Support</a>
</p>

This is a super awesome bootstrapped Python project

---

## Development

### Build

#### ⚙️ Configure your dotenv (.env) file

   ```console
   mv '.env.example' '.env'
   ```

Next, open up the file and fill in your Artifactory credentials by replacing the dummy values.

_Note_: The `.env` file containing your personal secrets must not to be checked in (it's therefore added to `.gitignore`).

   ```txt
   PYPI_USER="dummy-user"
   PYPI_RWD_TOKEN="dummy-token"
   ```

_Note_: Find your Artifactory credentials [here](https://lightspeedhq.jfrog.io/ui/admin/artifactory/user_profile)_

#### 🐳 Build the Docker image:

Now you can start building the docker image like this

   ```
   docker-compose build
   # or
   docker build . -t guardian --build-arg EXTRA_INDEX_URLS="--extra-index-url https://${PYPI_USER}:${PYPI_RWD_TOKEN}@lightspeedhq.jfrog.io/artifactory/api/pypi/pypi-local/simple"```
   ```

### Run

#### 🐳 Run in Docker:
   ```
   docker-compose up
   # or
   docker run --rm --name guardian -p 8080:8080 guardian
   ```

#### 🐍 Run the services directly on your machine from the commandline:

   ```console
   poetry install
   poetry run python -m guardian
   ```

## How to Contribute

In order to contribute you just have to have Python installed on your machine. In case you do not have it installed get it from [python.org](https://www.python.org/downloads/).

#### Linting Tool

This project is using [pre-commit](https://pre-commit.com/) to enable linting and auto-formatting as a pre-commit hook.
The hooks are configured in [.pre-commit-config.yaml](./.pre-commit-config.yaml).

To install the hooks you have to run the following command (only once):
```bash
poetry install
poetry run pre-commit install
```

Then you can trigger all the hooks manually by running:
```bash
poetry install
poetry run pre-commit run --all-files
```

Additionally, on every `git commit` the hooks will be triggered and have to pass.

#### How to run tests

You can run all the tests, by simply running:
```bash
poetry install
DOCKER_IMAGE_NAME=test poetry run python -m pytest
```

## Architecture & Documentation
