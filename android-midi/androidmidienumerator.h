#pragma once

#include "controllers/midi/midienumerator.h"

class AndroidMidiEnumerator final : public MidiEnumerator {
    Q_OBJECT
  public:
    AndroidMidiEnumerator() = default;
    ~AndroidMidiEnumerator() override;
    QList<Controller*> queryDevices() override;

  private:
    QList<Controller*> m_devices;
};
