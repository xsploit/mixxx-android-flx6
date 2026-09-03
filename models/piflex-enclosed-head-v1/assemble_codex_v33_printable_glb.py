"""Package the V33 printable parts as a coloured inspection GLB."""

from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
SHELL = HERE / "piflex-codex-v33-registered-screen-shell.stl"
REAR = HERE / "piflex-codex-v33-printable-rear-mount.stl"
OUTPUT = HERE / "piflex-codex-v33-printable-inspection.glb"


def material(name, colour):
    value = bpy.data.materials.new(name)
    value.diffuse_color = (*colour, 1.0)
    return value


bpy.ops.wm.read_factory_settings(use_empty=True)
blue = material("Original screen shell with 5 mm roof bridges", (0.02, 0.28, 0.43))
orange = material("Rear enclosure with full-depth USB ear pockets", (0.72, 0.24, 0.02))
for path, name, surface in (
    (SHELL, "V33 blue screen shell", blue),
    (REAR, "V33 rear enclosure and mount", orange),
):
    bpy.ops.wm.stl_import(filepath=str(path))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(surface)
bpy.ops.export_scene.gltf(filepath=str(OUTPUT), export_format="GLB")
print(f"Exported {OUTPUT.name}")
