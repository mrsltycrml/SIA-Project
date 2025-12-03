"""
Music module: search and return YouTube Music / YouTube results using `ytmusicapi`.
This replaces Spotify-based search. Each result includes:
- id: videoId
- name: track title
- artists: comma-separated artist names (best-effort)
- preview_url: always None (YouTube doesn't expose 30s preview mp3s)
- embed_url: YouTube embed URL usable in an iframe

Notes:
- Uses anonymous `YTMusic()` which works for public search. For user-scoped requests,
  `YTMusic` can be initialized with authenticated headers (not done here).
"""
import os
from typing import List, Dict

from ytmusicapi import YTMusic


def search_tracks(query: str, limit: int = 12) -> List[Dict]:
    """
    Perform a YouTube Music search and return a list of simplified track dicts.
    """
    try:
        ytmusic = YTMusic()
        items = ytmusic.search(query, filter="songs", limit=limit)
    except Exception as exc:
        # network or library error -> return empty list
        print(f"[music.search_tracks] YTMusic search failed: {exc}")
        items = []

    results: List[Dict] = []
    for it in items:
        video_id = it.get("videoId") or it.get("videoId", "")
        # artists may be a list of dicts or a single string depending on result shape
        artists_field = it.get("artists") or it.get("artist") or []
        if isinstance(artists_field, list):
            artists = ", ".join(a.get("name") for a in artists_field if a.get("name"))
        else:
            artists = str(artists_field)

        results.append({
            "id": video_id,
            "name": it.get("title"),
            "artists": artists,
            "preview_url": None,
            "embed_url": f"https://www.youtube.com/embed/{video_id}" if video_id else None
        })

    return results



