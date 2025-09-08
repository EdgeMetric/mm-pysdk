# Jobs API Reference

The Jobs API tracks asynchronous operations and provides methods to monitor job progress and retrieve results.

## Class: JobsAPI

Access through the client: `client.jobs`

```python
jobs_api = client.jobs
```

## Methods

### get_job()

Get details of a specific job by its ID.

```python
get_job(job_id: int) -> JobSchema
```

**Parameters:**
- `job_id` (int): Unique identifier of the job

**Returns:** `JobSchema` - Job details including status and response

**Raises:**
- `MammothAPIError`: If the API request fails

**Example:**

```python
job = client.jobs.get_job(job_id=456)
print(f"Job Status: {job.status}")
print(f"Created: {job.created_at}")
print(f"Last Updated: {job.last_updated_at}")

if job.status == "success":
    print(f"Job completed successfully")
    if 'ds_id' in job.response:
        print(f"Dataset ID: {job.response['ds_id']}")
elif job.status == "failure":
    print(f"Job failed: {job.response.get('failure_reason', 'Unknown error')}")
```

### get_jobs()

Get details of multiple jobs by their IDs.

```python
get_jobs(job_ids: List[int]) -> List[JobSchema]
```

**Parameters:**
- `job_ids` (List[int]): List of job IDs to retrieve

**Returns:** `List[JobSchema]` - List of job details

**Raises:**
- `MammothAPIError`: If the API request fails

**Example:**

```python
jobs = client.jobs.get_jobs(job_ids=[456, 457, 458])

for job in jobs:
    print(f"Job {job.id}: {job.status}")
    if job.status == "success" and 'ds_id' in job.response:
        print(f"  Dataset ID: {job.response['ds_id']}")
```

### wait_for_job()

Wait for a job to complete, polling until success or failure.

```python
wait_for_job(
    job_id: int,
    timeout: int = 300,
    poll_interval: int = 5
) -> JobSchema
```

**Parameters:**
- `job_id` (int): ID of the job to wait for
- `timeout` (int): Maximum time to wait in seconds. Defaults to 300 (5 minutes)
- `poll_interval` (int): Time between polls in seconds. Defaults to 5

**Returns:** `JobSchema` - Final job details when completed

**Raises:**
- `MammothJobTimeoutError`: If job doesn't complete within timeout
- `MammothJobFailedError`: If job fails during execution

**Example:**

```python
try:
    completed_job = client.jobs.wait_for_job(
        job_id=456,
        timeout=600,  # 10 minutes
        poll_interval=10  # Check every 10 seconds
    )
    
    print(f"Job completed with status: {completed_job.status}")
    
    if 'ds_id' in completed_job.response:
        dataset_id = completed_job.response['ds_id']
        print(f"Dataset created: {dataset_id}")
        
except MammothJobTimeoutError as e:
    print(f"Job {e.details['job_id']} timed out after {e.details['timeout']} seconds")
except MammothJobFailedError as e:
    print(f"Job {e.details['job_id']} failed: {e.details['failure_reason']}")
```

### wait_for_jobs()

Wait for multiple jobs to complete.

```python
wait_for_jobs(
    job_ids: List[int],
    timeout: int = 300,
    poll_interval: int = 5
) -> List[JobSchema]
```

**Parameters:**
- `job_ids` (List[int]): List of job IDs to wait for
- `timeout` (int): Maximum time to wait in seconds. Defaults to 300
- `poll_interval` (int): Time between polls in seconds. Defaults to 5

**Returns:** `List[JobSchema]` - Final job details for all completed jobs

**Raises:**
- `MammothJobTimeoutError`: If any job doesn't complete within timeout
- `MammothJobFailedError`: If any job fails during execution

**Example:**

```python
try:
    completed_jobs = client.jobs.wait_for_jobs(
        job_ids=[456, 457, 458],
        timeout=900  # 15 minutes for multiple jobs
    )
    
    print(f"All {len(completed_jobs)} jobs completed successfully")
    
    for job in completed_jobs:
        if 'ds_id' in job.response:
            print(f"Job {job.id} -> Dataset {job.response['ds_id']}")
            
except MammothJobFailedError as e:
    print(f"Job {e.details['job_id']} failed")
```

### extract_dataset_ids()

Extract dataset IDs from completed job responses.

```python
extract_dataset_ids(jobs: List[JobSchema]) -> List[Optional[int]]
```

**Parameters:**
- `jobs` (List[JobSchema]): List of completed job schemas

**Returns:** `List[Optional[int]]` - List of dataset IDs (None if not found in response)

**Example:**

```python
# Wait for jobs and extract dataset IDs
completed_jobs = client.jobs.wait_for_jobs(job_ids=[456, 457, 458])
dataset_ids = client.jobs.extract_dataset_ids(completed_jobs)

print("Created datasets:")
for i, dataset_id in enumerate(dataset_ids):
    if dataset_id:
        print(f"  Job {completed_jobs[i].id} -> Dataset {dataset_id}")
    else:
        print(f"  Job {completed_jobs[i].id} -> No dataset created")
```

## Data Models

### JobSchema

Schema for a job object.

**Fields:**
- `id` (int): Unique identifier of the job
- `status` (JobStatus): Current status of the job
- `response` (Dict[str, Any]): Result of the asynchronous task
- `last_updated_at` (datetime): Timestamp of the most recent job status update
- `created_at` (datetime): Timestamp when the asynchronous task was created
- `path` (str): API request path associated with the job operation
- `operation` (str): Name of the asynchronous operation tracked by the job

### JobStatus

Enumeration of possible job statuses.

**Values:**
- `SUCCESS`: Job completed successfully
- `FAILURE`: Job failed with an error
- `PROCESSING`: Job is currently running
- `ERROR`: Job encountered an error

## Usage Patterns

### Basic Job Monitoring

```python
# Start an operation that returns a job ID
job_ids = client.files.upload_files(
    workspace_id=1,
    project_id=1,
    files="large_file.csv",
    wait_for_completion=False  # Don't wait automatically
)

if job_ids:
    job_id = job_ids[0]
    print(f"Upload started with job ID: {job_id}")
    
    # Monitor manually with custom intervals
    while True:
        job = client.jobs.get_job(job_id)
        print(f"Job status: {job.status}")
        
        if job.status == JobStatus.SUCCESS:
            dataset_id = job.response.get('ds_id')
            print(f"Upload completed! Dataset ID: {dataset_id}")
            break
        elif job.status in [JobStatus.FAILURE, JobStatus.ERROR]:
            error = job.response.get('failure_reason', 'Unknown error')
            print(f"Upload failed: {error}")
            break
        
        time.sleep(10)  # Wait 10 seconds before checking again
```

### Batch Job Processing

```python
import time
from mammoth.models.jobs import JobStatus

# Start multiple uploads
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

print(f"Started {len(all_job_ids)} upload jobs")

# Monitor all jobs with custom logic
completed_jobs = []
failed_jobs = []

while all_job_ids:
    jobs = client.jobs.get_jobs(all_job_ids)
    
    for job in jobs:
        if job.status == JobStatus.SUCCESS:
            completed_jobs.append(job)
            all_job_ids.remove(job.id)
            print(f"✓ Job {job.id} completed")
            
        elif job.status in [JobStatus.FAILURE, JobStatus.ERROR]:
            failed_jobs.append(job)
            all_job_ids.remove(job.id)
            print(f"✗ Job {job.id} failed")
    
    if all_job_ids:  # Still have pending jobs
        print(f"Waiting for {len(all_job_ids)} jobs...")
        time.sleep(15)

# Extract results
dataset_ids = client.jobs.extract_dataset_ids(completed_jobs)
print(f"Created {len(dataset_ids)} datasets: {dataset_ids}")

if failed_jobs:
    print(f"Failed jobs: {[job.id for job in failed_jobs]}")
```

### Error Recovery

```python
from mammoth.exceptions import MammothJobTimeoutError, MammothJobFailedError

def upload_with_retry(client, workspace_id, project_id, file_path, max_retries=3):
    """Upload file with automatic retry on failure."""
    
    for attempt in range(max_retries):
        try:
            print(f"Upload attempt {attempt + 1} for {file_path}")
            
            # Start upload
            job_ids = client.files.upload_files(
                workspace_id=workspace_id,
                project_id=project_id,
                files=file_path,
                wait_for_completion=False
            )
            
            if not job_ids:
                print("No job started")
                continue
                
            job_id = job_ids[0]
            
            # Wait with shorter timeout for retry logic
            try:
                completed_job = client.jobs.wait_for_job(
                    job_id=job_id,
                    timeout=300  # 5 minutes
                )
                
                dataset_id = completed_job.response.get('ds_id')
                print(f"✓ Upload successful! Dataset ID: {dataset_id}")
                return dataset_id
                
            except MammothJobTimeoutError:
                print(f"Job {job_id} timed out, will retry...")
                continue
                
            except MammothJobFailedError as e:
                failure_reason = e.details.get('failure_reason', 'Unknown')
                print(f"Job {job_id} failed: {failure_reason}")
                
                # Don't retry for certain errors
                if 'authentication' in failure_reason.lower():
                    print("Authentication error - not retrying")
                    raise
                
                print("Will retry...")
                continue
                
        except Exception as e:
            print(f"Upload attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                print("Max retries exceeded")
                raise
            
    return None

# Usage
dataset_id = upload_with_retry(
    client=client,
    workspace_id=1,
    project_id=1,
    file_path="problematic_file.csv"
)
```

### Job Result Processing

```python
def process_upload_results(client, job_ids):
    """Process multiple upload job results and categorize outcomes."""
    
    # Wait for all jobs to complete
    try:
        completed_jobs = client.jobs.wait_for_jobs(job_ids, timeout=600)
    except (MammothJobTimeoutError, MammothJobFailedError):
        # Some jobs failed or timed out, get current status
        completed_jobs = client.jobs.get_jobs(job_ids)
    
    # Categorize results
    successful_datasets = []
    failed_jobs = []
    timeout_jobs = []
    
    for job in completed_jobs:
        if job.status == JobStatus.SUCCESS:
            dataset_id = job.response.get('ds_id')
            if dataset_id:
                successful_datasets.append(dataset_id)
        elif job.status == JobStatus.PROCESSING:
            timeout_jobs.append(job.id)
        else:
            failed_jobs.append({
                'job_id': job.id,
                'error': job.response.get('failure_reason', 'Unknown error')
            })
    
    return {
        'successful_datasets': successful_datasets,
        'failed_jobs': failed_jobs,
        'timeout_jobs': timeout_jobs
    }

# Usage
job_ids = [456, 457, 458]  # From upload operations
results = process_upload_results(client, job_ids)

print(f"Successful: {len(results['successful_datasets'])} datasets")
print(f"Failed: {len(results['failed_jobs'])} jobs")
print(f"Timed out: {len(results['timeout_jobs'])} jobs")
```

## Best Practices

### Efficient Polling

```python
# ✅ Good: Use appropriate poll intervals
completed_job = client.jobs.wait_for_job(
    job_id=job_id,
    timeout=600,
    poll_interval=10  # Check every 10 seconds for long-running jobs
)

# ❌ Avoid: Too frequent polling (wastes resources)
completed_job = client.jobs.wait_for_job(
    job_id=job_id,
    poll_interval=1  # Every second is too frequent
)
```

### Timeout Management

```python
# ✅ Good: Set appropriate timeouts based on operation
if file_size_mb < 10:
    timeout = 300  # 5 minutes for small files
elif file_size_mb < 100:
    timeout = 900  # 15 minutes for medium files
else:
    timeout = 1800  # 30 minutes for large files

completed_job = client.jobs.wait_for_job(job_id=job_id, timeout=timeout)
```

### Error Handling

```python
# ✅ Good: Handle specific job errors
try:
    completed_job = client.jobs.wait_for_job(job_id=job_id)
except MammothJobTimeoutError as e:
    print(f"Job {e.details['job_id']} is taking longer than expected")
    # Could continue monitoring or cancel
except MammothJobFailedError as e:
    error_reason = e.details.get('failure_reason', 'Unknown')
    print(f"Job failed: {error_reason}")
    # Handle specific error types
```

## See Also

- [Files API Reference](files.md) - Operations that create jobs
- [Exception Handling](exceptions.md) - Job-related exceptions
- [Job Management Examples](../examples/job-management.md) - Detailed examples
- [Best Practices](../examples/best-practices.md) - Recommended patterns
