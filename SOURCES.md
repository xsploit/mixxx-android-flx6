# Source provenance

## Mixxx

- Repository: https://github.com/mixxxdj/mixxx
- Commit: `86126792a3a11b493a74ea133dc1260890d9c200`
- Local changes: `patches/mixxx-android-wsl.patch`,
  `patches/mixxx-android-phone-ui.patch`,
  `patches/mixxx-android-v0.3-version.patch`,
  `patches/mixxx-android-active-phone-ui.patch`,
  `patches/mixxx-android-v0.4-performance-view.patch`,
  `patches/mixxx-android-v0.5-version.patch`, and
  `patches/mixxx-android-v0.5-waveform-fix.patch`
- License: GNU GPL v2 or later; see the upstream `LICENSE` file.

## Standalone/touchscreen layout references

- Fayaaz Mixxx Pi image: https://github.com/fayaaz/mixxx-pi-gen at
  `e5e11fc6f5ec9ffe99168c19c37527869cb524bf`. Its configuration supplied the
  stacked-waveform, two-deck, 30 FPS, and small-screen baseline.
- EmperorJack Mixxx Pi config: https://github.com/EmperorJack/mixxx-pi-config at
  `9b11abeec32bf8ef806f5b61f636055164ec1434`. Its instructions supplied the
  compact-deck, hidden-mixer, full-screen-library, and touch menu ideas.

These projects configure desktop Linux. No Pi filesystem or window-manager code
was copied into the Android APK; their proven layout choices were implemented in
Mixxx's existing QML Android interface.

## Experimental DDJ-FLX6 mapping

- Source: https://github.com/rayocta303/UNX-DJ-ENGINE/tree/cd8fdd68d9470795875026ace6c70627faf0d2a8/controllers
- Commit: `cd8fdd68d9470795875026ace6c70627faf0d2a8`
- Vendored files: `controller-mapping/Pioneer-DDJ-FLX6.midi.xml` and
  `controller-mapping/Pioneer-DDJ-FLX6-script.js`
- License: MIT; preserved in `controller-mapping/UNX-DJ-ENGINE-LICENSE.txt`.

The mapping parses as XML and JavaScript, contains 558 controls, and all 37
referenced `PioneerDDJFLX6` script bindings exist. Those checks do not replace a
physical controller test.
