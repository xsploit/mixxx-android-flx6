"""Build enclosed USB tunnels aligned across both ears.

V23 preserves the approved V21 service opening and the frozen V19 exterior.
It first fills the obsolete short V18/V19 cable cuts, then cuts two new roofed
passages from the V21 opening side walls to the hollow centres of the USB ears.
The blue screen frame is never cut for routing.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import cadquery as cq

import build_codex_v19_polished_structure as v19
import build_codex_v21_bay_merged_structure as v21


HERE = Path(__file__).resolve().parent

DESIGN_VERSION = os.environ.get("PIFLEX_TUNNEL_VERSION", "v23")
DESIGN_SLUG = os.environ.get("PIFLEX_TUNNEL_SLUG", "centered-usb-tunnels")

OPENING_MIDDLE_HALF_WIDTH = 89.0
TUNNEL_ENTRY_OVERLAP = 3.0
TUNNEL_CLEAR_WIDTH = 18.4
TUNNEL_CLEAR_HEIGHT = 10.0
TUNNEL_CENTRE_Y = float(os.environ.get("PIFLEX_TUNNEL_CENTRE_Y", "0.0"))
EAR_CENTRED_DOGLEG = os.environ.get("PIFLEX_EAR_CENTRED_DOGLEG") == "1"
OPEN_INNER_CHANNEL = os.environ.get("PIFLEX_OPEN_INNER_CHANNEL") == "1"
TUNNEL_DROP_BELOW_OLD_ROUTE = 4.5
TUNNEL_REAR_Z = float(
    os.environ.get(
        "PIFLEX_TUNNEL_REAR_Z",
        -v19.head.WING_REAR_DEPTH
        + v19.head.WING_WALL
        - TUNNEL_DROP_BELOW_OLD_ROUTE,
    )
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
EAR_CAVITY_REAR_Z = -v19.head.WING_REAR_DEPTH + v19.head.WING_WALL
EAR_CAVITY_FRONT_Z = v19.head.SCREEN_DEPTH - v19.head.WING_WALL
EAR_CAVITY_CENTRE_Z = (EAR_CAVITY_REAR_Z + EAR_CAVITY_FRONT_Z) / 2.0
EAR_TUNNEL_REAR_Z = EAR_CAVITY_CENTRE_Z - TUNNEL_CLEAR_HEIGHT / 2.0
SHELL_OUTER_X = v19.head.SCREEN_WIDTH / 2.0
EAR_RISER_INNER_ABS = SHELL_OUTER_X + 0.6
EAR_HIGH_RUN_INNER_ABS = EAR_RISER_INNER_ABS + 3.0
INNER_HIGH_RUN_OUTER_ABS = OPENING_MIDDLE_HALF_WIDTH - 0.5
# Run the opening completely through the exact shell edge; stopping on the
# coincident boundary leaves an open STL seam after float32 export.
OPEN_CHANNEL_OUTER_ABS = SHELL_OUTER_X + 1.0
OPEN_CHANNEL_SEAM_CLEARANCE = 0.20
OPEN_CHANNEL_BLUE_ROOF_LENGTH = float(
    os.environ.get("PIFLEX_OPEN_CHANNEL_BLUE_ROOF_LENGTH", "0.0")
)
OPEN_CHANNEL_ROOF_CUT_OUTER_ABS = (
    SHELL_OUTER_X - OPEN_CHANNEL_BLUE_ROOF_LENGTH
)
OPEN_CHANNEL_FLOOR_TOP_Z = float(
    os.environ.get("PIFLEX_OPEN_CHANNEL_FLOOR_TOP_Z", str(TUNNEL_REAR_Z))
)
EAR_USB_OPENING_TOP_Z = (
    v19.head.USB_OPENING_CENTRE_Z + v19.head.USB_OPENING_Z / 2.0
)
EAR_USB_OPENING_ORIGINAL_FLOOR_Z = (
    v19.head.USB_OPENING_CENTRE_Z - v19.head.USB_OPENING_Z / 2.0
)
EAR_USB_CUT_FLOOR_Z = float(
    os.environ.get(
        "PIFLEX_EAR_USB_CUT_FLOOR_Z",
        str(EAR_USB_OPENING_ORIGINAL_FLOOR_Z),
    )
)
EAR_USB_OPENING_OUTER_Y = (
    v19.head.WING_CENTRE_Y + v19.head.WING_HEIGHT / 2.0 + 6.0
)
EAR_USB_OPENING_ORIGINAL_INNER_Y = (
    v19.head.WING_CENTRE_Y + v19.head.WING_HEIGHT / 2.0 - 6.0
)
EAR_USB_CUT_INNER_Y = float(
    os.environ.get(
        "PIFLEX_EAR_USB_CUT_INNER_Y",
        str(EAR_USB_OPENING_ORIGINAL_INNER_Y),
    )
)


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
                    TUNNEL_CENTRE_Y,
                    TUNNEL_REAR_Z,
                )
            )
        )
        if EAR_CENTRED_DOGLEG:
            # Keep the middle span beneath the untouched blue shell. At the
            # already-open bay edge and inside the hollow ear, extend upward
            # to the ear cavity's true top-to-bottom centre.
            inner_high_length = INNER_HIGH_RUN_OUTER_ABS - TUNNEL_INNER_ABS
            inner_high_centre = sign * (
                TUNNEL_INNER_ABS + INNER_HIGH_RUN_OUTER_ABS
            ) / 2.0
            inner_riser = (
                cq.Workplane("XY")
                .box(
                    inner_high_length,
                    TUNNEL_CLEAR_WIDTH,
                    EAR_TUNNEL_REAR_Z + TUNNEL_CLEAR_HEIGHT - TUNNEL_REAR_Z,
                    centered=(True, True, False),
                )
                .translate((inner_high_centre, TUNNEL_CENTRE_Y, TUNNEL_REAR_Z))
            )

            ear_high_length = TUNNEL_OUTER_ABS - EAR_RISER_INNER_ABS
            ear_high_centre = sign * (
                EAR_RISER_INNER_ABS + TUNNEL_OUTER_ABS
            ) / 2.0
            ear_high = (
                cq.Workplane("XY")
                .box(
                    ear_high_length,
                    TUNNEL_CLEAR_WIDTH,
                    TUNNEL_CLEAR_HEIGHT,
                    centered=(True, True, False),
                )
                .translate((ear_high_centre, TUNNEL_CENTRE_Y, EAR_TUNNEL_REAR_Z))
            )
            ear_riser_length = EAR_HIGH_RUN_INNER_ABS - EAR_RISER_INNER_ABS
            ear_riser_centre = sign * (
                EAR_RISER_INNER_ABS + EAR_HIGH_RUN_INNER_ABS
            ) / 2.0
            ear_riser = (
                cq.Workplane("XY")
                .box(
                    ear_riser_length,
                    TUNNEL_CLEAR_WIDTH,
                    EAR_TUNNEL_REAR_Z + TUNNEL_CLEAR_HEIGHT - TUNNEL_REAR_Z,
                    centered=(True, True, False),
                )
                .translate((ear_riser_centre, TUNNEL_CENTRE_Y, TUNNEL_REAR_Z))
            )
            passage = passage.union(inner_riser).union(ear_riser).union(ear_high)
        passages.append(passage.combine(clean=True))
    return passages


def roof_opening_cutters():
    """Open only the inner run; the portion inside each USB ear stays roofed."""
    if not OPEN_INNER_CHANNEL:
        return []
    cutter_rear_z = OPEN_CHANNEL_FLOOR_TOP_Z + 0.02
    cutter_height = v19.head.SCREEN_DEPTH + 4.0 - cutter_rear_z
    cutter_length = OPEN_CHANNEL_ROOF_CUT_OUTER_ABS - TUNNEL_INNER_ABS
    cutters = []
    for sign in (-1.0, 1.0):
        centre_x = sign * (
            TUNNEL_INNER_ABS + OPEN_CHANNEL_ROOF_CUT_OUTER_ABS
        ) / 2.0
        cutters.append(
            cq.Workplane("XY")
            .box(
                cutter_length,
                TUNNEL_CLEAR_WIDTH + 2.0 * OPEN_CHANNEL_SEAM_CLEARANCE,
                cutter_height,
                centered=(True, True, False),
            )
            .translate((centre_x, TUNNEL_CENTRE_Y, cutter_rear_z))
        )
    return cutters


def routing_cutters():
    tunnels = corrected_usb_tunnels()
    roofs = roof_opening_cutters()
    if not roofs:
        return tunnels
    return [
        tunnel.union(roof).combine(clean=True)
        for tunnel, roof in zip(tunnels, roofs)
    ]


def deepened_ear_usb_cutters():
    """Extend each top-edge USB opening down and inward into the hollow ear."""
    if (
        EAR_USB_CUT_FLOOR_Z >= EAR_USB_OPENING_ORIGINAL_FLOOR_Z
        and EAR_USB_CUT_INNER_Y >= EAR_USB_OPENING_ORIGINAL_INNER_Y
    ):
        return []
    cut_height = EAR_USB_OPENING_TOP_Z - EAR_USB_CUT_FLOOR_Z
    cut_depth = EAR_USB_OPENING_OUTER_Y - EAR_USB_CUT_INNER_Y
    cut_centre_y = (EAR_USB_OPENING_OUTER_Y + EAR_USB_CUT_INNER_Y) / 2.0
    return [
        cq.Workplane("XY")
        .box(
            v19.head.USB_OPENING_X,
            cut_depth,
            cut_height,
            centered=(True, True, False),
        )
        .translate(
            (
                x,
                cut_centre_y,
                EAR_USB_CUT_FLOOR_Z,
            )
        )
        for x in EAR_CENTRES
    ]


def tunnel_housings():
    """Rounded outer raceways that retain a floor and walls below the bevel."""
    if OPEN_INNER_CHANNEL:
        # The inner span is a flat floor only. Its top is exactly the old
        # tunnel floor plane, so there is no raised U-shaped lip. A full
        # housing resumes just before the screen-shell edge and remains closed
        # through the USB ear.
        floor_inner_abs = TUNNEL_INNER_ABS - RACEWAY_WALL
        floor_outer_abs = OPEN_CHANNEL_OUTER_ABS + 1.0
        enclosed_inner_abs = OPEN_CHANNEL_OUTER_ABS - 1.0
        enclosed_outer_abs = TUNNEL_OUTER_ABS + RACEWAY_WALL
        housings = []
        for sign in (-1.0, 1.0):
            floor_centre = sign * (floor_inner_abs + floor_outer_abs) / 2.0
            floor = v19.head.rounded_box(
                floor_outer_abs - floor_inner_abs,
                RACEWAY_WIDTH,
                RACEWAY_WALL,
                OPEN_CHANNEL_FLOOR_TOP_Z - RACEWAY_WALL,
                3.0,
            ).translate((floor_centre, TUNNEL_CENTRE_Y, 0.0))
            enclosed_centre = sign * (
                enclosed_inner_abs + enclosed_outer_abs
            ) / 2.0
            enclosed = v19.head.rounded_box(
                enclosed_outer_abs - enclosed_inner_abs,
                RACEWAY_WIDTH,
                RACEWAY_HEIGHT,
                RACEWAY_REAR_Z,
                4.0,
            ).translate((enclosed_centre, TUNNEL_CENTRE_Y, 0.0))
            housings.append(floor.union(enclosed).combine(clean=True))
        return housings

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
        ).translate((centre_x, TUNNEL_CENTRE_Y, 0.0))
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
    for tunnel in routing_cutters():
        polished = polished.cut(tunnel)
    for ear_usb in deepened_ear_usb_cutters():
        polished = polished.cut(ear_usb)
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
for tunnel in routing_cutters():
    complete = complete.cut(v19.head.to_bracket_coordinates(tunnel))
complete = complete.combine(clean=True)
shape = complete.val()
solids = v19.head.bracket_source._nested_solids(shape)

if not shape.isValid() or len(solids) != 1:
    raise RuntimeError(
        f"V23 must be one valid solid; valid={shape.isValid()} solids={len(solids)}"
    )


def export():
    stem = f"piflex-codex-{DESIGN_VERSION}-{DESIGN_SLUG}"
    structure_stl = HERE / f"{stem}-structure.stl"
    structure_step = HERE / f"{stem}-structure.step"
    rear_stl = HERE / f"{stem}-rear-local.stl"
    tunnel_voids_stl = HERE / f"piflex-codex-{DESIGN_VERSION}-usb-tunnel-voids-local.stl"
    registered_tunnel_voids_stl = (
        HERE
        / f"piflex-codex-{DESIGN_VERSION}-usb-tunnel-voids-structure-coordinates.stl"
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
        [tunnel.val() for tunnel in routing_cutters()]
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
        "design": f"PiFlex Codex {DESIGN_VERSION.upper()} enclosed USB tunnels",
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
        "tunnel_centre_y_mm": TUNNEL_CENTRE_Y,
        "tunnel_y_range_mm": [
            round(TUNNEL_CENTRE_Y - TUNNEL_CLEAR_WIDTH / 2.0, 3),
            round(TUNNEL_CENTRE_Y + TUNNEL_CLEAR_WIDTH / 2.0, 3),
        ],
        "tunnel_z_range_mm": [
            round(TUNNEL_REAR_Z, 3),
            round(TUNNEL_REAR_Z + TUNNEL_CLEAR_HEIGHT, 3),
        ],
        "ear_cavity_z_range_mm": [
            round(EAR_CAVITY_REAR_Z, 3),
            round(EAR_CAVITY_FRONT_Z, 3),
        ],
        "ear_cavity_centre_z_mm": round(EAR_CAVITY_CENTRE_Z, 3),
        "ear_tunnel_z_range_mm": [
            round(EAR_TUNNEL_REAR_Z, 3),
            round(EAR_TUNNEL_REAR_Z + TUNNEL_CLEAR_HEIGHT, 3),
        ],
        "ear_usb_opening_z_range_mm": [
            round(EAR_USB_CUT_FLOOR_Z, 3),
            round(EAR_USB_OPENING_TOP_Z, 3),
        ],
        "ear_usb_opening_deepened_mm": round(
            EAR_USB_OPENING_ORIGINAL_FLOOR_Z - EAR_USB_CUT_FLOOR_Z,
            3,
        ),
        "ear_usb_pocket_y_range_mm": [
            round(EAR_USB_CUT_INNER_Y, 3),
            round(EAR_USB_OPENING_OUTER_Y, 3),
        ],
        "ear_usb_pocket_inward_depth_mm": round(
            EAR_USB_OPENING_OUTER_Y - EAR_USB_CUT_INNER_Y,
            3,
        ),
        "ear_usb_pocket_extra_inward_mm": round(
            EAR_USB_OPENING_ORIGINAL_INNER_Y - EAR_USB_CUT_INNER_Y,
            3,
        ),
        "ear_centred_dogleg": EAR_CENTRED_DOGLEG,
        "open_inner_channel": OPEN_INNER_CHANNEL,
        "open_channel_outer_abs_x_mm": (
            round(OPEN_CHANNEL_ROOF_CUT_OUTER_ABS, 3)
            if OPEN_INNER_CHANNEL
            else None
        ),
        "blue_roof_bridge_length_mm": (
            round(OPEN_CHANNEL_BLUE_ROOF_LENGTH, 3)
            if OPEN_INNER_CHANNEL
            else None
        ),
        "open_channel_floor_top_z_mm": (
            round(OPEN_CHANNEL_FLOOR_TOP_Z, 3) if OPEN_INNER_CHANNEL else None
        ),
        "tunnel_drop_below_old_route_mm": TUNNEL_DROP_BELOW_OLD_ROUTE,
        "raceway_outer_section_mm": [RACEWAY_WIDTH, RACEWAY_HEIGHT],
        "raceway_y_range_mm": [
            round(TUNNEL_CENTRE_Y - RACEWAY_WIDTH / 2.0, 3),
            round(TUNNEL_CENTRE_Y + RACEWAY_WIDTH / 2.0, 3),
        ],
        "ear_y_range_mm": [
            round(v19.head.WING_CENTRE_Y - v19.head.WING_HEIGHT / 2.0, 3),
            round(v19.head.WING_CENTRE_Y + v19.head.WING_HEIGHT / 2.0, 3),
        ],
        "raceway_wall_mm": RACEWAY_WALL,
        "raceway_roof_overlap_mm": RACEWAY_ROOF_OVERLAP,
        "raceway_rear_limit_mm": round(RACEWAY_REAR_Z, 3),
        "tunnel_entry": "3 mm overlap into each V21 opening side wall at x +/-89 mm",
        "tunnel_termination": (
            "hollow-ear sockets at x +/-143.077 mm, "
            f"y {TUNNEL_CENTRE_Y:g} mm, z 2.34 mm"
            if EAR_CENTRED_DOGLEG
            else "true hollow-ear X centre at x +/-143.077 mm"
        ),
        "blue_screen_frame_cut_for_usb": OPEN_INNER_CHANNEL,
        "routing_form": (
            "flush open inner channel with enclosed USB-ear tunnel"
            if OPEN_INNER_CHANNEL
            else "roofed internal tunnel, never an open canal"
        ),
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
    (HERE / f"inspection-codex-{DESIGN_VERSION}-{DESIGN_SLUG}.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    print(json.dumps(export(), indent=2))
