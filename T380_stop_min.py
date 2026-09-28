import can
import time
import threading

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

    try:
        bus.send(msg)
    except can.CanError:
        print(f"Failed to send CAN ID {hex(canid)}")


def SingleCanHundred_startTrip():
    data = [0, 4, 0, 0, 0, 0, 0, 0]

    TriggerCANMessage(
        canid=0x18FF0781,
        packet=data,
        variable="frame"
    )

    print("Trip started...")


def SingleCanHundred_EndTrip():
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


def Send0481_20ms(stop_event):
    """
    Send 0x18FF0481 every 20 ms until the trip ends.
    """

    data = [0, 0, 0, 2, 0, 0, 0, 0]

    next_send = time.monotonic()

    while not stop_event.is_set():

        TriggerCANMessage(
            canid=0x18FF0481,
            packet=data,
            variable="frame"
        )

        # Schedule next transmission exactly 20 ms later
        next_send += 0.020

        sleep_time = next_send - time.monotonic()

        if sleep_time > 0:
            stop_event.wait(sleep_time)


def HundredMilliSecondsProc():

    counter = 1
    direction = 1
    counter1 = 15

    # Event used to stop the 20 ms 0481 thread
    stop_0481 = threading.Event()

    # Start 0481 transmission thread
    t0481 = threading.Thread(
        target=Send0481_20ms,
        args=(stop_0481,),
        daemon=True
    )

    # Start trip
    SingleCanHundred_startTrip()

    # Start 20 ms 0481 transmission
    t0481.start()

    start_time = time.monotonic()

    try:

        # Run trip for 30 seconds
        while time.monotonic() - start_time < 60:

            elapsed = time.monotonic() - start_time

            # =====================================================
            # SPEED
            # 1 -> 2 -> 3 -> ... -> 120 -> 119 -> ... -> 1
            # =====================================================

            if counter == 120:
                direction = -1

            elif counter == 1:
                direction = 1

            counter += direction

            # =====================================================
            # 16-bit COUNTER -> BYTE 4 + BYTE 5
            # =====================================================

            byte4 = counter1 & 0xFF
            byte5 = (counter1 >> 8) & 0xFF

            data = [
                0, 0, 0, 0,
                byte4,
                byte5,
                0, 0
            ]

            TriggerCANMessage(
                canid=0x18FF0E81,
                packet=data,
                variable="frame"
            )

            if counter1 < 300:
                counter1 += 1

            print("Trip efficiency", counter1)

            # =====================================================
            # 24-bit COUNTER -> BYTE 6 + BYTE 7 + BYTE 8
            # =====================================================

            byte6 = counter & 0xFF
            byte7 = (counter >> 8) & 0xFF
            byte8 = (counter >> 16) & 0xFF

            data = [
                0, 0, 0, 0,
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
                f"Speed = {counter}, "
                f"Counter = {counter}"
            )

            # 100 ms cycle
            time.sleep(0.100)

    finally:

        # =====================================================
        # STOP 0481 TRANSMISSION FIRST
        # =====================================================

        stop_0481.set()
        t0481.join()

        # =====================================================
        # END TRIP
        # =====================================================

        SingleCanHundred_EndTrip()


if __name__ == "__main__":

    t1 = threading.Thread(
        target=HundredMilliSecondsProc
    )

    t1.start()
    t1.join()