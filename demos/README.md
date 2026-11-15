# Live demo runbook (5 minutes)

Use this script when presenting QtMesh validations / Cloud to prospects.

## 1. Green contrast (30 s)

```bash
make good
```

Expect: 3 passed, 0 errors. Screenshot the summary.

## 2. Red findings (90 s)

```bash
make issues
```

Call out:
- `prop_overbudget.glb` → triangle / vertex budget errors  
- `too_many_materials.glb` → material + draw-call errors  
- `texture_oversized/` → 4096 px vs 1024 mobile cap  
- `texture_npot/` → non–power-of-two albedo  
- `mesh_no_uvs.glb` → require UV0  
- `Bad File Name With Spaces.glb` → snake_case  
- `missing_texture/` → broken relative PNG  

## 3. Platform profiles (60 s)

```bash
make profiles
```

Same overbudget mesh under `ps1` → `mobile-low` → `modern-console`.

## 4. Fix loop (60 s)

```bash
make fix
```

Show before/after JSON under `reports/fix-pipeline/`.

## 5. Roblox poly limits (90 s)

```bash
make roblox
```

Call out Studio hard ceilings:
- MeshPart ≤ **20,000** tris · accessory ≤ **4,000** tris · textures ≤ **1024** px  
- Show `prop_fails_accessory.glb` under accessory (**red**) then MeshPart (**green**)  
- Generate inside the limit: `--game-preset roblox-meshpart` / `roblox-accessory`

## 6. Cloud (optional, 60 s)

```bash
export QTMESH_CLOUD_TOKEN=…
make cloud
```

Open https://qtmesh.dev — quality score, history, README badges.
