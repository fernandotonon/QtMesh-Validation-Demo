# Demo assets

- `good/` — ship-ready samples (expect pass under `configs/good-only.yml`)
- `issues/` — intentional failures for marketing / onboarding
- `roblox/good/` — under Roblox MeshPart (20k) and accessory (4k) ceilings
- `roblox/issues/` — over accessory, over MeshPart, over 1024 px texture
- `textures/` — source PNGs used when regenerating meshes
- `pipelines/` — optional output from `demo_character_pipeline.sh --run`

Regenerate with `make assets` (Blender required). Roblox stories: `docs/roblox.md`.
