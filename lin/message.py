"""
LIN message implementation.
"""
from typing import Optional, Union


class LinMessage:
    """
    The LinMessage object represents a LIN message for sending and receiving.
    
    LIN messages consist of:
    - Frame ID (0-63)
    - Data (0-8 bytes)
    - Checksum
    """
    
    __slots__ = (
        "__weakref__",
        "timestamp",
        "frame_id",
        "data",
        "checksum",
        "direction",  # "Rx" or "Tx"
        "is_error_frame",
        "channel",
    )
    
    def __init__(
        self,
        timestamp: float = 0.0,
        frame_id: int = 0,
        data: Optional[Union[bytes, bytearray, list[int]]] = None,
        checksum: Optional[int] = None,
        direction: str = "Rx",
        is_error_frame: bool = False,
        channel: Optional[str] = None,
    ):
        """
        Initialize a LIN message.
        
        :param timestamp: Timestamp of the message
        :param frame_id: LIN frame ID (0-63)
        :param data: Message data (0-8 bytes)
        :param checksum: Message checksum
        :param direction: "Rx" for received, "Tx" for transmitted
        :param is_error_frame: True if this is an error frame
        :param channel: Channel identifier
        """
        if frame_id < 0 or frame_id > 63:
            raise ValueError(f"Invalid LIN frame ID: {frame_id}. Must be 0-63.")
            
        self.timestamp = timestamp
        self.frame_id = frame_id
        self.direction = direction
        self.is_error_frame = is_error_frame
        self.channel = channel
        self.checksum = checksum
        
        if data is None:
            self.data = bytearray()
        elif isinstance(data, bytearray):
            self.data = data
        else:
            self.data = bytearray(data)
            
        if len(self.data) > 8:
            raise ValueError(f"LIN data length {len(self.data)} exceeds maximum of 8 bytes")
    
    def __str__(self) -> str:
        data_str = " ".join(f"{b:02X}" for b in self.data)
        return (
            f"LinMessage(ID: 0x{self.frame_id:02X}, "
            f"Data: [{data_str}], "
            f"Direction: {self.direction}, "
            f"Time: {self.timestamp:.6f})"
        )
    
    def __repr__(self) -> str:
        return self.__str__()