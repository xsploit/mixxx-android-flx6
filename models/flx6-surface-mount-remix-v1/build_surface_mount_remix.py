"""Parametric FLX6 remix of the supplied ``surfacemountddj.stl``.

The source stand's useful construction is retained: a full C-clamp carries the
controller and a side channel carries the display.  The mesh itself is not
deformed.  Rebuilding the profile makes the controller opening, screen cavity,
and viewing angle measurable and editable.

Coordinate system for one bracket:
    X: controller depth, positive toward the front of the controller
    Y: vertical
    Z: bracket width
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import cadquery as cq
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS


OUT = Path(__file__).resolve().parent

# Measured/reference geometry in millimetres.
FLX6_BODY_HEIGHT = 47.887
SCREEN_CASE_HEIGHT = 171.542
SCREEN_CASE_THICKNESS = 13.680

# Adjustable print-fit parameters.
BRACKET_WIDTH = 20.0
CLAMP_OPENING = 50.0
LOWER_JAW_DEPTH = 50.0
LOWER_JAW_THICKNESS = 5.0
REAR_WALL_THICKNESS = 6.0
TOP_LIP_DEPTH = 14.0
TOP_LIP_THICKNESS = 5.0
CONTROLLER_SCREW_HEIGHT = 19.0
CONTROLLER_SCREW_CLEARANCE = 3.6
CONTROLLER_SCREW_COUNTERBORE = 7.0
CONTROLLER_SCREW_COUNTERBORE_DEPTH = 2.2

# Outer mounting holes measured directly from the MakerWorld 10-inch shell STL.
# Source-shell coordinates are X horizontal, Y vertical, Z through thickness.
# The source shell must be rotated 180 degrees in its own plane so its molded
# rear text is upright. These are the correspondingly rotated hole centres:
# (x, y) -> (-x, -y).
SCREEN_OUTER_HOLES_X = {"left": -77.657, "right": 82.344}
SCREEN_OUTER_HOLES_Y = (-61.034, 60.768)
SCREEN_MOUNT_CLEARANCE = 3.6
SCREEN_MOUNT_COUNTERBORE = 7.0
SCREEN_MOUNT_COUNTERBORE_DEPTH = 2.4
SCREEN_TAB_RADIUS = 8.0

# Centered assembly bracket locations.  Local bracket Z=0 begins at the
# bracket's left/global-X edge because the bracket is extruded from 0..width.
CENTERED_BRACKET_X = {"left": -100.82, "right": 100.82}

BACKREST_THICKNESS = 6.0
SCREEN_CAVITY_LENGTH = SCREEN_CASE_HEIGHT + 0.8
SCREEN_CAVITY_DEPTH = SCREEN_CASE_THICKNESS + 0.8
END_SHELF_THICKNESS = 5.0
FRONT_RETENTION_THICKNESS = 4.0
FRONT_RETENTION_OVERLAP = 3.0
GUSSET_REACH = 38.0

ANGLE_VARIANTS = (20.0, 25.0, 30.0)


def _profile(points: list[tuple[float, float]], width: float = BRACKET_WIDTH):
    """Extrude an X/Y polygon across the bracket's Z width."""
    return cq.Workplane("XY").polyline(points).close().extrude(width)


def _oriented_rectangle(
    origin: tuple[float, float],
    u: tuple[float, float],
    n: tuple[float, float],
    u0: float,
    u1: float,
    n0: float,
    n1: float,
    width: float = BRACKET_WIDTH,
):
    """Create a rectangle located in an orthonormal u/n coordinate frame."""
    ox, oy = origin

    def point(uu: float, nn: float) -> tuple[float, float]:
        return (ox + u[0] * uu + n[0] * nn, oy + u[1] * uu + n[1] * nn)

    return _profile(
        [point(u0, n0), point(u1, n0), point(u1, n1), point(u0, n1)],
        width=width,
    )


def _nested_solids(shape) -> list:
    """Flatten CadQuery's occasionally nested one-object compounds."""
    explorer = TopExp_Explorer(shape.wrapped, TopAbs_SOLID)
    solids = []
    while explorer.More():
        solids.append(cq.Solid(TopoDS.Solid(explorer.Current())))
        explorer.Next()
    return solids


def make_clamp(
    width: float = BRACKET_WIDTH,
    drill_screw: bool = True,
    screw_local_z: float | None = None,
):
    """Full FLX6 C-clamp, also used by the cheap fit-test coupon."""
    lower = cq.Workplane("XY").box(
        LOWER_JAW_DEPTH + REAR_WALL_THICKNESS,
        LOWER_JAW_THICKNESS,
        width,
        centered=(False, False, False),
    ).translate((-REAR_WALL_THICKNESS, -LOWER_JAW_THICKNESS, 0.0))

    wall = cq.Workplane("XY").box(
        REAR_WALL_THICKNESS,
        CLAMP_OPENING + LOWER_JAW_THICKNESS + TOP_LIP_THICKNESS,
        width,
        centered=(False, False, False),
    ).translate(
        (-REAR_WALL_THICKNESS, -LOWER_JAW_THICKNESS, 0.0)
    )

    top = cq.Workplane("XY").box(
        TOP_LIP_DEPTH + REAR_WALL_THICKNESS,
        TOP_LIP_THICKNESS,
        width,
        centered=(False, False, False),
    ).translate((-REAR_WALL_THICKNESS, CLAMP_OPENING, 0.0))

    clamp = lower.union(wall).union(top).combine(clean=True)

    if not drill_screw:
        solids = clamp.combine(clean=True).val().Solids()
        if len(solids) != 1:
            raise RuntimeError(f"Clamp should be one solid, got {len(solids)}")
        return cq.Workplane(obj=solids[0])

    if screw_local_z is None:
        screw_local_z = width / 2.0

    # Backup fastener through the existing FLX6 rear screw location. The
    # clamp still supports the load; this screw prevents it walking backwards.
    through = (
        cq.Workplane("YZ")
        .workplane(offset=-REAR_WALL_THICKNESS - 1.0)
        .center(CONTROLLER_SCREW_HEIGHT, screw_local_z)
        .circle(CONTROLLER_SCREW_CLEARANCE / 2.0)
        .extrude(REAR_WALL_THICKNESS + 2.0)
    )
    counterbore = (
        cq.Workplane("YZ")
        .workplane(offset=-REAR_WALL_THICKNESS - 0.1)
        .center(CONTROLLER_SCREW_HEIGHT, screw_local_z)
        .circle(CONTROLLER_SCREW_COUNTERBORE / 2.0)
        .extrude(CONTROLLER_SCREW_COUNTERBORE_DEPTH + 0.1)
    )
    cut = clamp.cut(through).cut(counterbore).combine(clean=True)
    solids = cut.val().Solids()
    if len(solids) != 1:
        raise RuntimeError(f"Clamp should be one solid, got {len(solids)}")
    return cq.Workplane(obj=solids[0])


def build(
    angle_deg: float,
    top_hook: bool = True,
    drill_screw: bool = True,
):
    """Build one identical side bracket at the selected viewing angle."""
    theta = math.radians(angle_deg)
    # Screen rises toward the back of the controller.
    u = (-math.cos(theta), math.sin(theta))
    n = (math.sin(theta), math.cos(theta))

    # The screen's lower back corner is immediately above the clamp.  The
    # screen projects into +n (toward the player) from the backrest.
    origin = (-2.0, CLAMP_OPENING + TOP_LIP_THICKNESS + 1.0)
    cavity_length = SCREEN_CAVITY_LENGTH
    front = SCREEN_CAVITY_DEPTH

    clamp = make_clamp(drill_screw=drill_screw)
    backrest = _oriented_rectangle(
        origin,
        u,
        n,
        -END_SHELF_THICKNESS,
        cavity_length + END_SHELF_THICKNESS,
        -BACKREST_THICKNESS,
        0.0,
    )

    # Lower and upper shelves wrap around the case edges.  The screen slides
    # laterally through the two finished brackets, as with the source design.
    lower_shelf = _oriented_rectangle(
        origin,
        u,
        n,
        -END_SHELF_THICKNESS,
        0.0,
        -BACKREST_THICKNESS,
        front + FRONT_RETENTION_THICKNESS,
    )
    lower_retainer = _oriented_rectangle(
        origin,
        u,
        n,
        -END_SHELF_THICKNESS,
        FRONT_RETENTION_OVERLAP,
        front,
        front + FRONT_RETENTION_THICKNESS,
    )
    upper_shelf = _oriented_rectangle(
        origin,
        u,
        n,
        cavity_length,
        cavity_length + END_SHELF_THICKNESS,
        -BACKREST_THICKNESS,
        front + FRONT_RETENTION_THICKNESS,
    )
    upper_retainer = _oriented_rectangle(
        origin,
        u,
        n,
        cavity_length - FRONT_RETENTION_OVERLAP,
        cavity_length + END_SHELF_THICKNESS,
        front,
        front + FRONT_RETENTION_THICKNESS,
    )

    # Large triangular root ties the long screen rail into the rear wall.
    root_x = -REAR_WALL_THICKNESS
    rail_root = (
        origin[0] - u[0] * END_SHELF_THICKNESS - n[0] * BACKREST_THICKNESS,
        origin[1] - u[1] * END_SHELF_THICKNESS - n[1] * BACKREST_THICKNESS,
    )
    rail_reach = (
        origin[0] + u[0] * GUSSET_REACH - n[0] * BACKREST_THICKNESS,
        origin[1] + u[1] * GUSSET_REACH - n[1] * BACKREST_THICKNESS,
    )
    gusset = _profile(
        [
            (root_x, CLAMP_OPENING - 13.0),
            (root_x, CLAMP_OPENING + TOP_LIP_THICKNESS),
            rail_reach,
        ]
    )

    parts = [
        backrest,
        lower_shelf,
        lower_retainer,
        gusset,
    ]
    if top_hook:
        parts.extend((upper_shelf, upper_retainer))

    bracket = clamp
    for part in parts:
        bracket = bracket.union(part)
    solids = _nested_solids(bracket.val())
    if len(solids) != 1:
        details = [
            {
                "volume": round(s.Volume(), 3),
                "bounds": [
                    round(s.BoundingBox().xmin, 3),
                    round(s.BoundingBox().xmax, 3),
                    round(s.BoundingBox().ymin, 3),
                    round(s.BoundingBox().ymax, 3),
                ],
            }
            for s in solids
        ]
        raise RuntimeError(
            f"{angle_deg:g} degree bracket should be one solid, got "
            f"{len(solids)}: {details}; root={bracket.val().ShapeType()} "
            f"compounds={len(bracket.val().Compounds())}"
        )
    return cq.Workplane(obj=solids[0])


def build_centered_right_usb_notch(angle_deg: float = 25.0):
    """Centered right bracket with USB-B clearance and a factory-screw ear."""
    body = build(angle_deg, top_hook=False, drill_screw=False)

    # With the upright centered at +100.82 mm, local Z=0 maps to global
    # X=+90.82 mm. The factory screw at +113.739 mm is therefore local
    # Z=22.919 mm. A 9 mm round ear overlaps the original 20 mm wall and
    # provides ample material around the M3 clearance bore.
    screw_local_z = 22.919
    ear_radius = 9.0
    ear = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            ear_radius,
            REAR_WALL_THICKNESS,
            cq.Vector(-REAR_WALL_THICKNESS, CONTROLLER_SCREW_HEIGHT, screw_local_z),
            cq.Vector(1.0, 0.0, 0.0),
        )
    )
    body = body.union(ear)

    # USB-B reference from the one-to-one FLX6 model:
    # center X=+91.466, width=14.048, height=14.048. The notch opens through
    # the bracket's inner edge. V2 tightens the visible opening to 20 mm high
    # and 10.5 mm into the rail while retaining clearance around the modeled
    # 14.048 mm socket body. Cable strain relief exits rearward.
    usb_notch = cq.Workplane(
        obj=cq.Solid.makeBox(
            REAR_WALL_THICKNESS + 2.0,
            20.0,
            10.5,
            cq.Vector(-REAR_WALL_THICKNESS - 1.0, 9.0, -1.0),
        )
    )
    body = body.cut(usb_notch)

    screw_bore = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            CONTROLLER_SCREW_CLEARANCE / 2.0,
            REAR_WALL_THICKNESS + 2.0,
            cq.Vector(-REAR_WALL_THICKNESS - 1.0, CONTROLLER_SCREW_HEIGHT, screw_local_z),
            cq.Vector(1.0, 0.0, 0.0),
        )
    )
    counterbore = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            CONTROLLER_SCREW_COUNTERBORE / 2.0,
            CONTROLLER_SCREW_COUNTERBORE_DEPTH + 0.1,
            cq.Vector(-REAR_WALL_THICKNESS - 0.1, CONTROLLER_SCREW_HEIGHT, screw_local_z),
            cq.Vector(1.0, 0.0, 0.0),
        )
    )
    body = body.cut(screw_bore).cut(counterbore).combine(clean=True)
    solids = _nested_solids(body.val())
    if len(solids) != 1:
        raise RuntimeError(
            f"Centered right USB bracket should be one solid, got {len(solids)}"
        )
    return cq.Workplane(obj=solids[0])


def add_screen_case_tabs(part, angle_deg: float, side: str):
    """Add two round-backed tabs aligned to the shell's existing M3 holes."""
    if side not in ("left", "right"):
        raise ValueError(f"Unknown screen-tab side: {side}")

    theta = math.radians(angle_deg)
    u = (-math.cos(theta), math.sin(theta), 0.0)
    n = (math.sin(theta), math.cos(theta), 0.0)
    origin = (-2.0, CLAMP_OPENING + TOP_LIP_THICKNESS + 1.0)

    bracket_global_start = CENTERED_BRACKET_X[side] - BRACKET_WIDTH / 2.0
    hole_local_z = SCREEN_OUTER_HOLES_X[side] - bracket_global_start
    body_edge_z = BRACKET_WIDTH if side == "left" else 0.0
    bridge_z0 = min(body_edge_z, hole_local_z)
    bridge_width = abs(hole_local_z - body_edge_z)

    result_part = part
    for source_y in SCREEN_OUTER_HOLES_Y:
        hole_u = SCREEN_CASE_HEIGHT / 2.0 + source_y
        centre = cq.Vector(
            origin[0] + u[0] * hole_u,
            origin[1] + u[1] * hole_u,
            hole_local_z,
        )
        back_base = centre - cq.Vector(*n) * BACKREST_THICKNESS

        pad = cq.Workplane(
            obj=cq.Solid.makeCylinder(
                SCREEN_TAB_RADIUS,
                BACKREST_THICKNESS,
                back_base,
                cq.Vector(*n),
            )
        )
        result_part = result_part.union(pad)

        if bridge_width > 0.01:
            bridge = _oriented_rectangle(
                origin,
                (u[0], u[1]),
                (n[0], n[1]),
                hole_u - SCREEN_TAB_RADIUS,
                hole_u + SCREEN_TAB_RADIUS,
                -BACKREST_THICKNESS,
                0.0,
                width=bridge_width,
            ).translate((0.0, 0.0, bridge_z0))
            result_part = result_part.union(bridge)

        bore_start = centre - cq.Vector(*n) * (BACKREST_THICKNESS + 1.0)
        bore = cq.Workplane(
            obj=cq.Solid.makeCylinder(
                SCREEN_MOUNT_CLEARANCE / 2.0,
                BACKREST_THICKNESS + 2.0,
                bore_start,
                cq.Vector(*n),
            )
        )
        counterbore = cq.Workplane(
            obj=cq.Solid.makeCylinder(
                SCREEN_MOUNT_COUNTERBORE / 2.0,
                SCREEN_MOUNT_COUNTERBORE_DEPTH + 0.1,
                back_base - cq.Vector(*n) * 0.1,
                cq.Vector(*n),
            )
        )
        result_part = result_part.cut(bore).cut(counterbore)

    result_part = result_part.combine(clean=True)
    solids = _nested_solids(result_part.val())
    if len(solids) != 1:
        raise RuntimeError(
            f"{side} screen-tab bracket should be one solid, got {len(solids)}"
        )
    return cq.Workplane(obj=solids[0])


variants = {int(angle): build(angle) for angle in ANGLE_VARIANTS}
open_top_25 = build(25.0, top_hook=False)
centered_right_usb = build_centered_right_usb_notch(25.0)
left_screen_tabs = add_screen_case_tabs(open_top_25, 25.0, "left")
right_screen_tabs = add_screen_case_tabs(centered_right_usb, 25.0, "right")
recommended = open_top_25
coupon = make_clamp(width=12.0)

# Non-exported exact-size bodies used by the MCP fit render.
_fit_theta = math.radians(25.0)
_fit_u = (-math.cos(_fit_theta), math.sin(_fit_theta))
_fit_n = (math.sin(_fit_theta), math.cos(_fit_theta))
_fit_origin = (-2.0, CLAMP_OPENING + TOP_LIP_THICKNESS + 1.0)
_controller_proxy = (
    cq.Workplane("XY")
    .box(120.0, FLX6_BODY_HEIGHT, 18.0, centered=(False, False, False))
    .translate((0.0, 0.0, 1.0))
)
_screen_proxy = _oriented_rectangle(
    _fit_origin,
    _fit_u,
    _fit_n,
    0.0,
    SCREEN_CASE_HEIGHT,
    0.0,
    SCREEN_CASE_THICKNESS,
    width=18.0,
).translate((0.0, 0.0, 1.0))
fit_preview = cq.Compound.makeCompound(
    [open_top_25.val(), _controller_proxy.val(), _screen_proxy.val()]
)
result = recommended


def _stats(name: str, part) -> dict:
    shape = part.val()
    bb = shape.BoundingBox()
    return {
        "name": name,
        "valid": shape.isValid(),
        "solids": len(shape.Solids()),
        "dimensions_mm": [round(bb.xlen, 3), round(bb.ylen, 3), round(bb.zlen, 3)],
        "volume_cm3": round(shape.Volume() / 1000.0, 3),
    }


def export() -> dict:
    for angle, part in variants.items():
        stem = f"flx6-surface-mount-{angle}deg-v1"
        cq.exporters.export(part, str(OUT / f"{stem}.step"))
        cq.exporters.export(
            part,
            str(OUT / f"{stem}.stl"),
            tolerance=0.05,
            angularTolerance=0.10,
        )

    cq.exporters.export(coupon, str(OUT / "flx6-clamp-fit-test-v1.step"))
    cq.exporters.export(
        coupon,
        str(OUT / "flx6-clamp-fit-test-v1.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    cq.exporters.export(
        open_top_25, str(OUT / "flx6-surface-mount-25deg-open-top-v1.step")
    )
    cq.exporters.export(
        open_top_25,
        str(OUT / "flx6-surface-mount-25deg-open-top-v1.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    cq.exporters.export(
        centered_right_usb,
        str(OUT / "flx6-surface-mount-25deg-open-top-right-centered-usbb-tab-v1.step"),
    )
    cq.exporters.export(
        centered_right_usb,
        str(OUT / "flx6-surface-mount-25deg-open-top-right-centered-usbb-tab-v1.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    cq.exporters.export(
        left_screen_tabs,
        str(OUT / "flx6-surface-mount-25deg-left-screen-tabs-v2.step"),
    )
    cq.exporters.export(
        left_screen_tabs,
        str(OUT / "flx6-surface-mount-25deg-left-screen-tabs-v2.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    cq.exporters.export(
        right_screen_tabs,
        str(OUT / "flx6-surface-mount-25deg-right-usbb-controller-tab-screen-tabs-v2.step"),
    )
    cq.exporters.export(
        right_screen_tabs,
        str(OUT / "flx6-surface-mount-25deg-right-usbb-controller-tab-screen-tabs-v2.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )

    report = {
        "design": "FLX6 remix of surfacemountddj.stl",
        "recommended_angle_deg": 25,
        "print_quantity": 2,
        "parameters_mm": {
            "flx6_reference_body_height": FLX6_BODY_HEIGHT,
            "clamp_opening": CLAMP_OPENING,
            "lower_jaw_depth": LOWER_JAW_DEPTH,
            "screen_case_height": SCREEN_CASE_HEIGHT,
            "screen_case_thickness": SCREEN_CASE_THICKNESS,
            "screen_cavity_length": SCREEN_CAVITY_LENGTH,
            "screen_cavity_depth": SCREEN_CAVITY_DEPTH,
            "screen_backrest_thickness": BACKREST_THICKNESS,
            "controller_screw_clearance": CONTROLLER_SCREW_CLEARANCE,
            "screen_outer_holes_x": SCREEN_OUTER_HOLES_X,
            "screen_outer_holes_y": SCREEN_OUTER_HOLES_Y,
            "screen_mount_clearance": SCREEN_MOUNT_CLEARANCE,
            "screen_tab_radius": SCREEN_TAB_RADIUS,
        },
        "parts": [
            *[_stats(f"{angle} degree bracket", part) for angle, part in variants.items()],
            _stats("25 degree open-top bracket", open_top_25),
            _stats("centered right USB-notch screw-tab bracket", centered_right_usb),
            _stats("left bracket with two screen mounting tabs", left_screen_tabs),
            _stats(
                "right USB-notch/controller-tab bracket with two screen mounting tabs",
                right_screen_tabs,
            ),
            _stats("clamp fit-test coupon", coupon),
        ],
        "physical_fit_gate": (
            "Print the 12 mm wide clamp coupon first. Confirm the 50 mm opening, "
            "50 mm lower jaw, rear screw alignment, and required longer screw before "
            "printing two full brackets."
        ),
    }
    (OUT / "inspection-v1.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(export(), indent=2))
