"""Scan receipt images and append the results to output/expenses.csv.

    python scan.py samples/receipt_01.jpg
    python scan.py samples/            # whole folder
    python scan.py samples/ --debug    # also dumps the preprocessed image
"""

import csv
import sys
from pathlib import Path

from scanner.preprocess import preprocess
from scanner.ocr import extract_text
from scanner.parser import parse_receipt
from scanner.categorize import categorize

CSV_PATH = Path("output/expenses.csv")
FIELDS = ["file", "merchant", "date", "total", "category"]


def scan_one(path, debug=False):
    binary = preprocess(path, debug=debug)
    text = extract_text(binary)
    data = parse_receipt(text)
    data["category"] = categorize(data["merchant"])
    data["file"] = Path(path).name
    return data


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    debug = "--debug" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(1)

    target = Path(args[0])
    images = sorted(target.glob("*.[jp][pn]g")) if target.is_dir() else [target]
    if not images:
        print(f"No images found in {target}")
        sys.exit(1)

    CSV_PATH.parent.mkdir(exist_ok=True)
    new_file = not CSV_PATH.exists()

    results = []
    for img in images:
        print(f"Scanning {img.name}...", end=" ")
        try:
            data = scan_one(img, debug=debug)
            results.append(data)
            total = f"{data['total']:.2f}" if data["total"] else "?"
            print(f"{data['merchant']} | {data['date']} | {total} EUR | {data['category']}")
        except Exception as e:
            print(f"failed ({e})")

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerows(results)
    print(f"\n{len(results)} receipt(s) added to {CSV_PATH}")


if __name__ == "__main__":
    main()
