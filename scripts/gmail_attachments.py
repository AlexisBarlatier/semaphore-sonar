#!/usr/bin/env python3
"""Extrait les pieces jointes d'un message Gmail vers un dossier local."""
import base64, json, os, sys
from email import message_from_bytes
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = "/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/google_token.json"
OUT = "/home/alexis-barlatier/Documents/Semaphore-sonar/inbox_pj"

def walk(part, depth=0, msg=None):
    """Parcourt le payload MIME et retourne la liste des pieces jointes."""
    out = []
    fn = part.get("filename") or ""
    ctype = part.get_content_type() if hasattr(part, "get_content_type") else part.get("mimeType", "")
    body = part.get("body") if isinstance(part, dict) else None
    data = None
    if isinstance(part, dict):
        fn = part.get("filename") or ""
        body = part.get("body") or {}
        data = body.get("data")
        if part.get("mimeType") == "text/plain" and not fn:
            return []
        if fn and data:
            out.append((fn, base64.urlsafe_b64decode(data), part.get("mimeType", "")))
        for sub in part.get("parts", []):
            out += walk(sub, depth + 1)
    return out

def fetch_attachments(service, msg_id):
    """Recupere les PJ d'un message (format full, decode inline)."""
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    payload = msg.get("payload", {})
    atts = []
    def scan(node):
        fn = node.get("filename", "") or ""
        mime = node.get("mimeType", "")
        if fn and node.get("body", {}).get("attachmentId"):
            att_id = node["body"]["attachmentId"]
            data = service.users().messages().attachments().get(
                userId="me", messageId=msg_id, id=att_id
            ).execute().get("data", "")
            atts.append((fn, base64.urlsafe_b64decode(data), mime))
        for sub in node.get("parts", []):
            scan(sub)
    scan(payload)
    return atts, msg

def main():
    msg_id = sys.argv[1]
    tok = json.load(open(TOKEN))
    creds = Credentials.from_authorized_user_info(tok)
    svc = build("gmail", "v1", credentials=creds)

    atts, msg = fetch_attachments(svc, msg_id)
    os.makedirs(OUT, exist_ok=True)
    headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}
    print("Message:", msg_id)
    print("  From:", headers.get("from"))
    print("  Subject:", repr(headers.get("subject", "")))
    print(f"  {len(atts)} piece(s) jointe(s)")
    for fn, data, mime in atts:
        safe = fn.replace("/", "_").replace("\\", "_")
        path = os.path.join(OUT, safe)
        with open(path, "wb") as f:
            f.write(data)
        print(f"  - {fn} ({mime}, {len(data)} octets) -> {path}")

if __name__ == "__main__":
    main()
