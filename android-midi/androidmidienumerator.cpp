#include "controllers/midi/androidmidienumerator.h"

#include "controllers/midi/androidmidicontroller.h"
#include "moc_androidmidienumerator.cpp"

AndroidMidiEnumerator::~AndroidMidiEnumerator() {
    qDeleteAll(m_devices);
}

QList<Controller*> AndroidMidiEnumerator::queryDevices() {
    qDeleteAll(m_devices);
    m_devices.clear();
    for (auto info : AndroidMidiController::listDevices()) {
        // Output ports are data flowing out of the hardware and into Mixxx.
        // Ignore devices that cannot control the application.
        if (info.outputPortCount <= 0) {
            continue;
        }
        m_devices.append(new AndroidMidiController(std::move(info)));
    }
    return m_devices;
}
