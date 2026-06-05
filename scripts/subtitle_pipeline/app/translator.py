import json
import ollama
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Literal, TypedDict

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


TranslationMode = Literal["single", "batch"]


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


def translate_batch(subtitles: list[SubtitleCue], template: str) -> list[tuple[SubtitleCue, str]]:
    payload = [
        {
            "id": sub["index"],
            "text": sub["text"],
        }
        for sub in subtitles
    ]
    prompt = (
        "Follow the translation rules below, but translate all input subtitles "
        "and return only valid JSON in this exact shape:\n"
        '{"translations":[{"id":1,"text":"translated subtitle"}]}\n'
        "Use the original numeric id for each translation. Do not include "
        "Markdown or explanatory text.\n\n"
        f"Translation rules:\n{template}\n\n"
        f"Input subtitles:\n{json.dumps(payload, ensure_ascii=False)}"
    )

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        keep_alive=OLLAMA_KEEP_ALIVE,
        think=False,
        format="json",
        options={
            "num_ctx": OLLAMA_CONTEXT_LENGTH,
            "num_gpu": OLLAMA_GPU_LAYERS,
            "temperature": 0,
        }
    )

    raw_content = response["message"]["content"].strip()
    try:
        parsed = json.loads(raw_content)
        translations = parsed["translations"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        ids = ", ".join(str(sub["index"]) for sub in subtitles)
        print(f"Skipping batch [{ids}]: invalid JSON response ({exc})")
        return []

    translated_by_id: dict[int, str] = {}
    for item in translations:
        try:
            translated_by_id[int(item["id"])] = str(item["text"]).strip()
        except (KeyError, TypeError, ValueError):
            print(f"Skipping invalid translation item: {item!r}")

    return [
        (sub, translated_by_id[sub["index"]])
        for sub in subtitles
        if sub["index"] in translated_by_id
    ]


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


def translate_srt(
    srt_path: str | Path,
    language: str,
    mode: TranslationMode = "batch",
) -> Path:
    srt_path = Path(srt_path)
    subtitles = parse_srt(srt_path)
    if mode not in ("single", "batch"):
        raise ValueError("Translation mode must be 'single' or 'batch'")

    template = TRANSLATION_PROMPTS[
        (language, TARGET_LANGUAGE)
    ]

    job_dir = srt_path.parent
    output_srt = job_dir / f"{srt_path.name.replace('.srt', '')}_translated.srt"

    total = len(subtitles)
    worker_count = max(1, TRANSLATION_CONCURRENCY)

    def write_translation(f, sub: SubtitleCue, translated: str) -> None:
        f.write(f"{sub['index']}\n")
        f.write(f"{sub['time']}\n")
        f.write(f"{translated}\n\n")

    with open(output_srt, "w", encoding="utf-8") as f:
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            if mode == "single":
                def translate_subtitle(item: tuple[int, SubtitleCue]) -> tuple[SubtitleCue, str]:
                    i, sub = item
                    print(f"Translating subtitle {i}/{total}")
                    return sub, translate_single(sub["text"], template)

                for sub, translated in executor.map(
                    translate_subtitle,
                    enumerate(subtitles, start=1),
                ):
                    write_translation(f, sub, translated)
            else:
                batch_size = 3
                batches = [
                    subtitles[i:i + batch_size]
                    for i in range(0, total, batch_size)
                ]
                total_batches = len(batches)

                def translate_subtitle_batch(item: tuple[int, list[SubtitleCue]]) -> list[tuple[SubtitleCue, str]]:
                    i, batch = item
                    print(f"Translating batch {i}/{total_batches}")
                    return translate_batch(batch, template)

                results = executor.map(
                    translate_subtitle_batch,
                    enumerate(batches, start=1),
                )

                for batch_results in results:
                    for sub, translated in batch_results:
                        write_translation(f, sub, translated)

    print(
        f"\nDone.\n"
        f"Output: {output_srt}\n"
    )
    return output_srt
