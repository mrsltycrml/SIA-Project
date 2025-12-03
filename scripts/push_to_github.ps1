<#
.SYNOPSIS
  Automate initializing git (if needed), committing, and pushing to GitHub.

USAGE
  # interactive
  .\scripts\push_to_github.ps1

  # non-interactive (provide repo URL)
  .\scripts\push_to_github.ps1 -RepoUrl "https://github.com/your-username/your-repo.git"

  # create repo using gh and push
  .\scripts\push_to_github.ps1 -CreateRepo -RepoName "SIA-Project" -Private:$false

NOTES
  - Requires `git` to be installed. For repo creation, `gh` is optional.
  - If using HTTPS and you want non-interactive push, configure gh auth or provide credentials when prompted.
#>

param(
  [string]$RepoUrl,
  [switch]$CreateRepo,
  [string]$RepoName,
  [switch]$Private
)

function Exec($cmd) {
  Write-Host ">>> $cmd"
  $out = & cmd /c $cmd 2>&1
  $rc = $LASTEXITCODE
  return @{ rc = $rc; out = $out }
}

# Check git
$git = Exec("git --version")
if ($git.rc -ne 0) {
  Write-Error "git is not installed or not in PATH. Install Git (https://git-scm.com/download/win) and re-run."
  exit 1
}

Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Definition) | Out-Null
Set-Location ..  # move to project root

# Init repo if needed
if (-not (Test-Path .git)) {
  Exec("git init")
  Exec("git branch -M main")
}

# Create initial commit if there are changes
$status = Exec('git status --porcelain')
if ($status.out.Trim()) {
  Exec('git add .')
  Exec('git commit -m "Initial commit: Entertainment system"')
} else {
  Write-Host "No changes to commit."
}

if ($CreateRepo -and (Get-Command gh -ErrorAction SilentlyContinue)) {
  if (-not $RepoName) {
    $RepoName = Read-Host "Repo name (e.g. SIA-Project)"
  }
  if ($Private.IsPresent) {
    $privacy = "--private"
  } else {
    $privacy = "--public"
  }
  Write-Host "Creating GitHub repo using gh..."
  Exec("gh repo create $RepoName $privacy --source=. --remote=origin --push --confirm")
  exit 0
}

if (-not $RepoUrl) {
  $RepoUrl = Read-Host "Enter GitHub repo HTTPS URL (e.g. https://github.com/USER/REPO.git)"
}

# set remote (replace if exists)
$remote = Exec("git remote get-url origin")
if ($remote.rc -eq 0) {
  Write-Host "Remote 'origin' exists (replacing)..."
  Exec("git remote remove origin")
}
Exec("git remote add origin $RepoUrl")

Write-Host "Pushing to origin main..."
$push = Exec("git push -u origin main")
if ($push.rc -ne 0) {
  Write-Error "Push failed. If authentication failed, consider running 'gh auth login' or push manually."
  Write-Host $push.out
  exit $push.rc
}

Write-Host "Push succeeded."


