import os.path

import ollama
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.utils import parseaddr, parsedate_to_datetime

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
FAMILY_EMAILS = {
    "8011560@radford.act.edu.au",
    "8011638@radford.act.edu.au",
    "selina1224@gmail.com",
    "smtttt@gmail.com",
}
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:8b")

def get_header(headers, name):
    return next(
        (h["value"] for h in headers if h["name"].lower() == name.lower()),
        ""
    )

def decode_base64url(data):
    if not data:
        return ""
    return base64.urlsafe_b64decode(data.encode("UTF-8")).decode("UTF-8", errors="replace")


def extract_body(payload):
    # Case 1: body is directly on this payload
    body_data = payload.get("body", {}).get("data")
    mime_type = payload.get("mimeType", "")

    if body_data and mime_type == "text/plain":
        return decode_base64url(body_data)

    # Case 2: multipart email
    parts = payload.get("parts", [])
    plain_body = ""
    html_body = ""

    for part in parts:
        part_mime = part.get("mimeType", "")
        part_body_data = part.get("body", {}).get("data")

        if part_body_data:
            decoded = decode_base64url(part_body_data)

            if part_mime == "text/plain":
                plain_body += decoded
            elif part_mime == "text/html":
                html_body += decoded

        # recursive for nested multipart/alternative
        if part.get("parts"):
            nested_body = extract_body(part)
            if nested_body:
                plain_body += nested_body

    return plain_body or html_body

def has_replied_after_message(service, msg):
    thread_id = msg["threadId"]
    msg_timestamp = int(msg["internalDate"])

    thread = service.users().threads().get(
        userId="me",
        id=thread_id,
        format="metadata"
    ).execute()

    for thread_msg in thread.get("messages", []):
        labels = thread_msg.get("labelIds", [])
        internal_date = int(thread_msg.get("internalDate", 0))

        if "SENT" in labels and internal_date > msg_timestamp:
            return True

    return False

def draft_reply_with_ollama(sender, subject, body):
    prompt = (
        "Draft a concise, warm email reply. Do not include email headers or a subject line.\n\n"
        f"From: {sender}\n"
        f"Subject: {subject}\n"
        f"Email body:\n{body[:4000]}"
    )
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        think=False,
        options={
            "temperature": 0,
        }
    )

    return response["message"]["content"].strip()

def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "gmail-api-client-secret.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    print("Getting messages from your inbox...")
    results = (
      service.users().messages().list(userId="me", q="category:primary is:unread").execute()
    )
    messages = results.get("messages", [])

    if not messages:
      print("No messages found.")
      return
  
    print("Messages:")
    for message in messages:
      print(f'Message ID: {message["id"]}')
      msg = (
        service.users().messages().get(userId="me", id=message["id"]).execute()
      )
      headers = msg.get("payload", {}).get("headers", [])

      sender = get_header(headers, "From")
      subject = get_header(headers, "Subject")
      date_raw = get_header(headers, "Date")
      timestamp = parsedate_to_datetime(date_raw) if date_raw else None
      body = extract_body(msg.get("payload", {}))

      print(f'Message ID: {message["id"]}')
      print(f"  From: {sender}")
      print(f"  Subject: {subject}")
      print(f"  Date: {timestamp}")

      sender_email = parseaddr(sender)[1].lower()
      if sender_email not in FAMILY_EMAILS:
        print("Not a family email")
      elif has_replied_after_message(service, msg):
        print("Already replied")
        print(draft_reply_with_ollama(sender, subject, body))
      else:
        print("Need reply")
        print("Draft reply:")
        print(draft_reply_with_ollama(sender, subject, body))

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()
