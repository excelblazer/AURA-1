from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ProcessingStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    VALIDATED = "validated"
    FAILED = "failed"
    COMPLETED = "completed"

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
    resolved: bool = False
    resolution_note: Optional[str] = None

class ValidationResultBase(BaseModel):
    issues: List[ValidationIssue]
    total_sessions: int
    total_students: int
    total_tutors: int
    total_hours: float
    status: ProcessingStatus

class ValidationResultCreate(ValidationResultBase):
    job_id: str

class ValidationResult(ValidationResultBase):
    id: str
    job_id: str
    processing_date: datetime

    class Config:
        orm_mode = True
        json_encoders = {datetime: lambda v: v.isoformat()}

class ValidationResolution(BaseModel):
    issue_id: int
    resolution: str
    corrected_value: Optional[str] = None

class ValidationSummary(BaseModel):
    total_issues: int
    errors: int
    warnings: int
    resolved: int
    unresolved: int
    by_type: Dict[str, int]
    by_severity: Dict[str, int]
