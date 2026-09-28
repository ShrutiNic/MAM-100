import can
import time

# ---------------- CAN SETUP ----------------
bus = can.interface.Bus(
    interface='pcan',
    channel='PCAN_USBBUS1',
    bitrate=500000
)

CAN_ID = 0x18FF0781

ON_DATA = [0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
OFF_DATA = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]


def send_can(data):
    msg = can.Message(
        arbitration_id=CAN_ID,
        data=data,
        is_extended_id=True
    )
    bus.send(msg)


while True:

    # =========================
    # ON for 28 seconds
    # =========================
    print("IGN ON")

    start = time.monotonic()

    while time.monotonic() - start < 28:
        send_can(ON_DATA)
        time.sleep(0.5)

    # =========================
    # OFF
    # =========================
    print("IGN OFF")

    send_can(OFF_DATA)

    # =========================
    # OFF for 4 minutes
    # =========================
    print("Waiting 4 minutes...")

    time.sleep(240)

    print("Starting again...")
