#!/usr/bin/env python3
"""Cree l'arborescence du Drive Semaphore (a executer avec le venv hermes)."""
import json, subprocess, sys, os

PY = "/home/alexis-barlatier/.hermes/hermes-agent/venv/bin/python"
GAPI = "/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/skills/productivity/google-workspace/scripts/google_api.py"
CONV = "/home/alexis-barlatier/Documents/Semaphore-sonar/scripts/drive_conventions.txt"

created = []

def run(*args):
    r = subprocess.run([PY, GAPI, *args], capture_output=True, text=True)
    if r.returncode != 0:
        print("ERR:", r.stderr or r.stdout)
        sys.exit(1)
    return json.loads(r.stdout)

def folder(name, parent=None):
    cmd = ["drive", "create-folder", name]
    if parent:
        cmd += ["--parent", parent]
    out = run(*cmd)
    created.append(out["id"])
    print("CREATED", out["webViewLink"] or name)
    return out["id"]

def upload(path, parent=None):
    cmd = ["drive", "upload", path]
    if parent:
        cmd += ["--parent", parent]
    out = run(*cmd)
    created.append(out["id"])
    print("UPLOADED", out["webViewLink"] or out["name"])
    return out["id"]

# --- Racine ---
rid = {}
for name in ["00-INBOX", "01-Parc", "02-Pipeline-opportunites",
             "03-Banque-et-financement", "04-Fiscalite-SCI",
             "05-Notaire-et-juridique", "06-Reporting"]:
    rid[name] = folder(name)

# --- Squelette standard ---
SQUELETTE = ["Actes-et-compromis", "Financement", "Baux-et-locataires",
             "Copropriete", "Fiscalite-locale", "Assurance"]

# Bien 1 : La Valentine (13 parkings ss-sol, copro Verrerie)
b1 = folder("01a-Valentine-Jean-Rostand-13pkgs", rid["01-Parc"])
for s in SQUELETTE:
    folder(s, b1)

# Bien 2 : La Garde (2 places exterieures, sans syndic -> pas de Copropriete)
b2 = folder("01b-La-Garde-2-ext", rid["01-Parc"])
for s in SQUELETTE:
    if s != "Copropriete":
        folder(s, b2)

# --- Conventions a la racine ---
upload(CONV)

print(f"\nDONE: {len(created)} entrees creees.")
