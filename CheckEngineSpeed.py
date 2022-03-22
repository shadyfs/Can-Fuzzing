#!/usr/bin/python3
import socket
import struct
import time
import json
import os
import time
import datetime
import matplotlib.pyplot as plt

# Open a socket and bind to it from SocketCAN
sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
interface = "vcan0"

# Bind to the interface
sock.bind((interface,))

# To match this data structure, the following struct format can be used:
can_frame_format = "<lB3x8s"
#Make a CAN reading function
def unpack_CAN(can_packet,display=False):
    can_id, can_dlc, can_data = struct.unpack(can_frame_format, can_packet)
    extended_frame = bool(can_id & socket.CAN_EFF_FLAG)
    if extended_frame:
        can_id &= socket.CAN_EFF_MASK
        can_id_string = "{:08X}".format(can_id)
    else: #Standard Frame
        can_id &= socket.CAN_SFF_MASK
        can_id_string = "{:03X}".format(can_id)
    if display:
        hex_data_string = ' '.join(["{:02X}".format(b) for b in can_data[:can_dlc]])
        print("{} {} [{}] {}".format(interface, can_id_string, can_dlc, hex_data_string))
    return can_id, can_dlc, can_data


# parse J1939 protocol data unit information from the ID using bit masks and shifts
PRIORITY_MASK = 0x1C000000
EDP_MASK = 0x02000000
DP_MASK = 0x01000000
PF_MASK = 0x00FF0000
PS_MASK = 0x0000FF00
SA_MASK = 0x000000FF
PDU1_PGN_MASK = 0x03FF0000
PDU2_PGN_MASK = 0x03FFFF00


def get_j1939_from_id(can_id):
    # priority
    priority = (PRIORITY_MASK & can_id) >> 26

    # Extended Data Page
    edp = (EDP_MASK & can_id) >> 25

    # Data Page
    dp = (DP_MASK & can_id) >> 24

    # Protocol Data Unit (PDU) Format
    PF = (can_id & PF_MASK) >> 16

    # Protocol Data Unit (PDU) Specific
    PS = (can_id & PS_MASK) >> 8

    # Determine the Parameter Group Number and Destination Address
    if PF >= 0xF0:  # 240
        # PDU 2 format, include the PS as a group extension
        DA = 255
        PGN = (can_id & PDU2_PGN_MASK) >> 8
    else:
        PGN = (can_id & PDU1_PGN_MASK) >> 8
        DA = PS
    # Source address
    SA = (can_id & SA_MASK)

    return priority, PGN, DA, SA
presentDate = datetime.datetime.now()
unix_timestamp = datetime.datetime.timestamp(presentDate)*1000000
starttime = unix_timestamp
SPN = []
timelist = []
# Read and process some messages.
for i in range(10000):
    presentDate = datetime.datetime.now()
    unix_timestamp = datetime.datetime.timestamp(presentDate)*1000000
    tim = unix_timestamp - starttime
    # Read the message from the newtork
    can_packet = sock.recv(16)
    #Parse the bytes into a CAN message
    can_id, can_dlc, can_data = unpack_CAN(can_packet)
    #Parse the CAN ID into J1939
    priority,pgn,da,sa = get_j1939_from_id(can_id)
    if pgn == 61444 and sa == 0:
        spn190 = struct.unpack("<H",can_data[3:5])[0]*0.125/10
        print("Engine Speed in rpm : ",spn190)
        SPN.append(spn190)
        timelist.append(tim)