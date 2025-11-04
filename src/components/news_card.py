import re
from html import unescape
from urllib.parse import urlparse
import streamlit as st


def _sanitize_text(html_text: str) -> str:
    """Remove HTML tags and unescape entities from a string.

    Kept at module level so tests and debug scripts can import it directly.
    """
    if not html_text:
        return ""
    # unescape HTML entities first
    txt = unescape(html_text)
    # remove anchor/font tags specifically, then any remaining tags
    txt = re.sub(r"<\s*(a|font)[^>]*>", "", txt, flags=re.IGNORECASE)
    txt = re.sub(r"</\s*(a|font)\s*>", "", txt, flags=re.IGNORECASE)
    txt = re.sub(r"<[^>]+>", "", txt)
    return txt.strip()


def news_card(article: dict) -> None:
    """Render a news article card in Streamlit.

    article: dict with keys: title, link, description, published
    """
    title = article.get("title", "No title")
    link = article.get("link", "#")
    desc = article.get("description", "")
    published = article.get("published", "")

    main_title = _sanitize_text(title)
    main_desc = _sanitize_text(desc)

    # try to extract a human-friendly source name (Title - Source)
    source = ""
    if " - " in main_title:
        parts = main_title.rsplit(" - ", 1)
        if len(parts) == 2:
            main_title, source = parts[0].strip(), parts[1].strip()

    if not source:
        try:
            p = urlparse(link)
            source = p.netloc.replace("www.", "")
        except Exception:
            source = ""

    # tag (optional label injected by the app when bucketing topics)
    tag = article.get('tag', '')

    # Build the card HTML regardless of how `source` was derived
    card_html = f"""
<div class="card">
    <div class="card-body">
        <div class='card-title-row'>
            <a class='card-title' href="{link}" target="_blank">{main_title}</a>
            {f"<span class='card-tag'>{tag}</span>" if tag else ''}
            <div class='card-source'>{source}</div>
        </div>
        <div class='card-meta'>{published}</div>
        <div class='card-desc'>{main_desc}</div>
        <div class='card-readmore'><a href="{link}" target="_blank">Read more</a></div>
    </div>
</div>
"""

    # render the HTML block (unsafe HTML enabled for richer styling)
    st.markdown(card_html, unsafe_allow_html=True)