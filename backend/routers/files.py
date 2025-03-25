from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import shutil
from datetime import datetime

from ..database import crud
from ..database.database import get_db
from ..schemas import file as file_schema
from ..schemas import user as user_schema
from ..auth.security import get_current_active_user
from ..services.file_processor import extract_from_payroll, extract_from_feedback

router = APIRouter(prefix="/api/files", tags=["files"])

# Create upload directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

@router.post("/upload/payroll", response_model=file_schema.FileUpload)
async def upload_payroll_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Upload payroll detail sheet (PDF)"""
    return await save_file(file, file_schema.FileType.PAYROLL, db, current_user.id, background_tasks)

@router.post("/upload/feedback", response_model=file_schema.FileUpload)
async def upload_feedback_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Upload daily feedback sheet (Excel)"""
    return await save_file(file, file_schema.FileType.FEEDBACK, db, current_user.id, background_tasks)

@router.post("/upload/template", response_model=file_schema.FileUpload)
async def upload_template_file(
    file: UploadFile = File(...),
    template_type: str = None,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Upload template file (Word or Excel)"""
    return await save_file(file, file_schema.FileType.TEMPLATE, db, current_user.id)

async def save_file(
    file: UploadFile, 
    file_type: file_schema.FileType, 
    db: Session,
    owner_id: str,
    background_tasks: Optional[BackgroundTasks] = None
) -> file_schema.FileUpload:
    """Save uploaded file to disk and database"""
    # Generate unique filename
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    new_filename = f"{file_type.value}_{file_id}{ext}"
    file_path = os.path.join("uploads", new_filename)
    
    # Get file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    
    # Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create file record
    file_data = file_schema.FileCreate(
        id=file_id,
        original_filename=file.filename,
        saved_filename=new_filename,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        mime_type=file.content_type,
        owner_id=owner_id
    )
    
    db_file = crud.create_file(db, file_data)
    
    # Process file in background if needed
    if background_tasks and file_type in [file_schema.FileType.PAYROLL, file_schema.FileType.FEEDBACK]:
        background_tasks.add_task(process_file, file_path, file_type, file_id, db)
    
    return db_file

async def process_file(file_path: str, file_type: file_schema.FileType, file_id: str, db: Session):
    """Process uploaded file to extract data"""
    try:
        # Update file status
        crud.update_file_status(db, file_id, file_schema.ProcessingStatus.PROCESSING)
        
        # Extract data based on file type
        if file_type == file_schema.FileType.PAYROLL:
            extracted_data = extract_from_payroll(file_path)
            data_type = "tutors"
        elif file_type == file_schema.FileType.FEEDBACK:
            extracted_data = extract_from_feedback(file_path)
            data_type = "students_sessions"
        else:
            return
        
        # Save extracted data
        crud.create_extracted_data(db, file_id, data_type, extracted_data)
        
        # Update file status
        crud.update_file_status(db, file_id, file_schema.ProcessingStatus.VALIDATED)
    
    except Exception as e:
        # Update file status to failed
        crud.update_file_status(db, file_id, file_schema.ProcessingStatus.FAILED)
        print(f"Error processing file: {str(e)}")

@router.get("/{file_type}", response_model=List[file_schema.FileUpload])
async def get_files_by_type(
    file_type: file_schema.FileType,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Get files by type"""
    files = crud.get_files_by_type(db, file_type, skip, limit)
    return files

@router.get("/{file_id}", response_model=file_schema.FileUpload)
async def get_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Get file by ID"""
    db_file = crud.get_file(db, file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file

@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Download file by ID"""
    db_file = crud.get_file(db, file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    if not os.path.exists(db_file.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=db_file.file_path, 
        filename=db_file.original_filename,
        media_type=db_file.mime_type
    )

@router.delete("/{file_id}", response_model=dict)
async def delete_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """Delete file by ID"""
    db_file = crud.get_file(db, file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if user is owner or admin
    if db_file.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this file")
    
    # Delete file from disk if it exists
    if os.path.exists(db_file.file_path):
        os.remove(db_file.file_path)
    
    # Delete file from database
    # Implement delete_file in crud
    
    return {"detail": "File deleted successfully"}
