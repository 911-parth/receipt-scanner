import pytesseract


def extract_text(binary_image, lang="fra+eng"):
    """Receipts here are mostly French so we load both language packs."""
    config = "--psm 4"  # assume a single column of text, works well on receipts
    try:
        return pytesseract.image_to_string(binary_image, lang=lang, config=config)
    except pytesseract.TesseractError:
        # french traineddata not installed, fall back to english
        return pytesseract.image_to_string(binary_image, lang="eng", config=config)
