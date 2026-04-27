from __future__ import annotations

import hashlib
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
        # https://hub.docker.com/r/dxflrs/garage/tags
        "DOCKER_IMAGE": "docker.io/dxflrs/garage:v2.3.0",
        # https://hub.docker.com/r/khairul169/garage-webui/tags
        "WEBUI_DOCKER_IMAGE": "docker.io/khairul169/garage-webui:1.1.0",
        # Custom-built init job image: alpine + garage CLI
        "JOB_DOCKER_IMAGE": "openedx-garage-job:{{ MINIO_VERSION }}",
        "DISCOVERY_BUCKET_NAME": "{% if 'discovery' in PLUGINS %}discoveryuploads{% endif %}",  # noqa: E501
    },
    "unique": {
        "AWS_SECRET_ACCESS_KEY": "{{ 24|random_string }}",
        # Garage requires a 32-byte hex-encoded shared secret for inter-node
        # RPC and admin API auth. We generate a 64-char hex string (32 bytes).
        "RPC_SECRET": "{{ 64|random_string }}",
    },
    "overrides": {
        # Garage enforces a minimum key ID length of 8 chars (legacy MinIO had
        # no such requirement). "openedxs3" — 9 chars — is a stable, semantic
        # identifier that satisfies the constraint. CONFIG_OVERRIDES forces
        # this value on every render, so user-set values are ignored.
        "OPENEDX_AWS_ACCESS_KEY": "openedxs3",
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

# Garage requires its rpc_secret / admin_token to be exactly 32 bytes hex-encoded
# (64 hex chars). Tutor's built-in `random_string` filter produces alphanumeric
# strings, not hex — so we register a `to_hex` filter that derives a deterministic
# 64-char hex string from any input via SHA-256.
tutor_hooks.Filters.ENV_TEMPLATE_FILTERS.add_item(
    ("to_hex", lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()),
)


# Build the garage-job image (alpine + garage binary copied from the Garage image).
# This image is needed because the official Garage image is `scratch`-based and has
# no shell, but the init script needs a shell + awk + wget for cluster setup.
tutor_hooks.Filters.IMAGES_BUILD.add_item(
    (
        "garage-job",
        ("plugins", "minio", "build", "garage-job"),
        "{{ MINIO_JOB_DOCKER_IMAGE }}",
        (),
    )
)


# Auto-build the garage-job image during `tutor dev launch` / `tutor local launch`.
# Without this, the init task would fail because the job image doesn't exist yet.
@tutor_hooks.Filters.IMAGES_BUILD_REQUIRED.add()
def _build_garage_job_on_launch(
    image_names: list[str], context_name: t.Literal["local", "dev"]
) -> list[str]:
    image_names.append("garage-job")
    return image_names


@tutor_hooks.Filters.APP_PUBLIC_HOSTS.add()
def add_minio_hosts(
    hosts: list[str], context_name: t.Literal["local", "dev"]
) -> list[str]:
    if context_name == "dev":
        hosts.append("{{ MINIO_CONSOLE_HOST }}:3909")
    else:
        hosts.append("{{ MINIO_CONSOLE_HOST }}")
    return hosts


# Add pre-init script as init task with high priority. Service name "garage"
# means tutor will run the script in the docker-compose service "garage-job".
with open(
    os.path.join(HERE, "templates", "minio", "tasks", "minio", "init.sh"),
    encoding="utf-8",
) as fi:
    tutor_hooks.Filters.CLI_DO_INIT_TASKS.add_item(
        ("garage", fi.read()), priority=tutor_hooks.priorities.HIGH
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
