import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from subprocess import CompletedProcess
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
                run.side_effect = [
                    CompletedProcess(args=[], returncode=0, stdout='{"streams":[{"duration":"12.0"}]}', stderr=""),
                    CompletedProcess(args=[], returncode=0),
                    CompletedProcess(args=[], returncode=0, stdout='{"streams":[{"duration":"12.2"}]}', stderr=""),
                ]
                audio_path = audio.extract_audio(video_path)

        self.assertEqual(audio_path, working_dir / "input" / "input.wav")
        self.assertEqual(run.call_count, 3)


if __name__ == "__main__":
    unittest.main()
