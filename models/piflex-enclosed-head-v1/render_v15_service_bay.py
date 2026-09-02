"""Render V15's larger rear bay and an inspection-only open service view."""

from pathlib import Path
import os

import bpy
from mathutils import Vector


ROOT = Path(r"C:\Users\SUBSECT\Documents\Codex\2026-08-18\hey-i-need-you-to-research")
OUT = ROOT / "models" / "piflex-enclosed-head-v1"
REVISION = os.environ.get("PIFLEX_REVISION", "v15").lower()

if REVISION == "v20":
    LOCAL_STL = "piflex-v20-clean-service-bay-local.stl"
    OPEN_STL = "piflex-v20-service-open-inspection.stl"
    SHAPE_LABEL = "retained-plate-service-bay"
elif REVISION == "v19":
    LOCAL_STL = "piflex-v19-clean-service-bay-local.stl"
    OPEN_STL = "piflex-v19-service-open-inspection.stl"
    SHAPE_LABEL = "clean-service-bay"
elif REVISION == "v18":
    LOCAL_STL = "piflex-v18-screw-safe-service-bay-local.stl"
    OPEN_STL = "piflex-v18-service-open-inspection.stl"
    SHAPE_LABEL = "screw-safe-service-bay"
elif REVISION == "v17":
    LOCAL_STL = "piflex-v17-integrated-service-bay-local.stl"
    OPEN_STL = "piflex-v17-service-open-inspection.stl"
    SHAPE_LABEL = "integrated-service-bay"
elif REVISION == "v16":
    LOCAL_STL = "piflex-v16-rounded-service-bay-local.stl"
    OPEN_STL = "piflex-v16-service-open-inspection.stl"
    SHAPE_LABEL = "rounded-service-bay"
else:
    LOCAL_STL = "piflex-v15-rectangular-service-bay-local.stl"
    OPEN_STL = "piflex-v15-service-open-inspection.stl"
    SHAPE_LABEL = "rectangular-service-bay"


def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def material(name, colour, metallic=0.0, roughness=0.45):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*colour, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*colour, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def add_area(name, location, energy, size, colour):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = colour
    obj = bpy.data.objects.new(name, data)
    obj.location = location
    obj.rotation_euler = (Vector((0.0, 0.0, -8.0)) - obj.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.collection.objects.link(obj)


def setup_scene():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1800
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world.color = (0.055, 0.065, 0.085)

    bpy.ops.object.camera_add(location=(0.0, 245.0, -430.0))
    cam = bpy.context.object
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 385.0
    cam.rotation_euler = (Vector((0.0, 0.0, -7.0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam

    add_area("Key", (-220.0, 220.0, -260.0), 1350.0, 260.0, (0.82, 0.90, 1.0))
    add_area("Fill", (240.0, 40.0, -120.0), 900.0, 220.0, (1.0, 0.56, 0.26))
    add_area("Rim", (0.0, -240.0, 120.0), 1000.0, 190.0, (0.35, 0.55, 1.0))


def set_camera(location, target, scale):
    cam = bpy.context.scene.camera
    cam.location = location
    cam.data.ortho_scale = scale
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()


def render_model(stl_name, png_name, mat):
    bpy.ops.wm.stl_import(filepath=str(OUT / stl_name))
    obj = bpy.context.object
    obj.name = stl_name.removesuffix(".stl")
    obj.data.materials.append(mat)
    for polygon in obj.data.polygons:
        polygon.use_smooth = False
    bpy.context.scene.render.filepath = str(OUT / png_name)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(obj, do_unlink=True)


reset_scene()
setup_scene()
case_colour = (0.30, 0.37, 0.49) if REVISION in {"v17", "v18", "v19", "v20"} else (0.12, 0.15, 0.20)
case_material = material("PiFlex graphite", case_colour, metallic=0.05, roughness=0.38)
inspection_material = material("PiFlex inspection", (0.78, 0.22, 0.055), metallic=0.02, roughness=0.38)

render_model(
    LOCAL_STL,
    f"piflex-{REVISION}-{SHAPE_LABEL}-rear.png",
    case_material,
)
set_camera((330.0, 205.0, -350.0), (0.0, 0.0, -7.0), 385.0)
render_model(
    LOCAL_STL,
    f"piflex-{REVISION}-{SHAPE_LABEL}-three-quarter.png",
    case_material,
)
set_camera((350.0, -18.0, -88.0), (0.0, 0.0, -9.0), 190.0)
render_model(
    LOCAL_STL,
    f"piflex-{REVISION}-{SHAPE_LABEL}-side-profile.png",
    case_material,
)
set_camera((0.0, -350.0, -90.0), (0.0, 0.0, -9.0), 220.0)
render_model(
    LOCAL_STL,
    f"piflex-{REVISION}-{SHAPE_LABEL}-power-side.png",
    case_material,
)
set_camera((0.0, 245.0, -430.0), (0.0, 0.0, -7.0), 385.0)
render_model(
    OPEN_STL,
    f"piflex-{REVISION}-service-open-inspection.png",
    inspection_material,
)

print("PIFLEX_SERVICE_RENDERS", REVISION, OUT)
