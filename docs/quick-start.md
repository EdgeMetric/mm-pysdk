# Quick Start Guide

Get up and running with the Mammoth Python SDK in minutes.

## 1. Install the SDK

```bash
pip install mammoth-python-sdk
```

## 2. Set Up Authentication

Get your API credentials from your Mammoth dashboard and set environment variables:

```bash
export MAMMOTH_API_KEY="your-api-key"
export MAMMOTH_API_SECRET="your-api-secret"
```

## 3. Initialize the Client

```python
import os
from mammoth import MammothClient

client = MammothClient(
    api_key=os.getenv("MAMMOTH_API_KEY"),
    api_secret=os.getenv("MAMMOTH_API_SECRET")
)

# Test the connection
if client.test_connection():
    print("✓ Connected to Mammoth!")
```

## 4. Upload Your First File

```python
# Upload a single CSV file
dataset_id = client.files.upload_files(
    workspace_id=1,  # Replace with your workspace ID
    project_id=1,    # Replace with your project ID
    files="data.csv"  # Path to your CSV file
)

print(f"✓ Dataset created with ID: {dataset_id}")
```

## 5. List Your Files

```python
# Get a list of files in your project
files_list = client.files.list_files(
    workspace_id=1,
    project_id=1,
    limit=10
)

print(f"Found {len(files_list.files)} files:")
for file in files_list.files:
    print(f"  - {file.name} (Status: {file.status})")
```

## 6. Track Job Progress

When you upload files, Mammoth processes them asynchronously. You can track the progress:

```python
# Upload without waiting for completion
job_ids = client.files.upload_files(
    workspace_id=1,
    project_id=1,
    files="large_file.csv",
    wait_for_completion=False  # Don't wait
)

# Monitor the job manually
if job_ids:
    job_id = job_ids[0] if isinstance(job_ids, list) else job_ids
    print(f"Upload started with job ID: {job_id}")
    
    # Wait for completion
    completed_job = client.jobs.wait_for_job(job_id, timeout=300)
    
    if completed_job.status == "success":
        dataset_id = completed_job.response.get('ds_id')
        print(f"✓ Upload completed! Dataset ID: {dataset_id}")
    else:
        print("✗ Upload failed")
```

## Complete Example

Here's a complete example that demonstrates the main features:

```python
import os
from mammoth import MammothClient, MammothAPIError

def main():
    # Initialize client
    client = MammothClient(
        api_key=os.getenv("MAMMOTH_API_KEY"),
        api_secret=os.getenv("MAMMOTH_API_SECRET")
    )
    
    # Test connection
    if not client.test_connection():
        print("Failed to connect to Mammoth")
        return
    
    workspace_id = 1  # Replace with your workspace ID
    project_id = 1    # Replace with your project ID
    
    try:
        # Upload a file
        print("Uploading file...")
        dataset_id = client.files.upload_files(
            workspace_id=workspace_id,
            project_id=project_id,
            files="sample_data.csv"
        )
        print(f"✓ File uploaded successfully! Dataset ID: {dataset_id}")
        
        # List files
        print("\nListing files...")
        files_list = client.files.list_files(
            workspace_id=workspace_id,
            project_id=project_id,
            limit=5
        )
        
        print(f"Found {len(files_list.files)} files:")
        for file in files_list.files:
            print(f"  - {file.name} (ID: {file.id}, Status: {file.status})")
            
            # Get detailed file information
            if file.id:
                details = client.files.get_file_details(
                    workspace_id=workspace_id,
                    project_id=project_id,
                    file_id=file.id
                )
                print(f"    Created: {details.created_at}")
                if details.additional_info and details.additional_info.final_ds_id:
                    print(f"    Dataset ID: {details.additional_info.final_ds_id}")
        
    except MammothAPIError as e:
        print(f"API Error: {e.message}")
        if e.status_code:
            print(f"Status Code: {e.status_code}")

if __name__ == "__main__":
    main()
```

## Key Concepts

### Workspaces and Projects
- **Workspace**: Top-level organization unit tied to your subscription
- **Project**: Siloed area within a workspace for data management
- You need both workspace_id and project_id for most operations

### Files vs Datasets
- **Files**: Raw uploaded files (CSV, Excel, etc.)
- **Datasets**: Processed, standardized data stored in Mammoth's warehouse
- Uploading a file creates a corresponding dataset

### Asynchronous Operations
- File uploads are processed asynchronously
- You can either wait for completion or track jobs manually
- Jobs contain the final dataset ID in their response

## Next Steps

Now that you're up and running, explore more advanced features:

- [File Operations Guide](examples/file-operations.md) - Advanced file management
- [Job Management](examples/job-management.md) - Working with asynchronous operations
- [Error Handling](examples/error-handling.md) - Robust error handling patterns
- [API Reference](api/client.md) - Complete API documentation

## Common Issues

### Authentication Errors
- Verify your API key and secret are correct
- Check that your credentials have the necessary permissions
- Ensure you're using the correct base URL for your instance

### File Upload Issues
- Verify the file path exists and is readable
- Check that your workspace and project IDs are correct
- Ensure the file format is supported (CSV, Excel, etc.)

### Timeout Issues
- Large files may take longer to process
- Increase the timeout parameter for upload operations
- Use async operations for very large files

Need help? Check our [troubleshooting guide](advanced/troubleshooting.md) or contact support.
