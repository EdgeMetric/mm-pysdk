# Files API Models

This document describes all the data models used by the Files API in the Mammoth Analytics Python SDK.

## Core Models

### FileSchema

Represents a file object in Mammoth.

```python
from mammoth.models.files import FileSchema

file = FileSchema(
    id=123,
    name="data.csv",
    status="processed",
    created_at=datetime.now(),
    last_updated_at=datetime.now()
)
```

**Fields:**
- `id` (Optional[int]): Unique identifier for the file
- `name` (Optional[str]): Name of the file (min length: 1)
- `status` (Optional[str]): Current status of the file (min length: 1)
- `created_at` (Optional[datetime]): Timestamp when the file was created
- `last_updated_at` (Optional[datetime]): Timestamp when the file was last updated
- `status_info` (Optional[StatusInfo]): Detailed status information
- `additional_info` (Optional[AdditionalInfo]): Additional file information

### FilesList

Response model for listing files with pagination information.

```python
from mammoth.models.files import FilesList

files_response = client.files.list_files(workspace_id=1, project_id=1)
print(f"Found {len(files_response.files)} files")
print(f"Next page: {files_response.next}")
```

**Fields:**
- `files` (List[FileSchema]): List of files
- `limit` (int): Maximum number of results returned (default: 10)
- `offset` (int): Offset from the beginning of results (default: 0)
- `next` (str): URL for the next page of results

### FileDetails

Response wrapper for individual file details.

```python
from mammoth.models.files import FileDetails

# This is used internally by the SDK
file_details = FileDetails(file=file_schema)
```

**Fields:**
- `file` (FileSchema): The file object

## Supporting Models

### AdditionalInfo

Additional information about a file.

```python
from mammoth.models.files import AdditionalInfo

additional_info = AdditionalInfo(
    append_to_ds_id=456,
    password_protected=True,
    final_ds_id=789
)
```

**Fields:**
- `append_to_ds_id` (Optional[int]): Dataset ID to append to
- `parent_id` (Optional[str]): Parent folder ID
- `delete_existing_after_append` (bool): Whether to delete existing data after append (default: False)
- `password_protected` (bool): Whether the file is password protected (default: False)
- `sheets_info` (Optional[List[SheetInfo]]): Information about sheets in Excel files
- `final_ds_id` (Optional[int]): Final dataset ID after processing
- `url` (Optional[str]): URL of the file

### StatusInfo

Detailed status information for a file.

```python
from mammoth.models.files import StatusInfo

status_info = StatusInfo(
    processing="File is being processed",
    processed="File processed successfully",
    is_hidden=False,
    is_empty=False
)
```

**Fields:**
- `extracting` (Optional[str]): Extracting status information
- `extracted` (Optional[str]): Extracted status information
- `action_needed` (Optional[str]): Action needed information
- `processing` (Optional[str]): Processing status information
- `processed` (Optional[str]): Processed status information
- `error` (Optional[str]): Error status information
- `is_hidden` (bool): Whether the file is hidden (default: False)
- `is_empty` (bool): Whether the file is empty (default: False)

### SheetInfo

Information about a sheet in an Excel file.

```python
from mammoth.models.files import SheetInfo

sheet_info = SheetInfo(
    sheet_name="Sheet1",
    num_rows=1000,
    num_cols=5
)
```

**Fields:**
- `sheet_name` (str): Name of the sheet (min length: 1)
- `num_rows` (int): Number of rows in the sheet
- `num_cols` (int): Number of columns in the sheet

## Configuration Models

### FilePatchRequest

Request model for updating file configuration.

```python
from mammoth.models.files import FilePatchRequest, FilePatchData, FilePatchOperation, FilePatchPath

# Set password
patch_request = FilePatchRequest(
    patch=[
        FilePatchData(
            op=FilePatchOperation.REPLACE,
            path=FilePatchPath.PASSWORD,
            value="secret123"
        )
    ]
)
```

**Fields:**
- `patch` (List[FilePatchData]): List of patch operations

### FilePatchData

Individual patch operation data.

```python
from mammoth.models.files import FilePatchData, FilePatchOperation, FilePatchPath

patch_data = FilePatchData(
    op=FilePatchOperation.REPLACE,
    path=FilePatchPath.PASSWORD,
    value="new_password"
)
```

**Fields:**
- `op` (FilePatchOperation): Operation to perform
- `path` (FilePatchPath): Path to patch
- `value` (Union[str, ExtractSheetsPatch]): Value to set

### ExtractSheetsPatch

Configuration for extracting sheets from Excel files.

```python
from mammoth.models.files import ExtractSheetsPatch

extract_config = ExtractSheetsPatch(
    sheets=["Sheet1", "Sheet2"],
    delete_file_after_extract=True,
    combine_after_extract=False
)
```

**Fields:**
- `sheets` (List[str]): Names of sheets to extract
- `delete_file_after_extract` (bool): Whether to delete main file after extraction (default: True)
- `combine_after_extract` (bool): Whether to combine sheets after extraction (default: False)

## Enums

### FilePatchOperation

Valid operations for file patching.

```python
from mammoth.models.files import FilePatchOperation

# Available operations
FilePatchOperation.REPLACE  # "replace"
```

### FilePatchPath

Valid paths for file patching.

```python
from mammoth.models.files import FilePatchPath

# Available paths
FilePatchPath.EXTRACT_SHEETS  # "extract_sheets"
FilePatchPath.PASSWORD        # "password"
```

## Example Usage

### Complete File Upload and Configuration

```python
from mammoth import MammothClient
from mammoth.models.files import FilePatchRequest, FilePatchData, FilePatchOperation, FilePatchPath, ExtractSheetsPatch

client = MammothClient(api_key="key", api_secret="secret")

# Upload file
dataset_id = client.files.upload_files(
    workspace_id=1,
    project_id=1,
    files="workbook.xlsx"
)

# Get file details
files_list = client.files.list_files(workspace_id=1, project_id=1, limit=1)
file_id = files_list.files[0].id

# Set password
client.files.set_file_password(
    workspace_id=1,
    project_id=1,
    file_id=file_id,
    password="secret123"
)

# Extract specific sheets
client.files.extract_sheets(
    workspace_id=1,
    project_id=1,
    file_id=file_id,
    sheets=["Sheet1", "Data"],
    delete_file_after_extract=True
)
```

### Working with File Lists

```python
from mammoth.utils.helpers import format_date_range
from datetime import datetime, timedelta

# Get recent files
week_ago = datetime.now() - timedelta(days=7)
now = datetime.now()
date_filter = format_date_range(week_ago, now)

files_list = client.files.list_files(
    workspace_id=1,
    project_id=1,
    created_at=date_filter,
    statuses=["processed", "processing"],
    fields="__full"
)

for file in files_list.files:
    print(f"File: {file.name}")
    print(f"Status: {file.status}")
    if file.additional_info and file.additional_info.final_ds_id:
        print(f"Dataset ID: {file.additional_info.final_ds_id}")
    print("---")
```
