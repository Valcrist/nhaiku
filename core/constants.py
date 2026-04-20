from toolbox.fs import os_path, create_path
from toolbox.utils import get_env

COVER_DIR = os_path(get_env("COVER_DIR", required=True, verbose=1))
THUMB_DIR = os_path(get_env("THUMB_DIR", required=True, verbose=1))
IMAGE_DIR = os_path(get_env("IMAGE_DIR", required=True, verbose=1))
SCRATCH_DIR = os_path(get_env("SCRATCH_DIR", required=True, verbose=1))

create_path(SCRATCH_DIR)


OS_STRINGS = [
    "Windows NT 10.0; Win64; x64",
    "Windows NT 10.0; WOW64; x64",
    "Windows NT 11.0; Win64; x64",
    "Windows 7 Enterprise; x64",
    "Windows Server 2012 R2 Standard; x64",
    "X11; Linux x86_64",
    "X11; U; Linux x86_64",
    "X11; Linux x86_64; CentOS Ubuntu 19.04",
    "X11; Ubuntu; Linux x86_64",
    "Macintosh; Intel Mac OS X 10_15_7",
    "Macintosh; Intel Mac OS X 10_9_3",
    "Macintosh; Intel Mac OS X 10_6_8",
    "Macintosh; Intel Mac OS X 10_7_3",
    "Macintosh; Intel Mac OS X 14_2_0",
    "Macintosh; Intel Mac OS X 15_7_3",
    "Macintosh; Intel Mac OS X 15_5_2",
    "Macintosh; Intel Mac OS X 14_5_5",
]

UA_STRINGS = [
    "rv:146.0) Gecko/20100101 Firefox/146.0",
    "rv:138.0) Gecko/20100101 Firefox/138.0",
    "rv:137.0) Gecko/20100101 Firefox/137.0",
    "rv:136.0) Gecko/20100101 Firefox/136.0",
    "rv:133.0) Gecko/20100101 Firefox/133.0",
    "rv:132.0) Gecko/20100101 Firefox/132.0",
    "rv:131.0) Gecko/20100101 Firefox/131.0",
    "rv:130.0) Gecko/20100101 Firefox/130.0",
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.166 Safari/537.36",
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6099.71 Safari/537.36",
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5975.80 Safari/537.36",
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5957.0 Safari/537.36",
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5756.197 Safari/537.36",
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672 Safari/537.36",
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5633.224 Safari/537.36",
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.3713.147 Safari/537.36",
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36",
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
]
