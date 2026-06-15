"""
config.py
---------
Central place for settings shared across the project.

For now this just holds a few constants. As the project grows (for example
when we add the Google Photos uploader), credentials and other options will
live here too.
"""

# File extensions the scanner should look for.
ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".heic", ".mp4")

# Name of the SQLite database used to remember progress between runs.
DATABASE_FILE = "progress.db"

# How many bytes to read from the start of each file when hashing (64KB).
CHUNK_SIZE = 64 * 1024
