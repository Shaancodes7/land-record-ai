import re


def find_evidence(text, value, context_words=5):
    """
    OCR text mein extracted value ko locate karta hai
    aur uske aas-paas ka source text return karta hai.
    """

    if not value:
        return None

    text = " ".join(text.split())
    value = " ".join(str(value).split())

    pattern = re.escape(value)

    match = re.search(pattern, text, re.IGNORECASE)

    if not match:
        return None

    words = text.split()

    matched_start = len(text[:match.start()].split())

    start = max(0, matched_start - context_words)
    end = min(len(words), matched_start + len(value.split()) + context_words)

    return " ".join(words[start:end])