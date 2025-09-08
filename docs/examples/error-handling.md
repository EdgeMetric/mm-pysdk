# Error Handling Guide

The Mammoth SDK provides comprehensive error handling with specific exception types to help you build robust applications.

## Exception Hierarchy

```python
MammothError                    # Base exception
├── MammothAPIError            # General API errors
│   └── MammothAuthError       # Authentication failures
├── MammothJobTimeoutError     # Job timeout errors
└── MammothJobFailedError      # Job failure errors
```

## Exception Types

### MammothError (Base Exception)

Base class for all Mammoth SDK exceptions.

```python
from mammoth.exceptions import MammothError

try:
    # SDK operation
    pass
except MammothError as e:
    print(f"Mammoth error: {e.message}")
    print(f"Details: {e.details}")
```

**Attributes:**
- `message` (str): Human-readable error message
- `details` (dict): Additional error details

### MammothAPIError

Raised for API-related errors (HTTP 4xx, 5xx responses).

```python
from mammoth.exceptions import MammothAPIError

try:
    files = client.files.list_files(workspace_id=999, project_id=999)
except MammothAPIError as e:
    print(f"API Error: {e.message}")
    print(f"Status Code: {e.status_code}")
    print(f"Response: {e.response_body}")
    
    # Handle specific status codes
    if e.status_code == 404:
        print("Workspace or project not found")
    elif e.status_code == 400:
        print("Invalid request parameters")
    elif e.status_code >= 500:
        print("Server error - try again later")
```

**Attributes:**
- `message` (str): Error description
- `status_code` (int): HTTP status code
- `response_body` (dict): Full API response
- `details` (dict): Additional error details

### MammothAuthError

Raised for authentication failures (HTTP 401).

```python
from mammoth.exceptions import MammothAuthError

try:
    client = MammothClient(api_key="invalid", api_secret="invalid")
    files = client.files.list_files(workspace_id=1, project_id=1)
except MammothAuthError:
    print("Authentication failed - check your API credentials")
    print("Verify your API key and secret are correct")
```

### MammothJobTimeoutError

Raised when a job doesn't complete within the specified timeout.

```python
from mammoth.exceptions import MammothJobTimeoutError

try:
    dataset_id = client.files.upload_files(
        workspace_id=1,
        project_id=1,
        files="large_file.csv",
        timeout=60  # Short timeout for demo
    )
except MammothJobTimeoutError as e:
    job_id = e.details['job_id']
    timeout = e.details['timeout']
    print(f"Job {job_id} timed out after {timeout} seconds")
    print("The file may still be processing - check status later")
    
    # Optionally continue monitoring
    job = client.jobs.get_job(job_id)
    print(f"Current job status: {job.status}")
```

**Details:**
- `job_id` (int): ID of the timed-out job
- `timeout` (int): Timeout value in seconds

### MammothJobFailedError

Raised when a job fails during processing.

```python
from mammoth.exceptions import MammothJobFailedError

try:
    dataset_id = client.files.upload_files(
        workspace_id=1,
        project_id=1,
        files="corrupted_file.csv"
    )
except MammothJobFailedError as e:
    job_id = e.details['job_id']
    failure_reason = e.details.get('failure_reason', 'Unknown error')
    print(f"Job {job_id} failed: {failure_reason}")
    
    # Handle specific failure types
    if 'format' in failure_reason.lower():
        print("File format issue - check file structure")
    elif 'permission' in failure_reason.lower():
        print("Permission issue - check access rights")
```

**Details:**
- `job_id` (int): ID of the failed job
- `failure_reason` (str): Reason for failure

## Common Error Handling Patterns

### Basic Exception Handling

```python
from mammoth import MammothClient
from mammoth.exceptions import MammothAPIError, MammothAuthError

def safe_file_upload(client, workspace_id, project_id, file_path):
    """Upload file with basic error handling."""
    try:
        dataset_id = client.files.upload_files(
            workspace_id=workspace_id,
            project_id=project_id,
            files=file_path
        )
        print(f"✓ Upload successful: Dataset {dataset_id}")
        return dataset_id
        
    except MammothAuthError:
        print("✗ Authentication failed - check credentials")
        return None
        
    except MammothAPIError as e:
        print(f"✗ API Error: {e.message}")
        if e.status_code == 404:
            print("  Workspace or project not found")
        elif e.status_code == 400:
            print("  Invalid request - check parameters")
        return None
        
    except FileNotFoundError:
        print(f"✗ File not found: {file_path}")
        return None
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return None
```

### Comprehensive Job Error Handling

```python
from mammoth.exceptions import (
    MammothJobTimeoutError, 
    MammothJobFailedError,
    MammothAPIError
)

def robust_file_upload(client, workspace_id, project_id, file_path, max_timeout=1800):
    """Upload file with comprehensive error handling."""
    try:
        print(f"Starting upload: {file_path}")
        
        dataset_id = client.files.upload_files(
            workspace_id=workspace_id,
            project_id=project_id,
            files=file_path,
            timeout=max_timeout
        )
        
        print(f"✓ Upload completed: Dataset {dataset_id}")
        return {"success": True, "dataset_id": dataset_id}
        
    except MammothJobTimeoutError as e:
        job_id = e.details['job_id']
        timeout = e.details['timeout']
        
        print(f"⚠ Upload timed out after {timeout} seconds")
        print(f"Job ID: {job_id} - may still be processing")
        
        # Check current job status
        try:
            job = client.jobs.get_job(job_id)
            return {
                "success": False,
                "error": "timeout",
                "job_id": job_id,
                "status": job.status
            }
        except Exception:
            return {"success": False, "error": "timeout", "job_id": job_id}
            
    except MammothJobFailedError as e:
        job_id = e.details['job_id']
        failure_reason = e.details.get('failure_reason', 'Unknown error')
        
        print(f"✗ Upload failed: {failure_reason}")
        
        return {
            "success": False,
            "error": "job_failed",
            "job_id": job_id,
            "reason": failure_reason
        }
        
    except MammothAPIError as e:
        print(f"✗ API Error ({e.status_code}): {e.message}")
        
        return {
            "success": False,
            "error": "api_error",
            "status_code": e.status_code,
            "message": e.message
        }
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        
        return {
            "success": False,
            "error": "unexpected",
            "message": str(e)
        }
```

### Retry Logic with Exponential Backoff

```python
import time
import random
from mammoth.exceptions import MammothAPIError, MammothJobFailedError

def upload_with_retry(client, workspace_id, project_id, file_path, max_retries=3):
    """Upload with automatic retry and exponential backoff."""
    
    for attempt in range(max_retries):
        try:
            print(f"Upload attempt {attempt + 1}/{max_retries}")
            
            dataset_id = client.files.upload_files(
                workspace_id=workspace_id,
                project_id=project_id,
                files=file_path,
                timeout=600
            )
            
            print(f"✓ Upload successful on attempt {attempt + 1}")
            return dataset_id
            
        except MammothJobFailedError as e:
            failure_reason = e.details.get('failure_reason', '')
            
            # Don't retry for certain errors
            non_retryable_errors = [
                'authentication',
                'permission',
                'file format',
                'invalid file'
            ]
            
            if any(error in failure_reason.lower() for error in non_retryable_errors):
                print(f"✗ Non-retryable error: {failure_reason}")
                raise
            
            print(f"⚠ Attempt {attempt + 1} failed: {failure_reason}")
            
        except MammothAPIError as e:
            # Don't retry client errors (4xx)
            if 400 <= e.status_code < 500:
                print(f"✗ Client error ({e.status_code}): {e.message}")
                raise
            
            print(f"⚠ Server error ({e.status_code}): {e.message}")
            
        except Exception as e:
            print(f"⚠ Unexpected error: {e}")
        
        # Calculate backoff delay
        if attempt < max_retries - 1:
            delay = (2 ** attempt) + random.uniform(0, 1)
            print(f"Retrying in {delay:.1f} seconds...")
            time.sleep(delay)
    
    print(f"✗ Upload failed after {max_retries} attempts")
    return None
```

### Connection and Network Error Handling

```python
import requests
from mammoth.exceptions import MammothAPIError

def test_connection_with_diagnostics(client):
    """Test connection with detailed diagnostics."""
    try:
        if client.test_connection():
            print("✓ Connection successful")
            return True
        else:
            print("✗ Connection test failed")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Network connection error")
        print("  Check your internet connection")
        print("  Verify the base URL is correct")
        return False
        
    except requests.exceptions.Timeout:
        print("✗ Connection timeout")
        print("  The server may be slow or unreachable")
        print("  Try increasing the timeout value")
        return False
        
    except requests.exceptions.SSLError:
        print("✗ SSL certificate error")
        print("  Check your SSL configuration")
        return False
        
    except MammothAPIError as e:
        print(f"✗ API Error: {e.message}")
        if e.status_code == 401:
            print("  Check your API credentials")
        elif e.status_code == 403:
            print("  Check your access permissions")
        return False
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
```

## Error Recovery Strategies

### Graceful Degradation

```python
def get_files_with_fallback(client, workspace_id, project_id):
    """Get files with fallback options."""
    try:
        # Try to get full file details
        files = client.files.list_files(
            workspace_id=workspace_id,
            project_id=project_id,
            fields="__full",
            limit=100
        )
        print(f"✓ Retrieved {len(files.files)} files with full details")
        return files.files
        
    except MammothAPIError as e:
        if e.status_code == 413:  # Request too large
            print("⚠ Request too large, falling back to basic fields")
            try:
                files = client.files.list_files(
                    workspace_id=workspace_id,
                    project_id=project_id,
                    fields="__standard",
                    limit=50
                )
                print(f"✓ Retrieved {len(files.files)} files with basic details")
                return files.files
            except Exception:
                pass
        
        print(f"✗ Could not retrieve files: {e.message}")
        return []
```

### Circuit Breaker Pattern

```python
import time
from collections import defaultdict

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = defaultdict(int)
        self.last_failure_time = defaultdict(float)
        
    def call(self, func, operation_key, *args, **kwargs):
        """Call function with circuit breaker protection."""
        current_time = time.time()
        
        # Check if circuit is open
        if (self.failure_count[operation_key] >= self.failure_threshold and
            current_time - self.last_failure_time[operation_key] < self.recovery_timeout):
            raise Exception(f"Circuit breaker open for {operation_key}")
        
        try:
            result = func(*args, **kwargs)
            # Reset failure count on success
            self.failure_count[operation_key] = 0
            return result
            
        except Exception as e:
            self.failure_count[operation_key] += 1
            self.last_failure_time[operation_key] = current_time
            raise

# Usage
circuit_breaker = CircuitBreaker()

def safe_upload(client, workspace_id, project_id, file_path):
    try:
        return circuit_breaker.call(
            client.files.upload_files,
            "file_upload",
            workspace_id=workspace_id,
            project_id=project_id,
            files=file_path
        )
    except Exception as e:
        print(f"Upload failed or circuit breaker open: {e}")
        return None
```

## Logging and Debugging

### Structured Logging

```python
import logging
from mammoth.exceptions import MammothAPIError, MammothJobFailedError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mammoth_client')

def upload_with_logging(client, workspace_id, project_id, file_path):
    """Upload with comprehensive logging."""
    logger.info(f"Starting upload: {file_path}")
    logger.debug(f"Workspace: {workspace_id}, Project: {project_id}")
    
    try:
        dataset_id = client.files.upload_files(
            workspace_id=workspace_id,
            project_id=project_id,
            files=file_path
        )
        
        logger.info(f"Upload successful: Dataset {dataset_id}")
        return dataset_id
        
    except MammothJobFailedError as e:
        logger.error(f"Job failed: {e.details.get('failure_reason')}")
        logger.debug(f"Job ID: {e.details.get('job_id')}")
        raise
        
    except MammothAPIError as e:
        logger.error(f"API Error ({e.status_code}): {e.message}")
        logger.debug(f"Response body: {e.response_body}")
        raise
        
    except Exception as e:
        logger.exception(f"Unexpected error during upload: {e}")
        raise
```

### Debug Information

```python
def debug_api_call(client, operation_func, *args, **kwargs):
    """Wrapper to debug API calls."""
    import traceback
    import json
    
    print(f"=== DEBUG: API Call ===")
    print(f"Function: {operation_func.__name__}")
    print(f"Args: {args}")
    print(f"Kwargs: {json.dumps(kwargs, indent=2, default=str)}")
    
    try:
        result = operation_func(*args, **kwargs)
        print(f"✓ Success")
        print(f"Result type: {type(result)}")
        return result
        
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}")
        print(f"Message: {e}")
        if hasattr(e, 'status_code'):
            print(f"Status Code: {e.status_code}")
        if hasattr(e, 'response_body'):
            print(f"Response: {json.dumps(e.response_body, indent=2)}")
        print(f"Traceback:")
        traceback.print_exc()
        raise

# Usage
try:
    files = debug_api_call(
        client,
        client.files.list_files,
        workspace_id=1,
        project_id=1
    )
except Exception:
    print("API call failed - see debug info above")
```

## Best Practices

### 1. Always Handle Specific Exceptions

```python
# ✅ Good: Handle specific exceptions
try:
    dataset_id = client.files.upload_files(...)
except MammothAuthError:
    # Handle authentication error
    pass
except MammothJobFailedError as e:
    # Handle job failure
    pass
except MammothAPIError as e:
    # Handle other API errors
    pass

# ❌ Avoid: Catching all exceptions
try:
    dataset_id = client.files.upload_files(...)
except Exception:
    # Too broad - can't handle appropriately
    pass
```

### 2. Provide Meaningful Error Messages

```python
# ✅ Good: Descriptive error handling
try:
    files = client.files.list_files(workspace_id=ws_id, project_id=proj_id)
except MammothAPIError as e:
    if e.status_code == 404:
        raise ValueError(f"Workspace {ws_id} or project {proj_id} not found")
    elif e.status_code == 403:
        raise PermissionError(f"No access to workspace {ws_id}")
    else:
        raise RuntimeError(f"Failed to list files: {e.message}")
```

### 3. Log Errors for Debugging

```python
# ✅ Good: Log errors with context
import logging
logger = logging.getLogger(__name__)

try:
    dataset_id = client.files.upload_files(...)
except MammothJobFailedError as e:
    logger.error(
        "File upload failed",
        extra={
            "job_id": e.details.get('job_id'),
            "failure_reason": e.details.get('failure_reason'),
            "file_path": file_path,
            "workspace_id": workspace_id,
            "project_id": project_id
        }
    )
    raise
```

### 4. Implement Retry Logic Appropriately

```python
# ✅ Good: Retry with exponential backoff
retryable_errors = [MammothJobTimeoutError, ConnectionError]

for attempt in range(max_retries):
    try:
        return client.files.upload_files(...)
    except tuple(retryable_errors):
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)
        else:
            raise
    except MammothAuthError:
        # Don't retry authentication errors
        raise
```

## See Also

- [Basic Usage Examples](basic-usage.md) - Simple error handling examples
- [API Reference](../api/exceptions.md) - Complete exception documentation
- [Best Practices](best-practices.md) - Recommended patterns
- [Troubleshooting](../advanced/troubleshooting.md) - Common issues and solutions
