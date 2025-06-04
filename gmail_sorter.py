#!/usr/bin/env python3
"""Simple Gmail sorting script using Gmail API."""

import argparse
import os
from typing import List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Keyword-based categories
CATEGORIES = {
    "Work": ["project", "meeting", "deadline"],
    "Finance": ["invoice", "payment", "receipt"],
    "Personal": ["party", "family", "friend"],
    "Spam": ["lottery", "prize", "winner"],
}

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def authenticate(token_path: str, credentials_path: str):
    """Authenticate with Gmail and return a service object."""
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        raise RuntimeError(
            "Valid authentication token not found. Run Gmail OAuth flow first."
        )
    service = build("gmail", "v1", credentials=creds)
    return service


def get_messages(service) -> List[dict]:
    """Retrieve a list of message metadata."""
    response = service.users().messages().list(userId="me").execute()
    message_ids = [m["id"] for m in response.get("messages", [])]
    messages = []
    for mid in message_ids:
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=mid, format="metadata", metadataHeaders=["subject"])
            .execute()
        )
        messages.append(msg)
    return messages


def categorize_message(subject: str, snippet: str) -> str:
    """Categorize message based on subject or snippet keywords."""
    text = (subject + " " + snippet).lower()
    for category, keywords in CATEGORIES.items():
        if any(k in text for k in keywords):
            return category
    return "Uncategorized"


def apply_label(service, message_id: str, label: str, dry_run: bool):
    """Apply label to a message."""
    if dry_run:
        print(f"Would label {message_id} as {label}")
        return
    # Ensure label exists or create it
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    label_id = None
    for l in labels:
        if l.get("name") == label:
            label_id = l.get("id")
            break
    if not label_id:
        created = (
            service.users()
            .labels()
            .create(
                userId="me", body={"name": label, "labelListVisibility": "labelShow"}
            )
            .execute()
        )
        label_id = created.get("id")
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": [label_id]},
    ).execute()


def main():
    parser = argparse.ArgumentParser(description="Sort Gmail messages into labels")
    parser.add_argument(
        "--token", default="token.json", help="Path to OAuth token JSON file"
    )
    parser.add_argument(
        "--credentials",
        default="credentials.json",
        help="Path to OAuth credentials JSON file",
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not modify Gmail")
    args = parser.parse_args()

    try:
        service = authenticate(args.token, args.credentials)
        messages = get_messages(service)
        for msg in messages:
            headers = msg.get("payload", {}).get("headers", [])
            subject = next(
                (h.get("value") for h in headers if h.get("name").lower() == "subject"),
                "",
            )
            snippet = msg.get("snippet", "")
            category = categorize_message(subject, snippet)
            apply_label(service, msg["id"], category, args.dry_run)
    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
