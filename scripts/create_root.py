#!/usr/bin/env python3
"""Deplace sous Semaphore-Immo tous les elements de tete (parent = My Drive)."""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = "/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/google_token.json"
NEW_ROOT = "1Qroc25tfWV2q9At3qgQPkvdUt4eshP4Q"  # Semaphore-Immo

tok = json.load(open(TOKEN))
creds = Credentials.from_authorized_user_info(tok)
svc = build("drive", "v3", credentials=creds)

# Tous les fichiers avec leur parent
r = svc.files().list(
    q="trashed=false", pageSize=1000,
    fields="files(id,name,parents,mimeType)",
).execute()
items = r.get("files", [])

# Elements dont l'UNIQUE parent est le My Drive, hors la nouvelle racine
MYDRIVE = "0AAQk8EFTmvpAUk9PVA"
tete = [
    f for f in items
    if f["id"] != NEW_ROOT
    and f.get("parents") == [MYDRIVE]
]
print(f"{len(tete)} elements de tete a deplacer sous Semaphore-Immo")

for f in sorted(tete, key=lambda x: x["name"]):
    upd = svc.files().update(
        fileId=f["id"],
        addParents=NEW_ROOT,
        removeParents=MYDRIVE,
        fields="id,name,parents",
    ).execute()
    print("MOVED:", f["name"])

print("DONE")
