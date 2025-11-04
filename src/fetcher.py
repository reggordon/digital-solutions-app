import requests
import feedparser
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone
import time


def fetch_digital_solutions(fetch_images: bool = False, query: Optional[str] = None, days: int = 30, region: Optional[str] = None) -> List[Dict]:

    if query is None:
        # search any of these phrases
        query = 'Digital wallets OR network tokenisation OR "Click to Pay" OR "Account updater"'
    # build google news rss URL (simple encoding: spaces -> +)
    q = query.replace(' ', '+')

    # region -> (hl, gl, ceid) mapping. Google News understands hl (language), gl (country), ceid (country:lang)
    region_map = {
        'Global': ('en-US', 'US', 'US:en'),
        'United States': ('en-US', 'US', 'US:en'),
        'United Kingdom': ('en-GB', 'GB', 'GB:en'),
        # Europe doesn't have a single GL value, pick DE as a reasonable EU proxy for localized results
        'Europe': ('en-GB', 'DE', 'DE:en'),
    }

    if region in region_map:
        hl, gl, ceid = region_map[region]
    else:
        hl, gl, ceid = region_map['Global']

    url = f"https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={ceid}"
    try:
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (compatible; punk-news-fetcher/1.0)"
        })
    except Exception:
        return []

    if response.status_code != 200:
        return []

    feed = feedparser.parse(response.content)
    articles: List[Dict] = []
    now = datetime.now(timezone.utc)
    min_dt = now - timedelta(days=days)

    for entry in feed.entries:
        # link handling
        raw_link = entry.get("link", "")
        final_link = raw_link

        links = entry.get("links", [])
        if links:
            for l in links:
                href = l.get("href") if isinstance(l, dict) else None
                if href and href.startswith("http"):
                    if "news.google" not in href:
                        final_link = href
                        break
                    final_link = href

        if final_link and "news.google" in final_link:
            try:
                from urllib.parse import urlparse, parse_qs, unquote

                parsed = urlparse(final_link)
                qs = parse_qs(parsed.query)
                candidate = None
                for key in ("url", "u", "q"):
                    if key in qs and qs[key]:
                        candidate = qs[key][0]
                        break
                if candidate:
                    final_link = unquote(candidate)
            except Exception:
                pass

        # published filtering: prefer published_parsed if available
        published = entry.get("published", "")
        pub_parsed = entry.get("published_parsed") or entry.get("updated_parsed")
        if pub_parsed:
            try:
                pub_dt = datetime.fromtimestamp(time.mktime(pub_parsed), tz=timezone.utc)
            except Exception:
                pub_dt = None
        else:
            pub_dt = None

        # skip old items outside the window
        if pub_dt and pub_dt < min_dt:
            continue

        description = entry.get("summary", "")

        # build article dict without images (keep simple and fast)
        article = {
            "title": entry.get("title", ""),
            "link": final_link,
            "description": description,
            "published": published,
            # include an ISO timestamp when available to support timeline views
            "published_iso": pub_dt.isoformat() if pub_dt else "",
        }

        articles.append(article)

    return articles
    