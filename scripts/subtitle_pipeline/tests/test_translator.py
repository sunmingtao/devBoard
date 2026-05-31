import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from app import translator


class SrtParsingTests(unittest.TestCase):
    def test_parse_srt_handles_crlf_and_missing_final_blank_line(self) -> None:
        content = (
            "1\r\n"
            "00:00:01,000 --> 00:00:02,000\r\n"
            "Hello\r\n"
            "\r\n"
            "2\r\n"
            "00:00:03,000 --> 00:00:04,000\r\n"
            "Final line"
        )

        with TemporaryDirectory() as tmp:
            srt_path = Path(tmp) / "subtitle.srt"
            srt_path.write_text(content, encoding="utf-8")

            subtitles = translator.parse_srt(srt_path)

        self.assertEqual(len(subtitles), 2)
        self.assertEqual(subtitles[0]["text"], "Hello")
        self.assertEqual(subtitles[1]["index"], 2)
        self.assertEqual(subtitles[1]["text"], "Final line")

    def test_parse_srt_preserves_multiline_subtitle_text(self) -> None:
        content = (
            "1\n"
            "00:00:01,000 --> 00:00:02,000\n"
            "Line one\n"
            "Line two\n"
        )

        with TemporaryDirectory() as tmp:
            srt_path = Path(tmp) / "subtitle.srt"
            srt_path.write_text(content, encoding="utf-8")

            subtitles = translator.parse_srt(srt_path)

        self.assertEqual(subtitles[0]["text"], "Line one\nLine two")

    def test_parse_srt_skips_malformed_blocks(self) -> None:
        content = (
            "NOTE this is metadata\n\n"
            "1\n"
            "00:00:01,000 --> 00:00:02,000\n"
            "Hello\n"
        )

        with TemporaryDirectory() as tmp:
            srt_path = Path(tmp) / "subtitle.srt"
            srt_path.write_text(content, encoding="utf-8")

            subtitles = translator.parse_srt(srt_path)

        self.assertEqual(len(subtitles), 1)
        self.assertEqual(subtitles[0]["text"], "Hello")


class OllamaConfigTests(unittest.TestCase):
    def test_translate_single_uses_configured_ollama_model(self) -> None:
        with (
            patch.object(translator, "OLLAMA_MODEL", "configured-model"),
            patch.object(translator.ollama, "chat") as chat,
            patch("builtins.print"),
        ):
            chat.return_value = {"message": {"content": "翻译"}}

            translated = translator.translate_single("hello", "{text}")

        self.assertEqual(translated, "翻译")
        self.assertEqual(chat.call_args.kwargs["model"], "configured-model")


if __name__ == "__main__":
    unittest.main()
