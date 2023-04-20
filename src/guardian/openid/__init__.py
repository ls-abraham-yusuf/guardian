from oauthlib.openid import Server

from .request_validator import validator
from .utils import enable_oauthlib_debug, extract_params

__all__ = [
    "enable_oauthlib_debug",
    "extract_params",
    "provider",
]

provider = Server(validator)
