#!/usr/bin/env bash
# Run the mobile campaign scan via the official QtMesh Docker image (no local install).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="${QTMESH_IMAGE:-ghcr.io/fernandotonon/qtmesh:latest}"

mkdir -p "$ROOT/reports"

UPLOAD_FLAGS=(--no-upload)
if [[ -n "${QTMESH_CLOUD_TOKEN:-}" ]]; then
  UPLOAD_FLAGS=()
fi

docker run --rm \
  -v "$ROOT:/workspace" \
  -w /workspace \
  -e QTMESH_CLOUD_TOKEN="${QTMESH_CLOUD_TOKEN:-}" \
  "$IMAGE" \
  scan --config configs/mobile-campaign.yml \
       --report reports/docker-mobile.json \
       "${UPLOAD_FLAGS[@]}"
