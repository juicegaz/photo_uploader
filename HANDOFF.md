# Project Handoff: photo_uploader

## Context
I'm a Python beginner. Keep code simple/readable over clever, add clear
comments explaining each function, and give exact terminal commands to run
things. Platform: Windows 11, PowerShell. Project dir: C:\Projects\PhotoUploader

## What the project is
A Python tool to scan a folder for photos/videos, remove duplicates, and
(eventually) upload to Google Photos. Building/testing locally first.

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
- main.py           — DONE. Pipeline: scan -> dedupe. Supports --dir, --limit,
                      --quiet. Upload step is a placeholder message.
- config.py         — Shared constants (ALLOWED_EXTENSIONS, DATABASE_FILE,
                      CHUNK_SIZE).
- uploader.py       — Intentionally EMPTY placeholder. Google Photos upload
                      NOT implemented yet (deliberate — testing locally first).
- requirements.txt  — No active deps (stdlib only). google-auth-oauthlib and
                      google-api-python-client commented out for future uploader.
- .gitignore        — Ignores __pycache__, *.pyc, progress.db, venv dirs,
                      .claude/settings.local.json, editor/OS noise.

## Key technical notes
- Dedup uses FIRST 64KB only — fast but two different files sharing an
  identical first 64KB could be false-flagged as dupes. Acceptable for now;
  could add full-file hash tie-breaker later if needed.
- progress.db persists hashes across runs. After a --limit test run, those
  files count as duplicates in later runs. Delete progress.db for a clean run.

## Git / GitHub state — DONE
- Local git repo initialized (branch: main). First commit made (7c426d2):
  "Initial commit: photo scanner and deduplicator".
- Pushed to GitHub: https://github.com/juicegaz/photo_uploader (remote "origin",
  tracking set up, so plain `git push` works now).
- Git identity: name juicegaz, GitHub username juicegaz.

## Everyday git workflow I'm learning
  git add .
  git commit -m "message"
  git push
Auditing: git status / git diff / git log --oneline, plus GitHub Commits tab.

## Possible next steps (not yet done)
- Practice round: add a README.md and walk through status->diff->add->commit->push.
- Run a real end-to-end test (could create dummy test files).
- Eventually implement uploader.py (Google Photos).
