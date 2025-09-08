"""
Files API client for managing files and datasets in Mammoth.
"""

import os
from pathlib import Path
from typing import List, Optional, Union, BinaryIO
from ..models.files import (
    FilesList, FileDetails, FileSchema, FilePatchRequest, 
    FilePatchData, FilePatchOperation, FilePatchPath
)
from ..models.jobs import ObjectJobSchema


class FilesAPI:
    """Client for interacting with Mammoth Files API."""
    
    def __init__(self, client):
        self._client = client
    
    def list_files(
        self,
        workspace_id: int,
        project_id: int,
        fields: Optional[str] = None,
        file_ids: Optional[List[int]] = None,
        names: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        sort: Optional[str] = None
    ) -> FilesList:
        """
        List files in a project with optional filtering and pagination.
        
        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project  
            fields: Fields to return (e.g., "__standard", "__full", "__min", or comma-separated)
            file_ids: List of specific file IDs to retrieve
            names: List of file names to filter by
            statuses: List of statuses to filter by
            created_at: Date range filter for creation date (format: "(from:'YYYY-MM-DDTHH:MM:SSZ',to:'YYYY-MM-DDTHH:MM:SSZ')")
            updated_at: Date range filter for update date  
            limit: Maximum number of results (0-100, default: 50)
            offset: Number of results to skip (default: 0)
            sort: Sort specification (e.g., "(id:asc),(name:desc)")
            
        Returns:
            FilesList: List of files with pagination info
            
        Raises:
            MammothAPIError: If the API request fails
        """
        params = {}
        
        if fields:
            params["fields"] = fields
        if file_ids:
            params["id"] = ",".join(str(fid) for fid in file_ids)
        if names:
            params["name"] = ",".join(names)
        if statuses:
            params["status"] = ",".join(statuses)
        if created_at:
            params["created_at"] = created_at
        if updated_at:
            params["updated_at"] = updated_at
        if limit != 50:
            params["limit"] = limit
        if offset != 0:
            params["offset"] = offset
        if sort:
            params["sort"] = sort
            
        response = self._client._request(
            "GET",
            f"/workspaces/{workspace_id}/projects/{project_id}/files",
            params=params
        )
        return FilesList(**response)
    
    def get_file_details(
        self,
        workspace_id: int,
        project_id: int,
        file_id: int,
        fields: Optional[str] = None
    ) -> FileSchema:
        """
        Get detailed information about a specific file.
        
        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project
            file_id: ID of the file
            fields: Fields to return (default: "__standard")
            
        Returns:
            FileSchema: Detailed file information
            
        Raises:
            MammothAPIError: If the API request fails
        """
        params = {}
        if fields:
            params["fields"] = fields
            
        response = self._client._request(
            "GET",
            f"/workspaces/{workspace_id}/projects/{project_id}/files/{file_id}",
            params=params
        )
        file_details = FileDetails(**response)
        return file_details.file
    
    def upload_files(
        self,
        workspace_id: int,
        project_id: int,
        files: Union[List[Union[str, Path, BinaryIO]], str, Path, BinaryIO],
        folder_resource_id: Optional[str] = None,
        append_to_ds_id: Optional[int] = None,
        override_target_schema: Optional[bool] = None,
        wait_for_completion: bool = True,
        timeout: int = 300
    ) -> Union[List[int], int, None]:
        """
        Upload one or more files to create datasets. Each file will be treated as a
        separate dataset. If the file path contains a folder structure, that structure
        will be preserved, and the files will be placed in their respective folders.
        
        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project
            files: File(s) to upload - can be file paths, Path objects, or file-like objects
            folder_resource_id: Resource ID of target folder. This is the resource ID of the Mammoth folder
            append_to_ds_id: Dataset ID to append to (if appending to existing dataset)
            override_target_schema: Whether to override target schema when appending
            wait_for_completion: Whether to wait for upload processing to complete
            timeout: Timeout in seconds when waiting for completion
            
        Returns:
            List of dataset IDs if multiple files uploaded, single dataset ID if one file
            
        Raises:
            MammothAPIError: If the API request fails
            MammothJobTimeoutError: If job processing times out
            MammothJobFailedError: If job processing fails
        """
        # Normalize files to list
        if not isinstance(files, list):
            files = [files]
        
        # Prepare files for upload
        file_data = []
        opened_files = []
        
        try:
            for file_input in files:
                if isinstance(file_input, (str, Path)):
                    file_path = Path(file_input)
                    if not file_path.exists():
                        raise ValueError(f"File not found: {file_path}")
                    file_obj = open(file_path, 'rb')
                    opened_files.append(file_obj)
                    file_data.append(('files', (file_path.name, file_obj, 'application/octet-stream')))
                else:
                    # Assume it's a file-like object
                    filename = getattr(file_input, 'name', 'uploaded_file')
                    if hasattr(filename, 'split'):
                        filename = os.path.basename(filename)
                    file_data.append(('files', (filename, file_input, 'application/octet-stream')))
            
            # Prepare parameters
            params = {}
            if folder_resource_id:
                params["folder_resource_id"] = folder_resource_id
            if append_to_ds_id:
                params["append_to_ds_id"] = append_to_ds_id
            if override_target_schema is not None:
                params["override_target_schema"] = override_target_schema
            
            # Make upload request
            response = self._client._request(
                "POST",
                f"/workspaces/{workspace_id}/projects/{project_id}/files",
                params=params,
                files=file_data
            )
            
        finally:
            # Clean up opened files
            for file_obj in opened_files:
                file_obj.close()
        
        # Parse job response
        obj_jobs = [ObjectJobSchema(**obj_job) for obj_job in response]
        job_ids = [job.job_id for job in obj_jobs if job.job_id is not None]
        
        if not wait_for_completion:
            return job_ids
        
        # Wait for jobs to complete and extract dataset IDs
        if job_ids:
            completed_jobs = self._client.jobs.wait_for_jobs(job_ids, timeout=timeout)
            dataset_ids = self._client.jobs.extract_dataset_ids(completed_jobs)
            
            # Filter out None values
            valid_dataset_ids = [ds_id for ds_id in dataset_ids if ds_id is not None]
            
            if len(files) == 1:
                return valid_dataset_ids[0] if valid_dataset_ids else None
            return valid_dataset_ids
        
        return [] if len(files) > 1 else None
    
    def delete_file(
        self,
        workspace_id: int,
        project_id: int, 
        file_id: int
    ) -> None:
        """
        Delete a specific file.
        
        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project
            file_id: ID of the file to delete
            
        Raises:
            MammothAPIError: If the API request fails
        """
        self._client._request(
            "DELETE",
            f"/workspaces/{workspace_id}/projects/{project_id}/files/{file_id}"
        )
    
    def delete_files(
        self,
        workspace_id: int,
        project_id: int,
        file_ids: List[int]
    ) -> None:
        """
        Delete multiple files.
        
        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project
            file_ids: List of file IDs to delete
            
        Raises:
            MammothAPIError: If the API request fails
        """
        params = {"ids": ",".join(str(fid) for fid in file_ids)}
        self._client._request(
            "DELETE",
            f"/workspaces/{workspace_id}/projects/{project_id}/files",
            params=params
        )
    
    def update_file_config(
        self,
        workspace_id: int,
        project_id: int,
        file_id: int,
        patch_request: FilePatchRequest
    ) -> ObjectJobSchema:
        """
        Update file configuration (e.g., set password, extract sheets).
        
        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project
            file_id: ID of the file to update
            patch_request: Configuration changes to apply
            
        Returns:
            ObjectJobSchema: Job information for the update operation
            
        Raises:
            MammothAPIError: If the API request fails
        """
        response = self._client._request(
            "PATCH",
            f"/workspaces/{workspace_id}/projects/{project_id}/files/{file_id}",
            json=patch_request.dict()
        )
        return ObjectJobSchema(**response)
    
    def set_file_password(
        self,
        workspace_id: int,
        project_id: int,
        file_id: int,
        password: str
    ) -> ObjectJobSchema:
        """
        Set password for a password-protected file.
        
        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project  
            file_id: ID of the file
            password: Password to set
            
        Returns:
            ObjectJobSchema: Job information for the update operation
        """
        patch_data = FilePatchData(
            op=FilePatchOperation.REPLACE,
            path=FilePatchPath.PASSWORD,
            value=password
        )
        patch_request = FilePatchRequest(patch=[patch_data])
        return self.update_file_config(workspace_id, project_id, file_id, patch_request)
    
    def extract_sheets(
        self,
        workspace_id: int,
        project_id: int,
        file_id: int,
        sheets: List[str],
        delete_file_after_extract: bool = True,
        combine_after_extract: bool = False
    ) -> ObjectJobSchema:
        """
        Extract specific sheets from an Excel file.
        
        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project
            file_id: ID of the Excel file
            sheets: List of sheet names to extract
            delete_file_after_extract: Whether to delete main file after extraction
            combine_after_extract: Whether to combine sheets after extraction
            
        Returns:
            ObjectJobSchema: Job information for the extraction operation
        """
        from ..models.files import ExtractSheetsPatch
        
        extract_config = ExtractSheetsPatch(
            sheets=sheets,
            delete_file_after_extract=delete_file_after_extract,
            combine_after_extract=combine_after_extract
        )
        
        patch_data = FilePatchData(
            op=FilePatchOperation.REPLACE,
            path=FilePatchPath.EXTRACT_SHEETS,
            value=extract_config
        )
        patch_request = FilePatchRequest(patch=[patch_data])
        return self.update_file_config(workspace_id, project_id, file_id, patch_request)
