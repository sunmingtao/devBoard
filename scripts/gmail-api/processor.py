from __future__ import annotations

import base64
import binascii
import json
import logging
from concurrent.futures import TimeoutError
from dataclasses import dataclass
from typing import Any

from gmail_client import (
    get_message,
    has_replied_after_message,
    list_history_message_ids,
    list_messages,
    mark_message_read,
    send_reply,
)
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
    def __init__(self, service, settings, reply_generator, history_store=None) -> None:
        self.service = service
        self.settings = settings
        self.reply_generator = reply_generator
        self.history_store = history_store

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

    def process_history(self, start_history_id: str) -> tuple[list[ProcessResult], str | None]:
        message_ids, response_history_id = list_history_message_ids(
            service=self.service,
            user_id=self.settings.user_id,
            start_history_id=start_history_id,
        )

        if not message_ids:
            logger.info("No Gmail message changes since history id %s", start_history_id)
            return [], response_history_id

        logger.info("Processing %d Gmail history message change(s)", len(message_ids))
        results: list[ProcessResult] = []
        for message_id in message_ids:
            try:
                results.append(self.process_message({"id": message_id}))
            except Exception:
                logger.exception("Failed to process Gmail message %s", message_id)
                results.append(ProcessResult(message_id=message_id, action="error"))
        return results, response_history_id

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
        try:
            mark_message_read(self.service, self.settings.user_id, message_id)
        except Exception:
            logger.exception("Sent reply %s but failed to mark source message %s as read", sent_message_id, message_id)
        logger.info("Sent Gmail reply %s for source message %s", sent_message_id, message_id)
        return ProcessResult(
            message_id=message_id,
            action="replied",
            sender=sender,
            subject=subject,
            sent_message_id=sent_message_id,
        )

    def process_pubsub_notifications(
        self,
        subscriber,
        subscription_path: str,
        timeout: float | None = None,
        flow_control: Any | None = None,
    ) -> list[ProcessResult]:
        results: list[ProcessResult] = []

        def callback(message) -> None:
            logger.info("Received Gmail Pub/Sub notification %s", message.message_id)
            try:
                if self.history_store is None:
                    notification_results = self.process_inbox()
                else:
                    notification_results = self._process_history_notification(message.data)

                results.extend(notification_results)
                if any(result.action == "error" for result in notification_results):
                    message.nack()
                    return
            except Exception:
                logger.exception("Failed to process Gmail Pub/Sub notification %s", message.message_id)
                message.nack()
                return

            message.ack()

        subscribe_kwargs: dict[str, Any] = {"callback": callback}
        if flow_control is not None:
            subscribe_kwargs["flow_control"] = flow_control

        streaming_pull_future = subscriber.subscribe(subscription_path, **subscribe_kwargs)
        logger.info("Listening for Gmail Pub/Sub notifications on %s", subscription_path)

        with subscriber:
            try:
                streaming_pull_future.result(timeout=timeout)
            except TimeoutError:
                streaming_pull_future.cancel()
                streaming_pull_future.result()

        return results

    def _process_history_notification(self, data: bytes) -> list[ProcessResult]:
        notification_history_id = _decode_notification_history_id(data)
        last_history_id = self.history_store.get_history_id()
        if last_history_id is None:
            if notification_history_id:
                self.history_store.set_history_id(notification_history_id)
                logger.info("Initialized Gmail history id at %s", notification_history_id)
            else:
                logger.warning("Gmail Pub/Sub notification did not include a history id")
            return []

        results, response_history_id = self.process_history(last_history_id)
        if any(result.action == "error" for result in results):
            return results

        next_history_id = response_history_id or notification_history_id
        if next_history_id:
            self.history_store.set_history_id(next_history_id)
            logger.info("Persisted Gmail history id %s", next_history_id)
        return results


def _decode_notification_history_id(data: bytes | str | None) -> str | None:
    if not data:
        return None

    try:
        text = data.decode("utf-8") if isinstance(data, bytes) else str(data)
    except UnicodeDecodeError:
        return None

    payload = _loads_notification_json(text)
    history_id = payload.get("historyId")
    return str(history_id) if history_id else None


def _loads_notification_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    try:
        padded = text + "=" * (-len(text) % 4)
        decoded = base64.urlsafe_b64decode(padded).decode("utf-8")
        return json.loads(decoded)
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return {}
