#!/usr/bin/env bash
# Run every marketing validation demo and write reports under reports/.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p reports

QTMESH="${QTMESH:-qtmesh}"
if ! command -v "$QTMESH" >/dev/null 2>&1; then
  echo "qtmesh not found on PATH. Install QtMeshEditor or set QTMESH=/path/to/qtmesh" >&2
  exit 127
fi

banner() {
  printf '\n════════════════════════════════════════════════════════════\n'
  printf '  %s\n' "$1"
  printf '════════════════════════════════════════════════════════════\n'
}

run_scan() {
  local name="$1"
  shift
  banner "$name"
  set +e
  "$QTMESH" scan "$@"
  local rc=$?
  set -e
  echo "(exit $rc)"
  return 0
}

banner "1) Geometry validate — single-file gate"
for f in assets/good/crate_clean.glb assets/issues/mesh_degenerate_slivers.glb; do
  echo "--- validate $f ---"
  set +e
  "$QTMESH" validate "$f" --json | tee "reports/validate_$(basename "$f" .glb).json"
  echo "(exit $?)"
  set -e
done

run_scan "2) Good assets only (expect green)" \
  --config configs/good-only.yml \
  --report reports/good-only.json \
  --no-upload

run_scan "3) Full campaign scan — mobile budgets (expect findings)" \
  --config configs/mobile-campaign.yml \
  --report reports/mobile-campaign.json \
  --sarif reports/mobile-campaign.sarif \
  --no-upload

run_scan "4) WebGL profile comparison" \
  --config configs/webgl-campaign.yml \
  --report reports/webgl-campaign.json \
  --no-upload

run_scan "5) Built-in platform profiles showcase" \
  assets/issues --profile mobile-low --include "*.glb" --report reports/profile-mobile-low.json --no-upload

run_scan "6) Same issues under modern-console (looser)" \
  assets/issues --profile modern-console --include "*.glb" --report reports/profile-console.json --no-upload

banner "7) Memory / VRAM budget demo"
for f in assets/good/crate_clean.glb assets/issues/texture_oversized/texture_oversized.gltf assets/issues/prop_overbudget.glb; do
  echo "--- memory $f ---"
  set +e
  base="$(basename "$f")"
  base="${base%.*}"
  "$QTMESH" memory "$f" --json --no-cloud | tee "reports/memory_${base}.json"
  set -e
done

banner "8) Info cards for marketing screenshots"
"$QTMESH" info assets/good/crate_clean.glb --json | tee reports/info_crate_clean.json
"$QTMESH" info assets/issues/prop_overbudget.glb --json | tee reports/info_prop_overbudget.json

banner "9) Roblox MeshPart vs accessory"
bash scripts/demo_roblox.sh

banner "Done"
echo "Reports written to $ROOT/reports/"
echo "Tip: open https://qtmesh.dev and upload reports/mobile-campaign.json (or set QTMESH_CLOUD_TOKEN) to show Cloud history."
