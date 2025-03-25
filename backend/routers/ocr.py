"""
OCR Router Module

This module provides API endpoints for OCR functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import os
from pathlib import Path

from ..database import crud
from ..database.database import get_db
from ..schemas import user as user_schema
from ..auth.security import get_current_active_user
from ..services.ocr_service import ocr_service

router = APIRouter(prefix="/api/ocr", tags=["ocr"])


@router.get("/extract-text/{file_id}", response_model=Dict[str, Any])
async def extract_text_from_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """
    Extract text from a PDF file using OCR.
    
    Args:
        file_id: ID of the file to process
        
    Returns:
        dict: Extracted text from the file
    """
    # Get file from database
    file = crud.get_file(db, file_id)
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if user is authorized to access this file
    job_file = db.query(crud.models.JobFile).filter(crud.models.JobFile.file_id == file_id).first()
    if job_file:
        job = crud.get_processing_job(db, job_file.job_id)
        if job and job.owner_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this file"
            )
    
    # Check if file exists on disk
    file_path = Path(file.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    try:
        # Extract text from file
        extracted_text = ocr_service.extract_text_from_pdf(file_path)
        
        # Store extracted text in database
        extracted_data = crud.models.ExtractedData(
            file_id=file_id,
            data_type="text",
            content={"text": extracted_text}
        )
        db.add(extracted_data)
        db.commit()
        
        return {
            "file_id": file_id,
            "text": extracted_text,
            "character_count": len(extracted_text)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting text: {str(e)}"
        )


@router.get("/parse-payroll/{file_id}", response_model=Dict[str, Any])
async def parse_payroll_data(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """
    Parse payroll data from a PDF file using OCR.
    
    Args:
        file_id: ID of the file to process
        
    Returns:
        dict: Structured payroll data extracted from the file
    """
    # Get file from database
    file = crud.get_file(db, file_id)
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if user is authorized to access this file
    job_file = db.query(crud.models.JobFile).filter(crud.models.JobFile.file_id == file_id).first()
    if job_file:
        job = crud.get_processing_job(db, job_file.job_id)
        if job and job.owner_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this file"
            )
    
    # Check if file exists on disk
    file_path = Path(file.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    try:
        # Parse payroll data from file
        payroll_data = ocr_service.parse_payroll_data(file_path)
        
        # Store extracted data in database
        extracted_data = crud.models.ExtractedData(
            file_id=file_id,
            data_type="payroll",
            content=payroll_data
        )
        db.add(extracted_data)
        db.commit()
        
        return {
            "file_id": file_id,
            "payroll_data": payroll_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing payroll data: {str(e)}"
        )


@router.get("/extract-table/{file_id}", response_model=Dict[str, Any])
async def extract_table_from_file(
    file_id: str,
    page: int = 0,
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """
    Extract tabular data from a PDF file using OCR.
    
    Args:
        file_id: ID of the file to process
        page: Page number to extract table from (0-indexed)
        
    Returns:
        dict: Extracted table data from the file
    """
    # Get file from database
    file = crud.get_file(db, file_id)
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if user is authorized to access this file
    job_file = db.query(crud.models.JobFile).filter(crud.models.JobFile.file_id == file_id).first()
    if job_file:
        job = crud.get_processing_job(db, job_file.job_id)
        if job and job.owner_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this file"
            )
    
    # Check if file exists on disk
    file_path = Path(file.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    try:
        # Extract table from file
        table_data = ocr_service.extract_table_from_pdf(file_path, page)
        
        # Store extracted data in database
        extracted_data = crud.models.ExtractedData(
            file_id=file_id,
            data_type="table",
            content={"table": table_data, "page": page}
        )
        db.add(extracted_data)
        db.commit()
        
        return {
            "file_id": file_id,
            "page": page,
            "table": table_data,
            "rows": len(table_data),
            "columns": len(table_data[0]) if table_data else 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting table: {str(e)}"
        )


@router.post("/upload-and-extract", response_model=Dict[str, Any])
async def upload_and_extract(
    file: UploadFile = File(...),
    extraction_type: str = Form(...),
    page: Optional[int] = Form(0),
    db: Session = Depends(get_db),
    current_user: user_schema.User = Depends(get_current_active_user)
):
    """
    Upload a file and extract data from it using OCR.
    
    Args:
        file: File to upload and process
        extraction_type: Type of extraction to perform (text, payroll, table)
        page: Page number to extract from (for table extraction)
        
    Returns:
        dict: Extracted data from the file
    """
    # Check file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    # Save file to disk
    upload_dir = Path("uploads") / "temp"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / file.filename
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    try:
        # Process file based on extraction type
        if extraction_type == "text":
            extracted_text = ocr_service.extract_text_from_pdf(file_path)
            result = {
                "text": extracted_text,
                "character_count": len(extracted_text)
            }
        elif extraction_type == "payroll":
            payroll_data = ocr_service.parse_payroll_data(file_path)
            result = {
                "payroll_data": payroll_data
            }
        elif extraction_type == "table":
            table_data = ocr_service.extract_table_from_pdf(file_path, page)
            result = {
                "page": page,
                "table": table_data,
                "rows": len(table_data),
                "columns": len(table_data[0]) if table_data else 0
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid extraction type. Must be one of: text, payroll, table"
            )
        
        # Clean up temporary file
        os.unlink(file_path)
        
        return {
            "filename": file.filename,
            "extraction_type": extraction_type,
            "result": result
        }
    except Exception as e:
        # Clean up temporary file
        if file_path.exists():
            os.unlink(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )
