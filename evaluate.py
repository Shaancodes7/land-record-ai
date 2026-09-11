import json
import os

from preprocess import preprocess_image
from ocr_service import run_ocr_with_confidence
from extract import extract_fields


GROUND_TRUTH_FILE = "ground_truth.json"
DOCUMENT_DIR = "documents"


def normalize(value):
    if value is None:
        return None

    return " ".join(str(value).lower().split())


def process_document(image_path):
    """
    Same basic flow as our prototype:
    preprocess -> OCR -> fallback to original -> extraction
    """

    processed_path = "temp_evaluation_processed.png"

    os.makedirs("temp", exist_ok=True)

    processed_path = os.path.join(
        "temp",
        "evaluation_processed.png"
    )

    preprocess_image(
        image_path,
        processed_path
    )

    # Try processed image
    text, words = run_ocr_with_confidence(
        processed_path
    )

    # Fallback to original image
    if not text.strip():

        text, words = run_ocr_with_confidence(
            image_path
        )

    fields = extract_fields(text)

    return fields


def evaluate():
    with open(
        GROUND_TRUTH_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        ground_truth = json.load(file)

    total_fields = 0
    correct_fields = 0

    print("\n========== EVALUATION ==========\n")

    for filename, expected_fields in ground_truth.items():

        image_path = os.path.join(
            DOCUMENT_DIR,
            filename
        )

        print(f"Testing: {filename}")

        predicted_fields = process_document(
            image_path
        )

        document_correct = 0
        document_total = 0

        for field, expected in expected_fields.items():

            predicted = predicted_fields.get(field)

            document_total += 1
            total_fields += 1

            if normalize(predicted) == normalize(expected):
                correct_fields += 1
                document_correct += 1
                result = "PASS"
            else:
                result = "FAIL"

            print(
                f"{field}: "
                f"expected={expected!r}, "
                f"predicted={predicted!r} "
                f"[{result}]"
            )

        document_accuracy = (
            document_correct / document_total
            if document_total
            else 0
        )

        print(
            f"Document accuracy: "
            f"{document_accuracy:.2%}"
        )

        print("-" * 50)

    overall_accuracy = (
        correct_fields / total_fields
        if total_fields
        else 0
    )

    print("\n========== FINAL ==========\n")

    print(f"Correct fields: {correct_fields}")
    print(f"Total fields:   {total_fields}")
    print(f"Field accuracy: {overall_accuracy:.2%}")


if __name__ == "__main__":
    evaluate()