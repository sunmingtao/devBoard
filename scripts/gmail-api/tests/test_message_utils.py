from __future__ import annotations

import base64
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from message_utils import build_reply_email, decode_base64url, extract_body, get_header, reply_subject


def encoded(value: str) -> str:
    return base64.urlsafe_b64encode(value.encode("utf-8")).decode("utf-8").rstrip("=")


class MessageUtilsTest(unittest.TestCase):
    def test_get_header_is_case_insensitive(self) -> None:
        headers = [{"name": "Subject", "value": "Hello"}]
        self.assertEqual(get_header(headers, "subject"), "Hello")

    def test_decode_base64url_repairs_missing_padding(self) -> None:
        self.assertEqual(decode_base64url(encoded("hello")), "hello")

    def test_extract_body_prefers_nested_plain_text(self) -> None:
        payload = {
            "mimeType": "multipart/alternative",
            "parts": [
                {"mimeType": "text/html", "body": {"data": encoded("<p>HTML body</p>")}},
                {
                    "mimeType": "multipart/mixed",
                    "parts": [
                        {"mimeType": "text/plain", "body": {"data": encoded("Plain body")}},
                    ],
                },
            ],
        }

        self.assertEqual(extract_body(payload), "Plain body")

    def test_reply_subject_does_not_duplicate_re_prefix(self) -> None:
        self.assertEqual(reply_subject("Re: Hello"), "Re: Hello")
        self.assertEqual(reply_subject("Hello"), "Re: Hello")

    def test_build_reply_email_sets_threading_headers(self) -> None:
        headers = [
            {"name": "Message-ID", "value": "<child@example.com>"},
            {"name": "References", "value": "<root@example.com>"},
        ]

        reply = build_reply_email(
            to="Sender <sender@example.com>",
            subject="Question",
            body="Thanks!",
            original_headers=headers,
        )

        self.assertEqual(reply["To"], "Sender <sender@example.com>")
        self.assertEqual(reply["Subject"], "Re: Question")
        self.assertEqual(reply["In-Reply-To"], "<child@example.com>")
        self.assertEqual(reply["References"], "<root@example.com> <child@example.com>")
        self.assertIn("Thanks!", reply.get_content())


if __name__ == "__main__":
    unittest.main()
