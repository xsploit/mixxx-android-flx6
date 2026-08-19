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
"$aapt" dump badging "$apk" | grep "package: name='org.mixxx.flx6standalone' versionCode='9' versionName='0.9.0-collapsible-toolbar'" >/dev/null
"$aapt" dump badging "$apk" | grep "application-label:'Mixxx FLX6 v0.9 NEW'" >/dev/null
"$aapt" dump badging "$apk" | grep "launchable-activity: name='org.mixxx.MainActivity'" >/dev/null
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
unzip -p "$apk" assets/qml/main.qml | grep 'id: toolbarFlick' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'id: waveformDivider' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'id: toolbarTab' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'property bool toolbarExpanded: false' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'visible: root.toolbarExpanded' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'id: upperWaveformPane' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'id: lowerWaveformPane' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'height: parent.height / 2' >/dev/null
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
