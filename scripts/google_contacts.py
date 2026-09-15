#!/usr/bin/env python3
"""Carnet d'adresses Google — ajout idempotent d'un contact par email."""
import json, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = "/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/google_token.json"

def service():
    tok = json.load(open(TOKEN))
    creds = Credentials.from_authorized_user_info(tok)
    return build("people", "v1", credentials=creds)

def find_by_email(svc, email):
    if not email:
        return None
    res = svc.people().searchContacts(
        query=email, pageSize=10, readMask="names,emailAddresses"
    ).execute()
    for p in res.get("results", []):
        for e in p.get("person", {}).get("emailAddresses", []):
            if e.get("value", "").lower() == email.lower():
                return p["person"]["resourceName"]
    return None

def add(name, email=None, org=None, note=None):
    svc = service()
    existing = find_by_email(svc, email) if email else None
    body = {}
    if name:
        parts = name.rsplit(" ", 1)
        body["names"] = [{
            "givenName": parts[0],
            **({"familyName": parts[1]} if len(parts) == 2 else {}),
        }]
    if email:
        body["emailAddresses"] = [{"value": email}]
    if org:
        body["organizations"] = [{"name": org}]
    if note:
        body["biographies"] = [{"contentType": "TEXT_PLAIN", "value": note}]
    if existing:
        # update partiel : on complete via patchCaller? createContact n'existe pas
        # -> updateContact (remplace tout). Pour rester idempotent sans ecraser,
        # on ne fait que signaler l'existence.
        print(f"EXISTS: {name or email} -> {existing} (non modifie)")
        return existing
    person = svc.people().createContact(body=body).execute()
    print(f"CREATED: {name or email} -> {person.get('resourceName')}")
    return person.get("resourceName")

if __name__ == "__main__":
    # Usage: google_contacts.py add --name "X" --email x@y.fr [--org O] [--note N]
    args = sys.argv[1:]
    kw = {}
    i = 0
    while i < len(args):
        if args[i] in ("--name", "--email", "--org", "--note"):
            kw[args[i][2:]] = args[i + 1]
            i += 2
        else:
            i += 1
    add(kw.get("name"), kw.get("email"), kw.get("org"), kw.get("note"))
