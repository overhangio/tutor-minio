Object storage for Open edX with `MinIO <https://www.minio.io/>`_
=================================================================

This is a plugin for `Tutor <https://docs.tutor.overhang.io>`_ that provides S3-like object storage for Open edX platforms. It's S3, but without the dependency on AWS. This is achieved thanks to `MinIO <https://www.minio.io/>`_, an open source project that provides object storage with an API compatible with S3.

In particular, this plugin is essential for `Kubernetes deployment <https://docs.tutor.overhang.io/k8s.html>`_.

Installation
------------

The plugin is currently bundled with the `binary releases of Tutor <https://github.com/overhangio/tutor/releases>`_. If you have installed Tutor from source, you will have to install this plugin from source, too::

    pip install tutor-minio

Then, to enable this plugin, run::

    tutor plugins enable minio

Configuration
-------------

- ``MINIO_BUCKET_NAME`` (default: ``"openedx"``)
- ``MINIO_FILE_UPLOAD_BUCKET_NAME`` (default: ``"openedxuploads"``)
- ``MINIO_HOST`` (default: ``"minio.{{ LMS_HOST }}"``)
- ``MINIO_DOCKER_IMAGE`` (default: ``"{{ DOCKER_REGISTRY }}overhangio/minio:{{ MINIO_VERSION }}"``)

These values can be modified with ``tutor config save --set PARAM_NAME=VALUE`` commands.

DNS records
-----------

It is assumed that the ``MINIO_HOST`` DNS record points to your server. When running MinIO on your laptop, MinIO will be available at http://minio.local.overhang.io. In development mode, the MinIO interface will be available at http://minio.local.overhang.io:9000.

Web UI
------

The MinIO web UI can be accessed at http://<MINIO_HOST>. The credentials for accessing the UI can be obtained with::

  tutor config printvalue OPENEDX_AWS_ACCESS_KEY
  tutor config printvalue OPENEDX_AWS_SECRET_ACCESS_KEY
