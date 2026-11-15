# Example pipelines

This repo ships three pipeline shapes you can copy into a real game project.

## 1. Local gate (pre-commit / artist workstation)

```bash
# Fast geometry check on the file you just exported
qtmesh validate path/to/prop.glb

# Project rules from qtmesh.yml
qtmesh scan assets/ --fail-on error

# Memory / VRAM estimate
qtmesh memory path/to/prop.glb --budget 64mb --no-cloud
```

`make scan` / `make good` wrap the demo configs.

## 2. CI on every push (GitHub Actions)

Workflows:

- [`.github/workflows/qtmesh-scan.yml`](../.github/workflows/qtmesh-scan.yml) — scan + validate; good assets must pass
- [`.github/workflows/qtmesh-cloud.yml`](../.github/workflows/qtmesh-cloud.yml) — optional ingest to [qtmesh.dev](https://qtmesh.dev)

Required for Cloud badges:

1. Create a project at https://qtmesh.dev  
2. Create an ingest token  
3. Add GitHub secret `QTMESH_CLOUD_TOKEN`  
4. Push — scans appear in the Cloud dashboard with score + README badges  

Pinned action example:

```yaml
- uses: fernandotonon/QtMeshEditor@v1
  with:
    command: scan
    options: --config configs/mobile-campaign.yml
  env:
    QTMESH_CLOUD_TOKEN: ${{ secrets.QTMESH_CLOUD_TOKEN }}
```

## 3. Docker / GitLab / no-install runners

```bash
./pipelines/docker-scan.sh
```

GitLab: copy [`pipelines/gitlab-ci.yml`](../pipelines/gitlab-ci.yml) to `.gitlab-ci.yml` and set `QTMESH_CLOUD_TOKEN`.

## 4. Roblox MeshPart / accessory gate

```bash
make roblox
qtmesh scan --config configs/roblox-meshpart.yml --fail-on error
qtmesh scan --config configs/roblox-accessory.yml --fail-on error
```

Generate with the matching game preset so bake budgets match Studio upload limits:

```bash
qtmesh generate3d prop.png -o prop.glb --game-preset roblox-meshpart
qtmesh generate3d hat.png  -o hat.glb  --game-preset roblox-accessory
```

Details: [`roblox.md`](roblox.md).

## 5. Character production pipeline

Documented + gated by [`scripts/demo_character_pipeline.sh`](../scripts/demo_character_pipeline.sh) and [`configs/character-pipeline.yml`](../configs/character-pipeline.yml):

```
image/prompt → TRELLIS.2 → UniRig → Kimodo clips → merge → validate → engine
```

Use the `qtmesh-character-pipeline` skill / `qtmesh-character.sh` for the heavy AI steps, then **always** run `qtmesh scan` before Godot / Clayground / Roblox import.

## 6. Fix loop

[`scripts/demo_fix_pipeline.sh`](../scripts/demo_fix_pipeline.sh) shows the marketing “before → dry-run → fix → after” loop:

```bash
qtmesh scan … --fix --dry-run
qtmesh fix broken.glb -o fixed.glb --all
qtmesh validate fixed.glb
```

## Config precedence

1. Built-in defaults  
2. `--profile` / `--target` platform profile  
3. Local `qtmesh.yml` / `--config` (wins over Cloud rules)  
4. CLI flags  

Cloud project rules apply only when **no** local config file is present and a token is set.
