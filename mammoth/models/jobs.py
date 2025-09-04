"""
Job-related data models for the Mammoth Analytics SDK.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Status values for jobs."""
    SUCCESS = "success"
    FAILURE = "failure" 
    PROCESSING = "processing"
    ERROR = "error"


class JobSchema(BaseModel):
    """Schema for a job object."""
    
    id: int = Field(..., description="Unique identifier of the job")
    status: JobStatus = Field(..., description="Current status of the job")
    response: Dict[str, Any] = Field(..., description="Result of the asynchronous task")
    last_updated_at: datetime = Field(..., description="Timestamp of the most recent job status update")
    created_at: datetime = Field(..., description="Timestamp when the asynchronous task was created")
    path: str = Field(..., description="API request path associated with the job operation")
    operation: str = Field(..., description="Name of the asynchronous operation tracked by the job")


class JobResponse(BaseModel):
    """Response model for single job details."""
    
    job: JobSchema


class JobsGetResponse(BaseModel):
    """Response model for multiple jobs."""
    
    jobs: List[JobSchema] = Field(..., description="List of job objects")


class ObjectJobSchema(BaseModel):
    """Schema for job creation response."""
    
    status_code: Optional[int] = Field(None, description="HTTP status code")
    job_id: Optional[int] = Field(None, description="Unique identifier for the created job")
    failure_reason: Optional[str] = Field(None, description="Failure reason if status is failure")

