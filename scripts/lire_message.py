#!/usr/bin/env python3
"""Lecture complete d'un message (payload recursif) + extraction pieces jointes.

Usage:
  lire_message.py <message_id> [--pj DOSSIER] [--token CHEMIN]
"""
import argparse
import base64
import html
import json
import re
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

DEFAULT_TOKEN = "/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/google_token.json"


def service(token_path):
    data = json.loads(Path(token_path).read_text())
    creds = Credentials(
        token=data.get("token"),
        refresh_token=data.get("refresh_token"),
        token_uri=data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=data.get("client_id"),
        client_secret=data.get("client_secret"),
        scopes=data.get("scopes"),
    )
    if not creds.valid:
        creds.refresh(Request())
    return build("gmail", "v1", credentials=creds)


def strip_html(h):
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>", "\n", h)
    h = re.sub(r"(?i)</(p|div|tr|li|h[1-6]|table)>", "\n", h)
    h = re.sub(r"(?i)<li[^>]*>", "• ", h)
    h = re.sub(r"<[^>]+>", " ", h)
    h = html.unescape(h)
    h = re.sub(r"[ \t\xa0]+", " ", h)
    h = re.sub(r"\n\s*\n+", "\n", h)
    return h.strip()


def headers(payload):
    return {h["name"].lower(): h["value"] for h in payload.get("headers", [])}


def walk(part, svc, mid, pjdir, out):
    mt = part.get("mimeType", "")
    fn = part.get("filename") or ""
    body = part.get("body", {}) or {}
    data = body.get("data")
    if fn and body.get("attachmentId"):
        att = svc.users().messages().attachments().get(
            userId="me", messageId=mid, id=body["attachmentId"]
        ).execute()
        raw = base64.urlsafe_b64decode(att["data"])
        if pjdir:
            pjdir.mkdir(parents=True, exist_ok=True)
            target = pjdir / fn
            target.write_bytes(raw)
            out.append(("attachment", f"{target} ({len(raw)} octets)"))
        else:
            out.append(("attachment", f"{fn} ({len(raw)} octets, non ecrit)"))
    elif data:
        raw = base64.urlsafe_b64decode(data.encode())
        if mt == "text/plain":
            out.append(("text/plain", raw.decode("utf-8", "replace")))
        elif mt == "text/html":
            out.append(("text/html", raw.decode("utf-8", "replace")))
        else:
            out.append((mt, f"<binaire {len(raw)} octets>"))
    for sub in part.get("parts", []) or []:
        walk(sub, svc, mid, pjdir, out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("message_id")
    ap.add_argument("--pj", default=None)
    ap.add_argument("--token", default=DEFAULT_TOKEN)
    a = ap.parse_args()
    svc = service(a.token)
    msg = svc.users().messages().get(userId="me", id=a.message_id, format="full").execute()
    payload = msg["payload"]
    h = headers(payload)
    print("=== EN-TETES ===")
    for k in ["from", "to", "cc", "reply-to", "subject", "date", "message-id"]:
        if h.get(k):
            print(f"{k}: {h[k]}")
    out = []
    walk(payload, svc, a.message_id, Path(a.pj) if a.pj else None, out)
    print("=== CONTENU ===")
    for mt, content in out:
        if mt == "text/html":
            print(strip_html(content))
        else:
            print(f"[{mt}] {content}")


main()
