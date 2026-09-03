# PiFlex V26 straight raised USB tunnels

V26 restores the original side-to-side tunnel placement and raises the entire
USB route directly outward through the blue rear case. It replaces V24's
stepped dog-leg with one straight 18.4 x 10.0 mm clear passage on each side.

## Geometry

- Tunnel centre Y: 0.0 mm (the original centred placement).
- Tunnel Z range: -2.66 to +7.34 mm.
- Ear cavity Z range: -5.8 to +10.48 mm.
- Blue shell material removed for the two routes: 4862.308 mm3.
- The original screen screw pattern and main service opening remain intact.

## Validation

The final STL and 3MF round-trip as closed positive volumes with consistent
winding, zero degenerate faces, and zero duplicate faces. Both tunnel paths
pass the obstruction check with less than 0.02 mm3 numerical overlap.

## Print files

- `piflex-codex-v26-printable-monolithic.3mf`: preferred single-piece print.
- `piflex-codex-v26-printable-monolithic.stl`: equivalent single-piece STL.
- `piflex-codex-v26-printable-screen-shell.stl`: separate unregistered shell.
- `piflex-codex-v26-registered-screen-shell.stl`: shell with tunnel cuts.
- `piflex-codex-v26-printable-rear-mount.stl`: separate rear and mount.

Physical fit of the selected female USB-A extensions, screws, and cable bend
radius remains the final production check.
