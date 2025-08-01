"""
Ctypes wrapper for Vector LIN API functions.
"""
import ctypes
import logging
import platform
from ctypes.util import find_library
from . import xllinclass
from .exceptions import VectorLinInitializationError, VectorLinOperationError

LOG = logging.getLogger(__name__)

# Load Windows DLL
DLL_NAME = "vxlapi64" if platform.architecture()[0] == "64bit" else "vxlapi"
if dll_path := find_library(DLL_NAME):
    _xlapi_dll = ctypes.windll.LoadLibrary(dll_path)
else:
    raise FileNotFoundError(f"Vector XL library not found: {DLL_NAME}")


# Error handling functions
xlGetErrorString = _xlapi_dll.xlGetErrorString
xlGetErrorString.argtypes = [xllinclass.XLstatus]
xlGetErrorString.restype = ctypes.c_char_p


def check_status_operation(result, function, arguments):
    """Check status and raise VectorLinOperationError on error."""
    if result > 0:
        raise VectorLinOperationError(
            result, xlGetErrorString(result).decode(), function.__name__
        )
    return result


def check_status_initialization(result, function, arguments):
    """Check status and raise VectorLinInitializationError on error."""
    if result > 0:
        raise VectorLinInitializationError(
            result, xlGetErrorString(result).decode(), function.__name__
        )
    return result


# Driver functions
xlOpenDriver = _xlapi_dll.xlOpenDriver
xlOpenDriver.argtypes = []
xlOpenDriver.restype = xllinclass.XLstatus
xlOpenDriver.errcheck = check_status_initialization

xlCloseDriver = _xlapi_dll.xlCloseDriver
xlCloseDriver.argtypes = []
xlCloseDriver.restype = xllinclass.XLstatus
xlCloseDriver.errcheck = check_status_operation

# Port functions
xlOpenPort = _xlapi_dll.xlOpenPort
xlOpenPort.argtypes = [
    ctypes.POINTER(xllinclass.XLportHandle),
    ctypes.c_char_p,
    xllinclass.XLaccess,
    ctypes.POINTER(xllinclass.XLaccess),
    ctypes.c_uint,
    ctypes.c_uint,
    ctypes.c_uint,
]
xlOpenPort.restype = xllinclass.XLstatus
xlOpenPort.errcheck = check_status_initialization

xlClosePort = _xlapi_dll.xlClosePort
xlClosePort.argtypes = [xllinclass.XLportHandle]
xlClosePort.restype = xllinclass.XLstatus
xlClosePort.errcheck = check_status_operation

# LIN functions
# Note: xlLinSetChannelParams may not exist in all versions
# xlLinSetChannelParams = _xlapi_dll.xlLinSetChannelParams
# xlLinSetChannelParams.argtypes = [
#     xllinclass.XLportHandle,
#     xllinclass.XLaccess,
#     ctypes.POINTER(xllinclass.XLlinStatPar),
# ]
# xlLinSetChannelParams.restype = xllinclass.XLstatus
# xlLinSetChannelParams.errcheck = check_status_operation

xlActivateChannel = _xlapi_dll.xlActivateChannel
xlActivateChannel.argtypes = [
    xllinclass.XLportHandle,
    xllinclass.XLaccess,
    ctypes.c_uint,
    ctypes.c_uint,
]
xlActivateChannel.restype = xllinclass.XLstatus
xlActivateChannel.errcheck = check_status_operation

xlDeactivateChannel = _xlapi_dll.xlDeactivateChannel
xlDeactivateChannel.argtypes = [
    xllinclass.XLportHandle,
    xllinclass.XLaccess,
]
xlDeactivateChannel.restype = xllinclass.XLstatus
xlDeactivateChannel.errcheck = check_status_operation

xlReceive = _xlapi_dll.xlReceive
xlReceive.argtypes = [
    xllinclass.XLportHandle,
    ctypes.POINTER(ctypes.c_uint),
    ctypes.POINTER(xllinclass.XLevent),
]
xlReceive.restype = xllinclass.XLstatus

# LIN send request - may need to use generic transmit
# xlLinSendRequest = _xlapi_dll.xlLinSendRequest
# xlLinSendRequest.argtypes = [
#     xllinclass.XLportHandle,
#     xllinclass.XLaccess,
#     ctypes.c_ubyte,
#     ctypes.c_uint,
# ]
# xlLinSendRequest.restype = xllinclass.XLstatus
# xlLinSendRequest.errcheck = check_status_operation

# Use generic transmit function for LIN
xlTransmit = _xlapi_dll.xlTransmit
xlTransmit.argtypes = [
    xllinclass.XLportHandle,
    xllinclass.XLaccess,
    ctypes.POINTER(ctypes.c_uint),
    ctypes.POINTER(xllinclass.XLevent),
]
xlTransmit.restype = xllinclass.XLstatus
xlTransmit.errcheck = check_status_operation

xlCanSetChannelBitrate = _xlapi_dll.xlCanSetChannelBitrate
xlCanSetChannelBitrate.argtypes = [
    xllinclass.XLportHandle,
    xllinclass.XLaccess,
    ctypes.c_ulong,
]
xlCanSetChannelBitrate.restype = xllinclass.XLstatus
xlCanSetChannelBitrate.errcheck = check_status_operation