# Experimental Mixxx Android ARM64 native waveform split v0.8

This is an unofficial development build for testing Mixxx with a DDJ-FLX6 on
an Android phone or tablet. It is locally signed and may be unstable.

## Install

Download `mixxx-android-flx6-v0.8.apk` on an ARM64 device running Android 9 or
newer, allow installation from the selected file source, and open the APK.

SHA-256:
`c487829a2ec3d2e1e835716b59b37c942310aeb9755be50e5e7a39b3ab564a43`

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

## Live screen adjustment

- The waveform region is anchored between the bottom of the toolbar and the
  bottom of the app, so toolbar height is deducted before sizing either deck.
- The blue `↕ DRAG` line is now the real nested `SplitView` handle. Dragging it
  directly resizes both native waveform panes instead of moving only QML overlays.
- The nested split begins below both the top toolbar and compact deck headers,
  so those offsets are removed before the A/B heights are calculated.
- Each waveform pane keeps at least 20% of the available waveform space.
- The top toolbar scrolls horizontally instead of cutting off its last controls
  on a narrow phone screen.

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
