"""Build the MaheshKumarSE site into ./docs for GitHub Pages.

Usage: python3 tools/build.py
Reads posts/*.md and pages/*.md (YAML front matter + Markdown).
"""
import datetime as dt
import html
import json
import math
import re
import shutil
from email.utils import format_datetime
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"
SITE = {
    "name": "MaheshKumarSE",
    "url": "https://maheshkumarse.com",
    "author": "Mahesh",
        "description": "Practical notes on Intune, ConfigMgr, Windows 11, Cloud PC, AVD, Defender, Purview and Microsoft 365. What is new, what is broken, how to fix it and how to roll it out.",
}
TOPICS = [
    ("Intune", "intune", "Microsoft Intune policies, apps, enrolment and reporting."),
    ("ConfigMgr", "configmgr", "Configuration Manager releases, hotfixes, upgrades and comanagement."),
    ("Windows 11", "windows-11", "Windows 11 updates, known issues, builds and servicing."),
    ("macOS", "macos", "Managing Macs with Intune."),
    ("iOS", "ios", "Managing iPhone and iPad with Intune."),
    ("Android", "android", "Managing Android Enterprise devices with Intune."),
    ("Cloud PC", "cloud-pc", "Windows 365 Cloud PC provisioning, connectivity and management."),
    ("AVD", "avd", "Azure Virtual Desktop hosts, FSLogix and session issues."),
    ("Defender", "defender", "Microsoft Defender for Endpoint and endpoint security."),
    ("Purview", "purview", "Microsoft Purview data protection and compliance on endpoints."),
    ("Vulnerability Management", "vulnerability-management", "CVEs, Patch Tuesday priorities and Defender Vulnerability Management."),
    ("Entra ID", "entra-id", "Entra ID join, Conditional Access and device identity."),
    ("Microsoft 365", "microsoft-365", "Microsoft 365 apps and admin changes that affect endpoints."),
    ("Copilot", "copilot", "Microsoft 365 Copilot rollout, admin controls and licensing."),
]
TOPIC_NAMES = [t[0] for t in TOPICS]
TOPIC_SLUG = {t[0]: t[1] for t in TOPICS}
TYPES = ["What's new", "Known issue", "Fix", "Workaround", "How to"]
FONTS = "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700&family=JetBrains+Mono:wght@400;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap"


def esc(s):
    return html.escape(str(s), quote=True)


def read_doc(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise SystemExit(f"{path}: missing front matter")
    meta = yaml.safe_load(m.group(1)) or {}
    return meta, m.group(2)


def md_to_html(body):
    return markdown.markdown(body, extensions=["extra", "sane_lists"], output_format="html5")


def nice_date(d):
    return f"{d.day} {d.strftime('%B %Y')}"


def slug_of(path):
    return re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)


def topic_url(t):
    return f"/topics/{TOPIC_SLUG[t]}/"


def load_posts():
    posts = []
    for p in sorted((ROOT / "posts").glob("*.md")):
        meta, body = read_doc(p)
        d = meta["date"]
        if isinstance(d, str):
            d = dt.date.fromisoformat(d[:10])
        elif isinstance(d, dt.datetime):
            d = d.date()
        words = len(re.findall(r"\w+", re.sub(r"```.*?```", "", body, flags=re.S)))
        post = {
            "title": meta["title"],
            "description": meta.get("description", ""),
            "author": meta.get("author", SITE["author"]),
            "tags": [t for t in meta.get("tags", []) if t in TOPIC_NAMES],
            "type": meta.get("type", "") if meta.get("type") in TYPES else "",
            "date": d,
            "slug": slug_of(p),
            "html": md_to_html(body),
            "minutes": max(1, math.ceil(words / 220)),
        }
        post["path"] = f"/{d:%Y/%m/%d}/{post['slug']}/"
        posts.append(post)
    posts.sort(key=lambda x: (x["date"], x["slug"]), reverse=True)
    return posts


def page(title, body, *, path, description, current="", head_extra="", sidebar=""):
    full_title = SITE["name"] if title == SITE["name"] else f"{title} | {SITE['name']}"
    url = SITE["url"] + path
    nav = "".join(
        f'<a href="{href}"{" aria-current=\"page\"" if key == current else ""}>{label}</a>'
        for key, href, label in [("home", "/", "Home"), ("topics", "/topics/", "Topics"), ("about", "/about/", "About")]
    )
    layout = f'<div class="layout"><main>{body}</main><aside>{sidebar}</aside></div>' if sidebar else f'<div class="layout" style="grid-template-columns:minmax(0,1fr)"><main>{body}</main></div>'
    year = dt.date.today().year
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="author" content="{esc(SITE['author'])}">
<link rel="canonical" href="{esc(url)}">
<meta property="og:site_name" content="{esc(SITE['name'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(url)}">
<meta name="twitter:card" content="summary">
<link rel="alternate" type="application/rss+xml" title="{esc(SITE['name'])}" href="/feed.xml">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="/style.css">
{head_extra}
</head>
<body>
<div class="wrap">
<header class="site-head">
<a class="brand" href="/">MaheshKumar<span>SE</span></a>
<nav class="nav" aria-label="Main">{nav}</nav>
</header>
{layout}
<footer class="site-foot">
<span>Copyright {year} {esc(SITE['name'])}. Views here are my own.</span>
<span><a href="/feed.xml">RSS</a> &nbsp; <a href="/privacy/">Privacy</a></span>
</footer>
</div>
</body>
</html>
"""


def sidebar(posts):
    tags = "".join(f'<li><a href="{topic_url(t)}">{esc(t)}</a></li>' for t in TOPIC_NAMES)
    recent = "".join(
        f'<li><a href="{p["path"]}"><time datetime="{p["date"]}">{nice_date(p["date"])}</time>{esc(p["title"])}</a></li>'
        for p in posts[:6]
    )
    return f"""<section><h2>About</h2><p>I'm Mahesh, a Senior End User Computing Architect. I write here every day about what is new, what is broken and how to fix it across the Microsoft endpoint stack. <a href="/about/">More about me</a></p></section>
<section><h2>Topics</h2><ul class="tags">{tags}</ul></section>
<section><h2>Recent posts</h2><ul class="recent">{recent}</ul></section>"""


def meta_line(p):
    tags = "".join(f'<a class="tag" href="{topic_url(t)}">{esc(t)}</a>' for t in p["tags"])
    kind = f'<span class="kind kind-{re.sub(r"[^a-z]", "", p["type"].lower())}">{esc(p["type"])}</span>' if p["type"] else ""
    return f'<div class="meta">{kind}<time datetime="{p["date"]}">{nice_date(p["date"])}</time>{tags}</div>'


def write(rel, content):
    f = OUT / rel.lstrip("/")
    if rel.endswith("/"):
        f = f / "index.html"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    posts = load_posts()
    side = sidebar(posts)

    # Home
    items = "".join(
        f'<li>{meta_line(p)}<h2><a href="{p["path"]}">{esc(p["title"])}</a></h2><p>{esc(p["description"])}</p></li>'
        for p in posts
    ) or "<li><p>The first post is on its way.</p></li>"
    home = f'<p class="intro">{esc(SITE["description"])}</p><ul class="post-list">{items}</ul>'
    write("/", page(SITE["name"], home, path="/", description=SITE["description"], current="home", sidebar=side))

    # Posts
    for i, p in enumerate(posts):
        newer = posts[i - 1] if i > 0 else None
        older = posts[i + 1] if i + 1 < len(posts) else None
        nav = '<nav class="post-nav" aria-label="More posts">'
        nav += f'<a href="{older["path"]}"><span>Older</span>{esc(older["title"])}</a>' if older else "<i></i>"
        nav += f'<a href="{newer["path"]}" style="text-align:right"><span>Newer</span>{esc(newer["title"])}</a>' if newer else ""
        nav += "</nav>"
        ld = {
            "@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"],
            "description": p["description"], "datePublished": p["date"].isoformat(),
            "author": {"@type": "Person", "name": p["author"], "url": SITE["url"] + "/about/"},
            "publisher": {"@type": "Person", "name": p["author"]},
            "mainEntityOfPage": SITE["url"] + p["path"], "keywords": ", ".join(p["tags"]),
        }
        head_extra = (
            '<meta property="og:type" content="article">'
            f'<meta property="article:published_time" content="{p["date"].isoformat()}">'
            f'<script type="application/ld+json">{json.dumps(ld)}</script>'
        )
        body = f"""<article>
<header class="post-head">{meta_line(p)}<h1>{esc(p["title"])}</h1><p class="dek">{esc(p["description"])}</p>
<div class="byline"><span>By <strong>{esc(p["author"])}</strong></span><time datetime="{p["date"]}">{nice_date(p["date"])}</time><span>{p["minutes"]} min read</span></div>
</header>
<div class="prose">{p["html"]}</div>
{nav}
</article>"""
        write(p["path"], page(p["title"], body, path=p["path"], description=p["description"], head_extra=head_extra, sidebar=side))

    # Topics index and one page per topic
    rows = ""
    for name, slug, blurb in TOPICS:
        tp = [p for p in posts if name in p["tags"]]
        lis = "".join(f'<li><time datetime="{p["date"]}">{p["date"]:%d %b %Y}</time><a href="{p["path"]}">{esc(p["title"])}</a></li>' for p in tp[:5])
        more = f'<p class="more"><a href="/topics/{slug}/">All {len(tp)} posts on {esc(name)}</a></p>' if len(tp) > 5 else ""
        empty = "" if tp else '<p class="soon">Posts coming soon.</p>'
        rows += f'<section class="topic"><h2><a href="/topics/{slug}/">{esc(name)}</a></h2><p class="blurb">{esc(blurb)}</p><ul>{lis}</ul>{more}{empty}</section>'
        items = "".join(
            f'<li>{meta_line(p)}<h2><a href="{p["path"]}">{esc(p["title"])}</a></h2><p>{esc(p["description"])}</p></li>'
            for p in tp
        ) or '<li><p>Posts on this topic are coming soon.</p></li>'
        tbody = f'<header class="page-head"><h1>{esc(name)}</h1><p class="dek">{esc(blurb)}</p></header><ul class="post-list">{items}</ul>'
        write(f"/topics/{slug}/", page(name, tbody, path=f"/topics/{slug}/", description=blurb, current="topics", sidebar=side))
    topics_body = f'<header class="page-head"><h1>Topics</h1></header>{rows}'
    write("/topics/", page("Topics", topics_body, path="/topics/", description="Posts on " + SITE["name"] + " grouped by topic.", current="topics", sidebar=side))

    # Static pages
    for pg in sorted((ROOT / "pages").glob("*.md")):
        meta, bodymd = read_doc(pg)
        path = f"/{pg.stem}/"
        body = f'<article><header class="page-head"><h1>{esc(meta["title"])}</h1></header><div class="prose">{md_to_html(bodymd)}</div></article>'
        write(path, page(meta["title"], body, path=path, description=meta.get("description", SITE["description"]), current=pg.stem, sidebar=side))

    # 404
    nf = '<header class="page-head"><h1>Page not found</h1></header><div class="prose"><p>That page doesn\'t exist. Try the <a href="/">latest posts</a> or browse by <a href="/topics/">topic</a>.</p></div>'
    (OUT / "404.html").write_text(page("Page not found", nf, path="/404.html", description=SITE["description"]), encoding="utf-8")

    # RSS
    def rfc(d):
        return format_datetime(dt.datetime(d.year, d.month, d.day, 7, 0, tzinfo=dt.timezone(dt.timedelta(hours=5, minutes=30))))
    items = "".join(
        f"<item><title>{esc(p['title'])}</title><link>{SITE['url']}{p['path']}</link><guid>{SITE['url']}{p['path']}</guid>"
        f"<pubDate>{rfc(p['date'])}</pubDate><author>noreply@maheshkumarse.com ({esc(p['author'])})</author>"
        f"<description>{esc(p['description'])}</description></item>"
        for p in posts[:30]
    )
    (OUT / "feed.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{SITE["name"]}</title>'
        f'<link>{SITE["url"]}/</link><description>{esc(SITE["description"])}</description><language>en-gb</language>{items}</channel></rss>',
        encoding="utf-8",
    )

    # Sitemap and robots
    urls = ["/", "/topics/"] + [f"/topics/{t[1]}/" for t in TOPICS] + [f"/{pg.stem}/" for pg in sorted((ROOT / "pages").glob("*.md"))] + [p["path"] for p in posts]
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{SITE['url']}{u}</loc></url>" for u in urls) + "</urlset>",
        encoding="utf-8",
    )
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n", encoding="utf-8")

    # Static assets
    for f in (ROOT / "static").iterdir():
        shutil.copy(f, OUT / f.name)
    if (ROOT / "images").exists():
        shutil.copytree(ROOT / "images", OUT / "images")
    (OUT / "CNAME").write_text("maheshkumarse.com\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {len(posts)} post(s) into {OUT}")


if __name__ == "__main__":
    build()
