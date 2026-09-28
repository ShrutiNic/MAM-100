

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
Index3C0 = 0
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
def Multiframe3C0():
    global Index3C0, VIN_Trigger_Flag, VIN_Sent_Flag, VIN_Sent_Time

    if not VIN_Trigger_Flag:
        return

    payload = list(VIN_Base.encode())

    if Index3C0 * 7 < len(payload):
        chunk = payload[Index3C0*7 : (Index3C0*7)+7]

        while len(chunk) < 7:
            chunk.append(0)

        TriggerCANMessage(0x3C0, chunk + [Index3C0], "VIN")

        Index3C0 += 1
    else:
        print("✅ VIN SENT:", VIN_Base)

        Index3C0 = 0
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
def IGN_336():
    global Ignition_Status, Prev_Ignition_Status
    global VIN_Trigger_Flag, VIN_Sent_Flag, VIN_Sent_Time

    if Ignition_Status == 0:
        TriggerCANMessage(0x336, [0]*8, "IGN OFF")
        Ignition_Status = 1
    else:
        TriggerCANMessage(0x336, [0x0C]+[0]*7, "IGN ON")

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
    for i in [0x337,0x272,0x259]:
        TriggerCANMessage(i, [1,2,3,4,5,6,7,8], "20ms")

def SingleCanThirty():
    for i in [0x244,0x274,0x245]:
        TriggerCANMessage(i, [1,2,3,4,5,6,7,8], "30ms")

def SingleCanHundred():
    TriggerCANMessage(0x3D3, 0x3D2, 0x3E8, 0x3E9, 0x3EA, 0x3EB, 0x3EC, 0x5C3, 0x476, 0x3DD, 0x3DF, 0x5C7, 0x300, 0x3D7, 0x3DA, 0x428, 0x3D8, 0x3DB, 0x3DC, 0x140, 0x3FA, 0x5C9, 0x338, 0x336, 0x335, 0x3F9, 0x333, 0x134, 0x3E1[9,22,3,44,55,66,11,1],"100ms")
    
def SingleCanFiveHundred():
    for i in [0x5CA,0x5C6,0x5C4,0x5C8,0x5C2,0x5CC,0x5CD]:
        TriggerCANMessage(i, [2]*8, "500ms")

def Thousand():
    for i in [0x60A,0x60B,0x3C4]:
        TriggerCANMessage(i, [1,2,3,4,5,6,7,8], "1sec")

# ---------------- MULTIFRAMES ----------------
def Multiframe3EB():
    global Index3EB
    data = [Index3EB,1,1,1,1,1,1,Index3EB<<6]
    TriggerCANMessage(0x3EB, data, "3EB")
    Index3EB = (Index3EB+1)%3

def Multiframe3EC_14():
    global Index3EC14_u8

    payload = [0x11] * 102   # total data

    if Index3EC14_u8 < 14:   # 0 → 16 (17 frames)
        start = Index3EC14_u8 * 6
        end = start + 6

        last_byte = (Index3EC14_u8 << 4) & 0xFF

        data = (
            [Index3EC14_u8] +      # Byte 0 → frame index
            payload[start:end] +   # 6 bytes
            [last_byte]            # Byte 7
        )

        # ✅ FIX: standard frame
        TriggerCANMessage(0x3EC, data, False)

        Index3EC14_u8 += 1

        # Reset after 17 frames
        if Index3EC14_u8 >= 14:
            Index3EC14_u8 = 0


    
#---------------- THREADS ----------------
def TenMs():
    while True:
        time.sleep(0.01)
        SingleCanTen()

def TwentyMs():
    while True:
        time.sleep(0.02)
        SingleCanTwenty()

def ThirtyMs():
    while True:
        time.sleep(0.03)
        SingleCanThirty()

def HundredMs():
    while True:
        time.sleep(0.1)
        SingleCanHundred()
        Multiframe3EB()
        Multiframe3EC_14()
        

def FiveHundredMs():
    while True:
        time.sleep(0.5)

        IGN_336()

        if VIN_Trigger_Flag:
            Multiframe3C0()

        SingleCanFiveHundred()

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
threading.Thread(target=TenMs, daemon=True).start()
threading.Thread(target=TwentyMs, daemon=True).start()
threading.Thread(target=ThirtyMs, daemon=True).start()
threading.Thread(target=HundredMs, daemon=True).start()
threading.Thread(target=FiveHundredMs, daemon=True).start()
threading.Thread(target=OneSecond, daemon=True).start()

# ---------------- MAIN LOOP ----------------
while True:
    time.sleep(1)