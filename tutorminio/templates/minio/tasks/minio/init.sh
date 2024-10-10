mc config host add minio http://minio:9000 {{ OPENEDX_AWS_ACCESS_KEY }} {{ OPENEDX_AWS_SECRET_ACCESS_KEY }} --api s3v4
mc mb --ignore-existing minio/{{ MINIO_BUCKET_NAME }} minio/{{ MINIO_FILE_UPLOAD_BUCKET_NAME }} minio/{{ MINIO_VIDEO_UPLOAD_BUCKET_NAME }} minio/{{ MINIO_GRADES_BUCKET_NAME }} minio/{{ MINIO_OPENEDX_LEARNING_BUCKET_NAME }}

{% if MINIO_GATEWAY != "azure" %}
# Make common file upload bucket public (e.g: for forum image upload)
mc policy set public minio/{{ MINIO_BUCKET_NAME }}
{% else %}
echo "⚠️  It is your responsibility to grant public read access rights to the '{{ MINIO_BUCKET_NAME }}' bucket on Azure."
{% endif %}

# discovery bucket
{% if MINIO_DISCOVERY_BUCKET_NAME %}
mc mb --ignore-existing minio/{{ MINIO_DISCOVERY_BUCKET_NAME }}
{% if MINIO_GATEWAY != "azure" %}
# Make discovery media upload bucket public
mc policy set public minio/{{ MINIO_DISCOVERY_BUCKET_NAME }}
{% else %}
echo "⚠️  It is your responsibility to grant public read access rights to the '{{ MINIO_DISCOVERY_BUCKET_NAME }}' bucket on Azure."
{% endif %}
{% endif %}
