"""Render Chapter 7 locally; --publish prepares its GitHub Pages files."""

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
SLUG = "discrete-diffusion-models"
SOURCE = ROOT / "tools/content" / (SLUG + ".html")
DRAFT = ROOT / "drafts" / SLUG
SECTION_IDS = ["ctmc-models", "training-ctmc-models"]
MATH = re.compile(r"\\\[(.*?)\\\]|\\\((.*?)\\\)", re.S)
AUDIT = ROOT / ".runtime/discrete-diffusion-render-audit.json"


def docs_snapshot():
    return {
        str(path.relative_to(ROOT / "docs")): sha256(path.read_bytes()).hexdigest()
        for path in (ROOT / "docs").rglob("*") if path.is_file()
    }


def required_file(path):
    if not path.is_file():
        raise FileNotFoundError("Required Chapter 7 resource is missing: " + str(path))
    return path


def load_inputs():
    source = required_file(SOURCE).read_text(encoding="utf-8")
    post = json.loads(required_file(DRAFT / "post.json").read_text(encoding="utf-8"))
    metadata = json.loads(required_file(
        DRAFT / "images/lecture-original-figures.json").read_text(encoding="utf-8"))
    if post.get("slug") != SLUG or post.get("section") != "第 7 章":
        raise ValueError("Chapter 7 post.json must use the discrete-diffusion-models slug and 第 7 章 section")
    for key in ("title", "description"):
        if not isinstance(post.get(key), str) or not post[key].strip():
            raise ValueError("Chapter 7 post.json needs a nonempty " + key)
    sections = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', source)
    if [section_id for section_id, _ in sections] != SECTION_IDS:
        raise ValueError("Chapter 7 must retain these two ordered h2 IDs: " + ", ".join(SECTION_IDS))
    records = metadata.get("figures", [])
    if len(records) != 6:
        raise ValueError("Chapter 7 metadata must include all six original excerpts (Figures 17–20 and Algorithms 7–8)")
    paths = []
    for item in records:
        for key in ("filename", "image_size_px", "source_url"):
            if key not in item:
                raise ValueError("Original-figure metadata record is missing " + key)
        relative = "images/" + item["filename"]
        path = (DRAFT / relative).resolve()
        if not path.is_relative_to(DRAFT.resolve()):
            raise ValueError("Original figure must remain inside the Chapter 7 draft: " + relative)
        required_file(path)
        with Image.open(path) as raster:
            if list(raster.size) != item["image_size_px"]:
                raise ValueError("Original figure dimensions differ from metadata: " + relative)
        if item.get("output_sha256") and sha256(path.read_bytes()).hexdigest() != item["output_sha256"]:
            raise ValueError("Original figure hash differs from metadata: " + relative)
        paths.append(relative)
    article_paths = re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', source)
    if len(set(paths)) != 6 or sorted(article_paths) != sorted(paths):
        raise ValueError("Chapter 7 must embed each metadata image exactly once; article and image metadata differ")
    return source, post, metadata, sections


def render_math(source):
    version = required_file(ROOT / "docs/assets/katex/version.txt").read_text(encoding="utf-8").strip()
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
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path="C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", headless=True)
        try:
            page = browser.new_page()
            page.add_script_tag(path=str(script))
            if page.evaluate("katex.version") != version:
                raise ValueError("KaTeX script and stylesheet versions differ")
            rendered = page.evaluate(
                "items => items.map(i => katex.renderToString(i.tex, "
                "{displayMode:i.display,throwOnError:true,output:'htmlAndMathml'}))", expressions)
        finally:
            browser.close()
    iterator = iter(rendered)
    return MATH.sub(lambda _: next(iterator), source), len(expressions)


def image_dimensions(body):
    def sized(match):
        tag = match[0]
        relative = re.search(r'\bsrc="([^"]+)"', tag)
        if relative is None:
            raise ValueError("An article image has no src")
        image = (DRAFT / relative[1]).resolve()
        if not image.is_relative_to(DRAFT.resolve()):
            raise ValueError("Article image escapes the Chapter 7 draft: " + relative[1])
        with Image.open(required_file(image)) as raster:
            width, height = raster.size
        tag = re.sub(r'\s+(?:width|height)="[^"]*"', "", tag)
        return tag[:-1] + f' width="{width}" height="{height}">'
    return re.sub(r"<img\b[^>]*>", sized, body)


def table_of_contents(source):
    headings = list(re.finditer(r'<h([23]) id="([^"]+)">(.*?)</h\1>', source, re.S))
    groups = []
    for heading in headings:
        level, anchor, title = heading.groups()
        if level == "2" or not groups:
            groups.append([anchor, title, []])
        elif groups:
            groups[-1][2].append((anchor, title))
    items = []
    for anchor, title, children in groups:
        item = '<li><a href="#' + escape(anchor, quote=True) + '">' + title + '</a>'
        if children:
            item += '<ol>' + ''.join(
                '<li><a href="#' + escape(child, quote=True) + '">' + label + '</a></li>'
                for child, label in children) + '</ol>'
        items.append(item + '</li>')
    return ('<nav id="reading-toc" class="note-toc" aria-label="本篇目录">'
            '<p><strong>本篇目录</strong></p><ol>' + ''.join(items) + '</ol></nav>')


def article_html(source, body, post, local_preview):
    existing = required_file(ROOT / "docs/posts/guidance/index.html").read_text(encoding="utf-8")
    match = re.search(r"<head>(.*?)</head>", existing, re.S)
    if match is None:
        raise ValueError("The existing Guidance article has no head template")
    head = match[1]
    head = re.sub(r"<title>.*?</title>",
                  lambda _: '<title>' + escape(post["title"] + ' · ' + SITE_TITLE) + '</title>', head, count=1)
    description = '<meta name="description" content="' + escape(post["description"], quote=True) + '">'
    if re.search(r'<meta name="description" content="[^"]*">', head):
        head = re.sub(r'<meta name="description" content="[^"]*">', lambda _: description, head)
    else:
        head += description
    head = re.sub(r'<meta\b(?=[^>]*name=["\']robots["\'])[^>]*>', '', head, flags=re.I)
    if local_preview:
        head += '<meta name="robots" content="noindex, nofollow">'
    head += ('<style>'
             '.authored-note .katex{position:relative;}'
             '.authored-note .katex-display>.katex{min-width:max-content;}'
             '.authored-note .katex-display>.katex>.katex-html:has(>.tag){padding-inline:2.5em;}'
             '.note-toc>ol>li{margin-block:.8rem;}.note-toc ol ol{font-size:.94em;}'
             'h2[id],h3[id],details[id]{scroll-margin-top:1.5rem;}'
             '.reading-return{display:block;width:max-content;'
             'max-width:100%;margin:1rem 0 0 auto;padding:.4rem .75rem;'
             'background:rgba(255,255,255,.95);border:1px solid rgba(55,53,47,.2);'
             'border-radius:.35rem;font-size:.85rem;z-index:5;}'
             '</style>')
    reference = required_file(ROOT / "tools/reference.html").read_text(encoding="utf-8")
    reference = re.sub(
        r'<p>相关内容：.*?</p>',
        '<p>相关内容：第 7 章 Discrete Diffusion Models，7.1–7.2 节，第 54–66 页（含 Remark 40）。文中原图与算法截图附对应页码及来源链接。</p>',
        reference)
    label = ' · 本地预览' if local_preview else ''
    return ('<!doctype html><html lang="zh-CN"><head>' + head + '</head><body>'
            '<article id="top" class="page sans"><nav class="site-nav" aria-label="网站导航">'
            '<a href="../../index.html">← ' + escape(SITE_TITLE) + '</a></nav>'
            '<header><p class="post-meta">第 7 章 · 生成模型' + label + '</p>'
            '<h1 class="page-title">' + escape(post["title"]) + '</h1></header>'
            + table_of_contents(source) + '<div class="page-body authored-note">' + body + '</div>'
            + reference + '<nav class="post-nav" aria-label="文章导航">'
            '<a rel="prev" href="../guidance/index.html">上一篇：Guidance: How to Condition on a Prompt</a>'
            '<a href="../../index.html">返回文章目录</a></nav>'
            '<a class="reading-return" href="#reading-toc">↑ 返回目录</a>'
            '</article></body></html>')


def publish(html, post, metadata):
    posts = [item for item in load_posts(ROOT) if item["slug"] != SLUG]
    previous = next((i for i, item in enumerate(posts) if item["slug"] == "guidance"), None)
    if previous is None:
        raise ValueError("Cannot insert Chapter 7: the public catalog has no Guidance article")
    destination = ROOT / "docs/posts" / SLUG
    destination.mkdir(parents=True, exist_ok=True)
    for record in metadata["figures"]:
        relative = "images/" + record["filename"]
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(DRAFT / relative, target)
    (destination / "images/lecture-original-figures.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding="utf-8", newline="\n")
    (destination / "index.html").write_text(html, encoding="utf-8", newline="\n")
    posts.insert(previous + 1, post)
    (ROOT / "docs/posts.json").write_text(
        json.dumps(posts, ensure_ascii=False, indent=2) + '\n', encoding="utf-8", newline="\n")
    rebuild_site(ROOT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true", help="Prepare public docs, images, catalog and navigation; does not commit or push.")
    args = parser.parse_args()
    before = docs_snapshot()
    source, post, metadata, sections = load_inputs()
    body, count = render_math(source)
    body = image_dimensions(body)
    draft_html = article_html(source, body, post, local_preview=True)
    DRAFT.mkdir(parents=True, exist_ok=True)
    (DRAFT / "index.html").write_text(draft_html, encoding="utf-8", newline="\n")
    preview = draft_html.replace("url('../../assets/", "url('../../docs/assets/")
    preview = preview.replace('href="../../assets/', 'href="../../docs/assets/')
    preview = preview.replace('href="../../index.html"', 'href="../../docs/index.html"')
    preview = preview.replace('href="../guidance/index.html"', 'href="../../docs/posts/guidance/index.html"')
    (DRAFT / "preview.html").write_text(preview, encoding="utf-8", newline="\n")
    if args.publish:
        publish(article_html(source, body, post, local_preview=False), post, metadata)
    after = docs_snapshot()
    if not args.publish and after != before:
        raise RuntimeError("The default Chapter 7 draft render changed public docs")
    audit = {
        "docs_before": before, "docs_after": after,
        "public_docs_unchanged": before == after, "published": args.publish,
        "formulas": count, "sections": len(sections),
        "figures": len(re.findall(r'<figure\b', body)), "images": len(metadata["figures"]),
    }
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding="utf-8")
    print(json.dumps({key: value for key, value in audit.items() if not key.startswith("docs_")}
                     | {"preview": str((DRAFT / 'preview.html').relative_to(ROOT))}, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
