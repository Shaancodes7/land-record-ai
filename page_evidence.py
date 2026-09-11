def find_field_page(field_value, page_results):
    """
    Extracted value kis page par mila,
    uska page number return karta hai.
    """

    if not field_value:
        return None

    value = str(field_value).lower().strip()

    for page in page_results:

        page_text = page["text"].lower()

        if value in page_text:
            return page["page"]

    return None