#!/usr/bin/env python3
"""Compact summary of Gmail messages: from/subject/date/attachments + body head."""
import json
import subprocess
import sys

PY = "/home/alexis-barlatier/.hermes/hermes-agent/venv/bin/python"
GAPI = "/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/skills/productivity/google-workspace/scripts/google_api.py"


def run(args):
    r = subprocess.run([PY, GAPI] + args, capture_output=True, text=True)
    return r.stdout, r.stderr


def main():
    ids = sys.argv[1:]
    for mid in ids:
        out, err = run(["gmail", "get", mid])
        try:
            d = json.loads(out)
        except Exception:
            print(f"=== {mid} FAILED: {err[:300]}")
            continue
        if isinstance(d, list):
            d = d[0] if d else {}
        print("=" * 70)
        print(f"ID: {mid}")
        print(f"FROM: {d.get('from')}")
        print(f"TO: {d.get('to')}")
        print(f"DATE: {d.get('date')}")
        print(f"SUBJECT: {d.get('subject')}")
        att = d.get("attachments") or []
        names = []
        for a in att:
            if isinstance(a, dict):
                names.append(a.get("filename") or a.get("name"))
            else:
                names.append(str(a))
        print(f"ATTACHMENTS: {names}")
        body = (d.get("body") or "")
        print("BODY_HEAD:", body[:1200].replace("\n", " | "))
        print()


if __name__ == "__main__":
    main()
