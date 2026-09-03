"""Package the V34 printable parts as a coloured inspection GLB."""

from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
SHELL = HERE / "piflex-codex-v34-registered-screen-shell.stl"
REAR = HERE / "piflex-codex-v34-printable-rear-mount.stl"
OUTPUT = HERE / "piflex-codex-v34-printable-inspection.glb"
COLOURED_OUTPUT = HERE / "piflex-codex-v34-coloured-inspection.glb"


def material(name, colour):
    value = bpy.data.materials.new(name)
    value.diffuse_color = (*colour, 1.0)
    value.use_nodes = True
    principled = value.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (*colour, 1.0)
    principled.inputs["Roughness"].default_value = 0.42
    principled.inputs["Metallic"].default_value = 0.0
    return value


bpy.ops.wm.read_factory_settings(use_empty=True)
blue = material("Original screen shell with 5 mm roof bridges", (0.02, 0.28, 0.43))
orange = material("Rear enclosure with fully hollow USB ears", (0.72, 0.24, 0.02))
for path, name, surface in (
    (SHELL, "V34 blue screen shell", blue),
    (REAR, "V34 rear enclosure and mount", orange),
):
    bpy.ops.wm.stl_import(filepath=str(path))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(surface)
for output in (OUTPUT, COLOURED_OUTPUT):
    bpy.ops.export_scene.gltf(
        filepath=str(output),
        export_format="GLB",
        export_materials="EXPORT",
    )
    print(f"Exported {output.name}")
