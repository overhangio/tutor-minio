Object storage for Open edX with `Garage <https://garagehq.deuxfleurs.fr/>`_
==============================================================================

.. note::

   **MinIO → Garage migration (breaking change)**

   This plugin has replaced `MinIO <https://www.minio.io/>`_ with
   `Garage <https://garagehq.deuxfleurs.fr/>`_ as the S3-compatible storage
   backend. Open edX-side configuration (``MINIO_HOST``, bucket names,
   ``OPENEDX_AWS_SECRET_ACCESS_KEY``) is preserved; existing variable names
   keep the ``MINIO_`` prefix for backward compatibility.

   New / changed defaults:

   - ``MINIO_DOCKER_IMAGE`` now points to ``docker.io/dxflrs/garage:v2.3.0``
     (instead of the deprecated MinIO image).
   - ``MINIO_WEBUI_DOCKER_IMAGE`` (new) — points to
     ``docker.io/khairul169/garage-webui:1.1.0``; replaces the legacy MinIO
     console.
   - ``MINIO_JOB_DOCKER_IMAGE`` (new) — locally built alpine image bundling
     the ``garage`` CLI for cluster initialization.
   - ``MINIO_RPC_SECRET`` (new, auto-generated) — Garage cluster shared
     secret. Hashed to 32 bytes hex via the ``to_hex`` filter at render time.
   - ``OPENEDX_AWS_ACCESS_KEY`` default changed from ``openedx`` to
     ``openedxs3`` because Garage requires key IDs to be at least 8
     characters. **Existing installs that already have
     ``OPENEDX_AWS_ACCESS_KEY: openedx`` saved in ``config.yml`` must clear
     the line so the new default takes effect**::

         tutor config save --unset OPENEDX_AWS_ACCESS_KEY
         tutor config save

This is a plugin for `Tutor <https://docs.tutor.edly.io>`_ that provides
S3-like object storage for Open edX platforms. It's S3, but without the
dependency on AWS. This is achieved thanks to
`Garage <https://garagehq.deuxfleurs.fr/>`_, an open-source distributed
object storage system with an S3-compatible API.

In particular, this plugin is essential for
`Kubernetes deployment <https://docs.tutor.edly.io/k8s.html>`_.

Installation
------------

The plugin is currently bundled with the
`binary releases of Tutor <https://github.com/overhangio/tutor/releases>`_.
If you have installed Tutor from source, you will have to install this plugin
from source, too::

    tutor plugins install minio

Then, to enable this plugin, run::

    tutor plugins enable minio

The init job image is built automatically by ``tutor dev launch`` /
``tutor local launch``. To build it on demand::

    tutor images build garage-job

Configuration
-------------

- ``OPENEDX_AWS_ACCESS_KEY`` (default: ``"openedxs3"``)
- ``OPENEDX_AWS_SECRET_ACCESS_KEY`` (default: ``"{{ 24|random_string }}"``)
- ``MINIO_BUCKET_NAME`` (default: ``"openedx"``)
- ``MINIO_FILE_UPLOAD_BUCKET_NAME`` (default: ``"openedxuploads"``)
- ``MINIO_HOST`` (default: ``"files.{{ LMS_HOST }}"``)
- ``MINIO_CONSOLE_HOST`` (default: ``"minio.{{ LMS_HOST }}"``)
- ``MINIO_GRADES_BUCKET_NAME`` (default: ``"openedxgrades"``)
- ``MINIO_DOCKER_IMAGE`` (default: ``"docker.io/dxflrs/garage:v2.3.0"``)
- ``MINIO_WEBUI_DOCKER_IMAGE`` (default: ``"docker.io/khairul169/garage-webui:1.1.0"``)
- ``MINIO_JOB_DOCKER_IMAGE`` (default: ``"openedx-garage-job:{{ MINIO_VERSION }}"``)
- ``MINIO_RPC_SECRET`` (auto-generated 64-character random string, hashed to
  hex for Garage)

These values can be modified with ``tutor config save --set PARAM_NAME=VALUE``
commands.

DNS records
-----------

It is assumed that the ``MINIO_HOST`` DNS record points to your server. When
running Garage on your laptop, the S3 endpoint will be available at
http://files.local.openedx.io. In development mode, the S3 API is also
exposed on http://127.0.0.1:9000.

Web UI
------

The Garage web UI is accessible at:

- **Local/production mode**: ``http://<MINIO_CONSOLE_HOST>`` (proxied through
  Caddy)
- **Development mode**: ``http://<MINIO_CONSOLE_HOST>:3909``

It auto-reads the admin token from the mounted ``/etc/garage.toml``, so no
explicit login is required. Use the access key + secret to manage objects::

  tutor config printvalue OPENEDX_AWS_ACCESS_KEY
  tutor config printvalue OPENEDX_AWS_SECRET_ACCESS_KEY

Troubleshooting
---------------

This Tutor plugin is maintained by Abdul Rehman from `Edly <https://edly.io>`__.
Community support is available from the official
`Open edX forum <https://discuss.openedx.org>`__. Do you need help with this
plugin? See the
`troubleshooting <https://docs.tutor.edly.io/troubleshooting.html>`__ section
from the Tutor documentation.

License
-------

This work is licensed under the terms of the
`GNU Affero General Public License (AGPL) <https://github.com/overhangio/tutor-minio/blob/release/LICENSE.txt>`_.
