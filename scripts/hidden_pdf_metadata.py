import json
from typing import Optional

import pymupdf


def annotate_pdf(
    input_path: str,
    output_path: str,
    target: str,
    metadata: dict,
    replacement: Optional[str] = None,
) -> None:
    """1. Open the PDF.

    2. For each occurrence of `target`, optionally redact+replace it.
    3. At the location, add an invisible free-text annotation whose info dict holds your metadata.
    4. Save to output_path.
    """
    doc = pymupdf.open(input_path)
    for page in doc:
        # find bounding boxes for each match
        rects = page.search_for(target)
        for r in rects:
            # optional: redact and write replacement text
            if replacement is not None:
                page.add_redact_annot(r, fill=(1, 1, 1))
                page.apply_redactions()
                page.insert_textbox(r, replacement, fontsize=12)

            # add invisible free-text annotation
            annot = page.add_freetext_annot(
                r, text="", fontsize=0, opacity=0, border_width=0
            )
            info = annot.info
            # Store metadata as JSON in the contents field
            info["content"] = json.dumps(metadata)
            annot.set_info(info)
            annot.update()

    doc.save(output_path, incremental=False)


def extract_annotations(input_path: str) -> list:
    """1. Open the PDF.

    2. Iterate all annotations, collecting page number, rectangle, and metadata.
    Returns a list of dicts.
    """
    doc = pymupdf.open(input_path)
    results = []
    for page_number, page in enumerate(doc, start=1):
        for annot in page.annots(types=[pymupdf.PDF_ANNOT_FREE_TEXT]):
            info = annot.info
            rect = annot.rect
            # Extract and parse metadata from content field
            metadata = {}
            if info.get("content"):
                try:
                    metadata = json.loads(info["content"])
                except json.JSONDecodeError:
                    pass  # Not our JSON metadata

            results.append(
                {
                    "page": page_number,
                    "rect": (rect.x0, rect.y0, rect.x1, rect.y1),
                    "metadata": metadata,
                }
            )
    return results


if __name__ == "__main__":
    # Example usage
    input_pdf = "input.pdf"
    output_pdf = "output.pdf"
    annotate_pdf(
        input_path=input_pdf,
        output_path=output_pdf,
        target="markwesterweel@conduction.nl",
        replacement="REDACTED",
        metadata={"CaseID": "1234", "Reviewer": "Alice"},
    )
    # Later, in a different run:
    annotations = extract_annotations(output_pdf)
    for a in annotations:
        print(f"Page {a['page']} @ {a['rect']}: {a['metadata']}")

# Save this as annotation_utils.py
