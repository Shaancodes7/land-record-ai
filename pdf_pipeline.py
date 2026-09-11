import os

from pdf_processor import pdf_to_images
from ocr_service import run_ocr_with_confidence
from extract import extract_fields
from field_confidence import calculate_field_confidence
from evidence import find_evidence
from validate import validate_record


def process_pdf(pdf_path):
    # --------------------------------------------------
    # 1. PDF -> page images
    # --------------------------------------------------

    page_images = pdf_to_images(pdf_path)

    combined_text = ""
    all_words = []
    page_texts = []

    # --------------------------------------------------
    # 2. OCR each page
    # --------------------------------------------------

    for page_number, image_path in enumerate(
        page_images,
        start=1
    ):
        text, words = run_ocr_with_confidence(
            image_path
        )

        page_texts.append({
            "page": page_number,
            "text": text
        })

        combined_text += (
            f"\n[PAGE {page_number}]\n"
            f"{text}\n"
        )

        all_words.extend(words)

    # --------------------------------------------------
    # 3. Check OCR
    # --------------------------------------------------

    if not combined_text.strip():
        return {
            "status": "Needs Review",
            "flags": [
                "No readable text found in PDF."
            ],
            "data": {},
            "confidence": {},
            "evidence": {}
        }

    # --------------------------------------------------
    # 4. Extract fields from all pages
    # --------------------------------------------------

    fields = extract_fields(
        combined_text
    )

    # --------------------------------------------------
    # 5. Field confidence
    # --------------------------------------------------

    field_confidence = {}

    for field, value in fields.items():

        score = calculate_field_confidence(
            field,
            value,
            all_words
        )

        field_confidence[field] = score

    # --------------------------------------------------
    # 6. Evidence
    # --------------------------------------------------

    field_evidence = {}

    for field, value in fields.items():

        field_evidence[field] = find_evidence(
            combined_text,
            value
        )

    # --------------------------------------------------
    # 7. Existing records
    # Temporary data
    # --------------------------------------------------

    existing_records = [
        {
            "khasraNumber": "124/2",
            "ownerName": "Mahesh Kumar"
        },
        {
            "khasraNumber": "999/1",
            "ownerName": "Ramesh Singh"
        }
    ]

    # --------------------------------------------------
    # 8. Validation
    # --------------------------------------------------

    validation = validate_record(
        fields,
        field_confidence,
        existing_records
    )

    # --------------------------------------------------
    # 9. Result
    # --------------------------------------------------

    return {
        "data": fields,
        "confidence": field_confidence,
        "evidence": field_evidence,
        "status": validation["status"],
        "flags": validation["flags"],
        "pages": page_texts
    }