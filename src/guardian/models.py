import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


def uuid_str() -> str:
    return str(uuid.uuid4())


class GrantType(Enum):
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"  # pragma: allowlist secret
    IMPLICIT = "implicit"
    PASSWORD = "password"
    REFRESH_TOKEN = "refresh_token"


class User(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(default="", max_length=150)
    last_name: str = Field(default="", max_length=150)
    is_active: bool = True
    is_staff: bool = False
    is_superuser: bool = False
    last_login: datetime | None = None
    date_joined: datetime = Field(default_factory=datetime.utcnow)


class Client(BaseModel):
    client_id: str = Field(default_factory=uuid_str, max_length=36)  # unique client id
    grant_type: GrantType = GrantType.AUTHORIZATION_CODE
    response_type: str
    scopes: list[str]
    default_scopes: list[str]
    redirect_uris: list[str]
    default_redirect_uri: list[str]


class BearerToken(BaseModel):
    client_id: str
    scopes: list[str]
    access_token: str = Field(max_length=100)  # unique
    refresh_token: str = Field(max_length=100)  # unique
    expires_at: datetime


class AuthorizationCode(BaseModel):
    client_id: str
    user: User
    scopes: list[str]
    redirect_uri: str
    code: str = Field(max_length=100)  # unique
    expires_at: datetime
    challenge: str = Field(default="", max_length=128)
    challenge_method: str = Field(default="", max_length=6)
