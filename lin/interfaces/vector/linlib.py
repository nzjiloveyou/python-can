"""
Vector LIN interface implementation.

This module provides two implementations:
1. Native LIN implementation (if LIN-specific functions are available)
2. CAN-based fallback implementation
"""
import ctypes
import logging
import time
from typing import Optional, Union

from ...bus import LinBusABC
from ...message import LinMessage

LOG = logging.getLogger(__name__)

# Try to import native implementation components
try:
    from . import xllinclass, xllindefine, xllindriver
    from .exceptions import VectorLinError, VectorLinInitializationError
    NATIVE_LIN_AVAILABLE = True
except Exception as e:
    LOG.warning(f"Native LIN support not available: {e}")
    NATIVE_LIN_AVAILABLE = False

# Import CAN-based fallback
try:
    from .linlib_can_based import VectorLinBus as VectorLinBusCanBased
    CAN_BASED_AVAILABLE = True
except Exception as e:
    LOG.warning(f"CAN-based LIN support not available: {e}")
    CAN_BASED_AVAILABLE = False


class VectorLinBus(LinBusABC):
    """
    The LIN Bus implementation for Vector devices.
    
    This class automatically selects between native LIN implementation
    and CAN-based fallback depending on available support.
    """
    
    def __new__(cls, *args, **kwargs):
        """
        Factory method to create appropriate implementation.
        """
        # Try working implementation first
        try:
            from .linlib_working import VectorLinBusWorking
            LOG.info("Using working LIN implementation")
            return VectorLinBusWorking(*args, **kwargs)
        except Exception as e:
            LOG.warning(f"Working implementation failed: {e}")
            
        # Fallback to CAN-based implementation
        if CAN_BASED_AVAILABLE:
            LOG.info("Using CAN-based LIN implementation")
            return VectorLinBusCanBased(*args, **kwargs)
        else:
            raise NotImplementedError("No suitable Vector LIN implementation available")


# For backwards compatibility, keep the original native implementation below
# (This can be enabled by setting FORCE_NATIVE_LIN = True)

FORCE_NATIVE_LIN = False

if FORCE_NATIVE_LIN and NATIVE_LIN_AVAILABLE:
    
    class VectorLinBusNative(LinBusABC):
        """
        Native LIN Bus implementation for Vector devices.
        """
        
        def __init__(
            self,
            channel: Union[int, str],
            app_name: str = "Python-LIN",
            baudrate: int = 19200,
            lin_version: int = xllindefine.XL_LIN_Version.XL_LIN_VERSION_2_1,
            poll_interval: float = 0.01,
            **kwargs,
        ):
            """Initialize Vector LIN interface with native support."""
            super().__init__(channel=channel, **kwargs)
            
            self.poll_interval = poll_interval
            self.port_handle = xllinclass.XLportHandle()
            self.mask = 0
            self.permission_mask = xllinclass.XLaccess()
            self.channel_index = channel if isinstance(channel, int) else 0
            
            # Open driver
            try:
                xllindriver.xlOpenDriver()
            except VectorLinInitializationError:
                pass
            
            # Calculate channel mask
            if isinstance(channel, int):
                self.mask = 1 << channel
            else:
                self.mask = int(channel, 16) if isinstance(channel, str) else channel
            
            # Open port
            self.permission_mask.value = self.mask
            xllindriver.xlOpenPort(
                ctypes.byref(self.port_handle),
                app_name.encode(),
                self.mask,
                ctypes.byref(self.permission_mask),
                256,
                xllindefine.XL_BUS_TYPE_LIN,
                0,
            )
            
            # Set baudrate
            try:
                xllindriver.xlCanSetChannelBitrate(
                    self.port_handle,
                    self.permission_mask,
                    baudrate,
                )
            except Exception as e:
                LOG.warning(f"Could not set LIN baudrate: {e}")
            
            # Activate channel
            xllindriver.xlActivateChannel(
                self.port_handle,
                self.permission_mask,
                xllindefine.XL_BUS_TYPE_LIN,
                0,
            )
            
            self.channel_info = f"Vector LIN Channel {self.channel_index}"
            LOG.info("Vector LIN interface initialized on channel %d", self.channel_index)
        
        def send(self, msg: LinMessage, timeout: Optional[float] = None) -> None:
            """Send a LIN message."""
            if msg.frame_id > xllindefine.XL_LIN_ID_MAX:
                raise ValueError(f"Invalid LIN ID {msg.frame_id}")
            
            # Create event for transmission
            event = xllinclass.XLevent()
            event.tag = xllindefine.XL_LIN_EventTags.XL_LIN_EV_TAG_TX_MSG
            event.tagData.linMsg.id = msg.frame_id
            event.tagData.linMsg.dlc = len(msg.data)
            event.tagData.linMsg.flags = xllindefine.XL_LIN_MessageFlags.XL_LIN_MSGFLAG_TX
            
            # Copy data
            for i, byte in enumerate(msg.data[:8]):
                event.tagData.linMsg.data[i] = byte
            
            msg_count = ctypes.c_uint(1)
            
            # Transmit
            xllindriver.xlTransmit(
                self.port_handle,
                self.permission_mask,
                ctypes.byref(msg_count),
                ctypes.byref(event),
            )
            
            LOG.debug("Sent LIN message ID 0x%02X", msg.frame_id)
        
        def recv(self, timeout: Optional[float] = None) -> Optional[LinMessage]:
            """Receive a LIN message."""
            end_time = time.time() + timeout if timeout else None
            
            while True:
                event = xllinclass.XLevent()
                event_count = ctypes.c_uint(1)
                
                status = xllindriver.xlReceive(
                    self.port_handle,
                    ctypes.byref(event_count),
                    ctypes.byref(event),
                )
                
                if status == 0 and event_count.value > 0:
                    if event.tag == xllindefine.XL_LIN_EventTags.XL_LIN_EV_TAG_RX_MSG:
                        lin_msg = event.tagData.linMsg
                        
                        msg = LinMessage(
                            timestamp=event.timeStamp / 1000000.0,
                            frame_id=lin_msg.id,
                            data=bytes(lin_msg.data[:lin_msg.dlc]),
                            checksum=lin_msg.crc,
                            direction="Rx",
                            channel=str(self.channel_index),
                        )
                        return msg
                
                if end_time and time.time() > end_time:
                    return None
                
                if self.poll_interval:
                    time.sleep(self.poll_interval)
        
        def shutdown(self) -> None:
            """Shutdown the LIN interface."""
            if not self._is_shutdown:
                try:
                    xllindriver.xlDeactivateChannel(
                        self.port_handle,
                        self.permission_mask,
                    )
                    xllindriver.xlClosePort(self.port_handle)
                    xllindriver.xlCloseDriver()
                except VectorLinError as e:
                    LOG.warning("Error during shutdown: %s", e)
                
                self._is_shutdown = True
                LOG.info("Vector LIN interface shut down")