"""
deduplicator.py
---------------
Finds duplicate files based on their content (not just their name).

How it works:
1. For each file we read only the first 64KB and compute an MD5 hash.
   Hashing the whole file would be slow, and the first 64KB is usually
   enough to tell most photos/videos apart.
2. We remember every hash we have already seen in a small SQLite database
   called progress.db. Because the hashes are saved to disk, you can stop
   the script and run it again later without re-doing finished work.
3. Files whose hash we have not seen before are "unique". Files whose hash
   we have seen before are "duplicates".

This file is meant to be used together with scanner.py, which produces the
list of file information that we read here.
"""

import hashlib  # gives us the MD5 hashing function
import os       # lets us check the database file
import sqlite3  # the built-in SQLite database (no install needed)

# We import the scanner so we can run a full scan + dedupe in one go
# when this file is run directly from the command line.
import scanner


# The name of the database file that remembers which hashes we've seen.
DATABASE_FILE = "progress.db"

# How many bytes to read from the start of each file (64KB).
# 64 * 1024 = 65536 bytes.
CHUNK_SIZE = 64 * 1024


def compute_partial_hash(file_path):
    """
    Compute an MD5 hash of the first 64KB of a file.

    Returns the hash as a text string (for example "a1b2c3...").
    If the file cannot be read, returns None.
    """
    # Create a fresh MD5 "hasher" object.
    hasher = hashlib.md5()

    try:
        # Open the file in binary mode ("rb") because photos/videos are not text.
        with open(file_path, "rb") as open_file:
            # Read at most CHUNK_SIZE bytes from the beginning of the file.
            first_chunk = open_file.read(CHUNK_SIZE)
            # Feed those bytes into the hasher.
            hasher.update(first_chunk)
    except OSError:
        # OSError covers problems like the file being missing or unreadable.
        return None

    # hexdigest() turns the hash into a readable text string.
    return hasher.hexdigest()


def open_database():
    """
    Open (or create) the SQLite database and make sure our table exists.

    Returns the open database connection.
    """
    # connect() opens the database file, creating it if it doesn't exist yet.
    connection = sqlite3.connect(DATABASE_FILE)

    # Create a table to store the hashes we have already seen.
    # "IF NOT EXISTS" means it's safe to run this every time.
    # We store the file_hash (the MD5 text) and the file_path it came from.
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS seen_hashes (
            file_hash TEXT PRIMARY KEY,
            file_path TEXT
        )
        """
    )
    connection.commit()
    return connection


def hash_already_seen(connection, file_hash):
    """
    Return True if this hash is already stored in the database.
    """
    # Ask the database for any row whose file_hash matches.
    # The "?" is filled in safely with file_hash (this avoids SQL bugs).
    cursor = connection.execute(
        "SELECT file_hash FROM seen_hashes WHERE file_hash = ?",
        (file_hash,),
    )
    # fetchone() returns one matching row, or None if there were no matches.
    result = cursor.fetchone()
    return result is not None


def remember_hash(connection, file_hash, file_path):
    """
    Save a new hash (and the file it came from) into the database.
    """
    # "INSERT OR IGNORE" adds the row, but quietly does nothing if the hash
    # is somehow already there. This keeps the script safe to re-run.
    connection.execute(
        "INSERT OR IGNORE INTO seen_hashes (file_hash, file_path) VALUES (?, ?)",
        (file_hash, file_path),
    )
    connection.commit()


def deduplicate(files_found, quiet=False):
    """
    Split the scanned files into unique files and duplicates.

    Input:
        files_found -> the list of dictionaries produced by scanner.py
        quiet        -> if True, print only an occasional progress line
                        instead of one line per file. Defaults to False
                        (chatty mode, which is nice for small test runs).

    Returns two lists:
        unique_files     -> files whose content we had not seen before
        duplicate_files  -> files whose content matched something already seen
    """
    # Open the database that remembers hashes between runs.
    connection = open_database()

    # These lists will hold our results.
    unique_files = []
    duplicate_files = []

    # How many files we need to process in total. We use this to show
    # progress like "[3/50]" so you can see how far along we are.
    total_files = len(files_found)

    # In quiet mode we only print a progress line every so many files.
    # This keeps the screen readable when there are thousands of files.
    PROGRESS_EVERY = 100

    print("Starting de-duplication of", total_files, "files...")

    # enumerate() gives us a counter (file_number) along with each file.
    # We start counting at 1 so the first file shows as "[1/50]".
    for file_number, file_info in enumerate(files_found, start=1):
        file_path = file_info["path"]
        filename = file_info["filename"]

        # In chatty (non-quiet) mode, show every file we work on.
        if not quiet:
            print("[" + str(file_number) + "/" + str(total_files) + "]",
                  "Hashing:", filename)

        # Compute the hash of the first 64KB of the file.
        file_hash = compute_partial_hash(file_path)

        # If we couldn't read the file, skip it (don't crash the whole run).
        if file_hash is None:
            # Warnings are important, so we show them even in quiet mode.
            print("    -> WARNING: could not read file, skipping:", filename)
            continue

        # Decide whether this file is a duplicate or not.
        if hash_already_seen(connection, file_hash):
            # We've seen this content before -> it's a duplicate.
            if not quiet:
                print("    -> DUPLICATE (already seen this content), skipping.")
            duplicate_files.append(file_info)
        else:
            # New content -> it's unique. Remember it for next time.
            if not quiet:
                print("    -> UNIQUE, saving to database.")
            remember_hash(connection, file_hash, file_path)
            unique_files.append(file_info)

        # In quiet mode, print a short progress line now and then so the
        # user can tell the script is still working. We print every
        # PROGRESS_EVERY files, and also on the very last file.
        if quiet:
            reached_checkpoint = (file_number % PROGRESS_EVERY == 0)
            is_last_file = (file_number == total_files)
            if reached_checkpoint or is_last_file:
                print("  ...processed", file_number, "of", total_files, "files")

    # Close the database now that we're done with it.
    connection.close()

    return unique_files, duplicate_files


def print_dedupe_summary(files_found, unique_files, duplicate_files):
    """
    Print a friendly summary of the de-duplication results.
    """
    print("De-duplication complete!")
    print("Files scanned:    ", len(files_found))
    print("Duplicates skipped:", len(duplicate_files))
    print("Unique files left: ", len(unique_files))


def main():
    """
    Run a full scan + de-duplication from the command line:

        python deduplicator.py --dir /path/to/photos

    Note: hashes are remembered in progress.db. If you want a completely
    fresh run, delete progress.db first.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Scan a folder and find duplicate photos/videos."
    )
    parser.add_argument(
        "--dir",
        required=True,
        help="Path to the folder you want to scan.",
    )
    parser.add_argument(
        "--limit",
        type=int,      # turn the typed value into a whole number
        default=None,  # default is None, meaning "no limit, process them all"
        help="Only process the first N files (handy for quick test runs, "
             "for example --limit 50).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",  # makes --quiet a simple on/off switch
        help="Print only occasional progress instead of one line per file.",
    )
    arguments = parser.parse_args()

    # Make sure the folder exists before doing any work.
    if not os.path.isdir(arguments.dir):
        print("Error: that folder does not exist:", arguments.dir)
        return

    # Step 1: scan the folder (reusing the code from scanner.py).
    print("Scanning folder:", arguments.dir)
    files_found = scanner.scan_directory(arguments.dir)
    print("Files found:", len(files_found))

    # If the user asked for a limit, keep only the first N files.
    # Slicing a list with [:N] safely returns at most N items, even if the
    # list is shorter, so this can't crash on small folders.
    if arguments.limit is not None:
        files_found = files_found[:arguments.limit]
        print("Limiting this run to the first", len(files_found), "files.")

    # Step 2: separate unique files from duplicates.
    unique_files, duplicate_files = deduplicate(files_found, quiet=arguments.quiet)

    # Step 3: show the results.
    print_dedupe_summary(files_found, unique_files, duplicate_files)


# Only run main() when this file is started directly.
if __name__ == "__main__":
    main()
