from pdf_pipeline import process_pdf


result = process_pdf(
    "documents/sample.pdf"
)

print("\n===== PDF RESULT =====\n")

print("Status:")
print(result["status"])

print("\nData:")
print(result["data"])

print("\nConfidence:")
print(result["confidence"])

print("\nEvidence:")
print(result["evidence"])

print("\nFlags:")
for flag in result["flags"]:
    print("-", flag)

print("\nPages:")
for page in result["pages"]:
    print(f"\n--- PAGE {page['page']} ---")
    print(page["text"])