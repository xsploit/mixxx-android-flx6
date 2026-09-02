"""Render the V18-only small service-opening enlargement."""

from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "piflex-codex-v18-usb-routing.glb"


def point_camera(camera, target):
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def material(name, colour):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*colour, 1.0)
    return mat


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
shell = next(obj for obj in meshes if obj.name.startswith("Exact V18 screen case"))
mount = next(obj for obj in meshes if obj.name.startswith("PiFlex V18 shifted-placement"))
shell.data.materials.clear()
shell.data.materials.append(material("Original V18 shell, one cut", (0.08, 0.20, 0.34)))
mount.data.materials.clear()
mount.data.materials.append(material("Untouched V18 mount", (0.85, 0.23, 0.07)))

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = "BOTH"
scene.display.shading.color_type = "MATERIAL"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.render.resolution_x = 1400
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

bpy.ops.object.camera_add()
camera = bpy.context.object
camera.data.type = "ORTHO"
camera.data.ortho_scale = 360
scene.camera = camera

views = {
    "rear": ((0.0, -430.0, -18.0), (-30.0, 0.0, -20.0)),
    "front": ((0.0, 430.0, -18.0), (-30.0, 0.0, -20.0)),
    "rear-three-quarter": ((225.0, -380.0, 120.0), (-30.0, 0.0, -20.0)),
}
for suffix, (location, target) in views.items():
    camera.location = location
    point_camera(camera, target)
    scene.render.filepath = str(HERE / f"piflex-codex-v18-usb-routing-{suffix}.png")
    bpy.ops.render.render(write_still=True)

print("Rendered Codex V18 USB-routing revision")
