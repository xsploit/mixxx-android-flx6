"""Build V35 with the four original screw-tower joins repaired."""

from __future__ import annotations

import os


os.environ["PIFLEX_TUNNEL_VERSION"] = "v35"
os.environ["PIFLEX_TUNNEL_SLUG"] = "screw-tower-join-repair"
os.environ["PIFLEX_TUNNEL_CENTRE_Y"] = "0.0"
os.environ["PIFLEX_TUNNEL_REAR_Z"] = "-2.66"
os.environ["PIFLEX_EAR_CENTRED_DOGLEG"] = "0"
os.environ["PIFLEX_OPEN_INNER_CHANNEL"] = "1"
os.environ["PIFLEX_OPEN_CHANNEL_FLOOR_TOP_Z"] = "-4.66"
os.environ["PIFLEX_OPEN_CHANNEL_BLUE_ROOF_LENGTH"] = "5.0"
os.environ["PIFLEX_EAR_USB_CUT_FLOOR_Z"] = "-4.66"
os.environ["PIFLEX_EAR_USB_CUT_INNER_Y"] = "9.0"
os.environ["PIFLEX_HOLLOW_EAR_INTERIOR"] = "1"

# Repair only the four near-tangent orange joins. The source screw centers and
# 3.6 mm bores are unchanged; matching annular collars extend 2.3 mm backward
# into the existing Pi-case wall. No perimeter shelf, ring, or step is added.
os.environ["PIFLEX_EXTEND_ORIGINAL_SCREW_TOWERS"] = "1"
os.environ["PIFLEX_SCREW_TOWER_EXTENSION_Z0"] = "-11.2"
os.environ["PIFLEX_SCREW_TOWER_EXTENSION_TOP_Z"] = "-8.9"
os.environ["PIFLEX_SCREW_TOWER_EXTENSION_RADIUS"] = "6.1"

import build_codex_v23_centered_usb_tunnels as build


if __name__ == "__main__":
    build.export()
