"""
Parse WordPress category RSS for On a Roll posts → YYYY-MM → URL slug (for GA4 path contains)
and post title (RSS <title>, same text as the page H1 on typical WordPress themes).
"""

from __future__ import annotations

import html as html_module
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse
from urllib.request import Request, urlopen

DEFAULT_ON_A_ROLL_FEED = "https://www.tenacioustapes.com.au/category/on-a-roll/feed/"


def _slug_from_item_link(link: str) -> str:
    path = urlparse((link or "").strip()).path.strip("/")
    if not path:
        return ""
    return path.split("/")[-1]


def fetch_on_a_roll_by_month(
    feed_url: str = DEFAULT_ON_A_ROLL_FEED,
    timeout: int = 20,
) -> dict[str, str]:
    """Slug map only; see :func:`fetch_on_a_roll_meta_by_month` for titles."""
    slugs, _titles = fetch_on_a_roll_meta_by_month(feed_url=feed_url, timeout=timeout)
    return slugs


def fetch_on_a_roll_meta_by_month(
    feed_url: str = DEFAULT_ON_A_ROLL_FEED,
    timeout: int = 20,
) -> tuple[dict[str, str], dict[str, str]]:
    """
    Returns two maps keyed by YYYY-MM:
    - slugs from <link> (for GA4 path contains)
    - titles from <title> (decoded; matches on-page H1 for standard WP RSS)

    If several posts share the same calendar month, the **newest** pubDate wins.
    """
    url = (feed_url or DEFAULT_ON_A_ROLL_FEED).strip() or DEFAULT_ON_A_ROLL_FEED
    req = Request(url, headers={"User-Agent": "TenaciousStats/1.0 (internal; analytics dashboard)"})
    with urlopen(req, timeout=timeout) as resp:
        xml_data = resp.read()

    root = ET.fromstring(xml_data)
    channel = root.find("channel")
    if channel is None:
        return {}, {}

    # ym -> list of (datetime, slug, title)
    buckets: dict[str, list[tuple[datetime, str, str]]] = defaultdict(list)

    for item in channel.findall("item"):
        link_el = item.find("link")
        pub_el = item.find("pubDate")
        title_el = item.find("title")
        if link_el is None or pub_el is None:
            continue
        link = (link_el.text or "").strip()
        pub_raw = (pub_el.text or "").strip()
        raw_title = (title_el.text or "").strip() if title_el is not None else ""
        title = html_module.unescape(raw_title).strip()
        if not link:
            continue
        slug = _slug_from_item_link(link)
        if not slug:
            continue
        try:
            dt = parsedate_to_datetime(pub_raw)
            if dt.tzinfo is not None:
                dt = dt.astimezone().replace(tzinfo=None)
        except (TypeError, ValueError):
            continue
        ym = f"{dt.year}-{dt.month:02d}"
        buckets[ym].append((dt, slug, title))

    slugs: dict[str, str] = {}
    titles: dict[str, str] = {}
    for ym, triples in buckets.items():
        triples.sort(key=lambda x: x[0], reverse=True)
        _dt, slug, title = triples[0]
        slugs[ym] = slug
        titles[ym] = title
    return slugs, titles
