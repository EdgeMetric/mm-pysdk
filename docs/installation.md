# Installation

## Requirements

- Python 3.9 or higher
- pip or Poetry package manager

## Installation Methods

### Using pip (Recommended)

```bash
pip install mammoth-python-sdk
```

### Using Poetry

```bash
poetry add mammoth-python-sdk
```

### Development Installation

If you want to contribute to the SDK or install from source:

```bash
# Clone the repository
git clone https://github.com/mammoth-analytics/mammoth-python-sdk
cd mammoth-python-sdk

# Install with Poetry
poetry install

# Or install with pip
pip install -e .
```

## Dependencies

The SDK has minimal dependencies:

- `requests` (^2.32.0) - HTTP client for API requests
- `pydantic` (^2.11.0) - Data validation and serialization

Development dependencies include:
- `pytest` - Testing framework
- `black` - Code formatting
- `isort` - Import sorting
- `flake8` - Linting
- `mypy` - Type checking

## Verify Installation

After installation, verify the SDK is working:

```python
from mammoth import MammothClient

# This should not raise any import errors
print("Mammoth SDK installed successfully!")
```

## Environment Setup

For development or testing, you may want to set up environment variables:

```bash
export MAMMOTH_API_KEY="your-api-key"
export MAMMOTH_API_SECRET="your-api-secret"
export MAMMOTH_BASE_URL="https://your-instance.mammoth.io"
```

## Next Steps

- [Authentication Setup](authentication.md)
- [Quick Start Guide](quick-start.md)
