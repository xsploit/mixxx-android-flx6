"""Assemble V21 from the frozen V19 scene with a wider tapered opening."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
import bmesh


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "piflex-codex-v19-polished-usb-routing.glb"
STRUCTURE = HERE / "piflex-codex-v21-bay-merged-structure.stl"
OUT_GLB = HERE / "piflex-codex-v21-bay-merged-usb-routing.glb"
OUT_STL = HERE / "piflex-codex-v21-bay-merged-fit-check.stl"
REPORT = HERE / "inspection-codex-v21-bay-merged-assembly.json"

OPENING_POINTS = (
    (-72.0, 56.0),
    (77.0, 56.0),
    (89.0, 40.0),
    (89.0, -40.0),
    (77.0, -56.0),
    (-72.0, -56.0),
    (-89.0, -40.0),
    (-89.0, 40.0),
)
MIN_SCREW_CLEARANCE = 7.161854508435643


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(obj):
    return [
        [round(min(corner[i] for corner in obj.bound_box), 4) for i in range(3)],
        [round(max(corner[i] for corner in obj.bound_box), 4) for i in range(3)],
    ]


def point_inside_polygon(point, polygon):
    x, y = point
    inside = False
    previous = polygon[-1]
    for current in polygon:
        x1, y1 = previous
        x2, y2 = current
        if (y1 > y) != (y2 > y):
            crossing_x = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < crossing_x:
                inside = not inside
        previous = current
    return inside


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))

shell = next(
    obj
    for obj in bpy.context.scene.objects
    if obj.name.startswith("Exact V18 screen case")
)
old_structure = next(
    obj
    for obj in bpy.context.scene.objects
    if obj.name.startswith("PiFlex Codex V19")
)
structure_matrix = old_structure.matrix_world.copy()
bpy.data.objects.remove(old_structure, do_unlink=True)

source_hash_before = sha256(SOURCE)
shell_bounds_before = bounds(shell)

# Split the existing V19 shell along every edge of the new convex opening, then
# delete only faces whose centres fall inside it. This preserves the complete
# exterior frame and avoids unreliable solid Booleans on the display mesh.
bm = bmesh.new()
bm.from_mesh(shell.data)
for index, point_a in enumerate(OPENING_POINTS):
    point_b = OPENING_POINTS[(index + 1) % len(OPENING_POINTS)]
    dx = point_b[0] - point_a[0]
    dy = point_b[1] - point_a[1]
    length = math.hypot(dx, dy)
    normal = (dy / length, -dx / length, 0.0)
    bmesh.ops.bisect_plane(
        bm,
        geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
        dist=0.001,
        plane_co=(point_a[0], point_a[1], 0.0),
        plane_no=normal,
    )

remove_faces = [
    face
    for face in bm.faces
    if point_inside_polygon(
        (face.calc_center_median().x, face.calc_center_median().y), OPENING_POINTS
    )
]
bmesh.ops.delete(bm, geom=remove_faces, context="FACES")
bm.to_mesh(shell.data)
bm.free()
shell.data.update()
shell.name = "Exact V19 screen case - bay merged screw-safe opening"

bpy.ops.wm.stl_import(filepath=str(STRUCTURE))
structure = bpy.context.object
structure.name = "PiFlex Codex V21 bay-merged rear and mount"
structure.matrix_world = structure_matrix

if bounds(shell) != shell_bounds_before:
    raise RuntimeError("V19 exterior screen-case bounds changed")
if sha256(SOURCE) != source_hash_before:
    raise RuntimeError("Frozen V19 source was modified")

bpy.ops.object.select_all(action="DESELECT")
shell.select_set(True)
structure.select_set(True)
bpy.context.view_layer.objects.active = shell
bpy.ops.export_scene.gltf(filepath=str(OUT_GLB), export_format="GLB", use_selection=True)
bpy.ops.wm.stl_export(filepath=str(OUT_STL), export_selected_objects=True)

report = {
    "design": "PiFlex Codex V21 bay-merged assembly",
    "source": SOURCE.name,
    "source_sha256": sha256(SOURCE),
    "source_unchanged": True,
    "outer_case_bounds_unchanged": True,
    "shell_local_bounds": shell_bounds_before,
    "opening_profile_mm": [list(point) for point in OPENING_POINTS],
    "opening_middle_width_mm": 178.0,
    "opening_top_bottom_span_mm": 149.0,
    "opening_max_height_mm": 112.0,
    "minimum_screw_tower_clearance_mm": round(MIN_SCREW_CLEARANCE, 3),
    "blue_screen_frame_cut_for_usb": False,
    "usb_routing": "two concealed tunnels beneath the intact blue frame",
    "preserved": [
        "V19 exterior screen-case bounds",
        "V19 inner recessed bevel outside the expanded opening",
        "four screen screw holes and guarded towers",
        "orange bay and angled side-wall transition",
        "six-slot rear grill",
        "top-facing USB-A ear openings",
        "FLX6 brackets and alignment",
    ],
    "visible_change": "opening reaches bay inner walls and removes most logo area",
    "production_gate": "physical fastener and USB lead fit-check",
}
REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
