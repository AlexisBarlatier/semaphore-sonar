#!/usr/bin/env python3
"""Lecture complete d'un message Gmail : decode toutes les parties (text/plain, text/html),
liste les pieces jointes et les telecharge dans inbox_pj/."""
import base64, html, os, re, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = os.path.expanduser("~/.hermes/profiles/semaphore-sonar/google_token.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
OUT = "/home/alexis-barlatier/Documents/Semaphore-sonar/inbox_pj"

def svc():
    creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    return build("gmail", "v1", credentials=creds)

def walk(part, acc, atts):
    mt = part.get("mimeType", "")
    fn = part.get("filename") or ""
    body = part.get("body", {})
    data = body.get("data")
    if fn and body.get("attachmentId"):
        atts.append((fn, body["attachmentId"], body.get("size", 0)))
    if data:
        raw = base64.urlsafe_b64decode(data)
        acc.append((mt, fn, raw))
    for p in part.get("parts", []) or []:
        walk(p, acc, atts)

def to_text(mt, raw, fn):
    if mt == "text/html":
        t = raw.decode("utf-8", "replace")
        t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t)
        t = re.sub(r"(?i)<br\s*/?>", "\n", t)
        t = re.sub(r"(?i)</(p|div|tr|li|h[1-6])>", "\n", t)
        t = re.sub(r"(?i)<li[^>]*>", "\u2022 ", t)
        t = re.sub(r"<[^>]+>", "", t)
        t = html.unescape(t)
        t = re.sub(r"[ \t]+", " ", t)
        t = re.sub(r"\n\s*\n\s*\n+", "\n\n", t)
        return t.strip()
    return raw.decode("utf-8", "replace").strip()

def main():
    mid = sys.argv[1]
    m = svc().users().messages().get(userId="me", id=mid, format="full").execute()
    h = {x["name"]: x["value"] for x in m["payload"].get("headers", [])}
    print("=" * 70)
    for k in ("From", "To", "Cc", "Reply-To", "Subject", "Date"):
        if k in h:
            print(f"{k}: {h[k]}")
    print("=" * 70)
    acc, atts = [], []
    walk(m["payload"], acc, atts)
    for mt, fn, raw in acc:
        print(f"\n----- part {mt} {fn} -----")
        print(to_text(mt, raw, fn))
    if atts:
        os.makedirs(OUT, exist_ok=True)
        print("\n----- pieces jointes -----")
        for fn, aid, size in atts:
            a = svc().users().messages().attachments().get(userId="me", messageId=mid, id=aid).execute()
            raw = base64.urlsafe_b64decode(a["data"])
            path = os.path.join(OUT, fn)
            with open(path, "wb") as f:
                f.write(raw)
            print(f"{fn} ({len(raw)} octets) -> {path}")

if __name__ == "__main__":
    main()
