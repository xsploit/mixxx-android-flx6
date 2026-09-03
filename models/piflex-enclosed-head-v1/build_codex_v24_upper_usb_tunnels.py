"""Build V24 with centred ear mouths and a shell-safe internal dog-leg."""

from __future__ import annotations

import json
import os


os.environ["PIFLEX_TUNNEL_VERSION"] = "v24"
os.environ["PIFLEX_TUNNEL_SLUG"] = "upper-usb-tunnels"
os.environ["PIFLEX_TUNNEL_CENTRE_Y"] = "0.0"
os.environ["PIFLEX_EAR_CENTRED_DOGLEG"] = "1"

import build_codex_v23_centered_usb_tunnels as build  # noqa: E402


if __name__ == "__main__":
    print(json.dumps(build.export(), indent=2))
