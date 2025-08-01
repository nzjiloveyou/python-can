"""
Vector LIN interface implementation based on CAN infrastructure.
This approach reuses the existing Vector CAN implementation.
"""
import logging
from typing import Optional, Union

from can.interfaces.vector import VectorBus, xldefine
from can import Message as CanMessage
from ...bus import LinBusABC
from ...message import LinMessage

LOG = logging.getLogger(__name__)


class VectorLinBus(LinBusABC):
    """
    LIN Bus implementation for Vector devices using CAN infrastructure.
    
    This implementation leverages the existing Vector CAN interface
    since Vector XL API handles both CAN and LIN through similar mechanisms.
    """
    
    def __init__(
        self,
        channel: Union[int, str],
        app_name: Optional[str] = None,
        baudrate: int = 19200,
        **kwargs,
    ):
        """
        Initialize Vector LIN interface.
        
        :param channel: Channel index or mask
        :param app_name: Application name (None to use global channel)
        :param baudrate: LIN baudrate (typically 19200)
        """
        super().__init__(channel=channel, **kwargs)
        
        # Initialize to None in case of error
        self._can_bus = None
        
        # Remove any CAN-specific kwargs that might cause issues
        filtered_kwargs = {k: v for k, v in kwargs.items() 
                          if k not in ['fd', 'data_bitrate', 'sjw_abr', 'tseg1_abr', 'tseg2_abr']}
        
        try:
            # Create underlying CAN bus with LIN bus type
            # Note: This is a workaround - ideally we'd set bus_type to LIN
            self._can_bus = VectorBus(
                channel=channel,
                app_name=app_name,
                bitrate=baudrate,
                **filtered_kwargs
            )
            
            self.channel_info = f"Vector LIN Channel (via CAN interface)"
            LOG.info("Vector LIN interface initialized using CAN infrastructure")
        except Exception as e:
            self._is_shutdown = True
            raise Exception(
                f"Failed to initialize Vector LIN interface: {e}\n"
                "Possible solutions:\n"
                "1. Use app_name=None to use global channel\n"
                "2. Configure the channel in Vector Hardware Config\n"
                "3. Check if Vector hardware is connected"
            )
    
    def send(self, msg: LinMessage, timeout: Optional[float] = None) -> None:
        """
        Send a LIN message.
        
        :param msg: The LIN message to send
        :param timeout: Optional timeout
        """
        if msg.frame_id > 63:
            raise ValueError(f"Invalid LIN ID {msg.frame_id}, must be 0-63")
        
        # Convert LIN message to CAN message
        can_msg = CanMessage(
            arbitration_id=msg.frame_id,
            data=msg.data,
            is_extended_id=False,  # LIN uses standard IDs
            timestamp=msg.timestamp,
        )
        
        self._can_bus.send(can_msg, timeout=timeout)
        LOG.debug(f"Sent LIN message ID 0x{msg.frame_id:02X}")
    
    def recv(self, timeout: Optional[float] = None) -> Optional[LinMessage]:
        """
        Receive a LIN message.
        
        :param timeout: Optional timeout in seconds
        :return: Received message or None
        """
        can_msg = self._can_bus.recv(timeout=timeout)
        
        if can_msg is None:
            return None
        
        # Convert CAN message to LIN message
        lin_msg = LinMessage(
            timestamp=can_msg.timestamp,
            frame_id=can_msg.arbitration_id & 0x3F,  # Ensure 6-bit ID
            data=can_msg.data,
            direction="Rx",
            channel=can_msg.channel,
        )
        
        LOG.debug(f"Received LIN message ID 0x{lin_msg.frame_id:02X}")
        return lin_msg
    
    def shutdown(self) -> None:
        """Shutdown the LIN interface."""
        if not self._is_shutdown:
            if self._can_bus is not None:
                self._can_bus.shutdown()
            self._is_shutdown = True
            LOG.info("Vector LIN interface shut down")