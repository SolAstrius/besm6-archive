# SPDX-License-Identifier: Apache-2.0
"""Facsimile PDF of a СИПРОД printout (dispak line-printer listing): every framed ЕСПД sheet (from one
".----.' border line to the next) becomes one A4 page, set in a monospace Cyrillic font exactly as printed.
The monitor banner before the first sheet and the job trailer after the last are left out.
   uv run --with fpdf2 python tools/facsimile.py LISTING.lst OUT.pdf [TITLE]"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from printout import sheets

FONTS = [os.environ.get("FACSIMILE_FONT", ""),
         "/System/Library/Fonts/Supplemental/Courier New.ttf",
         "/usr/share/fonts/truetype/msttcorefonts/cour.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
FONT = next((f for f in FONTS if f and os.path.exists(f)), None)

def build(lst, pdf_path, title=""):
    from fpdf import FPDF
    pages = sheets(open(lst, encoding="utf-8").read())
    width = max(len(l) for p in pages for l in p)
    height = max(len(p) for p in pages)
    pdf = FPDF(orientation="P", unit="pt", format="A4")
    pdf.set_auto_page_break(False)
    pdf.add_font("mono", "", FONT)
    pdf.set_title(title)
    pw, ph = 595.28, 841.89
    margin = 36
    size = min((pw - 2 * margin) / (width * 0.6), (ph - 2 * margin) / (height * 1.18))
    lead = size * 1.18
    x0 = (pw - width * 0.6 * size) / 2
    y0 = (ph - height * lead) / 2
    for p in pages:
        pdf.add_page()
        pdf.set_font("mono", size=size)
        for i, line in enumerate(p):
            if line:
                pdf.text(x0, y0 + (i + 1) * lead - lead * 0.25, line)
    pdf.output(pdf_path)
    return len(pages), width, height, size

if __name__ == "__main__":
    n, w, h, s = build(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    print(f"{sys.argv[2]}: {n} pages, sheet {w}x{h} chars, {s:.2f} pt")
