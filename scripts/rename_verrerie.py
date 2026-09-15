#!/usr/bin/env python3
"""Renomme le dossier bien 01a (Jean Rostand -> La Verrerie)."""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = "/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/google_token.json"
FOLDER_ID = "1XgMfAlmTdDb9TkoZZYw-eHk4R05AJhhf"
NEW_NAME = "01a-Valentine-La-Verrerie-13pkgs"

tok = json.load(open(TOKEN))
creds = Credentials.from_authorized_user_info(tok)
svc = build("drive", "v3", credentials=creds)
r = svc.files().update(fileId=FOLDER_ID, body={"name": NEW_NAME}).execute()
print("RENAMED:", r["name"], "|", r["id"])
