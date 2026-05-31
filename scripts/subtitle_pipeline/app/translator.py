import ollama
import re
from pathlib import Path

from app.config import (
    TARGET_LANGUAGE
)

from app.prompts import (
    TRANSLATION_PROMPTS
)

def parse_srt(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        r"(\d+)\n" 
        r"([0-9:,]+ --> [0-9:,]+)\n" 
        r"(.*?)\n\n",
        re.DOTALL,
    )

    subtitles = []

    for match in pattern.finditer(content):
        subtitles.append(
            {
                "index": int(match.group(1)),
                "time": match.group(2),
                "text": match.group(3).strip(),
            }
        )

    return subtitles

def translate_single(text, template):
    print(f"Translating text: {text}")
    prompt = template.format(
        text=text
    )

    response = ollama.chat(
        model="qwen3:8b",
        messages=[
            {"role": "user", "content": prompt}
        ],
        think=False,
        options={
            "temperature": 0,
        }
    )

    return response["message"]["content"].strip()

def translate_srt(srt_path, language):
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