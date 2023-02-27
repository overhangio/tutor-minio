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

- ``OPENEDX_AWS_ACCESS_KEY`` (default: ``"openedx"``)
- ``OPENEDX_AWS_SECRET_ACCESS_KEY`` (default: ``"{{ 24|random_string }}"``)
- ``MINIO_BUCKET_NAME`` (default: ``"openedx"``)
- ``MINIO_FILE_UPLOAD_BUCKET_NAME`` (default: ``"openedxuploads"``)
- ``MINIO_HOST`` (default: ``"files.{{ LMS_HOST }}"``)
- ``MINIO_CONSOLE_HOST`` (default: ``"minio.{{ LMS_HOST }}"``)
- ``MINIO_DOCKER_IMAGE`` (default: ``"docker.io/minio/minio:RELEASE.2022-05-08T23-50-31Z"``)
- ``MINIO_MC_DOCKER_IMAGE`` (default: ``"docker.io/minio/mc:RELEASE.2022-05-09T04-08-26Z"``)

These values can be modified with ``tutor config save --set PARAM_NAME=VALUE`` commands.

- ``MINIO_GATEWAY`` (default: ``null``)

This feature allows your to run the MinIO server as a gateway to another object storage solution, such as `S3 <https://docs.minio.io/docs/minio-gateway-for-s3.html>`__ or `Azure <https://docs.minio.io/docs/minio-gateway-for-azure.html>`__. That way, static assets can be stored on these object storage backends without extensive changes to the Open edX runtime environment.

Note to Azure users: you will have to manually grant public access rights to the ``MINIO_BUCKET_NAME`` ("openedx") bucket.

DNS records
-----------

It is assumed that the ``MINIO_HOST`` DNS record points to your server. When running MinIO on your laptop, the MinIO Web UI will be available at http://minio.local.overhang.io. In development mode, the MinIO interface will be available at http://minio.local.overhang.io:9001.

Web UI
------

The MinIO web UI can be accessed at http://<MINIO_HOST>. The credentials for accessing the UI can be obtained with::

  tutor config printvalue OPENEDX_AWS_ACCESS_KEY
  tutor config printvalue OPENEDX_AWS_SECRET_ACCESS_KEY

Troubleshooting
---------------

This Tutor plugin is maintained by Régis Behmo from `Overhang.IO <https://overhang.io>`__. Community support is available from the official `Open edX forum <https://discuss.openedx.org>`__. Do you need help with this plugin? See the `troubleshooting <https://docs.tutor.overhang.io/troubleshooting.html>`__ section from the Tutor documentation.

License
-------

This work is licensed under the terms of the `GNU Affero General Public License (AGPL) <https://github.com/overhangio/tutor-minio/blob/master/LICENSE.txt>`_.
