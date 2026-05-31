import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from app import scanner


class ScannerTests(unittest.TestCase):
    def test_is_file_stable_returns_false_when_file_disappears(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "video.mp4"
            path.write_text("fake video")

            def remove_file(_: int) -> None:
                path.unlink()

            with patch.object(scanner.time, "sleep", side_effect=remove_file):
                stable = scanner.is_file_stable(path, wait_seconds=1)

        self.assertFalse(stable)


if __name__ == "__main__":
    unittest.main()
