#!/usr/bin/env python3
"""Classement du lot de rattrapage (9 documents) + creation 02a + fiches."""
import json, os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN = "/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/google_token.json"
INBOX = "/home/alexis-barlatier/Documents/Semaphore-sonar/inbox_pj"
SCRIPTS = "/home/alexis-barlatier/Documents/Semaphore-sonar/scripts"
EMAIL_ID = "1a070c02fdec5dad"                       # conteneur "à classer :-)"

# IDs connus
PARC = "1QIx252z9jmei5iG_tPQ-aXgn9ATtDust"          # 01-Parc
VERRERIE = "1XgMfAlmTdDb9TkoZZYw-eHk4R05AJhhf"      # 01a
GARDE = "1pMLD53NIMnI1nbkebVwBoiHaF0KzNg8y"         # 01b
PIPELINE = "15Zs4NuBmtO8ed5PTP2NhHTMIWdh-OBs6"       # 02
FISCALITE = "1PWeq-XD1ZATusAKRByS4y3knY3V_skPJ"      # 04
FICHE_VERRERIE_ID = "1UlBupY8HkHAd5gmVx7tkLDoacpwr13v1"

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

# 1. Resoudre les sous-dossiers existants
baux_v = find_child(VERRERIE, "Baux-et-locataires")
copro_v = find_child(VERRERIE, "Copropriete")
actes_g = find_child(GARDE, "Actes-et-compromis")
print(f"baux_v={baux_v} copro_v={copro_v} actes_g={actes_g}")

# 2. Ajouter Copropriete au 01b (copro Le Dionysos confirmee par le RC/EDD)
if not find_child(GARDE, "Copropriete"):
    copro_g = create_folder("Copropriete", GARDE)
else:
    copro_g = find_child(GARDE, "Copropriete")
    print("Copropriete (01b) existant")

# 3. Creer 02a-Parc-des-Arts-Marseille9 + squelette
d02a = create_folder("02a-Parc-des-Arts-Marseille9", PIPELINE)
SQUELETTE = ["Actes-et-compromis", "Financement", "Baux-et-locataires",
             "Copropriete", "Fiscalite-locale", "Assurance"]
subs = {}
for s in SQUELETTE:
    subs[s] = create_folder(s, d02a)

# 4. Uploads (source, dossier, nom final)
jobs = [
    # 01a Verrerie — copro
    (os.path.join(INBOX, "10059200.pdf"), copro_v,
     "2026-06-30_Releve-compte-appels-fonds_Verrerie.pdf"),
    # 01a Verrerie — locataire Schindler
    (os.path.join(INBOX, "facture SCHINDLER 01 07 26.pdf"), baux_v,
     "2026-07-02_Facture-loyer-T3-2026_Schindler.pdf"),
    (os.path.join(INBOX, "facture SCHINDLER 02 07 26.pdf"), baux_v,
     "2026-07-02_Facture-charges-T3-2026_Schindler.pdf"),
    # 01b La Garde — actes
    (os.path.join(INBOX, "ETAT CIVIL ACQUEREUR.docx"), actes_g,
     "2026-08-21_Fiche-renseignements-acquereur_Delta-Immobilier.docx"),
    # 04 Fiscalite-SCI — pieces comptables
    (os.path.join(INBOX, "Invoice-Z0ACVWIH-0001.pdf"), FISCALITE,
     "2026-07-23_Facture-LyBox-abonnement-2026-2027.pdf"),
    (os.path.join(INBOX, "efacturestabbord.aspx.pdf"), FISCALITE,
     "2026-07-15_Mandat-PDP-facturation-electronique.pdf"),
    # 02a Parc des Arts — docs vendeur
    (os.path.join(INBOX, "plan-de-masse-ok_compressed.pdf"), subs["Actes-et-compromis"],
     "2026-07-27_Plan-de-masse_Parc-des-Arts-Marseille9.pdf"),
    (os.path.join(INBOX, "erp-du-05.06.2023.pdf"), subs["Actes-et-compromis"],
     "2023-06-05_ERP_Parc-des-Arts-Marseille9.pdf"),
    (os.path.join(INBOX, "parc-des-arts-synoptiques-edd-2.pdf"), subs["Actes-et-compromis"],
     "2026-07-27_EDD-synoptique_Parc-des-Arts-Marseille9.pdf"),
]
for src, dst, name in jobs:
    upload(src, dst, name)

# 5. Fiches
# 01a : update contenu
svc.files().update(
    fileId=FICHE_VERRERIE_ID,
    media_body=MediaFileUpload(os.path.join(SCRIPTS, "fiche_verrerie.md"), resumable=False),
    fields="id,name",
).execute()
print("FICHE 01a mise a jour")
# 02a : upload fiche
upload(os.path.join(SCRIPTS, "fiche_parcdesarts.md"), d02a,
       "00-FICHE-02a-Parc-des-Arts-Marseille9.md")

# 6. Email traite
gmail.users().messages().modify(
    userId="me", id=EMAIL_ID, body={"removeLabelIds": ["UNREAD"]}
).execute()
print("EMAIL traite")

print("DONE")
