# PiFlex V24 centred-ear USB tunnel package

V24 corrects the low V23 tunnel placement shown in the user's annotated side
view. Both USB routes now terminate at the true centre of each ear cavity in
all three dimensions. The original 10-inch screen shell and its first recessed
blue bevel remain untouched.

## Exact ear centre

- Ear X centres: +/-143.077 mm.
- Ear Y centre: 0.0 mm.
- Hollow ear cavity Z range: -5.8 to +10.48 mm.
- True cavity Z centre: +2.34 mm.
- The 10 mm-high ear passage occupies Z=-2.66 to +7.34 mm.

The former green path occupied Z=-10.3 to -0.3 mm and was visibly sitting at
the bottom. The corrected ear section is 7.64 mm higher.

## Preserving the blue bevel

A straight high tunnel would intersect the original screen shell. V24 uses a
closed dog-leg instead:

1. A high service mouth sits in the old back-plate plane at the already-open
   V21 bay edge.
2. The concealed middle crossing drops to Z=-10.3 to -0.3 mm beneath the blue
   shell without cutting it.
3. Inside the ear, the path rises to the true Z=+2.34 mm cavity centre.

## Validation

The final STL and 3MF are closed positive volumes with consistent winding,
zero degenerate faces, and zero duplicate faces. Each intended tunnel void is
checked against the original blue shell and the final fused mesh. Both paths
pass with zero shell obstruction and less than 0.02 mm3 numerical overlap.

The fused print uses a 0.30 mm seam overlap and a 0.001 mm precision weld. The
weld changes volume by less than 0.00027 mm3 and does not move the designed
surface at printable scale.

## Print files

- `piflex-codex-v24-printable-monolithic.3mf`: preferred single-piece print.
- `piflex-codex-v24-printable-monolithic.stl`: equivalent single-piece STL.
- `piflex-codex-v24-printable-screen-shell.stl`: separate screen shell.
- `piflex-codex-v24-printable-rear-mount.stl`: separate rear/mount.
- `piflex-codex-v24-upper-usb-tunnels.glb`: visual inspection assembly.

The remaining production gate is a physical fit test using the actual female
USB-A extension bodies, cable bend radius, screws, and chosen print material.
