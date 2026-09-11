import re


def normalize(text):
    """Text ko comparison ke liye normalize karta hai."""
    text = text.lower().strip()
    text = re.sub(r"[^\w/.-]", "", text)
    return text


def calculate_field_confidence(field_name, value, words):
    """
    Field ke actual OCR words ki confidence se
    field-level confidence calculate karta hai.
    """

    if not value:
        return 0.0

    # Field value ko words mein todna
    value_words = str(value).split()

    matched_confidences = []

    for value_word in value_words:
        target = normalize(value_word)

        best_match = None

        for item in words:
            ocr_word = normalize(item["text"])

            if ocr_word == target:
                best_match = item["confidence"]
                break

        if best_match is not None:
            matched_confidences.append(best_match)

    # Agar field ke koi words OCR output mein match nahi hue
    if not matched_confidences:
        return 0.0

    # Average confidence of matched words
    score = sum(matched_confidences) / len(matched_confidences)

    # 0-100 → 0-1
    score = score / 100

    # Khasra format validation
    if field_name == "khasraNumber":
        if re.match(r"^\d+(?:/\d+)?$", str(value)):
            score = min(score + 0.05, 1.0)

    # Area format validation
    if field_name == "area":
        if re.match(
            r"^[\d.]+\s*(acres?|hectares?|sq\.?\s*ft\.?)$",
            str(value),
            re.IGNORECASE
        ):
            score = min(score + 0.03, 1.0)

    return round(score, 2)