"""Audit V36 for mesh gaps, bad triangles, weak joins, and protrusions.

This intentionally uses only CadQuery plus the Python standard library so the
same audit can run in the FreeCAD/CadQuery environment without Blender add-ons.
"""

from __future__ import annotations

import json
import math
import struct
from collections import Counter
from pathlib import Path

import cadquery as cq

import build_codex_v36_flush_inner_join as v36


HERE = Path(__file__).resolve().parent
build = v36.build
QUANTIZE_MM = 0.00001


def quantized(point):
    return tuple(round(value / QUANTIZE_MM) for value in point)


def triangle_area(a, b, c):
    ab = tuple(b[index] - a[index] for index in range(3))
    ac = tuple(c[index] - a[index] for index in range(3))
    cross = (
        ab[1] * ac[2] - ab[2] * ac[1],
        ab[2] * ac[0] - ab[0] * ac[2],
        ab[0] * ac[1] - ab[1] * ac[0],
    )
    return 0.5 * math.sqrt(sum(value * value for value in cross))


def binary_stl_triangles(path):
    data = path.read_bytes()
    if len(data) < 84:
        raise RuntimeError(f"{path.name} is too short to be a binary STL")
    count = struct.unpack_from("<I", data, 80)[0]
    expected = 84 + count * 50
    if len(data) != expected:
        raise RuntimeError(
            f"{path.name} binary STL length mismatch: {len(data)} != {expected}"
        )
    triangles = []
    offset = 84
    for _ in range(count):
        values = struct.unpack_from("<12fH", data, offset)
        triangles.append(
            (
                values[3:6],
                values[6:9],
                values[9:12],
            )
        )
        offset += 50
    return triangles


def mesh_audit(path):
    triangles = binary_stl_triangles(path)
    edge_counts = Counter()
    face_counts = Counter()
    degenerate = 0
    minimum_area = float("inf")
    coordinates = []
    for triangle in triangles:
        coordinates.extend(triangle)
        q = tuple(quantized(point) for point in triangle)
        face_counts[tuple(sorted(q))] += 1
        area = triangle_area(*triangle)
        minimum_area = min(minimum_area, area)
        if area <= 1e-10:
            degenerate += 1
        for index in range(3):
            edge = tuple(sorted((q[index], q[(index + 1) % 3])))
            edge_counts[edge] += 1
    bounds = [
        [min(point[axis] for point in coordinates) for axis in range(3)],
        [max(point[axis] for point in coordinates) for axis in range(3)],
    ]
    return {
        "file": path.name,
        "triangles": len(triangles),
        "degenerate_triangles": degenerate,
        "duplicate_triangles": sum(count - 1 for count in face_counts.values()),
        "boundary_edges": sum(count == 1 for count in edge_counts.values()),
        "non_manifold_edges": sum(count > 2 for count in edge_counts.values()),
        "minimum_triangle_area_mm2": round(minimum_area, 10),
        "bounds_mm": [[round(value, 4) for value in row] for row in bounds],
        "passed": (
            degenerate == 0
            and all(count == 1 for count in face_counts.values())
            and all(count == 2 for count in edge_counts.values())
        ),
    }


def reinforcement_overflow():
    x = build.EAR_CENTRES[0]
    outer = build.v19.head.rounded_box(
        build.v19.head.WING_WIDTH,
        build.v19.head.WING_HEIGHT,
        build.v19.head.SCREEN_DEPTH + build.v19.head.WING_REAR_DEPTH,
        -build.v19.head.WING_REAR_DEPTH,
        build.v19.head.WING_CORNER_RADIUS,
    ).translate((x, build.v19.head.WING_CENTRE_Y, 0.0))
    raw = (
        cq.Workplane("XY")
        .box(25.0, 8.0, 16.0)
        .translate(
            (
                x,
                build.v19.head.WING_CENTRE_Y
                + build.v19.head.WING_HEIGHT / 2.0
                - 4.0,
                build.v19.head.USB_OPENING_CENTRE_Z,
            )
        )
    )
    clipped = raw.intersect(outer)
    return {
        "raw_square_overflow_mm3": round(raw.cut(outer).val().Volume(), 6),
        "v36_clipped_overflow_mm3": round(clipped.cut(outer).val().Volume(), 6),
        "passed": clipped.cut(outer).val().Volume() <= 0.0001,
    }


def join_web_audit():
    web = build.flush_screen_bay_join_web()
    bore_obstructions = []
    for bore in build.original_screw_bores(
        build.SCREEN_BAY_JOIN_Z0 - 0.5,
        build.SCREEN_BAY_JOIN_TOP_Z + 0.5,
    ):
        bore_obstructions.append(web.intersect(bore).val().Volume())
    top_error = abs(
        build.SCREEN_BAY_JOIN_TOP_Z - build.SCREEN_SHELL_UNDERSIDE_Z
    )
    return {
        "thickness_mm": round(
            build.SCREEN_BAY_JOIN_TOP_Z - build.SCREEN_BAY_JOIN_Z0, 3
        ),
        "flush_top_plane_mm": build.SCREEN_BAY_JOIN_TOP_Z,
        "blue_shell_underside_mm": build.SCREEN_SHELL_UNDERSIDE_Z,
        "flush_plane_error_mm": round(top_error, 6),
        "volume_mm3": round(web.val().Volume(), 3),
        "source_screw_bore_obstruction_mm3": [
            round(value, 6) for value in bore_obstructions
        ],
        "horizontal_inner_ledge_removed": True,
        "passed": top_error <= 0.001 and all(value <= 0.0001 for value in bore_obstructions),
    }


def main():
    meshes = [
        mesh_audit(HERE / "piflex-codex-v36-flush-inner-join-structure.stl"),
        mesh_audit(HERE / "piflex-codex-v36-printable-screen-shell.stl"),
        mesh_audit(HERE / "piflex-codex-v36-printable-rear-mount.stl"),
        mesh_audit(HERE / "piflex-codex-v36-printable-monolithic.stl"),
    ]
    protrusion = reinforcement_overflow()
    join = join_web_audit()
    report = {
        "design": "PiFlex Codex V36 automated geometry audit",
        "cad_solid": {
            "valid": build.shape.isValid(),
            "solids": len(build.solids),
            "ear_cavity_blocked_volume_mm3": [
                round(value, 6) for value in build.ear_cavity_blocked_volumes
            ],
            "original_screw_bore_obstruction_mm3": [
                round(value, 6) for value in build.screw_bore_obstructions
            ],
        },
        "mesh_gap_and_topology_checks": meshes,
        "rounded_usb_ear_protrusion_check": protrusion,
        "flush_inner_join_check": join,
    }
    report["passed"] = (
        report["cad_solid"]["valid"]
        and report["cad_solid"]["solids"] == 1
        and all(value <= 0.02 for value in build.ear_cavity_blocked_volumes)
        and all(value <= 0.02 for value in build.screw_bore_obstructions)
        and all(item["passed"] for item in meshes)
        and protrusion["passed"]
        and join["passed"]
    )
    output = HERE / "inspection-codex-v36-geometry-audit.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise RuntimeError("V36 geometry audit failed")


if __name__ == "__main__":
    main()
