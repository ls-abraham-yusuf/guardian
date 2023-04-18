# pylint: disable=W0613
from pathlib import Path

import pytest
import requests

from tests.utils.docker_compose import docker_compose, save_logs
from tests.utils.wait import wait_is_healthy

from . import env

REPO_ROOT = Path(__file__).parent.parent.parent
COMPOSE_FILE_PATH = (REPO_ROOT / "docker-compose.yml").absolute()


@pytest.fixture(scope="session")
def services_log_file(request):
    """
    Fixture to preapare/create a file for the services logs
    """
    container_output_folder = REPO_ROOT.joinpath(Path("test-results/service-logs"))
    # create it
    container_output_folder.mkdir(exist_ok=True, parents=True)
    # the files where the docker container logs will go to
    # trying to make the log files be unique per test
    test_name = f"{request.node.name}"
    log_folder_for_this_test = container_output_folder / test_name
    log_folder_for_this_test.mkdir(exist_ok=True)
    # now all the container ran during this test would live in one folder with nice names
    out_log_file_path = log_folder_for_this_test / "services.log"
    return out_log_file_path


@pytest.fixture(scope="session")
def startup(services_log_file):
    """
    This fixture is responsible for starting the services and stopping them after the tests are done
    """
    if env.CI:
        docker_compose("pull")
    else:
        docker_compose("build", "--parallel")
    docker_compose(
        "up",
        "--detach",
        "--force-recreate",
        "--remove-orphans",
    )
    yield
    save_logs(services_log_file)
    docker_compose("down")


@pytest.fixture
async def service_url(startup):
    """
    Fixture to get the service url for the service under test
    """
    service_host = docker_compose("port", "guardian", "8080")
    host, port = service_host.split(":")
    service_url = f"http://{host}:{port}"
    await wait_is_healthy(requests.get, url=f"{service_url}/management/health")
    return service_url
