"""
Jobs API client for tracking asynchronous operations in Mammoth.
"""

import time
from typing import List, Optional
from ..models.jobs import JobResponse, JobsGetResponse, JobSchema, JobStatus
from ..exceptions import MammothJobTimeoutError, MammothJobFailedError


class JobsAPI:
    """Client for interacting with Mammoth Jobs API."""
    
    def __init__(self, client):
        self._client = client
    
    def get_job(self, job_id: int) -> JobSchema:
        """
        Get details of a specific job by its ID.
        
        Args:
            job_id: Unique identifier of the job
            
        Returns:
            JobSchema: Job details including status and response
            
        Raises:
            MammothAPIError: If the API request fails
        """
        response = self._client._request("GET", f"/jobs/{job_id}")
        job_response = JobResponse(**response)
        return job_response.job
    
    def get_jobs(self, job_ids: List[int]) -> List[JobSchema]:
        """
        Get details of multiple jobs by their IDs.
        
        Args:
            job_ids: List of job IDs to retrieve
            
        Returns:
            List[JobSchema]: List of job details
            
        Raises:
            MammothAPIError: If the API request fails
        """
        params = {"job_ids": ",".join(str(jid) for jid in job_ids)}
        response = self._client._request("GET", "/jobs", params=params)
        jobs_response = JobsGetResponse(**response)
        return jobs_response.jobs
    
    def wait_for_job(
        self, 
        job_id: int, 
        timeout: int = 300,
        poll_interval: int = 5
    ) -> JobSchema:
        """
        Wait for a job to complete, polling until success or failure.
        
        Args:
            job_id: ID of the job to wait for
            timeout: Maximum time to wait in seconds (default: 300)
            poll_interval: Time between polls in seconds (default: 5)
            
        Returns:
            JobSchema: Final job details when completed
            
        Raises:
            MammothJobTimeoutError: If job doesn't complete within timeout
            MammothJobFailedError: If job fails during execution
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            job = self.get_job(job_id)
            
            if job.status == JobStatus.SUCCESS:
                return job
            elif job.status in [JobStatus.FAILURE, JobStatus.ERROR]:
                failure_reason = None
                if hasattr(job, 'response') and isinstance(job.response, dict):
                    failure_reason = job.response.get('failure_reason')
                raise MammothJobFailedError(job_id, failure_reason)
            elif job.status == JobStatus.PROCESSING:
                time.sleep(poll_interval)
            else:
                # Unknown status, continue polling
                time.sleep(poll_interval)
        
        raise MammothJobTimeoutError(job_id, timeout)
    
    def wait_for_jobs(
        self,
        job_ids: List[int],
        timeout: int = 300,
        poll_interval: int = 5
    ) -> List[JobSchema]:
        """
        Wait for multiple jobs to complete.
        
        Args:
            job_ids: List of job IDs to wait for
            timeout: Maximum time to wait in seconds (default: 300) 
            poll_interval: Time between polls in seconds (default: 5)
            
        Returns:
            List[JobSchema]: Final job details for all completed jobs
            
        Raises:
            MammothJobTimeoutError: If any job doesn't complete within timeout
            MammothJobFailedError: If any job fails during execution
        """
        completed_jobs = []
        remaining_job_ids = job_ids.copy()
        start_time = time.time()
        
        while remaining_job_ids and time.time() - start_time < timeout:
            jobs = self.get_jobs(remaining_job_ids)
            
            for job in jobs:
                if job.status == JobStatus.SUCCESS:
                    completed_jobs.append(job)
                    remaining_job_ids.remove(job.id)
                elif job.status in [JobStatus.FAILURE, JobStatus.ERROR]:
                    failure_reason = None
                    if hasattr(job, 'response') and isinstance(job.response, dict):
                        failure_reason = job.response.get('failure_reason')
                    raise MammothJobFailedError(job.id, failure_reason)
            
            if remaining_job_ids:
                time.sleep(poll_interval)
        
        if remaining_job_ids:
            raise MammothJobTimeoutError(remaining_job_ids[0], timeout)
            
        return completed_jobs
    
    def extract_dataset_ids(self, jobs: List[JobSchema]) -> List[Optional[int]]:
        """
        Extract dataset IDs from completed job responses.
        
        Args:
            jobs: List of completed job schemas
            
        Returns:
            List of dataset IDs (None if not found in response)
        """
        dataset_ids = []
        for job in jobs:
            ds_id = None
            if (hasattr(job, 'response') and 
                isinstance(job.response, dict) and 
                'ds_id' in job.response):
                ds_id = job.response['ds_id']
            dataset_ids.append(ds_id)
        return dataset_ids
