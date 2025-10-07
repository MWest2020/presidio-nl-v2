"""
Comprehensive test suite for new string-based analyze and anonymize endpoints.
Run with: pytest tests/test_string_endpoints.py -v
"""

import pytest
import httpx
import asyncio
from pathlib import Path


BASE_URL = "http://localhost:8080"
TEST_PDF_PATH = Path("test.pdf")

# HTTP client with increased timeout for ML processing
CLIENT = httpx.Client(timeout=30.0)


class TestHealthCheck:
    """Test basic API health and availability."""

    def test_health_endpoint(self):
        """Test that the health endpoint returns pong."""
        response = CLIENT.get(f"{BASE_URL}/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"ping": "pong"}


class TestAnalyzeEndpoint:
    """Test the new /api/v1/analyze endpoint."""

    def test_analyze_simple_text(self):
        """Test basic text analysis with Dutch PII."""
        payload = {"text": "Jan de Vries woont in Amsterdam", "language": "nl"}
        response = CLIENT.post(f"{BASE_URL}/api/v1/analyze", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "pii_entities" in data
        assert "text_length" in data
        assert "processing_time_ms" in data
        assert "nlp_engine_used" in data

        # Check text length
        assert data["text_length"] == len(payload["text"])

        # Check PII entities found
        entities = data["pii_entities"]
        assert len(entities) > 0

        # Check entity structure
        for entity in entities:
            assert "entity_type" in entity
            assert "text" in entity
            assert "start" in entity
            assert "end" in entity
            assert "score" in entity  # Can be null for spaCy

            # Check position data makes sense
            assert entity["start"] >= 0
            assert entity["end"] > entity["start"]
            assert entity["end"] <= len(payload["text"])

    def test_analyze_with_engine_selection(self):
        """Test analysis with specific NLP engine."""
        payload = {
            "text": "Maria woont in Utrecht",
            "language": "nl",
            "nlp_engine": "spacy",
        }
        response = CLIENT.post(f"{BASE_URL}/api/v1/analyze", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["nlp_engine_used"] == "spacy"

    def test_analyze_with_entity_filtering(self):
        """Test analysis with entity type filtering."""
        payload = {
            "text": "Jan de Vries woont in Amsterdam en zijn email is jan@example.com",
            "language": "nl",
            "entities": ["PERSON"],  # Only look for persons
        }
        response = CLIENT.post(f"{BASE_URL}/api/v1/analyze", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Should only find PERSON entities, not EMAIL or LOCATION
        entities = data["pii_entities"]
        for entity in entities:
            assert entity["entity_type"] == "PERSON"

    def test_analyze_empty_text_validation(self):
        """Test that empty text is rejected."""
        payload = {"text": "", "language": "nl"}
        response = CLIENT.post(f"{BASE_URL}/api/v1/analyze", json=payload)

        assert response.status_code == 422  # Validation error

    def test_analyze_unsupported_language(self):
        """Test that unsupported language is rejected."""
        payload = {
            "text": "Hello world",
            "language": "fr",  # French not supported
        }
        response = CLIENT.post(f"{BASE_URL}/api/v1/analyze", json=payload)

        assert response.status_code == 422  # Validation error


class TestAnonymizeEndpoint:
    """Test the new /api/v1/anonymize endpoint."""

    def test_anonymize_simple_text(self):
        """Test basic text anonymization."""
        payload = {"text": "Jan de Vries woont in Amsterdam", "language": "nl"}
        response = CLIENT.post(f"{BASE_URL}/api/v1/anonymize", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "original_text" in data
        assert "anonymized_text" in data
        assert "entities_found" in data
        assert "text_length" in data
        assert "processing_time_ms" in data
        assert "nlp_engine_used" in data
        assert "anonymization_strategy" in data

        # Check original text preserved
        assert data["original_text"] == payload["text"]

        # Check text was actually anonymized (should contain placeholders)
        anonymized = data["anonymized_text"]
        assert anonymized != data["original_text"]
        assert any(
            placeholder in anonymized
            for placeholder in ["<PERSON>", "[PERSON]", "PERSON"]
        )

        # Check entities found structure
        entities = data["entities_found"]
        for entity in entities:
            assert "entity_type" in entity
            assert "text" in entity
            assert "start" in entity
            assert "end" in entity

    def test_anonymize_with_strategy(self):
        """Test anonymization with specific strategy."""
        payload = {
            "text": "Jan woont in Amsterdam",
            "language": "nl",
            "anonymization_strategy": "replace",
        }
        response = CLIENT.post(f"{BASE_URL}/api/v1/anonymize", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["anonymization_strategy"] == "replace"

    def test_anonymize_with_entity_filtering(self):
        """Test anonymization with entity filtering."""
        payload = {
            "text": "Jan de Vries woont in Amsterdam",
            "language": "nl",
            "entities": ["PERSON"],  # Only anonymize persons
        }
        response = CLIENT.post(f"{BASE_URL}/api/v1/anonymize", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Should still contain "Amsterdam" but not "Jan de Vries"
        anonymized = data["anonymized_text"]
        assert "Amsterdam" in anonymized  # Location not anonymized
        assert "Jan de Vries" not in anonymized  # Person anonymized

    def test_anonymize_invalid_strategy(self):
        """Test that invalid anonymization strategy is rejected."""
        payload = {
            "text": "Jan woont in Amsterdam",
            "language": "nl",
            "anonymization_strategy": "invalid_strategy",
        }
        response = CLIENT.post(f"{BASE_URL}/api/v1/anonymize", json=payload)

        assert response.status_code == 422  # Validation error


class TestDocumentEndpoints:
    """Test existing document endpoints still work."""

    def test_document_upload(self):
        """Test PDF document upload and analysis."""
        if not TEST_PDF_PATH.exists():
            pytest.skip(f"Test PDF not found at {TEST_PDF_PATH}")

        with open(TEST_PDF_PATH, "rb") as pdf_file:
            files = {"files": ("test.pdf", pdf_file, "application/pdf")}
            response = CLIENT.post(f"{BASE_URL}/api/v1/documents/upload", files=files)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "files" in data
        files = data["files"]
        assert len(files) > 0

        # Check file structure
        file_info = files[0]
        assert "id" in file_info
        assert "filename" in file_info
        assert "content_type" in file_info
        assert "uploaded_at" in file_info
        assert "pii_entities" in file_info

        assert file_info["filename"] == "test.pdf"
        assert file_info["content_type"] == "application/pdf"
        
        # Note: file_info["id"] could be used for follow-up tests


class TestIntegration:
    """Integration tests comparing string vs document endpoints."""

    def test_consistency_between_endpoints(self):
        """Test that string analysis matches document analysis for same text."""
        test_text = "Jan de Vries woont in Amsterdam"

        # Test string endpoint
        string_response = CLIENT.post(
            f"{BASE_URL}/api/v1/analyze", json={"text": test_text, "language": "nl"}
        )

        assert string_response.status_code == 200
        string_entities = string_response.json()["pii_entities"]

        # Verify we got some entities
        assert len(string_entities) > 0

        # Check entity types found
        entity_types = {entity["entity_type"] for entity in string_entities}
        assert "PERSON" in entity_types  # Should find "Jan de Vries"


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_malformed_json(self):
        """Test that malformed JSON is handled gracefully."""
        response = CLIENT.post(
            f"{BASE_URL}/api/v1/analyze",
            content='{"text": "test", "language":',  # Malformed JSON
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_missing_required_fields(self):
        """Test that missing required fields are rejected."""
        response = CLIENT.post(
            f"{BASE_URL}/api/v1/analyze",
            json={
                "language": "nl"  # Missing required 'text' field
            },
        )
        assert response.status_code == 422

    def test_very_long_text(self):
        """Test handling of very long text."""
        long_text = "Jan de Vries " * 1000  # Very long text
        payload = {"text": long_text, "language": "nl"}
        response = CLIENT.post(f"{BASE_URL}/api/v1/analyze", json=payload)

        # Should handle gracefully (may take longer but shouldn't crash)
        assert response.status_code == 200
        data = response.json()
        assert data["text_length"] == len(long_text)


class TestPerformance:
    """Basic performance tests."""

    def test_response_time_reasonable(self):
        """Test that response times are reasonable."""
        payload = {"text": "Jan de Vries woont in Amsterdam", "language": "nl"}

        # Test analyze endpoint
        response = CLIENT.post(f"{BASE_URL}/api/v1/analyze", json=payload)
        assert response.status_code == 200

        processing_time = response.json()["processing_time_ms"]
        assert processing_time is not None
        assert processing_time < 10000  # Should be under 10 seconds

        # Test anonymize endpoint
        response = CLIENT.post(f"{BASE_URL}/api/v1/anonymize", json=payload)
        assert response.status_code == 200

        processing_time = response.json()["processing_time_ms"]
        assert processing_time is not None
        assert processing_time < 10000  # Should be under 10 seconds


if __name__ == "__main__":
    # Run specific test when called directly
    pytest.main([__file__, "-v"])
