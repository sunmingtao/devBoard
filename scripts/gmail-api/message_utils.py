from __future__ import annotations

import base64
import binascii
import re
from email.message import EmailMessage
from email.utils import parseaddr, parsedate_to_datetime
from html import unescape
from typing import Any


TAG_RE = re.compile(r"<[^>]+>")
BLOCK_TAG_RE = re.compile(r"(?i)</?(?:br|p|div|li|tr|h[1-6])\b[^>]*>")


def get_header(headers: list[dict[str, str]] | None, name: str) -> str:
    wanted = name.lower()
    for header in headers or []:
        if header.get("name", "").lower() == wanted:
            return header.get("value", "")
    return ""


def decode_base64url(data: str | None) -> str:
    if not data:
        return ""

    padded = data + "=" * (-len(data) % 4)
    try:
        decoded = base64.urlsafe_b64decode(padded.encode("utf-8"))
    except (binascii.Error, ValueError):
        return ""

    return decoded.decode("utf-8", errors="replace")


def extract_body(payload: dict[str, Any]) -> str:
    plain_parts: list[str] = []
    html_parts: list[str] = []
    _collect_body_parts(payload, plain_parts, html_parts)

    plain_body = "\n".join(part.strip() for part in plain_parts if part.strip())
    if plain_body:
        return plain_body

    html_body = "\n".join(part.strip() for part in html_parts if part.strip())
    return html_to_text(html_body)


def html_to_text(value: str) -> str:
    with_breaks = BLOCK_TAG_RE.sub("\n", value)
    without_tags = TAG_RE.sub("", with_breaks)
    lines = [line.strip() for line in unescape(without_tags).splitlines()]
    return "\n".join(line for line in lines if line)


def sender_email(sender: str) -> str:
    return parseaddr(sender)[1].lower()


def parse_message_date(headers: list[dict[str, str]] | None):
    raw_date = get_header(headers, "Date")
    return parsedate_to_datetime(raw_date) if raw_date else None


def reply_subject(subject: str) -> str:
    return subject if subject.lower().startswith("re:") else f"Re: {subject}"


def build_reply_email(
    to: str,
    subject: str,
    body: str,
    original_headers: list[dict[str, str]] | None,
) -> EmailMessage:
    message = EmailMessage()
    message["To"] = to
    message["Subject"] = reply_subject(subject)

    message_id = get_header(original_headers, "Message-ID")
    if message_id:
        message["In-Reply-To"] = message_id
        references = get_header(original_headers, "References")
        message["References"] = f"{references} {message_id}".strip()

    message.set_content(body)
    return message


def encode_email(message: EmailMessage) -> str:
    return base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")


def _collect_body_parts(
    payload: dict[str, Any],
    plain_parts: list[str],
    html_parts: list[str],
) -> None:
    mime_type = payload.get("mimeType", "")
    body_data = payload.get("body", {}).get("data")

    if body_data:
        decoded = decode_base64url(body_data)
        if mime_type.startswith("text/plain"):
            plain_parts.append(decoded)
        elif mime_type.startswith("text/html"):
            html_parts.append(decoded)

    for part in payload.get("parts", []) or []:
        _collect_body_parts(part, plain_parts, html_parts)
