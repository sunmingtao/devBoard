from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


SCRIPT_DIR = Path(__file__).resolve().parent

SCOPES = (
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
)

DEFAULT_FAMILY_EMAILS = frozenset(
    {
        "8011560@radford.act.edu.au",
        "8011638@radford.act.edu.au",
        "selina1224@gmail.com",
        "smtttt@gmail.com",
    }
)
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_GMAIL_PUBSUB_PROJECT_ID = "cool-phalanx-303803"
DEFAULT_GMAIL_PUBSUB_TOPIC_ID = "smt-gmail-sub-topic"
DEFAULT_GMAIL_PUBSUB_SUBSCRIPTION_ID = "smt-gmail"


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class Settings:
    scopes: tuple[str, ...]
    family_emails: frozenset[str]
    ollama_model: str
    ollama_host: str
    token_file: Path
    client_secret_file: Path
    gmail_query: str
    user_id: str
    log_level: str
    local_server_port: int
    reply_body_limit: int
    max_results: int
    gmail_pubsub_project_id: str
    gmail_pubsub_topic_id: str
    gmail_pubsub_subscription_id: str
    gmail_pubsub_timeout_seconds: float | None


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    values = os.environ if env is None else env

    return Settings(
        scopes=SCOPES,
        family_emails=_parse_email_set(values.get("GMAIL_FAMILY_EMAILS")),
        ollama_model=values.get("OLLAMA_MODEL", "qwen3:8b"),
        ollama_host=values.get("OLLAMA_HOST", DEFAULT_OLLAMA_HOST),
        token_file=_path_setting(values.get("GMAIL_TOKEN_FILE"), "secrets/token.json"),
        client_secret_file=_path_setting(
            values.get("GMAIL_CLIENT_SECRET_FILE"),
            "secrets/gmail-api-client-secret.json",
        ),
        gmail_query=values.get("GMAIL_QUERY", "category:primary is:unread"),
        user_id=values.get("GMAIL_USER_ID", "me"),
        log_level=values.get("LOG_LEVEL", "INFO").upper(),
        local_server_port=_int_setting("GMAIL_OAUTH_PORT", values.get("GMAIL_OAUTH_PORT"), 0),
        reply_body_limit=_int_setting("GMAIL_REPLY_BODY_LIMIT", values.get("GMAIL_REPLY_BODY_LIMIT"), 4000),
        max_results=_int_setting("GMAIL_MAX_RESULTS", values.get("GMAIL_MAX_RESULTS"), 50, minimum=1),
        gmail_pubsub_project_id=_str_setting(
            "GMAIL_PUBSUB_PROJECT_ID",
            values.get("GMAIL_PUBSUB_PROJECT_ID"),
            DEFAULT_GMAIL_PUBSUB_PROJECT_ID,
        ),
        gmail_pubsub_topic_id=_str_setting(
            "GMAIL_PUBSUB_TOPIC_ID",
            values.get("GMAIL_PUBSUB_TOPIC_ID"),
            DEFAULT_GMAIL_PUBSUB_TOPIC_ID,
        ),
        gmail_pubsub_subscription_id=_str_setting(
            "GMAIL_PUBSUB_SUBSCRIPTION_ID",
            values.get("GMAIL_PUBSUB_SUBSCRIPTION_ID"),
            DEFAULT_GMAIL_PUBSUB_SUBSCRIPTION_ID,
        ),
        gmail_pubsub_timeout_seconds=_optional_float_setting(
            "GMAIL_PUBSUB_TIMEOUT_SECONDS",
            values.get("GMAIL_PUBSUB_TIMEOUT_SECONDS"),
            default=0.0,
            minimum=0.0,
        ),
    )


def _parse_email_set(raw: str | None) -> frozenset[str]:
    if raw is None:
        return DEFAULT_FAMILY_EMAILS

    normalized = raw.replace("\n", ",")
    return frozenset(email.strip().lower() for email in normalized.split(",") if email.strip())


def _path_setting(raw: str | None, default_name: str) -> Path:
    path = Path(raw or default_name).expanduser()
    return path if path.is_absolute() else SCRIPT_DIR / path


def _int_setting(name: str, raw: str | None, default: int, minimum: int | None = None) -> int:
    if raw is None or raw.strip() == "":
        value = default
    else:
        try:
            value = int(raw)
        except ValueError as exc:
            raise ConfigError(f"{name} must be an integer, got {raw!r}") from exc

    if minimum is not None and value < minimum:
        raise ConfigError(f"{name} must be >= {minimum}, got {value}")

    return value


def _float_setting(name: str, raw: str | None, default: float, minimum: float | None = None) -> float:
    if raw is None or raw.strip() == "":
        value = default
    else:
        try:
            value = float(raw)
        except ValueError as exc:
            raise ConfigError(f"{name} must be a number, got {raw!r}") from exc

    if minimum is not None and value < minimum:
        raise ConfigError(f"{name} must be >= {minimum}, got {value}")

    return value


def _optional_float_setting(
    name: str,
    raw: str | None,
    default: float,
    minimum: float | None = None,
) -> float | None:
    value = _float_setting(name, raw, default, minimum)
    return None if value == 0 else value


def _str_setting(name: str, raw: str | None, default: str) -> str:
    value = (raw if raw is not None else default).strip()
    if not value:
        raise ConfigError(f"{name} must not be empty")
    return value
