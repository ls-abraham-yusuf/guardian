import logging
import sys
from typing import TypeAlias

import oauthlib
from fastapi import Request

RequestParams: TypeAlias = tuple[str, str, bytes, dict[str, str]]


async def extract_params(request: Request) -> RequestParams:
    url = str(request.url)
    try:
        body = await request.body()
    except RuntimeError:
        body = b""
    return url, request.method, body, dict(request.headers)


def enable_oauthlib_debug():
    oauthlib.set_debug(True)
    log = logging.getLogger("oauthlib")
    log.addHandler(logging.StreamHandler(sys.stdout))
    log.setLevel(logging.DEBUG)
