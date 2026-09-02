# Codex V18 USB-routing variant

This branch starts from the exact last-known-good V18 GLB and changes only the
rear service opening in the original 10-inch screen shell.

## Geometry

- Opening: 147.001 x 108.802 mm
- Opening centre: X 2.343 mm, Y -0.133 mm in screen-shell coordinates
- Four original screen screw towers remain intact
- 1.0 mm structural web remains outside each 5.5 mm screw tower
- Both existing hollow USB ears, top-facing USB socket openings and concealed
  ear-to-Pi-cavity channels are unchanged from V18
- FLX6 mount and bracket mesh are byte-for-byte geometrically unchanged
- Outer dimensions and transform of the original screen case are unchanged

## Files

- `piflex-codex-v18-usb-routing.glb` - review model
- `piflex-codex-v18-usb-routing-fit-check.stl` - physical fit-check export
- `inspection-codex-v18-usb-routing.json` - source hash and geometry checks
- `piflex-codex-v18-usb-routing-*.png` - exterior review renders
- `piflex-codex-v18-usb-channel-cutaway.png` - internal routing reference

The STL remains a fit-check prototype until the actual female USB panel-mount
parts and Pi-side cable clearances are measured with calipers.
