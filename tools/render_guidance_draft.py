"""Render the Guidance draft; use --publish to prepare the reviewed site files."""
import argparse
from hashlib import sha256
from html import escape, unescape
from pathlib import Path
from urllib.request import urlopen
import json
import re
import shutil
import sys

from blog import SITE_TITLE, load_posts, rebuild_site
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/content/guidance.html"
DRAFT = ROOT / "drafts/guidance"
MATH = re.compile(r"\\\[(.*?)\\\]|\\\((.*?)\\\)", re.S)


def docs_snapshot():
    return {str(path.relative_to(ROOT / "docs")): sha256(path.read_bytes()).hexdigest()
            for path in (ROOT / "docs").rglob("*") if path.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true",
                        help="Prepare the reviewed article, images and navigation in docs/.")
    args = parser.parse_args()
    docs_before = docs_snapshot()
    source = SOURCE.read_text(encoding="utf-8")
    post = json.loads((DRAFT / "post.json").read_text(encoding="utf-8"))
    if post["slug"] != "guidance":
        raise ValueError("This renderer only renders the guidance draft")
    version = (ROOT / "docs/assets/katex/version.txt").read_text().strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Invalid local KaTeX version")
    script = ROOT / ".runtime" / f"katex-{version}.min.js"
    if not script.is_file():
        script.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(f"https://cdn.jsdelivr.net/npm/katex@{version}/dist/katex.min.js", timeout=30) as response:
            script.write_bytes(response.read())
    expressions = [
        {"tex": unescape(match[1] if match[1] is not None else match[2]),
         "display": match[1] is not None}
        for match in MATH.finditer(source)
    ]
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
            headless=True,
        )
        try:
            page = browser.new_page()
            page.add_script_tag(path=str(script))
            assert page.evaluate("katex.version") == version
            rendered = page.evaluate(
                "items => items.map(i => katex.renderToString(i.tex, "
                "{displayMode:i.display,throwOnError:true,output:'htmlAndMathml'}))",
                expressions,
            )
        finally:
            browser.close()
    iterator = iter(rendered)
    body = MATH.sub(lambda _: next(iterator), source)

    def sized_image(match):
        tag = match[0]
        relative = re.search(r'\bsrc="([^"]+)"', tag)[1]
        image_path = (DRAFT / relative).resolve()
        if not image_path.is_relative_to(DRAFT.resolve()):
            raise ValueError("Article images must be inside the draft directory")
        if not image_path.is_file():
            raise FileNotFoundError("Missing article image: " + relative)
        with Image.open(image_path) as raster:
            width, height = raster.size
        tag = re.sub(r'\s+(?:width|height)="[^"]*"', '', tag)
        return tag[:-1] + f' width="{width}" height="{height}">'

    body = re.sub(r'<img\b[^>]*>', sized_image, body)
    existing = (ROOT / "docs/posts/diffusion-models/index.html").read_text(encoding="utf-8")
    head = re.search(r"<head>(.*?)</head>", existing, re.S)[1]
    title = escape(post["title"] + " · " + SITE_TITLE)
    head = re.sub(r"<title>.*?</title>", "<title>" + title + "</title>", head, count=1)
    description = '<meta name="description" content="' + escape(post["description"], quote=True) + '">'
    if re.search(r'<meta name="description" content="[^"]*">', head):
        head = re.sub(r'<meta name="description" content="[^"]*">', description, head)
    else:
        head += description
    head = re.sub(r'<meta\b(?=[^>]*name=["\']robots["\'])[^>]*>', '', head, flags=re.I)
    if not args.publish:
        head += '<meta name="robots" content="noindex, nofollow">'
    # Reserve equation-number space inside each scrollable formula.
    head += ('<style>'
             '.authored-note .katex{position:relative;}'
             '.authored-note .katex-display>.katex{min-width:max-content;}'
             '.authored-note .katex-display>.katex>.katex-html:has(>.tag){padding-inline:2.5em;}'
             '</style>')

    sections = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', source)
    if [section_id for section_id, _ in sections] != ["vanilla-guidance", "classifier-free-guidance"]:
        raise ValueError("Guidance must retain the chapter's two ordered sections")
    toc = '<nav class="note-toc" aria-label="本篇目录"><p><strong>本篇目录</strong></p><ol>' + ''.join(
        '<li><a href="#' + section_id + '">' + section_title + '</a></li>'
        for section_id, section_title in sections
    ) + '</ol></nav>'
    reference = (ROOT / "tools/reference.html").read_text(encoding="utf-8")
    reference = re.sub(r"<p>相关内容：.*?</p>",
                       "<p>相关内容：第 5 章 Guidance: How to Condition on a Prompt，5.1–5.2 节，第 34–40 页。文中原文截图附有对应页码与来源链接。</p>", reference)
    review_label = '' if args.publish else ' · 待审核'
    html = ('<!doctype html><html lang="zh-CN"><head>' + head + '</head><body>'
            '<article class="page sans"><nav class="site-nav" aria-label="网站导航"><a href="../../index.html">← ' + escape(SITE_TITLE) + '</a></nav>'
            '<header><p class="post-meta">第 5 章 · 生成模型' + review_label + '</p><h1 class="page-title">' + escape(post["title"]) + '</h1></header>'
            + toc + '<div class="page-body authored-note">' + body + '</div>' + reference
            + '<nav class="post-nav" aria-label="文章导航"><a rel="prev" href="../score-matching/index.html">上一篇：Score Functions and Score Matching</a><a href="../../index.html">返回文章目录</a></nav>'
            '</article></body></html>')
    DRAFT.mkdir(parents=True, exist_ok=True)
    (DRAFT / "index.html").write_text(html, encoding="utf-8", newline="\n")
    # index.html retains eventual article paths. preview.html resolves local
    # fonts, styles and existing public navigation directly from drafts/.
    preview = html.replace("url('../../assets/", "url('../../docs/assets/")
    preview = preview.replace('href="../../assets/', 'href="../../docs/assets/')
    preview = preview.replace('href="../../index.html"', 'href="../../docs/index.html"')
    preview = preview.replace('href="../score-matching/index.html"', 'href="../../docs/posts/score-matching/index.html"')
    (DRAFT / "preview.html").write_text(preview, encoding="utf-8", newline="\n")
    if args.publish:
        posts = load_posts(ROOT)
        image_paths = set(re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', source))
        metadata = json.loads((DRAFT / "images/lecture-original-figures.json").read_text(encoding="utf-8"))
        destination = ROOT / "docs/posts/guidance"
        destination.mkdir(parents=True, exist_ok=True)
        for relative in sorted(image_paths):
            source_image = (DRAFT / relative).resolve()
            if not source_image.is_relative_to(DRAFT.resolve()) or not source_image.is_file():
                raise ValueError("Invalid article image: " + relative)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_image, target)
        metadata["figures"] = [record for record in metadata["figures"]
                               if "images/" + record["filename"] in image_paths]
        (destination / "images/lecture-original-figures.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        (destination / "index.html").write_text(html, encoding="utf-8", newline="\n")
        existing_index = next((i for i, item in enumerate(posts) if item["slug"] == post["slug"]), None)
        if existing_index is None:
            posts.append(post)
        else:
            posts[existing_index] = post
        (ROOT / "docs/posts.json").write_text(
            json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        rebuild_site(ROOT)
    docs_after = docs_snapshot()
    if not args.publish and docs_after != docs_before:
        raise RuntimeError("Public docs changed while rendering the draft")
    audit = {"docs_before": docs_before, "docs_after": docs_after,
             "public_docs_unchanged": docs_after == docs_before, "formulas": len(rendered),
             "sections": len(sections), "figures": len(re.findall(r'<figure\b', body)),
             "images": len(re.findall(r'<img\b', body)), "published": args.publish}
    audit_path = ROOT / ".runtime/guidance-render-audit.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in audit.items() if not key.startswith("docs_")}
                     | {"preview": str((DRAFT / 'preview.html').relative_to(ROOT))}, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
