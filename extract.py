import re


def extract_fields(text):
    # OCR/test text mein newlines ko spaces mein convert karo
    # taaki extraction layout par depend na kare.
    text = " ".join(text.split())

    fields = {
        "ownerName": None,
        "fatherName": None,
        "khasraNumber": None,
        "khataNumber": None,
        "surveyNumber": None,
        "area": None,
        "village": None,
        "tehsil": None,
        "district": None,
    }

    patterns = {
        "ownerName": (
            r"Owner\s*Name\s*:\s*"
            r"(.*?)(?=\s+Father\s*Name\s*:|\s+Khasra\s*No\.?\s*:|$)"
        ),

        "fatherName": (
            r"Father\s*Name\s*:\s*"
            r"(.*?)(?=\s+Khasra\s*No\.?\s*:|\s+Khata\s*No\.?\s*:|$)"
        ),

        "khasraNumber": (
            r"Khasra\s*No\.?\s*:\s*"
            r"([0-9]+(?:/[0-9]+)?)"
        ),

        "khataNumber": (
            r"Khata\s*No\.?\s*:\s*"
            r"([0-9]+)"
        ),

        "surveyNumber": (
            r"Survey\s*No\.?\s*:\s*"
            r"([A-Za-z0-9-]+)"
        ),

        "area": (
            r"Area\s*:\s*"
            r"(.*?)(?=\s+Village\s*:|$)"
        ),

        "village": (
            r"Village\s*:\s*"
            r"(.*?)(?=\s+Tehsil\s*:|\s+District\s*:|$)"
        ),

        "tehsil": (
            r"Tehsil\s*:\s*"
            r"(.*?)(?=\s+District\s*:|$)"
        ),

        "district": (
            r"District\s*:\s*(.*?)(?=$)"
        ),
    }

    for field, pattern in patterns.items():
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            value = match.group(1).strip()

            if value:
                fields[field] = value

    return fields