from fastapi.templating import Jinja2Templates

from guardian.config import guardian


def get_templates() -> Jinja2Templates:
    return Jinja2Templates(directory=guardian.server.JINJA2_TEMPLATES_DIR)
