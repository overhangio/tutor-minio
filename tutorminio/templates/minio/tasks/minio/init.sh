mc config host add minio http://minio:9000 {{ OPENEDX_AWS_ACCESS_KEY }} {{ OPENEDX_AWS_SECRET_ACCESS_KEY }} --api s3v4
mc mb --ignore-existing minio/{{ MINIO_BUCKET_NAME }} minio/{{ MINIO_FILE_UPLOAD_BUCKET_NAME }} minio/{{ MINIO_VIDEO_UPLOAD_BUCKET_NAME }}

# Make common file upload bucket public (e.g: for forum image upload)
mc policy set public minio/{{ MINIO_BUCKET_NAME }}