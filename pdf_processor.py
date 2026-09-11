import fitz
import os


def pdf_to_images(pdf_path, output_dir="temp/pdf_pages"):
    """
    PDF ke har page ko PNG image mein convert karta hai.
    """

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    os.makedirs(output_dir, exist_ok=True)

    document = fitz.open(pdf_path)

    image_paths = []

    for page_number in range(len(document)):

        page = document.load_page(page_number)

        # PDF page ko image mein render karo
        pixmap = page.get_pixmap(
            matrix=fitz.Matrix(2, 2)
        )

        output_path = os.path.join(
            output_dir,
            f"page_{page_number + 1}.png"
        )

        pixmap.save(output_path)

        image_paths.append(output_path)

    document.close()

    return image_paths