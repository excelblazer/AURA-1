from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random

from ..database import crud
from ..database.database import get_db
from ..schemas import job as job_schema
from ..schemas import user as user_schema
from ..schemas import validation as validation_schema
from ..auth.security import get_current_active_user
from ..services.document_generator import (
    generate_attendance_record,
    generate_progress_report,
    generate_invoice,
    generate_service_log
)

router = APIRouter(prefix="/api/processing", tags=["processing"])

@router.post("/jobs", response_model=job_schema.ProcessingJob)
async def create_processing_job(
    job: job_schema.ProcessingJobCreate,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Create a new processing job"""
    # Add owner_id to job
    job.owner_id = current_user.id
    return crud.create_processing_job(db, job)

@router.get("/jobs", response_model=List[job_schema.ProcessingJob])
async def get_processing_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Get all processing jobs for current user"""
    if current_user.is_admin:
        jobs = crud.get_processing_jobs(db, skip, limit)
    else:
        jobs = crud.get_user_processing_jobs(db, current_user.id, skip, limit)
    return jobs

@router.get("/jobs/{job_id}", response_model=job_schema.ProcessingJob)
async def get_processing_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Get processing job by ID"""
    job = crud.get_processing_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Processing job not found")
    
    # Check if user is owner or admin
    if job.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this job")
    
    return job

@router.post("/generate/documents", response_model=Dict[str, Any])
async def generate_documents(
    job_id: str,
    document_types: List[job_schema.DocumentType],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Generate documents for a processing job"""
    # Get job
    job = crud.get_processing_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Processing job not found")
    
    # Check if user is owner or admin
    if job.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this job")
    
    # Check if job is validated
    if job.status != validation_schema.ProcessingStatus.VALIDATED and job.status != validation_schema.ProcessingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job must be validated before generating documents"
        )
    
    # Update job status
    crud.update_processing_job_status(db, job_id, validation_schema.ProcessingStatus.GENERATING)
    
    # Run document generation in background
    background_tasks.add_task(
        run_document_generation,
        job_id,
        document_types,
        db
    )
    
    return {"message": "Document generation started", "job_id": job_id}

async def run_document_generation(
    job_id: str,
    document_types: List[job_schema.DocumentType],
    db: Session
):
    """Run document generation process"""
    try:
        # Get job
        job = crud.get_processing_job(db, job_id)
        if job is None:
            return
        
        # Get validation result
        validation_result = crud.get_validation_result(db, job_id)
        if validation_result is None:
            # Update job status
            crud.update_processing_job_status(db, job_id, validation_schema.ProcessingStatus.FAILED)
            return
        
        # Get extracted data
        job_files = db.query(crud.models.JobFile).filter(crud.models.JobFile.job_id == job_id).all()
        if not job_files:
            # Update job status
            crud.update_processing_job_status(db, job_id, validation_schema.ProcessingStatus.FAILED)
            return
        
        payroll_data = None
        feedback_data = None
        
        for job_file in job_files:
            file = crud.get_file(db, job_file.file_id)
            if file.file_type == crud.models.FileType.PAYROLL:
                extracted_data = crud.get_extracted_data(db, file.id)
                if extracted_data:
                    payroll_data = extracted_data[0].content
            elif file.file_type == crud.models.FileType.FEEDBACK:
                extracted_data = crud.get_extracted_data(db, file.id)
                if extracted_data:
                    feedback_data = extracted_data[0].content
        
        if not payroll_data or not feedback_data:
            # Update job status
            crud.update_processing_job_status(db, job_id, validation_schema.ProcessingStatus.FAILED)
            return
        
        # Get templates
        templates = {}
        for doc_type in document_types:
            template = crud.get_template_by_type(db, doc_type.value)
            if template:
                templates[doc_type.value] = template
        
        # Generate documents
        generated_documents = []
        
        for doc_type in document_types:
            if doc_type == job_schema.DocumentType.ATTENDANCE_RECORD:
                # Get students from feedback data
                students = feedback_data.get("students", [])
                for student in students:
                    # Get sessions for student
                    student_sessions = [
                        session for session in feedback_data.get("sessions", [])
                        if session.get("student_id") == student.get("id")
                    ]
                    
                    # Generate AR for student
                    template_id = templates.get(doc_type.value, {}).get("id") if doc_type.value in templates else None
                    ar_file = generate_attendance_record(student, student_sessions, job.month, job.year, template_id)
                    
                    # Create document record
                    document = job_schema.DocumentCreate(
                        job_id=job_id,
                        document_type=doc_type,
                        file_path=ar_file,
                        student_id=student.get("id"),
                        student_name=f"{student.get('first_name')} {student.get('last_name')}"
                    )
                    generated_doc = crud.create_document(db, document)
                    generated_documents.append(generated_doc)
            
            elif doc_type == job_schema.DocumentType.PROGRESS_REPORT:
                # Get students from feedback data
                students = feedback_data.get("students", [])
                for student in students:
                    # Get sessions for student
                    student_sessions = [
                        session for session in feedback_data.get("sessions", [])
                        if session.get("student_id") == student.get("id")
                    ]
                    
                    # Generate PR for student
                    template_id = templates.get(doc_type.value, {}).get("id") if doc_type.value in templates else None
                    pr_file = generate_progress_report(student, student_sessions, job.month, job.year, template_id)
                    
                    # Create document record
                    document = job_schema.DocumentCreate(
                        job_id=job_id,
                        document_type=doc_type,
                        file_path=pr_file,
                        student_id=student.get("id"),
                        student_name=f"{student.get('first_name')} {student.get('last_name')}"
                    )
                    generated_doc = crud.create_document(db, document)
                    generated_documents.append(generated_doc)
            
            elif doc_type == job_schema.DocumentType.INVOICE:
                # Generate invoice
                template_id = templates.get(doc_type.value, {}).get("id") if doc_type.value in templates else None
                invoice_file = generate_invoice(
                    feedback_data.get("students", []),
                    feedback_data.get("sessions", []),
                    job.month,
                    job.year,
                    template_id
                )
                
                # Create document record
                document = job_schema.DocumentCreate(
                    job_id=job_id,
                    document_type=doc_type,
                    file_path=invoice_file
                )
                generated_doc = crud.create_document(db, document)
                generated_documents.append(generated_doc)
            
            elif doc_type == job_schema.DocumentType.SERVICE_LOG:
                # Generate service log
                template_id = templates.get(doc_type.value, {}).get("id") if doc_type.value in templates else None
                service_log_file = generate_service_log(
                    feedback_data.get("students", []),
                    feedback_data.get("sessions", []),
                    job.month,
                    job.year,
                    template_id
                )
                
                # Create document record
                document = job_schema.DocumentCreate(
                    job_id=job_id,
                    document_type=doc_type,
                    file_path=service_log_file
                )
                generated_doc = crud.create_document(db, document)
                generated_documents.append(generated_doc)
        
        # Update job status
        crud.update_processing_job_status(db, job_id, validation_schema.ProcessingStatus.COMPLETED)
    
    except Exception as e:
        print(f"Error in document generation process: {str(e)}")
        # Update job status
        crud.update_processing_job_status(db, job_id, validation_schema.ProcessingStatus.FAILED)

@router.get("/stats", response_model=Dict[str, Any])
async def get_processing_stats(
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Get processing statistics for the dashboard"""
    # Get active jobs count
    active_jobs = db.query(crud.models.ProcessingJob).filter(
        crud.models.ProcessingJob.status.in_([
            validation_schema.ProcessingStatus.PENDING,
            validation_schema.ProcessingStatus.PROCESSING,
            validation_schema.ProcessingStatus.EXTRACTING,
            validation_schema.ProcessingStatus.VALIDATING,
            validation_schema.ProcessingStatus.GENERATING
        ])
    ).count()
    
    # Get completed jobs count
    completed_jobs = db.query(crud.models.ProcessingJob).filter(
        crud.models.ProcessingJob.status == validation_schema.ProcessingStatus.COMPLETED
    ).count()
    
    # Get failed jobs count
    failed_jobs = db.query(crud.models.ProcessingJob).filter(
        crud.models.ProcessingJob.status == validation_schema.ProcessingStatus.FAILED
    ).count()
    
    # Get total documents count
    total_documents = db.query(crud.models.Document).count()
    
    # Get processing stages distribution
    processing_stages = []
    stages = [
        ("File Upload", validation_schema.ProcessingStatus.PENDING),
        ("Data Extraction", validation_schema.ProcessingStatus.EXTRACTING),
        ("Validation", validation_schema.ProcessingStatus.VALIDATING),
        ("Document Generation", validation_schema.ProcessingStatus.GENERATING),
        ("PDF Conversion", validation_schema.ProcessingStatus.PROCESSING)
    ]
    
    for stage_name, stage_status in stages:
        count = db.query(crud.models.ProcessingJob).filter(
            crud.models.ProcessingJob.status == stage_status
        ).count()
        
        if count > 0:
            processing_stages.append({
                "stage": stage_name,
                "count": count
            })
    
    return {
        "activeJobs": active_jobs,
        "completedJobs": completed_jobs,
        "failedJobs": failed_jobs,
        "totalDocuments": total_documents,
        "processingStages": processing_stages
    }

@router.get("/stages", response_model=List[Dict[str, Any]])
async def get_processing_stages(
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Get processing stages for the dashboard"""
    stages = [
        {"id": "file_upload", "name": "File Upload", "description": "Uploading files to the system"},
        {"id": "data_extraction", "name": "Data Extraction", "description": "Extracting data from uploaded files"},
        {"id": "validation", "name": "Validation", "description": "Validating extracted data"},
        {"id": "document_generation", "name": "Document Generation", "description": "Generating output documents"},
        {"id": "pdf_conversion", "name": "PDF Conversion", "description": "Converting documents to PDF format"}
    ]
    
    return stages

@router.get("/estimated-time/{job_id}", response_model=Dict[str, Any])
async def get_estimated_time(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Get estimated time for job completion"""
    # Get job
    job = crud.get_processing_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Processing job not found")
    
    # Check if user is owner or admin
    if job.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this job")
    
    # If job is completed or failed, return 0
    if job.status in [validation_schema.ProcessingStatus.COMPLETED, validation_schema.ProcessingStatus.FAILED]:
        return {"estimatedMinutes": 0, "completed": True}
    
    # Define estimated time for each stage in minutes
    stage_times = {
        validation_schema.ProcessingStatus.PENDING: 1,
        validation_schema.ProcessingStatus.EXTRACTING: 3,
        validation_schema.ProcessingStatus.VALIDATING: 2,
        validation_schema.ProcessingStatus.GENERATING: 5,
        validation_schema.ProcessingStatus.PROCESSING: 2
    }
    
    # Get current stage
    current_stage = job.status
    
    # Calculate estimated time based on current stage
    estimated_minutes = 0
    stages_order = [
        validation_schema.ProcessingStatus.PENDING,
        validation_schema.ProcessingStatus.EXTRACTING,
        validation_schema.ProcessingStatus.VALIDATING,
        validation_schema.ProcessingStatus.GENERATING,
        validation_schema.ProcessingStatus.PROCESSING
    ]
    
    current_stage_index = stages_order.index(current_stage) if current_stage in stages_order else 0
    
    # Add half of current stage time (assuming we're halfway through)
    if current_stage in stage_times:
        estimated_minutes += stage_times[current_stage] / 2
    
    # Add full time for remaining stages
    for i in range(current_stage_index + 1, len(stages_order)):
        stage = stages_order[i]
        if stage in stage_times:
            estimated_minutes += stage_times[stage]
    
    return {
        "estimatedMinutes": estimated_minutes,
        "completed": False,
        "currentStage": current_stage,
        "totalStages": len(stages_order)
    }

@router.get("/documents/{job_id}", response_model=List[job_schema.Document])
async def get_documents(
    job_id: str,
    document_type: Optional[job_schema.DocumentType] = None,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Get documents for a processing job"""
    # Get job
    job = crud.get_processing_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Processing job not found")
    
    # Check if user is owner or admin
    if job.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this job")
    
    # Get documents
    if document_type:
        documents = crud.get_documents_by_type(db, job_id, document_type)
    else:
        documents = crud.get_documents(db, job_id)
    
    return documents

@router.get("/download/{document_id}")
async def download_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Download a document"""
    # Get document
    document = crud.get_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get job
    job = crud.get_processing_job(db, document.job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Processing job not found")
    
    # Check if user is owner or admin
    if job.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this document")
    
    # Return file response
    return FileResponse(
        document.file_path,
        filename=document.file_path.split("/")[-1],
        media_type="application/octet-stream"
    )
