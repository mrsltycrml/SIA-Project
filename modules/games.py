"""
Games module: enumerates local HTML5 games and supports metadata for embeds.
"""
import os
from typing import List, Dict

GAMES_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "games")

def _walk_games_dir() -> List[Dict]:
    games = []
    if not os.path.exists(GAMES_DIR):
        return games
    for name in os.listdir(GAMES_DIR):
        p = os.path.join(GAMES_DIR, name)
        if os.path.isdir(p):
            # expect index.html as entry point
            games.append({
                "slug": name,
                "title": name.replace("_", " ").title(),
                "path": f"/static/games/{name}/index.html",
                "local": True
            })
    # add an example external embed
    games.append({
        "slug": "space-invaders-embed",
        "title": "Space Invaders (Itch.io embed)",
        "embed_url": "https://itch.io/embed/123456?linkback=true",
        "local": False
    })
    return games

def list_games() -> List[Dict]:
    return _walk_games_dir()

def get_game(slug: str) -> Dict:
    for g in list_games():
        if g["slug"] == slug:
            return g
    return {}


