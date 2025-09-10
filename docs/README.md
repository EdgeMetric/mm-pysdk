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
- [Exports API](api/exports.md) - Export to Mammoth internal dataset or External sources
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

## Documentation Features

### Code Examples
Every documentation page includes:
- ✅ Working code examples
- ✅ Complete, runnable snippets
- ✅ Real-world use cases
- ✅ Error handling demonstrations

### Type Information
All examples include:
- ✅ Full type hints
- ✅ Parameter documentation
- ✅ Return value specifications
- ✅ Exception information

### Cross-References
Documentation includes:
- ✅ Links between related topics
- ✅ "See Also" sections
- ✅ API cross-references
- ✅ Example cross-links

## Contributing to Documentation

### Updating Examples
When updating the SDK:
1. Update relevant API documentation
2. Add new examples for new features
3. Update version information
4. Test all code examples

### Adding New Sections
For new features:
1. Add API reference documentation
2. Create practical examples
3. Update navigation links
4. Add cross-references

### Documentation Standards
- Use clear, concise language
- Include complete, working examples
- Provide proper error handling
- Link to related documentation

## Support and Feedback

### Getting Help
- 📖 Check relevant documentation section
- 🔍 Use the search functionality
- 💬 Contact support@mammoth.io
- 🐛 Report issues on GitHub

### Improving Documentation
- 📝 Suggest improvements
- 🚀 Contribute examples
- 🔧 Report documentation bugs
- 💡 Request new topics

## Version Information

This documentation covers:
- **SDK Version**: 0.1.0
- **Python Version**: 3.9+
- **API Version**: v2
- **Last Updated**: Current release

For version-specific information, see the [Changelog](changelog.md).


## Support

- **Mammoth Analytics Documentation**: [https://mammoth.io/docs](https://mammoth.io/docs)
- **Issues**: [GitHub Issues](https://github.com/EdgeMetric/mm-pysdk/issues)

## License

MIT License - see LICENSE file for details.
