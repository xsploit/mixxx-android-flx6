"""Build V18 with a screw-safe back opening and concealed USB channels."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
MOUNT_DIR = ROOT / "models" / "flx6-surface-mount-remix-v1"
sys.path.insert(0, str(OUT))
sys.path.insert(0, str(MOUNT_DIR))

import build_integrated_yoke as yoke  # noqa: E402
import build_piflex_enclosed_head as head  # noqa: E402
import build_rounded_service_bay_v16 as v16  # noqa: E402


# Keep the entire opening inside the four original screen fasteners.  The
# guard includes the 5.5 mm screw tower plus 2.5 mm of structural web.
SCREW_GUARD_RADIUS = head.BACK_SCREW_TUNNEL_RADIUS + 2.5
HOLE_X = tuple(head.bracket_source.SCREEN_OUTER_HOLES_X.values())
HOLE_Y = tuple(head.bracket_source.SCREEN_OUTER_HOLES_Y)

THROAT_X_MIN = min(HOLE_X) + SCREW_GUARD_RADIUS
THROAT_X_MAX = max(HOLE_X) - SCREW_GUARD_RADIUS
THROAT_Y_MIN = min(HOLE_Y) + SCREW_GUARD_RADIUS
THROAT_Y_MAX = max(HOLE_Y) - SCREW_GUARD_RADIUS
THROAT_WIDTH = THROAT_X_MAX - THROAT_X_MIN
THROAT_HEIGHT = THROAT_Y_MAX - THROAT_Y_MIN
THROAT_CENTRE_X = (THROAT_X_MIN + THROAT_X_MAX) / 2.0
THROAT_CENTRE_Y = (THROAT_Y_MIN + THROAT_Y_MAX) / 2.0
THROAT_RADIUS = 14.0

CHANNEL_CLEAR_HEIGHT = 18.0
CHANNEL_FRONT_Z = 1.0
CHANNEL_REAR_Z = -head.WING_REAR_DEPTH + head.WING_WALL


def _screw_safe_throat():
    return head.rounded_box(
        THROAT_WIDTH,
        THROAT_HEIGHT,
        head.CASE_RIM_DEPTH + 4.0,
        -head.CASE_RIM_DEPTH - 1.0,
        THROAT_RADIUS,
    ).translate((THROAT_CENTRE_X, THROAT_CENTRE_Y, 0.0))


def _concealed_ear_channels():
    """Hidden cable paths, bounded by the existing 9 mm ear envelope."""
    ear_inner_edge = abs(head.wing_centres()[1]) - (
        head.WING_WIDTH - 2.0 * head.WING_WALL
    ) / 2.0
    depth = CHANNEL_FRONT_Z - CHANNEL_REAR_Z
    passages = []

    for sign, throat_edge in (
        (-1.0, THROAT_X_MIN),
        (1.0, THROAT_X_MAX),
    ):
        start = abs(throat_edge) - 3.0
        end = ear_inner_edge + 3.0
        length = end - start
        centre = sign * (start + end) / 2.0
        passage = (
            cq.Workplane("XY")
            .box(
                length,
                CHANNEL_CLEAR_HEIGHT,
                depth,
                centered=(True, True, False),
            )
            .translate((centre, head.WING_CENTRE_Y, CHANNEL_REAR_Z))
        )
        passages.append(passage)
    return passages


def _usb_ethernet_side_window():
    return (
        cq.Workplane("XY")
        .box(30.0, 70.0, 24.0)
        .translate((v16.BAY_BACK_WIDTH / 2.0, 0.0, -18.0))
    )


def _power_hdmi_side_window():
    return (
        cq.Workplane("XY")
        .box(88.0, 30.0, 24.0)
        .translate((0.0, -v16.BAY_BACK_HEIGHT / 2.0, -18.0))
    )


def build_v18_rear_shell_local():
    shell = head.build_rear_shell_local().union(v16._bay_outer())
    shell = shell.cut(v16._bay_inner()).cut(_screw_safe_throat())

    for passage in _concealed_ear_channels():
        shell = shell.cut(passage)

    shell = shell.cut(_usb_ethernet_side_window())
    shell = shell.cut(_power_hdmi_side_window())
    micro_sd_window = (
        cq.Workplane("XY")
        .box(28.0, 18.0, 8.0)
        .translate((0.0, v16.BAY_BACK_HEIGHT / 2.0, -29.0))
    )
    shell = shell.cut(micro_sd_window)

    for y in (-25.0, -15.0, -5.0, 5.0, 15.0, 25.0):
        vent = (
            cq.Workplane("XY")
            .box(100.0, 3.2, 6.0)
            .translate((0.0, y, -v16.BAY_TOTAL_DEPTH))
        )
        shell = shell.cut(vent)
    return shell.combine(clean=True)


def _validate_screw_guards():
    throat = _screw_safe_throat()
    collisions = []
    for x in HOLE_X:
        for y in HOLE_Y:
            guard = (
                cq.Workplane("XY")
                .center(x, y)
                .circle(SCREW_GUARD_RADIUS)
                .extrude(head.CASE_RIM_DEPTH + 4.0)
                .translate((0.0, 0.0, -head.CASE_RIM_DEPTH - 1.0))
            )
            overlap = throat.intersect(guard).val().Volume()
            collisions.append({"hole_mm": [x, y], "opening_overlap_mm3": round(overlap, 6)})
    if any(item["opening_overlap_mm3"] > 0.001 for item in collisions):
        raise RuntimeError(f"Back opening violates a screen screw guard: {collisions}")
    return collisions


screw_guard_checks = _validate_screw_guards()
rear_local = build_v18_rear_shell_local()
rear = head.to_bracket_coordinates(rear_local)
result = rear.union(yoke.shifted_case_mount_result_v14).combine(clean=True)
shape = result.val()
solids = head.bracket_source._nested_solids(shape)
if len(solids) != 1 or not shape.isValid():
    raise RuntimeError(
        f"V18 must be one valid solid, got valid={shape.isValid()} solids={len(solids)}"
    )


def build_service_open_inspection_local():
    bay_window = head.rounded_box(
        v16.BAY_BACK_WIDTH - 12.0,
        v16.BAY_BACK_HEIGHT - 12.0,
        v16.BAY_WALL + 2.0,
        -v16.BAY_TOTAL_DEPTH - 1.0,
        v16.BAY_BACK_RADIUS - v16.BAY_WALL,
    )
    return rear_local.cut(bay_window).combine(clean=True)


def export():
    stem = "piflex-complete-v9-shifted-mount-v18"
    cq.exporters.export(result, str(OUT / f"{stem}.step"))
    cq.exporters.export(
        result,
        str(OUT / f"{stem}.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    cq.exporters.export(
        rear_local,
        str(OUT / "piflex-v18-screw-safe-service-bay-local.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    cq.exporters.export(
        build_service_open_inspection_local(),
        str(OUT / "piflex-v18-service-open-inspection.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )

    bb = shape.BoundingBox()
    report = {
        "name": "PiFlex V18 screw-safe rounded service bay",
        "valid": shape.isValid(),
        "solids": len(solids),
        "dimensions_mm": [round(bb.xlen, 3), round(bb.ylen, 3), round(bb.zlen, 3)],
        "volume_cm3": round(shape.Volume() / 1000.0, 3),
        "complete_assembly_install_shift_x_mm": yoke.ASSEMBLY_SHIFT_X,
        "rear_bay_back_face_mm": [v16.BAY_BACK_WIDTH, v16.BAY_BACK_HEIGHT],
        "rear_bay_screen_mouth_mm": [v16.BAY_MOUTH_WIDTH, v16.BAY_MOUTH_HEIGHT],
        "screw_safe_back_opening_mm": [round(THROAT_WIDTH, 3), round(THROAT_HEIGHT, 3)],
        "screw_safe_back_opening_centre_mm": [round(THROAT_CENTRE_X, 3), round(THROAT_CENTRE_Y, 3)],
        "screw_guard_radius_mm": SCREW_GUARD_RADIUS,
        "screw_guard_checks": screw_guard_checks,
        "concealed_channel_clear_mm": [CHANNEL_CLEAR_HEIGHT, CHANNEL_FRONT_Z - CHANNEL_REAR_Z],
        "channel_rear_limit_mm": CHANNEL_REAR_Z,
        "ear_rear_limit_mm": -head.WING_REAR_DEPTH,
        "external_raceway_bridges": False,
        "service_windows": ["USB/Ethernet side", "power/HDMI side", "microSD edge"],
        "production_gate": "verify Pi connector locations and panel USB lead dimensions with calipers",
    }
    (OUT / "inspection-v18.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    print(json.dumps(export(), indent=2))
