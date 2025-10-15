"""Job queue manager for asynchronous video generation."""

import asyncio
import json
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict


class JobStatus(Enum):
    """Job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    """Represents a video generation job."""
    job_id: str
    status: JobStatus
    script: str
    options: Dict[str, Any]
    created_at: str
    updated_at: str
    progress: int = 0
    error: Optional[str] = None
    output_file: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        return data


class JobManager:
    """Manages video generation jobs."""
    
    def __init__(self, storage_dir: Path):
        """Initialize job manager."""
        self.storage_dir = storage_dir
        self.jobs_file = storage_dir / "jobs.json"
        self.jobs: Dict[str, Job] = {}
        self.active_jobs: set = set()
        self._load_jobs()
    
    def _load_jobs(self) -> None:
        """Load jobs from disk."""
        if self.jobs_file.exists():
            try:
                with open(self.jobs_file, 'r') as f:
                    jobs_data = json.load(f)
                    for job_id, job_data in jobs_data.items():
                        job_data['status'] = JobStatus(job_data['status'])
                        self.jobs[job_id] = Job(**job_data)
            except Exception as e:
                print(f"Error loading jobs: {e}")
    
    def _save_jobs(self) -> None:
        """Save jobs to disk."""
        try:
            with open(self.jobs_file, 'w') as f:
                jobs_data = {job_id: job.to_dict() for job_id, job in self.jobs.items()}
                json.dump(jobs_data, f, indent=2)
        except Exception as e:
            print(f"Error saving jobs: {e}")
    
    def create_job(self, script: str, options: Dict[str, Any]) -> str:
        """Create a new job."""
        job_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        job = Job(
            job_id=job_id,
            status=JobStatus.PENDING,
            script=script,
            options=options,
            created_at=now,
            updated_at=now
        )
        
        self.jobs[job_id] = job
        self._save_jobs()
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        return self.jobs.get(job_id)
    
    def update_job(
        self,
        job_id: str,
        status: Optional[JobStatus] = None,
        progress: Optional[int] = None,
        error: Optional[str] = None,
        output_file: Optional[str] = None
    ) -> None:
        """Update job status and details."""
        if job_id not in self.jobs:
            return
        
        job = self.jobs[job_id]
        if status:
            job.status = status
        if progress is not None:
            job.progress = progress
        if error:
            job.error = error
        if output_file:
            job.output_file = output_file
        
        job.updated_at = datetime.utcnow().isoformat()
        self._save_jobs()
    
    def list_jobs(self, limit: int = 50) -> list[Job]:
        """List recent jobs."""
        sorted_jobs = sorted(
            self.jobs.values(),
            key=lambda j: j.created_at,
            reverse=True
        )
        return sorted_jobs[:limit]
    
    def delete_job(self, job_id: str) -> bool:
        """Delete a job."""
        if job_id in self.jobs:
            del self.jobs[job_id]
            self._save_jobs()
            return True
        return False
    
    async def process_job_queue(self, max_concurrent: int = 2) -> None:
        """Process pending jobs from queue."""
        # This will be implemented by the video generator service
        pass

