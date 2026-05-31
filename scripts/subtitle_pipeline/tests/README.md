# Subtitle pipeline tests

These tests use Python's built-in `unittest` framework.

Run them from `scripts/subtitle_pipeline`:

```bash
source venv/bin/activate
python -m unittest discover -s tests
```

Or run from the repository root:

```bash
PYTHONPATH=scripts/subtitle_pipeline scripts/subtitle_pipeline/venv/bin/python -m unittest discover -s scripts/subtitle_pipeline/tests
```

Most tests use `unittest.mock.patch` to replace slow or external calls with fake
versions. That lets us test pipeline decisions without running ffmpeg, Whisper,
Ollama, or Gmail SMTP.
