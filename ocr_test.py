import sys

from ocr_service import run_ocr_with_confidence
from extract import extract_fields
from field_confidence import calculate_field_confidence
from evidence import find_evidence
from validate import validate_record


# ============================================================
# 0. INPUT IMAGE
# ============================================================

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = "samplee.png"

image_path = f"documents/{filename}"

print(f"\nProcessing: {image_path}")


# ============================================================
# 1. OCR
# ============================================================

text, words = run_ocr_with_confidence(
    image_path
)

print("\n===== OCR TEXT =====\n")
print(text)


# ============================================================
# 2. FIELD EXTRACTION
# ============================================================

fields = extract_fields(text)

print("\n===== EXTRACTED FIELDS =====\n")

for field, value in fields.items():
    print(f"{field}: {value}")


# ============================================================
# 3. WORD-LEVEL OCR CONFIDENCE
# ============================================================

print("\n===== WORD CONFIDENCE =====\n")

for item in words:
    print(
        f"{item['text']} -> "
        f"{item['confidence']:.2f}"
    )


# ============================================================
# 4. FIELD-LEVEL CONFIDENCE
# ============================================================

field_confidence = {}

print("\n===== FIELD CONFIDENCE =====\n")

for field, value in fields.items():

    score = calculate_field_confidence(
        field,
        value,
        words
    )

    field_confidence[field] = score

    print(
        f"{field}: {value} -> {score}"
    )


# ============================================================
# 5. FIELD EVIDENCE
# ============================================================

field_evidence = {}

print("\n===== FIELD EVIDENCE =====\n")

for field, value in fields.items():

    evidence = find_evidence(
        text,
        value
    )

    field_evidence[field] = evidence

    print(f"{field}:")
    print(f"  Value: {value}")
    print(f"  Evidence: {evidence}")
    print()


# ============================================================
# 6. EXISTING RECORDS
# Temporary dummy data
# ============================================================

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


# ============================================================
# 7. VALIDATION + DUPLICATE CHECK
# ============================================================

validation = validate_record(
    fields,
    field_confidence,
    existing_records
)

print("\n===== VALIDATION =====\n")

print("Status:", validation["status"])

print("\nFlags:")

if validation["flags"]:
    for flag in validation["flags"]:
        print("-", flag)
else:
    print("No issues found ✅")


# ============================================================
# 8. FINAL SUMMARY
# ============================================================

print("\n===== FINAL SUMMARY =====\n")

print("Document:", filename)
print("Status:", validation["status"])

print("\nFields:")
for field, value in fields.items():
    print(f"- {field}: {value}")

print("\nConfidence:")
for field, score in field_confidence.items():
    print(f"- {field}: {score}")

print("\nFlags:")
for flag in validation["flags"]:
    print(f"- {flag}")