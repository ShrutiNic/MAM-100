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


def TriggerCANMessage(canid, packet, variable):

    msg = can.Message(
        arbitration_id=canid,
        data=packet,
        is_extended_id=extension
    )

    print("TriggerCANMessage:", msg)

    try:
        bus.send(msg)
    except can.CanError:
        print("Failed")


# =========================================================
# START TRIP
# =========================================================

def SingleCanHundred_startTrip():

    data = [0, 0, 0, 0, 0, 0, 0, 11]

    TriggerCANMessage(
        canid=0x18FF1481,
        packet=data,
        variable="frame"
    )

    data = [0, 0, 0, 0, 0, 0, 0, 0]

    TriggerCANMessage(
        canid=0x18FF1581,
        packet=data,
        variable="frame"
    )

    print("Trip started...")


# =========================================================
# END TRIP
# =========================================================

def SingleCanHundred_EndTrip():

    data = [0, 0, 0, 0, 0, 0, 0, 0]

    TriggerCANMessage(
        canid=0x18FF1481,
        packet=data,
        variable="frame"
    )

    data = [0, 0, 0, 0, 0, 0, 0, 0]

    TriggerCANMessage(
        canid=0x18FF1581,
        packet=data,
        variable="frame"
    )

    print("Trip End...")


# =========================================================
# 0x18FF0C81 - 20 ms THREAD
# =========================================================

def Send0C81_20ms(stop_event):

    """
    Send 0x18FF0C81 every 20 ms.

    Value:
        1 -> 2 -> 1 -> 2 -> ...

    This thread runs for the complete trip
    and stops only when stop_event is set.
    """

    speed_counter = 1
    direction = 1

    next_send = time.monotonic()

    while not stop_event.is_set():

        # -------------------------------------------------
        # Put speed value into Byte 5
        # -------------------------------------------------

        byte1 = speed_counter & 0xFF
        

        data = [
            byte1,
            0,
            0,
            0,
            0,
            0,
            0,
            0
        ]

        TriggerCANMessage(
            canid=0x18FF0C81,
            packet=data,
            variable="frame"
        )

        print("0x18FF0C81 value:", speed_counter)

        # -------------------------------------------------
        # 1 -> 2 -> 1 -> 2
        # -------------------------------------------------

        if speed_counter == 2:
            direction = -1

        elif speed_counter == 1:
            direction = 1

        speed_counter += direction

        # -------------------------------------------------
        # Exact 20 ms timing
        # -------------------------------------------------

        next_send += 0.020

        sleep_time = next_send - time.monotonic()

        if sleep_time > 0:
            stop_event.wait(sleep_time)


# =========================================================
# MAIN TRIP
# =========================================================

def HundredMilliSecondsProc():

    counter = 1
    direction = 1

    bat_current = 1
    counter_trip = 20

    start_time = time.monotonic()

    # =====================================================
    # Create stop event for 0x18FF0C81 thread
    # =====================================================

    stop_0c81_event = threading.Event()

    # =====================================================
    # START TRIP
    # =====================================================

    SingleCanHundred_startTrip()

    # =====================================================
    # START 20 ms 0x18FF0C81 THREAD
    # =====================================================

    t_0c81 = threading.Thread(
        target=Send0C81_20ms,
        args=(stop_0c81_event,),
        daemon=True
    )

    t_0c81.start()

    print("0x18FF0C81 20 ms thread started")

    # =====================================================
    # RUN TRIP FOR 15 SECONDS
    # =====================================================

    while time.monotonic() - start_time < 60:

        elapsed = time.monotonic() - start_time

        # =================================================
        # SPEED / 0x18FF0481
        # =================================================

        byte4 = counter

        data = [
            0,
            0,
            0,
            byte4,
            0,
            0,
            0,
            0
        ]

        TriggerCANMessage(
            canid=0x18FF0481,
            packet=data,
            variable="frame"
        )

        if counter == 130:
            direction = -1

        elif counter == 1:
            direction = 1

        counter += direction

        # =================================================
        # 24-BIT COUNTER / 0x18FF0F17
        # =================================================

        byte1 = counter & 0xFF
        byte2 = (counter >> 8) & 0xFF
        byte3 = (counter >> 16) & 0xFF

        data = [
            byte1,
            byte2,
            byte3,
            0,
            0,
            0,
            0,
            0
        ]

        TriggerCANMessage(
            canid=0x18FF0F17,
            packet=data,
            variable="frame"
        )

        # =================================================
        # BAT CURRENT / 0x18FF0D81
        # =================================================

        if bat_current < 100:

            byte1 = bat_current & 0xFF
            byte2 = (bat_current >> 8) & 0xFF

            data = [
                byte1,
                byte2,
                0,
                0,
                0,
                0,
                0,
                0
            ]

            TriggerCANMessage(
                canid=0x18FF0D81,
                packet=data,
                variable="frame"
            )

            bat_current += 1

        # =================================================
        # BAT TEMPERATURE / 0x18FF1681
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
        # 0x18FF0C81
        #
        # REMOVED FROM HERE
        #
        # It is now handled by Send0C81_20ms()
        # =================================================

        # =================================================
        # TRIP EFFICIENCY / 0x18FF0B81
        # =================================================

        byte5_ = counter_trip & 0xFF
        byte6_ = (counter_trip >> 8) & 0xFF

        data = [
            0,
            0,
            0,
            0,
            byte5_,
            byte6_,
            0,
            0
        ]

        TriggerCANMessage(
            canid=0x18FF0B81,
            packet=data,
            variable="frame"
        )

        if counter_trip < 310:
            counter_trip += 1

        actual_value = byte5_ | (byte6_ << 8)

        print("Byte5 decimal:", byte5_)
        print("Byte6 decimal:", byte6_)
        print("Actual transmitted decimal value:", actual_value)
        print("trip efficiency:", counter_trip)

        # =================================================
        # 100 ms CYCLE
        # =================================================

        time.sleep(0.1)

    # =====================================================
    # TRIP ENDED
    # =====================================================

    print("15 seconds completed - stopping trip")

    # -----------------------------------------------------
    # STOP 0x18FF0C81 THREAD
    # -----------------------------------------------------

    stop_0c81_event.set()

    # Wait until 20 ms thread has completely stopped
    t_0c81.join()

    print("0x18FF0C81 20 ms thread stopped")

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

    t1.join()

    print("Program finished")