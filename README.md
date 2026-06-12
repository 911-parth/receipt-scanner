# receipt-scanner

I kept losing track of what I spend as a student in Paris, and typing receipts
into a spreadsheet by hand lasted exactly four days. This scans a photo of a
receipt, reads it with OCR, pulls out the merchant / date / total, sorts it
into a category and logs everything to a CSV.

It started as a follow-up to an earlier OCR project of mine (image text
extraction with OpenCV) — this one goes further: the goal isn't just reading
text but getting *structured* data out of crumpled, badly-lit receipt photos.

## How it works

1. **Preprocess** (OpenCV): grayscale, denoise, adaptive threshold, deskew.
   This step does most of the heavy lifting — raw phone photos give Tesseract
   garbage, cleaned ones work fine.
2. **OCR** (Tesseract via pytesseract): `--psm 4`, single-column mode, which
   matches receipt layout.
3. **Parse** (regex + heuristics): merchant is usually the first ALL-CAPS line,
   total is the amount on a line containing TOTAL/MONTANT/TTC (skipping
   traps like "sous-total" and "rendu"), dates handle the dd/mm/yyyy variants.
   French receipts use commas in amounts, so that's handled too.
4. **Categorize**: keyword matching on the merchant name. I considered a
   classifier and decided that was a silly amount of machinery for the
   ~15 shops I actually visit.

## Usage

You need Tesseract installed (`apt install tesseract-ocr` or
`brew install tesseract`). Then:

```
pip install -r requirements.txt
python scan.py samples/          # try it on the included sample receipts
python report.py                 # spending summary + pie chart
```

Scan your own: `python scan.py path/to/photo.jpg`. Add `--debug` to dump the
preprocessed image and see what the OCR actually receives.

## Sample run

```
Scanning receipt_01.png... Carrefour City | 2026-05-15 | 16.41 EUR | groceries
Scanning receipt_02.png... Monoprix | 2026-05-22 | 7.20 EUR | groceries
Scanning receipt_03.png... Pharmacie De La Mairie | 2026-06-02 | 10.68 EUR | pharmacy
```

## Limitations (honest version)

- Very crumpled or shiny thermal paper still trips the OCR
- Handwritten receipts: no
- The "largest amount = total" fallback can grab a wrong number on receipts
  with no TOTAL line
- Install the `fra` Tesseract language pack for better accuracy on French
  receipts; it falls back to English automatically if missing

## Ideas for later

- Line-item extraction (product-level spending, not just per-receipt)
- A small web UI to drop photos onto
- Export to the banking app categories format
