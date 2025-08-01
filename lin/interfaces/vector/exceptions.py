"""
Exception classes for Vector LIN interface.
"""


class VectorLinError(Exception):
    """Base exception for Vector LIN interface."""
    
    def __init__(
        self,
        error_code: int,
        error_string: str,
        function: str,
    ) -> None:
        super().__init__(f"{function} failed: {error_string} (error code {error_code})")
        self.error_code = error_code
        self.error_string = error_string
        self.function = function


class VectorLinInitializationError(VectorLinError):
    """Exception raised during Vector LIN initialization."""
    pass


class VectorLinOperationError(VectorLinError):
    """Exception raised during Vector LIN operations."""
    pass