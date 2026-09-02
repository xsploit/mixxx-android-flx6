"""Build V16 with a broad, rounded and gently tapered rear service bay."""

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


# The face nearest the screen is wider than the rear face, creating the soft
# wedge visible in the Mako reference without growing to the full screen size.
BAY_BACK_WIDTH = 166.0
BAY_BACK_HEIGHT = 100.0
BAY_MOUTH_WIDTH = 184.0
BAY_MOUTH_HEIGHT = 118.0
BAY_TOTAL_DEPTH = 35.0
BAY_WALL = 3.0
BAY_BACK_RADIUS = 22.0
BAY_MOUTH_RADIUS = 18.0

RACEWAY_INNER_HEIGHT = 22.0
RACEWAY_INNER_DEPTH = 12.0
RACEWAY_WALL = 3.0
RACEWAY_OUTER_HEIGHT = RACEWAY_INNER_HEIGHT + 2.0 * RACEWAY_WALL
RACEWAY_OUTER_DEPTH = RACEWAY_INNER_DEPTH + 2.0 * RACEWAY_WALL
RACEWAY_REAR_Z = -15.0


def _bay_outer():
    return head.rounded_loft(
        BAY_BACK_WIDTH,
        BAY_BACK_HEIGHT,
        -BAY_TOTAL_DEPTH,
        BAY_BACK_RADIUS,
        BAY_MOUTH_WIDTH,
        BAY_MOUTH_HEIGHT,
        -0.2,
        BAY_MOUTH_RADIUS,
    )


def _bay_inner():
    return head.rounded_loft(
        BAY_BACK_WIDTH - 2.0 * BAY_WALL,
        BAY_BACK_HEIGHT - 2.0 * BAY_WALL,
        -BAY_TOTAL_DEPTH + BAY_WALL,
        BAY_BACK_RADIUS - BAY_WALL,
        BAY_MOUTH_WIDTH - 2.0 * BAY_WALL,
        BAY_MOUTH_HEIGHT - 2.0 * BAY_WALL,
        1.0,
        BAY_MOUTH_RADIUS - BAY_WALL,
    )


def _raceway_shapes():
    bay_mouth_half_width = BAY_MOUTH_WIDTH / 2.0
    ear_inner_x = abs(head.wing_centres()[1]) - head.WING_WIDTH / 2.0
    overlap = 4.0
    x0 = bay_mouth_half_width - overlap
    x1 = ear_inner_x + overlap
    length = x1 - x0
    centre = (x0 + x1) / 2.0
    shapes = []
    for sign in (-1.0, 1.0):
        outer = (
            cq.Workplane("XY")
            .box(
                length,
                RACEWAY_OUTER_HEIGHT,
                RACEWAY_OUTER_DEPTH,
                centered=(True, True, False),
            )
            .translate((sign * centre, 0.0, RACEWAY_REAR_Z))
        )
        inner = (
            cq.Workplane("XY")
            .box(
                length + 2.0 * overlap,
                RACEWAY_INNER_HEIGHT,
                RACEWAY_INNER_DEPTH,
                centered=(True, True, False),
            )
            .translate((sign * centre, 0.0, RACEWAY_REAR_Z + RACEWAY_WALL))
        )
        shapes.append((outer, inner))
    return shapes


def build_v16_rear_shell_local():
    shell = head.build_rear_shell_local().union(_bay_outer())
    for outer, _ in _raceway_shapes():
        shell = shell.union(outer)
    shell = shell.cut(_bay_inner())
    for _, inner in _raceway_shapes():
        shell = shell.cut(inner)

    usb_ethernet_window = (
        cq.Workplane("XY")
        .box(18.0, 70.0, 20.0)
        .translate((BAY_MOUTH_WIDTH / 2.0, 0.0, -18.0))
    )
    power_hdmi_window = (
        cq.Workplane("XY")
        .box(82.0, 18.0, 18.0)
        .translate((0.0, -BAY_MOUTH_HEIGHT / 2.0, -18.0))
    )
    micro_sd_window = (
        cq.Workplane("XY")
        .box(26.0, 16.0, 7.0)
        .translate((0.0, BAY_BACK_HEIGHT / 2.0, -29.0))
    )
    shell = shell.cut(usb_ethernet_window).cut(power_hdmi_window).cut(micro_sd_window)

    for y in (-25.0, -15.0, -5.0, 5.0, 15.0, 25.0):
        vent = (
            cq.Workplane("XY")
            .box(100.0, 3.2, 6.0)
            .translate((0.0, y, -BAY_TOTAL_DEPTH))
        )
        shell = shell.cut(vent)
    return shell.combine(clean=True)


rear_local = build_v16_rear_shell_local()
rear = head.to_bracket_coordinates(rear_local)
result = rear.union(yoke.shifted_case_mount_result_v14).combine(clean=True)
shape = result.val()
solids = head.bracket_source._nested_solids(shape)
if len(solids) != 1 or not shape.isValid():
    raise RuntimeError(
        f"V16 must be one valid solid, got valid={shape.isValid()} solids={len(solids)}"
    )


def build_service_open_inspection_local():
    opened = rear_local
    bay_window = head.rounded_box(
        BAY_BACK_WIDTH - 12.0,
        BAY_BACK_HEIGHT - 12.0,
        BAY_WALL + 2.0,
        -BAY_TOTAL_DEPTH - 1.0,
        BAY_BACK_RADIUS - BAY_WALL,
    )
    opened = opened.cut(bay_window)
    for x in head.wing_centres():
        ear_window = head.rounded_box(
            head.WING_WIDTH - 8.0,
            head.WING_HEIGHT - 8.0,
            head.WING_WALL + 2.0,
            -head.WING_REAR_DEPTH - 1.0,
            head.WING_CORNER_RADIUS - head.WING_WALL - 1.0,
        ).translate((x, head.WING_CENTRE_Y, 0.0))
        opened = opened.cut(ear_window)
    return opened.combine(clean=True)


def export():
    stem = "piflex-complete-v9-shifted-mount-v16"
    cq.exporters.export(result, str(OUT / f"{stem}.step"))
    cq.exporters.export(
        result,
        str(OUT / f"{stem}.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    cq.exporters.export(
        rear_local,
        str(OUT / "piflex-v16-rounded-service-bay-local.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    cq.exporters.export(
        build_service_open_inspection_local(),
        str(OUT / "piflex-v16-service-open-inspection.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )

    bb = shape.BoundingBox()
    report = {
        "name": "PiFlex V16 rounded wedge electronics bay and USB raceways",
        "valid": shape.isValid(),
        "solids": len(solids),
        "dimensions_mm": [round(bb.xlen, 3), round(bb.ylen, 3), round(bb.zlen, 3)],
        "volume_cm3": round(shape.Volume() / 1000.0, 3),
        "complete_assembly_install_shift_x_mm": yoke.ASSEMBLY_SHIFT_X,
        "rear_bay_back_face_mm": [BAY_BACK_WIDTH, BAY_BACK_HEIGHT],
        "rear_bay_screen_mouth_mm": [BAY_MOUTH_WIDTH, BAY_MOUTH_HEIGHT],
        "rear_bay_depth_mm": BAY_TOTAL_DEPTH,
        "rear_bay_wall_mm": BAY_WALL,
        "corner_radii_mm": [BAY_BACK_RADIUS, BAY_MOUTH_RADIUS],
        "usb_raceway_clear_section_mm": [
            RACEWAY_INNER_HEIGHT,
            RACEWAY_INNER_DEPTH,
        ],
        "preserved_mount": "V14 centred clamps, screw holes and Master RCA clearance",
        "production_gate": "verify selected panel-mount USB lead body and plug dimensions",
    }
    (OUT / "inspection-v16.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    print(json.dumps(export(), indent=2))
