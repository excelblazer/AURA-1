"""
Test configuration for pytest.

This module contains fixtures and configuration for pytest to use in testing
the AURA-1 backend application.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add the parent directory to sys.path to allow importing from the application
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import Base, get_db
from main import app
from auth.security import create_access_token
from database.models import User

# Create a test database in memory
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """
    Create a fresh database for each test.
    """
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session for the test
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after the test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Create a test client for the FastAPI application.
    """
    # Override the get_db dependency to use the test database
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear any overrides after the test
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db):
    """
    Create a test user in the database.
    """
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        full_name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def token(test_user):
    """
    Create a JWT token for the test user.
    """
    return create_access_token(data={"sub": test_user.username})


@pytest.fixture(scope="function")
def authorized_client(client, token):
    """
    Create a test client with authorization headers.
    """
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


@pytest.fixture(scope="function")
def test_files_dir():
    """
    Return the path to the test files directory.
    """
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_files")


@pytest.fixture(scope="function")
def test_payroll_pdf(test_files_dir):
    """
    Return the path to a test payroll PDF file.
    """
    return os.path.join(test_files_dir, "test_payroll.pdf")


@pytest.fixture(scope="function")
def test_feedback_excel(test_files_dir):
    """
    Return the path to a test feedback Excel file.
    """
    return os.path.join(test_files_dir, "test_feedback.xlsx")
