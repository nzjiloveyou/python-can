# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Running Tests
```bash
# Run all tests
tox -e py

# Run specific test file
pytest test/test_message_class.py

# Run with specific options
pytest -v --timeout=300 test/test_bus.py
```

### Code Quality Checks
```bash
# Run all checks (tests, lint, type checking, docs)
tox

# Run specific checks
tox -e lint      # Run black, ruff, pylint
tox -e type      # Run mypy type checking
tox -e docs      # Build and test documentation

# Run all checks in parallel
tox p

# Manual linting commands
black --check .
ruff check can examples doc
pylint can/**.py can/io doc/conf.py examples/**.py can/interfaces/socketcan
```

### Type Checking
```bash
# Run mypy for all supported Python versions
tox -e type

# Run mypy for specific Python version
mypy --python-version 3.9 .
```

### Building and Documentation
```bash
# Build the package
uv build

# Build documentation
python -m sphinx -b html -Wan --keep-going doc build
```

## High-Level Architecture

### Core Components

1. **BusABC** (can/bus.py:46) - Abstract base class for all CAN bus interfaces. Concrete implementations must implement methods like `send()`, `recv()`, and `shutdown()`. Supports context manager protocol and iterator pattern for message reception.

2. **Message** (can/message.py:16) - Core data structure representing CAN messages. Supports standard and extended IDs, remote frames, error frames, and CAN FD. Messages are immutable-like with slots for performance.

3. **Interfaces** (can/interfaces/) - Hardware/software specific implementations of BusABC:
   - Each interface is a separate module implementing the bus protocol
   - Registered in `BACKENDS` dictionary (can/interfaces/__init__.py:36)
   - Common interfaces: socketcan (Linux), pcan, kvaser, vector, virtual

4. **I/O Module** (can/io/) - File format readers and writers:
   - ASC, BLF, CSV, SQLite, TRC formats supported
   - Generic base classes for implementing new formats
   - Player and Logger for recording/replaying CAN traffic

5. **Notifier System** - Event-driven message handling:
   - Notifier class manages multiple listeners
   - Listeners process incoming messages (Logger, Printer, custom callbacks)
   - Thread-safe message distribution

6. **Broadcast Manager** (can/broadcastmanager.py) - Periodic message transmission:
   - CyclicSendTask for sending messages at intervals
   - Thread-based and native implementations available

### Key Design Patterns

- **Factory Pattern**: Bus creation through `can.Bus()` factory function
- **Observer Pattern**: Notifier/Listener system for message handling  
- **Iterator Pattern**: Buses are iterable for message reception
- **Context Manager**: Buses support `with` statement for resource cleanup
- **Plugin Architecture**: New interfaces can be added via entry points

### Extension Points

- New interfaces: Implement BusABC and register in BACKENDS
- New file formats: Extend classes in can.io module
- Custom listeners: Implement Listener class interface
- Message filters: Provide filter dictionaries to bus constructors