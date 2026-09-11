from pdf_processor import pdf_to_images


pdf_path = "documents/sample.pdf"

images = pdf_to_images(pdf_path)

print("\n===== PDF PAGES =====\n")

for image in images:
    print(image)