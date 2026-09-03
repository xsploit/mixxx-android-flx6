"""Build V33 with USB sockets extending inward to the routing channel."""

from __future__ import annotations

import os


os.environ["PIFLEX_TUNNEL_VERSION"] = "v33"
os.environ["PIFLEX_TUNNEL_SLUG"] = "full-depth-usb-ear-pockets"
os.environ["PIFLEX_TUNNEL_CENTRE_Y"] = "0.0"
os.environ["PIFLEX_TUNNEL_REAR_Z"] = "-2.66"
os.environ["PIFLEX_EAR_CENTRED_DOGLEG"] = "0"
os.environ["PIFLEX_OPEN_INNER_CHANNEL"] = "1"
os.environ["PIFLEX_OPEN_CHANNEL_FLOOR_TOP_Z"] = "-4.66"
os.environ["PIFLEX_OPEN_CHANNEL_BLUE_ROOF_LENGTH"] = "5.0"
os.environ["PIFLEX_EAR_USB_CUT_FLOOR_Z"] = "-4.66"
# Cut from the ear's outside edge through the internal reinforcement and meet
# the channel at its +Y wall (9.2 mm), with 0.2 mm overlap for a clean join.
os.environ["PIFLEX_EAR_USB_CUT_INNER_Y"] = "9.0"

import build_codex_v23_centered_usb_tunnels as build


if __name__ == "__main__":
    build.export()
