# OCR Setup for Scanned PDFs

The RAG system now supports OCR (Optical Character Recognition) to process scanned PDFs that don't have extractable text.

## How It Works

1. **Automatic Detection**: The system first tries regular text extraction
2. **OCR Fallback**: If little or no text is found (< 100 characters), it automatically attempts OCR
3. **Seamless Processing**: OCR-processed documents are handled the same way as regular PDFs

## Installation

### Step 1: Install Python Packages

```bash
pip install pytesseract pdf2image Pillow
```

### Step 2: Install Tesseract OCR Engine

The Python packages require the Tesseract OCR engine to be installed on your system.

#### Windows:
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (default location: `C:\Program Files\Tesseract-OCR`)
3. Add to PATH or configure in code (see below)

#### macOS:
```bash
brew install tesseract
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get install tesseract-ocr
```

### Step 3: Verify Installation

```bash
tesseract --version
```

## Configuration (Optional)

If Tesseract is not in your PATH, you can configure it in `core/rag_service.py`:

```python
import pytesseract

# Windows example
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# macOS/Linux - usually not needed if installed via package manager
```

## Usage

OCR is **automatic** - no special commands needed! Just run:

```bash
python manage.py ingest_documents
```

The system will:
- Process regular PDFs normally (fast)
- Automatically detect scanned PDFs
- Use OCR for scanned PDFs (slower but works!)
- Track which documents used OCR in the database

## Performance

- **Regular PDFs**: ~1-5 seconds per document
- **Scanned PDFs (OCR)**: ~10-30 seconds per page (depending on quality and size)

For a 10-page scanned PDF, expect ~2-5 minutes of processing time.

## Monitoring

Check which documents used OCR in Django admin:
- Visit `/admin/core/document/`
- Filter by "Used OCR" to see scanned PDFs
- The `used_ocr` field shows `True` for OCR-processed documents

## Troubleshooting

### "TesseractNotFoundError"
- Tesseract is not installed or not in PATH
- Install Tesseract (see Step 2 above)
- Or configure the path manually (see Step 3)

### OCR is slow
- This is normal - OCR is computationally intensive
- Consider processing scanned PDFs separately: `python manage.py ingest_documents --path RAG_DATA/MostlyUnsearchable`

### Poor OCR quality
- Increase DPI in `_extract_text_with_ocr()` method (change `dpi=200` to `dpi=300`)
- Note: Higher DPI = better quality but slower processing

### Memory issues with large PDFs
- The system processes one page at a time to minimize memory usage
- If issues persist, process documents in smaller batches using `--limit`

## Notes

- OCR is **optional** - the system works fine without it, but scanned PDFs will be skipped
- OCR quality depends on:
  - Image resolution (DPI)
  - Document quality (scanning quality, contrast)
  - Text clarity (handwriting vs printed text)
- The system uses English language OCR by default (`lang='eng'`)
- For other languages, modify the `pytesseract.image_to_string()` call in `_extract_text_with_ocr()`

## Example: Processing Only Scanned PDFs

```bash
# Process only the "MostlyUnsearchable" folder
python manage.py ingest_documents --path RAG_DATA/ASM\ Failure\ Analisys\ Cases/MostlyUnsearchable\ -\ Scanned20251112185202
```

This will process all 43 scanned PDFs in that folder using OCR.

