"""Safe YouTube resource construction for learning paths.

Anti-hallucination policy:
- Never invent arbitrary video IDs.
- Prefer curated *search* URLs that always resolve (results pages).
- Optional allowlisted watch URLs only when present in VERIFIED_WATCH_URLS.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote_plus, urlparse

ALGORITHM_VERSION = "ats-youtube-crew-v1"

# Curated educational search intents (no fabricated watch IDs).
VERIFIED_YOUTUBE_SEARCHES: dict[str, dict[str, str]] = {
    "python": {
        "title": "Python full course – freeCodeCamp on YouTube",
        "query": "python full course freecodecamp",
        "channel": "YouTube · freeCodeCamp",
    },
    "javascript": {
        "title": "JavaScript full course – freeCodeCamp on YouTube",
        "query": "javascript full course freecodecamp",
        "channel": "YouTube · freeCodeCamp",
    },
    "typescript": {
        "title": "TypeScript course – freeCodeCamp on YouTube",
        "query": "typescript full course freecodecamp",
        "channel": "YouTube · freeCodeCamp",
    },
    "react": {
        "title": "React course – freeCodeCamp on YouTube",
        "query": "react course freecodecamp",
        "channel": "YouTube · freeCodeCamp",
    },
    "sql": {
        "title": "SQL full course – freeCodeCamp on YouTube",
        "query": "sql full course freecodecamp",
        "channel": "YouTube · freeCodeCamp",
    },
    "docker": {
        "title": "Docker tutorial – freeCodeCamp on YouTube",
        "query": "docker tutorial freecodecamp",
        "channel": "YouTube · freeCodeCamp",
    },
    "git": {
        "title": "Git and GitHub – freeCodeCamp on YouTube",
        "query": "git and github for beginners freecodecamp",
        "channel": "YouTube · freeCodeCamp",
    },
    "kubernetes": {
        "title": "Kubernetes course – freeCodeCamp on YouTube",
        "query": "kubernetes course freecodecamp",
        "channel": "YouTube · freeCodeCamp",
    },
    "machine learning": {
        "title": "Machine learning course – freeCodeCamp on YouTube",
        "query": "machine learning for everybody freecodecamp",
        "channel": "YouTube · freeCodeCamp",
    },
    "fastapi": {
        "title": "FastAPI course – freeCodeCamp on YouTube",
        "query": "fastapi course freecodecamp",
        "channel": "YouTube · freeCodeCamp",
    },
    "aws": {
        "title": "AWS cloud course – freeCodeCamp on YouTube",
        "query": "aws certified cloud practitioner freecodecamp",
        "channel": "YouTube · freeCodeCamp",
    },
    "linux": {
        "title": "Linux course – freeCodeCamp on YouTube",
        "query": "linux full course freecodecamp",
        "channel": "YouTube · freeCodeCamp",
    },
    "node.js": {
        "title": "Node.js course – freeCodeCamp on YouTube",
        "query": "nodejs express full course freecodecamp",
        "channel": "YouTube · freeCodeCamp",
    },
    "nodejs": {
        "title": "Node.js course – freeCodeCamp on YouTube",
        "query": "nodejs express full course freecodecamp",
        "channel": "YouTube · freeCodeCamp",
    },
}

# Only add watch URLs here when they have been verified offline. Empty by default
# so the system never ships invented video IDs.
VERIFIED_WATCH_URLS: dict[str, dict[str, str]] = {}

_YOUTUBE_HOSTS = {
    "www.youtube.com",
    "youtube.com",
    "m.youtube.com",
    "youtu.be",
}


def normal_skill(value: str) -> str:
    text = value.lower().replace(".js", " js ").strip()
    text = re.sub(r"\s+", " ", text)
    return text


def catalog_match(gap: str) -> dict[str, str] | None:
    key = normal_skill(gap)
    if key in VERIFIED_WATCH_URLS:
        entry = VERIFIED_WATCH_URLS[key]
        return {
            "title": entry["title"],
            "url": entry["url"],
            "channel": entry.get("channel") or "YouTube",
            "kind": "watch",
        }
    if key in VERIFIED_YOUTUBE_SEARCHES:
        entry = VERIFIED_YOUTUBE_SEARCHES[key]
        return {
            "title": entry["title"],
            "url": youtube_search_url(entry["query"]),
            "channel": entry.get("channel") or "YouTube",
            "kind": "search",
            "query": entry["query"],
        }
    candidates = [k for k in VERIFIED_YOUTUBE_SEARCHES if k in key or key in k]
    if not candidates:
        return None
    best = max(candidates, key=len)
    entry = VERIFIED_YOUTUBE_SEARCHES[best]
    return {
        "title": entry["title"],
        "url": youtube_search_url(entry["query"]),
        "channel": entry.get("channel") or "YouTube",
        "kind": "search",
        "query": entry["query"],
    }


def youtube_search_url(query: str) -> str:
    cleaned = re.sub(r"\s+", " ", (query or "").strip())
    if not cleaned:
        raise ValueError("empty youtube search query")
    return f"https://www.youtube.com/results?search_query={quote_plus(cleaned)}"


def is_allowed_youtube_url(url: str) -> bool:
    """Accept only YouTube watch / results / youtu.be forms (no arbitrary domains)."""
    text = (url or "").strip()
    if not text.startswith("https://"):
        return False
    try:
        parsed = urlparse(text)
    except Exception:
        return False
    host = (parsed.netloc or "").lower()
    if host not in _YOUTUBE_HOSTS:
        return False
    path = parsed.path or ""
    if host == "youtu.be":
        return bool(re.fullmatch(r"/[\w-]{6,}", path))
    if path.startswith("/results"):
        return "search_query=" in (parsed.query or "")
    if path.startswith("/watch"):
        return "v=" in (parsed.query or "")
    if path.startswith("/playlist"):
        return "list=" in (parsed.query or "")
    return False


def build_grounded_resource(
    *,
    gap: str,
    search_query: str | None,
    preferred_title: str | None = None,
) -> dict[str, Any]:
    """
    Build a single resource payload that cannot invent unknown video IDs.

    Prefer curated catalog search/watch entry; otherwise emit a gap-bound search URL.
    """
    verified = catalog_match(gap)
    if verified:
        kind = verified.get("kind") or "search"
        return {
            "title": preferred_title or verified["title"],
            "resource_type": "youtube_video" if kind == "watch" else "youtube_search",
            "provider": verified.get("channel") or "YouTube",
            "url": verified["url"],
            "reason_recommended": (
                f"Curated YouTube learning entry for ATS gap '{gap}'. "
                "Only claim this skill on your resume when the experience is real."
            ),
            "metadata": {
                "source": "verified_youtube_catalog",
                "requirement": gap,
                "algorithm_version": ALGORITHM_VERSION,
                "grounding": "ats_evidence_only",
                "video_id_policy": "allowlist_or_search_only",
                "catalog_kind": kind,
            },
        }

    base_query = (search_query or "").strip()
    if normal_skill(gap) not in normal_skill(base_query):
        base_query = f"{gap} tutorial for beginners freecodecamp"
    url = youtube_search_url(base_query)
    return {
        "title": preferred_title or f"YouTube lessons: {gap}",
        "resource_type": "youtube_search",
        "provider": "YouTube",
        "url": url,
        "reason_recommended": (
            f"YouTube search grounded in ATS gap '{gap}'. "
            "No video ID was invented; choose a reputable free tutorial from the results."
        ),
        "metadata": {
            "source": "youtube_search_from_ats_gap",
            "requirement": gap,
            "search_query": base_query,
            "algorithm_version": ALGORITHM_VERSION,
            "grounding": "ats_evidence_only",
            "video_id_policy": "search_only_no_invented_ids",
        },
    }
