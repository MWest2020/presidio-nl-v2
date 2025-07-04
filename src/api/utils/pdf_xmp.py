import hashlib
import re
import uuid
import xml.sax.saxutils as saxutils
from typing import Dict, List, Optional, Tuple

import pikepdf
import pymupdf

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

    doc = pymupdf.open(input_path)
    occurrences: List[_Occurrence] = []
    id_counter = 0

    for target, entity_type in replacements.items():
        mask = masks.get(entity_type, f"[{entity_type.upper()}]")
        for page_idx, page in enumerate(doc):
            rects = page.search_for(target)
            for r in rects:
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

                # Redact & overlay mask
                page.add_redact_annot(r, fill=(1, 1, 1))
                page.apply_redactions()
                page.insert_textbox(r, mask, fontsize=12, color=(0, 0, 0), align=0)

    doc.save(output_path, incremental=incremental_save)

    _embed_occurrences_xmp(output_path, occurrences)
    return occurrences  # For further processing/testing


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
    with pikepdf.Pdf.open(input_path) as pdf:
        if "/Metadata" not in pdf.Root:
            return []
        xmp_xml = pdf.Root.Metadata.read_bytes().decode("utf-8", errors="replace")

    tag_re = re.compile(r"<rdf:Description([^>]*)/>", re.DOTALL)
    prop_re = re.compile(r"custom:([A-Za-z]+)=\"([^\"]*)\"")

    annotations: List[dict] = []
    for m in tag_re.finditer(xmp_xml):
        attrs_block = m.group(1)
        props = {k: saxutils.unescape(v) for k, v in prop_re.findall(attrs_block)}
        if decryption_key and "EncryptedEntity" in props:
            try:
                plaintext = decrypt_entity(
                    props["EncryptedEntity"], decryption_key, header
                )
                props["entity"] = plaintext.decode("utf-8", errors="replace")
            except Exception:
                props["entity"] = None  # leave undecoded # type: ignore
        annotations.append(props)
    return annotations


def _embed_occurrences_xmp(pdf_path: str, occs: List[_Occurrence]) -> None:
    """Create /Metadata with one <rdf:Description> element per occurrence."""

    def _make_description(o: _Occurrence) -> str:
        attrs = {
            "custom:Id": o["id"],
            "custom:Page": str(o["page"]),
            "custom:Rect": ",".join(f"{v:.2f}" for v in o["rect"]),
            "custom:EntityType": o["entity_type"],
            "custom:EntityMask": o["entity_mask"],
            "custom:EncryptedEntity": o["encrypted_entity"],
            "custom:Fingerprint": o["fingerprint"],
        }
        # XML-escape values (quotes, ampersands, etc.)
        esc = {k: saxutils.escape(v, {'"': "&quot;"}) for k, v in attrs.items()}
        return (
            "  <rdf:Description rdf:about='' "
            + " ".join(f'{k}="{v}"' for k, v in esc.items())
            + "/>"
        )

    # Build one <rdf:Description> per occurrence
    descriptions = "\n".join(_make_description(o) for o in occs)
    packet_id = uuid.uuid4().hex  # unique ID per XMP packet

    xmp = f"""<?xpacket begin='' id='{packet_id}'>
<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
         xmlns:custom='http://example.com/custom/'>
{descriptions}
</rdf:RDF>
<?xpacket end='w'?>"""

    # Embed/replace the metadata stream
    with pikepdf.Pdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        pdf.Root.Metadata = pdf.make_stream(xmp.encode("utf-8"))
        pdf.save(pdf_path)


def _attrs_to_dict(attr_block: str) -> dict:
    """Convert the attribute section of an XML tag into a dict."""
    matches = re.findall(r"(custom:[^=]+)=\"([^\"]*)\"", attr_block)
    return {k.split(":", 1)[1]: saxutils.unescape(v) for k, v in matches}


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
