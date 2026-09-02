"""Polish the existing V18 rear body without replacing its case geometry.

The existing V18 body is retained. A clean rounded skin is unioned over its
rear bay to close legacy Pi connector slots and stepped scars. Only the rear
grill, enlarged screw-safe service throat, and two concealed USB-A cable paths
are cut back into that filled surface.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cadquery as cq


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MOUNT_DIR = ROOT / "models" / "flx6-surface-mount-remix-v1"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(MOUNT_DIR))

import build_integrated_yoke as yoke  # noqa: E402
import build_piflex_enclosed_head as head  # noqa: E402
import build_rounded_service_bay_v16 as v16  # noqa: E402
import build_screw_safe_service_bay_v18 as v18  # noqa: E402


SCREW_TOWER_RADIUS = head.BACK_SCREW_TUNNEL_RADIUS
STRUCTURAL_WEB = 1.0
SCREW_GUARD_RADIUS = SCREW_TOWER_RADIUS + STRUCTURAL_WEB
HOLE_X = tuple(head.bracket_source.SCREEN_OUTER_HOLES_X.values())
HOLE_Y = tuple(head.bracket_source.SCREEN_OUTER_HOLES_Y)

THROAT_X_MIN = min(HOLE_X) + SCREW_GUARD_RADIUS
THROAT_X_MAX = max(HOLE_X) - SCREW_GUARD_RADIUS
THROAT_Y_MIN = min(HOLE_Y) + SCREW_GUARD_RADIUS
THROAT_Y_MAX = max(HOLE_Y) - SCREW_GUARD_RADIUS
THROAT_WIDTH = THROAT_X_MAX - THROAT_X_MIN
THROAT_HEIGHT = THROAT_Y_MAX - THROAT_Y_MIN
THROAT_CENTRE_X = (THROAT_X_MIN + THROAT_X_MAX) / 2.0
THROAT_CENTRE_Y = (THROAT_Y_MIN + THROAT_Y_MAX) / 2.0

CHANNEL_CLEAR_HEIGHT = 18.0
CHANNEL_FRONT_Z = 1.0
CHANNEL_REAR_Z = -head.WING_REAR_DEPTH + head.WING_WALL
GRILL_WIDTH = 100.0
GRILL_SLOT_HEIGHT = 3.2
GRILL_Y = (-25.0, -15.0, -5.0, 5.0, 15.0, 25.0)


def wide_service_throat():
    return head.rounded_box(
        THROAT_WIDTH,
        THROAT_HEIGHT,
        head.CASE_RIM_DEPTH + 4.0,
        -head.CASE_RIM_DEPTH - 1.0,
        14.0,
    ).translate((THROAT_CENTRE_X, THROAT_CENTRE_Y, 0.0))


def concealed_usb_channels():
    """Return two voids linking the central cavity to the hollow USB ears."""
    ear_inner_edge = abs(head.wing_centres()[1]) - (
        head.WING_WIDTH - 2.0 * head.WING_WALL
    ) / 2.0
    depth = CHANNEL_FRONT_Z - CHANNEL_REAR_Z
    passages = []
    for sign, throat_edge in ((-1.0, THROAT_X_MIN), (1.0, THROAT_X_MAX)):
        start = abs(throat_edge) - 3.0
        end = ear_inner_edge + 3.0
        length = end - start
        centre = sign * (start + end) / 2.0
        passages.append(
            cq.Workplane("XY")
            .box(length, CHANNEL_CLEAR_HEIGHT, depth, centered=(True, True, False))
            .translate((centre, head.WING_CENTRE_Y, CHANNEL_REAR_Z))
        )
    return passages


def clean_rear_bay_skin():
    """Uninterrupted V18 outer skin used only to fill existing openings."""
    return v16._bay_outer().cut(v16._bay_inner())


def rear_grill_cutters():
    for y in GRILL_Y:
        yield (
            cq.Workplane("XY")
            .box(GRILL_WIDTH, GRILL_SLOT_HEIGHT, 6.0)
            .translate((0.0, y, -v16.BAY_TOTAL_DEPTH))
        )


def build_polished_rear_local():
    # V18 remains the body. This union closes the old USB/Ethernet, HDMI/power,
    # micro-SD and stepped Pi-case openings without altering the outer envelope.
    polished = v18.rear_local.union(clean_rear_bay_skin())

    # Re-open only the functional geometry requested for this revision.
    polished = polished.cut(wide_service_throat())
    for channel in concealed_usb_channels():
        polished = polished.cut(channel)
    for grill in rear_grill_cutters():
        polished = polished.cut(grill)
    return polished.combine(clean=True)


rear_local = build_polished_rear_local()
rear = head.to_bracket_coordinates(rear_local)
complete = rear.union(yoke.shifted_case_mount_result_v14).combine(clean=True)
shape = complete.val()
solids = head.bracket_source._nested_solids(shape)
if not shape.isValid() or len(solids) != 1:
    raise RuntimeError(
        f"Polished V19 must be one valid solid; valid={shape.isValid()} solids={len(solids)}"
    )


def export():
    cq.exporters.export(
        complete,
        str(HERE / "piflex-codex-v19-polished-structure.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )
    cq.exporters.export(
        complete,
        str(HERE / "piflex-codex-v19-polished-structure.step"),
    )
    cq.exporters.export(
        rear_local,
        str(HERE / "piflex-codex-v19-polished-rear-local.stl"),
        tolerance=0.05,
        angularTolerance=0.10,
    )

    report = {
        "design": "PiFlex Codex V19 polished existing V18 rear",
        "valid": shape.isValid(),
        "solids": len(solids),
        "method": "union clean skin over V18, then recut only required openings",
        "filled": [
            "legacy Pi USB/Ethernet window",
            "legacy Pi HDMI/power window",
            "legacy micro-SD slot",
            "legacy stepped rear-case scars",
        ],
        "retained_openings": [
            "six-slot rear grill",
            "two top-facing USB-A ear sockets",
            "two concealed ear-to-Pi cable channels",
            "central screw-safe service opening",
        ],
        "service_opening_mm": [round(THROAT_WIDTH, 3), round(THROAT_HEIGHT, 3)],
        "service_opening_centre_mm": [
            round(THROAT_CENTRE_X, 3),
            round(THROAT_CENTRE_Y, 3),
        ],
        "screw_tower_radius_mm": SCREW_TOWER_RADIUS,
        "structural_web_mm": STRUCTURAL_WEB,
        "concealed_channel_clear_mm": [
            CHANNEL_CLEAR_HEIGHT,
            CHANNEL_FRONT_Z - CHANNEL_REAR_Z,
        ],
        "production_gate": "measure actual female USB-A panel lead bodies and bend radius",
    }
    (HERE / "inspection-codex-v19-polished-structure.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    print(json.dumps(export(), indent=2))
