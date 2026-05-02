from __future__ import annotations

from urllib.parse import quote, unquote, urlparse, urlunparse


WIKIMEDIA_UPLOAD_HOST = "upload.wikimedia.org"
WIKIMEDIA_THUMB_PREFIX = "/wikipedia/commons/thumb/"


def normalize_poi_image_url(value: str | None) -> str | None:
    if not value:
        return value

    normalized = value.strip()
    if not normalized:
        return None
    if normalized.startswith("//"):
        normalized = f"https:{normalized}"

    return _wikimedia_thumb_to_file_path(normalized) or normalized


def _wikimedia_thumb_to_file_path(value: str) -> str | None:
    parsed = urlparse(value)
    if parsed.netloc != WIKIMEDIA_UPLOAD_HOST or WIKIMEDIA_THUMB_PREFIX not in parsed.path:
        return None

    segments = [segment for segment in parsed.path.split("/") if segment]
    if len(segments) < 6:
        return None

    file_name_segment = segments[-2]
    size_segment = segments[-1]
    width = _extract_width(size_segment)
    if not file_name_segment:
        return None

    try:
        file_name = unquote(file_name_segment)
    except Exception:
        file_name = file_name_segment

    query = f"width={width}" if width is not None else ""
    return urlunparse(
        (
            "https",
            "commons.wikimedia.org",
            f"/wiki/Special:FilePath/{quote(file_name)}",
            "",
            query,
            "",
        )
    )


def _extract_width(size_segment: str) -> int | None:
    marker = "px-"
    if marker not in size_segment:
        return None
    prefix = size_segment.split(marker, maxsplit=1)[0]
    try:
        return int(prefix)
    except ValueError:
        return None
