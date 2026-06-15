"""
scanner.py
----------
Walks a directory tree and finds photo/video files.

For each matching file it collects some basic information (path, name,
size, last-modified date) and returns the results as a list of
dictionaries.

You can also run this file directly from the command line:

    python scanner.py --dir /path/to/photos
"""

import argparse  # builds the command-line interface (the --dir option)
import os        # lets us walk directories and read file info
from datetime import datetime  # turns a raw timestamp into a readable date


# The file extensions we care about. We store them lowercase so that we
# can compare them without worrying about upper/lower case (.JPG vs .jpg).
ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".heic", ".mp4")


def get_file_extension(filename):
    """
    Return the lowercase extension of a filename, including the dot.

    Example: "Photo.JPG" -> ".jpg"
    """
    # os.path.splitext splits "name.ext" into ("name", ".ext").
    # [1] grabs the ".ext" part, and .lower() makes it lowercase.
    return os.path.splitext(filename)[1].lower()


def scan_directory(root_dir):
    """
    Recursively walk root_dir and find all photo/video files.

    Returns a list of dictionaries. Each dictionary describes one file:
        {
            "path":          full path to the file,
            "filename":      just the file's name,
            "size_bytes":    size of the file in bytes,
            "modified_date": last modified date as a string,
        }
    """
    # This list will hold one dictionary per file we find.
    files_found = []

    # os.walk visits every folder under root_dir. On each step it gives us:
    #   current_folder -> the folder we are currently looking inside
    #   subfolders     -> list of folder names inside it (we don't need this)
    #   filenames      -> list of file names inside it
    for current_folder, subfolders, filenames in os.walk(root_dir):

        # Look at every file in the current folder.
        for filename in filenames:

            # Skip files whose extension is not in our allowed list.
            if get_file_extension(filename) not in ALLOWED_EXTENSIONS:
                continue

            # Build the full path by joining the folder and the file name.
            full_path = os.path.join(current_folder, filename)

            # os.path.getsize returns the file size in bytes.
            size_bytes = os.path.getsize(full_path)

            # os.path.getmtime returns the "last modified" time as a number
            # (seconds since 1970). We convert it to a readable date string.
            modified_timestamp = os.path.getmtime(full_path)
            modified_date = datetime.fromtimestamp(modified_timestamp)
            modified_date_text = modified_date.strftime("%Y-%m-%d %H:%M:%S")

            # Store everything we collected in a dictionary.
            file_info = {
                "path": full_path,
                "filename": filename,
                "size_bytes": size_bytes,
                "modified_date": modified_date_text,
            }

            # Add this file's dictionary to our results list.
            files_found.append(file_info)

    return files_found


def print_summary(files_found):
    """
    Print a human-friendly summary of the scan results.

    Shows the total number of files and a breakdown by file extension.
    """
    total_files = len(files_found)
    print("Scan complete!")
    print("Total files found:", total_files)

    # If we found nothing, there is no breakdown to show.
    if total_files == 0:
        return

    # Count how many files we found for each extension.
    # We use a dictionary like {".jpg": 12, ".png": 3}.
    counts_by_extension = {}
    for file_info in files_found:
        extension = get_file_extension(file_info["filename"])
        # If we've seen this extension before, add 1. Otherwise start at 1.
        if extension in counts_by_extension:
            counts_by_extension[extension] = counts_by_extension[extension] + 1
        else:
            counts_by_extension[extension] = 1

    # Print the breakdown, one line per extension.
    print("Breakdown by file type:")
    for extension in sorted(counts_by_extension):
        count = counts_by_extension[extension]
        print("  " + extension + ": " + str(count))


def main():
    """
    Handle the command line and run a scan.

    This function runs only when you start the file directly, for example:
        python scanner.py --dir /path/to/photos
    """
    # argparse reads the options the user typed after the script name.
    parser = argparse.ArgumentParser(
        description="Scan a folder for photos and videos."
    )
    parser.add_argument(
        "--dir",
        required=True,  # the user must provide a folder
        help="Path to the folder you want to scan.",
    )
    arguments = parser.parse_args()

    # Make sure the folder actually exists before we try to scan it.
    if not os.path.isdir(arguments.dir):
        print("Error: that folder does not exist:", arguments.dir)
        return

    # Do the scan and print the summary.
    print("Scanning folder:", arguments.dir)
    files_found = scan_directory(arguments.dir)
    print_summary(files_found)


# This line means: "only run main() if this file was started directly".
# It does NOT run when another file (like deduplicator.py) imports us.
if __name__ == "__main__":
    main()
