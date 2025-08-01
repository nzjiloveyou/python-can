"""
高级使用示例 - 展示python-lin的高级功能
"""
import time
import threading
from lin import LinMessageCollector, LinMessage
from lin.interfaces.vector import VectorLinBus


def custom_message_formatter(msg: LinMessage) -> str:
    """自定义消息格式化器"""
    return (f"[{msg.timestamp:.3f}] "
            f"ID:0x{msg.frame_id:02X} "
            f"Data:[{','.join(f'0x{b:02X}' for b in msg.data)}] "
            f"Len:{len(msg.data)}")


def process_messages_realtime(collector: LinMessageCollector):
    """实时处理消息的示例"""
    print("实时消息处理线程启动")
    
    while not collector._stop_event.is_set():
        # 检查队列中的消息
        if not collector.message_queue.empty():
            try:
                msg = collector.message_queue.get_nowait()
                # 这里可以添加实时处理逻辑
                if msg.frame_id == 0x10:
                    print(f"  -> 检测到特殊消息 0x10!")
            except:
                pass
        time.sleep(0.01)
    
    print("实时消息处理线程结束")


def main():
    """主函数"""
    print("Python-LIN 高级使用示例")
    print("=" * 50)
    
    # 示例1：使用自定义格式化器
    print("\n1. 使用自定义消息格式化器")
    with LinMessageCollector(
        print_messages=True,
        message_formatter=custom_message_formatter
    ) as collector:
        collector.register_bus(0, 0)
        messages = collector.collect_for_duration(2.0)
        print(f"   收集到 {len(messages)} 条消息")
    
    # 示例2：手动控制收集过程
    print("\n2. 手动控制消息收集")
    with LinMessageCollector(print_messages=False) as collector:
        collector.register_bus(0, 0)
        
        # 启动收集
        collector.start_collecting()
        print("   收集已启动...")
        
        # 等待一段时间
        time.sleep(3)
        
        # 停止收集
        collector.stop_collecting()
        messages = collector.get_messages()
        print(f"   手动停止，收集到 {len(messages)} 条消息")
    
    # 示例3：直接使用VectorLinBus
    print("\n3. 直接使用VectorLinBus接口")
    try:
        bus = VectorLinBus(channel=0, channel_index=0)
        print("   总线已创建")
        
        # 发送消息
        msg = LinMessage(frame_id=0x20, data=[0x11, 0x22, 0x33])
        bus.send(msg)
        print(f"   发送消息: {msg}")
        
        # 接收消息
        start_time = time.time()
        recv_count = 0
        while time.time() - start_time < 2:
            received = bus.recv(timeout=0.1)
            if received:
                recv_count += 1
                if recv_count <= 3:  # 只显示前3条
                    print(f"   接收到: ID=0x{received.frame_id:02X}")
        
        bus.shutdown()
        print(f"   总计接收 {recv_count} 条消息")
        
    except Exception as e:
        print(f"   错误: {e}")
    
    # 示例4：使用已有的总线对象
    print("\n4. 使用已有的总线对象和实时处理")
    try:
        # 创建总线
        bus = VectorLinBus(channel=0, channel_index=0)
        
        # 创建收集器并设置总线
        collector = LinMessageCollector(print_messages=False)
        collector.set_bus(bus)
        
        # 启动实时处理线程
        process_thread = threading.Thread(
            target=process_messages_realtime,
            args=(collector,)
        )
        process_thread.daemon = True
        process_thread.start()
        
        # 开始收集
        collector.start_collecting()
        print("   实时处理已启动...")
        
        # 运行一段时间
        time.sleep(3)
        
        # 停止并清理
        messages = collector.stop_and_get_messages()
        process_thread.join(timeout=1)
        collector.close()
        
        print(f"   实时处理完成，共 {len(messages)} 条消息")
        
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n所有示例完成！")


if __name__ == "__main__":
    main()