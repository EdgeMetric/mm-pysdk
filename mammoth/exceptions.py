"""
Custom exceptions for the Mammoth Analytics SDK.
"""

from typing import Optional, Dict, Any


class MammothError(Exception):
    """Base exception for Mammoth SDK errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class MammothAPIError(MammothError):
    """Exception raised for API-related errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_body: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.response_body = response_body or {}
        super().__init__(message, details)


class MammothAuthError(MammothAPIError):
    """Exception raised for authentication-related errors."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class MammothJobTimeoutError(MammothError):
    """Exception raised when a job times out."""
    
    def __init__(self, job_id: int, timeout_seconds: int):
        message = f"Job {job_id} timed out after {timeout_seconds} seconds"
        super().__init__(message, {"job_id": job_id, "timeout": timeout_seconds})


class MammothJobFailedError(MammothError):
    """Exception raised when a job fails."""
    
    def __init__(self, job_id: int, failure_reason: Optional[str] = None):
        message = f"Job {job_id} failed"
        if failure_reason:
            message += f": {failure_reason}"
        super().__init__(message, {"job_id": job_id, "failure_reason": failure_reason})
