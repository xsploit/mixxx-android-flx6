"""Build V21 with a bay-width, screw-safe central service opening.

V19 remains the approved visual baseline. V21 changes only the central service
opening: its middle reaches the inner walls of the orange rear bay, while the
top and bottom taper inward around the four screen screw towers.
"""

from __future__ import annotations

import json
from pathlib import Path

import cadquery as cq

import build_codex_v19_polished_structure as v19


HERE = Path(__file__).resolve().parent

# The wide vertical sides meet the inner face of the 184 mm V16 bay mouth.
# The tapered shoulders stop safely before the four screen screw towers.
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
OPENING_DEPTH = v19.head.CASE_RIM_DEPTH + 4.0
OPENING_Z0 = -v19.head.CASE_RIM_DEPTH - 1.0
MIN_SCREW_CLEARANCE = 7.161854508435643


def bay_merged_service_throat():
    return (
        cq.Workplane("XY")
        .polyline(OPENING_POINTS)
        .close()
        .extrude(OPENING_DEPTH)
        .translate((0.0, 0.0, OPENING_Z0))
    )


def build_bay_merged_rear_local():
    polished = v19.v18.rear_local.union(v19.clean_rear_bay_skin())
    polished = polished.cut(bay_merged_service_throat())
    for channel in v19.concealed_usb_channels():
        polished = polished.cut(channel)
    for grill in v19.rear_grill_cutters():
        polished = polished.cut(grill)
    return polished.combine(clean=True)


rear_local = build_bay_merged_rear_local()
rear = v19.head.to_bracket_coordinates(rear_local)
complete = rear.union(v19.yoke.shifted_case_mount_result_v14).combine(clean=True)
shape = complete.val()
solids = v19.head.bracket_source._nested_solids(shape)

if not shape.isValid() or len(solids) != 1:
    raise RuntimeError(
        f"V21 must be one valid solid; valid={shape.isValid()} solids={len(solids)}"
    )


def export():
    cq.exporters.export(
        complete,
        str(HERE / "piflex-codex-v21-bay-merged-structure.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    cq.exporters.export(
        complete,
        str(HERE / "piflex-codex-v21-bay-merged-structure.step"),
    )
    cq.exporters.export(
        rear_local,
        str(HERE / "piflex-codex-v21-bay-merged-rear-local.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )

    report = {
        "design": "PiFlex Codex V21 bay-merged service opening",
        "visual_baseline": "PiFlex Codex V19",
        "valid": shape.isValid(),
        "solids": len(solids),
        "opening_profile_mm": [list(point) for point in OPENING_POINTS],
        "opening_middle_width_mm": 178.0,
        "opening_top_bottom_span_mm": 149.0,
        "opening_max_height_mm": 112.0,
        "minimum_screw_tower_clearance_mm": round(MIN_SCREW_CLEARANCE, 3),
        "rear_bay_inner_mouth_width_mm": (
            v19.v16.BAY_MOUTH_WIDTH - 2.0 * v19.v16.BAY_WALL
        ),
        "preserved": [
            "V19 outer blue screen-case frame",
            "V19 recessed inner bevel",
            "four screen screw towers",
            "six-slot rear grill",
            "two top-facing USB-A ear sockets",
            "two concealed USB tunnels under the blue frame",
            "FLX6 bracket placement",
        ],
        "visible_change": (
            "central opening widens into the orange bay's angled inner side walls; "
            "most of the former logo area is removed by the opening"
        ),
        "production_gate": (
            "fit-check the physical screen fasteners and female USB-A panel leads"
        ),
    }
    (HERE / "inspection-codex-v21-bay-merged-structure.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    print(json.dumps(export(), indent=2))
