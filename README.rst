Object storage for Open edX with `RustFS <https://github.com/rustfs/rustfs>`_
=============================================================================

.. warning::

    **ALPHA — NOT FOR PRODUCTION USE.**

    RustFS is currently at **v1.0.0-alpha**. This branch exists as a
    preview so that the ``tutor-minio`` plugin is ready to adopt RustFS
    the moment a stable release is cut. Do **not** place real course
    data on a RustFS deployment today — the on-disk format is not
    guaranteed stable across alpha releases, and upstream may still
    change the API.

    If you need a production-ready MinIO alternative **right now**, use
    the sibling ``feat/replace-minio-with-garage`` branch (Garage v1.0.1,
    stable) or the ``feat/replace-minio-with-seaweedfs`` branch
    (SeaweedFS, stable but operationally heavier).

    Track upstream progress at https://github.com/rustfs/rustfs.

This is a plugin for `Tutor <https://docs.tutor.edly.io>`_ that provides S3-like object storage for Open edX platforms. It's S3, but without the dependency on AWS. This is achieved thanks to `RustFS <https://github.com/rustfs/rustfs>`_, a Rust re-implementation of the MinIO S3 API.

In particular, this plugin is essential for `Kubernetes deployment <https://docs.tutor.edly.io/k8s.html>`_.

.. note::

    The plugin package is still named ``tutor-minio`` and still installs as the ``minio`` Tutor plugin, to preserve compatibility with downstream tooling and existing ``tutor config`` files. Under the hood the object store is now RustFS. See `CHANGES.md <CHANGES.md>`_ for the full migration notes.

Why RustFS (eventually)
-----------------------

Of the three candidate replacements for MinIO (Garage, SeaweedFS, RustFS), RustFS is the closest drop-in:

- Same ports: ``9000`` (S3 API), ``9001`` (web console).
- Same ``mc`` client tooling — the init script can keep using
  ``mc policy set public``, ``mc mb``, and ``mc mirror`` verbatim.
- Same bucket policy semantics (public / download / upload / etc.).
- Same memory-and-CPU shape at rest, so capacity planning carries over.

Meaning once RustFS goes stable, this plugin essentially becomes a
sed from ``minio/minio`` to ``rustfs/rustfs``. Until then: preview
only.

Installation
------------

::

    tutor plugins install minio
    tutor plugins enable minio

Configuration
-------------

Preserved from the MinIO era (drive the Open edX S3 settings):

- ``OPENEDX_AWS_ACCESS_KEY`` (default: ``"openedx"``)
- ``OPENEDX_AWS_SECRET_ACCESS_KEY`` (default: ``"{{ 24|random_string }}"``)
- ``MINIO_BUCKET_NAME`` (default: ``"openedx"``)
- ``MINIO_FILE_UPLOAD_BUCKET_NAME`` (default: ``"openedxuploads"``)
- ``MINIO_VIDEO_UPLOAD_BUCKET_NAME`` (default: ``"openedxvideos"``)
- ``MINIO_GRADES_BUCKET_NAME`` (default: ``"openedxgrades"``)
- ``MINIO_OPENEDX_LEARNING_BUCKET_NAME`` (default: ``"openedxlearning"``)
- ``MINIO_HOST`` (default: ``"files.{{ LMS_HOST }}"``)
- ``MINIO_CONSOLE_HOST`` (default: ``"minio.{{ LMS_HOST }}"``)

RustFS-specific settings:

- ``RUSTFS_DOCKER_IMAGE`` (default: ``"rustfs/rustfs:latest"``) — pinned to ``latest`` for the alpha period. Once upstream cuts a stable tag, override with a specific version.
- ``RUSTFS_UID`` / ``RUSTFS_GID`` (both default: ``10001``) — the non-root user inside the RustFS container.

Deprecated (kept as aliases):

- ``MINIO_DOCKER_IMAGE`` → now an alias for ``RUSTFS_DOCKER_IMAGE``.
- ``MINIO_GATEWAY`` — no-op under RustFS.

``MINIO_MC_DOCKER_IMAGE`` is unchanged; RustFS is ``mc``-compatible, so we keep using the MinIO Client image for init/admin jobs.

Non-root caveat
---------------

RustFS runs as UID ``10001``. On a fresh bind-mounted data volume in local mode, the host directory may be owned by a different UID and RustFS will fail to write. Fix with::

    sudo chown -R 10001:10001 $(tutor config printroot)/data/minio

In Kubernetes the ``fsGroup: 10001`` on the Deployment handles this automatically.

DNS records
-----------

It is assumed that the ``MINIO_HOST`` DNS record points to your server. When running RustFS on your laptop, the Web UI will be available at ``http://minio.local.openedx.io``. In development mode, the web console will be at ``http://minio.local.openedx.io:9001``.

Web UI
------

The RustFS web console can be accessed at ``http://<MINIO_CONSOLE_HOST>``. Credentials are the same as MinIO's root credentials::

    tutor config printvalue OPENEDX_AWS_ACCESS_KEY
    tutor config printvalue OPENEDX_AWS_SECRET_ACCESS_KEY

Migration notes
---------------

Because RustFS uses the same S3 wire format and the same ``mc`` tooling,
a migration from MinIO is straightforward:

1. Stop MinIO.
2. Decide whether to keep the existing data volume. The v1.0.0-alpha
   on-disk format is **not** guaranteed stable across RustFS releases, so
   exporting your objects with ``mc mirror`` first is strongly advised.
3. Upgrade this plugin, then re-run::

       tutor config save
       tutor local do init

4. If you skipped the export, re-import with the following command against
   the running RustFS instance::

       mc mirror ./backup/<bucket>/ rustfs/<bucket>/

Troubleshooting
---------------

This Tutor plugin is maintained by Abdul Rehman from `Edly <https://edly.io>`__. Community support is available from the official `Open edX forum <https://discuss.openedx.org>`__. Do you need help with this plugin? See the `troubleshooting <https://docs.tutor.edly.io/troubleshooting.html>`__ section from the Tutor documentation.

License
-------

This work is licensed under the terms of the `GNU Affero General Public License (AGPL) <https://github.com/overhangio/tutor-minio/blob/release/LICENSE.txt>`_.