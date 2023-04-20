from typing import Any
from uuid import UUID

from oauthlib.common import Request
from oauthlib.openid import RequestValidator as BaseRequestValidator

from guardian.models import BearerToken, Client, GrantType, User


class OAuth2RequestValidatorMixin:
    def authenticate_client(self, request: Request, *args, **kwargs) -> bool:
        """Authenticate client through means outside the OAuth 2 spec.

        Means of authentication is negotiated beforehand and may for example
        be `HTTP Basic Authentication Scheme`_ which utilizes the Authorization
        header.

        Headers may be accesses through request.headers and parameters found in
        both body and query can be obtained by direct attribute access, i.e.
        request.client_id for client_id in the URL query.

        The authentication process is required to contain the identification of
        the client (i.e. search the database based on the client_id). In case the
        client doesn't exist based on the received client_id, this method has to
        return False and the HTTP response created by the library will contain
        'invalid_client' message.

        After the client identification succeeds, this method needs to set the
        client on the request, i.e. request.client = client. A client object's
        class must contain the 'client_id' attribute and the 'client_id' must have
        a value.

        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: True or False

        Method is used by:
            - Authorization Code Grant
            - Resource Owner Password Credentials Grant (may be disabled)
            - Client Credentials Grant
            - Refresh Token Grant

        .. _`HTTP Basic Authentication Scheme`: https://tools.ietf.org/html/rfc1945#section-11.1
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def authenticate_client_id(self, client_id: UUID, request: Request, *args, **kwargs) -> bool:
        """Ensure client_id belong to a non-confidential client.

        A non-confidential client is one that is not required to authenticate
        through other means, such as using HTTP Basic.

        Note, while not strictly necessary it can often be very convenient
        to set request.client to the client object associated with the
        given client_id.

        :param client_id: Unicode client identifier.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: True or False

        Method is used by:
            - Authorization Code Grant
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def confirm_redirect_uri(
        self, client_id: UUID, code: str, redirect_uri: str, client: Client, request: Request, *args, **kwargs
    ) -> bool:
        """Ensure that the authorization process represented by this authorization
        code began with this 'redirect_uri'.

        If the client specifies a redirect_uri when obtaining code then that
        redirect URI must be bound to the code and verified equal in this
        method, according to RFC 6749 section 4.1.3.  Do not compare against
        the client's allowed redirect URIs, but against the URI used when the
        code was saved.

        :param client_id: Unicode client identifier.
        :param code: Unicode authorization_code.
        :param redirect_uri: Unicode absolute URI.
        :param client: Client object set by you, see ``.authenticate_client``.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: True or False

        Method is used by:
            - Authorization Code Grant (during token request)
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def get_default_redirect_uri(self, client_id: UUID, request: Request, *args, **kwargs) -> str:
        """Get the default redirect URI for the client.

        :param client_id: Unicode client identifier.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: The default redirect URI for the client

        Method is used by:
            - Authorization Code Grant
            - Implicit Grant
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def get_default_scopes(self, client_id: UUID, request: Request, *args, **kwargs) -> list[str]:
        """Get the default scopes for the client.

        :param client_id: Unicode client identifier.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: List of default scopes

        Method is used by all core grant types:
            - Authorization Code Grant
            - Implicit Grant
            - Resource Owner Password Credentials Grant
            - Client Credentials grant
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def get_original_scopes(self, refresh_token: str, request: Request, *args, **kwargs) -> list[str]:
        """Get the list of scopes associated with the refresh token.

        :param refresh_token: Unicode refresh token.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: List of scopes.

        Method is used by:
            - Refresh token grant
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def introspect_token(
        self, token: str, token_type_hint: str, request: Request, *args, **kwargs
    ) -> dict[str, Any] | None:
        """Introspect an access or refresh token.

        Called once the introspect request is validated. This method should
        verify the *token* and either return a dictionary with the list of
        claims associated, or `None` in case the token is unknown.

        Below the list of registered claims you should be interested in:

        - scope : space-separated list of scopes
        - client_id : client identifier
        - username : human-readable identifier for the resource owner
        - token_type : type of the token
        - exp : integer timestamp indicating when this token will expire
        - iat : integer timestamp indicating when this token was issued
        - nbf : integer timestamp indicating when it can be "not-before" used
        - sub : subject of the token - identifier of the resource owner
        - aud : list of string identifiers representing the intended audience
        - iss : string representing issuer of this token
        - jti : string identifier for the token

        Note that most of them are coming directly from JWT RFC. More details
        can be found in `Introspect Claims`_ or `JWT Claims`_.

        The implementation can use *token_type_hint* to improve lookup
        efficiency, but must fallback to other types to be compliant with RFC.

        The dict of claims is added to request.token after this method.

        :param token: The token string.
        :param token_type_hint: access_token or refresh_token.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request

        Method is used by:
            - Introspect Endpoint (all grants are compatible)

        .. _`Introspect Claims`: https://tools.ietf.org/html/rfc7662#section-2.2
        .. _`JWT Claims`: https://tools.ietf.org/html/rfc7519#section-4
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def invalidate_authorization_code(self, client_id: UUID, code: str, request: Request, *args, **kwargs) -> None:
        """Invalidate an authorization code after use.

        :param client_id: Unicode client identifier.
        :param code: The authorization code grant (request.code).
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request

        Method is used by:
            - Authorization Code Grant
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def revoke_token(self, token: str, token_type_hint: str, request: Request, *args, **kwargs) -> None:
        """Revoke an access or refresh token.

        :param token: The token string.
        :param token_type_hint: access_token or refresh_token.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request

        Method is used by:
            - Revocation Endpoint
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def save_authorization_code(self, client_id: UUID, code: str, request: Request, *args, **kwargs) -> None:
        """Persist the authorization_code.

        The code should at minimum be stored with:
            - the client_id (``client_id``)
            - the redirect URI used (``request.redirect_uri``)
            - a resource owner / user (``request.user``)
            - the authorized scopes (``request.scopes``)

        To support PKCE, you MUST associate the code with:
            - Code Challenge (``request.code_challenge``) and
            - Code Challenge Method (``request.code_challenge_method``)

        To support OIDC, you MUST associate the code with:
            - nonce, if present (``code["nonce"]``)

        The ``code`` argument is actually a dictionary, containing at least a
        ``code`` key with the actual authorization code:

            ``{'code': 'sdf345jsdf0934f'}``

        It may also have a ``claims`` parameter which, when present, will be a dict
        deserialized from JSON as described at
        http://openid.net/specs/openid-connect-core-1_0.html#ClaimsParameter
        This value should be saved in this method and used again in ``.validate_code``.

        :param client_id: Unicode client identifier.
        :param code: A dict of the authorization code grant and, optionally, state.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request

        Method is used by:
            - Authorization Code Grant
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def save_token(self, token: BearerToken, request: Request, *args, **kwargs) -> None:
        """Persist the token with a token type specific method.

        Currently, only save_bearer_token is supported.

        :param token: A (Bearer) token dict.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        """
        return self.save_bearer_token(token, request, *args, **kwargs)

    def save_bearer_token(self, token: BearerToken, request: Request, *args, **kwargs) -> None:
        """Persist the Bearer token.

        The Bearer token should at minimum be associated with:
            - a client and it's client_id, if available
            - a resource owner / user (request.user)
            - authorized scopes (request.scopes)
            - an expiration time
            - a refresh token, if issued
            - a claims document, if present in request.claims

        The Bearer token dict may hold a number of items::

            {
                'token_type': 'Bearer',
                'access_token': 'askfjh234as9sd8',
                'expires_in': 3600,
                'scope': 'string of space separated authorized scopes',
                'refresh_token': '23sdf876234',  # if issued
                'state': 'given_by_client',  # if supplied by client (implicit ONLY)
            }

        Note that while "scope" is a string-separated list of authorized scopes,
        the original list is still available in request.scopes.

        The token dict is passed as a reference so any changes made to the dictionary
        will go back to the user.  If additional information must return to the client
        user, and it is only possible to get this information after writing the token
        to storage, it should be added to the token dictionary.  If the token
        dictionary must be modified but the changes should not go back to the user,
        a copy of the dictionary must be made before making the changes.

        Also note that if an Authorization Code grant request included a valid claims
        parameter (for OpenID Connect) then the request.claims property will contain
        the claims dict, which should be saved for later use when generating the
        id_token and/or UserInfo response content.

        :param token: A Bearer token dict.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: The default redirect URI for the client

        Method is used by all core grant types issuing Bearer tokens:
            - Authorization Code Grant
            - Implicit Grant
            - Resource Owner Password Credentials Grant (might not associate a client)
            - Client Credentials grant
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def validate_bearer_token(self, token: str, scopes: list[str], request: Request) -> bool:
        """Ensure the Bearer token is valid and authorized access to scopes.

        :param token: A string of random characters.
        :param scopes: A list of scopes associated with the protected resource.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request

        A key to OAuth 2 security and restricting impact of leaked tokens is
        the short expiration time of tokens, *always ensure the token has not
        expired!*.

        Two different approaches to scope validation:

            1) all(scopes). The token must be authorized access to all scopes
                            associated with the resource. For example, the
                            token has access to ``read-only`` and ``images``,
                            thus the client can view images but not upload new.
                            Allows for fine grained access control through
                            combining various scopes.

            2) any(scopes). The token must be authorized access to one of the
                            scopes associated with the resource. For example,
                            token has access to ``read-only-images``.
                            Allows for fine grained, although arguably less
                            convenient, access control.

        A powerful way to use scopes would mimic UNIX ACLs and see a scope
        as a group with certain privileges. For a restful API these might
        map to HTTP verbs instead of read, write and execute.

        Note, the request.user attribute can be set to the resource owner
        associated with this token. Similarly the request.client and
        request.scopes attribute can be set to associated client object
        and authorized scopes. If you then use a decorator such as the
        one provided for django these attributes will be made available
        in all protected views as keyword arguments.

        :param token: Unicode Bearer token
        :param scopes: List of scopes (defined by you)
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: True or False

        Method is indirectly used by all core Bearer token issuing grant types:
            - Authorization Code Grant
            - Implicit Grant
            - Resource Owner Password Credentials Grant
            - Client Credentials Grant
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def validate_client_id(self, client_id: UUID, request: Request, *args, **kwargs) -> bool:
        """Ensure client_id belong to a valid and active client.

        Note, while not strictly necessary it can often be very convenient
        to set request.client to the client object associated with the
        given client_id.

        :param client_id: Unicode client identifier.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: True or False

        Method is used by:
            - Authorization Code Grant
            - Implicit Grant
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def validate_code(self, client_id: UUID, code: str, client: Client, request: Request, *args, **kwargs) -> bool:
        """Verify that the authorization_code is valid and assigned to the given
        client.

        Before returning true, set the following based on the information stored
        with the code in 'save_authorization_code':

            - request.user
            - request.scopes
            - request.claims (if given)

        OBS! The request.user attribute should be set to the resource owner
        associated with this authorization code. Similarly request.scopes
        must also be set.

        The request.claims property, if it was given, should assigned a dict.

        If PKCE is enabled (see 'is_pkce_required' and 'save_authorization_code')
        you MUST set the following based on the information stored:

            - request.code_challenge
            - request.code_challenge_method

        :param client_id: Unicode client identifier.
        :param code: Unicode authorization code.
        :param client: Client object set by you, see ``.authenticate_client``.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: True or False

        Method is used by:
            - Authorization Code Grant
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def validate_grant_type(
        self, client_id: UUID, grant_type: GrantType, client: Client, request: Request, *args, **kwargs
    ) -> bool:
        """Ensure client is authorized to use the grant_type requested.

        :param client_id: Unicode client identifier.
        :param grant_type: Unicode grant type, i.e. authorization_code, password.
        :param client: Client object set by you, see ``.authenticate_client``.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: True or False

        Method is used by:
            - Authorization Code Grant
            - Resource Owner Password Credentials Grant
            - Client Credentials Grant
            - Refresh Token Grant
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def validate_redirect_uri(self, client_id: UUID, redirect_uri: str, request: Request, *args, **kwargs) -> bool:
        """Ensure client is authorized to redirect to the redirect_uri requested.

        All clients should register the absolute URIs of all URIs they intend
        to redirect to. The registration is outside of the scope of oauthlib.

        :param client_id: Unicode client identifier.
        :param redirect_uri: Unicode absolute URI.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: True or False

        Method is used by:
            - Authorization Code Grant
            - Implicit Grant
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def validate_refresh_token(self, refresh_token: str, client: Client, request: Request, *args, **kwargs) -> bool:
        """Ensure the Bearer token is valid and authorized access to scopes.

        OBS! The request.user attribute should be set to the resource owner
        associated with this refresh token.

        :param refresh_token: Unicode refresh token.
        :param client: Client object set by you, see ``.authenticate_client``.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: True or False

        Method is used by:
            - Authorization Code Grant (indirectly by issuing refresh tokens)
            - Resource Owner Password Credentials Grant (also indirectly)
            - Refresh Token Grant
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def validate_response_type(
        self, client_id: UUID, response_type: str, client: Client, request: Request, *args, **kwargs
    ) -> bool:
        """Ensure client is authorized to use the response_type requested.

        :param client_id: Unicode client identifier.
        :param response_type: Unicode response type, i.e. code, token.
        :param client: Client object set by you, see ``.authenticate_client``.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: True or False

        Method is used by:
            - Authorization Code Grant
            - Implicit Grant
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def validate_scopes(
        self, client_id: UUID, scopes: list[str], client: Client, request: Request, *args, **kwargs
    ) -> bool:
        """Ensure the client is authorized access to requested scopes.

        :param client_id: Unicode client identifier.
        :param scopes: List of scopes (defined by you).
        :param client: Client object set by you, see ``.authenticate_client``.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: True or False

        Method is used by all core grant types:
            - Authorization Code Grant
            - Implicit Grant
            - Resource Owner Password Credentials Grant
            - Client Credentials Grant
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def validate_user(self, username: str, password: str, client: Client, request: Request, *args, **kwargs) -> bool:
        """Ensure the username and password is valid.

        OBS! The validation should also set the user attribute of the request
        to a valid resource owner, i.e. request.user = username or similar. If
        not set you will be unable to associate a token with a user in the
        persistence method used (commonly, save_bearer_token).

        :param username: Unicode username.
        :param password: Unicode password.
        :param client: Client object set by you, see ``.authenticate_client``.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: True or False

        Method is used by:
            - Resource Owner Password Credentials Grant
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def get_code_challenge_method(self, code, request):
        """Is called during the "token" request processing, when a
        ``code_verifier`` and a ``code_challenge`` has been provided.

        See ``.get_code_challenge``.

        Must return ``plain`` or ``S256``. You can return a custom value if you have
        implemented your own ``AuthorizationCodeGrant`` class.

        :param code: Authorization code.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: code_challenge_method string

        Method is used by:
            - Authorization Code Grant - when PKCE is active

        """
        raise NotImplementedError("Subclasses must implement this method.")


class OpenIDRequestValidatorMixin:
    def get_authorization_code_scopes(
        self, client_id: UUID, code: str, redirect_uri: str, request: Request
    ) -> list[str]:
        """Extracts scopes from saved authorization code.

        The scopes returned by this method is used to route token requests
        based on scopes passed to Authorization Code requests.

        With that the token endpoint knows when to include OpenIDConnect
        id_token in token response only based on authorization code scopes.

        Only code param should be sufficient to retrieve grant code from
        any storage you are using, `client_id` and `redirect_uri` can have a
        blank value `""` don't forget to check it before using those values
        in a select query if a database is used.

        :param client_id: Unicode client identifier
        :param code: Unicode authorization code grant
        :param redirect_uri: Unicode absolute URI
        :return: A list of scope

        Method is used by:
            - Authorization Token Grant Dispatcher
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def get_authorization_code_nonce(self, client_id, code, redirect_uri, request):
        """Extracts nonce from saved authorization code.

        If present in the Authentication Request, Authorization
        Servers MUST include a nonce Claim in the ID Token with the
        Claim Value being the nonce value sent in the Authentication
        Request. Authorization Servers SHOULD perform no other
        processing on nonce values used. The nonce value is a
        case-sensitive string.

        Only code param should be sufficient to retrieve grant code from
        any storage you are using. However, `client_id` and `redirect_uri`
        have been validated and can be used also.

        :param client_id: Unicode client identifier
        :param code: Unicode authorization code grant
        :param redirect_uri: Unicode absolute URI
        :return: Unicode nonce

        Method is used by:
            - Authorization Token Grant Dispatcher
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def get_jwt_bearer_token(self, token: BearerToken, token_handler, request: Request):
        """Get JWT Bearer token or OpenID Connect ID token

        If using OpenID Connect this SHOULD call `oauthlib.oauth2.RequestValidator.get_id_token`

        :param token: A Bearer token dict
        :param token_handler: the token handler (BearerToken class)
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :return: The JWT Bearer token or OpenID Connect ID token (a JWS signed JWT)

        Method is used by JWT Bearer and OpenID Connect tokens:
            - JWTToken.create_token
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def finalize_id_token(self, id_token: dict, token: BearerToken, token_handler, request: Request) -> str:
        """Finalize OpenID Connect ID token & Sign or Encrypt.

        In the OpenID Connect workflows when an ID Token is requested
        this method is called.  Subclasses should implement the
        construction, signing and optional encryption of the ID Token
        as described in the OpenID Connect spec.

        The `id_token` parameter is a dict containing a couple of OIDC
        technical fields related to the specification. Prepopulated
        attributes are:

        - `aud`, equals to `request.client_id`.
        - `iat`, equals to current time.
        - `nonce`, if present, is equals to the `nonce` from the
          authorization request.
        - `at_hash`, hash of `access_token`, if relevant.
        - `c_hash`, hash of `code`, if relevant.

        This method MUST provide required fields as below:

        - `iss`, REQUIRED. Issuer Identifier for the Issuer of the response.
        - `sub`, REQUIRED. Subject Identifier
        - `exp`, REQUIRED. Expiration time on or after which the ID
          Token MUST NOT be accepted by the RP when performing
          authentication with the OP.

        Additionals claims must be added, note that `request.scope`
        should be used to determine the list of claims.

        More information can be found at `OpenID Connect Core#Claims`_

        .. _`OpenID Connect Core#Claims`: https://openid.net/specs/openid-connect-core-1_0.html#Claims

        :param id_token: A dict containing technical fields of id_token
        :param token: A Bearer token dict
        :param token_handler: the token handler (BearerToken class)
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :return: The ID Token (a JWS signed JWT or JWE encrypted JWT)
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def validate_jwt_bearer_token(self, token: str, scopes: list[str], request: Request) -> bool:
        """Ensure the JWT Bearer token or OpenID Connect ID token are valids and authorized access to scopes.

        If using OpenID Connect this SHOULD call `oauthlib.oauth2.RequestValidator.get_id_token`

        If not using OpenID Connect this can `return None` to avoid 5xx rather 401/3 response.

        OpenID connect core 1.0 describe how to validate an id_token:
            - http://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation
            - http://openid.net/specs/openid-connect-core-1_0.html#ImplicitIDTValidation
            - http://openid.net/specs/openid-connect-core-1_0.html#HybridIDTValidation
            - http://openid.net/specs/openid-connect-core-1_0.html#HybridIDTValidation2

        :param token: Unicode Bearer token
        :param scopes: List of scopes (defined by you)
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: True or False

        Method is indirectly used by all core OpenID connect JWT token issuing grant types:
            - Authorization Code Grant
            - Implicit Grant
            - Hybrid Grant
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def validate_id_token(self, token: str, scopes: list[str], request: Request) -> bool:
        """Ensure the id token is valid and authorized access to scopes.

        OpenID connect core 1.0 describe how to validate an id_token:
            - http://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation
            - http://openid.net/specs/openid-connect-core-1_0.html#ImplicitIDTValidation
            - http://openid.net/specs/openid-connect-core-1_0.html#HybridIDTValidation
            - http://openid.net/specs/openid-connect-core-1_0.html#HybridIDTValidation2

        :param token: Unicode Bearer token
        :param scopes: List of scopes (defined by you)
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: True or False

        Method is indirectly used by all core OpenID connect JWT token issuing grant types:
            - Authorization Code Grant
            - Implicit Grant
            - Hybrid Grant
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def validate_silent_authorization(self, request: Request) -> bool:
        """Ensure the logged in user has authorized silent OpenID authorization.

        Silent OpenID authorization allows access tokens and id tokens to be
        granted to clients without any user prompt or interaction.

        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: True or False

        Method is used by:
            - OpenIDConnectAuthCode
            - OpenIDConnectImplicit
            - OpenIDConnectHybrid
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def validate_silent_login(self, request: Request) -> bool:
        """Ensure session user has authorized silent OpenID login.

        If no user is logged in or has not authorized silent login, this
        method should return False.

        If the user is logged in but associated with multiple accounts and
        not selected which one to link to the token then this method should
        raise an oauthlib.oauth2.AccountSelectionRequired error.

        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: True or False

        Method is used by:
            - OpenIDConnectAuthCode
            - OpenIDConnectImplicit
            - OpenIDConnectHybrid
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def validate_user_match(self, id_token_hint: str, scopes: list[str], claims: dict, request: Request) -> bool:
        """Ensure client supplied user id hint matches session user.

        If the sub claim or id_token_hint is supplied then the session
        user must match the given ID.

        :param id_token_hint: User identifier string.
        :param scopes: List of OAuth 2 scopes and OpenID claims (strings).
        :param claims: OpenID Connect claims dict.
        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: True or False

        Method is used by:
            - OpenIDConnectAuthCode
            - OpenIDConnectImplicit
            - OpenIDConnectHybrid
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def get_userinfo_claims(self, request: Request) -> User:
        """Return the UserInfo claims in JSON or Signed or Encrypted.

        The UserInfo Claims MUST be returned as the members of a JSON object
         unless a signed or encrypted response was requested during Client
         Registration. The Claims defined in Section 5.1 can be returned, as can
         additional Claims not specified there.

        For privacy reasons, OpenID Providers MAY elect to not return values for
        some requested Claims.

        If a Claim is not returned, that Claim Name SHOULD be omitted from the
        JSON object representing the Claims; it SHOULD NOT be present with a
        null or empty string value.

        The sub (subject) Claim MUST always be returned in the UserInfo
        Response.

        Upon receipt of the UserInfo Request, the UserInfo Endpoint MUST return
        the JSON Serialization of the UserInfo Response as in Section 13.3 in
        the HTTP response body unless a different format was specified during
        Registration [OpenID.Registration].

        If the UserInfo Response is signed and/or encrypted, then the Claims are
        returned in a JWT and the content-type MUST be application/jwt. The
        response MAY be encrypted without also being signed. If both signing and
        encryption are requested, the response MUST be signed then encrypted,
        with the result being a Nested JWT, as defined in [JWT].

        If signed, the UserInfo Response SHOULD contain the Claims iss (issuer)
        and aud (audience) as members. The iss value SHOULD be the OP's Issuer
        Identifier URL. The aud value SHOULD be or include the RP's Client ID
        value.

        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :rtype: Claims as a dict OR JWT/JWS/JWE as a string

        Method is used by:
            UserInfoEndpoint
        """


class RequestValidator(BaseRequestValidator, OAuth2RequestValidatorMixin, OpenIDRequestValidatorMixin):
    pass


validator = RequestValidator()
