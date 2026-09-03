"""Build V31 with the V30 channel floor trimmed 2 mm deeper."""

from __future__ import annotations

import os


os.environ["PIFLEX_TUNNEL_VERSION"] = "v31"
os.environ["PIFLEX_TUNNEL_SLUG"] = "deeper-channel-blue-roof"
os.environ["PIFLEX_TUNNEL_CENTRE_Y"] = "0.0"
os.environ["PIFLEX_TUNNEL_REAR_Z"] = "-2.66"
os.environ["PIFLEX_EAR_CENTRED_DOGLEG"] = "0"
os.environ["PIFLEX_OPEN_INNER_CHANNEL"] = "1"
# V30 closed the channel at -2.66 mm. Trim exactly one 2 mm layer from that
# orange floor so its top sits deeper while leaving the ear tunnel and blue
# roof bridge untouched.
os.environ["PIFLEX_OPEN_CHANNEL_FLOOR_TOP_Z"] = "-4.66"
os.environ["PIFLEX_OPEN_CHANNEL_BLUE_ROOF_LENGTH"] = "5.0"

import build_codex_v23_centered_usb_tunnels as build


if __name__ == "__main__":
    build.export()
