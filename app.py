from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os

from preprocess import preprocess_image
from pdf_processor import pdf_to_images

from ocr_service import (
    run_ocr_with_confidence,
    retry_khasra_ocr
)

from extract import extract_fields
from field_confidence import calculate_field_confidence
from evidence import find_evidence
from page_evidence import find_field_page
from validate import validate_record


app = FastAPI(title="Land Record AI Service")

UPLOAD_DIR = "temp"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "AI service running"
    }


# ============================================================
# EXTRACT
# ============================================================

@app.post("/extract")
async def extract_document(file: UploadFile = File(...)):

    try:

        # ----------------------------------------------------
        # 1. File validation
        # ----------------------------------------------------

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No file provided."
            )

        filename = os.path.basename(file.filename)

        allowed_extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".pdf"
        }

        extension = os.path.splitext(filename)[1].lower()

        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Unsupported file type. "
                    "Use PNG, JPG, JPEG or PDF."
                )
            )

        # ----------------------------------------------------
        # 2. Save upload
        # ----------------------------------------------------

        input_path = os.path.join(
            UPLOAD_DIR,
            filename
        )

        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        # ----------------------------------------------------
        # 3. Convert PDF to pages
        # ----------------------------------------------------

        if extension == ".pdf":

            page_images = pdf_to_images(
                input_path,
                output_dir=os.path.join(
                    UPLOAD_DIR,
                    "pdf_pages"
                )
            )

        else:

            page_images = [
                input_path
            ]

        if not page_images:

            return {
                "status": "Needs Review",
                "reviewRequired": True,
                "issues": [
                    {
                        "reason": "No pages found in document."
                    }
                ],
                "data": {},
                "confidence": {},
                "evidence": {},
                "pages": []
            }

        # ----------------------------------------------------
        # 4. OCR all pages
        # ----------------------------------------------------

        combined_text = ""
        all_words = []
        page_results = []

        for page_number, image_path in enumerate(
            page_images,
            start=1
        ):

            # Original OCR first
            text, words = run_ocr_with_confidence(
                image_path
            )

            # Preprocessing fallback
            if len(words) < 3:

                processed_path = os.path.join(
                    UPLOAD_DIR,
                    f"processed_page_{page_number}.png"
                )

                preprocess_image(
                    image_path,
                    processed_path
                )

                processed_text, processed_words = (
                    run_ocr_with_confidence(
                        processed_path
                    )
                )

                if len(processed_words) > len(words):

                    text = processed_text
                    words = processed_words

            page_results.append({
                "page": page_number,
                "text": text,
                "word_count": len(words)
            })

            combined_text += (
                f"\n[PAGE {page_number}]\n"
                f"{text}\n"
            )

            all_words.extend(words)

        # ----------------------------------------------------
        # 5. OCR failure
        # ----------------------------------------------------

        if not combined_text.strip():

            return {
                "status": "Needs Review",
                "reviewRequired": True,
                "issues": [
                    {
                        "reason": (
                            "Unable to extract readable text."
                        )
                    }
                ],
                "data": {},
                "confidence": {},
                "evidence": {},
                "pages": page_results
            }

        # ----------------------------------------------------
        # 6. Extract fields
        # ----------------------------------------------------

        fields = extract_fields(
            combined_text
        )

        # ----------------------------------------------------
        # 7. Field confidence
        # ----------------------------------------------------

        field_confidence = {}

        for field, value in fields.items():

            score = calculate_field_confidence(
                field,
                value,
                all_words
            )

            field_confidence[field] = score

        # ----------------------------------------------------
        # 8. Khasra retry
        # ----------------------------------------------------

        khasra_value = fields.get(
            "khasraNumber"
        )

        khasra_confidence = field_confidence.get(
            "khasraNumber",
            0
        )

        if (
            khasra_value
            and khasra_confidence < 0.80
        ):

            retry_value = retry_khasra_ocr(
                page_images[0]
            )

            if retry_value:
                fields["khasraNumber"] = retry_value

                # Keep conservative confidence.
                field_confidence[
                    "khasraNumber"
                ] = 0.05

        # ----------------------------------------------------
        # 9. Evidence + page
        # ----------------------------------------------------

        field_evidence = {}

        for field, value in fields.items():

            evidence_text = find_evidence(
                combined_text,
                value
            )

            page_number = find_field_page(
                value,
                page_results
            )

            field_evidence[field] = {
                "text": evidence_text,
                "page": page_number
            }

        # ----------------------------------------------------
        # 10. Existing records
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # 11. Validation
        # ----------------------------------------------------

        validation = validate_record(
            fields,
            field_confidence,
            existing_records
        )

        # ----------------------------------------------------
        # 12. Build human-review issues
        # ----------------------------------------------------

        issues = []

        # Low-confidence fields
        for field, score in field_confidence.items():

            if score < 0.80 and fields.get(field):

                evidence = field_evidence.get(
                    field,
                    {}
                )

                issues.append({
                    "field": field,
                    "extractedValue": fields[field],
                    "confidence": score,
                    "page": evidence.get("page"),
                    "reason": "Low OCR confidence"
                })

        # Validation flags
        for flag in validation["flags"]:

            issues.append({
                "field": None,
                "extractedValue": None,
                "confidence": None,
                "page": None,
                "reason": flag
            })

        review_required = (
            validation["status"] == "Needs Review"
        )

        # ----------------------------------------------------
        # 13. Final response
        # ----------------------------------------------------

        return {
            "status": validation["status"],
            "reviewRequired": review_required,
            "data": fields,
            "confidence": field_confidence,
            "evidence": field_evidence,
            "issues": issues,
            "flags": validation["flags"],
            "pages": page_results
        }

    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except HTTPException:
        raise

    except Exception as error:

        print(
            f"❌ AI processing error: {error}"
        )

        return {
            "status": "Needs Review",
            "reviewRequired": True,
            "data": {},
            "confidence": {},
            "evidence": {},
            "issues": [
                {
                    "field": None,
                    "extractedValue": None,
                    "confidence": None,
                    "page": None,
                    "reason": "AI processing failed."
                }
            ],
            "flags": [
                "Please send the document for human review."
            ],
            "pages": []
        }