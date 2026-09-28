import can
import time
import threading
from datetime import datetime
import sys


extension = True

bus = can.interface.Bus(
    interface='pcan',
    channel='PCAN_USBBUS1',
    bitrate=500000
)


# =========================================================
# 20 ms THREAD CONTROL
# =========================================================
twenty_ms_stop_event = threading.Event()
twenty_ms_thread = None


def TriggerCANMessage(canid, packet, variable):

    msg = can.Message(
        arbitration_id=canid,
        data=packet,
        is_extended_id=extension
    )

    print("TriggerCANMessage for 0681", msg)

    try:
        bus.send(msg)
    except can.CanError:
        print("Failed")


# =========================================================
# 20 ms PROCESS
# =========================================================
##Change mode here in first byte
def TwentyMs():

    while not twenty_ms_stop_event.wait(0.02):

        data = [2, 0, 0, 0, 0, 0, 0, 0]

        TriggerCANMessage(
            canid=0x18FF0481,
            packet=data,
            variable="frame"
        )


# =========================================================
# START TRIP
# =========================================================
def SingleCanHundred_startTrip():

    global twenty_ms_thread

    data = [0, 4, 0, 0, 0, 0, 0, 0]

    TriggerCANMessage(
        canid=0x18FF0781,
        packet=data,
        variable="frame"
    )

    # =====================================================
    # START 20 ms THREAD
    # =====================================================
    twenty_ms_stop_event.clear()

    if twenty_ms_thread is None or not twenty_ms_thread.is_alive():

        twenty_ms_thread = threading.Thread(
            target=TwentyMs
        )

        twenty_ms_thread.start()

    print("Trip started...")


# =========================================================
# END TRIP
# =========================================================
def SingleCanHundred_EndTrip():

    global twenty_ms_thread

    # =====================================================
    # STOP 20 ms THREAD
    # =====================================================
    twenty_ms_stop_event.set()

    if twenty_ms_thread is not None:

        twenty_ms_thread.join()

        twenty_ms_thread = None

    # =====================================================
    # EXISTING END TRIP LOGIC
    # =====================================================

    data = [0, 0, 0, 0, 0, 0, 0, 0]

    TriggerCANMessage(
        canid=0x18FF0781,
        packet=data,
        variable="frame"
    )

    data = [40, 0, 0, 0, 0, 0, 0, 0]

    TriggerCANMessage(
        canid=0x18FF0781,
        packet=data,
        variable="frame"
    )

    print("Trip End...")


# =========================================================
# 100 ms PROCESS
# =========================================================
def HundredMilliSecondsProc():

    counter = 1
    direction = 1
    counter1 = 15
    start_time = time.monotonic()
    counter2 = 80
    counter3 = 11

    # =====================================================
    # Start trip once
    # =====================================================
    SingleCanHundred_startTrip()

    # =====================================================
    # Run trip for 30 seconds
    # =====================================================
    ##change time her in place of 40
    while time.monotonic() - start_time < 40:

        elapsed = time.monotonic() - start_time

        # =================================================
        # SPEED / BYTE 4
        # 1 -> 2 -> 3 -> ... -> 120 -> 119 -> ... -> 1
        # =================================================
        byte4 = counter

        # Change direction at limits
        if counter == 120:
            direction = -1

        elif counter == 1:
            direction = 1

        counter += direction

        # =================================================
        # 18FF0E81 COUNTER: BYTE 5 + BYTE 6
        # Value: 1 -> 300
        # =================================================

        # =================================================
        # 16-bit COUNTER -> bytes 4, 5
        # =================================================
        byte4 = counter1 & 0xFF
        byte5 = (counter1 >> 8) & 0xFF

        data = [
            0,
            0,
            0,
            0,
            byte4,
            byte5,
            0,
            0
        ]

        TriggerCANMessage(
            canid=0x18FF0E81,
            packet=data,
            variable="frame"
        )

        # Increase once every 100 ms, up to 300
        if counter1 < 300:
            counter1 += 1

        print("Trip efficiency", counter1)

        # =================================================
        # 24-bit COUNTER -> bytes 6, 7, 8
        # =================================================
        byte6 = counter & 0xFF
        byte7 = (counter >> 8) & 0xFF
        byte8 = (counter >> 16) & 0xFF

        data = [
            0,
            0,
            0,
            0,
            0,
            byte6,
            byte7,
            byte8
        ]

        TriggerCANMessage(
            canid=0x18FF1C81,
            packet=data,
            variable="frame"
        )

        print(
            f"Elapsed = {elapsed:.2f}s, "
            f"Speed = {byte4}, "
            f"Counter = {counter}"
        )

        # =================================================
        # BAT CURRENT
        # =================================================
        data = [
            0,
            0,
            0,
            0,
            0xD6,
            0x06,
            0,
            0
        ]

        TriggerCANMessage(
            canid=0x18FF2081,
            packet=data,
            variable="frame"
        )

        # =================================================
        # BAT TEMPERATURE
        # Before 5 sec  -> MAX temperature
        # After 5 sec   -> MIN temperature
        # =================================================
        if elapsed < 5:

            data = [
                30,
                40,
                50,
                60,
                70,
                80,
                90,
                100
            ]

        else:

            data = [
                10,
                9,
                8,
                7,
                6,
                5,
                4,
                3
            ]

        TriggerCANMessage(
            canid=0x18FF1681,
            packet=data,
            variable="frame"
        )

        # =================================================
        # CELL VOLTAGE GROUP 1
        # =================================================
        if elapsed < 5:

            data = [
                0xE8,
                0x03,
                0xDC,
                0x05,
                0xD0,
                0x07,
                0xC4,
                0x09
            ]

        else:

            data = [
                0xD0,
                0x07,
                0xC4,
                0x09,
                0xB8,
                0x0B,
                0xAC,
                0x0D
            ]

        TriggerCANMessage(
            canid=0x18FF1281,
            packet=data,
            variable="frame"
        )

        # =================================================
        # CELL VOLTAGE GROUP 2
        # =================================================
        if elapsed < 5:

            data = [
                0xE8,
                0x03,
                0xDC,
                0x05,
                0xD0,
                0x07,
                0xC4,
                0x09
            ]

        else:

            data = [
                0xD0,
                0x07,
                0xC4,
                0x09,
                0xB8,
                0x0B,
                0xAC,
                0x0D
            ]

        TriggerCANMessage(
            canid=0x18FF1381,
            packet=data,
            variable="frame"
        )

        # =================================================
        # CELL VOLTAGE GROUP 3
        # =================================================
        if elapsed < 5:

            data = [
                0xE8,
                0x03,
                0xDC,
                0x05,
                0xD0,
                0x07,
                0xC4,
                0x09
            ]

        else:

            data = [
                0xD0,
                0x07,
                0xC4,
                0x09,
                0xB8,
                0x0B,
                0xAC,
                0x0D
            ]

        TriggerCANMessage(
            canid=0x18FF1481,
            packet=data,
            variable="frame"
        )

        # =================================================
        # CELL VOLTAGE GROUP 4
        # =================================================
        if elapsed < 5:

            data = [
                0xE8,
                0x03,
                0xDC,
                0x05,
                0xD0,
                0x07,
                0xC4,
                0x09
            ]

        else:

            data = [
                0xD0,
                0x07,
                0xC4,
                0x09,
                0xB8,
                0x0B,
                0xAC,
                0x0D
            ]

        TriggerCANMessage(
            canid=0x18FF1581,
            packet=data,
            variable="frame"
        )

        # =================================================
        # 0x18FF0B81 COUNTER: 100 -> 1
        # =================================================
        byte5 = counter3 & 0xFF
        byte6 = (counter3 >> 8) & 0xFF

        data = [
            0,
            0,
            0,
            0,
            byte5,
            byte6,
            0,
            0
        ]

        TriggerCANMessage(
            canid=0x18FF0E81,
            packet=data,
            variable="frame"
        )

        # For changing KWH value use this loop
        # use counter3 variable for changing start value
        print(
            f"Counter3 = {counter3}, "
            f"Byte5 = {byte5}, "
            f"Byte6 = {byte6}"
        )

        # Increase every 100 ms until 300
        if counter3 < 300:

            counter3 += 1

            print(
                "0x18FF0E81 value:",
                counter3
            )

        TriggerCANMessage(
            canid=0x18FF0B81,
            packet=data,
            variable="frame"
        )

        # Decrease every 100 ms, stop at 1
        if counter2 > 20:
            counter2 -= 1

        print(
            "0x18FF0B81 value:",
            counter2
        )

        # =================================================
        # 100 ms cycle
        # =================================================
        time.sleep(0.1)

    # =====================================================
    # END TRIP
    # =====================================================
    SingleCanHundred_EndTrip()


# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":

    t1 = threading.Thread(
        target=HundredMilliSecondsProc,
        args=()
    )

    t1.start()

    # Wait for the 100 ms trip thread to finish
    t1.join()