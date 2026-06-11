from pathlib import Path

from faster_whisper import WhisperModel

from app.config import (
    WORKING_DIR,
    WHISPER_MODEL,
    WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE,
    WHISPER_CPU_THREADS,
)
from app.split_video import VideoChunk


MAX_SEGMENT_SECONDS = 15


def format_time(seconds: float) -> str:
    millis = round(seconds * 1000)

    hrs = millis // 3_600_000
    millis %= 3_600_000

    mins = millis // 60_000
    millis %= 60_000

    secs = millis // 1000
    millis %= 1000

    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"


def create_model() -> WhisperModel:
    device = WHISPER_DEVICE.lower()
    compute_type = WHISPER_COMPUTE_TYPE

    if device in {"auto", "cuda"}:
        try:
            import ctranslate2

            cuda_available = ctranslate2.get_cuda_device_count() > 0
        except Exception:
            cuda_available = False

        device = "cuda" if cuda_available else "cpu"

    if device == "cpu" and compute_type in {"float16", "bfloat16"}:
        compute_type = "int8"

    return WhisperModel(
        WHISPER_MODEL,
        device=device,
        compute_type=compute_type,
        cpu_threads=WHISPER_CPU_THREADS,
        num_workers=1,
    )


def transcribe_audio(
    video_path: str | Path,
    video_chunks: list[VideoChunk] | None = None,
    language: str | None = None,
) -> Path:
    """
    Video chunk audio -> subtitle.srt
    """
    video_path = Path(video_path)
    print(f"Transcribing audio: {video_path.name}, language={language}...")

    if video_chunks is None:
        raise ValueError("video_chunks must be provided")

    srt_path = WORKING_DIR / f"{video_path.stem}.srt"
    srt_path.parent.mkdir(parents=True, exist_ok=True)
    model = create_model()
    subtitle_index = 1

    with open(srt_path, "w", encoding="utf-8") as f:

        for chunk in video_chunks:
            chunk_file = Path(chunk["file"])
            actual_start = chunk["actual_start"]
            main_start = chunk["main_start"]
            main_end = chunk["main_end"]

            print(f"Transcribing chunk: {chunk_file.name}")

            segments, _ = model.transcribe(
                str(chunk_file),
                language=language,
                beam_size=1,
                best_of=1,
                temperature=0,
                vad_filter=False,
                condition_on_previous_text=False,
            )

            for segment in segments:
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
