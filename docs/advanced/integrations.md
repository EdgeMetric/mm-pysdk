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

### Round-trip Data Processing Workflow

This section demonstrates how to create a complete data processing pipeline where data flows from external sources into Mammoth, gets processed, and then exported back to external systems via CSV downloads.

```python
import os
import psycopg2
import pandas as pd
from mammoth import MammothClient
from mammoth.exceptions import MammothAPIError
import tempfile
from pathlib import Path

class MammothDataPipeline:
    """Complete data pipeline for round-trip processing."""
    
    def __init__(self, mammoth_client: MammothClient, workspace_id: int, project_id: int):
        self.mammoth = mammoth_client
        self.workspace_id = workspace_id
        self.project_id = project_id
    
    def ingest_from_file(self, file_path: str) -> int:
        """Step 1: Ingest data from local file into Mammoth."""
        try:
            dataset_id = self.mammoth.files.upload_files(
                workspace_id=self.workspace_id,
                project_id=self.project_id,
                files=file_path
            )
            print(f"Uploaded file to Mammoth dataset: {dataset_id}")
            return dataset_id
        except MammothAPIError as e:
            print(f"Failed to upload file: {e}")
            raise
    
    def ingest_from_postgres(self, postgres_conn_str: str, query: str, dataset_name: str) -> int:
        """Step 1: Ingest data from PostgreSQL into Mammoth."""
        temp_file = None
        try:
            # Create temporary CSV
            temp_file = tempfile.NamedTemporaryFile(
                mode='w', suffix='.csv', delete=False, 
                prefix=f"{dataset_name}_"
            )
            
            # Export PostgreSQL data to CSV
            with psycopg2.connect(postgres_conn_str) as conn:
                df = pd.read_sql_query(query, conn)
                df.to_csv(temp_file.name, index=False)
            
            temp_file.close()
            
            # Upload to Mammoth
            dataset_id = self.mammoth.files.upload_files(
                workspace_id=self.workspace_id,
                project_id=self.project_id,
                files=temp_file.name
            )
            
            print(f"Imported PostgreSQL data to Mammoth dataset: {dataset_id}")
            return dataset_id
            
        finally:
            if temp_file and Path(temp_file.name).exists():
                Path(temp_file.name).unlink()
    
    def process_data_in_mammoth(self, dataset_id: int) -> int:
        """Step 2: Process data in Mammoth and create a dataview."""
        # Create a dataview with your processing logic
        # This is where you would apply transformations, aggregations, etc.
        try:
            dataview_id = self.mammoth.dataviews.create_dataview(
                workspace_id=self.workspace_id,
                project_id=self.project_id,
                dataset_id=dataset_id,
                name="Processed Data",
                # Add your processing configuration here
            )
            print(f"Created processed dataview: {dataview_id}")
            return dataview_id
        except MammothAPIError as e:
            print(f"Failed to create dataview: {e}")
            raise
    
    def export_as_csv(self, dataview_id: int, output_path: str = None) -> str:
        """Step 3: Export processed dataview as CSV."""
        try:
            # Download the dataview data as CSV
            csv_content = self.mammoth.dataviews.download_as_csv(
                workspace_id=self.workspace_id,
                project_id=self.project_id,
                dataview_id=dataview_id
            )
            
            # Save to file
            if not output_path:
                output_path = f"mammoth_export_{dataview_id}.csv"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(csv_content)
            
            print(f"Exported dataview to CSV: {output_path}")
            return output_path
            
        except MammothAPIError as e:
            print(f"Failed to export CSV: {e}")
            raise
    
    def load_csv_to_postgres(self, csv_file_path: str, postgres_conn_str: str, 
                           table_name: str, if_exists: str = "replace"):
        """Step 4: Load exported CSV back into PostgreSQL."""
        try:
            # Read the CSV file
            df = pd.read_csv(csv_file_path)
            
            # Connect to PostgreSQL and load data
            with psycopg2.connect(postgres_conn_str) as conn:
                df.to_sql(table_name, conn, if_exists=if_exists, index=False)
            
            print(f"Loaded CSV data to PostgreSQL table: {table_name}")
            
        except Exception as e:
            print(f"Failed to load CSV to PostgreSQL: {e}")
            raise

# Complete workflow example
def complete_data_processing_workflow():
    """Example of complete round-trip data processing workflow."""
    
    # Initialize Mammoth client
    mammoth_client = MammothClient(
        api_key=os.getenv("MAMMOTH_API_KEY"),
        api_secret=os.getenv("MAMMOTH_API_SECRET")
    )
    
    # PostgreSQL connection
    postgres_conn = "postgresql://user:password@localhost:5432/database"
    
    # Initialize pipeline
    pipeline = MammothDataPipeline(
        mammoth_client=mammoth_client,
        workspace_id=1,
        project_id=1
    )
    
    # === WORKFLOW EXAMPLE 1: File-based processing ===
    print("=== File-based Processing Workflow ===")
    
    # Step 1: Upload local file to Mammoth
    source_file = "/path/to/your/data.csv"
    dataset_id = pipeline.ingest_from_file(source_file)
    
    # Step 2: Process data in Mammoth (create dataview)
    dataview_id = pipeline.process_data_in_mammoth(dataset_id)
    
    # Step 3: Export processed data as CSV
    exported_csv = pipeline.export_as_csv(dataview_id, "processed_data.csv")
    
    # Step 4: Load back to PostgreSQL
    pipeline.load_csv_to_postgres(
        csv_file_path=exported_csv,
        postgres_conn_str=postgres_conn,
        table_name="processed_results"
    )
    
    # === WORKFLOW EXAMPLE 2: PostgreSQL round-trip ===
    print("\n=== PostgreSQL Round-trip Workflow ===")
    
    # Step 1: Extract data from PostgreSQL source table
    source_query = """
        SELECT customer_id, product_id, quantity, price, order_date
        FROM raw_sales_data 
        WHERE order_date >= CURRENT_DATE - INTERVAL '7 days'
    """
    
    dataset_id = pipeline.ingest_from_postgres(
        postgres_conn_str=postgres_conn,
        query=source_query,
        dataset_name="weekly_sales"
    )
    
    # Step 2: Process in Mammoth (aggregations, transformations, etc.)
    dataview_id = pipeline.process_data_in_mammoth(dataset_id)
    
    # Step 3: Export processed results
    exported_csv = pipeline.export_as_csv(dataview_id, "sales_summary.csv")
    
    # Step 4: Load results back to PostgreSQL
    pipeline.load_csv_to_postgres(
        csv_file_path=exported_csv,
        postgres_conn_str=postgres_conn,
        table_name="sales_summary_weekly",
        if_exists="replace"
    )
    
    print("Workflow completed successfully!")

# Advanced workflow with error handling and logging
def production_workflow_example():
    """Production-ready workflow with comprehensive error handling."""
    
    import logging
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        mammoth_client = MammothClient(
            api_key=os.getenv("MAMMOTH_API_KEY"),
            api_secret=os.getenv("MAMMOTH_API_SECRET")
        )
        
        pipeline = MammothDataPipeline(
            mammoth_client=mammoth_client,
            workspace_id=int(os.getenv("MAMMOTH_WORKSPACE_ID")),
            project_id=int(os.getenv("MAMMOTH_PROJECT_ID"))
        )
        
        postgres_conn = os.getenv("POSTGRES_CONNECTION_STRING")
        
        # Data extraction with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                dataset_id = pipeline.ingest_from_postgres(
                    postgres_conn_str=postgres_conn,
                    query="SELECT * FROM source_table WHERE status = 'pending'",
                    dataset_name="pending_records"
                )
                break
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
        
        # Processing
        dataview_id = pipeline.process_data_in_mammoth(dataset_id)
        
        # Export with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = f"exports/processed_data_{timestamp}.csv"
        
        exported_csv = pipeline.export_as_csv(dataview_id, export_path)
        
        # Load to destination
        pipeline.load_csv_to_postgres(
            csv_file_path=exported_csv,
            postgres_conn_str=postgres_conn,
            table_name="processed_results"
        )
        
        logger.info("Production workflow completed successfully")
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        raise

if __name__ == "__main__":
    complete_data_processing_workflow()
```

### Key Benefits of This Workflow

1. **Flexible Data Sources**: Works with both file uploads and database connections
2. **Mammoth Processing Power**: Leverage Mammoth's analytics capabilities for data transformation
3. **Seamless Export**: Use the `download_as_csv` functionality to get processed results
4. **External Integration**: Push results back to PostgreSQL or other systems
5. **Production Ready**: Includes error handling, logging, and retry mechanisms

### Common Use Cases

- **Data Quality Workflows**: Import raw data, apply cleansing rules, export clean datasets
- **Analytics Workflows**: Pull operational data, perform analysis, push insights back to applications
- **Batch Processing**: Scheduled workflows for regular data processing tasks

## See Also

- [Best Practices Guide](best-practices.md) - Development best practices
- [Error Handling Guide](error-handling.md) - Robust error handling
- [Troubleshooting Guide](troubleshooting.md) - Common integration issues
- [API Reference](../api/client.md) - Complete SDK documentation
