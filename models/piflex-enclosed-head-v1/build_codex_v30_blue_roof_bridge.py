"""Build V30 with a 5 mm blue roof bridge before each enclosed USB ear."""

from __future__ import annotations

import os


os.environ["PIFLEX_TUNNEL_VERSION"] = "v30"
os.environ["PIFLEX_TUNNEL_SLUG"] = "pi-level-channel-blue-roof"
os.environ["PIFLEX_TUNNEL_CENTRE_Y"] = "0.0"
os.environ["PIFLEX_TUNNEL_REAR_Z"] = "-2.66"
os.environ["PIFLEX_EAR_CENTRED_DOGLEG"] = "0"
os.environ["PIFLEX_OPEN_INNER_CHANNEL"] = "1"
# Keep the channel's closing floor inside the screen-frame layer. Dropping the
# floor to the Pi pod's rear plane created two exposed tabs on the pod back.
os.environ["PIFLEX_OPEN_CHANNEL_FLOOR_TOP_Z"] = "-2.66"
os.environ["PIFLEX_OPEN_CHANNEL_BLUE_ROOF_LENGTH"] = "5.0"

import build_codex_v23_centered_usb_tunnels as build


if __name__ == "__main__":
    build.export()
