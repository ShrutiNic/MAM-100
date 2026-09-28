import can
import time
import threading

extension = True

bus = can.interface.Bus(
    interface='pcan',
    channel='PCAN_USBBUS1',
    bitrate=500000
)

# This event tells both processes when the trip is running/stopped
trip_running = threading.Event()


def TriggerCANMessage(canid, packet, variable):
    msg = can.Message(
        arbitration_id=canid,
        data=packet,
        is_extended_id=extension
    )

    try:
        bus.send(msg)
    except can.CanError:
        print(f"Failed to send CAN message: {hex(canid)}")


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


def SingleCanHundred_EndTrip():
    data = [0, 0, 0, 0, 0, 0, 0, 0]

    TriggerCANMessage(
        canid=0x18FF1481,
        packet=data,
        variable="frame"
    )

    TriggerCANMessage(
        canid=0x18FF1581,
        packet=data,
        variable="frame"
    )

    print("Trip End...")


# ============================================================
# 50 ms PROCESS
# ============================================================

def FiftyMillisecondsProc():
    data = [0, 0, 0, 5, 0, 0, 0, 0]

    TriggerCANMessage(
        canid=0x18FF0203,
        packet=data,
        variable="frame"
    )

    print("50 ms message sent", data)


def FiftyMillisecondsThread():
    next_time = time.monotonic()

    while trip_running.is_set():

        FiftyMillisecondsProc()

        # Next execution after 50 ms
        next_time += 0.050

        sleep_time = next_time - time.monotonic()

        if sleep_time > 0:
            time.sleep(sleep_time)


# ============================================================
# 100 ms PROCESS
# ============================================================

def HundredMillisecondsProc():

    counter = 1
    direction = 1
    bat_current = 1
    speed_counter = 10
    counter_trip = 20
    soc_consumed = 85

    next_time = time.monotonic()

    while trip_running.is_set():

        # =====================================================
        # SPEED / BYTE 4
        # =====================================================

        byte4 = counter

        data = [0, 0, 0, byte4, 0, 0, 0, 0]

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

        # =====================================================
        # 24-BIT COUNTER
        # =====================================================

        byte1 = counter & 0xFF
        byte2 = (counter >> 8) & 0xFF
        byte3 = (counter >> 16) & 0xFF

        data = [byte1, byte2, byte3, 0, 0, 0, 0, 0]

        TriggerCANMessage(
            canid=0x18FF0F17,
            packet=data,
            variable="frame"
        )

        # =====================================================
        # BATTERY CURRENT
        # =====================================================

        if bat_current < 100:

            byte1 = bat_current & 0xFF
            byte2 = (bat_current >> 8) & 0xFF

            data = [byte1, byte2, 0, 0, 0, 0, 0, 0]

            TriggerCANMessage(
                canid=0x18FF0D81,
                packet=data,
                variable="frame"
            )

            bat_current += 1

        # =====================================================
        # BATTERY TEMPERATURE
        # =====================================================

        data = [30, 40, 50, 60, 70, 80, 90, 100]

        TriggerCANMessage(
            canid=0x18FF1681,
            packet=data,
            variable="frame"
        )

        # =====================================================
        # SPEED + SOC
        # =====================================================

        byte5 = speed_counter & 0xFF
        byte6 = (speed_counter >> 8) & 0xFF

        data = [
            soc_consumed,
            0,
            3,
            0,
            byte5,
            byte6,
            0,
            0
        ]

        TriggerCANMessage(
            canid=0x18FF0C81,
            packet=data,
            variable="frame"
        )

        if speed_counter == 93:
            direction = -1
        elif speed_counter == 1:
            direction = 1

        speed_counter += direction

        if soc_consumed > 20:
            soc_consumed -= 1

        # =====================================================
        # TRIP EFFICIENCY
        # =====================================================

        byte5_ = counter_trip & 0xFF
        byte6_ = (counter_trip >> 8) & 0xFF

        data = [0, 0, 0, 0, byte5_, byte6_, 0, 0]

        TriggerCANMessage(
            canid=0x18FF0B81,
            packet=data,
            variable="frame"
        )

        if counter_trip < 310:
            counter_trip += 1

        print(
            "Speed:",
            speed_counter,
            "SOC:",
            soc_consumed,
            "Trip efficiency:",
            counter_trip
        )

        # =====================================================
        # NEXT 100 ms
        # =====================================================

        next_time += 0.100

        sleep_time = next_time - time.monotonic()

        if sleep_time > 0:
            time.sleep(sleep_time)


# ============================================================
# MAIN TRIP CONTROLLER
# ============================================================

def RunTrip(duration=60):

    print("Starting trip...")

    # Start-trip CAN messages
    SingleCanHundred_startTrip()

    # Tell both threads to start
    trip_running.set()

    # Create 50 ms thread
    thread_50ms = threading.Thread(
        target=FiftyMillisecondsThread,
        name="CAN_50ms"
    )

    # Create 100 ms thread
    thread_100ms = threading.Thread(
        target=HundredMillisecondsProc,
        name="CAN_100ms"
    )

    # Start both
    thread_50ms.start()
    thread_100ms.start()

    try:
        # Trip duration
        time.sleep(duration)

    finally:
        # Stop BOTH processes
        print("Stopping trip...")
        trip_running.clear()

        # Wait for both threads to finish
        thread_50ms.join()
        thread_100ms.join()

        # Send trip-end messages
        SingleCanHundred_EndTrip()

        print("Trip completed.")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    RunTrip(60)