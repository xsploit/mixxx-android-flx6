#include "controllers/midi/androidmidicontroller.h"

#include <QtCore/private/qandroidextras_p.h>

#include <QJniEnvironment>
#include <QJniObject>

#include "moc_androidmidicontroller.cpp"

QMutex AndroidMidiController::s_instanceMutex;
QSet<AndroidMidiController*> AndroidMidiController::s_instances;

AndroidMidiController::AndroidMidiController(DeviceInfo info)
        : MidiController(info.name),
          m_info(std::move(info)) {
    // Android names ports from the app's point of view. Device output ports
    // carry knob/button data into Mixxx; device input ports receive LED data.
    setInputDevice(m_info.outputPortCount > 0);
    setOutputDevice(m_info.inputPortCount > 0);
    QMutexLocker locker(&s_instanceMutex);
    s_instances.insert(this);
}

AndroidMidiController::~AndroidMidiController() {
    if (isOpen()) {
        close();
    }
    QMutexLocker locker(&s_instanceMutex);
    s_instances.remove(this);
}

QList<AndroidMidiController::DeviceInfo> AndroidMidiController::listDevices() {
    const QJniObject context = QNativeInterface::QAndroidApplication::context();
    const QJniObject encoded = QJniObject::callStaticObjectMethod(
            "org/mixxx/MidiBridge",
            "listDevices",
            "(Landroid/content/Context;)Ljava/lang/String;",
            context.object<jobject>());
    QList<DeviceInfo> result;
    const QString text = encoded.toString();
    for (const QString& line : text.split(QChar('\n'), Qt::SkipEmptyParts)) {
        const QStringList fields = line.split(QChar('\t'));
        if (fields.size() < 4) {
            continue;
        }
        bool idOk = false;
        bool inputOk = false;
        bool outputOk = false;
        DeviceInfo info;
        info.id = fields.at(0).toInt(&idOk);
        info.inputPortCount = fields.at(1).toInt(&inputOk);
        info.outputPortCount = fields.at(2).toInt(&outputOk);
        info.name = fields.mid(3).join(QStringLiteral(" ")).trimmed();
        if (idOk && inputOk && outputOk && !info.name.isEmpty()) {
            result.append(std::move(info));
        }
    }
    return result;
}

int AndroidMidiController::open(const QString& resourcePath) {
    if (isOpen()) {
        return 0;
    }
    const QJniObject context = QNativeInterface::QAndroidApplication::context();
    const bool opened = QJniObject::callStaticMethod<jboolean>(
            "org/mixxx/MidiBridge",
            "open",
            "(Landroid/content/Context;IJ)Z",
            context.object<jobject>(),
            static_cast<jint>(m_info.id),
            static_cast<jlong>(reinterpret_cast<quintptr>(this)));
    if (!opened) {
        qCWarning(m_logBase) << "Android could not open MIDI device" << getName();
        return -1;
    }
    startEngine();
    if (!applyMapping(resourcePath)) {
        stopEngine();
        QJniObject::callStaticMethod<void>("org/mixxx/MidiBridge",
                "close",
                "(J)V",
                static_cast<jlong>(reinterpret_cast<quintptr>(this)));
        return -2;
    }
    setOpen(true);
    qCInfo(m_logBase) << "Android MIDI ready:" << getName();
    return 0;
}

int AndroidMidiController::close() {
    if (!isOpen()) {
        return 0;
    }
    QJniObject::callStaticMethod<void>("org/mixxx/MidiBridge",
            "close",
            "(J)V",
            static_cast<jlong>(reinterpret_cast<quintptr>(this)));
    stopEngine();
    MidiController::close();
    setOpen(false);
    return 0;
}

void AndroidMidiController::sendShortMsg(
        unsigned char status, unsigned char byte1, unsigned char byte2) {
    QByteArray message;
    message.append(static_cast<char>(status));
    message.append(static_cast<char>(byte1));
    message.append(static_cast<char>(byte2));
    sendBytes(message);
}

bool AndroidMidiController::sendBytes(const QByteArray& data) {
    QJniEnvironment env;
    jbyteArray bytes = env->NewByteArray(data.size());
    if (!bytes) {
        return false;
    }
    env->SetByteArrayRegion(bytes,
            0,
            data.size(),
            reinterpret_cast<const jbyte*>(data.constData()));
    const bool sent = QJniObject::callStaticMethod<jboolean>(
            "org/mixxx/MidiBridge",
            "send",
            "(J[B)Z",
            static_cast<jlong>(reinterpret_cast<quintptr>(this)),
            bytes);
    env->DeleteLocalRef(bytes);
    return sent;
}

int AndroidMidiController::expectedMessageSize(unsigned char status) const {
    if (status < 0x80) {
        return 0;
    }
    if (status < 0xF0) {
        const unsigned char command = status & 0xF0;
        return command == 0xC0 || command == 0xD0 ? 2 : 3;
    }
    switch (status) {
    case 0xF1:
    case 0xF3:
        return 2;
    case 0xF2:
        return 3;
    default:
        return 1;
    }
}

void AndroidMidiController::processMidi(
        const QByteArray& data, qint64 timestampNanos) {
    const mixxx::Duration timestamp = mixxx::Duration::fromNanos(timestampNanos);
    for (const char raw : data) {
        const auto byte = static_cast<unsigned char>(raw);
        if (byte >= 0xF8) {
            receivedShortMessage(byte, 0, 0, timestamp);
            continue;
        }
        if (m_inSysex) {
            if (byte == 0xF7) {
                m_inSysex = false;
            }
            continue;
        }
        if (byte == 0xF0) {
            m_inSysex = true;
            m_pending.clear();
            continue;
        }
        if (byte & 0x80) {
            m_pending.clear();
            m_pending.append(static_cast<char>(byte));
            m_runningStatus = byte < 0xF0 ? byte : 0;
        } else {
            if (m_pending.isEmpty()) {
                if (!m_runningStatus) {
                    continue;
                }
                m_pending.append(static_cast<char>(m_runningStatus));
            }
            m_pending.append(static_cast<char>(byte));
        }

        const int expected = m_pending.isEmpty()
                ? 0
                : expectedMessageSize(static_cast<unsigned char>(m_pending.at(0)));
        if (expected > 0 && m_pending.size() >= expected) {
            const auto status = static_cast<unsigned char>(m_pending.at(0));
            const auto control = expected > 1
                    ? static_cast<unsigned char>(m_pending.at(1))
                    : 0;
            const auto value = expected > 2
                    ? static_cast<unsigned char>(m_pending.at(2))
                    : 0;
            receivedShortMessage(status, control, value, timestamp);
            m_pending.clear();
        }
    }
}

void AndroidMidiController::dispatchMidi(
        qint64 nativeHandle, const QByteArray& data, qint64 timestampNanos) {
    auto* controller = reinterpret_cast<AndroidMidiController*>(
            static_cast<quintptr>(nativeHandle));
    {
        QMutexLocker locker(&s_instanceMutex);
        if (!s_instances.contains(controller)) {
            return;
        }
    }
    QMetaObject::invokeMethod(controller, [controller, data, timestampNanos]() { controller->processMidi(data, timestampNanos); }, Qt::QueuedConnection);
}

extern "C" JNIEXPORT void JNICALL
Java_org_mixxx_MidiBridge_nativeOnMidi(JNIEnv* env,
        jclass,
        jlong nativeHandle,
        jbyteArray bytes,
        jint offset,
        jint count,
        jlong timestamp) {
    if (!bytes || count <= 0) {
        return;
    }
    QByteArray data(count, Qt::Uninitialized);
    env->GetByteArrayRegion(bytes,
            offset,
            count,
            reinterpret_cast<jbyte*>(data.data()));
    AndroidMidiController::dispatchMidi(nativeHandle, data, timestamp);
}
