#!/usr/bin/env python3
"""Renomme la racine du Drive en « Sémaphore Patrimoine »."""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = "/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/google_token.json"
ROOT_ID = "1Qroc25tfWV2q9At3qgQPkvdUt4eshP4Q"
NEW_NAME = "Sémaphore Patrimoine"

tok = json.load(open(TOKEN))
creds = Credentials.from_authorized_user_info(tok)
svc = build("drive", "v3", credentials=creds)
r = svc.files().update(fileId=ROOT_ID, body={"name": NEW_NAME}, fields="id,name,webViewLink").execute()
print("RENAMED:", r["name"], "|", r["id"])
print("LINK:", r["webViewLink"])
