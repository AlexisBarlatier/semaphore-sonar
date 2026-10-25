#!/usr/bin/env python3
"""Moissonne l'historique d'adjudications Licitor (Sud-Est) et filtre le périmètre Var + Marseille.

Sortie : adjudications.jsonl (une ligne par bien adjugé), reprise possible (les ids déjà
présents sont sautés). Listes par type, puis fiche détaillée pour les seuls biens du périmètre.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

BASE = "https://www.licitor.com"
LIST = BASE + "/ventes-aux-encheres-immobilieres/sud-est-mediterrannee/{slug}.html?type=H&p={p}"
TYPES = {
    "immeuble-residentiel": "immeuble",
    "local-a-usage-de-commerce": "local",
    "parking-garage": "parking",
}
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/122.0 Safari/537.36")
OUT = Path(__file__).resolve().parent / "adjudications.jsonl"
DELAY = 1.4          # politesse entre requêtes
MAX_PAGES = 400      # garde-fou


def get(url: str, tries: int = 3) -> str | None:
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fr"})
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception as e:                                    # noqa: BLE001
            print(f"  ! {url} ({e}) essai {k+1}/{tries}", flush=True)
            time.sleep(3 * (k + 1))
    return None


def in_perimetre(titre: str) -> tuple[bool, str]:
    """Le titre porte la commune et le département : 'Un immeuble, Toulon, Var, adjudication : ...'."""
    if ", Var," in titre:
        return True, "Var"
    if ", Bouches-du-Rhône," in titre and re.search(r"marseille", titre, re.I):
        return True, "Marseille"
    return False, ""


def num(s: str) -> int | None:
    d = re.sub(r"[^\d]", "", s or "")
    return int(d) if d else None


def parse_detail(html: str) -> dict:
    out: dict = {}
    m = re.search(r"Tribunal Judiciaire de\s+([^<(]+?)\s*(?:\(([^)]+)\))?\s*<", html)
    if m:
        out["tribunal"] = m.group(1).strip()
        out["departement_tj"] = (m.group(2) or "").strip()
    m = re.search(r"Adjudication\s*:\s*([\d\s\u202f\u00a0]+)\s*€", html)
    out["adjuge"] = num(m.group(1)) if m else None
    m = re.search(r"Mise à prix\s*:\s*([\d\s\u202f\u00a0]+)\s*€", html)
    out["mise_a_prix"] = num(m.group(1)) if m else None
    out["occupe"] = bool(re.search(r"\bOccup\S*", html))
    m = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", html)
    out["date_vente"] = m.group(1) if m else None
    m = re.search(r"de\s+([\d\s,\.]{2,9})\s*m²", html)
    out["surface_m2"] = float(m.group(1).replace(" ", "").replace(",", ".")) if m else None
    m = re.search(r"annonce publiée le\s*([^<]+)<", html, re.I)
    out["publication"] = m.group(1).strip() if m else None
    return out


def main() -> int:
    seen: set[str] = set()
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            try:
                seen.add(json.loads(line)["id"])
            except Exception:                                     # noqa: BLE001
                pass
    print(f"déjà en base : {len(seen)} biens", flush=True)

    total_ads = 0
    kept = 0
    with OUT.open("a", encoding="utf-8") as fh:
        for slug, famille in TYPES.items():
            print(f"\n=== {famille} ({slug})", flush=True)
            empty = 0
            for page in range(1, MAX_PAGES + 1):
                html = get(LIST.format(slug=slug, p=page))
                if not html:
                    break
                links = re.findall(r'href="(/annonce/[^"]+\.html)"\s+title="([^"]*)"', html)
                if not links:
                    empty += 1
                    if empty >= 2:
                        break
                    continue
                new_on_page = 0
                for href, titre in links:
                    ad_id = re.search(r"/(\d+)\.html$", href)
                    if not ad_id:
                        continue
                    ad_id = ad_id.group(1)
                    total_ads += 1
                    if ad_id in seen:
                        continue
                    seen.add(ad_id)
                    new_on_page += 1
                    ok, zone = in_perimetre(titre)
                    if not ok:
                        continue
                    detail = get(BASE + href)
                    if not detail:
                        continue
                    rec = {
                        "id": ad_id,
                        "famille": famille,
                        "zone": zone,
                        "titre": titre.split(", adjudication")[0],
                        "url": BASE + href,
                        "commune": titre.split(",")[1].strip() if titre.count(",") > 1 else None,
                        **parse_detail(detail),
                    }
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    fh.flush()
                    kept += 1
                    ratio = (f"{rec['adjuge']/rec['mise_a_prix']:.2f}"
                             if rec.get("adjuge") and rec.get("mise_a_prix") else "?")
                    print(f"  + {rec['commune']:<22} MAP {rec.get('mise_a_prix')} adjugé "
                          f"{rec.get('adjuge')} (x{ratio}) occupé={rec.get('occupe')} "
                          f"{rec.get('surface_m2')} m²", flush=True)
                print(f"  page {page}: {new_on_page} nouvelles annonces", flush=True)
                empty = empty + 1 if new_on_page == 0 else 0
                if empty >= 3:
                    print("  fin de liste", flush=True)
                    break
                time.sleep(DELAY)

    print(f"\nTerminé : {total_ads} annonces parcourues, {kept} retenues dans le périmètre", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
