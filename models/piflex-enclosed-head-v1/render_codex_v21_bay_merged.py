"""Render the V21 bay-merged opening from inspection angles."""

from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "piflex-codex-v21-bay-merged-usb-routing.glb"


def point_camera(camera, target):
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def material(name, colour):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*colour, 1.0)
    return mat


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
shell = next(obj for obj in meshes if obj.name.startswith("Exact V19 screen case"))
structure = next(obj for obj in meshes if obj.name.startswith("PiFlex Codex V21"))
shell.data.materials.clear()
shell.data.materials.append(material("Frozen V19 screen shell", (0.06, 0.23, 0.38)))
structure.data.materials.clear()
structure.data.materials.append(material("V21 rear and mount", (0.88, 0.25, 0.055)))

world_points = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
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
    scene.render.filepath = str(HERE / f"piflex-codex-v21-bay-merged-{suffix}.png")
    bpy.ops.render.render(write_still=True)

print("Rendered PiFlex Codex V21 bay-merged assembly")
