from .split_video import VideoChunk
from .config import WORKING_DIR
from pathlib import Path
import subprocess


def _get_media_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    return float(result.stdout.strip())


def extract_audio_chunks(video_path: Path, video_chunks: list[VideoChunk]) -> list[VideoChunk]:
    print(f"Extracting audio chunks for video: {video_path}")
    video_path = Path(video_path)
    chunk_dir = WORKING_DIR / video_path.stem / "chunks" / "audio"
    chunk_dir.mkdir(parents=True, exist_ok=True)

    for audio_file in chunk_dir.glob("chunk_*.wav"):
        audio_file.unlink()

    for video_chunk in video_chunks:
        chunk_file = Path(video_chunk["file"])
        chunk_duration = _get_media_duration(chunk_file)
        audio_path = chunk_dir / f"chunk_{video_chunk['chunk_index']}.wav"

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-fflags", "+genpts+discardcorrupt",
                "-err_detect", "ignore_err",
                "-i", str(chunk_file),
                "-map", "0:a:0",
                "-vn",
                "-af", "aresample=async=1:first_pts=0,dynaudnorm,apad",
                "-t", f"{chunk_duration:.6f}",
                "-ac", "1",
                "-ar", "16000",
                "-c:a", "pcm_s16le",
                str(audio_path),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        video_chunk["file"] = audio_path
    return video_chunks