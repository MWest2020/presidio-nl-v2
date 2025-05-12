from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class DutchPhoneNumberRecognizer(PatternRecognizer):
    """
    Herkenner voor Nederlandse telefoonnummers.
    Gebruikt een regex-patroon voor mobiele en vaste nummers in NL-formaat.
    """
    def __init__(
        self,
        context: Optional[List[str]] = None,
        supported_language: str = "nl",
    ) -> None:
        patterns = [
            Pattern("DUTCH_PHONE", r"\b(?:0|(?:\+|00)31)[- ]?(?:\d[- ]?){9}\b", 0.6)
        ]
        super().__init__(
            supported_entity="PHONE_NUMBER",
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )


class DutchIBANRecognizer(PatternRecognizer):
    """
    Herkenner voor Nederlandse IBAN bankrekeningnummers.
    Herkent alleen IBANs die beginnen met 'NL'.
    """
    def __init__(
        self,
        context: Optional[List[str]] = None,
        supported_language: str = "nl",
    ) -> None:
        patterns = [Pattern("DUTCH_IBAN", r"\bNL\d{2}[A-Z]{4}\d{10}\b", 0.6)]
        super().__init__(
            supported_entity="IBAN",
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )


class DutchEmailRecognizer(PatternRecognizer):
    """
    Herkenner voor e-mailadressen volgens het standaard e-mailpatroon.
    """
    def __init__(
        self,
        context: Optional[List[str]] = None,
        supported_language: str = "nl",
    ) -> None:
        patterns = [
            Pattern(
                "EMAIL_ADDRESS",
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                0.6,
            )
        ]
        super().__init__(
            supported_entity="EMAIL",
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
