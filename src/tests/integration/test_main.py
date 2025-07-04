"""Integration tests for the main API application."""

import pytest
from fastapi import status

from src.api.main import app


def test_app_root(client):
    """Test the root endpoint of the application."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "title" in data
    assert "version" in data
    assert "OpenAnonymiser" in data["title"]


def test_docs_endpoint(client):
    """Test that the documentation endpoint is accessible."""
    response = client.get("/docs")
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]
    assert "swagger" in response.text.lower() or "openapi" in response.text.lower()


def test_openapi_schema(client):
    """Test that the OpenAPI schema is available and valid."""
    response = client.get("/openapi.json")
    assert response.status_code == status.HTTP_200_OK
    schema = response.json()

    # Check basic schema structure
    assert "paths" in schema
    assert "components" in schema
    assert "info" in schema

    # Check document endpoints are included
    assert "/documents/upload" in schema["paths"]
    assert "/documents/{file_id}/metadata" in schema["paths"]
    assert "/documents/{file_id}/anonymize" in schema["paths"]
    assert "/documents/{file_id}/download" in schema["paths"]
