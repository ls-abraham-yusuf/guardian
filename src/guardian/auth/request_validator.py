from uuid import UUID

from oauthlib.common import Request
from oauthlib.oauth2 import RequestValidator as _RequestValidator


class RequestValidator(_RequestValidator):
    def validate_client_id(self, _client_id: UUID, _request: Request, *_args, **_kwargs) -> bool:
        # TODO: implement
        # return True if client_id exists in database and is a valid uuidv4 else False
        return True


validator = RequestValidator()
