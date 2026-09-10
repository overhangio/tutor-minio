# RustFS is wire-compatible with the MinIO `mc` client, so the init
# script is nearly identical to the MinIO version — we just point `mc`
# at the `rustfs` service instead of `minio`. The alias name is local
# to `mc` and does not affect Open edX, which talks to RustFS over
# standard S3 via MINIO_HOST.
mc config host add rustfs http://rustfs:9000 {{ OPENEDX_AWS_ACCESS_KEY }} {{ OPENEDX_AWS_SECRET_ACCESS_KEY }} --api s3v4
mc mb --ignore-existing rustfs/{{ MINIO_BUCKET_NAME }} rustfs/{{ MINIO_FILE_UPLOAD_BUCKET_NAME }} rustfs/{{ MINIO_VIDEO_UPLOAD_BUCKET_NAME }} rustfs/{{ MINIO_GRADES_BUCKET_NAME }} rustfs/{{ MINIO_OPENEDX_LEARNING_BUCKET_NAME }}

# Make common file upload bucket public (e.g: for forum image upload).
# RustFS honours MinIO-style bucket policies, so `mc policy set public`
# works the same as before.
mc policy set public rustfs/{{ MINIO_BUCKET_NAME }}

# discovery bucket
{% if MINIO_DISCOVERY_BUCKET_NAME %}
mc mb --ignore-existing rustfs/{{ MINIO_DISCOVERY_BUCKET_NAME }}
mc policy set public rustfs/{{ MINIO_DISCOVERY_BUCKET_NAME }}
{% endif %}

{% if MINIO_GATEWAY %}
echo "⚠️  MINIO_GATEWAY={{ MINIO_GATEWAY }} is set but RustFS has no gateway mode; the value is being ignored. Remove it from tutor config to silence this notice. See CHANGES.md."
{% endif %}
