import os
from glob import glob

import pkg_resources

from tutor import hooks as tutor_hooks

from .__about__ import __version__

HERE = os.path.abspath(os.path.dirname(__file__))

config = {
    "overrides": {
        "OPENEDX_AWS_ACCESS_KEY": "openedx",
        "OPENEDX_AWS_SECRET_ACCESS_KEY": "{{ MINIO_AWS_SECRET_ACCESS_KEY }}",
    },
    "unique": {
        "AWS_SECRET_ACCESS_KEY": "{{ 24|random_string }}",
    },
    "defaults": {
        "VERSION": __version__,
        "BUCKET_NAME": "openedx",
        "FILE_UPLOAD_BUCKET_NAME": "openedxuploads",
        "VIDEO_UPLOAD_BUCKET_NAME": "openedxvideos",
        "HOST": "files.{{ LMS_HOST }}",
        "CONSOLE_HOST": "minio.{{ LMS_HOST }}",
        "DOCKER_IMAGE": "docker.io/minio/minio:RELEASE.2022-05-08T23-50-31Z",
        "MC_DOCKER_IMAGE": "docker.io/minio/mc:RELEASE.2022-05-09T04-08-26Z",
        "GATEWAY": None,
    },
}

tutor_hooks.Filters.COMMANDS_PRE_INIT.add_item((
    "minio",
    ("minio", "tasks", "minio", "pre-init"),
))

# Add the "templates" folder as a template root
tutor_hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(
    pkg_resources.resource_filename("tutorminio", "templates")
)
# Render the "build" and "apps" folders
tutor_hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    [
        ("minio/build", "plugins"),
        ("minio/apps", "plugins"),
    ],
)
# Load patches from files
for path in glob(
    os.path.join(
        pkg_resources.resource_filename("tutorminio", "patches"),
        "*",
    )
):
    with open(path, encoding="utf-8") as patch_file:
        tutor_hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))
# Add configuration entries
tutor_hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        (f"MINIO_{key}", value)
        for key, value in config.get("defaults", {}).items()
    ]
)
tutor_hooks.Filters.CONFIG_UNIQUE.add_items(
    [
        (f"MINIO_{key}", value)
        for key, value in config.get("unique", {}).items()
    ]
)
tutor_hooks.Filters.CONFIG_OVERRIDES.add_items(list(config.get("overrides", {}).items()))
