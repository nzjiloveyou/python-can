import time

from .linlib import VectorLINBus
# from LIN_API.vecor_lin_bus.linlib import VectorLINBus
from .lin_notifier import LinNotifier
from .lin_listener import LinBufferedReader, LinListener
# from can.io import BLFWriter  # FIXME 直接导入会导致工程2s自动结束

from typing import Optional


class LINMsgWithVector:
    def __init__(self):

        self.bus: Optional[VectorLINBus] = None
        self.notifier: Optional[LinNotifier] = None
        self.listener_list = []
        self.receiver_listener = LinBufferedReader()
        self._closed = False

    def close(self):
        if self._closed:
            return
        
        try:
            print('start to close bus')
            self._closed = True
            
            # 先确保设置shutdown标志
            if self.bus:
                self.bus._is_shutdown = True
            
            # 确保 notifier 已停止
            if self.notifier and hasattr(self.notifier, '_running'):
                self.notifier._running = False
            
            # 给更多时间让线程完全退出
            time.sleep(0.5)
            
            # 清空所有引用
            self.receiver_listener = None
            self.notifier = None
            
            # 最后关闭bus
            if self.bus:
                self.bus.shutdown()
                # 不要立即设置为 None，让 Python 垃圾回收处理
                # self.bus = None
            print('close bus success')
        except Exception as e:
            print(f'close error: {e}')
            import traceback
            traceback.print_exc()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    
    @staticmethod
    def safe_exit(exit_code=0):
        """安全退出程序，避免 Vector 驱动清理问题
        
        注意：这会强制退出程序，跳过 Python 的正常清理过程。
        只在程序的最后调用此方法。
        """
        import os
        os._exit(exit_code)

    def register_bus(self,
                     hw_channel=1,
                     channel_index=1,
                     app_name='lin_test'):
        self.bus = VectorLINBus(channel=hw_channel,
                                channel_index=channel_index,
                                app_name=app_name)

    def start_recv_msg(self):
        self.notifier = LinNotifier(bus=self.bus, listeners=[self.receiver_listener])

    def stop_recv_and_get_messages(self):
        # 先设置shutdown标志
        if self.bus:
            self.bus._is_shutdown = True
            
        # 再停止notifier以防止新消息到达
        if self.notifier:
            self.notifier.stop(timeout=2)
        
        received_messages = []
        while True:
            msg = self.receiver_listener.get_message()  # 阻塞等待 0.5 秒
            if msg is not None:
                received_messages.append(msg)
            else:
                print('no more msg')
                # get_message 超时返回 None，此时暂时没有更多消息
                break

        return received_messages



# if __name__ == '__main__':
#     lin_obj = LINMsgWithVector()
#     lin_obj.register_bus()
#     lin_obj.start_recv_msg()
#
#     time.sleep(1)
#     lin_obj.close()
#     msg_list = lin_obj.stop_recv_and_get_messages()
#
#     print('total recv msg is ', len(msg_list))
