import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args: object, **kwargs: object) -> bool:
        return False

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Folders
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
WORKING_DIR = BASE_DIR / "working"
ARCHIVE_DIR = BASE_DIR / "archive"
FAILED_DIR = BASE_DIR / "failed"
LOG_DIR = BASE_DIR / "logs"

# Ollama
OLLAMA_MODEL = "qwen3:8b"

# Translation
TRANSLATION_BATCH_SIZE = 5

# Whisper
WHISPER_MODEL = "turbo"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"
WHISPER_CPU_THREADS = 12

# Audio
AUDIO_SAMPLE_RATE = 16000

# Scanner
SCAN_INTERVAL_SECONDS = 60

# Email
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USERNAME)
EMAIL_TO = os.getenv("EMAIL_TO", "")

TARGET_LANGUAGE = "zh"
