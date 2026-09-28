

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
Index0D81 = 0
Index3EB = 0
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
def Multiframe0D81():
    print("Multiframe0D81 called...")
    global Index0D81, VIN_Trigger_Flag, VIN_Sent_Flag, VIN_Sent_Time

    if not VIN_Trigger_Flag:
        return

    payload = list(VIN_Base.encode())

    if Index0D81 * 7 < len(payload):
        chunk = payload[Index0D81*7 : (Index0D81*7)+7]

        while len(chunk) < 7:
            chunk.append(0)

        TriggerCANMessage(0x18FF0D81, chunk + [Index0D81], "VIN")

        Index0D81 += 1
    else:
        print("✅ VIN SENT:", VIN_Base)

        Index0D81 = 0
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
def IGN_0781():
    global Ignition_Status, Prev_Ignition_Status
    global VIN_Trigger_Flag, VIN_Sent_Flag, VIN_Sent_Time

    if Ignition_Status == 0:
        TriggerCANMessage(0x18FF0781, [0]*8, "IGN OFF")
        Ignition_Status = 1
    else:
        TriggerCANMessage(0x18FF0781, [0x04], "IGN ON")

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
def SingleCanTen():
    ids = [0x12B,0x150,0x118,0x11B,0x122,0x1B6,0x1B7,0x1B5,0x112]
    for i in ids:
        TriggerCANMessage(i, [1,2,3,4,5,6,7,8], "10ms")

def SingleCanTwenty():
    #print("SingleCanTwenty called...")
    for i in [0x18FF0481, 0x18FF00FE, 0x18FF0981, 0x18FF3381, 0x18FF05FE]:
        TriggerCANMessage(i, [1,2,3,4,5,6,7,8], "20ms")

def SingleCanThirty():
    for i in [0x244,0x274,0x245]:
        TriggerCANMessage(i, [1,2,3,4,5,6,7,8], "30ms")

def SingleCanFifty():
    for i in [0x18FF2181]:
        TriggerCANMessage(i, [1,2,3,4,5,6,7,8], "50ms")

def SingleCanHundred():
    TriggerCANMessage(0x18FF0687,[9,22,3,44,55,66,11,1],"100ms")
    TriggerCANMessage(0x18FF0587,[19,23,3,43,52,61,21,11],"100ms")
    TriggerCANMessage(0x18FF0F17, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF0B81, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF0181, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF0781, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF1481, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF1581, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF1681, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF1281, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF1381, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF1781, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF1881, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF2081, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF0581, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF02FE, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF1C81, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF03FE, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF0A81, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF0E81, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF0F81, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF0987, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF1081, [4, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF0C81, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF1181, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF1981, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF2681, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF2981, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF3081, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF3181, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF3281, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FE0781, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF3481, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF3581, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF3681, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    TriggerCANMessage(0x18FF0A8C, [19, 23, 3, 43, 52, 61, 21, 11], "100ms")
    




def SingleCanFiveHundred():
    for i in [0x18FF04FE,0x18FF1E81,0x18FF0881, 0x18FF1F17, 0x18FF0681]:
        TriggerCANMessage(i, [2]*8, "500ms")

def Thousand():
    for i in [0x18FF0081,0x18FF0117,0x18FF0217, 0x18FF0118, 0x18FF0119, 0x18FF01FE, 0x18FF08FE, 0x18FF0281, 0x18FF018C, 0x18FF028C, 0x18FF0B8C, 0x18FF0C8C, 0x18FF0D8C]:
        TriggerCANMessage(i, [1,2,3,4,5,6,7,8], "1sec")

# ---------------- MULTIFRAMES ----------------

Index18FF0381_u8 = 0
def Multiframe18FF0381():
    global Index18FF0381_u8
    #print("Multiframe18FF0381 called with index:", Index18FF0381_u8)
    if Index18FF0381_u8 == 0:
        data = [Index18FF0381_u8, 0x42, 0x32, 0x42, 0x47, 0x33, 0x5B, 0x30]
        TriggerCANMessage(canid=0x18FF0381, packet=data, variable="frame")
        Index18FF0381_u8 += 1
    elif Index18FF0381_u8 == 1:
        data = [Index18FF0381_u8, 0x38, 0x51, 0x4B, 0x46, 0x31, 0x31, 0x31]
        TriggerCANMessage(canid=0x18FF0381, packet=data, variable="frame")
        Index18FF0381_u8 = 0


Index18FF0787_u8 = 0
def Multiframe18FF0787():
    global Index18FF0787_u8

    if Index18FF0787_u8 == 0:
        data = [0x64, 0x02, 0x04, 0x06, 0x01, 0x05, 0x5A, Index18FF0787_u8 << 6]
        TriggerCANMessage(canid=0x18FF0787, packet=data, variable="frame")
        Index18FF0787_u8 += 1
    elif Index18FF0787_u8 == 1:
        data = [0x32, 0x01, 0x11, 0x22, 0x33, 0x04, 0x44, Index18FF0787_u8 << 6]
        TriggerCANMessage(canid=0x18FF0787, packet=data, variable="frame")
        Index18FF0787_u8 += 1
    elif Index18FF0787_u8 == 2:
        data = [0x30, 0x02, 0x55, 0x66, 0x76, 0x07, 0x89, Index18FF0787_u8 << 6]
        TriggerCANMessage(canid=0x18FF0787, packet=data, variable="frame")
        Index18FF0787_u8 = 0

Index18FF0887_u8 = 0
def Multiframe18FF0887():
    global Index18FF0887_u8

    if Index18FF0887_u8 == 0:
        data = [0x4E, 0x42, 0x32, 0x42, 0x47, 0x33, 0x5B, Index18FF0887_u8]
        TriggerCANMessage(canid= 0x18FF0887, packet=data, variable="frame")
        Index18FF0887_u8 += 1
    elif Index18FF0887_u8 == 1:
        data = [0x42, 0x38, 0x51, 0x4B, 0x46, 0x31, 0x31, Index18FF0887_u8]
        TriggerCANMessage(canid= 0x18FF0887, packet=data, variable="frame")
        Index18FF0887_u8 += 1
    elif Index18FF0887_u8 == 2:
        data = [0x31, 0x31, 0x31, 0x10, 0x20, 0x30, 0x40, Index18FF0887_u8]
        TriggerCANMessage(canid= 0x18FF0887, packet=data, variable="frame")
        Index18FF0887_u8 = 0


Index18FF0881_u8 = 0
def Multiframe18FF0881():
    global Index18FF0881_u8

    if Index18FF0881_u8 == 0:
        data = [Index18FF0881_u8, 0x42, 0x32, 0x42, 0x47, 0x33, 0x5B, 0x30]
        TriggerCANMessage(canid=0x18FE0881, packet=data, variable="frame")
        Index18FF0881_u8 += 1
    elif Index18FF0881_u8 == 1:
        data = [Index18FF0881_u8, 0x38, 0x51, 0x4B, 0x46, 0x31, 0x31, 0x31]
        TriggerCANMessage(canid=0x18FE0881, packet=data, variable="frame")
        Index18FF0881_u8 = 0

Index18FF2781_u8 = 0
def Multiframe18FF2781():
    global Index18FF2781_u8

    if Index18FF2781_u8 == 0:
        data = [0x4E, 0x42, 0x32, 0x42, 0x47, 0x33, 0x5B, Index18FF2781_u8]
        TriggerCANMessage(canid=0x18FF2781, packet=data, variable="frame")
        Index18FF2781_u8 += 1
    elif Index18FF2781_u8 == 1:
        data = [0x32, 0x01, 0x11, 0x22, 0x33, 0x04, 0x44, Index18FF2781_u8 << 6]
        TriggerCANMessage(canid=0x18FF2781, packet=data, variable="frame")
        Index18FF2781_u8 += 1
    elif Index18FF2781_u8 == 2:
        data = [0x30, 0x02, 0x55, 0x66, 0x76, 0x07, 0x89, Index18FF2781_u8 << 6]
        TriggerCANMessage(canid=0x18FF2781, packet=data, variable="frame")
        Index18FF2781_u8 = 0

Index18FF2881_u8 = 0
def Multiframe18FF2881():
        global Index18FF2881_u8

        if Index18FF2881_u8 == 0:
            data = [0x4E, 0x42, 0x32, 0x42, 0x47, 0x33, 0x5B, Index18FF2881_u8]
            TriggerCANMessage(canid=0x18FF2881, packet=data, variable="frame")
            Index18FF2881_u8 += 1
        elif Index18FF2881_u8 == 1:
            data = [0x42, 0x38, 0x51, 0x4B, 0x46, 0x31, 0x31, Index18FF2881_u8]
            TriggerCANMessage(canid=0x18FF2881, packet=data, variable="frame")
            Index18FF2881_u8 += 1
        elif Index18FF2881_u8 == 2:
            data = [0x31, 0x31, 0x31, 0x10, 0x20, 0x30, 0x40, Index18FF2881_u8]
            TriggerCANMessage(canid=0x18FF2881, packet=data, variable="frame")
            Index18FF2881_u8 = 0


    #---------------- THREADS ----------------

def TwentyMs():
    while True:
        time.sleep(0.02)
        SingleCanTwenty()

def ThirtyMs():
    while True:
        time.sleep(0.03)
        SingleCanThirty()

def FiftyMs():
    while True:
        time.sleep(0.05)
        SingleCanFifty()


def HundredMs():
    while True:
        time.sleep(0.1)
        SingleCanHundred()
        Multiframe18FF0887()
        Multiframe18FF2781()
        Multiframe18FF2881()
        Multiframe18FF0787()


def FiveHundredMs():
    while True:
        time.sleep(0.5)

        IGN_0781()

        if VIN_Trigger_Flag:
            Multiframe0D81()

        SingleCanFiveHundred()
        Multiframe18FF0881()
        Multiframe18FF0381()

def OneSecond():
    global Odometer, SOC_u16

    while True:
        time.sleep(1)

        Thousand()

        Odometer += 1
        if SOC_u16 > 0:
            SOC_u16 -= 1

        print(f"Odo: {Odometer} | SOC: {SOC_u16}")

# ---------------- START ----------------

threading.Thread(target=TwentyMs, daemon=True).start()
threading.Thread(target=ThirtyMs, daemon=True).start()
threading.Thread(target=HundredMs, daemon=True).start()
threading.Thread(target=FiveHundredMs, daemon=True).start()
threading.Thread(target=OneSecond, daemon=True).start()
threading.Thread(target=FiftyMs, daemon=True).start()


# ---------------- MAIN LOOP ----------------
while True:
    time.sleep(1)




