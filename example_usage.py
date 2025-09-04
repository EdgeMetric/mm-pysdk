"""
Example usage of the Mammoth Analytics Python SDK.

This script demonstrates how to:
1. Initialize the client with authentication
2. Upload files to create datasets
3. Track job progress
4. List and manage files
5. Handle errors gracefully
"""

import os
from pathlib import Path
from datetime import datetime, timedelta

from mammoth import MammothClient
from mammoth.exceptions import MammothAPIError, MammothJobTimeoutError
from mammoth.models.files import FilePatchRequest, FilePatchData, FilePatchOperation, FilePatchPath
from mammoth.utils.helpers import format_date_range


def main():
    """Main example function demonstrating SDK usage."""
    
    # Initialize the Mammoth client
    # You can get these credentials from your Mammoth dashboard
    client = MammothClient(
        api_key=os.getenv("MAMMOTH_API_KEY", "your-api-key"),
        api_secret=os.getenv("MAMMOTH_API_SECRET", "your-api-secret"),
        base_url="https://api.mammoth.io"  # Replace with your instance URL
    )
    
    # Test connection
    print("Testing connection to Mammoth API...")
    if client.test_connection():
        print("✓ Connected successfully!")
    else:
        print("✗ Connection failed. Check your credentials.")
        return
    
    # Set your workspace and project IDs
    workspace_id = 1  # Replace with your workspace ID
    project_id = 1    # Replace with your project ID
    
    try:
        # Example 1: Upload a single file and wait for completion
        print("\n=== Example 1: Upload Single File ===")
        
        # Create a sample CSV file for demonstration
        sample_csv = Path("sample_data.csv")
        sample_csv.write_text("id,name,value\n1,Alice,100\n2,Bob,200\n3,Charlie,300\n")
        
        try:
            print(f"Uploading {sample_csv.name}...")
            dataset_id = client.files.upload_files(
                workspace_id=workspace_id,
                project_id=project_id,
                files=sample_csv,
                wait_for_completion=True,
                timeout=300  # 5 minutes
            )
            print(f"✓ File uploaded successfully! Dataset ID: {dataset_id}")
            
        except MammothJobTimeoutError as e:
            print(f"✗ Upload timed out: {e}")
        except MammothAPIError as e:
            print(f"✗ Upload failed: {e}")
        finally:
            # Clean up sample file
            if sample_csv.exists():
                sample_csv.unlink()
        
        # Example 2: Upload multiple files
        print("\n=== Example 2: Upload Multiple Files ===")
        
        # Create multiple sample files
        files_to_upload = []
        for i in range(2):
            file_path = Path(f"sample_data_{i+1}.csv")
            file_path.write_text(f"id,category,amount\n1,Category{i+1},50\n2,Category{i+1},75\n")
            files_to_upload.append(file_path)
        
        try:
            print(f"Uploading {len(files_to_upload)} files...")
            dataset_ids = client.files.upload_files(
                workspace_id=workspace_id,
                project_id=project_id,
                files=files_to_upload,
                wait_for_completion=True
            )
            print(f"✓ Files uploaded successfully! Dataset IDs: {dataset_ids}")
            
        except Exception as e:
            print(f"✗ Multi-file upload failed: {e}")
        finally:
            # Clean up sample files
            for file_path in files_to_upload:
                if file_path.exists():
                    file_path.unlink()
        
        # Example 3: List files with filtering
        print("\n=== Example 3: List Files ===")
        
        try:
            # List recent files
            files_list = client.files.list_files(
                workspace_id=workspace_id,
                project_id=project_id,
                fields="__standard",
                limit=10,
                sort="(created_at:desc)"
            )
            
            print(f"Found {len(files_list.files)} files:")
            for file in files_list.files[:5]:  # Show first 5
                print(f"  - {file.name} (ID: {file.id}, Status: {file.status})")
                
            # List files from the last week
            week_ago = datetime.now() - timedelta(days=7)
            now = datetime.now()
            date_filter = format_date_range(week_ago, now)
            
            recent_files = client.files.list_files(
                workspace_id=workspace_id,
                project_id=project_id,
                created_at=date_filter,
                statuses=["processed", "processing"]
            )
            print(f"Files from last week: {len(recent_files.files)}")
            
        except MammothAPIError as e:
            print(f"✗ Failed to list files: {e}")
        
        # Example 4: Get file details
        print("\n=== Example 4: Get File Details ===")
        
        if files_list.files:
            file_to_examine = files_list.files[0]
            try:
                file_details = client.files.get_file_details(
                    workspace_id=workspace_id,
                    project_id=project_id,
                    file_id=file_to_examine.id,
                    fields="__full"
                )
                
                print(f"File Details for '{file_details.name}':")
                print(f"  - Status: {file_details.status}")
                print(f"  - Created: {file_details.created_at}")
                print(f"  - Size: {len(file_details.name)} chars")
                
                if file_details.additional_info and file_details.additional_info.final_ds_id:
                    print(f"  - Dataset ID: {file_details.additional_info.final_ds_id}")
                    
            except MammothAPIError as e:
                print(f"✗ Failed to get file details: {e}")
        
        # Example 5: Working with jobs directly
        print("\n=== Example 5: Working with Jobs ===")
        
        # Create a sample file and upload without waiting
        sample_file = Path("async_upload.csv")
        sample_file.write_text("x,y,z\n1,2,3\n4,5,6\n")
        
        try:
            print("Starting async upload...")
            job_ids = client.files.upload_files(
                workspace_id=workspace_id,
                project_id=project_id,
                files=sample_file,
                wait_for_completion=False  # Don't wait
            )
            
            if job_ids:
                job_id = job_ids[0] if isinstance(job_ids, list) else job_ids
                print(f"Upload started with job ID: {job_id}")
                
                # Monitor job manually
                print("Monitoring job progress...")
                completed_job = client.jobs.wait_for_job(job_id, timeout=120)
                
                print(f"Job completed with status: {completed_job.status}")
                if completed_job.response and 'ds_id' in completed_job.response:
                    dataset_id = completed_job.response['ds_id']
                    print(f"Created dataset ID: {dataset_id}")
                    
        except Exception as e:
            print(f"✗ Async upload example failed: {e}")
        finally:
            if sample_file.exists():
                sample_file.unlink()
        
        # Example 6: Handle password-protected files (simulated)
        print("\n=== Example 6: Password-Protected Files ===")
        
        # This example shows how you would handle a password-protected file
        # In practice, you'd first upload the file, then set the password if needed
        
        print("Example of setting password for a protected file:")
        print("client.files.set_file_password(workspace_id, project_id, file_id, 'password123')")
        
        # Example 7: Extract sheets from Excel files (simulated)
        print("\n=== Example 7: Extract Excel Sheets ===")
        
        print("Example of extracting specific sheets from Excel file:")
        print("client.files.extract_sheets(")
        print("    workspace_id, project_id, file_id,")
        print("    sheets=['Sheet1', 'Sheet2'],")
        print("    delete_file_after_extract=True")
        print(")")
        
        print("\n✓ All examples completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


def advanced_examples():
    """Advanced usage examples."""
    
    print("\n=== Advanced Examples ===")
    
    # Using context manager
    with MammothClient(
        api_key=os.getenv("MAMMOTH_API_KEY"),
        api_secret=os.getenv("MAMMOTH_API_SECRET")
    ) as client:
        
        workspace_id = 1
        project_id = 1
        
        # Batch operations
        print("Batch file operations example:")
        
        try:
            # Upload multiple files to specific folder
            files = ["data1.csv", "data2.csv"]  # These would be real files
            
            # Simulated upload with folder targeting
            print("Would upload files to specific folder:")
            print("dataset_ids = client.files.upload_files(")
            print("    workspace_id=workspace_id,")
            print("    project_id=project_id,") 
            print("    files=files,")
            print("    folder_resource_id='folder_123'")
            print(")")
            
            # Error handling example
            print("\nError handling patterns:")
            
        except MammothAPIError as e:
            print(f"API Error: {e.message}")
            print(f"Status Code: {e.status_code}")
            print(f"Response: {e.response_body}")
            
        except MammothJobTimeoutError as e:
            print(f"Job timeout: {e.message}")
            print(f"Job ID: {e.details['job_id']}")
            
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    print("Mammoth Analytics SDK Example")
    print("=============================")
    print()
    print("Make sure to set your environment variables:")
    print("  export MAMMOTH_API_KEY='your-api-key'")
    print("  export MAMMOTH_API_SECRET='your-api-secret'")
    print()
    
    if not os.getenv("MAMMOTH_API_KEY") or not os.getenv("MAMMOTH_API_SECRET"):
        print("⚠️  Warning: API credentials not found in environment variables")
        print("   Using placeholder values - update the code with real credentials")
        print()
    
    main()
    advanced_examples()
