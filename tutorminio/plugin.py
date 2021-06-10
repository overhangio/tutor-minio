import os
from glob import glob

from .__about__ import __version__


HERE = os.path.abspath(os.path.dirname(__file__))

config = {
    "set": {
        "OPENEDX_AWS_ACCESS_KEY": "openedx",
        "OPENEDX_AWS_SECRET_ACCESS_KEY": "{{ MINIO_AWS_SECRET_ACCESS_KEY }}",
    },
    "add": {
        "AWS_SECRET_ACCESS_KEY": "{{ OPENEDX_AWS_SECRET_ACCESS_KEY|default('') or 24|random_string }}",
    },
    "defaults": {
        "VERSION": __version__,
        "BUCKET_NAME": "openedx",
        "FILE_UPLOAD_BUCKET_NAME": "openedxuploads",
        "VIDEO_UPLOAD_BUCKET_NAME": "openedxvideos",
        "HOST": "minio.{{ LMS_HOST }}",
        "DOCKER_IMAGE": "docker.io/minio/minio:RELEASE.2021-06-07T21-40-51Z",
        "MC_DOCKER_IMAGE": "docker.io/minio/mc:RELEASE.2021-06-08T01-29-37Z",
        "GATEWAY": None,
    },
}

templates = os.path.join(HERE, "templates")

hooks = {
    "pre-init": ["minio"],
}


def patches():
    all_patches = {}
    for path in glob(os.path.join(HERE, "patches", "*")):
        with open(path) as patch_file:
            name = os.path.basename(path)
            content = patch_file.read()
            all_patches[name] = content
    return all_patches
