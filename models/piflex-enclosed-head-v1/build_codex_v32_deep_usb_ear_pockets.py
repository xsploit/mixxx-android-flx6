"""Build V32 with USB ear openings extended down to the V31 channel floor."""

from __future__ import annotations

import os


os.environ["PIFLEX_TUNNEL_VERSION"] = "v32"
os.environ["PIFLEX_TUNNEL_SLUG"] = "deep-usb-ear-pockets"
os.environ["PIFLEX_TUNNEL_CENTRE_Y"] = "0.0"
os.environ["PIFLEX_TUNNEL_REAR_Z"] = "-2.66"
os.environ["PIFLEX_EAR_CENTRED_DOGLEG"] = "0"
os.environ["PIFLEX_OPEN_INNER_CHANNEL"] = "1"
os.environ["PIFLEX_OPEN_CHANNEL_FLOOR_TOP_Z"] = "-4.66"
os.environ["PIFLEX_OPEN_CHANNEL_BLUE_ROOF_LENGTH"] = "5.0"
# The original USB slot ended at -3.10 mm. Continue the same rectangular
# opening to the channel floor so the female connector body can enter the
# hollow ear and its lead can turn into the routing channel.
os.environ["PIFLEX_EAR_USB_CUT_FLOOR_Z"] = "-4.66"

import build_codex_v23_centered_usb_tunnels as build


if __name__ == "__main__":
    build.export()
