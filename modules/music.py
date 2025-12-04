from typing import List, Dict

import requests


def search_tracks(query: str, limit: int = 12) -> List[Dict]:
    """
    Search tracks using the public Deezer API.

    Returns a list of dicts shaped for the music template:
    - id: Deezer track id
    - name: track title
    - artists: artist name(s)
    - album: album title
    - image: album cover URL
    - preview_url: 30s MP3 preview (can be used in <audio>)
    - external_url: link to open track on Deezer
    """
    try:
        resp = requests.get(
            "https://api.deezer.com/search",
            params={"q": query, "limit": limit},
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        print(f"[music.search_tracks] Deezer search failed: {exc}")
        return []

    items = data.get("data", []) or []
    tracks: List[Dict] = []
    for item in items:
        artist = item.get("artist") or {}
        album = item.get("album") or {}
        tracks.append(
            {
                "id": item.get("id"),
                "name": item.get("title"),
                "artists": artist.get("name", ""),
                "album": album.get("title", ""),
                "image": album.get("cover_medium") or album.get("cover"),
                "preview_url": item.get("preview"),  # 30s MP3
                "external_url": item.get("link"),
            }
        )

    return tracks