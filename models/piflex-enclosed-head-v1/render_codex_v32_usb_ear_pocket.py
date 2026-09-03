"""Render the deepened V32 USB opening directly from the ear's top edge."""

from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "piflex-codex-v32-deep-usb-ear-pockets-rear-local.stl"
OUTPUT = HERE / "piflex-codex-v32-usb-ear-pocket-closeup.png"


def point_camera(camera, target):
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=str(SOURCE))
ear = bpy.context.object
ear.name = "V32 rear enclosure with deep USB ear pocket"
material = bpy.data.materials.new("V32 orange enclosure")
material.diffuse_color = (0.78, 0.27, 0.025, 1.0)
ear.data.materials.append(material)

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = "BOTH"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.background_type = "VIEWPORT"
scene.display.shading.background_color = (0.12, 0.14, 0.17)
scene.view_settings.look = "AgX - Medium High Contrast"
scene.render.resolution_x = 1200
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False

bpy.ops.object.camera_add()
camera = bpy.context.object
camera.data.type = "ORTHO"
camera.data.ortho_scale = 34.0
camera.location = (143.077, 150.0, 1.0)
camera.rotation_euler = (-1.5707963268, 0.0, 0.0)
scene.camera = camera
scene.render.filepath = str(OUTPUT)
bpy.ops.render.render(write_still=True)
print(f"Rendered {OUTPUT.name}")
