import gzip
import typing

if typing.TYPE_CHECKING:
    import os


class LINFilter(typing.Protocol):
    lin_id: int
    lin_mask: int


LINFilter = typing.Sequence[LINFilter]
