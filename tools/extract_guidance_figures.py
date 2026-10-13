"""Render Chapter 5 original excerpts from lecture_notes.pdf at 300 DPI.

Coordinates use PDF points from the top-left of 612 x 792 pt pages.
Writes only draft and output/pdf assets; never writes published docs/.
Requires Poppler pdftoppm and Pillow. Run from any working directory.
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
DRAFT_IMAGES = PROJECT / "drafts" / "guidance" / "images"
DELIVERY = WORKSPACE / "output" / "pdf" / "guidance-original-figures"
DPI = 300

EXCERPTS = (
    {
        "filename": "figure-11-corgi-guidance.png",
        "pdf_page_1_based": 35,
        "crop_points_top_left_ltrb": [54, 78, 558, 300],
        "content": "Figure 11: vanilla versus strengthened corgi conditioning, including all twelve original samples and the complete original caption",
        "reading_notes": [
            "Left: vanilla guidance. Right: reinforced prompt/class conditioning with guidance scale w = 4.",
            "The original caption labels the right group classifier guidance, then says classifier-free guidance. Chapter 5 page 39 explicitly identifies Figure 11 as class-based classifier-free guidance. Preserve the original image and clarify the inconsistent caption in the accompanying explanation.",
            "The illustration motivates stronger adherence to y; it is not a proof that increasing guidance always improves quality.",
        ],
    },
    {
        "filename": "figure-12-guidance-vector-fields.png",
        "pdf_page_1_based": 36,
        "crop_points_top_left_ltrb": [54, 78, 558, 391],
        "content": "Figure 12: full classifier and classifier-free vector-field diagrams with the complete original caption",
        "rows_top_to_bottom": ["classifier guidance", "classifier-free guidance"],
        "reading_notes": [
            "The gray unguided vector plus the green prompt-dependent vector gives the blue guided vector. Scaling the green vector produces the red reinforced vector.",
            "Upper row: the prompt-dependent component is a_t times the x-gradient of log p_t(y|x). Lower row: the same component is the guided vector minus the unguided vector.",
            "The caption's first sentence is grammatically incomplete; the diagrams and Equations 59-62 identify the decomposition precisely. The differentiated quantity is a log-probability, with the factor a_t converting the score difference to a velocity difference.",
            "For w > 1 this is extrapolation beyond the guided vector, not a convex average.",
        ],
    },
    {
        "filename": "figure-13-guidance-scales.png",
        "pdf_page_1_based": 39,
        "crop_points_top_left_ltrb": [54, 78, 558, 300],
        "content": "Figure 13: all three MNIST guidance-scale sample grids, w = 1, 2, 4, including the complete original caption",
        "guidance_scales_left_to_right": [1, 2, 4],
        "reading_notes": [
            "Each grid groups samples by the requested digit class; the panels compare different inference-time guidance scales.",
            "The visual example illustrates stronger class adherence, not exact distribution matching or a universal optimal value of w.",
            "Training-time label-drop probability eta and inference-time guidance scale w are different controls.",
        ],
    },
    {
        "filename": "algorithm-5-cfg-training.png",
        "pdf_page_1_based": 38,
        "crop_points_top_left_ltrb": [54, 333, 558, 523],
        "content": "Complete Algorithm 5, including title, Require line, all nine steps, conditional-velocity loss and enclosing rules",
        "reading_notes": [
            "Sample paired data (z,y), time and Gaussian noise; construct x = alpha_t z + beta_t epsilon.",
            "Drop only y, not z or the velocity target. Both guided and unguided inputs share one neural network.",
            "The algorithm's line 6 denotes label-drop probability by p; the prose and Summary 27 use eta for the same hyperparameter.",
            "Guidance scale w is not used in this training loop; it combines network outputs during sampling.",
        ],
    },
    {
        "filename": "lecture-summary-27-p38.png",
        "pdf_page_1_based": 38,
        "crop_points_top_left_ltrb": [54, 549, 558, 667],
        "content": "Summary 27 part 1: complete heading, guided/unguided fields, CFG combination Equation 65 and the sentence continued on page 39",
        "box_id": "summary-27",
        "part": 1,
    },
    {
        "filename": "lecture-summary-27-p39.png",
        "pdf_page_1_based": 39,
        "crop_points_top_left_ltrb": [54, 316, 558, 598],
        "content": "Summary 27 part 2: full continuation, training objective Equations 66-67, training procedure and inference-time ODE sampling",
        "box_id": "summary-27",
        "part": 2,
        "reading_notes": [
            "Summary 27 spans pages 38 and 39; display the two parts consecutively in their original order.",
            "Its final row promises adherence to y rather than exact sampling from p_data(.|y) for w > 1; the immediately following prose makes this limitation explicit.",
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
        pixel_box = [math.floor(left * scale), math.floor(top * scale),
                     math.ceil(right * scale), math.ceil(bottom * scale)]
        x, y, x_end, y_end = pixel_box
        width, height = x_end - x, y_end - y
        destination = DRAFT_IMAGES / spec["filename"]
        subprocess.run(
            [renderer, "-f", str(spec["pdf_page_1_based"]), "-singlefile",
             "-r", str(DPI), "-x", str(x), "-y", str(y),
             "-W", str(width), "-H", str(height), "-png", str(SOURCE),
             str(destination.with_suffix(""))], check=True,
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
        "reproduction_script": "learning-notes/tools/extract_guidance_figures.py",
        "figures": records,
    }
    for folder in (DRAFT_IMAGES, DELIVERY):
        (folder / "lecture-original-figures.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8", newline="\n",
        )


if __name__ == "__main__":
    main()
