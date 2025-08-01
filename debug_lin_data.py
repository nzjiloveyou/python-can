"""
调试LIN数据接收问题
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lin.interfaces.vector import VectorLinBus
from can.interfaces.vector import xlclass, xldefine, xldriver
import ctypes
import time

def main():
    """调试数据接收"""
    print("调试LIN数据结构...")
    
    # 创建LIN总线
    bus = VectorLinBus(channel=0, channel_index=0)
    
    # 直接访问驱动接收数据
    event = xlclass.XLevent()
    event_count = ctypes.c_uint(1)
    
    print("\nXLevent结构大小:", ctypes.sizeof(event))
    print("等待接收消息...")
    
    start_time = time.time()
    while time.time() - start_time < 5:
        # 使用原始API不带错误检查
        result = xldriver._xlapi_dll.xlReceive(
            bus.port_handle,
            ctypes.byref(event_count),
            ctypes.byref(event)
        )
        
        if result == xldefine.XL_Status.XL_SUCCESS and event_count.value > 0:
            if event.tag == 20:  # XL_LIN_MSG
                print(f"\n收到LIN消息 (tag={event.tag}):")
                print(f"  Channel Index: {event.chanIndex}")
                print(f"  Timestamp: {event.timeStamp}")
                
                # 尝试访问msg数据
                msg = event.tagData.msg
                print(f"  ID (msg.id): 0x{msg.id:02X}")
                print(f"  DLC (msg.dlc): {msg.dlc}")
                print(f"  Flags (msg.flags): 0x{msg.flags:04X}")
                
                # 打印前8个字节的原始数据
                print("  原始数据字节:")
                for i in range(8):
                    print(f"    data[{i}]: 0x{msg.data[i]:02X}")
                
                # 尝试将数据解释为不同的结构
                # 检查数据是否在错误的偏移位置
                if msg.dlc == 0 and msg.data[4] != 0:
                    print("\n  可能的数据偏移问题:")
                    print(f"    data[4-7]: {msg.data[4]:02X} {msg.data[5]:02X} {msg.data[6]:02X} {msg.data[7]:02X}")
                
                time.sleep(0.1)
    
    bus.shutdown()
    print("\n调试完成！")

if __name__ == "__main__":
    main()