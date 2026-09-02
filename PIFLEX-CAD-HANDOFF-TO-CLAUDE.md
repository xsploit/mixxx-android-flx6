# PiFlex CAD handoff for Claude

Date: 2026-09-02  
Workspace: `C:\Users\SUBSECT\Documents\Codex\2026-08-18\hey-i-need-you-to-research`  
Git branch: `main`  
Remote: `https://github.com/xsploit/mixxx-android-flx6.git`

## Immediate task

Start from the exact last-known-good V18 enclosure model and make **one small,
symmetrical enlargement of the existing rectangular opening in the rear of the
screen case**.

### Latest requirements supersede the earlier logo limit

The opening is not only for Pi access. It must create a usable cable-routing
volume between the Raspberry Pi cavity and both USB ears. The user's latest
instruction explicitly allows the opening to extend farther into the second
screen-case layer and past/through the printed logo if necessary. The logo is
therefore no longer protected geometry. The four screen fasteners and their
structural material are the hard limits.

The finished internal path is:

```text
left top-facing female USB socket
        -> hollow left ear
        -> enclosed left cable channel
        -> enlarged central Pi cavity
        <- enclosed right cable channel
        <- hollow right ear
        <- right top-facing female USB socket
```

Both ears must receive real internal cutouts for the panel-mount/female USB
connectors. From the middle/inside end of each ear, cut one concealed channel
through the adjacent screen-case layer into the central Pi opening. The channels
must be voids inside the enclosure, not solid protruding tunnels and not exposed
external raceways.

The user does **not** want a new case, a replacement plate, a rebuilt frame, or
a union that changes the visible enclosure. The complete V18 case must stay in
place. Only the existing rear opening should become slightly larger.

The enlarged opening should:

- remain centered left/right;
- extend far enough into the second/rear screen-case layer to meet both ear
  channels; it may remove printed-logo material;
- encompass/remove the two short horizontal raised slit/vent features directly
  above and below the old opening;
- retain the four screen screw areas;
- leave the front bezel, outside walls, ears, capped top USB openings, Pi pod,
  FLX6 clamps, controller-port clearances, angle, position, and all other V18
  geometry unchanged.

Earlier, the user described a small enlargement. The latest explanation adds
the functional reason for more clearance: female USB leads must pass from both
ears to the Pi cavity. Prefer the smallest opening that provides that complete
route, but do not preserve the logo at the expense of usable cable paths.

### Authoritative visual target

The user's annotated target image has been copied into the repository:

`models\piflex-enclosed-head-v1\reference-opening-target.png`

SHA-256:

`C187ADCCB211E418B519C16B5671C85A8792BFBF897F7C60A565FB27F899ACFD`

In that image, the black rectangle was the earlier requested opening boundary:

- enlarge the existing blue opening outward to approximately the black box;
- the upper and lower horizontal rails/slits inside that black box are removed
  as part of the opening;
- the opening remains symmetrical around the existing opening;
- every orange case surface outside the black box remains present.

The user's later USB-routing instruction supersedes the black box as a hard
maximum. The opening may grow past it and through the logo region, but only as
far as required to connect both concealed ear channels while retaining all four
screw guards and the surrounding case.

The markup indicates an earlier target roughly around `108-112 mm` wide and
`100-106 mm` high. The existing V18 parametric code also defines a larger proven
screw-safe throat of `144.001 x 105.802 mm`, centered at approximately
`(2.343, -0.133) mm`. That larger throat stops immediately before the four 8 mm
screw guards and is the strongest existing starting point for the revised
USB-routing requirement. Compare both options against the real channel path;
do not simply delete the entire back layer.

## Immutable last-known-good source

This is the user-designated last-known-good model:

`models\piflex-enclosed-head-v1\piflex-complete-shifted-enclosure-only-v18.glb`

SHA-256:

`1E8F38C9B0FE71293D4C65373161993A344A87A454690EFCA5019AC39078182C`

Git commit that introduced the V18 source:

`3a572fd Keep PiFlex service opening clear of screen screws`

Do not overwrite, rename, transform, or regenerate that GLB. Import it, duplicate
the screen-shell object, and save the result under a new revision filename.

The source contains two objects:

1. `Exact original 10-inch shell, opened only beneath Pi pod`
2. `PiFlex V18 shifted-placement complete enclosure`

Keep those as separate objects. Do not boolean-union the shell and mount merely
to make a one-object GLB; that is what caused the enclosure to look removed or
flattened in earlier attempts.

## Verified shell coordinate system

After importing the V18 GLB with Blender/bpy, the screen-shell object's local
coordinates are:

- X: screen width
- Y: screen height
- Z: case thickness
- local bounds: `[-126.577, -85.771, -6.840]` to
  `[126.577, 85.771, 6.840]` mm
- dimensions: `253.154 x 171.542 x 13.680 mm`

Its imported world matrix is:

```text
[-1.00000, -0.00000, -0.00000, -18.62900]
[ 0.00000, -0.90631, -0.42262, 244.24420]
[ 0.00000, -0.42262,  0.90631,  98.44753]
[ 0.00000,  0.00000,  0.00000,   1.00000]
```

Important: the screen face is local **X/Y** and thickness is local **Z**. One
failed attempt treated X/Z as the screen plane and therefore did not enlarge
the visible opening.

The old V18 opening was made in `render_enclosed_head.py` with:

```python
x_limit = 89.524 / 2.0 + 2.0
y_limit = 60.345 / 2.0 + 2.0
```

That is approximately `93.524 x 64.345 mm`, centered on the screen shell.

The screen screw centers used by V18 are approximately:

```text
(-77.657, -61.034)
(-77.657,  60.768)
( 82.344, -61.034)
( 82.344,  60.768)
```

V18 used an 8 mm keep-out radius around each screw. Any new opening must remain
outside those guards.

## Current candidate, not yet accepted

There is a current unaccepted candidate derived directly from the V18 GLB:

- `models\piflex-enclosed-head-v1\piflex-v18-wide-service-opening.glb`
- `models\piflex-enclosed-head-v1\piflex-v18-wide-service-opening.stl`
- build script:
  `models\piflex-enclosed-head-v1\build_v18_wide_opening.py`
- render script:
  `models\piflex-enclosed-head-v1\render_v18_wide_opening.py`
- report:
  `models\piflex-enclosed-head-v1\inspection-v18-wide-service-opening.json`

The candidate currently uses a centered `104 x 92 mm` X/Y opening
(`X = +/-52`, `Y = +/-46`). It is too small for the newly clarified two-ear
cable-routing goal and contains no newly verified connector/channel work. The
user has not accepted it. Treat it only as a reference for how to preserve the
V18 shell object while cutting; redesign the cavity/channel geometry around the
latest requirement.

Latest rear render:

`models\piflex-enclosed-head-v1\piflex-v18-wide-opening-rear.png`

The candidate preserves these checked invariants:

- original V18 source SHA-256 unchanged;
- V18 mount/bracket mesh digest unchanged;
- shell outer bounds unchanged;
- only the screen-shell object was edited;
- no shell/mount union was performed.

## Recommended editing method

Use the same bounded face-cut strategy used by V18:

1. Import the last-known-good V18 GLB.
2. Identify the shell and mount by their object names, not polygon count.
3. Duplicate the shell object for the new revision.
4. In the shell's local X/Y plane, bisect triangles at the four desired opening
   boundaries. Start from V18's `144.001 x 105.802 mm` screw-safe throat and
   reduce it only if the two ear channels still connect cleanly.
5. Delete only faces whose centers lie within those X/Y boundaries.
6. Leave the mount object byte-for-byte/vertex-for-vertex unchanged.
7. Export a new GLB with the edited shell and untouched V18 mount as two objects.
8. Render rear, front, side, and rear three-quarter images before calling it
   complete.

For the ears and channels:

1. Preserve the rounded exterior and permanent caps of both ears.
2. Use the existing top-facing USB socket openings as the connector locations.
3. Hollow sufficient internal space for the female USB bodies and cable bend
   radius; do not size this from the USB metal tongue alone.
4. Cut a channel from the inner middle of each ear into the central cavity.
5. Keep each channel within the ear/case envelope with continuous floor, roof,
   and outside walls.
6. Make the left and right routes symmetrical unless measured Pi connector or
   strain-relief requirements justify a difference.
7. Test with solid proxy models for the female USB connectors and plugs, then
   hide/remove the proxies before exporting the printable body.

The current `build_v18_wide_opening.py` demonstrates this method with Blender's
`bmesh.ops.bisect_plane`. Adjust only `OPENING_WIDTH`, `OPENING_BOTTOM`, and
`OPENING_TOP` if the user wants a smaller or larger cut.

Do not use a solid Boolean directly on this display GLB unless the shell is
first repaired and the before/after exterior is proven identical. The imported
V18 display meshes are not watertight, and one Boolean attempt incorrectly
expanded the shell thickness bounds from `+/-6.84` to `+/-10 mm`.

## Tooling and exact commands

Blender is available as the cached Python `bpy` package (version 5.0.1):

```powershell
uv run --python 3.11 --with bpy python "models\piflex-enclosed-head-v1\build_v18_wide_opening.py"
uv run --python 3.11 --with bpy python "models\piflex-enclosed-head-v1\render_v18_wide_opening.py"
```

CadQuery can be run through uv when needed:

```powershell
uv run --with cadquery python path\to\script.py
```

FreeCAD is installed here:

```text
C:\Users\SUBSECT\AppData\Local\Programs\FreeCAD 1.1\bin\FreeCADCmd.exe
```

The immediate V18 opening edit does not require CadQuery or FreeCAD; Blender is
the correct tool because the authoritative input is a GLB scene with two
already-positioned meshes.

To verify the protected source hash:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath "models\piflex-enclosed-head-v1\piflex-complete-shifted-enclosure-only-v18.glb"
```

## Required visual proof

Before handing a model back to the user, provide:

1. Rear V18 before/after images from the exact same camera.
2. A front three-quarter render proving the complete case is still present.
3. A side render proving case depth and screen angle are unchanged.
4. A close rear render showing the larger opening stops before the logo and
   includes the two horizontal slits.
5. A statement of the old and new opening dimensions.

Do not rely only on a script report claiming the case is preserved. Earlier
reports said that while the visible exported model was clearly wrong. The
render is the acceptance test.

## Printability warning

Do not describe the current GLB-derived STL as production-ready solely because
it exports. The exact V18 visualization shell was originally altered by
splitting/deleting faces and is not watertight. Before actual printing, repair
or recreate the accepted opening in the original solid screen-shell STL, then
validate manifoldness, wall thickness, screw towers, connector access, and fit
with physical caliper measurements.

Original solid screen-shell source:

`models\makerworld-3116241\stl\screen-case\10Inch_TouchDisplay2_DesktopCase_Shell.stl`

## Rejected approaches and files

Do not use these as the next source:

- `piflex-v18-cleaned-one-piece.*`
- `piflex-v18-cleaned-complete.*`
- the reverted V20 work

Those attempts regenerated/unioned geometry and produced the flat/missing-case
appearance the user rejected.

Relevant Git history:

```text
24177f3 Clean V18 case without cutting front rim        # rejected result
b67021e Revert "Retain PiFlex screen screw plate in V20"
93d9162 Retain PiFlex screen screw plate in V20         # reverted
3a572fd Keep PiFlex service opening clear of screen screws  # V18 baseline
```

## Broader model constraints already established

- Rear views must not be mirrored. On the FLX6, USB-B is on the right when
  viewed from the back.
- The right controller bracket has the controller USB-B clearance.
- The opposite bracket has the RCA/master-output clearance.
- The screen and enclosure are shifted approximately 18.629 mm from the earlier
  bracket placement to center the screen on the controller's center encoder.
- The screen angle is approximately 25 degrees, deliberately flatter than the
  original tablet-mount reference.
- The USB ears are part of the enclosure, capped, and their USB sockets face
  upward.
- Existing ear envelope: `38 x 70 mm`, 3.2 mm nominal wall, 9 mm rear depth.
- Existing top USB opening: `16.4 x 9.2 mm`, centered in the upper edge. Verify
  the actual female USB panel-mount hardware before final print.
- V18 already contains an initial concealed-channel concept with 18 mm clear
  height and 6.8 mm depth. Inspect and extend/repair it rather than adding the
  earlier protruding tunnel geometry.
- Both ear channels must terminate openly in the enlarged Pi cavity so a female
  USB extension can be inserted from the ear and routed to the Pi without
  removing exterior case material.
- Preserve the existing V18 port clearances, screw holes, clamp geometry, and
  placement unless the user explicitly requests a separate change.

## Repository safety

The worktree contains many untracked CAD renders, models, build artifacts, and
unrelated BiteDJ/PiFlex OS changes. Do not run broad `git clean`, reset, checkout,
or mass deletion. Do not overwrite old V18 files. Stage and commit only the
exact new handoff/model files intended for the next revision.
