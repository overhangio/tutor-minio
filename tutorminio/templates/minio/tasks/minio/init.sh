# Verify that `MINIO_GCS_APPLICATION_CREDENTIALS` and `MINIO_GCS_APPLICATION_ID` are defined if `MINIO_GATEWAY == "gcs"`
{% if MINIO_GATEWAY == "gcs" %}
  {% if not MINIO_GCS_APPLICATION_CREDENTIALS %}
    echo "⚠️  MINIO_GCS_APPLICATION_CREDENTIALS is not defined. It is required to when MINIO_GATEWAY is set to gcs."
    exit 1
  {% endif %}
  {% if not MINIO_GCS_APPLICATION_ID %}
    echo "⚠️  MINIO_GCS_APPLICATION_ID is not defined. It is required to when MINIO_GATEWAY is set to gcs."
    exit 1
  {% endif %}
{% endif %}

mc config host add minio http://minio:9000 {{ OPENEDX_AWS_ACCESS_KEY }} {{ OPENEDX_AWS_SECRET_ACCESS_KEY }} --api s3v4
mc mb --ignore-existing minio/{{ MINIO_BUCKET_NAME }} minio/{{ MINIO_FILE_UPLOAD_BUCKET_NAME }} minio/{{ MINIO_VIDEO_UPLOAD_BUCKET_NAME }} minio/{{ MINIO_GRADES_BUCKET_NAME }}

BUCKETS=(
    "{{ MINIO_BUCKET_NAME }}"
    "{{ MINIO_FILE_UPLOAD_BUCKET_NAME }}"
    "{{ MINIO_VIDEO_UPLOAD_BUCKET_NAME }}"
)

for BUCKET in "${BUCKETS[@]}"; do
    if mc ls minio/ | grep -q "${BUCKET}/$"; then
        echo "Bucket ${BUCKET} already exists!"
    else
        mc mb minio/${BUCKET}
    fi
done

{% if MINIO_GATEWAY == "azure" %}
echo "⚠️  It is your responsibility to grant public read access rights to the '{{ MINIO_BUCKET_NAME }}' bucket on Azure."
{% elif MINIO_GATEWAY == "gcs" %}
echo "⚠️  It is your responsibility to grant public read access rights to the '{{ MINIO_BUCKET_NAME }}' bucket on GCS."
{% else %}
# Make common file upload bucket public (e.g: for forum image upload)
mc policy set public minio/{{ MINIO_BUCKET_NAME }}
{% endif %}
