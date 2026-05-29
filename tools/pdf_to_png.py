import sys
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "deliverables.pdf"
OUT_DIR = ROOT

if not PDF.exists():
    print(f"deliverables.pdf not found at: {PDF}")
    sys.exit(2)

doc = fitz.open(str(PDF))
print(f"Opened PDF with {doc.page_count} pages.")

for i, page in enumerate(doc, start=1):
    pix = page.get_pixmap(dpi=200)
    out_path = OUT_DIR / f"deliverables_page_{i}.png"
    pix.save(str(out_path))
    print(f"Saved: {out_path}")

print("Conversion complete.")
