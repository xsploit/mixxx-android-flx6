#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
apk="$repo_dir/artifacts/mixxx-android-arm64.apk"
aapt="$(find /usr/lib/android-sdk/build-tools -type f -name aapt | sort -V | tail -1)"
apksigner="$(find /usr/lib/android-sdk/build-tools -type f -name apksigner | sort -V | tail -1)"

test -f "$apk"
test -n "$aapt"
test -n "$apksigner"

echo "== Package metadata =="
"$aapt" dump badging "$apk" | head -8
"$aapt" dump badging "$apk" | grep "versionCode='6' versionName='0.6.0-android-storage'" >/dev/null
echo "== Signature =="
"$apksigner" verify --verbose --print-certs "$apk"
echo "== Selected ARM64 native libraries =="
unzip -l "$apk" | grep -E 'lib/arm64-v8a/(libmixxx|libQt6Core|libc\+\+_shared)'
echo "== Phone UI resources =="
unzip -l "$apk" | grep -E 'assets/qml/(main.qml|Library.qml|Library/TrackList.qml|Settings.qml)'
unzip -p "$apk" assets/qml/main.qml | grep 'text: "4 Decks"' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'text: "Settings"' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'id: performanceDeckHeaders' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'id: waveformStack' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'text: "A"' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'text: "B"' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'active: root.maximizeLibrary || (!root.compactScreen' >/dev/null
unzip -p "$apk" assets/qml/Library/TrackList.qml | grep 'text: "Load 1"' >/dev/null
unzip -p "$apk" assets/qml/Library/TrackList.qml | grep 'text: "Load 2"' >/dev/null
unzip -p "$apk" assets/qml/Settings.qml | grep 'text: "Close"' >/dev/null
unzip -p "$apk" assets/qml/Settings/Library.qml | grep 'text: qsTr("Downloads")' >/dev/null
unzip -p "$apk" assets/qml/Settings/Library.qml | grep 'text: qsTr("Add path")' >/dev/null
unzip -p "$apk" assets/qml/Settings/Library.qml | grep 'Mixxx.Library.requestAndroidAllFilesAccess()' >/dev/null
echo "== Experimental FLX6 mapping =="
unzip -l "$apk" | grep -E 'assets/controllers/Pioneer-DDJ-FLX6(-script.js|.midi.xml)'
unzip -p "$apk" assets/controllers/Pioneer-DDJ-FLX6.midi.xml | grep 'BROWSE - press - Toggle full-screen library' >/dev/null
