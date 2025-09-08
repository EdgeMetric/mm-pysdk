# Mammoth Python SDK Documentation

A production-ready Python SDK for the Mammoth Analytics platform API.

## Quick Start

```python
from mammoth import MammothClient

client = MammothClient(
    api_key="your-api-key",
    api_secret="your-api-secret"
)

# Upload a file and create dataset
dataset_id = client.files.upload_files(
    workspace_id=1,
    project_id=1,
    files="data.csv"
)
```

## Documentation Structure

### Getting Started
- [Installation](installation.md) - Install the SDK and dependencies
- [Authentication](authentication.md) - Set up API credentials
- [Quick Start Guide](quick-start.md) - Your first API calls

### API Reference
- [Client](api/client.md) - MammothClient configuration and methods
- [Files API](api/files.md) - File upload, management, and operations
- [Jobs API](api/jobs.md) - Asynchronous job tracking and monitoring
- [Data Models](api/models.md) - Request/response schemas and types
- [Exceptions](api/exceptions.md) - Error handling and custom exceptions
- [Utilities](api/utilities.md) - Helper functions and utilities

### Examples & Guides
- [Basic Usage](examples/basic-usage.md) - Simple operations and common patterns
- [File Operations](examples/file-operations.md) - Advanced file management
- [Job Management](examples/job-management.md) - Working with asynchronous operations
- [Error Handling](examples/error-handling.md) - Handling errors gracefully
- [Best Practices](examples/best-practices.md) - Recommended patterns and tips

### Advanced Topics
- [Integration Examples](advanced/integrations.md) - Database integrations and workflows
- [Async Operations](advanced/async-operations.md) - Managing long-running tasks
- [Configuration](advanced/configuration.md) - Advanced client configuration
- [Troubleshooting](advanced/troubleshooting.md) - Common issues and solutions

## Features

- **Simple Authentication** - API key and secret-based authentication
- **File Management** - Upload, list, update, and delete files
- **Dataset Creation** - Automatic dataset creation from uploaded files
- **Job Tracking** - Comprehensive async job monitoring with automatic waiting
- **Type Safety** - Full type hints and Pydantic models for IDE support
- **Error Handling** - Comprehensive exception handling with detailed error information
- **Automatic Retries** - Built-in retry logic for robust API interactions

## Support

- **Documentation**: This documentation site
- **Issues**: [GitHub Issues](https://github.com/mammoth-analytics/mammoth-python-sdk/issues)
- **Support**: support@mammoth.io

## License

MIT License - see LICENSE file for details.
