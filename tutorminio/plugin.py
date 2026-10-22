from __future__ import annotations

import os
import typing as t
from glob import glob

import importlib_resources
from tutor import hooks as tutor_hooks
from tutor.__about__ import __version_suffix__

from .__about__ import __version__

# Handle version suffix in main mode, just like tutor core
if __version_suffix__:
    __version__ += "-" + __version_suffix__

HERE = os.path.abspath(os.path.dirname(__file__))

config: dict[str, dict[str, t.Any]] = {
    "defaults": {
        "VERSION": __version__,
        "BUCKET_NAME": "openedx",
        "FILE_UPLOAD_BUCKET_NAME": "openedxuploads",
        "VIDEO_UPLOAD_BUCKET_NAME": "openedxvideos",
        "HOST": "files.{{ LMS_HOST }}",
        "CONSOLE_HOST": "minio.{{ LMS_HOST }}",
        "OPENEDX_LEARNING_BUCKET_NAME": "openedxlearning",
        "GRADES_BUCKET_NAME": "openedxgrades",
        "QUERYSTRING_AUTH": True,
        # minio/minio and minio/mc are gone from Docker Hub and quay.io, so we pull
        # from Rancher's mirror instead. DOCKER_IMAGE is pinned before Gateway mode
        # was dropped (https://blog.min.io/deprecation-of-the-minio-gateway/); Rancher
        # has no mc build from that far back, but mc's `config`/`policy` (used in
        # init.sh) still work against this newer one, just undocumented.
        "DOCKER_IMAGE": "docker.io/rancher/mirrored-minio-minio:RELEASE.2022-03-24T00-43-44Z",  # noqa: E501
        "MC_DOCKER_IMAGE": "docker.io/rancher/mirrored-minio-mc:RELEASE.2022-05-09T04-08-26Z",  # noqa: E501
        "GATEWAY": None,
        "DISCOVERY_BUCKET_NAME": "{% if 'discovery' in PLUGINS %}discoveryuploads{% endif %}",  # noqa: E501
    },
    "unique": {
        "AWS_SECRET_ACCESS_KEY": "{{ 24|random_string }}",
    },
    "overrides": {
        "OPENEDX_AWS_ACCESS_KEY": "openedx",
        "OPENEDX_AWS_SECRET_ACCESS_KEY": "{{ MINIO_AWS_SECRET_ACCESS_KEY }}",
    },
}

# Add configuration entries
tutor_hooks.Filters.CONFIG_DEFAULTS.add_items(
    [(f"MINIO_{key}", value) for key, value in config.get("defaults", {}).items()]
)
tutor_hooks.Filters.CONFIG_UNIQUE.add_items(
    [(f"MINIO_{key}", value) for key, value in config.get("unique", {}).items()]
)
tutor_hooks.Filters.CONFIG_OVERRIDES.add_items(
    list(config.get("overrides", {}).items())
)


@tutor_hooks.Filters.APP_PUBLIC_HOSTS.add()
def add_minio_hosts(
    hosts: list[str], context_name: t.Literal["local", "dev"]
) -> list[str]:
    if context_name == "dev":
        hosts.append("{{ MINIO_CONSOLE_HOST }}:9001")
    else:
        hosts.append("{{ MINIO_CONSOLE_HOST }}")
    return hosts


# Add pre-init script as init task with high priority
with open(
    os.path.join(HERE, "templates", "minio", "tasks", "minio", "init.sh"),
    encoding="utf-8",
) as fi:
    tutor_hooks.Filters.CLI_DO_INIT_TASKS.add_item(
        ("minio", fi.read()), priority=tutor_hooks.priorities.HIGH
    )

# Add the "templates" folder as a template root
tutor_hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(
    str(importlib_resources.files("tutorminio") / "templates")
)
# Render the "build" and "apps" folders
tutor_hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    [
        ("minio/build", "plugins"),
        ("minio/apps", "plugins"),
    ],
)
# Load patches from files
for path in glob(str(importlib_resources.files("tutorminio") / "patches" / "*")):
    with open(path, encoding="utf-8") as patch_file:
        tutor_hooks.Filters.ENV_PATCHES.add_item(
            (os.path.basename(path), patch_file.read())
        )
