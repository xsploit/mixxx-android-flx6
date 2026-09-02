"""Build V20 with a modestly enlarged opening in the retained screw plate."""

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
import build_screw_safe_service_bay_v18 as v18  # noqa: E402


# The source Pi opening was about 93.5 x 64.3 mm.  Increase it only modestly;
# the broad first-layer plate and all four original screw bosses remain.
THROAT_WIDTH = 118.0
THROAT_HEIGHT = 88.0
THROAT_RADIUS = 10.0
THROAT_CENTRE_X = 0.0
THROAT_CENTRE_Y = 0.0

REAR_EDGE_RADIUS = 5.0
PORT_CORNER_RADIUS = 4.0
CHANNEL_CLEAR_HEIGHT = 18.0
CHANNEL_FRONT_Z = 1.0
CHANNEL_REAR_Z = -head.WING_REAR_DEPTH + head.WING_WALL


def _retained_plate_opening(depth=13.0, z0=-head.CASE_RIM_DEPTH - 1.0):
    return head.rounded_box(
        THROAT_WIDTH,
        THROAT_HEIGHT,
        depth,
        z0,
        THROAT_RADIUS,
    ).translate((THROAT_CENTRE_X, THROAT_CENTRE_Y, 0.0))


def _concealed_ear_channels():
    ear_inner_edge = abs(head.wing_centres()[1]) - (
        head.WING_WIDTH - 2.0 * head.WING_WALL
    ) / 2.0
    depth = CHANNEL_FRONT_Z - CHANNEL_REAR_Z
    passages = []
    for sign in (-1.0, 1.0):
        start = THROAT_WIDTH / 2.0 - 3.0
        end = ear_inner_edge + 3.0
        length = end - start
        centre = sign * (start + end) / 2.0
        passages.append(
            cq.Workplane("XY")
            .box(length, CHANNEL_CLEAR_HEIGHT, depth, centered=(True, True, False))
            .translate((centre, head.WING_CENTRE_Y, CHANNEL_REAR_Z))
        )
    return passages


def _smooth_bay_outer():
    return v16._bay_outer().edges("<Z").fillet(REAR_EDGE_RADIUS)


def _rounded_usb_ethernet_window():
    cutter = cq.Workplane("XY").box(30.0, 70.0, 24.0)
    return cutter.edges("|X").fillet(PORT_CORNER_RADIUS).translate(
        (v16.BAY_BACK_WIDTH / 2.0, 0.0, -18.0)
    )


def _rounded_power_hdmi_window():
    cutter = cq.Workplane("XY").box(88.0, 30.0, 24.0)
    return cutter.edges("|Y").fillet(PORT_CORNER_RADIUS).translate(
        (0.0, -v16.BAY_BACK_HEIGHT / 2.0, -18.0)
    )


def _validate_screw_clearance():
    opening = _retained_plate_opening()
    checks = []
    for x in v18.HOLE_X:
        for y in v18.HOLE_Y:
            guard = (
                cq.Workplane("XY")
                .center(x, y)
                .circle(v18.SCREW_GUARD_RADIUS)
                .extrude(head.CASE_RIM_DEPTH + 4.0)
                .translate((0.0, 0.0, -head.CASE_RIM_DEPTH - 1.0))
            )
            overlap = opening.intersect(guard).val().Volume()
            checks.append({"hole_mm": [x, y], "opening_overlap_mm3": round(overlap, 6)})
    if any(item["opening_overlap_mm3"] > 0.001 for item in checks):
        raise RuntimeError(f"Opening violates a retained screen screw area: {checks}")
    return checks


def build_v20_rear_shell_local():
    shell = head.build_rear_shell_local().union(_smooth_bay_outer())
    shell = shell.cut(v16._bay_inner()).cut(_retained_plate_opening())
    for passage in _concealed_ear_channels():
        shell = shell.cut(passage)
    shell = shell.cut(_rounded_usb_ethernet_window())
    shell = shell.cut(_rounded_power_hdmi_window())
    return shell.combine(clean=True)


screw_guard_checks = _validate_screw_clearance()
rear_local = build_v20_rear_shell_local()
rear = head.to_bracket_coordinates(rear_local)
result = rear.union(yoke.shifted_case_mount_result_v14).combine(clean=True)
shape = result.val()
solids = head.bracket_source._nested_solids(shape)
if len(solids) != 1 or not shape.isValid():
    raise RuntimeError(
        f"V20 must be one valid solid, got valid={shape.isValid()} solids={len(solids)}"
    )


def build_service_open_inspection_local():
    bay_window = head.rounded_box(
        v16.BAY_BACK_WIDTH - 12.0,
        v16.BAY_BACK_HEIGHT - 12.0,
        v16.BAY_WALL + REAR_EDGE_RADIUS + 2.0,
        -v16.BAY_TOTAL_DEPTH - 1.0,
        v16.BAY_BACK_RADIUS - v16.BAY_WALL,
    )
    return rear_local.cut(bay_window).combine(clean=True)


def build_original_screen_layer_cutter_local():
    return _retained_plate_opening(depth=50.0, z0=-25.0)


def export():
    stem = "piflex-complete-v9-shifted-mount-v20"
    cq.exporters.export(result, str(OUT / f"{stem}.step"))
    cq.exporters.export(result, str(OUT / f"{stem}.stl"), tolerance=0.05, angularTolerance=0.10)
    cq.exporters.export(
        rear_local,
        str(OUT / "piflex-v20-clean-service-bay-local.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    cq.exporters.export(
        build_service_open_inspection_local(),
        str(OUT / "piflex-v20-service-open-inspection.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    cq.exporters.export(
        build_original_screen_layer_cutter_local(),
        str(OUT / "piflex-v20-original-pi-layer-cutter-local.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )

    bb = shape.BoundingBox()
    report = {
        "name": "PiFlex V20 retained screw plate with modest opening",
        "valid": shape.isValid(),
        "solids": len(solids),
        "dimensions_mm": [round(bb.xlen, 3), round(bb.ylen, 3), round(bb.zlen, 3)],
        "volume_cm3": round(shape.Volume() / 1000.0, 3),
        "retained_first_layer": True,
        "original_approximate_opening_mm": [93.524, 64.345],
        "enlarged_opening_mm": [THROAT_WIDTH, THROAT_HEIGHT],
        "screw_guard_radius_mm": v18.SCREW_GUARD_RADIUS,
        "screw_guard_checks": screw_guard_checks,
        "rear_edge_radius_mm": REAR_EDGE_RADIUS,
        "rear_vent_slots": False,
        "micro_sd_edge_slot": False,
        "external_raceway_bridges": False,
        "production_gate": "verify Pi connector locations and panel USB lead dimensions with calipers",
    }
    (OUT / "inspection-v20.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(export(), indent=2))
