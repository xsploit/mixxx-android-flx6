# Experimental Mixxx Android build

- Start with `ANDROID-HARDWARE-TEST.md` for installation, FLX6 wiring, and the
  exact hardware test sequence.
- `scripts/build-mixxx-android.sh` reproduces the signed ARM64 APK from the
  prepared WSL build environment.
- `scripts/verify-mixxx-android.sh` inspects package metadata, signature, and
  native libraries.
- `patches/mixxx-android-wsl.patch` permits only the Android cross-build through
  Mixxx's WSL guard; it does not enable unsupported WSL desktop builds.

The APK is a development artifact, not an official Mixxx release. The source
build succeeds, but live Android and DDJ-FLX6 behavior must be verified on the
target device.

## Corresponding source and licensing

The APK was built from the Mixxx source at commit
[`86126792a3a11b493a74ea133dc1260890d9c200`](https://github.com/mixxxdj/mixxx/commit/86126792a3a11b493a74ea133dc1260890d9c200)
with only `patches/mixxx-android-wsl.patch` applied. Mixxx is distributed under
the GNU GPL version 2 or, at your option, any later version; its complete
license and third-party notices are in the upstream
[`LICENSE`](https://github.com/mixxxdj/mixxx/blob/86126792a3a11b493a74ea133dc1260890d9c200/LICENSE)
file. The exact upstream source archive is available from the commit page, and
this repository contains the build script and complete local source change.
