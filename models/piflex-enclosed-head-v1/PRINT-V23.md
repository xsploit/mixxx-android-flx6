# PiFlex V23 centred USB tunnel package

V23 keeps the approved V21 opening, original 10-inch screen shell, recessed
screen bevel, four screen fasteners, Pi bay, USB ears, and FLX6 brackets. It
replaces the obsolete short routing cuts with two functional enclosed paths.

## Opening symmetry

The V21 opening is not a perfect mirror about the case centreline. Its widest
section is centred at X=0, while its top and bottom shoulders follow the
slightly offset original screen-hole pattern. The opening vertex average is
X=+1.25 mm and the screen-hole pattern centre is X=+2.3435 mm. Measured opening
clearance at the four screw centres ranges from 7.162 to 7.543 mm.

V23 deliberately does not alter that approved opening. Making it visually
mirror-perfect would require choosing between moving the opening away from the
rear-bay mouth or making the screw tabs unequal.

## Corrected USB paths

- Ear centres: X=+/-143.077 mm, Y=0.
- Each tunnel runs from X=+/-86.0 mm to its ear centre at X=+/-143.077 mm.
- Clear tunnel section: 18.4 x 10.0 mm.
- Tunnel height range: Z=-10.3 to -0.3 mm, 4.5 mm below the obsolete route.
- Added raceway section: 24.8 x 13.6 mm with a 3.2 mm floor and sidewalls.
- The original blue screen frame and first recessed bevel are not cut.
- The final blue frame closes the route from above, making it a tunnel rather
  than an open canal.
- The route is re-cut after the FLX6 yoke union so mounting geometry cannot plug
  either side.

The final validation intersects both intended voids against the blue shell,
rear mount, and fused print mesh. Both routes pass; measured residual overlap
is below 0.005 mm3 and is numerical mesh tolerance, not an obstruction.

## Print files

- `piflex-codex-v23-printable-monolithic.3mf`: preferred single-piece print.
- `piflex-codex-v23-printable-monolithic.stl`: equivalent single-piece STL.
- `piflex-codex-v23-printable-screen-shell.stl`: separate flat screen shell.
- `piflex-codex-v23-printable-rear-mount.stl`: separate rear, ears, and mount.
- `piflex-codex-v23-printable-two-part-fit-check.stl`: registered inspection
  assembly, not the default print.

The monolithic STL and 3MF survive disk round trips as watertight, consistently
wound positive volumes. The STL contains zero degenerate and zero duplicate
faces. Overall exported bounds are approximately 324.154 x 211.273 x 145.970
mm.

Physical fit still depends on the selected female USB-A extension body, cable
bend radius, screws, and printer/material tolerances. Test the actual USB lead
before committing to the full-size print.
