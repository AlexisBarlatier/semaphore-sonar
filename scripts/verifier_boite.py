#!/usr/bin/env python3
"""Verifie l'identite de la boite Gmail associee a un token (users().getProfile())."""
import json
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

token_path = Path(sys.argv[1])
data = json.loads(token_path.read_text())
creds = Credentials(
    token=data.get("token"),
    refresh_token=data.get("refresh_token"),
    token_uri=data.get("token_uri", "https://oauth2.googleapis.com/token"),
    client_id=data.get("client_id"),
    client_secret=data.get("client_secret"),
    scopes=data.get("scopes"),
)
if not creds.valid:
    creds.refresh(Request())
svc = build("gmail", "v1", credentials=creds)
prof = svc.users().getProfile(userId="me").execute()
print(token_path)
print("  emailAddress :", prof.get("emailAddress"))
print("  messagesTotal:", prof.get("messagesTotal"))
print("  scopes       :", (data.get("scopes") or []))
