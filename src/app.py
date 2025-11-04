import streamlit as st
from fetcher import fetch_digital_solutions
from components.news_card import news_card
from datetime import datetime, timezone
import re


def humanize_timesince(iso_ts: str) -> str:
    try:
        t = datetime.fromisoformat(iso_ts)
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
    except Exception:
        return iso_ts
    now = datetime.now(timezone.utc)
    delta = now - t
    secs = int(delta.total_seconds())
    if secs < 60:
        return f"{secs}s ago"
    mins = secs // 60
    if mins < 60:
        return f"{mins}m ago"
    hrs = mins // 60
    if hrs < 24:
        return f"{hrs}h ago"
    days = hrs // 24
    return f"{days}d ago"


@st.cache_data(ttl=600)
def get_cached_news(query: str, days: int, region: str):
    """Cached wrapper around fetcher to avoid repeated network calls.

    Cache keys include query, days and region so UI controls produce distinct cached results.
    Returns a tuple: (articles_list, fetched_iso_timestamp)
    TTL: 600 seconds (10 minutes) by default.
    """
    articles = fetch_digital_solutions(fetch_images=False, query=query, days=days, region=region)
    return articles, datetime.now().isoformat()


def main():
        # Global styles and theme variables for a unified page look and feel
        st.markdown(
            """
        <style>
        :root {
            --bg: #f7f7fb;
            --panel: #ffffff;
            --border: #eaecf0;
            --text: #0f172a;
            --muted: #667085;
            --primary: #3730a3; /* indigo-800 */
            --primary-weak: #eef2ff;
        }

        /* Page and typography */
        body, html, .stApp { background-color: var(--bg); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; }
        .block-container { max-width: 960px; margin: 0 auto; padding-top: 18px; padding-left: 18px; padding-right: 18px; }

        /* Unified header */
        .app-header { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 24px 20px; margin: 24px 0 28px 0; }
        .app-title { font-size: 22px; font-weight: 800; color: var(--text); letter-spacing: -0.01em; }
        .app-subtitle { color: var(--muted); margin-top: 4px; font-size: 14px; }
        .app-meta { color: var(--muted); margin-top: 8px; font-size: 12px; }
        .app-actions { text-align: right; }
        .app-btn { appearance: none; border: 1px solid var(--border); background: #fff; color: var(--text); padding: 6px 10px; border-radius: 8px; font-size: 12px; cursor: pointer; }
        .app-btn:hover { background: #fafafa; }

        /* Cards */
        .card { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; margin-bottom: 14px; overflow: hidden; }
        .card-body { padding: 14px; }
        .card-title-row { display:flex; align-items: baseline; gap: 8px; justify-content: space-between; }
        .card-title { font-size:16px; font-weight:700; color:var(--text); text-decoration:none; }
        .card-source { color: var(--muted); font-size: 12px; margin-left: 8px; }
        .card-meta { color:#777; font-size:12px; margin-top:6px; }
        .card-desc { color:#333; margin-top:10px; font-size:14px; }
        .card-tag { display:inline-block; background:var(--primary-weak); color:var(--primary); padding:3px 8px; border-radius:999px; font-size:12px; margin-left:8px; white-space: nowrap; }
        .card-readmore a { color: var(--primary); font-size: 13px; }

        @media (max-width: 800px) {
            .block-container { padding-left: 12px; padding-right: 12px; }
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Controls: topics, region and days window
        with st.sidebar.expander("Filters", expanded=True):
            topic_options = [
                "Digital wallets",
                "network tokenisation",
                "Click to Pay",
                "Account updater",
                "Visa product announcements",
                "Mastercard product announcements",
            ]
            selected_topics = st.multiselect(
                "Topics",
                options=topic_options,
                default=topic_options,
                help="Choose which topics to include in the feed. Articles that match multiple topics will appear under each matching section.",
            )
            region = st.selectbox(
                "Region",
                options=["Global", "United States", "United Kingdom", "Europe"],
                index=0,
                help="Localize results by region (language/country hints sent to Google News).",
            )
            days = st.slider(
                "Last N days",
                min_value=1,
                max_value=90,
                value=30,
                help="Include articles published in the last N days (client-side filter). Increase to see older items.",
            )
            st.caption("How far back to search for articles. This filter is applied locally after fetching the RSS feed.")
            per_topic = st.number_input(
                "Articles per topic (visible)",
                min_value=1,
                max_value=50,
                value=8,
                help="Number of articles shown per topic before the 'Show more' expander appears.",
            )

        # compose a Google News compatible query (OR between topics)
        if not selected_topics:
            query = 'Digital wallets OR network tokenisation OR "Click to Pay" OR "Account updater"'
        else:
            # quote multi-word topics
            parts = []
            for t in selected_topics:
                if ' ' in t:
                    parts.append(f'"{t}"')
                else:
                    parts.append(t)
            query = ' OR '.join(parts)

        # Header placeholder renders immediately to avoid perceived blocking
        header_ph = st.empty()
        header_ph.markdown(
            """
    <div class="app-header">
      <div class="app-title">Digital Solutions News</div>
      <div class="app-subtitle">Latest on digital wallets, network tokenization, Click to Pay, account updater, and major network product updates.</div>
      <div class="app-meta">Fetching latest…</div>
    </div>
    """,
            unsafe_allow_html=True,
        )

        try:
            news_articles, fetched_at = get_cached_news(query=query, days=days, region=region)
        except Exception as e:
            st.error(f"Failed to fetch news: {e}")
            news_articles, fetched_at = [], datetime.now().isoformat()

        nice = humanize_timesince(fetched_at)

        # Update the header with real meta once data is ready
        header_ph.markdown(
            f"""
    <div class="app-header">
      <div class="app-title">Digital Solutions News</div>
      <div class="app-subtitle">Latest on digital wallets, network tokenization, Click to Pay, account updater, and major network product updates.</div>
      <div class="app-meta">Updated {nice} • {len(news_articles)} articles</div>
    </div>
    """,
            unsafe_allow_html=True,
        )

        # Refresh control
        rcol1, rcol2 = st.columns([6, 1])
        with rcol2:
            if st.button("Refresh", help="Clear cache and refetch the latest articles"):
                st.cache_data.clear()
                st.rerun()

        if not news_articles:
            st.write("No news articles found.")
            return

        # Group articles by selected topic. Use regex for stricter matching and allow multi-bucket assignment.
        topic_buckets = {t: [] for t in selected_topics}
        topic_buckets["Other"] = []

        def _matches_topic_regex(article: dict, topic: str) -> bool:
            txt = " ".join([article.get("title", ""), article.get("description", ""), article.get("link", "")])
            txt = txt.lower()
            key = topic.lower().strip('"')
            # if phrase (contains space), match the phrase anywhere; otherwise match whole word boundaries
            if " " in key:
                return re.search(re.escape(key), txt) is not None
            # match whole word for single words
            return re.search(r"\b" + re.escape(key) + r"\b", txt) is not None

        for art in news_articles:
            # compute all matching topics for this article
            matched = [t for t in selected_topics if _matches_topic_regex(art, t)]
            art['matched_topics'] = matched
            if matched:
                # assign to the first matching topic only to avoid duplicates
                art['tag'] = matched[0]
                topic_buckets[matched[0]].append(art)
            else:
                art['tag'] = 'Other'
                topic_buckets["Other"].append(art)

        # Render each topic section with a heading and a two-column article grid

        for topic in list(selected_topics) + ["Other"]:
            bucket = topic_buckets.get(topic, [])
            if not bucket:
                continue
            st.markdown(f"### {topic} ({len(bucket)})")
            head = bucket[:per_topic]
            tail = bucket[per_topic:]

            # render head in two columns
            cols = st.columns(2)
            for i, art in enumerate(head):
                try:
                    # put articles alternately into the two columns
                    with cols[i % 2]:
                        news_card(art)
                except Exception as e:
                    st.write(f"Error rendering article: {e}")

            if tail:
                with st.expander(f"Show {len(tail)} more for {topic}"):
                    cols2 = st.columns(2)
                    for i, art in enumerate(tail):
                        try:
                            with cols2[i % 2]:
                                news_card(art)
                        except Exception as e:
                            st.write(f"Error rendering article: {e}")
if __name__ == "__main__":
    main()