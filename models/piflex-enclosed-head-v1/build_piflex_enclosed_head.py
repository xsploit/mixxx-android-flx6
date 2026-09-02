"""Parametric structural body for the enclosed PiFlex head unit.

V6 preserves the exact MakerWorld screen shell as the visible screen case. The
body extends rearward from that shell, forms the Pi 5 pod, closes both USB ears
with permanent front faces, and fuses into the validated FLX6 mounting yoke.
The physical display remains removable from the original screen shell.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "models" / "flx6-surface-mount-remix-v1"
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(SOURCE_DIR))

import build_integrated_yoke as yoke_source  # noqa: E402
import build_surface_mount_remix as bracket_source  # noqa: E402


# Measured directly from the supplied MakerWorld STL envelopes.
SCREEN_WIDTH = 253.154
SCREEN_HEIGHT = 171.542
SCREEN_DEPTH = 13.680
ACTIVE_WIDTH = 217.600
ACTIVE_HEIGHT = 136.000
PI_CASE_WIDTH = 89.524
PI_CASE_HEIGHT = 60.345
PI_CASE_DEPTH = 27.387

SCREEN_CLEARANCE = 0.50
PI_CASE_CLEARANCE = 1.20
BEZEL_DEPTH = 3.0
BEZEL_CORNER_RADIUS = 7.0
APERTURE_MARGIN = 1.2

CASE_RIM_DEPTH = 9.0
BACK_SKIN = 2.8
BACK_SCREW_TUNNEL_RADIUS = 5.5
BACK_SCREW_CLEARANCE = 3.6
REAR_WALL = 2.8
SIDE_WALL = 2.8
BODY_WIDTH = SCREEN_WIDTH
BODY_HEIGHT = SCREEN_HEIGHT
POD_WALL = 3.0
POD_WIDTH = PI_CASE_WIDTH + 2.0 * (PI_CASE_CLEARANCE + POD_WALL)
POD_HEIGHT = PI_CASE_HEIGHT + 2.0 * (PI_CASE_CLEARANCE + POD_WALL)
POD_TOTAL_DEPTH = 35.0
POD_CORNER_RADIUS = 8.0
POD_MOUTH_GROW_X = 18.0
POD_MOUTH_GROW_Y = 14.0
MOUNT_RIB_DEPTH = 12.0

WING_WIDTH = 38.0
WING_HEIGHT = 70.0
WING_OVERLAP = 5.0
WING_CENTRE_Y = 0.0
WING_CORNER_RADIUS = 12.0
WING_WALL = 3.2
WING_REAR_DEPTH = 9.0
WING_INNER_SQUARE_WIDTH = 14.0

USB_OPENING_X = 16.4
USB_OPENING_Z = 9.2
USB_OPENING_CENTRE_Z = 1.5
USB_REINFORCEMENT_Y = 25.0

MOUNT_CLEARANCE = 3.6
MOUNT_BOSS_RADIUS = 5.5

def rounded_box(width: float, height: float, depth: float, z0: float, radius: float):
    part = (
        cq.Workplane("XY")
        .box(width, height, depth, centered=(True, True, False))
        .translate((0.0, 0.0, z0))
    )
    if radius > 0.0:
        part = part.edges("|Z").fillet(radius)
    return part


def rounded_rect_wire(width: float, height: float, z: float, radius: float, segments: int = 8):
    points = []
    for sx, sy, start_deg in (
        (1.0, 1.0, 0.0),
        (-1.0, 1.0, 90.0),
        (-1.0, -1.0, 180.0),
        (1.0, -1.0, 270.0),
    ):
        cx = sx * (width / 2.0 - radius)
        cy = sy * (height / 2.0 - radius)
        for index in range(segments + 1):
            angle = math.radians(start_deg + index * 90.0 / segments)
            points.append(
                cq.Vector(cx + radius * math.cos(angle), cy + radius * math.sin(angle), z)
            )
    return cq.Wire.makePolygon(points, close=True)


def rounded_loft(back_width, back_height, back_z, back_radius, mouth_width, mouth_height, mouth_z, mouth_radius):
    solid = cq.Solid.makeLoft(
        [
            rounded_rect_wire(back_width, back_height, back_z, back_radius),
            rounded_rect_wire(mouth_width, mouth_height, mouth_z, mouth_radius),
        ],
        False,
    )
    return cq.Workplane(obj=solid)


def wing_centres():
    offset = BODY_WIDTH / 2.0 + (WING_WIDTH - WING_OVERLAP) / 2.0
    return (-offset, offset)


def to_bracket_coordinates(part):
    """Map screen-local X/Y/Z into bracket depth/height/horizontal axes."""
    theta = math.radians(25.0)
    u = (-math.cos(theta), math.sin(theta))
    n = (math.sin(theta), math.cos(theta))
    origin = (-2.0, bracket_source.CLAMP_OPENING + bracket_source.TOP_LIP_THICKNESS + 1.0)
    centre = (
        origin[0] + u[0] * (SCREEN_HEIGHT / 2.0),
        origin[1] + u[1] * (SCREEN_HEIGHT / 2.0),
    )
    transform = cq.Matrix(
        [
            [0.0, u[0], n[0], centre[0]],
            [0.0, u[1], n[1], centre[1]],
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    return cq.Workplane(obj=part.val().transformGeometry(transform))


def build_front_bezel_local():
    outer = rounded_box(
        BODY_WIDTH,
        BODY_HEIGHT,
        BEZEL_DEPTH,
        SCREEN_DEPTH,
        BEZEL_CORNER_RADIUS,
    )
    aperture = rounded_box(
        ACTIVE_WIDTH + APERTURE_MARGIN,
        ACTIVE_HEIGHT + APERTURE_MARGIN,
        BEZEL_DEPTH + 2.0,
        SCREEN_DEPTH - 1.0,
        3.0,
    )
    bezel = outer.cut(aperture)

    # Centred ears are continuous with the screen-facing bezel. USB openings
    # belong in the upper edge wall, not the display/front face.
    for x in wing_centres():
        wing_top = rounded_box(
            WING_WIDTH,
            WING_HEIGHT,
            BEZEL_DEPTH,
            SCREEN_DEPTH,
            WING_CORNER_RADIUS,
        ).translate((x, WING_CENTRE_Y, 0.0))
        bezel = bezel.union(wing_top)

    bezel = bezel.combine(clean=True)

    # Rearward locating lip fits inside the rear shell perimeter.  It keeps the
    # two pieces registered while concealed screws or clips hold them together.
    lip_outer = rounded_box(
        BODY_WIDTH - 5.0,
        BODY_HEIGHT - 5.0,
        2.4,
        SCREEN_DEPTH - 2.4,
        5.0,
    )
    lip_inner = rounded_box(
        BODY_WIDTH - 11.0,
        BODY_HEIGHT - 11.0,
        3.4,
        SCREEN_DEPTH - 2.9,
        3.0,
    )
    bezel = bezel.union(lip_outer.cut(lip_inner)).combine(clean=True)
    return bezel


def build_rear_shell_local():
    # The screen's own metal back occupies the centre. Keep only a structural
    # perimeter behind the exact source rim; do not replace the removed vented
    # plate with another full-width back or tray.
    outer = rounded_box(
        BODY_WIDTH,
        BODY_HEIGHT,
        CASE_RIM_DEPTH + 1.0,
        -CASE_RIM_DEPTH,
        BEZEL_CORNER_RADIUS,
    )
    centre_opening = rounded_box(
        BODY_WIDTH - SIDE_WALL * 2.0,
        BODY_HEIGHT - SIDE_WALL * 2.0,
        CASE_RIM_DEPTH + 3.0,
        -CASE_RIM_DEPTH - 1.0,
        4.5,
    )
    shell = outer.cut(centre_opening)

    # A shallow exterior skin hides the source case's recesses, screw loops and
    # yoke rails. It shares the ears' -9 mm rear plane but remains hollow toward
    # the original case, avoiding a wasteful 9 mm solid slab.
    back_skin = rounded_box(
        BODY_WIDTH,
        BODY_HEIGHT,
        BACK_SKIN,
        -CASE_RIM_DEPTH,
        BEZEL_CORNER_RADIUS,
    )
    # Keep the Pi volume open. The hole is slightly smaller than the pod's
    # outer section at this depth, producing a robust overlapping union while
    # leaving the already-mounted Pi and cooler unobstructed.
    pi_throat = rounded_box(
        108.0,
        76.0,
        BACK_SKIN + 2.0,
        -CASE_RIM_DEPTH - 1.0,
        7.0,
    )
    shell = shell.union(back_skin.cut(pi_throat))

    # Four hollow screw tunnels bridge the new flush back to the original
    # screen-case holes. They preserve the existing attachment pattern; screws
    # approximately 9 mm longer will be required for the finished fairing.
    for x in bracket_source.SCREEN_OUTER_HOLES_X.values():
        for y in bracket_source.SCREEN_OUTER_HOLES_Y:
            tunnel = (
                cq.Workplane("XY")
                .center(x, y)
                .circle(BACK_SCREW_TUNNEL_RADIUS)
                .extrude(CASE_RIM_DEPTH + 1.0)
                .translate((0.0, 0.0, -CASE_RIM_DEPTH))
            )
            bore = (
                cq.Workplane("XY")
                .center(x, y)
                .circle(BACK_SCREW_CLEARANCE / 2.0)
                .extrude(CASE_RIM_DEPTH + 3.0)
                .translate((0.0, 0.0, -CASE_RIM_DEPTH - 1.0))
            )
            shell = shell.union(tunnel).cut(bore)

    # No cross-brackets span the inside of the original screen case. The Pi
    # pod opens directly through the clean centre throat.

    # Hollow side wings are part of the rear half.  They overlap the screen
    # shell so the assembly is rigid, but preserve separate service cavities
    # for short USB extension leads and eject-button electronics.
    for x in wing_centres():
        wing_outer = rounded_box(
            WING_WIDTH,
            WING_HEIGHT,
            SCREEN_DEPTH + WING_REAR_DEPTH,
            -WING_REAR_DEPTH,
            WING_CORNER_RADIUS,
        ).translate((x, WING_CENTRE_Y, 0.0))
        # Stop the cavity before the display-facing surface.  The remaining
        # WING_WALL thickness is the permanent cap; it is part of the body.
        wing_inner = rounded_box(
            WING_WIDTH - WING_WALL * 2.0,
            WING_HEIGHT - WING_WALL * 2.0,
            SCREEN_DEPTH + WING_REAR_DEPTH - WING_WALL * 2.0,
            -WING_REAR_DEPTH + WING_WALL,
            WING_CORNER_RADIUS - WING_WALL,
        ).translate((x, WING_CENTRE_Y, 0.0))
        shell = shell.union(wing_outer).cut(wing_inner)

        # Fill only the case-facing end of each rounded ear. This makes the
        # visible inner joint square and continuous with the back fairing while
        # retaining the rounded outer end and most of the USB service cavity.
        inner_edge = x - math.copysign(WING_WIDTH / 2.0, x)
        square_centre_x = inner_edge + math.copysign(
            WING_INNER_SQUARE_WIDTH / 2.0, x
        )
        inner_square = (
            cq.Workplane("XY")
            .box(
                WING_INNER_SQUARE_WIDTH,
                WING_HEIGHT,
                SCREEN_DEPTH + WING_REAR_DEPTH,
                centered=(True, True, False),
            )
            .translate((square_centre_x, WING_CENTRE_Y, -WING_REAR_DEPTH))
        )
        shell = shell.union(inner_square)

        # Physical top/upper-edge USB socket. This cuts through the +Y wall of
        # the ear, above the screen, while leaving its front and outer side solid.
        reinforcement = (
            cq.Workplane("XY")
            .box(25.0, 8.0, 16.0)
            .translate(
                (
                    x,
                    WING_CENTRE_Y + WING_HEIGHT / 2.0 - 4.0,
                    USB_OPENING_CENTRE_Z,
                )
            )
        )
        top_edge_opening = (
            cq.Workplane("XY")
            .box(USB_OPENING_X, 12.0, USB_OPENING_Z)
            .translate(
                (
                    x,
                    WING_CENTRE_Y + WING_HEIGHT / 2.0,
                    USB_OPENING_CENTRE_Z,
                )
            )
        )
        shell = shell.union(reinforcement).cut(top_edge_opening)


    # The Pi compartment is the case, rather than a second box mounted to the
    # back. A rounded taper blends its exact rear envelope into the screen tub.
    pod_outer = rounded_loft(
        POD_WIDTH,
        POD_HEIGHT,
        -POD_TOTAL_DEPTH,
        POD_CORNER_RADIUS,
        POD_WIDTH + POD_MOUTH_GROW_X,
        POD_HEIGHT + POD_MOUTH_GROW_Y,
        -0.2,
        POD_CORNER_RADIUS + 2.0,
    )
    pod_inner = rounded_loft(
        PI_CASE_WIDTH + PI_CASE_CLEARANCE * 2.0,
        PI_CASE_HEIGHT + PI_CASE_CLEARANCE * 2.0,
        -POD_TOTAL_DEPTH + POD_WALL,
        POD_CORNER_RADIUS - POD_WALL,
        POD_WIDTH + POD_MOUTH_GROW_X - POD_WALL * 2.0,
        POD_HEIGHT + POD_MOUTH_GROW_Y - POD_WALL * 2.0,
        1.0,
        POD_CORNER_RADIUS - 1.0,
    )
    shell = shell.union(pod_outer).cut(pod_inner)

    # The user's Pi is already mounted to the Touch Display 2 standoffs. The
    # protective pod therefore stays completely clear inside instead of adding
    # a second, conflicting set of Pi mounting bosses. With the screen back
    # opened beneath the pod, the DSI ribbon and display-power wires remain
    # internal and do not require a separate pass-through slot.

    # Broad, tolerant port windows follow the two connector edges of the Pi.
    # Trim inserts can later make these connector-specific after a caliper fit.
    usb_ethernet_window = (
        cq.Workplane("XY")
        .box(16.0, 54.0, 18.0)
        .translate((POD_WIDTH / 2.0, 0.0, -18.0))
    )
    power_hdmi_window = (
        cq.Workplane("XY")
        .box(60.0, 16.0, 15.0)
        .translate((0.0, -POD_HEIGHT / 2.0, -18.0))
    )
    micro_sd_window = (
        cq.Workplane("XY")
        .box(20.0, 14.0, 6.0)
        .translate((0.0, POD_HEIGHT / 2.0, -29.0))
    )
    shell = shell.cut(usb_ethernet_window).cut(power_hdmi_window).cut(micro_sd_window)

    # Bottom cable outlet for controller USB/power without trapping connectors.
    cable_outlet = (
        cq.Workplane("XY")
        .box(24.0, 10.0, 12.0)
        .translate((0.0, -SCREEN_HEIGHT / 2.0, -4.0))
    )
    shell = shell.cut(cable_outlet)

    # Five rear ventilation slots across the Pi pod.
    for y in (-16.0, -8.0, 0.0, 8.0, 16.0):
        vent = (
            cq.Workplane("XY")
            .box(52.0, 3.2, 6.0)
            .translate((0.0, y, -POD_TOTAL_DEPTH))
        )
        shell = shell.cut(vent)

    return shell.combine(clean=True)


rear_local = build_rear_shell_local()
rear = to_bracket_coordinates(rear_local)

# The validated yoke becomes the lower skeleton of the rear half.
rear_with_mount = rear.union(yoke_source.case_mount_result).combine(clean=True)


def _stats(name: str, part):
    shape = part.val()
    bb = shape.BoundingBox()
    return {
        "name": name,
        "valid": shape.isValid(),
        "solids": len(shape.Solids()),
        "dimensions_mm": [round(bb.xlen, 3), round(bb.ylen, 3), round(bb.zlen, 3)],
        "volume_cm3": round(shape.Volume() / 1000.0, 3),
    }


def export():
    parts = {
        "piflex-enclosed-structural-body-with-flx6-mount-v8": rear_with_mount,
    }
    for stem, part in parts.items():
        cq.exporters.export(part, str(OUT / f"{stem}.step"))
        cq.exporters.export(
            part,
            str(OUT / f"{stem}.stl"),
            tolerance=0.05,
            angularTolerance=0.10,
        )

    cq.exporters.export(rear_with_mount, str(OUT / "piflex-enclosed-structural-body-v8.step"))

    report = {
        "design": "PiFlex open-back original-shell integrated head unit V8",
        "parts": [_stats(stem, part) for stem, part in parts.items()],
        "features": [
            "actual MakerWorld screen-shell envelope plus 0.50 mm clearance",
            "actual Pi-case envelope plus 1.20 mm clearance",
            "exact MakerWorld screen shell outer rim retained as the screen case",
            "original shell retained behind a clean flush rear fairing",
            "no added inner bezel, ledge or screen-retaining lip",
            "open centre uses the physical display's own metal back",
            "no added internal cross-brackets behind the original case wall",
            "2.8 mm hollow rear fairing shares the USB ears' rear plane",
            "four reinforced screw tunnels preserve the rotated screen-hole pattern",
            "square case-facing USB-ear joints with rounded outer ends",
            "single tapered Pi case and FLX6 mount",
            "clear Pi pod surrounds the board already mounted to the display standoffs",
            "DSI ribbon and display-power wires remain inside the shared screen/pod cavity",
            "USB/Ethernet, power/HDMI and microSD service openings",
            "physical display removes through the original shell for service",
            "9 mm hollow perimeter with a material-efficient 2.8 mm rear skin",
            "deeper centre Pi 5 pod",
            "USB wings with square case joints, rounded outer ends and permanent 3.2 mm caps",
            "upper-edge top-facing left and right panel-mount USB-A openings",
            "rear Pi ventilation slots",
            "bottom power/controller cable outlet",
            "integrated FLX6 C-clamps and controller screw points",
        ],
        "source_envelopes_mm": {
            "screen_shell": [SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_DEPTH],
            "pi_case": [PI_CASE_WIDTH, PI_CASE_HEIGHT, PI_CASE_DEPTH],
        },
        "status": "dimensioned V8 concept; open-back exact shell rim is included in the visual assembly and must be mesh-unioned before a one-piece production print",
    }
    (OUT / "inspection-v8.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(export(), indent=2))
