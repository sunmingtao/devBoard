import subprocess
from pathlib import Path
import json
from fractions import Fraction
from app.config import WORKING_DIR


import json
import subprocess
from pathlib import Path
from fractions import Fraction


def _probe_stream_duration(path: Path, stream_selector: str) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-select_streams", stream_selector,
            "-show_entries", "stream=duration,duration_ts,time_base",
            "-of", "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)
    streams = data.get("streams", [])

    if streams:
        stream = streams[0]

        if stream.get("duration_ts") not in (None, "N/A") and stream.get("time_base"):
            return int(stream["duration_ts"]) * float(Fraction(stream["time_base"]))

        if stream.get("duration") not in (None, "N/A"):
            return float(stream["duration"])

    # fallback: format duration
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)
    duration = data.get("format", {}).get("duration")

    if duration in (None, "N/A"):
        raise ValueError(f"Could not probe duration: {path}")

    return float(duration)


def _probe_video_duration(path: Path) -> float:
    return _probe_stream_duration(path, "v:0")


def _probe_audio_duration(path: Path) -> float:
    return _probe_stream_duration(path, "a:0")


def extract_audio(video_path: str | Path) -> Path:
    video_path = Path(video_path)
    print(f"Extracting audio from {video_path.name}...")
    job_dir = WORKING_DIR / video_path.stem
    job_dir.mkdir(parents=True, exist_ok=True)

    audio_path = job_dir / f"{video_path.stem}.wav"     
    video_duration = _probe_video_duration(video_path)

    subprocess.run([
        "ffmpeg", "-y",
        "-fflags", "+genpts+discardcorrupt",
        "-err_detect", "ignore_err",
        "-i", str(video_path),
        "-map", "0:a:0",
        "-vn",
        "-af", "aresample=async=1:first_pts=0,dynaudnorm",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        str(audio_path)
    ], check=True)
    
    audio_duration = _probe_audio_duration(audio_path)
    if abs(video_duration - audio_duration) > 0.5:
        raise RuntimeError(
            f"Audio duration differs from video by more than 0.5 seconds: "
            f"video={video_duration:.3f}s audio={audio_duration:.3f}s"
        )

    return audio_path
