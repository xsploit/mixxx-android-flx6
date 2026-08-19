# Mixxx Android FLX6 phone preview

- Start with `ANDROID-HARDWARE-TEST.md` for installation, FLX6 wiring, and the
  exact hardware test sequence.
- `scripts/build-mixxx-android.sh` reproduces the signed ARM64 APK from the
  prepared WSL build environment.
- `scripts/verify-mixxx-android.sh` inspects package metadata, signature, and
  native libraries.
- `patches/mixxx-android-wsl.patch` permits only the Android cross-build through
  Mixxx's WSL guard; it does not enable unsupported WSL desktop builds.
- `patches/mixxx-android-phone-ui.patch` adds the responsive phone layout,
  always-visible library/settings controls, and 30 FPS Android UI target.
- `controller-mapping/` contains the bundled experimental DDJ-FLX6 mapping and
  its upstream license.

The APK is a development artifact, not an official Mixxx release. The source
build and static APK checks succeed, but live Android USB audio, mapping
accuracy, touch layout, and DDJ-FLX6 behavior must be verified on the target
device.

## Phone layout

- Performance view: two vertically stacked moving waveforms, compact deck/track
  information, and a small library area.
- `LIBRARY`: full-screen browser. Select a track and use `LOAD 1` or `LOAD 2`.
- `SETTINGS`: maximized preferences dialog for library folders, sound hardware,
  and controller configuration.
- Desktop mixer/effects/sampler controls are hidden below the phone breakpoint;
  the connected FLX6 provides those physical controls.

## Corresponding source and licensing

The APK was built from the Mixxx source at commit
[`86126792a3a11b493a74ea133dc1260890d9c200`](https://github.com/mixxxdj/mixxx/commit/86126792a3a11b493a74ea133dc1260890d9c200)
with the two repository patches applied. Mixxx is distributed under the GNU
GPL version 2 or, at your option, any later version; its complete license and
third-party notices are in the upstream
[`LICENSE`](https://github.com/mixxxdj/mixxx/blob/86126792a3a11b493a74ea133dc1260890d9c200/LICENSE)
file. The exact source and inspiration revisions are recorded in `SOURCES.md`.
