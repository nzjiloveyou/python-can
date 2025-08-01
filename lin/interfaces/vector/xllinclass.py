"""
Definition of data types and structures for Vector LIN API.
"""
import ctypes
from . import xllindefine

# Type definitions
XLuint64 = ctypes.c_uint64
XLaccess = XLuint64
XLhandle = ctypes.c_void_p
XLstatus = ctypes.c_short
XLportHandle = ctypes.c_long


# LIN message structure
class s_xl_lin_msg(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_ubyte),              # LIN ID (0-63)
        ("dlc", ctypes.c_ubyte),             # Data length
        ("flags", ctypes.c_ushort),          # Message flags
        ("data", ctypes.c_ubyte * xllindefine.XL_LIN_MAX_DATA_LEN),  # Data bytes
        ("crc", ctypes.c_ubyte),             # Checksum
    ]


# LIN sleep mode event
class s_xl_lin_sleep(ctypes.Structure):
    _fields_ = [
        ("flag", ctypes.c_ubyte),
    ]


# LIN wake up event
class s_xl_lin_wakeup(ctypes.Structure):
    _fields_ = [
        ("flag", ctypes.c_ubyte),
        ("unused", ctypes.c_ubyte * 3),
        ("time", XLuint64),
    ]


# LIN no answer event
class s_xl_lin_no_ans(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_ubyte),
    ]


# LIN CRC info
class s_xl_lin_crc_info(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_ubyte),
        ("flags", ctypes.c_ubyte),
    ]


# LIN message API union (wrapper for LIN messages)
class XL_LinMsgAPI(ctypes.Union):
    _fields_ = [
        ("linMsg", s_xl_lin_msg),
        ("linNoAns", s_xl_lin_no_ans),
        ("linWakeUp", s_xl_lin_wakeup),
        ("linSleep", s_xl_lin_sleep),
        ("linCRCinfo", s_xl_lin_crc_info),
    ]


# CAN message structure placeholder
class XL_CAN_Msg(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint),
        ("flags", ctypes.c_uint),
        ("dlc", ctypes.c_ubyte),
        ("res1", ctypes.c_ubyte),
        ("res2", ctypes.c_ushort),
        ("data", ctypes.c_ubyte * 8),
    ]


# Other event data structures
class XL_ChipState(ctypes.Structure):
    _fields_ = []


class XL_SyncPulse(ctypes.Structure):
    _fields_ = []


class XL_Transceiver(ctypes.Structure):
    _fields_ = []


# Union for all possible event data types
class s_xl_tag_data(ctypes.Union):
    _fields_ = [
        ("msg", XL_CAN_Msg),
        ("chipState", XL_ChipState),
        ("linMsgApi", XL_LinMsgAPI),
        ("syncPulse", XL_SyncPulse),
        ("transceiver", XL_Transceiver),
    ]


# LIN event structure (compatible with Vector XL API)
class XLevent(ctypes.Structure):
    _fields_ = [
        ("tag", ctypes.c_ubyte),              # Event type tag
        ("chanIndex", ctypes.c_ubyte),        # Channel index
        ("transId", ctypes.c_ushort),         # Transaction ID
        ("portHandle", XLportHandle),         # Port handle
        ("flags", ctypes.c_ubyte),            # Flags
        ("reserved", ctypes.c_ubyte),         # Reserved
        ("timeStamp", XLuint64),              # Timestamp
        ("tagData", s_xl_tag_data),          # Event data (union)
    ]


# Application configuration for LIN
class XLlinStatPar(ctypes.Structure):
    _fields_ = [
        ("LINMode", ctypes.c_uint),          # LIN mode (Master/Slave)
        ("baudrate", ctypes.c_uint),         # Baudrate
        ("LINVersion", ctypes.c_uint),       # LIN version
    ]