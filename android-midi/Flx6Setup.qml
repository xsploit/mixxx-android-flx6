import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Mixxx 1.0 as Mixxx
import ".." as Skin
import "../Theme"

Category {
    id: root

    property string controllerStatus: "Checking controller..."
    property string audioStatus: "Checking audio..."

    function refresh() {
        controllerStatus = Mixxx.ControllerManager.flx6Status();
        audioStatus = Mixxx.SoundManager.flx6AudioStatus();
    }

    function save() {}
    function load() { refresh(); }

    label: "FLX6 Setup"

    Component.onCompleted: refresh()
    onActivated: {
        refresh();
        if (audioStatus.indexOf("Ready") !== 0)
            audioStatus = Mixxx.SoundManager.autoConfigureFlx6();
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 14

        Text {
            Layout.fillWidth: true
            color: Theme.white
            font.bold: true
            font.pixelSize: 24
            text: "DDJ-FLX6 connection"
        }
        Text {
            Layout.fillWidth: true
            color: Theme.midGray
            font.pixelSize: 14
            text: "Plug in the controller before opening Mixxx. The app loads the mapping and routes Master + headphones automatically."
            wrapMode: Text.WordWrap
        }
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 78
            color: Theme.darkGray3
            radius: 8
            Column {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 7
                Text { color: Theme.white; font.bold: true; text: "CONTROLS" }
                Text { color: root.controllerStatus.indexOf("Ready") === 0 ? "#63e681" : "#ffcf5a"; text: root.controllerStatus }
            }
        }
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 78
            color: Theme.darkGray3
            radius: 8
            Column {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 7
                Text { color: Theme.white; font.bold: true; text: "AUDIO" }
                Text { color: root.audioStatus.indexOf("Ready") === 0 ? "#63e681" : "#ffcf5a"; text: root.audioStatus }
            }
        }
        Skin.FormButton {
            Layout.preferredHeight: 48
            Layout.fillWidth: true
            activeColor: Theme.accentColor
            text: "CHECK AND SET UP FLX6"
            onPressed: {
                root.controllerStatus = Mixxx.ControllerManager.flx6Status();
                root.audioStatus = Mixxx.SoundManager.autoConfigureFlx6();
            }
        }
        Text {
            Layout.fillWidth: true
            color: Theme.midGray
            font.pixelSize: 12
            text: "If Controls says not detected, leave the cable connected and reopen the app. No controller utility mode is required."
            wrapMode: Text.WordWrap
        }
        Item { Layout.fillHeight: true }
    }
}
