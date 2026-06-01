import ollama
import json
import re
from pathlib import Path
from typing import TypedDict

from app.config import (
    OLLAMA_MODEL,
    TARGET_LANGUAGE,
    TRANSLATION_BATCH_SIZE,
)

from app.prompts import (
    TRANSLATION_PROMPTS
)


class SubtitleCue(TypedDict):
    index: int
    time: str
    text: str


def translation_schema(batch_size: int) -> dict:
    return {
        "type": "object",
        "properties": {
            "translations": {
                "type": "array",
                "minItems": batch_size,
                "maxItems": batch_size,
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "text": {"type": "string"},
                    },
                    "required": ["id", "text"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["translations"],
        "additionalProperties": False,
    }


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
    print(f"Translating text: {text}")
    prompt = template.format(
        text=text
    )

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        think=False,
        options={
            "temperature": 0,
        }
    )

    return response["message"]["content"].strip()


def translate_batch(texts: list[str], language: str) -> list[str]:
    if len(texts) == 1:
        template = TRANSLATION_PROMPTS[
            (language, TARGET_LANGUAGE)
        ]
        return [translate_single(texts[0], template)]

    payload = [
        {"id": index, "text": text}
        for index, text in enumerate(texts, start=1)
    ]
    prompt = (
        "你是一名专业字幕翻译。\n"
        f"请把下面 JSON 数组中每个 text 字段从 {language} 翻译成 {TARGET_LANGUAGE}。\n"
        "必须逐条独立翻译，不能合并、拆分、省略或改写 id。\n"
        "即使字幕很短或只有一个字母，也必须为每个输入返回一个独立结果。\n"
        "只输出符合 schema 的 JSON。\n\n"
        f"输入 JSON:\n{json.dumps(payload, ensure_ascii=False)}"
    )

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        think=False,
        format=translation_schema(len(texts)),
        options={
            "temperature": 0,
        }
    )

    content = response["message"]["content"].strip()
    data = json.loads(content)
    translations = data.get("translations")

    if not isinstance(translations, list) or len(translations) != len(texts):
        raise ValueError(f"Unexpected translation response: {content}")

    translated_texts: list[str] = []
    for expected_id, item in enumerate(translations, start=1):
        if (
            not isinstance(item, dict)
            or item.get("id") != expected_id
            or not isinstance(item.get("text"), str)
        ):
            raise ValueError(f"Unexpected translation response: {content}")
        translated_texts.append(item["text"].strip())

    return translated_texts


def generate_bilingual_srt(
    original_srt_path: str | Path,
    translated_srt_path: str | Path,
) -> Path:
    original_srt_path = Path(original_srt_path)
    translated_srt_path = Path(translated_srt_path)
    original_subtitles = parse_srt(original_srt_path)
    translated_subtitles = parse_srt(translated_srt_path)
    output_srt = original_srt_path.parent / "subtitle_bilingual.srt"

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

    job_dir = srt_path.parent
    output_srt = job_dir / "subtitle_translated.srt"

    open(output_srt, "w", encoding="utf-8").close()

    total = len(subtitles)

    with open(output_srt, "a", encoding="utf-8") as f:

        for start in range(0, total, TRANSLATION_BATCH_SIZE):
            batch = subtitles[start:start + TRANSLATION_BATCH_SIZE]

            print(f"Translating {start + 1}-{start + len(batch)}/{total}")

            for attempt in range(1, 4):
                try:
                    translated_texts = translate_batch(
                        [sub["text"] for sub in batch],
                        language,
                    )
                    break
                except (json.JSONDecodeError, ValueError):
                    if attempt == 3:
                        raise
                    print(f"Retrying {start + 1}-{start + len(batch)}/{total}")

            for sub, translated in zip(batch, translated_texts):
                f.write(f"{sub['index']}\n")
                f.write(f"{sub['time']}\n")
                f.write(f"{translated}\n\n")

    print(
        f"\nDone.\n"
        f"Output: {output_srt}\n"
    )
    return output_srt
