#!/usr/bin/env python3
"""Dump complet d'un message Gmail : headers, text/plain, text/html converti, PJ."""
import base64
import html
import json
import re
import sys

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = "/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/google_token.json"


def strip_html(s: str) -> str:
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</(p|div|tr|li|h[1-6])>", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\u00a0]+", " ", s)
    s = re.sub(r"\n\s*\n\s*\n+", "\n\n", s)
    return s.strip()


def walk(node, acc):
    mime = node.get("mimeType", "")
    fn = node.get("filename") or ""
    data = (node.get("body") or {}).get("data")
    if fn and not data:
        acc.setdefault("attachments", []).append((fn, mime, node.get("body", {}).get("attachmentId")))
    if data and not fn:
        raw = base64.urlsafe_b64decode(data).decode("utf-8", "replace")
        if mime == "text/plain":
            acc.setdefault("plain", []).append(raw)
        elif mime == "text/html":
            acc.setdefault("html", []).append(raw)
    for sub in node.get("parts", []) or []:
        walk(sub, acc)


def main():
    mid = sys.argv[1]
    creds = Credentials.from_authorized_user_info(json.load(open(TOKEN)))
    svc = build("gmail", "v1", credentials=creds)
    msg = svc.users().messages().get(userId="me", id=mid, format="full").execute()
    payload = msg.get("payload", {})
    headers = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}
    acc = {}
    walk(payload, acc)
    print("=== HEADERS ===")
    for k in ("from", "to", "cc", "reply-to", "subject", "date", "message-id"):
        if k in headers:
            print(f"{k}: {headers[k]}")
    print("threadId:", msg.get("threadId"))
    if acc.get("attachments"):
        print("=== ATTACHMENTS ===")
        for a in acc["attachments"]:
            print(a)
    txt = "\n".join(acc.get("plain", []))
    if txt.strip():
        print("=== TEXT/PLAIN ===")
        print(txt.strip())
    for h in acc.get("html", []):
        print("=== TEXT/HTML (converti) ===")
        print(strip_html(h))


if __name__ == "__main__":
    main()
