from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import load_settings


class ConfigTest(unittest.TestCase):
    def test_load_settings_from_environment(self) -> None:
        token_file = Path("/tmp/gmail-token.json")
        client_secret_file = Path("/tmp/gmail-client.json")

        settings = load_settings(
            {
                "GMAIL_FAMILY_EMAILS": "A@Example.com, b@example.com",
                "GMAIL_TOKEN_FILE": str(token_file),
                "GMAIL_CLIENT_SECRET_FILE": str(client_secret_file),
                "GMAIL_QUERY": "is:unread",
                "GMAIL_USER_ID": "me",
                "LOG_LEVEL": "debug",
                "GMAIL_OAUTH_PORT": "8080",
                "GMAIL_REPLY_BODY_LIMIT": "123",
                "GMAIL_MAX_RESULTS": "7",
                "OLLAMA_MODEL": "test-model",
            }
        )

        self.assertEqual(settings.family_emails, frozenset({"a@example.com", "b@example.com"}))
        self.assertEqual(settings.token_file, token_file)
        self.assertEqual(settings.client_secret_file, client_secret_file)
        self.assertEqual(settings.gmail_query, "is:unread")
        self.assertEqual(settings.log_level, "DEBUG")
        self.assertEqual(settings.local_server_port, 8080)
        self.assertEqual(settings.reply_body_limit, 123)
        self.assertEqual(settings.max_results, 7)
        self.assertEqual(settings.ollama_model, "test-model")


if __name__ == "__main__":
    unittest.main()
