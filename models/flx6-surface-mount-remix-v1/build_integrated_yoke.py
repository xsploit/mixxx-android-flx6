"""Build a one-piece PiFlex screen yoke from the validated V2 brackets.

The two side brackets retain all measured interfaces.  Three cross-members
turn them into one rigid, visually symmetric assembly while leaving the rear
I/O and the centre of the screen shell open for airflow and Pi access.
"""

from __future__ import annotations

import json
from pathlib import Path

import cadquery as cq

import build_surface_mount_remix as base


OUT = Path(__file__).resolve().parent
ANGLE_DEG = 25.0

# Common horizontal coordinate used by the full assembly.  The two bracket
# STLs normally begin at local Z=0; these offsets place them around centreline.
LEFT_Z = base.CENTERED_BRACKET_X["left"] - base.BRACKET_WIDTH / 2.0
RIGHT_Z = base.CENTERED_BRACKET_X["right"] - base.BRACKET_WIDTH / 2.0

# Cross-members overlap each 20 mm rail by 1 mm so the CAD union is robust.
BRIDGE_Z0 = LEFT_Z + base.BRACKET_WIDTH - 1.0
BRIDGE_Z1 = RIGHT_Z + 1.0
BRIDGE_WIDTH = BRIDGE_Z1 - BRIDGE_Z0


def integrated_yoke():
    theta = base.math.radians(ANGLE_DEG)
    u = (-base.math.cos(theta), base.math.sin(theta))
    n = (base.math.sin(theta), base.math.cos(theta))
    origin = (-2.0, base.CLAMP_OPENING + base.TOP_LIP_THICKNESS + 1.0)

    left = base.left_screen_tabs.translate((0.0, 0.0, LEFT_Z))
    right = base.right_screen_tabs.translate((0.0, 0.0, RIGHT_Z))

    # Player-facing fascia immediately below the screen.  It fills the visual
    # gap between rails without entering the display cavity or rear I/O zone.
    lower_fascia = base._oriented_rectangle(
        origin,
        u,
        n,
        -14.0,
        0.0,
        -base.BACKREST_THICKNESS,
        base.SCREEN_CAVITY_DEPTH,
        width=BRIDGE_WIDTH,
    ).translate((0.0, 0.0, BRIDGE_Z0))

    # Flat bands concealed behind the shell tie the long rails together.  The
    # middle remains completely open around the Pi vents and cable openings.
    lower_rear_bridge = base._oriented_rectangle(
        origin,
        u,
        n,
        0.0,
        18.0,
        -base.BACKREST_THICKNESS,
        0.0,
        width=BRIDGE_WIDTH,
    ).translate((0.0, 0.0, BRIDGE_Z0))
    upper_rear_bridge = base._oriented_rectangle(
        origin,
        u,
        n,
        base.SCREEN_CASE_HEIGHT - 18.0,
        base.SCREEN_CAVITY_LENGTH,
        -base.BACKREST_THICKNESS,
        0.0,
        width=BRIDGE_WIDTH,
    ).translate((0.0, 0.0, BRIDGE_Z0))

    result = left.union(right)
    for member in (lower_fascia, lower_rear_bridge, upper_rear_bridge):
        result = result.union(member)
    result = result.combine(clean=True)

    solids = base._nested_solids(result.val())
    if len(solids) != 1:
        raise RuntimeError(f"Integrated yoke should be one solid, got {len(solids)}")
    return cq.Workplane(obj=solids[0])


result = integrated_yoke()


def _rear_right_notched_clamp_only():
    """Rear-view right FLX6 clamp with USB-B notch and screw ear.

    Rear-view right is the assembly's negative horizontal coordinate.  The
    original implementation put this asymmetric clamp at positive Z, which
    made it appear on the left when standing behind the controller.
    """
    body = base.make_clamp(drill_screw=False)
    # Mirror the old local-Z details around the 20 mm clamp width: the screw
    # ear moves from +22.919 to -2.919 mm and the inner-edge notch moves from
    # -1..9.5 to 10.5..21 mm.
    screw_local_z = base.BRACKET_WIDTH - 22.919
    ear_radius = 9.0
    ear = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            ear_radius,
            base.REAR_WALL_THICKNESS,
            cq.Vector(-base.REAR_WALL_THICKNESS, base.CONTROLLER_SCREW_HEIGHT, screw_local_z),
            cq.Vector(1.0, 0.0, 0.0),
        )
    )
    usb_notch = cq.Workplane(
        obj=cq.Solid.makeBox(
            base.REAR_WALL_THICKNESS + 2.0,
            20.0,
            10.5,
            cq.Vector(
                -base.REAR_WALL_THICKNESS - 1.0,
                9.0,
                base.BRACKET_WIDTH - 9.5,
            ),
        )
    )
    screw_bore = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            base.CONTROLLER_SCREW_CLEARANCE / 2.0,
            base.REAR_WALL_THICKNESS + 2.0,
            cq.Vector(
                -base.REAR_WALL_THICKNESS - 1.0,
                base.CONTROLLER_SCREW_HEIGHT,
                screw_local_z,
            ),
            cq.Vector(1.0, 0.0, 0.0),
        )
    )
    counterbore = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            base.CONTROLLER_SCREW_COUNTERBORE / 2.0,
            base.CONTROLLER_SCREW_COUNTERBORE_DEPTH + 0.1,
            cq.Vector(
                -base.REAR_WALL_THICKNESS - 0.1,
                base.CONTROLLER_SCREW_HEIGHT,
                screw_local_z,
            ),
            cq.Vector(1.0, 0.0, 0.0),
        )
    )
    return body.union(ear).cut(usb_notch).cut(screw_bore).cut(counterbore).combine(clean=True)


def _case_backrest(clamp, side: str):
    """Attach the clamp to the rear of the case without shelves or retainers."""
    theta = base.math.radians(ANGLE_DEG)
    u = (-base.math.cos(theta), base.math.sin(theta))
    n = (base.math.sin(theta), base.math.cos(theta))
    origin = (-2.0, base.CLAMP_OPENING + base.TOP_LIP_THICKNESS + 1.0)

    backrest = base._oriented_rectangle(
        origin,
        u,
        n,
        0.0,
        base.SCREEN_CAVITY_LENGTH,
        -base.BACKREST_THICKNESS,
        0.0,
    )
    root_x = -base.REAR_WALL_THICKNESS
    rail_reach = (
        origin[0] + u[0] * base.GUSSET_REACH - n[0] * base.BACKREST_THICKNESS,
        origin[1] + u[1] * base.GUSSET_REACH - n[1] * base.BACKREST_THICKNESS,
    )
    gusset = base._profile(
        [
            (root_x, base.CLAMP_OPENING - 13.0),
            (root_x, base.CLAMP_OPENING + base.TOP_LIP_THICKNESS),
            rail_reach,
        ]
    )
    rail = clamp.union(backrest).union(gusset).combine(clean=True)
    return base.add_screen_case_tabs(rail, ANGLE_DEG, side)


def integrated_case_mount_no_screen_lip():
    """V6 yoke: rear supports only; the display is the case's front face."""
    theta = base.math.radians(ANGLE_DEG)
    u = (-base.math.cos(theta), base.math.sin(theta))
    n = (base.math.sin(theta), base.math.cos(theta))
    origin = (-2.0, base.CLAMP_OPENING + base.TOP_LIP_THICKNESS + 1.0)

    # Standing behind the controller, the USB-B notch belongs on the viewer's
    # right. In this CAD coordinate system that is the negative-Z/LEFT_Z rail.
    left = _case_backrest(_rear_right_notched_clamp_only(), "left").translate(
        (0.0, 0.0, LEFT_Z)
    )
    right = _case_backrest(base.make_clamp(), "right").translate(
        (0.0, 0.0, RIGHT_Z)
    )

    # Rear-only bridges stiffen the shell. Nothing projects around the physical
    # display's bottom, sides or top.
    lower_rear_bridge = base._oriented_rectangle(
        origin,
        u,
        n,
        0.0,
        18.0,
        -base.BACKREST_THICKNESS,
        0.0,
        width=BRIDGE_WIDTH,
    ).translate((0.0, 0.0, BRIDGE_Z0))
    upper_rear_bridge = base._oriented_rectangle(
        origin,
        u,
        n,
        base.SCREEN_CASE_HEIGHT - 18.0,
        base.SCREEN_CAVITY_LENGTH,
        -base.BACKREST_THICKNESS,
        0.0,
        width=BRIDGE_WIDTH,
    ).translate((0.0, 0.0, BRIDGE_Z0))

    mounted = left.union(right).union(lower_rear_bridge).union(upper_rear_bridge).combine(clean=True)
    solids = base._nested_solids(mounted.val())
    if len(solids) != 1:
        raise RuntimeError(f"Lipless case mount should be one solid, got {len(solids)}")
    return cq.Workplane(obj=solids[0])


case_mount_result = integrated_case_mount_no_screen_lip()


# V12 placement keeps the complete V9 enclosure and yoke rigidly together,
# then installs that whole assembly 18.629 mm left on the controller. These
# bracket details compensate for the new factory-screw positions in the
# assembly's local horizontal coordinate system.
ASSEMBLY_SHIFT_X = -18.629
REAR_RIGHT_CONTROLLER_SCREW_X = -113.739182
REAR_LEFT_CONTROLLER_SCREW_X = 100.821609
REAR_LEFT_MASTER_RCA_OUTER_X = 78.647079
MASTER_RCA_CENTER_HEIGHT = 18.939297
MASTER_RCA_PLUG_CLEARANCE_RADIUS = 7.5
INNER_CLAMP_EXTENSION = 2.0
LEFT_TAB_CONNECTION_EXTENSION = 1.5


def _cut_screw_hole(clamp, screw_local_z: float):
    screw_bore = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            base.CONTROLLER_SCREW_CLEARANCE / 2.0,
            base.REAR_WALL_THICKNESS + 2.0,
            cq.Vector(
                -base.REAR_WALL_THICKNESS - 1.0,
                base.CONTROLLER_SCREW_HEIGHT,
                screw_local_z,
            ),
            cq.Vector(1.0, 0.0, 0.0),
        )
    )
    counterbore = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            base.CONTROLLER_SCREW_COUNTERBORE / 2.0,
            base.CONTROLLER_SCREW_COUNTERBORE_DEPTH + 0.1,
            cq.Vector(
                -base.REAR_WALL_THICKNESS - 0.1,
                base.CONTROLLER_SCREW_HEIGHT,
                screw_local_z,
            ),
            cq.Vector(1.0, 0.0, 0.0),
        )
    )
    return clamp.cut(screw_bore).cut(counterbore).combine(clean=True)


def _shifted_rear_right_filled_direct_hole_clamp():
    """Rear-view right: no notch or round ear; hole passes through the rail."""
    target_local_assembly_x = REAR_RIGHT_CONTROLLER_SCREW_X - ASSEMBLY_SHIFT_X
    screw_local_z = target_local_assembly_x - LEFT_Z
    # Positive local Z is inward for the rear-view-right bracket. Add a small
    # amount of material on that edge so the screw is comfortably surrounded.
    body = base.make_clamp(
        width=base.BRACKET_WIDTH + INNER_CLAMP_EXTENSION,
        drill_screw=False,
    )
    return _cut_screw_hole(body, screw_local_z)


def _shifted_rear_left_tab_clamp():
    """Rear-view left: circular extension reaches the unchanged factory screw."""
    target_local_assembly_x = REAR_LEFT_CONTROLLER_SCREW_X - ASSEMBLY_SHIFT_X
    screw_local_z = target_local_assembly_x - RIGHT_Z
    # Negative local Z is inward on this side. Widen inward by 2 mm, while a
    # further 1.5 mm on the outer edge gives the circular screw tab a proper
    # printable overlap instead of a near-tangent contact.
    body = base.make_clamp(
        width=(
            base.BRACKET_WIDTH
            + INNER_CLAMP_EXTENSION
            + LEFT_TAB_CONNECTION_EXTENSION
        ),
        drill_screw=False,
    ).translate((0.0, 0.0, -INNER_CLAMP_EXTENSION))
    ear = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            9.0,
            base.REAR_WALL_THICKNESS,
            cq.Vector(
                -base.REAR_WALL_THICKNESS,
                base.CONTROLLER_SCREW_HEIGHT,
                screw_local_z,
            ),
            cq.Vector(1.0, 0.0, 0.0),
        )
    )
    body = _cut_screw_hole(body.union(ear), screw_local_z)

    # The complete-unit shift places this rail over the outer jack of the
    # Master RCA pair. Bore through the rear wall with enough room for the RCA
    # plug body, not merely the metal socket. It opens slightly through the
    # rail's inner edge so the cable can be inserted without binding.
    rca_local_assembly_x = REAR_LEFT_MASTER_RCA_OUTER_X - ASSEMBLY_SHIFT_X
    rca_local_z = rca_local_assembly_x - RIGHT_Z
    rca_clearance = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            MASTER_RCA_PLUG_CLEARANCE_RADIUS,
            base.REAR_WALL_THICKNESS + 2.0,
            cq.Vector(
                -base.REAR_WALL_THICKNESS - 1.0,
                MASTER_RCA_CENTER_HEIGHT,
                rca_local_z,
            ),
            cq.Vector(1.0, 0.0, 0.0),
        )
    )
    return body.cut(rca_clearance).combine(clean=True)


def integrated_shifted_case_mount_v13():
    """V13 yoke with stronger inner edges and RCA/tab connections."""
    theta = base.math.radians(ANGLE_DEG)
    u = (-base.math.cos(theta), base.math.sin(theta))
    n = (base.math.sin(theta), base.math.cos(theta))
    origin = (-2.0, base.CLAMP_OPENING + base.TOP_LIP_THICKNESS + 1.0)

    # Negative horizontal is rear-view right; positive is rear-view left.
    rear_right = _case_backrest(
        _shifted_rear_right_filled_direct_hole_clamp(), "left"
    ).translate((0.0, 0.0, LEFT_Z))
    rear_left = _case_backrest(
        _shifted_rear_left_tab_clamp(), "right"
    ).translate((0.0, 0.0, RIGHT_Z))

    lower_rear_bridge = base._oriented_rectangle(
        origin,
        u,
        n,
        0.0,
        18.0,
        -base.BACKREST_THICKNESS,
        0.0,
        width=BRIDGE_WIDTH,
    ).translate((0.0, 0.0, BRIDGE_Z0))
    upper_rear_bridge = base._oriented_rectangle(
        origin,
        u,
        n,
        base.SCREEN_CASE_HEIGHT - 18.0,
        base.SCREEN_CAVITY_LENGTH,
        -base.BACKREST_THICKNESS,
        0.0,
        width=BRIDGE_WIDTH,
    ).translate((0.0, 0.0, BRIDGE_Z0))

    mounted = (
        rear_right
        .union(rear_left)
        .union(lower_rear_bridge)
        .union(upper_rear_bridge)
        .combine(clean=True)
    )
    solids = base._nested_solids(mounted.val())
    if len(solids) != 1:
        raise RuntimeError(f"Shifted V13 case mount should be one solid, got {len(solids)}")
    return cq.Workplane(obj=solids[0])


shifted_case_mount_result_v13 = integrated_shifted_case_mount_v13()


# V14 fills each bracket outward to the main screen case's rounded side edge.
# The case is 253.154 mm wide, so the original bracket outer edge at 110.82 mm
# needs another 15.757 mm of support on both sides.
MAIN_SCREEN_CASE_WIDTH = 253.154
OUTER_CASE_EDGE_EXTENSION = (
    MAIN_SCREEN_CASE_WIDTH / 2.0
    - (abs(base.CENTERED_BRACKET_X["right"]) + base.BRACKET_WIDTH / 2.0)
)


def _v14_rear_right_filled_direct_hole_clamp():
    target_local_assembly_x = REAR_RIGHT_CONTROLLER_SCREW_X - ASSEMBLY_SHIFT_X
    screw_local_z = target_local_assembly_x - LEFT_Z
    width = base.BRACKET_WIDTH + INNER_CLAMP_EXTENSION + OUTER_CASE_EDGE_EXTENSION
    body = base.make_clamp(width=width, drill_screw=False).translate(
        (0.0, 0.0, -OUTER_CASE_EDGE_EXTENSION)
    )
    return _cut_screw_hole(body, screw_local_z)


def _v14_rear_left_tab_and_rca_clamp():
    target_local_assembly_x = REAR_LEFT_CONTROLLER_SCREW_X - ASSEMBLY_SHIFT_X
    screw_local_z = target_local_assembly_x - RIGHT_Z
    width = base.BRACKET_WIDTH + INNER_CLAMP_EXTENSION + OUTER_CASE_EDGE_EXTENSION
    body = base.make_clamp(width=width, drill_screw=False).translate(
        (0.0, 0.0, -INNER_CLAMP_EXTENSION)
    )
    ear = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            9.0,
            base.REAR_WALL_THICKNESS,
            cq.Vector(
                -base.REAR_WALL_THICKNESS,
                base.CONTROLLER_SCREW_HEIGHT,
                screw_local_z,
            ),
            cq.Vector(1.0, 0.0, 0.0),
        )
    )
    body = _cut_screw_hole(body.union(ear), screw_local_z)

    rca_local_assembly_x = REAR_LEFT_MASTER_RCA_OUTER_X - ASSEMBLY_SHIFT_X
    rca_local_z = rca_local_assembly_x - RIGHT_Z
    rca_clearance = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            MASTER_RCA_PLUG_CLEARANCE_RADIUS,
            base.REAR_WALL_THICKNESS + 2.0,
            cq.Vector(
                -base.REAR_WALL_THICKNESS - 1.0,
                MASTER_RCA_CENTER_HEIGHT,
                rca_local_z,
            ),
            cq.Vector(1.0, 0.0, 0.0),
        )
    )
    return body.cut(rca_clearance).combine(clean=True)


def _v14_case_backrest_to_outer_case_edge(clamp, side: str):
    theta = base.math.radians(ANGLE_DEG)
    u = (-base.math.cos(theta), base.math.sin(theta))
    n = (base.math.sin(theta), base.math.cos(theta))
    origin = (-2.0, base.CLAMP_OPENING + base.TOP_LIP_THICKNESS + 1.0)

    if side == "left":
        width = base.BRACKET_WIDTH + OUTER_CASE_EDGE_EXTENSION
        horizontal_shift = -OUTER_CASE_EDGE_EXTENSION
    else:
        width = base.BRACKET_WIDTH + OUTER_CASE_EDGE_EXTENSION
        horizontal_shift = 0.0

    backrest = base._oriented_rectangle(
        origin,
        u,
        n,
        0.0,
        base.SCREEN_CAVITY_LENGTH,
        -base.BACKREST_THICKNESS,
        0.0,
        width=width,
    ).translate((0.0, 0.0, horizontal_shift))

    root_x = -base.REAR_WALL_THICKNESS
    rail_reach = (
        origin[0] + u[0] * base.GUSSET_REACH - n[0] * base.BACKREST_THICKNESS,
        origin[1] + u[1] * base.GUSSET_REACH - n[1] * base.BACKREST_THICKNESS,
    )
    gusset = base._profile(
        [
            (root_x, base.CLAMP_OPENING - 13.0),
            (root_x, base.CLAMP_OPENING + base.TOP_LIP_THICKNESS),
            rail_reach,
        ],
        width=width,
    ).translate((0.0, 0.0, horizontal_shift))

    rail = clamp.union(backrest).union(gusset).combine(clean=True)
    return base.add_screen_case_tabs(rail, ANGLE_DEG, side)


def integrated_shifted_case_mount_v14():
    theta = base.math.radians(ANGLE_DEG)
    u = (-base.math.cos(theta), base.math.sin(theta))
    n = (base.math.sin(theta), base.math.cos(theta))
    origin = (-2.0, base.CLAMP_OPENING + base.TOP_LIP_THICKNESS + 1.0)

    rear_right = _v14_case_backrest_to_outer_case_edge(
        _v14_rear_right_filled_direct_hole_clamp(), "left"
    ).translate((0.0, 0.0, LEFT_Z))
    rear_left = _v14_case_backrest_to_outer_case_edge(
        _v14_rear_left_tab_and_rca_clamp(), "right"
    ).translate((0.0, 0.0, RIGHT_Z))

    lower_rear_bridge = base._oriented_rectangle(
        origin, u, n, 0.0, 18.0,
        -base.BACKREST_THICKNESS, 0.0,
        width=BRIDGE_WIDTH,
    ).translate((0.0, 0.0, BRIDGE_Z0))
    upper_rear_bridge = base._oriented_rectangle(
        origin, u, n,
        base.SCREEN_CASE_HEIGHT - 18.0,
        base.SCREEN_CAVITY_LENGTH,
        -base.BACKREST_THICKNESS, 0.0,
        width=BRIDGE_WIDTH,
    ).translate((0.0, 0.0, BRIDGE_Z0))

    mounted = (
        rear_right.union(rear_left)
        .union(lower_rear_bridge)
        .union(upper_rear_bridge)
        .combine(clean=True)
    )
    solids = base._nested_solids(mounted.val())
    if len(solids) != 1:
        raise RuntimeError(f"Shifted V14 case mount should be one solid, got {len(solids)}")
    return cq.Workplane(obj=solids[0])


shifted_case_mount_result_v14 = integrated_shifted_case_mount_v14()


def export():
    stem = "piflex-integrated-screen-yoke-25deg-v1"
    cq.exporters.export(result, str(OUT / f"{stem}.step"))
    cq.exporters.export(
        result,
        str(OUT / f"{stem}.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    shape = result.val()
    bb = shape.BoundingBox()
    report = {
        "name": "PiFlex integrated one-piece screen yoke V1",
        "valid": shape.isValid(),
        "solids": len(shape.Solids()),
        "dimensions_mm": [round(bb.xlen, 3), round(bb.ylen, 3), round(bb.zlen, 3)],
        "volume_cm3": round(shape.Volume() / 1000.0, 3),
        "interfaces_preserved": [
            "FLX6 full C-clamp profiles",
            "left controller screw",
            "rear-view right USB-B cutout and controller screw ear",
            "four existing 10-inch screen-shell holes",
        ],
    }
    (OUT / "integrated-yoke-inspection.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    print(json.dumps(export(), indent=2))
