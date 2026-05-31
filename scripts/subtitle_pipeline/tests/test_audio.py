import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from app import audio


class AudioExtractionTests(unittest.TestCase):
    def test_extract_audio_uses_configured_working_directory(self) -> None:
        with TemporaryDirectory() as tmp:
            working_dir = Path(tmp) / "working"
            video_path = Path(tmp) / "input.mp4"
            video_path.write_text("fake video")

            with (
                patch.object(audio, "WORKING_DIR", working_dir),
                patch.object(audio.subprocess, "run") as run,
                patch("builtins.print"),
            ):
                audio_path = audio.extract_audio(video_path)

        self.assertEqual(audio_path, working_dir / "input" / "audio.wav")
        run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
