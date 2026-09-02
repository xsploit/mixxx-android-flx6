"""Create topology-checked print parts from the approved V21 geometry.

The V21 GLB is a visual assembly whose display shell was edited by face
deletion. This script reapplies the approved opening to the original watertight
MakerWorld shell with the Manifold mesh kernel, registers the repaired shell
against the V21 rear/mount, and exports separate and fused print candidates.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import bpy
import bmesh
import numpy as np
import trimesh


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW_SHELL = (
    ROOT
    / "models"
    / "makerworld-3116241"
    / "stl"
    / "screen-case"
    / "10Inch_TouchDisplay2_DesktopCase_Shell.stl"
)
PRINT_VERSION = os.environ.get("PIFLEX_PRINT_VERSION", "v22")
ASSEMBLY = HERE / os.environ.get(
    "PIFLEX_ASSEMBLY", "piflex-codex-v21-bay-merged-usb-routing.glb"
)
REAR_OBJECT_PREFIX = os.environ.get("PIFLEX_REAR_PREFIX", "PiFlex Codex V21")
APPROVED_GEOMETRY = os.environ.get(
    "PIFLEX_APPROVED_GEOMETRY",
    "V21 bay-merged opening on frozen V19 visual form",
)
TUNNEL_VOIDS_NAME = os.environ.get("PIFLEX_TUNNEL_VOIDS")
TUNNEL_VOIDS = HERE / TUNNEL_VOIDS_NAME if TUNNEL_VOIDS_NAME else None

OUT_SHELL = HERE / f"piflex-codex-{PRINT_VERSION}-printable-screen-shell.stl"
OUT_REAR_MOUNT = HERE / f"piflex-codex-{PRINT_VERSION}-printable-rear-mount.stl"
OUT_REGISTERED_SHELL = HERE / f"piflex-codex-{PRINT_VERSION}-registered-screen-shell.stl"
OUT_REGISTERED = HERE / f"piflex-codex-{PRINT_VERSION}-printable-two-part-fit-check.stl"
OUT_MONOLITHIC = HERE / f"piflex-codex-{PRINT_VERSION}-printable-monolithic.stl"
OUT_MONOLITHIC_3MF = HERE / f"piflex-codex-{PRINT_VERSION}-printable-monolithic.3mf"
REPORT = HERE / f"inspection-codex-{PRINT_VERSION}-print-parts.json"

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
FUSION_SEAM_RELIEF_MM = float(os.environ.get("PIFLEX_FUSION_SEAM_RELIEF", "0.10"))
FUSION_JITTER_WORLD_MM = np.array(
    [
        float(value)
        for value in os.environ.get(
            "PIFLEX_FUSION_JITTER_WORLD", "0.0,0.0,0.0"
        ).split(",")
    ],
    dtype=float,
)
if FUSION_JITTER_WORLD_MM.shape != (3,):
    raise RuntimeError("PIFLEX_FUSION_JITTER_WORLD must contain three numbers")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mesh_report(mesh):
    return {
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "volume": bool(mesh.is_volume),
        "faces": int(len(mesh.faces)),
        "vertices": int(len(mesh.vertices)),
        "volume_mm3": round(float(mesh.volume), 3),
        "bounds_mm": [[round(float(v), 4) for v in row] for row in mesh.bounds],
    }


def opening_cutter():
    point_count = len(OPENING_POINTS)
    vertices = (
        [(x, y, -20.0) for x, y in OPENING_POINTS]
        + [(x, y, 20.0) for x, y in OPENING_POINTS]
    )
    faces = []
    # Convex cap fans, then triangulated walls.
    for index in range(1, point_count - 1):
        faces.append((0, index + 1, index))
        faces.append((point_count, point_count + index, point_count + index + 1))
    for index in range(point_count):
        nxt = (index + 1) % point_count
        faces.extend(
            (
                (index, nxt, point_count + nxt),
                (index, point_count + nxt, point_count + index),
            )
        )
    cutter = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    if cutter.volume < 0:
        cutter.invert()
    if not cutter.is_volume:
        raise RuntimeError("Opening cutter is not a valid closed volume")
    return cutter


def select_only(*objects):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]


def export_stl(path, *objects):
    select_only(*objects)
    bpy.ops.wm.stl_export(filepath=str(path), export_selected_objects=True)


def blender_topology(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    result = {
        "boundary_edges": sum(edge.is_boundary for edge in bm.edges),
        "non_manifold_edges": sum(not edge.is_manifold for edge in bm.edges),
    }
    bm.free()
    result["manifold"] = result["non_manifold_edges"] == 0
    return result


# 1. Apply the approved V21 cut to the authoritative watertight shell.
raw_shell = trimesh.load_mesh(RAW_SHELL, process=True)
if not raw_shell.is_volume:
    raise RuntimeError("Authoritative raw screen shell is not a closed volume")
raw_hash = sha256(RAW_SHELL)
printable_shell = trimesh.boolean.difference(
    [raw_shell, opening_cutter()], engine="manifold", check_volume=True
)
if not printable_shell.is_volume:
    raise RuntimeError("Manifold cut did not produce a closed screen-shell volume")
if not (abs(printable_shell.bounds - raw_shell.bounds) < 0.001).all():
    raise RuntimeError("Approved opening changed the exterior screen-shell bounds")
printable_shell.export(OUT_SHELL)

# 2. Recover the exact V21 registration and replace only its visualization
# shell with the repaired solid shell.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ASSEMBLY))
visual_shell = next(
    obj for obj in bpy.context.scene.objects if obj.name.startswith("Exact V19 screen case")
)
rear_mount = next(
    obj
    for obj in bpy.context.scene.objects
    if obj.name.startswith(REAR_OBJECT_PREFIX)
)
shell_matrix = visual_shell.matrix_world.copy()
bpy.data.objects.remove(visual_shell, do_unlink=True)

bpy.ops.wm.stl_import(filepath=str(OUT_SHELL))
registered_shell = bpy.context.object
registered_shell.name = "PiFlex V22 registered printable screen shell"
registered_shell.matrix_world = shell_matrix

# Bake both exact assembly transforms into standalone printable meshes.
select_only(registered_shell)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
select_only(rear_mount)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

shell_blender_topology = blender_topology(registered_shell)
if not shell_blender_topology["manifold"]:
    raise RuntimeError(f"Registered screen shell opened: {shell_blender_topology}")

export_stl(OUT_REGISTERED_SHELL, registered_shell)
export_stl(OUT_REAR_MOUNT, rear_mount)

# 3. Validate the exported registered parts independently of Blender.
registered_shell_mesh = trimesh.load_mesh(OUT_REGISTERED_SHELL, process=True)
rear_mount_mesh = trimesh.load_mesh(OUT_REAR_MOUNT, process=True)
if rear_mount_mesh.is_watertight and rear_mount_mesh.volume < 0:
    # The exact assembly registration contains a reflection, so reverse the
    # transformed STL's face winding while preserving every coordinate.
    rear_mount_mesh.invert()
    rear_mount_mesh.export(OUT_REAR_MOUNT)
if not registered_shell_mesh.is_volume:
    raise RuntimeError("Exported registered screen shell is not a volume")
if not rear_mount_mesh.is_volume:
    raise RuntimeError("Exported rear/mount is not a volume")

# Re-export the two-part inspection file from the independently validated,
# positively wound meshes rather than Blender's reflected triangle stream.
two_part_mesh = trimesh.util.concatenate(
    [registered_shell_mesh.copy(), rear_mount_mesh.copy()]
)
two_part_mesh.export(OUT_REGISTERED)

# 4. Produce a monolithic enclosure only when the two registered solids truly
# overlap and the Manifold union survives an STL round trip as a closed volume.
# A 0.10 mm fusion-only relief moves the rear body away from exactly coplanar
# contact; this is below a normal FDM layer height and prevents zero-area seam
# triangles without altering the two-part fit-check registration.
fusion_normal = np.array(
    [shell_matrix[0][2], shell_matrix[1][2], shell_matrix[2][2]], dtype=float
)
fusion_normal /= np.linalg.norm(fusion_normal)
fusion_translation = (
    -fusion_normal * FUSION_SEAM_RELIEF_MM + FUSION_JITTER_WORLD_MM
)
fusion_rear_mesh = rear_mount_mesh.copy()
fusion_rear_mesh.apply_translation(fusion_translation)
intersection = trimesh.boolean.intersection(
    [registered_shell_mesh, fusion_rear_mesh], engine="manifold", check_volume=True
)
intersection_volume = abs(float(intersection.volume)) if len(intersection.faces) else 0.0
monolithic_exported = False
monolithic_report = None
monolithic_3mf_report = None
tunnel_validation = None
if intersection_volume > 0.1:
    monolithic = trimesh.boolean.union(
        [registered_shell_mesh, fusion_rear_mesh], engine="manifold", check_volume=True
    )
    monolithic.export(OUT_MONOLITHIC)
    monolithic_disk = trimesh.load_mesh(OUT_MONOLITHIC, process=True)
    degenerate_faces = int(
        len(monolithic_disk.faces) - monolithic_disk.nondegenerate_faces().sum()
    )
    duplicate_faces = int(
        len(monolithic_disk.faces) - monolithic_disk.unique_faces().sum()
    )
    monolithic_report = {
        **mesh_report(monolithic_disk),
        "degenerate_faces": degenerate_faces,
        "duplicate_faces": duplicate_faces,
        "round_trip_validated": True,
    }
    monolithic_exported = (
        monolithic_disk.is_volume
        and degenerate_faces == 0
        and duplicate_faces == 0
    )
    if monolithic_exported:
        monolithic_disk.export(OUT_MONOLITHIC_3MF)
        monolithic_3mf = trimesh.load(
            OUT_MONOLITHIC_3MF, force="scene", process=True
        ).to_geometry()
        monolithic_3mf_report = {
            **mesh_report(monolithic_3mf),
            "round_trip_validated": True,
        }
        if not monolithic_3mf.is_volume:
            raise RuntimeError("3MF round trip did not remain a closed volume")
if not monolithic_exported and OUT_MONOLITHIC.exists():
    OUT_MONOLITHIC.unlink()
if not monolithic_exported and OUT_MONOLITHIC_3MF.exists():
    OUT_MONOLITHIC_3MF.unlink()

# Optional functional-route validation. The registered void reference is moved
# by the same fusion-only relief as the rear body, then intersected with the
# actual disk-round-tripped monolithic mesh. Any meaningful overlap means the
# route was silently plugged by the screen shell, yoke, or final union.
if TUNNEL_VOIDS is not None and not monolithic_exported:
    raise RuntimeError("Cannot validate USB tunnels without a monolithic export")
if TUNNEL_VOIDS is not None:
    tunnel_mesh = trimesh.load_mesh(TUNNEL_VOIDS, process=True)
    route_reports = []
    for index, route in enumerate(tunnel_mesh.split(only_watertight=False)):
        if route.volume < 0:
            route.invert()
        shell_block = trimesh.boolean.intersection(
            [route, registered_shell_mesh], engine="manifold", check_volume=True
        )
        rear_block = trimesh.boolean.intersection(
            [route, rear_mount_mesh], engine="manifold", check_volume=True
        )
        fused_route = route.copy()
        fused_route.apply_translation(fusion_translation)
        final_block = trimesh.boolean.intersection(
            [fused_route, monolithic_disk], engine="manifold", check_volume=True
        )
        route_reports.append(
            {
                "route": index,
                "void_volume_mm3": round(abs(float(route.volume)), 6),
                "blue_shell_blocked_mm3": round(
                    abs(float(shell_block.volume)) if len(shell_block.faces) else 0.0,
                    6,
                ),
                "rear_mount_blocked_mm3": round(
                    abs(float(rear_block.volume)) if len(rear_block.faces) else 0.0,
                    6,
                ),
                "monolithic_blocked_mm3": round(
                    abs(float(final_block.volume)) if len(final_block.faces) else 0.0,
                    6,
                ),
            }
        )
    maximum_block = max(
        report["monolithic_blocked_mm3"] for report in route_reports
    )
    tunnel_validation = {
        "reference_file": TUNNEL_VOIDS.name,
        "routes": route_reports,
        "maximum_allowed_numerical_overlap_mm3": 0.02,
        "passed": maximum_block <= 0.02,
    }
    if not tunnel_validation["passed"]:
        raise RuntimeError(f"Final union obstructed a USB tunnel: {tunnel_validation}")

if sha256(RAW_SHELL) != raw_hash:
    raise RuntimeError("Authoritative raw screen shell changed during build")

report = {
    "design": f"PiFlex Codex {PRINT_VERSION.upper()} topology-checked print parts",
    "approved_geometry": APPROVED_GEOMETRY,
    "assembly_source": ASSEMBLY.name,
    "raw_shell": str(RAW_SHELL.relative_to(ROOT)),
    "raw_shell_sha256": raw_hash,
    "opening_profile_mm": [list(point) for point in OPENING_POINTS],
    "screen_shell_local": {
        "file": OUT_SHELL.name,
        **mesh_report(printable_shell),
    },
    "screen_shell_registered": {
        "file": OUT_REGISTERED_SHELL.name,
        **mesh_report(registered_shell_mesh),
    },
    "rear_mount": {
        "file": OUT_REAR_MOUNT.name,
        **mesh_report(rear_mount_mesh),
    },
    "two_part_fit_check": OUT_REGISTERED.name,
    "fusion_seam_relief_mm": FUSION_SEAM_RELIEF_MM,
    "fusion_seam_relief_direction_world": [
        round(float(value), 7) for value in -fusion_normal
    ],
    "fusion_jitter_world_mm": [
        round(float(value), 7) for value in FUSION_JITTER_WORLD_MM
    ],
    "fusion_total_translation_world_mm": [
        round(float(value), 7) for value in fusion_translation
    ],
    "registered_part_overlap_mm3": round(intersection_volume, 3),
    "monolithic": {
        "file": OUT_MONOLITHIC.name if monolithic_exported else None,
        "3mf_file": OUT_MONOLITHIC_3MF.name if monolithic_exported else None,
        "exported": monolithic_exported,
        "mesh": monolithic_report,
        "3mf_mesh": monolithic_3mf_report,
    },
    "usb_tunnel_validation": tunnel_validation,
    "nominal_designed_walls_mm": {
        "rear_bay": 3.0,
        "USB_ears": 3.2,
        "screw_tower_web": 1.0,
    },
    "physical_fit_gates": [
        "screen screw diameter and engagement",
        "female USB-A panel body dimensions",
        "USB cable bend radius",
        "printer-specific clearance and shrink compensation",
    ],
}
REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
