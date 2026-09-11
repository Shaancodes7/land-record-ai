# Land Record AI API Contract

## Endpoint

POST /extract

### Content-Type

multipart/form-data

### Request

Field:

file

Supported file types:

- PNG
- JPG
- JPEG
- PDF

Example:

POST /extract
file = land_record.pdf


# Success Response

{
  "status": "Approved",
  "reviewRequired": false,

  "data": {
    "ownerName": "Rajesh Kumar",
    "fatherName": "Mahesh Kumar",
    "khasraNumber": "124/2",
    "khataNumber": "782",
    "surveyNumber": "SR-2041",
    "area": "2.5 Acres",
    "village": "Nangli",
    "tehsil": "Najafgarh",
    "district": "Delhi"
  },

  "confidence": {
    "ownerName": 0.95,
    "fatherName": 0.96,
    "khasraNumber": 0.99,
    "khataNumber": 0.95,
    "surveyNumber": 0.92,
    "area": 0.97,
    "village": 0.92,
    "tehsil": 0.90,
    "district": 0.95
  },

  "evidence": {
    "ownerName": {
      "text": "Owner Name: Rajesh Kumar",
      "page": 1
    },

    "khasraNumber": {
      "text": "Khasra No: 124/2",
      "page": 1
    }
  },

  "issues": [],

  "flags": [],

  "pages": [
    {
      "page": 1,
      "text": "OCR text...",
      "word_count": 28
    }
  ]
}


# Needs Review Response

{
  "status": "Needs Review",
  "reviewRequired": true,

  "data": {
    "ownerName": "Rajesh Kumar",
    "khasraNumber": "124/232"
  },

  "confidence": {
    "ownerName": 0.95,
    "khasraNumber": 0.05
  },

  "evidence": {
    "khasraNumber": {
      "text": "Khasra No: 124/232",
      "page": 1
    }
  },

  "issues": [
    {
      "field": "khasraNumber",
      "extractedValue": "124/232",
      "confidence": 0.05,
      "page": 1,
      "reason": "Low OCR confidence"
    }
  ],

  "flags": [
    "Low confidence: khasraNumber (0.05)"
  ],

  "pages": [
    {
      "page": 1,
      "text": "OCR text...",
      "word_count": 28
    }
  ]
}


# Missing Fields

If a field is not present in the document:

value = null

Example:

"tehsil": null

The AI must NOT invent missing information.


# Backend Responsibility

Backend should:

1. Receive document from frontend.
2. Send document to AI /extract endpoint.
3. Store AI response.
4. Create a review case if reviewRequired = true.
5. Return AI result to frontend.


# Frontend Responsibility

Frontend should display:

1. Extracted values.
2. Confidence.
3. Evidence.
4. Page number.
5. Review warnings.
6. Conflict/validation flags.


# Human Review

If:

reviewRequired = true

Frontend should show a review screen.

Reviewer can:

- approve
- correct
- reject

Corrections should be stored by backend.


# Important

The AI service does NOT make the final legal/ownership decision.

AI only extracts, validates and flags uncertain/conflicting information.

Human reviewer makes the final decision.