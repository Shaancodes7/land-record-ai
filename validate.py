import re
from difflib import SequenceMatcher


MANDATORY_FIELDS = [
    "ownerName",
    "khasraNumber",
    "village"
]


def validate_record(fields, confidence_scores, existing_records=None):
    flags = []

    # 1. Mandatory fields
    for field in MANDATORY_FIELDS:
        if not fields.get(field):
            flags.append(f"Missing mandatory field: {field}")

    # 2. Khasra format
    khasra = fields.get("khasraNumber")

    if khasra:
        if not re.match(r"^\d+(?:/\d+)?$", str(khasra)):
            flags.append(f"Invalid Khasra format: {khasra}")

    # 3. Low confidence
    for field, score in confidence_scores.items():
        if score < 0.80:
            flags.append(
                f"Low confidence: {field} ({score})"
            )

    # 4. Duplicate / similarity check
    if existing_records:
        for record in existing_records:

            if (
                record.get("khasraNumber")
                == fields.get("khasraNumber")
            ):

                existing_owner = record.get("ownerName", "")
                new_owner = fields.get("ownerName", "")

                similarity = SequenceMatcher(
                    None,
                    existing_owner.lower(),
                    new_owner.lower()
                ).ratio()

                if similarity < 0.95:
                    flags.append(
                        f"Possible owner conflict: "
                        f"similarity {round(similarity, 2)}"
                    )

                else:
                    flags.append(
                        f"Possible duplicate record: "
                        f"similarity {round(similarity, 2)}"
                    )

    # 5. Final status
    if flags:
        status = "Needs Review"
    else:
        status = "Approved"

    return {
        "status": status,
        "flags": flags
    }