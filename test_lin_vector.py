"""
Test script for Vector LIN interface.
"""
import time
import logging
from lin.interfaces.vector import VectorLinBus
from lin.message import LinMessage

# 设置日志
logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)


def test_lin_basic():
    """基本的LIN通信测试"""
    print("=== Vector LIN 接口基本测试 ===\n")
    
    # 创建LIN总线实例
    # 注意：需要根据实际硬件配置调整channel参数
    try:
        bus = VectorLinBus(
            channel=0,  # 使用通道0
            baudrate=19200,  # LIN标准波特率
            app_name="Python-LIN-Test"
        )
        print(f"✓ LIN总线初始化成功: {bus.channel_info}")
    except Exception as e:
        print(f"✗ LIN总线初始化失败: {e}")
        return
    
    try:
        # 测试1：发送LIN请求
        print("\n1. 发送LIN主机请求测试")
        test_id = 0x10
        msg = LinMessage(frame_id=test_id)
        bus.send(msg)
        print(f"   ✓ 发送LIN请求，ID: 0x{test_id:02X}")
        
        # 测试2：接收LIN消息
        print("\n2. 接收LIN消息测试（等待5秒）")
        start_time = time.time()
        msg_count = 0
        
        while time.time() - start_time < 5:
            msg = bus.recv(timeout=1.0)
            if msg:
                msg_count += 1
                print(f"   ✓ 收到消息 #{msg_count}: {msg}")
        
        if msg_count == 0:
            print("   ℹ 未收到任何消息（可能没有连接从机）")
        
        # 测试3：发送多个不同ID的请求
        print("\n3. 批量发送测试")
        test_ids = [0x20, 0x21, 0x22, 0x23]
        for frame_id in test_ids:
            msg = LinMessage(frame_id=frame_id)
            bus.send(msg)
            print(f"   ✓ 发送请求，ID: 0x{frame_id:02X}")
            time.sleep(0.1)  # 短暂延迟
        
    except Exception as e:
        print(f"\n✗ 测试过程中出错: {e}")
    
    finally:
        # 关闭总线
        bus.shutdown()
        print("\n✓ LIN总线已关闭")


def test_lin_message_creation():
    """测试LIN消息创建"""
    print("\n=== LIN消息创建测试 ===\n")
    
    # 测试1：创建基本消息
    msg1 = LinMessage(
        frame_id=0x3C,
        data=[0x01, 0x02, 0x03, 0x04]
    )
    print(f"1. 基本消息: {msg1}")
    
    # 测试2：创建带时间戳的消息
    msg2 = LinMessage(
        timestamp=1234.567890,
        frame_id=0x3D,
        data=b'\x11\x22\x33\x44\x55',
        direction="Tx"
    )
    print(f"2. 带时间戳消息: {msg2}")
    
    # 测试3：测试边界值
    try:
        # 最大ID
        msg3 = LinMessage(frame_id=63, data=[0xFF] * 8)
        print(f"3. 最大ID消息: {msg3}")
        
        # 无效ID（应该抛出异常）
        try:
            msg4 = LinMessage(frame_id=64)
        except ValueError as e:
            print(f"4. ✓ 正确拒绝无效ID: {e}")
        
        # 超长数据（应该抛出异常）
        try:
            msg5 = LinMessage(frame_id=0x10, data=[0x00] * 9)
        except ValueError as e:
            print(f"5. ✓ 正确拒绝超长数据: {e}")
            
    except Exception as e:
        print(f"✗ 消息创建测试失败: {e}")


def test_lin_with_context_manager():
    """使用上下文管理器测试"""
    print("\n=== 上下文管理器测试 ===\n")
    
    try:
        with VectorLinBus(channel=0) as bus:
            print(f"✓ 在with语句中使用LIN总线: {bus.channel_info}")
            
            # 尝试接收一条消息
            msg = bus.recv(timeout=1.0)
            if msg:
                print(f"  收到消息: {msg}")
            else:
                print("  未收到消息（1秒超时）")
        
        print("✓ 退出with语句，总线自动关闭")
        
    except Exception as e:
        print(f"✗ 上下文管理器测试失败: {e}")


if __name__ == "__main__":
    print("Vector LIN 接口测试程序")
    print("=" * 50)
    print("注意：需要安装Vector驱动和硬件")
    print("=" * 50)
    
    # 运行测试
    test_lin_message_creation()
    
    # 如果有Vector硬件，运行硬件相关测试
    user_input = input("\n是否有Vector硬件连接？(y/n): ").lower()
    if user_input == 'y':
        test_lin_basic()
        test_lin_with_context_manager()
    else:
        print("\n跳过硬件相关测试")
    
    print("\n测试完成！")