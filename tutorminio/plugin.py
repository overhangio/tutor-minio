import os
from glob import glob

from .__about__ import __version__


HERE = os.path.abspath(os.path.dirname(__file__))

config = {
    "set": {
        "OPENEDX_AWS_ACCESS_KEY": "openedx",
        "OPENEDX_AWS_SECRET_ACCESS_KEY": "{{ 24|random_string }}",
    },
    "defaults": {
        "VERSION": __version__,
        "BUCKET_NAME": "openedx",
        "FILE_UPLOAD_BUCKET_NAME": "openedxuploads",
        "COURSE_IMPORT_EXPORT_BUCKET": "openedxcourseimportexport",
        "HOST": "minio.{{ LMS_HOST }}",
        "DOCKER_REGISTRY": "{{ DOCKER_REGISTRY }}",
        "DOCKER_IMAGE": "overhangio/minio:{{ MINIO_VERSION }}",
        "MODE": "server",
        "GATEWAY": "s3",
        "GATEWAY_ENDPOINT": "https://s3.us-east-2.amazonaws.com",
    },
}

templates = os.path.join(HERE, "templates")

hooks = {
    "pre-init": ["minio"],
    "build-image": {"minio": "{{ DOCKER_REGISTRY }}{{ MINIO_DOCKER_IMAGE }}"},
    "remote-image": {"minio": "{{ DOCKER_REGISTRY }}{{ MINIO_DOCKER_IMAGE }}"},
}


def patches():
    all_patches = {}
    for path in glob(os.path.join(HERE, "patches", "*")):
        with open(path) as patch_file:
            name = os.path.basename(path)
            content = patch_file.read()
            all_patches[name] = content
    return all_patches
