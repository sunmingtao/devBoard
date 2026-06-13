from __future__ import annotations

from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from message_utils import build_reply_email, encode_email


class GmailApiError(RuntimeError):
    pass


def build_gmail_service(credentials):
    try:
        return build("gmail", "v1", credentials=credentials, cache_discovery=False)
    except Exception as exc:
        raise GmailApiError("Could not initialize Gmail API client") from exc


def list_messages(service, user_id: str, query: str, max_results: int) -> list[dict[str, Any]]:
    response = _execute(
        service.users()
        .messages()
        .list(userId=user_id, q=query, maxResults=max_results),
        "list Gmail messages",
    )
    return response.get("messages", [])


def list_history_message_ids(
    service,
    user_id: str,
    start_history_id: str,
    label_id: str = "INBOX",
) -> tuple[list[str], str | None]:
    message_ids: list[str] = []
    seen: set[str] = set()
    page_token: str | None = None
    newest_history_id: str | None = None

    while True:
        kwargs: dict[str, Any] = {
            "userId": user_id,
            "startHistoryId": start_history_id,
            "historyTypes": ["messageAdded", "labelAdded"],
            "labelId": label_id,
        }
        if page_token:
            kwargs["pageToken"] = page_token

        response = _execute(
            service.users().history().list(**kwargs),
            f"list Gmail history since {start_history_id}",
        )
        response_history_id = response.get("historyId")
        if response_history_id:
            newest_history_id = str(response_history_id)

        for history in response.get("history", []):
            for change in history.get("messagesAdded", []):
                _append_message_id(change.get("message", {}), seen, message_ids)
            for change in history.get("labelsAdded", []):
                if label_id in change.get("labelIds", []):
                    _append_message_id(change.get("message", {}), seen, message_ids)

        page_token = response.get("nextPageToken")
        if not page_token:
            return message_ids, newest_history_id


def get_message(service, user_id: str, message_id: str) -> dict[str, Any]:
    return _execute(
        service.users().messages().get(userId=user_id, id=message_id, format="full"),
        f"load Gmail message {message_id}",
    )


def mark_message_read(service, user_id: str, message_id: str) -> dict[str, Any]:
    return _execute(
        service.users()
        .messages()
        .modify(userId=user_id, id=message_id, body={"removeLabelIds": ["UNREAD"]}),
        f"mark Gmail message {message_id} as read",
    )


def has_replied_after_message(service, user_id: str, message: dict[str, Any]) -> bool:
    thread_id = message["threadId"]
    message_timestamp = int(message["internalDate"])
    thread = _execute(
        service.users().threads().get(userId=user_id, id=thread_id, format="metadata"),
        f"load Gmail thread {thread_id}",
    )

    for thread_message in thread.get("messages", []):
        labels = thread_message.get("labelIds", [])
        internal_date = int(thread_message.get("internalDate", 0))
        if "SENT" in labels and internal_date > message_timestamp:
            return True

    return False


def send_reply(
    service,
    user_id: str,
    original_message: dict[str, Any],
    to: str,
    subject: str,
    body: str,
    headers: list[dict[str, str]],
) -> dict[str, Any]:
    reply = build_reply_email(to=to, subject=subject, body=body, original_headers=headers)
    return _execute(
        service.users()
        .messages()
        .send(
            userId=user_id,
            body={"raw": encode_email(reply), "threadId": original_message["threadId"]},
        ),
        f"send Gmail reply for thread {original_message['threadId']}",
    )


def _execute(request, action: str):
    try:
        return request.execute()
    except HttpError as exc:
        raise GmailApiError(f"Failed to {action}: {exc}") from exc


def _append_message_id(
    message: dict[str, Any],
    seen: set[str],
    message_ids: list[str],
) -> None:
    message_id = message.get("id")
    if message_id and message_id not in seen:
        seen.add(message_id)
        message_ids.append(message_id)
