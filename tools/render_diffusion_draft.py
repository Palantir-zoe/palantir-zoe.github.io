"""Render a local Diffusion Models preview; publish reviewed content with --publish."""
import argparse
from html import escape, unescape
from pathlib import Path
from urllib.request import urlopen
import json
import re
import shutil
import sys

from blog import SITE_TITLE, load_posts, rebuild_site
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/content/diffusion-models.html"
DRAFT = ROOT / "drafts/diffusion-models"
MATH = re.compile(r"\\\[(.*?)\\\]|\\\((.*?)\\\)", re.S)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true",
                        help="Publish the reviewed article and images to docs/ and rebuild the catalog.")
    args = parser.parse_args()
    source = SOURCE.read_text(encoding="utf-8")
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

    # Reuse the established article typography, with assets relative to a post URL.
    existing = (ROOT / "docs/posts/flow-models/index.html").read_text(encoding="utf-8")
    head = re.search(r"<head>(.*?)</head>", existing, re.S)[1]
    post = json.loads((DRAFT / "post.json").read_text(encoding="utf-8"))
    head = re.sub(r"<title>.*?</title>", "<title>Diffusion Models · " + escape(SITE_TITLE) + "</title>", head, count=1)
    head = re.sub(r'<meta name="description" content="[^"]*">',
                  '<meta name="description" content="' + escape(post["description"], quote=True) + '">', head)
    if not args.publish:
        head += '<meta name="robots" content="noindex, nofollow">'
    head += '''<style>
.authored-note blockquote {font-size:1rem; line-height:1.65;}
.note-toc {white-space:normal; margin:2rem 0;}
.note-toc li {margin:.35rem 0;}
.note-detail {margin:1.5rem 0; padding:.9rem 1rem; border:1px solid #e6e6e4; border-radius:4px; background:#fafaf9;}
.note-detail summary {cursor:pointer; font-size:.95rem; font-weight:500; line-height:1.6;}
.note-detail summary::marker {color:#787774;}
.note-detail[open] summary {margin-bottom:1.25rem;}
.note-detail h3 {font-size:1.05rem;}
.note-focus {border-left:3px solid #787774; padding:.85rem 1rem; background:#fafaf9; line-height:1.8;}
.lecture-figure {margin:1.75rem 0;}
.lecture-figure > a {display:block; cursor:zoom-in;}
.lecture-figure img {display:block; width:100%; height:auto;}
.lecture-figure figcaption {margin-top:.7rem; color:#787774; font-size:.85rem; line-height:1.6;}
@media print {.note-detail {background:none;}}
</style>'''

    sections = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', source)
    toc = '<nav class="note-toc" aria-label="本篇目录"><p><strong>本篇目录</strong></p><ol>' + ''.join(
        '<li><a href="#' + section_id + '">' + title + '</a></li>'
        for section_id, title in sections
    ) + '</ol></nav>'
    reference = (ROOT / "tools/reference.html").read_text(encoding="utf-8")
    reference = re.sub(r"<p>相关内容：.*?</p>", "<p>相关内容：第 2.2 节 Diffusion Models，第 10–13 页。</p>", reference)
    reference = reference.replace('</section>', '<p>随机积分与解的定义补充：<a href="https://people.maths.ox.ac.uk/fehrman/SDENotes.pdf#page=88" target="_blank" rel="noopener noreferrer">Benjamin Fehrman, Stochastic Differential Equations，第 7 节</a>。</p></section>')
    review_label = '' if args.publish else ' · 待审核'
    html = ('<!doctype html><html lang="zh-CN"><head>' + head + '</head><body>'
            '<article class="page sans"><nav class="site-nav" aria-label="网站导航"><a href="../../index.html">← ' + escape(SITE_TITLE) + '</a></nav>'
            '<header><p class="post-meta">第 2.2 节 · 生成模型' + review_label + '</p><h1 class="page-title">Diffusion Models</h1></header>'
            + toc + '<div class="page-body authored-note">' + body + '</div>' + reference
            + '<nav class="post-nav" aria-label="文章导航"><a rel="prev" href="../flow-models/index.html">上一篇：Flow Models</a><a href="../../index.html">返回文章目录</a></nav>'
            '</article></body></html>')
    DRAFT.mkdir(parents=True, exist_ok=True)
    (DRAFT / "index.html").write_text(html, encoding="utf-8", newline="\n")
    # The preview is directly openable as a local file and still remains outside docs/.
    preview = html.replace("url('../../assets/", "url('../../docs/assets/")
    preview = preview.replace('href="../../assets/', 'href="../../docs/assets/')
    preview = preview.replace('href="../../index.html"', 'href="../../docs/index.html"')
    preview = preview.replace('href="../flow-models/index.html"', 'href="../../docs/posts/flow-models/index.html"')
    (DRAFT / "preview.html").write_text(preview, encoding="utf-8", newline="\n")
    if args.publish:
        if post["slug"] != "diffusion-models":
            raise ValueError("This renderer only publishes the diffusion-models article")
        images = DRAFT / "images"
        for relative in re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', source):
            if not (DRAFT / relative).is_file():
                raise FileNotFoundError("Missing article image: " + relative)
        posts = load_posts(ROOT)
        destination = ROOT / "docs/posts/diffusion-models"
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copytree(images, destination / "images", dirs_exist_ok=True)
        (destination / "index.html").write_text(html, encoding="utf-8", newline="\n")
        existing_index = next((i for i, item in enumerate(posts) if item["slug"] == post["slug"]), None)
        if existing_index is None:
            posts.append(post)
        else:
            posts[existing_index] = post
        (ROOT / "docs/posts.json").write_text(json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        rebuild_site(ROOT)
    print(json.dumps({"formulas": len(rendered), "sections": len(sections),
                      "draft": str((DRAFT / 'index.html').relative_to(ROOT)),
                      "preview": str((DRAFT / 'preview.html').relative_to(ROOT)),
                      "published": args.publish}, ensure_ascii=True))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
