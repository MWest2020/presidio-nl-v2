"""Mock objects for text analyzer in tests."""

from unittest.mock import patch


class MockTextAnalyzer:
    """Mock implementation of ModularTextAnalyzer for testing."""

    def analyze_text(self, text):
        """Mock text analysis with predefined entities."""
        # Return some mock entities regardless of input text
        # This simplifies testing by providing consistent results
        if not text:
            return []

        return [
            {
                "entity_type": "PERSON",
                "text": "John Doe",
                "start": 10,
                "end": 18,
                "score": 0.95,
            },
            {
                "entity_type": "EMAIL",
                "text": "john.doe@example.com",
                "start": 30,
                "end": 50,
                "score": 0.99,
            },
            {
                "entity_type": "LOCATION",
                "text": "New York",
                "start": 60,
                "end": 68,
                "score": 0.85,
            },
            {
                "entity_type": "ORGANIZATION",
                "text": "ACME Corp",
                "start": 80,
                "end": 89,
                "score": 0.80,
            },
            {
                "entity_type": "DATE",
                "text": "2023-01-01",
                "start": 100,
                "end": 110,
                "score": 0.98,
            },
        ]


def patch_text_analyzer():
    """Return a patch for the ModularTextAnalyzer."""
    return patch(
        "src.api.services.text_analyzer.ModularTextAnalyzer",
        return_value=MockTextAnalyzer(),
    )
