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

# -----------------------------------------------------------------------------
# RustFS replaces MinIO.
#
# RustFS is the most direct MinIO drop-in of the three alternatives we
# evaluated: same S3 API wire protocol, same default ports (9000 for the
# API, 9001 for the web console), and same `mc` (MinIO Client) tooling.
# Migrating from MinIO is mostly just "change the image tag + the root
# user/password env var names".
#
# ⚠️  ALPHA STATUS — READ BEFORE DEPLOYING
# ----------------------------------------
# RustFS is currently v1.0.0-alpha (as of 2025). It is NOT recommended
# for production. Use this branch only as a preview / test bed and
# monitor https://github.com/rustfs/rustfs for a stable release before
# placing real course data on it. If you need a production-ready
# MinIO alternative today, see the sibling `feat/replace-minio-with-garage`
# branch.
# -----------------------------------------------------------------------------

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
        # MINIO_GATEWAY is kept as a config key for backwards-compat,
        # but RustFS has no gateway mode. Setting it is a no-op and the
        # init script prints a warning.
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

# MINIO_-prefixed entries (historical convention preserved so existing
# tutor config files keep working)
tutor_hooks.Filters.CONFIG_DEFAULTS.add_items(
    [(f"MINIO_{key}", value) for key, value in config.get("defaults", {}).items()]
)
tutor_hooks.Filters.CONFIG_UNIQUE.add_items(
    [(f"MINIO_{key}", value) for key, value in config.get("unique", {}).items()]
)
tutor_hooks.Filters.CONFIG_OVERRIDES.add_items(
    list(config.get("overrides", {}).items())
)

# RustFS-specific config.
tutor_hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        # https://hub.docker.com/r/rustfs/rustfs/tags
        # Pinning to `latest` is deliberate for the alpha-preview phase;
        # once RustFS cuts a stable tag, replace this with a specific
        # version.
        ("RUSTFS_DOCKER_IMAGE", "rustfs/rustfs:latest"),
        # RustFS containers run as UID 10001 by default. We pass this
        # explicitly to the `user:` directive so `docker run --rm` and
        # one-shot commands don't accidentally run as root and leave
        # root-owned files in the data volume.
        ("RUSTFS_UID", 10001),
        ("RUSTFS_GID", 10001),
        # DEPRECATED aliases. Downstream plugins / config overrides
        # that still reference these keep working but now resolve to
        # the RustFS image. Removed in a future release.
        ("MINIO_DOCKER_IMAGE", "{{ RUSTFS_DOCKER_IMAGE }}"),
        # The `mc` client is a plain Go binary published separately; the
        # RustFS image does NOT ship `mc`, so we keep the MinIO mc image
        # for the init/admin job. This is intentional — RustFS is wire-
        # compatible with `mc`.
        ("MC_DOCKER_IMAGE", "docker.io/minio/mc:RELEASE.2022-03-31T04-55-30Z"),
    ]
)


@tutor_hooks.Filters.APP_PUBLIC_HOSTS.add()
def add_minio_hosts(
    hosts: list[str], context_name: t.Literal["local", "dev"]
) -> list[str]:
    # Same default port map as MinIO: console on 9001, S3 API on 9000.
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
