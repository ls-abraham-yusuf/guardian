from fastapi.templating import Jinja2Templates

from guardian import config


def get_templates() -> Jinja2Templates:
    return Jinja2Templates(directory=config.guardian.TEMPLATES_DIR)
