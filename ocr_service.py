import re

import cv2
import numpy as np
import pytesseract
from PIL import Image


# ============================================================
# TESSERACT PATH
# ============================================================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# ============================================================
# BASIC OCR
# ============================================================

def run_ocr(image_path, lang="eng"):
    """
    Image ko OCR karke plain text return karta hai.
    """

    image = Image.open(image_path)

    text = pytesseract.image_to_string(
        image,
        lang=lang
    )

    return text


# ============================================================
# OCR + WORD LEVEL CONFIDENCE
# ============================================================

def run_ocr_with_confidence(image_path, lang="eng"):
    """
    OCR text aur har detected word ka confidence return karta hai.

    Returns:
        text  -> complete OCR text
        words -> list of dictionaries:
                 {
                     "text": "...",
                     "confidence": 95.4
                 }
    """

    image = Image.open(image_path)

    data = pytesseract.image_to_data(
        image,
        lang=lang,
        output_type=pytesseract.Output.DICT
    )

    words = []

    for i, word in enumerate(data["text"]):

        word = word.strip()

        if not word:
            continue

        try:
            confidence = float(data["conf"][i])
        except (ValueError, TypeError):
            continue

        words.append({
            "text": word,
            "confidence": confidence
        })

    text = " ".join(
        item["text"]
        for item in words
    )

    return text, words


# ============================================================
# KHASRA-SPECIFIC OCR RETRY
# ============================================================

def retry_khasra_ocr(image_path):
    """
    Khasra number ko focused crop + numeric OCR se
    dobara read karne ki koshish karta hai.

    Example:
        Khasra No: 124/2

    Expected:
        124/2
    """

    image = Image.open(
        image_path
    ).convert("RGB")

    # --------------------------------------------------------
    # Convert PIL image to OpenCV format
    # --------------------------------------------------------

    img = np.array(image)

    img = cv2.cvtColor(
        img,
        cv2.COLOR_RGB2BGR
    )

    # --------------------------------------------------------
    # Detect words and their positions
    # --------------------------------------------------------

    data = pytesseract.image_to_data(
        image,
        lang="eng",
        config="--psm 6",
        output_type=pytesseract.Output.DICT
    )

    khasra_idx = None
    khata_idx = None

    # Find Khasra and Khata positions
    for i, word in enumerate(data["text"]):

        clean = word.strip().lower()

        if "khasra" in clean and khasra_idx is None:
            khasra_idx = i

        if (
            "khata" in clean
            and khasra_idx is not None
        ):
            khata_idx = i
            break

    # Khasra word not found
    if khasra_idx is None:
        return None

    # --------------------------------------------------------
    # Khasra bounding box
    # --------------------------------------------------------

    khasra_x = int(data["left"][khasra_idx])
    khasra_y = int(data["top"][khasra_idx])

    khasra_width = int(
        data["width"][khasra_idx]
    )

    khasra_height = int(
        data["height"][khasra_idx]
    )

    # --------------------------------------------------------
    # Value region starts after "Khasra"
    # --------------------------------------------------------

    value_start_x = (
        khasra_x
        + khasra_width
    )

    # If Khata was detected, stop before it
    if khata_idx is not None:

        value_end_x = int(
            data["left"][khata_idx]
        )

    else:

        value_end_x = img.shape[1]

    # --------------------------------------------------------
    # Vertical crop
    # --------------------------------------------------------

    y1 = max(
        0,
        khasra_y - int(khasra_height * 0.5)
    )

    y2 = min(
        img.shape[0],
        khasra_y + int(khasra_height * 1.5)
    )

    x1 = max(
        0,
        value_start_x
    )

    x2 = min(
        img.shape[1],
        value_end_x
    )

    # --------------------------------------------------------
    # Crop only the Khasra value area
    # --------------------------------------------------------

    crop = img[
        y1:y2,
        x1:x2
    ]

    if crop.size == 0:
        return None

    # --------------------------------------------------------
    # Upscale
    # --------------------------------------------------------

    crop = cv2.resize(
        crop,
        None,
        fx=5,
        fy=5,
        interpolation=cv2.INTER_CUBIC
    )

    # --------------------------------------------------------
    # Grayscale
    # --------------------------------------------------------

    gray = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2GRAY
    )

    # --------------------------------------------------------
    # Threshold
    # --------------------------------------------------------

    _, binary = cv2.threshold(
        gray,
        180,
        255,
        cv2.THRESH_BINARY
    )

    # --------------------------------------------------------
    # Numeric-only OCR
    # --------------------------------------------------------

    result = pytesseract.image_to_string(
        binary,
        config=(
            "--psm 7 "
            "-c tessedit_char_whitelist=0123456789/"
        )
    )

    # --------------------------------------------------------
    # Find Khasra-like pattern
    # --------------------------------------------------------

    candidates = re.findall(
        r"\d+/\d+",
        result
    )

    if candidates:
        return candidates[0]

    return None