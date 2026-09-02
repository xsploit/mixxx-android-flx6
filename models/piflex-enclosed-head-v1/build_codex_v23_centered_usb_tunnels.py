"""Build V23 with USB tunnels aligned to the true centres of both ears.

V23 preserves the approved V21 service opening and the frozen V19 exterior.
It first fills the obsolete short V18/V19 cable cuts, then cuts two new roofed
passages from the V21 opening side walls to the hollow centres of the USB ears.
The blue screen frame is never cut for routing.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import cadquery as cq

import build_codex_v19_polished_structure as v19
import build_codex_v21_bay_merged_structure as v21


HERE = Path(__file__).resolve().parent

OPENING_MIDDLE_HALF_WIDTH = 89.0
TUNNEL_ENTRY_OVERLAP = 3.0
TUNNEL_CLEAR_WIDTH = 18.4
TUNNEL_CLEAR_HEIGHT = 10.0
TUNNEL_DROP_BELOW_OLD_ROUTE = 4.5
TUNNEL_REAR_Z = (
    -v19.head.WING_REAR_DEPTH
    + v19.head.WING_WALL
    - TUNNEL_DROP_BELOW_OLD_ROUTE
)
RACEWAY_WALL = v19.head.WING_WALL
RACEWAY_ROOF_OVERLAP = 0.4
RACEWAY_WIDTH = TUNNEL_CLEAR_WIDTH + 2.0 * RACEWAY_WALL
RACEWAY_REAR_Z = TUNNEL_REAR_Z - RACEWAY_WALL
RACEWAY_HEIGHT = RACEWAY_WALL + TUNNEL_CLEAR_HEIGHT + RACEWAY_ROOF_OVERLAP

EAR_CENTRES = tuple(v19.head.wing_centres())
EAR_CENTRE_ABS = abs(EAR_CENTRES[1])
TUNNEL_INNER_ABS = OPENING_MIDDLE_HALF_WIDTH - TUNNEL_ENTRY_OVERLAP
TUNNEL_OUTER_ABS = EAR_CENTRE_ABS
TUNNEL_LENGTH = TUNNEL_OUTER_ABS - TUNNEL_INNER_ABS


def corrected_usb_tunnels():
    """Two enclosed voids from the service bay into the ear cavity centres."""
    passages = []
    for sign in (-1.0, 1.0):
        centre_x = sign * (TUNNEL_INNER_ABS + TUNNEL_OUTER_ABS) / 2.0
        passage = (
            cq.Workplane("XY")
            .box(
                TUNNEL_LENGTH,
                TUNNEL_CLEAR_WIDTH,
                TUNNEL_CLEAR_HEIGHT,
                centered=(True, True, False),
            )
            .translate(
                (
                    centre_x,
                    v19.head.WING_CENTRE_Y,
                    TUNNEL_REAR_Z,
                )
            )
        )
        passages.append(passage)
    return passages


def tunnel_housings():
    """Rounded outer raceways that retain a floor and walls below the bevel."""
    housing_inner_abs = TUNNEL_INNER_ABS - RACEWAY_WALL
    housing_outer_abs = TUNNEL_OUTER_ABS + RACEWAY_WALL
    housing_length = housing_outer_abs - housing_inner_abs
    housings = []
    for sign in (-1.0, 1.0):
        centre_x = sign * (housing_inner_abs + housing_outer_abs) / 2.0
        housing = v19.head.rounded_box(
            housing_length,
            RACEWAY_WIDTH,
            RACEWAY_HEIGHT,
            RACEWAY_REAR_Z,
            4.0,
        ).translate((centre_x, v19.head.WING_CENTRE_Y, 0.0))
        housings.append(housing)
    return housings


def build_centered_tunnel_rear_local():
    # V18 contains the obsolete short cuts. Restore their exact cutter volumes
    # before making the approved V21 opening and the corrected longer tunnels.
    polished = v19.v18.rear_local.union(v19.clean_rear_bay_skin())
    for obsolete_channel in v19.concealed_usb_channels():
        polished = polished.union(obsolete_channel)
    for housing in tunnel_housings():
        polished = polished.union(housing)

    polished = polished.cut(v21.bay_merged_service_throat())
    for tunnel in corrected_usb_tunnels():
        polished = polished.cut(tunnel)
    for grill in v19.rear_grill_cutters():
        polished = polished.cut(grill)
    return polished.combine(clean=True)


def point_segment_distance(point, start, end):
    px, py = point
    ax, ay = start
    bx, by = end
    dx = bx - ax
    dy = by - ay
    length_squared = dx * dx + dy * dy
    amount = ((px - ax) * dx + (py - ay) * dy) / length_squared
    amount = max(0.0, min(1.0, amount))
    nearest = (ax + amount * dx, ay + amount * dy)
    return math.hypot(px - nearest[0], py - nearest[1])


def opening_screw_clearances():
    holes = [
        (x, y)
        for x in v19.HOLE_X
        for y in v19.HOLE_Y
    ]
    clearances = []
    for hole in holes:
        distance = min(
            point_segment_distance(
                hole,
                v21.OPENING_POINTS[index],
                v21.OPENING_POINTS[(index + 1) % len(v21.OPENING_POINTS)],
            )
            for index in range(len(v21.OPENING_POINTS))
        )
        clearances.append(
            {"hole_mm": list(hole), "opening_clearance_mm": round(distance, 3)}
        )
    return clearances


rear_local = build_centered_tunnel_rear_local()
rear = v19.head.to_bracket_coordinates(rear_local)
complete = rear.union(v19.yoke.shifted_case_mount_result_v14)
# The FLX6 yoke overlaps the rear body at the mounting roots. Re-cut the same
# voids after that union so the yoke cannot silently plug either cable route.
for tunnel in corrected_usb_tunnels():
    complete = complete.cut(v19.head.to_bracket_coordinates(tunnel))
complete = complete.combine(clean=True)
shape = complete.val()
solids = v19.head.bracket_source._nested_solids(shape)

if not shape.isValid() or len(solids) != 1:
    raise RuntimeError(
        f"V23 must be one valid solid; valid={shape.isValid()} solids={len(solids)}"
    )


def export():
    structure_stl = HERE / "piflex-codex-v23-centered-usb-tunnels-structure.stl"
    structure_step = HERE / "piflex-codex-v23-centered-usb-tunnels-structure.step"
    rear_stl = HERE / "piflex-codex-v23-centered-usb-tunnels-rear-local.stl"
    tunnel_voids_stl = HERE / "piflex-codex-v23-usb-tunnel-voids-local.stl"
    registered_tunnel_voids_stl = (
        HERE / "piflex-codex-v23-usb-tunnel-voids-structure-coordinates.stl"
    )

    cq.exporters.export(
        complete,
        str(structure_stl),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    cq.exporters.export(complete, str(structure_step))
    cq.exporters.export(
        rear_local,
        str(rear_stl),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    tunnel_compound = cq.Compound.makeCompound(
        [tunnel.val() for tunnel in corrected_usb_tunnels()]
    )
    cq.exporters.export(
        tunnel_compound,
        str(tunnel_voids_stl),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    tunnel_workplane = cq.Workplane(obj=tunnel_compound)
    cq.exporters.export(
        v19.head.to_bracket_coordinates(tunnel_workplane),
        str(registered_tunnel_voids_stl),
        tolerance=0.05,
        angularTolerance=0.10,
    )

    screw_clearances = opening_screw_clearances()
    report = {
        "design": "PiFlex Codex V23 centred enclosed USB tunnels",
        "visual_baseline": "PiFlex Codex V21 opening on frozen V19 exterior",
        "valid": shape.isValid(),
        "solids": len(solids),
        "opening_profile_mm": [list(point) for point in v21.OPENING_POINTS],
        "opening_is_mirror_symmetric_about_case_x0": False,
        "opening_vertex_average_x_mm": round(
            sum(point[0] for point in v21.OPENING_POINTS) / len(v21.OPENING_POINTS),
            3,
        ),
        "screen_hole_pattern_centre_x_mm": round(
            sum(v19.HOLE_X) / len(v19.HOLE_X), 4
        ),
        "opening_screw_clearances": screw_clearances,
        "ear_centres_mm": [
            [round(x, 3), v19.head.WING_CENTRE_Y] for x in EAR_CENTRES
        ],
        "tunnel_x_ranges_mm": [
            [-round(TUNNEL_OUTER_ABS, 3), -round(TUNNEL_INNER_ABS, 3)],
            [round(TUNNEL_INNER_ABS, 3), round(TUNNEL_OUTER_ABS, 3)],
        ],
        "tunnel_clear_section_mm": [TUNNEL_CLEAR_WIDTH, TUNNEL_CLEAR_HEIGHT],
        "tunnel_centre_y_mm": v19.head.WING_CENTRE_Y,
        "tunnel_z_range_mm": [
            round(TUNNEL_REAR_Z, 3),
            round(TUNNEL_REAR_Z + TUNNEL_CLEAR_HEIGHT, 3),
        ],
        "tunnel_drop_below_old_route_mm": TUNNEL_DROP_BELOW_OLD_ROUTE,
        "raceway_outer_section_mm": [RACEWAY_WIDTH, RACEWAY_HEIGHT],
        "raceway_wall_mm": RACEWAY_WALL,
        "raceway_roof_overlap_mm": RACEWAY_ROOF_OVERLAP,
        "raceway_rear_limit_mm": round(RACEWAY_REAR_Z, 3),
        "tunnel_entry": "3 mm overlap into each V21 opening side wall at x +/-89 mm",
        "tunnel_termination": "true hollow-ear centre at x +/-143.077 mm",
        "blue_screen_frame_cut_for_usb": False,
        "routing_form": "roofed internal tunnel, never an open canal",
        "preserved": [
            "V21 service opening",
            "V19 exterior screen frame and recessed bevel",
            "four screen screw towers",
            "six-slot rear grill",
            "top-facing USB-A ear sockets",
            "FLX6 brackets and alignment",
        ],
        "production_gate": (
            "fit-check the selected female USB-A extension body and cable bend radius"
        ),
    }
    (HERE / "inspection-codex-v23-centered-usb-tunnels.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    print(json.dumps(export(), indent=2))
