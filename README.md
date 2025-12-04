# Python Entertainment System (Flask)

- Features:
- Simple local email/password signup, login, logout (session-based, in-memory for dev)
- Music search via YouTube Music (`ytmusicapi`) (embed playback)
- TV channel streaming via IPTV-org API (direct stream playback)
- Playable HTML5 games (local + external embed)
- Uses Flask with templates and static files

## Setup (local)

1. Clone the repo.
2. Create a virtualenv and install requirements:

```bash
python -m venv venv
venv\\Scripts\\activate      # Windows
source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with (at minimum):

```
SECRET_KEY=a-random-secret
```

4. Run locally:

```bash
python api/app.py
```

Visit http://localhost:5000

## Deploying to Vercel

1. Push the repository to GitHub.
2. Connect GitHub repo to Vercel.
3. Add environment variables in Vercel dashboard (same names as `.env`).
4. Vercel will use `api/app.py` as the server entrypoint.

Note: Vercel Python runtimes can vary; alternatively deploy to DigitalOcean, Render, or Heroku for full WSGI support.

## Configuration

- No API keys required for video functionality! Videos use the free IPTV-org API (https://iptv-org.github.io/api/channels.json)
- `config.py` — Optional YouTube API key (not required for videos, may be used for other features)

## Environment variables
- `SECRET_KEY` — Flask secret key for sessions

## Notes
-- The app currently uses a simple in-memory auth store for signup/login. This is only suitable for local development. For production replace with a proper auth backend (database, Supabase, Auth0, etc).
-- Music searching uses `ytmusicapi` to query YouTube Music and returns YouTube embed URLs for playback.
-- Video/TV channel streaming uses IPTV-org API to access thousands of free TV channels from around the world. No API key required!

## Automate push to GitHub

For convenience there are two scripts to automate initializing git, committing, and pushing:

- PowerShell (Windows): `scripts/push_to_github.ps1`
- POSIX shell (Linux/macOS): `scripts/push_to_github.sh`

Usage (PowerShell example):

```powershell
# interactive - prompts for repo URL
.\scripts\push_to_github.ps1

# non-interactive - provide repo URL
.\scripts\push_to_github.ps1 -RepoUrl "https://github.com/your-username/your-repo.git"

# create repo using GitHub CLI (gh) and push
.\scripts\push_to_github.ps1 -CreateRepo -RepoName "SIA-Project" -Private:$false
```

Usage (bash):

```bash
# interactive
./scripts/push_to_github.sh

# non-interactive
./scripts/push_to_github.sh "https://github.com/your-username/your-repo.git"

# create repo using gh: ./scripts/push_to_github.sh "" true "SIA-Project" false
```

Security note:
- The scripts rely on `git` for pushing. For non-interactive authentication prefer `gh auth login` (GitHub CLI) or configure a credential helper; avoid embedding PATs directly in URLs.
