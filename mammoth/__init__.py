"""
Mammoth Analytics Python SDK

A Python client for the Mammoth Analytics platform API.
"""

from .client import MammothClient
from .exceptions import MammothError, MammothAPIError, MammothAuthError
from .models import *

__version__ = "0.1.0"
__all__ = [
    "MammothClient",
    "MammothError", 
    "MammothAPIError",
    "MammothAuthError",
]
