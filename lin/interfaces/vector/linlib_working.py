"""
基于工作代码的Vector LIN接口实现
"""
import ctypes
import logging
import time
from typing import Optional, Union

from can.interfaces.vector import xlclass, xldefine, xldriver
from can.interfaces.vector.exceptions import VectorInitializationError, VectorOperationError
from can.util import time_perfcounter_correlation

from ...bus import LinBusABC
from ...message import LinMessage
from . import xllinclass, xllindefine

LOG = logging.getLogger(__name__)

# Windows API for events
try:
    from _winapi import INFINITE, WaitForSingleObject
    HAS_EVENTS = True
except ImportError:
    WaitForSingleObject, INFINITE = None, None
    HAS_EVENTS = False


class VectorLinBusWorking(LinBusABC):
    """
    基于工作代码的LIN Bus实现
    """
    
    def __init__(
        self,
        channel: Union[int, str] = 0,
        channel_index: Optional[int] = None,
        app_name: Optional[str] = "Python-LIN",
        baudrate: int = 19200,
        rx_queue_size: int = 8196,
        poll_interval: float = 0.01,
        **kwargs,
    ):
        """
        初始化Vector LIN接口
        
        :param channel: 硬件通道号 (hw_channel)
        :param channel_index: 通道索引（如果提供，将直接使用）
        :param app_name: 应用程序名称
        :param baudrate: LIN波特率
        :param rx_queue_size: 接收队列大小
        :param poll_interval: 轮询间隔
        """
        super().__init__(channel=channel, **kwargs)
        
        self.poll_interval = poll_interval
        self.event_handle = None
        self._time_offset = 0.0
        self.RECV_LOGGING_LEVEL = 9  # 与工作代码相同
        
        if xldriver is None:
            raise ImportError("Vector API has not been loaded")
        
        self.xldriver = xldriver
        
        # 打开驱动
        result = self.xldriver.xlOpenDriver()
        if result != xldefine.XL_Status.XL_SUCCESS and result != 119:  # 119 = already open
            LOG.warning(f"Error opening driver: {result}")
        
        # 处理通道
        if isinstance(channel, int):
            self.channels = [channel]
        else:
            self.channels = [int(ch.strip()) for ch in str(channel).split(",")]
        
        self._app_name = app_name.encode() if app_name else b""
        self.channel_info = f"LIN Channel: {channel}"
        
        # 处理channel_index - 这是关键
        # 如果kwargs中有channel_index，使用它
        if 'channel_index' in kwargs:
            channel_index = kwargs['channel_index']
        
        # 计算通道掩码
        self.mask = 0
        self.channel_masks = {}
        self.index_to_channel = {}
        
        for ch in self.channels:
            # 如果提供了channel_index，直接使用
            if channel_index is not None:
                ch_index = channel_index
            else:
                # 否则使用通道号作为索引
                ch_index = ch
            
            ch_mask = 1 << ch_index
            self.channel_masks[ch] = ch_mask
            self.index_to_channel[ch_index] = ch
            self.mask |= ch_mask
        
        # 设置权限掩码
        permission_mask = xlclass.XLaccess()
        permission_mask.value = self.mask
        
        # 打开端口
        self.port_handle = xlclass.XLportHandle(xldefine.XL_INVALID_PORTHANDLE)
        interface_version = xldefine.XL_InterfaceVersion.XL_INTERFACE_VERSION
        
        result = self.xldriver.xlOpenPort(
            ctypes.byref(self.port_handle),
            self._app_name,
            self.mask,
            ctypes.byref(permission_mask),
            rx_queue_size,
            interface_version,
            xldefine.XL_BusTypes.XL_BUS_TYPE_LIN
        )
        
        if result != xldefine.XL_Status.XL_SUCCESS:
            raise VectorInitializationError(result, "xlOpenPort failed", "xlOpenPort")
        
        self.permission_mask = permission_mask.value
        LOG.info(f"Opened LIN port: handle={self.port_handle.value}, mask=0x{self.mask:X}")
        
        # 设置事件通知
        if HAS_EVENTS:
            self.event_handle = xlclass.XLhandle()
            self.xldriver.xlSetNotification(self.port_handle, ctypes.byref(self.event_handle), 1)
        
        # 同步时间
        self._setup_time_offset()
        
        # 激活通道
        try:
            result = self.xldriver.xlActivateChannel(
                self.port_handle,
                self.mask,
                xldefine.XL_BusTypes.XL_BUS_TYPE_LIN,
                0  # flags
            )
            if result != xldefine.XL_Status.XL_SUCCESS:
                raise VectorOperationError(result, "xlActivateChannel failed", "xlActivateChannel")
        except VectorOperationError as e:
            self.shutdown()
            raise VectorInitializationError.from_generic(e)
        
        # 设置LIN参数（如果有原生LIN支持）
        try:
            from . import xllindriver
            if hasattr(xllindriver, 'xlLinSetChannelParams'):
                lin_params = xllinclass.XLlinStatPar()
                lin_params.LINMode = 1  # Master mode
                lin_params.baudrate = baudrate
                lin_params.LINVersion = xllindefine.XL_LIN_Version.XL_LIN_VERSION_2_1
                
                xllindriver.xlLinSetChannelParams(
                    self.port_handle,
                    self.mask,
                    ctypes.byref(lin_params)
                )
        except Exception as e:
            LOG.debug(f"Could not set LIN params (using CAN mode): {e}")
        
        LOG.info("Vector LIN interface initialized successfully")
    
    def _setup_time_offset(self):
        """设置时间偏移"""
        offset = xlclass.XLuint64()
        try:
            if time.get_clock_info("time").resolution > 1e-5:
                ts, perfcounter = time_perfcounter_correlation()
                try:
                    self.xldriver.xlGetSyncTime(self.port_handle, ctypes.byref(offset))
                except VectorInitializationError:
                    self.xldriver.xlGetChannelTime(self.port_handle, self.mask, ctypes.byref(offset))
                current_perfcounter = time.perf_counter()
                now = ts + (current_perfcounter - perfcounter)
                self._time_offset = now - offset.value * 1e-9
            else:
                try:
                    self.xldriver.xlGetSyncTime(self.port_handle, ctypes.byref(offset))
                except VectorInitializationError:
                    self.xldriver.xlGetChannelTime(self.port_handle, self.mask, ctypes.byref(offset))
                self._time_offset = time.time() - offset.value * 1e-9
        except VectorInitializationError:
            self._time_offset = 0.0
    
    def recv(self, timeout: Optional[float] = None) -> Optional[LinMessage]:
        """接收LIN消息"""
        end_time = time.time() + timeout if timeout else None
        
        while True:
            if self.event_handle and timeout is not None:
                time_left = max(0, int((end_time - time.time()) * 1000)) if end_time else INFINITE
                if WaitForSingleObject(self.event_handle.value, time_left) != 0:
                    return None
            
            # 接收消息 - 使用CAN的XLevent结构
            event = xlclass.XLevent()
            event_count = ctypes.c_uint(1)
            
            result = self.xldriver.xlReceive(
                self.port_handle,
                ctypes.byref(event_count),
                ctypes.byref(event)
            )
            
            if result == xldefine.XL_Status.XL_SUCCESS and event_count.value > 0:
                # 检查事件类型
                # print(f"DEBUG: Received event with tag: {event.tag}")
                
                # 处理LIN消息 (标签20)
                if event.tag == xllindefine.XL_LIN_EventTags.XL_LIN_MSG:
                    try:
                        # LIN数据在CAN XLevent中的布局：
                        # 对于LIN消息，数据存储在tagData的原始字节中
                        # 需要手动解析LIN消息结构
                        
                        # 获取tagData的原始字节
                        raw_data = ctypes.cast(ctypes.byref(event.tagData), ctypes.POINTER(ctypes.c_ubyte))
                        
                        # LIN消息结构偏移：
                        # id: offset 0
                        # dlc: offset 1
                        # flags: offset 2-3
                        # data: offset 4-11
                        # crc: offset 12
                        
                        lin_id = raw_data[0] & 0x3F  # LIN ID是6位
                        lin_dlc = min(raw_data[1], 8)  # DLC最大8
                        # flags = (raw_data[3] << 8) | raw_data[2]  # 16位flags
                        
                        # 提取数据字节
                        data_bytes = bytes(raw_data[4:4+lin_dlc]) if lin_dlc > 0 else b''
                        lin_crc = raw_data[12]
                        
                        msg = LinMessage(
                            timestamp=self._time_offset + event.timeStamp * 1e-9,
                            frame_id=lin_id,
                            data=data_bytes,
                            checksum=lin_crc,
                            direction="Rx",
                            channel=str(self.channels[0])
                        )
                        
                        LOG.log(self.RECV_LOGGING_LEVEL, 
                               f"Received LIN: ID=0x{msg.frame_id:02X} Data={data_bytes.hex(' ')} Checksum=0x{lin_crc:02X}")
                        return msg
                    except Exception as e:
                        LOG.debug(f"Error processing LIN message: {e}")
                elif event.tag == xllindefine.XL_LIN_EventTags.XL_LIN_NOANS:
                    # 无应答事件
                    try:
                        raw_data = ctypes.cast(ctypes.byref(event.tagData), ctypes.POINTER(ctypes.c_ubyte))
                        no_ans_id = raw_data[0] & 0x3F
                        LOG.debug(f"LIN no answer event for ID: 0x{no_ans_id:02X}")
                    except:
                        pass
                    return None
            
            if end_time and time.time() > end_time:
                return None
            
            if not self.event_handle:
                time.sleep(self.poll_interval)
    
    def send(self, msg: LinMessage, timeout: Optional[float] = None) -> None:
        """发送LIN消息"""
        # 尝试使用原生LIN发送功能
        try:
            from . import xllindriver
            if hasattr(xllindriver, 'xlLinSendRequest'):
                # 使用原生LIN API发送请求
                lin_id = ctypes.c_ubyte(msg.frame_id)
                flags = ctypes.c_uint(0)
                
                result = xllindriver.xlLinSendRequest(
                    self.port_handle,
                    self.mask,
                    lin_id,
                    flags
                )
                
                if result == xldefine.XL_Status.XL_SUCCESS:
                    LOG.debug(f"Sent LIN request: ID=0x{msg.frame_id:02X}")
                    return
        except Exception as e:
            LOG.debug(f"Native LIN send not available: {e}")
        
        # 如果原生LIN不可用，使用通用传输方法
        # 创建CAN格式的事件，但填充LIN数据
        event = xlclass.XLevent()
        event.tag = xldefine.XL_EventTags.XL_TRANSMIT_MSG
        event.timeStamp = 0
        event.chanIndex = 0
        
        # 对于LIN over CAN模式，使用CAN消息格式
        event.tagData.msg.id = msg.frame_id
        event.tagData.msg.dlc = len(msg.data)
        event.tagData.msg.flags = 0
        
        # 复制数据
        for i, byte_val in enumerate(msg.data[:8]):
            event.tagData.msg.data[i] = byte_val
        
        msg_count = ctypes.c_uint(1)
        
        result = self.xldriver.xlTransmit(
            self.port_handle,
            self.mask,
            ctypes.byref(msg_count),
            ctypes.byref(event)
        )
        
        if result != xldefine.XL_Status.XL_SUCCESS:
            raise VectorOperationError(result, "xlTransmit failed", "xlTransmit")
        
        LOG.debug(f"Sent LIN message: ID=0x{msg.frame_id:02X}")
    
    def shutdown(self) -> None:
        """关闭LIN接口"""
        if not self._is_shutdown:
            try:
                self.xldriver.xlDeactivateChannel(self.port_handle, self.mask)
                self.xldriver.xlClosePort(self.port_handle)
            except Exception as e:
                LOG.warning(f"Error during shutdown: {e}")
            
            self._is_shutdown = True
            LOG.info("Vector LIN interface shut down")