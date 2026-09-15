#!/usr/bin/env python3
"""Classement lot 3 (rattrapage threads) + creation 02b Sollies-Pont + releves bancaires."""
import json, os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN = "/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/google_token.json"
INBOX = "/home/alexis-barlatier/Documents/Semaphore-sonar/inbox_pj"
SCRIPTS = "/home/alexis-barlatier/Documents/Semaphore-sonar/scripts"
EMAIL_ID = "1a070d222e1ee562"

VERRERIE = "1XgMfAlmTdDb9TkoZZYw-eHk4R05AJhhf"
PIPELINE = "15Zs4NuBmtO8ed5PTP2NhHTMIWdh-OBs6"
FISCALITE = "1PWeq-XD1ZATusAKRByS4y3knY3V_skPJ"
FICHE_V_ID = "1UlBupY8HkHAd5gmVx7tkLDoacpwr13v1"

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

def create_folder(name, parent_id):
    r = svc.files().create(
        body={"name": name, "mimeType": "application/vnd.google-apps.folder",
              "parents": [parent_id]},
        fields="id,name",
    ).execute()
    print("FOLDER:", name)
    return r["id"]

def upload(path, parent_id, final_name):
    r = svc.files().create(
        body={"name": final_name, "parents": [parent_id]},
        media_body=MediaFileUpload(path, resumable=False),
        fields="id,name",
    ).execute()
    print("UPLOAD:", final_name)
    return r["id"]

# --- 1. Dossiers cibles ---
baux_v = find_child(VERRERIE, "Baux-et-locataires")
copro_v = find_child(VERRERIE, "Copropriete")

# Releves bancaires : sous-dossier dans 04
rb = find_child(FISCALITE, "Releves-bancaires-2026") or create_folder("Releves-bancaires-2026", FISCALITE)

# --- 2. 02b Sollies-Pont (squelette complet + fiche) ---
d02b = create_folder("02b-Sollies-Pont-2-appartements", PIPELINE)
subs = {}
for s in ["Actes-et-compromis", "Financement", "Baux-et-locataires",
          "Copropriete", "Fiscalite-locale", "Assurance"]:
    subs[s] = create_folder(s, d02b)

# --- 3. Uploads ---
jobs = [
    # Verrerie / Copropriete : regularisation charges 2025 (releve du 22/05/2026)
    (os.path.join(INBOX, "10058196 (1).pdf"), copro_v,
     "2026-05-22_Regul-charges-2025_Verrerie.pdf"),
    # Verrerie / Baux : factures Schindler T2 + PNO + regul 2025 + justificatif
    (os.path.join(INBOX, "facture SCHINDLER 02 04 26.pdf"), baux_v,
     "2026-04-23_Facture-loyer-T2-2026_Schindler.pdf"),
    (os.path.join(INBOX, "facture SCHINDLER 03 04 26.pdf"), baux_v,
     "2026-04-23_Facture-PNO-2026-2027-refacture_Schindler.pdf"),
    (os.path.join(INBOX, "facture SCHINDLER 01 05 26.pdf"), baux_v,
     "2026-05-26_Facture-regul-charges-2025_Schindler.pdf"),
    (os.path.join(INBOX, "facture regul charges 2025.pdf"), baux_v,
     "2026-05-26_Justificatif-regul-charges-2025_Schindler.pdf"),
    # 04 / Releves bancaires CM (compte pro 08980 000214417 03)
    (os.path.join(INBOX, "Extrait de comptes Compte 08980 000214417 03 COMPTE COURANT PROFESSIONNEL SEMAPHORE PATRIMOINE au 2026-06-30.pdf"), rb,
     "2026-06-30_Extrait-compte-pro-CM.pdf"),
    (os.path.join(INBOX, "Extrait de comptes Compte 08980 000214417 03 COMPTE COURANT PROFESSIONNEL SEMAPHORE PATRIMOINE au 2026-06-01.pdf"), rb,
     "2026-06-01_Extrait-compte-pro-CM.pdf"),
    (os.path.join(INBOX, "Compte principal_2026-06-01_2026-06-30.pdf"), rb,
     "2026-06-30_Compte-principal-CM.pdf"),
    (os.path.join(INBOX, "Compte principal_2026-05-01_2026-05-31.pdf"), rb,
     "2026-05-31_Compte-principal-CM.pdf"),
    (os.path.join(INBOX, "Facture de commissions Compte 08980 000214417 03 COMPTE COURANT PROFESSIONNEL SEMAPHORE PATRIMOINE au 2026-06-03.pdf"), rb,
     "2026-06-03_Facture-commissions-CM.pdf"),
    # 02b Sollies-Pont / Financement : projection integration
    (os.path.join(INBOX, "sci semaphoe integraton 2 appartements.xlsx"), subs["Financement"],
     "2026-06-11_Projection-integration-2-appartements.xlsx"),
]
for src, dst, name in jobs:
    upload(src, dst, name)

# --- 4. Fiche 02b ---
upload(os.path.join(SCRIPTS, "fiche_sollies.md"), d02b, "00-FICHE-02b-Sollies-Pont-2-appartements.md")

# --- 5. Fiche 01a enrichie ---
svc.files().update(
    fileId=FICHE_V_ID,
    media_body=MediaFileUpload(os.path.join(SCRIPTS, "fiche_verrerie.md"), resumable=False),
    fields="id,name",
).execute()
print("FICHE 01a mise a jour")

# --- 6. Email traite ---
gmail.users().messages().modify(userId="me", id=EMAIL_ID, body={"removeLabelIds": ["UNREAD"]}).execute()
print("EMAIL traite")
print("DONE")
