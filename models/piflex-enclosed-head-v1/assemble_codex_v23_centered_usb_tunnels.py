"""Replace only the V21 rear/mount with the corrected V23 tunnel body."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
DESIGN_VERSION = os.environ.get("PIFLEX_TUNNEL_VERSION", "v23")
DESIGN_SLUG = os.environ.get("PIFLEX_TUNNEL_SLUG", "centered-usb-tunnels")
TUNNEL_CENTRE_Y = float(os.environ.get("PIFLEX_TUNNEL_CENTRE_Y", "0.0"))
EAR_CENTRED_DOGLEG = os.environ.get("PIFLEX_EAR_CENTRED_DOGLEG") == "1"
SOURCE = HERE / "piflex-codex-v21-bay-merged-usb-routing.glb"
STEM = f"piflex-codex-{DESIGN_VERSION}-{DESIGN_SLUG}"
STRUCTURE = HERE / f"{STEM}-structure.stl"
TUNNEL_VOIDS = HERE / f"piflex-codex-{DESIGN_VERSION}-usb-tunnel-voids-structure-coordinates.stl"
OUT_GLB = HERE / f"{STEM}.glb"
OUT_STL = HERE / f"{STEM}-fit-check.stl"
OUT_REGISTERED_TUNNEL_VOIDS = HERE / f"piflex-codex-{DESIGN_VERSION}-usb-tunnel-voids-registered.stl"
REPORT = HERE / f"inspection-codex-{DESIGN_VERSION}-{DESIGN_SLUG}-assembly.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def world_bounds(obj):
    corners = [obj.matrix_world @ Vector(obj.bound_box[index]) for index in range(8)]
    return [
        [round(min(corner[axis] for corner in corners), 4) for axis in range(3)],
        [round(max(corner[axis] for corner in corners), 4) for axis in range(3)],
    ]


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))

shell = next(
    obj
    for obj in bpy.context.scene.objects
    if obj.name.startswith("Exact V19 screen case")
)
old_structure = next(
    obj
    for obj in bpy.context.scene.objects
    if obj.name.startswith("PiFlex Codex V21")
)
structure_matrix = old_structure.matrix_world.copy()
shell_bounds_before = world_bounds(shell)
source_hash_before = sha256(SOURCE)
bpy.data.objects.remove(old_structure, do_unlink=True)

bpy.ops.wm.stl_import(filepath=str(STRUCTURE))
structure = bpy.context.object
structure.name = f"PiFlex Codex {DESIGN_VERSION.upper()} enclosed USB tunnels rear and mount"
structure.matrix_world = structure_matrix

bpy.ops.wm.stl_import(filepath=str(TUNNEL_VOIDS))
tunnel_voids = bpy.context.object
tunnel_voids.name = f"PiFlex Codex {DESIGN_VERSION.upper()} registered USB tunnel voids"
tunnel_voids.matrix_world = structure_matrix
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.select_all(action="DESELECT")
tunnel_voids.select_set(True)
bpy.context.view_layer.objects.active = tunnel_voids
bpy.ops.wm.stl_export(
    filepath=str(OUT_REGISTERED_TUNNEL_VOIDS), export_selected_objects=True
)
bpy.data.objects.remove(tunnel_voids, do_unlink=True)

if world_bounds(shell) != shell_bounds_before:
    raise RuntimeError("V21 screen shell registration changed")
if sha256(SOURCE) != source_hash_before:
    raise RuntimeError("Frozen V21 source was modified")

bpy.ops.object.select_all(action="DESELECT")
shell.select_set(True)
structure.select_set(True)
bpy.context.view_layer.objects.active = shell
bpy.ops.export_scene.gltf(filepath=str(OUT_GLB), export_format="GLB", use_selection=True)
bpy.ops.wm.stl_export(filepath=str(OUT_STL), export_selected_objects=True)

report = {
    "design": f"PiFlex Codex {DESIGN_VERSION.upper()} enclosed USB tunnels assembly",
    "source": SOURCE.name,
    "source_sha256": source_hash_before,
    "source_unchanged": True,
    "screen_shell_world_bounds_unchanged": True,
    "screen_shell_world_bounds_mm": shell_bounds_before,
    "opening_changed_from_v21": False,
    "blue_screen_frame_cut_for_usb": False,
    "rear_mount_replaced": True,
    "usb_tunnel_centres_local_mm": [
        [-143.077, TUNNEL_CENTRE_Y],
        [143.077, TUNNEL_CENTRE_Y],
    ],
    "usb_tunnel_clear_section_mm": [18.4, 10.0],
    "ear_cavity_centre_z_mm": 2.34 if EAR_CENTRED_DOGLEG else None,
    "ear_centred_dogleg": EAR_CENTRED_DOGLEG,
    "routing_form": "internal roofed tunnels beneath intact screen frame",
    "production_gate": "physical USB-A extension fit-check",
}
REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
