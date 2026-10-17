import win32com.client
import re
import time
import serial


# =========================================
# Arduino UNO Q
# =========================================

ARDUINO_PORT = "COM3"
BAUD_RATE = 115200


# =========================================
# APPROVED USB DEVICES
# =========================================

APPROVED_DEVICES = {
    ("2341", "0078"),   # Arduino UNO Q
}


# =========================================
# IGNORE BUILT-IN DEVICES
# =========================================

IGNORED_DEVICES = {
    ("13d3", "3579"),   # Bluetooth
    ("13d3", "54a2"),   # Built-in camera
}


# =========================================
# Connect to UNO Q
# =========================================

print("Connecting to Arduino UNO Q...")

arduino = serial.Serial(
    ARDUINO_PORT,
    BAUD_RATE,
    timeout=1
)

time.sleep(2)

print("Arduino connected.")
print()


# =========================================
# Find USB devices
# =========================================

def get_usb_devices():

    wmi = win32com.client.GetObject("winmgmts:")

    devices = wmi.ExecQuery(
        "SELECT Name, PNPDeviceID "
        "FROM Win32_PnPEntity "
        "WHERE PNPDeviceID LIKE 'USB%'"
    )

    result = []

    for device in devices:

        if not device.PNPDeviceID:
            continue

        match = re.search(
            r"VID_([0-9A-Fa-f]{4})&PID_([0-9A-Fa-f]{4})",
            device.PNPDeviceID
        )

        if match:

            vid = match.group(1).lower()
            pid = match.group(2).lower()

            result.append(
                (device.Name, vid, pid)
            )

    return result


# =========================================
# Send status to Arduino
# =========================================

def send_to_arduino(status):

    command = status + "\n"

    arduino.write(command.encode())
    arduino.flush()

    print("SENT TO UNO Q:", status)


# =========================================
# USB SECURITY MONITOR
# =========================================

print("USB SECURITY MONITOR")
print("====================")

print("Approved devices:")

for vid, pid in APPROVED_DEVICES:
    print(
        f"  VID={vid.upper()} PID={pid.upper()}"
    )

print()

print("Ignored built-in devices:")

for vid, pid in IGNORED_DEVICES:
    print(
        f"  VID={vid.upper()} PID={pid.upper()}"
    )

print()

print("Monitoring USB devices...")
print()


last_status = None


try:

    while True:

        devices = get_usb_devices()

        unknown_devices = []

        print("CONNECTED USB DEVICES")
        print("-" * 60)

        for name, vid, pid in devices:

            key = (vid, pid)

            # -----------------------------
            # Approved
            # -----------------------------

            if key in APPROVED_DEVICES:

                status = "APPROVED"


            # -----------------------------
            # Ignored built-in device
            # -----------------------------

            elif key in IGNORED_DEVICES:

                status = "IGNORED"


            # -----------------------------
            # Unknown device
            # -----------------------------

            else:

                status = "UNKNOWN"

                unknown_devices.append(
                    (name, vid, pid)
                )


            print(
                f"{name} | "
                f"VID={vid.upper()} "
                f"PID={pid.upper()} "
                f"→ {status}"
            )


        # =================================
        # SECURITY DECISION
        # =================================

        if unknown_devices:

            security_status = "RED"

        else:

            security_status = "GREEN"


        print()

        print(
            "SECURITY STATUS:",
            security_status
        )


        # =================================
        # Send only when status changes
        # =================================

        if security_status != last_status:

            send_to_arduino(security_status)

            last_status = security_status

        else:

            print("LED status unchanged")


        print("-" * 60)

        time.sleep(2)


except KeyboardInterrupt:

    print()
    print("USB monitor stopped.")


finally:

    arduino.close()

    print("Arduino connection closed.")