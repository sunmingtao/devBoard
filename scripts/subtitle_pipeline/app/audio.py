import subprocess
from pathlib import Path

from app.config import WORKING_DIR


def extract_audio(video_path: str | Path) -> Path:
    video_path = Path(video_path)
    print(f"Extracting audio from {video_path.name}...")
    job_dir = WORKING_DIR / video_path.stem
    job_dir.mkdir(parents=True, exist_ok=True)

    audio_path = job_dir / "audio.wav"

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

    return audio_path
