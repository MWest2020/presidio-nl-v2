import json
from typing import Any, Dict, Optional

import pikepdf
import pymupdf


def annotate_pdf(
    input_path: str,
    output_path: str,
    target: str,
    metadata: dict,
    replacement: Optional[str] = None,
) -> None:
    """Annotate a PDF by searching for target text, optionally replacing it, and embedding metadata.

    A step-by-step process:
    1. Open the PDF and optionally redact/replace target text.
    2. Collect locations and metadata for each match.
    3. Save intermediate PDF.
    4. Embed collected metadata as JSON in the XMP metadata stream.

    Args:
        input_path (str): Path to the input PDF file.
        output_path (str): Path to save the annotated PDF.
        target (str): Text to search for in the PDF.
        metadata (dict): Metadata to embed in the PDF.
        replacement (Optional[str]): Text to replace the target text with. If None, no replacement is done.

    Returns:
        None: The function modifies the PDF in place and saves it to `output_path`.
    """
    # Step 1-2: Process with PyMuPDF
    doc = pymupdf.open(input_path)
    occurrences = []
    for page_number, page in enumerate(doc, start=1):
        rects = page.search_for(target)
        for r in rects:
            if replacement is not None:
                page.add_redact_annot(r, fill=(1, 1, 1))
                page.apply_redactions()
                page.insert_textbox(r, replacement, fontsize=12)
            # Record occurrence
            occurrences.append(
                {
                    "page": page_number,
                    "rect": (r.x0, r.y0, r.x1, r.y1),
                    "metadata": metadata,
                }
            )
    doc.save(output_path, incremental=False)

    # Step 3-4: Embed JSON in XMP with pikepdf
    with pikepdf.Pdf.open(output_path, allow_overwriting_input=True) as pdf:
        # Build JSON blob of all occurrences
        blob = json.dumps({"occurrences": occurrences})

        # Store the data as a CDATA section to avoid XML escaping issues
        xmp = f"""<?xpacket begin='' id="W5M0MpCehiHzreSzNTczkc9d"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:custom="http://example.com/custom/">
  <rdf:Description rdf:about="">
    <custom:AnnotationData><![CDATA[{blob}]]></custom:AnnotationData>
  </rdf:Description>
</rdf:RDF>
<?xpacket end='w'?>"""
        pdf.Root.Metadata = pdf.make_stream(xmp.encode("utf-8"))
        pdf.save(output_path)


def extract_annotations(input_path: str) -> Dict[str, Any]:
    """Extract annotations from PDF XMP metadata.

    Step-by-step process:
    1. Open the PDF.
    2. Read and parse JSON from the XMP metadata.

    Args:
        input_path (str): Path to the input PDF file.

    Returns:
        A dictionary containing the parsed annotations (e.g., {"occurrences": [...]})
    """
    with pikepdf.Pdf.open(input_path) as pdf:
        if "/Metadata" in pdf.Root:
            xmp_stream = pdf.Root.Metadata.read_bytes().decode("utf-8")

            # Look for the AnnotationData content (not in CDATA anymore)
            import re

            annotation_pattern = r"<custom:AnnotationData>(.*?)</custom:AnnotationData>"
            match = re.search(annotation_pattern, xmp_stream, re.DOTALL)
            if match:
                json_blob = match.group(1)
                try:
                    return dict(json.loads(json_blob))
                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON from CDATA: {e}")
                    print(f"JSON data: {json_blob[:100]}...")

            # Try alternative pattern (attribute-style)
            start = xmp_stream.find('custom:AnnotationData="')
            if start != -1:
                start += len('custom:AnnotationData="')
                end = xmp_stream.find('"', start)
                json_blob = xmp_stream[start:end]

                # Unescape XML entities
                import xml.sax.saxutils as saxutils

                unescaped_json = saxutils.unescape(json_blob)

                try:
                    return dict(json.loads(unescaped_json))
                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON: {e}")
                    print(f"JSON data: {unescaped_json[:100]}...")

            # Debug: Dump the XMP content to see what's actually in there
            print("\nXMP content preview:")
            print(xmp_stream[:500] + "...")
            print("\n")
            print("Metadata found but AnnotationData not found in XMP")
        else:
            print("No /Metadata found in PDF Root")

    return {}


if __name__ == "__main__":
    # Example usage
    input_pdf = "input.pdf"
    output_pdf = "output.pdf"
    print("Annotating PDF:", input_pdf)

    # Debug: Check if the input file exists and can be opened
    try:
        with open(input_pdf, "rb") as f:
            print(f"Successfully opened {input_pdf}, size: {len(f.read())} bytes")
    except Exception as e:
        print(f"Error opening input file: {e}")

    # Specify the search term and run annotation
    search_term = "markwesterweel@conduction.nl"
    print(f"Searching for: {search_term}")

    try:
        annotate_pdf(
            input_path=input_pdf,
            output_path=output_pdf,
            target=search_term,
            replacement="REDACTED",
            metadata={"CaseID": "1234", "Reviewer": "Alice"},
        )
        print(f"Successfully annotated PDF and saved to {output_pdf}")

        with open(output_pdf, "rb") as f:
            output_size = len(f.read())
            print(f"Output file size: {output_size} bytes")

        print("Extracting annotations from:", output_pdf)
        data = extract_annotations(output_pdf)
        print("Extracted data:", json.dumps(data, indent=2))

    except Exception as e:
        import traceback

        print(f"Error during processing: {e}")
        traceback.print_exc()
