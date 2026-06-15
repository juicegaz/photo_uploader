"""
uploader.py
-----------
Uploads photos and videos to Google Photos using the Google Photos Library API.

How authentication works:
1. On the first run, the script reads credentials.json (your app's ID card
   downloaded from Google Cloud) and opens a browser window so you can log
   in and grant permission.
2. After you click "Allow", a token is saved to token.json so future runs
   skip the browser step entirely.
3. If the token expires mid-run, the session renews it silently.
"""

import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import AuthorizedSession, Request


# The permission we ask Google for.
# "appendonly" lets us upload new photos but not read or delete existing ones.
SCOPES = ["https://www.googleapis.com/auth/photoslibrary.appendonly"]

# Where the credential files live (in the same folder as the scripts).
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"

# Google Photos API endpoints.
UPLOAD_URL = "https://photoslibrary.googleapis.com/v1/uploads"
CREATE_URL = "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate"


def get_authorized_session():
    """
    Handle the OAuth2 login flow and return an authorized HTTP session.

    Think of the returned session as a web browser that is already logged in —
    every request it makes automatically includes your Google login token,
    and it silently refreshes that token if it expires during a long run.
    """
    credentials = None

    # If a token from a previous run exists, load it.
    if os.path.exists(TOKEN_FILE):
        credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If we have no credentials, or they are invalid, get new ones.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            # Token expired but we have a refresh token — silently renew it.
            credentials.refresh(Request())
        else:
            # First run (or token.json was deleted) — open the browser login page.
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            credentials = flow.run_local_server(port=0)

        # Save the token so the next run skips the browser step.
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(credentials.to_json())

    # AuthorizedSession is like requests.Session but automatically adds the
    # Authorization header (your login token) to every request we make.
    return AuthorizedSession(credentials)


def upload_file(session, file_path):
    """
    Upload a single file to Google Photos.

    Google requires two steps:
      Step 1 — Send the raw file bytes to get back an "upload token".
               (The upload token is Google's reference to the bytes you sent.)
      Step 2 — Use the upload token to register the file as a visible
               media item in your Google Photos library.

    Returns True if both steps succeeded, False otherwise.
    """
    filename = os.path.basename(file_path)

    # --- Step 1: send the file bytes ---
    upload_headers = {
        "Content-type": "application/octet-stream",  # raw binary data
        "X-Goog-Upload-File-Name": filename,
        "X-Goog-Upload-Protocol": "raw",
    }

    try:
        with open(file_path, "rb") as photo_file:
            response = session.post(
                UPLOAD_URL, headers=upload_headers, data=photo_file
            )
    except OSError:
        print("    -> ERROR: could not read file:", filename)
        return False

    if response.status_code != 200:
        print(
            "    -> ERROR: step 1 (bytes upload) failed for",
            filename,
            "(HTTP " + str(response.status_code) + ")",
        )
        return False

    # The response body is the upload token — a plain text string.
    upload_token = response.text

    # --- Step 2: register the bytes as a media item ---
    create_body = {
        "newMediaItems": [
            {
                "simpleMediaItem": {
                    "fileName": filename,
                    "uploadToken": upload_token,
                }
            }
        ]
    }

    response = session.post(CREATE_URL, json=create_body)

    if response.status_code != 200:
        print(
            "    -> ERROR: step 2 (media item creation) failed for",
            filename,
            "(HTTP " + str(response.status_code) + ")",
        )
        return False

    # Google embeds a status message in the JSON — check it really succeeded.
    result = response.json()
    item_status = (
        result.get("newMediaItemResults", [{}])[0].get("status", {})
    )
    if item_status.get("message") != "Success":
        print(
            "    -> ERROR:",
            item_status.get("message", "unknown error"),
            "for",
            filename,
        )
        return False

    return True


def upload_files(unique_files):
    """
    Upload a list of unique files to Google Photos.

    Input:
        unique_files -> the list of file dictionaries produced by deduplicator.py

    Returns two numbers: files successfully uploaded, files that failed.
    """
    if not unique_files:
        print("No files to upload.")
        return 0, 0

    print("Authenticating with Google Photos...")
    session = get_authorized_session()
    print("Authentication successful.")
    print()

    total = len(unique_files)
    succeeded = 0
    failed = 0

    print("Uploading", total, "files to Google Photos...")

    for file_number, file_info in enumerate(unique_files, start=1):
        file_path = file_info["path"]
        filename = file_info["filename"]

        print("[" + str(file_number) + "/" + str(total) + "] Uploading:", filename)

        success = upload_file(session, file_path)

        if success:
            print("    -> uploaded successfully.")
            succeeded += 1
        else:
            failed += 1

    return succeeded, failed


def print_upload_summary(succeeded, failed):
    """Print a friendly summary of the upload results."""
    print("Upload complete!")
    print("Successfully uploaded:", succeeded)
    print("Failed:               ", failed)
