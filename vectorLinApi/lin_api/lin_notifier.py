"""
This module contains the implementation of :class:`~lin.Notifier`.
"""

import asyncio
import functools
import logging
import threading
import time
from typing import Awaitable, Callable, Iterable, List, Optional, Union, cast

from .linlib import VectorLINBus
from .lin_message import LINMessage
from .lin_listener import LinListener

logger = logging.getLogger("lin.Notifier")

MessageRecipient = Union[LinListener, Callable[[LINMessage], Union[Awaitable[None], None]]]
# 定义了一个联合类型 MessageRecipient，
# 表示消息接收者可以是 LinListener 对象或一个可调用对象（函数或方法），
# 该可调用对象接受一个 LINMessage 参数并返回一个 Awaitable[None] 或 None。


class LinNotifier:
    def __init__(
        self,
        bus: Union[VectorLINBus, List[VectorLINBus]],
        listeners: Iterable[MessageRecipient],
        timeout: float = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        """Manages the distribution of :class:`~lin.LinMessage` instances to listeners.

        Supports multiple buses and listeners.

        Note::

            Remember to call `stop()` after all messages are received as
            many listeners carry out flush operations to persist data.

        :param bus: A LIN bus instance or a list of LIN buses to listen to.
        :param listeners:
            An iterable of :class:`~lin.LinListener` or callables that receive a
            :class:`~lin.LinMessage` and return nothing.
        :param timeout: An optional maximum number of seconds to wait for any
            :class:`~lin.LinMessage`.
        :param loop: An :mod:`asyncio` event loop to schedule the ``listeners`` in.
        """
        self.listeners: List[MessageRecipient] = list(listeners)
        self.bus = bus
        self.timeout = timeout
        self._loop = loop

        #: Exception raised in thread
        self.exception: Optional[Exception] = None

        self._running = True
        self._lock = threading.Lock()

        self._readers: List[Union[int, threading.Thread]] = []
        buses = self.bus if isinstance(self.bus, list) else [self.bus]
        for each_bus in buses:
            self.add_bus(each_bus)


            # note 多线程为各个Bus中对消息的接收

    def add_bus(self, bus: VectorLINBus) -> None:
        #  NOTE: 将VectorLINBus添加到监听器中
        """
        将1个VectorLINBus添加到监听器中。

        :param bus:
            LIN bus instance.
        """
        reader: int = -1
        try:
            reader = bus.fileno()
        except NotImplementedError:
            pass

        if self._loop is not None and reader >= 0:
            self._loop.add_reader(reader, self._on_message_available, bus)
            self._readers.append(reader)
        else:
            reader_thread = threading.Thread(
                target=self._rx_thread,
                args=(bus,),
                name=f'lin.notifier for bus "{bus.channel_info}"',
            )
            reader_thread.daemon = True
            reader_thread.start()
            self._readers.append(reader_thread)

    # todo stop
    def stop(self, timeout: float = 5) -> None:
        """Stop notifying Listeners when new :class:`~lin.LinMessage` objects arrive
        and call :meth:`~lin.LinListener.stop` on each Listener.

        :param timeout:
            Max time in seconds to wait for receive threads to finish.
            Should be longer than timeout given at instantiation.
        """
        self._running = False
        end_time = time.time() + timeout
        for reader in self._readers:
            if isinstance(reader, threading.Thread):
                now = time.time()
                if now < end_time:
                    reader.join(end_time - now)
            elif self._loop:
                # reader is a file descriptor
                self._loop.remove_reader(reader)
        for listener in self.listeners:
            if hasattr(listener, "stop"):
                print("stop")
                listener.stop()

    def _rx_thread(self, bus: VectorLINBus) -> None:
        # NOTE: LIN总线接收消息的处理程序
        """LIN总线接收消息的处理程序"""
        # determine message handling callable early, not inside while loop
        handle_message = cast(
            Callable[[LINMessage], None],     # Callable[[LINMessage], None] 表示一个函数类型
            (
                self._on_message_received
                if self._loop is None     # None
                else functools.partial(
                    self._loop.call_soon_threadsafe, self._on_message_received
                )
            ),
        )
        while self._running:   # True
            try:
                if not self._running:
                    break
                if msg := bus.recv_lin(self.timeout):
                    # self._lock = threading.Lock()
                    with self._lock:
                        # self._lock.acquire()
                        if self._running:  # 再次检查，避免在停止后处理消息
                            handle_message(msg)
            except Exception as exc:  # pylint: disable=broad-except
                if not self._running:
                    break  # 如果正在停止，忽略异常并退出
                self.exception = exc
                if self._loop is not None:
                    self._loop.call_soon_threadsafe(self._on_error, exc)
                    # Raise anyway
                    raise
                elif not self._on_error(exc):
                    # If it was not handled, raise the exception here
                    raise
                else:
                    # It was handled, so only log it
                    logger.debug("suppressed exception: %s", exc)

    def _on_message_available(self, bus: VectorLINBus) -> None:
        if msg := bus.recv_lin(0):
            self._on_message_received(msg)

    def _on_message_received(self, msg: LINMessage) -> None:
        for callback in self.listeners:
            # NOTE: 如果回调函数返回一个可执行对象，即‘__call__’，那么这里会将其加入到事件循环中
            res = callback(msg)
            if res and self._loop and asyncio.iscoroutine(res):
                # Schedule coroutine
                self._loop.create_task(res)

    def _on_error(self, exc: Exception) -> bool:
        """Calls ``on_error()`` for all listeners if they implement it.

        :returns: ``True`` if at least one error handler was called.
        """
        was_handled = False

        for listener in self.listeners:
            if hasattr(listener, "on_error"):
                try:
                    listener.on_error(exc)
                except NotImplementedError:
                    pass
                else:
                    was_handled = True

        return was_handled

    def add_listener(self, listener: MessageRecipient) -> None:
        """Add new Listener to the notification list.
        If it is already present, it will be called two times
        each time a message arrives.

        :param listener: Listener to be added to the list to be notified
        """
        if listener not in self.listeners:
            self.listeners.append(listener)
        else:
            print("Listener already added!")
            pass

    def remove_listener(self, listener: MessageRecipient) -> None:
        """Remove a listener from the notification list. This method
        throws an exception if the given listener is not part of the
        stored listeners.

        :param listener: Listener to be removed from the list to be notified
        :raises ValueError: if `listener` was never added to this notifier
        """
        if listener in self.listeners:
            self.listeners.remove(listener)
        else:
            pass  # todo 错误提示
