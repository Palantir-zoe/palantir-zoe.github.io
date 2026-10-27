"""Browser-check the Appendix D preview, or public files with --published."""

import argparse
from hashlib import sha256
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname
import json
import re
import sys

from playwright.sync_api import sync_playwright

from render_vae_perspectives_draft import (
    AUDIT, DRAFT, ROOT, SECTION_IDS, SLUG, docs_snapshot, load_inputs,
)


def file_path(url):
    parsed = urlparse(url)
    if parsed.scheme != "file":
        raise ValueError("Expected a local file URL: " + url)
    path = Path(url2pathname(unquote(parsed.path)))
    if path.is_dir():
        path = path / "index.html"
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--published", action="store_true", help="Check docs/posts/vae-additional-perspectives instead of the draft preview.")
    args = parser.parse_args()
    source, post, metadata, _ = load_inputs()
    article = ROOT / "docs/posts" / SLUG if args.published else DRAFT
    preview = article / ("index.html" if args.published else "preview.html")
    if not preview.is_file():
        raise FileNotFoundError("Appendix D page is missing; run its renderer first: " + str(preview))
    out = ROOT / ".runtime" / ("vae-perspectives-published-qa" if args.published else "vae-perspectives-draft-qa")
    out.mkdir(parents=True, exist_ok=True)
    formulas = [unescape(match[1] if match[1] is not None else match[2])
                for match in re.finditer(r"\\\[(.*?)\\\]|\\\((.*?)\\\)", source, re.S)]
    records = {"images/" + item["filename"]: item for item in metadata["figures"]}
    before = docs_snapshot()
    report = {
        "mode": "published" if args.published else "draft",
        "checks": {}, "viewports": [], "images": [], "errors": [],
        "failed_requests": [], "http_errors": [], "local_links": [],
    }
    checks = report["checks"]
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    checks["render_audit_matches_current_public_files"] = audit["docs_after"] == before
    if args.published:
        catalog = json.loads((ROOT / "docs/posts.json").read_text(encoding="utf-8"))
        matches = [i for i, item in enumerate(catalog) if item["slug"] == SLUG]
        checks["exactly_one_catalog_entry"] = len(matches) == 1
        checks["catalog_metadata_matches"] = len(matches) == 1 and catalog[matches[0]] == post
        checks["catalog_follows_discrete_diffusion"] = (
            len(matches) == 1 and matches[0] > 0 and catalog[matches[0] - 1]["slug"] == "discrete-diffusion-models")
        checks["images_metadata_copied"] = json.loads((
            article / "images/lecture-original-figures.json").read_text(encoding="utf-8")) == metadata
    elif not audit["published"]:
        checks["default_render_preserved_public_files"] = (
            audit["public_docs_unchanged"] and audit["docs_before"] == audit["docs_after"])

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path="C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", headless=True)
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.on("pageerror", lambda error: report["errors"].append(str(error)))
            page.on("requestfailed", lambda request: report["failed_requests"].append(
                {"url": request.url, "failure": request.failure}))
            page.on("response", lambda response: report["http_errors"].append(
                {"url": response.url, "status": response.status}) if response.status >= 400 else None)
            page.goto(preview.as_uri(), wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            page.screenshot(path=str(out / "intro-desktop.png"))
            robots = page.locator('meta[name="robots"]')
            meta = page.locator("header .post-meta").inner_text()
            if args.published:
                checks["public_page_keeps_review_marker_without_local_preview_or_noindex"] = (
                    "本地预览" not in meta and "审阅稿" in meta
                    and all("noindex" not in item.lower() for item in robots.evaluate_all(
                        "els=>els.map(el=>el.content)")))
            else:
                checks["preview_marker_and_noindex"] = (
                    "本地预览" in meta and "审阅稿" in meta and robots.count() == 1
                    and robots.get_attribute("content") == "noindex, nofollow")
            annotations = page.locator('.page-body .katex annotation[encoding="application/x-tex"]').all_text_contents()
            checks["all_formulas_rendered_in_order"] = annotations == formulas and len(formulas) > 0
            checks["no_formula_errors"] = page.locator(".katex-error").count() == 0
            report["formula_count"] = len(annotations)
            checks["nine_ordered_appendix_sections"] = page.locator(".page-body h2[id]").evaluate_all(
                "els=>els.map(el=>el.id)") == SECTION_IDS
            heading_ids = [anchor for _, anchor in re.findall(r'<h([23]) id="([^"]+)"', source)]
            checks["toc_matches_all_anchored_headings"] = page.locator(".note-toc a").evaluate_all(
                "els=>els.map(el=>el.getAttribute('href'))") == ["#" + anchor for anchor in heading_ids]
            all_ids = page.locator("[id]").evaluate_all("els=>els.map(el=>el.id)")
            checks["all_ids_are_unique"] = len(all_ids) == len(set(all_ids))
            previous = file_path(page.locator('a[rel="prev"]').evaluate("el=>el.href"))
            checks["discrete_diffusion_is_previous"] = previous.resolve() == (
                ROOT / "docs/posts/discrete-diffusion-models/index.html").resolve()
            checks["table_headers_have_scope"] = all(page.locator(".page-body th").evaluate_all(
                "els=>els.map(el=>['col','row','colgroup','rowgroup'].includes(el.getAttribute('scope')))"))
            images = page.locator(".page-body img")
            checks["all_metadata_images_embedded"] = images.count() == len(records) == 4
            for img in images.all():
                img.scroll_into_view_if_needed()
                img.evaluate("el=>el.decode()")
                status = img.evaluate("el=>({src:el.getAttribute('src'),width:el.naturalWidth,height:el.naturalHeight,alt:el.alt,complete:el.complete})")
                record = records.get(status["src"])
                status["matches_original"] = (
                    record is not None and [status["width"], status["height"]] == record["image_size_px"])
                figure = img.locator("xpath=ancestor::figure")
                status["has_pdf_source"] = record is not None and record["source_url"] in figure.locator(
                    "figcaption a").evaluate_all("els=>els.map(el=>el.getAttribute('href'))")
                local_image = article / status["src"]
                status["matches_source_bytes"] = local_image.read_bytes() == (DRAFT / status["src"]).read_bytes()
                if record is not None and record.get("output_sha256"):
                    status["matches_source_bytes"] = status["matches_source_bytes"] and (
                        sha256(local_image.read_bytes()).hexdigest() == record["output_sha256"])
                with page.expect_popup() as event:
                    img.locator("xpath=parent::a").click()
                popup = event.value
                popup.wait_for_load_state()
                popup.locator("img").evaluate("el=>el.decode()")
                status["opens_full_size"] = record is not None and popup.locator("img").evaluate(
                    "el=>[el.naturalWidth,el.naturalHeight]") == record["image_size_px"]
                popup.close()
                report["images"].append(status)
            checks["all_images_load_match_and_open"] = len(report["images"]) == len(records) and all(
                item["complete"] and item["alt"] and item["matches_original"] and item["has_pdf_source"]
                and item["opens_full_size"] and item["matches_source_bytes"] for item in report["images"])
            for href in page.locator("a[href]").evaluate_all("els=>els.map(el=>el.href)"):
                parsed = urlparse(href)
                if parsed.scheme != "file":
                    continue
                target = file_path(href)
                status = {"url": href, "exists": target.is_file()}
                if target.resolve() == preview.resolve() and parsed.fragment:
                    status["anchor_exists"] = unquote(parsed.fragment) in all_ids
                report["local_links"].append(status)
            checks["all_local_links_and_anchors_resolve"] = bool(report["local_links"]) and all(
                item["exists"] and item.get("anchor_exists", True) for item in report["local_links"])
            for anchor in SECTION_IDS:
                page.locator("#" + anchor).scroll_into_view_if_needed()
                page.screenshot(path=str(out / (anchor + "-desktop.png")))
            for width in (390, 768, 1440):
                page.set_viewport_size({"width": width, "height": 900})
                page.locator("details").evaluate_all("els=>els.forEach(el=>el.open=true)")
                page.evaluate("document.fonts.ready")
                page.wait_for_timeout(100)
                result = page.evaluate("""() => ({
                    width:innerWidth, scrollWidth:document.documentElement.scrollWidth,
                    details:document.querySelectorAll('details').length,
                    openDetails:document.querySelectorAll('details[open]').length,
                    badMath:[...document.querySelectorAll('.katex-display')]
                      .filter(el=>el.scrollWidth>el.clientWidth+2 && !['auto','scroll'].includes(getComputedStyle(el).overflowX))
                      .map(el=>el.textContent.slice(0,80)),
                    brokenImages:[...document.querySelectorAll('.page-body img')]
                      .filter(el=>!el.complete||!el.naturalWidth).map(el=>el.src)
                })""")
                report["viewports"].append(result)
                if width == 390:
                    page.evaluate("window.scrollTo(0,0)")
                    page.screenshot(path=str(out / "intro-mobile.png"))
                    page.locator("#elbo").scroll_into_view_if_needed()
                    page.screenshot(path=str(out / "elbo-mobile-expanded.png"))
                page.locator("details").evaluate_all("els=>els.forEach(el=>el.open=false)")
            checks["expanded_mobile_and_desktop_fit"] = all(
                item["scrollWidth"] <= item["width"] + 1 and not item["badMath"] and not item["brokenImages"]
                and item["details"] == item["openDetails"] for item in report["viewports"])
            page.locator(".reading-return").click()
            checks["return_to_toc_works"] = page.evaluate("location.hash") == "#reading-toc"
            checks["no_browser_or_request_errors"] = (
                not report["errors"] and not report["failed_requests"] and not report["http_errors"])
        finally:
            browser.close()
    checks["qa_preserved_public_files"] = docs_snapshot() == before
    report["passed"] = all(checks.values())
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "mode", "passed", "checks", "formula_count", "viewports", "images", "errors", "failed_requests", "http_errors")},
        ensure_ascii=False, indent=2))
    raise SystemExit(not report["passed"])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
