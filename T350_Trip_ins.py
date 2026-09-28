# import can
# import time
# import threading

# # ---------------- CAN INIT ----------------
# extension = True
# bus = can.interface.Bus(
#     interface='pcan',
#     channel='PCAN_USBBUS1',
#     bitrate=500000
# )

# # ---------------- GLOBAL STATE ----------------
# Ignition_Status = 1
# ODO = 1

# # ---------------- SPEED MODEL ---------------- 
# VehicleSpeed_kmph = 40
# VehicleSpeed_mps = VehicleSpeed_kmph / 3.6

# TargetSpeed_kmph = 10

# DECEL_MS2 = 2.8   # physical limit (>2 m/s² requirement satisfied)
# DT = 0.1

# # ---------------- IGNITION TIMER ----------------
# ignition_start_time = time.time()
# IGNITION_ON_DURATION = 60

# # ---------------- MULTI FRAME INDEX ----------------
# Index18FF0881_u8 = 0



# # ---------------- TRANSMIT FUNCTION ----------------
# def TriggerCANMessage(canid, packet, variable=""):
#     msg = can.Message(
#         arbitration_id=canid,
#         data=packet,
#         is_extended_id=extension
#     )
#     print(f"{variable} -> {hex(canid)} {packet}")

#     try:
#         bus.send(msg)
#     except can.CanError:
#         print("CAN send failed")


# # ---------------- SIGNAL FRAMES ----------------
# def IGN_Frame():
#     return [0x03, 0, 0, 0, 0, 0, 0, 0x11] if Ignition_Status == 1 else [0]*8


# def ChargePlugFrame():
#     return [0x00, 0x80, 0, 0, 0, 0, 0, 0]


# def DriveModeFrame():
#     return [0x00, 0x00, 0x03, 0, 0, 0, 0, 0]


# def ODO_Frame():
#     global ODO
#     data = [
#         ODO & 0xFF,
#         (ODO >> 8) & 0xFF,
        
#         (ODO >> 16) & 0xFF,
#         0, 0, 0, 0, 0
#     ]
#     ODO += 1
#     print(f"ODO Frame: {data}, ODO Value: {ODO}")
#     return data


# # ---------------- MULTIFRAME ----------------
# def Multiframe18FF0881():
#     global Index18FF0881_u8

#     frames = [
#         [0x00, 0x4E, 0x42, 0x32, 0x42, 0x47, 0x33, 0x5B],
#         [0x01, 0x42, 0x38, 0x51, 0x4B, 0x46, 0x31, 0x31],
#         [0x02, 0x31, 0x31, 0x31, 0x01, 0x02, 0x03, 0x04],
#         [0x03, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x11],
#         [0x04, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18],
#         [0x05, 0x19, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25],
#         [0x06, 0x26, 0x27, 0x28, 0x29, 0x30, 0x31, 0x32],
#     ]

#     TriggerCANMessage(0x18FF0881, frames[Index18FF0881_u8], "MF 0881")
#     Index18FF0881_u8 = (Index18FF0881_u8 + 1) % len(frames)


# # ---------------- 100ms TASK ----------------
# def Tx_100ms():
#     global VehicleSpeed_mps, VehicleSpeed_kmph, Ignition_Status, ignition_start_time

#     while True:
#         time.sleep(DT)

#         # ---------------- CONTROL LAYER ----------------
#         target_mps = TargetSpeed_kmph / 3.6
#         error = VehicleSpeed_mps - target_mps

#         if error > 0:
#             commanded_decel = min(DECEL_MS2, error / DT)
#         else:
#             commanded_decel = 0

#         # ---------------- PHYSICS LAYER ----------------
#         VehicleSpeed_mps -= commanded_decel * DT

#         if VehicleSpeed_mps < target_mps:
#             VehicleSpeed_mps = target_mps

#         VehicleSpeed_kmph = VehicleSpeed_mps * 3.6


#         # ---------------- MULTIFRAME ----------------
#         Multiframe18FF0881()

#         # ---------------- CAN FRAMES ----------------
#         TriggerCANMessage(0x18FF1481, IGN_Frame(), "IGN")
#         TriggerCANMessage(0x18FF1581, ChargePlugFrame(), "CHARGE")
#         TriggerCANMessage(0x18FF0C81, DriveModeFrame(), "DRIVE")
#         TriggerCANMessage(0x18FF0F17, ODO_Frame(), "ODO")

#         # ---------------- IGNITION TIMER ----------------
#         if Ignition_Status == 1:
#             if time.time() - ignition_start_time > IGNITION_ON_DURATION:
#                 Ignition_Status = 0
#                 print("Ignition turned OFF automatically")


# # ---------------- MAIN ----------------
# if __name__ == "__main__":
#     print("CAN Simulation Started (Hybrid Speed Control + Physics Model)")

#     t1 = threading.Thread(target=Tx_100ms)
#     t1.start()


import can
import time
import threading

# ---------------- CAN INIT ----------------
extension = True

bus = can.interface.Bus(
    interface='pcan',
    channel='PCAN_USBBUS1',
    bitrate=500000
)

# ---------------- GLOBAL STATE ----------------
Ignition_Status = 1
ODO = 1

# ---------------- SPEED MODEL ----------------
INITIAL_SPEED_KMPH = 40
TARGET_SPEED_KMPH = 10

VehicleSpeed_kmph = INITIAL_SPEED_KMPH
VehicleSpeed_mps = VehicleSpeed_kmph / 3.6

TARGET_SPEED_MPS = TARGET_SPEED_KMPH / 3.6

# 40 -> 10 km/h in exactly 3 sec
RAMP_TIME_SEC = 3.0
DECEL_MS2 = (
    (INITIAL_SPEED_KMPH / 3.6) -
    (TARGET_SPEED_KMPH / 3.6)
) / RAMP_TIME_SEC

DT = 0.1

# ---------------- IGNITION TIMER ----------------
ignition_start_time = time.time()
IGNITION_ON_DURATION = 60

# ---------------- MULTI FRAME INDEX ----------------
Index18FF0881_u8 = 0

# ---------------- TRANSMIT FUNCTION ----------------
def TriggerCANMessage(canid, packet, variable=""):
    msg = can.Message(
        arbitration_id=canid,
        data=packet,
        is_extended_id=extension
    )

    print(f"{variable} -> {hex(canid)} {packet}")

    try:
        bus.send(msg)

    except can.CanError:
        print("CAN send failed")


# ---------------- SIGNAL FRAMES ----------------
def IGN_Frame():
    if Ignition_Status == 1:
        return [0x03, 0, 0, 0, 0, 0, 0, 0x11]

    return [0] * 8


def ChargePlugFrame():
    return [0x00, 0x80, 0, 0, 0, 0, 0, 0]


def DriveModeFrame():
    return [0x00, 0x00, 0x03, 0, 0, 0, 0, 0]


def ODO_Frame():
    global ODO

    data = [
        ODO & 0xFF,
        (ODO >> 8) & 0xFF,
        (ODO >> 16) & 0xFF,
        0,
        0,
        0,
        0,
        0
    ]

    ODO += 1

    print(f"ODO Frame: {data}, ODO Value: {ODO}")

    return data


# ---------------- MULTIFRAME ----------------
def Multiframe18FF0881():
    global Index18FF0881_u8

    frames = [
        [0x00, 0x4E, 0x42, 0x32, 0x42, 0x47, 0x33, 0x5B],
        [0x01, 0x42, 0x38, 0x51, 0x4B, 0x46, 0x31, 0x31],
        [0x02, 0x31, 0x31, 0x31, 0x01, 0x02, 0x03, 0x04],
        [0x03, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x11],
        [0x04, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18],
        [0x05, 0x19, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25],
        [0x06, 0x26, 0x27, 0x28, 0x29, 0x30, 0x31, 0x32],
    ]

    TriggerCANMessage(
        0x18FF0881,
        frames[Index18FF0881_u8],
        "MF 0881"
    )

    Index18FF0881_u8 = (
        Index18FF0881_u8 + 1
    ) % len(frames)


# ---------------- 100ms TASK ----------------
def Tx_100ms():
    global VehicleSpeed_mps
    global VehicleSpeed_kmph
    global Ignition_Status

    while True:

        time.sleep(DT)

        # -----------------------------------
        # SPEED DECELERATION PROFILE
        # 40 km/h -> 10 km/h in 3 seconds
        # -----------------------------------
        if Ignition_Status == 1:

            if VehicleSpeed_mps > TARGET_SPEED_MPS:

                VehicleSpeed_mps -= DECEL_MS2 * DT

                if VehicleSpeed_mps < TARGET_SPEED_MPS:
                    VehicleSpeed_mps = TARGET_SPEED_MPS

            VehicleSpeed_kmph = VehicleSpeed_mps * 3.6

        print(
            f"Vehicle Speed = "
            f"{VehicleSpeed_kmph:.2f} km/h"
        )

        # ---------------- MULTIFRAME ----------------
        Multiframe18FF0881()

        # ---------------- CAN FRAMES ----------------
        TriggerCANMessage(
            0x18FF1481,
            IGN_Frame(),
            "IGN"
        )

        TriggerCANMessage(
            0x18FF1581,
            ChargePlugFrame(),
            "CHARGE"
        )

        TriggerCANMessage(
            0x18FF0C81,
            DriveModeFrame(),
            "DRIVE"
        )

        TriggerCANMessage(
            0x18FF0F17,
            ODO_Frame(),
            "ODO"
        )

        # ---------------- IGNITION TIMER ----------------
        if Ignition_Status == 1:

            if (
                time.time() - ignition_start_time
                > IGNITION_ON_DURATION
            ):
                Ignition_Status = 0
                print(
                    "Ignition turned OFF automatically"
                )
                break

# ---------------- MAIN ----------------
if __name__ == "__main__":

    print("CAN Simulation Started")
    print(
        f"Initial Speed : {INITIAL_SPEED_KMPH} km/h"
    )
    print(
        f"Target Speed  : {TARGET_SPEED_KMPH} km/h"
    )
    print(
        f"Deceleration  : {DECEL_MS2:.3f} m/s²"
    )

    t1 = threading.Thread(
        target=Tx_100ms,
        daemon=True
    )

    t1.start()

    while True:
        time.sleep(1)