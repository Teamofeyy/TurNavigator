from __future__ import annotations

import ssl
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin
from urllib.request import Request, urlopen

import certifi

from app.models import POI, POIImage

DEFAULT_HTML_TIMEOUT_SECONDS = 12


@dataclass(slots=True)
class WebsiteMediaResult:
    scanned: int = 0
    enriched: int = 0
    skipped: int = 0
    failed: int = 0


class _MetaTagParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}
        self.link: dict[str, str] = {}
        self.title: str | None = None
        self._inside_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key.lower(): (value or "") for key, value in attrs}
        if tag.lower() == "meta":
            key = (attributes.get("property") or attributes.get("name") or "").strip().lower()
            content = (attributes.get("content") or "").strip()
            if key and content:
                self.meta[key] = content
        elif tag.lower() == "link":
            rel = (attributes.get("rel") or "").strip().lower()
            href = (attributes.get("href") or "").strip()
            if rel and href:
                self.link[rel] = href
        elif tag.lower() == "title":
            self._inside_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._inside_title = False

    def handle_data(self, data: str) -> None:
        if self._inside_title:
            value = data.strip()
            if value:
                self.title = value


def enrich_poi_with_website_media(
    poi: POI,
    *,
    timeout_seconds: int = DEFAULT_HTML_TIMEOUT_SECONDS,
) -> bool:
    if not poi.website or poi.images:
        return False

    html, final_url = fetch_html(poi.website, timeout_seconds=timeout_seconds)
    media = extract_website_media(html, base_url=final_url)
    if media is None:
        return False

    poi.images.append(
        POIImage(
            provider="website",
            original_url=media["original_url"],
            thumbnail_url=media["thumbnail_url"],
            source_page_url=media["source_page_url"],
            license=media.get("license"),
            author=media.get("author"),
            attribution_text=media.get("attribution_text"),
            width=media.get("width"),
            height=media.get("height"),
            is_primary=True,
        )
    )

    description = media.get("description")
    if description and (not poi.description or poi.description.startswith("Точка интереса")):
        poi.description = description
    return True


def extract_website_media(html: str, *, base_url: str) -> dict[str, Any] | None:
    parser = _MetaTagParser()
    parser.feed(html)

    image_url = (
        parser.meta.get("og:image")
        or parser.meta.get("twitter:image")
        or parser.meta.get("twitter:image:src")
        or parser.link.get("image_src")
    )
    if not image_url:
        return None

    normalized_image_url = urljoin(base_url, image_url)
    return {
        "original_url": normalized_image_url,
        "thumbnail_url": normalized_image_url,
        "source_page_url": base_url,
        "license": None,
        "author": parser.meta.get("author"),
        "attribution_text": None,
        "description": parser.meta.get("og:description")
        or parser.meta.get("description")
        or parser.meta.get("twitter:description"),
        "title": parser.meta.get("og:title") or parser.title,
        "width": None,
        "height": None,
    }


def fetch_html(url: str, *, timeout_seconds: int = DEFAULT_HTML_TIMEOUT_SECONDS) -> tuple[str, str]:
    request = Request(
        url,
        headers={
            "Accept": "text/html,application/xhtml+xml",
            "User-Agent": "TravelContextPrototype/0.1",
        },
        method="GET",
    )
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    with urlopen(request, timeout=timeout_seconds, context=ssl_context) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        html = response.read().decode(charset, errors="ignore")
        return html, response.geturl()
