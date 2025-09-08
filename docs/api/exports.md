# Exports API Reference

The Exports API handles dataview pipeline exports, allowing you to send processed data to external destinations or create internal datasets.

## Class: ExportsAPI

Access through the client: `client.exports`

```python
exports_api = client.exports
```

## Methods

### list_exports()

Get dataview pipeline exports information with optional filtering and pagination.

```python
list_exports(
    workspace_id: int,
    project_id: int,
    dataset_id: int,
    dataview_id: int,
    fields: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    sort: Optional[str] = None,
    sequence: Optional[int] = None,
    status: Optional[ExportStatus] = None,
    reordered: Optional[bool] = None,
    handler_type: Optional[HandlerType] = None,
    end_of_pipeline: Optional[bool] = None,
    runnable: Optional[bool] = None
) -> PipelineExportsPaginated
```

**Parameters:**
- `workspace_id` (int): ID of the workspace
- `project_id` (int): ID of the project  
- `dataset_id` (int): ID of the dataset
- `dataview_id` (int): ID of the dataview
- `fields` (str, optional): Fields to return ("__standard", "__full", "__min", or comma-separated)
- `limit` (int): Maximum number of results (0-100). Defaults to 50
- `offset` (int): Number of results to skip for pagination. Defaults to 0
- `sort` (str, optional): Sort specification (e.g., "(id:asc)", "(sequence:desc)")
- `sequence` (int, optional): Filter by specific sequence number
- `status` (ExportStatus, optional): Filter by export status
- `reordered` (bool, optional): Filter by reordered status
- `handler_type` (HandlerType, optional): Filter by export destination type
- `end_of_pipeline` (bool, optional): Filter by end-of-pipeline exports
- `runnable` (bool, optional): Filter by runnable status

**Returns:** `PipelineExportsPaginated` - Paginated list of pipeline exports

**Raises:**
- `MammothAPIError`: If the API request fails

**Examples:**

```python
# List all exports with standard fields
exports_list = client.exports.list_exports(
    workspace_id=1,
    project_id=1,
    dataset_id=123,
    dataview_id=456,
    fields="__standard"
)

# List only S3 exports that are executed
s3_exports = client.exports.list_exports(
    workspace_id=1,
    project_id=1,
    dataset_id=123,
    dataview_id=456,
    handler_type=HandlerType.S3,
    status=ExportStatus.EXECUTED,
    limit=10
)

# With pagination and sorting
exports_page = client.exports.list_exports(
    workspace_id=1,
    project_id=1,
    dataset_id=123,
    dataview_id=456,
    sort="(last_modified_time:desc)",
    limit=25,
    offset=0
)

# Access results
for export in exports_list.exports:
    print(f"Export {export.id}: {export.handler_type} - {export.status}")
```

### add_export()

Add a new export to the dataview pipeline with full configuration control.

```python
add_export(
    workspace_id: int,
    project_id: int,
    dataset_id: int,
    dataview_id: int,
    export_spec: AddExportSpec
) -> Union[PipelineExportsModificationResp, JobResponse]
```

**Parameters:**
- `workspace_id` (int): ID of the workspace
- `project_id` (int): ID of the project
- `dataset_id` (int): ID of the dataset  
- `dataview_id` (int): ID of the dataview
- `export_spec` (AddExportSpec): Complete export specification

**Returns:**
- `PipelineExportsModificationResp` - If export is added immediately (status 201)
- `JobResponse` - If export creation is processed asynchronously (status 202)

**Raises:**
- `MammothAPIError`: If the API request fails

**Example:**

```python
from mammoth.models.exports import AddExportSpec, HandlerType, TriggerType, S3TargetProperties

# Create S3 target properties
target_props = S3TargetProperties(
    file="monthly_report.csv",
    file_type="csv", 
    include_hidden=False,
    is_format_set=True,
    use_format=True
)

# Create export specification
export_spec = AddExportSpec(
    DATAVIEW_ID=456,
    handler_type=HandlerType.S3,
    trigger_type=TriggerType.PIPELINE,
    target_properties=target_props,
    additional_properties={},
    condition={},
    run_immediately=True,
    validate_only=False
)

# Add the export
result = client.exports.add_export(
    workspace_id=1,
    project_id=1,
    dataset_id=123,
    dataview_id=456,
    export_spec=export_spec
)

print(f"Export created with trigger_id: {result.trigger_id}")
```

### create_s3_export()

Create an S3 export with simplified parameters - a convenience method for common S3 exports.

```python
create_s3_export(
    workspace_id: int,
    project_id: int,
    dataset_id: int,
    dataview_id: int,
    file: str,
    file_type: str = "csv",
    include_hidden: bool = False,
    is_format_set: bool = True,
    use_format: bool = True,
    sequence: Optional[int] = None,
    trigger_id: Optional[int] = None,
    end_of_pipeline: bool = True,
    trigger_type: TriggerType = TriggerType.NONE,
    condition: Optional[dict] = None,
    run_immediately: bool = True,
    validate_only: bool = False,
    additional_properties: Optional[dict] = None
) -> Union[PipelineExportsModificationResp, JobResponse]
```

**Parameters:**
- `workspace_id` (int): ID of the workspace
- `project_id` (int): ID of the project
- `dataset_id` (int): ID of the dataset
- `dataview_id` (int): ID of the dataview
- `file` (str): Output filename
- `file_type` (str): File format type. Defaults to "csv"
- `include_hidden` (bool): Include hidden columns. Defaults to False
- `is_format_set` (bool): Format explicitly set. Defaults to True
- `use_format` (bool): Apply formatting. Defaults to True
- `sequence` (int, optional): Position in pipeline (None = append to end)
- `trigger_id` (int, optional): Trigger ID for editing existing export
- `end_of_pipeline` (bool): Execute at end of pipeline. Defaults to True
- `trigger_type` (TriggerType): Type of trigger. Defaults to NONE
- `condition` (dict, optional): Export conditions. Defaults to empty
- `run_immediately` (bool): Execute immediately. Defaults to True
- `validate_only` (bool): Only validate config. Defaults to False
- `additional_properties` (dict, optional): Additional configuration

**Returns:** `PipelineExportsModificationResp` or `JobResponse` - Result of the operation

**Example:**

```python
# Simple S3 export
result = client.exports.create_s3_export(
    workspace_id=1,
    project_id=1,
    dataset_id=123,
    dataview_id=456,
    file="data_export.csv"
)

# S3 export with custom settings
result = client.exports.create_s3_export(
    workspace_id=1,
    project_id=1,
    dataset_id=123,
    dataview_id=456,
    file="detailed_export.json",
    file_type="json",
    include_hidden=True,
    trigger_type=TriggerType.SCHEDULE,
    condition={"status": "active"},
    run_immediately=False
)

print(f"S3 export created: {result.trigger_id}")
```

### create_internal_dataset_export()

Create an internal dataset export with simplified parameters - a convenience method for creating new datasets in Mammoth.

```python
create_internal_dataset_export(
    workspace_id: int,
    project_id: int,
    dataset_id: int,
    dataview_id: int,
    dataset_name: str,
    column_mapping: Optional[dict] = None,
    sequence: Optional[int] = None,
    trigger_id: Optional[int] = None,
    end_of_pipeline: bool = True,
    trigger_type: TriggerType = TriggerType.PIPELINE,
    condition: Optional[dict] = None,
    run_immediately: bool = True,
    validate_only: bool = False,
    additional_properties: Optional[dict] = None
) -> Union[PipelineExportsModificationResp, JobResponse]
```

**Parameters:**
- `workspace_id` (int): ID of the workspace
- `project_id` (int): ID of the project
- `dataset_id` (int): ID of the dataset
- `dataview_id` (int): ID of the dataview
- `dataset_name` (str): Name for the created dataset
- `column_mapping` (dict, optional): Column mapping configuration
- `sequence` (int, optional): Position in pipeline (None = append to end)
- `trigger_id` (int, optional): Trigger ID for editing existing export
- `end_of_pipeline` (bool): Execute at end of pipeline. Defaults to True
- `trigger_type` (TriggerType): Type of trigger. Defaults to PIPELINE
- `condition` (dict, optional): Export conditions. Defaults to empty
- `run_immediately` (bool): Execute immediately. Defaults to True
- `validate_only` (bool): Only validate config. Defaults to False
- `additional_properties` (dict, optional): Additional configuration

**Returns:** `PipelineExportsModificationResp` or `JobResponse` - Result of the operation

**Example:**

```python
# Simple internal dataset export
result = client.exports.create_internal_dataset_export(
    workspace_id=1,
    project_id=1,
    dataset_id=123,
    dataview_id=456,
    dataset_name="processed_customer_data"
)

# Internal dataset export with column mapping
result = client.exports.create_internal_dataset_export(
    workspace_id=1,
    project_id=1,
    dataset_id=123,
    dataview_id=456,
    dataset_name="customer_summary",
    column_mapping={
        "customer_id": "id",
        "full_name": "name", 
        "email_address": "email"
    },
    condition={"customer_status": "active"}
)

print(f"Internal dataset export created: {result.trigger_id}")
```

## Data Models

### PipelineExportsPaginated

Response model for listing exports with pagination information.

**Fields:**
- `exports` (List[ItemExportInfo]): List of export items
- `limit` (int): Maximum number of items in this page  
- `offset` (int): Starting position in the full result set
- `next` (str): URL for retrieving the next page of results

### ItemExportInfo

Information about an individual export in the pipeline.

**Fields:**
- `id` (int, optional): Unique identifier for the export
- `dataview_id` (int, optional): ID of the dataview this export belongs to
- `sequence` (int, optional): Position in pipeline execution order
- `handler_type` (HandlerType, optional): Type of export destination
- `trigger_type` (TriggerType, optional): How the export is triggered
- `status` (ExportStatus, optional): Current status of the export
- `target_properties` (dict, optional): Destination-specific configuration
- `last_modified_time` (datetime, optional): When export was last modified
- `execution_start_time` (datetime, optional): When execution started
- `execution_end_time` (datetime, optional): When execution ended
- `error_info` (dict, optional): Error information if execution failed

### PipelineExportsModificationResp

Response for export modification operations.

**Fields:**
- `trigger_id` (int): ID of the created or modified export
- `status` (ExportStatus, optional): New status of the export
- `future_id` (int, optional): ID of trackable background job if operation is asynchronous

## Usage Patterns

### Creating Simple Data Exports

```python
# Export processed data to CSV
try:
    result = client.exports.create_s3_export(
        workspace_id=1,
        project_id=1,
        dataset_id=123,
        dataview_id=456,
        file="monthly_sales.csv",
        trigger_type=TriggerType.PIPELINE,
        run_immediately=True
    )
    
    print(f"Export created successfully: {result.trigger_id}")
    
    if result.future_id:
        # Track async job if needed
        job = client.jobs.get_job(result.future_id)
        print(f"Job status: {job.status}")

except MammothAPIError as e:
    print(f"Export creation failed: {e.message}")
```

### Export Status Monitoring

```python
# Check export status regularly
exports = client.exports.list_exports(
    workspace_id=1,
    project_id=1,
    dataset_id=123,
    dataview_id=456,
    sort="(last_modified_time:desc)",
    limit=10
)

for export in exports.exports:
    print(f"Export {export.id}: {export.status}")
    
    if export.status == ExportStatus.EXECUTED:
        print(f"  ✓ Completed at {export.execution_end_time}")
    elif export.status == ExportStatus.EXECUTING:
        print(f"  ⏳ Running since {export.execution_start_time}")
    elif export.error_info:
        print(f"  ✗ Error: {export.error_info}")
```

### Batch Export Creation

```python
# Create multiple exports for different destinations
export_configs = [
    {
        "file": "sales_summary.csv",
        "condition": {"department": "sales"},
        "trigger_type": TriggerType.PIPELINE
    },
    {
        "file": "marketing_data.json", 
        "file_type": "json",
        "condition": {"department": "marketing"},
        "trigger_type": TriggerType.SCHEDULE
    }
]

created_exports = []
for config in export_configs:
    try:
        result = client.exports.create_s3_export(
            workspace_id=1,
            project_id=1,
            dataset_id=123,
            dataview_id=456,
            **config
        )
        created_exports.append(result.trigger_id)
        print(f"Created export: {result.trigger_id}")
        
    except MammothAPIError as e:
        print(f"Failed to create export {config['file']}: {e.message}")

print(f"Successfully created {len(created_exports)} exports")
```

### Working with Internal Dataset Exports

```python
# Create processed datasets for downstream use
processed_datasets = [
    {
        "dataset_name": "customer_analytics",
        "column_mapping": {
            "id": "customer_id",
            "name": "customer_name",
            "email": "contact_email"
        },
        "condition": {"status": "active"}
    },
    {
        "dataset_name": "sales_metrics", 
        "column_mapping": {
            "transaction_id": "id",
            "amount": "sale_amount",
            "date": "sale_date"
        },
        "condition": {"amount": ">0"}
    }
]

for dataset_config in processed_datasets:
    try:
        result = client.exports.create_internal_dataset_export(
            workspace_id=1,
            project_id=1,
            dataset_id=123,
            dataview_id=456,
            **dataset_config
        )
        
        print(f"Created dataset export: {dataset_config['dataset_name']}")
        print(f"  Trigger ID: {result.trigger_id}")
        
        if result.future_id:
            # Wait for completion if needed
            completed_job = client.jobs.wait_for_job(result.future_id, timeout=300)
            if 'ds_id' in completed_job.response:
                new_dataset_id = completed_job.response['ds_id']
                print(f"  New Dataset ID: {new_dataset_id}")
                
    except MammothJobFailedError as e:
        print(f"Dataset creation failed: {e.details.get('failure_reason', 'Unknown error')}")
    except MammothAPIError as e:
        print(f"API error: {e.message}")
```

### Conditional Exports with Filtering

```python
# Create exports with complex conditions
conditional_exports = [
    {
        "name": "high_value_customers",
        "condition": {
            "total_purchases": ">1000",
            "status": "active",
            "registration_date": ">2023-01-01"
        }
    },
    {
        "name": "recent_transactions", 
        "condition": {
            "transaction_date": ">30_days_ago",
            "amount": ">50"
        }
    }
]

for export_config in conditional_exports:
    result = client.exports.create_s3_export(
        workspace_id=1,
        project_id=1,
        dataset_id=123,
        dataview_id=456,
        file=f"{export_config['name']}.csv",
        condition=export_config['condition'],
        trigger_type=TriggerType.SCHEDULE,
        run_immediately=False  # Schedule for later
    )
    
    print(f"Scheduled export: {export_config['name']} (ID: {result.trigger_id})")
```

## See Also

- [Jobs API Reference](jobs.md) - Track export processing jobs
- [Exports Models](models/exports.md) - Complete model definitions  
- [Export Operations Examples](../examples/export-operations.md) - Detailed examples
- [Error Handling](../examples/error-handling.md) - Handle export operation errors
