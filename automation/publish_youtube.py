import json
import os
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def missing():
    needed = ["YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"]
    return [k for k in needed if not os.getenv(k)]


def main(package_path: str, video_path: str):
    if missing():
        print("YouTube credentials not configured; skipping YouTube publish.")
        return

    package = json.loads(Path(package_path).read_text(encoding="utf-8"))
    meta = package["metadata"]

    creds = Credentials(
        token=None,
        refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["YOUTUBE_CLIENT_ID"],
        client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
        scopes=SCOPES,
    )
    creds.refresh(Request())
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": meta["title"][:100],
            "description": meta["caption"],
            "tags": ["space", "science", "what if", "shorts", "orbit unknown"],
            "categoryId": "27",
        },
        "status": {
            "privacyStatus": meta.get("privacyStatus", "public"),
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"YouTube upload progress: {int(status.progress() * 100)}%")
    print("YouTube uploaded:", response.get("id"))
    Path("outbox/youtube_result.json").write_text(json.dumps(response, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
