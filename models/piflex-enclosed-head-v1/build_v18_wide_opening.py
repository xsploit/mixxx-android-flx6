"""Enlarge only the rear service opening in the last-known-good V18 GLB.

The V18 source is imported unchanged.  A centred rectangular cutter removes
the old opening plus both horizontal vent slots, stopping below the logo.
The mount/brackets and every other part of the screen case are untouched.
"""

from pathlib import Path
import hashlib
import json

import bpy
import bmesh


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "piflex-complete-shifted-enclosure-only-v18.glb"
OUT_GLB = HERE / "piflex-v18-wide-service-opening.glb"
OUT_STL = HERE / "piflex-v18-wide-service-opening.stl"
REPORT = HERE / "inspection-v18-wide-service-opening.json"

# Screen-shell local coordinates.  The exact shell is 253.154 x 171.542 mm.
# This is centred left/right, stays below the printed logo, encompasses the
# original rectangular opening and both horizontal vent lines, and remains
# well inside the four screen screws at x ~= +/-80 and z ~= +/-61 mm.
OPENING_WIDTH = 104.0
OPENING_BOTTOM = -46.0
OPENING_TOP = 46.0
OPENING_DEPTH = 20.0


def source_sha256():
    return hashlib.sha256(SOURCE.read_bytes()).hexdigest()


def mesh_digest(obj):
    digest = hashlib.sha256()
    for vertex in obj.data.vertices:
        digest.update(f"{vertex.co.x:.7f},{vertex.co.y:.7f},{vertex.co.z:.7f};".encode())
    for polygon in obj.data.polygons:
        digest.update((",".join(str(i) for i in polygon.vertices) + ";").encode())
    return digest.hexdigest()


def object_bounds(obj):
    return [
        [round(min(corner[i] for corner in obj.bound_box), 4) for i in range(3)],
        [round(max(corner[i] for corner in obj.bound_box), 4) for i in range(3)],
    ]


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))

shell = next(obj for obj in bpy.context.scene.objects if obj.name.startswith("Exact original 10-inch shell"))
mount = next(obj for obj in bpy.context.scene.objects if obj.name.startswith("PiFlex V18 shifted-placement"))

source_hash_before = source_sha256()
shell_bounds_before = object_bounds(shell)
mount_digest_before = mesh_digest(mount)

# Use the same bounded face-cut method that produced the known-good V18 shell.
# Splitting on all four boundaries first prevents partial triangles outside the
# requested opening from being deleted.  No replacement body is generated.
x_limit = OPENING_WIDTH / 2.0
bm = bmesh.new()
bm.from_mesh(shell.data)
for plane_co, plane_no in (
    ((x_limit, 0.0, 0.0), (1.0, 0.0, 0.0)),
    ((-x_limit, 0.0, 0.0), (1.0, 0.0, 0.0)),
    ((0.0, OPENING_TOP, 0.0), (0.0, 1.0, 0.0)),
    ((0.0, OPENING_BOTTOM, 0.0), (0.0, 1.0, 0.0)),
):
    bmesh.ops.bisect_plane(
        bm,
        geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
        dist=0.001,
        plane_co=plane_co,
        plane_no=plane_no,
    )
central_faces = []
for face in bm.faces:
    centre = face.calc_center_median()
    if -x_limit < centre.x < x_limit and OPENING_BOTTOM < centre.y < OPENING_TOP:
        central_faces.append(face)
bmesh.ops.delete(bm, geom=central_faces, context="FACES")
bm.to_mesh(shell.data)
bm.free()
shell.data.update()
shell.name = "Exact V18 screen case - rear opening enlarged only"

shell_bounds_after = object_bounds(shell)
mount_digest_after = mesh_digest(mount)
source_hash_after = source_sha256()

if shell_bounds_after != shell_bounds_before:
    raise RuntimeError(f"Outer case bounds changed: {shell_bounds_before} -> {shell_bounds_after}")
if mount_digest_after != mount_digest_before:
    raise RuntimeError("V18 mount/bracket geometry changed")
if source_hash_after != source_hash_before:
    raise RuntimeError("Last-known-good V18 source file changed")

# Preserve the source's two-object construction; do not union or rebuild it.
bpy.ops.object.select_all(action="DESELECT")
shell.select_set(True)
mount.select_set(True)
bpy.context.view_layer.objects.active = shell
bpy.ops.export_scene.gltf(filepath=str(OUT_GLB), export_format="GLB", use_selection=True)
bpy.ops.wm.stl_export(filepath=str(OUT_STL), export_selected_objects=True)

report = {
    "source": SOURCE.name,
    "source_sha256": source_hash_after,
    "source_unchanged": True,
    "mount_geometry_unchanged": True,
    "outer_case_bounds_unchanged": True,
    "shell_local_bounds": shell_bounds_after,
    "shell_dimensions": [round(value, 4) for value in shell.dimensions],
    "shell_matrix_world": [[round(value, 5) for value in row] for row in shell.matrix_world],
    "opening_local_mm": {
        "width": OPENING_WIDTH,
        "bottom": OPENING_BOTTOM,
        "top": OPENING_TOP,
        "depth": OPENING_DEPTH,
        "centered_x": True,
    },
    "scope": "one bounded rectangular face cut on the original V18 screen-shell object",
}
REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
