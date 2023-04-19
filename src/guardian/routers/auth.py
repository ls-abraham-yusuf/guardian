from typing import Annotated

import structlog
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from oauthlib.oauth2.rfc6749.errors import FatalClientError, OAuth2Error

from guardian.auth import authorization_server, extract_params

router = APIRouter()

log = structlog.get_logger()


templates = Jinja2Templates(directory="templates")


@router.get("/authorize", response_class=HTMLResponse)
async def authorization_request(request: Request):
    uri, http_method, body, headers = await extract_params(request)
    try:
        scopes, credentials = authorization_server.validate_authorization_request(uri, http_method, body, headers)

        # Not necessarily in session but they need to be
        # accessible in the POST view after form submit.
        request.session["oauth2_credentials"] = credentials

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
    credentials = request.session.get("oauth2_credentials", {})

    try:
        headers, body, status = authorization_server.create_authorization_response(
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

    headers, body, status = authorization_server.create_token_response(uri, http_method, body, headers, credentials)

    return Response(content=body, status_code=status, headers=headers)
