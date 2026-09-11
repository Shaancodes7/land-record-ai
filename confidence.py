import re


def calculate_field_confidence(field_name, value, ocr_confidences):
    """
    OCR word-level confidence se ek basic field confidence banata hai.
    """

    # Value missing hai
    if value is None:
        return 0.0

    # OCR ne koi confidence nahi diya
    if not ocr_confidences:
        return 0.0

    # Basic average OCR confidence
    score = sum(ocr_confidences) / len(ocr_confidences)

    # 0-100 -> 0-1
    score = score / 100

    # Simple field-specific validation adjustment
    if field_name == "khasraNumber":
        if re.match(r"^\d+/\d+$", str(value)):
            score += 0.05
        else:
            score -= 0.20

    if field_name == "area":
        if re.match(r"^[\d.]+\s*acres?$", str(value), re.IGNORECASE):
            score += 0.03
        else:
            score -= 0.15

    # Keep between 0 and 1
    score = max(0.0, min(score, 1.0))

    return round(score, 2)