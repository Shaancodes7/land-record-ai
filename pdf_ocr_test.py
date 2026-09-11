from pdf_processor import pdf_to_images
from ocr_service import run_ocr_with_confidence


PDF_PATH = "documents/sample.pdf"


# PDF ko page images mein convert karo
pages = pdf_to_images(PDF_PATH)

print("\n===== PDF OCR =====\n")


# Har page ka OCR
for page_number, image_path in enumerate(pages, start=1):

    text, words = run_ocr_with_confidence(
        image_path
    )

    print(f"\n--- PAGE {page_number} ---\n")
    print(text)

    print(
        f"\nWords detected: {len(words)}"
    )