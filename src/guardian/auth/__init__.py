from oauthlib.oauth2 import Server

from .request_validator import validator
from .utils import enable_oauthlib_debug, extract_params

__all__ = [
    "authorization_server",
    "enable_oauthlib_debug",
    "extract_params",
]

authorization_server = Server(validator)
