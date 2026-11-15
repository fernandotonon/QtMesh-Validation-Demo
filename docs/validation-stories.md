# Validation stories (marketing demos)

Each asset under `assets/issues/` is **intentionally broken** so a scan produces a clear, screenshot-ready finding. Clean counterparts live in `assets/good/`.

| Story | Asset | What QtMesh catches | Why it matters |
|---|---|---|---|
| Triangle budget | `issues/prop_overbudget.glb` (~184k tris) | `max_triangle_count` / profile budgets | Mobile & WebGL frames drop when props ship at film density |
| Missing UVs | `issues/mesh_no_uvs.glb` | `require_uv_channels: 1` | Lightmaps, atlases, and AI texture tools need UV0 |
| Non-manifold | `issues/mesh_non_manifold.glb` | `detect_non_manifold_edges_pct` (opt-in) | Booleans, collision, and 3D-print pipelines expect manifold mesh. Enable the rule in `qtmesh.yml` — hard-edged glTF UV seams can look non-manifold on tiny props, so campaign configs leave it off by default. |
| Degenerate faces | `issues/mesh_degenerate_slivers.glb` | `ps1_rip_zero_area_pct` / `qtmesh validate` | Zero-area slivers waste GPU and break baking |
| Oversized texture | `issues/texture_oversized/` (4096²) | `max_texture_resolution` | VRAM spikes on mobile / WebGL |
| Non–power-of-two | `issues/texture_npot/` (900×700 PNG) | `texture_not_power_of_two` | Older GPUs & mipmap chains expect POT |
| Draw-call explosion | `issues/too_many_materials.glb` (20 mats) | `max_material_count` / `max_draw_calls` | Batching dies when every face gets its own material |
| Naming convention | `issues/Bad File Name With Spaces.glb` | `file_name_case: snake_case` | CI enforces repo conventions before merge |
| Missing texture file | `issues/missing_texture/` | `require_textures_exist` | Broken relative paths fail silently in engines |
| Clean crate / barrel / character | `good/*.glb` | Pass under mobile-low | Green badge / “ship ready” contrast shot |
| Roblox accessory OK | `roblox/good/accessory_hat_ok.glb` | Pass ≤4k accessory | Cosmetics under Studio upload limit |
| Roblox MeshPart OK | `roblox/good/meshpart_crate_ok.glb` | Pass ≤20k MeshPart | Prop ready for Import 3D |
| Roblox accessory vs MeshPart | `roblox/issues/prop_fails_accessory.glb` | Fail 4k / pass 20k | Same asset, two Roblox gates |
| Roblox over MeshPart | `roblox/issues/prop_over_meshpart.glb` | Fail ≤20k | Hard MeshPart ceiling |
| Roblox texture 1024 | `roblox/issues/texture_over_1024/` | Fail `max_texture_resolution` | Studio texture upload cap |

Roblox deep-dive: [`roblox.md`](roblox.md).

## How to show one story

```bash
# Single finding
qtmesh scan assets/issues --include "prop_overbudget.glb" --profile mobile-low

# Contrast: green vs red
make good
make issues

# Same mesh, different platforms
./scripts/demo_profiles.sh
```

## Platform profiles

Built-in profiles ship with QtMesh (`qtmesh scan --list-profiles`):

`ps1`, `n64`, `nds`, `dreamcast`, `mobile-low`, `webgl`, `steamdeck`, `switch-like`, `modern-console`, `vr`

Marketing tip: run `prop_overbudget.glb` under `ps1` then `modern-console` — the same asset flips from hard fail to “maybe ok”, which makes Cloud rule dashboards intuitive.
