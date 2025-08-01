# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-01-XX

### Added
- Initial release of python-lin
- Basic LIN bus interface (`LinBusABC`)
- LIN message class (`LinMessage`)
- Vector hardware support via `VectorLinBus`
- Message collector with threading support (`LinMessageCollector`)
- Support for LIN 1.3, 2.0, 2.1, and 2.2 protocols
- Examples for basic usage and message collection
- Comprehensive documentation

### Features
- Send and receive LIN messages
- Background message collection with statistics
- Multiple implementation strategies (native LIN, CAN-based fallback)
- Context manager support for automatic resource cleanup
- Compatible with python-can architecture

### Known Issues
- Currently only supports master mode
- Windows only (due to Vector driver requirements)
- Requires Vector hardware for operation

[Unreleased]: https://github.com/yourusername/python-lin/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/python-lin/releases/tag/v0.1.0