import json
import uuid
from typing import Any, Literal, Type

import itsdangerous
from fastapi import FastAPI
from itsdangerous.exc import BadSignature
from redis import asyncio as redis
from redis.asyncio.connection import ConnectionPool
from starlette.datastructures import MutableHeaders, Secret
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from guardian.config import Guardian


class RedisMiddleware:
    def __init__(self, app: ASGIApp, url: str, connection_pool_class: Type[ConnectionPool] = ConnectionPool, **kwargs):
        self.app = app
        self.pool = connection_pool_class.from_url(url, **kwargs)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        scope["redis"] = redis.Redis(connection_pool=self.pool)

        await self.app(scope, receive, send)


class SessionBackend:
    def __init__(self, client: redis.Redis, prefix: str = "guardian:session:"):
        self.client = client
        self.key_prefix = prefix

    def get_key(self, session_id: str) -> str:
        return self.key_prefix + session_id

    async def get(self, session_id: str) -> dict[str, Any]:
        if data := await self.client.get(self.get_key(session_id)):
            return json.loads(data)
        return {}

    async def set(self, data: dict, max_age: int) -> str:
        session_id = str(uuid.uuid4())
        await self.client.setex(self.get_key(session_id), max_age, json.dumps(data))
        return session_id


class SessionMiddleware:
    def __init__(  # pylint: disable=too-many-arguments
        self,
        app: ASGIApp,
        secret_key: str | Secret,
        session_cookie: str = "session",
        max_age: int = 14 * 24 * 60 * 60,  # 14 days, in seconds
        path: str = "/",
        same_site: Literal["lax", "strict", "none"] = "lax",
        https_only: bool = False,
    ) -> None:
        self.app = app
        self.signer = itsdangerous.TimestampSigner(str(secret_key))
        self.session_cookie = session_cookie
        self.max_age = max_age
        self.path = path
        self.security_flags = "httponly; samesite=none" + same_site
        if https_only:  # Secure flag can be used with HTTPS only
            self.security_flags += "; secure"

    def get_cookie_value(self, data: str) -> str:
        expires, max_age = "", f"Max-Age={self.max_age}; " if self.max_age else ""

        if data == "null":
            expires, max_age = "expires=Thu, 01 Jan 1970 00:00:00 GMT; ", ""

        return f"{self.session_cookie}={data}; path={self.path}; {expires}{max_age}{self.security_flags}"

    async def extract_data_from_cookies(self, cookies: dict[str, str], backend: SessionBackend) -> dict[str, Any]:
        if self.session_cookie in cookies:
            signed_key = cookies[self.session_cookie]
            try:
                key = self.signer.unsign(signed_key, max_age=self.max_age).decode("utf-8")
                return await backend.get(key)
            except BadSignature:
                return {}
        return {}

    async def store_session_data(self, data: dict, backend: SessionBackend) -> str:
        session_id = await backend.set(data, self.max_age)
        return self.signer.sign(session_id).decode("utf-8")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        connection = HTTPConnection(scope)
        initial_session_was_empty = True

        backend = SessionBackend(scope["redis"])

        scope["session"] = await self.extract_data_from_cookies(connection.cookies, backend)

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                if scope["session"]:
                    # We have session data to persist.
                    headers = MutableHeaders(scope=message)
                    data = await self.store_session_data(scope["session"], backend)
                    header_value = self.get_cookie_value(data)
                    headers.append("Set-Cookie", header_value)
                elif not initial_session_was_empty:
                    # The session has been cleared.
                    headers = MutableHeaders(scope=message)
                    header_value = self.get_cookie_value("null")
                    headers.append("Set-Cookie", header_value)
            await send(message)

        await self.app(scope, receive, send_wrapper)


def register_middlewares(app: FastAPI, config: Guardian):
    app.add_middleware(RedisMiddleware, url=config.redis_url)
    app.add_middleware(
        SessionMiddleware,
        secret_key=config.SECRET_KEY,
        session_cookie=config.SESSION_COOKIE,
        same_site="none",
        https_only=False,
    )
