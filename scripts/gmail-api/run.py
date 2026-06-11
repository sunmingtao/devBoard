from __future__ import annotations

import logging
import sys

from google.cloud import pubsub_v1

from auth import CredentialError, load_credentials
from config import ConfigError, load_settings
from gmail_client import GmailApiError, build_gmail_service
from processor import GmailAutoResponder
from reply_generator import OllamaReplyGenerator


def configure_logging(level_name: str) -> None:
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def main() -> int:
    logger = logging.getLogger(__name__)

    try:
        settings = load_settings()
        configure_logging(settings.log_level)
        credentials = load_credentials(settings)
        service = build_gmail_service(credentials)
        topic_name = (
            f"projects/{settings.gmail_pubsub_project_id}"
            f"/topics/{settings.gmail_pubsub_topic_id}"
        )
        service.users().watch(
            userId=settings.user_id,
            body={
                "topicName": topic_name,
                "labelIds": ["INBOX"],
                "labelFilterBehavior": "INCLUDE",
            },
        ).execute()
        logger.info("Started watching Gmail inbox for changes on %s", topic_name)
        responder = GmailAutoResponder(
            service=service,
            settings=settings,
            reply_generator=OllamaReplyGenerator(
                model=settings.ollama_model,
                body_limit=settings.reply_body_limit,
                host=settings.ollama_host,
            ),
        )
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(
            settings.gmail_pubsub_project_id,
            settings.gmail_pubsub_subscription_id,
        )
        results = responder.process_pubsub_notifications(
            subscriber=subscriber,
            subscription_path=subscription_path,
            timeout=settings.gmail_pubsub_timeout_seconds,
            flow_control=pubsub_v1.types.FlowControl(max_messages=1),
        )
    except (ConfigError, CredentialError, GmailApiError) as exc:
        logger.error("%s", exc)
        return 1
    except KeyboardInterrupt:
        logger.info("Interrupted")
        return 130

    return 1 if any(result.action == "error" for result in results) else 0


if __name__ == "__main__":
    sys.exit(main())
