"""
测试Vector LIN接口（简化版）
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 测试使用CAN基础设施的简化LIN接口
print("测试Vector LIN接口（使用CAN基础设施）")
print("=" * 50)

try:
    from lin.interfaces.vector.linlib_simple import VectorLinBusSimple
    from lin.message import LinMessage
    
    print("1. 创建LIN总线...")
    bus = VectorLinBusSimple(channel=0)
    print(f"   ✓ 成功: {bus.channel_info}")
    
    print("\n2. 测试发送...")
    msg = LinMessage(frame_id=0x10, data=[0x01, 0x02])
    bus.send(msg)
    print("   ✓ 发送测试完成")
    
    print("\n3. 测试接收（1秒超时）...")
    received = bus.recv(timeout=1.0)
    if received:
        print(f"   ✓ 收到消息: {received}")
    else:
        print("   ℹ 未收到消息（超时）")
    
    print("\n4. 关闭总线...")
    bus.shutdown()
    print("   ✓ 关闭成功")
    
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n测试完成。")