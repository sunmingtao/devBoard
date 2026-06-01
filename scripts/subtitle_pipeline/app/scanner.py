# app/scanner.py

import time
import subprocess
from pathlib import Path

from app.config import INPUT_DIR


VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm"}
AUDIO_EXTENSIONS = {".aac", ".flac", ".m4a", ".mp3", ".ogg", ".opus", ".wav", ".wma"}
MEDIA_EXTENSIONS = VIDEO_EXTENSIONS | AUDIO_EXTENSIONS


def is_video_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS


def is_audio_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS


def is_media_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in MEDIA_EXTENSIONS


def is_file_stable(path: Path, wait_seconds: int = 30) -> bool:
    try:
        size1 = path.stat().st_size
        time.sleep(wait_seconds)
        size2 = path.stat().st_size
    except FileNotFoundError:
        return False

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


def find_new_media_files() -> list[Path]:
    """
    Scan input folder and return stable, valid media files.
    """

    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    media_files = []

    for path in sorted(INPUT_DIR.iterdir()):

        if not is_media_file(path):
            continue

        print(f"Found media: {path.name}")

        if not is_file_stable(path):
            print(f"Skipping unstable file: {path.name}")
            continue

        if not is_valid_video(path):
            print(f"Skipping invalid media: {path.name}")
            continue

        media_files.append(path)

    return media_files
