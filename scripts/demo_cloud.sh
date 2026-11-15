#!/usr/bin/env bash
# QtMesh Cloud demo — login status, local scan upload, optional project upload.
# Safe to run without a token: scans stay local with --no-upload.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p reports
QTMESH="${QTMESH:-qtmesh}"

echo "══ Cloud session ══"
"$QTMESH" cloud status --json || true

if [[ -n "${QTMESH_CLOUD_TOKEN:-}${QTMESH_TOKEN:-}" ]]; then
  echo
  echo "══ Scan + upload to QtMesh Cloud (token detected) ══"
  "$QTMESH" scan --config configs/mobile-campaign.yml \
    --report reports/cloud-upload-scan.json \
    --strict-upload || true
  echo
  echo "Open https://qtmesh.dev to review scan history, quality score, and README badges."
else
  echo
  echo "No QTMESH_CLOUD_TOKEN / QTMESH_TOKEN set — running local-only scan."
  echo "Sign up at https://qtmesh.dev, create a project token, then:"
  echo "  export QTMESH_CLOUD_TOKEN=qtm_…"
  echo "  ./scripts/demo_cloud.sh"
  "$QTMESH" scan --config configs/mobile-campaign.yml \
    --report reports/cloud-local-scan.json \
    --no-upload || true
fi

echo
echo "══ Optional: package + upload a single good asset ══"
echo "  qtmesh cloud login"
echo "  qtmesh cloud upload assets/good/crate_clean.glb --name demo-crate-clean"
echo "  qtmesh cloud list --json"
