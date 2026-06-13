# Gmail Auto Reply

This project watches a Gmail inbox for new messages, filters messages to a configured family sender allowlist, asks Ollama to draft a concise reply, and sends that reply through the Gmail API.

The service is designed for homelab deployment. GitHub Actions builds and pushes `sunmingtao/gmail-auto-reply:latest` when files under `scripts/gmail-api/` change, and the homelab `docker-compose.yml` uses Watchtower to pull the refreshed image every 5 minutes.

## Solution Design

1. `run.py` loads configuration and Gmail OAuth credentials.
2. The Gmail API `users.watch` endpoint binds the mailbox inbox label to a Google Pub/Sub topic.
3. Gmail publishes mailbox change notifications to the topic.
4. The app consumes notifications from the configured Pub/Sub subscription.
5. `GmailHistoryStore` stores the last Gmail history id in SQLite so each notification only processes new changes.
6. `processor.py` loads changed Gmail messages, skips senders outside `GMAIL_FAMILY_EMAILS`, and skips threads that already have a later sent reply.
7. `reply_generator.py` sends the email body to Ollama and requests a concise, warm response.
8. `gmail_client.py` sends the generated reply back into the original Gmail thread.

## Prerequisites

- Python 3.12 for local setup.
- Docker and Docker Compose for homelab deployment.
- Ollama installed on the homelab host with the configured model pulled, for example `qwen3:8b`.
- Google Cloud project with Gmail API and Pub/Sub API enabled.
- OAuth client secret JSON for the Gmail account.
- Google Cloud ADC credentials that can read from the Pub/Sub subscription.

When Ollama runs on the homelab host and this app runs in Docker, Ollama must listen on all interfaces:

```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

The compose file then reaches it through `http://host.docker.internal:11434`.

## Google Cloud Setup

Enable the APIs:

```bash
gcloud services enable gmail.googleapis.com pubsub.googleapis.com
```

Create the Pub/Sub topic and subscription:

```bash
gcloud pubsub topics create smt-gmail-sub-topic
gcloud pubsub subscriptions create smt-gmail --topic=smt-gmail-sub-topic
```

Allow Gmail to publish mailbox notifications to the topic:

```bash
gcloud pubsub topics add-iam-policy-binding smt-gmail-sub-topic \
  --member=serviceAccount:gmail-api-push@system.gserviceaccount.com \
  --role=roles/pubsub.publisher
```

The app calls `users.watch` on startup, so no separate watch registration command is needed. Gmail watches expire periodically; restarting the service refreshes the watch and stores the initial history id when needed.

## Local Setup

From `scripts/gmail-api`:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
mkdir -p secrets
```

Place the OAuth client secret at:

```text
secrets/gmail-api-client-secret.json
```

Create Application Default Credentials for Pub/Sub:

```bash
gcloud auth application-default login
```

The code does not reference `GOOGLE_APPLICATION_CREDENTIALS` directly because Google client libraries use Application Default Credentials automatically. In Docker, `docker-compose.yml` sets `GOOGLE_APPLICATION_CREDENTIALS=/secrets/application_default_credentials.json` so `google-cloud-pubsub` can find the mounted credential file.

Generate the Gmail OAuth token locally, where a browser is available:

```bash
.venv/bin/python -c "from auth import load_credentials; from config import load_settings; load_credentials(load_settings())"
```

This writes `secrets/token.json`. Docker containers usually cannot complete the browser-based OAuth flow, so generate this token locally and copy it to the homelab secrets directory.

## Configuration

Configuration is read from environment variables.

| Variable | Default | Purpose |
| --- | --- | --- |
| `GMAIL_TOKEN_FILE` | `secrets/token.json` | Gmail OAuth authorized-user token. |
| `GMAIL_CLIENT_SECRET_FILE` | `secrets/gmail-api-client-secret.json` | Gmail OAuth client secret JSON. |
| `GMAIL_HISTORY_DB_FILE` | `secrets/gmail-history.sqlite3` | SQLite state file for the last processed Gmail history id. |
| `GMAIL_QUERY` | `category:primary is:unread` | Query used by fallback inbox processing. |
| `GMAIL_USER_ID` | `me` | Gmail API user id. |
| `GMAIL_FAMILY_EMAILS` | built-in allowlist | Comma- or newline-separated sender allowlist. |
| `GMAIL_MAX_RESULTS` | `50` | Maximum Gmail messages to list in fallback mode. |
| `GMAIL_REPLY_BODY_LIMIT` | `4000` | Maximum source email characters sent to Ollama. |
| `GMAIL_OAUTH_PORT` | `0` | Local OAuth callback port; `0` lets the OS choose. |
| `GMAIL_PUBSUB_PROJECT_ID` | `cool-phalanx-303803` | Google Cloud project id for Pub/Sub. |
| `GMAIL_PUBSUB_TOPIC_ID` | `smt-gmail-sub-topic` | Pub/Sub topic used by Gmail watch. |
| `GMAIL_PUBSUB_SUBSCRIPTION_ID` | `smt-gmail` | Pub/Sub subscription consumed by the app. |
| `GMAIL_PUBSUB_TIMEOUT_SECONDS` | `0` | Subscriber timeout; `0` means run until stopped. |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama HTTP endpoint. |
| `OLLAMA_MODEL` | `qwen3:8b` | Ollama model used to draft replies. |
| `LOG_LEVEL` | `INFO` | Python logging level. |
| `GOOGLE_APPLICATION_CREDENTIALS` | unset | ADC file path used by Google Pub/Sub libraries. |

The Gmail OAuth scopes are:

```python
SCOPES = (
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
)
```

## Run Locally

```bash
.venv/bin/python run.py
```

For a bounded local smoke run:

```bash
GMAIL_PUBSUB_TIMEOUT_SECONDS=10 .venv/bin/python run.py
```

## Homelab Deployment

Prepare the homelab secrets directory:

```bash
sudo mkdir -p /opt/gmail-auto-reply/secrets
sudo cp secrets/token.json /opt/gmail-auto-reply/secrets/token.json
sudo cp secrets/gmail-api-client-secret.json /opt/gmail-auto-reply/secrets/gmail-api-client-secret.json
sudo cp ~/.config/gcloud/application_default_credentials.json /opt/gmail-auto-reply/secrets/application_default_credentials.json
```

Start the service:

```bash
docker compose up -d
```

The compose stack contains:

- `gmail-auto-reply`, running `sunmingtao/gmail-auto-reply:latest`.
- `watchtower`, checking every 300 seconds and replacing the app container when a newer Docker Hub image is available.

GitHub Actions builds the image from `scripts/gmail-api/Dockerfile` and pushes:

- `sunmingtao/gmail-auto-reply:latest`
- `sunmingtao/gmail-auto-reply:<github-sha>`

## Troubleshooting

### `invalid_scope: Bad Request`

If OAuth fails with:

```text
`invalid_scope: Bad Request', {'error': 'invalid_scope', 'error_description': 'Bad Request'}`
```

delete the old token and regenerate it with the scopes shown above:

```bash
rm secrets/token.json
.venv/bin/python -c "from auth import load_credentials; from config import load_settings; load_credentials(load_settings())"
```

Also confirm the OAuth consent screen and client are configured for Gmail API access.

### Pub/Sub Permission Errors

Confirm Gmail can publish to the topic:

```bash
gcloud pubsub topics get-iam-policy smt-gmail-sub-topic
```

The policy must include `serviceAccount:gmail-api-push@system.gserviceaccount.com` with `roles/pubsub.publisher`.

### Docker Cannot Reach Ollama

Confirm Ollama is listening on `0.0.0.0:11434` on the host and that the container is using:

```text
OLLAMA_HOST=http://host.docker.internal:11434
```

### Docker Starts OAuth Flow

The container should not need browser OAuth. Generate `secrets/token.json` locally first, then copy it into `/opt/gmail-auto-reply/secrets/token.json`.
