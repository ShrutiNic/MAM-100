import can
import threading
import time
import traceback

# ---------------- CAN SETUP ----------------
bus = can.interface.Bus(
    interface='pcan',
    channel='PCAN_USBBUS1',
    bitrate=500000
)

print("PCAN connected!")


# ---------------- SETTINGS ----------------
SEND_DURATION = 30     # ON time
STOP_DURATION = 10     # OFF time
SEND_PERIOD = 0.5      # CAN transmit rate


# ---------------- CAN SEND ----------------
def TriggerCANMessage():

    msg = can.Message(
        arbitration_id=0x18FF0781,
        data=[1,2,3,4,5,6,7,8],
        is_extended_id=True
    )

    try:
        print("Before CAN send")

        # timeout prevents hanging forever
        bus.send(msg, timeout=0.2)

        print("After CAN send")

    except can.CanError as e:
        print("CAN ERROR:", e)

    except Exception as e:
        print("UNKNOWN ERROR:", e)
        traceback.print_exc()


# ---------------- THREAD ----------------
def SendThread():

    state = True       # True = ON, False = OFF
    state_start = time.monotonic()

    while True:

        try:

            now = time.monotonic()
            elapsed = now - state_start


            if state:

                TriggerCANMessage()

                print(
                    time.strftime("%H:%M:%S"),
                    "ON",
                    "elapsed:",
                    round(elapsed,1)
                )


                if elapsed >= SEND_DURATION:
                    state = False
                    state_start = time.monotonic()
                    print("========== DEVICE OFF ==========")


            else:

                print(
                    time.strftime("%H:%M:%S"),
                    "OFF",
                    "elapsed:",
                    round(elapsed,1)
                )


                if elapsed >= STOP_DURATION:
                    state = True
                    state_start = time.monotonic()
                    print("========== DEVICE ON ==========")


            time.sleep(SEND_PERIOD)


        except Exception:
            print("THREAD CRASH")
            traceback.print_exc()
            break



# Start thread
t = threading.Thread(
    target=SendThread,
    daemon=False
)

t.start()


# Keep alive
while True:
    time.sleep(1)