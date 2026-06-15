import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from app import main


class MainBatchTests(unittest.TestCase):
    def test_main_continues_after_one_media_file_fails(self) -> None:
        media_files = [Path("one.mp4"), Path("two.mp4"), Path("three.mp4")]
        processed = []

        def fake_process_media_file(
            video: Path,
            translation_mode: main.TranslationMode = "batch",
        ) -> None:
            processed.append(video.name)
            if video.name == "two.mp4":
                raise RuntimeError("boom")

        with (
            patch.object(main, "find_new_media_files", return_value=media_files),
            patch.object(main, "process_media_file", side_effect=fake_process_media_file),
            patch("builtins.print"),
        ):
            main.main()

        self.assertEqual(processed, ["one.mp4", "two.mp4", "three.mp4"])


class CompletedJobCleanupTests(unittest.TestCase):
    def test_cleanup_archives_video_and_removes_working_directory(self) -> None:
        with TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            video_path = base_dir / "input.mp4"
            video_path.write_text("fake video")

            job_dir = base_dir / "working" / "input"
            job_dir.mkdir(parents=True)
            (job_dir / "audio.wav").write_text("fake audio")

            archive_dir = base_dir / "archive"

            with (
                patch.object(main, "ARCHIVE_DIR", archive_dir),
                patch("builtins.print"),
            ):
                archived_path = main.cleanup_completed_job(video_path, job_dir)

            self.assertEqual(archived_path, archive_dir / "input.mp4")
            self.assertTrue(archived_path.exists())
            self.assertFalse(video_path.exists())
            self.assertFalse(job_dir.exists())

    def test_unique_archive_path_adds_suffix_when_file_exists(self) -> None:
        with TemporaryDirectory() as tmp:
            archive_dir = Path(tmp) / "archive"
            archive_dir.mkdir()
            (archive_dir / "input.mp4").write_text("existing")
            (archive_dir / "input_1.mp4").write_text("existing")

            with patch.object(main, "ARCHIVE_DIR", archive_dir):
                archive_path = main.unique_archive_path(Path("input.mp4"))

            self.assertEqual(archive_path, archive_dir / "input_2.mp4")


class SubtitleOutputTests(unittest.TestCase):
    def test_copy_subtitle_to_output_copies_generated_srt(self) -> None:
        with TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            subtitle_path = base_dir / "working" / "subtitle_bilingual.srt"
            subtitle_path.parent.mkdir()
            subtitle_path.write_text("1\n00:00:00,000 --> 00:00:01,000\nHello\n", encoding="utf-8")
            output_dir = base_dir / "output"

            with (
                patch.object(main, "OUTPUT_DIR", output_dir),
                patch("builtins.print"),
            ):
                output_path = main.copy_subtitle_to_output(subtitle_path)

            self.assertEqual(output_path, output_dir / subtitle_path.name)
            self.assertEqual(output_path.read_text(encoding="utf-8"), subtitle_path.read_text(encoding="utf-8"))


class ProcessMediaFileTests(unittest.TestCase):
    def test_process_media_file_transcribes_and_translates_with_detected_language(self) -> None:
        video_path = Path("input~ja.mp4")
        audio_path = Path("working/input/audio.wav")
        srt_path = Path("working/input/subtitle.srt")
        zh_srt_path = Path("working/input/subtitle_translated.srt")
        bilingual_srt_path = Path("working/input/subtitle_bilingual.srt")
        subtitle_output_path = Path("output/subtitle_bilingual.srt")
        soft_subtitled_video_path = Path("output/input~jaC.mp4")
        archived_video_path = Path("archive/input~ja.mp4")

        with (
            patch.object(main, "extract_audio", return_value=audio_path) as extract_audio,
            patch.object(main, "transcribe_audio", return_value=srt_path) as transcribe_audio,
            patch.object(main, "translate_srt", return_value=zh_srt_path) as translate_srt,
            patch.object(main, "generate_bilingual_srt", return_value=bilingual_srt_path) as generate_bilingual_srt,
            patch.object(main, "copy_subtitle_to_output", return_value=subtitle_output_path) as copy_subtitle_to_output,
            patch.object(main, "burn_subtitles") as burn_subtitles,
            patch.object(main, "soft_burn_subtitles", return_value=soft_subtitled_video_path) as soft_burn_subtitles,
            patch.object(main, "cleanup_completed_job", return_value=archived_video_path) as cleanup_completed_job,
            patch.object(main, "send_success") as send_success,
            patch.object(main, "send_failure") as send_failure,
        ):
            main.process_media_file(video_path)

        extract_audio.assert_called_once_with(video_path)
        transcribe_audio.assert_called_once_with(audio_path, language="ja")
        translate_srt.assert_called_once_with(
            srt_path,
            language="ja",
            mode="batch",
        )
        generate_bilingual_srt.assert_called_once_with(srt_path, zh_srt_path)
        copy_subtitle_to_output.assert_called_once_with(bilingual_srt_path)
        burn_subtitles.assert_not_called()
        soft_burn_subtitles.assert_called_once_with(video_path, subtitle_output_path)
        cleanup_completed_job.assert_called_once_with(video_path, audio_path.parent)
        send_success.assert_called_once_with(archived_video_path, soft_subtitled_video_path)
        send_failure.assert_not_called()

    def test_process_media_file_sends_failure_and_reraises(self) -> None:
        video_path = Path("input.mp4")

        with (
            patch.object(main, "extract_audio", side_effect=RuntimeError("ffmpeg failed")),
            patch.object(main, "send_failure") as send_failure,
            patch.object(main, "send_success") as send_success,
        ):
            with self.assertRaises(RuntimeError):
                main.process_media_file(video_path)

        send_failure.assert_called_once_with(video_path, "ffmpeg failed")
        send_success.assert_not_called()


if __name__ == "__main__":
    unittest.main()
