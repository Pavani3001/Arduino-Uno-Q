# Arduino UNO Q USB Security Monitor

This project monitors USB devices connected to a Windows computer and reports the
security status to an Arduino UNO Q over a serial connection. The Arduino can use
the received status to control an indicator LED:

- `GREEN` means every detected device is approved or ignored.
- `RED` means an unknown USB device was detected.

## Files

- [`usb_security.py`](./usb_security.py) - Recommended monitor. It approves the
  Arduino UNO Q and ignores configured built-in Bluetooth and camera devices.
- [`usb_detector.py`](./usb_detector.py) - Basic monitor that treats every
  non-approved USB device as unknown.
- [Watch the demonstration video](./WhatsApp%20Video%202026-10-16%20at%209.45.11%20PM.mp4)

## Demonstration

<video controls width="720">
  <source src="./WhatsApp%20Video%202026-10-16%20at%209.45.11%20PM.mp4" type="video/mp4">
  Your browser does not support embedded video. [Watch the demonstration video](./WhatsApp%20Video%202026-10-16%20at%209.45.11%20PM.mp4).
</video>

[Download or watch the demonstration video](./WhatsApp%20Video%202026-10-16%20at%209.45.11%20PM.mp4).

## Requirements

- Windows
- Python 3.9 or newer
- Arduino UNO Q connected over USB
- The Arduino's serial port and LED/control sketch configured to accept
  newline-terminated `GREEN` and `RED` messages

Install the Python dependencies:

```powershell
py -m pip install pyserial pywin32
```

## Configuration

Before starting the monitor, open the selected Python file and update:

```python
ARDUINO_PORT = "COM3"
BAUD_RATE = 115200
```

Set `ARDUINO_PORT` to the COM port assigned to the Arduino UNO Q in Windows
Device Manager. Keep the baud rate aligned with the Arduino sketch.

The approved Arduino device is currently configured as:

```text
VID=2341
PID=0078
```

To add or remove devices, update `APPROVED_DEVICES`. In `usb_security.py`,
devices that should not affect the security decision, such as built-in hardware,
can be added to `IGNORED_DEVICES`.

## Usage

Close any other application using the Arduino's serial port, then run the
recommended monitor:

```powershell
py .\usb_security.py
```

For the basic detection behavior:

```powershell
py .\usb_detector.py
```

The monitor prints the connected devices and current security status, then
checks again periodically. Press `Ctrl+C` to stop it safely and close the serial
connection.

## How it works

1. The script queries Windows WMI for USB Plug and Play devices.
2. It extracts each device's vendor ID (VID) and product ID (PID).
3. Each device is classified as approved, ignored, or unknown.
4. The overall status is sent to the Arduino only when it changes.

Use this project as a prototype for USB-device awareness and alerting. The
approved-device list is local configuration and should be reviewed before using
the monitor in a security-sensitive environment.
