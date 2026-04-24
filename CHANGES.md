# CHANGES — `feat/replace-minio-with-rustfs`

> ## ⚠️  ALPHA — NOT FOR PRODUCTION
>
> **RustFS is currently at v1.0.0-alpha.** This branch exists as a
> preview so that this plugin is ready to adopt RustFS the moment a
> stable release is cut. Do **not** place real course data on a RustFS
> deployment today. If you need a production-ready MinIO alternative
> right now, use the sibling `feat/replace-minio-with-garage` branch.
>
> Track upstream at <https://github.com/rustfs/rustfs>.

## Summary

MinIO has been archived upstream. This branch replaces the MinIO
server with [RustFS](https://github.com/rustfs/rustfs), a Rust
re-implementation of the MinIO S3 API. RustFS is the most direct drop-
in of the three alternatives we evaluated: same ports (9000 S3 / 9001
console), same `mc` client tooling, same bucket policy semantics.

## What changed

- **Docker image**
  - `MINIO_DOCKER_IMAGE` is superseded by `RUSTFS_DOCKER_IMAGE`
    (`rustfs/rustfs:latest` — pinned to `latest` for the alpha period).
    The old name is kept as a deprecated alias pointing at the same
    image.
  - `MINIO_MC_DOCKER_IMAGE` is **unchanged** — still
    `docker.io/minio/mc:RELEASE.2022-03-31T04-55-30Z`. RustFS is wire-
    compatible with `mc`, so we keep using the MinIO Client image for
    init jobs.
- **Ports** — unchanged from MinIO. `:9000` S3, `:9001` console.
  `AWS_S3_ENDPOINT_URL` and Caddy routes did not change.
- **New config variables**
  - `RUSTFS_DOCKER_IMAGE`
  - `RUSTFS_UID` (default `10001`), `RUSTFS_GID` (default `10001`) —
    the non-root user inside the RustFS container. Exposed as config
    so operators can override if their host's user namespace maps
    differently (e.g. rootless Docker).
- **Environment variables** in the server container changed from
  MinIO's `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` to RustFS's
  `RUSTFS_ACCESS_KEY` / `RUSTFS_SECRET_KEY`, plus `RUSTFS_VOLUMES`,
  `RUSTFS_ADDRESS`, `RUSTFS_CONSOLE_ENABLE`, `RUSTFS_CONSOLE_ADDRESS`.
  These values are sourced from the existing `OPENEDX_AWS_ACCESS_KEY`
  / `OPENEDX_AWS_SECRET_ACCESS_KEY` keys so Open edX needs no change.
- **Non-root process**
  - Compose service has `user: "10001:10001"`. On a fresh bind mount,
    Docker creates the host directory with the invoking user's UID,
    which may not be 10001. If you hit `EACCES` on /data, run
    `sudo chown -R 10001:10001 $(tutor config printroot)/data/minio`.
  - K8s Deployment sets `securityContext.runAsUser` / `runAsGroup` /
    `fsGroup` to 10001, which makes the PVC owner match on mount.
- **Removed/deprecated**
  - `MINIO_GATEWAY` — RustFS has no gateway mode. Still accepted for
    backwards-compat; setting it is a no-op with a warning from
    `init.sh`.
- **Init script** (`tasks/minio/init.sh`) — near-identical to the
  MinIO version. The `mc` alias was renamed from `minio` to `rustfs`
  and points at `http://rustfs:9000`. Bucket creation and
  `mc policy set public` use the same commands as before.
- **Service naming**
  - `minio` service is renamed to `rustfs` in compose and k8s.
  - `minio-job` is preserved as the init job service name so existing
    `CLI_DO_INIT_TASKS` entries targeting `"minio"` keep resolving.
  - LMS/CMS dependency patches now declare a dep on `rustfs`.

## Why

RustFS is the most attractive future home for this plugin once it
stabilises — it matches MinIO's API surface almost exactly, so there
is close to zero adapter code. Shipping this branch now lets us (a)
exercise the plumbing, (b) report back any incompatibilities upstream,
and (c) flip users over quickly when a stable release appears.

## Migration notes

Because RustFS uses the same S3 wire format and the same `mc` tooling,
a migration from MinIO is in principle straightforward:

1. Stop MinIO.
2. Decide whether to keep the existing data volume. The v1.0.0-alpha
   on-disk format is NOT guaranteed stable across RustFS releases, so
   exporting your objects with `mc mirror` first is strongly advised.
3. Upgrade this plugin, re-run `tutor config save` and
   `tutor local do init`.
4. If you skipped the export, re-import with
   `mc mirror ./backup/<bucket>/ rustfs/<bucket>/` against the running
   RustFS instance.

If you previously set `MINIO_GATEWAY=s3` or `MINIO_GATEWAY=azure`,
unset it (`tutor config save --unset MINIO_GATEWAY`) and point Open
edX's `AWS_S3_ENDPOINT_URL` at your cloud provider directly.
