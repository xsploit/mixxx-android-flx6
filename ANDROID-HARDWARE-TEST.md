# Mixxx Android + DDJ-FLX6 hardware test

This is an experimental, locally signed ARM64 Android build of current upstream
Mixxx. It is not an official Mixxx Android release.

## What was built

- APK: `artifacts/mixxx-android-arm64.apk`
- Package: `org.mixxx`
- Source commit: `86126792a3a11b493a74ea133dc1260890d9c200`
- Minimum Android version: Android 9 / API 28
- CPU architecture: ARM64
- APK SHA-256: `a9438ddaa4cb3f23685fe2d89c7957a2f818a186ffc2c0244a65e7427e01ee0a`

The APK's v3 signature verifies. It contains the ARM64 Mixxx and Qt native
libraries. No Android device was attached to this machine, so installation,
launch, touch layout, controller I/O, and live audio still need a physical test.

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

1. Launch Mixxx without the controller. Grant requested music/file access,
   import one track, load it, press Play, and confirm audio from the phone.
2. Close Mixxx. Connect charger, hub, and FLX6 in the diagram above. Wait until
   the FLX6 finishes powering up, then launch Mixxx and accept any USB permission
   prompt.
3. In **Preferences > Sound Hardware**, look for `DDJ-FLX6`, `USB Audio`, or the
   product name Android reports. If it exposes four outputs, assign:
   - **Master** to channels 1-2
   - **Headphones** to channels 3-4
4. Connect speakers only to the FLX6 MASTER RCA sockets and headphones to its
   PHONES socket. Do not expect sound from the phone speaker after USB audio is
   selected.
5. In **Preferences > Controllers**, confirm that the FLX6 is listed and that
   moving a control produces input activity.

Start at 48 kHz with a moderate buffer. Turn off Bluetooth audio and remove
Android battery optimization for Mixxx while testing.

## Expected controller limitation

Current upstream Mixxx includes mappings for the DDJ-200, DDJ-400, DDJ-FLX4,
and some older Pioneer controllers, but not the DDJ-FLX6. Detection and USB
permission code are present in this build, but one-to-one FLX6 controls are not
yet bundled.

The next practical step is to capture the FLX6 MIDI messages and build a proper
Mixxx XML/JavaScript mapping. The safest fast path is:

1. Connect the FLX6 to desktop Mixxx first.
2. Use Mixxx's MIDI-learning tools for basic deck, mixer, browser, and transport
   controls.
3. Capture the harder jog-wheel, LED, VU meter, and pad behavior with MIDI debug
   logging.
4. Add the finished mapping to `res/controllers/` and rebuild this APK so it is
   available inside the Android app.

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
- **Controls register but do the wrong thing or nothing:** this is the missing
  FLX6 mapping, not an audio-cable problem.

For a useful log while reproducing a failure:

```powershell
adb logcat | findstr /i "mixxx audiomanager portaudio oboe usbpermission flx6"
```
