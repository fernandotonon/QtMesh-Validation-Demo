# Roblox validation demos

Roblox Studio rejects uploads that exceed hard geometry/texture ceilings. QtMesh catches those **before** Import 3D — same numbers as `--game-preset roblox-meshpart` / `roblox-accessory`.

| Gate | Triangles | Textures | Typical use |
|---|---|---|---|
| **MeshPart** | ≤ **20,000** | ≤ **1024** px | Props, structures, static meshes |
| **Accessory** | ≤ **4,000** | ≤ **1024** px | Hats, backpacks, layered clothing, cosmetics |

## Demo assets

| Asset | Approx. tris | Accessory | MeshPart | Story |
|---|---|---|---|---|
| `roblox/good/accessory_hat_ok.glb` | ~2k | ✅ | ✅ | Cosmetics that ship |
| `roblox/good/meshpart_crate_ok.glb` | tiny | ✅ | ✅ | Prop under both ceilings |
| `roblox/issues/prop_fails_accessory.glb` | ~8k | ❌ | ✅ | **Headline** — fine as MeshPart, rejected as accessory |
| `roblox/issues/prop_over_meshpart.glb` | ~25k | ❌ | ❌ | Over the MeshPart hard ceiling |
| `roblox/issues/texture_over_1024/` | low | ❌ tex | ❌ tex | 2048 albedo vs 1024 upload cap |

## Run

```bash
make roblox                 # full Roblox demo script
qtmesh scan --config configs/roblox-meshpart.yml
qtmesh scan --config configs/roblox-accessory.yml

# Same mid-poly prop, two gates (always use --config in this repo so
# rules win over the root qtmesh.yml mobile defaults):
qtmesh scan assets/roblox/issues --include prop_fails_accessory.glb \
  --config configs/roblox-accessory.yml
qtmesh scan assets/roblox/issues --include prop_fails_accessory.glb \
  --config configs/roblox-meshpart.yml
```

## Generate inside the limit (don't post-decimate)

```bash
qtmesh generate3d cutout.png -o hat.glb \
  --backend trellis2 --preset balanced --matting best \
  --game-preset roblox-accessory --tex-res 1024 --seed 42

qtmesh generate3d cutout.png -o crate.glb \
  --backend trellis2 --preset balanced --matting best \
  --game-preset roblox-meshpart --tex-res 1024 --seed 42

# Then gate before Studio:
qtmesh scan hat.glb --config configs/roblox-accessory.yml --fail-on error
qtmesh validate crate.glb
```

Detail belongs in the baked normal/albedo at generation time. Decimating after bake loses texture binding.

## Pipeline sketch

```
image → qtmesh generate3d --game-preset roblox-* → qtmesh scan (this repo)
      → Studio Import 3D → SurfaceAppearance → ReplicatedStorage.Assets
```

See the `qtmesh-to-roblox` skill for organizer scripts, yaw fixes, and Rojo layout.

## Configs / profiles

- `configs/roblox-meshpart.yml` / `configs/profiles/roblox-meshpart.json`
- `configs/roblox-accessory.yml` / `configs/profiles/roblox-accessory.json`
