"""Extract original Flow Matching figures, boxed statements and Algorithm 3 at 300 DPI.

Run from any directory: python learning-notes/tools/extract_flow_matching_figures.py
Requires Poppler's pdftoppm and Pillow. Coordinates are PDF points measured from
the top-left of the unrotated 612 x 792 point pages. Original captions are kept.
This script writes only draft assets and output/pdf/, never published docs/.
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
DRAFT_IMAGES = PROJECT / "drafts" / "flow-matching" / "images"
DELIVERY = WORKSPACE / "output" / "pdf" / "flow-matching-original-figures"
DPI = 300

EXCERPTS = (
    {
        "filename": "lecture-example-8-p15.png",
        "pdf_page_1_based": 15,
        "crop_points_top_left_ltrb": [54, 560, 558, 671],
        "content": "Example 8, part 1: complete original Gaussian conditional probability path statement and Equation 15",
        "box_id": "example-8",
        "part": 1,
    },
    {
        "filename": "lecture-example-8-p16.png",
        "pdf_page_1_based": 16,
        "crop_points_top_left_ltrb": [54, 79, 558, 267],
        "content": "Example 8, part 2: complete continuation, endpoint distributions, sampling rule and Equation 16",
        "box_id": "example-8",
        "part": 2,
    },
    {
        "filename": "lecture-theorem-9.png",
        "pdf_page_1_based": 16,
        "crop_points_top_left_ltrb": [54, 519, 558, 693],
        "content": "Complete Theorem 9 (Marginalization trick), including Equations 18-19 and the endpoint conclusion",
        "box_id": "theorem-9",
    },
    {
        "filename": "lecture-example-10.png",
        "pdf_page_1_based": 17,
        "crop_points_top_left_ltrb": [54, 501, 558, 690],
        "content": "Complete Example 10 statement (Target ODE for Gaussian probability paths), including Equation 20",
        "box_id": "example-10",
        "part": "statement",
    },
    {
        "filename": "lecture-example-10-proof.png",
        "pdf_page_1_based": 18,
        "crop_points_top_left_ltrb": [54, 79, 558, 423],
        "content": "Complete Example 10 continuation: original proof, Equation 21, all algebraic steps and its footnote",
        "box_id": "example-10",
        "part": "proof",
    },
    {
        "filename": "lecture-theorem-11.png",
        "pdf_page_1_based": 19,
        "crop_points_top_left_ltrb": [54, 79, 558, 198],
        "content": "Complete Theorem 11 (Continuity Equation), including the initial condition, iff statement, Equation 23 and derivative definition",
        "box_id": "theorem-11",
    },
    {
        "filename": "lecture-theorem-12.png",
        "pdf_page_1_based": 20,
        "crop_points_top_left_ltrb": [54, 369, 558, 552],
        "content": "Complete Theorem 12, including both loss and gradient equalities and the expressivity assumption",
        "box_id": "theorem-12",
    },
    {
        "filename": "lecture-example-13-p22.png",
        "pdf_page_1_based": 22,
        "crop_points_top_left_ltrb": [54, 303, 558, 693],
        "content": "Example 13, part 1: Gaussian conditional flow matching, Equations 28-31 and the CondOT specialization",
        "box_id": "example-13",
        "part": 1,
    },
    {
        "filename": "lecture-example-13-p23.png",
        "pdf_page_1_based": 23,
        "crop_points_top_left_ltrb": [54, 370, 558, 399],
        "content": "Example 13, part 2: complete final sentence continued on the next page",
        "box_id": "example-13",
        "part": 2,
    },
    {
        "filename": "lecture-summary-14-p23.png",
        "pdf_page_1_based": 23,
        "crop_points_top_left_ltrb": [54, 414, 558, 694],
        "content": "Summary 14, part 1: Flow Matching construction and training, including Equations 32-34",
        "box_id": "summary-14",
        "part": 1,
    },
    {
        "filename": "lecture-summary-14-p24.png",
        "pdf_page_1_based": 24,
        "crop_points_top_left_ltrb": [54, 79, 558, 226],
        "content": "Summary 14, part 2: Gaussian formulas 35-37 and all noise scheduler conditions",
        "box_id": "summary-14",
        "part": 2,
    },
    {
        "filename": "figure-4-noise-to-data.png",
        "pdf_page_1_based": 14,
        "crop_points_top_left_ltrb": [53, 316, 562, 460],
        "content": "Figure 4: five grids of digit images along a Gaussian conditional probability path, with the complete original caption",
        "reading_notes": [
            "Each grid contains nine individual image samples, not a two-dimensional histogram of the data distribution.",
            "Each original digit image is a data point of dimension 32 x 32 = 1024.",
            "Left to right shows the progression from noise to digit images; the original figure does not label its five time values.",
        ],
    },
    {
        "filename": "figure-5-probability-paths.png",
        "pdf_page_1_based": 15,
        "crop_points_top_left_ltrb": [53, 80, 561, 342],
        "content": "Figure 5: complete conditional and marginal probability-path rows and original caption",
        "time_labels_left_to_right": [0, 0.25, 0.5, 0.75, 1],
        "noise_schedulers": {"alpha_t": "t", "beta_t": "1 - t"},
        "reading_notes": [
            "The top row conditions on one fixed data point z and shrinks a Gaussian to the point mass at z.",
            "The bottom row marginalizes over data points and evolves a Gaussian into the two-dimensional checkerboard data distribution.",
            "The colored panels are distribution histograms; they do not depict individual image samples as Figure 4 does.",
        ],
    },
    {
        "filename": "figure-6-vector-fields.png",
        "pdf_page_1_based": 17,
        "crop_points_top_left_ltrb": [53, 78, 561, 485],
        "content": "Figure 6: all six conditional/marginal ODE comparison panels with the complete original caption",
        "rows_top_to_bottom": ["conditional probability path", "marginal probability path"],
        "columns_left_to_right": ["ground-truth samples", "ODE samples over time", "ODE trajectories"],
        "reading_notes": [
            "The background data distribution is blue, while the initial Gaussian is red.",
            "Conditioning on the red-star target z gives trajectories towards that one target; marginal trajectories distribute samples among the data modes.",
            "Compare distributions in the first two columns rather than demanding pointwise equality of individual sampled trajectories.",
            "The original bottom-middle and bottom-right panel titles explicitly say Learned Marginal ODE.",
        ],
    },
    {
        "filename": "algorithm-3-training.png",
        "pdf_page_1_based": 22,
        "crop_points_top_left_ltrb": [53, 79, 561, 290],
        "content": "Complete original Algorithm 3, including heading, Require line, steps 1-8, general-case formulas, and enclosing horizontal rules",
        "reading_notes": [
            "Sample a data point z, a time t, and Gaussian noise epsilon.",
            "For the Gaussian CondOT path, construct x = t z + (1 - t) epsilon and regress the neural vector field onto z - epsilon.",
            "The network parameters are updated during this training procedure; the displayed training loop does not solve an ODE.",
            "The source heading uses the compact variance notation (1 - t)^2; in d dimensions the corresponding covariance is (1 - t)^2 I_d.",
        ],
    },
    {
        "filename": "figure-7-trained-flow.png",
        "pdf_page_1_based": 23,
        "crop_points_top_left_ltrb": [53, 78, 561, 355],
        "content": "Figure 7: both ground-truth and trained-flow histogram rows with the complete original caption",
        "ground_truth_time_labels": [0, 0.25, 0.5, 0.75, 1],
        "learned_time_labels": [0, 0.25, 0.51, 0.76, 1],
        "reading_notes": [
            "The top row shows samples from the prescribed marginal probability path.",
            "The bottom row shows samples obtained by simulating the trained flow-matching ODE.",
            "The corresponding distributions approximately match after training; the figure is not a claim that individual sample paths are identical.",
            "The source caption attributes remaining differences to training error; the plotted time labels also reflect the simulation grid.",
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
        "reproduction_script": "learning-notes/tools/extract_flow_matching_figures.py",
        "figures": records,
    }
    for folder in (DRAFT_IMAGES, DELIVERY):
        (folder / "lecture-original-figures.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8", newline="\n",
        )


if __name__ == "__main__":
    main()
