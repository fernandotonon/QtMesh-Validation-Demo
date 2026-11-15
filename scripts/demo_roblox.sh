#!/usr/bin/env bash
# Roblox upload-limit demos — MeshPart (≤20k) vs accessory (≤4k), textures ≤1024.
# Always pass --config so these rules win over the repo-root qtmesh.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p reports/roblox
QTMESH="${QTMESH:-qtmesh}"

banner() {
  printf '\n════════════════════════════════════════════════════════════\n'
  printf '  %s\n' "$1"
  printf '════════════════════════════════════════════════════════════\n'
}

banner "Roblox limits (Studio upload)"
cat <<'EOF'
  MeshPart / static mesh : ≤ 20,000 triangles, textures ≤ 1024 px
  Accessory / clothing   : ≤  4,000 triangles, textures ≤ 1024 px
  Generate inside the limit with:
    qtmesh generate3d img.png -o out.glb --game-preset roblox-meshpart
    qtmesh generate3d img.png -o out.glb --game-preset roblox-accessory
EOF

banner "1) Asset triangle cards"
for f in \
  assets/roblox/good/accessory_hat_ok.glb \
  assets/roblox/good/meshpart_crate_ok.glb \
  assets/roblox/issues/prop_fails_accessory.glb \
  assets/roblox/issues/prop_over_meshpart.glb
do
  echo "--- $f ---"
  "$QTMESH" info "$f" 2>&1 | sed -n '1,8p'
done

banner "2) Good Roblox assets under MeshPart (expect pass)"
set +e
"$QTMESH" scan assets/roblox/good \
  --config configs/roblox-meshpart.yml \
  --report reports/roblox/good-meshpart.json --no-upload
echo "(exit $?)"
set -e

banner "3) Same good assets under accessory (expect pass)"
set +e
"$QTMESH" scan assets/roblox/good \
  --config configs/roblox-accessory.yml \
  --report reports/roblox/good-accessory.json --no-upload
echo "(exit $?)"
set -e

banner "4) Headline: fails accessory (4k), passes MeshPart (20k)"
ASSET=assets/roblox/issues/prop_fails_accessory.glb
echo "Asset: $ASSET (~8k tris)"
set +e
echo "── accessory (≤4k) — expect FAIL ──"
"$QTMESH" scan "$(dirname "$ASSET")" --include "$(basename "$ASSET")" \
  --config configs/roblox-accessory.yml \
  --report reports/roblox/fails-accessory.json --no-upload
echo "(exit $?)"
echo "── MeshPart (≤20k) — expect PASS ──"
"$QTMESH" scan "$(dirname "$ASSET")" --include "$(basename "$ASSET")" \
  --config configs/roblox-meshpart.yml \
  --report reports/roblox/passes-meshpart.json --no-upload
echo "(exit $?)"
set -e

banner "5) Over MeshPart ceiling (~25k tris) — expect FAIL"
set +e
"$QTMESH" scan assets/roblox/issues --include "prop_over_meshpart.glb" \
  --config configs/roblox-meshpart.yml \
  --report reports/roblox/over-meshpart.json --no-upload
echo "(exit $?)"
set -e

banner "6) Texture over 1024 (both gates) — expect WARN/FAIL on resolution"
set +e
"$QTMESH" scan assets/roblox/issues/texture_over_1024 \
  --config configs/roblox-meshpart.yml \
  --report reports/roblox/texture-over-1024.json --no-upload
echo "(exit $?)"
set -e

banner "7) Full Roblox tree — MeshPart then accessory"
set +e
"$QTMESH" scan --config configs/roblox-meshpart.yml \
  --report reports/roblox/full-meshpart.json --no-upload
echo "(exit $?)"
"$QTMESH" scan --config configs/roblox-accessory.yml \
  --report reports/roblox/full-accessory.json --no-upload
echo "(exit $?)"
set -e

banner "Done"
echo "Reports in reports/roblox/"
echo "Presenter tip: show prop_fails_accessory under accessory (red) then MeshPart (green)."
