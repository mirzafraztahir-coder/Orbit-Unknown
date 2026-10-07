"""Orbit Unknown automation pipeline skeleton."""

from dataclasses import dataclass

@dataclass
class VideoJob:
    topic: str
    script: str
    duration_seconds: int = 35

def prepare_job(topic: str, script: str) -> VideoJob:
    if not topic.strip() or not script.strip():
        raise ValueError("Topic and script are required.")
    return VideoJob(topic=topic.strip(), script=script.strip())

if __name__ == "__main__":
    job = prepare_job(
        "What If Earth Stopped Spinning for 5 Seconds?",
        "Draft placeholder: final production script is supplied by the content stage."
    )
    print(job)
