"""
Example: LIN Master-Slave communication pattern.
"""
import time
import threading
from lin.interfaces.vector import VectorLinBus
from lin.message import LinMessage


class LinMaster:
    """LIN主机示例"""
    
    def __init__(self, channel=0):
        self.bus = VectorLinBus(
            channel=channel,
            baudrate=19200,
            app_name="LIN-Master"
        )
        self.running = True
        self.schedule = [
            # 调度表: (帧ID, 周期(秒))
            (0x10, 0.1),   # 100ms周期
            (0x11, 0.1),   # 100ms周期
            (0x20, 0.2),   # 200ms周期
            (0x21, 0.2),   # 200ms周期
            (0x30, 0.5),   # 500ms周期
        ]
    
    def run_schedule(self):
        """运行LIN调度表"""
        print("LIN主机：开始运行调度表")
        schedule_index = 0
        last_times = {}
        
        while self.running:
            current_time = time.time()
            
            # 检查每个调度项
            for frame_id, period in self.schedule:
                if frame_id not in last_times:
                    last_times[frame_id] = 0
                
                # 检查是否到了发送时间
                if current_time - last_times[frame_id] >= period:
                    # 发送帧头
                    msg = LinMessage(frame_id=frame_id)
                    self.bus.send(msg)
                    print(f"主机: 发送请求 ID=0x{frame_id:02X}")
                    last_times[frame_id] = current_time
                    
                    # 等待可能的从机响应
                    response = self.bus.recv(timeout=0.01)
                    if response and response.direction == "Rx":
                        print(f"主机: 收到响应 ID=0x{response.frame_id:02X}, "
                              f"数据={list(response.data)}")
            
            time.sleep(0.001)  # 1ms循环
    
    def stop(self):
        """停止主机"""
        self.running = False
        self.bus.shutdown()


class LinSlave:
    """LIN从机示例（模拟）"""
    
    def __init__(self):
        # 从机响应表
        self.response_table = {
            0x10: [0x01, 0x02, 0x03, 0x04],      # ID 0x10的响应数据
            0x11: [0x11, 0x22, 0x33, 0x44, 0x55], # ID 0x11的响应数据  
            0x20: [0xAA, 0xBB],                    # ID 0x20的响应数据
            # 0x21和0x30不响应（模拟无响应情况）
        }
        print("LIN从机：初始化完成")
        print(f"响应表: {list(self.response_table.keys())}")
    
    def get_response(self, frame_id):
        """获取指定ID的响应数据"""
        return self.response_table.get(frame_id)


def demo_master_only():
    """仅演示主机功能"""
    print("\n=== LIN主机演示 ===")
    print("（没有真实从机，仅发送请求）\n")
    
    master = LinMaster(channel=0)
    
    try:
        # 运行10秒
        master_thread = threading.Thread(target=master.run_schedule)
        master_thread.start()
        
        time.sleep(10)
        
    except KeyboardInterrupt:
        print("\n用户中断")
    finally:
        master.stop()
        master_thread.join()
        print("主机已停止")


def demo_master_slave_simulation():
    """演示主从机通信（模拟）"""
    print("\n=== LIN主从机通信模拟 ===")
    print("注意：这是一个概念演示，实际从机需要硬件支持\n")
    
    # 创建主机和从机
    master = LinMaster(channel=0)
    slave = LinSlave()
    
    # 模拟通信过程
    print("模拟5轮调度：")
    for round_num in range(5):
        print(f"\n--- 第{round_num + 1}轮 ---")
        
        for frame_id, _ in master.schedule[:3]:  # 只演示前3个
            print(f"主机: 请求 ID=0x{frame_id:02X}")
            
            # 模拟从机响应
            response_data = slave.get_response(frame_id)
            if response_data:
                print(f"从机: 响应数据 {response_data}")
            else:
                print(f"从机: 无响应")
            
            time.sleep(0.1)


if __name__ == "__main__":
    print("LIN主从机通信示例")
    print("=" * 50)
    
    # 选择演示模式
    print("\n选择演示模式:")
    print("1. 仅主机模式（需要Vector硬件）")
    print("2. 主从机模拟（概念演示）")
    
    choice = input("\n请选择 (1/2): ").strip()
    
    if choice == "1":
        try:
            demo_master_only()
        except Exception as e:
            print(f"错误: {e}")
            print("请确保Vector硬件已连接并正确配置")
    elif choice == "2":
        demo_master_slave_simulation()
    else:
        print("无效选择")