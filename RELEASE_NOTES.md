# Experimental Mixxx Android ARM64 active phone UI v0.3

This is an unofficial development build for testing Mixxx with a DDJ-FLX6 on
an Android phone or tablet. It is locally signed and may be unstable.

## Install

Download `mixxx-android-flx6-v0.3.apk` on an ARM64 device running Android 9 or
newer, allow installation from the selected file source, and open the APK.

SHA-256:
`dee07671d57f2b9449cdf41402f40d3a0f304172b59668b5ec89238d66cb8e27`

v0.2 changed an unused LateNight skin, so Android's `--new-ui` screen looked
unchanged. v0.3 corrects that mistake by patching the APK's real
`assets/qml/main.qml` entry point and its native library/settings components.

## New phone interface

- Fits landscape screens down to 640x320 logical pixels.
- Defaults to two vertically stacked waveforms with compact deck information.
- `LIBRARY` opens the full browser; `LOAD 1`, `LOAD 2`, and `LOAD NEXT` remain visible.
- `SETTINGS` opens the native settings screen with a visible `CLOSE` button.
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
with the repository patches applied. Mapping provenance and the exact
Pi-layout inspiration revisions are recorded in `SOURCES.md`. Mixxx's GPL and
bundled third-party license notices are in the upstream `LICENSE` file.
