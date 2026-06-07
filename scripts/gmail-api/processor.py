from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from gmail_client import get_message, has_replied_after_message, list_messages, send_reply
from message_utils import extract_body, get_header, parse_message_date, sender_email


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProcessResult:
    message_id: str
    action: str
    sender: str = ""
    subject: str = ""
    sent_message_id: str = ""


class GmailAutoResponder:
    def __init__(self, service, settings, reply_generator) -> None:
        self.service = service
        self.settings = settings
        self.reply_generator = reply_generator

    def process_inbox(self) -> list[ProcessResult]:
        messages = list_messages(
            service=self.service,
            user_id=self.settings.user_id,
            query=self.settings.gmail_query,
            max_results=self.settings.max_results,
        )

        if not messages:
            logger.info("No Gmail messages matched query %r", self.settings.gmail_query)
            return []

        logger.info("Processing %d Gmail message(s)", len(messages))
        results: list[ProcessResult] = []
        for summary in messages:
            message_id = summary.get("id", "")
            try:
                results.append(self.process_message(summary))
            except Exception:
                logger.exception("Failed to process Gmail message %s", message_id or "<unknown>")
                results.append(ProcessResult(message_id=message_id, action="error"))
        return results

    def process_message(self, summary: dict[str, Any]) -> ProcessResult:
        message_id = summary["id"]
        message = get_message(self.service, self.settings.user_id, message_id)
        headers = message.get("payload", {}).get("headers", [])

        sender = get_header(headers, "From")
        subject = get_header(headers, "Subject")
        sent_at = parse_message_date(headers)
        normalized_sender = sender_email(sender)

        logger.info(
            "Message %s from=%r subject=%r date=%s",
            message_id,
            sender,
            subject,
            sent_at,
        )

        if normalized_sender not in self.settings.family_emails:
            logger.info("Skipping %s because sender is not configured as family", message_id)
            return ProcessResult(message_id=message_id, action="skipped_non_family", sender=sender, subject=subject)

        if has_replied_after_message(self.service, self.settings.user_id, message):
            logger.info("Skipping %s because a later sent reply already exists", message_id)
            return ProcessResult(message_id=message_id, action="skipped_already_replied", sender=sender, subject=subject)

        body = extract_body(message.get("payload", {}))
        reply_body = self.reply_generator.draft(sender=sender, subject=subject, body=body)
        sent_message = send_reply(
            service=self.service,
            user_id=self.settings.user_id,
            original_message=message,
            to=sender,
            subject=subject,
            body=reply_body,
            headers=headers,
        )
        sent_message_id = sent_message.get("id", "")
        logger.info("Sent Gmail reply %s for source message %s", sent_message_id, message_id)
        return ProcessResult(
            message_id=message_id,
            action="replied",
            sender=sender,
            subject=subject,
            sent_message_id=sent_message_id,
        )
