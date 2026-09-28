import can
import time
import threading
from datetime import datetime

# ---------------- CAN SETUP ----------------
bus = can.interface.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
print("PCAN connected!")

# ---------------- GLOBALS ----------------
extension = True

# Vehicle Signals
VehicleMode = 2
VehicleSpeed_u16 = 0
SOC_u16 = 80
Odometer = 0
Sts_Ign = 0

# VIN CONTROL
VIN_Base = 'ACCDEV02261111132'
VIN_Increment_Count = 0
VIN_Trigger_Flag = False
VIN_Sent_Flag = False
VIN_Sent_Time = 0

# IGN
Ignition_Status = 0
Prev_Ignition_Status = 0

# Indexes
Index0E81 = 0
Index3EB = 0
Index1181 = 0
Index3EC14 = 0
Index3EC14_u8 = 0
Index3EC17_u8 = 0
# ---------------- CAN SEND ----------------
def TriggerCANMessage(canid, packet, variable):
    msg = can.Message(arbitration_id=canid, data=packet, is_extended_id=True)
    try:
        bus.send(msg)
    except:
        print("Send Failed:", variable)

# ---------------- VIN MULTIFRAME ----------------
def Multiframe0E81():
    global Index0E81, VIN_Trigger_Flag, VIN_Sent_Flag, VIN_Sent_Time

    if not VIN_Trigger_Flag:
        return

    payload = list(VIN_Base.encode())

    if Index0E81 * 7 < len(payload):
        chunk = payload[Index0E81*7 : (Index0E81*7)+7]

        while len(chunk) < 7:
            chunk.append(0)

        TriggerCANMessage(0x18FF0E81, chunk + [Index0E81], "VIN")

        Index0E81 += 1
    else:
        print("✅ VIN SENT:", VIN_Base)

        Index0E81 = 0
        VIN_Trigger_Flag = False
        VIN_Sent_Flag = True
        VIN_Sent_Time = time.time()

        increment_vin()

def increment_vin():
    global VIN_Base, VIN_Increment_Count

    if VIN_Increment_Count >= 10:
        print("VIN LOCKED:", VIN_Base)
        return

    prefix = VIN_Base[:-3]
    number = int(VIN_Base[-3:]) + 1
    VIN_Base = f"{prefix}{number:03d}"

    VIN_Increment_Count += 1
    print("Next VIN:", VIN_Base)

# ---------------- IGN ----------------
def IGN_1481():
    global Ignition_Status, Prev_Ignition_Status
    global VIN_Trigger_Flag, VIN_Sent_Flag, VIN_Sent_Time

    if Ignition_Status == 0:
        TriggerCANMessage(0x18FF1481, [0]*8, "IGN OFF")
        Ignition_Status = 1
    else:
        TriggerCANMessage(0x18FF1481, [0x0]*7+[1], "IGN ON")

    if Prev_Ignition_Status == 0 and Ignition_Status == 1:
        print("🔥 IGN ON → VIN START")
        VIN_Trigger_Flag = True
        VIN_Sent_Flag = False

    if VIN_Sent_Flag and (time.time() - VIN_Sent_Time >= 30):
        print("⏱ IGN OFF after 30 sec")
        Ignition_Status = 0
        VIN_Sent_Flag = False

    Prev_Ignition_Status = Ignition_Status

# ---------------- ORIGINAL SIGNAL FUNCTIONS ----------------


def SingleCanFifty():
    for i in [0x18FF0403,0x18FF0203,0x18FF0003, 0x18FF0103]:
        TriggerCANMessage(i, [1,2,3,4,5,6,7,8], "50ms")

def SingleCanHundred():
    TriggerCANMessage(0x18FF0687,[9,22,3,44,55,66,11,1],"100ms")
    TriggerCANMessage(0x18FF0587,[19,23,3,43,52,61,21,11],"100ms")
    TriggerCANMessage(0x18FF0F17,[19,23,3,43,52,61,21,11],"100ms")
    TriggerCANMessage(0x18FF0C81,[19,23,3,43,52,61,21,11],"100ms")
    TriggerCANMessage(0x18FF0A81,[19,23,3,43,52,61,21,11],"100ms")
    TriggerCANMessage(0x18FF0D81,[19,23,3,43,52,61,21,11],"100ms")
    TriggerCANMessage(0x18FF0981,[19,23,3,43,52,61,21,11],"100ms")
    TriggerCANMessage(0x18FF1281,[19,23,3,43,52,61,21,11],"100ms")
    TriggerCANMessage(0x18FF1381,[19,23,3,43,52,61,21,11],"100ms")
    TriggerCANMessage(0x18FF1481,[19,23,3,43,52,61,21,11],"100ms")
    TriggerCANMessage(0x18FF1581,[19,23,3,43,52,61,21,11],"100ms")
    TriggerCANMessage(0x18FF1681,[19,23,3,43,52,61,21,11],"100ms")
    TriggerCANMessage(0x18FF0487,[19,23,3,43,52,61,21,11],"100ms")
    TriggerCANMessage(0x18FF0987,[19,23,3,43,52,61,21,11],"100ms")
    TriggerCANMessage(0x18FF0503,[19,23,3,43,52,61,21,11],"100ms")
    TriggerCANMessage(0x18FF1081,[19,23,3,43,52,61,21,11],"100ms")
    TriggerCANMessage(0x18FF0A8C,[19,23,3,43,52,61,21,11],"100ms")
    TriggerCANMessage(0x18FF1181,[19,23,3,43,52,61,21,11],"100ms")
    
    

    


Index18FF0887_u8 = 0
def Multiframe18FF0887():
      global Index18FF0887_u8
      
      if Index18FF0887_u8 == 0:
            data = [0x4E, 0x42, 0x32, 0x42, 0x47, 0x33, 0x5B, Index18FF0887_u8]
            TriggerCANMessage(canid=0x18FF0887, packet=data, variable= "frame")
            Index18FF0887_u8 +=1
      elif Index18FF0887_u8 == 1:
            data = [0x42, 0x38, 0x51, 0x4B, 0x46, 0x31, 0x31, Index18FF0887_u8]
            TriggerCANMessage(canid=0x18FF0887, packet=data, variable= "frame")
            Index18FF0887_u8 +=1
      elif Index18FF0887_u8 == 2:
            data = [0x31, 0x31, 0x31, 0x10, 0x20, 0x30, 0x40, Index18FF0887_u8]
            TriggerCANMessage(canid=0x18FF0887, packet=data, variable= "frame")
            Index18FF0887_u8 = 0

# Index18FF0881_u8 = 0

# def Multiframe18FF0881():
#     global Index18FF0881_u8

#     if Index18FF0881_u8 == 0:
#         data = [0, 0x4E, 0x42, 0x32, 0x42, 0x47, 0x33, 0x5B]
#         TriggerCANMessage(canid=0x18FF0881, packet=data, variable="frame")

#     elif Index18FF0881_u8 == 1:
#         data = [1, 0x42, 0x38, 0x51, 0x4B, 0x46, 0x31, 0x31]
#         TriggerCANMessage(canid=0x18FF0881, packet=data, variable="frame")

#     elif Index18FF0881_u8 == 2:
#         data = [2, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47]
#         TriggerCANMessage(canid=0x18FF0881, packet=data, variable="frame")

#     elif Index18FF0881_u8 == 3:
#         data = [3, 0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70]
#         TriggerCANMessage(canid=0x18FF0881, packet=data, variable="frame")

#     elif Index18FF0881_u8 == 4:
#         data = [4, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77]
#         TriggerCANMessage(canid=0x18FF0881, packet=data, variable="frame")

#     elif Index18FF0881_u8 == 5:
#         data = [5, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00]
#         TriggerCANMessage(canid=0x18FF0881, packet=data, variable="frame")

#     elif Index18FF0881_u8 == 6:
#         data = [6, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07]
#         TriggerCANMessage(canid=0x18FF0881, packet=data, variable="frame")
#         Index18FF0881_u8 = -1  # reset after last frame

#     Index18FF0881_u8 += 1
# Index18FF0881_u8 = 0

##### For In range temperature 8°C to 10°C for 15 seconds each, then repeat#############

Index18FF0881_u8 = 0
temp_counter = 0


def Multiframe18FF0881():
    global Index18FF0881_u8
    global temp_counter

    print(f"\nIndex18FF0881_u8 = {Index18FF0881_u8}")

    # Send 8°C for 15 seconds, then 10°C for 15 seconds
    if temp_counter < 15:
        temp_raw = 80       # 8°C (8*10)
    elif temp_counter < 30:
        temp_raw = 100      # 10°C (10*10)
    else:
        temp_counter = 0
        temp_raw = 80

    temp_lsb = temp_raw & 0xFF
    temp_msb = (temp_raw >> 8) & 0xFF

    if Index18FF0881_u8 == 0:
        data = [0, 0x4E, 0x42, 0x32, 0x42, 0x47, 0x33, 0x5B]

    elif Index18FF0881_u8 == 1:
        data = [1, 0x42, 0x38, 0x51, 0x4B, 0x46, 0x31, 0x31]

    elif Index18FF0881_u8 == 2:
        data = [2, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47]

    elif Index18FF0881_u8 == 3:
        data = [3, 0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70]

    elif Index18FF0881_u8 == 4:
        data = [4, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77]

    elif Index18FF0881_u8 == 5:
        # CELLTEMP1 = current temperature
        # CELLTEMP2 = current temperature
        data = [
            5,
            0xAA,
            0xBB,
            temp_lsb, temp_msb,   # Temp1
            temp_lsb, temp_msb,   # Temp2
            0x00
        ]

    elif Index18FF0881_u8 == 6:
        # CELLTEMP3 = current temperature
        # CELLTEMP4 = current temperature
        data = [
            6,
            temp_lsb, temp_msb,   # Temp3
            temp_lsb, temp_msb,   # Temp4
            0x05,
            0x06,
            0x07
        ]

    else:
        Index18FF0881_u8 = 0
        return

    print(f"Temperature Raw = {temp_raw}")
    print(f"CAN ID : {hex(0x18FF0881)}")
    print("Data   :", [hex(b) for b in data])

    TriggerCANMessage(
        canid=0x18FF0881,
        packet=data,
        variable="frame"
    )

    print("Frame transmitted.")

    if Index18FF0881_u8 >= 6:
        Index18FF0881_u8 = 0
        temp_counter += 1
    else:
        Index18FF0881_u8 += 1

    print(f"Next Index18FF0881_u8 = {Index18FF0881_u8}")
    print(f"Temperature timer = {temp_counter}s")



Index18FF0881_u8 = 0
voltage_test_counter = 0


def Multiframe18FF0881():
    global Index18FF0881_u8
    global voltage_test_counter

    print(f"\nIndex18FF0881_u8 = {Index18FF0881_u8}")

    # Send MIN=3500 and MAX=20000 for 10 seconds
    if voltage_test_counter < 60:
        min_voltage = 1000
        max_voltage = 4000
    # else:
    #     # Normal value after 10 sec
    #     min_voltage = 5000
    #     max_voltage = 5000

    min_lsb = min_voltage & 0xFF
    min_msb = (min_voltage >> 8) & 0xFF

    max_lsb = max_voltage & 0xFF
    max_msb = (max_voltage >> 8) & 0xFF


    if Index18FF0881_u8 == 0:
        # CELLVOLTAGE1,2,3

        data = [
            0,
            min_lsb, min_msb,   # CELLVOLTAGE1 = 3500
            min_lsb, min_msb,   # CELLVOLTAGE2 = 3500
            max_lsb, max_msb,   # CELLVOLTAGE3 = 20000
        ]

    elif Index18FF0881_u8 == 1:
        # CELLVOLTAGE4,5,6

        data = [
            1,
            min_lsb, min_msb,   # CELLVOLTAGE4 = 3500
            min_lsb, min_msb,   # CELLVOLTAGE5 = 3500
            max_lsb, max_msb,   # CELLVOLTAGE6 = 20000
        ]

    elif Index18FF0881_u8 == 2:
        # CELLVOLTAGE7,8,9

        data = [
            2,
            min_lsb, min_msb,   # CELLVOLTAGE7
            min_lsb, min_msb,   # CELLVOLTAGE8
            max_lsb, max_msb,   # CELLVOLTAGE9
        ]

    elif Index18FF0881_u8 == 3:
        # CELLVOLTAGE10,11,12

        data = [
            3,
            min_lsb, min_msb,   # CELLVOLTAGE10
            min_lsb, min_msb,   # CELLVOLTAGE11
            max_lsb, max_msb,   # CELLVOLTAGE12
        ]

    elif Index18FF0881_u8 == 4:
        # CELLVOLTAGE13,14,15

        data = [
            4,
            min_lsb, min_msb,   # CELLVOLTAGE13
            min_lsb, min_msb,   # CELLVOLTAGE14
            max_lsb, max_msb,   # CELLVOLTAGE15
        ]

    elif Index18FF0881_u8 == 5:
        # CELLVOLTAGE16

        data = [
            5,
            max_lsb, max_msb,   # CELLVOLTAGE16 = 2000
            0x00,
            0x00,
            0x00,
            0x00,
            0x00
        ]

    elif Index18FF0881_u8 == 6:
        data = [
            6,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00
        ]

    else:
        Index18FF0881_u8 = 0
        return


    print(f"MIN Voltage = {min_voltage}")
    print(f"MAX Voltage = {max_voltage}")

    print(f"CAN ID : {hex(0x18FF0881)}")
    print("Data   :", [hex(b) for b in data])


    TriggerCANMessage(
        canid=0x18FF0881,
        packet=data,
        variable="frame"
    )

    print("Frame transmitted.")


    if Index18FF0881_u8 >= 6:
        Index18FF0881_u8 = 0
        voltage_test_counter += 1
    else:
        Index18FF0881_u8 += 1


    print(f"Next Index18FF0881_u8 = {Index18FF0881_u8}")
    print(f"Voltage Test Time = {voltage_test_counter}s")

Index18FF0787_u8 = 0

def Multiframe18FF0787():
    global Index18FF0787_u8

    if Index18FF0787_u8 == 0:
        data = [0x64, 0x02, 0x04, 0x06, 0x01, 0x05, 0x5A, (Index18FF0787_u8 << 6)]
        TriggerCANMessage(canid=0x18FF0787, packet=data, variable="frame")
        Index18FF0787_u8 = 1

    elif Index18FF0787_u8 == 1:
        data = [0x32, 0x01, 0x11, 0x22, 0x33, 0x04, 0x44, (Index18FF0787_u8 << 6)]
        TriggerCANMessage(canid=0x18FF0787, packet=data, variable="frame")
        Index18FF0787_u8 = 2

    elif Index18FF0787_u8 == 2:
        data = [0x30, 0x02, 0x55, 0x66, 0x76, 0x07, 0x89, (Index18FF0787_u8 << 6)]
        TriggerCANMessage(canid=0x18FF0787, packet=data, variable="frame")
        Index18FF0787_u8 = 0
    

def SingleCanFiveHundred():
    #print("SingleCanFiveHundred called")
    for i in [0X18FF0B81,0x18FF0F81,0x18FF03C3]:
        TriggerCANMessage(i, [2]*8, "500ms")

def Thousand():
    #print("Thousand function called")
    for i in [0x18FF018C,0x18FF028C,0x18FF0B8C, 0x18FF0C8C, 0x18FF0D8C]:
        TriggerCANMessage(i, [1,2,3,4,5,6,7,8], "1sec")

# ---------------- MULTIFRAMES ----------------
def Multiframe3EB():
    global Index3EB
    data = [Index3EB,1,1,1,1,1,1,Index3EB<<6]
    TriggerCANMessage(0x3EB, data, "3EB")
    Index3EB = (Index3EB+1)%3

# def Multiframe3EC_14():
#     global Index3EC14_u8

#     payload = [0x11] * 102   # total data

#     if Index3EC14_u8 < 14:   # 0 → 16 (17 frames)
#         start = Index3EC14_u8 * 6
#         end = start + 6

#         last_byte = (Index3EC14_u8 << 4) & 0xFF

#         data = (
#             [Index3EC14_u8] +      # Byte 0 → frame index
#             payload[start:end] +   # 6 bytes
#             [last_byte]            # Byte 7
#         )

#         # ✅ FIX: standard frame
#         TriggerCANMessage(0x3EC, data, False)

#         Index3EC14_u8 += 1

#         # Reset after 17 frames
#         if Index3EC14_u8 >= 14:
#             Index3EC14_u8 = 0

def Multiframe3EC_17():
    global Index3EC17_u8

    payload = [0x11] * 102   # 17 frames × 6 bytes

    start = Index3EC17_u8 * 6
    chunk = payload[start:start + 6]

    # Ensure always 6 bytes
    while len(chunk) < 6:
        chunk.append(0x00)

    last_byte = (Index3EC17_u8 << 4) & 0xFF

    data = [Index3EC17_u8] + chunk + [last_byte]

    TriggerCANMessage(0x3EC, data, "3EC_17")

    # Loop 0 → 16 (17 frames)
    Index3EC17_u8 = (Index3EC17_u8 + 1) % 17
    
seed = 0x67
def Immo():
    global seed
    
    for msgs in bus:
        if msgs.arbitration_id == 0x3FC:
            print("message received for immo")

            if msgs.data[2] == 0x01:
                time.sleep(0.55)
                TriggerCANMessage(
                    canid=0x18FF0681,
                    packet=[0x00, 0x01, 0, 0x54, 0x2D, 0x12, seed, 0],
                    variable="Immo response"
                )

                print(f"immo seed send: {hex(seed)}")

                # increment seed
                seed += 1

                # keep it within 1 byte (0x00 - 0xFF)
                if seed > 0xFF:
                    seed = 0x00
    
#---------------- THREADS ----------------

def FiftyMs():
    #print("50ms thread started")
    while True:
        time.sleep(0.05)
        SingleCanFifty()

def HundredMs():
    #print("100ms thread started")
    while True:
        time.sleep(0.1)
        # SingleCanHundred()
        # Multiframe18FF0887()
        Multiframe18FF0881()
        # Multiframe18FF0787()
        
        

def FiveHundredMs():
    #print("500ms thread started")
    while True:
        time.sleep(0.5)

        IGN_1481()

        if VIN_Trigger_Flag:
            Multiframe0E81()

        SingleCanFiveHundred()

def OneSecond():
    global Odometer, SOC_u16

    #print("1sec thread started")
    while True:
        time.sleep(1)

        Thousand()

        Odometer += 1
        if SOC_u16 > 0:
            SOC_u16 -= 1

        print(f"Odo: {Odometer} | SOC: {SOC_u16}")



# ---------------- START ----------------
threading.Thread(target=FiftyMs, daemon=True).start()
threading.Thread(target=HundredMs, daemon=True).start()
threading.Thread(target=FiveHundredMs, daemon=True).start()
threading.Thread(target=OneSecond, daemon=True).start()
threading.Thread(target=Immo, daemon=True).start()
# ---------------- MAIN LOOP ----------------
while True:
    time.sleep(1)