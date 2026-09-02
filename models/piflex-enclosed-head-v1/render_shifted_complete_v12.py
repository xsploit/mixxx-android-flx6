"""Replace V9's mount with V12, shift the entire assembly, and export viewers."""

from pathlib import Path
import os

import bpy
from mathutils import Vector


ROOT = Path(r"C:\Users\SUBSECT\Documents\Codex\2026-08-18\hey-i-need-you-to-research")
OUT = ROOT / "models" / "piflex-enclosed-head-v1"
REVISION = os.environ.get("PIFLEX_REVISION", "v12").lower()
CAD_STL = OUT / f"piflex-complete-v9-shifted-mount-{REVISION}.stl"
SHIFT_X_MM = -18.629

OLD_BODY = "PiFlex V8 open-back case, USB ears and FLX6 mount"
SHELL = "Exact original 10-inch shell, opened only beneath Pi pod"


old_body = bpy.data.objects.get(OLD_BODY)
shell = bpy.data.objects.get(SHELL)
if old_body is None or shell is None:
    raise RuntimeError("Authoritative V9 enclosure objects are missing")

body_matrix = old_body.matrix_world.copy()
body_materials = list(old_body.data.materials)
bpy.data.objects.remove(old_body, do_unlink=True)

bpy.ops.wm.stl_import(filepath=str(CAD_STL))
body = bpy.context.object
body.name = f"PiFlex {REVISION.upper()} shifted-placement complete enclosure"
body.matrix_world = body_matrix
for mat in body_materials:
    body.data.materials.append(mat)

# The upper enclosure, brackets and clamps move as one rigid V9-derived unit.
for obj in (body, shell):
    matrix = obj.matrix_world.copy()
    matrix.translation.x += SHIFT_X_MM
    obj.matrix_world = matrix
    obj["complete_assembly_install_shift_x_mm"] = SHIFT_X_MM


def camera(name, location, target, scale, size=(1920, 1050)):
    old = bpy.data.objects.get(name)
    if old is not None:
        bpy.data.objects.remove(old, do_unlink=True)
    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.object
    cam.name = name
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = scale
    cam.data.clip_end = 5000.0
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam["rx"], cam["ry"] = size
    return cam


def render(cam, filename):
    scene = bpy.context.scene
    scene.camera = cam
    scene.render.resolution_x = cam["rx"]
    scene.render.resolution_y = cam["ry"]
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(OUT / filename)
    bpy.ops.render.render(write_still=True)


front = bpy.data.objects.get("full-controller-no-screen")
rear = bpy.data.objects.get("full-controller-no-screen-rear")
if front is None or rear is None:
    raise RuntimeError("V9 inspection cameras are missing")

straight_rear = camera(
    "v12-straight-rear-clearance",
    (0.0, 930.0, 205.0),
    (0.0, 155.0, 66.0),
    710.0,
)
render(front, f"piflex-complete-shifted-{REVISION}.png")
render(rear, f"piflex-complete-shifted-rear-{REVISION}.png")
render(straight_rear, f"piflex-complete-shifted-rear-clearance-{REVISION}.png")

# Full interactive controller assembly.
bpy.ops.object.select_all(action="DESELECT")
for obj in bpy.context.scene.objects:
    if obj.type == "MESH" and obj.name != "Reference floor":
        obj.hide_set(False)
        obj.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.export_scene.gltf(
    filepath=str(OUT / f"piflex-complete-shifted-full-controller-{REVISION}.glb"),
    export_format="GLB",
    use_selection=True,
)

# Smaller enclosure-only interactive model.
bpy.ops.object.select_all(action="DESELECT")
for obj in (body, shell):
    obj.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.export_scene.gltf(
    filepath=str(OUT / f"piflex-complete-shifted-enclosure-only-{REVISION}.glb"),
    export_format="GLB",
    use_selection=True,
)

scene = bpy.context.scene
scene.camera = front
scene["complete_assembly_install_shift_x_mm"] = SHIFT_X_MM
scene[f"{REVISION}_rear_right"] = "filled bracket with direct screw hole"
scene[f"{REVISION}_rear_left"] = "relocated circular factory-screw tab"
bpy.ops.wm.save_as_mainfile(
    filepath=str(OUT / f"piflex-complete-shifted-full-controller-{REVISION}.blend")
)
print("PIFLEX_SHIFTED_RENDERED", REVISION, OUT)
