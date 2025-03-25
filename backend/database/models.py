from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid

from .database import Base

class FileType(str, enum.Enum):
    PAYROLL = "payroll"
    FEEDBACK = "feedback"
    TEMPLATE = "template"
    OUTPUT = "output"

class ProcessingStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    VALIDATED = "validated"
    FAILED = "failed"
    COMPLETED = "completed"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    files = relationship("File", back_populates="owner")
    templates = relationship("Template", back_populates="owner")
    processing_jobs = relationship("ProcessingJob", back_populates="owner")

class File(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    original_filename = Column(String)
    saved_filename = Column(String)
    file_path = Column(String)
    file_type = Column(Enum(FileType))
    file_size = Column(Integer)
    mime_type = Column(String)
    upload_date = Column(DateTime, server_default=func.now())
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.UPLOADED)
    owner_id = Column(String, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="files")
    processing_jobs = relationship("ProcessingJob", back_populates="files")
    extracted_data = relationship("ExtractedData", back_populates="source_file", uselist=False)

class Template(Base):
    __tablename__ = "templates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    description = Column(String)
    template_type = Column(String)  # AR, PR, Invoice, ServiceLog
    content = Column(JSON)  # Store template structure as JSON
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    owner_id = Column(String, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="templates")

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    month = Column(String)
    year = Column(Integer)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PROCESSING)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    owner_id = Column(String, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="processing_jobs")
    files = relationship("File", back_populates="processing_jobs", secondary="job_files")
    validation_results = relationship("ValidationResult", back_populates="job")
    output_documents = relationship("OutputDocument", back_populates="job")

class JobFile(Base):
    __tablename__ = "job_files"

    job_id = Column(String, ForeignKey("processing_jobs.id"), primary_key=True)
    file_id = Column(String, ForeignKey("files.id"), primary_key=True)

class ExtractedData(Base):
    __tablename__ = "extracted_data"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String, ForeignKey("files.id"))
    data_type = Column(String)  # tutors, students, sessions
    content = Column(JSON)
    extraction_date = Column(DateTime, server_default=func.now())
    
    source_file = relationship("File", back_populates="extracted_data")

class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("processing_jobs.id"))
    issues = Column(JSON)  # List of validation issues
    total_sessions = Column(Integer)
    total_students = Column(Integer)
    total_tutors = Column(Integer)
    total_hours = Column(Float)
    processing_date = Column(DateTime, server_default=func.now())
    status = Column(Enum(ProcessingStatus))
    
    job = relationship("ProcessingJob", back_populates="validation_results")

class OutputDocument(Base):
    __tablename__ = "output_documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("processing_jobs.id"))
    document_type = Column(String)  # AR, PR, Invoice, ServiceLog
    file_path = Column(String)
    student_id = Column(String, nullable=True)  # For AR and PR
    generation_date = Column(DateTime, server_default=func.now())
    template_id = Column(String, ForeignKey("templates.id"))
    
    job = relationship("ProcessingJob", back_populates="output_documents")
    template = relationship("Template")

class TemplateCustomization(Base):
    __tablename__ = "template_customizations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = Column(String, ForeignKey("templates.id"))
    logo_path = Column(String, nullable=True)
    header_text = Column(String, nullable=True)
    footer_text = Column(String, nullable=True)
    font_family = Column(String, default="Arial")
    font_size = Column(Integer, default=12)
    primary_color = Column(String, default="#000000")
    secondary_color = Column(String, default="#808080")
    additional_settings = Column(JSON, nullable=True)
    
    template = relationship("Template")
