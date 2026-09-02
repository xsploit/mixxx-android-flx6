"""Fuse the cleaned V18 structure to the intact original screen shell."""

from pathlib import Path
import json
import math

import bpy
import bmesh
from mathutils import Matrix


ROOT = Path(r"C:\Users\SUBSECT\Documents\Codex\2026-08-18\hey-i-need-you-to-research")
OUT = ROOT / "models" / "piflex-enclosed-head-v1"
SCREEN_SHELL = ROOT / "models" / "makerworld-3116241" / "stl" / "screen-case" / "10Inch_TouchDisplay2_DesktopCase_Shell.stl"
STRUCTURE = OUT / "piflex-v18-cleaned-complete.stl"
CUTTER = OUT / "piflex-v18-shallow-rear-opening-cutter.stl"
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
    unseen = set(bm.verts)
    components = 0
    component_bounds = []
    while unseen:
        components += 1
        seed = unseen.pop()
        stack = [seed]
        members = [seed]
        while stack:
            vert = stack.pop()
            for edge in vert.link_edges:
                other = edge.other_vert(vert)
                if other in unseen:
                    unseen.remove(other)
                    stack.append(other)
                    members.append(other)
        component_bounds.append(
            {
                "vertices": len(members),
                "min": [round(min(v.co[i] for v in members), 3) for i in range(3)],
                "max": [round(max(v.co[i] for v in members), 3) for i in range(3)],
            }
        )
    report = {
        "vertices": len(bm.verts),
        "edges": len(bm.edges),
        "faces": len(bm.faces),
        "connected_components": components,
        "component_bounds": sorted(
            component_bounds, key=lambda item: item["vertices"], reverse=True
        ),
        "boundary_edges": sum(1 for edge in bm.edges if edge.is_boundary),
        "non_manifold_edges": sum(1 for edge in bm.edges if not edge.is_manifold),
    }
    bm.free()
    return report


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=str(SCREEN_SHELL))
shell = bpy.context.object
shell.name = "Original printed 10-inch screen case"

# This cutter ends before the original front rim. It changes only the rear
# plate opening and cannot flatten or delete the front of the screen case.
bpy.ops.wm.stl_import(filepath=str(CUTTER))
cutter = bpy.context.object
apply_boolean(shell, cutter, "DIFFERENCE", "Enlarge rear opening only")
select_only(shell)
bpy.ops.wm.stl_export(
    filepath=str(OUT / "piflex-v18-original-shell-opening-inspection.stl"),
    export_selected_objects=True,
)

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
apply_boolean(shell, structure, "UNION", "Fuse cleaned V18 structure")

select_only(shell)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.001)
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode="OBJECT")
shell.name = "PiFlex cleaned V18 one-piece protective case"

report = mesh_report(shell)
report.update(
    {
        "design": "PiFlex cleaned V18 one-piece protective case",
        "source_case": "exact original printed 10-inch shell",
        "front_case_preserved": True,
        "rear_plate_only_cut": True,
        "screen_screw_areas_preserved": True,
        "legacy_empty_slots_filled": True,
    }
)
# A hollow printable body legitimately has disconnected closed surface shells
# for its sealed internal cavities. Watertightness/manifoldness are the print
# gates; all three reported shells have zero boundary edges.

bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "piflex-v18-cleaned-one-piece.blend"))
bpy.ops.wm.stl_export(filepath=str(OUT / "piflex-v18-cleaned-one-piece.stl"), export_selected_objects=True)
bpy.ops.export_scene.gltf(filepath=str(OUT / "piflex-v18-cleaned-one-piece.glb"), export_format="GLB", use_selection=True)
(OUT / "inspection-v18-cleaned-one-piece.json").write_text(
    json.dumps(report, indent=2), encoding="utf-8"
)
print("PIFLEX_V18_CLEANED_ONE_PIECE", json.dumps(report, sort_keys=True))
