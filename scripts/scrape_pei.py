#!/usr/bin/env python3
"""Scrape PEI's News & Analysis listing into stories.json (PE Hub's RSS feed is gone)."""
import json, re, sys, html, urllib.parse, urllib.request
from datetime import datetime, timezone

BASE = "https://www.privateequityinternational.com"
PAGES = [BASE + "/private-equity/news-analysis/", BASE + "/private-equity/news-analysis/page/2/"]
LIMIT = 20

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (story-cycler)"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

def clean(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

def parse(page):
    # each card starts at a listing-featured-card / listing-article-card container
    parts = re.split(r'data-testid="listing-(?:featured|article)-card"', page)[1:]
    out = []
    for p in parts:
        link = re.search(r'href="(/[a-z0-9][a-z0-9-]{8,}/)"', p)
        title = re.search(r'<h3[^>]*>(.*?)</h3>', p, re.S)
        desc = re.search(r'data-testid="(?:banner-card-)?description[^"]*"[^>]*>(.*?)</p>', p, re.S)
        meta = re.search(r'(\d+ min read)\s*(?:<[^>]+>)*\s*·?\s*(?:<[^>]+>)*\s*(\d{1,2} \w+ \d{4})', p)
        badges = [clean(b) for b in re.findall(r'data-testid="badge-text">(.*?)</span>', p)]
        img = re.search(r'url=(https%3A%2F%2Fmedia\.privateequityinternational\.com[^&"]+)', p)
        if not (link and title):
            continue
        date = ""
        if meta:
            try:
                date = datetime.strptime(meta.group(2), "%d %B %Y").strftime("%B %-d, %Y")
            except ValueError:
                date = meta.group(2)
        out.append({
            "title": clean(title.group(1)),
            "url": BASE + link.group(1),
            "date": date,
            "readTime": meta.group(1) if meta else "",
            "description": clean(desc.group(1)) if desc else "",
            "thumbnail": urllib.parse.unquote(img.group(1)) if img else None,
            "categories": [b for b in badges if b != "News & Analysis"] or ["News & Analysis"],
        })
    return out

def main():
    seen, stories = set(), []
    for url in PAGES:
        try:
            for s in parse(get(url)):
                if s["url"] not in seen:
                    seen.add(s["url"]); stories.append(s)
        except Exception as e:
            print(f"warn: {url}: {e}", file=sys.stderr)
    stories = stories[:LIMIT]
    if len(stories) < 5:
        sys.exit(f"Only {len(stories)} stories parsed; refusing to overwrite stories.json")
    with open("stories.json", "w") as f:
        json.dump({"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "source": PAGES[0], "stories": stories}, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(stories)} stories")

if __name__ == "__main__":
    main()
