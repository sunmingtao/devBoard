import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from app import video


class SubtitleBurnTests(unittest.TestCase):
    def test_escape_ffmpeg_filter_value_escapes_filter_special_characters(self) -> None:
        escaped = video.escape_ffmpeg_filter_value(r"/tmp/a'b:c,d[e]\f.srt")

        self.assertEqual(escaped, r"/tmp/a\'b\:c\,d\[e\]\\f.srt")

    def test_burn_subtitles_uses_escaped_subtitle_path(self) -> None:
        with TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "output"
            subtitle_path = Path(tmp) / "sub's:1,2.srt"
            video_path = Path(tmp) / "input.mp4"

            with (
                patch.object(video, "OUTPUT_DIR", output_dir),
                patch.object(video.subprocess, "run") as run,
                patch("builtins.print"),
            ):
                output_path = video.burn_subtitles(video_path, subtitle_path)

        self.assertEqual(output_path, output_dir / "input_zh_burned.mp4")

        ffmpeg_args = run.call_args.args[0]
        subtitle_filter = ffmpeg_args[ffmpeg_args.index("-vf") + 1]

        self.assertIn(r"sub\'s\:1\,2.srt", subtitle_filter)
        self.assertNotIn(str(subtitle_path), subtitle_filter)


if __name__ == "__main__":
    unittest.main()
