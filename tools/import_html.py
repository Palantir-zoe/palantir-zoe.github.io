"""Import one exported HTML article and its local assets into the public site."""
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import urlopen
import re
import shutil

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


def append_reference(html):
    """Keep the article reference when importing a fresh export."""
    snippet = ROOT / "tools/reference.html"
    if not snippet.is_file() or re.search(r'\bid=["\']references["\']', html):
        return html
    reference = snippet.read_text(encoding="utf-8").strip()
    for closing_tag in ("</article>", "</body>"):
        position = html.lower().rfind(closing_tag)
        if position != -1:
            return html[:position] + "\n" + reference + "\n" + html[position:]
    raise ValueError("Cannot place the reference: missing article/body closing tag")


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
    args = parser.parse_args()
    source = args.html.expanduser().resolve()
    if not source.is_file() or source.suffix.lower() not in (".html", ".htm"):
        parser.error("Provide an existing HTML file")
    html = source.read_text(encoding="utf-8-sig")
    if not re.search(r"</head>", html, re.I):
        parser.error("The export must contain an HTML head element")
    assets = local_assets(source, html)
    output = ROOT / "docs"
    output.mkdir(parents=True, exist_ok=True)
    for _, relative in assets:
        target = (output / relative).resolve()
        target.relative_to(output.resolve())
        if target == (output / "index.html").resolve():
            raise ValueError("A linked asset conflicts with the homepage")
    html = localize_katex(html, output)
    if not re.search(r'<meta\b[^>]*\bname\s*=\s*["\']viewport["\']', html, re.I):
        html = re.sub(
            r"<head\b[^>]*>",
            lambda m: m.group(0) + '<meta name="viewport" content="width=device-width, initial-scale=1">',
            html, count=1, flags=re.I,
        )
    if 'id="share-reading-layout"' not in html:
        html = re.sub(r"</head>", LAYOUT + "</head>", html, count=1, flags=re.I)
    html = append_reference(html)
    for asset, relative in assets:
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if asset != target.resolve():
            shutil.copy2(asset, target)
    (output / "index.html").write_text(html, encoding="utf-8")
    (output / ".nojekyll").touch()
    print(f"Imported homepage and {len(assets)} referenced files into docs/")
    print("Preview locally, then commit and push to publish.")


if __name__ == "__main__":
    main()
