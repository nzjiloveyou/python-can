# Python-LIN

A Python library for LIN (Local Interconnect Network) bus communication with Vector hardware support.

[![Python Version](https://img.shields.io/pypi/pyversions/python-lin.svg)](https://pypi.org/project/python-lin/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Python-LIN 是一个用于 LIN (Local Interconnect Network) 总线通信的Python库，提供了简洁的API来发送和接收LIN消息。该库基于python-can的架构设计，支持Vector硬件。

## 特性

- 支持LIN 1.3, 2.0, 2.1, 2.2协议
- 基于Vector XL Driver Library (vxlapi.dll)
- 支持主机模式的消息收发
- 与python-can相似的API设计
- 完整的错误处理和日志记录
- 自动选择原生LIN或基于CAN的实现

## 安装要求

1. Vector驱动程序和运行时库
2. Vector硬件（如VN1610, CANcaseXL等）
3. Windows操作系统（Vector驱动仅支持Windows）

## 安装

### 从PyPI安装（推荐）

```bash
pip install python-lin
```

### 从源码安装

```bash
git clone https://github.com/yourusername/python-lin.git
cd python-lin
pip install -e .
```

### 开发安装

```bash
pip install -e ".[dev,test]"
```

## 快速开始

### 基本使用

```python
from lin.interfaces.vector import VectorLinBus
from lin.message import LinMessage

# 创建LIN总线
with VectorLinBus(channel=0, app_name=None) as bus:
    # 发送LIN消息
    msg = LinMessage(frame_id=0x10, data=[0x01, 0x02, 0x03])
    bus.send(msg)
    
    # 接收LIN消息
    response = bus.recv(timeout=1.0)
    if response:
        print(f"收到消息: {response}")
```

### 使用消息收集器

```python
from lin.collector import LinMessageCollector

# 使用消息收集器自动收集消息
with LinMessageCollector() as collector:
    # 注册总线
    collector.register_bus(hw_channel=0, channel_index=0)
    
    # 收集5秒的消息
    messages = collector.collect_for_duration(5.0)
    
    print(f"收到 {len(messages)} 条消息")
    
    # 获取统计信息
    stats = collector.get_statistics()
    print(f"消息速率: {stats['message_rate']:.2f} msg/s")
```

### 高级用法 - 后台线程收集

```python
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
```

### LIN消息结构

```python
# 创建LIN消息
msg = LinMessage(
    frame_id=0x3C,           # LIN ID (0-63)
    data=[0x01, 0x02, 0x03], # 数据 (0-8字节)
    timestamp=1234.56,       # 时间戳
    direction="Tx",          # 方向: "Tx" 或 "Rx"
)
```

## API参考

### VectorLinBus

主要的LIN总线接口类。

**参数:**
- `channel`: 通道索引（0开始）或通道掩码
- `baudrate`: 波特率（默认19200）
- `lin_version`: LIN协议版本
- `app_name`: 应用程序名称（在Vector Hardware Config中显示）

**方法:**
- `send(msg)`: 发送LIN消息
- `recv(timeout)`: 接收LIN消息
- `shutdown()`: 关闭接口

### LinMessage

LIN消息类。

**属性:**
- `frame_id`: LIN帧ID (0-63)
- `data`: 数据字节 (0-8字节)
- `timestamp`: 时间戳
- `checksum`: 校验和
- `direction`: 传输方向 ("Tx"/"Rx")
- `is_error_frame`: 是否为错误帧

## 示例程序

查看 `examples/` 目录中的示例：
- `lin_receive_example.py` - 基本的消息接收示例
- `lin_master_slave_example.py` - 主从机通信模式示例

## 常见问题

### 1. "Channel is not assigned" 错误

如果遇到此错误，有以下解决方案：

```python
# 方案1：使用全局通道（推荐）
bus = VectorLinBus(channel=0, app_name=None)

# 方案2：在Vector Hardware Config中配置应用程序
# 然后使用配置的应用程序名称
bus = VectorLinBus(channel=0, app_name="YourAppName")
```

### 2. "xlTransmit function not found" 警告

这是正常的，系统会自动切换到基于CAN的实现。

### 3. 未收到消息

LIN是主从协议，如果没有从机响应，主机只会发送请求而收不到响应。

## 实现细节

本LIN接口有两种实现方式：

1. **原生LIN实现** - 使用Vector XL API的LIN特定函数（如果可用）
2. **基于CAN的实现** - 利用CAN接口处理LIN通信（自动后备方案）

系统会自动选择可用的实现方式。

## 限制

1. 当前仅支持主机模式
2. 需要Vector硬件和驱动
3. 仅支持Windows平台
4. 从机响应需要实际的LIN从机硬件

## 开发

### 项目结构

```
lin/
├── __init__.py          # 包主入口
├── bus.py               # LinBusABC 抽象基类
├── message.py           # LinMessage 消息类
├── collector.py         # LinMessageCollector 收集器
├── interfaces/          # 硬件接口实现
│   ├── __init__.py
│   └── vector/          # Vector硬件支持
│       ├── __init__.py
│       ├── linlib.py
│       └── ...
├── examples/            # 示例代码
├── tests/              # 单元测试
├── setup.cfg           # 包配置
├── setup.py            # 安装脚本
└── README.md           # 本文档
```

### 贡献指南

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

### 测试

运行所有测试：
```bash
pytest
```

运行特定测试：
```bash
pytest tests/test_message.py
```

### 代码风格

本项目使用以下工具保证代码质量：
- `black` - 代码格式化
- `ruff` - 代码检查
- `mypy` - 类型检查

运行代码检查：
```bash
black --check lin/
ruff check lin/
mypy lin/
```

## 扩展

要添加其他厂商的LIN接口支持：

1. 在 `lin/interfaces/` 下创建新的接口模块
2. 继承 `LinBusABC` 基类
3. 实现必要的方法（send, recv, shutdown）
4. 在 `lin/interfaces/__init__.py` 中注册新接口

示例：
```python
# lin/interfaces/myvendor/mybus.py
from lin.bus import LinBusABC
from lin.message import LinMessage

class MyVendorLinBus(LinBusABC):
    def __init__(self, channel, **kwargs):
        super().__init__(channel=channel, **kwargs)
        # 初始化硬件...
    
    def send(self, msg: LinMessage, timeout=None):
        # 实现发送...
        pass
    
    def recv(self, timeout=None):
        # 实现接收...
        pass
    
    def shutdown(self):
        # 清理资源...
        pass
```

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 致谢

- 基于 [python-can](https://github.com/hardbyte/python-can) 的架构设计
- 感谢 Vector Informatik GmbH 提供的硬件支持
- 感谢所有贡献者

## 联系方式

- 项目主页: https://github.com/yourusername/python-lin
- 问题追踪: https://github.com/yourusername/python-lin/issues
- 邮件列表: python-lin@googlegroups.com