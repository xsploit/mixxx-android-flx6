"""Enlarge only the rear service opening in the last-known-good V18 GLB.

The V18 source is imported unchanged. A screw-safe rectangular face cut grows
the service opening to within 1 mm of the four existing screw towers. The
mount, ears, concealed USB channels and every outer case surface stay intact.
"""

from pathlib import Path
import hashlib
import json

import bpy
import bmesh


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "piflex-complete-shifted-enclosure-only-v18.glb"
OUT_GLB = HERE / "piflex-codex-v18-usb-routing.glb"
OUT_STL = HERE / "piflex-codex-v18-usb-routing-fit-check.stl"
REPORT = HERE / "inspection-codex-v18-usb-routing.json"

# Screen-shell local coordinates.  The exact shell is 253.154 x 171.542 mm.
# Enlarge to the four original screen-screw centres, retaining the complete
# 5.5 mm screw towers plus 1.0 mm of structural web around each one.  This is
# deliberately the last sensible increment: widening farther would cut into
# the screw supports that attach the case to the display.
SCREW_GUARD_RADIUS = 6.5
OPENING_LEFT = -77.657 + SCREW_GUARD_RADIUS
OPENING_RIGHT = 82.344 - SCREW_GUARD_RADIUS
OPENING_BOTTOM = -61.034 + SCREW_GUARD_RADIUS
OPENING_TOP = 60.768 - SCREW_GUARD_RADIUS
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
bm = bmesh.new()
bm.from_mesh(shell.data)
for plane_co, plane_no in (
    ((OPENING_RIGHT, 0.0, 0.0), (1.0, 0.0, 0.0)),
    ((OPENING_LEFT, 0.0, 0.0), (1.0, 0.0, 0.0)),
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
    if OPENING_LEFT < centre.x < OPENING_RIGHT and OPENING_BOTTOM < centre.y < OPENING_TOP:
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
        "left": OPENING_LEFT,
        "right": OPENING_RIGHT,
        "width": round(OPENING_RIGHT - OPENING_LEFT, 3),
        "bottom": OPENING_BOTTOM,
        "top": OPENING_TOP,
        "height": round(OPENING_TOP - OPENING_BOTTOM, 3),
        "depth": OPENING_DEPTH,
        "centre": [
            round((OPENING_LEFT + OPENING_RIGHT) / 2.0, 3),
            round((OPENING_BOTTOM + OPENING_TOP) / 2.0, 3),
        ],
    },
    "screw_guard_radius_mm": SCREW_GUARD_RADIUS,
    "remaining_structural_web_outside_screw_tower_mm": 1.0,
    "existing_v18_mount_features_preserved": [
        "two hollow 38 x 70 mm USB ears",
        "two top-facing 16.4 x 9.2 mm USB openings",
        "two concealed 18 mm high x 6.8 mm deep ear-to-cavity channels",
    ],
    "scope": "one screw-safe rectangular face cut on the original V18 screen-shell object; V18 mount unchanged",
}
REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
