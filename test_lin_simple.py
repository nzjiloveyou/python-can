"""
简单的LIN接口测试脚本
"""
import sys
import os

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 测试导入
try:
    from lin.interfaces.vector import VectorLinBus
    from lin.message import LinMessage
    print("✓ 成功导入LIN模块")
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 测试消息创建
try:
    msg = LinMessage(frame_id=0x10, data=[0x01, 0x02, 0x03])
    print(f"✓ 成功创建LIN消息: {msg}")
except Exception as e:
    print(f"✗ 创建消息失败: {e}")

# 测试总线初始化
print("\n尝试初始化Vector LIN总线...")
try:
    bus = VectorLinBus(channel=0)
    print("✓ LIN总线初始化成功!")
    print(f"  通道信息: {bus.channel_info}")
    
    # 尝试接收一条消息
    print("\n尝试接收消息（1秒超时）...")
    msg = bus.recv(timeout=1.0)
    if msg:
        print(f"✓ 收到消息: {msg}")
    else:
        print("  没有收到消息（超时）")
    
    # 关闭总线
    bus.shutdown()
    print("\n✓ LIN总线已关闭")
    
except Exception as e:
    print(f"✗ 错误: {e}")
    print(f"  错误类型: {type(e).__name__}")
    
    # 打印更详细的错误信息
    import traceback
    print("\n详细错误信息:")
    traceback.print_exc()

print("\n测试完成。")