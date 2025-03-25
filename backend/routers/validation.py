from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ..database import crud
from ..database.database import get_db
from ..schemas import validation as validation_schema
from ..schemas import job as job_schema
from ..schemas import user as user_schema
from ..auth.security import get_current_active_user
from ..services.validator import validate_data

router = APIRouter(prefix="/api/validation", tags=["validation"])

@router.post("/process", response_model=validation_schema.ValidationResult)
async def process_validation(
    job_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Process data validation for a job"""
    # Get job
    job = crud.get_processing_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Processing job not found")
    
    # Check if user is owner or admin
    if job.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this job")
    
    # Update job status
    crud.update_processing_job_status(db, job_id, validation_schema.ProcessingStatus.PROCESSING)
    
    # Run validation in background
    background_tasks.add_task(run_validation, job_id, db)
    
    return {
        "id": job_id,
        "job_id": job_id,
        "issues": [],
        "total_sessions": 0,
        "total_students": 0,
        "total_tutors": 0,
        "total_hours": 0,
        "processing_date": job.started_at,
        "status": validation_schema.ProcessingStatus.PROCESSING
    }

async def run_validation(job_id: str, db: Session):
    """Run validation process"""
    try:
        # Get job
        job = crud.get_processing_job(db, job_id)
        if job is None:
            return
        
        # Get files associated with job
        job_files = db.query(crud.models.JobFile).filter(crud.models.JobFile.job_id == job_id).all()
        if not job_files:
            # Update job status
            crud.update_processing_job_status(db, job_id, validation_schema.ProcessingStatus.FAILED)
            return
        
        # Get extracted data
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
        
        # Run validation
        validation_result = validate_data(payroll_data, feedback_data)
        
        # Create validation result
        validation_data = validation_schema.ValidationResultCreate(
            job_id=job_id,
            issues=validation_result.get("issues", []),
            total_sessions=validation_result.get("total_sessions", 0),
            total_students=validation_result.get("total_students", 0),
            total_tutors=validation_result.get("total_tutors", 0),
            total_hours=validation_result.get("total_hours", 0),
            status=validation_schema.ProcessingStatus.VALIDATED
        )
        
        crud.create_validation_result(db, validation_data)
        
        # Update job status
        crud.update_processing_job_status(db, job_id, validation_schema.ProcessingStatus.VALIDATED)
    
    except Exception as e:
        print(f"Error in validation process: {str(e)}")
        # Update job status
        crud.update_processing_job_status(db, job_id, validation_schema.ProcessingStatus.FAILED)

@router.get("/{job_id}", response_model=validation_schema.ValidationResult)
async def get_validation_result(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Get validation result for a job"""
    # Get job
    job = crud.get_processing_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Processing job not found")
    
    # Check if user is owner or admin
    if job.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this job")
    
    # Get validation result
    validation_result = crud.get_validation_result(db, job_id)
    if validation_result is None:
        raise HTTPException(status_code=404, detail="Validation result not found")
    
    return validation_result

@router.post("/resolve", response_model=Dict[str, Any])
async def resolve_validation_issues(
    job_id: str,
    resolutions: List[validation_schema.ValidationResolution],
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Resolve validation issues"""
    # Get job
    job = crud.get_processing_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Processing job not found")
    
    # Check if user is owner or admin
    if job.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this job")
    
    # Get validation result
    validation_result = crud.get_validation_result(db, job_id)
    if validation_result is None:
        raise HTTPException(status_code=404, detail="Validation result not found")
    
    # Apply resolutions
    issues = validation_result.issues
    for resolution in resolutions:
        for i, issue in enumerate(issues):
            if i == resolution.issue_id:
                issues[i]["resolved"] = True
                issues[i]["resolution_note"] = resolution.resolution
                if resolution.corrected_value:
                    issues[i]["corrected_value"] = resolution.corrected_value
    
    # Update validation result
    validation_result.issues = issues
    db.commit()
    
    # Check if all issues are resolved
    all_resolved = all(issue.get("resolved", False) for issue in issues)
    if all_resolved:
        # Update job status
        crud.update_processing_job_status(db, job_id, validation_schema.ProcessingStatus.COMPLETED)
    
    return {"message": "Validation issues resolved successfully", "all_resolved": all_resolved}

@router.get("/summary/{job_id}", response_model=validation_schema.ValidationSummary)
async def get_validation_summary(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Get validation summary for a job"""
    # Get job
    job = crud.get_processing_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Processing job not found")
    
    # Check if user is owner or admin
    if job.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this job")
    
    # Get validation result
    validation_result = crud.get_validation_result(db, job_id)
    if validation_result is None:
        raise HTTPException(status_code=404, detail="Validation result not found")
    
    # Calculate summary
    issues = validation_result.issues
    total_issues = len(issues)
    errors = sum(1 for issue in issues if issue.get("severity") == "error")
    warnings = sum(1 for issue in issues if issue.get("severity") == "warning")
    resolved = sum(1 for issue in issues if issue.get("resolved", False))
    unresolved = total_issues - resolved
    
    # Count by type
    by_type = {}
    for issue in issues:
        issue_type = issue.get("issue_type")
        if issue_type in by_type:
            by_type[issue_type] += 1
        else:
            by_type[issue_type] = 1
    
    # Count by severity
    by_severity = {
        "error": errors,
        "warning": warnings
    }
    
    return {
        "total_issues": total_issues,
        "errors": errors,
        "warnings": warnings,
        "resolved": resolved,
        "unresolved": unresolved,
        "by_type": by_type,
        "by_severity": by_severity
    }
