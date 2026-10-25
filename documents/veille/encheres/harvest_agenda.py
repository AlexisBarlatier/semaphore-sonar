#!/usr/bin/env python3
"""Agenda des ventes aux enchères à venir (Licitor) — Var + Marseille.

Parcourt les listes « ventes à venir » des trois familles utiles, garde les biens du
périmètre et relève pour chacun la date d'audience, le tribunal, la mise à prix, la
surface, l'occupation et le lien.

Sortie : agenda.jsonl (une ligne par lot à venir, dédoublonné par id d'annonce).
La date d'audience s'écrit en toutes lettres chez Licitor (« vendredi 19 mars 2010 à 8h30 »).
"""
from __future__ import annotations

import html as H
import json
import re
import sys
import time
import urllib.request
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = "https://www.licitor.com"
LIST = BASE + "/ventes-aux-encheres-immobilieres/sud-est-mediterrannee/{slug}.html?type=A&p={p}"
TYPES = {"immeuble-residentiel": "immeuble", "local-a-usage-de-commerce": "local",
         "parking-garage": "parking"}
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/122.0 Safari/537.36")
MOIS = {m: i for i, m in enumerate(
    ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
     "septembre", "octobre", "novembre", "décembre"], start=1)}
DELAY = 1.3
MAX_PAGES = 60


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


def texte(html: str) -> str:
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", t)))


def parse_detail(html: str) -> dict:
    t = texte(html)
    out: dict = {}
    m = re.search(r"(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\s+(\d{1,2})(?:er)?\s+"
                  r"([a-zûéô]+)\s+(\d{4})\s+à\s+(\d{1,2})h(\d{2})?", t)
    if m and m.group(3) in MOIS:
        out["audience"] = f"{m.group(4)}-{MOIS[m.group(3)]:02d}-{int(m.group(2)):02d}"
        out["heure"] = f"{m.group(5)}h{m.group(6) or '00'}"
    m = re.search(r"Tribunal Judiciaire de\s+([^<(]+?)\s*(?:\(([^)]+)\))?\s+", t)
    if m:
        out["tribunal"] = m.group(1).strip()
    m = re.search(r"Mise à prix\s*:\s*([\d\s\u202f\u00a0]+)\s*€", t)
    out["mise_a_prix"] = int(re.sub(r"\D", "", m.group(1))) if m else None
    m = re.search(r"de\s+([\d\s,\.]{2,9})\s*m²", t)
    out["surface_m2"] = float(m.group(1).replace(" ", "").replace(",", ".")) if m else None
    out["occupe"] = bool(re.search(r"\bOccup\S*", t))
    out["libre"] = bool(re.search(r"\bLibre\b|\bInoccup\S*", t))
    m = re.search(r"Annonce publiée le\s*([0-9]{1,2} [a-zûé]+ 20[0-9]{2})", t)
    out["publication"] = m.group(1) if m else None
    m = re.search(r"\b(Vente (?:aux enchères|sur)\S?[^.]{0,90})", t)
    out["nature"] = m.group(1).strip() if m else None
    return out


def in_perimetre(titre: str) -> str | None:
    if re.search(r",\s*Var\b", titre):
        return "Var"
    if re.search(r",\s*Bouches-du-Rhône\b", titre) and re.search(r"marseille", titre, re.I):
        return "Marseille"
    return None


def main() -> int:
    aujourdhui = date.today().isoformat()
    vus: set[str] = set()
    fichier = HERE / "agenda.jsonl"
    if fichier.exists():
        for line in fichier.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
                if rec.get("audience", "9999") >= aujourdhui:
                    vus.add(rec["id"])
            except Exception:                                      # noqa: BLE001
                pass
    neufs: list[dict] = []
    with fichier.open("a", encoding="utf-8") as fh:
        for slug, famille in TYPES.items():
            print(f"=== {famille}", flush=True)
            vides = 0
            derniere_page = ()
            for page in range(1, MAX_PAGES + 1):
                html = get(LIST.format(slug=slug, p=page))
                if not html:
                    break
                liens = re.findall(r'href="(/annonce/[^"]+\.html)"\s+title="([^"]*)"', html)
                if not liens:
                    vides += 1
                    if vides >= 2:
                        break
                    continue
                ids_page = tuple(re.search(r"/(\d+)\.html$", h).group(1) for h, _ in liens
                                 if re.search(r"/(\d+)\.html$", h))
                if ids_page == derniere_page:
                    print("  pagination figée, arrêt", flush=True)
                    break
                derniere_page = ids_page
                inedits = 0
                for href, titre in liens:
                    m = re.search(r"/(\d+)\.html$", href)
                    if not m:
                        continue
                    aid = m.group(1)
                    if aid in vus:
                        continue
                    inedits += 1
                    zone = in_perimetre(titre)
                    if not zone:
                        vus.add(aid)
                        continue
                    detail = get(BASE + href)
                    if not detail:
                        continue
                    vus.add(aid)
                    rec = {"id": aid, "famille": famille, "zone": zone,
                           "commune": titre.split(",")[1].strip() if titre.count(",") > 1 else "?",
                           "intitule": titre.split(", adjudication")[0],
                           "url": BASE + href, **parse_detail(detail)}
                    if (rec.get("audience") or "9999") < aujourdhui:
                        continue
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    fh.flush()
                    neufs.append(rec)
                    print(f"  + {rec.get('audience')} {rec['commune'][:18]:<19} {famille:<8} "
                          f"MAP {rec.get('mise_a_prix')}", flush=True)
                print(f"  page {page}: {len(neufs)} retenues cumulées", flush=True)
                vides = vides + 1 if inedits == 0 else 0
                if vides >= 3:
                    break
                time.sleep(DELAY)

    print(f"\n{len(neufs)} lots à venir retenus", flush=True)
    if neufs:
        neufs.sort(key=lambda r: (r.get("audience") or "9999", r.get("tribunal") or ""))
        print("\nAGENDA", flush=True)
        for r in neufs:
            print(f"- {r.get('audience')} {r.get('heure','')} | TJ {r.get('tribunal','?')} | "
                  f"{r['commune']} | {r['famille']} | MAP {r.get('mise_a_prix')} €"
                  f"{' | OCCUPÉ' if r.get('occupe') else (' | libre' if r.get('libre') else '')}"
                  f" | {r['url']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
