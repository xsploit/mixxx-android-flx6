"""Build V34 with the internal square raceways removed from both USB ears."""

from __future__ import annotations

import os


os.environ["PIFLEX_TUNNEL_VERSION"] = "v34"
os.environ["PIFLEX_TUNNEL_SLUG"] = "fully-hollow-usb-ears"
os.environ["PIFLEX_TUNNEL_CENTRE_Y"] = "0.0"
os.environ["PIFLEX_TUNNEL_REAR_Z"] = "-2.66"
os.environ["PIFLEX_EAR_CENTRED_DOGLEG"] = "0"
os.environ["PIFLEX_OPEN_INNER_CHANNEL"] = "1"
os.environ["PIFLEX_OPEN_CHANNEL_FLOOR_TOP_Z"] = "-4.66"
os.environ["PIFLEX_OPEN_CHANNEL_BLUE_ROOF_LENGTH"] = "5.0"
os.environ["PIFLEX_EAR_USB_CUT_FLOOR_Z"] = "-4.66"
os.environ["PIFLEX_EAR_USB_CUT_INNER_Y"] = "9.0"
# Re-cut the original rounded inner cavity after all channel and reinforcement
# unions. This removes the square raceway from inside each ear while retaining
# the original 3.2 mm rounded exterior shell.
os.environ["PIFLEX_HOLLOW_EAR_INTERIOR"] = "1"

import build_codex_v23_centered_usb_tunnels as build


if __name__ == "__main__":
    build.export()
