# PiFlex V22 printable enclosure

V22 transfers the approved V21 opening onto the original watertight 10-inch
screen-shell STL and validates every delivered print mesh with the Manifold
kernel and an independent Trimesh volume check.

## Print files

- `piflex-codex-v22-printable-monolithic.stl`: one fused enclosure containing
  the screen shell, rear Pi bay, USB ears, and FLX6 brackets.
- `piflex-codex-v22-printable-monolithic.3mf`: the same fused enclosure in a
  slicer-friendly 3MF container with millimetre units.
- `piflex-codex-v22-printable-screen-shell.stl`: repaired screen shell in the
  original flat source orientation.
- `piflex-codex-v22-printable-rear-mount.stl`: rear Pi bay, USB ears, and FLX6
  brackets in their registered assembly orientation.
- `piflex-codex-v22-printable-two-part-fit-check.stl`: both separate parts in
  their exact assembled placement; use this for inspection, not as the default
  print file.

The monolithic enclosure is watertight, consistently wound, has positive
volume, and contains zero degenerate or duplicate faces after an STL disk
round trip. Its 3MF round trip also remains a closed positive volume. The
registered blue and orange bodies overlap by 6,467.418 mm3 before fusion,
proving the result is joined rather than merely coincident.

## Dimensions and material notes

- Monolithic assembled bounds: 324.154 x 211.273 x 145.986 mm in the exported
  assembly orientation. Confirm the printer build volume before slicing.
- The fused version uses a 0.10 mm seam relief along the screen normal to avoid
  coplanar zero-area triangles. Separate-part registration remains exact V21.
- Rear-bay nominal wall: 3.0 mm.
- USB-ear nominal wall: 3.2 mm.
- Minimum web around guarded screen screw towers: 1.0 mm.
- The V21 opening retains at least 7.162 mm from its cut boundary to the screw
  tower centres.

Topology is print-ready. Physical fit still requires confirming the actual
screen screws, female USB-A panel-lead bodies, cable bend radius, and the chosen
printer/material shrink compensation. Print a connector/fastener test coupon
before committing to the full enclosure.

The exact validation data is in `inspection-codex-v22-print-parts.json`.
