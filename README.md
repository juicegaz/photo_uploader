# Photo Uploader

A Python tool that scans a folder for photos and videos, removes duplicates,
and (eventually) uploads them to Google Photos.

> **Status:** scanning and deduplication work locally. Upload to Google Photos
> is not implemented yet.

---

## What it does

1. **Scan** — walks a folder (and all subfolders) and finds every photo/video
   with these extensions: `.jpg` `.jpeg` `.png` `.heic` `.mp4`
2. **Deduplicate** — reads the first 64 KB of each file, computes a hash, and
   flags any file whose content has already been seen as a duplicate
3. **Upload** — placeholder only (coming later)

---

## Requirements

- Python 3.8 or newer (no extra packages to install — everything used is built
  into Python)

Check your Python version in PowerShell:

```powershell
python --version
```

---

## How to run

All commands are run in PowerShell from the project folder
(`C:\Projects\PhotoUploader`).

### Full pipeline (scan + deduplicate)

```powershell
python main.py --dir "C:\path\to\your\photos"
```

### Just scan (no deduplication)

```powershell
python scanner.py --dir "C:\path\to\your\photos"
```

### Just deduplicate

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

Example — process only the first 10 files, quietly:

```powershell
python main.py --dir "C:\path\to\your\photos" --limit 10 --quiet
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
| `main.py` | Entry point — runs the full scan → deduplicate pipeline |
| `scanner.py` | Walks a folder and finds photo/video files |
| `deduplicator.py` | Hashes files and identifies duplicates |
| `config.py` | Shared constants (extensions, database name, chunk size) |
| `uploader.py` | Placeholder — Google Photos upload not yet implemented |
| `requirements.txt` | Dependencies (none active yet; future upload libs listed) |
| `progress.db` | Created automatically; stores hashes between runs (not in git) |

---

## Roadmap

- [x] Scan folders recursively
- [x] Deduplicate by file content
- [x] Resumable progress (SQLite)
- [ ] Upload unique files to Google Photos
