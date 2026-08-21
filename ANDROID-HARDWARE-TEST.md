# Mixxx Android + DDJ-FLX6 hardware test

This is an experimental, locally signed ARM64 Android build of current upstream
Mixxx. It is not an official Mixxx Android release.

## What was built

- APK: `artifacts/mixxx-android-arm64.apk`
- Package: `org.mixxx.flx6standalone`
- Source commit: `86126792a3a11b493a74ea133dc1260890d9c200`
- Minimum Android version: Android 9 / API 28
- CPU architecture: ARM64
- APK version: `0.20.0-flx6-auto-setup` (version code 20)
- APK label: `Mixxx FLX6 v0.20`
- APK SHA-256: `4f9c156835b3328943d19f6cdd88716b4e981b312f918ff1b45bb25b1e769cb9`

The APK's v3 signature verifies. It contains the ARM64 Mixxx and Qt native
libraries. No Android device was attached to this machine, so installation,
launch, touch layout, controller I/O, and live audio still need a physical test.
The APK contains the active phone QML interface and experimental FLX6 mapping.
The normal compact view has deck headers and stacked waveforms but no library
panel. The complete toolbar is hidden behind a tiny top-center arrow and opens
as an overlay without resizing the waveform view. Android safe-area margins
keep Deck B above any system navigation bar, and the obsolete 320-logical-pixel
minimum window height has been removed. The main waveform viewport begins below
the track header and splits all remaining height equally around its blue divider.
The adjustable stack remains clipped inside that lower layer. Use Android's App Info screen to confirm
version `0.20.0-flx6-auto-setup` and package
`org.mixxx.flx6standalone`.

## Correct hookup

Use a powered USB-C OTG/host hub or adapter:

```text
PD charger ----> hub PD-IN
Android phone -> hub HOST/PHONE cable
DDJ-FLX6 ------> hub USB-A data port (USB-B-to-A data cable)

DDJ-FLX6 MASTER RCA -> powered speakers / amplifier
DDJ-FLX6 PHONES     -> headphones
```

There are not two independent USB data paths. The one USB data connection can
carry controller messages from the FLX6 to Android and mixed audio from Android
back to the FLX6. The extra connection on the hub is power injection so the
phone stays in USB-host mode while the bus-powered FLX6 gets adequate power.

A powered Meta Quest link cable is only useful if it explicitly supports an
Android phone acting as the USB host and powers the attached USB device. Most
Quest charging/link cables assume a PC is the host, so their connector topology
is wrong for this job even though they carry both power and data.

## Install

Copy the APK to the Android device and open it, allowing installation from that
file source. If Android platform tools are installed on Windows and USB
debugging is enabled, the equivalent command is:

```powershell
adb install -r "C:\Users\SUBSECT\Documents\Codex\2026-08-18\hey-i-need-you-to-research\artifacts\mixxx-android-arm64.apk"
```

Android may warn that this is an unknown or locally signed app. That is expected.

## Test order

1. Close Mixxx completely.
2. Connect the FLX6 and wait for it to finish powering up.
3. Open **Mixxx FLX6 v0.20**. No FLX6 utility-mode button combination is needed.
4. Tap **SETTINGS**. The first page is **FLX6 Setup**. Tap
   **CHECK AND SET UP FLX6** once.
5. Read the two plain status lines:
   - **Controls: Ready** means Android MIDI is open and the FLX6 mapping loaded.
   - **Audio: Ready** means Master 1/2 is routed; if Android exposes four
     channels, headphones 3/4 is routed too.
6. Close Settings and try **PLAY**, a channel fader, and the browse encoder.
   The browse encoder press should open the full-screen library.

If Controls says **Not detected**, leave the cable connected, close Mixxx, and
open it once more. If Audio alone says **Not detected**, the MIDI test can still
continue; Android has not exposed the FLX6 audio endpoint on that phone.

Start at 48 kHz with a moderate buffer. Turn off Bluetooth audio and remove
Android battery optimization for Mixxx while testing.

## Experimental controller mapping

Current upstream Mixxx includes mappings for the DDJ-200, DDJ-400, DDJ-FLX4,
and some older Pioneer controllers, but not the DDJ-FLX6. This APK adds a
community FLX6 mapping derived from the Pioneer mappings. It is structurally
valid and bundled in the APK, but physical behavior is not proven yet.

Test browser, load, play/cue, channel faders, EQ, crossfader, jog wheels, pads,
deck switching, LEDs, and VU meters in that order. Record anything incorrect;
the repair path is:

1. Connect the FLX6 to desktop Mixxx first.
2. Use Mixxx's MIDI-learning tools for basic deck, mixer, browser, and transport
   controls.
3. Capture the harder jog-wheel, LED, VU meter, and pad behavior with MIDI debug
   logging.
4. Correct `controller-mapping/Pioneer-DDJ-FLX6.midi.xml` or its JavaScript and
   rebuild the APK.

Trying to make rekordbox identify one controller as a different model does not
solve Mixxx's mapping or Android audio routing. A native Mixxx FLX6 mapping is
the shorter, maintainable route.

## Failure clues

- **FLX6 has no lights:** the adapter is not providing enough bus power or is
  not maintaining USB host mode. Use a powered OTG hub with PD input.
- **FLX6 powers up but is absent from both Sound Hardware and Controllers:** the
  cable/adapter is charge-only or has the wrong host topology.
- **Controller appears but no FLX6 audio device appears:** Android did not expose
  its USB audio endpoints to Mixxx. Controller input can still work, but master
  and cue would need a separate Android-compatible multichannel USB interface.
- **Audio appears but only two output channels exist:** master can use the FLX6,
  but separate cue may require an Android/driver fix or a second supported audio
  interface. A DDJ-200-style phone splitter is only a fallback and reduces
  master and cue to mono.
- **Controls register but do the wrong thing or nothing:** the bundled mapping
  needs hardware-specific correction; this is separate from the audio path.

For a useful log while reproducing a failure:

```powershell
adb logcat | findstr /i "mixxx audiomanager portaudio oboe usbpermission flx6"
```
