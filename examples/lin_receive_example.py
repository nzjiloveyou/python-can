"""
Example: Receiving LIN messages using Vector interface.
"""
import time
from lin.interfaces.vector import VectorLinBus
from lin.message import LinMessage
from typing import List, Dict


def main():
    """
    演示如何使用Vector LIN接口接收消息
    等待10秒，收集所有报文，然后输出并退出
    """
    print("LIN消息接收示例（10秒收集）")
    print("-" * 40)
    
    # 存储接收到的消息
    received_messages: List[LinMessage] = []
    
    # 创建LIN总线
    # 注意：channel参数需要根据实际的Vector硬件配置
    # app_name=None 使用全局通道，无需在Vector Hardware Config中配置
    try:
        with VectorLinBus(
            channel=0,              # 通道0
            channel_index=0,        # 通道索引0
            baudrate=19200,         # 标准LIN波特率
            app_name=None           # 使用全局通道（无需预配置）
        ) as bus:
            
            print(f"LIN总线已打开: {bus.channel_info}")
            print("开始接收LIN消息（等待10秒）...\n")
            
            start_time = time.time()
            collection_duration = 10  # 收集10秒
            
            # 实时显示进度
            last_print_time = start_time
            
            while True:
                current_time = time.time()
                elapsed = current_time - start_time
                
                # 检查是否已经过了10秒
                if elapsed >= collection_duration:
                    break
                
                # 计算剩余超时时间
                remaining_time = collection_duration - elapsed
                recv_timeout = min(0.5, remaining_time)  # 最多等待0.5秒
                
                # 接收消息
                msg = bus.recv(timeout=recv_timeout)
                
                if msg:
                    received_messages.append(msg)
                
                # 每秒更新一次进度
                if current_time - last_print_time >= 1.0:
                    print(f"已收集 {len(received_messages)} 条消息... "
                          f"剩余时间: {int(remaining_time)} 秒")
                    last_print_time = current_time
            
            print(f"\n收集完成！共收到 {len(received_messages)} 条消息\n")
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 分析和显示收到的消息
    if received_messages:
        print("=" * 60)
        print("收到的消息详情:")
        print("=" * 60)
        
        # 按ID分组统计
        msg_by_id: Dict[int, List[LinMessage]] = {}
        
        for i, msg in enumerate(received_messages):
            # 显示每条消息
            print(f"[{i+1:04d}] "
                  f"时间戳: {msg.timestamp:.6f} | "
                  f"通道: {msg.channel} | "
                  f"帧ID: 0x{msg.frame_id:02X} | "
                  f"数据: {' '.join(f'{b:02X}' for b in msg.data)} | "
                  f"长度: {len(msg.data)}")
            
            # 分组统计
            if msg.frame_id not in msg_by_id:
                msg_by_id[msg.frame_id] = []
            msg_by_id[msg.frame_id].append(msg)
        
        # 显示统计信息
        print("\n" + "=" * 60)
        print("消息统计:")
        print("=" * 60)
        print(f"总消息数: {len(received_messages)}")
        print(f"不同ID数: {len(msg_by_id)}")
        print(f"收集时长: {collection_duration} 秒")
        print(f"平均速率: {len(received_messages)/collection_duration:.2f} 消息/秒")
        
        print("\n按ID分组统计:")
        for frame_id in sorted(msg_by_id.keys()):
            msgs = msg_by_id[frame_id]
            print(f"  ID 0x{frame_id:02X}: {len(msgs)} 条消息")
            
            # 显示该ID的第一条和最后一条消息的数据
            if msgs:
                first_data = ' '.join(f'{b:02X}' for b in msgs[0].data)
                last_data = ' '.join(f'{b:02X}' for b in msgs[-1].data)
                print(f"    首条数据: {first_data}")
                if len(msgs) > 1 and first_data != last_data:
                    print(f"    末条数据: {last_data}")
    else:
        print("\n未收到任何消息")
    
    print("\n程序正常结束")


if __name__ == "__main__":
    main()