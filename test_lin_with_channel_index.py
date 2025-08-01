"""
测试LIN接口，使用channel_index参数（与工作代码相同）
"""
import logging
import time

# 设置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from lin.interfaces.vector import VectorLinBus
from lin.message import LinMessage


def test_with_channel_index():
    """使用channel_index参数测试（与vectorLinApi相同）"""
    print("Vector LIN 测试（使用channel_index）")
    print("=" * 50)
    
    try:
        # 使用与工作代码相同的参数
        # register_bus(0, 0) 对应 channel=0, channel_index=0
        print("\n1. 创建LIN总线...")
        bus = VectorLinBus(
            channel=0,           # hw_channel
            channel_index=0,     # channel_index  
            app_name="VCDS",     # 与工作代码相同的app_name
            rx_queue_size=8196   # 与工作代码相同
        )
        print(f"   ✓ 成功: {bus.channel_info}")
        
        print("\n2. 接收消息测试（5秒）...")
        start_time = time.time()
        msg_count = 0
        
        while time.time() - start_time < 5:
            msg = bus.recv(timeout=0.5)
            if msg:
                msg_count += 1
                print(f"\n收到消息 #{msg_count}:")
                print(f"  时间戳: {msg.timestamp:.6f}")
                print(f"  帧ID: 0x{msg.frame_id:02X}")
                print(f"  数据: {' '.join(f'{b:02X}' for b in msg.data)}")
                print(f"  长度: {len(msg.data)}")
                
                # 像工作代码一样显示详细信息
                if hasattr(msg, 'checksum') and msg.checksum is not None:
                    print(f"  校验和: 0x{msg.checksum:02X}")
                if hasattr(msg, 'is_error_frame'):
                    print(f"  错误帧: {msg.is_error_frame}")
                if hasattr(msg, 'is_rx'):
                    print(f"  is_rx: {msg.direction == 'Rx'}")
        
        print(f"\n总计接收到 {msg_count} 条消息")
        
        # 关闭总线
        print("\n3. 关闭总线...")
        bus.shutdown()
        print("   ✓ 关闭成功")
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()


def test_different_configs():
    """测试不同的配置组合"""
    print("\n\n测试不同配置")
    print("=" * 50)
    
    configs = [
        {"channel": 0, "channel_index": 0, "desc": "通道0, 索引0"},
        {"channel": 1, "channel_index": 1, "desc": "通道1, 索引1"},
        {"channel": 0, "channel_index": None, "desc": "通道0, 自动索引"},
        {"channel": 0, "app_name": None, "desc": "通道0, 全局"},
    ]
    
    for config in configs:
        try:
            desc = config.pop("desc")
            print(f"\n尝试: {desc}")
            with VectorLinBus(**config) as bus:
                print(f"  ✓ 成功")
                # 快速测试接收
                msg = bus.recv(timeout=0.1)
                if msg:
                    print(f"  收到消息: ID=0x{msg.frame_id:02X}")
        except Exception as e:
            print(f"  ✗ 失败: {str(e)[:60]}...")


if __name__ == "__main__":
    # 主测试
    test_with_channel_index()
    
    # 询问是否测试其他配置
    choice = input("\n是否测试其他配置？(y/n): ").strip().lower()
    if choice == 'y':
        test_different_configs()
    
    print("\n测试完成！")