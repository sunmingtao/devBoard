import shutil
from pathlib import Path

from app.scanner import find_new_videos
from app.audio import extract_audio
from app.transcriber import transcribe_audio
from app.translator import generate_bilingual_srt, translate_srt
from app.video import burn_subtitles
from app.notifier import send_success, send_failure
from app.config import ARCHIVE_DIR, OUTPUT_DIR


def unique_archive_path(path: str | Path) -> Path:
    path = Path(path)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    destination = ARCHIVE_DIR / path.name
    if not destination.exists():
        return destination

    counter = 1
    while True:
        candidate = ARCHIVE_DIR / f"{path.stem}_{counter}{path.suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def cleanup_completed_job(video_path: str | Path, job_dir: str | Path) -> Path:
    video_path = Path(video_path)
    job_dir = Path(job_dir)
    archived_video_path = unique_archive_path(video_path)
    shutil.move(str(video_path), archived_video_path)
    shutil.rmtree(job_dir, ignore_errors=True)
    print(f"Archived completed video: {archived_video_path}")
    print(f"Cleaned working directory: {job_dir}")
    return archived_video_path


def copy_subtitle_to_output(subtitle_path: str | Path) -> Path:
    subtitle_path = Path(subtitle_path)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / subtitle_path.name
    shutil.copyfile(subtitle_path, output_path)
    print(f"Copied subtitle to output: {output_path}")
    return output_path


def process_video(video_path: str | Path) -> None:
    video_path = Path(video_path)
    language = "ja" if "~" in video_path.name else "en"
    try:
        audio_path = extract_audio(video_path)
        srt_path = transcribe_audio(audio_path, language=language)
        zh_srt_path = translate_srt(srt_path, language=language)

        subtitle_path = (
            generate_bilingual_srt(srt_path, zh_srt_path)
            if language == "ja"
            else zh_srt_path
        )

        subtitle_output_path = copy_subtitle_to_output(subtitle_path)

        if language == "en":
            output_path = burn_subtitles(video_path, subtitle_path)
        else:
            output_path = subtitle_output_path  # No burning for Japanese videos
        archived_video_path = cleanup_completed_job(video_path, audio_path.parent)
        send_success(archived_video_path, output_path)

    except Exception as e:
        send_failure(video_path, str(e))
        raise


def main() -> None:
    videos = find_new_videos()
    failed_videos = []

    for video in videos:
        try:
            process_video(video)
        except Exception as exc:
            failed_videos.append((video, exc))
            print(f"Failed processing {video.name}; continuing with next video.")

    if failed_videos:
        print("\nFailed videos:")
        for video, exc in failed_videos:
            print(f"- {video.name}: {exc}")
