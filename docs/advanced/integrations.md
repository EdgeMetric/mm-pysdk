# System Integrations Guide

This guide demonstrates how to integrate the Mammoth Python SDK with various databases, and other systems for production workflows.

## External Data Source Integrations

This section demonstrates how to pull data from external sources and upload it to Mammoth using CSV files.

### PostgreSQL Integration

Pull data from PostgreSQL and upload to Mammoth:

```python
import os
import csv
import psycopg2
import pandas as pd
from mammoth import MammothClient
from mammoth.exceptions import MammothAPIError
import tempfile
from pathlib import Path

def import_postgres_to_mammoth():
    """Import data from PostgreSQL into Mammoth."""
    
    # Initialize Mammoth client
    mammoth_client = MammothClient(
        api_key=os.getenv("MAMMOTH_API_KEY"),
        api_secret=os.getenv("MAMMOTH_API_SECRET")
    )
    
    workspace_id = 1
    project_id = 1
    postgres_conn = "postgresql://user:password@localhost:5432/database"
    
    try:
        # Step 1: Pull data from PostgreSQL
        query = """
            SELECT customer_id, name, email, total_orders, last_order_date
            FROM customers 
            WHERE created_date >= '2024-01-01'
        """
        
        # Export to CSV
        csv_file = "postgres_customers.csv"
        with psycopg2.connect(postgres_conn) as conn:
            df = pd.read_sql(query, conn)
            df.to_csv(csv_file, index=False)
            print(f"Exported {len(df)} rows to {csv_file}")
        
        # Step 2: Upload CSV to Mammoth
        dataset_id = mammoth_client.files.upload_files(
            workspace_id=workspace_id,
            project_id=project_id,
            files=csv_file
        )
        
        print(f"Successfully uploaded to Mammoth dataset: {dataset_id}")
        
    except psycopg2.Error as e:
        print(f"PostgreSQL error: {e}")
        raise
    except MammothAPIError as e:
        print(f"Mammoth API error: {e}")
        raise
    finally:
        # Clean up CSV file
        if Path(csv_file).exists():
            Path(csv_file).unlink()

if __name__ == "__main__":
    import_postgres_to_mammoth()
```

### HubSpot Integration

Pull data from HubSpot CRM and upload to Mammoth:

```python
import os
import pandas as pd
import requests
from mammoth import MammothClient
from mammoth.exceptions import MammothAPIError
from pathlib import Path

def import_hubspot_to_mammoth():
    """Import data from HubSpot into Mammoth."""
    
    # Initialize Mammoth client
    mammoth_client = MammothClient(
        api_key=os.getenv("MAMMOTH_API_KEY"),
        api_secret=os.getenv("MAMMOTH_API_SECRET")
    )
    
    workspace_id = 1
    project_id = 1
    hubspot_api_key = os.getenv("HUBSPOT_API_KEY")
    
    try:
        # Step 1: Pull contacts from HubSpot API
        url = "https://api.hubapi.com/crm/v3/objects/contacts"
        headers = {
            "Authorization": f"Bearer {hubspot_api_key}",
            "Content-Type": "application/json"
        }
        
        params = {
            "properties": "firstname,lastname,email,company,createdate,lastmodifieddate",
            "limit": 100
        }
        
        contacts = []
        while url:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            contacts.extend(data.get("results", []))
            
            # Check for next page
            url = data.get("paging", {}).get("next", {}).get("link")
            params = None  # Only use params for first request
        
        print(f"Retrieved {len(contacts)} contacts from HubSpot")
        
        # Step 2: Convert to DataFrame and save as CSV
        df_data = []
        for contact in contacts:
            properties = contact.get("properties", {})
            df_data.append({
                "contact_id": contact.get("id"),
                "first_name": properties.get("firstname", ""),
                "last_name": properties.get("lastname", ""),
                "email": properties.get("email", ""),
                "company": properties.get("company", ""),
                "created_date": properties.get("createdate", ""),
                "last_modified": properties.get("lastmodifieddate", "")
            })
        
        df = pd.DataFrame(df_data)
        csv_file = "hubspot_contacts.csv"
        df.to_csv(csv_file, index=False)
        print(f"Saved {len(df)} contacts to {csv_file}")
        
        # Step 3: Upload CSV to Mammoth
        dataset_id = mammoth_client.files.upload_files(
            workspace_id=workspace_id,
            project_id=project_id,
            files=csv_file
        )
        
        print(f"Successfully uploaded to Mammoth dataset: {dataset_id}")
        
    except requests.exceptions.RequestException as e:
        print(f"HubSpot API error: {e}")
        raise
    except MammothAPIError as e:
        print(f"Mammoth API error: {e}")
        raise
    finally:
        # Clean up CSV file
        if Path(csv_file).exists():
            Path(csv_file).unlink()

if __name__ == "__main__":
    import_hubspot_to_mammoth()
```

## CSV Export Workflows

### Exporting Mammoth Data to External Sources

This section demonstrates how to export data from Mammoth dataviews and push it to external systems like PostgreSQL.

#### How Exporting Mammoth Data to External Sources is Achieved:

• **Download**: Use the `download_dataview_csv()` utility function which creates an export job, monitors completion, and returns the local file path
• **Process**: Load the downloaded CSV data using pandas or similar tools
• **Transfer**: Push the processed data to external destinations (databases, APIs, file systems)
• **Cleanup**: Remove temporary files after successful transfer

```python
import os
import psycopg2
import pandas as pd
from mammoth import MammothClient
from mammoth.exceptions import MammothAPIError
from pathlib import Path

def export_mammoth_to_postgres():
    """Export dataview data from Mammoth to PostgreSQL."""
    
    # Initialize Mammoth client
    mammoth_client = MammothClient(
        api_key=os.getenv("MAMMOTH_API_KEY"),
        api_secret=os.getenv("MAMMOTH_API_SECRET")
    )
    
    workspace_id = 1
    project_id = 1
    dataset_id = 123  # Your dataset ID
    dataview_id = 456  # Your dataview ID
    
    try:
        # Step 1: Download dataview data as CSV using the utility function
        # This function internally uses add_export but handles job monitoring
        csv_file_path = mammoth_client.exports.download_dataview_csv(
            workspace_id=workspace_id,
            project_id=project_id,
            dataset_id=dataset_id,
            dataview_id=dataview_id,
            output_path="mammoth_export.csv",
            timeout=300  # 5 minutes timeout for large datasets
        )
        
        print(f"Downloaded dataview data to: {csv_file_path}")
        
        # Step 2: Load CSV data
        df = pd.read_csv(csv_file_path)
        print(f"Loaded {len(df)} rows from Mammoth dataview")
        
        # Step 3: Push to PostgreSQL
        postgres_conn = "postgresql://user:password@localhost:5432/database"
        
        with psycopg2.connect(postgres_conn) as conn:
            # Insert data into PostgreSQL table
            df.to_sql('mammoth_export', conn, if_exists='replace', index=False)
        
        print("Successfully exported Mammoth data to PostgreSQL")
        
    except MammothAPIError as e:
        print(f"Mammoth API error: {e}")
        raise
    except Exception as e:
        print(f"Export failed: {e}")
        raise
    finally:
        # Clean up CSV file
        if 'csv_file_path' in locals() and Path(csv_file_path).exists():
            Path(csv_file_path).unlink()
            print(f"Cleaned up temporary file: {csv_file_path}")

if __name__ == "__main__":
    export_mammoth_to_postgres()
```

### Key Benefits

- **Automated Job Management**: `download_dataview_csv()` handles export job creation and monitoring
- **File Path Return**: Returns the local file path for immediate processing
- **Error Handling**: Built-in timeout and error handling for export operations
- **Direct Integration**: Seamlessly push exported data to external systems

## See Also

- [Best Practices Guide](best-practices.md) - Development best practices
- [Error Handling Guide](error-handling.md) - Robust error handling
- [Troubleshooting Guide](troubleshooting.md) - Common integration issues
- [API Reference](../api/client.md) - Complete SDK documentation
