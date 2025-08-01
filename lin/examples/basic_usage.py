"""
基本使用示例 - 展示如何使用python-lin包
"""
import time
from lin import LinMessageCollector, LinMessage


def main():
    """主函数"""
    print("Python-LIN 基本使用示例")
    print("=" * 50)
    
    # 创建消息收集器
    with LinMessageCollector() as collector:
        # 注册总线
        print("注册LIN总线...")
        collector.register_bus(
            hw_channel=0,
            channel_index=0,
            app_name=None  # 使用全局通道
        )
        
        # 收集5秒的消息
        print("\n开始收集消息（5秒）...")
        messages = collector.collect_for_duration(5.0)
        
        # 显示结果
        print(f"\n收集完成！")
        print(f"总计收到: {len(messages)} 条消息")
        
        # 获取统计信息
        stats = collector.get_statistics()
        print(f"\n统计信息:")
        print(f"  - 总消息数: {stats['total_messages']}")
        print(f"  - 运行时间: {stats['elapsed_time']:.2f} 秒")
        print(f"  - 消息速率: {stats['message_rate']:.2f} 消息/秒")
        
        # 显示前5条消息
        if messages:
            print(f"\n前5条消息:")
            for i, msg in enumerate(messages[:5], 1):
                print(f"{i}. ID=0x{msg.frame_id:02X}, "
                      f"数据={' '.join(f'{b:02X}' for b in msg.data)}, "
                      f"时间={msg.timestamp:.6f}")
    
    print("\n程序结束")


if __name__ == "__main__":
    main()