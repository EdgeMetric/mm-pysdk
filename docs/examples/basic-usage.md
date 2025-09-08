# Basic Usage Examples

This guide provides simple, practical examples to get you started with the Mammoth Python SDK.

## Setup and Authentication

```python
import os
from mammoth import MammothClient

# Initialize the client with environment variables (recommended)
client = MammothClient(
    api_key=os.getenv("MAMMOTH_API_KEY"),
    api_secret=os.getenv("MAMMOTH_API_SECRET"),
    base_url=os.getenv("MAMMOTH_BASE_URL", "https://api.mammoth.io")
)

# Test the connection
if client.test_connection():
    print("✓ Connected to Mammoth successfully!")
else:
    print("✗ Connection failed. Check your credentials.")
```

## File Upload Examples

### Single File Upload

```python
# Upload a single CSV file
dataset_id = client.files.upload_files(
    workspace_id=1,
    project_id=1,
    files="sales_data.csv"
)

print(f"✓ File uploaded! Dataset ID: {dataset_id}")
```

### Multiple File Upload

```python
# Upload multiple files at once
files_to_upload = [
    "sales_data.csv",
    "customer_data.csv",
    "product_catalog.xlsx"
]

dataset_ids = client.files.upload_files(
    workspace_id=1,
    project_id=1,
    files=files_to_upload
)

print(f"✓ Uploaded {len(dataset_ids)} files:")
for i, dataset_id in enumerate(dataset_ids):
    print(f"  {files_to_upload[i]} → Dataset {dataset_id}")
```

### Upload from File Objects

```python
# Upload from file objects or streams
with open("data.csv", "rb") as file_obj:
    dataset_id = client.files.upload_files(
        workspace_id=1,
        project_id=1,
        files=file_obj
    )
    print(f"✓ Uploaded from file object: Dataset {dataset_id}")
```

### Upload to Specific Folder

```python
# Upload to a specific folder in your project
dataset_id = client.files.upload_files(
    workspace_id=1,
    project_id=1,
    files="quarterly_report.xlsx",
    folder_resource_id="folder_123"
)

print(f"✓ File uploaded to folder: Dataset {dataset_id}")
```

## File Listing and Management

### Basic File Listing

```python
# Get all files in a project
files_list = client.files.list_files(
    workspace_id=1,
    project_id=1
)

print(f"Found {len(files_list.files)} files:")
for file in files_list.files:
    print(f"  - {file.name} (ID: {file.id}, Status: {file.status})")
```

### Filtered File Listing

```python
# List only processed files
processed_files = client.files.list_files(
    workspace_id=1,
    project_id=1,
    statuses=["processed"],
    limit=20,
    sort="(created_at:desc)"
)

print("Recently processed files:")
for file in processed_files.files:
    print(f"  - {file.name} (Created: {file.created_at})")
```

### File Details

```python
# Get detailed information about a specific file
file_details = client.files.get_file_details(
    workspace_id=1,
    project_id=1,
    file_id=123,
    fields="__full"
)

print(f"File Details:")
print(f"  Name: {file_details.name}")
print(f"  Status: {file_details.status}")
print(f"  Created: {file_details.created_at}")

# Check if dataset was created
if file_details.additional_info and file_details.additional_info.final_ds_id:
    dataset_id = file_details.additional_info.final_ds_id
    print(f"  Dataset ID: {dataset_id}")
```

## Job Management

### Asynchronous Upload

```python
# Start upload without waiting for completion
job_ids = client.files.upload_files(
    workspace_id=1,
    project_id=1,
    files="large_dataset.csv",
    wait_for_completion=False
)

if job_ids:
    job_id = job_ids[0]
    print(f"Upload started with job ID: {job_id}")
    
    # Check job status manually
    job = client.jobs.get_job(job_id)
    print(f"Job status: {job.status}")
    
    # Wait for completion
    completed_job = client.jobs.wait_for_job(job_id, timeout=600)
    
    if completed_job.status == "success":
        dataset_id = completed_job.response.get('ds_id')
        print(f"✓ Upload completed! Dataset ID: {dataset_id}")
```

### Monitoring Multiple Jobs

```python
# Upload multiple files and track all jobs
files = ["file1.csv", "file2.csv", "file3.csv"]
all_job_ids = []

# Start all uploads
for file_path in files:
    job_ids = client.files.upload_files(
        workspace_id=1,
        project_id=1,
        files=file_path,
        wait_for_completion=False
    )
    all_job_ids.extend(job_ids)

print(f"Started {len(all_job_ids)} upload jobs")

# Wait for all to complete
try:
    completed_jobs = client.jobs.wait_for_jobs(all_job_ids, timeout=900)
    dataset_ids = client.jobs.extract_dataset_ids(completed_jobs)
    
    print(f"✓ All uploads completed!")
    print(f"Created datasets: {dataset_ids}")
    
except Exception as e:
    print(f"Some uploads failed: {e}")
```

## Working with Excel Files

### Basic Excel Upload

```python
# Upload Excel file (automatic processing)
try:
    dataset_id = client.files.upload_files(
        workspace_id=1,
        project_id=1,
        files="financial_report.xlsx"
    )
    print(f"✓ Excel file processed: Dataset {dataset_id}")
    
except Exception as e:
    print(f"Excel upload failed: {e}")
    # May need manual sheet selection (see advanced examples)
```

### Extract Specific Sheets

```python
# First upload the Excel file
files_list = client.files.list_files(
    workspace_id=1,
    project_id=1,
    names=["financial_report.xlsx"]
)

if files_list.files:
    file_id = files_list.files[0].id
    
    # Extract specific sheets
    job = client.files.extract_sheets(
        workspace_id=1,
        project_id=1,
        file_id=file_id,
        sheets=["Revenue", "Expenses", "Summary"],
        delete_file_after_extract=True
    )
    
    print(f"Sheet extraction started: Job {job.job_id}")
```

## Error Handling

### Basic Error Handling

```python
from mammoth.exceptions import MammothAPIError, MammothAuthError

try:
    dataset_id = client.files.upload_files(
        workspace_id=1,
        project_id=1,
        files="data.csv"
    )
    print(f"✓ Success: Dataset {dataset_id}")
    
except MammothAuthError:
    print("✗ Authentication failed - check your API credentials")
    
except MammothAPIError as e:
    print(f"✗ API Error: {e.message}")
    if e.status_code == 404:
        print("  Workspace or project not found")
    elif e.status_code == 400:
        print("  Invalid request - check your parameters")
        
except FileNotFoundError:
    print("✗ File not found - check the file path")
    
except Exception as e:
    print(f"✗ Unexpected error: {e}")
```

### Job Error Handling

```python
from mammoth.exceptions import MammothJobTimeoutError, MammothJobFailedError

try:
    dataset_id = client.files.upload_files(
        workspace_id=1,
        project_id=1,
        files="data.csv",
        timeout=300
    )
    print(f"✓ Upload completed: Dataset {dataset_id}")
    
except MammothJobTimeoutError as e:
    job_id = e.details['job_id']
    timeout = e.details['timeout']
    print(f"✗ Job {job_id} timed out after {timeout} seconds")
    print("  File may still be processing - check later")
    
except MammothJobFailedError as e:
    job_id = e.details['job_id']
    reason = e.details.get('failure_reason', 'Unknown error')
    print(f"✗ Job {job_id} failed: {reason}")
```

## File Deletion

### Delete Single File

```python
# Delete a specific file
try:
    client.files.delete_file(
        workspace_id=1,
        project_id=1,
        file_id=123
    )
    print("✓ File deleted successfully")
    
except MammothAPIError as e:
    print(f"✗ Failed to delete file: {e.message}")
```

### Delete Multiple Files

```python
# Delete multiple files at once
file_ids_to_delete = [123, 124, 125]

try:
    client.files.delete_files(
        workspace_id=1,
        project_id=1,
        file_ids=file_ids_to_delete
    )
    print(f"✓ Deleted {len(file_ids_to_delete)} files")
    
except MammothAPIError as e:
    print(f"✗ Failed to delete files: {e.message}")
```

## Context Manager Usage

```python
# Use context manager for automatic cleanup
with MammothClient(
    api_key=os.getenv("MAMMOTH_API_KEY"),
    api_secret=os.getenv("MAMMOTH_API_SECRET")
) as client:
    
    # Upload file
    dataset_id = client.files.upload_files(
        workspace_id=1,
        project_id=1,
        files="data.csv"
    )
    
    # List files
    files = client.files.list_files(workspace_id=1, project_id=1)
    
    print(f"Uploaded dataset {dataset_id}")
    print(f"Total files: {len(files.files)}")
    
# Connection automatically closed here
```

## Date Range Filtering

```python
from mammoth.utils.helpers import format_date_range
from datetime import datetime, timedelta

# Get files from the last 7 days
end_date = datetime.now()
start_date = end_date - timedelta(days=7)
date_filter = format_date_range(start_date, end_date)

recent_files = client.files.list_files(
    workspace_id=1,
    project_id=1,
    created_at=date_filter
)

print(f"Files from last 7 days: {len(recent_files.files)}")
for file in recent_files.files:
    print(f"  - {file.name} ({file.created_at})")
```

## Complete Workflow Example

```python
import os
from mammoth import MammothClient
from mammoth.exceptions import MammothAPIError

def complete_upload_workflow():
    """Complete example of uploading and managing files."""
    
    # Initialize client
    client = MammothClient(
        api_key=os.getenv("MAMMOTH_API_KEY"),
        api_secret=os.getenv("MAMMOTH_API_SECRET")
    )
    
    # Configuration
    workspace_id = 1
    project_id = 1
    files_to_upload = ["sales.csv", "customers.csv"]
    
    try:
        print("🚀 Starting upload workflow...")
        
        # 1. Test connection
        if not client.test_connection():
            raise Exception("Failed to connect to Mammoth")
        print("✓ Connection verified")
        
        # 2. Upload files
        print(f"📤 Uploading {len(files_to_upload)} files...")
        dataset_ids = client.files.upload_files(
            workspace_id=workspace_id,
            project_id=project_id,
            files=files_to_upload,
            timeout=600
        )
        print(f"✓ Uploaded {len(dataset_ids)} files successfully")
        
        # 3. List updated files
        print("📋 Listing current files...")
        files_list = client.files.list_files(
            workspace_id=workspace_id,
            project_id=project_id,
            limit=10,
            sort="(created_at:desc)"
        )
        
        print(f"📊 Current files in project:")
        for file in files_list.files[:5]:  # Show latest 5
            status_emoji = "✅" if file.status == "processed" else "⏳"
            print(f"  {status_emoji} {file.name} (Status: {file.status})")
        
        # 4. Get details of uploaded files
        for i, dataset_id in enumerate(dataset_ids):
            print(f"\n📄 Details for {files_to_upload[i]}:")
            print(f"   Dataset ID: {dataset_id}")
            
        print("\n🎉 Workflow completed successfully!")
        return dataset_ids
        
    except MammothAPIError as e:
        print(f"❌ API Error: {e.message}")
        if e.status_code:
            print(f"   Status Code: {e.status_code}")
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

# Run the workflow
if __name__ == "__main__":
    dataset_ids = complete_upload_workflow()
    if dataset_ids:
        print(f"\nCreated datasets: {dataset_ids}")
```

## Next Steps

- [File Operations Guide](file-operations.md) - Advanced file management
- [Job Management Examples](job-management.md) - Advanced job tracking
- [Error Handling Guide](error-handling.md) - Comprehensive error handling
- [API Reference](../api/client.md) - Complete API documentation
