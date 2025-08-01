"""
This module contains the implementation of `lin.Listener` and some readers.
"""

from abc import ABCMeta, abstractmethod
from queue import Empty, SimpleQueue
from typing import Optional
from .lin_message import LINMessage


class LinListener(metaclass=ABCMeta):
    """The basic listener that can be called directly to handle some
    LIN message::

        listener = SomeListener()
        msg = my_bus.recv()

        # now either call
        listener(msg)
        # or
        listener.on_message_received(msg)

        # Important to ensure all outputs are flushed
        listener.stop()
    """

    @abstractmethod
    def on_lin_message_received(self, msg: LINMessage) -> None:
        """This method is called to handle the given message.

        :param msg: the delivered message
        """

    def __call__(self, msg: LINMessage) -> None:
        # 可被调用函数
        self.on_lin_message_received(msg)

    def on_error(self, exc: Exception) -> None:
        """This method is called to handle any exception in the receive thread.

        :param exc: The exception causing the thread to stop
        """
        raise NotImplementedError()

    def stop(self) -> None:  # noqa: B027
        """
        Stop handling new messages, carry out any final tasks to ensure
        data is persisted and cleanup any open resources.

        Concrete implementations override.
        """
        print("stop1")

class LinBufferedReader(LinListener):  # pylint: disable=abstract-method
    """
    A BufferedReader is a subclass of :class:`~lin.Listener` which implements a
    **message buffer**: that is, when the :class:`lin.BufferedReader` instance is
    notified of a new message it pushes it into a queue of messages waiting to
    be serviced. The messages can then be fetched with
    :meth:`~lin.BufferedReader.get_message`.

    Putting in messages after :meth:`~lin.BufferedReader.stop` has been called will raise
    an exception, see :meth:`~lin.BufferedReader.on_message_received`.

    :attr is_stopped: ``True`` if the reader has been stopped
    """

    def __init__(self) -> None:
        # set to "infinite" size
        self.buffer: SimpleQueue[LINMessage] = SimpleQueue()
        self.is_stopped: bool = False

    def on_lin_message_received(self, msg: LINMessage) -> None:
        """Append a message to the buffer.

        :raises: BufferError
            if the reader has already been stopped
        """
        if self.is_stopped:
            raise RuntimeError("reader has already been stopped")
        else:
            self.buffer.put(msg)

    def get_message(self, timeout: float = 0.5) -> Optional[LINMessage]:
        """
        Attempts to retrieve the message that has been in the queue for the longest amount
        of time (FIFO). If no message is available, it blocks for given timeout or until a
        message is received (whichever is shorter), or else returns None. This method does
        not block after :meth:`lin.BufferedReader.stop` has been called.

        :param timeout: The number of seconds to wait for a new message.
        :return: the received :class:`lin.Message` or `None`, if the queue is empty.
        """
        try:
            return self.buffer.get(block=True, timeout=timeout)
        except Empty:
            return None

    def stop(self) -> None:
        """Prohibits any more additions to this reader."""
        self.is_stopped = True
