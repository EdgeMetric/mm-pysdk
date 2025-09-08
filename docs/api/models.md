# Data Models Reference

The Mammoth SDK uses Pydantic models for type-safe data validation and serialization. This document describes all data models used in API requests and responses.

## File Models

### FileSchema

Main schema for file objects returned by the API.

```python
from mammoth.models.files import FileSchema

class FileSchema(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    last_updated_at: Optional[datetime] = None
    status_info: Optional[StatusInfo] = None
    additional_info: Optional[AdditionalInfo] = None
```

**Fields:**
- `id` (int, optional): Unique identifier for the file
- `name` (str, optional): Name of the file
- `status` (str, optional): Current processing status ("processing", "processed", "error", etc.)
- `created_at` (datetime, optional): Timestamp when the file was created
- `last_updated_at` (datetime, optional): Timestamp when the file was last updated
- `status_info` (StatusInfo, optional): Detailed status information
- `additional_info` (AdditionalInfo, optional): Additional file metadata

**Example:**
```python
# Access file properties
file = files_list.files[0]
print(f"File ID: {file.id}")
print(f"Name: {file.name}")
print(f"Status: {file.status}")
print(f"Created: {file.created_at}")

# Check if dataset was created
if file.additional_info and file.additional_info.final_ds_id:
    print(f"Dataset ID: {file.additional_info.final_ds_id}")
```

### FilesList

Response model for file listing operations.

```python
from mammoth.models.files import FilesList

class FilesList(BaseModel):
    files: List[FileSchema] = Field(..., description="List of files")
    limit: int = Field(10, description="Maximum number of results returned")
    offset: int = Field(0, description="Offset from the beginning of results")
    next: str = Field(..., description="URL for the next page of results")
```

**Fields:**
- `files` (List[FileSchema]): List of file objects
- `limit` (int): Maximum number of results returned (pagination)
- `offset` (int): Offset from the beginning of results (pagination)
- `next` (str): URL for the next page of results

**Example:**
```python
files_list = client.files.list_files(workspace_id=1, project_id=1)

print(f"Retrieved {len(files_list.files)} files")
print(f"Limit: {files_list.limit}, Offset: {files_list.offset}")

# Process all files
for file in files_list.files:
    print(f"- {file.name} ({file.status})")

# Check if there are more pages
if files_list.next:
    print("More files available on next page")
```

### FileDetails

Response wrapper for individual file details.

```python
from mammoth.models.files import FileDetails

class FileDetails(BaseModel):
    file: FileSchema
```

**Fields:**
- `file` (FileSchema): The file object with detailed information

**Example:**
```python
file_details = client.files.get_file_details(
    workspace_id=1, 
    project_id=1, 
    file_id=123
)

file = file_details.file
print(f"File name: {file.name}")
print(f"Status: {file.status}")
```

### AdditionalInfo

Additional metadata about a file.

```python
from mammoth.models.files import AdditionalInfo

class AdditionalInfo(BaseModel):
    append_to_ds_id: Optional[int] = None
    parent_id: Optional[str] = None
    delete_existing_after_append: bool = False
    password_protected: bool = False
    sheets_info: Optional[List[SheetInfo]] = None
    final_ds_id: Optional[int] = None
    url: Optional[str] = None
```

**Fields:**
- `append_to_ds_id` (int, optional): Dataset ID this file appends to
- `parent_id` (str, optional): Parent folder ID
- `delete_existing_after_append` (bool): Whether existing data is deleted after append
- `password_protected` (bool): Whether the file is password protected
- `sheets_info` (List[SheetInfo], optional): Excel sheet information
- `final_ds_id` (int, optional): Final dataset ID after processing
- `url` (str, optional): URL of the file

**Example:**
```python
if file.additional_info:
    info = file.additional_info
    
    # Check if dataset was created
    if info.final_ds_id:
        print(f"Dataset created: {info.final_ds_id}")
    
    # Check if it's an Excel file with sheets
    if info.sheets_info:
        print(f"Excel file with {len(info.sheets_info)} sheets:")
        for sheet in info.sheets_info:
            print(f"  - {sheet.sheet_name}: {sheet.num_rows} rows, {sheet.num_cols} cols")
    
    # Check if password protected
    if info.password_protected:
        print("File is password protected")
```

### StatusInfo

Detailed status information for a file.

```python
from mammoth.models.files import StatusInfo

class StatusInfo(BaseModel):
    extracting: Optional[str] = None
    extracted: Optional[str] = None
    action_needed: Optional[str] = None
    processing: Optional[str] = None
    processed: Optional[str] = None
    error: Optional[str] = None
    is_hidden: bool = False
    is_empty: bool = False
```

**Fields:**
- `extracting` (str, optional): Extracting status information
- `extracted` (str, optional): Extracted status information
- `action_needed` (str, optional): Action needed information
- `processing` (str, optional): Processing status information
- `processed` (str, optional): Processed status information
- `error` (str, optional): Error status information
- `is_hidden` (bool): Whether the file is hidden
- `is_empty` (bool): Whether the file is empty

**Example:**
```python
if file.status_info:
    status = file.status_info
    
    if status.error:
        print(f"File has error: {status.error}")
    elif status.action_needed:
        print(f"Action needed: {status.action_needed}")
    elif status.processing:
        print(f"Processing: {status.processing}")
    elif status.processed:
        print(f"Processed: {status.processed}")
```

### SheetInfo

Information about a sheet in an Excel file.

```python
from mammoth.models.files import SheetInfo

class SheetInfo(BaseModel):
    sheet_name: str = Field(..., min_length=1)
    num_rows: int = Field(...)
    num_cols: int = Field(...)
```

**Fields:**
- `sheet_name` (str): Name of the Excel sheet
- `num_rows` (int): Number of rows in the sheet
- `num_cols` (int): Number of columns in the sheet

**Example:**
```python
if file.additional_info and file.additional_info.sheets_info:
    for sheet in file.additional_info.sheets_info:
        print(f"Sheet '{sheet.sheet_name}':")
        print(f"  Dimensions: {sheet.num_rows} rows × {sheet.num_cols} columns")
        print(f"  Total cells: {sheet.num_rows * sheet.num_cols}")
```

### File Operation Models

#### FilePatchRequest

Request model for updating file configuration.

```python
from mammoth.models.files import FilePatchRequest, FilePatchData

class FilePatchRequest(BaseModel):
    patch: List[FilePatchData] = Field(..., description="List of patch operations")
```

**Example:**
```python
# Set file password
patch_data = FilePatchData(
    op=FilePatchOperation.REPLACE,
    path=FilePatchPath.PASSWORD,
    value="secret123"
)
patch_request = FilePatchRequest(patch=[patch_data])

job = client.files.update_file_config(
    workspace_id=1,
    project_id=1,
    file_id=123,
    patch_request=patch_request
)
```

#### FilePatchData

Individual patch operation data.

```python
from mammoth.models.files import FilePatchData, FilePatchOperation, FilePatchPath

class FilePatchData(BaseModel):
    op: FilePatchOperation = Field(..., description="Operation to perform")
    path: FilePatchPath = Field(..., description="Path to patch")
    value: Union[str, ExtractSheetsPatch] = Field(..., description="Value to set")
```

**Enums:**
```python
class FilePatchOperation(str, Enum):
    REPLACE = "replace"

class FilePatchPath(str, Enum):
    EXTRACT_SHEETS = "extract_sheets"
    PASSWORD = "password"
```

#### ExtractSheetsPatch

Configuration for extracting sheets from Excel files.

```python
from mammoth.models.files import ExtractSheetsPatch

class ExtractSheetsPatch(BaseModel):
    sheets: List[str] = Field(..., description="Names of sheets to extract")
    delete_file_after_extract: bool = Field(True, description="Delete main file after extraction")
    combine_after_extract: bool = Field(False, description="Combine sheets after extraction")
```

**Example:**
```python
# Extract specific sheets
extract_config = ExtractSheetsPatch(
    sheets=["Data", "Summary", "Charts"],
    delete_file_after_extract=True,
    combine_after_extract=False
)

patch_data = FilePatchData(
    op=FilePatchOperation.REPLACE,
    path=FilePatchPath.EXTRACT_SHEETS,
    value=extract_config
)
```

## Job Models

### JobSchema

Main schema for job objects.

```python
from mammoth.models.jobs import JobSchema, JobStatus

class JobSchema(BaseModel):
    id: int = Field(..., description="Unique identifier of the job")
    status: JobStatus = Field(..., description="Current status of the job")
    response: Dict[str, Any] = Field(..., description="Result of the asynchronous task")
    last_updated_at: datetime = Field(..., description="Most recent job status update")
    created_at: datetime = Field(..., description="When the task was created")
    path: str = Field(..., description="API request path")
    operation: str = Field(..., description="Name of the operation")
```

**Fields:**
- `id` (int): Unique identifier of the job
- `status` (JobStatus): Current status (success, failure, processing, error)
- `response` (Dict[str, Any]): Result data from the asynchronous task
- `last_updated_at` (datetime): Timestamp of the most recent status update
- `created_at` (datetime): Timestamp when the task was created
- `path` (str): API request path associated with the job
- `operation` (str): Name of the asynchronous operation

**Example:**
```python
job = client.jobs.get_job(job_id=456)

print(f"Job {job.id}: {job.status}")
print(f"Operation: {job.operation}")
print(f"Created: {job.created_at}")
print(f"Last updated: {job.last_updated_at}")

# Check for results
if job.status == JobStatus.SUCCESS:
    if 'ds_id' in job.response:
        print(f"Dataset created: {job.response['ds_id']}")
    print(f"Full response: {job.response}")
elif job.status == JobStatus.FAILURE:
    error = job.response.get('failure_reason', 'Unknown error')
    print(f"Job failed: {error}")
```

### JobStatus

Enumeration of possible job statuses.

```python
from mammoth.models.jobs import JobStatus

class JobStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PROCESSING = "processing"
    ERROR = "error"
```

**Values:**
- `SUCCESS`: Job completed successfully
- `FAILURE`: Job failed with an error
- `PROCESSING`: Job is currently running
- `ERROR`: Job encountered an error

**Example:**
```python
from mammoth.models.jobs import JobStatus

# Check job status
if job.status == JobStatus.SUCCESS:
    print("Job completed successfully")
elif job.status == JobStatus.PROCESSING:
    print("Job is still running")
elif job.status in [JobStatus.FAILURE, JobStatus.ERROR]:
    print("Job failed or encountered an error")
```

### JobResponse

Response wrapper for individual job details.

```python
from mammoth.models.jobs import JobResponse

class JobResponse(BaseModel):
    job: JobSchema
```

**Example:**
```python
# Internal use - you typically work with JobSchema directly
job_response = JobResponse(**api_response)
job = job_response.job
```

### JobsGetResponse

Response model for multiple jobs.

```python
from mammoth.models.jobs import JobsGetResponse

class JobsGetResponse(BaseModel):
    jobs: List[JobSchema] = Field(..., description="List of job objects")
```

**Example:**
```python
jobs = client.jobs.get_jobs(job_ids=[456, 457, 458])

for job in jobs:
    print(f"Job {job.id}: {job.status}")
    if job.status == JobStatus.SUCCESS and 'ds_id' in job.response:
        print(f"  Dataset: {job.response['ds_id']}")
```

### ObjectJobSchema

Schema for job creation response.

```python
from mammoth.models.jobs import ObjectJobSchema

class ObjectJobSchema(BaseModel):
    status_code: Optional[int] = None
    job_id: Optional[int] = None
    failure_reason: Optional[str] = None
```

**Fields:**
- `status_code` (int, optional): HTTP status code
- `job_id` (int, optional): Unique identifier for the created job
- `failure_reason` (str, optional): Failure reason if status is failure

**Example:**
```python
# Returned from operations that create jobs
job = client.files.set_file_password(
    workspace_id=1,
    project_id=1,
    file_id=123,
    password="secret"
)

print(f"Password update job: {job.job_id}")
if job.status_code:
    print(f"Status code: {job.status_code}")
```

## Model Usage Patterns

### Type Safety with Models

```python
from mammoth.models.files import FileSchema, FilesList
from mammoth.models.jobs import JobSchema

# Type hints for better IDE support
def process_files(files_list: FilesList) -> List[int]:
    """Process files and return dataset IDs."""
    dataset_ids = []
    
    file: FileSchema  # Type hint for loop variable
    for file in files_list.files:
        if (file.status == "processed" and 
            file.additional_info and 
            file.additional_info.final_ds_id):
            dataset_ids.append(file.additional_info.final_ds_id)
    
    return dataset_ids

def monitor_job(job: JobSchema) -> bool:
    """Monitor job and return success status."""
    print(f"Job {job.id} status: {job.status}")
    
    if job.status == JobStatus.SUCCESS:
        return True
    elif job.status in [JobStatus.FAILURE, JobStatus.ERROR]:
        error = job.response.get('failure_reason', 'Unknown error')
        print(f"Job failed: {error}")
        return False
    else:
        print("Job still processing")
        return False
```

### Model Validation

```python
from pydantic import ValidationError
from mammoth.models.files import ExtractSheetsPatch

# Models validate data automatically
try:
    extract_config = ExtractSheetsPatch(
        sheets=["Sheet1", "Sheet2"],
        delete_file_after_extract=True,
        combine_after_extract=False
    )
    print("✓ Valid configuration")
except ValidationError as e:
    print(f"✗ Invalid configuration: {e}")

# Invalid data will raise ValidationError
try:
    invalid_config = ExtractSheetsPatch(
        sheets=[],  # Empty list not allowed
        delete_file_after_extract="invalid"  # Should be boolean
    )
except ValidationError as e:
    print(f"Validation error: {e}")
```

### Working with Optional Fields

```python
def extract_file_info(file: FileSchema) -> dict:
    """Extract file information safely handling optional fields."""
    info = {
        "id": file.id,
        "name": file.name or "Unknown",
        "status": file.status or "Unknown"
    }
    
    # Safe access to optional nested fields
    if file.additional_info:
        info["dataset_id"] = file.additional_info.final_ds_id
        info["password_protected"] = file.additional_info.password_protected
        
        if file.additional_info.sheets_info:
            info["excel_sheets"] = [
                {
                    "name": sheet.sheet_name,
                    "rows": sheet.num_rows,
                    "cols": sheet.num_cols
                }
                for sheet in file.additional_info.sheets_info
            ]
    
    if file.status_info:
        info["is_hidden"] = file.status_info.is_hidden
        info["is_empty"] = file.status_info.is_empty
        if file.status_info.error:
            info["error_message"] = file.status_info.error
    
    return info
```

### Model Serialization

```python
import json
from datetime import datetime

def serialize_file_data(file: FileSchema) -> str:
    """Serialize file data to JSON."""
    # Pydantic models can be easily serialized
    return file.model_dump_json(indent=2)

def deserialize_file_data(json_str: str) -> FileSchema:
    """Deserialize file data from JSON."""
    return FileSchema.model_validate_json(json_str)

# Example usage
file_json = serialize_file_data(file)
print(file_json)

# Recreate the model from JSON
recreated_file = deserialize_file_data(file_json)
print(f"Recreated file: {recreated_file.name}")
```

### Custom Model Extensions

```python
from mammoth.models.files import FileSchema
from typing import Optional

class ExtendedFileInfo(FileSchema):
    """Extended file information with computed properties."""
    
    @property
    def is_processed(self) -> bool:
        """Check if file is fully processed."""
        return self.status == "processed"
    
    @property
    def dataset_id(self) -> Optional[int]:
        """Get dataset ID if available."""
        if self.additional_info:
            return self.additional_info.final_ds_id
        return None
    
    @property
    def excel_sheet_count(self) -> int:
        """Get number of Excel sheets."""
        if (self.additional_info and 
            self.additional_info.sheets_info):
            return len(self.additional_info.sheets_info)
        return 0
    
    def get_sheet_names(self) -> List[str]:
        """Get list of Excel sheet names."""
        if (self.additional_info and 
            self.additional_info.sheets_info):
            return [sheet.sheet_name for sheet in self.additional_info.sheets_info]
        return []

# Usage
extended_file = ExtendedFileInfo(**file.model_dump())
print(f"Is processed: {extended_file.is_processed}")
print(f"Dataset ID: {extended_file.dataset_id}")
print(f"Excel sheets: {extended_file.get_sheet_names()}")
```

## Best Practices

### 1. Use Type Hints

```python
# ✅ Good: Use proper type hints
from mammoth.models.files import FilesList, FileSchema

def process_files(files_list: FilesList) -> List[str]:
    file_names = []
    file: FileSchema
    for file in files_list.files:
        if file.name:
            file_names.append(file.name)
    return file_names
```

### 2. Handle Optional Fields Safely

```python
# ✅ Good: Check for None before accessing
if file.additional_info and file.additional_info.final_ds_id:
    dataset_id = file.additional_info.final_ds_id

# ❌ Avoid: Direct access without checking
dataset_id = file.additional_info.final_ds_id  # May raise AttributeError
```

### 3. Use Model Methods

```python
# ✅ Good: Use Pydantic model methods
file_dict = file.model_dump()  # Convert to dictionary
file_json = file.model_dump_json()  # Convert to JSON string

# ✅ Good: Validate data with models
try:
    config = ExtractSheetsPatch(sheets=sheets, delete_file_after_extract=True)
except ValidationError as e:
    print(f"Invalid configuration: {e}")
```

### 4. Leverage Model Properties

```python
# ✅ Good: Use computed properties for complex logic
@property
def processing_time(self) -> Optional[timedelta]:
    """Calculate processing time."""
    if self.created_at and self.last_updated_at:
        return self.last_updated_at - self.created_at
    return None
```

## See Also

- [Files API Reference](files.md) - API methods that use these models
- [Jobs API Reference](jobs.md) - Job-related operations
- [Basic Usage Examples](../examples/basic-usage.md) - Working with models
- [Type Safety Guide](../examples/best-practices.md) - Type hints and validation
