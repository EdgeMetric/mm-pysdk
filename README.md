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
poetry add git+ssh://git@github.com/EdgeMetric/mm-pysdk.git
```

### Using pip

```bash
pip install git+ssh://git@github.com/EdgeMetric/mm-pysdk.git
```

## Quick Start

```python
from mammoth import MammothClient

# Initialize client
client = MammothClient(
    api_key="your-api-key",
    api_secret="your-api-secret",
    base_url="https://app.mammoth.io/api/v2"
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
    base_url="https://app.mammoth.io/api/v2"  # Or your instance URL
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

## Support

- **Documentation**: [https://mammoth.io/docs](https://mammoth.io/docs)
- **Issues**: [GitHub Issues](https://github.com/EdgeMetric/mm-pysdk/issues)

## License

MIT License - see LICENSE file for details.
