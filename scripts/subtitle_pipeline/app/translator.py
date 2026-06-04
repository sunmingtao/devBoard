import ollama
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TypedDict

from app.config import (
    OLLAMA_CONTEXT_LENGTH,
    OLLAMA_GPU_LAYERS,
    OLLAMA_KEEP_ALIVE,
    OLLAMA_MODEL,
    TARGET_LANGUAGE,
    TRANSLATION_CONCURRENCY,
)

from app.prompts import (
    TRANSLATION_PROMPTS
)


class SubtitleCue(TypedDict):
    index: int
    time: str
    text: str


def parse_srt(filename: str | Path) -> list[SubtitleCue]:
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read().replace("\r\n", "\n").replace("\r", "\n").strip()

    if not content:
        return []

    subtitles: list[SubtitleCue] = []

    for block in re.split(r"\n\s*\n", content):
        lines = block.splitlines()
        if len(lines) < 3 or "-->" not in lines[1]:
            continue

        try:
            index = int(lines[0].strip())
        except ValueError:
            continue

        subtitles.append(
            {
                "index": index,
                "time": lines[1].strip(),
                "text": "\n".join(lines[2:]).strip(),
            }
        )

    return subtitles

def translate_single(text: str, template: str) -> str:
    prompt = template.format(
        text=text
    )

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        keep_alive=OLLAMA_KEEP_ALIVE,
        think=False,
        options={
            "num_ctx": OLLAMA_CONTEXT_LENGTH,
            "num_gpu": OLLAMA_GPU_LAYERS,
            "temperature": 0,
        }
    )

    return response["message"]["content"].strip()


def generate_bilingual_srt(
    original_srt_path: str | Path,
    translated_srt_path: str | Path,
) -> Path:
    original_srt_path = Path(original_srt_path)
    translated_srt_path = Path(translated_srt_path)
    original_subtitles = parse_srt(original_srt_path)
    translated_subtitles = parse_srt(translated_srt_path)
    output_srt = original_srt_path.parent / f"{original_srt_path.name.replace('.srt', '')}_bilingual.srt"

    with open(output_srt, "w", encoding="utf-8") as f:
        for original, translated in zip(original_subtitles, translated_subtitles):
            f.write(f"{original['index']}\n")
            f.write(f"{original['time']}\n")
            f.write(f"{original['text']}\n")
            f.write(f"{translated['text']}\n\n")

    return output_srt


def translate_srt(srt_path: str | Path, language: str) -> Path:
    srt_path = Path(srt_path)
    subtitles = parse_srt(srt_path)

    template = TRANSLATION_PROMPTS[
        (language, TARGET_LANGUAGE)
    ]

    job_dir = srt_path.parent
    output_srt = job_dir / f"{srt_path.name.replace('.srt', '')}_translated.srt"

    open(output_srt, "w", encoding="utf-8").close()

    total = len(subtitles)
    worker_count = max(1, TRANSLATION_CONCURRENCY)

    def translate_subtitle(item: tuple[int, SubtitleCue]) -> tuple[SubtitleCue, str]:
        i, sub = item
        print(f"Translating {i}/{total}")
        return sub, translate_single(sub["text"], template)

    with open(output_srt, "a", encoding="utf-8") as f:
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            results = executor.map(
                translate_subtitle,
                enumerate(subtitles, start=1),
            )

            for sub, translated in results:
                f.write(f"{sub['index']}\n")
                f.write(f"{sub['time']}\n")
                f.write(f"{translated}\n\n")

    print(
        f"\nDone.\n"
        f"Output: {output_srt}\n"
    )
    return output_srt
