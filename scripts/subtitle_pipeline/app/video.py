# app/video.py

import subprocess
from pathlib import Path

from app.config import OUTPUT_DIR


def burn_subtitles(video_path: Path, subtitle_path: Path) -> Path:
    """
    Burn subtitles into video permanently.
    The output video cannot turn subtitles off.
    """
    print(f"Burning subtitles into video: {video_path.name} with subtitle {subtitle_path.name}...")

    video_path = Path(video_path)
    subtitle_path = Path(subtitle_path)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / f"{video_path.stem}_zh_burned.mp4"

    subtitle_filter = (
        f"subtitles='{subtitle_path}':"
        f"force_style='FontName=Noto Sans CJK SC,FontSize=24,"
        f"PrimaryColour=&H00FFFFFF&,OutlineColour=&H00000000&,"
        f"BorderStyle=1,Outline=2,Shadow=0,MarginV=15'"
    )

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i", str(video_path),
            "-vf", subtitle_filter,
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "veryfast",
            "-c:a", "copy",
            str(output_path),
        ],
        check=True,
    )

    return output_path