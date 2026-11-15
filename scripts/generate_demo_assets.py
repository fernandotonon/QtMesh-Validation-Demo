#!/usr/bin/env python3
"""Generate intentional good/bad demo meshes for QtMesh validation demos.

Run with Blender (no UI):
  blender --background --python scripts/generate_demo_assets.py
"""

from __future__ import annotations

import math
import os
import struct
import zlib
from pathlib import Path

import bpy
import bmesh

ROOT = Path(__file__).resolve().parents[1]
GOOD = ROOT / "assets" / "good"
ISSUES = ROOT / "assets" / "issues"
TEXTURES = ROOT / "assets" / "textures"
ROBLOX_GOOD = ROOT / "assets" / "roblox" / "good"
ROBLOX_ISSUES = ROOT / "assets" / "roblox" / "issues"


def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def ensure_dirs() -> None:
    for path in (GOOD, ISSUES, TEXTURES, ROBLOX_GOOD, ROBLOX_ISSUES):
        path.mkdir(parents=True, exist_ok=True)


def triangle_count(obj: bpy.types.Object) -> int:
    mesh = obj.data
    mesh.calc_loop_triangles()
    return len(mesh.loop_triangles)


def write_png(path: Path, width: int, height: int, rgba: tuple[int, int, int, int]) -> None:
    """Minimal uncompressed-ish PNG writer (no Pillow dependency)."""
    r, g, b, a = rgba
    raw = b"".join(
        b"\x00" + bytes([r, g, b, a]) * width for _ in range(height)
    )

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    path.write_bytes(png)


def make_checker_png(path: Path, size: int, c0=(40, 120, 200, 255), c1=(220, 230, 240, 255)) -> None:
    rows = []
    for y in range(size):
        row = [b"\x00"]
        for x in range(size):
            color = c0 if ((x // 16) + (y // 16)) % 2 == 0 else c1
            row.append(bytes(color))
        rows.append(b"".join(row))
    raw = b"".join(rows)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    path.write_bytes(png)


def export_glb(obj: bpy.types.Object, path: Path) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
    )


def add_principled_material(name: str, color=(0.2, 0.55, 0.9, 1.0), image_path: Path | None = None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if image_path and image_path.exists():
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(str(image_path))
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        bsdf.inputs["Base Color"].default_value = color
    return mat


def create_clean_crate() -> None:
    reset_scene()
    tex = TEXTURES / "crate_albedo_512.png"
    make_checker_png(tex, 512, c0=(120, 78, 42, 255), c1=(168, 118, 70, 255))
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
    obj = bpy.context.active_object
    obj.name = "crate_clean"
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    mat = add_principled_material("crate_mat", image_path=tex)
    obj.data.materials.append(mat)
    export_glb(obj, GOOD / "crate_clean.glb")


def create_clean_prop() -> None:
    reset_scene()
    tex = TEXTURES / "barrel_albedo_1024.png"
    make_checker_png(tex, 1024, c0=(70, 90, 110, 255), c1=(140, 150, 160, 255))
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.35, depth=0.9, location=(0, 0, 0.45))
    obj = bpy.context.active_object
    obj.name = "barrel_clean"
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.cylinder_project(direction="VIEW_ON_EQUATOR", align="POLAR_ZX")
    bpy.ops.object.mode_set(mode="OBJECT")
    mat = add_principled_material("barrel_mat", image_path=tex)
    obj.data.materials.append(mat)
    export_glb(obj, GOOD / "barrel_clean.glb")


def create_overbudget_mesh() -> None:
    """Dense subdivided sphere — fails mobile / web triangle budgets."""
    reset_scene()
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=6, radius=1.0, location=(0, 0, 1.0))
    obj = bpy.context.active_object
    obj.name = "prop_overbudget"
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.subdivide(number_cuts=2)
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66))
    bpy.ops.object.mode_set(mode="OBJECT")
    mat = add_principled_material("overbudget_mat", color=(0.85, 0.25, 0.2, 1.0))
    obj.data.materials.append(mat)
    export_glb(obj, ISSUES / "prop_overbudget.glb")


def create_no_uv_mesh() -> None:
    reset_scene()
    bpy.ops.mesh.primitive_monkey_add(size=1.5, location=(0, 0, 0.75))
    obj = bpy.context.active_object
    obj.name = "mesh_no_uvs"
    # Explicitly strip UV layers
    while obj.data.uv_layers:
        obj.data.uv_layers.remove(obj.data.uv_layers[0])
    mat = add_principled_material("nouv_mat", color=(0.9, 0.7, 0.2, 1.0))
    obj.data.materials.append(mat)
    export_glb(obj, ISSUES / "mesh_no_uvs.glb")


def create_non_manifold_mesh() -> None:
    """Intersecting cubes sharing faces / internal geometry — non-manifold edges."""
    reset_scene()
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
    a = bpy.context.active_object
    a.name = "non_manifold"
    bpy.ops.mesh.primitive_cube_add(size=0.8, location=(0.3, 0.2, 0.7))
    b = bpy.context.active_object
    bpy.ops.object.select_all(action="DESELECT")
    a.select_set(True)
    b.select_set(True)
    bpy.context.view_layer.objects.active = a
    bpy.ops.object.join()
    obj = bpy.context.active_object
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(obj.data)
    # Duplicate a face inward to force non-manifold / internal faces
    faces = [f for f in bm.faces]
    if faces:
        bmesh.ops.duplicate(bm, geom=[faces[0]])
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66))
    bpy.ops.object.mode_set(mode="OBJECT")
    mat = add_principled_material("nm_mat", color=(0.6, 0.2, 0.7, 1.0))
    obj.data.materials.append(mat)
    export_glb(obj, ISSUES / "mesh_non_manifold.glb")


def create_degenerate_slivers() -> None:
    """Mesh with near-zero-area triangles (PS1-rip style issues)."""
    reset_scene()
    mesh = bpy.data.meshes.new("sliver_mesh")
    obj = bpy.data.objects.new("mesh_degenerate_slivers", mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    # Solid triangle
    v0 = bm.verts.new((0, 0, 0))
    v1 = bm.verts.new((1, 0, 0))
    v2 = bm.verts.new((0.5, 1, 0))
    bm.faces.new((v0, v1, v2))
    # Near-collinear sliver
    v3 = bm.verts.new((2, 0, 0))
    v4 = bm.verts.new((3, 0, 0))
    v5 = bm.verts.new((2.5, 0.00001, 0))
    bm.faces.new((v3, v4, v5))
    # Another sliver
    v6 = bm.verts.new((0, 2, 0))
    v7 = bm.verts.new((1, 2, 0))
    v8 = bm.verts.new((0.5, 2.00002, 0))
    bm.faces.new((v6, v7, v8))
    bm.to_mesh(mesh)
    bm.free()
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66))
    bpy.ops.object.mode_set(mode="OBJECT")
    mat = add_principled_material("sliver_mat", color=(0.2, 0.8, 0.4, 1.0))
    obj.data.materials.append(mat)
    export_glb(obj, ISSUES / "mesh_degenerate_slivers.glb")


def create_oversized_texture_asset() -> None:
    reset_scene()
    out_dir = ISSUES / "texture_oversized"
    out_dir.mkdir(parents=True, exist_ok=True)
    tex = out_dir / "hero_albedo_4096.png"
    # Solid color 4096 keeps file size manageable while failing max_texture_dimension
    write_png(tex, 4096, 4096, (30, 144, 255, 255))
    (TEXTURES / "hero_albedo_4096.png").write_bytes(tex.read_bytes())
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.6, location=(0, 0, 0.6))
    obj = bpy.context.active_object
    obj.name = "texture_oversized"
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.sphere_project()
    bpy.ops.object.mode_set(mode="OBJECT")
    mat = add_principled_material("tex_big_mat", image_path=tex)
    obj.data.materials.append(mat)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(
        filepath=str(out_dir / "texture_oversized.gltf"),
        export_format="GLTF_SEPARATE",
        use_selection=True,
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
    )


def create_npot_texture_asset() -> None:
    """External NPOT PNG so scan texture inspection can flag power-of-two rules."""
    reset_scene()
    out_dir = ISSUES / "texture_npot"
    out_dir.mkdir(parents=True, exist_ok=True)
    tex = out_dir / "npot_albedo_900x700.png"
    write_png(tex, 900, 700, (220, 80, 60, 255))
    bpy.ops.mesh.primitive_plane_add(size=1.2, location=(0, 0, 0.01))
    obj = bpy.context.active_object
    obj.name = "texture_npot"
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.unwrap(method="ANGLE_BASED", margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    mat = add_principled_material("npot_mat", image_path=tex)
    obj.data.materials.append(mat)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(
        filepath=str(out_dir / "texture_npot.gltf"),
        export_format="GLTF_SEPARATE",
        use_selection=True,
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
    )
    # Keep a copy under textures/ for the generator inventory
    (TEXTURES / "npot_albedo_900x700.png").write_bytes(tex.read_bytes())


def create_bad_filename_asset() -> None:
    reset_scene()
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.4, depth=0.9, location=(0, 0, 0.45))
    obj = bpy.context.active_object
    obj.name = "Bad Naming Example"
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66))
    bpy.ops.object.mode_set(mode="OBJECT")
    mat = add_principled_material("name_mat", color=(0.95, 0.55, 0.15, 1.0))
    obj.data.materials.append(mat)
    export_glb(obj, ISSUES / "Bad File Name With Spaces.glb")


def create_multi_material_drawcalls() -> None:
    """Many materials on one asset — fails max_material_count / draw-call budgets."""
    reset_scene()
    objs = []
    for i in range(20):
        angle = (i / 20.0) * math.tau
        loc = (math.cos(angle) * 1.2, math.sin(angle) * 1.2, 0.25)
        bpy.ops.mesh.primitive_cube_add(size=0.35, location=loc)
        o = bpy.context.active_object
        o.name = f"mat_piece_{i:02d}"
        color = (
            0.2 + 0.7 * ((i * 37) % 100) / 100.0,
            0.2 + 0.7 * ((i * 57) % 100) / 100.0,
            0.2 + 0.7 * ((i * 97) % 100) / 100.0,
            1.0,
        )
        mat = add_principled_material(f"mat_{i:02d}", color=color)
        o.data.materials.append(mat)
        objs.append(o)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    obj = bpy.context.active_object
    obj.name = "too_many_materials"
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66))
    bpy.ops.object.mode_set(mode="OBJECT")
    export_glb(obj, ISSUES / "too_many_materials.glb")


def create_missing_texture_sidecar() -> None:
    """glTF that references a texture path that does not exist."""
    reset_scene()
    missing = TEXTURES / "does_not_exist_albedo.png"
    # Intentionally do NOT create the file
    bpy.ops.mesh.primitive_torus_add(major_radius=0.5, minor_radius=0.18, location=(0, 0, 0.4))
    obj = bpy.context.active_object
    obj.name = "missing_texture"
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66))
    bpy.ops.object.mode_set(mode="OBJECT")
    # Export as glTF separate so we can break the texture reference
    out_dir = ISSUES / "missing_texture"
    out_dir.mkdir(parents=True, exist_ok=True)
    mat = add_principled_material("missing_tex_mat", color=(0.3, 0.3, 0.3, 1.0))
    # Create a real texture then delete it after export
    temp_tex = out_dir / "_temp_albedo.png"
    write_png(temp_tex, 64, 64, (128, 128, 128, 255))
    mat = add_principled_material("missing_tex_mat2", image_path=temp_tex)
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(
        filepath=str(out_dir / "missing_texture.gltf"),
        export_format="GLTF_SEPARATE",
        use_selection=True,
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
    )
    # Remove texture files so the scan reports missing textures
    for png in out_dir.glob("*.png"):
        png.unlink()
    if temp_tex.exists():
        temp_tex.unlink()
    # Also remove blender-packed leftovers if any
    _ = missing  # documented intentional missing path


def create_clean_character_proxy() -> None:
    """Low-poly A-pose proxy that passes character scopes (no skeleton — used for geometry budgets)."""
    reset_scene()
    # Body
    bpy.ops.mesh.primitive_cube_add(size=0.5, location=(0, 0, 1.1))
    torso = bpy.context.active_object
    torso.scale = (0.7, 0.4, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.22, location=(0, 0, 1.75))
    head = bpy.context.active_object
    # Legs
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.1, depth=0.7, location=(-0.15, 0, 0.35))
    leg_l = bpy.context.active_object
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.1, depth=0.7, location=(0.15, 0, 0.35))
    leg_r = bpy.context.active_object
    # Arms
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=0.7, location=(-0.55, 0, 1.25))
    arm_l = bpy.context.active_object
    arm_l.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=0.7, location=(0.55, 0, 1.25))
    arm_r = bpy.context.active_object
    arm_r.rotation_euler = (0, math.radians(-90), 0)
    bpy.ops.object.transform_apply(rotation=True)

    parts = [torso, head, leg_l, leg_r, arm_l, arm_r]
    bpy.ops.object.select_all(action="DESELECT")
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = torso
    bpy.ops.object.join()
    obj = bpy.context.active_object
    obj.name = "character_proxy_clean"
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    tex = TEXTURES / "character_albedo_512.png"
    make_checker_png(tex, 512, c0=(60, 100, 160, 255), c1=(200, 180, 140, 255))
    mat = add_principled_material("char_mat", image_path=tex)
    obj.data.materials.append(mat)
    export_glb(obj, GOOD / "character_proxy_clean.glb")


# ── Roblox demos (MeshPart ≤20k / accessory ≤4k / textures ≤1024) ─────────────

def _uv_and_export(obj: bpy.types.Object, path: Path, mat_name: str, color, image_path: Path | None = None) -> None:
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    mat = add_principled_material(mat_name, color=color, image_path=image_path)
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    print(f"    tris≈{triangle_count(obj)} → {path.relative_to(ROOT)}")
    export_glb(obj, path)


def create_roblox_accessory_hat() -> None:
    """~2k tris hat — PASSES roblox-accessory (4k) and MeshPart (20k)."""
    reset_scene()
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.45, location=(0, 0, 0.2))
    crown = bpy.context.active_object
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.7, depth=0.08, location=(0, 0, 0.02))
    brim = bpy.context.active_object
    bpy.ops.object.select_all(action="DESELECT")
    crown.select_set(True)
    brim.select_set(True)
    bpy.context.view_layer.objects.active = crown
    bpy.ops.object.join()
    obj = bpy.context.active_object
    obj.name = "accessory_hat_ok"
    tex = TEXTURES / "roblox_hat_512.png"
    make_checker_png(tex, 512, c0=(180, 40, 50, 255), c1=(220, 90, 70, 255))
    _uv_and_export(obj, ROBLOX_GOOD / "accessory_hat_ok.glb", "hat_mat", (0.8, 0.2, 0.2, 1.0), tex)


def create_roblox_meshpart_crate() -> None:
    """Low-poly crate — PASSES MeshPart; also accessory-safe for tiny props."""
    reset_scene()
    tex = TEXTURES / "roblox_crate_1024.png"
    make_checker_png(tex, 1024, c0=(110, 70, 35, 255), c1=(160, 110, 60, 255))
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
    obj = bpy.context.active_object
    obj.name = "meshpart_crate_ok"
    _uv_and_export(obj, ROBLOX_GOOD / "meshpart_crate_ok.glb", "rbx_crate_mat", (0.5, 0.35, 0.2, 1.0), tex)


def create_roblox_fails_accessory_ok_meshpart() -> None:
    """~8k tris prop — FAILS accessory (4k), PASSES MeshPart (20k). Headline Roblox story.

    UV sphere tris ≈ 2 * segments * (rings - 1); 64×64 ≈ 8k.
    """
    reset_scene()
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=64, ring_count=64, radius=0.9, location=(0, 0, 0.9)
    )
    obj = bpy.context.active_object
    obj.name = "prop_fails_accessory"
    _uv_and_export(obj, ROBLOX_ISSUES / "prop_fails_accessory.glb", "mid_mat", (0.2, 0.55, 0.85, 1.0))


def create_roblox_over_meshpart() -> None:
    """~25k tris — FAILS Roblox MeshPart hard ceiling (20k).

    UV sphere 112×112 ≈ 2*112*111 ≈ 24.8k tris.
    """
    reset_scene()
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=112, ring_count=112, radius=1.0, location=(0, 0, 1.0)
    )
    obj = bpy.context.active_object
    obj.name = "prop_over_meshpart"
    _uv_and_export(obj, ROBLOX_ISSUES / "prop_over_meshpart.glb", "over_mp_mat", (0.85, 0.25, 0.2, 1.0))


def create_roblox_texture_over_1024() -> None:
    """1024 is Roblox upload cap — 2048 albedo fails both MeshPart and accessory texture rules."""
    reset_scene()
    out_dir = ROBLOX_ISSUES / "texture_over_1024"
    out_dir.mkdir(parents=True, exist_ok=True)
    tex = out_dir / "albedo_2048.png"
    write_png(tex, 2048, 2048, (40, 160, 90, 255))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.5, location=(0, 0, 0.5))
    obj = bpy.context.active_object
    obj.name = "texture_over_1024"
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.sphere_project()
    bpy.ops.object.mode_set(mode="OBJECT")
    mat = add_principled_material("rbx_tex_mat", image_path=tex)
    obj.data.materials.append(mat)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(
        filepath=str(out_dir / "texture_over_1024.gltf"),
        export_format="GLTF_SEPARATE",
        use_selection=True,
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
    )
    print(f"    tris≈{triangle_count(obj)} → {out_dir.relative_to(ROOT)}")


def main() -> None:
    ensure_dirs()
    creators = [
        ("crate_clean", create_clean_crate),
        ("barrel_clean", create_clean_prop),
        ("character_proxy_clean", create_clean_character_proxy),
        ("prop_overbudget", create_overbudget_mesh),
        ("mesh_no_uvs", create_no_uv_mesh),
        ("mesh_non_manifold", create_non_manifold_mesh),
        ("mesh_degenerate_slivers", create_degenerate_slivers),
        ("texture_oversized", create_oversized_texture_asset),
        ("texture_npot", create_npot_texture_asset),
        ("bad_filename", create_bad_filename_asset),
        ("too_many_materials", create_multi_material_drawcalls),
        ("missing_texture", create_missing_texture_sidecar),
        ("roblox_accessory_hat", create_roblox_accessory_hat),
        ("roblox_meshpart_crate", create_roblox_meshpart_crate),
        ("roblox_fails_accessory", create_roblox_fails_accessory_ok_meshpart),
        ("roblox_over_meshpart", create_roblox_over_meshpart),
        ("roblox_texture_over_1024", create_roblox_texture_over_1024),
    ]
    for name, fn in creators:
        print(f"[generate] {name}…")
        fn()
        print(f"[generate] {name} done")
    print("[generate] all demo assets ready")


if __name__ == "__main__":
    main()
