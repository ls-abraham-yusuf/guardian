from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from oauthlib.oauth2 import FatalClientError, MetadataEndpoint, OAuth2Error
from structlog import get_logger

from guardian.dependencies import get_templates
from guardian.openid import extract_params, provider

router = APIRouter()

log = get_logger()

SESSION_KEY = "oauth2_credentials"


@router.get("/authorize", response_class=HTMLResponse)
async def authorization_request(request: Request, templates: Annotated[Jinja2Templates, Depends(get_templates)]):
    uri, http_method, body, headers = await extract_params(request)
    try:
        scopes, credentials = provider.validate_authorization_request(uri, http_method, body, headers)

        # Not necessarily in session but they need to be
        # accessible in the POST view after form submit.
        request.session[SESSION_KEY] = credentials

        return templates.TemplateResponse(
            "authorize.html",
            {
                "request": request,
                "scopes": scopes,
                "credentials": credentials,
            },
        )

    except FatalClientError as e:
        raise HTTPException(status_code=e.status_code, detail=e.description) from e

    except OAuth2Error as e:
        return RedirectResponse(e.in_uri(e.redirect_uri))


@router.post("/authorize")
async def authorize(request: Request, scopes: Annotated[list[str], Form()]):
    uri, http_method, body, headers = await extract_params(request)
    credentials = request.session.get(SESSION_KEY, {})

    try:
        headers, body, status = provider.create_authorization_response(
            uri, http_method, body, headers, scopes, credentials
        )
        return Response(content=body, status_code=status, headers=headers)

    except FatalClientError as e:
        raise HTTPException(status_code=e.status_code, detail=e.description) from e


@router.post("/token")
async def token(request: Request):
    uri, http_method, body, headers = await extract_params(request)

    # If you wish to include request specific extra credentials for
    # use in the validator, do so here.
    credentials = {"foo": "bar"}

    headers, body, status = provider.create_token_response(uri, http_method, body, headers, credentials)

    return Response(content=body, status_code=status, headers=headers)


@router.post("/introspect")
async def introspect(request: Request):
    uri, http_method, body, headers = await extract_params(request)
    headers, body, status = provider.create_introspect_response(uri, http_method, body, headers)
    return Response(content=body, status_code=status, headers=headers)


@router.post("/revoke")
async def revoke_token(request: Request):
    uri, http_method, body, headers = await extract_params(request)
    headers, body, status = provider.create_revocation_response(uri, http_method, body, headers)
    return Response(content=body, status_code=status, headers=headers)


@router.post("/userinfo")
async def userinfo(request: Request):
    uri, http_method, body, headers = await extract_params(request)
    headers, body, status = provider.create_userinfo_response(uri, http_method, body, headers)
    return Response(content=body, status_code=status, headers=headers)


@router.get("/.well-known")
async def metadata(request: Request):
    claims = {
        "issuer": f"{request.base_url}",
        "scopes_supported": ["openid", "email", "profile"],
        "grant_types_supported": [
            "authorization_code",
            "client_credentials",
        ],
        "token_endpoint": f"{request.url_for('token')}",
        "authorization_endpoint": f"{request.url_for('authorize')}",
        "revocation_endpoint": f"{request.url_for('revoke_token')}",
        "introspection_endpoint": f"{request.url_for('introspect')}",
        "userinfo_endpoint": f"{request.url_for('userinfo')}",
    }
    endpoint = MetadataEndpoint([provider], claims=claims)

    uri, http_method, body, headers = await extract_params(request)
    headers, body, status = endpoint.create_metadata_response(uri, http_method, body, headers)
    return Response(content=body, status_code=status, headers=headers)
