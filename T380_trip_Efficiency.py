
import can
import time
import threading
from datetime import datetime
import sys


extension = True
bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)

def TriggerCANMessage(canid, packet, variable):
    
    msg = can.Message(arbitration_id=canid,data=packet,is_extended_id=extension)
    print("TriggerCANMessage for 0681", msg)
    try:
        bus.send(msg)
    except can.CanError:
          print("Failed")



import time


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


# def HundredMilliSecondsProc():
#     counter = 0
#     start_time = time.monotonic()

#     # Start trip once
#     SingleCanHundred_startTrip()

#     # Run for 100 seconds
#     while time.monotonic() - start_time < 20:

#         # 24-bit counter -> bytes 6, 7, 8
#         byte6 = counter & 0xFF
#         byte7 = (counter >> 8) & 0xFF
#         byte8 = (counter >> 16) & 0xFF

#         data = [0, 0, 0, 0, 0, byte6, byte7, byte8]

#         TriggerCANMessage(
#             canid=0x18FF1C81,
#             packet=data,
#             variable="frame"
#         )

        
#         print(f"Counter = {counter}, Data = {data}")

#         counter += 1
# ###################BAT Current For -350 value is 0x54 0xF2  for 350 0xAC 0x0D    for 175 0xD6 06   consider value for 5th & 6th byte#####
#         data = [0, 0, 0, 0, 0xD6, 0x06, 0, 0]
        
#         TriggerCANMessage(
#                     canid=0x18FF2081,
#                     packet=data,
#                     variable="frame"
#                 )
#         time.sleep(0.1)
        
# ############# BAT Temperature Raw value from vspy will be consider for data -20=0,-19= 1,-18 = 2 and so on
#         data = [30,40,50,60,70,80,90,100]  ####max bat temp
                
#         TriggerCANMessage(
#                             canid=0x18FF1681,
#                             packet=data,
#                             variable="frame"
#                         )
        
#         print("start time", start_time)
#         if start_time > 5:
#             data = [10,9,8,7,6,5,4,3]   #min bat temp

                            
#             TriggerCANMessage(
#                                         canid=0x18FF1681,
#                                         packet=data,
#                                         variable="frame"
#                                     )
#             time.sleep(0.1)
            
#         data = [0xE8,0x03,0xDC,0x05,0xD0,0x07,0xC4,0x09]   ###Min cell voltage 1,5,9,13 each number is of 2 bytes                     
#         TriggerCANMessage(
#                                     canid=0x18FF1281,
#                                     packet=data,
#                                     variable="frame"
#                                 )
                
#         print("start time", start_time)
#         if start_time > 5:
#                 data = [0xD0,0x07,0xC4,0x09,0xB8,0x0B,0xAC,0x0D]   #Max cell voltage 1,5,9,13 each number is of 2 bytes 
        
                                    
#                 TriggerCANMessage(
#                                                 canid=0x18FF1281,
#                                                 packet=data,
#                                                 variable="frame"
#                                             )
#         data = [0xE8,0x03,0xDC,0x05,0xD0,0x07,0xC4,0x09]   ###Min cell voltage 2,6,10,14 each number is of 2 bytes                        
#         TriggerCANMessage(
#                                             canid=0x18FF1381,
#                                             packet=data,
#                                             variable="frame"
#                                         )
                        
#         print("start time", start_time)
#         if start_time > 5:
#             data = [0xD0,0x07,0xC4,0x09,0xB8,0x0B,0xAC,0x0D]   ####Max cell voltage 2,6,10,14 each number is of 2 bytes
#             TriggerCANMessage(
#                                                         canid=0x18FF1381,
#                                                         packet=data,
#                                                         variable="frame"
#                                                     )
#         data = [0xE8,0x03,0xDC,0x05,0xD0,0x07,0xC4,0x09]   ###Min cell voltage 3,11,15,17 each number is of 2 bytes                        
#         TriggerCANMessage(
#                                                     canid=0x18FF1481,
#                                                     packet=data,
#                                                     variable="frame"
#                                                 )
                                
#         print("start time", start_time)
#         if start_time > 5:
#             data = [0xD0,0x07,0xC4,0x09,0xB8,0x0B,0xAC,0x0D]   ####Max cell voltage 3,11,15,17 each number is of 2 bytes
#             TriggerCANMessage(
#                                                                 canid=0x18FF1481,
#                                                                 packet=data,
#                                                                 variable="frame"
#                                                             )
#         data = [0xE8,0x03,0xDC,0x05,0xD0,0x07,0xC4,0x09]   ###Min cell voltage 4,8,12,16 each number is of 2 bytes                        
#         TriggerCANMessage(
#                                                             canid=0x18FF1581,
#                                                             packet=data,
#                                                             variable="frame"
#                                                         )
                                        
#         print("start time", start_time)
#         if start_time > 5:
#             data = [0xD0,0x07,0xC4,0x09,0xB8,0x0B,0xAC,0x0D]   ####Max cell voltage 4,8,12,16 each number is of 2 bytes
#             TriggerCANMessage(
#                                                                         canid=0x18FF1581,
#                                                                         packet=data,
#                                                                         variable="frame"
#                                                                     )
#         data = [0xD0,0x07,0xC4,0x09,0xB8,0x0B,0xAC,0x0D]   ####Max cell voltage 4,8,12,16 each number is of 2 bytes
#         TriggerCANMessage(
#                                                                                 canid=0x18FF1581,
#                                                                                 packet=data,
#                                                                                 variable="frame"
#                                                                             )
        
#         time.sleep(0.1)
#     # End trip after 10 seconds
#     SingleCanHundred_EndTrip()

def HundredMilliSecondsProc():
    counter = 1
    direction = 1

    # 0x18FF0E81 value starts at 20
    value_0E81 = 23

    start_time = time.monotonic()


    # Start trip once
    SingleCanHundred_startTrip()

    # Run trip for 20 seconds
    while time.monotonic() - start_time < 30:

        elapsed = time.monotonic() - start_time

        # =========================================================
        # SPEED / BYTE 4
        # 1 -> 2 -> 3 -> ... -> 120 -> 119 -> ... -> 1
        # =========================================================
        byte4 = counter

        data = [0, 0, 0, byte4, 0, 0, 0, 0]

        TriggerCANMessage(
            canid=0x18FF0481,
            packet=data,
            variable="frame"
        )

        # Change direction at limits
        if counter == 120:
            direction = -1
        elif counter == 1:
            direction = 1

        counter += direction

        # =========================================================
        # 0x18FF0E81
        # 5th + 6th BYTE = VALUE
        #
        # 20 -> 21 -> 22 -> ... -> 299
        #
        # Byte 5 = Low Byte
        # Byte 6 = High Byte
        # =========================================================
        byte5 = value_0E81 & 0xFF
        byte6 = (value_0E81 >> 8) & 0xFF

        data = [
            0, 0, 0, 0,
            byte5,
            byte6,
            0, 0
        ]

        TriggerCANMessage(
            canid=0x18FF0E81,
            packet=data,
            variable="frame"
        )
        if value_0E81<290:
            value_0E81 += 1
        # =========================================================
        # 24-bit COUNTER -> bytes 6, 7, 8
        # =========================================================
        byte6 = counter & 0xFF
        byte7 = (counter >> 8) & 0xFF
        byte8 = (counter >> 16) & 0xFF

        data = [0, 0, 0, 0, 0, byte6, byte7, byte8]

        TriggerCANMessage(
            canid=0x18FF1C81,
            packet=data,
            variable="frame"
        )

        print(
            f"Elapsed = {elapsed:.2f}s, "
            f"Speed = {byte4}, "
            f"0E81 Value = {value_0E81}, "
            f"Counter = {counter}"
        )
        
        # =========================================================
        # BAT CURRENT
        # =========================================================
        data = [0, 0, 0, 0, 0xD6, 0x06, 0, 0]

        TriggerCANMessage(
            canid=0x18FF2081,
            packet=data,
            variable="frame"
        )

        # =========================================================
        # BAT TEMPERATURE
        # Before 5 sec  -> MAX temperature
        # After 5 sec   -> MIN temperature
        # =========================================================
        if elapsed < 5:
            data = [30, 40, 50, 60, 70, 80, 90, 100]
        else:
            data = [10, 9, 8, 7, 6, 5, 4, 3]

        TriggerCANMessage(
            canid=0x18FF1681,
            packet=data,
            variable="frame"
        )

        # =========================================================
        # CELL VOLTAGE GROUP 1
        # =========================================================
        if elapsed < 5:
            data = [
                0xE8, 0x03,
                0xDC, 0x05,
                0xD0, 0x07,
                0xC4, 0x09
            ]
        else:
            data = [
                0xD0, 0x07,
                0xC4, 0x09,
                0xB8, 0x0B,
                0xAC, 0x0D
            ]

        TriggerCANMessage(
            canid=0x18FF1281,
            packet=data,
            variable="frame"
        )

        # =========================================================
        # CELL VOLTAGE GROUP 2
        # =========================================================
        if elapsed < 5:
            data = [
                0xE8, 0x03,
                0xDC, 0x05,
                0xD0, 0x07,
                0xC4, 0x09
            ]
        else:
            data = [
                0xD0, 0x07,
                0xC4, 0x09,
                0xB8, 0x0B,
                0xAC, 0x0D
            ]

        TriggerCANMessage(
            canid=0x18FF1381,
            packet=data,
            variable="frame"
        )

        # =========================================================
        # CELL VOLTAGE GROUP 3
        # =========================================================
        if elapsed < 5:
            data = [
                0xE8, 0x03,
                0xDC, 0x05,
                0xD0, 0x07,
                0xC4, 0x09
            ]
        else:
            data = [
                0xD0, 0x07,
                0xC4, 0x09,
                0xB8, 0x0B,
                0xAC, 0x0D
            ]

        TriggerCANMessage(
            canid=0x18FF1481,
            packet=data,
            variable="frame"
        )

        # =========================================================
        # CELL VOLTAGE GROUP 4
        # =========================================================
        if elapsed < 5:
            data = [
                0xE8, 0x03,
                0xDC, 0x05,
                0xD0, 0x07,
                0xC4, 0x09
            ]
        else:
            data = [
                0xD0, 0x07,
                0xC4, 0x09,
                0xB8, 0x0B,
                0xAC, 0x0D
            ]

        TriggerCANMessage(
            canid=0x18FF1581,
            packet=data,
            variable="frame"
        )

        data = [3, 0, 0, 0, 0, 0, 0, 0]
        TriggerCANMessage(
                canid=0x18FF0481,
                packet=data,
                variable="frame"
            )

        # =========================================================
        # 100 ms cycle
        # =========================================================
        time.sleep(0.1)

    # =============================================================
    # END TRIP AFTER 20 SECONDS
    # =============================================================
    SingleCanHundred_EndTrip()



        
   
    # End trip
    SingleCanHundred_EndTrip()
    
if __name__=="__main__":
    
    t1 = threading.Thread(target=HundredMilliSecondsProc, args=())
t1.start()