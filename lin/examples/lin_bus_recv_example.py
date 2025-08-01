# -*- coding: utf-8 -*-
# Create Time: 2025/7/31 20:43
# Author: nzj
# Function：

from lin.collector import LinMessageCollector
import time

with LinMessageCollector(print_messages=True) as collector:
    collector.register_bus(0, 0)
    collector.start_collecting()

    # 执行其他操作...
    time.sleep(10)

    # 停止并获取所有消息
    messages = collector.stop_and_get_messages()
    print(f"总计收到 {len(messages)} 条消息")