package org.mixxx;

import android.content.Context;
import android.media.midi.MidiDevice;
import android.media.midi.MidiDeviceInfo;
import android.media.midi.MidiInputPort;
import android.media.midi.MidiManager;
import android.media.midi.MidiOutputPort;
import android.media.midi.MidiReceiver;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

/** Thin bridge between Android's class-compliant MIDI service and Mixxx. */
public final class MidiBridge {
    private static final String TAG = "MixxxMidiBridge";
    private static final Map<Long, Connection> CONNECTIONS = new HashMap<>();

    private MidiBridge() {}

    public static String listDevices(Context context) {
        MidiManager manager = (MidiManager) context.getSystemService(Context.MIDI_SERVICE);
        if (manager == null) {
            return "";
        }
        StringBuilder result = new StringBuilder();
        for (MidiDeviceInfo info : manager.getDevices()) {
            Bundle properties = info.getProperties();
            String name = properties.getString(MidiDeviceInfo.PROPERTY_PRODUCT);
            if (name == null || name.trim().isEmpty()) {
                name = properties.getString(MidiDeviceInfo.PROPERTY_NAME);
            }
            if (name == null || name.trim().isEmpty()) {
                name = "Android MIDI " + info.getId();
            }
            name = name.replace('\t', ' ').replace('\n', ' ').trim();
            if (result.length() > 0) {
                result.append('\n');
            }
            result.append(info.getId()).append('\t')
                    .append(info.getInputPortCount()).append('\t')
                    .append(info.getOutputPortCount()).append('\t')
                    .append(name);
        }
        return result.toString();
    }

    public static boolean open(Context context, int deviceId, long nativeHandle) {
        close(nativeHandle);
        MidiManager manager = (MidiManager) context.getSystemService(Context.MIDI_SERVICE);
        if (manager == null) {
            Log.e(TAG, "Android MIDI service is unavailable");
            return false;
        }
        MidiDeviceInfo target = null;
        for (MidiDeviceInfo info : manager.getDevices()) {
            if (info.getId() == deviceId) {
                target = info;
                break;
            }
        }
        if (target == null) {
            Log.e(TAG, "MIDI device disappeared before it could be opened: " + deviceId);
            return false;
        }

        CountDownLatch latch = new CountDownLatch(1);
        Connection[] opened = new Connection[1];
        manager.openDevice(target, device -> {
            if (device != null) {
                opened[0] = new Connection(device, nativeHandle);
            }
            latch.countDown();
        }, new Handler(Looper.getMainLooper()));

        try {
            if (!latch.await(4, TimeUnit.SECONDS) || opened[0] == null) {
                Log.e(TAG, "Timed out opening Android MIDI device " + deviceId);
                return false;
            }
        } catch (InterruptedException error) {
            Thread.currentThread().interrupt();
            return false;
        }
        synchronized (CONNECTIONS) {
            CONNECTIONS.put(nativeHandle, opened[0]);
        }
        Log.i(TAG, "Opened Android MIDI device " + deviceId);
        return true;
    }

    public static boolean send(long nativeHandle, byte[] data) {
        Connection connection;
        synchronized (CONNECTIONS) {
            connection = CONNECTIONS.get(nativeHandle);
        }
        return connection != null && connection.send(data);
    }

    public static void close(long nativeHandle) {
        Connection connection;
        synchronized (CONNECTIONS) {
            connection = CONNECTIONS.remove(nativeHandle);
        }
        if (connection != null) {
            connection.close();
        }
    }

    private static native void nativeOnMidi(
            long nativeHandle, byte[] data, int offset, int count, long timestamp);

    private static final class Connection {
        private final MidiDevice device;
        private final ArrayList<MidiInputPort> inputPorts = new ArrayList<>();
        private final ArrayList<MidiOutputPort> outputPorts = new ArrayList<>();
        private final MidiReceiver receiver;

        Connection(MidiDevice device, long nativeHandle) {
            this.device = device;
            receiver = new MidiReceiver() {
                @Override
                public void onSend(byte[] data, int offset, int count, long timestamp) {
                    nativeOnMidi(nativeHandle, data, offset, count, timestamp);
                }
            };
            for (MidiDeviceInfo.PortInfo port : device.getInfo().getPorts()) {
                if (port.getType() == MidiDeviceInfo.PortInfo.TYPE_OUTPUT) {
                    MidiOutputPort output = device.openOutputPort(port.getPortNumber());
                    if (output != null) {
                        output.connect(receiver);
                        outputPorts.add(output);
                    }
                } else if (port.getType() == MidiDeviceInfo.PortInfo.TYPE_INPUT) {
                    MidiInputPort input = device.openInputPort(port.getPortNumber());
                    if (input != null) {
                        inputPorts.add(input);
                    }
                }
            }
        }

        boolean send(byte[] data) {
            boolean sent = false;
            for (MidiInputPort input : inputPorts) {
                try {
                    input.send(data, 0, data.length);
                    sent = true;
                } catch (IOException error) {
                    Log.w(TAG, "MIDI output failed", error);
                }
            }
            return sent;
        }

        void close() {
            for (MidiOutputPort output : outputPorts) {
                try {
                    output.disconnect(receiver);
                    output.close();
                } catch (IOException ignored) {
                }
            }
            for (MidiInputPort input : inputPorts) {
                try {
                    input.close();
                } catch (IOException ignored) {
                }
            }
            try {
                device.close();
            } catch (IOException ignored) {
            }
        }
    }
}
