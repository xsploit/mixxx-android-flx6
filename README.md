# Mixxx Android FLX6 phone preview

- Start with `ANDROID-HARDWARE-TEST.md` for installation, FLX6 wiring, and the
  exact hardware test sequence.
- `scripts/build-mixxx-android.sh` reproduces the signed ARM64 APK from the
  prepared WSL build environment.
- `scripts/verify-mixxx-android.sh` inspects package metadata, signature, and
  native libraries.
- `patches/mixxx-android-wsl.patch` permits only the Android cross-build through
  Mixxx's WSL guard; it does not enable unsupported WSL desktop builds.
- `patches/mixxx-android-phone-ui.patch` adds the Android frame-rate target and
  retains the earlier skin experiment for provenance.
- `patches/mixxx-android-active-phone-ui.patch` patches Android's actual
  `qml/main.qml` entry point, native library, and native settings screens.
- `patches/mixxx-android-v0.3-version.patch` sets APK version code 3.
- `patches/mixxx-android-v0.4-performance-view.patch` keeps the full toolbar,
  expands the stacked waveforms, and makes the library a separate full-screen view.
- `patches/mixxx-android-v0.5-waveform-fix.patch` gives both waveform lanes
  deterministic equal height and adds permanent A/B deck markers.
- `patches/mixxx-android-v0.6-storage-access.patch` replaces Android's unusable
  desktop folder dialog with file-access, Downloads/Music, and custom-path controls.
- `patches/mixxx-android-v0.7-live-layout.patch` anchors the waveform region
  below the toolbar, makes the toolbar horizontally scrollable, and adds a live
  A/B waveform-height divider.
- `patches/mixxx-android-v0.8-native-waveform-split.patch` makes that blue
  divider the actual nested `SplitView` handle, directly resizing both waveform renderers.
- `patches/mixxx-android-v0.9-version-and-package.patch` gives the repaired
  build a new Android package ID so it installs beside older previews.
- `patches/mixxx-android-v0.9-collapsible-toolbar.patch` keeps the two
  waveform lanes fixed at equal height and moves the complete toolbar into a
  collapsible overlay that never changes the waveform layout.
- `patches/mixxx-android-v0.10-safe-area-viewports.patch` keeps the waveform
  view inside Android's reported safe area and restores a draggable blue
  divider that allocates viewport height without changing waveform zoom.
- `patches/mixxx-android-v0.11-visible-window-height.patch` removes desktop
  minimum-window dimensions that made the QML scene taller than some phone
  screens and physically clipped the bottom of Deck B.
- `patches/mixxx-android-v0.12-fixed-waveform-stack.patch` preserves the
  original equal A/B renderer heights and changes the blue handle to translate
  the complete waveform-and-label stack vertically inside a clipped viewport.
- `patches/mixxx-android-v0.13-draggable-waveform-stack.patch` gives that
  translation an unconditional 72-pixel/18% range instead of disabling it when
  Qt reports a viewport taller than the earlier design constant.
- `patches/mixxx-android-v0.14-clipped-waveform-lanes.patch` removes that
  oversized translated canvas. The track headers own their 62-pixel region;
  the remaining clipped viewport is split into equal A/B lanes around a 2-pixel
  divider, with 1-pixel compact-screen padding and adjustable visual waveform gain.
- `patches/mixxx-android-v0.15-layered-adjustable-waveforms.patch` restores the
  draggable A+B stack while separating its bounds from the header: the header
  is an opaque high-z layer and the clipped waveform viewport explicitly starts
  at the shared 62-pixel boundary beneath it.
- `patches/mixxx-android-v0.16-five-pixel-header-guard.patch` adds a 5-pixel
  guard beneath that header. The waveform viewport and both side overlays now
  begin at pixel 67, without changing the working stack adjustment.
- `patches/mixxx-android-v0.17-measured-header-layout.patch` removes the fixed
  header height. Each minimized deck reports its actual layout implicit height,
  including margins; the waveform viewport follows the measured header bottom.
- `patches/mixxx-android-v0.18-edit-locked-draw-scale.patch` keeps both lane
  containers fixed, adds edit-only vertical scaling of the centered native
  waveform drawing surfaces, locks stack movement outside edit mode, and makes
  the toolbar arrow visually smaller without shrinking its touch target.
- `patches/mixxx-android-v0.19-independent-waveform-centers.patch` makes the A
  and B badges track their actual renderer centers. In edit mode, each badge
  independently drags its renderer through the unused space inside its fixed lane.
- `patches/mixxx-android-v0.20-flx6-autosetup.patch` adds the Android MIDI
  backend, automatic FLX6 mapping/audio setup, and the simple hardware status page.
- `android-midi/` contains the Java/Qt MIDI bridge and FLX6 setup UI.
- `controller-mapping/` contains the bundled experimental DDJ-FLX6 mapping and
  its upstream license.

The APK is a development artifact, not an official Mixxx release. The source
build and static APK checks succeed, but live Android USB audio, mapping
accuracy, touch layout, and DDJ-FLX6 behavior must be verified on the target
device.

## Phone layout

- Performance view: compact deck/track information above two large vertically
  stacked moving waveforms, divided evenly and marked `A` and `B`. The library
  is not shown in this view.
- `LIBRARY`: full-screen browser. Select a track and use `LOAD 1` or `LOAD 2`.
- `SETTINGS`: maximized preferences dialog for library folders, sound hardware,
  and controller configuration.
- In `SETTINGS > Library`, tap `ALLOW FILES`, enable Mixxx in Android's file
  access screen, then add `Downloads`, `Music`, or any full `/storage/...` path.
- The complete top toolbar remains available, including `4 DECKS`, effects,
  auxiliary, sampler, edit, developer, library, and settings controls. Tap the
  tiny top-center arrow to show or hide it.
- Pressing the FLX6 browse encoder toggles the full-screen library; turning it
  continues to move through the track list.
- The toolbar floats over the waveform screen instead of pushing either deck
  downward. Swipe it sideways when expanded to reach controls on narrow screens.
- The track labels and overview waveforms occupy a fixed header. The black main
  waveform viewport begins at the header's bottom edge and cannot render behind it.
- Deck A and Deck B receive equal shares of the remaining visible height after
  the 2-pixel blue divider is subtracted. Each compact lane has 1-pixel top and
  bottom padding and its own clip boundary.
- Turn on `EDIT`, then pinch vertically over the waveform stack or use `DRAW -`
  and `DRAW +`. This scales each native waveform drawing surface from 35% to
  100%, centered inside its unchanged lane. It does not alter audio gain, visual
  sample amplitude, horizontal zoom, scroll position, or A/B lane dimensions.
- In `EDIT`, dragging the blue center grip moves the complete fixed-size A+B
  stack through its previous 72-pixel/18% adjustment range. Outside `EDIT`, the
  grip and pinch scaling are locked. The opaque header remains fixed above the
  clipped waveform viewport.
- After shrinking the drawing surfaces, drag the `A` or `B` badge vertically in
  `EDIT` to position that renderer independently. The badge stays attached to
  the renderer center, and movement is clamped so the complete drawing surface
  remains inside its unchanged lane. This can close the A-bottom or B-top gap
  without resizing the lane or moving the blue divider.
- The toolbar arrow is 28 x 12 visible pixels with a centered 44 x 28 invisible
  touch target, keeping it clear of the cue controls without making it hard to tap.
- A 5-pixel opaque guard separates the measured cue/overview header from the
  black waveform viewport, preventing edge bleed over those controls. The same
  calculation responds to different phone, tablet, density, and font layouts.

## Corresponding source and licensing

The APK was built from the Mixxx source at commit
[`86126792a3a11b493a74ea133dc1260890d9c200`](https://github.com/mixxxdj/mixxx/commit/86126792a3a11b493a74ea133dc1260890d9c200)
with the repository patches applied. Mixxx is distributed under the GNU
GPL version 2 or, at your option, any later version; its complete license and
third-party notices are in the upstream
[`LICENSE`](https://github.com/mixxxdj/mixxx/blob/86126792a3a11b493a74ea133dc1260890d9c200/LICENSE)
file. The exact source and inspiration revisions are recorded in `SOURCES.md`.
