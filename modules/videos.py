"""
Video module: search Vimeo videos using a personal access token.
"""
import os
from typing import List, Dict

import requests

VIMEO_SEARCH_URL = "https://api.vimeo.com/videos"
VIMEO_ACCESS_TOKEN = os.environ.get("VIMEO_ACCESS_TOKEN")


def search_videos(query: str, max_results: int = 12) -> List[Dict]:
    """
    Search Vimeo for videos matching the given query.

    Requires a Vimeo personal access token in the VIMEO_ACCESS_TOKEN env var.
    """
    if not VIMEO_ACCESS_TOKEN:
        print("[videos.search_videos] VIMEO_ACCESS_TOKEN is not set; returning no results.")
        return []

    headers = {
        "Authorization": f"Bearer {VIMEO_ACCESS_TOKEN}",
        "Accept": "application/vnd.vimeo.*+json;version=3.4",
    }
    params = {
        "query": query,
        "per_page": max_results,
        "sort": "relevant",
        "direction": "desc",
    }

    try:
        r = requests.get(VIMEO_SEARCH_URL, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception as exc:
        print(f"[videos.search_videos] Vimeo search failed: {exc}")
        return []

    items = data.get("data", []) or []
    results: List[Dict] = []
    for it in items:
        uri = it.get("uri", "")  # e.g. "/videos/123456789"
        video_id = uri.split("/")[-1] if uri else None
        name = it.get("name")
        description = it.get("description")
        pictures = (it.get("pictures") or {}).get("sizes") or []
        thumb = pictures[-1].get("link") if pictures else None

        if not video_id:
            continue

        results.append(
            {
                "id": video_id,
                "title": name,
                "description": description,
                "thumbnail": thumb,
                "embed_url": f"https://player.vimeo.com/video/{video_id}",
            }
        )

    return results



