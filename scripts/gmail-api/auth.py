from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Iterable

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


logger = logging.getLogger(__name__)


class CredentialError(RuntimeError):
    pass


def token_has_required_scopes(token_file: Path, required_scopes: Iterable[str]) -> bool:
    try:
        token_data = json.loads(Path(token_file).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False

    token_scopes = token_data.get("scopes", [])
    if isinstance(token_scopes, str):
        token_scopes = token_scopes.split()

    return set(required_scopes).issubset(set(token_scopes))


def load_credentials(settings) -> Credentials:
    credentials = _load_stored_credentials(settings)

    if credentials and credentials.valid:
        return credentials

    if credentials and credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
            logger.info("Refreshed Gmail OAuth credentials")
        except RefreshError as exc:
            logger.warning("Stored Gmail OAuth credentials could not be refreshed: %s", exc)
            credentials = None

    if not credentials or not credentials.valid:
        credentials = _run_oauth_flow(settings)

    _save_credentials(settings.token_file, credentials)
    return credentials


def _load_stored_credentials(settings) -> Credentials | None:
    token_file = settings.token_file
    if not token_file.exists():
        return None

    if not token_has_required_scopes(token_file, settings.scopes):
        logger.info("Ignoring stored Gmail token because it lacks required scopes")
        return None

    try:
        return Credentials.from_authorized_user_file(str(token_file), settings.scopes)
    except ValueError as exc:
        logger.warning("Ignoring invalid Gmail token file %s: %s", token_file, exc)
        return None


def _run_oauth_flow(settings) -> Credentials:
    if not settings.client_secret_file.exists():
        raise CredentialError(f"Missing Gmail client secret file: {settings.client_secret_file}")

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(settings.client_secret_file),
            settings.scopes,
        )
        return flow.run_local_server(port=settings.local_server_port)
    except Exception as exc:
        raise CredentialError("Gmail OAuth flow failed") from exc


def _save_credentials(token_file: Path, credentials: Credentials) -> None:
    try:
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text(credentials.to_json(), encoding="utf-8")
    except OSError as exc:
        raise CredentialError(f"Could not save Gmail token file {token_file}: {exc}") from exc
