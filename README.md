# Mammoth Python SDK

A production-ready Python SDK for the Mammoth Analytics platform, providing easy access to file management, dataset operations, and job tracking functionality.

## Features

- **Simple Authentication**: API key and secret-based authentication
- **File Management**: Upload, list, update, and delete files
- **Dataset Creation**: Automatic dataset creation from uploaded files
- **Job Tracking**: Comprehensive async job monitoring with automatic waiting
- **Type Safety**: Full type hints and Pydantic models for IDE support
- **Error Handling**: Comprehensive exception handling with detailed error information
- **Automatic Retries**: Built-in retry logic for robust API interactions

## Installation

### Using Poetry (Recommended)

```bash
poetry add mammoth-python-sdk
```

### Using pip

```bash
pip install mammoth-python-sdk
```

## Quick Start

```python
from mammoth import MammothClient

# Initialize client
client = MammothClient(
    api_key="your-api-key",
    api_secret="your-api-secret",
    base_url="https://your-mammoth-instance.com"
)

# Upload a file and create dataset
dataset_id = client.files.upload_files(
    workspace_id=1,
    project_id=1,
    files="data.csv"
)

print(f"Created dataset: {dataset_id}")
```

## Authentication

Get your API credentials from your Mammoth dashboard:

```python
client = MammothClient(
    api_key="your-api-key",      # X-API-KEY header
    api_secret="your-api-secret", # X-API-SECRET header
    base_url="https://api.mammoth.io"  # Your instance URL
)

# Test connection
if client.test_connection():
    print("Connected successfully!")
```

## Core Concepts

### Files vs Datasets
- **Files**: Raw uploaded files (CSV, Excel, etc.)
- **Datasets**: Processed, standardized data stored in Mammoth's warehouse
- When you upload a file, Mammoth processes it and creates a dataset

### Jobs
- Many operations are asynchronous and return job IDs
- Use the Jobs API to track progress and get results
- The SDK automatically handles job waiting for file uploads

## API Reference

### Files API

#### Upload Files

Upload single or multiple files to create datasets:

```python
# Single file
dataset_id = client.files.upload_files(
    workspace_id=1,
    project_id=1,
    files="data.csv"
)

# Multiple files
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
    append_to_ds_id=existing_dataset_id,
    override_target_schema=False
)
```

#### List Files

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
    fields="__full",  # or "__standard", "__min", or "id,name,status"
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
```

#### Get File Details

```python
file_details = client.files.get_file_details(
    workspace_id=1,
    project_id=1,
    file_id=123,
    fields="__full"
)

print(f"File: {file_details.name}")
print(f"Status: {file_details.status}")
print(f"Dataset ID: {file_details.additional_info.final_ds_id}")
```

#### Update File Configuration

```python
# Set password for protected file
job = client.files.set_file_password(
    workspace_id=1,
    project_id=1,
    file_id=123,
    password="secret123"
)

# Extract specific sheets from Excel file
job = client.files.extract_sheets(
    workspace_id=1,
    project_id=1,
    file_id=123,
    sheets=["Sheet1", "Data"],
    delete_file_after_extract=True,
    combine_after_extract=False
)
```

#### Delete Files

```python
# Delete single file
client.files.delete_file(
    workspace_id=1,
    project_id=1,
    file_id=123
)

# Delete multiple files
client.files.delete_files(
    workspace_id=1,
    project_id=1,
    file_ids=[123, 124, 125]
)
```

### Jobs API

#### Track Individual Jobs

```python
# Get job status
job = client.jobs.get_job(job_id=456)
print(f"Status: {job.status}")

# Wait for job completion
completed_job = client.jobs.wait_for_job(
    job_id=456,
    timeout=300,  # 5 minutes
    poll_interval=5  # Check every 5 seconds
)

# Extract dataset ID from job response
if 'ds_id' in completed_job.response:
    dataset_id = completed_job.response['ds_id']
    print(f"Dataset created: {dataset_id}")
```

#### Track Multiple Jobs

```python
# Get multiple job statuses
jobs = client.jobs.get_jobs(job_ids=[456, 457, 458])

# Wait for all jobs to complete
completed_jobs = client.jobs.wait_for_jobs(
    job_ids=[456, 457, 458],
    timeout=300
)

# Extract all dataset IDs
dataset_ids = client.jobs.extract_dataset_ids(completed_jobs)
print(f"Created datasets: {dataset_ids}")
```

## Error Handling

The SDK provides comprehensive error handling with specific exception types:

```python
from mammoth.exceptions import (
    MammothAPIError,
    MammothAuthError, 
    MammothJobTimeoutError,
    MammothJobFailedError
)

try:
    dataset_id = client.files.upload_files(
        workspace_id=1,
        project_id=1,
        files="data.csv"
    )
except MammothAuthError:
    print("Authentication failed - check your API credentials")
except MammothJobTimeoutError as e:
    print(f"Upload timed out after {e.details['timeout']} seconds")
    print(f"Job ID: {e.details['job_id']}")
except MammothJobFailedError as e:
    print(f"Upload failed: {e.details['failure_reason']}")
except MammothAPIError as e:
    print(f"API error: {e.message}")
    print(f"Status code: {e.status_code}")
    print(f"Response: {e.response_body}")
```

## Advanced Usage

### Async Operations

For long-running operations, you can start them without waiting and track progress manually:

```python
# Start upload without waiting
job_ids = client.files.upload_files(
    workspace_id=1,
    project_id=1,
    files=["large_file1.csv", "large_file2.csv"],
    wait_for_completion=False
)

# Do other work...

# Check progress later
for job_id in job_ids:
    job = client.jobs.get_job(job_id)
    print(f"Job {job_id}: {job.status}")

# Wait for all to complete
completed_jobs = client.jobs.wait_for_jobs(job_ids)
dataset_ids = client.jobs.extract_dataset_ids(completed_jobs)
```

### Working with Excel Files

```python
# Upload Excel file - may require sheet selection
try:
    dataset_id = client.files.upload_files(
        workspace_id=1,
        project_id=1,
        files="workbook.xlsx"
    )
except MammothJobFailedError:
    # File might need sheet selection or password
    file_id = get_uploaded_file_id()  # Get from files list
    
    # Set password if needed
    client.files.set_file_password(
        workspace_id=1,
        project_id=1, 
        file_id=file_id,
        password="secret"
    )
    
    # Extract specific sheets
    job = client.files.extract_sheets(
        workspace_id=1,
        project_id=1,
        file_id=file_id,
        sheets=["Data", "Summary"]
    )
```

### Context Manager

Use the client as a context manager for automatic cleanup:

```python
with MammothClient(api_key="key", api_secret="secret") as client:
    files_list = client.files.list_files(
        workspace_id=1,
        project_id=1
    )
    # Connection automatically closed when exiting context
```

### Custom Configuration

```python
client = MammothClient(
    api_key="your-key",
    api_secret="your-secret", 
    base_url="https://your-instance.com",
    timeout=60,  # 60 second request timeout
    max_retries=5  # Retry failed requests up to 5 times
)
```

## Data Models

The SDK uses Pydantic models for type safety and validation:

```python
from mammoth.models.files import FileSchema, FilesList
from mammoth.models.jobs import JobSchema, JobStatus

# All API responses are parsed into typed models
files_list: FilesList = client.files.list_files(workspace_id=1, project_id=1)
file: FileSchema = files_list.files[0]

# Access typed fields
print(f"File ID: {file.id}")  
print(f"Name: {file.name}")
print(f"Status: {file.status}")
print(f"Created: {file.created_at}")

# Check for additional info
if file.additional_info and file.additional_info.final_ds_id:
    print(f"Dataset ID: {file.additional_info.final_ds_id}")
```

## Utilities

The SDK includes helpful utility functions:

```python
from mammoth.utils.helpers import format_date_range, validate_file_path
from datetime import datetime, timedelta

# Format date ranges for API queries
start_date = datetime.now() - timedelta(days=30)
end_date = datetime.now()
date_filter = format_date_range(start_date, end_date)

# Validate file paths before upload
from pathlib import Path
try:
    valid_path = validate_file_path("data.csv")
    print(f"File is valid: {valid_path}")
except FileNotFoundError:
    print("File not found")
```

## Environment Variables

Set up your environment for easy credential management:

```bash
export MAMMOTH_API_KEY="your-api-key"
export MAMMOTH_API_SECRET="your-api-secret"
export MAMMOTH_BASE_URL="https://your-instance.com"
```

```python
import os
from mammoth import MammothClient

client = MammothClient(
    api_key=os.getenv("MAMMOTH_API_KEY"),
    api_secret=os.getenv("MAMMOTH_API_SECRET"),
    base_url=os.getenv("MAMMOTH_BASE_URL", "https://api.mammoth.io")
)
```

## Development

### Installation for Development

```bash
git clone https://github.com/mammoth-analytics/mammoth-python-sdk
cd mammoth-python-sdk
poetry install
```

### Running Tests

```bash
poetry run pytest
poetry run pytest --cov=mammoth  # With coverage
```

### Code Quality

```bash
poetry run black mammoth/  # Format code
poetry run isort mammoth/  # Sort imports  
poetry run flake8 mammoth/  # Lint code
poetry run mypy mammoth/  # Type checking
```

## Examples

See `example_usage.py` for comprehensive examples including:

- Basic file upload and dataset creation
- Multi-file operations
- Job tracking and monitoring
- Error handling patterns
- Advanced filtering and pagination
- Working with Excel files and sheets

## API Coverage

This SDK currently covers:

### Files API
- ✅ List files with filtering and pagination
- ✅ Upload single/multiple files
- ✅ Get file details
- ✅ Update file configuration (password, sheet extraction)
- ✅ Delete files

### Jobs API  
- ✅ Get job status
- ✅ Track multiple jobs
- ✅ Wait for completion with timeout
- ✅ Extract results from completed jobs

## Support

- **Documentation**: [https://docs.mammoth.io](https://docs.mammoth.io)
- **Issues**: [GitHub Issues](https://github.com/mammoth-analytics/mammoth-python-sdk/issues)
- **Support**: support@mammoth.io

## License

MIT License - see LICENSE file for details.
