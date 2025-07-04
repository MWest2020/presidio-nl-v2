"""Mock objects for PDF XMP utility in tests."""

from unittest.mock import patch


def patch_pdf_xmp():
    """Return a patch for the pdf_xmp utility functions."""
    return patch("src.api.utils.pdf_xmp.anonymize_pdf", return_value=None)
