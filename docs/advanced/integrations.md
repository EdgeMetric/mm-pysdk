# System Integrations Guide

This guide demonstrates how to integrate the Mammoth Python SDK with various databases, ETL pipelines, and other systems for production workflows.

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

### MySQL Integration

```python
import mysql.connector
from typing import Dict, Any, Optional
import pandas as pd

class MySQLMammothIntegration:
    """Integration between MySQL and Mammoth."""
    
    def __init__(self, 
                 mammoth_client: MammothClient,
                 mysql_config: Dict[str, Any],
                 workspace_id: int,
                 project_id: int):
        self.mammoth = mammoth_client
        self.mysql_config = mysql_config
        self.workspace_id = workspace_id
        self.project_id = project_id
    
    def export_table_to_mammoth(self, 
                               table_name: str,
                               columns: Optional[list] = None,
                               conditions: Optional[str] = None) -> int:
        """Export MySQL table to Mammoth using pandas for efficiency."""
        
        # Build query
        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {table_name}"
        if conditions:
            query += f" WHERE {conditions}"
        
        try:
            # Use pandas for efficient data transfer
            with mysql.connector.connect(**self.mysql_config) as conn:
                df = pd.read_sql(query, conn)
            
            # Save to temporary CSV
            temp_file = tempfile.NamedTemporaryFile(
                mode='w', suffix='.csv', delete=False
            )
            df.to_csv(temp_file.name, index=False)
            temp_file.close()
            
            # Upload to Mammoth
            dataset_id = self.mammoth.files.upload_files(
                workspace_id=self.workspace_id,
                project_id=self.project_id,
                files=temp_file.name
            )
            
            logger.info(f"Exported {len(df)} rows from {table_name} to dataset {dataset_id}")
            return dataset_id
            
        finally:
            if 'temp_file' in locals() and Path(temp_file.name).exists():
                Path(temp_file.name).unlink()
    
    def sync_tables_batch(self, table_configs: list) -> Dict[str, int]:
        """Sync multiple tables in batch."""
        results = {}
        
        for config in table_configs:
            table_name = config['table']
            try:
                dataset_id = self.export_table_to_mammoth(
                    table_name=table_name,
                    columns=config.get('columns'),
                    conditions=config.get('conditions')
                )
                results[table_name] = dataset_id
                logger.info(f"✓ Synced {table_name} -> Dataset {dataset_id}")
                
            except Exception as e:
                logger.error(f"✗ Failed to sync {table_name}: {e}")
                results[table_name] = None
        
        return results

# Example usage
mysql_config = {
    'host': 'localhost',
    'user': 'username',
    'password': 'password',
    'database': 'mydb'
}

mysql_integration = MySQLMammothIntegration(
    mammoth_client=mammoth_client,
    mysql_config=mysql_config,
    workspace_id=1,
    project_id=1
)

# Sync multiple tables
table_configs = [
    {
        'table': 'customers',
        'columns': ['customer_id', 'name', 'email', 'created_at']
    },
    {
        'table': 'orders',
        'conditions': "order_date >= '2024-01-01'"
    }
]

results = mysql_integration.sync_tables_batch(table_configs)
```

## ETL Pipeline Integration

### Apache Airflow Integration

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from mammoth import MammothClient
import os

# Default DAG arguments
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    'mammoth_etl_pipeline',
    default_args=default_args,
    description='ETL pipeline with Mammoth integration',
    schedule_interval='@daily',
    catchup=False,
    tags=['etl', 'mammoth', 'data-pipeline']
)

def extract_data_task(**context):
    """Extract data from source systems."""
    execution_date = context['execution_date']
    logger.info(f"Extracting data for {execution_date}")
    
    # Extract logic here
    # Save extracted data to staging area
    staging_file = f"/tmp/extracted_data_{execution_date.strftime('%Y%m%d')}.csv"
    
    # Your extraction logic here
    # ...
    
    return staging_file

def transform_data_task(**context):
    """Transform extracted data."""
    ti = context['ti']
    staging_file = ti.xcom_pull(task_ids='extract_data')
    
    # Transform logic here
    transformed_file = staging_file.replace('extracted', 'transformed')
    
    # Your transformation logic here
    # ...
    
    return transformed_file

def upload_to_mammoth_task(**context):
    """Upload transformed data to Mammoth."""
    ti = context['ti']
    transformed_file = ti.xcom_pull(task_ids='transform_data')
    
    # Initialize Mammoth client
    client = MammothClient(
        api_key=os.getenv("MAMMOTH_API_KEY"),
        api_secret=os.getenv("MAMMOTH_API_SECRET")
    )
    
    try:
        # Upload to Mammoth
        dataset_id = client.files.upload_files(
            workspace_id=int(os.getenv("MAMMOTH_WORKSPACE_ID")),
            project_id=int(os.getenv("MAMMOTH_PROJECT_ID")),
            files=transformed_file
        )
        
        logger.info(f"Successfully uploaded to Mammoth: Dataset {dataset_id}")
        
        # Store dataset ID for downstream tasks
        context['ti'].xcom_push(key='dataset_id', value=dataset_id)
        
        return dataset_id
        
    except Exception as e:
        logger.error(f"Failed to upload to Mammoth: {e}")
        raise
    finally:
        # Clean up temporary files
        if os.path.exists(transformed_file):
            os.remove(transformed_file)

def validate_upload_task(**context):
    """Validate the uploaded dataset."""
    ti = context['ti']
    dataset_id = ti.xcom_pull(task_ids='upload_to_mammoth', key='dataset_id')
    
    client = MammothClient(
        api_key=os.getenv("MAMMOTH_API_KEY"),
        api_secret=os.getenv("MAMMOTH_API_SECRET")
    )
    
    # Get file details to validate upload
    files_list = client.files.list_files(
        workspace_id=int(os.getenv("MAMMOTH_WORKSPACE_ID")),
        project_id=int(os.getenv("MAMMOTH_PROJECT_ID")),
        limit=10,
        sort="(created_at:desc)"
    )
    
    # Find our dataset
    for file in files_list.files:
        if (file.additional_info and 
            file.additional_info.final_ds_id == dataset_id and
            file.status == "processed"):
            logger.info(f"✓ Dataset {dataset_id} successfully processed")
            return True
    
    raise Exception(f"Dataset {dataset_id} not found or not processed")

# Define tasks
extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data_task,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data_task,
    dag=dag
)

upload_task = PythonOperator(
    task_id='upload_to_mammoth',
    python_callable=upload_to_mammoth_task,
    dag=dag
)

validate_task = PythonOperator(
    task_id='validate_upload',
    python_callable=validate_upload_task,
    dag=dag
)

# Set task dependencies
extract_task >> transform_task >> upload_task >> validate_task
```

### Pandas Integration

```python
import pandas as pd
from typing import Union, List, Dict, Any
import io

class PandasMammothIntegration:
    """Integration between Pandas DataFrames and Mammoth."""
    
    def __init__(self, mammoth_client: MammothClient, workspace_id: int, project_id: int):
        self.mammoth = mammoth_client
        self.workspace_id = workspace_id
        self.project_id = project_id
    
    def dataframe_to_mammoth(self, 
                            df: pd.DataFrame, 
                            filename: str = "dataframe_export.csv",
                            **upload_kwargs) -> int:
        """Upload pandas DataFrame to Mammoth."""
        
        # Convert DataFrame to CSV in memory
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue().encode('utf-8')
        
        # Create file-like object
        file_obj = io.BytesIO(csv_data)
        file_obj.name = filename
        
        # Upload to Mammoth
        dataset_id = self.mammoth.files.upload_files(
            workspace_id=self.workspace_id,
            project_id=self.project_id,
            files=file_obj,
            **upload_kwargs
        )
        
        logger.info(f"Uploaded DataFrame ({len(df)} rows) to dataset {dataset_id}")
        return dataset_id
    
    def process_and_upload(self, 
                          df: pd.DataFrame,
                          processing_func: callable,
                          filename: str = "processed_data.csv") -> int:
        """Apply processing function and upload result."""
        
        # Apply processing
        processed_df = processing_func(df)
        
        # Upload processed data
        return self.dataframe_to_mammoth(processed_df, filename)
    
    def batch_upload_dataframes(self, 
                               dataframes: Dict[str, pd.DataFrame]) -> Dict[str, int]:
        """Upload multiple DataFrames in batch."""
        results = {}
        
        for name, df in dataframes.items():
            try:
                dataset_id = self.dataframe_to_mammoth(
                    df, filename=f"{name}.csv"
                )
                results[name] = dataset_id
                logger.info(f"✓ Uploaded {name}: Dataset {dataset_id}")
            except Exception as e:
                logger.error(f"✗ Failed to upload {name}: {e}")
                results[name] = None
        
        return results

# Example usage
def pandas_processing_example():
    """Example of pandas processing with Mammoth upload."""
    
    # Create sample data
    data = {
        'date': pd.date_range('2024-01-01', periods=1000),
        'sales': pd.np.random.randint(100, 1000, 1000),
        'region': pd.np.random.choice(['North', 'South', 'East', 'West'], 1000)
    }
    df = pd.DataFrame(data)
    
    # Initialize integration
    pandas_integration = PandasMammothIntegration(
        mammoth_client=mammoth_client,
        workspace_id=1,
        project_id=1
    )
    
    # Define processing function
    def monthly_aggregation(df):
        """Aggregate sales data by month and region."""
        df['month'] = df['date'].dt.to_period('M')
        return df.groupby(['month', 'region']).agg({
            'sales': ['sum', 'mean', 'count']
        }).round(2)
    
    # Process and upload
    dataset_id = pandas_integration.process_and_upload(
        df=df,
        processing_func=monthly_aggregation,
        filename="monthly_sales_summary.csv"
    )
    
    print(f"Processed data uploaded to dataset: {dataset_id}")

# Batch upload example
def batch_upload_example():
    """Example of batch DataFrame upload."""
    
    # Create multiple DataFrames
    customers_df = pd.DataFrame({
        'customer_id': range(1, 101),
        'name': [f'Customer {i}' for i in range(1, 101)],
        'signup_date': pd.date_range('2023-01-01', periods=100)
    })
    
    orders_df = pd.DataFrame({
        'order_id': range(1, 201),
        'customer_id': pd.np.random.randint(1, 101, 200),
        'order_amount': pd.np.random.uniform(50, 500, 200),
        'order_date': pd.date_range('2024-01-01', periods=200)
    })
    
    dataframes = {
        'customers': customers_df,
        'orders': orders_df
    }
    
    pandas_integration = PandasMammothIntegration(
        mammoth_client=mammoth_client,
        workspace_id=1,
        project_id=1
    )
    
    results = pandas_integration.batch_upload_dataframes(dataframes)
    print("Batch upload results:", results)
```

## Cloud Storage Integration

### AWS S3 Integration

```python
import boto3
import tempfile
from botocore.exceptions import ClientError, NoCredentialsError

class S3MammothIntegration:
    """Integration between AWS S3 and Mammoth."""
    
    def __init__(self, 
                 mammoth_client: MammothClient,
                 aws_access_key: str = None,
                 aws_secret_key: str = None,
                 aws_region: str = 'us-east-1',
                 workspace_id: int = None,
                 project_id: int = None):
        
        self.mammoth = mammoth_client
        self.workspace_id = workspace_id
        self.project_id = project_id
        
        # Initialize S3 client
        if aws_access_key and aws_secret_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )
        else:
            # Use default credentials (from ~/.aws/credentials, IAM role, etc.)
            self.s3_client = boto3.client('s3', region_name=aws_region)
    
    def upload_s3_file_to_mammoth(self, 
                                 bucket_name: str, 
                                 s3_key: str,
                                 **mammoth_kwargs) -> int:
        """Download file from S3 and upload to Mammoth."""
        
        temp_file = None
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            
            # Download from S3
            logger.info(f"Downloading s3://{bucket_name}/{s3_key}")
            self.s3_client.download_fileobj(bucket_name, s3_key, temp_file)
            temp_file.close()
            
            # Upload to Mammoth
            dataset_id = self.mammoth.files.upload_files(
                workspace_id=self.workspace_id,
                project_id=self.project_id,
                files=temp_file.name,
                **mammoth_kwargs
            )
            
            logger.info(f"Successfully uploaded s3://{bucket_name}/{s3_key} to dataset {dataset_id}")
            return dataset_id
            
        except ClientError as e:
            logger.error(f"AWS S3 error: {e}")
            raise
        except Exception as e:
            logger.error(f"Upload error: {e}")
            raise
        finally:
            # Clean up temporary file
            if temp_file and Path(temp_file.name).exists():
                Path(temp_file.name).unlink()
    
    def sync_s3_folder_to_mammoth(self, 
                                 bucket_name: str, 
                                 folder_prefix: str = "",
                                 file_pattern: str = "*.csv") -> Dict[str, int]:
        """Sync entire S3 folder to Mammoth."""
        
        results = {}
        
        try:
            # List objects in S3 folder
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket_name, Prefix=folder_prefix)
            
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        s3_key = obj['Key']
                        
                        # Skip directories
                        if s3_key.endswith('/'):
                            continue
                        
                        # Check file pattern
                        if file_pattern != "*" and not Path(s3_key).match(file_pattern):
                            continue
                        
                        try:
                            dataset_id = self.upload_s3_file_to_mammoth(
                                bucket_name=bucket_name,
                                s3_key=s3_key
                            )
                            results[s3_key] = dataset_id
                            logger.info(f"✓ Synced {s3_key} -> Dataset {dataset_id}")
                            
                        except Exception as e:
                            logger.error(f"✗ Failed to sync {s3_key}: {e}")
                            results[s3_key] = None
            
            return results
            
        except ClientError as e:
            logger.error(f"Error listing S3 objects: {e}")
            raise

# Usage example
def s3_integration_example():
    """Example of S3 to Mammoth integration."""
    
    s3_integration = S3MammothIntegration(
        mammoth_client=mammoth_client,
        workspace_id=1,
        project_id=1,
        aws_region='us-west-2'
    )
    
    # Upload single file
    dataset_id = s3_integration.upload_s3_file_to_mammoth(
        bucket_name='my-data-bucket',
        s3_key='exports/sales_data_2024.csv'
    )
    
    # Sync entire folder
    results = s3_integration.sync_s3_folder_to_mammoth(
        bucket_name='my-data-bucket',
        folder_prefix='daily_exports/',
        file_pattern='*.csv'
    )
    
    print(f"Synced {len(results)} files from S3")
```

## Monitoring and Alerting

### Slack Integration

```python
import requests
from typing import Optional
import json

class MammothSlackNotifier:
    """Send Mammoth operation notifications to Slack."""
    
    def __init__(self, webhook_url: str, default_channel: str = None):
        self.webhook_url = webhook_url
        self.default_channel = default_channel
    
    def send_notification(self, 
                         message: str, 
                         channel: str = None,
                         username: str = "Mammoth Bot",
                         emoji: str = ":mammoth:",
                         color: str = "good") -> bool:
        """Send notification to Slack."""
        
        payload = {
            "username": username,
            "icon_emoji": emoji,
            "text": message
        }
        
        if channel or self.default_channel:
            payload["channel"] = channel or self.default_channel
        
        # Add color for rich formatting
        if color:
            payload["attachments"] = [{"color": color, "text": message}]
            payload.pop("text")  # Remove plain text when using attachments
        
        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    def notify_upload_success(self, dataset_id: int, file_name: str):
        """Notify successful upload."""
        message = f"✅ File upload successful!\nFile: {file_name}\nDataset ID: {dataset_id}"
        return self.send_notification(message, color="good")
    
    def notify_upload_failure(self, file_name: str, error: str):
        """Notify upload failure."""
        message = f"❌ File upload failed!\nFile: {file_name}\nError: {error}"
        return self.send_notification(message, color="danger")
    
    def notify_batch_completion(self, results: Dict[str, Any]):
        """Notify batch operation completion."""
        successful = len([r for r in results.values() if r is not None])
        total = len(results)
        
        message = f"📊 Batch upload completed!\n" \
                 f"Successful: {successful}/{total}\n" \
                 f"Failed: {total - successful}"
        
        color = "good" if successful == total else "warning"
        return self.send_notification(message, color=color)

# Usage with upload operations
def upload_with_slack_notifications(client, workspace_id, project_id, files):
    """Upload files with Slack notifications."""
    
    slack = MammothSlackNotifier(
        webhook_url=os.getenv("SLACK_WEBHOOK_URL"),
        default_channel="#data-alerts"
    )
    
    try:
        dataset_ids = client.files.upload_files(
            workspace_id=workspace_id,
            project_id=project_id,
            files=files
        )
        
        # Notify success
        if isinstance(files, list):
            for i, file_path in enumerate(files):
                slack.notify_upload_success(
                    dataset_ids[i] if i < len(dataset_ids) else None,
                    Path(file_path).name
                )
        else:
            slack.notify_upload_success(dataset_ids, Path(files).name)
        
        return dataset_ids
        
    except Exception as e:
        # Notify failure
        if isinstance(files, list):
            for file_path in files:
                slack.notify_upload_failure(Path(file_path).name, str(e))
        else:
            slack.notify_upload_failure(Path(files).name, str(e))
        raise
```

## Scheduled Operations

### Cron-based Scheduling

```python
import schedule
import time
import logging
from datetime import datetime, timedelta

class MammothScheduler:
    """Scheduler for regular Mammoth operations."""
    
    def __init__(self, mammoth_client: MammothClient):
        self.mammoth = mammoth_client
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def daily_data_sync(self, workspace_id: int, project_id: int):
        """Daily data synchronization job."""
        try:
            self.logger.info("Starting daily data sync")
            
            # Example: sync yesterday's data
            yesterday = datetime.now() - timedelta(days=1)
            data_file = f"/data/exports/daily_export_{yesterday.strftime('%Y%m%d')}.csv"
            
            if Path(data_file).exists():
                dataset_id = self.mammoth.files.upload_files(
                    workspace_id=workspace_id,
                    project_id=project_id,
                    files=data_file
                )
                self.logger.info(f"Daily sync completed: Dataset {dataset_id}")
            else:
                self.logger.warning(f"Daily export file not found: {data_file}")
                
        except Exception as e:
            self.logger.error(f"Daily sync failed: {e}")
            # Send alert (email, Slack, etc.)
    
    def weekly_cleanup(self, workspace_id: int, project_id: int):
        """Weekly cleanup of old files."""
        try:
            self.logger.info("Starting weekly cleanup")
            
            # Get files older than 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            
            files_list = self.mammoth.files.list_files(
                workspace_id=workspace_id,
                project_id=project_id,
                limit=100
            )
            
            old_files = [
                f for f in files_list.files 
                if f.created_at and f.created_at < cutoff_date
            ]
            
            if old_files:
                file_ids = [f.id for f in old_files if f.id]
                self.mammoth.files.delete_files(
                    workspace_id=workspace_id,
                    project_id=project_id,
                    file_ids=file_ids
                )
                self.logger.info(f"Deleted {len(file_ids)} old files")
            
        except Exception as e:
            self.logger.error(f"Weekly cleanup failed: {e}")
    
    def start_scheduler(self, workspace_id: int, project_id: int):
        """Start the scheduler with configured jobs."""
        
        # Schedule daily sync at 2 AM
        schedule.every().day.at("02:00").do(
            self.daily_data_sync, workspace_id, project_id
        )
        
        # Schedule weekly cleanup on Sundays at 3 AM
        schedule.every().sunday.at("03:00").do(
            self.weekly_cleanup, workspace_id, project_id
        )
        
        self.logger.info("Scheduler started")
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

# Usage
def run_scheduler():
    """Run the Mammoth scheduler."""
    
    client = MammothClient(
        api_key=os.getenv("MAMMOTH_API_KEY"),
        api_secret=os.getenv("MAMMOTH_API_SECRET")
    )
    
    scheduler = MammothScheduler(client)
    scheduler.start_scheduler(workspace_id=1, project_id=1)

# Run as a service
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_scheduler()
```

## Docker Integration

### Dockerfile for Mammoth Operations

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create data directory
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONPATH=/app/src
ENV DATA_DIR=/app/data

# Create non-root user
RUN useradd -m -u 1001 mammoth
RUN chown -R mammoth:mammoth /app
USER mammoth

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python src/health_check.py

# Default command
CMD ["python", "src/main.py"]
```

### Docker Compose for Complete Stack

```yaml
# docker-compose.yml
version: '3.8'

services:
  mammoth-etl:
    build: .
    environment:
      - MAMMOTH_API_KEY=${MAMMOTH_API_KEY}
      - MAMMOTH_API_SECRET=${MAMMOTH_API_SECRET}
      - MAMMOTH_WORKSPACE_ID=${MAMMOTH_WORKSPACE_ID}
      - MAMMOTH_PROJECT_ID=${MAMMOTH_PROJECT_ID}
      - POSTGRES_CONNECTION_STRING=${POSTGRES_CONNECTION_STRING}
      - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - postgres
    networks:
      - mammoth-network

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=etl_db
      - POSTGRES_USER=etl_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - mammoth-network

  redis:
    image: redis:7-alpine
    networks:
      - mammoth-network

volumes:
  postgres_data:

networks:
  mammoth-network:
    driver: bridge
```

## See Also

- [Best Practices Guide](best-practices.md) - Development best practices
- [Error Handling Guide](error-handling.md) - Robust error handling
- [Troubleshooting Guide](troubleshooting.md) - Common integration issues
- [API Reference](../api/client.md) - Complete SDK documentation
