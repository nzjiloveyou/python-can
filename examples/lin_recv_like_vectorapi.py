"""
LIN 总线接收示例 - 完全仿照vectorLinApi的风格
"""
import time
from lin.interfaces.vector import VectorLinBus
from lin.message import LinMessage


class LINMsgCollector:
    """仿照LINMsgWithVector的消息收集器"""
    
    def __init__(self):
        self.bus = None
        self.received_messages = []
        self._is_receiving = False
        self._start_time = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    
    def register_bus(self, hw_channel, channel_index):
        """注册总线 - 与vectorLinApi相同的参数"""
        self.bus = VectorLinBus(
            channel=hw_channel,
            channel_index=channel_index,
            app_name=None  # 使用全局通道避免配置问题
        )
    
    def start_recv_msg(self):
        """开始接收消息"""
        self._is_receiving = True
        self._start_time = time.time()
        self.received_messages = []
        
        # 后台接收线程（这里简化为主线程接收）
        # 在实际的vectorLinApi中，这里会启动一个notifier
    
    def recv_messages_for_duration(self, duration):
        """接收指定时长的消息"""
        end_time = time.time() + duration
        
        while time.time() < end_time and self._is_receiving:
            msg = self.bus.recv(timeout=0.1)
            if msg:
                self.received_messages.append(msg)
                # 打印消息 - 完全仿照vectorLinApi的格式
                self._print_msg_vectorapi_style(msg)
    
    def _print_msg_vectorapi_style(self, msg):
        """按照vectorLinApi的格式打印消息"""
        data_str = ' '.join(f'{b:02X}' for b in msg.data)
        
        # 模拟校验和（实际LIN校验和需要根据协议计算）
        checksum = (~sum(msg.data) + 1) & 0xFF if msg.data else 0
        
        # 完全复制vectorLinApi的输出格式
        print(f" Timestamp: {msg.timestamp:<20.6f} | Channel: {msg.channel}  "
              f"Frame ID: {msg.frame_id:02X}  |  Data: {data_str:<23} | "
              f"Length: {len(msg.data)}    Checksum: {checksum:02X} ；|| "
              f"Is Error Frame: False | is_rx: True  ")
    
    def stop_recv_and_get_messages(self):
        """停止接收并返回消息列表"""
        self._is_receiving = False
        print('stop')
        print('no more msg')
        return self.received_messages
    
    def close(self):
        """关闭总线"""
        if self.bus:
            print('start to close bus')
            self.bus.shutdown()
            print('close bus success')


if __name__ == '__main__':
    try:
        with LINMsgCollector() as lin_obj:
            # 与vectorLinApi完全相同的调用方式
            lin_obj.register_bus(0, 0)
            lin_obj.start_recv_msg()
            
            # 接收2秒的消息
            duration = 2
            print(f'Receiving messages for {duration} seconds...')
            lin_obj.recv_messages_for_duration(duration)
            
            # 停止并获取消息
            msg_list = lin_obj.stop_recv_and_get_messages()
            print('total recv msg number is ', len(msg_list))
            
    except Exception as e:
        print(f'Error during execution: {e}')
    
    print('program ending normally')