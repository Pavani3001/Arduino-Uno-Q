import win32com.client
import re
import time
import serial


# ============================================================
# UNO Q
# ============================================================

ARDUINO_PORT = "COM3"
BAUD_RATE = 115200


# ============================================================
# APPROVED DEVICES
# ============================================================

APPROVED_DEVICES = {
    ("2341", "0078"),   # Arduino UNO Q
}


# ============================================================
# CONNECT TO UNO Q
# ============================================================

print("Connecting to Arduino UNO Q...")

arduino = serial.Serial(
    ARDUINO_PORT,
    BAUD_RATE,
    timeout=1
)

time.sleep(2)

print("Connected to UNO Q on", ARDUINO_PORT)
print()


# ============================================================
# GET USB DEVICES
# ============================================================

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
                (
                    device.Name,
                    vid,
                    pid
                )
            )

    return result


# ============================================================
# CHECK APPROVED
# ============================================================

def is_approved(vid, pid):

    return (
        vid.lower(),
        pid.lower()
    ) in {
        (v.lower(), p.lower())
        for v, p in APPROVED_DEVICES
    }


# ============================================================
# SEND LED STATUS
# ============================================================

def send_led_status(status):

    if status == "APPROVED":

        arduino.write(b"GREEN\n")

        print("→ SENT TO UNO Q: GREEN")

    else:

        arduino.write(b"RED\n")

        print("→ SENT TO UNO Q: RED")


# ============================================================
# START
# ============================================================

print("=" * 60)
print("USB SECURITY MONITOR")
print("=" * 60)

print()
print("Approved device:")
print("Arduino UNO Q = VID 2341 / PID 0078")
print()
print("Monitoring USB devices...")
print()


last_security_status = None


# ============================================================
# MAIN LOOP
# ============================================================

try:

    while True:

        devices = get_usb_devices()

        seen = set()

        unknown_device_found = False

        print()
        print("CONNECTED USB DEVICES")
        print("-" * 60)

        for name, vid, pid in devices:

            key = (vid, pid)

            if key in seen:
                continue

            seen.add(key)

            if is_approved(vid, pid):

                status = "APPROVED"

            else:

                status = "UNKNOWN"
                unknown_device_found = True

            print(
                f"{name} | "
                f"VID={vid.upper()} "
                f"PID={pid.upper()} "
                f"→ {status}"
            )


        # ====================================================
        # SECURITY DECISION
        # ====================================================

        if unknown_device_found:

            security_status = "UNKNOWN"

        else:

            security_status = "APPROVED"


        print()
        print("SECURITY STATUS:", security_status)


        # ====================================================
        # ONLY CHANGE LED WHEN STATUS CHANGES
        # ====================================================

        if security_status != last_security_status:

            send_led_status(security_status)

            last_security_status = security_status

        else:

            print("LED status unchanged")


        print("-" * 60)

        time.sleep(3)


except KeyboardInterrupt:

    print()
    print("Stopping USB Security Monitor...")


finally:

    arduino.close()

    print("UNO Q connection closed.")