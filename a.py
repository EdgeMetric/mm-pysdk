import os
import csv
import psycopg2
from mammoth import MammothClient
from mammoth.exceptions import (
    MammothAPIError,
    MammothAuthError,
    MammothJobTimeoutError,
    MammothJobFailedError
)

def download_from_postgres(db_url, query, output_file='data.csv'):
    """
    Connect to PostgreSQL, execute the query, and save results to a CSV file.
    
    :param db_url: PostgreSQL connection string (e.g., 'postgresql://user:pass@host:port/dbname')
    :param query: SQL query to execute (e.g., 'SELECT * FROM my_table')
    :param output_file: Path to save the CSV file
    """
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write headers
            writer.writerow([desc[0] for desc in cur.description])
            # Write data rows
            writer.writerows(rows)
        
        print(f"Data downloaded from PostgreSQL and saved to {output_file}")
    except psycopg2.Error as e:
        raise RuntimeError(f"PostgreSQL error: {e}")
    finally:
        if conn:
            conn.close()

def upload_to_mammoth(client: MammothClient, workspace_id, project_id, file_path):
    """
    Upload the CSV file to Mammoth Analytics using the SDK.
    
    :param client: Initialized MammothClient
    :param workspace_id: Mammoth workspace ID (int)
    :param project_id: Mammoth project ID (int)
    :param file_path: Path to the CSV file to upload
    :return: Dataset ID
    """
    try:
        dataset_id = client.files.upload_files(
            workspace_id=workspace_id,
            project_id=project_id,
            files=file_path
        )
        print(f"Uploaded to Mammoth. Created dataset ID: {dataset_id}")
        return dataset_id
    except MammothAuthError:
        raise RuntimeError("Authentication failed - check your API credentials")
    except MammothJobTimeoutError as e:
        raise RuntimeError(f"Upload timed out: {e}")
    except MammothJobFailedError as e:
        raise RuntimeError(f"Upload failed: {e.details.get('failure_reason', 'Unknown error')}")
    except MammothAPIError as e:
        raise RuntimeError(f"API error: {e.message} (Status: {e.status_code})")

if __name__ == "__main__":
    # Load Mammoth credentials from environment variables (as recommended in docs)
    api_key = "tP6D6FEdU9hlQ1c3tmrBveQGRZz0" 
    api_secret = "qvJtTOXpi5KqwnwfZRIQLYxewzPqJjSNA5" 
    base_url = os.getenv("MAMMOTH_BASE_URL", "https://live.mammoth.io/api/v2")
    
    if not api_key or not api_secret:
        raise ValueError("MAMMOTH_API_KEY and MAMMOTH_API_SECRET must be set in environment variables.")
    
    # Example usage - replace with your actual values
    # PostgreSQL connection string (set as env var or hardcode carefully)
    db_url = "postgresql://postgres:appPasswordComplex@db.mrmkgkuggzbehaospsds.supabase.co:5432/postgres"
    query = "SELECT * FROM store_transactions LIMIT 100"  # Replace with your SQL query
    workspace_id = 2  # Replace with your Mammoth workspace ID
    project_id = 9    # Replace with your Mammoth project ID
    output_file = "postgres_data.csv"
    
    # Step 1: Download from Postgres
    download_from_postgres(db_url, query, output_file)
    
    # Step 2: Initialize Mammoth client
    client = MammothClient(
        api_key=api_key,
        api_secret=api_secret,
        base_url=base_url
    )
    
    # Step 3: Upload to Mammoth
    upload_to_mammoth(client, workspace_id, project_id, output_file)
    
    # Optional: Clean up the local CSV file after upload
    # os.remove(output_file)
