"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.app.web import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200


def test_generate_video_no_script():
    """Test video generation without script."""
    response = client.post("/api/generate", data={})
    assert response.status_code == 422  # Validation error


def test_generate_video_with_script():
    """Test video generation with valid script."""
    response = client.post(
        "/api/generate",
        data={
            "script": "This is a test video script about AI technology.",
            "use_tts": True,
            "voice": "default",
            "add_captions": True,
            "caption_style": "modern",
            "add_music": True,
            "mood": "professional"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"


def test_job_status_not_found():
    """Test job status for non-existent job."""
    response = client.get("/api/status/nonexistent-job-id")
    assert response.status_code == 404


def test_settings_get():
    """Test getting settings."""
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert "has_gemini" in data


def test_settings_post():
    """Test saving settings."""
    response = client.post(
        "/api/settings",
        json={
            "gemini_api_key": "test_key_123",
            "pexels_api_key": "test_pexels_key"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Settings saved successfully"


def test_list_jobs():
    """Test listing jobs."""
    response = client.get("/api/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert isinstance(data["jobs"], list)
