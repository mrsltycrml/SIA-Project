"""
Video module: search IPTV TV channels using the IPTV-org API.
"""
from typing import List, Dict, Optional
import requests

IPTV_CHANNELS_URL = "https://iptv-org.github.io/api/channels.json"
IPTV_STREAMS_URL = "https://iptv-org.github.io/api/streams.json"
IPTV_COUNTRIES_URL = "https://iptv-org.github.io/api/countries.json"

# Cache for data
_channels_cache = None
_streams_cache = None
_countries_cache = None
_channel_stream_map = None


def _load_channels() -> List[Dict]:
    """Load channels from IPTV API with caching."""
    global _channels_cache
    if _channels_cache is not None:
        return _channels_cache
    
    try:
        r = requests.get(IPTV_CHANNELS_URL, timeout=30)
        r.raise_for_status()
        _channels_cache = r.json()
        print(f"[videos._load_channels] Loaded {len(_channels_cache)} channels from IPTV API")
        return _channels_cache
    except Exception as exc:
        print(f"[videos._load_channels] Failed to load channels: {exc}")
        return []


def _load_streams() -> List[Dict]:
    """Load streams from IPTV API with caching."""
    global _streams_cache
    if _streams_cache is not None:
        return _streams_cache
    
    try:
        r = requests.get(IPTV_STREAMS_URL, timeout=30)
        r.raise_for_status()
        _streams_cache = r.json()
        print(f"[videos._load_streams] Loaded {len(_streams_cache)} streams from IPTV API")
        return _streams_cache
    except Exception as exc:
        print(f"[videos._load_streams] Failed to load streams: {exc}")
        return []


def _load_countries() -> Dict[str, str]:
    """Load countries mapping (code -> name) with caching."""
    global _countries_cache
    if _countries_cache is not None:
        return _countries_cache
    
    try:
        r = requests.get(IPTV_COUNTRIES_URL, timeout=30)
        r.raise_for_status()
        countries_data = r.json()
        # Convert list to dict: code -> name
        _countries_cache = {c.get("code", ""): c.get("name", "") for c in countries_data if c.get("code")}
        print(f"[videos._load_countries] Loaded {len(_countries_cache)} countries from IPTV API")
        return _countries_cache
    except Exception as exc:
        print(f"[videos._load_countries] Failed to load countries: {exc}")
        return {}


def _build_channel_stream_map() -> Dict[str, List[Dict]]:
    """Build a map of channel_id -> list of streams."""
    global _channel_stream_map
    if _channel_stream_map is not None:
        return _channel_stream_map
    
    streams = _load_streams()
    _channel_stream_map = {}
    
    for stream in streams:
        channel_id = stream.get("channel")
        if channel_id:
            if channel_id not in _channel_stream_map:
                _channel_stream_map[channel_id] = []
            _channel_stream_map[channel_id].append(stream)
    
    print(f"[videos._build_channel_stream_map] Mapped {len(_channel_stream_map)} channels with streams")
    return _channel_stream_map


def search_videos(
    query: str = "",
    max_results: int = 12,
    country: Optional[str] = None,
    category: Optional[str] = None
) -> List[Dict]:
    """
    Search IPTV channels matching the given query, country, and category.
    
    Args:
        query: Search query (searches in channel name)
        max_results: Maximum number of results to return
        country: Filter by country code (e.g., 'US', 'GB') or country name
        category: Filter by category (e.g., 'general', 'sports', 'news', 'movies')
    
    Returns:
        List of channel dictionaries with id, title, description, thumbnail, and stream_url.
    """
    channels = _load_channels()
    streams_map = _build_channel_stream_map()
    countries_map = _load_countries()
    
    if not channels:
        return []
    
    query_lower = query.lower().strip() if query else ""
    country_lower = country.lower().strip() if country else ""
    category_lower = category.lower().strip() if category else ""
    
    results: List[Dict] = []
    
    for channel in channels:
        channel_id = channel.get("id", "")
        
        # Skip if no streams available for this channel
        if channel_id not in streams_map or not streams_map[channel_id]:
            continue
        
        # Get the first/best stream URL
        stream = streams_map[channel_id][0]
        stream_url = stream.get("url", "")
        if not stream_url:
            continue
        
        # Extract channel information
        name = channel.get("name", "Unknown Channel")
        name_lower = name.lower()
        
        # Country filtering
        channel_country_code = channel.get("country", "")
        channel_country_name = countries_map.get(channel_country_code, "").lower() if channel_country_code else ""
        
        if country_lower:
            # Match by country code (exact match, case-insensitive)
            # or by country name (contains match, case-insensitive)
            country_match = False
            if channel_country_code:
                country_match = country_lower == channel_country_code.lower()
            if not country_match and channel_country_name:
                country_match = country_lower in channel_country_name or channel_country_name.startswith(country_lower)
            if not country_match:
                continue
        
        # Category filtering
        channel_categories = [cat.lower() for cat in channel.get("categories", [])]
        if category_lower:
            if category_lower not in channel_categories:
                continue
        
        # Query filtering (search in name)
        if query_lower:
            if query_lower not in name_lower:
                continue
        
        # Build description
        desc_parts = []
        if channel_country_code and channel_country_code in countries_map:
            desc_parts.append(f"Country: {countries_map[channel_country_code]}")
        if channel_categories:
            desc_parts.append(f"Category: {', '.join([c.capitalize() for c in channel_categories])}")
        description = " | ".join(desc_parts) if desc_parts else "TV Channel"
        
        # Get logo/thumbnail (channels.json doesn't have logo, but we can try to get it from streams)
        logo = channel.get("logo", "")
        thumbnail = logo if logo else ""
        
        results.append(
            {
                "id": channel_id,
                "title": name,
                "description": description,
                "thumbnail": thumbnail,
                "embed_url": stream_url,
                "stream_url": stream_url,
                "country": countries_map.get(channel_country_code, channel_country_code) if channel_country_code else "",
                "country_code": channel_country_code,
                "categories": channel_categories,
            }
        )
        
        # Limit results
        if len(results) >= max_results:
            break
    
    return results


def get_available_countries() -> List[Dict[str, str]]:
    """Get list of available countries with codes and names."""
    countries_map = _load_countries()
    return [{"code": code, "name": name} for code, name in sorted(countries_map.items(), key=lambda x: x[1])]


def get_available_categories() -> List[str]:
    """Get list of available categories."""
    channels = _load_channels()
    categories = set()
    for channel in channels:
        categories.update(channel.get("categories", []))
    return sorted([c for c in categories if c])

