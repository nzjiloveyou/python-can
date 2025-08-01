"""
The `lin_message` module contains the `LINMessage` class.


"""
from copy import deepcopy
from typing import Optional


class LINMessage:
    """
    The `LINMessage` object is used to represent LIN messages for sending,
    receiving, and logging purposes.
    """

    __slots__ = (
        "timestamp",
        "frame_id",
        "data",
        "checksum",
        "direction",
        "is_rx",
        "length",
        "channel",
        "is_error_frame",
        "__weakref__",
    )

    def __init__(
            self,
            timestamp: float = 0.0,
            frame_id: int = 0,
            data: Optional[bytes] = None,
            checksum: Optional[int] = None,
            # direction: str = "Tx",  # Tx for transmit, Rx for receive
            is_rx: bool = True,
            check: bool = False,
            channel: Optional[int] = None,
            is_error_frame: bool = False,
    ):
        self.timestamp = timestamp
        self.frame_id = frame_id
        self.data = data if data else bytes()
        self.checksum = checksum if checksum else self.calculate_checksum()
        # self.direction = direction
        self.is_rx = is_rx
        self.length = len(self.data)
        self.channel = channel
        self.is_error_frame = is_error_frame

        if check:
            self._check()

    def __str__(self) -> str:
        data_str = " ".join(f"{byte:02X}" for byte in self.data)
        return (
            f" Timestamp: {self.timestamp:.6f}  | Channel: {self.channel} "
            f" Frame ID: {self.frame_id:02X}  | "
            f" Data: {data_str}  | Length: {self.length}   "
            f" Checksum: {self.checksum:02X} ；|| Is Error Frame: {self.is_error_frame} | is_rx: {self.is_rx}  "

        )

    def __len__(self) -> int:
        return len(self.data)

    def __bool__(self) -> bool:
        return True

    def __repr__(self) -> str:
        return (
            f"LINMessage(timestamp={self.timestamp}, frame_id={self.frame_id}, "
            f"data={self.data}, checksum={self.checksum}, is_rx={self.is_rx}, "
            f"length={self.length}, channel={self.channel}, is_error_frame={self.is_error_frame})"
        )

    def __copy__(self) -> 'LINMessage':
        return LINMessage(
            timestamp=self.timestamp,
            frame_id=self.frame_id,
            data=self.data,
            checksum=self.checksum,
            is_rx=self.is_rx,
            channel=self.channel,
            is_error_frame=self.is_error_frame
        )

    def __deepcopy__(self, memo: dict) -> 'LINMessage':
        return LINMessage(
            timestamp=self.timestamp,
            frame_id=self.frame_id,
            data=deepcopy(self.data, memo),
            checksum=self.checksum,
            is_rx=self.is_rx,
            channel=self.channel,
            is_error_frame=self.is_error_frame
        )

    def _check(self) -> None:
        """Checks if the message parameters are valid."""
        if self.timestamp < 0.0:
            raise ValueError("Timestamp may not be negative.")
        if not (0 <= self.frame_id <= 0x3F):
            raise ValueError("Frame ID must be between 0 and 63.")
        if self.checksum is not None and not (0 <= self.checksum <= 0xFF):
            raise ValueError("Checksum must be a valid byte.")

    def calculate_checksum(self) -> int:
        """Calculate the checksum for the LIN message data."""
        return (sum(self.data) & 0xFF) ^ 0xFF  # Classic LIN checksum example

    def equals(
            self,
            other: 'LINMessage',
            timestamp_delta: Optional[float] = 1.0e-6,
            check_direction: bool = True,
    ) -> bool:
        """Compare two LIN messages."""
        return (
                self is other
                or (
                        (
                                timestamp_delta is None
                                or abs(self.timestamp - other.timestamp) <= timestamp_delta
                        )
                        and self.frame_id == other.frame_id
                        and self.data == other.data
                        and self.checksum == other.checksum
                        and (self.is_rx == other.is_rx or not check_direction)
                        and self.length == other.length
                        and (self.channel == other.channel or self.channel is None or other.channel is None)
                        and self.is_error_frame == other.is_error_frame
                )
        )




