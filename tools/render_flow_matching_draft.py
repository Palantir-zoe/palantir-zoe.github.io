"""Render a local Flow Matching preview; publish reviewed content with --publish."""
import argparse
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
SOURCE = ROOT / "tools/content/flow-matching.html"
DRAFT = ROOT / "drafts/flow-matching"
MATH = re.compile(r"\\\[(.*?)\\\]|\\\((.*?)\\\)", re.S)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true",
                        help="Publish the reviewed article and images to docs/ and rebuild the catalog.")
    args = parser.parse_args()
    source = SOURCE.read_text(encoding="utf-8")
    post = json.loads((DRAFT / "post.json").read_text(encoding="utf-8"))
    if post["slug"] != "flow-matching":
        raise ValueError("This renderer only publishes the flow-matching article")
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
        image_path = DRAFT / relative
        if not image_path.is_file():
            raise FileNotFoundError("Missing article image: " + relative)
        with Image.open(image_path) as raster:
            width, height = raster.size
        return tag[:-1] + f' width="{width}" height="{height}">'

    body = re.sub(r'<img\b[^>]*>', sized_image, body)
    existing = (ROOT / "docs/posts/diffusion-models/index.html").read_text(encoding="utf-8")
    head = re.search(r"<head>(.*?)</head>", existing, re.S)[1]
    title = escape(post["title"] + " · " + SITE_TITLE)
    head = re.sub(r"<title>.*?</title>", "<title>" + title + "</title>", head, count=1)
    head = re.sub(r'<meta name="description" content="[^"]*">',
                  '<meta name="description" content="' + escape(post["description"], quote=True) + '">', head)
    if not args.publish:
        head += '<meta name="robots" content="noindex, nofollow">'

    sections = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', source)
    toc = '<nav class="note-toc" aria-label="本篇目录"><p><strong>本篇目录</strong></p><ol>' + ''.join(
        '<li><a href="#' + section_id + '">' + title + '</a></li>'
        for section_id, title in sections
    ) + '</ol></nav>'
    reference = (ROOT / "tools/reference.html").read_text(encoding="utf-8")
    reference = re.sub(r"<p>相关内容：.*?</p>",
                       "<p>相关内容：第 3 章 Flow Matching，3.1–3.3 节，第 14–24 页。Theorem 9、11、12，Summary 14，以及 Figure 4–7 与 Algorithm 3 均为原文截图；Summary 14 保留完整续页。</p>", reference)
    review_label = '' if args.publish else ' · 待审核'
    html = ('<!doctype html><html lang="zh-CN"><head>' + head + '</head><body>'
            '<article class="page sans"><nav class="site-nav" aria-label="网站导航"><a href="../../index.html">← ' + escape(SITE_TITLE) + '</a></nav>'
            '<header><p class="post-meta">第 3 章 · 生成模型' + review_label + '</p><h1 class="page-title">Flow Matching</h1></header>'
            + toc + '<div class="page-body authored-note">' + body + '</div>' + reference
            + '<nav class="post-nav" aria-label="文章导航"><a rel="prev" href="../diffusion-models/index.html">上一篇：Diffusion Models</a><a href="../../index.html">返回文章目录</a></nav>'
            '</article></body></html>')
    DRAFT.mkdir(parents=True, exist_ok=True)
    (DRAFT / "index.html").write_text(html, encoding="utf-8", newline="\n")
    # Local preview resolves the shared styles, fonts and published navigation.
    preview = html.replace("url('../../assets/", "url('../../docs/assets/")
    preview = preview.replace('href="../../assets/', 'href="../../docs/assets/')
    preview = preview.replace('href="../../index.html"', 'href="../../docs/index.html"')
    preview = preview.replace('href="../diffusion-models/index.html"', 'href="../../docs/posts/diffusion-models/index.html"')
    (DRAFT / "preview.html").write_text(preview, encoding="utf-8", newline="\n")
    if args.publish:
        posts = load_posts(ROOT)
        destination = ROOT / "docs/posts/flow-matching"
        destination.mkdir(parents=True, exist_ok=True)
        image_paths = set(re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', source))
        for relative in sorted(image_paths):
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(DRAFT / relative, target)
        metadata = json.loads((DRAFT / "images/lecture-original-figures.json").read_text(encoding="utf-8"))
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
    print(json.dumps({"formulas": len(rendered), "sections": len(sections),
                      "figures": len(re.findall(r'<figure\b', body)),
                      "preview": str((DRAFT / 'preview.html').relative_to(ROOT)),
                      "published": args.publish}, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
