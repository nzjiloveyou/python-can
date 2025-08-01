"""
演示如何使用python-lin包
这个脚本应该在lin包的父目录运行
"""
import sys
import os

# 添加lin包到Python路径（如果还没有安装）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 现在可以导入lin包
from lin import LinMessage, LinMessageCollector
from lin.interfaces.vector import VectorLinBus


def main():
    """演示基本用法"""
    print("Python-LIN 包使用演示")
    print("=" * 50)
    
    # 1. 创建LIN消息
    print("\n1. 创建LIN消息:")
    msg = LinMessage(
        frame_id=0x10,
        data=[0x11, 0x22, 0x33],
        timestamp=1234.5678
    )
    print(f"   {msg}")
    
    # 2. 使用消息收集器
    print("\n2. 使用消息收集器:")
    try:
        with LinMessageCollector(print_messages=True) as collector:
            # 注册总线
            collector.register_bus(hw_channel=0, channel_index=0)
            
            # 收集3秒的消息
            print("   收集3秒的消息...")
            messages = collector.collect_for_duration(3.0)
            
            print(f"\n   收集完成！总计: {len(messages)} 条消息")
            
            # 显示统计
            stats = collector.get_statistics()
            print(f"   消息速率: {stats['message_rate']:.2f} msg/s")
            
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n演示完成！")
    
    # 显示包信息
    print("\n包信息:")
    import lin
    print(f"   版本: {lin.__version__}")
    print(f"   模块: {lin.__all__}")


if __name__ == "__main__":
    main()