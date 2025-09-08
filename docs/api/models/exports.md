# Exports API Models

This document describes all the data models used by the Exports API in the Mammoth Analytics Python SDK.

## Core Models

### ItemExportInfo

Represents an individual export in the dataview pipeline.

```python
from mammoth.models.exports import ItemExportInfo

export = ItemExportInfo(
    id=123,
    dataview_id=456,
    sequence=1,
    handler_type=HandlerType.S3,
    trigger_type=TriggerType.PIPELINE,
    status=ExportStatus.EXECUTED
)
```

**Fields:**
- `id` (Optional[int]): Unique identifier for the export
- `dataview_id` (Optional[int]): ID of the dataview this export belongs to
- `sequence` (Optional[int]): Position in pipeline execution order
- `sub_sequence` (Optional[int]): Sub-position within the same sequence
- `handler_type` (Optional[HandlerType]): Type of export destination
- `trigger_type` (Optional[TriggerType]): How the export is triggered
- `end_of_pipeline` (Optional[bool]): Whether export executes at pipeline end
- `status` (Optional[ExportStatus]): Current status of the export
- `target_properties` (Optional[Dict[str, Any]]): Destination-specific configuration
- `runnable` (Optional[bool]): Whether the export can be executed
- `reordered` (Optional[bool]): Whether the export has been reordered
- `data_pass_through` (Optional[bool]): Whether data passes through this export
- `additional_properties` (Optional[Dict[str, Any]]): Additional configuration
- `condition` (Optional[Dict[str, Any]]): Conditional logic for the export
- `last_modified_time` (Optional[datetime]): When export was last modified
- `execution_start_time` (Optional[datetime]): When execution started
- `execution_end_time` (Optional[datetime]): When execution ended
- `last_run_result` (Optional[Dict[str, Any]]): Result of the last execution
- `error_info` (Optional[Dict[str, Any]]): Error information if execution failed

### PipelineExportsPaginated

Response model for listing exports with pagination information.

```python
from mammoth.models.exports import PipelineExportsPaginated

exports_response = client.exports.list_exports(workspace_id=1, project_id=1, dataset_id=123, dataview_id=456)
print(f"Found {len(exports_response.exports)} exports")
print(f"Next page: {exports_response.next}")
```

**Fields:**
- `exports` (List[ItemExportInfo]): List of export items
- `limit` (int): Maximum number of items in this page (default: 10)
- `offset` (int): Starting position in the full result set (default: 0)
- `next` (str): URL for retrieving the next page of results

### PipelineExportsModificationResp

Response model for export modification operations.

```python
from mammoth.models.exports import PipelineExportsModificationResp

# This is returned by export creation/modification operations
result = PipelineExportsModificationResp(
    trigger_id=789,
    status=ExportStatus.ADDED,
    future_id=101112
)
```

**Fields:**
- `trigger_id` (int): ID of the created or modified export
- `status` (Optional[ExportStatus]): New status of the export
- `future_id` (Optional[int]): ID of trackable background job if operation is asynchronous

## Supporting Models

### AddExportSpec

Complete specification for adding export tasks to dataview pipeline.

```python
from mammoth.models.exports import AddExportSpec, HandlerType, TriggerType, S3TargetProperties

export_spec = AddExportSpec(
    DATAVIEW_ID=456,
    sequence=None,
    handler_type=HandlerType.S3,
    trigger_type=TriggerType.PIPELINE,
    target_properties=S3TargetProperties(
        file="export.csv",
        file_type="csv",
        include_hidden=False,
        is_format_set=True,
        use_format=True
    ),
    additional_properties={},
    condition={"status": "active"},
    run_immediately=True
)
```

**Fields:**
- `DATAVIEW_ID` (int): The ID of the dataview to export from
- `sequence` (Optional[int]): Position in pipeline execution order. If None, appended to end
- `TRIGGER_ID` (Optional[int]): ID of trigger for editing existing export. None for new exports
- `end_of_pipeline` (bool): Whether export executes at end of pipeline after transformations (default: True)
- `handler_type` (HandlerType): Type of export destination
- `trigger_type` (TriggerType): How the export is triggered
- `target_properties` (Union[S3TargetProperties, Dict[str, Any]]): Destination-specific configuration
- `additional_properties` (Dict[str, Any]): Additional configuration options
- `condition` (Dict[str, Any]): Conditional logic for what data to export. Empty means no conditions (default: {})
- `run_immediately` (bool): Whether to execute immediately upon creation
- `validate_only` (bool): Whether to only validate configuration without executing (default: False)

### S3TargetProperties

Configuration properties for S3 export destinations.

```python
from mammoth.models.exports import S3TargetProperties

s3_config = S3TargetProperties(
    file="monthly_report.csv",
    file_type="csv",
    include_hidden=False,
    is_format_set=True,
    use_format=True
)
```

**Fields:**
- `file` (str): The name of the output file
- `file_type` (str): File format type such as "csv", "json", "xlsx"
- `include_hidden` (bool): Whether to include hidden columns in the export
- `is_format_set` (bool): Whether formatting has been explicitly configured
- `use_format` (bool): Whether to apply formatting to the output

## Enums

### HandlerType

Supported export destination types.

```python
from mammoth.models.exports import HandlerType

# Available handler types
HandlerType.POSTGRES       # "postgres"
HandlerType.CSV_FILE       # "csv_file"
HandlerType.S3             # "s3"
HandlerType.MYSQL          # "mysql"
HandlerType.MSSQL          # "mssql"
HandlerType.FTP            # "ftp"
HandlerType.SFTP           # "sftp"
HandlerType.EMAIL          # "email"
HandlerType.ELASTICSEARCH  # "elasticsearch"
HandlerType.POWERBI        # "powerbi"
HandlerType.REDSHIFT       # "redshift"
HandlerType.BIGQUERY       # "bigquery"
HandlerType.INTERNAL_DATASET # "internal_dataset"
HandlerType.PUBLISHDB      # "publishdb"
```

### TriggerType

How exports are triggered.

```python
from mammoth.models.exports import TriggerType

# Available trigger types
TriggerType.NONE      # "none" - Manual execution only
TriggerType.PIPELINE  # "pipeline" - Triggered when pipeline runs
TriggerType.SCHEDULE  # "schedule" - Triggered on a schedule
```

### ExportStatus

Current status of an export.

```python
from mammoth.models.exports import ExportStatus

# Available export statuses
ExportStatus.DELETED     # "deleted"
ExportStatus.EXECUTED    # "executed"
ExportStatus.EXECUTING   # "executing"
ExportStatus.EDITED      # "edited"
ExportStatus.ADDED       # "added"
ExportStatus.SUSPENDED   # "suspended"
ExportStatus.SUSPENDING  # "suspending"
```

## Example Usage

### Complete Export Creation and Monitoring

```python
from mammoth import MammothClient
from mammoth.models.exports import AddExportSpec, HandlerType, TriggerType, S3TargetProperties, ExportStatus

client = MammothClient(api_key="key", api_secret="secret")

# Create S3 export specification
s3_target = S3TargetProperties(
    file="customer_data.csv",
    file_type="csv",
    include_hidden=False,
    is_format_set=True,
    use_format=True
)

export_spec = AddExportSpec(
    DATAVIEW_ID=456,
    handler_type=HandlerType.S3,
    trigger_type=TriggerType.PIPELINE,
    target_properties=s3_target,
    additional_properties={},
    condition={"customer_status": "active"},
    run_immediately=True,
    validate_only=False
)

# Create the export
result = client.exports.add_export(
    workspace_id=1,
    project_id=1,
    dataset_id=123,
    dataview_id=456,
    export_spec=export_spec
)

print(f"Export created with trigger_id: {result.trigger_id}")

# Monitor export status
exports = client.exports.list_exports(
    workspace_id=1,
    project_id=1,
    dataset_id=123,
    dataview_id=456,
    handler_type=HandlerType.S3
)

for export in exports.exports:
    if export.id == result.trigger_id:
        print(f"Export status: {export.status}")
        if export.execution_start_time:
            print(f"Started: {export.execution_start_time}")
        if export.error_info:
            print(f"Error: {export.error_info}")
```

### Working with Different Export Types

```python
from mammoth.models.exports import AddExportSpec, HandlerType, TriggerType

# S3 Export
s3_export = AddExportSpec(
    DATAVIEW_ID=456,
    handler_type=HandlerType.S3,
    trigger_type=TriggerType.PIPELINE,
    target_properties={
        "file": "data.csv",
        "file_type": "csv",
        "include_hidden": False,
        "is_format_set": True,
        "use_format": True
    },
    additional_properties={},
    condition={},
    run_immediately=True
)

# Internal Dataset Export  
dataset_export = AddExportSpec(
    DATAVIEW_ID=456,
    handler_type=HandlerType.INTERNAL_DATASET,
    trigger_type=TriggerType.PIPELINE,
    target_properties={
        "dataset_name": "processed_customers",
        "COLUMN_MAPPING": {
            "id": "customer_id",
            "name": "customer_name",
            "email": "contact_email"
        }
    },
    additional_properties={},
    condition={"status": "active"},
    run_immediately=True
)

# Database Export
postgres_export = AddExportSpec(
    DATAVIEW_ID=456,
    handler_type=HandlerType.POSTGRES,
    trigger_type=TriggerType.SCHEDULE,
    target_properties={
        "connection_id": "postgres_prod",
        "table_name": "customer_exports",
        "schema": "analytics",
        "mode": "replace"
    },
    additional_properties={},
    condition={},
    run_immediately=False
)
```

### Filtering and Status Monitoring

```python
from mammoth.models.exports import ExportStatus, HandlerType

# Filter exports by status and type
executing_exports = client.exports.list_exports(
    workspace_id=1,
    project_id=1,
    dataset_id=123,
    dataview_id=456,
    status=ExportStatus.EXECUTING,
    handler_type=HandlerType.S3,
    fields="__full"
)

for export in executing_exports.exports:
    print(f"Export {export.id} is running:")
    print(f"  Handler: {export.handler_type}")
    print(f"  Started: {export.execution_start_time}")
    print(f"  Target: {export.target_properties}")
    
# Check for failed exports
failed_exports = client.exports.list_exports(
    workspace_id=1,
    project_id=1,
    dataset_id=123,
    dataview_id=456,
    sort="(last_modified_time:desc)",
    limit=10
)

for export in failed_exports.exports:
    if export.error_info:
        print(f"Export {export.id} failed:")
        print(f"  Error: {export.error_info}")
        print(f"  Last modified: {export.last_modified_time}")
```

### Using Convenience Methods vs. Full Specification

```python
# Using convenience method (recommended for common cases)
result = client.exports.create_s3_export(
    workspace_id=1,
    project_id=1,
    dataset_id=123,
    dataview_id=456,
    file="simple_export.csv",
    condition={"active": True}
)

# Using full specification (for complex cases)
complex_spec = AddExportSpec(
    DATAVIEW_ID=456,
    sequence=2,  # Specific position in pipeline
    TRIGGER_ID=None,
    end_of_pipeline=False,  # Run mid-pipeline
    handler_type=HandlerType.BIGQUERY,
    trigger_type=TriggerType.SCHEDULE,
    target_properties={
        "project_id": "my-project",
        "dataset_id": "analytics",
        "table_id": "customer_export",
        "write_disposition": "WRITE_TRUNCATE"
    },
    additional_properties={
        "labels": {"env": "prod", "team": "analytics"}
    },
    condition={
        "created_date": ">=2024-01-01",
        "customer_tier": "premium"
    },
    run_immediately=False,
    validate_only=True  # Test configuration first
)

result = client.exports.add_export(
    workspace_id=1,
    project_id=1,
    dataset_id=123,
    dataview_id=456,
    export_spec=complex_spec
)
```
