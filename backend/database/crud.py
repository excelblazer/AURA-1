from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from . import models
from ..schemas import file as file_schema
from ..schemas import template as template_schema
from ..schemas import validation as validation_schema
from ..schemas import user as user_schema
from ..auth.security import get_password_hash

# File CRUD operations
def create_file(db: Session, file: file_schema.FileCreate) -> models.File:
    """Create a new file record in the database"""
    db_file = models.File(
        id=file.id,
        original_filename=file.original_filename,
        saved_filename=file.saved_filename,
        file_path=file.file_path,
        file_type=file.file_type,
        file_size=file.file_size,
        mime_type=file.mime_type,
        upload_date=datetime.now(),
        status=file.status,
        owner_id=file.owner_id
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_file(db: Session, file_id: str) -> Optional[models.File]:
    """Get a file by ID"""
    return db.query(models.File).filter(models.File.id == file_id).first()

def get_files_by_type(db: Session, file_type: str, skip: int = 0, limit: int = 100) -> List[models.File]:
    """Get files by type"""
    return db.query(models.File).filter(models.File.file_type == file_type).offset(skip).limit(limit).all()

def get_files_by_owner(db: Session, owner_id: str, skip: int = 0, limit: int = 100) -> List[models.File]:
    """Get files by owner ID"""
    return db.query(models.File).filter(models.File.owner_id == owner_id).offset(skip).limit(limit).all()

def update_file_status(db: Session, file_id: str, status: str) -> Optional[models.File]:
    """Update file status"""
    db_file = get_file(db, file_id)
    if db_file:
        db_file.status = status
        db.commit()
        db.refresh(db_file)
    return db_file

# Template CRUD operations
def create_template(db: Session, template: template_schema.TemplateCreate) -> models.Template:
    """Create a new template"""
    db_template = models.Template(
        name=template.name,
        description=template.description,
        template_type=template.template_type,
        content=template.content,
        is_default=template.is_default,
        owner_id=template.owner_id
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def get_template(db: Session, template_id: str) -> Optional[models.Template]:
    """Get a template by ID"""
    return db.query(models.Template).filter(models.Template.id == template_id).first()

def get_templates_by_type(db: Session, template_type: str, skip: int = 0, limit: int = 100) -> List[models.Template]:
    """Get templates by type"""
    return db.query(models.Template).filter(models.Template.template_type == template_type).offset(skip).limit(limit).all()

def get_default_template(db: Session, template_type: str) -> Optional[models.Template]:
    """Get default template by type"""
    return db.query(models.Template).filter(
        models.Template.template_type == template_type,
        models.Template.is_default == True
    ).first()

def update_template(db: Session, template_id: str, template_data: Dict[str, Any]) -> Optional[models.Template]:
    """Update template"""
    db_template = get_template(db, template_id)
    if db_template:
        for key, value in template_data.items():
            setattr(db_template, key, value)
        db.commit()
        db.refresh(db_template)
    return db_template

# Template Customization CRUD operations
def create_template_customization(db: Session, customization: template_schema.TemplateCustomizationCreate) -> models.TemplateCustomization:
    """Create a new template customization"""
    db_customization = models.TemplateCustomization(
        template_id=customization.template_id,
        logo_path=customization.logo_path,
        header_text=customization.header_text,
        footer_text=customization.footer_text,
        font_family=customization.font_family,
        font_size=customization.font_size,
        primary_color=customization.primary_color,
        secondary_color=customization.secondary_color,
        additional_settings=customization.additional_settings
    )
    db.add(db_customization)
    db.commit()
    db.refresh(db_customization)
    return db_customization

def get_template_customization(db: Session, template_id: str) -> Optional[models.TemplateCustomization]:
    """Get template customization by template ID"""
    return db.query(models.TemplateCustomization).filter(
        models.TemplateCustomization.template_id == template_id
    ).first()

def update_template_customization(db: Session, template_id: str, customization_data: Dict[str, Any]) -> Optional[models.TemplateCustomization]:
    """Update template customization"""
    db_customization = get_template_customization(db, template_id)
    if db_customization:
        for key, value in customization_data.items():
            setattr(db_customization, key, value)
        db.commit()
        db.refresh(db_customization)
    return db_customization

# Processing Job CRUD operations
def create_processing_job(db: Session, job_data: Dict[str, Any]) -> models.ProcessingJob:
    """Create a new processing job"""
    db_job = models.ProcessingJob(
        month=job_data.get("month"),
        year=job_data.get("year"),
        status=job_data.get("status", models.ProcessingStatus.PROCESSING),
        owner_id=job_data.get("owner_id")
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_processing_job(db: Session, job_id: str) -> Optional[models.ProcessingJob]:
    """Get a processing job by ID"""
    return db.query(models.ProcessingJob).filter(models.ProcessingJob.id == job_id).first()

def update_processing_job_status(db: Session, job_id: str, status: str) -> Optional[models.ProcessingJob]:
    """Update processing job status"""
    db_job = get_processing_job(db, job_id)
    if db_job:
        db_job.status = status
        if status == models.ProcessingStatus.COMPLETED:
            db_job.completed_at = datetime.now()
        db.commit()
        db.refresh(db_job)
    return db_job

def add_file_to_job(db: Session, job_id: str, file_id: str) -> None:
    """Add a file to a processing job"""
    db_job_file = models.JobFile(job_id=job_id, file_id=file_id)
    db.add(db_job_file)
    db.commit()

# Validation Result CRUD operations
def create_validation_result(db: Session, validation_data: validation_schema.ValidationResultCreate) -> models.ValidationResult:
    """Create a new validation result"""
    db_validation = models.ValidationResult(
        job_id=validation_data.job_id,
        issues=validation_data.issues,
        total_sessions=validation_data.total_sessions,
        total_students=validation_data.total_students,
        total_tutors=validation_data.total_tutors,
        total_hours=validation_data.total_hours,
        status=validation_data.status
    )
    db.add(db_validation)
    db.commit()
    db.refresh(db_validation)
    return db_validation

def get_validation_result(db: Session, job_id: str) -> Optional[models.ValidationResult]:
    """Get validation result by job ID"""
    return db.query(models.ValidationResult).filter(models.ValidationResult.job_id == job_id).first()

# Extracted Data CRUD operations
def create_extracted_data(db: Session, file_id: str, data_type: str, content: Dict[str, Any]) -> models.ExtractedData:
    """Create a new extracted data record"""
    db_extracted_data = models.ExtractedData(
        file_id=file_id,
        data_type=data_type,
        content=content
    )
    db.add(db_extracted_data)
    db.commit()
    db.refresh(db_extracted_data)
    return db_extracted_data

def get_extracted_data(db: Session, file_id: str) -> List[models.ExtractedData]:
    """Get extracted data by file ID"""
    return db.query(models.ExtractedData).filter(models.ExtractedData.file_id == file_id).all()

# Output Document CRUD operations
def create_output_document(db: Session, document_data: Dict[str, Any]) -> models.OutputDocument:
    """Create a new output document record"""
    db_document = models.OutputDocument(
        job_id=document_data.get("job_id"),
        document_type=document_data.get("document_type"),
        file_path=document_data.get("file_path"),
        student_id=document_data.get("student_id"),
        template_id=document_data.get("template_id")
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_output_documents(db: Session, job_id: str) -> List[models.OutputDocument]:
    """Get output documents by job ID"""
    return db.query(models.OutputDocument).filter(models.OutputDocument.job_id == job_id).all()

# User CRUD operations
def create_user(db: Session, user: user_schema.UserCreate) -> models.User:
    """Create a new user"""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active=user.is_active,
        is_admin=user.is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: str) -> Optional[models.User]:
    """Get a user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get a user by username"""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get a user by email"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get all users"""
    return db.query(models.User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: str, user_data: user_schema.UserUpdate) -> Optional[models.User]:
    """Update user"""
    db_user = get_user(db, user_id)
    if db_user:
        update_data = user_data.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: str) -> bool:
    """Delete user"""
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False
