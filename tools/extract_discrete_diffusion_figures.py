"""Extract complete Chapter 7 figures and algorithms from lecture_notes.pdf.

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
DRAFT_IMAGES = PROJECT / "drafts/discrete-diffusion-models/images"
DPI = 300

# All regions include the complete original caption or algorithm title, and
# exclude unrelated neighboring prose. Algorithm 7 and Algorithm 8 each fit on
# one source page and therefore require no joining or continuation images.
EXCERPTS = (
    {
        "filename": "figure-17-ctmc-trajectory.png",
        "kind": "figure",
        "label": "Figure 17",
        "pdf_page_1_based": 54,
        "crop_points_top_left_ltrb": [304, 387, 558, 570],
        "content": "Entire continuous-time Markov-chain trajectory with three discrete states, including the complete Figure 17 caption",
        "reading_notes": [
            "Time is continuous, while the state takes values in a discrete set.",
            "Horizontal segments show a state being retained between random jump times; filled and open circles distinguish the state at a jump from its preceding value.",
            "The example has sequence length d = 1 and three possible states.",
        ],
    },
    {
        "filename": "figure-18-factorized-rate-matrix.png",
        "kind": "figure",
        "label": "Figure 18",
        "pdf_page_1_based": 58,
        "crop_points_top_left_ltrb": [54, 81, 558, 297],
        "content": "Both general and factorized rate-matrix diagrams, with the complete Figure 18 caption",
        "reading_notes": [
            "The grid illustrates a state space of sequences with d = 2 positions; each axis corresponds to one position.",
            "An individual jump of a factorized CTMC changes only one sequence position, so arrows are axis-aligned.",
            "Parallel-token Euler sampling can nevertheless change several positions within one finite step, with higher-order simultaneous-update probability.",
        ],
    },
    {
        "filename": "algorithm-7-factorized-ctmc-sampling.png",
        "kind": "algorithm",
        "label": "Algorithm 7",
        "pdf_page_1_based": 58,
        "crop_points_top_left_ltrb": [54, 367, 558, 657],
        "content": "Complete sampling algorithm: title, Require line, all twelve numbered steps, per-position Euler probability formula, and enclosing rules",
        "reading_notes": [
            "The factorized rates are evaluated from the full current sequence before the per-position parallel updates.",
            "For a finite step h, each position either stays or jumps according to a categorical Euler approximation.",
            "The step size must make all categorical probabilities nonnegative; the displayed formula is not an unconditional guarantee for arbitrary h.",
        ],
    },
    {
        "filename": "figure-19-discrete-probability-path.png",
        "kind": "figure",
        "label": "Figure 19",
        "pdf_page_1_based": 60,
        "crop_points_top_left_ltrb": [54, 299, 558, 562],
        "content": "All ten panels of the conditional and marginal discrete probability paths, with the complete Figure 19 caption",
        "reading_notes": [
            "Each grid cell is a discrete sequence state with d = 2; color indicates its probability mass.",
            "The top row fixes one terminal data state, marked by an orange cross; the bottom row averages over data states.",
            "These panels depict distributions, rather than successive states of one sampled trajectory.",
            "In this chapter the generation-time direction runs from the initial distribution at t = 0 to the data distribution at t = 1.",
        ],
    },
    {
        "filename": "algorithm-8-discrete-diffusion-training.png",
        "kind": "algorithm",
        "label": "Algorithm 8",
        "pdf_page_1_based": 65,
        "crop_points_top_left_ltrb": [54, 80, 558, 413],
        "content": "Complete discrete-diffusion training algorithm: title, all Require lines, all fourteen numbered steps, corruption sampling, posterior prediction, loss, and parameter update",
        "reading_notes": [
            "A Bernoulli value m_j = 1 retains the clean token z_j; m_j = 0 draws that position from the initial-noise marginal.",
            "The network sees the whole noisy sequence and time, and predicts a vocabulary distribution for each position.",
            "The training target is the original terminal token z_j; the displayed objective sums token-wise negative log-likelihoods.",
        ],
    },
    {
        "filename": "figure-20-masked-diffusion-language-model.png",
        "kind": "figure",
        "label": "Figure 20",
        "pdf_page_1_based": 65,
        "crop_points_top_left_ltrb": [54, 434, 558, 593],
        "content": "All four rows of the masked language-model trajectory, including time labels, seven token positions, and the complete Figure 20 caption",
        "reading_notes": [
            "The trajectory proceeds from all [MASK] tokens at t = 0 to a full sentence at t = 1.",
            "Several different positions can be revealed in parallel, rather than strictly from left to right.",
            "The diagram is an illustrative trajectory, not a claim that general CTMC sampling can never revise an existing token.",
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
        "reproduction_script": "learning-notes/tools/extract_discrete_diffusion_figures.py",
        "figures": records,
    }
    (DRAFT_IMAGES / "lecture-original-figures.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )


if __name__ == "__main__":
    main()
