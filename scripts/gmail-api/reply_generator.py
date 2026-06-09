from __future__ import annotations

from ollama import Client

from config import DEFAULT_OLLAMA_HOST


class ReplyDraftError(RuntimeError):
    pass


class OllamaReplyGenerator:
    def __init__(self, model: str, body_limit: int, host: str = DEFAULT_OLLAMA_HOST) -> None:
        self.model = model
        self.body_limit = body_limit
        self.client = Client(host=host)

    def draft(self, sender: str, subject: str, body: str) -> str:
        prompt = (
            "Draft a concise, warm email reply. "
            "Do not include email headers or a subject line.\n\n"
            f"From: {sender}\n"
            f"Subject: {subject}\n"
            f"Email body:\n{body[: self.body_limit]}"
        )

        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                think=False,
                options={"temperature": 0},
            )
        except Exception as exc:
            raise ReplyDraftError("Ollama failed to draft a reply") from exc

        content = response.get("message", {}).get("content", "").strip()
        if not content:
            raise ReplyDraftError("Ollama returned an empty reply")

        return content
