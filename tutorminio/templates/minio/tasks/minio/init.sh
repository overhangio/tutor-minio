#!/bin/sh
set -e

export GARAGE_RPC_SECRET="{{ MINIO_RPC_SECRET | to_hex }}"

# Determine the node ID.
#
# Local/docker-compose: the job container mounts the same metadata volume
# (read-only) as the garage service, so `garage node id` reads the private key
# from disk — no network call needed.
#
# Kubernetes: the metadata PVC is ReadWriteOnce and cannot be mounted in the
# job pod while the garage pod holds it, so we query the admin API instead.
if garage node id -q > /dev/null 2>&1; then
    NODE_ID=$(garage node id -q | cut -d'@' -f1)
else
    echo "Metadata volume not available; querying Garage admin API for node ID..."
    until wget -qO /dev/null \
          --header "Authorization: Bearer $GARAGE_RPC_SECRET" \
          "http://garage:3903/v2/GetClusterStatus" 2>/dev/null; do
        echo "Waiting for Garage admin API..."
        sleep 2
    done
    # The node ID is a unique 64-character hex string in the response JSON.
    NODE_ID=$(wget -qO- \
        --header "Authorization: Bearer $GARAGE_RPC_SECRET" \
        "http://garage:3903/v2/GetClusterStatus" \
        | grep -o '[0-9a-f]\{64\}' | head -1)
fi
echo "Garage node ID: ${NODE_ID}"

# Point the garage CLI at the running daemon over RPC.
export GARAGE_RPC_HOST="${NODE_ID}@garage:3901"

echo "Waiting for Garage cluster to be ready..."
until garage status > /dev/null 2>&1; do sleep 2; done
echo "Garage is ready."

# Assign storage capacity to this node and apply layout.
# On subsequent init runs this is a no-op because layout is already active —
# the apply will fail (version already used) but we ignore that.
garage layout assign -z dc1 -c 1G "${NODE_ID}" 2>/dev/null || true
garage layout apply --version 1 2>/dev/null || true

# Import the Tutor-configured S3 key so Open edX credentials remain unchanged.
# Idempotent: skip if a key with this ID already exists.
garage key info {{ OPENEDX_AWS_ACCESS_KEY }} > /dev/null 2>&1 || \
    garage key import {{ OPENEDX_AWS_ACCESS_KEY }} {{ OPENEDX_AWS_SECRET_ACCESS_KEY }} -n tutor-key --yes

# Create buckets and grant full access to the imported key.
for bucket in \
    {{ MINIO_BUCKET_NAME }} \
    {{ MINIO_FILE_UPLOAD_BUCKET_NAME }} \
    {{ MINIO_VIDEO_UPLOAD_BUCKET_NAME }} \
    {{ MINIO_GRADES_BUCKET_NAME }} \
    {{ MINIO_OPENEDX_LEARNING_BUCKET_NAME }}; do
    garage bucket create "${bucket}" 2>/dev/null || true
    garage bucket allow --read --write --owner --key tutor-key "${bucket}"
done

{% if MINIO_DISCOVERY_BUCKET_NAME %}
garage bucket create {{ MINIO_DISCOVERY_BUCKET_NAME }} 2>/dev/null || true
garage bucket allow --read --write --owner --key tutor-key {{ MINIO_DISCOVERY_BUCKET_NAME }}
{% endif %}

# Enable website (public read) access for buckets that Open edX serves publicly.
garage bucket website --allow {{ MINIO_BUCKET_NAME }}
{% if MINIO_DISCOVERY_BUCKET_NAME %}
garage bucket website --allow {{ MINIO_DISCOVERY_BUCKET_NAME }}
{% endif %}
