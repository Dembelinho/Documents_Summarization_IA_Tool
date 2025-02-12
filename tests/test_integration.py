import os
import unittest
import pytest
from app import create_app, db
from io import BytesIO


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_upload_file(client):
    """Test document upload and summary generation."""
    data = {
        "file": (BytesIO(b"Sample text for testing"), "test.txt"),
        "summary_type": "default",
        "summary_length": "moderate",
        "language": "english"
    }
    response = client.post("/upload", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    json_data = response.get_json()
    assert "summary" in json_data


def test_history_page(client):
    """Test fetching history page."""
    response = client.get("/history")
    assert response.status_code == 200
    assert b"Summary History" in response.data


def test_delete_summary(client):
    """Test deleting a summary."""
    # Upload a file first
    data = {
        "file": (BytesIO(b"Sample text for testing"), "test.txt"),
        "summary_type": "default",
        "summary_length": "moderate",
        "language": "english"
    }
    client.post("/upload", data=data, content_type="multipart/form-data")

    # Retrieve the first summary and delete it
    response = client.get("/history")
    assert response.status_code == 200

    # Extract summary ID (mock method, replace if necessary)
    summary_id = 1
    delete_response = client.post(f"/delete_summary/{summary_id}")

    assert delete_response.status_code == 302  # Redirect after deletion


if __name__ == "__main__":
    unittest.main()