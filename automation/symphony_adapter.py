"""TikTok Symphony adapter.

This module deliberately contains no guessed API endpoint.
Enable it only after TikTok grants Symphony API access and supplies
the official authentication and endpoint documentation.
"""

import os

class SymphonyNotEnabled(RuntimeError):
    pass

def generate_video(script: str, **kwargs):
    if os.getenv("SYMPHONY_API_ENABLED") != "1":
        raise SymphonyNotEnabled(
            "Symphony API access is not enabled. Await TikTok allowlisting."
        )
    raise NotImplementedError(
        "Insert TikTok's official Symphony endpoint/auth flow after access is granted."
    )
