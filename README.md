# QtMesh Validation Demo

**Marketing & onboarding playground for [QtMesh](https://github.com/fernandotonon/QtMeshEditor) validations and [QtMesh Cloud](https://qtmesh.dev).**

Intentional *good* and *broken* 3D assets, ready-made scan configs, demo scripts, and CI pipelines — so teammates, prospects, and campaign screenshots can *see* what automated asset QA catches before a game ships.

---

## Why this repo exists

Game teams lose days to silent asset bugs: 180k-tri props on mobile, missing UVs, NPOT textures, broken material paths, draw-call explosions. QtMesh turns those into **CI failures and Cloud quality scores** with clear rule names.

This demo makes that value obvious in under five minutes:

```bash
make good      # green — ship-ready props
make issues    # red — each finding is a marketing story
make profiles  # same mesh, different platform budgets
```

---

## Quick start

**Requirements:** [QtMeshEditor](https://github.com/fernandotonon/QtMeshEditor) / `qtmesh` on your `PATH` (this repo was built against **3.69+**). Optional: Blender 4+/5+ to regenerate meshes, Docker for no-install scans.

```bash
git clone <this-repo> && cd QtMesh-Validation-Demo

# Run every demo → reports/*.json
./scripts/run_all_demos.sh
# or
make demos
```

No local install?

```bash
./pipelines/docker-scan.sh
```

---

## What’s inside

| Path | Purpose |
|---|---|
| `assets/good/` | Clean crate, barrel, character proxy — pass mobile budgets |
| `assets/issues/` | Overbudget / no-UVs / non-manifold / huge texture / NPOT / naming / missing textures |
| `assets/roblox/` | MeshPart (≤20k) vs accessory (≤4k) pass/fail demos + 1024 px texture gate |
| `configs/` | Campaign configs: mobile, WebGL, console, Roblox, good-only, character gate |
| `configs/profiles/` | Custom profiles: `roblox-meshpart.json`, `roblox-accessory.json` |
| `qtmesh.yml` | Root project rules (overrides Cloud when present) |
| `scripts/` | Runnable demos: all-scan, profiles, fix loop, cloud, character pipeline |
| `pipelines/` | Docker + GitLab examples |
| `.github/workflows/` | GitHub Actions scan + optional Cloud upload |
| `docs/` | Validation stories + pipeline deep-dive |

---

## Demo menu

| Command | Story |
|---|---|
| `make good` | Green badge / “assets ready” screenshot |
| `make issues` | Full finding list under mobile budgets |
| `make profiles` | PS1 → modern-console budget comparison |
| `make fix` | Before → dry-run → `qtmesh fix` → after |
| `make cloud` | Local scan, or upload when `QTMESH_CLOUD_TOKEN` is set |
| `make character` | Documented generate → rig → anim → validate gate |
| `make roblox` | MeshPart ≤20k vs accessory ≤4k — same prop, two gates |
| `make docker` | Same scan via `ghcr.io/fernandotonon/qtmesh` |

Details for each intentional failure: [`docs/validation-stories.md`](docs/validation-stories.md) · Roblox: [`docs/roblox.md`](docs/roblox.md).

---

## QtMesh Cloud (badges & history)

1. Sign in at [qtmesh.dev](https://qtmesh.dev) and create a project  
2. Create an ingest token → GitHub secret `QTMESH_CLOUD_TOKEN`  
3. Push to `main` or run **QtMesh Cloud Upload** workflow  
4. Paste Cloud README badges (status / score / errors / warnings)

```bash
export QTMESH_CLOUD_TOKEN=qtm_…
./scripts/demo_cloud.sh
```

Local `qtmesh.yml` always wins over Cloud-hosted rules — keep campaign configs in-repo for reproducible demos.

---

## Example: one finding

```bash
qtmesh info assets/issues/prop_overbudget.glb
# Triangles: 184320

qtmesh scan assets/issues --include "prop_overbudget.glb" --profile mobile-low
# → fails max_triangle_count (mobile-low budget: 25 000)
```

## Example: Roblox poly limits

```bash
make roblox

# Headline marketing beat — mid-poly prop (~8k tris):
qtmesh scan assets/roblox/issues --include prop_fails_accessory.glb \
  --config configs/roblox-accessory.yml   # FAIL (≤4k)
qtmesh scan assets/roblox/issues --include prop_fails_accessory.glb \
  --config configs/roblox-meshpart.yml    # PASS (≤20k)
```

Fix path for geometry hygiene demos:

```bash
./scripts/demo_fix_pipeline.sh
```

---

## Example pipelines

See [`docs/pipelines.md`](docs/pipelines.md) for:

- Local artist workstation gates  
- GitHub Actions (`fernandotonon/QtMeshEditor@v1`)  
- GitLab CI + Docker  
- Character AI pipeline → validation before engine import  

---

## Regenerate demo meshes

```bash
make assets
# blender --background --python scripts/generate_demo_assets.py
```

---

## Links

- QtMeshEditor: https://github.com/fernandotonon/QtMeshEditor  
- QtMesh Cloud: https://qtmesh.dev  
- CLI: `qtmesh scan --list-profiles` · `qtmesh validate <file>` · `qtmesh cloud status`
