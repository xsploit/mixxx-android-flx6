"""Render a topology-checked PiFlex print assembly and monolithic result."""

import os
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
PRINT_VERSION = os.environ.get("PIFLEX_PRINT_VERSION", "v22")
SHELL = HERE / f"piflex-codex-{PRINT_VERSION}-registered-screen-shell.stl"
REAR = HERE / f"piflex-codex-{PRINT_VERSION}-printable-rear-mount.stl"
MONOLITHIC = HERE / f"piflex-codex-{PRINT_VERSION}-printable-monolithic.stl"


def point_camera(camera, target):
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def material(name, colour):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*colour, 1.0)
    return mat


def import_stl(path, name, mat):
    bpy.ops.wm.stl_import(filepath=str(path))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj


bpy.ops.wm.read_factory_settings(use_empty=True)
shell = import_stl(SHELL, f"{PRINT_VERSION.upper()} printable screen shell", material("Screen shell", (0.06, 0.23, 0.38)))
rear = import_stl(REAR, f"{PRINT_VERSION.upper()} printable rear mount", material("Rear mount", (0.88, 0.25, 0.055)))
monolithic = import_stl(MONOLITHIC, f"{PRINT_VERSION.upper()} fused enclosure", material("Fused enclosure", (0.08, 0.32, 0.42)))
monolithic.hide_render = True

assembly = [shell, rear]
world_points = [obj.matrix_world @ Vector(corner) for obj in assembly for corner in obj.bound_box]
centre = Vector(
    tuple(
        (min(point[axis] for point in world_points) + max(point[axis] for point in world_points)) / 2.0
        for axis in range(3)
    )
)

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = "BOTH"
scene.display.shading.color_type = "MATERIAL"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.render.resolution_x = 1600
scene.render.resolution_y = 1300
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

bpy.ops.object.camera_add()
camera = bpy.context.object
camera.data.type = "ORTHO"
scene.camera = camera

views = {
    "rear": (centre + Vector((0.0, -430.0, 0.0)), centre, 355),
    "rear-three-quarter": (centre + Vector((225.0, -390.0, 145.0)), centre, 385),
    "opposite-rear-three-quarter": (centre + Vector((-225.0, -390.0, 145.0)), centre, 385),
    "upper-edge": (centre + Vector((0.0, -260.0, 360.0)), centre, 355),
}
for suffix, (location, target, scale) in views.items():
    camera.location = location
    camera.data.ortho_scale = scale
    point_camera(camera, target)
    scene.render.filepath = str(HERE / f"piflex-codex-{PRINT_VERSION}-printable-{suffix}.png")
    bpy.ops.render.render(write_still=True)

# Render the union separately to prove the same accepted exterior survived the
# final manifold fusion.
shell.hide_render = True
rear.hide_render = True
monolithic.hide_render = False
location, target, scale = views["rear-three-quarter"]
camera.location = location
camera.data.ortho_scale = scale
point_camera(camera, target)
scene.render.filepath = str(HERE / f"piflex-codex-{PRINT_VERSION}-printable-monolithic-three-quarter.png")
bpy.ops.render.render(write_still=True)

print(f"Rendered PiFlex Codex {PRINT_VERSION.upper()} print parts")
