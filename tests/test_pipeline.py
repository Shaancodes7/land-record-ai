from extract import extract_fields
from field_confidence import calculate_field_confidence
from validate import validate_record


def test_extract_fields():
    text = """
    LAND RECORD

    Owner Name: Rajesh Kumar
    Father Name: Mahesh Kumar
    Khasra No: 124/2
    Khata No: 782
    Survey No: SR-2041
    Area: 2.5 Acres
    Village: Nangli
    Tehsil: Najafgarh
    District: Delhi
    """

    fields = extract_fields(text)

    assert fields["ownerName"] == "Rajesh Kumar"
    assert fields["fatherName"] == "Mahesh Kumar"
    assert fields["khasraNumber"] == "124/2"
    assert fields["khataNumber"] == "782"
    assert fields["surveyNumber"] == "SR-2041"
    assert fields["area"] == "2.5 Acres"
    assert fields["village"] == "Nangli"
    assert fields["tehsil"] == "Najafgarh"
    assert fields["district"] == "Delhi"


def test_missing_field_is_none():
    text = """
    Owner Name: Rajesh Kumar
    Khasra No: 124/2
    Village: Nangli
    """

    fields = extract_fields(text)

    assert fields["ownerName"] == "Rajesh Kumar"
    assert fields["khasraNumber"] == "124/2"
    assert fields["khataNumber"] is None

def test_missing_owner_triggers_review():
    fields = {
        "ownerName": None,
        "khasraNumber": "124/2",
        "village": "Nangli"
    }

    confidence = {
        "ownerName": 0.0,
        "khasraNumber": 0.95,
        "village": 0.95
    }

    result = validate_record(
        fields,
        confidence,
        []
    )

    assert result["status"] == "Needs Review"

    assert any(
        "Missing mandatory field" in flag
        for flag in result["flags"]
    )


def test_invalid_khasra_triggers_review():
    fields = {
        "ownerName": "Rajesh Kumar",
        "khasraNumber": "ABC",
        "village": "Nangli"
    }

    confidence = {
        "ownerName": 0.95,
        "khasraNumber": 0.95,
        "village": 0.95
    }

    result = validate_record(
        fields,
        confidence,
        []
    )

    assert result["status"] == "Needs Review"

    assert any(
        "Invalid Khasra format" in flag
        for flag in result["flags"]
    )


def test_low_confidence_triggers_review():
    fields = {
        "ownerName": "Rajesh Kumar",
        "khasraNumber": "124/2",
        "village": "Nangli"
    }

    confidence = {
        "ownerName": 0.95,
        "khasraNumber": 0.95,
        "village": 0.60
    }

    result = validate_record(
        fields,
        confidence,
        []
    )

    assert result["status"] == "Needs Review"

    assert any(
        "Low confidence" in flag
        for flag in result["flags"]
    )


def test_duplicate_conflict():
    fields = {
        "ownerName": "Rajesh Kumar",
        "khasraNumber": "124/2",
        "village": "Nangli"
    }

    confidence = {
        "ownerName": 0.95,
        "khasraNumber": 0.95,
        "village": 0.95
    }

    existing_records = [
        {
            "ownerName": "Mahesh Kumar",
            "khasraNumber": "124/2"
        }
    ]

    result = validate_record(
        fields,
        confidence,
        existing_records
    )

    assert result["status"] == "Needs Review"

    assert any(
        "conflict" in flag.lower()
        for flag in result["flags"]
    )