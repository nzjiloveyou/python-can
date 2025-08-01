import can.interfaces.vector.xlclass as origin_xlclass

import ctypes

"""
定义data types and structures for vxlapi，对LIN的内容进行补充

"""
XLuint64 = ctypes.c_int64
XLaccess = XLuint64
XLhandle = ctypes.c_void_p
XLstatus = ctypes.c_short
XLportHandle = ctypes.c_long
XLeventTag = ctypes.c_ubyte
XLstringType = ctypes.c_char_p


class XLlinStatPar(ctypes.Structure):
    _fields_ = [
        ("LINMode", ctypes.c_int),
        ("baudrate", ctypes.c_uint),
        ("LINVersion", ctypes.c_uint),
        ("reserved", ctypes.c_uint),

    ]


class XLLinMSG(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_ubyte),
        ("dlc", ctypes.c_ubyte),
        ("flags", ctypes.c_ushort),
        ("data", ctypes.c_ubyte * 8),
        ("crc", ctypes.c_ubyte),
]


class XLLinNoAns(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_ubyte),
    ]


class XLLinWakeUP(ctypes.Structure):
    _fields_ = [
            ("flag", ctypes.c_ubyte),  # unsigned char
            ("unused", ctypes.c_ubyte * 3),  # unsigned char[3]
            ("startOffs", ctypes.c_uint),  # unsigned int
            ("width", ctypes.c_uint)  # unsigned int
    ]


class XLLinSleep(ctypes.Structure):
    _fields_ = [
        ("flag", ctypes.c_ubyte),
    ]


class XLLinCRCInfo(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_ubyte),
        ("flags", ctypes.c_ubyte),
    ]


class XL_LinMsgAPI(ctypes.Union):
    _fields_ = [
        ("linMsg", XLLinMSG),
        ("linNoAns", XLLinNoAns),
        ("linWakeUp", XLLinWakeUP),
        ("linSleep", XLLinSleep),
        ("linCRCinfo", XLLinCRCInfo),
    ]


class XL_CAN_Msg(ctypes.Structure):
    _fields_ = [
        # 用适当类型定义字段，例如
        # ("id", ctypes.c_uint),
        # ("dlc", ctypes.c_ubyte),
        # ("data", ctypes.c_ubyte * 8),
    ]

class XL_ChipState(ctypes.Structure):
    _fields_ = [
        # 结构字段
    ]

class XL_SyncPulse(ctypes.Structure):
    _fields_ = [
        # 结构字段
    ]

class XL_Transceiver(ctypes.Structure):
    _fields_ = [
        # 结构字段
    ]

class XL_DaioData(ctypes.Structure):
    _fields_ = [
        # 结构字段
    ]

class XL_DaioPiggyData(ctypes.Structure):
    _fields_ = [
        # 结构字段
    ]

class XL_KlineData(ctypes.Structure):
    _fields_ = [
        # 结构字段
    ]


class s_rxTagData(ctypes.Union):   # s_xl_tag_data
    _fields_ = [
        ("msg", XL_CAN_Msg),
        ("chipState", XL_ChipState),
        ("linMsgApi", XL_LinMsgAPI),
        ("syncPulse", XL_SyncPulse),
        ("transceiver", XL_Transceiver),
        ("daioData", XL_DaioData),
        ("daioPiggyData", XL_DaioPiggyData),
        ("klineData", XL_KlineData),
    ]


class XLEvent(ctypes.Structure):   # s_xl_event
    _fields_ = [
        ("tag", XLeventTag),
        ("chanIndex", ctypes.c_ubyte),
        ("transId", ctypes.c_ushort),
        ("portHandle", ctypes.c_ushort),
        ("flags", ctypes.c_ubyte),
        ("reserved", ctypes.c_ubyte),
        ("timeStamp", XLuint64),
        ("tagData", s_rxTagData),
    ]


def print_union_fields(union_obj):
    """
    自动遍历并打印Union内部每个字段的所有子属性。
    每个字段本身也是一个c_types结构体或类似结构，因此再递归获取其 fields。
    注意Union只以某一个字段真实生效。
    """
    union_type = type(union_obj)
    # union_type.fields 中包含类似 [("linMsg", XLLinMSG), ("linNoAns", XLLinNoAns), ...]
    for field_name, field_type in union_type.fields:
        print(f"\nField: {field_name}")
        field_value = getattr(union_obj, field_name)
        # 若子字段本身还是一个结构体/Union，则可进一步遍历
        if hasattr(field_type, "fields"):
            for subfield_name, subfield_type in field_type.fields:
                subfield_value = getattr(field_value, subfield_name)
                print(f" {subfield_name}: {subfield_value}")
        else:
            # 如果不是结构体或者Union
            print(f" Value: {field_value}")