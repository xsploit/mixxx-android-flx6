import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Mixxx 1.0 as Mixxx
import ".." as Skin
import "../Theme"

Category {
    id: root

    property bool committing: false
    property bool loading: false
    property var outputDevices: []
    property var sampleRates: []
    property string statusText: "Ready"

    function indexOfValue(values, value) {
        for (let i = 0; i < values.length; ++i) {
            if (values[i] === value)
                return i;
        }
        return -1;
    }

    function channelLabels(device) {
        let labels = [];
        if (!device)
            return labels;
        for (let channel = 0; channel + 1 < device.channelCount; channel += 2)
            labels.push(qsTr("USB %1 / %2").arg(channel + 1).arg(channel + 2));
        return labels;
    }

    function updateMainChannels(preferredIndex) {
        const device = outputDevices[mainDevice.currentIndex];
        mainChannels.model = channelLabels(device);
        mainChannels.currentIndex = Math.max(0,
                Math.min(preferredIndex ?? 0, mainChannels.count - 1));
    }

    function updateHeadphoneChannels(preferredIndex) {
        const deviceIndex = headphoneDevice.currentIndex - 1;
        const device = deviceIndex >= 0 ? outputDevices[deviceIndex] : null;
        headphoneChannels.model = channelLabels(device);
        headphoneChannels.currentIndex = Math.max(0,
                Math.min(preferredIndex ?? 0, headphoneChannels.count - 1));
        headphoneChannels.enabled = !!device;
    }

    function updateSampleRates(api, preferredRate) {
        let rates = Mixxx.SoundManager.getSampleRates(api);
        if (!rates.length)
            rates = [44100, 48000];
        sampleRates = rates;
        let labels = [];
        for (const rate of rates)
            labels.push(qsTr("%1 Hz").arg(rate));
        sampleRate.model = labels;
        let rateIndex = indexOfValue(rates, preferredRate);
        sampleRate.currentIndex = rateIndex >= 0 ? rateIndex : 0;
        updateBufferLabels();
    }

    function updateBufferLabels() {
        const rate = sampleRates[sampleRate.currentIndex] || 48000;
        let labels = [];
        let frames = 1;
        while (frames / rate * 1000 < 1.0)
            frames *= 2;
        for (let i = 0; i < 7; ++i) {
            labels.push(qsTr("%1 ms").arg((frames / rate * 1000).toFixed(1)));
            frames *= 2;
        }
        const previous = audioBuffer.currentIndex;
        audioBuffer.model = labels;
        audioBuffer.currentIndex = Math.max(0, Math.min(previous, labels.length - 1));
    }

    function updateDevices(api, preserveSelection) {
        const oldMainName = preserveSelection && outputDevices[mainDevice.currentIndex]
                ? outputDevices[mainDevice.currentIndex].displayName : "";
        const oldHeadIndex = headphoneDevice.currentIndex - 1;
        const oldHeadName = preserveSelection && outputDevices[oldHeadIndex]
                ? outputDevices[oldHeadIndex].displayName : "";
        outputDevices = Mixxx.SoundManager.availableOutputDevices(api);

        let names = [];
        for (const device of outputDevices)
            names.push(qsTr("%1  (%2 ch)").arg(device.displayName).arg(device.channelCount));
        mainDevice.model = names.length ? names : [qsTr("No output devices")];
        headphoneDevice.model = [qsTr("Off")].concat(names);

        let mainIndex = 0;
        let headIndex = 0;
        if (oldMainName || oldHeadName) {
            for (let i = 0; i < outputDevices.length; ++i) {
                if (outputDevices[i].displayName === oldMainName)
                    mainIndex = i;
                if (outputDevices[i].displayName === oldHeadName)
                    headIndex = i + 1;
            }
        }
        mainDevice.currentIndex = mainIndex;
        headphoneDevice.currentIndex = headIndex;
        updateMainChannels(0);
        updateHeadphoneChannels(0);
    }

    function load() {
        loading = true;
        const manager = Mixxx.SoundManager;
        const apis = manager.getHostAPIList();
        soundApi.model = apis;
        let apiIndex = indexOfValue(apis, manager.getAPI());
        soundApi.currentIndex = apiIndex >= 0 ? apiIndex : 0;
        const api = soundApi.currentText;
        updateDevices(api, false);

        let mainDeviceIndex = 0;
        let mainPair = 0;
        let headDeviceIndex = -1;
        let headPair = 0;
        for (let i = 0; i < outputDevices.length; ++i) {
            const connections = outputDevices[i].connections(manager);
            for (const connection of connections) {
                if (connection.type === 0) {
                    mainDeviceIndex = i;
                    mainPair = Math.floor(connection.channelGroup / 2);
                } else if (connection.type === 1) {
                    headDeviceIndex = i;
                    headPair = Math.floor(connection.channelGroup / 2);
                }
            }
        }
        mainDevice.currentIndex = mainDeviceIndex;
        updateMainChannels(mainPair);
        headphoneDevice.currentIndex = headDeviceIndex + 1;
        updateHeadphoneChannels(headPair);
        updateSampleRates(api, manager.getSampleRate());
        audioBuffer.currentIndex = Math.max(0,
                Math.min(manager.getAudioBufferSizeIndex() - 1, 6));
        mainMix.checked = mainEnabled.value > 0;
        statusText = manager.flx6AudioStatus();
        loading = false;
    }

    function save() {
        applyManualRouting();
    }

    function applyManualRouting() {
        if (!outputDevices.length) {
            statusText = qsTr("No output device is available for this API");
            return;
        }
        const manager = Mixxx.SoundManager;
        manager.setAPI(soundApi.currentText);
        manager.setSampleRate(sampleRates[sampleRate.currentIndex] || 48000);
        manager.setAudioBufferSizeIndex(audioBuffer.currentIndex + 1);
        manager.clearOutputs();
        manager.addOutput(outputDevices[mainDevice.currentIndex],
                0, mainChannels.currentIndex * 2, 0);
        const headphoneIndex = headphoneDevice.currentIndex - 1;
        if (headphoneIndex >= 0) {
            manager.addOutput(outputDevices[headphoneIndex],
                    1, headphoneChannels.currentIndex * 2, 0);
        }
        mainEnabled.value = mainMix.checked ? 1 : 0;
        committing = true;
        statusText = qsTr("Applying audio settings...");
        manager.commit();
    }

    label: "Sound hardware"
    Component.onCompleted: load()
    onActivated: load()

    Mixxx.ControlProxy {
        id: mainEnabled
        group: "[Master]"
        key: "enabled"
    }
    Mixxx.ControlProxy {
        id: deck1Pfl
        group: "[Channel1]"
        key: "pfl"
    }

    ScrollView {
        anchors.fill: parent
        clip: true

        ColumnLayout {
            width: Math.max(560, parent.width)
            spacing: 12

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 76
                color: Theme.darkGray3
                radius: 8

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 12

                    ColumnLayout {
                        Layout.fillWidth: true
                        Text {
                            color: Theme.white
                            font.bold: true
                            font.pixelSize: 17
                            text: "DDJ-FLX6 automatic routing"
                        }
                        Text {
                            Layout.fillWidth: true
                            color: root.statusText.indexOf("Ready") === 0 ? "#63e681" : "#ffcf5a"
                            elide: Text.ElideRight
                            font.pixelSize: 13
                            text: root.statusText
                        }
                    }
                    Skin.FormButton {
                        Layout.preferredHeight: 44
                        Layout.preferredWidth: 210
                        activeColor: Theme.accentColor
                        enabled: !root.committing
                        text: "AUTO SET UP FLX6"
                        onPressed: {
                            root.statusText = Mixxx.SoundManager.autoConfigureFlx6();
                            root.committing = root.statusText.indexOf("Ready") === 0;
                        }
                    }
                }
            }

            GridLayout {
                Layout.fillWidth: true
                columns: 2
                columnSpacing: 18
                rowSpacing: 8

                Text { color: Theme.white; text: "Audio API" }
                Skin.ComboBox {
                    id: soundApi
                    Layout.fillWidth: true
                    Layout.preferredHeight: 42
                    font.pixelSize: 14
                    onActivated: {
                        if (!root.loading) {
                            root.updateDevices(currentText, false);
                            root.updateSampleRates(currentText, 48000);
                        }
                    }
                }

                Text { color: Theme.white; text: "Master device" }
                Skin.ComboBox {
                    id: mainDevice
                    Layout.fillWidth: true
                    Layout.preferredHeight: 42
                    font.pixelSize: 14
                    onActivated: root.updateMainChannels(0)
                }

                Text { color: Theme.white; text: "Master channels" }
                Skin.ComboBox {
                    id: mainChannels
                    Layout.fillWidth: true
                    Layout.preferredHeight: 42
                    font.pixelSize: 14
                }

                Text { color: Theme.white; text: "Headphones / PFL device" }
                Skin.ComboBox {
                    id: headphoneDevice
                    Layout.fillWidth: true
                    Layout.preferredHeight: 42
                    font.pixelSize: 14
                    onActivated: root.updateHeadphoneChannels(0)
                }

                Text { color: Theme.white; text: "Headphones / PFL channels" }
                Skin.ComboBox {
                    id: headphoneChannels
                    Layout.fillWidth: true
                    Layout.preferredHeight: 42
                    font.pixelSize: 14
                    opacity: enabled ? 1.0 : 0.45
                }

                Text { color: Theme.white; text: "Sample rate" }
                Skin.ComboBox {
                    id: sampleRate
                    Layout.fillWidth: true
                    Layout.preferredHeight: 42
                    font.pixelSize: 14
                    onActivated: root.updateBufferLabels()
                }

                Text { color: Theme.white; text: "Audio buffer" }
                Skin.ComboBox {
                    id: audioBuffer
                    Layout.fillWidth: true
                    Layout.preferredHeight: 42
                    font.pixelSize: 14
                }

                Text { color: Theme.white; text: "Main mix" }
                CheckBox {
                    id: mainMix
                    checked: true
                    text: checked ? "On" : "Off"
                    contentItem: Text {
                        color: Theme.white
                        leftPadding: mainMix.indicator.width + mainMix.spacing
                        text: mainMix.text
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                Skin.FormButton {
                    Layout.preferredHeight: 46
                    Layout.preferredWidth: 130
                    activeColor: Theme.midGray
                    enabled: !root.committing
                    text: "REFRESH"
                    onPressed: root.load()
                }
                Skin.FormButton {
                    Layout.preferredHeight: 46
                    Layout.preferredWidth: 185
                    activeColor: deck1Pfl.value ? "#d78a21" : Theme.midGray
                    enabled: !root.committing
                    text: deck1Pfl.value ? "DECK 1 CUE: ON" : "TEST CUE: DECK 1"
                    onPressed: deck1Pfl.value = deck1Pfl.value ? 0 : 1
                }
                Item { Layout.fillWidth: true }
                Skin.FormButton {
                    Layout.preferredHeight: 46
                    Layout.preferredWidth: 170
                    activeColor: Theme.accentColor
                    enabled: !root.committing
                    text: root.committing ? "APPLYING..." : "APPLY"
                    onPressed: root.applyManualRouting()
                }
            }

            Text {
                Layout.fillWidth: true
                color: Theme.midGray
                font.pixelSize: 12
                text: "Headphone test uses Deck 1 PFL. Load and play a track, then use the FLX6 HEADPHONES MIX and LEVEL knobs. Connect new USB hardware before opening Mixxx."
                wrapMode: Text.WordWrap
            }
        }
    }

    Connections {
        target: Mixxx.SoundManager
        function onCommitted(error) {
            root.committing = false;
            root.statusText = error ? error : qsTr("Ready - settings applied");
            if (!error)
                root.load();
        }
    }
}
