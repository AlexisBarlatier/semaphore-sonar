#!/usr/bin/env python3
"""Re-saisie du T4 de 75 m² de Champ de Mars (Toulon) : double diffusion du même bien.

Le bien analysé le 13/10/2026 sous le slug 2026-10-13-t4-75m2-champs-de-mars-toulon (SeLoger
264PZD3FK11R, BRETTE IMMOBILIER, 170 000 €) est re-listé par IBOX JAURÈS (SeLoger 263ML9SJH5KS,
réf. 3753JS) à 180 000 €. Même bien : T4 de 75 m², 3e étage sur 6 avec ascenseur, copropriété de
88 lots, DPE C / GES C, balcon 2 m², WC séparé, quartier Champs de Mars.

Usage : python3 scripts/resaisie_2026-10-13_t4_champs_de_mars_double_diffusion.py [--ecrire]
"""
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts"))
from analyse_app import engine, schema, scoring  # noqa: E402

BASE = RACINE / "analyses" / "analyses.json"
SLUG = "2026-10-13-t4-75m2-champs-de-mars-toulon"
URL_IBOX = "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/toulon-83000/263ML9SJH5KS"

VENDEUR = ("le même bien est diffusé par DEUX agences : BRETTE IMMOBILIER (réf. 3839, "
           "contact Thomas Duval, 128 avenue Émile Vincent à Toulon) à 170 000 € (prix barré 180 000 €), "
           "et IBOX JAURÈS (réf. 3753JS, 323 rue Jean Jaurès à Toulon) à 180 000 €. Honoraires à la charge "
           "du vendeur dans les deux cas. L'analyse retient le prix le plus bas des deux mandats")

SURFACES = ("75 m² annoncés (Carrez non précisé), balcon 2 m². Divergence entre les deux annonces du même "
            "bien : BRETTE annonce « pas de cave », un garage et une exposition nord-ouest, quand IBOX "
            "annonce une cave de 5 m², pas de garage et une exposition ouest-est. Une cave et un garage ne "
            "sont pas la même chose : statut des annexes à établir sur le titre de propriété")

COPRO = ("2 012 €/an annoncés par BRETTE IMMOBILIER, 2 200 €/an par IBOX JAURÈS pour le même lot — "
         "copropriété de 88 lots, aucune procédure syndicale en cours. Retenu : 2 012 €/an, le montant le "
         "plus bas ; budget prévisionnel et trois derniers PV à exiger")

RISQUE = {
    "facteur": "Même bien diffusé par deux agences à deux prix",
    "detail": "BRETTE IMMOBILIER affiche 170 000 € (prix barré 180 000 €) et IBOX JAURÈS 180 000 € pour le "
              "même appartement — même surface, même étage, même copropriété de 88 lots, même DPE C, même "
              "balcon de 2 m². Les deux annonces divergent sur les annexes (cave chez l'une, garage chez "
              "l'autre), sur l'exposition et sur l'année de construction (1950 contre 1948). L'écart de "
              "10 000 € entre les deux mandataires est un point d'appui de négociation — le vendeur a déjà "
              "affiché 170 000 € — mais il signale aussi un mandat mal tenu, et il faudra faire préciser "
              "par écrit les annexes réellement vendues avant toute proposition.",
    "severite": 2,
}


def main():
    ecrire = "--ecrire" in sys.argv
    data = json.loads(BASE.read_text(encoding="utf-8"))
    rec = [a for a in data["analyses"] if a["slug"] == SLUG][0]

    avant = {k: rec["annonce"][k] for k in ("url", "prix_affiche_euros", "vendeur")}
    rec["annonce"]["vendeur"] = VENDEUR
    rec["annonce"]["url_secondaire"] = URL_IBOX
    rec["bien"]["surfaces"]["texte"] = SURFACES
    rec["bien"]["copro"]["charges_source"] = COPRO
    rec["date_maj"] = "2026-10-14"
    if not any(r["facteur"] == RISQUE["facteur"] for r in rec["analyse"]["risques"]):
        rec["analyse"]["risques"].append(dict(RISQUE))

    print("vendeur avant :", avant["vendeur"][:90])
    print("url secondaire :", rec["annonce"]["url_secondaire"])
    print("validation du record :", schema.validate_record(rec) or "aucune erreur")
    c = engine.compute(rec)
    n, v, comp = scoring.note_et_verdict(rec, c)
    plafond, det = scoring.prix_plafond(rec)
    print(f"note {n} {v} | net/revient {c['rendements']['net_sur_revient_pct']:.2f} % | "
          f"plafond {plafond} € ({det}) | cible {scoring.prix_cible(rec)}")
    print(f"risques : {len(rec['analyse']['risques'])} (sévérité moyenne "
          f"{sum(r['severite'] for r in rec['analyse']['risques'])/len(rec['analyse']['risques']):.2f})")
    if not ecrire:
        print("\n(base non modifiée — relancer avec --ecrire)")
        return
    data["meta"]["count"] = len(data["analyses"])
    for a in data["analyses"]:
        a["champs_manquants"] = schema.champs_manquants(a)
    BASE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nbase écrite : {len(data['analyses'])} dossiers, meta.count = {data['meta']['count']}")


if __name__ == "__main__":
    main()
