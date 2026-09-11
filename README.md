# 🏛️ Land Record AI Service

An AI-powered document processing microservice for extracting, validating, and reviewing structured information from land-record documents.

The service accepts PNG, JPG/JPEG, and PDF documents and returns extracted fields, confidence scores, evidence, validation flags, and human-review requirements.

---

## 🚀 Features

- 📄 PNG, JPG/JPEG and PDF document support
- 🔍 OCR using Tesseract
- 🧹 Image preprocessing with OpenCV
- 🧾 Structured land-record field extraction
- 📊 Field-level OCR confidence
- 🔎 Evidence/source tracking
- 📑 Page-level evidence for PDFs
- ✅ Field validation
- ⚠️ Low-confidence detection
- 🔄 Duplicate/conflict detection
- 👨‍⚖️ Human-review workflow
- 🌐 FastAPI REST API
- 🧪 Automated tests with Pytest
- 🛡️ Graceful error handling

---

## 🧠 Architecture

```text
                 Document
                     │
             ┌───────┴────────┐
             │                │
          PNG/JPG             PDF
             │                │
             │          PDF → Pages
             │                │
             └───────┬────────┘
                     │
               Preprocessing
                     │
                    OCR
                     │
             Field Extraction
                     │
          ┌──────────┼──────────┐
          │          │          │
      Confidence   Evidence  Validation
          │          │          │
          └──────────┼──────────┘
                     │
            Duplicate Detection
                     │
                     ▼
              Structured JSON
                     │
              Human Review
