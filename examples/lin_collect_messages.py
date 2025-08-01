"""
LIN消息收集示例 - 仿照vectorLinApi的写法
收集消息一段时间后停止并输出
"""
import time
from lin.interfaces.vector import VectorLinBus
from lin.message import LinMessage
from typing import List, Optional


class LinMessageCollector:
    """LIN消息收集器"""
    
    def __init__(self):
        self.bus: Optional[VectorLinBus] = None
        self.messages: List[LinMessage] = []
        self.is_collecting = False
        self._start_time = 0
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    
    def register_bus(self, hw_channel=0, channel_index=0):
        """注册LIN总线"""
        self.bus = VectorLinBus(
            channel=hw_channel,
            channel_index=channel_index,
            app_name=None  # 使用全局通道
        )
        print(f"Bus registered: channel={hw_channel}, index={channel_index}")
    
    def start_collect(self):
        """开始收集消息"""
        if not self.bus:
            raise RuntimeError("Bus not registered. Call register_bus first.")
        
        self.is_collecting = True
        self._start_time = time.time()
        self.messages.clear()
        print("Start collecting messages...")
    
    def collect_for_duration(self, duration: float):
        """收集指定时长的消息"""
        if not self.is_collecting:
            self.start_collect()
        
        end_time = self._start_time + duration
        
        while time.time() < end_time and self.is_collecting:
            # 计算剩余时间
            remaining = end_time - time.time()
            if remaining <= 0:
                break
            
            # 接收消息，超时设为较短时间以便实时显示
            timeout = min(0.1, remaining)
            msg = self.bus.recv(timeout=timeout)
            
            if msg:
                self.messages.append(msg)
                # 实时显示收到的消息（仿照vectorLinApi的格式）
                self._print_message(msg)
    
    def stop_collect(self):
        """停止收集"""
        self.is_collecting = False
        print("stop")
        print("no more msg")
        return self.messages
    
    def _print_message(self, msg: LinMessage):
        """打印单条消息（仿照vectorLinApi的格式）"""
        # 格式: Timestamp: xxx | Channel: x Frame ID: xx | Data: xx xx | Length: x Checksum: xx
        data_str = ' '.join(f'{b:02X}' for b in msg.data)
        
        # 计算简单校验和（如果消息中没有）
        if not hasattr(msg, 'checksum') or msg.checksum is None:
            checksum = (~sum(msg.data) + 1) & 0xFF
        else:
            checksum = msg.checksum
        
        print(f" Timestamp: {msg.timestamp:<20.6f} | "
              f"Channel: {msg.channel}  "
              f"Frame ID: {msg.frame_id:02X}  |  "
              f"Data: {data_str:<23} | "
              f"Length: {len(msg.data)}    "
              f"Checksum: {checksum:02X} ；|| "
              f"Is Error Frame: False | "
              f"is_rx: {msg.direction == 'Rx'}  ")
    
    def close(self):
        """关闭总线"""
        if self.bus:
            print("start to close bus")
            self.bus.shutdown()
            print("close bus success")
            self.bus = None


def main():
    """主函数 - 仿照vectorLinApi的使用方式"""
    try:
        with LinMessageCollector() as collector:
            # 注册总线
            collector.register_bus(0, 0)  # hw_channel=0, channel_index=0
            
            # 开始收集
            collector.start_collect()
            
            # 收集5秒的消息
            print("Collecting messages for 5 seconds...")
            collector.collect_for_duration(5.0)
            
            # 停止并获取所有消息
            messages = collector.stop_collect()
            print(f"total recv msg number is  {len(messages)}")
            
    except Exception as e:
        print(f'Error during execution: {e}')
    
    print('program ending normally')


if __name__ == '__main__':
    main()