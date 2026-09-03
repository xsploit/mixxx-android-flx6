"""Build V29 with open channels dropped to the Pi-case inner back level."""

from __future__ import annotations

import os


os.environ["PIFLEX_TUNNEL_VERSION"] = "v29"
os.environ["PIFLEX_TUNNEL_SLUG"] = "pi-level-open-channels"
os.environ["PIFLEX_TUNNEL_CENTRE_Y"] = "0.0"
os.environ["PIFLEX_TUNNEL_REAR_Z"] = "-2.66"
os.environ["PIFLEX_EAR_CENTRED_DOGLEG"] = "0"
os.environ["PIFLEX_OPEN_INNER_CHANNEL"] = "1"
# V16 Pi bay: rear exterior at -35 mm with a 3 mm wall. The visible inside
# surface is therefore -32 mm; the channel floor meets it without a step.
os.environ["PIFLEX_OPEN_CHANNEL_FLOOR_TOP_Z"] = "-32.0"

import build_codex_v23_centered_usb_tunnels as build


if __name__ == "__main__":
    build.export()
