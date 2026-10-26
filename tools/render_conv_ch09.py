"""Build the concise Chinese 09_conv reading note for GitHub Pages."""

from __future__ import annotations

from html import escape, unescape
from pathlib import Path
import json
import re
import subprocess

from blog import SITE_TITLE, rebuild_site


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/content/conv-ch09.html"
POST = json.loads((ROOT / "tools/content/conv-ch09-post.json").read_text(encoding="utf-8"))
DEST = ROOT / "docs/posts/conv-ch09/index.html"
NODE = ROOT / ".runtime/qa-venv/Lib/site-packages/playwright/driver/node.exe"
MATH = re.compile(r"\\\[([\s\S]*?)\\\]|\\\(([\s\S]*?)\\\)")
IMAGES = re.compile(r'(<img\s+src="([^"]+)"[^>]*>)')

STYLE = r"""
html{scroll-behavior:smooth;scroll-padding-top:1rem}
.authored-note{white-space:normal;line-height:1.72;font-size:1.02rem;color:#273a33}
.authored-note p{margin:.7rem 0;line-height:1.72}
.authored-note h2{margin:3.2rem 0 1rem;padding-bottom:.42rem;border-bottom:1px solid #dfe9e3;font-size:1.55rem;scroll-margin-top:1rem}
.authored-note h3{margin:1rem 0 .5rem;font-size:1.12rem;line-height:1.42}
.authored-note ol,.authored-note ul{padding-left:1.35rem;margin:.6rem 0}.authored-note li{margin:.42rem 0}
.authored-note .katex-display{overflow-x:auto;overflow-y:hidden;padding:.2rem 0 .4rem;margin:1rem 0}
.authored-note .katex{font-size:1.03em}
.authored-note pre{white-space:pre;overflow:auto;padding:1rem 1.15rem;background:#21342f;color:#f4faf6;border-radius:.5rem;font-size:.86rem;line-height:1.6}
.authored-note pre code{white-space:pre;background:none;color:inherit}
.lead{font-size:1.11rem;color:#315442}
.review-banner{background:#eff7f2;border:1px solid #bfdcc8;border-radius:.6rem;padding:.75rem 1rem;margin:.4rem 0 1.3rem}
.review-banner span{display:inline-block;background:#276c4c;color:white;font-size:.78rem;font-weight:700;padding:.12rem .58rem;border-radius:99px}
.review-banner p{font-size:.87rem;color:#486352;margin:.48rem 0 0}
.note-focus{border-left:4px solid #4c9b74;background:#eef7f1;border-radius:0 .35rem .35rem 0;padding:.8rem 1rem;margin:1.05rem 0}
.note-focus small{color:#566d61;font-size:.8rem}
.slide-card{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:1.1rem;align-items:start;margin:1.45rem 0;padding:1rem;border:1px solid #dae7de;background:#fbfdfb;border-radius:.55rem}
.slide-card>figure{margin:0;min-width:0}.slide-card>div{min-width:0}.slide-card figure img{display:block;width:100%;height:auto;border:1px solid #e1e5e0;background:#fff;border-radius:.25rem}
.slide-card figure a{display:block}.slide-card figure a:hover img,.slide-card figure a:focus-visible img{outline:2px solid #70a486;outline-offset:2px}
.slide-card figcaption{margin:.35rem 0 0;font-size:.78rem;line-height:1.45;color:#617568;opacity:1}
.slide-card h3:first-child{margin-top:0}.slide-card.pair{grid-template-columns:repeat(2,minmax(0,1fr))}.slide-card.pair>div{grid-column:1/-1}
.slide-card.wide{grid-template-columns:minmax(0,.78fr) minmax(0,1.22fr)}
.table-scroll{overflow-x:auto;max-width:100%;margin:.8rem 0}.authored-note table{width:100%;border-collapse:collapse;font-size:.9rem;line-height:1.5}.authored-note th,.authored-note td{border:1px solid #d9e4dc;padding:.58rem .65rem;vertical-align:top;text-align:left}.authored-note th{background:#eef5ef;color:#285a3e}.authored-note tr:nth-child(even) td{background:#f8fbf8}
.muted,.source-note{font-size:.88rem;color:#5e6e62}.source-note{border-top:1px solid #dfe9e3;padding-top:.8rem}
.note-toc{background:#f7faf8;border:1px solid #dde8e0;border-radius:.5rem;padding:.8rem 1.15rem;margin:1rem 0 1.6rem;white-space:normal}.note-toc p{margin:.2rem 0}.note-toc ol{columns:2;column-gap:2rem;padding-left:0;list-style:none}.note-toc li{break-inside:avoid;margin:.28rem 0;font-size:.88rem}.note-toc a{color:#315f46;text-decoration:none}.note-toc a:hover{text-decoration:underline}
@media(max-width:700px){.authored-note{font-size:.98rem}.authored-note h2{font-size:1.33rem}.slide-card,.slide-card.wide,.slide-card.pair{display:block;padding:.75rem}.slide-card>figure{margin:0 0 .9rem}.slide-card.pair>figure+figure{margin-top:.8rem}.note-toc ol{columns:1}.authored-note table{font-size:.82rem}}
@media print{.slide-card,.note-focus,.authored-note table{break-inside:avoid}.note-toc{break-after:page}}
"""


def compile_math(source: str) -> tuple[str, int]:
    matches = list(MATH.finditer(source))
    payload = [
        {"tex": unescape(m.group(1) if m.group(1) is not None else m.group(2)).strip(),
         "display": m.group(1) is not None}
        for m in matches
    ]
    result = subprocess.run(
        [str(NODE), str(ROOT / "tools/render_prml_math.cjs")],
        input=json.dumps(payload, ensure_ascii=False), text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", check=True,
    )
    rendered = iter(json.loads(result.stdout))
    return MATH.sub(lambda _: next(rendered), source), len(payload)


def main() -> None:
    if not NODE.is_file():
        raise FileNotFoundError("Local Node runtime for static KaTeX rendering is unavailable")
    raw = SOURCE.read_text(encoding="utf-8")
    headings = re.findall(r'<h2\s+id="([^"]+)"\s*>(.*?)</h2>', raw, flags=re.S)
    toc = '<nav class="note-toc" aria-label="本篇目录"><p><strong>阅读目录</strong></p><ol>' + ''.join(
        f'<li><a href="#{escape(ident, quote=True)}">{title}</a></li>'
        for ident, title in headings
    ) + '</ol></nav>'
    body, formulas = compile_math(raw)
    body = IMAGES.sub(lambda m: f'<a href="{escape(m.group(2), quote=True)}" target="_blank" rel="noopener" title="打开讲义图示大图">{m.group(1)}</a>', body)
    sample = (ROOT / "docs/posts/prml-mixture-models-em/index.html").read_text(encoding="utf-8")
    head = re.search(r"<head>(.*?)</head>", sample, re.S).group(1)
    head = re.sub(r"<title>.*?</title>", f"<title>{escape(POST['title'])} · {escape(SITE_TITLE)}</title>", head, count=1)
    head = re.sub(r'<meta\s+name="description"[^>]*>', "", head)
    head += f'<meta name="description" content="{escape(POST["description"], quote=True)}">'
    if 'name="robots"' not in head:
        head += '<meta name="robots" content="noindex, nofollow">'
    head += f"<style>{STYLE}</style>"
    html = (
        '<!doctype html><html lang="zh-CN"><head>' + head + '</head><body>'
        '<article class="page sans"><nav class="site-nav" aria-label="网站导航">'
        '<a href="../../">← ' + escape(SITE_TITLE) + '</a></nav>'
        '<header><p class="post-meta">' + escape(POST["section"]) + '</p>'
        '<h1 class="page-title">' + escape(POST["title"]) + '</h1></header>'
        + toc + '<div class="page-body authored-note">' + body + '</div>'
        '<nav class="post-nav" aria-label="文章导航"><a href="../../">返回文章目录</a></nav>'
        '</article></body></html>'
    )
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(html, encoding="utf-8", newline="\n")
    catalog = ROOT / "docs/posts.json"
    posts = json.loads(catalog.read_text(encoding="utf-8"))
    posts = [entry for entry in posts if entry["slug"] != POST["slug"]] + [POST]
    catalog.write_text(json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    rebuild_site(ROOT)
    print(json.dumps({"page": str(DEST.relative_to(ROOT)), "figures": len(IMAGES.findall(raw)),
                      "formulas": formulas, "sections": len(headings)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
