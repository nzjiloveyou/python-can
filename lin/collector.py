"""
LIN消息收集器模块
提供线程化的消息接收功能
"""
import time
import threading
from queue import Queue, Empty
from typing import List, Optional, Callable
from .bus import LinBusABC
from .message import LinMessage


class LinMessageCollector:
    """
    LIN消息收集器 - 使用后台线程接收消息
    
    Example:
        >>> from lin.interfaces.vector import VectorLinBus
        >>> from lin.collector import LinMessageCollector
        >>> 
        >>> with LinMessageCollector() as collector:
        ...     collector.register_bus(0, 0)
        ...     collector.start_collecting()
        ...     time.sleep(5)
        ...     messages = collector.stop_and_get_messages()
    """
    
    def __init__(self, print_messages: bool = True, message_formatter: Optional[Callable] = None):
        """
        初始化消息收集器
        
        :param print_messages: 是否实时打印收到的消息
        :param message_formatter: 自定义消息格式化函数
        """
        self.bus: Optional[LinBusABC] = None
        self.recv_thread: Optional[threading.Thread] = None
        self.message_queue = Queue()
        self._stop_event = threading.Event()
        self._closed = False
        self.print_messages = print_messages
        self.message_formatter = message_formatter or self._default_message_formatter
        
        # 统计信息
        self.total_messages = 0
        self.start_time = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    
    def register_bus(self, hw_channel: int = 0, channel_index: int = 0, 
                    app_name: Optional[str] = None, **kwargs):
        """
        注册LIN总线
        
        :param hw_channel: 硬件通道号
        :param channel_index: 通道索引
        :param app_name: 应用程序名称
        :param kwargs: 其他总线参数
        """
        from .interfaces.vector import VectorLinBus
        
        self.bus = VectorLinBus(
            channel=hw_channel,
            channel_index=channel_index,
            app_name=app_name,
            **kwargs
        )
    
    def set_bus(self, bus: LinBusABC):
        """
        设置已存在的总线对象
        
        :param bus: LinBusABC实例
        """
        self.bus = bus
    
    def start_collecting(self):
        """开始收集消息"""
        if not self.bus:
            raise RuntimeError("Bus not registered. Call register_bus() or set_bus() first.")
        
        self._stop_event.clear()
        self.total_messages = 0
        self.start_time = time.time()
        
        # 清空队列
        while not self.message_queue.empty():
            try:
                self.message_queue.get_nowait()
            except Empty:
                break
        
        # 启动接收线程
        self.recv_thread = threading.Thread(target=self._recv_loop)
        self.recv_thread.daemon = True
        self.recv_thread.start()
        
        if self.print_messages:
            print("Started collecting LIN messages...")
    
    def _recv_loop(self):
        """接收循环 - 在后台线程中运行"""
        while not self._stop_event.is_set():
            try:
                msg = self.bus.recv(timeout=0.1)
                if msg:
                    self.message_queue.put(msg)
                    self.total_messages += 1
                    
                    if self.print_messages:
                        print(self.message_formatter(msg))
                        
            except Exception as e:
                if not self._closed:
                    print(f'Receive error: {e}')
                break
    
    def _default_message_formatter(self, msg: LinMessage) -> str:
        """
        默认消息格式化器 - 仿照vectorLinApi的格式
        
        :param msg: LIN消息
        :return: 格式化的字符串
        """
        data_str = ' '.join(f'{b:02X}' for b in msg.data)
        
        # 计算简单校验和
        if hasattr(msg, 'checksum') and msg.checksum is not None:
            checksum = msg.checksum
        else:
            checksum = (~sum(msg.data) + 1) & 0xFF if msg.data else 0
        
        return (f" Timestamp: {msg.timestamp:<20.6f} | "
                f"Channel: {msg.channel}  "
                f"Frame ID: {msg.frame_id:02X}  |  "
                f"Data: {data_str:<23} | "
                f"Length: {len(msg.data)}    "
                f"Checksum: {checksum:02X} ；|| "
                f"Is Error Frame: {getattr(msg, 'is_error_frame', False)} | "
                f"is_rx: {msg.direction == 'Rx'}  ")
    
    def stop_collecting(self):
        """停止收集消息"""
        self._stop_event.set()
        
        if self.recv_thread and self.recv_thread.is_alive():
            self.recv_thread.join(timeout=2)
        
        if self.print_messages:
            print("stop")
    
    def get_messages(self) -> List[LinMessage]:
        """
        获取所有收集到的消息
        
        :return: 消息列表
        """
        messages = []
        while True:
            try:
                msg = self.message_queue.get_nowait()
                messages.append(msg)
            except Empty:
                if self.print_messages:
                    print("no more msg")
                break
        
        return messages
    
    def stop_and_get_messages(self) -> List[LinMessage]:
        """
        停止收集并返回所有消息
        
        :return: 消息列表
        """
        self.stop_collecting()
        return self.get_messages()
    
    def collect_for_duration(self, duration: float) -> List[LinMessage]:
        """
        收集指定时长的消息
        
        :param duration: 收集时长（秒）
        :return: 消息列表
        """
        self.start_collecting()
        time.sleep(duration)
        return self.stop_and_get_messages()
    
    def get_statistics(self) -> dict:
        """
        获取统计信息
        
        :return: 包含统计信息的字典
        """
        if self.start_time:
            elapsed = time.time() - self.start_time
            rate = self.total_messages / elapsed if elapsed > 0 else 0
        else:
            elapsed = 0
            rate = 0
        
        return {
            'total_messages': self.total_messages,
            'elapsed_time': elapsed,
            'message_rate': rate,
            'queue_size': self.message_queue.qsize()
        }
    
    def close(self):
        """关闭收集器和总线"""
        if self._closed:
            return
        
        self._closed = True
        self._stop_event.set()
        
        # 等待线程结束
        if self.recv_thread and self.recv_thread.is_alive():
            self.recv_thread.join(timeout=1)
        
        # 关闭总线
        if self.bus:
            if self.print_messages:
                print('start to close bus')
            self.bus.shutdown()
            if self.print_messages:
                print('close bus success')


# 兼容性别名
LINMsgCollector = LinMessageCollector