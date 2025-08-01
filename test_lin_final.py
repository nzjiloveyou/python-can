"""
最终的LIN接口测试脚本
测试基于CAN基础设施的LIN实现
"""
import logging
import time

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 测试LIN接口
def test_lin_interface():
    print("Vector LIN 接口测试（基于CAN基础设施）")
    print("=" * 60)
    
    try:
        from lin.interfaces.vector import VectorLinBus
        from lin.message import LinMessage
        
        print("\n1. 初始化LIN总线...")
        with VectorLinBus(channel=0, app_name="Python-LIN-Test") as bus:
            print(f"   ✓ 成功: {bus.channel_info}")
            
            print("\n2. 发送LIN消息...")
            # 发送几个测试消息
            test_messages = [
                LinMessage(frame_id=0x10, data=[0x01, 0x02]),
                LinMessage(frame_id=0x20, data=[0xAA, 0xBB, 0xCC]),
                LinMessage(frame_id=0x3C, data=[0x11, 0x22, 0x33, 0x44]),
            ]
            
            for msg in test_messages:
                bus.send(msg)
                print(f"   ✓ 发送: {msg}")
                time.sleep(0.1)
            
            print("\n3. 接收LIN消息（等待3秒）...")
            start_time = time.time()
            received_count = 0
            
            while time.time() - start_time < 3:
                msg = bus.recv(timeout=0.5)
                if msg:
                    received_count += 1
                    print(f"   ✓ 收到 #{received_count}: {msg}")
            
            if received_count == 0:
                print("   ℹ 未收到消息（可能没有其他LIN节点响应）")
            
        print("\n✓ 测试完成，总线已自动关闭")
        
    except ImportError as e:
        print(f"\n✗ 导入错误: {e}")
        print("   请确保在python-can项目目录中运行")
        
    except Exception as e:
        print(f"\n✗ 运行时错误: {e}")
        print(f"   错误类型: {type(e).__name__}")
        
        # 如果是Vector相关错误，给出提示
        if "Vector" in str(e) or "XL" in str(e):
            print("\n   可能的原因：")
            print("   - Vector驱动未安装")
            print("   - Vector硬件未连接")
            print("   - 通道配置不正确")


def test_lin_message_only():
    """仅测试LIN消息创建（无需硬件）"""
    print("\n\nLIN消息创建测试（无需硬件）")
    print("=" * 60)
    
    from lin.message import LinMessage
    
    # 测试各种消息
    test_cases = [
        {"frame_id": 0x00, "data": [], "desc": "最小ID，无数据"},
        {"frame_id": 0x3F, "data": [0xFF] * 8, "desc": "最大ID，满数据"},
        {"frame_id": 0x10, "data": [0x01, 0x02, 0x03], "desc": "标准消息"},
        {"frame_id": 0x3C, "data": b'\xAA\xBB\xCC\xDD', "desc": "字节串数据"},
    ]
    
    for i, test in enumerate(test_cases, 1):
        try:
            msg = LinMessage(
                frame_id=test["frame_id"],
                data=test["data"],
                timestamp=time.time()
            )
            print(f"\n{i}. {test['desc']}")
            print(f"   创建成功: {msg}")
            print(f"   - ID: 0x{msg.frame_id:02X}")
            print(f"   - 数据长度: {len(msg.data)}")
            print(f"   - 数据: {' '.join(f'{b:02X}' for b in msg.data)}")
        except Exception as e:
            print(f"\n{i}. {test['desc']}")
            print(f"   ✗ 失败: {e}")


if __name__ == "__main__":
    # 先测试消息创建
    test_lin_message_only()
    
    # 询问是否测试硬件
    print("\n" + "=" * 60)
    user_input = input("\n是否测试Vector硬件接口？(y/n): ").strip().lower()
    
    if user_input == 'y':
        test_lin_interface()
    else:
        print("\n跳过硬件测试。")
    
    print("\n所有测试完成！")