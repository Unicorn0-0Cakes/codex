# codex

This repository contains example projects and utilities. The `gmail_sorter.py` script demonstrates how to use the Gmail API to automatically label incoming messages based on simple keyword rules.

## gmail_sorter.py

The script connects to Gmail using OAuth credentials and categorizes each message by inspecting its subject and snippet. Labels are applied according to predefined keywords.

### Setup

1. Install dependencies:
   ```bash
   pip install google-auth google-auth-oauthlib google-api-python-client
   ```
2. Create OAuth credentials and download `credentials.json` from the Google Cloud console. Run the OAuth flow separately to generate `token.json`.

### Usage

```bash
python gmail_sorter.py --dry-run
```

Use `--dry-run` to preview labeling without modifying your account. Omitting this flag will apply labels to messages.
