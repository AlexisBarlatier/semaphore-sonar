#!/usr/bin/env python3
"""Récupère la date de vente, l'occupation et le descriptif de chaque immeuble déjà collecté.

Le premier passage stockait `date_vente` via un motif jj/mm/aaaa, alors que Licitor écrit
« vendredi 19 mars 2010 » : le champ sortait vide, et une adjudication de 2010 se comparait
à un marché de 2024. Ce script répare ça — la date est indispensable pour filtrer la récence.
"""
from __future__ import annotations

import html as H
import json
import re
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/122.0 Safari/537.36")
MOIS = {m: i for i, m in enumerate(
    ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
     "septembre", "octobre", "novembre", "décembre"], start=1)}


def get(url: str, tries: int = 4) -> str | None:
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fr"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception as e:                                     # noqa: BLE001
            print(f"  ! {e} — essai {k+1}/{tries}", flush=True)
            time.sleep(4 * (k + 1))
    return None


def parse(html: str) -> dict:
    txt = H.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>", "", html, flags=re.S)))
    txt = re.sub(r"\s+", " ", txt)
    date = None
    m = re.search(r"(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\s+(\d{1,2})(?:er)?\s+"
                  r"([a-zûé]+)\s+(\d{4})", txt)
    if m and m.group(2) in MOIS:
        date = f"{m.group(3)}-{MOIS[m.group(2)]:02d}-{int(m.group(1)):02d}"
    nature = None
    m = re.search(r"Vente (aux enchères publiques[^.]{0,80}|sur [^.]{0,60})", txt)
    if m:
        nature = m.group(1).strip()
    desc = ""
    m = re.search(r"##\s*(?:Un|Une)\s[^#]{0,600}", txt)
    if m:
        desc = m.group(0)[:600]
    return {
        "date_vente": date,
        "nature": nature,
        "occupe": bool(re.search(r"\bOccup\S*", txt)),
        "inhabitable": bool(re.search(r"inhabitab|à rénover|en cours de rénovation|vétust", txt, re.I)),
        "descriptif": desc,
    }


def main() -> int:
    rows = [json.loads(l) for l in (HERE / "adjudications.jsonl").read_text(encoding="utf-8").splitlines()]
    cible = rows  # toutes familles : la date est la seule facon de filtrer la recence
    print(f"{len(cible)} immeubles à réinterroger", flush=True)
    out = []
    for i, r in enumerate(cible, 1):
        h = get(r["url"])
        rec = dict(r)
        if h:
            rec.update(parse(h))
        out.append(rec)
        print(f"  {i:>3}/{len(cible)} {r['commune'][:22]:<23} {rec.get('date_vente')} "
              f"{'OCCUPÉ ' if rec.get('occupe') else '       '}{rec.get('nature') or ''}", flush=True)
        time.sleep(1.0)
    (HERE / "details_tous.json").write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                                 encoding="utf-8")
    print("écrit : details_tous.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
