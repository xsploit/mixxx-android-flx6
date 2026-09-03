"""Build V36: V35 plus a flush orange join web and rounded-ear cleanup."""

from __future__ import annotations

import os


os.environ["PIFLEX_TUNNEL_VERSION"] = "v36"
os.environ["PIFLEX_TUNNEL_SLUG"] = "flush-inner-join"
os.environ["PIFLEX_TUNNEL_CENTRE_Y"] = "0.0"
os.environ["PIFLEX_TUNNEL_REAR_Z"] = "-2.66"
os.environ["PIFLEX_EAR_CENTRED_DOGLEG"] = "0"
os.environ["PIFLEX_OPEN_INNER_CHANNEL"] = "1"
os.environ["PIFLEX_OPEN_CHANNEL_FLOOR_TOP_Z"] = "-4.66"
os.environ["PIFLEX_OPEN_CHANNEL_BLUE_ROOF_LENGTH"] = "5.0"
os.environ["PIFLEX_EAR_USB_CUT_FLOOR_Z"] = "-4.66"
os.environ["PIFLEX_EAR_USB_CUT_INNER_Y"] = "9.0"
os.environ["PIFLEX_HOLLOW_EAR_INTERIOR"] = "1"

# Do not raise, widen, or relocate any of the four original screw features.
# Only the surrounding inner wall is extended toward the blue shell.
os.environ["PIFLEX_EXTEND_ORIGINAL_SCREW_TOWERS"] = "0"
os.environ["PIFLEX_FILL_FLUSH_SCREEN_BAY_JOIN"] = "1"
os.environ["PIFLEX_SCREEN_BAY_JOIN_Z0"] = "-10.0"
os.environ["PIFLEX_SCREEN_BAY_JOIN_TOP_Z"] = "-6.84"

# Clip the internal rectangular USB support to the rounded ear envelope.
os.environ["PIFLEX_CLIP_USB_REINFORCEMENT_TO_EAR"] = "1"

import build_codex_v23_centered_usb_tunnels as build


if __name__ == "__main__":
    build.export()
