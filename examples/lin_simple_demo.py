"""
简单的LIN演示程序
使用全局通道，不需要在Vector Hardware Config中预先配置
"""
import logging
import time
from lin.interfaces.vector import VectorLinBus
from lin.message import LinMessage

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def demo_without_hardware():
    """演示LIN消息创建（不需要硬件）"""
    print("=== LIN消息演示（无需硬件）===\n")
    
    # 创建各种LIN消息
    messages = [
        LinMessage(frame_id=0x01, data=[0x00]),
        LinMessage(frame_id=0x10, data=[0x11, 0x22, 0x33]),
        LinMessage(frame_id=0x3C, data=[0xAA, 0xBB, 0xCC, 0xDD]),
        LinMessage(frame_id=0x3F, data=b'\xFF' * 8),  # 最大ID和数据
    ]
    
    for msg in messages:
        print(f"创建消息: {msg}")
        print(f"  - Frame ID: 0x{msg.frame_id:02X}")
        print(f"  - 数据: {' '.join(f'{b:02X}' for b in msg.data)}")
        print(f"  - 长度: {len(msg.data)} 字节\n")


def demo_with_hardware():
    """演示硬件接口（需要Vector硬件）"""
    print("\n=== LIN硬件接口演示 ===\n")
    
    try:
        # 使用全局通道（app_name=None），避免配置问题
        print("1. 尝试打开LIN接口（使用全局通道）...")
        with VectorLinBus(channel=1, app_name=None) as bus:
            print(f"   ✓ 成功打开: {bus.channel_info}")
            
            # 发送测试消息
            print("\n2. 发送测试消息...")
            test_msg = LinMessage(frame_id=0x10, data=[0x01, 0x02, 0x03])
            bus.send(test_msg)
            print(f"   ✓ 已发送: {test_msg}")
            
            # 尝试接收
            print("\n3. 等待接收消息（3秒）...")
            start_time = time.time()
            received = 0
            
            while time.time() - start_time < 3:
                msg = bus.recv(timeout=0.5)
                if msg:
                    received += 1
                    print(f"   ✓ 收到消息 #{received}: {msg}")
            
            if received == 0:
                print("   ℹ 未收到消息（正常情况，需要其他LIN节点）")
                
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        print("\n可能的解决方案：")
        print("1. 确认Vector硬件已连接")
        print("2. 确认Vector驱动已安装") 
        print("3. 尝试使用不同的通道号（如channel=1）")
        print("4. 在Vector Hardware Config中配置LIN通道")


def demo_alternative_channels():
    """尝试不同的通道配置"""
    print("\n=== 尝试不同的通道配置 ===\n")
    
    # 尝试不同的配置选项
    configs = [
        {"channel": 0, "app_name": None, "desc": "全局通道0"},
        {"channel": 1, "app_name": None, "desc": "全局通道1"},
        {"channel": "0x01", "app_name": None, "desc": "通道掩码0x01"},
        {"channel": "0x02", "app_name": None, "desc": "通道掩码0x02"},
    ]
    
    for config in configs:
        try:
            print(f"尝试: {config['desc']}")
            with VectorLinBus(**config) as bus:
                print(f"  ✓ 成功: {bus.channel_info}")
        except Exception as e:
            print(f"  ✗ 失败: {str(e)[:60]}...")
        print()


if __name__ == "__main__":
    print("Vector LIN 接口简单演示")
    print("=" * 50)
    
    # 1. 演示消息创建
    demo_without_hardware()
    
    # 2. 询问是否测试硬件
    choice = input("\n是否测试硬件接口？(y/n): ").strip().lower()
    
    if choice == 'y':
        # 测试硬件
        demo_with_hardware()
        
        # 询问是否尝试其他通道
        choice2 = input("\n是否尝试其他通道配置？(y/n): ").strip().lower()
        if choice2 == 'y':
            demo_alternative_channels()
    
    print("\n演示完成！")