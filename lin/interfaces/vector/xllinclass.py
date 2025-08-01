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


# Union for different LIN event data
class s_xl_lin_tag_data(ctypes.Union):
    _fields_ = [
        ("linMsg", s_xl_lin_msg),
        ("linSleep", s_xl_lin_sleep),
        ("linWakeUp", s_xl_lin_wakeup),
        ("linNoAns", s_xl_lin_no_ans),
    ]


# LIN event structure
class XLevent(ctypes.Structure):
    _fields_ = [
        ("tag", ctypes.c_ubyte),              # Event type tag
        ("chanIndex", ctypes.c_ubyte),        # Channel index
        ("transId", ctypes.c_ushort),         # Transaction ID
        ("portHandle", XLportHandle),         # Port handle
        ("flags", ctypes.c_ubyte),            # Flags
        ("reserved", ctypes.c_ubyte),         # Reserved
        ("timeStamp", XLuint64),              # Timestamp
        ("tagData", s_xl_lin_tag_data),      # Event data
    ]


# Application configuration for LIN
class XLlinStatPar(ctypes.Structure):
    _fields_ = [
        ("LINMode", ctypes.c_uint),          # LIN mode (Master/Slave)
        ("baudrate", ctypes.c_uint),         # Baudrate
        ("LINVersion", ctypes.c_uint),       # LIN version
    ]