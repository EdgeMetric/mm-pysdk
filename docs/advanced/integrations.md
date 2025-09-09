# System Integrations Guide

This guide demonstrates how to integrate the Mammoth Python SDK with various databases, and other systems for production workflows.

## Database Integrations

### PostgreSQL Integration

```python
import os
import csv
import psycopg2
from mammoth import MammothClient
from mammoth.exceptions import MammothAPIError
import tempfile
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PostgreSQLMammothBridge:
    """Bridge between PostgreSQL and Mammoth Analytics."""
    
    def __init__(self, 
                 mammoth_client: MammothClient,
                 postgres_connection_string: str,
                 workspace_id: int,
                 project_id: int):
        self.mammoth = mammoth_client
        self.postgres_conn_str = postgres_connection_string
        self.workspace_id = workspace_id
        self.project_id = project_id
    
    def export_query_to_mammoth(self, 
                               query: str, 
                               dataset_name: str,
                               chunk_size: int = 10000) -> int:
        """Export PostgreSQL query results to Mammoth as a dataset."""
        
        temp_file = None
        try:
            # Create temporary CSV file
            temp_file = tempfile.NamedTemporaryFile(
                mode='w', suffix='.csv', delete=False, 
                prefix=f"{dataset_name}_"
            )
            
            # Connect to PostgreSQL and execute query
            with psycopg2.connect(self.postgres_conn_str) as conn:
                with conn.cursor() as cursor:
                    logger.info(f"Executing query for {dataset_name}")
                    cursor.execute(query)
                    
                    # Write CSV header
                    column_names = [desc[0] for desc in cursor.description]
                    writer = csv.writer(temp_file)
                    writer.writerow(column_names)
                    
                    # Write data in chunks
                    row_count = 0
                    while True:
                        rows = cursor.fetchmany(chunk_size)
                        if not rows:
                            break
                        
                        writer.writerows(rows)
                        row_count += len(rows)
                        logger.debug(f"Exported {row_count} rows so far")
            
            temp_file.close()
            logger.info(f"Exported {row_count} rows to {temp_file.name}")
            
            # Upload to Mammoth
            dataset_id = self.mammoth.files.upload_files(
                workspace_id=self.workspace_id,
                project_id=self.project_id,
                files=temp_file.name
            )
            
            logger.info(f"Successfully created dataset {dataset_id} from PostgreSQL query")
            return dataset_id
            
        except psycopg2.Error as e:
            logger.error(f"PostgreSQL error: {e}")
            raise
        except MammothAPIError as e:
            logger.error(f"Mammoth API error: {e}")
            raise
        finally:
            # Clean up temporary file
            if temp_file and Path(temp_file.name).exists():
                Path(temp_file.name).unlink()
    
    def sync_table_to_mammoth(self, 
                             table_name: str, 
                             where_clause: str = None,
                             append_mode: bool = False,
                             existing_dataset_id: int = None) -> int:
        """Sync a PostgreSQL table to Mammoth."""
        
        # Build query
        query = f"SELECT * FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        
        # Handle append mode
        if append_mode and existing_dataset_id:
            return self.append_query_to_dataset(query, existing_dataset_id)
        else:
            return self.export_query_to_mammoth(query, table_name)
    
    def append_query_to_dataset(self, query: str, dataset_id: int) -> int:
        """Append query results to existing Mammoth dataset."""
        
        temp_file = None
        try:
            temp_file = tempfile.NamedTemporaryFile(
                mode='w', suffix='.csv', delete=False
            )
            
            # Export data
            with psycopg2.connect(self.postgres_conn_str) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    
                    column_names = [desc[0] for desc in cursor.description]
                    writer = csv.writer(temp_file)
                    writer.writerow(column_names)
                    writer.writerows(cursor.fetchall())
            
            temp_file.close()
            
            # Append to existing dataset
            result_dataset_id = self.mammoth.files.upload_files(
                workspace_id=self.workspace_id,
                project_id=self.project_id,
                files=temp_file.name,
                append_to_ds_id=dataset_id
            )
            
            return result_dataset_id
            
        finally:
            if temp_file and Path(temp_file.name).exists():
                Path(temp_file.name).unlink()

# Usage example
def postgres_to_mammoth_example():
    """Example of PostgreSQL to Mammoth integration."""
    
    # Initialize clients
    mammoth_client = MammothClient(
        api_key=os.getenv("MAMMOTH_API_KEY"),
        api_secret=os.getenv("MAMMOTH_API_SECRET")
    )
    
    postgres_conn = "postgresql://user:password@localhost:5432/database"
    
    bridge = PostgreSQLMammothBridge(
        mammoth_client=mammoth_client,
        postgres_connection_string=postgres_conn,
        workspace_id=1,
        project_id=1
    )
    
    # Export sales data from last month
    sales_query = """
        SELECT order_id, customer_id, product_id, quantity, price, order_date
        FROM sales 
        WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
    """
    
    dataset_id = bridge.export_query_to_mammoth(
        query=sales_query,
        dataset_name="monthly_sales"
    )
    
    print(f"Sales data exported to Mammoth dataset: {dataset_id}")
```

## CSV Export Workflows

### Exporting Mammoth Data to External Sources

This section demonstrates how to export data from Mammoth dataviews and push it to external systems like PostgreSQL.

```python
import os
import psycopg2
import pandas as pd
from mammoth import MammothClient
from mammoth.exceptions import MammothAPIError
import tempfile
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
    dataview_id = 123  # Your dataview ID
    
    try:
        # Step 1: Export dataview data as CSV using add_export
        csv_content = mammoth_client.dataviews.add_export(
            workspace_id=workspace_id,
            project_id=project_id,
            dataview_id=dataview_id,
            export_type="csv"
        )
        
        # Step 2: Save CSV to temporary file
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', delete=False
        )
        
        with open(temp_file.name, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        print(f"Downloaded dataview data to: {temp_file.name}")
        
        # Step 3: Push to PostgreSQL
        postgres_conn = "postgresql://user:password@localhost:5432/database"
        
        # Read CSV and load to PostgreSQL
        df = pd.read_csv(temp_file.name)
        
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
        # Clean up temporary file
        if temp_file and Path(temp_file.name).exists():
            Path(temp_file.name).unlink()

if __name__ == "__main__":
    export_mammoth_to_postgres()
```

### Key Benefits

- **Simple Export**: Use `add_export` to download dataview data as CSV
- **Direct Integration**: Push exported data directly to PostgreSQL or other databases
- **Lightweight**: Minimal code for maximum functionality

## See Also

- [Best Practices Guide](best-practices.md) - Development best practices
- [Error Handling Guide](error-handling.md) - Robust error handling
- [Troubleshooting Guide](troubleshooting.md) - Common integration issues
- [API Reference](../api/client.md) - Complete SDK documentation
