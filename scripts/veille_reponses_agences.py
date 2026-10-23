#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Veille des réponses d'agences — sortie déterministe pour le `monitor` du cron.

Principe : n'affiche que les messages ENTRANTS des domaines d'agences surveillés.
Le monitor compare la sortie à celle du passage précédent : sortie identique =
aucune exécution d'agent, donc aucun message envoyé au groupe. C'est ce qui
empêche le relais de dire « rien de nouveau » trois fois par jour.

Sortie : une ligne par message, triée, sans horodatage de run.
"""
import json
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = Path("/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/google_token.json")

# Domaines des agences avec lesquelles un fil est ouvert.
DOMAINES = [
    "hvs-immo.fr",            # HVS Real Estate (Lagavon, terrain Les Pennes-Mirabeau)
    "agenceibox.com",         # IBOX Vauban (parking Toulon Saint-Jean)
    "agence-rex.com",         # Agence REX (immeuble 8 lots Brignoles)
    "newstyleimmo.fr",        # New Style Immo (immeuble 256 m² Toulon)
    "newstyle-immo.fr",       # variante avec tiret
    "skylinerealestate.fr",   # Skyline (T3 La Cabucelle)
    "laforet.com",            # Laforêt (Cuers Les Bousquets)
    "safti.fr",               # SAFTI (Le Luc, clos mais on laisse le fil)
    "dvacchino3@gmail.com",   # Déborah Vacchino — HAPPYSSIMMO / IMVESTIGO (Brignoles Dréo)
    "ehimmobilier.fr",        # E.H Immobilier (immeuble 300 m² Toulon Ouest)
]


def main():
    try:
        scopes = json.loads(TOKEN.read_text())["scopes"]
        creds = Credentials.from_authorized_user_file(str(TOKEN), scopes)
        service = build("gmail", "v1", credentials=creds)

        filtre = " OR ".join(f"from:{d}" for d in DOMAINES)
        requete = f"newer_than:21d -in:sent ({filtre})"
        res = service.users().messages().list(
            userId="me", q=requete, maxResults=60
        ).execute()

        lignes = []
        for m in res.get("messages", []):
            detail = service.users().messages().get(
                userId="me", id=m["id"], format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            ).execute()
            entetes = {x["name"].lower(): x["value"] for x in detail["payload"]["headers"]}
            lignes.append(
                f'{entetes.get("date", "")} | {entetes.get("from", "")} | '
                f'{entetes.get("subject", "")} | {m["id"]}'
            )

        print("\n".join(sorted(lignes)) if lignes else "AUCUN")
    except Exception as exc:  # sortie stable en cas de panne : pas de faux réveil
        print(f"ERREUR {type(exc).__name__}")
        sys.exit(0)


if __name__ == "__main__":
    main()
