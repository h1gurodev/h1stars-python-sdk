"""
H1Stars Payment Gateway Python SDK
"""

from .client import H1StarsClient
from .exceptions import (
    H1StarsError,
    H1StarsAPIError,
    H1StarsAuthError,
    H1StarsValidationError,
    H1StarsNotFoundError,
    H1StarsRateLimitError,
    H1StarsServerError
)

__version__ = "1.0.0"
__all__ = [
    "H1StarsClient",
    "H1StarsError",
    "H1StarsAPIError",
    "H1StarsAuthError",
    "H1StarsValidationError",
    "H1StarsNotFoundError",
    "H1StarsRateLimitError",
    "H1StarsServerError"
]