# Experimental Mixxx Android ARM64 FLX6 automatic headphones v0.22

This is an unofficial development build for testing Mixxx with a DDJ-FLX6 on
an Android phone or tablet. It is locally signed and may be unstable.

## Install

Download `mixxx-android-flx6-v0.22-auto-headphones.apk` on an ARM64 device running Android 9 or
newer, allow installation from the selected file source, and open the APK.

This build uses package `org.mixxx.flx6standalone` and appears as
`Mixxx FLX6 v0.22`. It upgrades v0.9-v0.21 and still installs beside the older
`org.mixxx` previews.

SHA-256:
`fc7078d439290a170c6392b15876b4369713793570c66841e99166eaacc812cc`

## Verified FLX6 headphone cue

- Fixes FLX6 discovery across Android's actual PortAudio/Oboe API instead of
  querying an empty API name.
- Selects the API that owns the FLX6 and routes Master to USB 1/2 plus the
  controller's front PHONES/PFL output to USB 3/4.
- Skips legacy bulk/HID USB scans on Android so they cannot reset the composite
  FLX6 while Android MIDI and USB audio are opening it.
- Runs FLX6 audio setup automatically shortly after launch; the settings page
  remains available as a status display and manual retry.
- Physically verified on a Samsung S24 with FLX6 controls and front headphone
  CUE audio working through USB OTG.

## FLX6 auto-setup

- Adds a real Android MIDI backend using `android.media.midi`; the earlier APK
  bundled a mapping but had no Android MIDI backend to deliver controller data.
- Detects a connected DDJ-FLX6, enables it, and loads the bundled mapping at startup.
- Adds **SETTINGS > FLX6 Setup** with separate, plain Controls and Audio status.
- **SET UP MASTER + HEADPHONES** automatically routes Master to 1/2 and, when Android
  exposes four output channels, headphones to 3/4.
- Treats empty Android USB-audio capability arrays as unspecified and uses safe
  stereo/48 kHz fallbacks instead of silently omitting the sound card.
- No controller utility-mode button combination is part of the normal setup.

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

- The complete toolbar is hidden by default behind a 28 x 12 top-center arrow
  tab. Its invisible touch target remains 44 x 28 for reliable tapping.
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
- The waveform viewport uses only the real remaining window height and does not
  rescale when the toolbar opens. Stack adjustment stays inside that viewport.

## Precisely clipped waveform lanes

- The compact track-name, play/cue, and overview-waveform row measures its real
  implicit content height, including the deck layout's top and bottom margins.
  It has an opaque background at z-level 20 and its controls render at z-level 21.
- The black main waveform viewport is a separate lower layer at z-level 0. Its
  top is `measured header height + 5` and its height is the remaining visible
  screen. It therefore cannot begin inside overflowing cue or overview controls.
- The left and right waveform overlays use the same measured boundary. No fixed
  phone-specific header dimension remains.
- The 2-pixel blue divider is subtracted first. Every remaining visible pixel is
  assigned to Deck A or Deck B, with A receiving `floor(remaining / 2)` and B
  receiving the remainder. No waveform viewport extends into the header bounds.
- Each compact lane has 1 pixel of top and bottom padding and its own clip boundary.
- The A/B lane containers remain fixed and equal. The renderer gain is fixed at
  its normal value; this build does not stretch or compress sample amplitudes.
- Turn on `EDIT`, then pinch vertically over the stack or use `DRAW -` and
  `DRAW +` to resize only each centered native waveform drawing surface from
  35% to 100% of its unchanged lane height. Horizontal zoom, scrolling,
  playheads, lane bounds, and audio gain remain unchanged.
- The blue center grip retains the previous 72-pixel/18% whole-stack position
  adjustment, but it is movable only while `EDIT` is enabled. Pinch scaling is
  also edit-only, preventing accidental layout changes while mixing.
- The `A` and `B` badges now mark the actual centers of their respective native
  drawing surfaces instead of the fixed lane centers. In `EDIT`, drag `A` or
  `B` vertically to position that renderer independently through the space made
  available by draw scaling. Dragging is clamped at both lane edges, preserves
  the initial finger offset without jumping, and cannot alter the blue divider,
  the other deck, lane dimensions, zoom, or waveform gain.

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
