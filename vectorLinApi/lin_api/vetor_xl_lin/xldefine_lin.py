import can.interfaces.vector.xldefine as origin_xldefine
from enum import IntEnum, IntFlag
import ctypes
import logging
import platform
from ctypes.util import find_library


"""
xldefine_lin:
补充了LIN的枚举类型，主要依据vxlapi.h 对LIN的定义进行补充
"""

class XL_LinMode(IntEnum):
    XL_LIN_MASTER = 1
    XL_LIN_SLAVE = 2


class XL_LinVersion(IntEnum):
    XL_LIN_VERSION_1_3 = 1
    XL_LIN_VERSION_2_0 = 2
    XL_LIN_VERSION_2_1 = 3


class XL_LinChecksum(IntEnum):
    XL_LIN_CHECKSUM_CLASSIC = 0
    XL_LIN_CHECKSUM_ENHANCED = 1
    XL_LIN_CHECKSUM_UNDEFINED = 255


class XL_flags(IntEnum):
    XL_LIN_FLAG_NONE = 0
    XL_ACTIVATE_RESET_CLOCK = 8


class XL_SleepMode(IntEnum):
    XL_LIN_SET_SILENT = 1
    XL_LIN_SET_WAKEUPID = 3


class XL_LIN_CHECKSUM_CLASSIC(IntEnum):
    XL_LIN_CHECKSUM_CLASSIC = 0
    XL_LIN_CHECKSUM_ENHANCED = 1
    XL_LIN_CHECKSUM_UNDEFINED = 255


class XL_LIN_EventTags(IntEnum):
    XL_LIN_MSG= 20
    XL_LIN_ERRMSG = 21
    XL_LIN_SYNCERR = 22
    XL_LIN_NOANS = 23
    XL_LIN_WAKEUP = 24
    XL_LIN_SLEEP = 25
    XL_LIN_CRCINFO = 26


