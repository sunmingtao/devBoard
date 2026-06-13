import smtplib
import time
from collections.abc import Iterable
from datetime import timedelta
from email.message import EmailMessage
from pathlib import Path

from app.config import (
    EMAIL_FROM,
    EMAIL_TO,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USERNAME,
)

_PROCESSING_STARTED_AT = time.perf_counter()


class NotificationError(RuntimeError):
    """Raised when an email notification cannot be sent."""


def _recipient_list(recipients: str | Iterable[str]) -> list[str]:
    if isinstance(recipients, str):
        normalized = recipients.replace(";", ",")
        return [email.strip() for email in normalized.split(",") if email.strip()]

    return [email.strip() for email in recipients if email and email.strip()]


def _missing_settings(recipients: list[str]) -> list[str]:
    required_settings = {
        "SMTP_HOST": SMTP_HOST,
        "SMTP_PORT": SMTP_PORT,
        "SMTP_USERNAME": SMTP_USERNAME,
        "SMTP_PASSWORD": SMTP_PASSWORD,
        "EMAIL_FROM": EMAIL_FROM,
        "EMAIL_TO": recipients,
    }

    return [name for name, value in required_settings.items() if not value]


def _redact_setting_names(setting_names: Iterable[str]) -> list[str]:
    sensitive_tokens = ("PASSWORD", "SECRET", "TOKEN", "KEY")
    redacted: list[str] = []
    for name in setting_names:
        upper_name = name.upper()
        if any(token in upper_name for token in sensitive_tokens):
            redacted.append("REDACTED_SENSITIVE_SETTING")
        else:
            redacted.append(name)
    return redacted


def _elapsed_processing_time() -> str:
    return str(timedelta(seconds=int(time.perf_counter() - _PROCESSING_STARTED_AT)))


def send_email(
    subject: str,
    body: str,
    *,
    recipients: str | Iterable[str] = EMAIL_TO,
    raise_on_error: bool = False,
) -> bool:
    """
    Send a plain-text email notification through Gmail SMTP.

    Returns True when the email is sent. Returns False when notification is not
    configured or SMTP fails, unless raise_on_error is True.
    """
    to_addresses = _recipient_list(recipients)
    missing = _missing_settings(to_addresses)

    if missing:
        safe_missing = _redact_setting_names(missing)
        message = "Email notification skipped; missing settings: " + ", ".join(safe_missing)
        if raise_on_error:
            raise NotificationError(message)
        print(message)
        return False

    email = EmailMessage()
    email["From"] = EMAIL_FROM
    email["To"] = ", ".join(to_addresses)
    email["Subject"] = subject
    email.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(email)
    except (OSError, smtplib.SMTPException) as exc:
        message = f"Email notification failed: {exc}"
        if raise_on_error:
            raise NotificationError(message) from exc
        print(message)
        return False

    print(f"Email notification sent to {', '.join(to_addresses)}")
    return True

def send_success(video_path: str | Path, output_path: str | Path) -> bool:
    video_path = Path(video_path)
    output_path = Path(output_path)

    subject = f"[subtitle_pipeline] Success: {video_path.name}"
    body = (
        "Subtitle pipeline completed successfully.\n\n"
        f"Input video: {video_path}\n"
        f"Output video: {output_path}\n"
        f"Processing time: {_elapsed_processing_time()}\n"
    )

    return send_email(subject, body)

def send_failure(video_path: str | Path, error_message: str) -> bool:
    video_path = Path(video_path)

    subject = f"[subtitle_pipeline] Failed: {video_path.name}"
    body = (
        "Subtitle pipeline failed.\n\n"
        f"Input video: {video_path}\n"
        f"Error: {error_message}\n"
        f"Processing time: {_elapsed_processing_time()}\n"
    )

    return send_email(subject, body)
