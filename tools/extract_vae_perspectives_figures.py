"""Extract original Appendix D proposition and remarks from lecture_notes.pdf.

Coordinates are PDF points from the top-left corner of a 612 x 792 pt page.
Poppler renders the selected original PDF regions directly at 300 DPI, without
redrawing, OCR replacement, or resizing. Only unpublished draft assets are
written; the source PDF is never copied into the draft.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess

from PIL import Image


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parent
SOURCE = WORKSPACE / "lecture_notes.pdf"
SOURCE_URL = "https://diffusion.csail.mit.edu/2026/docs/lecture_notes.pdf"
DRAFT_IMAGES = PROJECT / "drafts/vae-additional-perspectives/images"
DPI = 300

# Regions preserve complete original shaded boxes without neighboring prose.
# The source wording is intentionally preserved, including the issues in
# Remarks 42 and 43 that the article explicitly explains and corrects.
EXCERPTS = (
    {
        "filename": "proposition-3-kl-chain-rule.png",
        "kind": "proposition",
        "label": "Proposition 3",
        "pdf_page_1_based": 78,
        "crop_points_top_left_ltrb": [54, 165, 558, 331],
        "content": "Entire original shaded Proposition 3 box, including the chain rule and data-processing inequality (138)",
        "reading_notes": [
            "The joint KL equals the x-marginal KL plus the expected conditional posterior KL.",
            "The proof is transcribed and expanded in the article; this crop preserves the original proposition only.",
        ],
    },
    {
        "filename": "remark-42-joint-matching.png",
        "kind": "remark",
        "label": "Remark 42",
        "pdf_page_1_based": 80,
        "crop_points_top_left_ltrb": [54, 271, 558, 454],
        "content": "Entire original Remark 42 box concerning joint matching and the aggregate latent marginal",
        "reading_notes": [
            "Original wording is preserved; matching joint distributions alone does not guarantee low paired reconstruction distortion.",
            "The article provides a counterexample and distinguishes distributional matching from reconstruction quality.",
        ],
    },
    {
        "filename": "remark-43-variational.png",
        "kind": "remark",
        "label": "Remark 43",
        "pdf_page_1_based": 80,
        "crop_points_top_left_ltrb": [54, 465, 558, 612],
        "content": "Entire original Remark 43 box, including the posterior identity and the source's equals-zero typo",
        "reading_notes": [
            "The source's equality of two joint distributions to zero is a typographical error and is not silently edited in this crop.",
            "Even an exact posterior alone does not guarantee matching the model marginal to the data distribution.",
            "The article separately explains these errors and the meaning of variational inference.",
        ],
    },
    {
        "filename": "figure-22-reconstruction-rate-distortion.png",
        "kind": "figure",
        "label": "Figure 22",
        "pdf_page_1_based": 82,
        "crop_points_top_left_ltrb": [54, 75, 558, 310],
        "content": "Both complete panels, all latent visualizations and rates/distortions, and the entire Figure 22 caption",
        "reading_notes": [
            "The left panel illustrates that improved reconstruction FID can accompany worse generation FID across tokenizer configurations.",
            "The right panel distinguishes perceptual compression from semantic compression on a rate-distortion diagram.",
            "The caption labels both panels Right; the article explains this source label typo and interprets panels by their actual positions.",
            "This is an empirical illustration, not a theorem that reconstruction and generation must always trade off.",
        ],
    },
)


def main() -> None:
    renderer = shutil.which("pdftoppm")
    if not renderer:
        raise SystemExit("Poppler pdftoppm was not found on PATH")
    if not SOURCE.is_file():
        raise SystemExit(f"Source PDF does not exist: {SOURCE}")

    DRAFT_IMAGES.mkdir(parents=True, exist_ok=True)
    version = subprocess.run([renderer, "-v"], capture_output=True, text=True, check=False)
    records = []
    for spec in EXCERPTS:
        left, top, right, bottom = spec["crop_points_top_left_ltrb"]
        if not (0 <= left < right <= 612 and 0 <= top < bottom <= 792):
            raise ValueError(f"Invalid crop for {spec['filename']}")
        scale = DPI / 72
        pixel_box = [
            math.floor(left * scale),
            math.floor(top * scale),
            math.ceil(right * scale),
            math.ceil(bottom * scale),
        ]
        x, y, x_end, y_end = pixel_box
        width, height = x_end - x, y_end - y
        destination = DRAFT_IMAGES / spec["filename"]
        subprocess.run(
            [renderer, "-f", str(spec["pdf_page_1_based"]), "-singlefile",
             "-r", str(DPI), "-x", str(x), "-y", str(y),
             "-W", str(width), "-H", str(height), "-png", str(SOURCE),
             str(destination.with_suffix(""))],
            check=True,
        )
        with Image.open(destination) as image:
            if image.size != (width, height):
                raise RuntimeError(f"Unexpected crop dimensions: {destination}")
            actual_size = list(image.size)
            png_dpi = image.info.get("dpi")
        record = dict(spec)
        record.update({
            "source_url": SOURCE_URL + "#page=" + str(spec["pdf_page_1_based"]),
            "pixel_crop_ltrb": pixel_box,
            "image_size_px": actual_size,
            "png_dpi_metadata": png_dpi,
            "draft_relative_path": "images/" + destination.name,
            "output_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        })
        records.append(record)
        print(f"{spec['label']}: {destination.name}: {width} x {height} px")

    metadata = {
        "source_pdf_relative_to_workspace": "lecture_notes.pdf",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "source_title": "An Introduction to Flow Matching and Diffusion Models",
        "source_url": SOURCE_URL,
        "authors": ["Peter Holderrieth", "Ezra Erives"],
        "source_year": 2026,
        "source_page_size_points": [612, 792],
        "dpi": DPI,
        "coordinate_system": "PDF points (1/72 inch), top-left origin, [left, top, right, bottom]",
        "renderer": "pdftoppm (Poppler)",
        "renderer_version": (version.stdout + version.stderr).strip(),
        "processing": "Original PDF regions rendered directly; no redrawing, OCR replacement, or resizing",
        "reproduction_script": "learning-notes/tools/extract_vae_perspectives_figures.py",
        "figures": records,
    }
    (DRAFT_IMAGES / "lecture-original-figures.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )


if __name__ == "__main__":
    main()
