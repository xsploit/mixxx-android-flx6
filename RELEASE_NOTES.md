# Experimental Mixxx Android ARM64 phone preview v0.2

This is an unofficial development build for testing Mixxx with a DDJ-FLX6 on
an Android phone or tablet. It is locally signed and may be unstable.

## Install

Download `mixxx-android-arm64.apk` on an ARM64 device running Android 9 or
newer, allow installation from the selected file source, and open the APK.

SHA-256:
`cbd003cac2484d393729a7a0764100205893822c6f4e37dc828a28964dbe5219`

## New phone interface

- Fits landscape screens down to 640x320 logical pixels.
- Defaults to two vertically stacked waveforms with compact deck information.
- `LIBRARY` opens the full browser; `LOAD 1`, `LOAD 2`, and `BACK` remain visible.
- `SETTINGS` directly opens a maximized preferences dialog.
- Mixer, effects, sampler, and four-deck toolbar clutter is hidden in phone mode.
- Android visual updates target 30 FPS to reduce heat and battery use.

## DDJ-FLX6 status

- Android USB audio, MIDI, HID, and USB permission code is present.
- This preview bundles an experimental community DDJ-FLX6 XML/JavaScript
  mapping. Its 558 controls parse correctly, and all 37 script bindings resolve,
  but the mapping has not yet been verified on this physical controller.
- FLX6 detection, four-channel master/cue audio, touch UI, and performance must
  be tested on physical hardware.
- Use a powered USB-C OTG/host hub with PD input. Connect speakers and
  headphones to the FLX6, not the phone.

See `ANDROID-HARDWARE-TEST.md` in this repository for the hookup diagram and
test sequence.

## Corresponding source

Built from upstream Mixxx commit
[`86126792a3a11b493a74ea133dc1260890d9c200`](https://github.com/mixxxdj/mixxx/commit/86126792a3a11b493a74ea133dc1260890d9c200)
with the repository's two patches applied. Mapping provenance and the exact
Pi-layout inspiration revisions are recorded in `SOURCES.md`. Mixxx's GPL and
bundled third-party license notices are in the upstream `LICENSE` file.
