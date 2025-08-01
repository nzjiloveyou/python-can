"""
LIN 总线接收示例 - 使用线程后台接收（更接近vectorLinApi的实现）
"""
import time
import threading
from queue import Queue, Empty
from lin.interfaces.vector import VectorLinBus
from lin.message import LinMessage


class LINMsgWithThread:
    """使用后台线程接收LIN消息"""
    
    def __init__(self):
        self.bus = None
        self.recv_thread = None
        self.message_queue = Queue()
        self._stop_event = threading.Event()
        self._closed = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    
    def register_bus(self, hw_channel, channel_index):
        """注册总线"""
        self.bus = VectorLinBus(
            channel=hw_channel,
            channel_index=channel_index,
            app_name=None
        )
    
    def start_recv_msg(self):
        """启动接收线程"""
        self._stop_event.clear()
        self.recv_thread = threading.Thread(target=self._recv_loop)
        self.recv_thread.daemon = True
        self.recv_thread.start()
    
    def _recv_loop(self):
        """接收循环 - 在后台线程中运行"""
        while not self._stop_event.is_set():
            try:
                msg = self.bus.recv(timeout=0.1)
                if msg:
                    self.message_queue.put(msg)
                    # 实时打印
                    self._print_message(msg)
            except Exception as e:
                if not self._closed:
                    print(f'Recv error: {e}')
                break
    
    def _print_message(self, msg):
        """打印消息"""
        data_str = ' '.join(f'{b:02X}' for b in msg.data)
        checksum = (~sum(msg.data) + 1) & 0xFF if msg.data else 0
        
        print(f" Timestamp: {msg.timestamp:<20.6f} | Channel: {msg.channel}  "
              f"Frame ID: {msg.frame_id:02X}  |  Data: {data_str:<23} | "
              f"Length: {len(msg.data)}    Checksum: {checksum:02X} ；|| "
              f"Is Error Frame: False | is_rx: True  ")
    
    def stop_recv_and_get_messages(self):
        """停止接收并获取所有消息"""
        # 停止接收线程
        self._stop_event.set()
        if self.recv_thread and self.recv_thread.is_alive():
            self.recv_thread.join(timeout=2)
        
        # 收集所有消息
        messages = []
        while True:
            try:
                msg = self.message_queue.get_nowait()
                messages.append(msg)
            except Empty:
                print('stop')
                print('no more msg')
                break
        
        return messages
    
    def close(self):
        """关闭总线"""
        if self._closed:
            return
        
        self._closed = True
        self._stop_event.set()
        
        if self.recv_thread and self.recv_thread.is_alive():
            self.recv_thread.join(timeout=1)
        
        if self.bus:
            print('start to close bus')
            self.bus.shutdown()
            print('close bus success')


def main():
    """主函数"""
    try:
        with LINMsgWithThread() as lin_obj:
            # 注册总线
            lin_obj.register_bus(0, 0)
            
            # 启动接收
            lin_obj.start_recv_msg()
            
            # 等待几秒
            wait_time = 3
            print(f'Collecting messages for {wait_time} seconds...')
            time.sleep(wait_time)
            
            # 停止并获取消息
            msg_list = lin_obj.stop_recv_and_get_messages()
            print('total recv msg number is ', len(msg_list))
            
    except Exception as e:
        print(f'Error during execution: {e}')
    
    print('program ending normally')


if __name__ == '__main__':
    main()