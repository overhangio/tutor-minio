# Build the Garage init job image: alpine shell + garage binary for cluster setup.
# The official Garage image is `scratch`-based and has no shell, but our init
# script needs sh + awk + wget for orchestration, so we layer the binary on alpine.
FROM {{ MINIO_DOCKER_IMAGE }} AS garage
FROM alpine:3.20
COPY --from=garage /garage /usr/local/bin/garage
