"""Extract selected Chapter 4 originals from the local lecture PDF at 300 DPI.

Coordinates are PDF points measured from the top-left of 612 x 792 pt pages.
Writes local draft assets and output/pdf only; never writes published docs/.
Requires Poppler pdftoppm and Pillow. Re-run from any working directory.
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
DRAFT_IMAGES = PROJECT / "drafts" / "score-matching" / "images"
DELIVERY = WORKSPACE / "output" / "pdf" / "score-matching-original-figures"
DPI = 300

EXCERPTS = (
    {
        "filename": "figure-8-score.png",
        "pdf_page_1_based": 25,
        "crop_points_top_left_ltrb": [253, 188, 558, 392],
        "content": "Figure 8: probability density at left and score vector field at right, with the complete original caption",
        "reading_notes": [
            "The arrows are the gradient with respect to x of the log density, not an already chosen generative velocity field.",
            "The original caption says black rows; these are the black arrows visible in the right panel.",
            "The figure sits beside body text in the PDF; the crop excludes the left-column prose.",
        ],
    },
    {
        "filename": "lecture-proposition-1.png",
        "pdf_page_1_based": 26,
        "crop_points_top_left_ltrb": [54, 127, 558, 288],
        "content": "Complete Proposition 1: Gaussian probability-path conversion between conditional or marginal score and vector field, Equations 41-42",
        "box_id": "proposition-1",
        "reading_notes": [
            "The displayed coefficients divide by alpha_t, so the expression is evaluated where alpha_t is nonzero.",
            "Recovering the score from the vector field additionally requires nonzero a_t; endpoint singularities need a limit or separate treatment.",
        ],
    },
    {
        "filename": "figure-9-sde-paths.png",
        "pdf_page_1_based": 27,
        "crop_points_top_left_ltrb": [53, 78, 561, 462],
        "content": "Figure 9: complete two-by-three comparison of conditional and marginal probability paths with SDE samples and trajectories, including the original caption",
        "rows_top_to_bottom": ["conditional probability path", "marginal probability path"],
        "columns_left_to_right": ["ground-truth samples", "SDE samples", "SDE trajectories"],
        "reading_notes": [
            "SDE trajectories are irregular even though their time marginals follow the same prescribed probability path as the corresponding ODE.",
            "The red star marks the fixed conditional target z in the top row; marginal samples in the bottom row cover multiple data modes.",
            "Matching distributions does not assert that individual stochastic and deterministic trajectories are equal.",
        ],
    },
    {
        "filename": "lecture-theorem-17-p27.png",
        "pdf_page_1_based": 27,
        "crop_points_top_left_ltrb": [54, 633, 558, 688],
        "content": "Theorem 17, part 1: SDE Extension Trick heading and the opening conditional/marginal vector-field assumptions",
        "box_id": "theorem-17",
        "part": 1,
    },
    {
        "filename": "lecture-theorem-17-p28.png",
        "pdf_page_1_based": 28,
        "crop_points_top_left_ltrb": [54, 79, 558, 249],
        "content": "Theorem 17, part 2: complete continuation with diffusion coefficient, score-corrected SDE, Equations 44-45, endpoint conclusion and Langevin connection",
        "box_id": "theorem-17",
        "part": 2,
        "reading_notes": [
            "The score correction sigma_t squared over two times the marginal score accompanies the added Brownian noise.",
            "The statement concerns exact continuous dynamics under the relevant regularity assumptions; learned networks and discretization introduce errors.",
        ],
    },
    {
        "filename": "figure-10-langevin.png",
        "pdf_page_1_based": 30,
        "crop_points_top_left_ltrb": [53, 78, 561, 401],
        "content": "Figure 10: Langevin particle samples and kernel density estimates over four times, including the complete original caption",
        "time_labels_left_to_right": [0, 1.7, 3.3, 5],
        "reading_notes": [
            "Langevin dynamics preserve the target distribution when initialized from it.",
            "This figure instead illustrates convergence from a different starting distribution toward the five-mode target.",
            "The plotted times extend beyond one; this optional fixed-distribution example is not the main noise-to-data time interval.",
        ],
    },
    {
        "filename": "lecture-theorem-22.png",
        "pdf_page_1_based": 31,
        "crop_points_top_left_ltrb": [54, 282, 558, 435],
        "content": "Complete Theorem 22: score matching and conditional/denoising score matching losses differ by a parameter-independent constant and have equal gradients",
        "box_id": "theorem-22",
        "reading_notes": [
            "Equality of expected gradients does not mean the two numerical loss values are identical.",
            "The final exact recovery sentence presumes an adequately expressive function class and ideal optimization, as in the preceding flow-matching discussion.",
        ],
    },
    {
        "filename": "algorithm-4-training.png",
        "pdf_page_1_based": 32,
        "crop_points_top_left_ltrb": [53, 399, 561, 600],
        "content": "Complete Algorithm 4: score matching training for Gaussian probability paths, with Require line, steps 1-8, general-case alternatives and all enclosing rules",
        "reading_notes": [
            "Training draws data z, time t, and Gaussian noise epsilon, then constructs x_t = alpha_t z + beta_t epsilon.",
            "The score label is minus epsilon divided by beta_t; the noise-prediction alternative uses epsilon as the label.",
            "This is a parameter-update training loop, not an SDE sampling loop.",
            "The unweighted noise-prediction alternative changes the relative weighting across time compared with the unweighted score loss.",
        ],
    },
    {
        "filename": "lecture-summary-24-p32.png",
        "pdf_page_1_based": 32,
        "crop_points_top_left_ltrb": [54, 620, 558, 688],
        "content": "Summary 24, part 1: complete heading and opening definitions of conditional and marginal scores, continued on page 33",
        "box_id": "summary-24",
        "part": 1,
    },
    {
        "filename": "lecture-summary-24-p33.png",
        "pdf_page_1_based": 33,
        "crop_points_top_left_ltrb": [54, 79, 558, 450],
        "content": "Summary 24, part 2: complete continuation, score-corrected SDE, score matching objective, Gaussian conversion, and sampling formulas, Equations 52-56",
        "box_id": "summary-24",
        "part": 2,
        "reading_notes": [
            "The velocity-only SDE form divides by a_t; the score-only form avoids that division.",
            "The final text explicitly describes the trained-model samples as approximate.",
        ],
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
    version = subprocess.run([renderer, "-v"], capture_output=True, text=True, check=False)
    records = []
    for spec in EXCERPTS:
        left, top, right, bottom = spec["crop_points_top_left_ltrb"]
        if not (0 <= left < right <= 612 and 0 <= top < bottom <= 792):
            raise ValueError(f"Invalid crop for {spec['filename']}")
        scale = DPI / 72
        pixel_box = [
            math.floor(left * scale), math.floor(top * scale),
            math.ceil(right * scale), math.ceil(bottom * scale),
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
        with Image.open(destination) as raster:
            if raster.size != (width, height):
                raise RuntimeError(f"Unexpected crop size for {destination.name}")
            actual_size = list(raster.size)
            png_dpi = raster.info.get("dpi")
        shutil.copy2(destination, DELIVERY / destination.name)
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
        print(f"{destination.name}: {width} x {height} px at {DPI} DPI")
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
        "reproduction_script": "learning-notes/tools/extract_score_matching_figures.py",
        "figures": records,
    }
    for folder in (DRAFT_IMAGES, DELIVERY):
        (folder / "lecture-original-figures.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8", newline="\n",
        )


if __name__ == "__main__":
    main()
