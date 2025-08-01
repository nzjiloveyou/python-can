"""
LIN interfaces contain low level implementations that interact with LIN hardware.
"""

__all__ = [
    "vector",
]

# interface_name => (module, classname)
BACKENDS = {
    "vector": ("lin.interfaces.vector", "VectorLinBus"),
}