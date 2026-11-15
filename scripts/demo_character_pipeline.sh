#!/usr/bin/env bash
# Example character pipeline gates (generate → rig → anim → validate).
# Does NOT run TRELLIS/UniRig/Kimodo by default (heavy models).
# Pass --run to execute a real qtmesh-character.sh generation when available.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p reports/character-pipeline assets/pipelines/character
QTMESH="${QTMESH:-qtmesh}"

CHARACTER_SH="${QTMESH_CHARACTER_SH:-$HOME/.claude/skills/qtmesh-character-pipeline/scripts/qtmesh-character.sh}"
OUT="assets/pipelines/character/demo_hero"

print_pipeline() {
  cat <<'EOF'
Example QtMesh character pipeline (best practices)
──────────────────────────────────────────────────
1. Generate (TRELLIS.2 balanced + BiRefNet matte)
   qtmesh generate3d concept.png -o 1_model.glb \
     --backend trellis2 --preset balanced --matting best \
     --target-tris 15000 --texture-size 2048 --seed 42 --json

2. Rig (UniRig — verify boneCount >> 19, no fallbackReason)
   QTMESH_ONNX_PREFER_GPU=0 qtmesh rig 1_model.glb \
     --algo unirig --skin -o 2_rig.glb --json > rig.json

3. Animate (NVIDIA Kimodo, one clip per command)
   qtmesh anim 2_rig.glb --generate "a hero standing idle, breathing" \
     --backend kimodo --duration 3 --no-root-motion --name idle -o 3_idle.glb
   qtmesh anim 2_rig.glb --generate "a hero walking forward at a steady pace" \
     --backend kimodo --duration 2 --no-root-motion --name walk -o 3_walk.glb

4. Merge + verify
   qtmesh anim 3_idle.glb --merge 3_walk.glb -o final.glb
   qtmesh turntable final.glb --animation walk --frames 8 -o previews/walk.png

5. Validate before engine import
   qtmesh validate final.glb --json
   qtmesh scan final.glb --config configs/character-pipeline.yml --fail-on error
   qtmesh memory final.glb --budget 64mb --no-cloud

Or one-shot:
   ~/.claude/skills/qtmesh-character-pipeline/scripts/qtmesh-character.sh \
     --image concept.png --name hero --out assets/pipelines/character/hero \
     --tris 15000 --texture 2048 --seed 42 \
     --clip "idle|3|a hero standing idle, breathing, shifting weight" \
     --clip "walk|2|a hero walking forward at a steady, upright pace"
EOF
}

print_pipeline | tee reports/character-pipeline/README.txt

echo
echo "══ Geometry gate on existing character proxy ══"
"$QTMESH" scan --config configs/character-pipeline.yml \
  --report reports/character-pipeline/proxy-scan.json --no-upload || true
"$QTMESH" validate assets/good/character_proxy_clean.glb --json \
  | tee reports/character-pipeline/proxy-validate.json || true

if [[ "${1:-}" == "--run" ]]; then
  if [[ ! -x "$CHARACTER_SH" && ! -f "$CHARACTER_SH" ]]; then
    echo "qtmesh-character.sh not found at $CHARACTER_SH" >&2
    exit 1
  fi
  echo
  echo "══ Running full character generation (--run) ══"
  bash "$CHARACTER_SH" \
    --prompt "stylized game hero in A-pose, full body, plain background" \
    --name demo_hero --out "$OUT" \
    --tris 15000 --texture 2048 --seed 42 \
    --clip "idle|3|a hero standing idle, breathing, shifting weight" \
    --clip "walk|2|a hero walking forward at a steady, upright pace"
  "$QTMESH" scan "$OUT" --config configs/character-pipeline.yml \
    --report reports/character-pipeline/generated-scan.json --no-upload || true
else
  echo
  echo "Dry documentation mode. Re-run with --run to generate a real character (needs AI models)."
fi
