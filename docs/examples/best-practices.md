# Best Practices Guide

This guide provides recommended patterns and best practices for using the Mammoth Python SDK effectively and efficiently.

## Client Configuration

### Environment-Based Configuration

```python
import os
from mammoth import MammothClient

# ✅ Good: Use environment variables for configuration
def create_mammoth_client():
    """Create a properly configured Mammoth client."""
    return MammothClient(
        api_key=os.getenv("MAMMOTH_API_KEY"),
        api_secret=os.getenv("MAMMOTH_API_SECRET"),
        base_url=os.getenv("MAMMOTH_BASE_URL", "https://api.mammoth.io"),
        timeout=int(os.getenv("MAMMOTH_TIMEOUT", "60")),
        max_retries=int(os.getenv("MAMMOTH_MAX_RETRIES", "3"))
    )

# ❌ Avoid: Hardcoding credentials
client = MammothClient(
    api_key="pk_live_12345",  # Never hardcode!
    api_secret="sk_live_67890"
)
```

### Configuration Management

```python
# config.py
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class MammothConfig:
    api_key: str
    api_secret: str
    base_url: str = "https://api.mammoth.io"
    timeout: int = 60
    max_retries: int = 3
    
    @classmethod
    def from_env(cls) -> 'MammothConfig':
        """Load configuration from environment variables."""
        api_key = os.getenv("MAMMOTH_API_KEY")
        api_secret = os.getenv("MAMMOTH_API_SECRET")
        
        if not api_key or not api_secret:
            raise ValueError("MAMMOTH_API_KEY and MAMMOTH_API_SECRET must be set")
        
        return cls(
            api_key=api_key,
            api_secret=api_secret,
            base_url=os.getenv("MAMMOTH_BASE_URL", cls.base_url),
            timeout=int(os.getenv("MAMMOTH_TIMEOUT", str(cls.timeout))),
            max_retries=int(os.getenv("MAMMOTH_MAX_RETRIES", str(cls.max_retries)))
        )
    
    def create_client(self) -> MammothClient:
        """Create a client with this configuration."""
        return MammothClient(
            api_key=self.api_key,
            api_secret=self.api_secret,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries
        )

# Usage
config = MammothConfig.from_env()
client = config.create_client()
```

### Client Lifecycle Management

```python
# ✅ Good: Use context manager for automatic cleanup
with MammothClient.from_env() as client:
    files = client.files.list_files(workspace_id=1, project_id=1)
    # Connection automatically closed

# ✅ Good: Reuse client instance
client = MammothClient.from_env()
try:
    # Multiple operations with same client
    files1 = client.files.list_files(workspace_id=1, project_id=1)
    files2 = client.files.list_files(workspace_id=1, project_id=2)
    upload_result = client.files.upload_files(
        workspace_id=1, project_id=1, files="data.csv"
    )
finally:
    # Manual cleanup if not using context manager
    if hasattr(client, 'session'):
        client.session.close()

# ❌ Avoid: Creating new client for each operation
for project_id in [1, 2, 3]:
    client = MammothClient.from_env()  # Inefficient
    files = client.files.list_files(workspace_id=1, project_id=project_id)
```

## File Upload Best Practices

### Efficient File Upload Patterns

```python
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def batch_upload_files(
    client: MammothClient,
    workspace_id: int,
    project_id: int,
    file_paths: List[str],
    batch_size: int = 5,
    timeout_per_file: int = 600
) -> Dict[str, Any]:
    """Upload files in batches for better performance."""
    
    results = {
        "successful": [],
        "failed": [],
        "dataset_ids": []
    }
    
    # Process files in batches
    for i in range(0, len(file_paths), batch_size):
        batch = file_paths[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} files")
        
        try:
            # Upload batch
            dataset_ids = client.files.upload_files(
                workspace_id=workspace_id,
                project_id=project_id,
                files=batch,
                timeout=timeout_per_file * len(batch),
                wait_for_completion=True
            )
            
            # Record successes
            for j, file_path in enumerate(batch):
                results["successful"].append(file_path)
                if j < len(dataset_ids):
                    results["dataset_ids"].append(dataset_ids[j])
                    
        except Exception as e:
            logger.error(f"Batch upload failed: {e}")
            # Try individual uploads for failed batch
            for file_path in batch:
                try:
                    dataset_id = client.files.upload_files(
                        workspace_id=workspace_id,
                        project_id=project_id,
                        files=file_path,
                        timeout=timeout_per_file
                    )
                    results["successful"].append(file_path)
                    results["dataset_ids"].append(dataset_id)
                except Exception as individual_error:
                    logger.error(f"Individual upload failed for {file_path}: {individual_error}")
                    results["failed"].append({
                        "file": file_path,
                        "error": str(individual_error)
                    })
    
    return results
```

### File Validation

```python
from pathlib import Path
from typing import List, Tuple
import mimetypes

def validate_files_for_upload(file_paths: List[str]) -> Tuple[List[str], List[str]]:
    """Validate files before upload."""
    valid_files = []
    invalid_files = []
    
    # Supported file types
    supported_types = {
        '.csv', '.xlsx', '.xls', '.json', '.txt'
    }
    
    for file_path in file_paths:
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            invalid_files.append(f"{file_path}: File not found")
            continue
        
        # Check if it's a file (not directory)
        if not path.is_file():
            invalid_files.append(f"{file_path}: Not a file")
            continue
        
        # Check file extension
        if path.suffix.lower() not in supported_types:
            invalid_files.append(f"{file_path}: Unsupported file type")
            continue
        
        # Check file size (e.g., max 500MB)
        max_size = 500 * 1024 * 1024  # 500MB
        if path.stat().st_size > max_size:
            invalid_files.append(f"{file_path}: File too large (>{max_size//1024//1024}MB)")
            continue
        
        # Check if file is readable
        try:
            with open(path, 'rb') as f:
                f.read(1024)  # Try reading first 1KB
            valid_files.append(file_path)
        except Exception as e:
            invalid_files.append(f"{file_path}: Cannot read file ({e})")
    
    return valid_files, invalid_files

# Usage
valid_files, invalid_files = validate_files_for_upload(file_paths)

if invalid_files:
    print("Invalid files found:")
    for error in invalid_files:
        print(f"  ✗ {error}")

if valid_files:
    print(f"Uploading {len(valid_files)} valid files...")
    results = batch_upload_files(client, workspace_id, project_id, valid_files)
```

### Progress Tracking

```python
from typing import Callable, Optional
import time

def upload_with_progress(
    client: MammothClient,
    workspace_id: int,
    project_id: int,
    file_paths: List[str],
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> List[int]:
    """Upload files with progress tracking."""
    
    dataset_ids = []
    
    for i, file_path in enumerate(file_paths):
        if progress_callback:
            progress_callback(i, len(file_paths), f"Uploading {Path(file_path).name}")
        
        try:
            # Upload without waiting for completion
            job_ids = client.files.upload_files(
                workspace_id=workspace_id,
                project_id=project_id,
                files=file_path,
                wait_for_completion=False
            )
            
            if job_ids:
                job_id = job_ids[0]
                
                # Monitor job with progress updates
                while True:
                    job = client.jobs.get_job(job_id)
                    
                    if progress_callback:
                        progress_callback(
                            i, len(file_paths), 
                            f"Processing {Path(file_path).name} ({job.status})"
                        )
                    
                    if job.status == "success":
                        dataset_id = job.response.get('ds_id')
                        if dataset_id:
                            dataset_ids.append(dataset_id)
                        break
                    elif job.status in ["failure", "error"]:
                        logger.error(f"Upload failed for {file_path}")
                        break
                    
                    time.sleep(5)  # Wait before next check
                    
        except Exception as e:
            logger.error(f"Upload error for {file_path}: {e}")
    
    if progress_callback:
        progress_callback(len(file_paths), len(file_paths), "Upload complete")
    
    return dataset_ids

# Usage with simple progress callback
def simple_progress(current: int, total: int, message: str):
    percent = (current / total) * 100 if total > 0 else 0
    print(f"Progress: {percent:.1f}% - {message}")

dataset_ids = upload_with_progress(
    client, workspace_id, project_id, file_paths, simple_progress
)
```

## Error Handling Strategies

### Robust Error Handling Pattern

```python
from mammoth.exceptions import (
    MammothAPIError, MammothAuthError, 
    MammothJobTimeoutError, MammothJobFailedError
)
import logging
from typing import Optional, Dict, Any
import time
import random

class MammothOperationError(Exception):
    """Custom exception for operation failures."""
    pass

def robust_operation(
    operation_func: Callable,
    operation_name: str,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    *args, **kwargs
) -> Any:
    """Execute operation with robust error handling and retry logic."""
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting {operation_name} (attempt {attempt + 1}/{max_retries})")
            return operation_func(*args, **kwargs)
            
        except MammothAuthError as e:
            # Don't retry authentication errors
            logger.error(f"Authentication failed for {operation_name}")
            raise MammothOperationError(f"Authentication failed: {e.message}")
            
        except MammothJobFailedError as e:
            failure_reason = e.details.get('failure_reason', 'Unknown')
            
            # Check if error is retryable
            non_retryable_patterns = [
                'file format', 'invalid file', 'permission denied',
                'malformed', 'corrupted', 'unsupported'
            ]
            
            if any(pattern in failure_reason.lower() for pattern in non_retryable_patterns):
                logger.error(f"Non-retryable error for {operation_name}: {failure_reason}")
                raise MammothOperationError(f"Operation failed: {failure_reason}")
            
            logger.warning(f"Retryable job failure for {operation_name}: {failure_reason}")
            
        except MammothJobTimeoutError as e:
            logger.warning(f"Timeout for {operation_name} (job {e.details['job_id']})")
            
        except MammothAPIError as e:
            # Don't retry client errors (4xx)
            if 400 <= e.status_code < 500:
                logger.error(f"Client error for {operation_name}: {e.message}")
                raise MammothOperationError(f"Client error: {e.message}")
            
            logger.warning(f"Server error for {operation_name}: {e.message}")
            
        except Exception as e:
            logger.error(f"Unexpected error for {operation_name}: {e}")
            if attempt == max_retries - 1:
                raise MammothOperationError(f"Operation failed after {max_retries} attempts: {e}")
        
        # Calculate delay with exponential backoff and jitter
        if attempt < max_retries - 1:
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)  # 10% jitter
            total_delay = delay + jitter
            
            logger.info(f"Retrying {operation_name} in {total_delay:.1f} seconds...")
            time.sleep(total_delay)
    
    raise MammothOperationError(f"{operation_name} failed after {max_retries} attempts")

# Usage
try:
    dataset_id = robust_operation(
        client.files.upload_files,
        "file upload",
        max_retries=3,
        workspace_id=workspace_id,
        project_id=project_id,
        files="data.csv"
    )
    print(f"✓ Upload successful: {dataset_id}")
except MammothOperationError as e:
    print(f"✗ Operation failed: {e}")
```

### Graceful Degradation

```python
def get_files_with_fallback(
    client: MammothClient,
    workspace_id: int,
    project_id: int,
    preferred_fields: str = "__full"
) -> List[FileSchema]:
    """Get files with graceful degradation on failures."""
    
    # Try different field levels in order of preference
    field_options = [preferred_fields, "__standard", "__min", None]
    
    for fields in field_options:
        try:
            files_list = client.files.list_files(
                workspace_id=workspace_id,
                project_id=project_id,
                fields=fields,
                limit=100
            )
            
            logger.info(f"Retrieved {len(files_list.files)} files with fields: {fields}")
            return files_list.files
            
        except MammothAPIError as e:
            if e.status_code == 413:  # Request too large
                logger.warning(f"Request too large with fields '{fields}', trying simpler fields")
                continue
            elif e.status_code == 400:  # Bad request
                logger.warning(f"Invalid fields '{fields}', trying simpler fields")
                continue
            else:
                logger.error(f"API error with fields '{fields}': {e.message}")
                if fields == field_options[-1]:  # Last option
                    raise
                continue
        except Exception as e:
            logger.error(f"Unexpected error with fields '{fields}': {e}")
            if fields == field_options[-1]:  # Last option
                raise
            continue
    
    # This should not be reached, but just in case
    return []
```

## Performance Optimization

### Connection Pooling and Reuse

```python
from threading import Lock
from typing import Dict, Optional
import threading

class MammothClientPool:
    """Thread-safe client pool for connection reuse."""
    
    def __init__(self, config: MammothConfig, max_clients: int = 5):
        self.config = config
        self.max_clients = max_clients
        self._clients: Dict[int, MammothClient] = {}
        self._lock = Lock()
    
    def get_client(self) -> MammothClient:
        """Get a client for the current thread."""
        thread_id = threading.get_ident()
        
        with self._lock:
            if thread_id not in self._clients:
                if len(self._clients) >= self.max_clients:
                    # Reuse existing client
                    client = next(iter(self._clients.values()))
                else:
                    # Create new client
                    client = self.config.create_client()
                
                self._clients[thread_id] = client
            
            return self._clients[thread_id]
    
    def close_all(self):
        """Close all clients in the pool."""
        with self._lock:
            for client in self._clients.values():
                if hasattr(client, 'session'):
                    client.session.close()
            self._clients.clear()

# Usage
config = MammothConfig.from_env()
client_pool = MammothClientPool(config)

def worker_function(file_path: str):
    client = client_pool.get_client()
    return client.files.upload_files(
        workspace_id=1, project_id=1, files=file_path
    )

# Use in thread pool
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(worker_function, file_path)
        for file_path in file_paths
    ]
    
    results = [future.result() for future in futures]

# Clean up
client_pool.close_all()
```

### Efficient Pagination

```python
def get_all_files(
    client: MammothClient,
    workspace_id: int,
    project_id: int,
    batch_size: int = 100
) -> List[FileSchema]:
    """Efficiently retrieve all files using pagination."""
    
    all_files = []
    offset = 0
    
    while True:
        files_list = client.files.list_files(
            workspace_id=workspace_id,
            project_id=project_id,
            limit=batch_size,
            offset=offset,
            fields="__standard"  # Faster than __full
        )
        
        all_files.extend(files_list.files)
        
        # Check if we got fewer files than requested (last page)
        if len(files_list.files) < batch_size:
            break
        
        offset += batch_size
        
        # Optional: Add small delay to avoid overwhelming the API
        time.sleep(0.1)
    
    logger.info(f"Retrieved {len(all_files)} files total")
    return all_files
```

### Caching Strategies

```python
from functools import lru_cache
from datetime import datetime, timedelta
import threading

class CachedMammothClient:
    """Client wrapper with caching for expensive operations."""
    
    def __init__(self, client: MammothClient, cache_ttl: int = 300):
        self.client = client
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Dict] = {}
        self._cache_lock = Lock()
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid."""
        if key not in self._cache:
            return False
        
        cache_time = self._cache[key]['timestamp']
        return datetime.now() - cache_time < timedelta(seconds=self.cache_ttl)
    
    def list_files_cached(self, workspace_id: int, project_id: int, **kwargs) -> FilesList:
        """List files with caching."""
        cache_key = f"files_{workspace_id}_{project_id}_{hash(frozenset(kwargs.items()))}"
        
        with self._cache_lock:
            if self._is_cache_valid(cache_key):
                logger.debug(f"Cache hit for {cache_key}")
                return self._cache[cache_key]['data']
        
        # Cache miss - fetch from API
        files_list = self.client.files.list_files(
            workspace_id=workspace_id,
            project_id=project_id,
            **kwargs
        )
        
        with self._cache_lock:
            self._cache[cache_key] = {
                'data': files_list,
                'timestamp': datetime.now()
            }
        
        logger.debug(f"Cache updated for {cache_key}")
        return files_list
    
    def invalidate_cache(self, pattern: Optional[str] = None):
        """Invalidate cache entries."""
        with self._cache_lock:
            if pattern:
                keys_to_remove = [k for k in self._cache.keys() if pattern in k]
                for key in keys_to_remove:
                    del self._cache[key]
            else:
                self._cache.clear()
```

## Security Best Practices

### Credential Management

```python
import os
from pathlib import Path
import json
import keyring  # Optional: for secure credential storage

class SecureCredentialManager:
    """Secure credential management."""
    
    @staticmethod
    def get_credentials_from_env() -> tuple[str, str]:
        """Get credentials from environment variables."""
        api_key = os.getenv("MAMMOTH_API_KEY")
        api_secret = os.getenv("MAMMOTH_API_SECRET")
        
        if not api_key or not api_secret:
            raise ValueError("MAMMOTH_API_KEY and MAMMOTH_API_SECRET must be set")
        
        return api_key, api_secret
    
    @staticmethod
    def get_credentials_from_keyring(service_name: str = "mammoth-sdk") -> tuple[str, str]:
        """Get credentials from system keyring (requires keyring package)."""
        try:
            api_key = keyring.get_password(service_name, "api_key")
            api_secret = keyring.get_password(service_name, "api_secret")
            
            if not api_key or not api_secret:
                raise ValueError("Credentials not found in keyring")
            
            return api_key, api_secret
        except ImportError:
            raise ImportError("keyring package required for keyring credential storage")
    
    @staticmethod
    def store_credentials_in_keyring(
        api_key: str, 
        api_secret: str, 
        service_name: str = "mammoth-sdk"
    ):
        """Store credentials in system keyring."""
        try:
            keyring.set_password(service_name, "api_key", api_key)
            keyring.set_password(service_name, "api_secret", api_secret)
        except ImportError:
            raise ImportError("keyring package required for keyring credential storage")

# Usage
try:
    api_key, api_secret = SecureCredentialManager.get_credentials_from_env()
except ValueError:
    # Fallback to keyring
    api_key, api_secret = SecureCredentialManager.get_credentials_from_keyring()

client = MammothClient(api_key=api_key, api_secret=api_secret)
```

### Input Validation

```python
import re
from pathlib import Path
from typing import Union

def validate_workspace_project_ids(workspace_id: int, project_id: int):
    """Validate workspace and project IDs."""
    if not isinstance(workspace_id, int) or workspace_id <= 0:
        raise ValueError(f"Invalid workspace_id: {workspace_id}")
    
    if not isinstance(project_id, int) or project_id <= 0:
        raise ValueError(f"Invalid project_id: {project_id}")

def sanitize_file_path(file_path: Union[str, Path]) -> Path:
    """Sanitize and validate file path."""
    path = Path(file_path)
    
    # Check for path traversal attempts
    if ".." in path.parts:
        raise ValueError(f"Path traversal not allowed: {file_path}")
    
    # Ensure path is absolute or relative to current directory
    if not path.is_absolute():
        path = Path.cwd() / path
    
    # Resolve symbolic links
    path = path.resolve()
    
    return path

def validate_file_for_upload(file_path: Union[str, Path]) -> Path:
    """Comprehensive file validation."""
    path = sanitize_file_path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    
    # Check file size (100MB limit)
    max_size = 100 * 1024 * 1024
    if path.stat().st_size > max_size:
        raise ValueError(f"File too large: {path.stat().st_size} bytes (max: {max_size})")
    
    # Check file extension
    allowed_extensions = {'.csv', '.xlsx', '.xls', '.json', '.txt'}
    if path.suffix.lower() not in allowed_extensions:
        raise ValueError(f"Unsupported file type: {path.suffix}")
    
    return path

# Usage in upload function
def safe_upload_file(
    client: MammothClient,
    workspace_id: int,
    project_id: int,
    file_path: Union[str, Path]
) -> int:
    """Safely upload file with input validation."""
    
    # Validate inputs
    validate_workspace_project_ids(workspace_id, project_id)
    validated_path = validate_file_for_upload(file_path)
    
    # Proceed with upload
    return client.files.upload_files(
        workspace_id=workspace_id,
        project_id=project_id,
        files=str(validated_path)
    )
```

## Testing Strategies

### Unit Testing with Mocks

```python
import unittest
from unittest.mock import Mock, patch, MagicMock
from mammoth import MammothClient
from mammoth.models.files import FilesList, FileSchema

class TestMammothOperations(unittest.TestCase):
    """Unit tests for Mammoth operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = MammothClient(
            api_key="test_key",
            api_secret="test_secret"
        )
    
    @patch('mammoth.client.requests.Session.request')
    def test_list_files_success(self, mock_request):
        """Test successful file listing."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "files": [
                {
                    "id": 1,
                    "name": "test.csv",
                    "status": "processed",
                    "created_at": "2023-01-01T00:00:00Z"
                }
            ],
            "limit": 50,
            "offset": 0,
            "next": ""
        }
        mock_request.return_value = mock_response
        
        # Test the operation
        files_list = self.client.files.list_files(
            workspace_id=1,
            project_id=1
        )
        
        # Assertions
        self.assertIsInstance(files_list, FilesList)
        self.assertEqual(len(files_list.files), 1)
        self.assertEqual(files_list.files[0].name, "test.csv")
        
        # Verify API call
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "GET")
    
    @patch('mammoth.client.requests.Session.request')
    def test_upload_file_success(self, mock_request):
        """Test successful file upload."""
        # Mock job creation response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"job_id": 123, "status_code": 200}
        ]
        mock_request.return_value = mock_response
        
        # Mock job completion
        with patch.object(self.client.jobs, 'wait_for_jobs') as mock_wait:
            mock_job = Mock()
            mock_job.status = "success"
            mock_job.response = {"ds_id": 456}
            mock_wait.return_value = [mock_job]
            
            # Test upload
            dataset_id = self.client.files.upload_files(
                workspace_id=1,
                project_id=1,
                files="test.csv"
            )
            
            # Assertions
            self.assertEqual(dataset_id, 456)
            mock_wait.assert_called_once_with([123], timeout=300)

class TestWithTestClient:
    """Integration tests with test client."""
    
    def setUp(self):
        """Set up test client with test credentials."""
        self.client = MammothClient(
            api_key=os.getenv("MAMMOTH_TEST_API_KEY"),
            api_secret=os.getenv("MAMMOTH_TEST_API_SECRET"),
            base_url=os.getenv("MAMMOTH_TEST_BASE_URL", "https://test-api.mammoth.io")
        )
        self.test_workspace_id = int(os.getenv("MAMMOTH_TEST_WORKSPACE_ID", "1"))
        self.test_project_id = int(os.getenv("MAMMOTH_TEST_PROJECT_ID", "1"))
    
    def test_connection(self):
        """Test connection to test environment."""
        self.assertTrue(self.client.test_connection())
    
    def test_list_files(self):
        """Test file listing in test environment."""
        files_list = self.client.files.list_files(
            workspace_id=self.test_workspace_id,
            project_id=self.test_project_id,
            limit=5
        )
        
        self.assertIsInstance(files_list, FilesList)
        self.assertLessEqual(len(files_list.files), 5)
```

### Integration Testing

```python
import tempfile
import csv
from pathlib import Path

class TestMammothIntegration:
    """Integration tests for Mammoth SDK."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = MammothClient.from_env()
        self.workspace_id = int(os.getenv("TEST_WORKSPACE_ID"))
        self.project_id = int(os.getenv("TEST_PROJECT_ID"))
    
    def create_test_csv(self, rows: int = 100) -> str:
        """Create a test CSV file."""
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', delete=False
        )
        
        with temp_file as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'value'])
            for i in range(rows):
                writer.writerow([i, f'Item {i}', i * 10])
        
        return temp_file.name
    
    def test_full_upload_workflow(self):
        """Test complete upload workflow."""
        # Create test file
        test_file = self.create_test_csv(50)
        
        try:
            # Upload file
            dataset_id = self.client.files.upload_files(
                workspace_id=self.workspace_id,
                project_id=self.project_id,
                files=test_file
            )
            
            self.assertIsNotNone(dataset_id)
            self.assertIsInstance(dataset_id, int)
            
            # Verify file appears in listing
            files_list = self.client.files.list_files(
                workspace_id=self.workspace_id,
                project_id=self.project_id,
                limit=10,
                sort="(created_at:desc)"
            )
            
            # Find our uploaded file
            uploaded_file = None
            for file in files_list.files:
                if (file.additional_info and 
                    file.additional_info.final_ds_id == dataset_id):
                    uploaded_file = file
                    break
            
            self.assertIsNotNone(uploaded_file)
            self.assertEqual(uploaded_file.status, "processed")
            
        finally:
            # Clean up test file
            Path(test_file).unlink(missing_ok=True)
```

## Monitoring and Observability

### Comprehensive Logging

```python
import logging
import sys
from datetime import datetime
import json

def setup_mammoth_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    include_api_calls: bool = False
):
    """Set up comprehensive logging for Mammoth operations."""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create logger
    logger = logging.getLogger('mammoth')
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # API call logging if enabled
    if include_api_calls:
        requests_logger = logging.getLogger('requests.packages.urllib3')
        requests_logger.setLevel(logging.DEBUG)
        requests_logger.addHandler(console_handler)
        if log_file:
            requests_logger.addHandler(file_handler)

# Usage
setup_mammoth_logging(level="DEBUG", log_file="mammoth.log", include_api_calls=True)
```

### Metrics Collection

```python
import time
from contextlib import contextmanager
from typing import Dict, Any
import threading

class MammothMetrics:
    """Collect metrics for Mammoth operations."""
    
    def __init__(self):
        self._metrics: Dict[str, Any] = {
            "operations": {},
            "errors": {},
            "timing": {}
        }
        self._lock = threading.Lock()
    
    @contextmanager
    def time_operation(self, operation_name: str):
        """Context manager to time operations."""
        start_time = time.time()
        try:
            yield
            self._record_success(operation_name, time.time() - start_time)
        except Exception as e:
            self._record_error(operation_name, e, time.time() - start_time)
            raise
    
    def _record_success(self, operation: str, duration: float):
        """Record successful operation."""
        with self._lock:
            if operation not in self._metrics["operations"]:
                self._metrics["operations"][operation] = {"count": 0, "total_time": 0}
            
            self._metrics["operations"][operation]["count"] += 1
            self._metrics["operations"][operation]["total_time"] += duration
    
    def _record_error(self, operation: str, error: Exception, duration: float):
        """Record operation error."""
        with self._lock:
            error_type = type(error).__name__
            key = f"{operation}:{error_type}"
            
            if key not in self._metrics["errors"]:
                self._metrics["errors"][key] = 0
            
            self._metrics["errors"][key] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        with self._lock:
            summary = {}
            
            # Operation summaries
            for op, data in self._metrics["operations"].items():
                count = data["count"]
                total_time = data["total_time"]
                avg_time = total_time / count if count > 0 else 0
                
                summary[op] = {
                    "count": count,
                    "avg_time": avg_time,
                    "total_time": total_time
                }
            
            # Error summaries
            summary["errors"] = dict(self._metrics["errors"])
            
            return summary

# Global metrics instance
metrics = MammothMetrics()

# Usage in operations
def upload_with_metrics(client, workspace_id, project_id, files):
    with metrics.time_operation("file_upload"):
        return client.files.upload_files(
            workspace_id=workspace_id,
            project_id=project_id,
            files=files
        )

# Print metrics summary
def print_metrics_summary():
    summary = metrics.get_summary()
    print("=== Mammoth SDK Metrics ===")
    print(json.dumps(summary, indent=2))
```

## See Also

- [Error Handling Guide](error-handling.md) - Comprehensive error handling
- [API Reference](../api/client.md) - Complete API documentation
- [Advanced Topics](../advanced/integrations.md) - Production deployment patterns
- [Troubleshooting](../advanced/troubleshooting.md) - Common issues and solutions
