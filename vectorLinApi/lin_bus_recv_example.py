from lin_api.lin_bus_recv import LINMsgWithVector
import time

"""
LIN 总线接收示例

注意：由于 Vector 驱动的清理问题，程序可能在退出时崩溃（错误代码 0xC0000005）。
这是一个已知问题，不影响程序的正常功能。

解决方案：
1. 使用 LINMsgWithVector.safe_exit() 替代正常退出（推荐）
2. 使用 lin_bus_recv_wrapper.py 运行此示例
3. 忽略退出时的错误（数据已经正确接收和处理）
"""

if __name__ == '__main__':
    try:
        with LINMsgWithVector() as lin_obj:
            lin_obj.register_bus(0, 0)
            lin_obj.start_recv_msg()
            
            time.sleep(2)
            
            msg_list = lin_obj.stop_recv_and_get_messages()
            print('total recv msg number is ', len(msg_list))
    except Exception as e:
        print(f'Error during execution: {e}')
    
    print('program ending normally')
    
    # 使用安全退出避免 Vector 驱动清理问题
    # 注释掉这行将使用正常的 Python 退出（可能导致崩溃）
    LINMsgWithVector.safe_exit(0)
    
    # 方式2：传统方式（备选）
    # lin_obj = None
    # try:
    #     lin_obj = LINMsgWithVector()
    #     lin_obj.register_bus(0, 0)
    #     lin_obj.start_recv_msg()
    #     
    #     time.sleep(2)
    #     
    #     msg_list = lin_obj.stop_recv_and_get_messages()
    #     print('total recv msg number is ', len(msg_list))
    # except Exception as e:
    #     print(f'Error during execution: {e}')
    # finally:
    #     if lin_obj:
    #         lin_obj.close()
    #     print('close')


