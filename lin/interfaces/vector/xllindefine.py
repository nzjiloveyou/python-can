"""
Definition of constants for Vector LIN API.
"""
from enum import IntEnum, IntFlag


# LIN constants
XL_LIN_MAX_DATA_LEN = 8
XL_LIN_ID_MAX = 63

# LIN version
class XL_LIN_Version(IntEnum):
    XL_LIN_VERSION_1_3 = 0x13
    XL_LIN_VERSION_2_0 = 0x20
    XL_LIN_VERSION_2_1 = 0x21
    XL_LIN_VERSION_2_2 = 0x22


# LIN message flags
class XL_LIN_MessageFlags(IntFlag):
    XL_LIN_MSGFLAG_TX = 0x01         # Transmitted message
    XL_LIN_MSGFLAG_RX = 0x02         # Received message
    XL_LIN_MSGFLAG_WAKEUP = 0x04     # Wake up frame
    XL_LIN_MSGFLAG_NERR = 0x08       # No error
    XL_LIN_MSGFLAG_CRCERR = 0x10     # Checksum error
    XL_LIN_MSGFLAG_PARITYERR = 0x20  # Parity error
    XL_LIN_MSGFLAG_NOANS = 0x40      # No slave response
    XL_LIN_MSGFLAG_OVERRUN = 0x80    # Overrun error


# LIN event tags  
class XL_LIN_EventTags(IntEnum):
    XL_LIN_MSG = 20                   # LIN消息事件
    XL_LIN_ERRMSG = 21               # LIN错误消息
    XL_LIN_SYNCERR = 22              # 同步错误
    XL_LIN_NOANS = 23                # 无应答
    XL_LIN_WAKEUP = 25               # 唤醒事件
    XL_LIN_SLEEP = 26                # 休眠事件
    XL_LIN_CRCINFO = 27              # CRC信息


# LIN error codes
class XL_LIN_ErrorCode(IntEnum):
    XL_LIN_ERR_OK = 0
    XL_LIN_ERR_CHECKSUM = 1
    XL_LIN_ERR_PARITY = 2
    XL_LIN_ERR_FRAMING = 3
    XL_LIN_ERR_SYNCH = 4
    XL_LIN_ERR_NO_RESPONSE = 5


# Bus types (from Vector XL API)
class XL_BusTypes(IntFlag):
    XL_BUS_TYPE_NONE = 0
    XL_BUS_TYPE_CAN = 1
    XL_BUS_TYPE_LIN = 2

# 为了方便访问，直接定义常量
XL_BUS_TYPE_LIN = 2