"""
Video module: search YouTube videos using API key.
"""
import requests
from typing import List, Dict

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v={}"

def search_videos(query: str, api_key: str, max_results: int = 12) -> List[Dict]:
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": api_key,
    }
    r = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=10)
    r.raise_for_status()
    items = r.json().get("items", [])
    results = []
    for it in items:
        vid = it["id"]["videoId"]
        snippet = it["snippet"]
        results.append({
            "id": vid,
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url"),
            "embed_url": f"https://www.youtube.com/embed/{vid}"
        })
    return results


