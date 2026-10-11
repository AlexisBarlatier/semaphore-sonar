#!/usr/bin/env python3
import json, sys
raw = sys.stdin.read()
try:
    d = json.loads(raw)
except Exception as e:
    print("PARSE ERR", e)
    print(raw[:2000])
    raise SystemExit(1)
if isinstance(d, dict):
    d = d.get("messages", [d])
for m in d:
    print(" | ".join([
        str(m.get("date")),
        str(m.get("from")),
        str(m.get("subject")),
        str(m.get("threadId")),
        str(m.get("id")),
    ]))
