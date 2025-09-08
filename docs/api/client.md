# MammothClient API Reference

The `MammothClient` is the main entry point for interacting with the Mammoth Analytics API.

## Class: MammothClient

```python
from mammoth import MammothClient
```

### Constructor

```python
MammothClient(
    api_key: str,
    api_secret: str,
    base_url: str = "https://api.mammoth.io",
    timeout: int = 30,
    max_retries: int = 3
)
```

**Parameters:**
- `api_key` (str): Your Mammoth API key
- `api_secret` (str): Your Mammoth API secret
- `base_url` (str, optional): Base URL for the Mammoth API. Defaults to "https://api.mammoth.io"
- `timeout` (int, optional): Request timeout in seconds. Defaults to 30
- `max_retries` (int, optional): Maximum number of retries for failed requests. Defaults to 3

**Example:**
```python
client = MammothClient(
    api_key="your-api-key",
    api_secret="your-api-secret",
    base_url="https://your-instance.mammoth.io",
    timeout=60,
    max_retries=5
)
```

### Properties

#### client.files
Access to the Files API for file management operations.

**Type:** `FilesAPI`

**Example:**
```python
files_list = client.files.list_files(workspace_id=1, project_id=1)
```

#### client.jobs
Access to the Jobs API for tracking asynchronous operations.

**Type:** `JobsAPI`

**Example:**
```python
job = client.jobs.get_job(job_id=123)
```

### Methods

#### test_connection()

Test the connection to the Mammoth API to verify authentication and connectivity.

**Returns:** `bool` - True if connection is successful, False otherwise

**Example:**
```python
if client.test_connection():
    print("✓ Connected successfully!")
else:
    print("✗ Connection failed")
```

**Usage Notes:**
- This method makes a lightweight API call to verify connectivity
- Returns False for authentication errors or network issues
- Useful for health checks and connection validation

### Context Manager Support

The `MammothClient` supports Python's context manager protocol for automatic resource cleanup:

```python
with MammothClient(api_key="key", api_secret="secret") as client:
    files_list = client.files.list_files(workspace_id=1, project_id=1)
    # Connection automatically closed when exiting context
```

**Benefits:**
- Automatic session cleanup
- Proper resource management
- Exception-safe connection handling

### Configuration Examples

#### Basic Configuration
```python
client = MammothClient(
    api_key="your-api-key",
    api_secret="your-api-secret"
)
```

#### Production Configuration
```python
client = MammothClient(
    api_key=os.getenv("MAMMOTH_API_KEY"),
    api_secret=os.getenv("MAMMOTH_API_SECRET"),
    base_url="https://api.mammoth.io",
    timeout=60,
    max_retries=5
)
```

#### Development Configuration
```python
client = MammothClient(
    api_key="dev-api-key",
    api_secret="dev-api-secret",
    base_url="https://dev-api.mammoth.io",
    timeout=30,
    max_retries=2
)
```

### Authentication Details

The client automatically handles authentication by adding the required headers to all requests:
- `X-API-KEY`: Your API key
- `X-API-SECRET`: Your API secret
- `User-Agent`: SDK identification string

### Request Handling

#### Automatic Retries
The client implements exponential backoff retry logic:
- Retries failed requests up to `max_retries` times
- Uses exponential backoff (2^attempt seconds between retries)
- Only retries for network errors, not authentication or client errors

#### Error Handling
The client raises specific exceptions for different error types:
- `MammothAuthError`: Authentication failures (401)
- `MammothAPIError`: General API errors (4xx, 5xx)
- Network errors are automatically retried

#### Request Timeouts
- All requests respect the configured timeout
- Timeout applies to the entire request/response cycle
- Adjust timeout based on expected operation duration

### Threading and Async Support

#### Thread Safety
The `MammothClient` is thread-safe and can be shared across multiple threads:

```python
import threading
from mammoth import MammothClient

client = MammothClient(api_key="key", api_secret="secret")

def worker(thread_id):
    files = client.files.list_files(workspace_id=1, project_id=1)
    print(f"Thread {thread_id}: Found {len(files.files)} files")

# Create multiple threads using the same client
threads = []
for i in range(5):
    t = threading.Thread(target=worker, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

#### Async Usage
While the client itself is synchronous, you can use it in async contexts:

```python
import asyncio
from mammoth import MammothClient

async def async_upload():
    client = MammothClient(api_key="key", api_secret="secret")
    
    # Run in executor to avoid blocking
    loop = asyncio.get_event_loop()
    dataset_id = await loop.run_in_executor(
        None,
        lambda: client.files.upload_files(
            workspace_id=1,
            project_id=1,
            files="data.csv"
        )
    )
    return dataset_id

# Usage
dataset_id = await async_upload()
```

### Best Practices

#### Connection Management
```python
# ✅ Good: Use context manager for automatic cleanup
with MammothClient(api_key="key", api_secret="secret") as client:
    result = client.files.list_files(workspace_id=1, project_id=1)

# ✅ Good: Reuse client instance
client = MammothClient(api_key="key", api_secret="secret")
files1 = client.files.list_files(workspace_id=1, project_id=1)
files2 = client.files.list_files(workspace_id=1, project_id=2)

# ❌ Avoid: Creating new client for each operation
for project_id in [1, 2, 3]:
    client = MammothClient(api_key="key", api_secret="secret")  # Inefficient
    files = client.files.list_files(workspace_id=1, project_id=project_id)
```

#### Error Handling
```python
from mammoth import MammothClient, MammothAPIError, MammothAuthError

client = MammothClient(api_key="key", api_secret="secret")

try:
    files = client.files.list_files(workspace_id=1, project_id=1)
except MammothAuthError:
    print("Check your API credentials")
except MammothAPIError as e:
    print(f"API error: {e.message}")
    if e.status_code == 404:
        print("Workspace or project not found")
```

#### Configuration Management
```python
import os
from mammoth import MammothClient

# ✅ Good: Use environment variables
client = MammothClient(
    api_key=os.getenv("MAMMOTH_API_KEY"),
    api_secret=os.getenv("MAMMOTH_API_SECRET"),
    base_url=os.getenv("MAMMOTH_BASE_URL", "https://api.mammoth.io")
)

# ✅ Good: Validate configuration
if not all([client.api_key, client.api_secret]):
    raise ValueError("API credentials are required")
```

## See Also

- [Files API Reference](files.md)
- [Jobs API Reference](jobs.md)
- [Exception Handling](exceptions.md)
- [Basic Usage Examples](../examples/basic-usage.md)
