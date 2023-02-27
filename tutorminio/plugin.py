import os
from glob import glob

import pkg_resources

from tutor import hooks as tutor_hooks

from .__about__ import __version__

HERE = os.path.abspath(os.path.dirname(__file__))


tutor_hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        ("MINIO_VERSION", __version__),
        ("MINIO_BUCKET_NAME", "openedx"),
        ("MINIO_FILE_UPLOAD_BUCKET_NAME", "openedxuploads"),
        ("MINIO_VIDEO_UPLOAD_BUCKET_NAME", "openedxvideos"),
        ("MINIO_HOST", "files.{{ LMS_HOST }}"),
        ("MINIO_CONSOLE_HOST", "minio.{{ LMS_HOST }}"),
        # https://hub.docker.com/r/minio/minio/tags
        # https://hub.docker.com/r/minio/mc/tags
        # We must stick to these older releases because they are the last ones that support gateway mode to Azure:
        # https://blog.min.io/deprecation-of-the-minio-gateway/
        # https://min.io/docs/minio/linux/operations/install-deploy-manage/migrate-fs-gateway.html
        (
            "MINIO_DOCKER_IMAGE",
            "docker.io/minio/minio:RELEASE.2022-03-26T06-49-28Z.hotfix.26ec6a857",
        ),
        ("MINIO_MC_DOCKER_IMAGE", "docker.io/minio/mc:RELEASE.2022-03-31T04-55-30Z"),
        ("MINIO_GATEWAY", None),
    ]
)

tutor_hooks.Filters.CONFIG_UNIQUE.add_items(
    [
        ("MINIO_AWS_SECRET_ACCESS_KEY", "{{ 24|random_string }}"),
    ]
)
tutor_hooks.Filters.CONFIG_OVERRIDES.add_items(
    [
        ("OPENEDX_AWS_ACCESS_KEY", "openedx"),
        ("OPENEDX_AWS_SECRET_ACCESS_KEY", "{{ MINIO_AWS_SECRET_ACCESS_KEY }}"),
    ]
)

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
        tutor_hooks.Filters.ENV_PATCHES.add_item(
            (os.path.basename(path), patch_file.read())
        )
