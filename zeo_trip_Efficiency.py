# import can
# import time
# import threading

# extension = True

# bus = can.interface.Bus(
#     interface='pcan',
#     channel='PCAN_USBBUS1',
#     bitrate=500000
# )

# # This event tells both processes when the trip is running/stopped
# trip_running = threading.Event()


# def TriggerCANMessage(canid, packet, variable):
#     msg = can.Message(
#         arbitration_id=canid,
#         data=packet,
#         is_extended_id=extension
#     )

#     try:
#         bus.send(msg)
#     except can.CanError:
#         print(f"Failed to send CAN message: {hex(canid)}")


# def SingleCanHundred_startTrip():
#     data = [0x6C, 0, 0, 0, 0, 0, 0, 0]
#     TriggerCANMessage(
#         canid=0x336,
#         packet=data,
#         variable="frame"
#     )


#     print("Trip started...")


# def SingleCanHundred_EndTrip():
#     data = [0, 0, 0, 0, 0, 0, 0, 0]

#     TriggerCANMessage(
#         canid=0x336,
#         packet=data,
#         variable="frame"
#     )

#     print("Trip End...")


# # ============================================================
# # 50 ms PROCESS
# # ============================================================

# def FiftyMillisecondsProc():
#     data = [0, 0, 0, 5, 0, 0, 0, 0]

#     TriggerCANMessage(
#         canid=0x18FF0203,
#         packet=data,
#         variable="frame"
#     )

#     print("50 ms message sent", data)


# def FiftyMillisecondsThread():
#     next_time = time.monotonic()

#     while trip_running.is_set():

#         FiftyMillisecondsProc()

#         # Next execution after 50 ms
#         next_time += 0.050

#         sleep_time = next_time - time.monotonic()

#         if sleep_time > 0:
#             time.sleep(sleep_time)


# # ============================================================
# # 100 ms PROCESS
# # ============================================================

# def HundredMillisecondsProc():

#     counter = 1
#     direction = 1
#     bat_temp = 1280
#     speed_counter = 0
#     counter_trip = 20
#     soc_consumed = 85
#     bat_vtg = 20
#     next_time = time.monotonic()

#     while trip_running.is_set():

#         # =====================================================
#         # SPEED / BYTE 4
#         # =====================================================

#         byte4 = counter

#         data = [0, 0, 0, byte4, 0, 0, 0, 0]

#         TriggerCANMessage(
#             canid=0x18FF0481,
#             packet=data,
#             variable="frame"
#         )

#         if counter == 130:
#             direction = -1
#         elif counter == 1:
#             direction = 1

#         counter += direction

#         # =====================================================
#         # 24-BIT COUNTER
#         # =====================================================

#         byte1 = counter & 0xFF
#         byte2 = (counter >> 8) & 0xFF
#         byte3 = (counter >> 16) & 0xFF

#         data = [byte1, byte2, byte3, 0, 0, 0, 0, 0]

#         TriggerCANMessage(
#             canid=0x18FF0F17,
#             packet=data,
#             variable="frame"
#         )

#         # =====================================================
#         # BATTERY CURRENT
#         # =====================================================

#         byte5_bat = bat_temp & 0xFF
#         byte6_bat = (bat_temp >> 8) & 0xFF

#         data = [0, 0, 0, 0, byte5_bat, byte6_bat, 0, 0]

#         TriggerCANMessage(
#             canid=0x3D3,
#             packet=data,
#             variable="frame"
#         )

#         print("bat Temp:", bat_temp)

#         bat_temp += 1

#         if bat_temp >= 1340:
#             bat_temp = 10

#         # =====================================================
#         # BATTERY Voltage
#         # =====================================================
#         byte1_vtg = bat_vtg & 0xFF
#         byte2_vtg = (bat_vtg >> 8) & 0xFF
#         data = [byte1_vtg, byte2_vtg, 0, 0, 0, 0, 0, 0]

#         TriggerCANMessage(
#             canid=0x150,
#             packet=data,
#             variable="frame"
#         )

#         if bat_vtg< 200:
#             bat_vtg += 1

#         # =====================================================
#         # SPEED + SOC
#         # =====================================================
#         byte4 = speed_counter
#         byte5 = speed_counter & 0xFF
#         byte6 = (speed_counter >> 8) & 0xFF

#         data = [
#             0,
#             0,
#             0,
#             byte4,
#             byte5,
#             byte6,
#             0,
#             0
#         ]

#         TriggerCANMessage(
#             canid=0x5C2,
#             packet=data,
#             variable="frame"
#         )

#         if speed_counter == 100:
#             direction = -1
#         elif speed_counter == 1:
#             direction = 1

#         speed_counter += direction

#         if soc_consumed > 20:
#             soc_consumed -= 1

#         # =====================================================
#         # TRIP EFFICIENCY
#         # =====================================================

#         byte5_ = counter_trip & 0xFF
#         byte6_ = (counter_trip >> 8) & 0xFF

#         data = [0, 0, 0, 0, byte5_, byte6_, 0, 0]

#         TriggerCANMessage(
#             canid=0x336,
#             packet=data,
#             variable="frame"
#         )
#         # =====================================================
#         # NEXT 100 ms
#         # =====================================================

#         next_time += 0.100

#         sleep_time = next_time - time.monotonic()

#         if sleep_time > 0:
#             time.sleep(sleep_time)


# # ============================================================
# # MAIN TRIP CONTROLLER
# # ============================================================

# def RunTrip(duration=20):

#     print("Starting trip...")

#     # Start-trip CAN messages
#     SingleCanHundred_startTrip()

#     # Tell both threads to start
#     trip_running.set()

#     # Create 50 ms thread
#     thread_50ms = threading.Thread(
#         target=FiftyMillisecondsThread,
#         name="CAN_50ms"
#     )

#     # Create 100 ms thread
#     thread_100ms = threading.Thread(
#         target=HundredMillisecondsProc,
#         name="CAN_100ms"
#     )

#     # Start both
#     #thread_50ms.start()
#     thread_100ms.start()

#     try:
#         # Trip duration
#         time.sleep(duration)

#     finally:
#         # Stop BOTH processes
#         print("Stopping trip...")
#         trip_running.clear()

#         # Wait for both threads to finish
#         thread_50ms.join()
#         thread_100ms.join()

#         # Send trip-end messages
#         SingleCanHundred_EndTrip()

#         print("Trip completed.")


# # ============================================================
# # MAIN
# # ============================================================

# if __name__ == "__main__":
#     RunTrip(20)


import can
import time
import threading


# ============================================================
# CAN BUS
# ============================================================

bus = can.interface.Bus(
    interface='pcan',
    channel='PCAN_USBBUS1',
    bitrate=500000
)


# This event tells both processes when the trip is running/stopped
trip_running = threading.Event()


# ============================================================
# CAN MESSAGE
# ============================================================

def TriggerCANMessage(canid, packet, variable="frame"):

    # 0x336, 0x3D3, 0x150 and 0x5C2 are standard 11-bit IDs.
    # 0x18FFxxxx IDs are extended 29-bit IDs.
    is_extended = canid > 0x7FF

    msg = can.Message(
        arbitration_id=canid,
        data=packet,
        is_extended_id=is_extended
    )

    try:
        bus.send(msg)

    except can.CanError as e:
        print(
            f"Failed to send CAN message "
            f"ID={hex(canid)}, DATA={packet}, ERROR={e}"
        )


# ============================================================
# 0x336 - TRIP START
# ============================================================

def SingleCanHundred_startTrip():

    data = [
        0x6C,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00
    ]

    TriggerCANMessage(
        canid=0x336,
        packet=data
    )

    print(
        "Trip started - 0x336:",
        " ".join(f"{x:02X}" for x in data)
    )


# ============================================================
# 0x336 - TRIP END
# ============================================================

def SingleCanHundred_EndTrip():

    data = [
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00
    ]

    TriggerCANMessage(
        canid=0x336,
        packet=data
    )

    print(
        "Trip End - 0x336:",
        " ".join(f"{x:02X}" for x in data)
    )


# ============================================================
# 50 ms PROCESS
# ============================================================

def FiftyMillisecondsProc():

    data = [
        0x00,
        0x00,
        0x00,
        0x05,
        0x00,
        0x00,
        0x00,
        0x00
    ]

    TriggerCANMessage(
        canid=0x18FF0203,
        packet=data
    )

    print(
        "50 ms:",
        "0x18FF0203",
        " ".join(f"{x:02X}" for x in data)
    )


def FiftyMillisecondsThread():

    next_time = time.monotonic()

    while trip_running.is_set():

        FiftyMillisecondsProc()

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

    bat_temp = 1280
    speed_counter = 0

    # Trip efficiency starts at 20
    counter_trip = 20
    trip_efficiency = 6
    soc_consumed = 85
    bat_vtg = 20
    kwh_consumed = 25

    next_time = time.monotonic()

    while trip_running.is_set():

        # ====================================================
        # SPEED / BYTE 4
        # ====================================================

        byte4 = counter

        data = [
            0x00,
            0x00,
            0x00,
            byte4,
            0x00,
            0x00,
            0x00,
            0x00
        ]

        TriggerCANMessage(
            canid=0x18FF0481,
            packet=data
        )

        if counter == 130:
            direction = -1

        elif counter == 1:
            direction = 1

        counter += direction


        # ====================================================
        # 24-BIT COUNTER
        # ====================================================

        byte1 = counter & 0xFF
        byte2 = (counter >> 8) & 0xFF
        byte3 = (counter >> 16) & 0xFF

        data = [
            byte1,
            byte2,
            byte3,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00
        ]

        TriggerCANMessage(
            canid=0x18FF0F17,
            packet=data
        )


        # ====================================================
        # BATTERY CURRENT
        # ====================================================

        byte5_bat = bat_temp & 0xFF
        byte6_bat = (bat_temp >> 8) & 0xFF

        data = [
            0x00,
            0x00,
            0x00,
            0x00,
            byte5_bat,
            byte6_bat,
            0x00,
            0x00
        ]

        TriggerCANMessage(
            canid=0x3D3,
            packet=data
        )

        print("Battery Temp:", bat_temp)

        bat_temp += 1

        if bat_temp >= 1340:
            bat_temp = 10


        # ====================================================
        # BATTERY VOLTAGE
        # ====================================================

        byte1_vtg = bat_vtg & 0xFF
        byte2_vtg = (bat_vtg >> 8) & 0xFF

        data = [
            byte1_vtg,
            byte2_vtg,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00
        ]

        TriggerCANMessage(
            canid=0x150,
            packet=data
        )

        if bat_vtg < 200:
            bat_vtg += 1


        # ====================================================
        # SPEED + SOC
        # ====================================================

        byte4 = speed_counter
        byte5 = speed_counter & 0xFF
        byte6 = (speed_counter >> 8) & 0xFF

        data = [
            0x00,
            0x00,
            0x00,
            byte4,
            byte5,
            byte6,
            0x00,
            0x00
        ]

        TriggerCANMessage(
            canid=0x5C2,
            packet=data
        )

        if speed_counter == 100:
            direction = -1

        elif speed_counter == 1:
            direction = 1

        speed_counter += direction


        # ====================================================
        # SOC
        # ====================================================

        data = [soc_consumed, 0, 0, 0, 0, 0, 0, 0]
                
        TriggerCANMessage(
                            canid=0x134,
                            packet=data,
                            variable="frame"
                        )
        if soc_consumed > 5:
            soc_consumed -= 1        
        print("134 SOC Consumed:", soc_consumed)


        
                

        # ====================================================
        # 0x3EA - TRIP EFFICIENCY
        # ====================================================

        data = [0, 0, trip_efficiency, 0, 0, 0, 0, 0]
        
        TriggerCANMessage(
                    canid=0x3EA,
                    packet=data,
                    variable="frame"
                )
        
        print("3EA Trip Efficiency:", trip_efficiency)
        
                # Decrement every 500 ms
        if trip_efficiency < 18:
            trip_efficiency += 1


        # ====================================================
        # ECO Mode/ Boost Mode
        # change 1st byte for changing mode
        #
        # ====================================================

        data = [1, 0, 0, 0, 0, 0, 0, 0]
                                
        TriggerCANMessage(
                                            canid=0x3F9,
                                            packet=data,
                                            variable="frame"
                                        )
        


        # ====================================================
        # NEXT 100 ms
        # ====================================================

        next_time += 0.100

        sleep_time = next_time - time.monotonic()

        if sleep_time > 0:
            time.sleep(sleep_time)


# ============================================================
# MAIN TRIP CONTROLLER
# ============================================================

def RunTrip(duration=20):

    print("Starting trip...")

    # --------------------------------------------------------
    # Send 0x336 trip-start message
    # --------------------------------------------------------

    SingleCanHundred_startTrip()

    # --------------------------------------------------------
    # Start both periodic processes
    # --------------------------------------------------------

    trip_running.set()

    thread_50ms = threading.Thread(
        target=FiftyMillisecondsThread,
        name="CAN_50ms"
    )

    thread_100ms = threading.Thread(
        target=HundredMillisecondsProc,
        name="CAN_100ms"
    )

    thread_50ms.start()
    thread_100ms.start()

    try:

        # Run trip for specified duration
        time.sleep(duration)

    finally:

        print("Stopping trip...")

        # Stop both threads
        trip_running.clear()

        # Wait for threads to finish
        thread_50ms.join()
        thread_100ms.join()

        # ----------------------------------------------------
        # Send 0x336 trip-end message
        # ----------------------------------------------------

        SingleCanHundred_EndTrip()

        print("Trip completed.")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    RunTrip(20)