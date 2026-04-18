from toolbox.fs import os_path, create_path
from toolbox.utils import get_env

COVER_DIR = os_path(get_env("COVER_DIR", required=True, verbose=1))
THUMB_DIR = os_path(get_env("THUMB_DIR", required=True, verbose=1))
IMAGE_DIR = os_path(get_env("IMAGE_DIR", required=True, verbose=1))
SCRATCH_DIR = os_path(get_env("SCRATCH_DIR", required=True, verbose=1))

create_path(SCRATCH_DIR)
