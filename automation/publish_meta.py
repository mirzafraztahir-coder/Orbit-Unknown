import json
import os
import sys
from pathlib import Path
import requests

GRAPH = "https://graph.facebook.com/v24.0"


def main(package_path: str, video_path: str):
    token = os.getenv("META_ACCESS_TOKEN")
    ig_user_id = os.getenv("META_IG_USER_ID")
    page_id = os.getenv("META_PAGE_ID")
    if not token:
        print("Meta access token not configured; skipping Meta publish.")
        return

    package = json.loads(Path(package_path).read_text(encoding="utf-8"))
    caption = package["metadata"]["caption"]

    # Instagram Reels publishing requires a publicly reachable video_url.
    # GitHub Actions local files are not public. In production, upload latest.mp4
    # to durable public storage first, then set PUBLIC_VIDEO_URL.
    public_video_url = os.getenv("PUBLIC_VIDEO_URL")
    results = {}

    if ig_user_id and public_video_url:
        create = requests.post(
            f"{GRAPH}/{ig_user_id}/media",
            data={
                "media_type": "REELS",
                "video_url": public_video_url,
                "caption": caption,
                "access_token": token,
            },
            timeout=60,
        )
        create.raise_for_status()
        creation_id = create.json()["id"]
        publish = requests.post(
            f"{GRAPH}/{ig_user_id}/media_publish",
            data={"creation_id": creation_id, "access_token": token},
            timeout=60,
        )
        publish.raise_for_status()
        results["instagram"] = publish.json()
        print("Instagram published:", results["instagram"])
    else:
        print("Instagram credentials or PUBLIC_VIDEO_URL missing; skipping Instagram publish.")

    if page_id and public_video_url:
        # Minimal Facebook Page video publish from hosted URL.
        fb = requests.post(
            f"{GRAPH}/{page_id}/videos",
            data={
                "file_url": public_video_url,
                "description": caption,
                "access_token": token,
            },
            timeout=60,
        )
        fb.raise_for_status()
        results["facebook"] = fb.json()
        print("Facebook published:", results["facebook"])
    else:
        print("Facebook Page ID or PUBLIC_VIDEO_URL missing; skipping Facebook publish.")

    Path("outbox/meta_result.json").write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
