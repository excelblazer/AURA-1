from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class FileType(str, Enum):
    PAYROLL = "payroll"
    FEEDBACK = "feedback"
    TEMPLATE = "template"
    OUTPUT = "output"

class ProcessingStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    VALIDATED = "validated"
    FAILED = "failed"
    COMPLETED = "completed"

class FileBase(BaseModel):
    original_filename: str
    saved_filename: str
    file_path: str
    file_type: FileType
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    status: ProcessingStatus = ProcessingStatus.UPLOADED

class FileCreate(FileBase):
    id: str
    owner_id: Optional[str] = None

class FileUpload(FileBase):
    id: str
    upload_date: datetime
    owner_id: Optional[str] = None

    class Config:
        orm_mode = True
        json_encoders = {datetime: lambda v: v.isoformat()}

class ValidationIssue(BaseModel):
    issue_type: str
    description: str
    severity: str = "warning"  # warning, error
    student_id: Optional[str] = None
    tutor_id: Optional[str] = None
    session_date: Optional[str] = None
    field: Optional[str] = None
    value: Optional[str] = None
    suggested_correction: Optional[str] = None

class ValidationResult(BaseModel):
    id: str
    file_id: str
    issues: List[ValidationIssue]
    total_sessions: int
    total_students: int
    total_tutors: int
    total_hours: float
    processing_date: datetime
    status: ProcessingStatus

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ExtractedDataBase(BaseModel):
    data_type: str  # tutors, students, sessions
    content: dict

class ExtractedDataCreate(ExtractedDataBase):
    file_id: str

class ExtractedData(ExtractedDataBase):
    id: str
    file_id: str
    extraction_date: datetime

    class Config:
        orm_mode = True
        json_encoders = {datetime: lambda v: v.isoformat()}