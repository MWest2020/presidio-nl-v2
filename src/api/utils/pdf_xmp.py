import hashlib
import json
import logging
import re
import xml.sax.saxutils as saxutils
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pikepdf
import pymupdf

from src.api.services.text_analyzer import ModularTextAnalyzer
from src.api.utils.crypto import (
    aes_gcm_decrypt as decrypt_entity,
)
from src.api.utils.crypto import (
    aes_gcm_encrypt as encrypt_entity,
)
from src.api.utils.crypto import (
    fingerprint_sha256 as get_fingerprint,
)

_DEFAULT_ENTITY_MASK = {
    "person": "[PERSON]",
    "iban": "[IBAN]",
    "email": "[EMAIL]",
    "phone": "[PHONE]",
}


class _Occurrence(dict):
    """Typed helper for a single PII occurrence."""

    id: str  # Unique ID within the document
    page: int  # 1‑based page index
    rect: Tuple[float, float, float, float]  # (x0,y0,x1,y1)
    entity_type: str
    entity_mask: str
    encrypted_entity: str
    fingerprint: str


def extract_text_from_pdf(source_path: Path) -> str:
    text = ""
    try:
        doc = pymupdf.open(str(source_path))
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
    except Exception:
        text = ""
    return text


async def extract_unique_entities(
    analyzer: ModularTextAnalyzer,
    text: str,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Extract unique entities from the given text using the provided analyzer.

    Args:
        analyzer (ModularTextAnalyzer): The text analyzer instance to use for entity extraction.
        text (str): The text to analyze for entities.

    Returns:
        tuple[list[dict[str, str]], list[dict[str, str]]]: the first list contains all entities found,
            the second list contains unique entities with their types and text.
    """
    entities = analyzer.analyze_text(text) if text else []
    unique: list[dict[str, str]] = []
    seen = set()
    for ent in entities:
        key = (ent["entity_type"], ent["text"])
        if key not in seen:
            unique.append({"entity_type": ent["entity_type"], "text": ent["text"]})
            seen.add(key)
    return entities, unique


def anonymize_pdf(
    input_path: str,
    output_path: str,
    replacements: Dict[str, str],
    private_key: str,
    *,
    entity_masks: Optional[Dict[str, str]] = None,
    incremental_save: bool = False,
) -> List[dict]:
    """Anonymise *input_path* and write to *output_path*.

    Args:
        input_path (str): Path to the input PDF file.
        output_path (str): Path to save the anonymised PDF.
        replacements (Dict[str, str]): Mapping of target text to entity type.
            E.g. {"Bob": "person", "NL91ABNA": "iban"}.
        private_key (str): Private key for encrypting PII entities.
        entity_masks (Optional[Dict[str, str]]): Custom masks for entity types.
        incremental_save (bool): If True, save changes incrementally to the PDF.

    Returns:
        List[dict]: List of occurrences with metadata about each redaction.
    """
    hashed_key = hashlib.sha256(private_key.encode()).digest()
    masks = {**_DEFAULT_ENTITY_MASK, **(entity_masks or {})}

    doc: pymupdf.Document = pymupdf.open(input_path)
    occurrences: List[_Occurrence] = []
    id_counter = 0

    for target, entity_type in replacements.items():
        mask = masks.get(entity_type, f"[{entity_type.upper()}]")
        for page_idx, page in enumerate(doc):
            page: pymupdf.Page
            rects = page.search_for(target)
            for r in rects:
                # Get text style information around the target text
                font_size = 11  # Default font size if we can't determine
                font_name = "Helvetica"
                try:
                    blocks = page.get_text("dict")["blocks"]
                except Exception as e:
                    if "font" in str(e):
                        logging.warning(
                            f"Could not determine font for page {page_idx + 1}: {e}"
                        )
                    blocks = []  # Fallback to empty list if text extraction fails
                for block in blocks:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            span_rect = pymupdf.Rect(span["bbox"])
                            if r.intersects(span_rect):
                                font_size = span.get("size", font_size)
                                font_name = span.get("font", font_name)
                                break

                logging.debug(
                    f"Found target target='{target.encode('utf-8', errors='ignore').decode('ascii', errors='ignore')}"
                    f"with font size {str(font_size)} and font name {str(font_name)}"
                )
                font_size = int(font_size)  # Ensure font size is an integer
                # Record before redaction so coordinates refer to original.
                occ: _Occurrence = {  # type: ignore
                    "id": f"ann{id_counter}",
                    "page": page_idx + 1,
                    "rect": (r.x0, r.y0, r.x1, r.y1),
                    "entity_type": entity_type,
                    "entity_mask": mask,
                    "encrypted_entity": encrypt_entity(
                        data=target.encode("utf-8"), key=hashed_key
                    ),
                    "key_fingerprint": get_fingerprint(data=private_key),
                }
                occurrences.append(occ)
                id_counter += 1

                try:
                    page.add_redact_annot(
                        r,
                        fill=(1, 1, 1),
                        text=mask,
                        fontsize=font_size,
                    )
                    page.apply_redactions()
                except Exception as e:
                    logging.error(
                        f"Failed to add redaction for target='{target.encode('utf-8', errors='replace').decode('ascii', errors='ignore')} on page {page_idx + 1}: {e}"
                    )
                    continue  # Skip this occurrence if redaction fails
                logging.debug(
                    f"Added redaction for target='{
                        target.encode('utf-8', errors='ignore').decode(
                            'ascii', errors='ignore'
                        )
                    }' on page {page_idx + 1}."
                )

    doc.save(output_path, incremental=incremental_save)

    _embed_occurrences_xmp(output_path, occurrences)
    return occurrences  # For further processing/testing # type: ignore


def extract_annotations(
    input_path: str,
    *,
    decryption_key: Optional[bytes] = None,
    header: bytes = b"header",
) -> List[dict]:
    """Return list of dictionaries parsed from XMP.

    If *decryption_key* is supplied, the function will attempt to decrypt the
    ``EncryptedEntity`` field of each record and add ``entity`` (plaintext).
    """
    logging.debug(f"Extracting annotations from {input_path}")
    try:
        with pikepdf.Pdf.open(input_path) as pdf:
            if "/Metadata" not in pdf.Root:
                logging.debug("No metadata found in PDF")
                return []

            try:
                # Use errors='ignore' to handle any problematic characters
                xmp_xml = pdf.Root.Metadata.read_bytes().decode(
                    "utf-8", errors="ignore"
                )
            except UnicodeDecodeError:
                logging.error("Failed to decode XMP metadata as UTF-8")
                return []

            # Remove any byte order mark that might cause issues
            if xmp_xml.startswith("\ufeff"):
                xmp_xml = xmp_xml[1:]

            # Output debug info about the metadata structure
            safe_preview = "".join(c for c in xmp_xml[:200] if ord(c) < 128)
            logging.debug(f"Raw XMP content preview: {safe_preview}...")

    except Exception as e:
        logging.error(f"Failed to open PDF or read metadata: {e}")
        return []

    # Try multiple extraction methods for maximum compatibility

    # Method 1: Look for CDATA section with various patterns
    cdata_patterns = [
        r"<custom:AnnotationData><!\[CDATA\[(.*?)\]\]></custom:AnnotationData>",
        r"<custom:AnnotationData>\s*<!\[CDATA\[(.*?)\]\]>\s*</custom:AnnotationData>",
        r"<custom:AnnotationData>(.*?)</custom:AnnotationData>",  # Non-CDATA version
    ]

    for pattern in cdata_patterns:
        match = re.search(pattern, xmp_xml, re.DOTALL)
        if match:
            json_blob = match.group(1).strip()
            try:
                data = json.loads(json_blob)
                if isinstance(data, dict) and "occurrences" in data:
                    occurrences = data["occurrences"]
                    if occurrences:
                        logging.debug(
                            f"Found {len(occurrences)} occurrences using CDATA pattern"
                        )

                        # Process decryption if key is provided
                        if decryption_key:
                            for occ in occurrences:
                                if "encrypted_entity" in occ:
                                    try:
                                        plaintext = decrypt_entity(
                                            occ["encrypted_entity"],
                                            decryption_key,
                                            header,
                                        )

                                        occ["entity"] = plaintext.decode(
                                            "utf-8", errors="replace"
                                        )
                                        logging.debug(
                                            f"Decrypted entity for occurrence ID {occ.get('id', 'unknown')}"
                                        )
                                    except Exception as e:
                                        logging.error(f"Failed to decrypt entity: {e}")
                                        occ["entity"] = None
                        else:
                            logging.debug(
                                "No decryption key provided, skipping entity decryption"
                            )

                        return occurrences
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse JSON from pattern match: {e}")
                blob_preview = json_blob[:100] if json_blob else "empty"
                logging.debug(f"JSON data preview: {blob_preview}...")

    # Method 2: Try attribute-style extraction
    attr_start = xmp_xml.find('custom:AnnotationData="')
    if attr_start != -1:
        attr_start += len('custom:AnnotationData="')
        attr_end = xmp_xml.find('"', attr_start)
        if attr_end != -1:
            json_blob = xmp_xml[attr_start:attr_end]
            # Unescape XML entities
            unescaped_json = saxutils.unescape(json_blob)

            try:
                data = json.loads(unescaped_json)
                if isinstance(data, dict) and "occurrences" in data:
                    occurrences = data["occurrences"]
                    if occurrences:
                        logging.debug(
                            f"Found {len(occurrences)} occurrences using attribute pattern"
                        )

                        # Process decryption if key is provided
                        if decryption_key:
                            for occ in occurrences:
                                if "encrypted_entity" in occ:
                                    try:
                                        plaintext = decrypt_entity(
                                            occ["encrypted_entity"],
                                            decryption_key,
                                            header,
                                        )
                                        occ["entity"] = plaintext.decode(
                                            "utf-8", errors="replace"
                                        )
                                    except Exception as e:
                                        logging.error(f"Failed to decrypt entity: {e}")
                                        occ["entity"] = None

                        return occurrences
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse JSON from attribute: {e}")

    # Method 3: Fallback to the old format with multiple Description elements
    tag_re = re.compile(r"<rdf:Description([^>]*)/>", re.DOTALL)
    prop_re = re.compile(r"custom:([A-Za-z]+)=\"([^\"]*)\"")

    annotations: List[dict] = []
    for m in tag_re.finditer(xmp_xml):
        attrs_block = m.group(1)
        props = {k: saxutils.unescape(v) for k, v in prop_re.findall(attrs_block)}
        if props:  # Only add if we found properties
            if decryption_key and "encrypted_entity" in props:
                try:
                    plaintext = decrypt_entity(
                        props["encrypted_entity"], decryption_key, header
                    )
                    props["entity"] = plaintext.decode("utf-8", errors="replace")
                except Exception:
                    props["entity"] = None  # leave undecoded # type: ignore
            annotations.append(props)

    if annotations:
        logging.debug(f"Found {len(annotations)} annotations using old format")
        return annotations

    # Method 4: Last resort - try to find JSON anywhere in the XMP
    # This is a bit risky but might catch JSON embedded in unusual ways
    json_pattern = r'\{"occurrences":\s*\[(.*?)\]\}'
    match = re.search(json_pattern, xmp_xml, re.DOTALL)
    if match:
        try:
            # Reconstruct the full JSON string
            json_blob = f'{{"occurrences": [{match.group(1)}]}}'
            data = json.loads(json_blob)
            occurrences = data.get("occurrences", [])
            if occurrences:
                logging.debug(
                    f"Found {len(occurrences)} occurrences using JSON pattern search"
                )

                # Process decryption if key is provided
                if decryption_key:
                    for occ in occurrences:
                        if "encrypted_entity" in occ:
                            try:
                                plaintext = decrypt_entity(
                                    occ["encrypted_entity"], decryption_key, header
                                )
                                occ["entity"] = plaintext.decode(
                                    "utf-8", errors="replace"
                                )
                            except Exception as e:
                                logging.error(f"Failed to decrypt entity: {e}")
                                occ["entity"] = None

                return occurrences
        except (json.JSONDecodeError, Exception) as e:
            logging.error(f"Failed to parse JSON from pattern search: {e}")

    # No annotations found with any method
    logging.debug("No annotations found in XMP with any extraction method")
    return []


def _embed_occurrences_xmp(pdf_path: str, occs: List[_Occurrence]) -> None:
    """Create /Metadata with one <rdf:Description> element per occurrence."""
    # Convert occurrences to JSON for embedding in CDATA section
    import json

    # Format the occurrences into a proper dictionary
    # Make sure to convert all values to standard Python types
    safe_occs = []
    for occ in occs:
        # Create a clean dictionary from the occurrence
        safe_occ = {
            "id": str(occ.get("id", "")),
            "page": int(occ.get("page", 0)),
            "rect": [float(v) for v in occ.get("rect", (0, 0, 0, 0))],
            "entity_type": str(occ.get("entity_type", "")),
            "entity_mask": str(occ.get("entity_mask", "")),
            "encrypted_entity": str(occ.get("encrypted_entity", "")),
            "key_fingerprint": str(occ.get("key_fingerprint", "")),
        }
        safe_occs.append(safe_occ)

    occurrences_dict = {"occurrences": safe_occs}

    # Convert to JSON string - ensure ASCII encoding to avoid Unicode issues
    json_blob = json.dumps(occurrences_dict, ensure_ascii=True)

    # Use a standard packet ID as seen in the working example
    xmp = f"""<?xpacket begin='' id='W5M0MpCehiHzreSzNTczkc9d'?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:custom="http://example.com/custom/">
  <rdf:Description rdf:about="">
    <custom:AnnotationData><![CDATA[{json_blob}]]></custom:AnnotationData>
  </rdf:Description>
</rdf:RDF>
<?xpacket end='w'?>"""

    # Debug output to help diagnose any issues
    logging.debug(f"XMP metadata preview (first 200 chars): {xmp[:200]}...")

    # First clear any existing metadata to avoid conflicts
    try:
        # Try to open and clean up the PDF before adding new metadata
        with pikepdf.Pdf.open(pdf_path, allow_overwriting_input=True) as pdf:
            # Create a clean XMP metadata object
            pdf.Root.Metadata = pdf.make_stream(xmp.encode("utf-8"))
            # Save without any additional options
            pdf.save(pdf_path)
            logging.debug(
                f"Embedded {len(occs)} occurrences in XMP metadata for {pdf_path}"
            )
    except Exception as e:
        logging.error(f"Failed to embed XMP metadata: {e}")
        # Print the first part of the XMP for debugging
        logging.error(f"XMP content preview: {xmp[:500]}...")


if __name__ == "__main__":
    res = extract_annotations("test.pdf")
    print(res)
    exit(0)
    import argparse

    parser = argparse.ArgumentParser(description="PDF anonymiser util")
    parser.add_argument("input", help="Input PDF path")
    parser.add_argument("output", help="Output PDF path")
    parser.add_argument(
        "--mapping",
        nargs="*",
        metavar="S=TYPE",
        help="Replacement mapping e.g. 'Bob=person' 'NL91ABNA=iban'",
    )
    parser.add_argument(
        "--key",
        default="your_private_key_here",
        help="Private key for encryption (will be hashed to appropriate length)",
    )
    args = parser.parse_args()

    mapping = {}
    for pair in args.mapping or []:
        try:
            key, etype = pair.split("=", 1)
            mapping[key] = etype
        except ValueError:
            parser.error(f"Invalid mapping pair: {pair}")

    anonymize_pdf(args.input, args.output, mapping, args.key)
    print("Done. Embedded", len(mapping), "PII item(s).")
