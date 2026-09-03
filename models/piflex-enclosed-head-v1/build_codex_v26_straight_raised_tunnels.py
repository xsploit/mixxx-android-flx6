"""Build V26 with straight USB tunnels raised through the blue case back."""

from __future__ import annotations

import os


os.environ["PIFLEX_TUNNEL_VERSION"] = "v26"
os.environ["PIFLEX_TUNNEL_SLUG"] = "straight-raised-tunnels"
os.environ["PIFLEX_TUNNEL_CENTRE_Y"] = "0.0"
# Match the already-established ear opening height for the entire passage.
os.environ["PIFLEX_TUNNEL_REAR_Z"] = "-2.66"
os.environ["PIFLEX_EAR_CENTRED_DOGLEG"] = "0"

import build_codex_v23_centered_usb_tunnels as build


if __name__ == "__main__":
    build.export()
