# Project Handoff: photo_uploader

## Context
I'm a Python beginner. Keep code simple/readable over clever, add clear
comments explaining each function, and give exact terminal commands to run
things. Platform: Windows 11, PowerShell. Project dir: C:\Projects\PhotoUploader

## What the project is
A Python tool to scan a folder for photos/videos, remove duplicates, and
upload unique files to Google Photos. All three steps are now implemented.

## Files (all in C:\Projects\PhotoUploader)
- scanner.py        — DONE. Recursively walks a dir, finds .jpg/.jpeg/.png/
                      .heic/.mp4, collects path/filename/size_bytes/
                      modified_date per file, returns list of dicts. Has CLI:
                      `python scanner.py --dir <path>` prints total + breakdown
                      by file type.
- deduplicator.py   — DONE. MD5-hashes first 64KB of each file (speed),
                      tracks seen hashes in SQLite progress.db so runs can
                      resume. Returns (unique_files, duplicate_files). Prints
                      per-file progress. CLI supports --dir, --limit N (process
                      only first N files), --quiet (checkpoint every 100 files
                      instead of per-file; warnings still print).
- main.py           — DONE. Full pipeline: scan -> dedupe -> upload. Supports
                      --dir, --limit, --quiet. All three steps wired up.
- uploader.py       — DONE. OAuth2 auth flow (browser popup on first run,
                      token.json saved for subsequent runs, auto-refresh on
                      expiry). Two-step Google Photos upload: POST bytes to get
                      upload token, then POST to create media item. Functions:
                      get_authorized_session(), upload_file(), upload_files(),
                      print_upload_summary().
- config.py         — Shared constants (ALLOWED_EXTENSIONS, DATABASE_FILE,
                      CHUNK_SIZE).
- requirements.txt  — Two active deps: google-auth-oauthlib,
                      google-api-python-client. Install with:
                      `pip install -r requirements.txt`
- .gitignore        — Ignores __pycache__, *.pyc, progress.db, venv dirs,
                      credentials.json, token.json,
                      .claude/settings.local.json, editor/OS noise.

## Key technical notes
- Dedup uses FIRST 64KB only — fast but two different files sharing an
  identical first 64KB could be false-flagged as dupes. Acceptable for now;
  could add full-file hash tie-breaker later if needed.
- progress.db persists hashes across runs. After a --limit test run, those
  files count as duplicates in later runs. Delete progress.db for a clean run.
- Auth: credentials.json = Google Cloud OAuth client ID/secret (app's ID card,
  downloaded from GCP Console once). token.json = user's login token, created
  automatically on first run after browser approval. Neither file is in git.
- Upload scope is "appendonly" — can upload but cannot read or delete existing
  photos. This is intentional (least privilege).
- Google Photos upload is two steps: (1) POST raw bytes → get upload token,
  (2) POST upload token → create media item. Both must succeed.

## Git / GitHub state
- GitHub repo: https://github.com/juicegaz/photo_uploader (public)
- Branch: main. Remote "origin" set up, so plain `git push` works.
- Git identity: juicegaz
- Recent commits:
    09a9a70  Add README with usage instructions and project overview
    5a65786  Ignore Google API credentials and token files
    (uploader changes not yet committed — do that next)

## Everyday git workflow I'm learning
  git status           <- see what changed
  git diff --cached    <- see what's staged (after git add)
  git add <file>
  git commit -m "message"
  git push
Auditing: git status / git diff / git log --oneline, plus GitHub Commits tab.

## Possible next steps (not yet done)
- Commit and push the uploader work (uploader.py, main.py, requirements.txt,
  README.md changes).
- End-to-end test: run `python main.py --dir <real photo folder> --limit 5`
  and confirm photos appear in Google Photos.
- Handle already-uploaded files: currently the script re-uploads unique files
  on every run. Could track uploaded file paths in progress.db to skip them.
- Add quiet mode to uploader (currently always prints per-file).
