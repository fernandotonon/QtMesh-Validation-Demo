#!/usr/bin/env bash
# Show how the SAME assets pass/fail under different platform profiles.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p reports/profiles
QTMESH="${QTMESH:-qtmesh}"

ASSET="assets/issues/prop_overbudget.glb"
PROFILES=(ps1 n64 mobile-low webgl steamdeck modern-console vr)

echo "Comparing triangle budgets for: $ASSET"
"$QTMESH" info "$ASSET" --json | tee reports/profiles/asset_info.json

for p in "${PROFILES[@]}"; do
  echo
  echo "── profile: $p ──"
  set +e
  "$QTMESH" scan "$(dirname "$ASSET")" \
    --include "$(basename "$ASSET")" \
    --profile "$p" \
    --report "reports/profiles/${p}.json" \
    --json --no-upload
  echo "exit=$?"
  set -e
done

echo
echo "Profile reports in reports/profiles/"
echo "List built-in profiles with: qtmesh scan --list-profiles"
