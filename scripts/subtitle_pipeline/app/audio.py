import subprocess
from pathlib import Path

from app.config import WORKING_DIR


def extract_audio(video_path):
    print(f"Extracting audio from {video_path.name}...")
    video_path = Path(video_path)
    job_dir = WORKING_DIR / video_path.stem
    job_dir.mkdir(parents=True, exist_ok=True)

    audio_path = job_dir / "audio.wav"

    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-af", "loudnorm",
        str(audio_path)
    ], check=True)

    return audio_path
