"""Render a diagnostic centre section through the two enclosed USB tunnels."""

from pathlib import Path

import bpy
import bmesh
from mathutils import Vector


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "piflex-codex-v23-centered-usb-tunnels-rear-local.stl"
OUTPUT = HERE / "piflex-codex-v23-centered-usb-tunnels-cutaway.png"

TUNNEL_INNER_ABS = 86.0
TUNNEL_OUTER_ABS = 143.077
TUNNEL_Z0 = -10.3
TUNNEL_HEIGHT = 10.0


def material(name, colour):
    value = bpy.data.materials.new(name)
    value.diffuse_color = (*colour, 1.0)
    return value


def point_camera(camera, target):
    camera.rotation_euler = (
        Vector(target) - camera.location
    ).to_track_quat("-Z", "Y").to_euler()


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=str(SOURCE))
body = bpy.context.object
body.name = "V23 centre-section rear body"
body.data.materials.append(material("Body", (0.88, 0.25, 0.055)))

# Retain the +Y half. Looking from -Y exposes the centre plane and proves the
# route is a covered internal void rather than a slot opened through the frame.
bm = bmesh.new()
bm.from_mesh(body.data)
bmesh.ops.bisect_plane(
    bm,
    geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
    dist=0.0001,
    plane_co=(0.0, 0.0, 0.0),
    plane_no=(0.0, 1.0, 0.0),
    clear_inner=True,
    clear_outer=False,
)
bm.to_mesh(body.data)
bm.free()
body.data.update()

route_material = material("Tunnel void reference", (0.12, 0.85, 0.32))
length = TUNNEL_OUTER_ABS - TUNNEL_INNER_ABS
for sign in (-1.0, 1.0):
    centre_x = sign * (TUNNEL_INNER_ABS + TUNNEL_OUTER_ABS) / 2.0
    bpy.ops.mesh.primitive_cube_add(
        location=(centre_x, -0.8, TUNNEL_Z0 + TUNNEL_HEIGHT / 2.0)
    )
    route = bpy.context.object
    route.name = f"{'Left' if sign < 0 else 'Right'} tunnel reference"
    route.dimensions = (length, 1.2, TUNNEL_HEIGHT)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    route.data.materials.append(route_material)

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = "BOTH"
scene.display.shading.color_type = "MATERIAL"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.render.resolution_x = 1800
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

bpy.ops.object.camera_add(location=(0.0, -360.0, 45.0))
camera = bpy.context.object
camera.data.type = "ORTHO"
camera.data.ortho_scale = 360.0
point_camera(camera, (0.0, 0.0, -7.0))
scene.camera = camera
scene.render.filepath = str(OUTPUT)
bpy.ops.render.render(write_still=True)

print(f"Rendered {OUTPUT.name}")
