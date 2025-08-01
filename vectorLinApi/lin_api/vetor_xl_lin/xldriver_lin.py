
import ctypes

import can.interfaces.vector.xldriver as origin_xld
from . import xlclass_lin

from . import xlclass_lin
from can.interfaces.vector.exceptions import VectorInitializationError, VectorOperationError
from can.interfaces.vector.xldriver import check_status_operation




# ctypes wrapping for API functions



""" 
xld模块说明：

复用xldriver 驱动，补充lin协议相关函数

"""

xlapi_dll = origin_xld._xlapi_dll
xlapi_class = origin_xld.xlclass


xlGetErrorString = xlapi_dll.xlGetErrorString
xlGetErrorString.argtypes = [xlapi_class.XLstatus]
xlGetErrorString.restype = xlapi_class.XLstringType

xlLinSetChannelParams = xlapi_dll.xlLinSetChannelParams
xlLinSetChannelParams.argtypes = [
    xlapi_class.XLportHandle,
    ctypes.c_uint,
    xlclass_lin.XLlinStatPar
]
xlLinSetChannelParams.restype = xlapi_class.XLstatus


xlLinSetDLC = xlapi_dll.xlLinSetDLC
xlLinSetDLC.argtypes = [
    xlapi_class.XLportHandle,
    ctypes.c_uint,
    ctypes.POINTER(ctypes.c_uint8 * 60)
]
xlLinSetDLC.restype = xlapi_class.XLstatus


xlLinSetChecksum = xlapi_dll. xlLinSetChecksum
xlLinSetChecksum.argtypes = [
    xlapi_class.XLportHandle,
    ctypes.c_uint,
    ctypes.POINTER(ctypes.c_uint8 * 60)
]
xlLinSetChecksum.restype = xlapi_class.XLstatus

xlActivateChannel = xlapi_dll.xlActivateChannel
xlActivateChannel.argtypes = [
    xlapi_class.XLportHandle,
    ctypes.c_uint,
    ctypes.c_uint,
    ctypes.c_uint
]
xlActivateChannel.restype = xlapi_class.XLstatus


xlLinSendRequest = xlapi_dll.xlLinSendRequest
xlLinSendRequest.argtypes = [
    xlapi_class.XLportHandle,
    xlapi_class.XLaccess,
    ctypes.c_ubyte,  # unsigned char linId
    ctypes.c_uint
]
xlLinSendRequest.restype = xlapi_class.XLstatus

xlLinWakeUp = xlapi_dll.xlLinWakeUp
xlLinWakeUp.argtypes = [
    xlapi_class.XLportHandle,
    xlapi_class.XLaccess
]
xlLinWakeUp.restype = xlapi_class.XLstatus


xlLinSetSleepMode = xlapi_dll.xlLinSetSleepMode
xlLinSetSleepMode.argtypes = [
    xlapi_class.XLportHandle,
    xlapi_class.XLaccess,
    ctypes.c_uint,
    ctypes.c_ubyte
]
xlLinSetSleepMode.restype = xlapi_class.XLstatus


xlLinSetSlave = xlapi_dll.xlLinSetSlave
xlLinSetSlave.argtypes = [
    xlapi_class.XLportHandle,
    xlapi_class.XLaccess,
    ctypes.c_ubyte,
    ctypes.POINTER(ctypes.c_uint * 8),
    ctypes.c_ubyte,
    ctypes.c_uint
]
xlLinSetSlave.restype = xlapi_class.XLstatus


xlReceive = xlapi_dll.xlReceive
xlReceive.argtypes = [
    xlapi_class.XLportHandle,
    ctypes.POINTER(ctypes.c_uint),
    ctypes.POINTER(xlclass_lin.XLEvent),
]
xlReceive.restype = xlapi_class.XLstatus
xlReceive.errcheck = check_status_operation





if __name__ == '__main__':
    pass