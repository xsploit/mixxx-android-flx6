"""Build V17 with a widened service opening and concealed USB channels.

V17 keeps the rounded V16 electronics bay but removes the visible rectangular
raceway bridges.  Each ear now opens into the service cavity through a shallow
channel contained inside the existing rear skin, so nothing projects behind
the ears.  The former Pi-sized throat is also opened to the width of the new
bay.
"""

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


# The opening through the former flat back follows the expanded bay mouth.
THROAT_WIDTH = v16.BAY_MOUTH_WIDTH - 2.0 * v16.BAY_WALL
THROAT_HEIGHT = v16.BAY_MOUTH_HEIGHT - 2.0 * v16.BAY_WALL
THROAT_RADIUS = v16.BAY_MOUTH_RADIUS - v16.BAY_WALL

# Only the cable, not a complete USB-A plug, needs to pass between the service
# bay and each pre-wired panel socket.  These passages remain inside the ear's
# 9 mm rear envelope and are hidden behind the existing 2.8 mm rear skin.
CHANNEL_CLEAR_HEIGHT = 18.0
CHANNEL_FRONT_Z = 1.0
CHANNEL_REAR_Z = -head.WING_REAR_DEPTH + head.WING_WALL


def _expanded_throat():
    return head.rounded_box(
        THROAT_WIDTH,
        THROAT_HEIGHT,
        head.CASE_RIM_DEPTH + 4.0,
        -head.CASE_RIM_DEPTH - 1.0,
        THROAT_RADIUS,
    )


def _concealed_ear_channels():
    """Return negative volumes linking the bay cavity to both hollow ears."""
    bay_inner_edge = THROAT_WIDTH / 2.0 - 2.0
    ear_inner_edge = abs(head.wing_centres()[1]) - (
        head.WING_WIDTH - 2.0 * head.WING_WALL
    ) / 2.0
    overlap = 3.0
    start = bay_inner_edge - overlap
    end = ear_inner_edge + overlap
    length = end - start
    centre = (start + end) / 2.0
    depth = CHANNEL_FRONT_Z - CHANNEL_REAR_Z

    passages = []
    for sign in (-1.0, 1.0):
        passage = (
            cq.Workplane("XY")
            .box(
                length,
                CHANNEL_CLEAR_HEIGHT,
                depth,
                centered=(True, True, False),
            )
            .translate((sign * centre, head.WING_CENTRE_Y, CHANNEL_REAR_Z))
        )
        passages.append(passage)
    return passages


def _usb_ethernet_side_window():
    # A single generous service opening through the Pi connector side.  It is
    # intentionally trim-insert ready because the final Pi/cooler position must
    # be confirmed with calipers before making connector-specific apertures.
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


def build_v17_rear_shell_local():
    # Start with the proven screen shell and ears.  The V16 bay is fused in,
    # then its full interior and the matching wide throat are cleared again.
    shell = head.build_rear_shell_local().union(v16._bay_outer())
    shell = shell.cut(v16._bay_inner()).cut(_expanded_throat())

    # Direct, hidden paths: no added bars and no geometry behind the ear plane.
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


rear_local = build_v17_rear_shell_local()
rear = head.to_bracket_coordinates(rear_local)
result = rear.union(yoke.shifted_case_mount_result_v14).combine(clean=True)
shape = result.val()
solids = head.bracket_source._nested_solids(shape)
if len(solids) != 1 or not shape.isValid():
    raise RuntimeError(
        f"V17 must be one valid solid, got valid={shape.isValid()} solids={len(solids)}"
    )


def build_service_open_inspection_local():
    opened = rear_local
    bay_window = head.rounded_box(
        v16.BAY_BACK_WIDTH - 12.0,
        v16.BAY_BACK_HEIGHT - 12.0,
        v16.BAY_WALL + 2.0,
        -v16.BAY_TOTAL_DEPTH - 1.0,
        v16.BAY_BACK_RADIUS - v16.BAY_WALL,
    )
    return opened.cut(bay_window).combine(clean=True)


def export():
    stem = "piflex-complete-v9-shifted-mount-v17"
    cq.exporters.export(result, str(OUT / f"{stem}.step"))
    cq.exporters.export(
        result,
        str(OUT / f"{stem}.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    cq.exporters.export(
        rear_local,
        str(OUT / "piflex-v17-integrated-service-bay-local.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    cq.exporters.export(
        build_service_open_inspection_local(),
        str(OUT / "piflex-v17-service-open-inspection.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )

    bb = shape.BoundingBox()
    report = {
        "name": "PiFlex V17 rounded service bay with concealed ear channels",
        "valid": shape.isValid(),
        "solids": len(solids),
        "dimensions_mm": [round(bb.xlen, 3), round(bb.ylen, 3), round(bb.zlen, 3)],
        "volume_cm3": round(shape.Volume() / 1000.0, 3),
        "complete_assembly_install_shift_x_mm": yoke.ASSEMBLY_SHIFT_X,
        "rear_bay_back_face_mm": [v16.BAY_BACK_WIDTH, v16.BAY_BACK_HEIGHT],
        "rear_bay_screen_mouth_mm": [v16.BAY_MOUTH_WIDTH, v16.BAY_MOUTH_HEIGHT],
        "expanded_back_opening_mm": [THROAT_WIDTH, THROAT_HEIGHT],
        "concealed_channel_clear_mm": [CHANNEL_CLEAR_HEIGHT, CHANNEL_FRONT_Z - CHANNEL_REAR_Z],
        "channel_rear_limit_mm": CHANNEL_REAR_Z,
        "ear_rear_limit_mm": -head.WING_REAR_DEPTH,
        "external_raceway_bridges": False,
        "service_windows": ["USB/Ethernet side", "power/HDMI side", "microSD edge"],
        "preserved_mount": "V14 centred clamps, screw holes and Master RCA clearance",
        "production_gate": "verify Pi connector locations and selected panel USB lead dimensions with calipers",
    }
    (OUT / "inspection-v17.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    print(json.dumps(export(), indent=2))
