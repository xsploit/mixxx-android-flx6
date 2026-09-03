"""Render a diagnostic section through the two enclosed USB tunnels."""

import os
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector


HERE = Path(__file__).resolve().parent
DESIGN_VERSION = os.environ.get("PIFLEX_TUNNEL_VERSION", "v23")
DESIGN_SLUG = os.environ.get("PIFLEX_TUNNEL_SLUG", "centered-usb-tunnels")
TUNNEL_CENTRE_Y = float(os.environ.get("PIFLEX_TUNNEL_CENTRE_Y", "0.0"))
STEM = f"piflex-codex-{DESIGN_VERSION}-{DESIGN_SLUG}"
SOURCE = HERE / f"{STEM}-rear-local.stl"
OUTPUT = HERE / f"{STEM}-cutaway.png"
TUNNEL_VOIDS = HERE / f"piflex-codex-{DESIGN_VERSION}-usb-tunnel-voids-local.stl"


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
body.name = f"{DESIGN_VERSION.upper()} tunnel-section rear body"
body.data.materials.append(material("Body", (0.88, 0.25, 0.055)))

# Retain the +Y half. Looking from -Y exposes the centre plane and proves the
# route is a covered internal void rather than a slot opened through the frame.
bm = bmesh.new()
bm.from_mesh(body.data)
bmesh.ops.bisect_plane(
    bm,
    geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
    dist=0.0001,
    plane_co=(0.0, TUNNEL_CENTRE_Y, 0.0),
    plane_no=(0.0, 1.0, 0.0),
    clear_inner=True,
    clear_outer=False,
)
bm.to_mesh(body.data)
bm.free()
body.data.update()

bpy.ops.wm.stl_import(filepath=str(TUNNEL_VOIDS))
routes = bpy.context.object
routes.name = f"{DESIGN_VERSION.upper()} exact tunnel voids"
routes.data.materials.append(material("Tunnel void reference", (0.12, 0.85, 0.32)))

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

bpy.ops.object.camera_add(location=(0.0, TUNNEL_CENTRE_Y - 360.0, 45.0))
camera = bpy.context.object
camera.data.type = "ORTHO"
camera.data.ortho_scale = 360.0
point_camera(camera, (0.0, TUNNEL_CENTRE_Y, -7.0))
scene.camera = camera
scene.render.filepath = str(OUTPUT)
bpy.ops.render.render(write_still=True)

print(f"Rendered {OUTPUT.name}")
