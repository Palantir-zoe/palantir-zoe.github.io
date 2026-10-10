"""Render original lecture excerpts without redrawing or re-typesetting.

Run from any directory: python learning-notes/tools/extract_diffusion_figures.py
Requires Poppler's pdftoppm and Pillow. Page coordinates use PDF points measured
from the top-left of the unrotated 612 x 792 point source pages.
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
DRAFT_IMAGES = PROJECT / "drafts" / "diffusion-models" / "images"
DELIVERY = WORKSPACE / "output" / "pdf" / "diffusion-original-figures"
DPI = 300

EXCERPTS = (
    {
        "filename": "lecture-figure-3-ou.png",
        "pdf_page_1_based": 11,
        "crop_points_top_left_ltrb": [52, 78, 566, 280],
        "content": "Figure 3: all four OU panels and the complete original caption",
        "panel_parameters_left_to_right": [
            {"theta": 0.25, "sigma": 0.0},
            {"theta": 0.25, "sigma": 0.25},
            {"theta": 0.25, "sigma": 0.5},
            {"theta": 0.25, "sigma": 1.0},
        ],
        "horizontal_axis_time_range": [0, 20],
    },
    {
        "filename": "lecture-summary-7.png",
        "pdf_page_1_based": 13,
        "crop_points_top_left_ltrb": [53, 339, 559, 563],
        "content": "Complete original Summary 7 gray box, including its final sentence",
    },
    {
        "filename": "lecture-algorithm-2.png",
        "pdf_page_1_based": 13,
        "crop_points_top_left_ltrb": [53, 78, 559, 228],
        "content": "Complete original Algorithm 2, including title, Require, lines 1-9, and horizontal rules",
    },
)


def main() -> None:
    renderer = shutil.which("pdftoppm")
    if not renderer:
        raise SystemExit("Poppler pdftoppm was not found on PATH.")
    if not SOURCE.is_file():
        raise SystemExit(f"Source PDF does not exist: {SOURCE}")
    DRAFT_IMAGES.mkdir(parents=True, exist_ok=True)
    DELIVERY.mkdir(parents=True, exist_ok=True)
    version = subprocess.run(
        [renderer, "-v"], capture_output=True, text=True, check=False
    )
    records = []
    for spec in EXCERPTS:
        left, top, right, bottom = spec["crop_points_top_left_ltrb"]
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
            [
                renderer,
                "-f", str(spec["pdf_page_1_based"]),
                "-singlefile", "-r", str(DPI),
                "-x", str(x), "-y", str(y),
                "-W", str(width), "-H", str(height),
                "-png", str(SOURCE), str(destination.with_suffix("")),
            ],
            check=True,
        )
        with Image.open(destination) as raster:
            if raster.size != (width, height):
                raise RuntimeError(f"Unexpected crop size for {destination.name}")
            actual_size = list(raster.size)
        shutil.copy2(destination, DELIVERY / destination.name)
        record = dict(spec)
        record.update(
            {
                "pixel_crop_ltrb": pixel_box,
                "image_size_px": actual_size,
                "draft_relative_path": "images/" + destination.name,
                "output_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
            }
        )
        records.append(record)
        print(f"{destination.name}: {width} x {height} px at {DPI} DPI")
    metadata = {
        "source_pdf_relative_to_workspace": "lecture_notes.pdf",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "source_title": "An Introduction to Flow Matching and Diffusion Models",
        "authors": ["Peter Holderrieth", "Ezra Erives"],
        "source_year": 2026,
        "source_page_size_points": [612, 792],
        "dpi": DPI,
        "coordinate_system": "PDF points (1/72 inch), top-left origin, [left, top, right, bottom]",
        "renderer": "pdftoppm (Poppler)",
        "renderer_version": (version.stdout + version.stderr).strip(),
        "processing": "Original PDF regions rendered directly; no redrawing, OCR replacement, or resizing",
        "reproduction_script": "learning-notes/tools/extract_diffusion_figures.py",
        "figures": records,
    }
    for folder in [DRAFT_IMAGES, DELIVERY]:
        (folder / "lecture-original-figures.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
        )


if __name__ == "__main__":
    main()
