import smtplib
import unittest
from unittest.mock import patch

from app import notifier


class NotifierTests(unittest.TestCase):
    def test_recipient_list_accepts_commas_and_semicolons(self) -> None:
        recipients = notifier._recipient_list("a@example.com, b@example.com; c@example.com")

        self.assertEqual(
            recipients,
            ["a@example.com", "b@example.com", "c@example.com"],
        )

    def test_send_email_skips_when_required_settings_are_missing(self) -> None:
        with (
            patch.object(notifier, "SMTP_USERNAME", ""),
            patch.object(notifier, "SMTP_PASSWORD", ""),
            patch.object(notifier, "EMAIL_FROM", ""),
            patch("builtins.print") as print_mock,
        ):
            sent = notifier.send_email("Subject", "Body", recipients="")

        self.assertFalse(sent)
        print_mock.assert_called_once()
        self.assertIn("missing settings", print_mock.call_args.args[0])

    def test_send_email_sends_message_through_smtp(self) -> None:
        with (
            patch.object(notifier, "SMTP_HOST", "smtp.example.com"),
            patch.object(notifier, "SMTP_PORT", 587),
            patch.object(notifier, "SMTP_USERNAME", "sender@example.com"),
            patch.object(notifier, "SMTP_PASSWORD", "app-password"),
            patch.object(notifier, "EMAIL_FROM", "sender@example.com"),
            patch.object(notifier.smtplib, "SMTP") as smtp_class,
            patch("builtins.print"),
        ):
            smtp = smtp_class.return_value.__enter__.return_value

            sent = notifier.send_email(
                "Pipeline finished",
                "All done",
                recipients="recipient@example.com",
            )

        self.assertTrue(sent)
        smtp_class.assert_called_once_with("smtp.example.com", 587, timeout=30)
        smtp.starttls.assert_called_once_with()
        smtp.login.assert_called_once_with("sender@example.com", "app-password")
        smtp.send_message.assert_called_once()

        email_message = smtp.send_message.call_args.args[0]
        self.assertEqual(email_message["From"], "sender@example.com")
        self.assertEqual(email_message["To"], "recipient@example.com")
        self.assertEqual(email_message["Subject"], "Pipeline finished")

    def test_send_email_returns_false_when_smtp_fails(self) -> None:
        with (
            patch.object(notifier, "SMTP_HOST", "smtp.example.com"),
            patch.object(notifier, "SMTP_PORT", 587),
            patch.object(notifier, "SMTP_USERNAME", "sender@example.com"),
            patch.object(notifier, "SMTP_PASSWORD", "app-password"),
            patch.object(notifier, "EMAIL_FROM", "sender@example.com"),
            patch.object(notifier.smtplib, "SMTP", side_effect=smtplib.SMTPException("nope")),
            patch("builtins.print") as print_mock,
        ):
            sent = notifier.send_email("Subject", "Body", recipients="recipient@example.com")

        self.assertFalse(sent)
        self.assertIn("Email notification failed", print_mock.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
