# Files API Reference

The Files API handles file uploads, management, and dataset creation operations.

## Class: FilesAPI

Access through the client: `client.files`

```python
files_api = client.files
```

## Methods

### upload_files()

Upload one or more files to create datasets. Each file becomes a separate dataset.

```python
upload_files(
    workspace_id: int,
    project_id: int,
    files: Union[List[Union[str, Path, BinaryIO]], str, Path, BinaryIO],
    folder_resource_id: Optional[str] = None,
    append_to_ds_id: Optional[int] = None,
    override_target_schema: Optional[bool] = None,
    wait_for_completion: bool = True,
    timeout: int = 300
) -> Union[List[int], int, None]
```

**Parameters:**
- `workspace_id` (int): ID of the workspace
- `project_id` (int): ID of the project
- `files`: File(s) to upload - can be file paths, Path objects, or file-like objects
- `folder_resource_id` (str, optional): Resource ID of target folder
- `append_to_ds_id` (int, optional): Dataset ID to append to (for existing dataset)
- `override_target_schema` (bool, optional): Whether to override target schema when appending
- `wait_for_completion` (bool): Whether to wait for upload processing to complete. Defaults to True
- `timeout` (int): Timeout in seconds when waiting for completion. Defaults to 300

**Returns:**
- Single file: `int` (dataset ID) or `None`
- Multiple files: `List[int]` (list of dataset IDs)

**Raises:**
- `MammothAPIError`: If the API request fails
- `MammothJobTimeoutError`: If job processing times out
- `MammothJobFailedError`: If job processing fails

**Examples:**

```python
# Upload single file
dataset_id = client.files.upload_files(
    workspace_id=1,
    project_id=1,
    files="data.csv"
)

# Upload multiple files
dataset_ids = client.files.upload_files(
    workspace_id=1,
    project_id=1,
    files=["data1.csv", "data2.csv", "data3.csv"]
)

# Upload to specific folder
dataset_id = client.files.upload_files(
    workspace_id=1,
    project_id=1,
    files="data.csv",
    folder_resource_id="folder_123"
)

# Append to existing dataset
dataset_id = client.files.upload_files(
    workspace_id=1,
    project_id=1,
    files="new_data.csv",
    append_to_ds_id=456,
    override_target_schema=False
)

# Async upload (don't wait)
job_ids = client.files.upload_files(
    workspace_id=1,
    project_id=1,
    files="large_file.csv",
    wait_for_completion=False
)
```

### list_files()

List files in a project with optional filtering and pagination.

```python
list_files(
    workspace_id: int,
    project_id: int,
    fields: Optional[str] = None,
    file_ids: Optional[List[int]] = None,
    names: Optional[List[str]] = None,
    statuses: Optional[List[str]] = None,
    created_at: Optional[str] = None,
    updated_at: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    sort: Optional[str] = None
) -> FilesList
```

**Parameters:**
- `workspace_id` (int): ID of the workspace
- `project_id` (int): ID of the project
- `fields` (str, optional): Fields to return ("__standard", "__full", "__min", or comma-separated)
- `file_ids` (List[int], optional): List of specific file IDs to retrieve
- `names` (List[str], optional): List of file names to filter by
- `statuses` (List[str], optional): List of statuses to filter by
- `created_at` (str, optional): Date range filter for creation date
- `updated_at` (str, optional): Date range filter for update date
- `limit` (int): Maximum number of results (0-100). Defaults to 50
- `offset` (int): Number of results to skip. Defaults to 0
- `sort` (str, optional): Sort specification (e.g., "(id:asc),(name:desc)")

**Returns:** `FilesList` - List of files with pagination info

**Examples:**

```python
# Basic listing
files_list = client.files.list_files(
    workspace_id=1,
    project_id=1
)

# With filtering and pagination
files_list = client.files.list_files(
    workspace_id=1,
    project_id=1,
    fields="__full",
    statuses=["processed", "processing"],
    limit=50,
    offset=0,
    sort="(created_at:desc)"
)

# Filter by date range
from mammoth.utils.helpers import format_date_range
from datetime import datetime, timedelta

week_ago = datetime.now() - timedelta(days=7)
now = datetime.now()
date_filter = format_date_range(week_ago, now)

recent_files = client.files.list_files(
    workspace_id=1,
    project_id=1,
    created_at=date_filter
)

# Access results
for file in files_list.files:
    print(f"File: {file.name} (ID: {file.id}, Status: {file.status})")
```

### get_file_details()

Get detailed information about a specific file.

```python
get_file_details(
    workspace_id: int,
    project_id: int,
    file_id: int,
    fields: Optional[str] = None
) -> FileSchema
```

**Parameters:**
- `workspace_id` (int): ID of the workspace
- `project_id` (int): ID of the project
- `file_id` (int): ID of the file
- `fields` (str, optional): Fields to return. Defaults to "__standard"

**Returns:** `FileSchema` - Detailed file information

**Example:**

```python
file_details = client.files.get_file_details(
    workspace_id=1,
    project_id=1,
    file_id=123,
    fields="__full"
)

print(f"File: {file_details.name}")
print(f"Status: {file_details.status}")
print(f"Created: {file_details.created_at}")

if file_details.additional_info and file_details.additional_info.final_ds_id:
    print(f"Dataset ID: {file_details.additional_info.final_ds_id}")
```

### delete_file()

Delete a specific file.

```python
delete_file(
    workspace_id: int,
    project_id: int,
    file_id: int
) -> None
```

**Parameters:**
- `workspace_id` (int): ID of the workspace
- `project_id` (int): ID of the project
- `file_id` (int): ID of the file to delete

**Example:**

```python
client.files.delete_file(
    workspace_id=1,
    project_id=1,
    file_id=123
)
```

### delete_files()

Delete multiple files.

```python
delete_files(
    workspace_id: int,
    project_id: int,
    file_ids: List[int]
) -> None
```

**Parameters:**
- `workspace_id` (int): ID of the workspace
- `project_id` (int): ID of the project
- `file_ids` (List[int]): List of file IDs to delete

**Example:**

```python
client.files.delete_files(
    workspace_id=1,
    project_id=1,
    file_ids=[123, 124, 125]
)
```

### set_file_password()

Set password for a password-protected file.

```python
set_file_password(
    workspace_id: int,
    project_id: int,
    file_id: int,
    password: str
) -> ObjectJobSchema
```

**Parameters:**
- `workspace_id` (int): ID of the workspace
- `project_id` (int): ID of the project
- `file_id` (int): ID of the file
- `password` (str): Password to set

**Returns:** `ObjectJobSchema` - Job information for the update operation

**Example:**

```python
job = client.files.set_file_password(
    workspace_id=1,
    project_id=1,
    file_id=123,
    password="secret123"
)

print(f"Password set job ID: {job.job_id}")
```

### extract_sheets()

Extract specific sheets from an Excel file.

```python
extract_sheets(
    workspace_id: int,
    project_id: int,
    file_id: int,
    sheets: List[str],
    delete_file_after_extract: bool = True,
    combine_after_extract: bool = False
) -> ObjectJobSchema
```

**Parameters:**
- `workspace_id` (int): ID of the workspace
- `project_id` (int): ID of the project
- `file_id` (int): ID of the Excel file
- `sheets` (List[str]): List of sheet names to extract
- `delete_file_after_extract` (bool): Whether to delete main file after extraction. Defaults to True
- `combine_after_extract` (bool): Whether to combine sheets after extraction. Defaults to False

**Returns:** `ObjectJobSchema` - Job information for the extraction operation

**Example:**

```python
job = client.files.extract_sheets(
    workspace_id=1,
    project_id=1,
    file_id=123,
    sheets=["Sheet1", "Data"],
    delete_file_after_extract=True,
    combine_after_extract=False
)

print(f"Sheet extraction job ID: {job.job_id}")
```

## Data Models

### FilesList

Response model for listing files.

**Fields:**
- `files` (List[FileSchema]): List of files
- `limit` (int): Maximum number of results returned
- `offset` (int): Offset from the beginning of results
- `next` (str): URL for the next page of results

### FileSchema

Schema for a file object.

**Fields:**
- `id` (int, optional): Unique identifier for the file
- `name` (str, optional): Name of the file
- `status` (str, optional): Current status of the file
- `created_at` (datetime, optional): Timestamp when the file was created
- `last_updated_at` (datetime, optional): Timestamp when the file was last updated
- `status_info` (StatusInfo, optional): Detailed status information
- `additional_info` (AdditionalInfo, optional): Additional file information

### AdditionalInfo

Additional information about a file.

**Fields:**
- `append_to_ds_id` (int, optional): Dataset ID to append to
- `parent_id` (str, optional): Parent folder ID
- `delete_existing_after_append` (bool): Whether to delete existing data after append
- `password_protected` (bool): Whether the file is password protected
- `sheets_info` (List[SheetInfo], optional): Information about sheets in Excel files
- `final_ds_id` (int, optional): Final dataset ID after processing
- `url` (str, optional): URL of the file

## Usage Patterns

### Batch File Upload

```python
# Upload multiple files efficiently
files_to_upload = ["data1.csv", "data2.csv", "data3.csv"]

try:
    dataset_ids = client.files.upload_files(
        workspace_id=1,
        project_id=1,
        files=files_to_upload,
        wait_for_completion=True,
        timeout=600  # 10 minutes for large files
    )
    
    print(f"Successfully uploaded {len(dataset_ids)} files")
    for i, dataset_id in enumerate(dataset_ids):
        print(f"  {files_to_upload[i]} -> Dataset {dataset_id}")
        
except MammothJobTimeoutError as e:
    print(f"Upload timed out: {e}")
except MammothJobFailedError as e:
    print(f"Upload failed: {e.details.get('failure_reason', 'Unknown error')}")
```

### File Status Monitoring

```python
# Check file processing status
files = client.files.list_files(
    workspace_id=1,
    project_id=1,
    statuses=["processing", "processed", "error"]
)

for file in files.files:
    print(f"{file.name}: {file.status}")
    
    if file.status == "processed" and file.additional_info:
        dataset_id = file.additional_info.final_ds_id
        print(f"  -> Dataset {dataset_id} ready for use")
    elif file.status == "error":
        print(f"  -> Processing failed")
```

### Working with Excel Files

```python
# Upload Excel file and handle sheets
try:
    dataset_id = client.files.upload_files(
        workspace_id=1,
        project_id=1,
        files="workbook.xlsx"
    )
    print(f"Excel file processed: Dataset {dataset_id}")
    
except MammothJobFailedError:
    # File might need sheet selection
    files = client.files.list_files(
        workspace_id=1,
        project_id=1,
        names=["workbook.xlsx"]
    )
    
    if files.files:
        file_id = files.files[0].id
        
        # Extract specific sheets
        job = client.files.extract_sheets(
            workspace_id=1,
            project_id=1,
            file_id=file_id,
            sheets=["Data", "Summary"],
            delete_file_after_extract=True
        )
        
        print(f"Sheet extraction started: Job {job.job_id}")
```

## See Also

- [Jobs API Reference](jobs.md) - Track file processing jobs
- [Data Models](models.md) - Complete model definitions
- [File Operations Examples](../examples/file-operations.md) - Detailed examples
- [Error Handling](../examples/error-handling.md) - Handle file operation errors
