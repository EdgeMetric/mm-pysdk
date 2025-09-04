"""
File-related data models for the Mammoth Analytics SDK.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field


class SheetInfo(BaseModel):
    """Information about a sheet in an Excel file."""
    
    sheet_name: str = Field(..., min_length=1, description="Name of the sheet")
    num_rows: int = Field(..., description="Number of rows in the sheet") 
    num_cols: int = Field(..., description="Number of columns in the sheet")


class AdditionalInfo(BaseModel):
    """Additional information about a file."""
    
    append_to_ds_id: Optional[int] = Field(None, description="Dataset ID to append to")
    parent_id: Optional[str] = Field(None, description="Parent folder ID")
    delete_existing_after_append: bool = Field(False, description="Whether to delete existing data after append")
    password_protected: bool = Field(False, description="Whether the file is password protected")
    sheets_info: Optional[List[SheetInfo]] = Field(None, description="Information about sheets in Excel files")
    final_ds_id: Optional[int] = Field(None, description="Final dataset ID after processing")
    url: Optional[str] = Field(None, description="URL of the file")


class StatusInfo(BaseModel):
    """Status information for a file."""
    
    extracting: Optional[str] = Field(None, description="Extracting status information")
    extracted: Optional[str] = Field(None, description="Extracted status information") 
    action_needed: Optional[str] = Field(None, description="Action needed information")
    processing: Optional[str] = Field(None, description="Processing status information")
    processed: Optional[str] = Field(None, description="Processed status information")
    error: Optional[str] = Field(None, description="Error status information")
    is_hidden: bool = Field(False, description="Whether the file is hidden")
    is_empty: bool = Field(False, description="Whether the file is empty")


class FileSchema(BaseModel):
    """Schema for a file object."""
    
    id: Optional[int] = Field(None, description="Unique identifier for the file")
    name: Optional[str] = Field(None, min_length=1, description="Name of the file")
    status: Optional[str] = Field(None, min_length=1, description="Current status of the file")
    created_at: Optional[datetime] = Field(None, description="Timestamp when the file was created")
    last_updated_at: Optional[datetime] = Field(None, description="Timestamp when the file was last updated")
    status_info: Optional[StatusInfo] = Field(None, description="Detailed status information")
    additional_info: Optional[AdditionalInfo] = Field(None, description="Additional file information")


class FileDetails(BaseModel):
    """Response model for file details."""
    
    file: FileSchema


class FilesList(BaseModel):
    """Response model for listing files."""
    
    files: List[FileSchema] = Field(..., description="List of files")
    limit: int = Field(10, description="Maximum number of results returned")
    offset: int = Field(0, description="Offset from the beginning of results")
    next: str = Field(..., description="URL for the next page of results")


class ExtractSheetsPatch(BaseModel):
    """Configuration for extracting sheets from Excel files."""
    
    sheets: List[str] = Field(..., description="Names of sheets to extract")
    delete_file_after_extract: bool = Field(True, description="Whether to delete main file after extraction")
    combine_after_extract: bool = Field(False, description="Whether to combine sheets after extraction")


class FilePatchOperation(str, Enum):
    """Valid operations for file patching."""
    REPLACE = "replace"


class FilePatchPath(str, Enum):
    """Valid paths for file patching."""
    EXTRACT_SHEETS = "extract_sheets"
    PASSWORD = "password"


class FilePatchData(BaseModel):
    """Data for a single patch operation."""
    
    op: FilePatchOperation = Field(..., description="Operation to perform")
    path: FilePatchPath = Field(..., description="Path to patch")
    value: Union[str, ExtractSheetsPatch] = Field(..., description="Value to set")


class FilePatchRequest(BaseModel):
    """Request model for patching file configuration."""
    
    patch: List[FilePatchData] = Field(..., description="List of patch operations")
    
    class Config:
        schema_extra = {
            "examples": [
                {
                    "patch": [
                        {
                            "op": "replace",
                            "path": "password", 
                            "value": "test"
                        }
                    ]
                },
                {
                    "patch": [
                        {
                            "op": "replace",
                            "path": "extract_sheets",
                            "value": {
                                "sheets": ["Sheet1", "Sheet2"],
                                "delete_file_after_extract": True
                            }
                        }
                    ]
                }
            ]
        }


