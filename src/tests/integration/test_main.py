"""Integration tests for the main API application."""

from fastapi import status


def test_app_root(client):
    """Test the root endpoint of the application."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == {"ping": "pong"}


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
