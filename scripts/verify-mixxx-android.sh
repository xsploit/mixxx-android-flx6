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
"$aapt" dump badging "$apk" | grep "package: name='org.mixxx.flx6standalone' versionCode='23' versionName='0.23.0-simple-sound-menu'" >/dev/null
"$aapt" dump badging "$apk" | grep "application-label:'Mixxx FLX6 v0.23'" >/dev/null
"$aapt" dump badging "$apk" | grep "launchable-activity: name='org.mixxx.MainActivity'" >/dev/null
echo "== Signature =="
"$apksigner" verify --verbose --print-certs "$apk"
echo "== Selected ARM64 native libraries =="
unzip -l "$apk" | grep -E 'lib/arm64-v8a/(libmixxx|libQt6Core|libc\+\+_shared)'
echo "== Phone UI resources =="
unzip -l "$apk" | grep -E 'assets/qml/(main.qml|Deck.qml|WaveformDisplay.qml|Library.qml|Library/TrackList.qml|Settings.qml|Settings/Flx6Setup.qml)'
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
unzip -p "$apk" assets/qml/main.qml | grep 'parent.SafeArea.margins.bottom' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'id: waveformContent' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'property real waveformStackPosition: 1.0' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'Mixxx.SoundManager.autoConfigureFlx6()' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'property real waveformDrawScale: 1.0' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'property real deckADrawPosition: 0.5' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'property real deckBDrawPosition: 0.5' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'readonly property int waveformTopGuard: compactScreen ? 5 : 0' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'readonly property real waveformViewportTop: performanceDeckHeaders.height + waveformTopGuard' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'readonly property real measuredHeight: Math.max(performanceDeck1.implicitHeight,' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'height: root.compactScreen ? Math.ceil(measuredHeight) : 0' >/dev/null
if unzip -p "$apk" assets/qml/main.qml | grep -q 'performanceHeaderHeight'; then
    echo "Fixed performance header height is still packaged" >&2
    exit 1
fi
unzip -p "$apk" assets/qml/Deck.qml | grep 'readonly property int layoutMargin: 4' >/dev/null
unzip -p "$apk" assets/qml/Deck.qml | grep 'readonly property real measuredContentHeight: minimized' >/dev/null
unzip -p "$apk" assets/qml/Deck.qml | grep 'minimizedGrid.implicitHeight + layoutMargin \* 2' >/dev/null
unzip -p "$apk" assets/qml/Deck.qml | grep 'implicitHeight: Math.ceil(measuredContentHeight)' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'readonly property int waveformDividerThickness: 2' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'readonly property int waveformLanePadding: compactScreen ? 1 : 0' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'text: "Draw -"' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'text: "Draw +"' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'id: waveformDrawPinch' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'gestureStartScale \* activeScale' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'text: root.editDeck ? "↕" : "•"' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'height: 12' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'width: 28' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'anchors.fill: parent' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'Math.floor((parent.height - root.waveformDividerThickness) / 2)' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'y: upperWaveformPane.height + root.waveformDividerThickness' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'id: performanceDeckHeaderMask' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'height: Math.max(0, parent.height - root.waveformViewportTop)' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'y: root.waveformViewportTop' >/dev/null
test "$(unzip -p "$apk" assets/qml/main.qml | grep -c 'topMargin: root.waveformTopGuard')" -eq 2
unzip -p "$apk" assets/qml/main.qml | grep 'verticalTravel: Math.min(72, height \* 0.18)' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'function updateStackPosition(pointer)' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep -- '-desiredY / waveformStack.verticalTravel' >/dev/null
if unzip -p "$apk" assets/qml/main.qml | grep -q 'minimumHeight: 320'; then
    echo "Obsolete 320-pixel minimum height is still packaged" >&2
    exit 1
fi
unzip -p "$apk" assets/qml/main.qml | grep 'id: upperWaveformPane' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'id: lowerWaveformPane' >/dev/null
unzip -p "$apk" assets/qml/WaveformDisplay.qml | grep 'property real verticalDrawScale: 1.0' >/dev/null
unzip -p "$apk" assets/qml/WaveformDisplay.qml | grep 'property real verticalDrawPosition: 0.5' >/dev/null
unzip -p "$apk" assets/qml/WaveformDisplay.qml | grep 'readonly property real verticalDrawCenter: nativeWaveform.y + nativeWaveform.height / 2' >/dev/null
unzip -p "$apk" assets/qml/WaveformDisplay.qml | grep 'id: nativeWaveform' >/dev/null
unzip -p "$apk" assets/qml/WaveformDisplay.qml | grep 'height: parent.height \* root.verticalDrawScale' >/dev/null
unzip -p "$apk" assets/qml/WaveformDisplay.qml | grep 'y: (parent.height - height) \* Math.max(0, Math.min(1, root.verticalDrawPosition))' >/dev/null
unzip -p "$apk" assets/qml/WaveformDisplay.qml | grep 'gainAll: 1.0' >/dev/null
unzip -p "$apk" assets/qml/WaveformDisplay.qml | grep 'gainAll: root.splitStemTracks ? 2.0 : 1.0' >/dev/null
if unzip -p "$apk" assets/qml/main.qml assets/qml/WaveformDisplay.qml | grep -q 'waveformVisualGain\|visualGain:'; then
    echo "Obsolete waveform visual-gain control is still packaged" >&2
    exit 1
fi
test "$(unzip -p "$apk" assets/qml/main.qml | grep -c 'verticalDrawPosition: root.deckADrawPosition')" -eq 2
test "$(unzip -p "$apk" assets/qml/main.qml | grep -c 'verticalDrawPosition: root.deckBDrawPosition')" -eq 2
unzip -p "$apk" assets/qml/main.qml | grep 'id: deckALabel' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'id: deckBLabel' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'deck1waveform.verticalDrawCenter - height / 2' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'deck2waveform.verticalDrawCenter - height / 2' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'root.deckADrawPosition = travel > 0' >/dev/null
unzip -p "$apk" assets/qml/main.qml | grep 'root.deckBDrawPosition = travel > 0' >/dev/null
test "$(unzip -p "$apk" assets/qml/main.qml | grep -c 'property real grabOffsetY: 0')" -eq 2
unzip -p "$apk" assets/qml/main.qml | grep 'active: root.maximizeLibrary || (!root.compactScreen' >/dev/null
unzip -p "$apk" assets/qml/Library/TrackList.qml | grep 'text: "Load 1"' >/dev/null
unzip -p "$apk" assets/qml/Library/TrackList.qml | grep 'text: "Load 2"' >/dev/null
unzip -p "$apk" assets/qml/Settings.qml | grep 'text: "Close"' >/dev/null
unzip -p "$apk" assets/qml/Settings.qml | grep 'Settings.Flx6Setup' >/dev/null
unzip -p "$apk" assets/qml/Settings/Flx6Setup.qml | grep 'SET UP MASTER + HEADPHONES' >/dev/null
unzip -p "$apk" assets/qml/Settings/SoundHardware.qml | grep 'AUTO SET UP FLX6' >/dev/null
unzip -p "$apk" assets/qml/Settings/SoundHardware.qml | grep 'Headphones / PFL device' >/dev/null
unzip -p "$apk" assets/qml/Settings/SoundHardware.qml | grep 'TEST CUE: DECK 1' >/dev/null
unzip -p "$apk" assets/qml/Settings/SoundHardware.qml | grep 'root.applyManualRouting()' >/dev/null
unzip -p "$apk" assets/qml/Settings/Flx6Setup.qml | grep 'Mixxx.ControllerManager.flx6Status()' >/dev/null
unzip -p "$apk" assets/qml/Settings/Flx6Setup.qml | grep 'Mixxx.SoundManager.autoConfigureFlx6()' >/dev/null
unzip -p "$apk" assets/qml/Settings/Library.qml | grep 'text: qsTr("Downloads")' >/dev/null
unzip -p "$apk" assets/qml/Settings/Library.qml | grep 'text: qsTr("Add path")' >/dev/null
unzip -p "$apk" assets/qml/Settings/Library.qml | grep 'Mixxx.Library.requestAndroidAllFilesAccess()' >/dev/null
echo "== Experimental FLX6 mapping =="
unzip -l "$apk" | grep -E 'assets/controllers/Pioneer-DDJ-FLX6(-script.js|.midi.xml)'
unzip -p "$apk" assets/controllers/Pioneer-DDJ-FLX6.midi.xml | grep 'BROWSE - press - Toggle full-screen library' >/dev/null
