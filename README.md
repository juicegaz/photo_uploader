# Photo Uploader

A Python tool that scans a folder for photos and videos, removes duplicates,
and uploads them to Google Photos.

> **Status:** all three steps are implemented and working.

---

## What it does

1. **Scan** — walks a folder (and all subfolders) and finds every photo/video
   with these extensions: `.jpg` `.jpeg` `.png` `.heic` `.mp4`
2. **Deduplicate** — reads the first 64 KB of each file, computes a hash, and
   flags any file whose content has already been seen as a duplicate
3. **Upload** — sends unique files to your Google Photos library via the
   Google Photos Library API

---

## Requirements

- Python 3.8 or newer
- Two packages (install once with the command below):

```powershell
pip install -r requirements.txt
```

Check your Python version in PowerShell:

```powershell
python --version
```

---

## First-time Google Photos setup

Before the uploader can talk to your Google Photos account you need to create
a credentials file. This is a one-time step.

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and sign
   in with your Google account
2. Create a new project (name it anything, e.g. `photo-uploader`)
3. Search for **"Photos Library API"** and enable it
4. Go to **APIs & Services → Credentials → + Create Credentials → OAuth client ID**
   - If prompted, configure the consent screen first (choose External, fill in
     app name and your email, save, then come back)
   - Application type: **Desktop app**
5. Download the JSON file and save it to this folder as **`credentials.json`**

On the **first run** a browser window will open asking you to log in and click
Allow. After that a `token.json` file is saved and the browser step is skipped
on all future runs.

> Both `credentials.json` and `token.json` are listed in `.gitignore` and will
> never be committed to the repository.

---

## How to run

All commands are run in PowerShell from the project folder
(`C:\Projects\PhotoUploader`).

### Full pipeline (scan + deduplicate + upload)

```powershell
python main.py --dir "C:\path\to\your\photos"
```

### Just scan (no deduplication or upload)

```powershell
python scanner.py --dir "C:\path\to\your\photos"
```

### Just deduplicate (no upload)

```powershell
python deduplicator.py --dir "C:\path\to\your\photos"
```

---

## Options

| Option | What it does |
|---|---|
| `--dir <path>` | **Required.** The folder to scan. |
| `--limit N` | Only process the first N files. Useful for a quick test run. |
| `--quiet` | Print a short progress line every 100 files instead of one line per file. |

Example — test with just the first 5 files:

```powershell
python main.py --dir "C:\path\to\your\photos" --limit 5
```

---

## How deduplication works

- The script reads only the **first 64 KB** of each file to compute an MD5
  hash. This is fast but means two completely different files that happen to
  share identical first 64 KB would be treated as duplicates (very unlikely
  for real photos, acceptable for now).
- Hashes are saved in a local file called **`progress.db`** (SQLite database).
  This means if you stop the script halfway through, the next run picks up
  where it left off without re-hashing already-processed files.
- **To start completely fresh**, delete `progress.db` before running:
  ```powershell
  Remove-Item progress.db
  ```

---

## Files in this project

| File | Purpose |
|---|---|
| `main.py` | Entry point — runs the full scan → deduplicate → upload pipeline |
| `scanner.py` | Walks a folder and finds photo/video files |
| `deduplicator.py` | Hashes files and identifies duplicates |
| `uploader.py` | Authenticates with Google and uploads unique files |
| `config.py` | Shared constants (extensions, database name, chunk size) |
| `requirements.txt` | Python packages to install (`pip install -r requirements.txt`) |
| `credentials.json` | Your Google Cloud OAuth credentials — **not in git** |
| `token.json` | Your saved login token — created automatically, **not in git** |
| `progress.db` | Dedup progress database — created automatically, **not in git** |

---

## Roadmap

- [x] Scan folders recursively
- [x] Deduplicate by file content
- [x] Resumable progress (SQLite)
- [x] Upload unique files to Google Photos
