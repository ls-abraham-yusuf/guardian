import logging
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
COMPOSE_FILE_PATH = (REPO_ROOT / "docker-compose.test.yml").absolute()

logger = logging.getLogger()


def docker_compose(*args):
    out = None
    cmd = ["docker-compose", "-f", str(COMPOSE_FILE_PATH)] + list(args)
    try:
        logger.info("Executing command: %s", " ".join(cmd))
        out = (
            subprocess.check_output(
                cmd,
                cwd=REPO_ROOT,
                stdin=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=dict(os.environ),
            )
            .decode()
            .rstrip("\n")
        )
        return out
    except subprocess.CalledProcessError as exc:
        logger.error("Failed to execute command '%s' - Error: %s", cmd, exc.stdout)
        raise exc
    except Exception as exc:
        logger.error("Failed to execute command with unknown error '%s' - Error: %s", cmd, exc)
        raise exc


def save_logs(log_file_path: Path):
    logs = docker_compose("logs", "--no-color")
    print(f"Writing service logs to {str(log_file_path.absolute())}")
    with log_file_path.open("w") as f:
        f.write(logs)
