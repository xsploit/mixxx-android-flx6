"""Assemble the polished V19 structure with the V18 screen-case frame intact.

Only the enlarged central service opening is cut in the exact screen shell.
Both USB routes remain concealed tunnels in the structure beneath the blue
frame; the frame edge is never opened into an exposed channel.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy
import bmesh


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "piflex-complete-shifted-enclosure-only-v18.glb"
STRUCTURE = HERE / "piflex-codex-v19-polished-structure.stl"
OUT_GLB = HERE / "piflex-codex-v19-polished-usb-routing.glb"
OUT_STL = HERE / "piflex-codex-v19-polished-usb-routing-fit-check.stl"
REPORT = HERE / "inspection-codex-v19-polished-assembly.json"

SCREW_GUARD_RADIUS = 6.5
OPENING_LEFT = -77.657 + SCREW_GUARD_RADIUS
OPENING_RIGHT = 82.344 - SCREW_GUARD_RADIUS
OPENING_BOTTOM = -61.034 + SCREW_GUARD_RADIUS
OPENING_TOP = 60.768 - SCREW_GUARD_RADIUS


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mesh_digest(obj):
    digest = hashlib.sha256()
    for vertex in obj.data.vertices:
        digest.update(f"{vertex.co.x:.7f},{vertex.co.y:.7f},{vertex.co.z:.7f};".encode())
    for polygon in obj.data.polygons:
        digest.update((",".join(str(i) for i in polygon.vertices) + ";").encode())
    return digest.hexdigest()


def bounds(obj):
    return [
        [round(min(corner[i] for corner in obj.bound_box), 4) for i in range(3)],
        [round(max(corner[i] for corner in obj.bound_box), 4) for i in range(3)],
    ]


def face_in_rect(face, rect):
    x0, x1, y0, y1 = rect
    centre = face.calc_center_median()
    return x0 < centre.x < x1 and y0 < centre.y < y1


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))

shell = next(
    obj
    for obj in bpy.context.scene.objects
    if obj.name.startswith("Exact original 10-inch shell")
)
old_structure = next(
    obj
    for obj in bpy.context.scene.objects
    if obj.name.startswith("PiFlex V18 shifted-placement")
)
structure_matrix = old_structure.matrix_world.copy()
bpy.data.objects.remove(old_structure, do_unlink=True)

source_hash_before = sha256(SOURCE)
shell_bounds_before = bounds(shell)

# Enlarge only the central service opening. The surrounding blue frame stays
# continuous above the two hidden USB tunnels in the orange structure.
rectangles = [
    (OPENING_LEFT, OPENING_RIGHT, OPENING_BOTTOM, OPENING_TOP),
]

bm = bmesh.new()
bm.from_mesh(shell.data)
for x in sorted({value for rect in rectangles for value in rect[:2]}):
    bmesh.ops.bisect_plane(
        bm,
        geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
        dist=0.001,
        plane_co=(x, 0.0, 0.0),
        plane_no=(1.0, 0.0, 0.0),
    )
for y in sorted({value for rect in rectangles for value in rect[2:]}):
    bmesh.ops.bisect_plane(
        bm,
        geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
        dist=0.001,
        plane_co=(0.0, y, 0.0),
        plane_no=(0.0, 1.0, 0.0),
    )
remove_faces = [face for face in bm.faces if any(face_in_rect(face, rect) for rect in rectangles)]
bmesh.ops.delete(bm, geom=remove_faces, context="FACES")
bm.to_mesh(shell.data)
bm.free()
shell.data.update()
shell.name = "Exact V18 screen case - enlarged opening and dual USB passages"

bpy.ops.wm.stl_import(filepath=str(STRUCTURE))
structure = bpy.context.object
structure.name = "PiFlex Codex V19 polished V18 body and mount"
# CadQuery STL axes differ from Blender/glTF axes. Reuse the exact transform
# carried by the known-good V18 structure so no alignment is re-derived.
structure.matrix_world = structure_matrix

if bounds(shell) != shell_bounds_before:
    raise RuntimeError("Outer bounds of the exact screen case changed")
if sha256(SOURCE) != source_hash_before:
    raise RuntimeError("Last-known-good V18 source was modified")

bpy.ops.object.select_all(action="DESELECT")
shell.select_set(True)
structure.select_set(True)
bpy.context.view_layer.objects.active = shell
bpy.ops.export_scene.gltf(filepath=str(OUT_GLB), export_format="GLB", use_selection=True)
bpy.ops.wm.stl_export(filepath=str(OUT_STL), export_selected_objects=True)

report = {
    "design": "PiFlex Codex V19 polished USB-routing assembly",
    "source": SOURCE.name,
    "source_sha256": sha256(SOURCE),
    "source_unchanged": True,
    "outer_case_bounds_unchanged": True,
    "shell_local_bounds": shell_bounds_before,
    "service_opening_mm": [
        round(OPENING_RIGHT - OPENING_LEFT, 3),
        round(OPENING_TOP - OPENING_BOTTOM, 3),
    ],
    "blue_screen_frame_cut_for_usb": False,
    "usb_routing": "two concealed tunnels beneath the intact blue frame",
    "structure_mesh_digest": mesh_digest(structure),
    "structure_transform_reused_from_v18": True,
    "preserved": [
        "exact V18 exterior screen-case bounds",
        "four screen screw towers with 1 mm web",
        "FLX6 brackets and alignment",
        "six-slot rear grill",
        "two top-facing USB-A ear openings",
        "continuous blue screen-case frame above USB tunnels",
    ],
    "filled": [
        "old Pi connector openings",
        "old micro-SD opening",
        "stepped rear-case scars",
    ],
    "production_gate": "fit-check female USB-A body dimensions and cable bend radius",
}
REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
