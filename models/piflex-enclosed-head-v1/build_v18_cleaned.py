"""Conservative cleanup of V18.

V18 is the source of truth.  This fills its legacy pod/vent/slot geometry with
one continuous rounded bay, then re-cuts only the required connector windows,
the screw-safe service throat, and the concealed ear cable paths.
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
import build_screw_safe_service_bay_v18 as v18  # noqa: E402


REAR_EDGE_RADIUS = 5.0
PORT_CORNER_RADIUS = 4.0


def _filled_rounded_bay_outer():
    # A fresh uninterrupted outer solid fills the old Pi mold, vent slots,
    # micro-SD slot and rough port cuts before the clean cavity is made.
    return v16._bay_outer().edges("<Z").fillet(REAR_EDGE_RADIUS)


def _clean_usb_ethernet_window():
    return (
        cq.Workplane("XY")
        .box(30.0, 70.0, 24.0)
        .edges("|X")
        .fillet(PORT_CORNER_RADIUS)
        .translate((v16.BAY_BACK_WIDTH / 2.0, 0.0, -18.0))
    )


def _clean_power_hdmi_window():
    return (
        cq.Workplane("XY")
        .box(88.0, 30.0, 24.0)
        .edges("|Y")
        .fillet(PORT_CORNER_RADIUS)
        .translate((0.0, -v16.BAY_BACK_HEIGHT / 2.0, -18.0))
    )


def build_cleaned_v18_rear_local():
    # Start with V18's case/ears, solid-fill the rear bay, and then cut back
    # only the openings that have a functional purpose.
    shell = head.build_rear_shell_local().union(_filled_rounded_bay_outer())
    shell = shell.cut(v16._bay_inner()).cut(v18._screw_safe_throat())
    for channel in v18._concealed_ear_channels():
        shell = shell.cut(channel)
    shell = shell.cut(_clean_usb_ethernet_window())
    shell = shell.cut(_clean_power_hdmi_window())
    return shell.combine(clean=True)


def build_shallow_original_case_cutter():
    # The exact MakerWorld screen shell spans local Z=-6.84..+6.84 mm.  Cut
    # only its rear plate/details (-6.84..about -1.81), never its front rim.
    return head.rounded_box(
        v18.THROAT_WIDTH,
        v18.THROAT_HEIGHT,
        7.2,
        -7.6,
        v18.THROAT_RADIUS,
    ).translate((v18.THROAT_CENTRE_X, v18.THROAT_CENTRE_Y, 0.0))


v18._validate_screw_guards()
rear_local = build_cleaned_v18_rear_local()
rear = head.to_bracket_coordinates(rear_local)
result = rear.union(yoke.shifted_case_mount_result_v14).combine(clean=True)
shape = result.val()
solids = head.bracket_source._nested_solids(shape)
if len(solids) != 1 or not shape.isValid():
    raise RuntimeError(
        f"Cleaned V18 must be one valid solid, got valid={shape.isValid()} solids={len(solids)}"
    )


def export():
    stem = "piflex-v18-cleaned-complete"
    cq.exporters.export(result, str(OUT / f"{stem}.step"))
    cq.exporters.export(
        result,
        str(OUT / f"{stem}.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    cq.exporters.export(
        rear_local,
        str(OUT / "piflex-v18-cleaned-rear-local.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    cq.exporters.export(
        build_shallow_original_case_cutter(),
        str(OUT / "piflex-v18-shallow-rear-opening-cutter.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    bb = shape.BoundingBox()
    report = {
        "name": "PiFlex V18 conservative cleanup",
        "source": "V18",
        "valid": shape.isValid(),
        "solids": len(solids),
        "dimensions_mm": [round(bb.xlen, 3), round(bb.ylen, 3), round(bb.zlen, 3)],
        "volume_cm3": round(shape.Volume() / 1000.0, 3),
        "service_opening_mm": [round(v18.THROAT_WIDTH, 3), round(v18.THROAT_HEIGHT, 3)],
        "screen_screw_areas_preserved": True,
        "original_front_rim_cut": False,
        "legacy_vent_and_slot_gaps_filled": True,
        "intentional_openings": [
            "two top-facing ear USB sockets",
            "rounded USB/Ethernet connector window",
            "rounded power/HDMI connector window",
        ],
    }
    (OUT / "inspection-v18-cleaned.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    print(json.dumps(export(), indent=2))
