"""Pull structured fields out of raw OCR text.

OCR output is messy (O vs 0, missing spaces, random noise lines) so
everything here is regex + heuristics, tuned on real receipts.
"""

import re
from datetime import datetime

# 12,50 / 12.50 / 12 , 50  -- French receipts use commas
AMOUNT = re.compile(r"(\d{1,4})\s*[.,]\s*(\d{2})")

TOTAL_KEYWORDS = ["total", "montant", "a payer", "à payer", "ttc", "somme"]
# lines we should never read a total from
SKIP_KEYWORDS = ["sous-total", "subtotal", "tva", "rendu", "espece", "espèce",
                 "carte", "cb ", "change", "cash"]

DATE_PATTERNS = [
    (re.compile(r"(\d{2})[/.-](\d{2})[/.-](\d{4})"), "%d/%m/%Y"),
    (re.compile(r"(\d{2})[/.-](\d{2})[/.-](\d{2})\b"), "%d/%m/%y"),
    (re.compile(r"(\d{4})[/.-](\d{2})[/.-](\d{2})"), "%Y/%m/%d"),
]


def parse_receipt(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return {
        "merchant": find_merchant(lines),
        "date": find_date(lines),
        "total": find_total(lines),
    }


def find_merchant(lines):
    """The merchant name is almost always in the first few lines, in caps."""
    for line in lines[:5]:
        cleaned = re.sub(r"[^A-Za-zÀ-ÿ' ]", "", line).strip()
        if len(cleaned) >= 3 and cleaned.upper() == cleaned:
            return cleaned.title()
    # fallback: first line with letters
    for line in lines[:5]:
        if re.search(r"[A-Za-z]{3}", line):
            return line[:40]
    return "Unknown"


def find_date(lines):
    for line in lines:
        for pattern, fmt in DATE_PATTERNS:
            m = pattern.search(line)
            if not m:
                continue
            try:
                raw = "/".join(m.groups())
                return datetime.strptime(raw, fmt).date().isoformat()
            except ValueError:
                continue  # things like 99/99/2025 from OCR noise
    return None


def find_total(lines):
    # pass 1: a line that says TOTAL with an amount on it
    candidates = []
    for line in lines:
        low = line.lower()
        if any(k in low for k in SKIP_KEYWORDS):
            continue
        if any(k in low for k in TOTAL_KEYWORDS):
            m = AMOUNT.search(line)
            if m:
                candidates.append(_to_float(m))
    if candidates:
        return max(candidates)  # "TOTAL TTC" beats partial totals

    # pass 2: no TOTAL line found, take the largest amount on the receipt.
    # not bulletproof but right more often than not
    amounts = []
    for line in lines:
        low = line.lower()
        if any(k in low for k in SKIP_KEYWORDS):
            continue
        amounts += [_to_float(m) for m in AMOUNT.finditer(line)]
    return max(amounts) if amounts else None


def _to_float(match):
    return float(f"{match.group(1)}.{match.group(2)}")
