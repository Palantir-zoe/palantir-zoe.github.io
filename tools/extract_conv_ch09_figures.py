"""Render the figures used by the 09_conv reading note from the local lecture PDF.

Usage: python tools/extract_conv_ch09_figures.py [path/to/09_conv.pdf]
The PDF is a local source only; the site contains cropped teaching figures.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs/posts/conv-ch09/figures"
DEFAULT_PDF = ROOT.parent / "DeepLearning/09_conv.pdf"

# Coordinates refer to a 1100 px wide rendering of the 4:3 PDF pages.
# Each rectangle keeps the original drawing and removes the slide heading/footer.
FIGURES = {
    1: (6, (205, 175, 805, 750)),
    2: (8, (50, 205, 1005, 780)),
    3: (9, (50, 205, 1005, 780)),
    4: (10, (125, 190, 970, 675)),
    5: (11, (30, 190, 1035, 760)),
    6: (12, (100, 205, 1005, 735)),
    7: (14, (290, 230, 830, 730)),
    8: (15, (250, 185, 830, 715)),
    9: (16, (170, 255, 935, 715)),
    10: (17, (105, 265, 1000, 555)),
    11: (18, (290, 230, 810, 810)),
    12: (19, (300, 205, 825, 800)),
    13: (20, (30, 190, 885, 790)),
    14: (21, (285, 215, 1035, 745)),
    15: (22, (290, 140, 715, 755)),
    16: (23, (255, 190, 820, 750)),
    17: (24, (185, 190, 770, 710)),
    18: (25, (35, 245, 1075, 575)),
    19: (26, (105, 225, 1005, 660)),
}


def main() -> None:
    pdf = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PDF
    if not pdf.is_file():
        raise FileNotFoundError(pdf)
    DEST.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="conv-ch09-") as temporary:
        temp = Path(temporary)
        for number, (page, box) in FIGURES.items():
            stem = temp / f"slide-{page:02d}"
            subprocess.run(
                ["pdftoppm", "-f", str(page), "-l", str(page),
                 "-singlefile", "-scale-to-x", "1100", "-scale-to-y", "-1",
                 "-png", str(pdf), str(stem)],
                check=True,
            )
            with Image.open(stem.with_suffix(".png")) as slide:
                slide.crop(box).save(DEST / f"fig-9-{number:02d}.png", optimize=True)
    print(f"Extracted {len(FIGURES)} figures to {DEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
