#!/usr/bin/env python3
"""Lit un message Gmail (format full), decode recursivement les parts et affiche le texte.
Usage: read_msg.py <message_id> [--headers]"""
import base64
import html
import json
import re
import sys

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = "/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/google_token.json"


def to_text(raw: str) -> str:
    txt = re.sub(r"(?is)<(script|style).*?</\1>", "", raw)
    txt = re.sub(r"(?i)<br\s*/?>", "\n", txt)
    txt = re.sub(r"(?i)</p>", "\n\n", txt)
    txt = re.sub(r"(?i)</tr>", "\n", txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt)
    txt = re.sub(r"[ \t\xa0]+", " ", txt)
    txt = re.sub(r"\n\s*\n\s*\n+", "\n\n", txt)
    return txt.strip()


def walk(node, acc, atts):
    mime = node.get("mimeType", "")
    fn = node.get("filename") or ""
    body = node.get("body") or {}
    if fn and body.get("attachmentId"):
        atts.append((fn, mime, body.get("size")))
    if mime == "text/plain" and body.get("data"):
        acc.setdefault("plain", []).append(base64.urlsafe_b64decode(body["data"]).decode("utf-8", "replace"))
    elif mime == "text/html" and body.get("data"):
        acc.setdefault("html", []).append(base64.urlsafe_b64decode(body["data"]).decode("utf-8", "replace"))
    for sub in node.get("parts", []):
        walk(sub, acc, atts)


def main():
    msg_id = sys.argv[1]
    show_headers = "--headers" in sys.argv
    tok = json.load(open(TOKEN))
    svc = build("gmail", "v1", credentials=Credentials.from_authorized_user_info(tok))
    msg = svc.users().messages().get(userId="me", id=msg_id, format="full").execute()
    payload = msg.get("payload", {})
    headers = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}
    acc, atts = {}, []
    walk(payload, acc, atts)
    print("From:", headers.get("from"))
    print("To:", headers.get("to"))
    print("Cc:", headers.get("cc"))
    print("Date:", headers.get("date"))
    print("Subject:", headers.get("subject"))
    print("Labels:", ",".join(msg.get("labelIds", [])))
    if atts:
        print("Pieces jointes:")
        for fn, mime, size in atts:
            print(f"  - {fn} ({mime}, {size} octets)")
    else:
        print("Pieces jointes: aucune")
    if show_headers:
        print("--- headers bruts ---")
        for h in payload.get("headers", []):
            print(f"  {h['name']}: {h['value']}")
    print("--- corps texte ---")
    if acc.get("plain"):
        print("\n".join(acc["plain"])[:6000])
    elif acc.get("html"):
        print(to_text("\n".join(acc["html"]))[:6000])
    else:
        print("(aucune part texte, ni plain ni html)")


if __name__ == "__main__":
    main()
