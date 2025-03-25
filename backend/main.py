from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
import uuid
import shutil
from typing import List, Optional
from datetime import datetime

from database.database import get_db, engine
from database.models import Base
from routers import auth, files, templates, validation, processing, ocr

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Client1 Invoicing Automation")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create required directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("output", exist_ok=True)
os.makedirs("output/attendance_records", exist_ok=True)
os.makedirs("output/progress_reports", exist_ok=True)
os.makedirs("output/invoices", exist_ok=True)
os.makedirs("output/service_logs", exist_ok=True)

# Serve static files
app.mount("/output", StaticFiles(directory="output"), name="output")

# Include routers
app.include_router(auth.router)
app.include_router(files.router)
app.include_router(templates.router)
app.include_router(validation.router)
app.include_router(processing.router)
app.include_router(ocr.router)

@app.get("/")
async def root():
    return {"message": "Client1 Invoicing Automation API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}