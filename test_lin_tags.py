"""
测试LIN接收的事件标签
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lin.interfaces.vector import VectorLinBus
from can.interfaces.vector import xldefine
import time

def main():
    """测试接收LIN消息的标签"""
    print("测试LIN消息接收...")
    
    # 创建LIN总线
    bus = VectorLinBus(channel=0, channel_index=0)
    
    # 接收几条消息
    print("\n开始接收消息（10秒）...")
    start_time = time.time()
    msg_count = 0
    
    while time.time() - start_time < 10:
        msg = bus.recv(timeout=0.1)
        if msg:
            msg_count += 1
            print(f"\n消息 {msg_count}:")
            print(f"  ID: 0x{msg.frame_id:02X}")
            print(f"  数据: {list(msg.data)}")
            print(f"  十六进制: {msg.data.hex(' ')}")
    
    print(f"\n总计收到 {msg_count} 条消息")
    
    # 关闭总线
    bus.shutdown()
    print("测试完成！")

if __name__ == "__main__":
    main()