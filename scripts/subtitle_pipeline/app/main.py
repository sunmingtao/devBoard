import shutil
from pathlib import Path

from app.scanner import find_new_videos
from app.audio import extract_audio
from app.transcriber import transcribe_audio
from app.translator import translate_srt
from app.video import burn_subtitles
from app.notifier import send_success, send_failure
from app.config import ARCHIVE_DIR


def unique_archive_path(path: Path) -> Path:
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


def cleanup_completed_job(video_path: Path, job_dir: Path) -> Path:
    archived_video_path = unique_archive_path(video_path)
    shutil.move(str(video_path), archived_video_path)
    shutil.rmtree(job_dir, ignore_errors=True)
    print(f"Archived completed video: {archived_video_path}")
    print(f"Cleaned working directory: {job_dir}")
    return archived_video_path


def process_video(video_path):
    video_path = Path(video_path)

    try:
        audio_path = extract_audio(video_path)
        ja_srt_path = transcribe_audio(audio_path)
        zh_srt_path = translate_srt(ja_srt_path)
        output_path = burn_subtitles(video_path, zh_srt_path)

        archived_video_path = cleanup_completed_job(video_path, audio_path.parent)
        send_success(archived_video_path, output_path)

    except Exception as e:
        send_failure(video_path, str(e))
        raise


def main():
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
