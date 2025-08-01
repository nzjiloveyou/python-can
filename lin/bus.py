"""
LIN bus abstract base class.
"""
from abc import ABC, abstractmethod
from typing import Optional, Union
from .message import LinMessage


class LinBusABC(ABC):
    """
    The LIN Bus Abstract Base Class that serves as the basis
    for all concrete LIN interfaces.
    """
    
    channel_info = "unknown"
    
    @abstractmethod
    def __init__(self, channel: Union[int, str], **kwargs):
        """
        Construct and open a LIN bus instance.
        
        :param channel: The LIN interface identifier
        :param kwargs: Backend dependent configurations
        """
        self._is_shutdown = False
    
    @abstractmethod
    def send(self, msg: LinMessage, timeout: Optional[float] = None) -> None:
        """
        Send a LIN message.
        
        :param msg: The message to send
        :param timeout: Optional timeout in seconds
        """
        raise NotImplementedError
    
    @abstractmethod
    def recv(self, timeout: Optional[float] = None) -> Optional[LinMessage]:
        """
        Receive a LIN message.
        
        :param timeout: Optional timeout in seconds
        :return: Received message or None if timeout
        """
        raise NotImplementedError
    
    @abstractmethod
    def shutdown(self) -> None:
        """
        Called to carry out any interface specific cleanup.
        """
        raise NotImplementedError
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
    
    def __del__(self):
        if not self._is_shutdown:
            self.shutdown()