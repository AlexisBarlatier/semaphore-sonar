#!/usr/bin/env python3
"""Lister / lire des messages de la boite semaphoresonar via google_api.py."""
import json
import subprocess
import sys
import base64
import html
import re

PY = "/home/alexis-barlatier/.hermes/hermes-agent/venv/bin/python3"
GAPI = "/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/skills/productivity/google-workspace/scripts/google_api.py"


def run(args):
    p = subprocess.run([PY, GAPI] + args, capture_output=True, text=True)
    if p.returncode != 0:
        print("ERR", p.stderr[:500])
        return None
    try:
        return json.loads(p.stdout)
    except Exception:
        return p.stdout


def strip_html(h):
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>", "\n", h)
    h = re.sub(r"(?i)</(p|div|tr|li|h[1-6])>", "\n", h)
    h = re.sub(r"(?i)<li[^>]*>", "• ", h)
    h = re.sub(r"<[^>]+>", " ", h)
    h = html.unescape(h)
    h = re.sub(r"[ \t\xa0]+", " ", h)
    h = re.sub(r"\n\s*\n+", "\n", h)
    return h.strip()


def walk(part, out):
    mt = part.get("mimeType", "")
    body = part.get("body", {})
    data = body.get("data")
    if data:
        raw = base64.urlsafe_b64decode(data.encode())
        if mt == "text/plain":
            out.append(("text/plain", raw.decode("utf-8", "replace")))
        elif mt == "text/html":
            out.append(("text/html", raw.decode("utf-8", "replace")))
        else:
            out.append((mt, f"<binaire {len(raw)} octets>"))
    for sub in part.get("parts", []) or []:
        walk(sub, out)
    for att in part.get("attachments", []) or []:
        out.append(("attachment", json.dumps(att)))


def main():
    cmd = sys.argv[1]
    if cmd == "list":
        q = sys.argv[2] if len(sys.argv) > 2 else "newer_than:2d"
        mx = sys.argv[3] if len(sys.argv) > 3 else "60"
        d = run(["gmail", "search", q, "--max", mx])
        if not isinstance(d, list):
            print(d)
            return
        print(len(d), "messages")
        for m in d:
            print(f"{m['date']} | {m['from'][:50]} | {m['subject'][:65]} | {m['id']} | {m['threadId']}")
    elif cmd == "read":
        mid = sys.argv[2]
        d = run(["gmail", "get", mid, "--format", "full"])
        if not isinstance(d, dict):
            print(d)
            return
        print("HEADERS:", json.dumps({k: v for k, v in d.items() if k != "body"}, ensure_ascii=False)[:1500])
        payload = d.get("payload")
        out = []
        if payload:
            walk(payload, out)
        for mt, content in out:
            if mt == "text/html":
                print("--- HTML ---")
                print(strip_html(content)[:6000])
            else:
                print(f"--- {mt} ---")
                print(content[:3000])


main()
