"""
Export-related data models for the Mammoth Analytics SDK.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field


class HandlerType(str, Enum):
    """Handler types for export operations."""
    POSTGRES = "postgres"
    CSV_FILE = "csv_file"
    S3 = "s3"
    MYSQL = "mysql"
    MSSQL = "mssql"
    FTP = "ftp"
    SFTP = "sftp"
    EMAIL = "email"
    ELASTICSEARCH = "elasticsearch"
    POWERBI = "powerbi"
    REDSHIFT = "redshift"
    BIGQUERY = "bigquery"
    INTERNAL_DATASET = "internal_dataset"
    PUBLISHDB = "publishdb"


class TriggerType(str, Enum):
    """Trigger types for export operations."""
    NONE = "none"
    PIPELINE = "pipeline"
    SCHEDULE = "schedule"


class ExportStatus(str, Enum):
    """Status values for exports."""
    DELETED = "deleted"
    EXECUTED = "executed"
    EXECUTING = "executing"
    EDITED = "edited"
    ADDED = "added"
    SUSPENDED = "suspended"
    SUSPENDING = "suspending"


class S3TargetProperties(BaseModel):
    """Configuration properties for S3 export destinations."""
    
    file: str = Field(..., description="Output filename")
    file_type: str = Field(..., description="File format type e.g. csv")
    include_hidden: bool = Field(..., description="Include hidden columns")
    is_format_set: bool = Field(..., description="Format explicitly set")
    use_format: bool = Field(..., description="Apply formatting")


class AddExportSpec(BaseModel):
    """Specification for adding export tasks to dataview pipeline."""
    
    DATAVIEW_ID: int = Field(..., description="The ID of the View (dataview) from which data will be exported")
    sequence: Optional[int] = Field(description="The position of this export task in the pipeline execution order. If None, appended to end.", default=None)
    TRIGGER_ID: Optional[int] = Field(description="Optional ID of the trigger that initiates this export. When non-None, it means the export is being edited otherwise, export is being added", default=None)
    end_of_pipeline: bool = Field(description="Whether this export should execute at the end of the pipeline after all transformations", default=True)
    handler_type: HandlerType = Field(..., description="The type of export handler (destination type) for this export operation")
    trigger_type: TriggerType = Field(..., description="The type of trigger that controls when this export executes")
    target_properties: Union[S3TargetProperties, Dict[str, Any]] = Field(..., description="Configuration properties specific to the export destination")
    additional_properties: Dict[str, Any] = Field(..., description="Additional configuration options for the export operation")
    condition: dict[str, Any] = Field(description="Conditional logic that determines what data from the view should be exported. Empty dict means no conditions.", default=dict())
    run_immediately: bool = Field(..., description="Whether to execute this export task immediately upon creation")
    validate_only: bool = Field(description="Whether to only validate the export configuration without executing it. Useful for testing.", default=False)


class ItemExportInfo(BaseModel):
    """Information about an individual export in the pipeline."""
    
    id: Optional[int] = Field(None, description="Unique identifier for the export")
    dataview_id: Optional[int] = Field(None, description="ID of the dataview this export belongs to")
    sequence: Optional[int] = Field(None, description="Position in the pipeline execution order")
    sub_sequence: Optional[int] = Field(None, description="Sub-position within the same sequence")
    handler_type: Optional[HandlerType] = Field(None, description="Type of export handler")
    trigger_type: Optional[TriggerType] = Field(None, description="Type of trigger for this export")
    end_of_pipeline: Optional[bool] = Field(None, description="Whether this export executes at the end of the pipeline")
    status: Optional[ExportStatus] = Field(None, description="Current status of the export")
    target_properties: Optional[Dict[str, Any]] = Field(None, description="Export destination configuration")
    runnable: Optional[bool] = Field(None, description="Whether the export can be executed")
    reordered: Optional[bool] = Field(None, description="Whether the export has been reordered")
    data_pass_through: Optional[bool] = Field(None, description="Whether data passes through this export")
    additional_properties: Optional[Dict[str, Any]] = Field(None, description="Additional export configuration")
    condition: Optional[Dict[str, Any]] = Field(None, description="Conditional logic for the export")
    last_modified_time: Optional[datetime] = Field(None, description="When the export was last modified")
    execution_start_time: Optional[datetime] = Field(None, description="When the export execution started")
    execution_end_time: Optional[datetime] = Field(None, description="When the export execution ended")
    last_run_result: Optional[Dict[str, Any]] = Field(None, description="Result of the last execution")
    error_info: Optional[Dict[str, Any]] = Field(None, description="Error information if execution failed")


class PipelineExportsPaginated(BaseModel):
    """Paginated response for pipeline exports."""
    
    limit: int = Field(10, description="Setting limit would limit the items received in the page")
    offset: int = Field(0, description="First position to return from the results")
    next: str = Field(..., description="Url of the next page")
    exports: List[ItemExportInfo] = Field(..., description="List of export items")


class PipelineExportsModificationResp(BaseModel):
    """Response for export modification operations."""
    
    trigger_id: int = Field(..., description="Id of the export")
    status: Optional[ExportStatus] = Field(None, description="New status of the export")
    future_id: Optional[int] = Field(None, description="Id of the trackable job running in the background")
