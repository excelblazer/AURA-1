"""
Tests for authentication endpoints.
"""

import pytest
from fastapi import status


def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "password"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_incorrect_password(client, test_user):
    """Test login with incorrect password."""
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()


def test_login_nonexistent_user(client):
    """Test login with nonexistent user."""
    response = client.post(
        "/api/auth/login",
        data={"username": "nonexistentuser", "password": "password"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()


def test_get_current_user(authorized_client, test_user):
    """Test getting the current user profile."""
    response = authorized_client.get("/api/auth/profile")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == test_user.username
    assert response.json()["email"] == test_user.email
    assert "hashed_password" not in response.json()


def test_get_current_user_unauthorized(client):
    """Test getting the current user profile without authentication."""
    response = client.get("/api/auth/profile")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()


def test_register_user(client):
    """Test user registration."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
            "full_name": "New User"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["username"] == "newuser"
    assert response.json()["email"] == "newuser@example.com"
    assert "hashed_password" not in response.json()


def test_register_existing_username(client, test_user):
    """Test registration with an existing username."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "different@example.com",
            "password": "newpassword",
            "full_name": "Different User"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in response.json()


def test_register_existing_email(client, test_user):
    """Test registration with an existing email."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "differentuser",
            "email": "test@example.com",
            "password": "newpassword",
            "full_name": "Different User"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in response.json()
