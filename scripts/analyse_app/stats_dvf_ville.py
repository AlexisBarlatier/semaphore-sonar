#!/usr/bin/env python3
"""Statistiques DVF par commune — brique de base des fiches ville.

Lit le fichier DVF du departement (csv.gz) et sort, par commune, les prix/m2
reels des ventes d'appartements et de maisons, par tranche de surface.

Usage :
    python3 stats_dvf_ville.py --communes 83023 83153 83073 --json out.json
    python3 stats_dvf_ville.py --list                # toutes les communes du fichier

Le fichier DVF attendu est /tmp/dvf83.csv.gz par defaut (--fichier pour changer).
Regle de calcul : les lots multiples d'une meme mutation sont agreges (surface
sommee, valeur comptee une fois), sinon les ventes en bloc faussent la mediane.
"""
import argparse
import collections
import csv
import gzip
import json
import statistics as st
import sys

TRANCHES = [
    (0, 30, "moins de 30 m²"),
    (30, 45, "30 à 45 m²"),
    (45, 60, "45 à 60 m²"),
    (60, 80, "60 à 80 m²"),
    (80, 150, "80 à 150 m²"),
    (150, 10_000, "plus de 150 m²"),
]


def charge(fichier, communes=None, types=("Appartement", "Maison")):
    """Retourne {code_commune: {type_local: [mutations]}} deja agregees."""
    mut = collections.defaultdict(dict)
    noms = {}
    with gzip.open(fichier, "rt", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            cc = row["code_commune"]
            if communes and cc not in communes:
                continue
            tl = row["type_local"]
            if tl not in types:
                continue
            noms[cc] = row["nom_commune"]
            mid = row["id_mutation"]
            m = mut[cc].setdefault((tl, mid), {
                "date": row["date_mutation"], "vf": None, "surf": 0.0, "n": 0,
                "pieces": set(), "voie": row["adresse_nom_voie"],
            })
            if m["vf"] is None:
                try:
                    m["vf"] = float(row["valeur_fonciere"])
                except (TypeError, ValueError):
                    m["vf"] = 0.0
            try:
                m["surf"] += float(row["surface_reelle_bati"] or 0)
            except ValueError:
                pass
            m["n"] += 1
            if row["nombre_pieces_principales"]:
                m["pieces"].add(row["nombre_pieces_principales"])
    out = collections.defaultdict(lambda: collections.defaultdict(list))
    for cc, d in mut.items():
        for (tl, _), m in d.items():
            if m["n"] > 0 and m["surf"] > 5 and m["vf"] > 5_000:
                out[cc][tl].append(m)
    return out, noms


def resume(muts):
    if not muts:
        return None
    v = [m["vf"] / m["surf"] for m in muts]
    if len(v) < 2:
        q = [v[0], v[0]]
    else:
        qq = st.quantiles(v, n=4)
        q = [qq[0], qq[2]]
    montants = [m["vf"] for m in muts]
    return {
        "n": len(v),
        "mediane_m2": round(st.median(v)),
        "q1_m2": round(q[0]),
        "q3_m2": round(q[1]),
        "mediane_montant": round(st.median(montants)),
        "plus_bas_m2": round(min(v)),
    }


def par_tranche(muts):
    res = {}
    for lo, hi, lab in TRANCHES:
        sel = [m for m in muts if lo <= m["surf"] < hi]
        if sel:
            res[lab] = resume(sel)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fichier", default="/tmp/dvf83.csv.gz")
    ap.add_argument("--communes", nargs="*", default=None)
    ap.add_argument("--json", default=None)
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    data, noms = charge(a.fichier, set(a.communes) if a.communes else None)

    if a.list:
        for cc in sorted(noms, key=lambda c: -len(data[c].get("Appartement", []))):
            n = len(data[cc].get("Appartement", []))
            if n >= 15:
                print(f"{cc}  {noms[cc]:<28} {n:>4} ventes d'appartements")
        return

    sortie = {}
    for cc in (a.communes or sorted(noms)):
        app = data.get(cc, {}).get("Appartement", [])
        mai = data.get(cc, {}).get("Maison", [])
        if not app and not mai:
            continue
        sortie[cc] = {
            "commune": noms.get(cc, cc),
            "appartements": {"global": resume(app), "par_tranche": par_tranche(app)},
            "maisons": {"global": resume(mai), "par_tranche": par_tranche(mai)},
        }
        print(f"=== {noms.get(cc,cc)} ({cc}) ===")
        r = resume(app)
        if r:
            print(f"  appartements : {r['n']:>3} ventes | médiane {r['mediane_m2']:>5,} €/m² | Q1 {r['q1_m2']:>5,} | Q3 {r['q3_m2']:>5,} | montant médian {r['mediane_montant']:>7,} €")
            for lab, t in par_tranche(app).items():
                print(f"     {lab:<16} n={t['n']:>3} | médiane {t['mediane_m2']:>5,} €/m² | Q1 {t['q1_m2']:>5,} | plancher {t['plus_bas_m2']:>5,}")
        r = resume(mai)
        if r:
            print(f"  maisons      : {r['n']:>3} ventes | médiane {r['mediane_m2']:>5,} €/m² | montant médian {r['mediane_montant']:>7,} €")

    if a.json:
        with open(a.json, "w") as f:
            json.dump(sortie, f, ensure_ascii=False, indent=2)
        print(f"\n→ {a.json}")


if __name__ == "__main__":
    sys.exit(main())
