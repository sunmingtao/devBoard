import ollama
import re
from pathlib import Path
from typing import TypedDict

from app.config import (
    OLLAMA_MODEL,
    TARGET_LANGUAGE
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

def translate_srt(srt_path: str | Path, language: str) -> Path:
    srt_path = Path(srt_path)
    subtitles = parse_srt(srt_path)

    template = TRANSLATION_PROMPTS[
        (language, TARGET_LANGUAGE)
    ]

    job_dir = srt_path.parent
    output_srt = job_dir / "subtitle_translated.srt"

    open(output_srt, "w", encoding="utf-8").close()

    total = len(subtitles)

    with open(output_srt, "a", encoding="utf-8") as f:

        for i, sub in enumerate(subtitles, start=1):

            print(f"Translating {i}/{total}")

            translated = translate_single(sub["text"], template)

            f.write(f"{sub['index']}\n")
            f.write(f"{sub['time']}\n")
            f.write(f"{translated}\n\n")

    print(
        f"\nDone.\n"
        f"Output: {output_srt}\n"
    )
    return output_srt
