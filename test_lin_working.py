"""
基于工作脚本的LIN测试程序
使用与vectorLinApi相同的配置方式
"""
import sys
import time

# 添加vectorLinApi路径
sys.path.insert(0, 'vectorLinApi')

try:
    from lin_api.lin_bus_recv import LINMsgWithVector
    
    print("Vector LIN 接收测试（使用工作配置）")
    print("=" * 50)
    
    with LINMsgWithVector() as lin_obj:
        # 使用与工作脚本相同的参数
        lin_obj.register_bus(0, 0)  # hw_channel=0, channel_index=0
        lin_obj.start_recv_msg()
        
        print("开始接收LIN消息...")
        print("等待2秒...")
        
        time.sleep(2)
        
        msg_list = lin_obj.stop_recv_and_get_messages()
        print(f'\n收到的消息总数: {len(msg_list)}')
        
        # 显示前10条消息
        if msg_list:
            print("\n前10条消息:")
            for i, msg in enumerate(msg_list[:10]):
                print(f"{i+1}. {msg}")
                
    print('\n程序正常结束')
    
    # 使用安全退出
    LINMsgWithVector.safe_exit(0)
    
except ImportError as e:
    print(f"导入错误: {e}")
    print("\n请确保：")
    print("1. 在python-can目录中运行")
    print("2. vectorLinApi目录存在")
    
except Exception as e:
    print(f"运行错误: {e}")
    import traceback
    traceback.print_exc()