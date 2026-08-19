# Experimental Mixxx Android ARM64 safe-area viewports v0.10

This is an unofficial development build for testing Mixxx with a DDJ-FLX6 on
an Android phone or tablet. It is locally signed and may be unstable.

## Install

Download `mixxx-android-flx6-v0.10-safe-area.apk` on an ARM64 device running Android 9 or
newer, allow installation from the selected file source, and open the APK.

This build uses package `org.mixxx.flx6standalone` and appears as
`Mixxx FLX6 v0.10`. It upgrades v0.9 and still installs beside the older
`org.mixxx` previews.

SHA-256:
`bbb712a8ed3a9f541078b34d0cd503df48ae30c37b30aca73b0a6b68477bcfbd`

v0.2 changed an unused LateNight skin, so Android's `--new-ui` screen looked
unchanged. v0.3 corrects that mistake by patching the APK's real
`assets/qml/main.qml` entry point and its native library/settings components.

## New phone interface

- Fits landscape screens down to 640x320 logical pixels.
- Defaults to compact deck information above two large vertically stacked waveforms.
- Uses an explicit zero-spacing waveform column so Deck A and Deck B each
  receive exactly half of the available waveform area.
- Adds large permanent `A` and `B` badges plus a visible divider between lanes.
- The normal performance view contains no library panel, so the waveforms use
  all remaining space below the toolbar and deck headers.
- Restores every top toolbar control, including `4 DECKS` and `SETTINGS`.
- `LIBRARY` opens the full browser; `LOAD 1`, `LOAD 2`, and `LOAD NEXT` remain visible.
- Pressing the FLX6 browse encoder toggles the full-screen library; rotating it
  scrolls through the library as before.
- `SETTINGS` opens the native settings screen with a visible `CLOSE` button.
- Android visual updates target 30 FPS to reduce heat and battery use.

## Collapsible overlay toolbar

- The complete toolbar is hidden by default behind a tiny 42 x 18 top-center
  arrow tab.
- Opening the toolbar places it over the waveform view. It does not consume
  layout height or push the bottom waveform offscreen.
- Deck A and Deck B keep equal height and fill the full available screen behind
  the overlay; the blue middle divider remains fixed between them.
- The expanded toolbar scrolls horizontally so every control, including
  `4 DECKS`, `LIBRARY`, and `SETTINGS`, remains reachable.

## Safe-area waveform viewports

- Android's top, bottom, left, and right safe-area insets are removed before
  calculating the usable performance view, so a system navigation bar cannot
  cover the bottom of Deck B.
- Deck A and Deck B default to exactly 50% each inside the visible safe area.
- The blue divider is draggable from 20/80 through 80/20 using a 36-pixel touch
  target. It changes each deck's viewport allocation; waveform zoom is untouched.

## Android music folders

- `SETTINGS > Library` now has an Android-native `ALLOW FILES` shortcut instead
  of relying on Qt's desktop folder dialog.
- `DOWNLOADS` and `MUSIC` add the common phone folders directly.
- `ADD PATH` accepts any full path such as `/storage/emulated/0/DJ Music`.
- After adding a folder, press `SAVE` to register it and start the library scan.

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
