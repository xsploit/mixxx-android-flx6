"""Render the corrected V18 case from its real front and rear sides."""

from pathlib import Path
import math

import bpy
from mathutils import Matrix, Vector


OUT = Path(r"C:\Users\SUBSECT\Documents\Codex\2026-08-18\hey-i-need-you-to-research\models\piflex-enclosed-head-v1")
MODEL = OUT / "piflex-v18-cleaned-one-piece.stl"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=str(MODEL))
case = bpy.context.object
case.name = "Corrected V18 complete printable case"

mat = bpy.data.materials.new("Blue-grey print")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.075, 0.22, 0.44, 1.0)
bsdf.inputs["Roughness"].default_value = 0.3
case.data.materials.append(mat)

points = [case.matrix_world @ Vector(corner) for corner in case.bound_box]
low = Vector(tuple(min(p[i] for p in points) for i in range(3)))
high = Vector(tuple(max(p[i] for p in points) for i in range(3)))
centre = (low + high) * 0.5

theta = math.radians(25.0)
screen_up = Vector((-math.cos(theta), math.sin(theta), 0.0)).normalized()
screen_normal = Vector((math.sin(theta), math.cos(theta), 0.0)).normalized()
screen_right = Vector((0.0, 0.0, 1.0))

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1800
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.view_settings.exposure = 1.8
scene.world = bpy.data.worlds.new("Light neutral studio")
scene.world.use_nodes = True
background = scene.world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value = (0.09, 0.11, 0.15, 1.0)
background.inputs["Strength"].default_value = 0.8


def area(name, offset, energy, size):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = centre + Vector(offset)
    obj.rotation_euler = (centre - obj.location).to_track_quat("-Z", "Y").to_euler()


area("Key", (-280, 360, 260), 2100, 260)
area("Fill", (300, -240, -220), 1500, 220)
area("Rim", (-220, -280, 240), 1300, 180)

bpy.ops.object.camera_add()
camera = bpy.context.object
camera.data.type = "ORTHO"
camera.data.ortho_scale = 400.0
camera.data.clip_end = 3000.0
scene.camera = camera


def set_camera_basis(position_direction, up_direction):
    camera.location = centre + position_direction.normalized() * 600.0
    local_z = position_direction.normalized()
    local_y = up_direction.normalized()
    local_x = local_y.cross(local_z).normalized()
    rotation = Matrix(
        (
            (local_x.x, local_y.x, local_z.x),
            (local_x.y, local_y.y, local_z.y),
            (local_x.z, local_y.z, local_z.z),
        )
    ).to_4x4()
    rotation.translation = camera.location
    camera.matrix_world = rotation


def render(filename, direction, up=screen_up, scale=400.0):
    camera.data.ortho_scale = scale
    set_camera_basis(direction, up)
    scene.render.filepath = str(OUT / filename)
    bpy.ops.render.render(write_still=True)


# +normal is the open/front side of the original MakerWorld case; -normal is
# its flat rear plate and the new rounded Pi service bay.
render("piflex-v18-cleaned-true-front.png", screen_normal)
render("piflex-v18-cleaned-true-rear.png", -screen_normal)

# Rear three-quarter view, rolled so the screen remains naturally horizontal.
rear_three_quarter = (-screen_normal * 0.92 + screen_up * 0.34 - screen_right * 0.42)
render("piflex-v18-cleaned-rear-three-quarter.png", rear_three_quarter, scale=500.0)

print("PIFLEX_V18_CLEANED_RENDERED")
