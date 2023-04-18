# pylint: disable=W4901
import distutils.util
import os

CI = bool(distutils.util.strtobool(os.getenv("CI", "false")))
