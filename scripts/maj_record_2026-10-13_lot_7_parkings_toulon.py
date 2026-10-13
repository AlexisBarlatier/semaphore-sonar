#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mise à jour du record « 2026-10-13-lot-7-parkings-toulon-les-routes ».

Donnée réelle reçue le 13/10/2026 : les sept emplacements sont des LOTS DE COPROPRIÉTÉ
DISTINCTS (information du vendeur), et non un lot unique. Conséquences propagées :
- `bien.lots` : statut renseigné, sept lots distincts ;
- `marche.valeur` : la valeur s'ancre désormais sur les prix unitaires relevés à Toulon
  (annonces 10/2026), plus une somme d'unités au lieu d'une capitalisation ;
- `analyse.risques` : le risque « statut des lots non communiqué » tombe, remplacé par
  la liquidité unitaire (avec ses témoins de prix) ;
- `analyse.strategies_explorees` : la revente à l'unité passe de pari à sortie possible.

Entrées seulement : aucun résultat de calcul n'est stocké.
"""
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

from analyse_app import schema  # noqa: E402

SLUG = "2026-10-13-lot-7-parkings-toulon-les-routes"
BASE = os.path.join(RACINE, "analyses", "analyses.json")

RELEVE_VENTES = (
    "Relevé de ventes de places et garages à Toulon (annonces 10/2026) : 17 000 € (parking 12 m²), "
    "19 000 € (stationnement sécurisé 12,5 m², Serinette-La Barre), 23 000 € (place 13 m² en sous-sol "
    "sécurisé, transformable en box), 27 000 € (garage en sous-sol, résidence fermée sécurisée, Pont du Las "
    "et Bon Rencontre), 27 500 € et 33 000 € (places de 14 m²). Somme des unités du lot : deux places "
    "extérieures retenues à 8 000 € et cinq emplacements de sous-sol à 15 000 € — décote appliquée pour le "
    "secteur Les Routes et pour des places nues sans porte, face aux annonces de garages fermés."
)


def main():
    with open(BASE, encoding="utf-8") as fh:
        data = json.load(fh)
    assert isinstance(data.get("analyses"), list)
    rec = next((r for r in data["analyses"] if r["slug"] == SLUG), None)
    if rec is None:
        raise SystemExit(f"record absent : {SLUG}")

    rec["date_maj"] = "2026-10-13"
    rec["bien"]["lots"] = {
        "count": 7,
        "nature": "7 lots de copropriété distincts, un par emplacement — revente à l'unité possible "
                  "(statut confirmé par le vendeur le 13/10/2026)",
        "lots_distincts": True,
    }
    rec["marche"]["valeur"] = {
        "basse_euros": 75000.0,
        "haute_euros": 120000.0,
        "retenue_euros": 91000.0,
        "source": RELEVE_VENTES,
        "confiance": "faible",
    }
    rec["marche"]["notes"] = (
        rec["marche"]["notes"] + " Sept lots distincts : la revente à l'unité est juridiquement possible, "
        "et les prix unitaires relevés à Toulon (17 000 à 27 500 € pour un emplacement en sous-sol) sont très "
        "au-dessus du prix par emplacement du lot (13 571 €) — mais ce sont des prix d'annonce, souvent des "
        "garages fermés, et il faut retrancher frais, délai et friction de revente avant d'y voir une marge."
    )
    rec["analyse"]["strategies_explorees"] = [
        {"strategie": "Location longue durée du lot entier", "lots": 7,
         "faisabilite": "Sept emplacements à louer, aucun bail en place", "risque": "modéré"},
        {"strategie": "Revente à l'unité (sept lots distincts)", "lots": 7,
         "faisabilite": "Possible sans modification du règlement — sortie place par place, délai de vente non mesuré",
         "risque": "modéré"},
        {"strategie": "Offre basse unique, non poursuivie", "lots": 7,
         "faisabilite": "Immédiate — le dossier traîne, une offre basse ne coûte qu'un refus", "risque": "faible"},
    ]
    risques = [r for r in rec["analyse"]["risques"] if r["facteur"] != "Statut des lots non communiqué"]
    risques.append({
        "facteur": "Liquidité unitaire : prix d'annonce ou prix de vente ?",
        "detail": "Les sept lots étant distincts, la revente à l'unité est ouverte. Les annonces toulonnaises "
                  "affichent 17 000 à 27 500 € pour un emplacement en sous-sol sécurisé, contre 13 571 € par "
                  "emplacement dans ce lot — l'écart semble favorable, mais ce sont des prix demandés, souvent "
                  "pour des garages fermés, et le secteur Les Routes est moins cher que Pont du Las ou Bon "
                  "Rencontre. Une place nue se revend lentement et sous son prix d'affichage.",
        "severite": 2,
    })
    rec["analyse"]["risques"] = risques

    # « lots_distincts » était un champ à lever : il est levé, la stratégie de découpe remonte
    # et la valeur saisie change, donc toutes les valeurs affichées sont régénérées par le script.

    erreurs = schema.validate_record(rec)
    if erreurs:
        raise SystemExit(f"record invalide après mise à jour : {erreurs}")
    data["meta"]["count"] = len(data["analyses"])
    with open(BASE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)

    with open(BASE, encoding="utf-8") as fh:
        relu = json.load(fh)
    maj = next(r for r in relu["analyses"] if r["slug"] == SLUG)
    print(f"mise à jour OK — lots_distincts={maj['bien']['lots']['lots_distincts']} | "
          f"valeur retenue={maj['marche']['valeur']['retenue_euros']:.0f} € | "
          f"risques={len(maj['analyse']['risques'])} | champs manquants : {schema.champs_manquants(maj) or 'aucun'}")
    print(f"meta.count={relu['meta']['count']} | fiches={len(relu['analyses'])} | "
          f"parasites : {[k for k in relu if k not in ('meta', 'analyses')] or 'aucune'}")


if __name__ == "__main__":
    main()
