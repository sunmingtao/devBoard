# app/scanner.py

import time
import subprocess
from pathlib import Path

from app.config import INPUT_DIR


VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm"}


def is_video_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS


def is_file_stable(path: Path, wait_seconds: int = 30) -> bool:
    size1 = path.stat().st_size
    time.sleep(wait_seconds)
    size2 = path.stat().st_size

    return size1 == size2


def is_valid_video(path: Path) -> bool:
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-i", str(path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    return result.returncode == 0


def find_new_videos():
    """
    Scan input folder and return stable, valid video files.
    """

    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    videos = []

    for path in sorted(INPUT_DIR.iterdir()):

        if not is_video_file(path):
            continue

        print(f"Found video: {path.name}")

        if not is_file_stable(path):
            print(f"Skipping unstable file: {path.name}")
            continue

        if not is_valid_video(path):
            print(f"Skipping invalid video: {path.name}")
            continue

        videos.append(path)

    return videos