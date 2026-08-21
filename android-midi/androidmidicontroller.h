#pragma once

#include <QByteArray>
#include <QList>
#include <QMutex>
#include <QSet>

#include "controllers/midi/midicontroller.h"

class AndroidMidiController final : public MidiController {
    Q_OBJECT
  public:
    struct DeviceInfo {
        int id{-1};
        int inputPortCount{0};
        int outputPortCount{0};
        QString name;
    };

    explicit AndroidMidiController(DeviceInfo info);
    ~AndroidMidiController() override;

    static QList<DeviceInfo> listDevices();
    static void dispatchMidi(
            qint64 nativeHandle, const QByteArray& data, qint64 timestampNanos);

    PhysicalTransportProtocol getPhysicalTransportProtocol() const override {
        return PhysicalTransportProtocol::USB;
    }
    QString getVendorString() const override {
        return QStringLiteral("AlphaTheta / Pioneer DJ");
    }
    QString getProductString() const override {
        return m_info.name;
    }
    std::optional<uint16_t> getVendorId() const override {
        return std::nullopt;
    }
    std::optional<uint16_t> getProductId() const override {
        return std::nullopt;
    }
    QString getSerialNumber() const override {
        return QString();
    }
    std::optional<uint8_t> getUsbInterfaceNumber() const override {
        return std::nullopt;
    }

  protected:
    void sendShortMsg(unsigned char status,
            unsigned char byte1,
            unsigned char byte2) override;

  private:
    int open(const QString& resourcePath) override;
    int close() override;
    bool sendBytes(const QByteArray& data) override;
    bool isPolling() const override {
        return false;
    }
    void processMidi(const QByteArray& data, qint64 timestampNanos);
    int expectedMessageSize(unsigned char status) const;

    DeviceInfo m_info;
    unsigned char m_runningStatus{0};
    bool m_inSysex{false};
    QByteArray m_pending;

    static QMutex s_instanceMutex;
    static QSet<AndroidMidiController*> s_instances;
};
