from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class DutchPhoneNumberRecognizer(PatternRecognizer):
    """Herkenner voor Nederlandse telefoonnummers.

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
            context=context,  # type: ignore[arg-type]
            supported_language=supported_language,
        )


class DutchIBANRecognizer(PatternRecognizer):
    """Herkenner voor Nederlandse IBAN bankrekeningnummers.

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
            context=context,  # type: ignore[arg-type]
            supported_language=supported_language,
        )


class DutchEmailRecognizer(PatternRecognizer):
    """Herkenner voor e-mailadressen volgens het standaard e-mailpatroon."""

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
            context=context,  # type: ignore[arg-type]
            supported_language=supported_language,
        )


class DutchBSNRecognizer(PatternRecognizer):
    def __init__(self, context: Optional[List[str]] = None) -> None:
        pattern = Pattern("NL_BSN", r"\b\d{3}[- ]?\d{2}[- ]?\d{3}\b", 0.6)
        super().__init__(
            supported_entity="NATIONAL_ID",
            patterns=[pattern],
            context=context,  # type: ignore[arg-type]
            supported_language="nl",
        )

    def _is_valid_bsn(self, bsn: str) -> bool:
        digits = [int(d) for d in bsn if d.isdigit()]
        return sum((9 - i) * d for i, d in enumerate(digits)) % 11 == 0


class DutchPostcodeRecognizer(PatternRecognizer):
    def __init__(
        self, context: Optional[List[str]] = None, supported_language: str = "nl"
    ) -> None:
        pattern = Pattern("NL_POSTCODE", r"\b\d{4}\s?[A-Z]{2}\b", 0.55)
        super().__init__(
            "POSTCODE",
            patterns=[pattern],
            context=context,  # type: ignore[arg-type]
            supported_language=supported_language,
        )


# 2. BTW-/VAT-nummer (NL999999999B99 – nieuw formaat)
class DutchVATRecognizer(PatternRecognizer):
    def __init__(
        self, context: Optional[List[str]] = None, supported_language: str = "nl"
    ) -> None:
        pattern = Pattern("NL_VAT", r"\bNL\d{9}B\d{2}\b", 0.6)
        super().__init__(
            "VAT_NUMBER",
            patterns=[pattern],
            context=context,  # type: ignore[arg-type]
            supported_language=supported_language,
        )


# 3. KvK-nummer (8 cijfers in Handelsregister)
class DutchKvKRecognizer(PatternRecognizer):
    def __init__(
        self, context: Optional[List[str]] = None, supported_language: str = "nl"
    ) -> None:
        patterns = [
            Pattern("KVK_8_DIGIT", r"\b\d{8}\b", 0.45)  # raise score with context
        ]
        super().__init__(
            "KVK_NUMBER",
            patterns=patterns,
            context=context,  # type: ignore[arg-type]
            supported_language=supported_language,
        )


# Nederlands kenteken (6 posities, diverse combinaties)
_LICENSE_PATTERNS = [
    r"[A-Z]{2}-\d{2}-\d{2}",
    r"\d{2}-\d{2}-[A-Z]{2}",
    r"\d{2}-[A-Z]{2}-\d{2}",
    r"[A-Z]{2}-\d{2}-[A-Z]{2}",
    r"[A-Z]{2}-[A-Z]{2}-\d{2}",
    r"\d{2}-[A-Z]{2}-[A-Z]{2}",
]


class DutchLicensePlateRecognizer(PatternRecognizer):
    def __init__(
        self, context: Optional[List[str]] = None, supported_language: str = "nl"
    ) -> None:
        pattern = Pattern("NL_PLATE", rf"\b(?:{'|'.join(_LICENSE_PATTERNS)})\b", 0.5)
        super().__init__(
            "LICENSE_PLATE",
            patterns=[pattern],
            context=context,  # type: ignore[arg-type]
            supported_language=supported_language,
        )


# Taal-onafhankelijke IPv4-adres-herkenner
class IPv4Recognizer(PatternRecognizer):
    def __init__(
        self, context: Optional[List[str]] = None, supported_language: str = "any"
    ) -> None:
        pattern = Pattern(
            "IPV4",
            r"\b(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)"
            r"(?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}\b",
            0.5,
        )
        super().__init__(
            "IP_ADDRESS",
            patterns=[pattern],
            context=context,  # type: ignore[arg-type]
            supported_language=supported_language,
        )
