"""Rebuild the blog directory and previous/next links from docs/posts.json."""
from html import escape
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SITE_TITLE = "泛科研学习笔记"
RESERVED_SLUGS = {"assets", "posts", "index", "index-html", "guide", "tools"}
SITE_NAV = re.compile(
    r'<nav\b(?=[^>]*\bclass=["\'][^"\']*\bsite-nav\b)[^>]*>.*?</nav>',
    re.I | re.S,
)
POST_NAV = re.compile(
    r'<nav\b(?=[^>]*\bclass=["\'][^"\']*\bpost-nav\b)[^>]*>.*?</nav>',
    re.I | re.S,
)


def validate_slug(slug):
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError("Slug must use lowercase English letters, digits and single hyphens")
    if slug in RESERVED_SLUGS:
        raise ValueError("This slug is reserved: " + slug)
    return slug


def load_posts(root=ROOT):
    posts = json.loads((root / "docs/posts.json").read_text(encoding="utf-8"))
    if not isinstance(posts, list):
        raise ValueError("docs/posts.json must contain an array")
    seen = set()
    for post in posts:
        if not isinstance(post, dict):
            raise ValueError("Each catalog entry must be an object")
        slug = validate_slug(post.get("slug"))
        if slug in seen:
            raise ValueError("Duplicate article slug: " + slug)
        seen.add(slug)
        for key in ("title", "section", "description"):
            if not isinstance(post.get(key), str):
                raise ValueError(f"Article {slug} needs a text field: {key}")
        if not post["title"].strip() or not post["section"].strip():
            raise ValueError(f"Article {slug} needs a non-empty title and section")
    return posts


def render_post_list(posts):
    entries = []
    for post in posts:
        entries.append(
            '<li><p class="post-meta">' + escape(post["section"]) + '</p>'
            '<h2><a href="posts/' + post["slug"] + '/">' + escape(post["title"]) + '</a></h2>'
            '<p>' + escape(post["description"]) + '</p></li>'
        )
    return '<ol class="post-list">' + ''.join(entries) + '</ol>'


def navigation(posts, index):
    links = []
    if index:
        previous = posts[index - 1]
        links.append('<a rel="prev" href="../' + previous["slug"] + '/">上一篇：'
                     + escape(previous["title"]) + '</a>')
    links.append('<a href="../../">返回文章目录</a>')
    if index + 1 < len(posts):
        following = posts[index + 1]
        links.append('<a rel="next" href="../' + following["slug"] + '/">下一篇：'
                     + escape(following["title"]) + '</a>')
    return '<nav class="post-nav" aria-label="文章导航">' + ''.join(links) + '</nav>'


def with_navigation(html, nav):
    if POST_NAV.search(html):
        return POST_NAV.sub(lambda _: nav, html, count=1)
    for closing in ("</article>", "</body>"):
        position = html.lower().rfind(closing)
        if position >= 0:
            return html[:position] + nav + html[position:]
    raise ValueError("Article needs an article or body closing tag for navigation")


def with_site_branding(html, title):
    """Set the article browser title and its controlled link to the site home."""
    title_tag = '<title>' + escape(title + ' · ' + SITE_TITLE) + '</title>'
    html, count = re.subn(r'<title\b[^>]*>.*?</title>', lambda _: title_tag,
                         html, count=1, flags=re.I | re.S)
    if not count:
        html = re.sub(r'</head>', lambda _: title_tag + '</head>', html, count=1, flags=re.I)
    nav = '<nav class="site-nav" aria-label="网站导航"><a href="../../">← ' + escape(SITE_TITLE) + '</a></nav>'
    if SITE_NAV.search(html):
        return SITE_NAV.sub(lambda _: nav, html, count=1)
    html, count = re.subn(r'<article\b[^>]*>', lambda match: match.group(0) + nav,
                         html, count=1, flags=re.I)
    if not count:
        html = re.sub(r'<body\b[^>]*>', lambda match: match.group(0) + nav,
                      html, count=1, flags=re.I)
    return html


def rebuild_site(root=ROOT):
    root = Path(root)
    posts = load_posts(root)
    template = (root / "tools/home-template.html").read_text(encoding="utf-8")
    if template.count("{{POST_LIST}}") != 1:
        raise ValueError("Home template must contain exactly one {{POST_LIST}} placeholder")
    updates = []
    for index, post in enumerate(posts):
        page = root / "docs/posts" / post["slug"] / "index.html"
        html = with_site_branding(page.read_text(encoding="utf-8"), post["title"])
        updates.append((page, with_navigation(html, navigation(posts, index))))
    # Validate every article before writing any generated page.
    for page, html in updates:
        page.write_text(html, encoding="utf-8", newline="\n")
    (root / "docs/index.html").write_text(
        template.replace("{{POST_LIST}}", render_post_list(posts)), encoding="utf-8", newline="\n"
    )
    return len(posts)


if __name__ == "__main__":
    print(f"Rebuilt the directory and navigation for {rebuild_site()} articles.")
