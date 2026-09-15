#!/usr/bin/env python3
"""Met a jour le contenu d'un fichier Drive texte (sans changer le nom)."""
import json, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN = "/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/google_token.json"
FILE_ID = sys.argv[1]
LOCAL = sys.argv[2]

tok = json.load(open(TOKEN))
creds = Credentials.from_authorized_user_info(tok)
svc = build("drive", "v3", credentials=creds)
r = svc.files().update(
    fileId=FILE_ID,
    media_body=MediaFileUpload(LOCAL, resumable=False),
    fields="id,name",
).execute()
print("UPDATED:", r["name"], "|", r["id"])
