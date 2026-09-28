#!/usr/bin/env python3
"""
KWP2000 ECU Simulator over ISO-TP using PCAN

Supports:
- 0x21 ReadDataByLocalIdentifier
- LID 0xA0 Summary Read

Summary Request:
21 A0 cycleMSB cycleLSB type

type:
01 -> Charge Summary
02 -> Drive Summary

Summary Response:
61 A0 + 313 bytes
"""

import argparse
import logging
import time
from dataclasses import dataclass

@dataclass
class EcuState:
    pass

import can
import isotp


# ---------------- KWP constants ----------------

SID_READ_LOCAL_ID      = 0x21
SID_NEGATIVE_RESPONSE  = 0x7F

POS_RESP_BASE          = 0x40

LID_SUMMARY_READ       = 0xA0

SUMMARY_CHARGE         = 0x01
SUMMARY_DRIVE          = 0x02

SUMMARY_DATA_SIZE      = 313


# NRC
NRC_SERVICE_NOT_SUPPORTED     = 0x11
NRC_SUBFUNCTION_NOT_SUPPORTED = 0x12
NRC_INCORRECT_MESSAGE_LENGTH  = 0x13
NRC_REQUEST_OUT_OF_RANGE      = 0x31
event_counter = 0x01
def nrc(sid: int, code: int) -> bytes:
    return bytes([
        SID_NEGATIVE_RESPONSE,
        sid & 0xFF,
        code & 0xFF
    ])


def hex_bytes(b: bytes) -> str:
    return " ".join(f"{x:02X}" for x in b)

# =============================================================================
# KWP Summary Handler
# =============================================================================

def handle_kwp_summary(req: bytes, st: EcuState) -> bytes:

    #
    # Expected Request:
    #
    # 21 A0 cycleMSB cycleLSB type
    #

    if len(req) < 5:

        return nrc(
            SID_READ_LOCAL_ID,
            NRC_INCORRECT_MESSAGE_LENGTH
        )

    sid = req[0]
    lid = req[1]

    #
    # Validate LID
    #

    if lid != LID_SUMMARY_READ:

        return nrc(
            SID_READ_LOCAL_ID,
            NRC_REQUEST_OUT_OF_RANGE
        )

    #
    # Cycle Number
    # BIG-ENDIAN
    #

    cycle = (req[2] << 8) | req[3]

    #
    # Summary Type
    #

    summary_type = req[4]

    print("\n====================================")

    print(f"Cycle Number : {cycle}")

    if summary_type == SUMMARY_CHARGE:

        print("Charge Summary Request")

    elif summary_type == SUMMARY_DRIVE:

        print("Drive Summary Request")

    else:

        return nrc(
            SID_READ_LOCAL_ID,
            NRC_REQUEST_OUT_OF_RANGE
        )

    #
    # Generate 313-byte dummy summary data
    #

    summary_data = bytes([
        (ord('A') + (x % 26))
        for x in range(SUMMARY_DATA_SIZE)
    ])

    #
    # Positive Response:
    #
    # 61 A0 + 313 bytes
    #

    resp = bytes([
        sid + POS_RESP_BASE,
        LID_SUMMARY_READ
    ]) + summary_data

    print(f"Sending {SUMMARY_DATA_SIZE} bytes response")

    return resp


# =============================================================================
# Dispatcher
# =============================================================================

def dispatch_uds(req: bytes, st: EcuState) -> bytes:

    if not req:

        return nrc(
            0x00,
            NRC_INCORRECT_MESSAGE_LENGTH
        )

    sid = req[0]

    #
    # KWP Summary Request
    #

    if sid == SID_READ_LOCAL_ID:

        return handle_kwp_summary(req, st)
        

    #
    # Unsupported SID
    #

    return nrc(
        sid,
        NRC_SERVICE_NOT_SUPPORTED
    )

def send_event_frame(bus):
    """
    Send raw CAN event frame (not ISO-TP)
    ID:   0x18FF0F81
    DATA: counter 00 00 00 00 00 00 00

    Counter increases by 2 every transmission.
    """

    global event_counter

    msg = can.Message(
        arbitration_id=0x18FF1481,
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
        
def send_ign_frame(bus):
    """
    Send raw CAN event frame (not ISO-TP)
    ID:   0x18FF0F81
    DATA: counter 00 00 00 00 00 00 00

    Counter increases by 2 every transmission.
    """

    

    msg = can.Message(
        arbitration_id=0x18FF1481,
        is_extended_id=True,
        data=[
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x01
        ]
    )

    try:
        bus.send(msg)

        logging.info(
            "Event TX: ID=0x%X DATA=%s",
            msg.arbitration_id,
            hex_bytes(msg.data)
        )


    except can.CanError as e:
        logging.error("Event frame send failed: %s", e)

# =============================================================================
# Main
# =============================================================================

def main():

    parser = argparse.ArgumentParser(
        description="KWP2000 ECU Simulator over PCAN ISO-TP"
    )

    parser.add_argument(
        "--channel",
        default="PCAN_USBBUS1",
        help="PCAN channel"
    )

    parser.add_argument(
        "--bitrate",
        type=int,
        default=500000,
        help="CAN bitrate"
    )

    parser.add_argument(
        "--rxid",
        type=lambda x: int(x, 0),
        default=0x1CFF81F9,
        help="Tester -> ECU CAN ID"
    )

    parser.add_argument(
        "--txid",
        type=lambda x: int(x, 0),
        default=0x1CFFF981,
        help="ECU -> Tester CAN ID"
    )

    parser.add_argument(
        "--extid",
        action="store_true",
        help="Use 29-bit CAN IDs"
    )

    parser.add_argument(
        "--log",
        default="INFO",
        help="Logging level"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log.upper(), logging.INFO),
        format="%(asctime)s.%(msecs)03d %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    log = logging.getLogger("kwp-ecu")

    st = EcuState()

    #
    # Create CAN bus
    #

    bus = can.Bus(
        interface="pcan",
        channel=args.channel,
        bitrate=args.bitrate
    )

    auto_ext = (
        (args.rxid > 0x7FF)
        or
        (args.txid > 0x7FF)
    )

    use_ext = args.extid or auto_ext

    #
    # ISO-TP Addressing
    #

    addr = isotp.Address(
        isotp.AddressingMode.Normal_29bits
        if use_ext
        else isotp.AddressingMode.Normal_11bits,

        txid=args.txid,
        rxid=args.rxid
    )

    #
    # ISO-TP Stack
    #

    stack = isotp.CanStack(
        bus=bus,
        address=addr,
        params={
            "stmin": 0,
            "blocksize": 8,
            "wftmax": 0,
            "tx_padding": 0x00,
            "rx_flowcontrol_timeout": 10000,
            "rx_consecutive_frame_timeout": 1000,
        }
    )

    log.info(
        "KWP ECU started. "
        "RXID=0x%X "
        "TXID=0x%X "
        "extid=%s "
        "channel=%s "
        "bitrate=%d",

        args.rxid,
        args.txid,
        args.extid,
        args.channel,
        args.bitrate
    )

    #
    # Main Loop
    #

    while True:

        #
        # Process ISO-TP transport
        #

        stack.process()
        send_ign_frame(bus)
        send_event_frame(bus)
        #
        # Full payload received
        #

        if stack.available():

            req = stack.recv()

            if req is None:
                continue

            log.info(
                "RX KWP: %s",
                hex_bytes(req)
            )

            #
            # Generate response
            #

            resp = dispatch_uds(
                req,
                st
            )

            log.info(
                "TX KWP: %s",
                hex_bytes(resp)
            )

            #
            # Send response
            #

            stack.send(resp)

        #
        # Reduce CPU load
        #

        time.sleep(0.0005)


if __name__ == "__main__":

    main()