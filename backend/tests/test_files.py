"""
Tests for file upload and processing endpoints.
"""

import os
import pytest
from fastapi import status
import io
import shutil


def test_upload_files(authorized_client, test_files_dir, monkeypatch):
    """Test uploading files."""
    # Create test directory if it doesn't exist
    os.makedirs(test_files_dir, exist_ok=True)
    
    # Create test files if they don't exist
    test_payroll_path = os.path.join(test_files_dir, "test_payroll.pdf")
    test_feedback_path = os.path.join(test_files_dir, "test_feedback.xlsx")
    
    # Create a simple PDF file for testing
    if not os.path.exists(test_payroll_path):
        with open(test_payroll_path, "wb") as f:
            f.write(b"%PDF-1.4\n%Test PDF file")
    
    # Create a simple Excel file for testing
    if not os.path.exists(test_feedback_path):
        with open(test_feedback_path, "wb") as f:
            f.write(b"PK\x03\x04\x14\x00\x00\x00\x08\x00")  # Excel file signature
    
    # Mock the file processor to avoid actual processing
    def mock_process_files(*args, **kwargs):
        return {"job_id": 1, "status": "pending"}
    
    from services.file_processor import process_uploaded_files
    monkeypatch.setattr("services.file_processor.process_uploaded_files", mock_process_files)
    
    # Test uploading files
    with open(test_payroll_path, "rb") as payroll_file, open(test_feedback_path, "rb") as feedback_file:
        response = authorized_client.post(
            "/api/files/upload",
            files={
                "payroll_file": ("test_payroll.pdf", payroll_file, "application/pdf"),
                "feedback_file": ("test_feedback.xlsx", feedback_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            }
        )
    
    assert response.status_code == status.HTTP_201_CREATED
    assert "job_id" in response.json()
    assert response.json()["status"] == "pending"


def test_upload_files_unauthorized(client, test_files_dir):
    """Test uploading files without authentication."""
    test_payroll_path = os.path.join(test_files_dir, "test_payroll.pdf")
    test_feedback_path = os.path.join(test_files_dir, "test_feedback.xlsx")
    
    # Ensure test files exist
    assert os.path.exists(test_payroll_path), "Test payroll file not found"
    assert os.path.exists(test_feedback_path), "Test feedback file not found"
    
    # Test uploading files without authentication
    with open(test_payroll_path, "rb") as payroll_file, open(test_feedback_path, "rb") as feedback_file:
        response = client.post(
            "/api/files/upload",
            files={
                "payroll_file": ("test_payroll.pdf", payroll_file, "application/pdf"),
                "feedback_file": ("test_feedback.xlsx", feedback_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            }
        )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()


def test_upload_invalid_file_types(authorized_client, test_files_dir):
    """Test uploading files with invalid file types."""
    # Create a text file for testing
    test_text_path = os.path.join(test_files_dir, "test_text.txt")
    with open(test_text_path, "w") as f:
        f.write("This is a test text file")
    
    # Test uploading invalid file types
    with open(test_text_path, "rb") as text_file:
        response = authorized_client.post(
            "/api/files/upload",
            files={
                "payroll_file": ("test_text.txt", text_file, "text/plain"),
                "feedback_file": ("test_text.txt", text_file, "text/plain")
            }
        )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in response.json()
    
    # Clean up
    os.remove(test_text_path)


def test_get_upload_history(authorized_client, monkeypatch):
    """Test getting upload history."""
    # Mock the database query to return test data
    def mock_get_jobs(*args, **kwargs):
        return [
            {
                "id": 1,
                "user_id": 1,
                "status": "completed",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T01:00:00",
                "files": [
                    {"id": 1, "filename": "test_payroll.pdf", "file_type": "payroll"},
                    {"id": 2, "filename": "test_feedback.xlsx", "file_type": "feedback"}
                ]
            },
            {
                "id": 2,
                "user_id": 1,
                "status": "processing",
                "created_at": "2023-01-02T00:00:00",
                "updated_at": "2023-01-02T00:30:00",
                "files": [
                    {"id": 3, "filename": "test_payroll2.pdf", "file_type": "payroll"},
                    {"id": 4, "filename": "test_feedback2.xlsx", "file_type": "feedback"}
                ]
            }
        ]
    
    # Apply the mock
    monkeypatch.setattr("routers.files.get_user_jobs", mock_get_jobs)
    
    # Test getting upload history
    response = authorized_client.get("/api/files/history")
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    assert response.json()[0]["id"] == 1
    assert response.json()[0]["status"] == "completed"
    assert len(response.json()[0]["files"]) == 2


def test_get_upload_history_unauthorized(client):
    """Test getting upload history without authentication."""
    response = client.get("/api/files/history")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()


def test_get_file_by_id(authorized_client, monkeypatch):
    """Test getting a file by ID."""
    # Mock the database query to return test data
    def mock_get_file(*args, **kwargs):
        return {
            "id": 1,
            "job_id": 1,
            "filename": "test_payroll.pdf",
            "file_type": "payroll",
            "file_path": "/path/to/test_payroll.pdf",
            "created_at": "2023-01-01T00:00:00"
        }
    
    # Apply the mock
    monkeypatch.setattr("routers.files.get_file_by_id", mock_get_file)
    
    # Test getting a file by ID
    response = authorized_client.get("/api/files/1")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1
    assert response.json()["filename"] == "test_payroll.pdf"
    assert response.json()["file_type"] == "payroll"


def test_get_file_by_id_not_found(authorized_client, monkeypatch):
    """Test getting a file by ID that doesn't exist."""
    # Mock the database query to return None
    def mock_get_file(*args, **kwargs):
        return None
    
    # Apply the mock
    monkeypatch.setattr("routers.files.get_file_by_id", mock_get_file)
    
    # Test getting a file by ID that doesn't exist
    response = authorized_client.get("/api/files/999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in response.json()


def test_get_file_by_id_unauthorized(client):
    """Test getting a file by ID without authentication."""
    response = client.get("/api/files/1")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()
