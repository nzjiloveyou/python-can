"""
LIN (Local Interconnect Network) interface module for Python.
"""

from .bus import LinBusABC
from .message import LinMessage
from .collector import LinMessageCollector

__version__ = "0.1.0"

__all__ = [
    "LinBusABC",
    "LinMessage",
    "LinMessageCollector",
]