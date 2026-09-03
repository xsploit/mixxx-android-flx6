"""Package the verified V26 printable parts as a coloured inspection GLB."""

from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
SHELL = HERE / "piflex-codex-v26-registered-screen-shell.stl"
REAR = HERE / "piflex-codex-v26-printable-rear-mount.stl"
OUTPUT = HERE / "piflex-codex-v26-printable-inspection.glb"


def material(name, colour):
    value = bpy.data.materials.new(name)
    value.diffuse_color = (*colour, 1.0)
    return value


bpy.ops.wm.read_factory_settings(use_empty=True)
blue = material("Original screen shell with straight tunnel cuts", (0.02, 0.28, 0.43))
orange = material("Rear enclosure and FLX6 mount", (0.72, 0.24, 0.02))

for path, name, surface in (
    (SHELL, "V26 blue screen shell", blue),
    (REAR, "V26 rear enclosure and mount", orange),
):
    bpy.ops.wm.stl_import(filepath=str(path))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(surface)

bpy.ops.export_scene.gltf(
    filepath=str(OUTPUT),
    export_format="GLB",
    use_selection=False,
)
print(f"Exported {OUTPUT.name}")
