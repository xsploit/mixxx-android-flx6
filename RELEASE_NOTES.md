# Experimental Mixxx Android ARM64 build

This is an unofficial development build for testing Mixxx with a DDJ-FLX6 on
an Android phone or tablet. It is locally signed and may be unstable.

## Install

Download `mixxx-android-arm64.apk` on an ARM64 device running Android 9 or
newer, allow installation from the selected file source, and open the APK.

SHA-256:
`a9438ddaa4cb3f23685fe2d89c7957a2f818a186ffc2c0244a65e7427e01ee0a`

## DDJ-FLX6 status

- Android USB audio, MIDI, HID, and USB permission code is present.
- Current upstream Mixxx has no bundled DDJ-FLX6 mapping.
- FLX6 detection, four-channel master/cue audio, touch UI, and performance must
  be tested on physical hardware.
- Use a powered USB-C OTG/host hub with PD input. Connect speakers and
  headphones to the FLX6, not the phone.

See `ANDROID-HARDWARE-TEST.md` in this repository for the hookup diagram and
test sequence.

## Corresponding source

Built from upstream Mixxx commit
[`86126792a3a11b493a74ea133dc1260890d9c200`](https://github.com/mixxxdj/mixxx/commit/86126792a3a11b493a74ea133dc1260890d9c200)
with the repository's `patches/mixxx-android-wsl.patch` applied. The upstream
commit page provides the complete source archive; this repository provides the
complete local patch and build script. Mixxx's GPL and bundled third-party
license notices are in the upstream `LICENSE` file.
