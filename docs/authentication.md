# Authentication

The Mammoth SDK uses API key and secret-based authentication for secure access to the Mammoth Analytics platform.

## Getting API Credentials

1. Log into your Mammoth Analytics dashboard
2. Navigate to your profile settings
3. Generate or retrieve your API key and secret
4. Store these credentials securely

## Authentication Methods

### Direct Authentication

```python
from mammoth import MammothClient

client = MammothClient(
    api_key="your-api-key",
    api_secret="your-api-secret",
    base_url="https://your-instance.mammoth.io"  # Optional, defaults to https://api.mammoth.io
)
```

### Environment Variables (Recommended)

Set up environment variables for better security:

```bash
export MAMMOTH_API_KEY="your-api-key"
export MAMMOTH_API_SECRET="your-api-secret"
export MAMMOTH_BASE_URL="https://your-instance.mammoth.io"
```

Then initialize the client:

```python
import os
from mammoth import MammothClient

client = MammothClient(
    api_key=os.getenv("MAMMOTH_API_KEY"),
    api_secret=os.getenv("MAMMOTH_API_SECRET"),
    base_url=os.getenv("MAMMOTH_BASE_URL", "https://api.mammoth.io")
)
```

### Configuration File

Create a configuration file (e.g., `mammoth_config.py`):

```python
# mammoth_config.py
MAMMOTH_CONFIG = {
    "api_key": "your-api-key",
    "api_secret": "your-api-secret",
    "base_url": "https://your-instance.mammoth.io"
}
```

Use it in your application:

```python
from mammoth import MammothClient
from mammoth_config import MAMMOTH_CONFIG

client = MammothClient(**MAMMOTH_CONFIG)
```

## Testing Connection

Always test your connection after setup:

```python
from mammoth import MammothClient

client = MammothClient(
    api_key="your-api-key",
    api_secret="your-api-secret"
)

# Test the connection
if client.test_connection():
    print("✓ Connected successfully!")
else:
    print("✗ Connection failed. Check your credentials.")
```

## Error Handling

Handle authentication errors gracefully:

```python
from mammoth import MammothClient, MammothAuthError

try:
    client = MammothClient(
        api_key="invalid-key",
        api_secret="invalid-secret"
    )
    files = client.files.list_files(workspace_id=1, project_id=1)
except MammothAuthError:
    print("Authentication failed - check your API credentials")
```

## Security Best Practices

### 1. Never Hardcode Credentials

❌ **Don't do this:**
```python
client = MammothClient(
    api_key="pk_live_123456789",  # Never hardcode!
    api_secret="sk_live_987654321"
)
```

✅ **Do this instead:**
```python
client = MammothClient(
    api_key=os.getenv("MAMMOTH_API_KEY"),
    api_secret=os.getenv("MAMMOTH_API_SECRET")
)
```

### 2. Use Different Credentials for Different Environments

```python
# config.py
import os

def get_mammoth_config():
    if os.getenv("ENVIRONMENT") == "production":
        return {
            "api_key": os.getenv("MAMMOTH_PROD_API_KEY"),
            "api_secret": os.getenv("MAMMOTH_PROD_API_SECRET"),
            "base_url": "https://api.mammoth.io"
        }
    else:
        return {
            "api_key": os.getenv("MAMMOTH_DEV_API_KEY"),
            "api_secret": os.getenv("MAMMOTH_DEV_API_SECRET"),
            "base_url": "https://dev-api.mammoth.io"
        }
```

### 3. Rotate Credentials Regularly

- Regularly rotate your API credentials
- Invalidate old credentials promptly
- Monitor API usage for unusual activity

## Custom Headers and Configuration

You can customize the client with additional settings:

```python
client = MammothClient(
    api_key="your-api-key",
    api_secret="your-api-secret",
    timeout=60,  # Request timeout in seconds
    max_retries=5  # Maximum number of retries for failed requests
)
```

## Next Steps

- [Quick Start Guide](quick-start.md)
- [Basic Usage Examples](examples/basic-usage.md)
