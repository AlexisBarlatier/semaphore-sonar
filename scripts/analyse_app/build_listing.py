# -*- coding: utf-8 -*-
"""Génère analyses/index.html depuis analyses/analyses.json (E3).

Le listing ne contient que des valeurs CALCULÉES au build (moteur + scoring) :
- rendement : net après IS / prix de revient et / prix d'achat (pair)
- note /10  : formule officielle (40/30/20/10) — jamais lue depuis la base
Toute fiche dont les entrées ne permettent pas un calcul affiche « — »
(décision Alexis 06/09 : pas de résultat historique stocké).

Déterminisme garanti : deux builds successifs produisent un fichier identique
(contrôlé par le hash affiché).

Usage : python3 scripts/analyse_app/build_listing.py [--project chemin]
"""

import hashlib
import json
import os
import re
import sys
from datetime import date

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)
from analyse_app.engine import compute            # noqa: E402
from analyse_app.scoring import note_et_verdict   # noqa: E402
from analyse_app.schema import validate_record    # noqa: E402

PROJECT_DIR = None
for arg in sys.argv[1:]:
    if not arg.startswith("--"):
        PROJECT_DIR = os.path.abspath(arg)
        break
if PROJECT_DIR is None:
    for c in [os.getcwd(), os.path.expanduser("~/Documents/Semaphore-sonar"),
              os.path.expanduser("~/semaphore-sonar")]:
        if os.path.isdir(os.path.join(c, "analyses")):
            PROJECT_DIR = c
            break
if PROJECT_DIR is None:
    sys.exit("Erreur : dossier analyses/ introuvable")
ANALYSES_DIR = os.path.join(PROJECT_DIR, "analyses")
DB_PATH = os.path.join(ANALYSES_DIR, "analyses.json")
OUT_PATH = os.path.join(ANALYSES_DIR, "index.html")

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]


def date_fr(iso):
    try:
        y, m, d = iso.split("-")
        return f"{int(d)} {MOIS[int(m) - 1]} {y}"
    except Exception:
        return iso or "—"


def money_fr(v):
    if v is None:
        return None
    s = f"{v:,.0f}".replace(",", " ")
    return f"{s} €"


def pct_fr(v):
    if v is None:
        return None
    return f"{v:.1f} %".replace(".", ",")


def fmt_m2(v):
    m = money_fr(v)
    return m.replace(" €", " m²") if m else None


def surface_display(rec):
    s = rec.get("bien", {}).get("surfaces", {}).get("texte")
    if s:
        return s
    lots = (rec.get("bien") or {}).get("lots") or {}
    if lots.get("count") and lots.get("surface_par_lot_m2"):
        return f"{lots['count']} × {fmt_m2(lots['surface_par_lot_m2'])}"
    return "—"


def prix_display(rec):
    a = rec.get("annonce") or {}
    if a.get("prix_retenu_euros") and a.get("prix_statut") == "offre":
        return f"{money_fr(a['prix_retenu_euros'])} (offre)"
    if a.get("prix_affiche_euros"):
        base = money_fr(a["prix_affiche_euros"])
        mx = a.get("prix_affiche_max_euros")
        if mx and mx != a["prix_affiche_euros"]:
            return f"{money_fr(a['prix_affiche_euros'])} – {money_fr(mx)}"
        return base
    if a.get("prix_retenu_euros"):
        return money_fr(a["prix_retenu_euros"])
    return "—"


def rendement_display(computed):
    if not computed.get("calculable"):
        return "—"
    if computed.get("mdb"):
        roi = computed["mdb"].get("roi_pct")
        return pct_fr(roi) if roi is not None else "—"
    r = computed.get("rendements") or {}
    a, b = r.get("net_sur_revient_pct"), r.get("net_sur_achat_pct")
    if a is None and b is None:
        return "—"
    if a is not None and b is not None:
        return f"{pct_fr(a)} / {pct_fr(b)}"
    return pct_fr(a if a is not None else b)


def note_class(n):
    if n >= 7.5:
        return "note-high"
    if n >= 5.0:
        return "note-mid"
    return "note-low"


def note_fr(n):
    return f"{n:.1f}".replace(".", ",") + "/10"


def process(rec):
    """(calcul, note, verdict) — tout calculé, rien lu depuis la base."""
    c = compute(rec)
    note, verdict, comp = note_et_verdict(rec, c)
    return c, note, verdict, comp


def build(records):
    rows, cards_h = [], []
    for rec in records:
        c, note, verdict, comp = process(rec)
        slug = rec["slug"]
        titre = rec.get("titre") or slug
        href = f"{slug}/index.html"
        src = ""
        if rec.get("annonce", {}).get("url"):
            src = (f' <a href="{rec["annonce"]["url"]}" title="Annonce '
                   f'originale" class="listing-src-link">🔗</a>')
        date_txt = date_fr(rec.get("date_analyse"))
        prix = prix_display(rec)
        surf = surface_display(rec)
        rdt = rendement_display(c)
        note_txt = note_fr(note) if note is not None else "—"
        cls = note_class(note) if note is not None else "note-low"

        rows.append(
            f'<tr><td>{date_txt}</td><td><a href="{href}">{titre}</a>{src}</td>'
            f'<td>{prix}</td><td>{surf}</td><td>{rdt}</td>'
            f'<td style="text-align:center"><span class="listing-badge '
            f'{cls}">{note_txt}</span></td></tr>')
        cards_h.append(
            f'<div class="listing-card"><div class="listing-card-header">'
            f'<span class="listing-card-date">{date_txt}</span>'
            f'<span class="listing-badge {cls}">{note_txt}</span></div>'
            f'<a class="listing-card-title" href="{href}">{titre}</a>{src}'
            f'<div class="listing-card-meta"><span>{prix}</span>'
            f'<span class="meta-sep">·</span><span>{surf}</span>'
            f'<span class="meta-sep">·</span><span>{rdt}</span></div></div>')

    nl = "\n"
    html = (
        '<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
        '<title>Sémaphore Sonar — Analyses</title>'
        '<link rel="stylesheet" href="../style.css"></head><body>'
        '<header class="listing-hero"><h1>Sémaphore Sonar</h1>'
        '<p class="hero-subtitle">Analyses d\'investissement immobilier</p>'
        '</header><main><div class="listing-stats"><span><strong>'
        f'{len(records)}</strong> analyses</span></div>'
        '<table class="listing-table"><thead><tr><th>Date</th><th>Adresse</th>'
        '<th>Prix</th><th>Surface</th><th>Rendement</th><th>Note</th></tr>'
        f'</thead><tbody>{nl}{nl.join(rows)}{nl}</tbody></table>'
        f'<div class="listing-cards">{nl}{nl.join(cards_h)}{nl}</div></main>'
        '</body></html>')
    return html


def main():
    with open(DB_PATH, encoding="utf-8") as f:
        data = json.load(f)
    records = sorted(data["analyses"], key=lambda r: r["slug"], reverse=True)

    # Contrôle schéma avant publication
    invalides = [(r["slug"], e) for r in records for e in validate_record(r)]
    if invalides:
        print("⚠ fiches structurellement invalides (build continué, à traiter) :")
        for s, e in invalides[:10]:
            print(f"   {s} -> {e[:1]}")

    html = build(records)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    h = hashlib.sha256(html.encode("utf-8")).hexdigest()[:12]
    # comptage des cellules calculées
    n_note = sum(1 for r in records if process(r)[1] is not None)
    n_rdt = sum(1 for r in records if rendement_display(compute(r)) != "—")
    print(f"✓ Listing généré : {OUT_PATH}")
    print(f"  {len(records)} analyses | notes calculées : {n_note} | "
          f"rendements calculés : {n_rdt} | hash : {h}")
    print("  Contrôle déterminisme : relancer la commande — deux builds "
          "successifs doivent afficher le même hash.")


if __name__ == "__main__":
    main()
