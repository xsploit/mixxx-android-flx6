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
- The complete top toolbar remains available, including `4 DECKS`, effects,
  auxiliary, sampler, edit, developer, library, and settings controls.
- Pressing the FLX6 browse encoder toggles the full-screen library; turning it
  continues to move through the track list.

## Corresponding source and licensing

The APK was built from the Mixxx source at commit
[`86126792a3a11b493a74ea133dc1260890d9c200`](https://github.com/mixxxdj/mixxx/commit/86126792a3a11b493a74ea133dc1260890d9c200)
with the repository patches applied. Mixxx is distributed under the GNU
GPL version 2 or, at your option, any later version; its complete license and
third-party notices are in the upstream
[`LICENSE`](https://github.com/mixxxdj/mixxx/blob/86126792a3a11b493a74ea133dc1260890d9c200/LICENSE)
file. The exact source and inspiration revisions are recorded in `SOURCES.md`.
