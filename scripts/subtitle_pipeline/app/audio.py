import subprocess
from pathlib import Path

from app.config import WORKING_DIR


def _probe_duration(media_path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=nw=1:nk=1",
            str(media_path),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return float(result.stdout.strip())


def extract_audio(video_path: str | Path) -> Path:
    video_path = Path(video_path)
    print(f"Extracting audio from {video_path.name}...")
    job_dir = WORKING_DIR / video_path.stem
    job_dir.mkdir(parents=True, exist_ok=True)

    audio_path = job_dir / f"{video_path.stem}.wav"

    subprocess.run([
        "ffmpeg", "-y",
        "-fflags", "+genpts",
        "-i", str(video_path),
        "-map", "0:a:0",
        "-vn",
        "-af", "aresample=async=1000:first_pts=0,dynaudnorm",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        str(audio_path)
    ], check=True)

    video_duration = _probe_duration(video_path)
    audio_duration = _probe_duration(audio_path)
    if abs(video_duration - audio_duration) > 0.5:
        raise RuntimeError(
            f"Audio duration differs from video by more than 0.5 seconds: "
            f"video={video_duration:.3f}s audio={audio_duration:.3f}s"
        )

    return audio_path
