from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


class GmailClient:
    def __init__(self, credentials_file: str, token_file: str) -> None:
        self.credentials_file = credentials_file
        self.token_file = token_file

    def _service(self):
        creds = None
        token_path = Path(self.token_file)
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            token_path.write_text(creds.to_json())
        return build("gmail", "v1", credentials=creds)

    def list_messages(self, query: str = "", max_results: int = 10) -> list[dict[str, Any]]:
        svc = self._service()
        result = svc.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        return result.get("messages", [])

    def get_message(self, msg_id: str) -> dict[str, Any]:
        svc = self._service()
        return svc.users().messages().get(userId="me", id=msg_id, format="full").execute()

    def create_draft(self, to: str, subject: str, body: str) -> dict[str, Any]:
        svc = self._service()
        raw = f"To: {to}\r\nSubject: Re: {subject}\r\n\r\n{body}".encode("utf-8")
        encoded = base64.urlsafe_b64encode(raw).decode("utf-8")
        return svc.users().drafts().create(userId="me", body={"message": {"raw": encoded}}).execute()
