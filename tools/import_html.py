"""Import one exported HTML article and its local assets into the public site."""
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import urlopen
import re
import shutil
import json

from blog import load_posts, rebuild_site, validate_slug

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = """<style id="share-reading-layout">
.page-body p:has(.katex) {
  overflow-x: auto;
  overflow-y: hidden;
  padding-block: .2em;
}
@media only screen and (max-width: 640px) {
  body { margin: 1.25rem 1.125rem; }
  .page-title { font-size: 2rem; overflow-wrap: anywhere; }
}
</style>"""


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("src", "href", "poster") and value:
                self.urls.add(value)


def fetch(url):
    with urlopen(url, timeout=30) as response:
        return response.read()


def append_reference(html, slug):
    """Add the MIT source only to its corresponding course-note articles."""
    scopes = {
        "introduction": "第 1 章 Introduction",
        "flow-models": "第 2.1 节 Flow Models",
        "diffusion-models": "第 2.2 节 Diffusion Models",
    }
    snippet = ROOT / "tools/reference.html"
    if slug not in scopes or not snippet.is_file() or re.search(r'\bid=["\']references["\']', html):
        return html
    reference = snippet.read_text(encoding="utf-8").strip()
    reference = re.sub(r'<p>相关内容：.*?</p>', '<p>相关内容：' + scopes[slug] + '。</p>', reference)
    for closing_tag in ("</article>", "</body>"):
        position = html.lower().rfind(closing_tag)
        if position != -1:
            return html[:position] + "\n" + reference + "\n" + html[position:]
    raise ValueError("Cannot place the reference: missing article/body closing tag")


def prepare_article(html, title):
    """Keep the export layout while adding the blog title and home link."""
    html = re.sub(r'<title\b[^>]*>.*?</title>', lambda _: '<title>' + escape(title) + '</title>',
                  html, count=1, flags=re.I | re.S)
    html = re.sub(
        r'(<h1\b(?=[^>]*\bclass=["\'][^"\']*\bpage-title\b)[^>]*>).*?(</h1>)',
        lambda match: match.group(1) + escape(title) + match.group(2),
        html, count=1, flags=re.I | re.S,
    )
    if not re.search(r'<meta\b[^>]*\bname\s*=\s*["\']viewport["\']', html, re.I):
        html = re.sub(r'<head\b[^>]*>', lambda match: match.group(0)
                      + '<meta name="viewport" content="width=device-width, initial-scale=1">',
                      html, count=1, flags=re.I)
    if 'id="share-reading-layout"' not in html:
        html = re.sub(r'</head>', LAYOUT + '</head>', html, count=1, flags=re.I)
    if '../../assets/blog.css' not in html:
        html = re.sub(r'</head>', '<link rel="stylesheet" href="../../assets/blog.css"></head>',
                      html, count=1, flags=re.I)
    if not re.search(r'<nav\b[^>]*\bclass=["\'][^"\']*\bsite-nav\b', html, re.I):
        nav = '<nav class="site-nav" aria-label="网站导航"><a href="../../">← 返回文章目录</a></nav>'
        html, count = re.subn(r'<article\b[^>]*>', lambda match: match.group(0) + nav,
                             html, count=1, flags=re.I)
        if not count:
            html = re.sub(r'<body\b[^>]*>', lambda match: match.group(0) + nav,
                          html, count=1, flags=re.I)
    return html


def local_assets(source, html):
    """Resolve referenced files within the export folder before changing the site."""
    parser = References()
    parser.feed(html)
    assets = []
    for url in sorted(parser.urls):
        parsed = urlsplit(url)
        if parsed.scheme in ("http", "https", "data", "mailto", "tel") or parsed.netloc:
            continue
        if not parsed.path:
            continue
        if parsed.scheme or parsed.path.startswith(("/", "\\")):
            raise ValueError("Expected a relative asset path: " + url)
        asset = (source.parent / unquote(parsed.path)).resolve()
        relative = asset.relative_to(source.parent)
        if not asset.is_file():
            raise ValueError("Missing referenced file: " + str(relative))
        assets.append((asset, relative))
    return assets


def localize_katex(html, output):
    pattern = r"https://cdn\.jsdelivr\.net/npm/katex@([0-9.]+)/dist/(katex(?:-swap)?\.min\.css)"
    match = re.search(pattern, html)
    if not match:
        return html
    url, version, name = match.group(0), match.group(1), match.group(2)
    asset_dir = output / "assets/katex"
    asset_dir.mkdir(parents=True, exist_ok=True)
    marker = asset_dir / "version.txt"
    css_path = asset_dir / name
    cached = marker.exists() and marker.read_text().strip() == version and css_path.exists()
    css_bytes = css_path.read_bytes() if cached else fetch(url)
    fonts = sorted(set(re.findall(
        r"url\((?:['\"])?(fonts/[^)'\"\s]+)", css_bytes.decode("utf-8")
    )))
    if not fonts:
        raise ValueError("No fonts found in the KaTeX stylesheet")
    for relative in fonts:
        (asset_dir / relative).resolve().relative_to(asset_dir.resolve())

    def save_font(relative):
        target = asset_dir / relative
        if not cached or not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(fetch(urljoin(url, relative)))

    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(save_font, fonts))
    license_file = asset_dir / "LICENSE"
    if not cached or not license_file.exists():
        license_file.write_bytes(fetch(
            f"https://cdn.jsdelivr.net/npm/katex@{version}/LICENSE"
        ))
    css_path.write_bytes(css_bytes)
    marker.write_text(version + "\n", encoding="utf-8")
    return html.replace(url, "assets/katex/" + name)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path, help="Exported .html file with assets alongside it")
    parser.add_argument("--slug", required=True, help="Article URL name, e.g. flow-models")
    parser.add_argument("--title", help="Article title; required for a new article")
    parser.add_argument("--section", help="Section label; required for a new article")
    parser.add_argument("--description", help="Short description for the article directory")
    args = parser.parse_args()
    try:
        slug = validate_slug(args.slug)
        posts = load_posts(ROOT)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    post = next((entry for entry in posts if entry["slug"] == slug), None)
    if post is None:
        if not args.title or not args.title.strip() or not args.section or not args.section.strip():
            parser.error("A new article requires --title and --section")
        post = {"slug": slug, "title": args.title, "section": args.section, "description": args.description or ""}
        posts.append(post)
    else:
        for key in ("title", "section", "description"):
            value = getattr(args, key)
            if value is not None:
                if key != "description" and not value.strip():
                    parser.error("--" + key + " cannot be empty")
                post[key] = value
    source = args.html.expanduser().resolve()
    if not source.is_file() or source.suffix.lower() not in (".html", ".htm"):
        parser.error("Provide an existing HTML file")
    html = source.read_text(encoding="utf-8-sig")
    if not re.search(r"</head>", html, re.I):
        parser.error("The export must contain an HTML head element")
    assets = local_assets(source, html)
    output = ROOT / "docs/posts" / slug
    output.mkdir(parents=True, exist_ok=True)
    for _, relative in assets:
        target = (output / relative).resolve()
        target.relative_to(output.resolve())
        if target == (output / "index.html").resolve():
            raise ValueError("A linked asset conflicts with the article's index.html")
    html = localize_katex(html, output)
    html = prepare_article(html, post["title"])
    html = append_reference(html, slug)
    for asset, relative in assets:
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if asset != target.resolve():
            shutil.copy2(asset, target)
    (output / "index.html").write_text(html, encoding="utf-8")
    (ROOT / "docs/posts.json").write_text(json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rebuild_site(ROOT)
    (ROOT / "docs/.nojekyll").touch()
    print(f"Imported {slug} and {len(assets)} referenced files into docs/posts/{slug}/")
    print("Rebuilt the article directory and previous/next links.")
    print("Preview locally, then commit and push to publish.")


if __name__ == "__main__":
    main()
