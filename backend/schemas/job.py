from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from .validation import ProcessingStatus

class ProcessingJobBase(BaseModel):
    month: str
    year: int
    status: ProcessingStatus = ProcessingStatus.PROCESSING

class ProcessingJobCreate(ProcessingJobBase):
    owner_id: str
    file_ids: List[str]

class ProcessingJob(ProcessingJobBase):
    id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    owner_id: str

    class Config:
        orm_mode = True
        json_encoders = {datetime: lambda v: v.isoformat()}

class ProcessingJobWithDetails(ProcessingJob):
    files: List[Dict[str, Any]]
    validation_results: Optional[Dict[str, Any]] = None
    output_documents: List[Dict[str, Any]] = []

class OutputDocumentBase(BaseModel):
    document_type: str  # AR, PR, Invoice, ServiceLog
    file_path: str
    student_id: Optional[str] = None  # For AR and PR

class OutputDocumentCreate(OutputDocumentBase):
    job_id: str
    template_id: str

class OutputDocument(OutputDocumentBase):
    id: str
    job_id: str
    generation_date: datetime
    template_id: str

    class Config:
        orm_mode = True
        json_encoders = {datetime: lambda v: v.isoformat()}
