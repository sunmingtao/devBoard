import subprocess
from pathlib import Path
from typing import TypedDict

from app.config import WORKING_DIR

CHUNK_SECONDS = 300
OVERLAP_SECONDS = 15
MAX_SEGMENT_SECONDS = 15

class VideoChunk(TypedDict):
    file: Path
    chunk_index: int
    main_start: float
    main_end: float
    actual_start: float

def split_video_with_overlap(video_path: Path) -> list[VideoChunk]:
    print(f"Splitting video into chunks: {video_path}")
    chunk_dir = WORKING_DIR / video_path.stem / "chunks" / "video"
    chunk_dir.mkdir(parents=True, exist_ok=True)

    for file in chunk_dir.glob("chunk_*.mp4"):
        file.unlink()

    duration = get_video_duration(video_path)

    chunks: list[VideoChunk] = []
    start = 0.0
    index = 0

    while start < duration:
        chunk_start = max(0.0, start - OVERLAP_SECONDS)
        chunk_duration = CHUNK_SECONDS + OVERLAP_SECONDS
        chunk_file = chunk_dir / f"chunk_{index}.mp4"

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss", str(chunk_start),
                "-i", str(video_path),
                "-t", str(chunk_duration),
                "-map", "0",
                "-c", "copy",
                "-avoid_negative_ts", "make_zero",
                str(chunk_file),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        chunks.append(
            {
                "file": chunk_file,
                "chunk_index": index,
                "main_start": start,
                "main_end": min(start + CHUNK_SECONDS, duration),
                "actual_start": chunk_start,
            }
        )

        start += CHUNK_SECONDS
        index += 1

    return chunks


def get_video_duration(video_path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    return float(result.stdout.strip())
