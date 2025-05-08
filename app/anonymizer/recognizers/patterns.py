from presidio_analyzer import Pattern, PatternRecognizer
from typing import List, Optional

class DutchPhoneNumberRecognizer(PatternRecognizer):
    def __init__(self, patterns: Optional[List[Pattern]] = None, context: Optional[List[str]] = None, supported_language: str = "nl"):
        if patterns is None:
            patterns = [Pattern("DUTCH_PHONE", r"\b(?:0|(?:\+|00)31)[- ]?(?:\d[- ]?){9}\b", 0.6)]
        super().__init__(supported_entity="PHONE_NUMBER", patterns=patterns, context=context, supported_language=supported_language)

class DutchIBANRecognizer(PatternRecognizer):
    def __init__(self, patterns: Optional[List[Pattern]] = None, context: Optional[List[str]] = None, supported_language: str = "nl"):
        if patterns is None:
            patterns = [Pattern("DUTCH_IBAN", r"\bNL\d{2}[A-Z]{4}\d{10}\b", 0.6)]
        super().__init__(supported_entity="IBAN", patterns=patterns, context=context, supported_language=supported_language)

class DutchEmailRecognizer(PatternRecognizer):
    def __init__(self, patterns: Optional[List[Pattern]] = None, context: Optional[List[str]] = None, supported_language: str = "nl"):
        if patterns is None:
            patterns = [Pattern("EMAIL_ADDRESS", r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", 0.6)]
        super().__init__(supported_entity="EMAIL", patterns=patterns, context=context, supported_language=supported_language) 