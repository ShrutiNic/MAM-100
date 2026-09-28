 #!/usr/bin/env python3
"""
UDS Server (ECU simulator) over ISO-TP using PCAN.

Supports:
- 0x10 DiagnosticSessionControl (0x01 default, 0x02 programming, 0x03 extended)
- 0x27 SecurityAccess Level 1 (0x01 request seed, 0x02 send key)
- 0x31 RoutineControl (0x01 start, 0x02 stop, 0x03 results) for routine 0xFF00

Tested conceptually with ISO-TP stack. Adjust IDs/params as needed.
"""

import argparse
import logging
import os
import struct
import time
from dataclasses import dataclass

import can
import isotp


# ---------------- UDS constants ----------------
SID_DIAG_SESSION_CTRL = 0x10
SID_SECURITY_ACCESS   = 0x27
SID_ROUTINE_CONTROL   = 0x31
SID_NEGATIVE_RESPONSE = 0x7F

POS_RESP_BASE = 0x40

# NRC (Negative Response Codes)
NRC_GENERAL_REJECT               = 0x10
NRC_SERVICE_NOT_SUPPORTED        = 0x11
NRC_SUBFUNCTION_NOT_SUPPORTED    = 0x12
NRC_INCORRECT_MESSAGE_LENGTH     = 0x13
NRC_CONDITIONS_NOT_CORRECT       = 0x22
NRC_REQUEST_OUT_OF_RANGE         = 0x31
NRC_SECURITY_ACCESS_DENIED       = 0x33
NRC_INVALID_KEY                  = 0x35
NRC_EXCEEDED_NUMBER_OF_ATTEMPTS  = 0x36
NRC_REQUIRED_TIME_DELAY_NOT_EXP  = 0x37

# Sessions
SESSION_DEFAULT     = 0x01
SESSION_PROGRAMMING = 0x02
SESSION_EXTENDED    = 0x03
event_counter = 0x01

@dataclass
class EcuState:
    session: int = SESSION_DEFAULT
    security_level_1_unlocked: bool = False
    last_seed: bytes = b""
    failed_key_attempts: int = 0
    lockout_until_ts: float = 0.0
    routine_ff00_running: bool = False
    routine_ff00_last_status: int = 0x00  # application-defined status
    first_request_seen: bool = False
    sess_ctrl_count = 0
def nrc(sid: int, code: int) -> bytes:
    return bytes([SID_NEGATIVE_RESPONSE, sid & 0xFF, code & 0xFF])


def hex_bytes(b: bytes) -> str:
    return " ".join(f"{x:02X}" for x in b)


# ---------------- Seed/Key algorithm (simple demo) ----------------
# IMPORTANT: Replace with your OEM algorithm.
# This is a simple example: key = seed XOR secret (repeated), then rotate-left by 1 bit.
def compute_key_level1(seed: bytes, secret: bytes) -> bytes:
    if not seed:
        return b""
    xored = bytes([seed[i] ^ secret[i % len(secret)] for i in range(len(seed))])

    # rotate-left each byte by 1
    rol1 = bytes([((v << 1) & 0xFF) | ((v >> 7) & 0x01) for v in xored])
    return rol1


# ---------------- UDS handlers ----------------
def handle_session_control(req: bytes, st: EcuState) -> bytes:
    print("I am here...")
    # Request: 10 <subfn>
    if len(req) < 2:
        return nrc(SID_DIAG_SESSION_CTRL, NRC_SUBFUNCTION_NOT_SUPPORTED)

    subfn = req[1]
    if subfn not in (SESSION_DEFAULT, SESSION_PROGRAMMING, SESSION_EXTENDED):
        return nrc(SID_DIAG_SESSION_CTRL, NRC_SUBFUNCTION_NOT_SUPPORTED)

    # Example policy: entering default locks security again
    st.session = subfn
    if st.session == SESSION_DEFAULT:
        st.security_level_1_unlocked = False

    # Response: 50 <subfn> <P2_hi><P2_lo> <P2*_hi><P2*_lo>
    # Using example timings (ms): P2=50ms, P2*=5000ms
    p2_ms = 5000
    p2_star_ms = 5000
    return bytes([
        SID_DIAG_SESSION_CTRL + POS_RESP_BASE,
        subfn,
        (p2_ms >> 8) & 0xFF, p2_ms & 0xFF,
        (p2_star_ms >> 8) & 0xFF, p2_star_ms & 0xFF
    ])

def handle_security_access(req, st):
    """
    Security Level 1 always unlocked
    Ignore key validation
    """

    if len(req) < 1:
        return bytes([0x7F, 0x27, 0x13])  # Incorrect length

    subfn = req[1]

    # Seed Request (27 01)
    if subfn == 0x01:
        dummy_seed = bytes([0x51, 0x89, 0x0F, 0xC2])
        return bytes([0x67, 0x01]) + dummy_seed

    # Key Send (27 02)
    elif subfn == 0x02:
        st.security_level_1_unlocked = True
        return bytes([0x67, 0x02])

    else:
        return bytes([0x7F, 0x27, 0x12])  # Subfunction not supported

def handle_routine_control(req, st):

    if len(req) < 3:
        return bytes([0x7F, 0x31, 0x13])

    routine_type = req[1]
    rid_hi = req[2]
    rid_lo = req[3]

    # Example: Only for RID = FF00
    if rid_hi == 0xC0 and rid_lo == 0x00:

        # Generate 360 bytes routine data
        routine_data = bytes([(ord('a') + (x % 26)) for x in range(360)])

        resp = bytes([
            0x71,               # Positive response
            routine_type,       # Echo routine type
            rid_hi,
            rid_lo
        ]) + routine_data

        return resp

    return bytes([0x7F, 0x31, 0x31])

# def dispatch_uds(req: bytes, st: EcuState, secret: bytes, seed_len: int) -> bytes:
#     if req:
#         return nrc(0x00, NRC_SUBFUNCTION_NOT_SUPPORTED)

#     sid = req[0]

#     if sid == SID_DIAG_SESSION_CTRL:
#         #return nrc(0x00, NRC_SUBFUNCTION_NOT_SUPPORTED)
#         return handle_session_control(req, st)

#     if sid == SID_SECURITY_ACCESS:
#         return handle_security_access(req, st,)

#     if sid == SID_ROUTINE_CONTROL:
#         return handle_routine_control(req, st)

#     return nrc(sid, NRC_SERVICE_NOT_SUPPORTED)

def dispatch_uds(req: bytes, st: EcuState, secret: bytes, seed_len: int) -> bytes:
    if not req:
        return nrc(0x00, NRC_INCORRECT_MESSAGE_LENGTH)

    sid = req[0]

    if sid == SID_DIAG_SESSION_CTRL:
        return handle_session_control(req, st)

    if sid == SID_SECURITY_ACCESS:
        return handle_security_access(req, st)

    if sid == SID_ROUTINE_CONTROL:
        return handle_routine_control(req, st)

    return nrc(sid, NRC_SERVICE_NOT_SUPPORTED)

def send_event_frame(bus):
    """
    Send raw CAN event frame (not ISO-TP)
    ID:   0x18FF0F81
    DATA: counter 00 00 00 00 00 00 00

    Counter increases by 2 every transmission.
    """

    global event_counter

    msg = can.Message(
        arbitration_id=0x18FF0F81,
        is_extended_id=True,
        data=[
            event_counter,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00
        ]
    )

    try:
        bus.send(msg)

        logging.info(
            "Event TX: ID=0x%X DATA=%s",
            msg.arbitration_id,
            hex_bytes(msg.data)
        )

        # Increment by 2 for next transmission
        event_counter += 2

        # Wrap around after 0xFF
        if event_counter > 0xFF:
            event_counter = 0x01

    except can.CanError as e:
        logging.error("Event frame send failed: %s", e)


# ---------------- Main loop ----------------
def main():
    parser = argparse.ArgumentParser(description="UDS Server (ECU) over PCAN ISO-TP")
    parser.add_argument("--channel", default="PCAN_USBBUS1", help="PCAN channel (e.g., PCAN_USBBUS1)")
    parser.add_argument("--bitrate", type=int, default=500000, help="CAN bitrate")
    parser.add_argument("--rxid", type=lambda x: int(x, 0), default=0x1CFF81F9, help="Tester->ECU CAN ID (hex)")
    parser.add_argument("--txid", type=lambda x: int(x, 0), default=0x1CFFF981, help="ECU->Tester CAN ID (hex)")
    parser.add_argument("--extid", action="store_true", help="Use 29-bit CAN IDs")
    parser.add_argument("--secret", default="A1B2C3D4", help="Hex secret for seed/key (demo) e.g. A1B2C3D4")
    parser.add_argument("--seed-len", type=int, default=4, help="Seed length bytes")
    parser.add_argument("--log", default="INFO", help="Logging level (DEBUG/INFO/WARN/ERROR)")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log.upper(), logging.INFO),
        format="%(asctime)s.%(msecs)03d %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    log = logging.getLogger("uds-ecu")

    try:
        secret_bytes = bytes.fromhex(args.secret)
    except ValueError:
        raise SystemExit("Invalid --secret hex string. Example: --secret A1B2C3D4")

    st = EcuState()

    # Create CAN bus (PCAN)
    bus = can.Bus(
        interface="pcan",
        channel=args.channel,
        bitrate=args.bitrate
    )

    auto_ext = (args.rxid > 0x7FF) or (args.txid > 0x7FF)
    use_ext = args.extid or auto_ext

    addr = isotp.Address(
        isotp.AddressingMode.Normal_29bits if use_ext else isotp.AddressingMode.Normal_11bits,
        txid=args.txid,
        rxid=args.rxid
    )

    # ISO-TP stack (ECU side)
    stack = isotp.CanStack(
        bus=bus,
        address=addr,
        params={
            "stmin": 0,
            "blocksize": 1,
            "wftmax": 0,
            "tx_padding": 0x00,
            "rx_flowcontrol_timeout": 10000,
            "rx_consecutive_frame_timeout": 5000,
        }
    )

    log.info("UDS ECU started. RXID=0x%X TXID=0x%X extid=%s channel=%s bitrate=%d",
             args.rxid, args.txid, args.extid, args.channel, args.bitrate)
    log.info("Policy: 0x27 allowed only in Extended/Programming. 0x31 allowed only when unlocked + Programming session.")
    log.info("Supported routine: 0xFF00")

    # Main server loop
    while True:
        # process ISO-TP transport
        stack.process()
        send_event_frame(bus)
        # if complete UDS payload received
        if stack.available():
            req = stack.recv()
            if req is None:
                continue

            log.info("RX UDS: %s", hex_bytes(req))

            resp = dispatch_uds(req, st, secret_bytes, args.seed_len)
            # log.info("TX UDS: %s", hex_bytes(resp))

            # stack.send(resp)
            if req[0] == 0x31 and len(resp) > 7:
                total_len = len(resp)

                ff_data = [
                    0x10 | ((total_len >> 8) & 0x0F),
                    total_len & 0xFF,
                ]
                ff_data.extend(resp[:6])

                msg = can.Message(
                    arbitration_id=args.txid,
                    is_extended_id=use_ext,
                    data=ff_data
                )

                bus.send(msg)
                log.info("Sent only ISO-TP First Frame")

            else:
                stack.send(resp)

        # small sleep to reduce CPU
        time.sleep(0.5)


if __name__ == "__main__":
    main()
 