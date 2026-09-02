"""Fuse V20 to the exact shell while retaining its screw-bearing first layer."""

from pathlib import Path
import json
import math

import bpy
import bmesh
from mathutils import Matrix


ROOT = Path(r"C:\Users\SUBSECT\Documents\Codex\2026-08-18\hey-i-need-you-to-research")
OUT = ROOT / "models" / "piflex-enclosed-head-v1"
SCREEN_SHELL = ROOT / "models" / "makerworld-3116241" / "stl" / "screen-case" / "10Inch_TouchDisplay2_DesktopCase_Shell.stl"
STRUCTURE = OUT / "piflex-complete-v9-shifted-mount-v20.stl"
CUTTER = OUT / "piflex-v20-original-pi-layer-cutter-local.stl"
SCREEN_HEIGHT = 171.542
SCREEN_DEPTH = 13.680


def select_only(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_boolean(target, tool, operation, label):
    select_only(target)
    modifier = target.modifiers.new(label, "BOOLEAN")
    modifier.operation = operation
    modifier.solver = "EXACT"
    modifier.object = tool
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(tool, do_unlink=True)


def mesh_report(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    report = {
        "vertices": len(bm.verts),
        "edges": len(bm.edges),
        "faces": len(bm.faces),
        "boundary_edges": sum(1 for edge in bm.edges if edge.is_boundary),
        "non_manifold_edges": sum(1 for edge in bm.edges if not edge.is_manifold),
    }
    bm.free()
    return report


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=str(SCREEN_SHELL))
shell = bpy.context.object
shell.name = "Exact 10-inch shell with retained screw plate"
bpy.ops.wm.stl_import(filepath=str(CUTTER))
cutter = bpy.context.object
apply_boolean(shell, cutter, "DIFFERENCE", "Modestly enlarge original Pi opening")

theta = math.radians(25.0)
u = (-math.cos(theta), math.sin(theta))
n = (math.sin(theta), math.cos(theta))
origin = (-2.0, 56.0)
centre = (
    origin[0] + u[0] * (SCREEN_HEIGHT / 2.0),
    origin[1] + u[1] * (SCREEN_HEIGHT / 2.0),
)
local_to_bracket = Matrix(
    (
        (0.0, u[0], n[0], centre[0]),
        (0.0, u[1], n[1], centre[1]),
        (1.0, 0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )
)
shell.matrix_world = local_to_bracket @ Matrix.Translation((0.0, 0.0, SCREEN_DEPTH / 2.0))
select_only(shell)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

bpy.ops.wm.stl_import(filepath=str(STRUCTURE))
structure = bpy.context.object
apply_boolean(shell, structure, "UNION", "Fuse V20 clean structure")

select_only(shell)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.001)
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode="OBJECT")
shell.name = "PiFlex one-piece clean protective case V20"

report = mesh_report(shell)
report.update(
    {
        "design": "PiFlex one-piece clean protective case V20",
        "construction": "first screw-bearing layer retained; center opening modestly enlarged; V20 structure fused",
        "screen_screw_bosses_preserved": True,
        "enlarged_opening_mm": [118.0, 88.0],
    }
)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "piflex-one-piece-clean-case-v20.blend"))
bpy.ops.wm.stl_export(filepath=str(OUT / "piflex-one-piece-clean-case-v20.stl"), export_selected_objects=True)
bpy.ops.export_scene.gltf(filepath=str(OUT / "piflex-one-piece-clean-case-v20.glb"), export_format="GLB", use_selection=True)
(OUT / "inspection-one-piece-v20.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("PIFLEX_ONE_PIECE_V20", json.dumps(report, sort_keys=True))
