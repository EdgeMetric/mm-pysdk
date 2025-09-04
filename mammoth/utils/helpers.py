"""
Helper functions for the Mammoth Analytics SDK.
"""

import os
from pathlib import Path
from typing import Union, List
from datetime import datetime


def format_date_range(from_date: datetime, to_date: datetime) -> str:
    """
    Format a date range for API queries.
    
    Args:
        from_date: Start date
        to_date: End date
        
    Returns:
        Formatted date range string for API
    """
    from_str = from_date.isoformat() + 'Z' if not from_date.tzinfo else from_date.isoformat()
    to_str = to_date.isoformat() + 'Z' if not to_date.tzinfo else to_date.isoformat()
    return f"(from:'{from_str}',to:'{to_str}')"


def validate_file_path(file_path: Union[str, Path]) -> Path:
    """
    Validate and normalize a file path.
    
    Args:
        file_path: File path to validate
        
    Returns:
        Normalized Path object
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If path is not a file
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    
    return path


def parse_job_ids(job_ids_str: str) -> List[int]:
    """
    Parse comma-separated job IDs string into list of integers.
    
    Args:
        job_ids_str: Comma-separated job IDs
        
    Returns:
        List of job ID integers
        
    Raises:
        ValueError: If any job ID is not a valid integer
    """
    if not job_ids_str.strip():
        return []
    
    try:
        return [int(job_id.strip()) for job_id in job_ids_str.split(',')]
    except ValueError as e:
        raise ValueError(f"Invalid job ID format: {e}")

