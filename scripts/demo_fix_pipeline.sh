#!/usr/bin/env bash
# Before → fix → after story for marketing (auto-fix + dry-run).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p reports/fix-pipeline
QTMESH="${QTMESH:-qtmesh}"

SRC="assets/issues/mesh_degenerate_slivers.glb"
WORKDIR="reports/fix-pipeline"
cp "$SRC" "$WORKDIR/before.glb"

echo "══ Before: validate + scan ══"
"$QTMESH" validate "$WORKDIR/before.glb" --json | tee "$WORKDIR/before_validate.json" || true
"$QTMESH" scan "$WORKDIR" --include "before.glb" \
  --config configs/mobile-campaign.yml \
  --report "$WORKDIR/before_scan.json" --no-upload || true

echo
echo "══ Dry-run: what --fix would change ══"
"$QTMESH" scan "$WORKDIR" --include "before.glb" \
  --config configs/mobile-campaign.yml \
  --fix --dry-run --no-upload || true

echo
echo "══ Apply geometry fixes ══"
"$QTMESH" fix "$WORKDIR/before.glb" -o "$WORKDIR/after.glb" --all || \
  "$QTMESH" fix "$WORKDIR/before.glb" -o "$WORKDIR/after.glb" --remove-degenerates --weld-vertices

echo
echo "══ After: validate ══"
"$QTMESH" validate "$WORKDIR/after.glb" --json | tee "$WORKDIR/after_validate.json" || true
"$QTMESH" info "$WORKDIR/before.glb" --json | tee "$WORKDIR/before_info.json"
"$QTMESH" info "$WORKDIR/after.glb" --json | tee "$WORKDIR/after_info.json"

echo
echo "Fix pipeline artifacts in $WORKDIR/"
