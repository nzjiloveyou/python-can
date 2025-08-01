"""
This module contains the implementation of linbus , contains :
1. driver init
2. channel setup
3. on bus send and receive
"""
import time
import atexit
import weakref

from can.interfaces.vector import canlib
import ctypes
from .lin_message import LINMessage
from .vetor_xl_lin import xlclass_lin

from typing import (
    Dict,
    Any,
    cast,
    Optional,
    Union,
    List,
    Tuple,
    Sequence,
    Callable,
)

from . import vetor_xl_lin
import logging

from can.interfaces.vector.exceptions import VectorError, VectorInitializationError, VectorOperationError

from can.util import (
    # dlc2len,
    # len2dlc,
    time_perfcounter_correlation,
)
LOG = logging.getLogger(__name__)


WaitForSingleObject: Optional[Callable[[int, int], int]]
INFINITE: Optional[int]
try:
    # Try builtin Python 3 Windows API
    from _winapi import (  # type: ignore[attr-defined,no-redef,unused-ignore]
        INFINITE,
        WaitForSingleObject,
    )

    HAS_EVENTS = True
except ImportError:
    WaitForSingleObject, INFINITE = None, None
    HAS_EVENTS = False

# 全局管理所有 VectorLINBus 实例
_active_buses = weakref.WeakSet()
_cleanup_registered = False

def _cleanup_all_buses():
    """在程序退出时清理所有活动的总线"""
    for bus in list(_active_buses):
        try:
            if hasattr(bus, '_is_shutdown') and not bus._is_shutdown:
                bus._is_shutdown = True
        except:
            pass


class VectorLINBus:
    """The LIN  Bus Vector implemented for the Vector interface."""

    def __init__(
            self,
            channel: Union[int, Sequence[int], str],
            app_name: Optional[str] = "VCDS",
            serial: Optional[int] = None,
            rx_queue_size: int = 8196,
            # bitrate: Optional[int] = None,
            **kwargs: Any
    ):
        """
        Create a LIN bus vector.
        channel: The channel to use.
        app_name:  The name of the application.
        serial:  The serial number of the vector device to use.
        rx_queue_size:  The size of the receive queue.
        """
        self.event_handle = None

        poll_interval: float = 0.01
        self.poll_interval = poll_interval

        self._is_shutdown: bool = False

        if canlib.xldriver is None:
            raise ImportError("The Vector API has not been loaded")
        self.xldriver_common = canlib.xldriver
        self.xldriver_lin = vetor_xl_lin.xldriver_lin

        self.RECV_LOGGING_LEVEL = 9
        result = self.xldriver_common.xlOpenDriver()
        if result != canlib.xldefine.XL_Status.XL_SUCCESS:
            print("Error opening driver: {}".format(result))
            # todo log output

        #  如果 `channel` 是整数，则将其存储为单个元素的列表。
        #  如果 `channel` 是字符串，则根据逗号分割并转换为整数列表。
        #  如果 `channel` 是序列，则直接将每个元素转换为整数后存储。
        self.channels: Sequence[int]
        if isinstance(channel, int):
            self.channels = [channel]
        elif isinstance(channel, str):
            self.channels = [int(ch.strip()) for ch in channel.split(",")]
        elif isinstance(channel, Sequence):
            self.channels = [int(ch) for ch in channel]
        else:
            raise TypeError(
                f"Invalid type for parameter 'channel': {type(channel).__name__}"
            )

        self._app_name = app_name.encode() if app_name is not None else b""
        self.channel_info = "Application {}: {}".format(
            app_name,
            ", ".join(f"LIN {ch + 1}" for ch in self.channels),
        )
        channel_configs = canlib.get_channel_configs()

        from pprint import pprint
        pprint(channel_configs)

        self.mask = 0
        self.channel_masks: Dict[int, int] = {}
        self.index_to_channel: Dict[int, int] = {}

        for channel in self.channels:
            if (
                    len(self.channels) == 1
                    and (_channel_index := kwargs.get("channel_index", None)) is not None
                    # 尝试从 kwargs 中获取键为 "channel_index" 的值。如果不存在该键，则返回 None。
            ):

                channel_index = cast(int, _channel_index)
            else:
                channel_index = self.find_global_channel_idx(
                    channel=channel,
                    serial=serial,
                    app_name=app_name,
                    channel_configs=channel_configs,

                )
                print(f"channel_index: {channel_index}")
            LOG.debug("Channel index %d found", channel)

            channel_mask = 1 << channel_index

            self.channel_masks[channel] = channel_mask
            self.index_to_channel[channel_index] = channel
            self.mask |= channel_mask

        permission_mask = canlib.xlclass.XLaccess()
        permission_mask.value = self.mask
        interface_version = (
            canlib.xldefine.XL_InterfaceVersion.XL_INTERFACE_VERSION

        )

        self.port_handle = canlib.xlclass.XLportHandle(canlib.xldefine.XL_INVALID_PORTHANDLE)
        # todo 目前遇到问题是连接多个设备后 hw_index会不更新 导致无法正确识别设备
        result = self.xldriver_common.xlOpenPort(
            self.port_handle,
            self._app_name,
            self.mask,
            permission_mask,
            rx_queue_size,
            interface_version,
            canlib.xldefine.XL_BusTypes.XL_BUS_TYPE_LIN
        )
        self.permission_mask = permission_mask.value

        LOG.debug(
            "Open Port: PortHandle: %d, ChannelMask: 0x%X, PermissionMask: 0x%X",
            self.port_handle.value,
            self.mask,
            self.permission_mask,
        )

        if HAS_EVENTS:  # True

            self.event_handle = vetor_xl_lin.xlclass_lin.XLhandle()
            self.xldriver_common.xlSetNotification(self.port_handle, self.event_handle, 1)
        else:
            pass
        offset = canlib.xlclass.XLuint64()
        try:
            if time.get_clock_info("time").resolution > 1e-5:
                ts, perfcounter = time_perfcounter_correlation()
                try:
                    self.xldriver_common.xlGetSyncTime(self.port_handle, offset)
                except VectorInitializationError:
                    self.xldriver_common.xlGetChannelTime(self.port_handle, self.mask, offset)
                current_perfcounter = time.perf_counter()
                now = ts + (current_perfcounter - perfcounter)
                self._time_offset = now - offset.value * 1e-9
            else:
                try:
                    self.xldriver_common.xlGetSyncTime(self.port_handle, offset)
                except VectorInitializationError:
                    self.xldriver_common.xlGetChannelTime(self.port_handle, self.mask, offset)
                self._time_offset = time.time() - offset.value * 1e-9

        except VectorInitializationError:
            self._time_offset = 0.0
        self._is_filtered = False

        try:
            rst = self.xldriver_common.xlActivateChannel(
                self.port_handle,
                self.mask,
                canlib.xldefine.XL_BusTypes.XL_BUS_TYPE_LIN,
                vetor_xl_lin.xldefine_lin.XL_flags.XL_LIN_FLAG_NONE)

        except VectorOperationError as error:
            self.shutdown()
            raise VectorInitializationError.from_generic(error) from None

        self.lin_sts = vetor_xl_lin.xlclass_lin.XLlinStatPar()
        self.lin_sts.LINMode = vetor_xl_lin.xldefine_lin.XL_LinMode.XL_LIN_MASTER
        self.lin_sts.baudrate = 19200
        self.lin_sts.LINVersion = vetor_xl_lin.xldefine_lin.XL_LinVersion.XL_LIN_VERSION_2_1

        rst = self.xldriver_lin.xlLinSetChannelParams(
            self.port_handle,
            self.mask,
            self.lin_sts)
        
        # 注册实例到全局集合
        global _cleanup_registered
        _active_buses.add(self)
        if not _cleanup_registered:
            _cleanup_registered = True
            atexit.register(_cleanup_all_buses)

    def shutdown(self):
        if self._is_shutdown:
            LOG.debug("%s is already shut down", self.__class__)
            return
        self._is_shutdown = True
        self.stop_all_periodic_tasks()

        # 简化关闭过程，避免可能导致崩溃的 API 调用
        # Vector 驱动会在进程退出时自动清理资源
        LOG.debug("VectorLINBus shutdown called - resources will be cleaned up automatically")

    def stop_all_periodic_tasks(self, remove_tasks: bool = True) -> None:
        pass
        # todo 当前无发送因此无需要停止的任务

    def find_global_channel_idx(
            self,
            channel: int,
            serial: Optional[int],
            app_name: Optional[str],
            channel_configs: List["canlib.xlclass.VectorChannelConfig"],
    ):
        if serial is not None:
            serial_found = False
            for channel_config in channel_configs:
                if channel_config.serial_number != serial:
                    continue

                serial_found = True
                if channel_config.hw_channel == channel:
                    return channel_config.channel_index

            if not serial_found:
                err_msg = f"No interface with serial {serial} found."
            else:
                err_msg = (
                    f"Channel {channel} not found on interface with serial {serial}."
                )
            print(err_msg)
            # # raise canlib.xlclass.CanInitializationError(
            # #     err_msg, error_code=canlib.xldefine.XL_Status.XL_ERR_HW_NOT_PRESENT
            # )

        if app_name:
            hw_type, hw_index, hw_channel = self.get_application_config(
                app_name, channel
            )
            print('hw_type, hw_index, hw_channel is', hw_type, hw_index, hw_channel)
            idx = cast(
                int, self.xldriver_common.xlGetChannelIndex(hw_type, hw_index, hw_channel)
            )
            if idx < 0:
                # Undocumented behavior! See issue #353.
                # If hardware is unavailable, this function returns -1.
                # Raise an exception as if the driver
                # would have signalled XL_ERR_HW_NOT_PRESENT.
                raise VectorInitializationError(
                    canlib.xldefine.XL_Status.XL_ERR_HW_NOT_PRESENT,
                    canlib.xldefine.XL_Status.XL_ERR_HW_NOT_PRESENT.name,
                    "xlGetChannelIndex",
                )
            return idx

        # check if channel is a valid global channel index
        for channel_config in channel_configs:
            if channel == channel_config.channel_index:
                return channel

        raise canlib.xlclass.CanInitializationError(
            f"Channel {channel} not found. The 'channel' parameter must be "
            f"a valid global channel index if neither 'app_name' nor 'serial' were given.",
            error_code=canlib.xldefine.XL_Status.XL_ERR_HW_NOT_PRESENT,
        )

    @staticmethod
    def get_application_config(
            app_name: str, app_channel: int
    ) -> Tuple[Union[int, canlib.xldefine.XL_HardwareType], int, int]:
        """Retrieve information for an application in Vector Hardware Configuration.

        :param app_name:
            The name of the application.
        :param app_channel:
            The channel of the application.
        :return:
            Returns a tuple of the hardware type, the hardware index and the
            hardware channel.

        :raises can.interfaces.vector.VectorInitializationError:
            If the application name does not exist in the Vector hardware configuration.
        """
        if canlib.xldriver is None:
            raise canlib.xlclass.CanInterfaceNotImplementedError("The Vector API has not been loaded")

        hw_type = ctypes.c_uint()
        hw_index = ctypes.c_uint()
        hw_channel = ctypes.c_uint()
        _app_channel = ctypes.c_uint(app_channel)

        try:
            print(app_name.encode(), _app_channel, hw_type, hw_index, hw_channel)
            canlib.xldriver.xlGetApplConfig(
                app_name.encode(),
                _app_channel,
                hw_type,
                hw_index,
                hw_channel,
                canlib.xldefine.XL_BusTypes.XL_BUS_TYPE_LIN,
            )
        except VectorError as e:
            raise VectorInitializationError(
                error_code=e.error_code,
                error_string=(
                    f"Vector HW Config: Channel '{app_channel}' of "
                    f"application '{app_name}' is not assigned to any interface"
                ),
                function="xlGetApplConfig",
            ) from None
        return canlib._hw_type(hw_type.value), hw_index.value, hw_channel.value

    @staticmethod
    def set_application_config(
            app_name: str,
            app_channel: int,
            hw_type: Union[int, canlib.xldefine.XL_HardwareType],
            hw_index: int,
            hw_channel: int,

    ) -> None:
        """Modify the application settings in Vector Hardware Configuration.

        This method can also be used with a channel config dictionary::
            import can
            from can.interfaces.vector import VectorBus

            configs = can.detect_available_configs(interfaces=['vector'])
            cfg = configs[0]
            VectorBus.set_application_config(app_name="MyApplication", app_channel=0, **cfg)
        :param app_name:
            The name of the application. Creates a new application if it does
            not exist yet.
        :param app_channel:
            The channel of the application.
        :param hw_type:
            The hardware type of the interface.
            E.g XL_HardwareType.XL_HWTYPE_VIRTUAL
        :param hw_index:
            The index of the interface if multiple interface with the same
            hardware type are present.
        :param hw_channel:
            The channel index of the interface.
        :raises can.interfaces.vector.VectorInitializationError:
            If the application name does not exist in the Vector hardware configuration.
        """
        if canlib.xldriver is None:
            raise canlib.xlclass.CanInterfaceNotImplementedError("The Vector API has not been loaded")

        canlib.xldriver.xlSetApplConfig(
            app_name.encode(),
            app_channel,
            hw_type,
            hw_index,
            hw_channel,
            canlib.xldefine.XL_BusTypes.XL_BUS_TYPE_CAN,
        )

    # lin 相关的方法
    def channel_setup_Setdlc(self, dlc_values):
        dlc_array = (ctypes.c_uint8 * 60)(*dlc_values)
        self.xldriver_lin.xlLinSetDLC(
            self.port_handle,
            self.mask,
            ctypes.byref(dlc_array))

    def channel_setup_SetChecksum(self):
        # todo  当前默认都设置为不包含 checksum

        # 创建一个包含 60 个 unsigned char 的数组
        checksum = (ctypes.c_uint8 * 60)()
        # 使用循环将所有元素设为 255
        for i in range(60):
            checksum[i] = 255
        checksum_ptr = (ctypes.c_uint8 * 60)(*checksum)

        self.xldriver_lin.xlLinSetChecksum(
            self.port_handle,
            self.mask,
            checksum_ptr)

    def init_master(self,  dlc_values):

        self.channel_setup_SetChecksum()
        self.channel_setup_Setdlc(dlc_values)

        self.lin_sts = vetor_xl_lin.xlclass_lin.XLlinStatPar()
        self.lin_sts.LINMode = vetor_xl_lin.xldefine_lin.XL_LinMode.XL_LIN_MASTER
        self.lin_sts.LINVersion = vetor_xl_lin.xldefine_lin.XL_LinVersion.XL_LIN_VERSION_2_1

        self.xldriver_lin.xlLinSetChannelParams(
            self.port_handle,
            self.mask,
            self.lin_sts)

        # activate channels
        result = self.xldriver_common.xlActivateChannel(
            self.port_handle,
            self.mask,
            canlib.xldefine.XL_BusTypes.XL_BUS_TYPE_LIN,
            vetor_xl_lin.xldefine_lin.XL_flags.XL_LIN_FLAG_NONE)

        print('xlActivateChannel result is ', result)

    def init_slave(self, dlc_values):

        self.channel_setup_SetChecksum()
        self.channel_setup_Setdlc(dlc_values)

        self.lin_sts = vetor_xl_lin.xlclass_lin.XLlinStatPar()
        self.lin_sts.LINMode = vetor_xl_lin.xldefine_lin.XL_LinMode.XL_LIN_SLAVE
        self.lin_sts.LINVersion = vetor_xl_lin.xldefine_lin.XL_LinVersion.XL_LIN_VERSION_2_1

        self.xldriver_lin.xlLinSetChannelParams(
            self.port_handle,
            self.mask,
            self.lin_sts)

        # activate channels
        result = self.xldriver_common.xlActivateChannel(
            self.port_handle,
            self.mask,
            canlib.xldefine.XL_BusTypes.XL_BUS_TYPE_LIN,
            vetor_xl_lin.xldefine_lin.XL_flags.XL_LIN_FLAG_NONE)

        print('xlActivateChannel result is ', result)

    def wake_up(self):

        # self.xldriver_lin.xlLinSetSleepMode(
        #     self.port_handle,
        #     self.mask,
        #     vetor_xl_lin.xldefine_lin.XL_SleepMode.XL_LIN_SET_WAKEUPID)
        self.xldriver_lin.xlLinWakeUp(self.port_handle, self.mask)

    def send(self, msg: LINMessage, lin_id):
        mask = self._get_tx_channel_mask([msg])
        lin_id = ctypes.c_ubyte(lin_id)
        flags = ctypes.c_uint(0)
        self.xldriver_lin.xlLinSendRequest(
            self.port_handle,
            mask,
            lin_id,
            flags
        )

    def set_slave(self,
                  lin_id,
                  value: list,
                  dlc
                  ):

        lin_id = ctypes.c_ubyte(lin_id)
        # 创建一个包含8个无符号整数的数组

        lin_slave_data = (ctypes.c_uint * 8)(*value)

        # 将数组转换为指针类型
        data_ptr = ctypes.cast(lin_slave_data, ctypes.POINTER(ctypes.c_uint * 8))
        self.xldriver_lin.xlLinSetSlave(
            self.port_handle,
            self.mask,
            lin_id,
            data_ptr,
            ctypes.c_uint(dlc),
            vetor_xl_lin.xldefine_lin.XL_LIN_CHECKSUM_CLASSIC.XL_LIN_CHECKSUM_CLASSIC
        )

    def _get_tx_channel_mask(self, msgs: Sequence[LINMessage]) -> int:
        if len(msgs) == 1:
            return self.channel_masks.get(msgs[0].channel, self.mask)  # type: ignore[arg-type]
        else:
            return self.mask

    def _recv_lin(self):
        """
        接收LIN消息。

        Returns:
            Optional[LINMessage]: 返回收到的LINMessage对象，如果未收到任何LINMessage则返回None。
        """
        if self._is_shutdown:
            return None

        try:
            # xl_event = canlib.xlclass.XLevent()
            # 会报以下错误 argument 2: TypeError: expected LP_XLlinRxEvent instance instead of pointer to XLeven
            xl_lin_rx_event = xlclass_lin.XLEvent()
            event_count = ctypes.c_uint32(1)
            
            if self._is_shutdown:
                return None
                
            canlib.xldriver.xlReceive(self.port_handle,
                                      ctypes.byref(event_count),
                                      ctypes.byref(xl_lin_rx_event),
                                      )
            
            if self._is_shutdown:
                return None
                
            # 默认收到的报文都是接收方报文 设备并不不主动发送报文
            if xl_lin_rx_event.tag == vetor_xl_lin.xldefine_lin.XL_LIN_EventTags.XL_LIN_MSG:
                is_rx = True
                data_struct = xl_lin_rx_event.tagData.linMsgApi.linMsg
            else:
                return None
                
            lin_msg_id = data_struct.id
            lin_dlc = min(data_struct.dlc, 8)  # 确保DLC不超过8
            lin_flags = data_struct.flags
            lin_data = data_struct.data
            lin_crc = data_struct.crc

            timestamp = xl_lin_rx_event.timeStamp * 1e-9
            channel = self.index_to_channel.get(xl_lin_rx_event.chanIndex, 0)

            # 安全地转换 ctypes 数组到 Python bytes
            data_bytes = bytes(lin_data[:lin_dlc]) if lin_dlc > 0 else b''

            return LINMessage(
                timestamp=timestamp + self._time_offset,
                is_rx=is_rx,
                frame_id=lin_msg_id,
                data=data_bytes,
                checksum=lin_crc,
                channel=channel,
                is_error_frame=bool(False),  # todo lin报文的flag
            )
        except VectorOperationError as e:
            # XL_ERR_QUEUE_IS_EMPTY 是正常情况，不需要打印错误
            if e.error_code == canlib.xldefine.XL_Status.XL_ERR_QUEUE_IS_EMPTY:
                return None
            if self._is_shutdown:
                return None
            print(f"Error in _recv_lin: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None
        except Exception as e:
            if self._is_shutdown:
                return None
            print(f"Error in _recv_lin: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _recv_internal(self, timeout):
        """
        用于在指定超时时间内从 LIN 总线接收消息
        """
        if self._is_shutdown:
            return None, self._is_filtered
            
        end_time = time.time() + timeout if timeout is not None else None

        while True:
            if self._is_shutdown:
                return None, self._is_filtered
                
            try:
                msg = self._recv_lin()
            except VectorOperationError as exception:
                if self._is_shutdown:
                    return None, self._is_filtered
                if exception.error_code != canlib.xldefine.XL_Status.XL_ERR_QUEUE_IS_EMPTY:
                    raise
                # 如果接收过程中抛出 VectorOperationError不是 XL_ERR_QUEUE_IS_EMPTY，则重新抛出异常
            else:
                if msg:
                    return msg, self._is_filtered

            if end_time is not None and time.time() > end_time:
                return None, self._is_filtered
            # 如果 end_time 不为 None，并且当前时间已经超过 end_time，则返回 None 和 self._is_filtered，表示接收超时

            if HAS_EVENTS:
                # Wait for receive event to occur
                if end_time is None:
                    time_left_ms = INFINITE
                else:
                    time_left = end_time - time.time()
                    time_left_ms = max(0, int(time_left * 1000))
                if not self._is_shutdown:
                    WaitForSingleObject(self.event_handle.value, time_left_ms)  # type: ignore
                # 调用 WaitForSingleObject 函数，等待事件句柄 self.event_handle.value 在 time_left_ms 毫秒内被触发，
                # 程序会继续执行后续代码，处理事件触发的逻辑
            else:
                # Wait a short time until we try again
                time.sleep(self.poll_interval)

    def recv_lin(self, timeout):
        if self._is_shutdown:
            return None

        start = time.time()
        time_left = timeout
        while True:
            if self._is_shutdown:
                return None
            
            try:
                msg, already_filtered = self._recv_internal(timeout=time_left)
            except Exception as e:
                if self._is_shutdown:
                    return None
                raise

            if msg and not self._is_shutdown:  # todo , and (already_filtered or self._matches_filters(msg))
                # print("Received: ", msg)
                try:
                    print(msg)
                except Exception as e:
                    print(f"Error printing message: {type(e).__name__}: {e}")
                    # 尝试打印基本信息
                    try:
                        print(f"Message ID: {msg.frame_id}, Data length: {len(msg.data)}")
                    except:
                        pass
                return msg
                # if not, and timeout is None, try indefinitely
            elif timeout is None:
                continue
            else:
                time_left = timeout - (time.time() - start)

                if time_left > 0:
                    continue

                return None

    def fileno(self) -> int:
        raise NotImplementedError("fileno is not implemented using current  bus")






