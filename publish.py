#!/usr/bin/env python3
"""
Tiny static article publisher.

Use from the terminal:
  python publish.py new "Article title" --summary "Short summary"
  python publish.py build

Use from Jupyter:
  from publish import publish_article
  publish_article("Title", "# Title\n\nYour article body...")
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import shutil
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ARTICLES_DIR = ROOT / "articles"
PAGES_DIR = ROOT / "pages"
PUBLIC_DIR = ROOT / "public"
DOCS_DIR = ROOT / "docs"


SITE_TITLE = "Research Notes"
SITE_DESCRIPTION = "Curious by nature. Building with purpose. Learning always."

NAV_ITEMS = [
    ("Home", "index.html"),
    ("Articles", "articles.html"),
    ("About", "about.html"),
    ("Project", "project.html"),
]


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title.strip().lower()).strip("-")
    return slug or "untitled"


def parse_frontmatter(markdown: str) -> tuple[dict[str, str], str]:
    if not markdown.startswith("---\n"):
        return {}, markdown

    end = markdown.find("\n---\n", 4)
    if end == -1:
        return {}, markdown

    raw_meta = markdown[4:end]
    body = markdown[end + 5 :]
    meta: dict[str, str] = {}
    for line in raw_meta.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip().strip('"')
    return meta, body


def inline_markdown(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        r'<a href="\2">\1</a>',
        escaped,
    )
    escaped = re.sub(
        r"\[([^\]]+)\]\(([a-zA-Z0-9._/-]+\.html)\)",
        r'<a href="\2">\1</a>',
        escaped,
    )
    return escaped


def markdown_to_html(markdown: str) -> str:
    blocks: list[str] = []
    paragraph: list[str] = []
    code_lines: list[str] = []
    in_code = False
    list_items: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
            paragraph.clear()

    def flush_list() -> None:
        if list_items:
            items = "".join(f"<li>{inline_markdown(item)}</li>" for item in list_items)
            blocks.append(f"<ul>{items}</ul>")
            list_items.clear()

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()

        if line.startswith("```"):
            if in_code:
                blocks.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
                code_lines.clear()
                in_code = False
            else:
                flush_paragraph()
                flush_list()
                in_code = True
            continue

        if in_code:
            code_lines.append(raw_line)
            continue

        if not line:
            flush_paragraph()
            flush_list()
            continue

        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            blocks.append(f"<h{level}>{inline_markdown(heading.group(2))}</h{level}>")
            continue

        if line.startswith("- "):
            flush_paragraph()
            list_items.append(line[2:])
            continue

        if line.startswith("=> "):
            flush_paragraph()
            flush_list()
            blocks.append(f'<p class="page-action">{inline_markdown(line[3:])}</p>')
            continue

        paragraph.append(line)

    flush_paragraph()
    flush_list()
    if in_code:
        blocks.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")

    return "\n".join(blocks)


def remove_leading_title(markdown: str) -> str:
    lines = markdown.lstrip().splitlines()
    if lines and lines[0].startswith("# "):
        return "\n".join(lines[1:]).lstrip()
    return markdown


def nav_html() -> str:
    links = "\n".join(
        f'      <a href="{href}">{html.escape(label)}</a>' for label, href in NAV_ITEMS
    )
    return f"""<header class="site-header">
    <a class="brand" href="index.html">{html.escape(SITE_TITLE)}</a>
    <nav class="site-nav" aria-label="Primary navigation">
{links}
    </nav>
  </header>"""


def article_nav_html(
    previous_article: dict[str, str] | None,
    next_article: dict[str, str] | None,
) -> str:
    links = ['<a href="articles.html">See all articles</a>']
    if previous_article:
        links.append(
            f'<a href="{html.escape(previous_article["slug"])}.html">See previous article</a>'
        )
    if next_article:
        links.append(
            f'<a href="{html.escape(next_article["slug"])}.html">See next article</a>'
        )
    return "\n".join(links)


def article_template(
    title: str,
    date: str,
    summary: str,
    body_html: str,
    previous_article: dict[str, str] | None = None,
    next_article: dict[str, str] | None = None,
) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} | {html.escape(SITE_TITLE)}</title>
  <meta name="description" content="{html.escape(summary)}">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  {nav_html()}
  <main class="article">
    <p class="date">{html.escape(date)}</p>
    <h1>{html.escape(title)}</h1>
    <p class="summary">{html.escape(summary)}</p>
    <div class="article-body">
      {body_html}
    </div>
    <nav class="article-links" aria-label="Article navigation">
      {article_nav_html(previous_article, next_article)}
    </nav>
  </main>
</body>
</html>
"""


def page_template(title: str, summary: str, body_html: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} | {html.escape(SITE_TITLE)}</title>
  <meta name="description" content="{html.escape(summary)}">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  {nav_html()}
  <main class="article">
    <p class="kicker">Page</p>
    <h1>{html.escape(title)}</h1>
    <p class="summary">{html.escape(summary)}</p>
    <div class="article-body">
      {body_html}
    </div>
  </main>
</body>
</html>
"""


def articles_template(articles: list[dict[str, str]]) -> str:
    article_cards = "\n".join(
        f"""<article class="post">
      <p class="date">{html.escape(article["date"])}</p>
      <h2><a href="{html.escape(article["slug"])}.html">{html.escape(article["title"])}</a></h2>
      <p>{html.escape(article["summary"])}</p>
    </article>"""
        for article in articles
    )

    if not article_cards:
        article_cards = '<p class="empty">No articles yet.</p>'

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Articles | {html.escape(SITE_TITLE)}</title>
  <meta name="description" content="All published research notes and articles.">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  {nav_html()}
  <main class="posts page-list">
    <div class="section-title">
      <p class="kicker">Archive</p>
      <h1>Articles</h1>
    </div>
    {article_cards}
  </main>
</body>
</html>
"""


def index_template(articles: list[dict[str, str]]) -> str:
    latest_articles = articles[:5]
    article_cards = "\n".join(
        f"""<article class="post">
      <p class="date">{html.escape(article["date"])}</p>
      <h2><a href="{html.escape(article["slug"])}.html">{html.escape(article["title"])}</a></h2>
      <p>{html.escape(article["summary"])}</p>
    </article>"""
        for article in latest_articles
    )

    if not article_cards:
        article_cards = '<p class="empty">No articles yet.</p>'

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(SITE_TITLE)}</title>
  <meta name="description" content="{html.escape(SITE_DESCRIPTION)}">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  {nav_html()}
  <header class="hero">
    <div class="hero-copy">
      <p class="kicker">Open research archive</p>
      <h1>{html.escape(SITE_TITLE)}</h1>
      <p>{html.escape(SITE_DESCRIPTION)}</p>
    </div>
  </header>
  <main class="posts">
    <div class="section-title">
      <div>
        <p class="kicker">Latest notes</p>
        <h2>Field notes, essays, and working drafts</h2>
      </div>
      <div class="section-actions">
        <a href="articles.html">See all</a>
        <a href="project.html">Check out my projects</a>
      </div>
    </div>
    {article_cards}
  </main>
</body>
</html>
"""


def stylesheet() -> str:
    return """* {
  box-sizing: border-box;
}

:root {
  --paper: #f3ead8;
  --ink: #2a271f;
  --soft-ink: #6e6b59;
  --leaf: #778261;
  --moss: #4f6446;
  --wood: #7b5534;
  --line: rgba(90, 78, 54, 0.22);
}

body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.65;
}

body::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 18% 16%, rgba(255, 250, 236, 0.88), transparent 34%),
    linear-gradient(90deg, rgba(255, 252, 241, 0.74), rgba(255, 252, 241, 0.24));
  mix-blend-mode: soft-light;
}

a {
  color: inherit;
}

.site-header,
.posts,
.article {
  width: min(920px, calc(100% - 32px));
  margin: 0 auto;
}

.site-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 22px 0;
}

.site-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 18px;
  color: var(--soft-ink);
  font-size: 0.94rem;
}

.site-nav a {
  text-decoration: none;
}

.site-nav a:hover {
  color: var(--moss);
  text-decoration: underline;
}

.hero {
  min-height: 72vh;
  display: flex;
  align-items: flex-end;
  padding: 48px max(32px, calc((100vw - 1100px) / 2)) 56px;
  background:
    linear-gradient(90deg, rgba(246, 235, 213, 0.96) 0%, rgba(246, 235, 213, 0.86) 34%, rgba(246, 235, 213, 0.08) 64%),
    url("assets/study.png") right center / cover no-repeat;
  border-bottom: 1px solid var(--line);
  position: relative;
}

.hero::after {
  content: "";
  position: absolute;
  left: max(32px, calc((100vw - 1100px) / 2));
  bottom: 36px;
  width: min(430px, calc(100% - 64px));
  height: 1px;
  background: linear-gradient(90deg, var(--line), transparent);
}

.hero-copy {
  width: min(580px, 100%);
  padding-bottom: 32px;
}

.hero h1,
.article h1 {
  margin: 0;
  font-family: ui-serif, Georgia, "Times New Roman", serif;
  font-size: clamp(2.3rem, 7vw, 5rem);
  line-height: 1;
  letter-spacing: 0;
}

.hero p {
  max-width: 660px;
  font-size: 1.15rem;
  color: var(--soft-ink);
}

.kicker,
.date {
  color: var(--leaf);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.posts {
  display: grid;
  gap: 0;
  padding: 36px 0 72px;
}

.page-list {
  padding-top: 48px;
}

.section-title {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 4px;
  padding: 6px 0 12px;
  border-bottom: 1px solid var(--line);
}

.section-title h2 {
  margin: 0;
  color: var(--wood);
  font-family: ui-serif, Georgia, "Times New Roman", serif;
  font-size: clamp(1.45rem, 4vw, 2.2rem);
  line-height: 1.15;
}

.section-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 16px;
  justify-content: flex-end;
  font-size: 0.94rem;
  font-weight: 700;
}

.section-actions a {
  color: var(--moss);
  text-decoration: none;
}

.section-actions a:hover {
  text-decoration: underline;
}

.post {
  padding: 28px 0;
  border-bottom: 1px solid var(--line);
}

.post h2 {
  margin: 0 0 8px;
  font-size: 1.45rem;
  line-height: 1.2;
}

.post h2 a {
  text-decoration: none;
}

.post h2 a:hover {
  text-decoration: underline;
}

.post p {
  max-width: 720px;
  margin: 0;
  color: var(--soft-ink);
}

.brand {
  color: var(--moss);
  font-weight: 800;
  text-decoration: none;
}

.article {
  max-width: 760px;
  padding: 48px 0 88px;
}

.article .summary {
  color: var(--soft-ink);
  font-size: 1.2rem;
  margin: 18px 0 42px;
}

.article-body h2,
.article-body h3 {
  line-height: 1.2;
  margin-top: 38px;
}

.article-body p,
.article-body li {
  font-size: 1.04rem;
}

.article-body pre {
  background: #2c3327;
  color: #f7f0df;
  overflow-x: auto;
  padding: 18px;
  border-radius: 8px;
}

.article-body code {
  font-size: 0.95em;
}

.page-action {
  display: flex;
  justify-content: flex-end;
  margin-top: 42px;
}

.page-action a {
  color: var(--moss);
  font-weight: 800;
  text-decoration: none;
}

.page-action a:hover {
  text-decoration: underline;
}

.article-links {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  justify-content: flex-end;
  margin-top: 54px;
  padding-top: 22px;
  border-top: 1px solid var(--line);
}

.article-links a {
  color: var(--moss);
  font-weight: 800;
  text-decoration: none;
}

.article-links a:hover {
  text-decoration: underline;
}

.empty {
  color: var(--leaf);
}

@media (max-width: 720px) {
  .site-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .hero {
    min-height: 74vh;
    padding: 36px 24px 42px;
    background:
      linear-gradient(180deg, rgba(246, 235, 213, 0.92) 0%, rgba(246, 235, 213, 0.72) 42%, rgba(246, 235, 213, 0.18) 100%),
      url("assets/study.png") 62% center / cover no-repeat;
  }

  .section-title {
    align-items: start;
    flex-direction: column;
  }

  .section-actions {
    justify-content: flex-start;
  }

  .hero-copy {
    padding-bottom: 18px;
  }

  .hero h1,
  .article h1 {
    font-size: 3rem;
  }
}
"""


def read_articles() -> list[dict[str, str]]:
    articles = []
    for path in sorted(ARTICLES_DIR.glob("*.md")):
        markdown = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(markdown)
        title = meta.get("title", path.stem.replace("-", " ").title())
        date = meta.get("date", "undated")
        summary = meta.get("summary", "")
        slug = meta.get("slug", path.stem)
        articles.append(
            {
                "path": str(path),
                "slug": slug,
                "title": title,
                "date": date,
                "summary": summary,
                "body": body,
            }
        )
    return sorted(articles, key=lambda item: item["date"], reverse=True)


def read_pages() -> list[dict[str, str]]:
    pages = []
    for path in sorted(PAGES_DIR.glob("*.md")):
        markdown = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(markdown)
        title = meta.get("title", path.stem.replace("-", " ").title())
        summary = meta.get("summary", "")
        slug = meta.get("slug", path.stem)
        pages.append(
            {
                "path": str(path),
                "slug": slug,
                "title": title,
                "summary": summary,
                "body": body,
            }
        )
    return pages


def sync_docs() -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    for path in DOCS_DIR.glob("*.html"):
        path.unlink()
    for path in PUBLIC_DIR.glob("*.html"):
        shutil.copy2(path, DOCS_DIR / path.name)
    shutil.copy2(PUBLIC_DIR / "style.css", DOCS_DIR / "style.css")
    assets_dir = PUBLIC_DIR / "assets"
    if assets_dir.exists():
        shutil.copytree(assets_dir, DOCS_DIR / "assets", dirs_exist_ok=True)


def build_site() -> None:
    PUBLIC_DIR.mkdir(exist_ok=True)
    for path in PUBLIC_DIR.glob("*.html"):
        path.unlink()
    articles = read_articles()
    for index, article in enumerate(articles):
        body_html = markdown_to_html(remove_leading_title(article["body"]))
        previous_article = articles[index + 1] if index + 1 < len(articles) else None
        next_article = articles[index - 1] if index > 0 else None
        output = article_template(
            article["title"],
            article["date"],
            article["summary"],
            body_html,
            previous_article,
            next_article,
        )
        (PUBLIC_DIR / f"{article['slug']}.html").write_text(output, encoding="utf-8")

    for page in read_pages():
        body_html = markdown_to_html(remove_leading_title(page["body"]))
        output = page_template(page["title"], page["summary"], body_html)
        (PUBLIC_DIR / f"{page['slug']}.html").write_text(output, encoding="utf-8")

    (PUBLIC_DIR / "index.html").write_text(index_template(articles), encoding="utf-8")
    (PUBLIC_DIR / "articles.html").write_text(articles_template(articles), encoding="utf-8")
    (PUBLIC_DIR / "style.css").write_text(stylesheet(), encoding="utf-8")
    sync_docs()


def publish_article(
    title: str,
    body: str,
    *,
    summary: str = "",
    date: str | None = None,
    slug: str | None = None,
) -> Path:
    ARTICLES_DIR.mkdir(exist_ok=True)
    date = date or dt.date.today().isoformat()
    slug = slug or slugify(title)
    path = ARTICLES_DIR / f"{slug}.md"
    markdown = textwrap.dedent(
        f"""\
---
title: "{title}"
date: {date}
summary: "{summary}"
slug: {slug}
---

{body.strip()}
"""
    )
    path.write_text(markdown, encoding="utf-8")
    build_site()
    return path


def new_article(title: str, summary: str = "") -> Path:
    body = f"""# {title}

Write your article here. You can use:

- headings
- bullet lists
- `inline code`
- fenced code blocks
- links like [OpenAI](https://openai.com)
"""
    return publish_article(title, body, summary=summary)


def new_page(title: str, summary: str = "") -> Path:
    PAGES_DIR.mkdir(exist_ok=True)
    slug = slugify(title)
    path = PAGES_DIR / f"{slug}.md"
    body = f"""# {title}

Write this page here.
"""
    markdown = textwrap.dedent(
        f"""\
---
title: "{title}"
summary: "{summary}"
slug: {slug}
---

{body.strip()}
"""
    )
    path.write_text(markdown, encoding="utf-8")
    build_site()
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish Markdown articles as a static site.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_parser = subparsers.add_parser("new", help="Create a draft article and rebuild the site.")
    new_parser.add_argument("title")
    new_parser.add_argument("--summary", default="")

    page_parser = subparsers.add_parser("page", help="Create a standalone page and rebuild the site.")
    page_parser.add_argument("title")
    page_parser.add_argument("--summary", default="")

    build_parser = subparsers.add_parser("build", help="Rebuild public/ from articles/.")
    build_parser.set_defaults(command="build")

    args = parser.parse_args()
    if args.command == "new":
        path = new_article(args.title, args.summary)
        print(f"Created {path}")
        print(f"Preview: {PUBLIC_DIR / 'index.html'}")
    elif args.command == "page":
        path = new_page(args.title, args.summary)
        print(f"Created {path}")
        print(f"Preview: {PUBLIC_DIR / 'index.html'}")
    elif args.command == "build":
        build_site()
        print(f"Built {PUBLIC_DIR}")
        print(f"Synced {DOCS_DIR}")


if __name__ == "__main__":
    main()
