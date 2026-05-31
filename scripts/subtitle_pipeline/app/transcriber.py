# app/transcriber.py

import subprocess
from pathlib import Path
from typing import TypedDict

from faster_whisper import WhisperModel

from app.config import (
    WHISPER_MODEL,
    WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE,
    WHISPER_CPU_THREADS,
)


CHUNK_SECONDS = 300
OVERLAP_SECONDS = 15
MAX_SEGMENT_SECONDS = 15


class AudioChunk(TypedDict):
    file: Path
    chunk_index: int
    main_start: float
    main_end: float
    actual_start: float


def format_time(seconds: float) -> str:
    millis = round(seconds * 1000)

    hrs = millis // 3_600_000
    millis %= 3_600_000

    mins = millis // 60_000
    millis %= 60_000

    secs = millis // 1000
    millis %= 1000

    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"


def split_audio_with_overlap(audio_path: Path, chunk_dir: Path) -> list[AudioChunk]:
    chunk_dir.mkdir(parents=True, exist_ok=True)

    # Clear old chunks
    for file in chunk_dir.glob("chunk_*.wav"):
        file.unlink()

    duration = get_audio_duration(audio_path)

    chunks: list[AudioChunk] = []
    start = 0
    index = 0

    while start < duration:
        chunk_start = max(0, start - OVERLAP_SECONDS)
        chunk_duration = CHUNK_SECONDS + OVERLAP_SECONDS

        chunk_file = chunk_dir / f"chunk_{index:03}.wav"

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss", str(chunk_start),
                "-i", str(audio_path),
                "-t", str(chunk_duration),
                "-ac", "1",
                "-ar", "16000",
                str(chunk_file),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        chunks.append(
            {
                "file": chunk_file,
                "chunk_index": index,
                "main_start": start,
                "main_end": min(start + CHUNK_SECONDS, duration),
                "actual_start": chunk_start,
            }
        )

        start += CHUNK_SECONDS
        index += 1

    return chunks


def get_audio_duration(audio_path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    return float(result.stdout.strip())


def create_model() -> WhisperModel:
    return WhisperModel(
        WHISPER_MODEL,
        device=WHISPER_DEVICE,
        compute_type=WHISPER_COMPUTE_TYPE,
        cpu_threads=WHISPER_CPU_THREADS,
        num_workers=1,
    )


def transcribe_audio(audio_path: str | Path, language: str | None = None) -> Path:
    """
    audio.wav -> subtitle.srt
    """
    print(f"Transcribing audio: {audio_path.name}, language={language}...")
    audio_path = Path(audio_path)

    job_dir = audio_path.parent
    chunk_dir = job_dir / "chunks"
    srt_path = job_dir / "subtitle.srt"

    chunks = split_audio_with_overlap(audio_path, chunk_dir)
    model = create_model()

    subtitle_index = 1

    with open(srt_path, "w", encoding="utf-8") as f:

        for chunk in chunks:
            chunk_file = chunk["file"]
            actual_start = chunk["actual_start"]
            main_start = chunk["main_start"]
            main_end = chunk["main_end"]

            print(f"Transcribing chunk: {chunk_file.name}")

            segments, info = model.transcribe(
                str(chunk_file),
                language=language,
                beam_size=5,
                best_of=5,
                temperature=0,
                vad_filter=False,
                condition_on_previous_text=False,
            )

            for segment in segments:
                print(segment)
                text = segment.text.strip()

                if not text:
                    continue

                start = actual_start + segment.start
                end = actual_start + segment.end
                duration = end - start

                # Only keep subtitles that belong to this chunk's main window
                if start < main_start:
                    continue

                if start >= main_end:
                    continue

                # Drop obviously broken segments
                if duration <= 0:
                    continue

                if duration > MAX_SEGMENT_SECONDS:
                    print(
                        "Skipping suspicious segment:",
                        format_time(start),
                        format_time(end),
                        text,
                    )
                    continue

                f.write(f"{subtitle_index}\n")
                f.write(f"{format_time(start)} --> {format_time(end)}\n")
                f.write(text + "\n\n")

                subtitle_index += 1

    return srt_path
