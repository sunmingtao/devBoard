import shutil
from pathlib import Path

from app.scanner import find_new_media_files, is_audio_file
from app.audio import extract_audio
from app.transcriber import transcribe_audio
from app.translator import generate_bilingual_srt, translate_srt
from app.video import burn_subtitles
from app.notifier import send_success, send_failure
from app.config import ARCHIVE_DIR, OUTPUT_DIR, WORKING_DIR


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


def stage_audio_file(audio_path: str | Path) -> Path:
    audio_path = Path(audio_path)
    job_dir = WORKING_DIR / audio_path.stem
    job_dir.mkdir(parents=True, exist_ok=True)

    staged_audio_path = job_dir / audio_path.name
    if staged_audio_path.exists():
        staged_audio_path.unlink()

    try:
        staged_audio_path.hardlink_to(audio_path)
    except OSError:
        shutil.copyfile(audio_path, staged_audio_path)

    print(f"Using input audio directly: {audio_path.name}")
    return staged_audio_path


def process_media_file(media_path: str | Path) -> None:
    media_path = Path(media_path)
    language = "ja" if "~" in media_path.name else "en"
    try:
        input_is_audio = is_audio_file(media_path)
        audio_path = (
            stage_audio_file(media_path)
            if input_is_audio
            else extract_audio(media_path)
        )
        srt_path = transcribe_audio(audio_path, language=language)
        zh_srt_path = translate_srt(srt_path, language=language)

        subtitle_path = (
            generate_bilingual_srt(srt_path, zh_srt_path)
            if language == "ja"
            else zh_srt_path
        )

        subtitle_output_path = copy_subtitle_to_output(subtitle_path)

        if language == "en" and not input_is_audio:
            output_path = burn_subtitles(media_path, subtitle_path)
        else:
            output_path = subtitle_output_path
        archived_video_path = cleanup_completed_job(media_path, audio_path.parent)
        send_success(archived_video_path, output_path)

    except Exception as e:
        send_failure(media_path, str(e))
        raise


def main() -> None:
    media_files = find_new_media_files()

    failed_media_files = []

    for media_file in media_files:
        try:
            process_media_file(media_file)
        except Exception as exc:
            failed_media_files.append((media_file, exc))
            print(f"Failed processing {media_file.name}; continuing with next file.")

    if failed_media_files:
        print("\nFailed media files:")
        for media_file, exc in failed_media_files:
            print(f"- {media_file.name}: {exc}")
