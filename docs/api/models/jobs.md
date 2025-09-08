# Jobs API Models

This document describes all the data models used by the Jobs API in the Mammoth Analytics Python SDK.

## Core Models

### JobSchema

Represents a job object in Mammoth that tracks asynchronous operations.

```python
from mammoth.models.jobs import JobSchema, JobStatus

job = JobSchema(
    id=123,
    status=JobStatus.SUCCESS,
    response={"ds_id": 456},
    last_updated_at=datetime.now(),
    created_at=datetime.now(),
    path="/workspaces/1/projects/1/files",
    operation="file_upload"
)
```

**Fields:**
- `id` (int): Unique identifier of the job
- `status` (JobStatus): Current status of the job
- `response` (Dict[str, Any]): Result of the asynchronous task
- `last_updated_at` (datetime): Timestamp of the most recent job status update
- `created_at` (datetime): Timestamp when the asynchronous task was created
- `path` (str): API request path associated with the job operation
- `operation` (str): Name of the asynchronous operation tracked by the job

### JobResponse

Response wrapper for single job details.

```python
from mammoth.models.jobs import JobResponse

# This is used internally by the SDK
job_response = JobResponse(job=job_schema)
```

**Fields:**
- `job` (JobSchema): The job object

### JobsGetResponse

Response model for multiple jobs.

```python
from mammoth.models.jobs import JobsGetResponse

jobs_response = client.jobs.get_jobs([123, 124, 125])
print(f"Retrieved {len(jobs_response.jobs)} jobs")
```

**Fields:**
- `jobs` (List[JobSchema]): List of job objects

### ObjectJobSchema

Schema for job creation response, typically returned when starting asynchronous operations.

```python
from mammoth.models.jobs import ObjectJobSchema

# This is typically returned from upload operations
object_job = ObjectJobSchema(
    status_code=200,
    job_id=123,
    failure_reason=None
)
```

**Fields:**
- `status_code` (Optional[int]): HTTP status code
- `job_id` (Optional[int]): Unique identifier for the created job
- `failure_reason` (Optional[str]): Failure reason if status is failure

## Enums

### JobStatus

Status values for jobs.

```python
from mammoth.models.jobs import JobStatus

# Available statuses
JobStatus.SUCCESS     # "success"
JobStatus.FAILURE     # "failure"
JobStatus.PROCESSING  # "processing"
JobStatus.ERROR       # "error"
```

## Example Usage

### Basic Job Tracking

```python
from mammoth import MammothClient
from mammoth.models.jobs import JobStatus

client = MammothClient(api_key="key", api_secret="secret")

# Start an async operation (returns job ID)
job_ids = client.files.upload_files(
    workspace_id=1,
    project_id=1,
    files="data.csv",
    wait_for_completion=False  # Don't wait
)

job_id = job_ids[0]  # Get first job ID

# Check job status
job = client.jobs.get_job(job_id)
print(f"Job {job.id} status: {job.status}")
print(f"Operation: {job.operation}")
print(f"Created: {job.created_at}")
print(f"Updated: {job.last_updated_at}")

# Check if completed
if job.status == JobStatus.SUCCESS:
    print("Job completed successfully!")
    if 'ds_id' in job.response:
        dataset_id = job.response['ds_id']
        print(f"Created dataset: {dataset_id}")
elif job.status in [JobStatus.FAILURE, JobStatus.ERROR]:
    print("Job failed!")
    if 'failure_reason' in job.response:
        print(f"Reason: {job.response['failure_reason']}")
else:
    print("Job still processing...")
```

### Waiting for Job Completion

```python
from mammoth.exceptions import MammothJobTimeoutError, MammothJobFailedError

try:
    # Wait for job to complete
    completed_job = client.jobs.wait_for_job(
        job_id=job_id,
        timeout=300,  # 5 minutes
        poll_interval=5  # Check every 5 seconds
    )
    
    print(f"Job completed with status: {completed_job.status}")
    
    # Extract dataset ID from response
    if 'ds_id' in completed_job.response:
        dataset_id = completed_job.response['ds_id']
        print(f"Dataset created: {dataset_id}")
        
except MammothJobTimeoutError as e:
    print(f"Job timed out after {e.details['timeout']} seconds")
    print(f"Job ID: {e.details['job_id']}")
    
except MammothJobFailedError as e:
    print(f"Job failed: {e.details['failure_reason']}")
    print(f"Job ID: {e.details['job_id']}")
```

### Multiple Job Management

```python
# Start multiple operations
file_paths = ["file1.csv", "file2.csv", "file3.csv"]
all_job_ids = []

for file_path in file_paths:
    job_ids = client.files.upload_files(
        workspace_id=1,
        project_id=1,
        files=file_path,
        wait_for_completion=False
    )
    all_job_ids.extend(job_ids)

print(f"Started {len(all_job_ids)} jobs")

# Get status of all jobs
jobs = client.jobs.get_jobs(all_job_ids)
for job in jobs:
    print(f"Job {job.id}: {job.status}")

# Wait for all jobs to complete
try:
    completed_jobs = client.jobs.wait_for_jobs(
        job_ids=all_job_ids,
        timeout=600  # 10 minutes
    )
    
    # Extract all dataset IDs
    dataset_ids = client.jobs.extract_dataset_ids(completed_jobs)
    successful_datasets = [ds_id for ds_id in dataset_ids if ds_id is not None]
    
    print(f"Successfully created {len(successful_datasets)} datasets:")
    for ds_id in successful_datasets:
        print(f"  - Dataset {ds_id}")
        
except MammothJobTimeoutError as e:
    print(f"Some jobs timed out")
    
except MammothJobFailedError as e:
    print(f"At least one job failed: {e.details['failure_reason']}")
```

### Job Response Analysis

```python
# Analyze job responses to understand what happened
def analyze_job_response(job: JobSchema):
    """Analyze a job response and extract useful information."""
    
    print(f"=== Job {job.id} Analysis ===")
    print(f"Operation: {job.operation}")
    print(f"Status: {job.status}")
    print(f"Path: {job.path}")
    print(f"Duration: {job.last_updated_at - job.created_at}")
    
    if job.response:
        print("Response data:")
        for key, value in job.response.items():
            print(f"  {key}: {value}")
    
    # Extract common response fields
    if job.status == JobStatus.SUCCESS:
        if 'ds_id' in job.response:
            print(f"✓ Created dataset: {job.response['ds_id']}")
        if 'file_id' in job.response:
            print(f"✓ Created file: {job.response['file_id']}")
    elif job.status in [JobStatus.FAILURE, JobStatus.ERROR]:
        if 'failure_reason' in job.response:
            print(f"✗ Failure reason: {job.response['failure_reason']}")
        if 'error_details' in job.response:
            print(f"✗ Error details: {job.response['error_details']}")
    
    print()

# Analyze completed jobs
for job in completed_jobs:
    analyze_job_response(job)
```

### Custom Job Monitoring

```python
import time
from mammoth.models.jobs import JobStatus

def monitor_jobs_with_progress(job_ids: List[int], check_interval: int = 10):
    """Monitor jobs with progress reporting."""
    
    remaining_jobs = set(job_ids)
    completed_jobs = []
    
    print(f"Monitoring {len(job_ids)} jobs...")
    
    while remaining_jobs:
        # Get status of remaining jobs
        jobs = client.jobs.get_jobs(list(remaining_jobs))
        
        newly_completed = []
        for job in jobs:
            if job.status in [JobStatus.SUCCESS, JobStatus.FAILURE, JobStatus.ERROR]:
                newly_completed.append(job)
                remaining_jobs.remove(job.id)
                completed_jobs.append(job)
        
        # Report progress
        if newly_completed:
            for job in newly_completed:
                status_icon = "✓" if job.status == JobStatus.SUCCESS else "✗"
                print(f"{status_icon} Job {job.id} completed with status: {job.status}")
        
        total_completed = len(completed_jobs)
        total_jobs = len(job_ids)
        progress_pct = (total_completed / total_jobs) * 100
        
        print(f"Progress: {total_completed}/{total_jobs} ({progress_pct:.1f}%) completed")
        
        if remaining_jobs:
            print(f"Waiting {check_interval}s before next check...")
            time.sleep(check_interval)
    
    print("All jobs completed!")
    return completed_jobs

# Use the custom monitor
completed_jobs = monitor_jobs_with_progress(all_job_ids, check_interval=5)
```

## Error Handling

The Jobs API integrates with the SDK's exception system:

```python
from mammoth.exceptions import MammothJobTimeoutError, MammothJobFailedError, MammothAPIError

try:
    job = client.jobs.get_job(invalid_job_id)
except MammothAPIError as e:
    print(f"API error: {e.message}")
    print(f"Status code: {e.status_code}")
    
try:
    completed_job = client.jobs.wait_for_job(job_id, timeout=60)
except MammothJobTimeoutError as e:
    print(f"Job {e.details['job_id']} timed out after {e.details['timeout']} seconds")
except MammothJobFailedError as e:
    print(f"Job {e.details['job_id']} failed: {e.details['failure_reason']}")
```
