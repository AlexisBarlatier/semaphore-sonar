#!/usr/bin/env python3
"""Renomme un fichier Drive. Usage: drive_rename.py FILE_ID "Nouveau nom"."""
import json, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = "/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/google_token.json"
FILE_ID, NEW_NAME = sys.argv[1], sys.argv[2]

tok = json.load(open(TOKEN))
creds = Credentials.from_authorized_user_info(tok)
svc = build("drive", "v3", credentials=creds)
r = svc.files().update(fileId=FILE_ID, body={"name": NEW_NAME}, fields="id,name").execute()
print("RENAMED:", r["name"], "|", r["id"])
