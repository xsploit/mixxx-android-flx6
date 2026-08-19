# Experimental Mixxx Android ARM64 clipped waveform lanes v0.14

This is an unofficial development build for testing Mixxx with a DDJ-FLX6 on
an Android phone or tablet. It is locally signed and may be unstable.

## Install

Download `mixxx-android-flx6-v0.14-clipped-waveform-lanes.apk` on an ARM64 device running Android 9 or
newer, allow installation from the selected file source, and open the APK.

This build uses package `org.mixxx.flx6standalone` and appears as
`Mixxx FLX6 v0.14`. It upgrades v0.9-v0.13 and still installs beside the older
`org.mixxx` previews.

SHA-256:
`8d259fef26affc265ae7dc70d9ebd5d633cc645102e4ab2c9047195a8adef70f`

v0.2 changed an unused LateNight skin, so Android's `--new-ui` screen looked
unchanged. v0.3 corrects that mistake by patching the APK's real
`assets/qml/main.qml` entry point and its native library/settings components.

## New phone interface

- Fits landscape screens down to 640x320 logical pixels.
- Defaults to compact deck information above two large vertically stacked waveforms.
- Uses an explicit compact waveform stack with equal A and B lanes and 1-pixel padding.
- Adds large permanent `A` and `B` badges plus a visible divider between lanes.
- The normal performance view contains no library panel; a clipped viewport
  below the deck headers shows the fixed waveform stack.
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
- Deck A and Deck B keep equal height behind the overlay.
- The expanded toolbar scrolls horizontally so every control, including
  `4 DECKS`, `LIBRARY`, and `SETTINGS`, remains reachable.

## Safe-area waveform viewports

- Android's top, bottom, left, and right safe-area insets are removed before
  calculating the usable performance view, so a system navigation bar cannot
  cover the bottom of Deck B.
- The performance viewport is calculated inside the visible safe area before
  positioning the fixed waveform stack.

## Visible phone height

- Removes the desktop-oriented 640x320 minimum window size. On the reported
  1280x591 screen, that minimum produced an approximately 640-pixel-tall scene
  at 2x scaling and placed the bottom roughly 49 physical pixels offscreen.
- The QML window now accepts Android's real landscape height before subtracting
  the deck header and calculating the A/B split.
- The waveform viewport uses only the real remaining window height; it does not
  translate into hidden space or rescale when the toolbar opens.

## Precisely clipped waveform lanes

- The compact track-name and overview-waveform row owns a fixed 62-pixel header.
  The black main waveform viewport starts at its bottom edge and is hard-clipped,
  so it cannot bleed behind the labels or mini overview waveforms.
- The 2-pixel blue divider is subtracted first. Every remaining visible pixel is
  assigned to Deck A or Deck B, with A receiving `floor(remaining / 2)` and B
  receiving the remainder. There is no oversized or translated hidden canvas.
- Each compact lane has 1 pixel of top and bottom padding and its own clip boundary.
- The colored waveform signal defaults to 1.7x visual gain to use more of each
  lane. `WAVE -` and `WAVE +` adjust it between 1.0x and 2.5x without resizing
  the lanes or changing waveform zoom, horizontal scrolling, or the playhead.

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
