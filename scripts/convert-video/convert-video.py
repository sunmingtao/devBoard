#!/usr/bin/env python3

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


RECIPIENT = "sunmingtao@gmail.com"
MAX_JOBS = int(os.environ.get("MAX_JOBS", "4"))
CONVERT_TIMEOUT = os.environ.get("CONVERT_TIMEOUT", "15m")
SUBTITLE_FONT = os.environ.get("SUBTITLE_FONT", "Noto Sans CJK SC")
BASE_DIR = Path(os.environ.get("CONVERT_VIDEO_BASE_DIR", Path(__file__).resolve().parent)).resolve()
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
ARCHIVED_DIR = BASE_DIR / "archived"
VIDEO_EXTENSIONS = {
    ".3g2",
    ".3gp",
    ".asf",
    ".avi",
    ".flv",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpeg",
    ".mpg",
    ".mts",
    ".m2ts",
    ".ogv",
    ".rm",
    ".rmvb",
    ".ts",
    ".vob",
    ".webm",
    ".wmv",
}
TEXT_SUBTITLE_CODECS = {"ass", "mov_text", "ssa", "subrip", "text", "webvtt"}
CHINESE_LANGUAGE_RE = re.compile(r"^(chi|zho|zh)([-_].*)?$")


@dataclass(frozen=True)
class VideoJob:
    source: Path
    destination: Path


@dataclass(frozen=True)
class VideoResult:
    job: VideoJob
    status: str
    elapsed_seconds: float
    message: str = ""

    @property
    def successful(self) -> bool:
        return self.status in {"converted", "skipped"}


def parse_timeout(value: str) -> float | None:
    value = value.strip().lower()
    if not value or value == "0":
        return None

    match = re.fullmatch(r"(\d+(?:\.\d+)?)([smh]?)", value)
    if not match:
        raise ValueError(f"Invalid CONVERT_TIMEOUT value: {value!r}")

    amount = float(match.group(1))
    unit = match.group(2) or "s"
    return amount * {"s": 1, "m": 60, "h": 3600}[unit]


def format_duration(seconds: float) -> str:
    total = int(round(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours:
        return f"{hours}h {minutes:02d}m {seconds:02d}s"
    if minutes:
        return f"{minutes}m {seconds:02d}s"
    return f"{seconds}s"


def configure_logging() -> Path:
    log_file = BASE_DIR / f"convert-video-{datetime.now():%Y%m%d-%H%M%S}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(threadName)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler(log_file, encoding="utf-8")],
    )
    return log_file


def discover_video_directories() -> list[Path]:
    if not INPUT_DIR.is_dir():
        return []
    return sorted(path for path in INPUT_DIR.iterdir() if path.is_dir())


def find_videos(video_title_dir: Path) -> list[Path]:
    return sorted(
        (path for path in video_title_dir.rglob("*") if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS),
        key=lambda path: str(path).lower(),
    )


def escape_filter_value(value: Path | str) -> str:
    escaped = str(value).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def choose_subtitle_stream(source: Path) -> int | None:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "s",
        "-show_entries",
        "stream=index,codec_name:stream_tags=language,title",
        "-of",
        "json",
        str(source),
    ]

    try:
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
    except OSError as exc:
        logging.info("Unable to inspect subtitles for %s: %s", source, exc)
        return None

    if completed.returncode != 0:
        logging.info("ffprobe failed for %s: %s", source, completed.stderr.strip())
        return None

    try:
        streams = json.loads(completed.stdout).get("streams", [])
    except json.JSONDecodeError as exc:
        logging.info("Unable to parse ffprobe output for %s: %s", source, exc)
        return None

    fallback_index: int | None = None
    chinese_index: int | None = None

    for subtitle_index, stream in enumerate(streams):
        codec_name = str(stream.get("codec_name", "")).lower()
        if codec_name not in TEXT_SUBTITLE_CODECS:
            continue

        if fallback_index is None:
            fallback_index = subtitle_index

        tags = stream.get("tags") or {}
        language = str(tags.get("language", "")).lower()
        title = str(tags.get("title", ""))
        title_lower = title.lower()
        is_chinese = (
            bool(CHINESE_LANGUAGE_RE.match(language))
            or "chinese" in title_lower
            or "\u4e2d\u6587" in title
        )

        if not is_chinese:
            continue

        if chinese_index is None:
            chinese_index = subtitle_index

        if "simplified" in title_lower or "\u7b80\u4f53" in title or "\u7b80\u4e2d" in title:
            return subtitle_index

    return chinese_index if chinese_index is not None else fallback_index


def build_ffmpeg_command(job: VideoJob) -> list[str]:
    video_filter = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2"
    subtitle_stream = choose_subtitle_stream(job.source)

    if subtitle_stream is not None:
        style = (
            f"Fontname={SUBTITLE_FONT},Fontsize=36,Bold=1,Outline=3,Shadow=1,MarginV=18,"
            "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000"
        )
        video_filter += (
            f",subtitles=filename={escape_filter_value(job.source)}:si={subtitle_stream}:"
            f"force_style={escape_filter_value(style)}"
        )

    return [
        "ffmpeg",
        "-nostdin",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(job.source),
        "-map",
        "0:v:0",
        "-map",
        "0:a:0?",
        "-vf",
        video_filter,
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-b:v",
        "1.5M",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "+faststart",
        str(job.destination),
    ]


def convert_video(job: VideoJob, timeout_seconds: float | None) -> VideoResult:
    start = time.monotonic()

    if job.destination.exists():
        message = f"Skipping {job.source}: output {job.destination} already exists."
        logging.info(message)
        return VideoResult(job, "skipped", time.monotonic() - start, message)

    job.destination.parent.mkdir(parents=True, exist_ok=True)
    command = build_ffmpeg_command(job)
    logging.info("Starting conversion: input=%s output=%s", job.source, job.destination)

    try:
        completed = subprocess.run(command, text=True, capture_output=True, timeout=timeout_seconds, check=False)
    except subprocess.TimeoutExpired as exc:
        job.destination.unlink(missing_ok=True)
        elapsed = time.monotonic() - start
        message = f"Timed out converting {job.source} after {CONVERT_TIMEOUT}."
        logging.info("%s stderr=%s", message, (exc.stderr or "").strip())
        return VideoResult(job, "timeout", elapsed, message)
    except OSError as exc:
        job.destination.unlink(missing_ok=True)
        elapsed = time.monotonic() - start
        message = f"Failed to start ffmpeg for {job.source}: {exc}"
        logging.info(message)
        return VideoResult(job, "failed", elapsed, message)

    elapsed = time.monotonic() - start
    if completed.returncode == 0:
        message = f"Converted {job.source} -> {job.destination} in {format_duration(elapsed)}."
        logging.info(message)
        return VideoResult(job, "converted", elapsed, message)

    job.destination.unlink(missing_ok=True)
    message = f"Failed to convert {job.source}; ffmpeg exited with {completed.returncode}."
    logging.info("%s stderr=%s", message, completed.stderr.strip())
    return VideoResult(job, "failed", elapsed, message)


def process_video_directory(video_title_dir: Path, timeout_seconds: float | None) -> list[VideoResult]:
    title = video_title_dir.name
    output_title_dir = OUTPUT_DIR / title
    videos = find_videos(video_title_dir)

    logging.info("Processing folder: folder=%s videos=%d", video_title_dir, len(videos))
    if not videos:
        return []

    output_title_dir.mkdir(parents=True, exist_ok=True)
    jobs = [
        VideoJob(
            source=source,
            destination=(output_title_dir / source.relative_to(video_title_dir)).with_suffix(".mp4"),
        )
        for source in videos
    ]

    results: list[VideoResult] = []
    with ThreadPoolExecutor(max_workers=max(1, MAX_JOBS), thread_name_prefix=title[:24] or "convert") as executor:
        future_to_job = {
            executor.submit(convert_video, job, timeout_seconds): job
            for job in jobs
        }

        for future in as_completed(future_to_job):
            job = future_to_job[future]
            try:
                result = future.result()
            except Exception as exc:
                result = VideoResult(job, "failed", 0, f"Unexpected error: {exc}")
                logging.exception("Unexpected error converting %s", job.source)

            results.append(result)

    if all(result.successful for result in results):
        archive_destination = ARCHIVED_DIR / title
        ARCHIVED_DIR.mkdir(parents=True, exist_ok=True)
        if archive_destination.exists():
            logging.info("Not archiving %s: %s already exists.", video_title_dir, archive_destination)
        else:
            shutil.move(str(video_title_dir), str(archive_destination))
            logging.info("Archived %s -> %s", video_title_dir, archive_destination)

    return results


def send_email(subject: str, body: str) -> bool:
    mail = shutil.which("mail") or shutil.which("mailx")
    if mail:
        completed = subprocess.run([mail, "-s", subject, RECIPIENT], input=body, text=True, capture_output=True, check=False)
        if completed.returncode == 0:
            return True
        logging.info("Failed to send email with %s: %s", mail, completed.stderr.strip())
        return False

    sendmail = shutil.which("sendmail")
    if sendmail:
        message = f"To: {RECIPIENT}\nSubject: {subject}\n\n{body}"
        completed = subprocess.run([sendmail, RECIPIENT], input=message, text=True, capture_output=True, check=False)
        if completed.returncode == 0:
            return True
        logging.info("Failed to send email with sendmail: %s", completed.stderr.strip())
        return False

    logging.info("No supported mail command found; completion email was not sent.")
    return False


def build_summary(results: list[VideoResult], elapsed_seconds: float, log_file: Path) -> str:
    converted = sum(result.status == "converted" for result in results)
    skipped = sum(result.status == "skipped" for result in results)
    timed_out = sum(result.status == "timeout" for result in results)
    failed = sum(result.status == "failed" for result in results)
    success = converted + skipped

    return "\n".join(
        [
            "Video conversion complete.",
            "",
            f"Total time taken: {format_duration(elapsed_seconds)}",
            f"Success count: {success}",
            f"Failure count: {failed}",
            f"Timed out: {timed_out}",
            f"Converted: {converted}",
            f"Skipped: {skipped}",
            f"Log file: {log_file}",
            f"Directory: {BASE_DIR}",
            "",
        ]
    )


def main() -> int:
    if not os.environ.get("TMUX"):
        print("Run this script inside a tmux session.", file=sys.stderr)
        return 1

    log_file = configure_logging()
    start = time.monotonic()
    timeout_seconds = parse_timeout(CONVERT_TIMEOUT)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    logging.info("Starting video conversion: base_dir=%s max_jobs=%d timeout=%s", BASE_DIR, MAX_JOBS, CONVERT_TIMEOUT)
    all_results: list[VideoResult] = []

    for video_title_dir in discover_video_directories():
        all_results.extend(process_video_directory(video_title_dir, timeout_seconds))

    elapsed = time.monotonic() - start
    summary = build_summary(all_results, elapsed, log_file)
    send_email("Video conversion complete", summary)
    print(summary)
    logging.info("Finished video conversion")

    return 1 if any(not result.successful for result in all_results) else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        logging.exception("Unhandled conversion error")
        raise
