"""
main.py
-------
The entry point that ties the whole project together.

For now it runs a scan followed by de-duplication. Uploading is not wired
up yet because we are testing locally first.

Run it like this:

    python main.py --dir /path/to/photos
"""

import argparse
import os

import scanner
import deduplicator


def main():
    # Read the --dir option from the command line.
    parser = argparse.ArgumentParser(
        description="Scan a folder for photos/videos and find duplicates."
    )
    parser.add_argument(
        "--dir",
        required=True,
        help="Path to the folder you want to process.",
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

    # Make sure the folder exists.
    if not os.path.isdir(arguments.dir):
        print("Error: that folder does not exist:", arguments.dir)
        return

    # Step 1: scan.
    print("Scanning folder:", arguments.dir)
    files_found = scanner.scan_directory(arguments.dir)
    scanner.print_summary(files_found)

    # If the user asked for a limit, keep only the first N files.
    # Slicing a list with [:N] safely returns at most N items, even if the
    # list is shorter, so this can't crash on small folders.
    if arguments.limit is not None:
        files_found = files_found[:arguments.limit]
        print("Limiting this run to the first", len(files_found), "files.")

    print()  # blank line for readability

    # Step 2: de-duplicate.
    unique_files, duplicate_files = deduplicator.deduplicate(
        files_found, quiet=arguments.quiet
    )
    deduplicator.print_dedupe_summary(files_found, unique_files, duplicate_files)

    # Step 3: upload (not implemented yet).
    print()
    print("Uploading is not implemented yet — local testing only for now.")


if __name__ == "__main__":
    main()
