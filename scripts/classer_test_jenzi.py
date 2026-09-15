#!/usr/bin/env python3
"""Classement du test Jenzi/Dionysos vers 01b-La-Garde-2-ext + contacts."""
import json, os, shutil, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN = "/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/google_token.json"
INBOX = "/home/alexis-barlatier/Documents/Semaphore-sonar/inbox_pj"
WORK = "/home/alexis-barlatier/Documents/Semaphore-sonar/inbox_classement"
BIEN_GARDE = "1pMLD53NIMnI1nbkebVwBoiHaF0KzNg8y"   # 01b-La-Garde-2-ext
FICHE_GARDE_ID = "1OuQFTQcwMNWEgIx3vss2aZgKk3MDMWFQ"  # 00-FICHE-BIEN.md du 01b
EMAIL_ID = "1a0709fb1e9c41a8"                     # email test d'Alexis

SRC_PDF = os.path.join(INBOX, "Copie AAE REGLMT COPRO-EDD JENZI - LE DIONYSOS.pdf")
SRC_EML = os.path.join(INBOX, "Fwd: VENTE JENZI (Dionysos) _ SCI SEMAPHORE PATRIMOINE* (lots 80 et 81).eml")
DST_PDF = os.path.join(WORK, "2024-11-21_RC-EDD_Le-Dionysos-lots-80-81.pdf")
DST_EML = os.path.join(WORK, "2026-09-03_Conversation-Jenzi-vente-lots-80-81.eml")
FICHE_LOCAL = "/home/alexis-barlatier/Documents/Semaphore-sonar/scripts/fiche_garde.md"

tok = json.load(open(TOKEN))
creds = Credentials.from_authorized_user_info(tok)
svc = build("drive", "v3", credentials=creds)
gmail = build("gmail", "v1", credentials=creds)

def find_child(parent_id, child_name):
    r = svc.files().list(
        q=f"'{parent_id}' in parents and trashed=false and name='{child_name}'",
        pageSize=10, fields="files(id,name)",
    ).execute()
    fl = r.get("files", [])
    return fl[0]["id"] if fl else None

os.makedirs(WORK, exist_ok=True)
shutil.copy(SRC_PDF, DST_PDF)
shutil.copy(SRC_EML, DST_EML)

# 1. Resoudre le sous-dossier Actes-et-compromis du 01b
actes = find_child(BIEN_GARDE, "Actes-et-compromis")
print("Actes-et-compromis (01b):", actes)

# 2. Upload PDF + EML
for path in (DST_PDF, DST_EML):
    up = svc.files().create(
        body={"name": os.path.basename(path), "parents": [actes]},
        media_body=MediaFileUpload(path, resumable=False),
        fields="id,name,webViewLink",
    ).execute()
    print("UPLOADED:", up["name"], "->", up["webViewLink"])

# 3. Mise a jour de la fiche bien (contenu remplace, nom conserve)
upd = svc.files().update(
    fileId=FICHE_GARDE_ID,
    media_body=MediaFileUpload(FICHE_LOCAL, resumable=False),
    fields="id,name",
).execute()
print("FICHE UPDATED:", upd["name"], "|", upd["id"])

# 4. Marquer l'email traite (retirer UNREAD)
gmail.users().messages().modify(
    userId="me", id=EMAIL_ID, body={"removeLabelIds": ["UNREAD"]}
).execute()
print("EMAIL traite:", EMAIL_ID)

print("DONE")
