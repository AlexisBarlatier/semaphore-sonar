#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saisie du dossier « 2026-10-13-lot-7-parkings-toulon-les-routes ».

SeLoger 26U7H4J75RR8 — lot de 7 emplacements (2 extérieurs, 4 en 2e sous-sol, 1 double
en enfilade pour 2 véhicules), copropriété de 2022 (77 lots), Toulon Les Routes (83200),
95 000 €, BRETTE IMMOBILIER. Entrées seulement : aucun résultat de calcul n'est stocké.
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

RECORD = {
    "slug": SLUG,
    "date_analyse": "2026-10-13",
    "date_maj": "2026-10-13",
    "titre": "Lot de 7 emplacements de stationnement — Toulon Les Routes",
    "bien": {
        "type_bien": "parking",
        "sous_type": "sous-sol",
        "type_detail": "7 emplacements : 2 places extérieures, 4 places au 2e sous-sol et 1 place double en enfilade (2 véhicules), dans une copropriété livrée en 2022",
        "neuf": False,
        "adresse": {
            "texte": "Secteur Les Routes, Toulon (83200) — copropriété récente de 77 lots, adresse exacte non communiquée",
            "ville": "Toulon",
            "code_postal": "83200",
            "quartier": "Les Routes",
        },
        "surfaces": {"texte": "7 emplacements (aucune dimension communiquée)"},
        "lots": {
            "count": 7,
            "nature": "7 emplacements — lot unique regroupant les places ou lots distincts : non communiqué par l'agence",
            "lots_distincts": None,
        },
        "copro": {
            "charges_annuelles_euros": 700.0,
            "charges_source": "700 €/an estimé (100 €/place/an, sous-sol résidence récente) — non communiqué, à vérifier par l'appel de charges",
        },
        "travaux": {"montant_euros": 0.0,
                    "nature": "Aucun — copropriété livrée en 2022, places en état ; aucun appel de fonds connu"},
    },
    "annonce": {
        "plateforme": "seloger",
        "url": "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/toulon-83000/26U7H4J75RR8",
        "prix_affiche_euros": 95000.0,
        "prix_retenu_euros": 95000.0,
        "prix_statut": "affiche",
        "vendeur": "BRETTE IMMOBILIER (réf. 2026-10, contact Pierre-Antoine Petit) — honoraires à la charge du vendeur",
    },
    "marche": {
        "valeur": {
            "basse_euros": 55000.0,
            "haute_euros": 80000.0,
            "retenue_euros": 70000.0,
            "source": "Relevé maison des ventes de places : 11 000 à 13 000 €/place en sous-sol sécurisé et 6 500 € pour une extérieure (fiches du parc) ; le lot est donc valorisé par capitalisation du loyer plutôt que par somme des unités, l'indissociabilité n'étant pas tranchée.",
            "confiance": "faible",
        },
        "loyers": [
            {"lot": "2 places extérieures", "quantite": 2, "loyer_mensuel_euros": 60.0, "occupe": False,
             "note": "Aucune place louée aujourd'hui. Loyer de marché extérieur à Toulon : 50 à 70 €/mois."},
            {"lot": "4 places au 2e sous-sol", "quantite": 4, "loyer_mensuel_euros": 100.0, "occupe": False,
             "note": "Loyer de marché en sous-sol sécurisé à Toulon (secteur Les Routes) : 85 à 115 €/mois, relevés 112 € CC (garage 12 m², même secteur), 100 € pour la double place en enfilade de la même copropriété, 85 € (Foncia, Saint-Roch)."},
            {"lot": "1 place double en enfilade (2 véhicules)", "quantite": 1, "loyer_mensuel_euros": 100.0,
             "occupe": False,
             "note": "Un emplacement double en enfilade ne se loue pas deux fois le prix d'une place : la seconde voiture est bloquée par la première. Relevé dans la même copropriété : 100 €/mois."},
        ],
        "notes": "Relevés de location Toulon 10/2026 : 18 à 20 annonces de places, dont 60 € (Toulon 83200), 85 € (Foncia, garage sous-sol sécurisé Saint-Roch), 100 € (Les Routes, double place en enfilade), 112 € CC (garage 12 m², Les Routes), 115 € CC (Pont du Las, 17 m²). Aucune place du lot n'est louée à ce jour.",
    },
    "hypotheses": {
        "vacance_base_pct": 10.0,
        "vacance_best_pct": 5.0,
        "vacance_worst_pct": 25.0,
        "taux_placement_reserve_pct": 2.84,
        "quote_part_bati_pct": 71.0,
        "vacance_justification": "Lot entièrement vide à l'achat : sept emplacements à louer, la première année part de zéro. Vacance structurelle 10 % en base (règle parking), 5 % en best, 25 % en worst (trois mois de vide par an sur des produits binaires).",
        "charges": {
            "charges_copro_annuelles_euros": 700.0,
            "charges_copro_commentaire": "700 €/an estimé (100 €/place/an, sous-sol récent) — non communiqué, à vérifier par l'appel de charges",
            "taxe_fonciere_annuelle_euros": 420.0,
            "taxe_fonciere_commentaire": "420 €/an estimé (60 €/place/an) — avis de taxe foncière à exiger",
            "entretien_annuel_euros": 0.0,
            "pno_annuelle_euros": 0.0,
            "comptabilite_annuelle_euros": 0.0,
        },
        "frais_acquisition_euros": 7125.0,
        "frais_acquisition_commentaire": "7,5 % du prix (7 125 €) — barème d'ancien, honoraires à la charge du vendeur. À vérifier : droit réduit si le vendeur cède des lots acquis neufs depuis moins de cinq ans, soit environ 3 000 € de moins.",
    },
    "analyse": {
        "branche": "parking",
        "type_operation": "locatif",
        "strategie_retenue": {"nom": "Location longue durée du lot de 7 emplacements", "code": "parking-ld", "lots": None},
        "strategies_explorees": [
            {"strategie": "Location longue durée du lot entier", "lots": 7,
             "faisabilite": "Sept emplacements à louer, aucun bail en place", "risque": "modéré"},
            {"strategie": "Achat à la découpe puis revente à l'unité", "lots": 7,
             "faisabilite": "Dépend du statut des lots (distincts ou lot unique), non communiqué", "risque": "élevé"},
            {"strategie": "Offre basse unique, non poursuivie", "lots": 7,
             "faisabilite": "Immédiate — le dossier traîne, une offre basse ne coûte qu'un refus", "risque": "faible"},
        ],
        "attractivite": [
            {"dimension": "tension_stationnement", "score": 7,
             "justification": "Secteur Les Routes dense et résidentiel de Toulon Ouest, où le stationnement résidentiel est contraint ; 18 à 20 annonces de location de places seulement dans toute la ville."},
            {"dimension": "densite_residentielle", "score": 8,
             "justification": "Copropriété récente de 77 lots dans un secteur de collectifs : vivier immédiat de locataires sur place et dans les résidences voisines."},
            {"dimension": "accessibilite", "score": 7,
             "justification": "Deux places extérieures en accès direct, cinq emplacements en 2e sous-sol : rampe et manœuvre à vérifier, la place double en enfilade imposant un usage en tandem."},
            {"dimension": "securite_acces", "score": 8,
             "justification": "Copropriété sécurisée livrée en 2022, sous-sol fermé : le produit le plus sûr de la gamme stationnement."},
            {"dimension": "protection", "score": 8,
             "justification": "Cinq des sept emplacements en sous-sol (protection maximale, amortissables) ; deux en extérieur, exposés aux intempéries."},
            {"dimension": "demande_locative", "score": 6,
             "justification": "Le marché locatif existe (60 à 115 €/mois relevés) mais aucune place du lot n'est louée : la demande réelle sur cette résidence n'est pas établie, et le lot arrive avec sept emplacements à commercialiser d'un coup."},
        ],
        "risques": [
            {"facteur": "Sept emplacements vides à commercialiser d'un seul coup",
             "detail": "Aucune place n'est louée aujourd'hui : le dossier part de zéro revenu, et la concurrence immédiate est l'offre de la même copropriété (77 lots, dont des propriétaires qui revendent ou louent leurs places). La vacance de 10 % retenue est une hypothèse de régime, pas une mesure.",
             "severite": 3},
            {"facteur": "Prix demandé hors doctrine par emplacement",
             "detail": "95 000 € pour 7 emplacements, soit 13 571 €/place acte en main hors frais, contre un plafond de doctrine de 10 800 € pour une place en sous-sol (et 6 500 € en extérieur). Le prix affiché est au-dessus de la ligne de son produit avant tout calcul de rendement.",
             "severite": 3},
            {"facteur": "Statut des lots non communiqué",
             "detail": "Lot unique regroupant les sept emplacements ou lots distincts : la découpe et la revente à l'unité en dépendent entièrement. C'est la première question à poser, et elle déplace la liquidité du dossier.",
             "severite": 3},
            {"facteur": "Loyer de la place double surestimé par construction",
             "detail": "Une place double en enfilade ne se loue pas deux fois le prix d'une place : le second véhicule est bloqué. Elle est retenue à 100 €/mois, le prix relevé dans la même copropriété — la compter à 200 € gonflerait le loyer du lot de 16 %.",
             "severite": 2},
            {"facteur": "Charges et taxe foncière non communiquées sur sept lots",
             "detail": "700 €/an de copropriété et 420 €/an de taxe foncière sont des estimations (100 € et 60 € par place). Sur sept emplacements, un écart de 50 €/place/an déplace le loyer nécessaire d'environ 30 €/mois, donc le prix.",
             "severite": 3},
            {"facteur": "Appel de fonds de copropriété",
             "detail": "Résidence livrée en 2022 : les premières assemblées votent souvent les travaux de parachèvement et les mises au point d'étanchéité ou d'éclairage du sous-sol. Un appel de 500 à 1 500 € par place efface un à trois ans de loyer. PV des AG à exiger.",
             "severite": 3},
            {"facteur": "Droits de mutation selon l'ancienneté du titre du vendeur",
             "detail": "Résidence achevée en 2022 : si le vendeur cède des lots qu'il détient depuis la livraison, le droit réduit peut s'appliquer ; environ 3 000 € d'écart sur ce ticket. Question à poser avant l'acte.",
             "severite": 2},
        ],
    },
}


def main():
    erreurs = schema.validate_record(RECORD)
    if erreurs:
        raise SystemExit(f"record invalide : {erreurs}")
    with open(BASE, encoding="utf-8") as fh:
        data = json.load(fh)
    assert isinstance(data.get("analyses"), list)
    avant = len(data["analyses"])
    data["analyses"] = [r for r in data["analyses"] if r.get("slug") != SLUG]
    data["analyses"].append(RECORD)
    data["meta"]["count"] = len(data["analyses"])
    with open(BASE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    with open(BASE, encoding="utf-8") as fh:
        relu = json.load(fh)
    assert relu["meta"]["count"] == len(relu["analyses"])
    print(f"meta.count={relu['meta']['count']} | fiches {avant} → {len(relu['analyses'])} | "
          f"parasites : {[k for k in relu if k not in ('meta', 'analyses')] or 'aucune'}")
    print(f"champs manquants : {schema.champs_manquants(RECORD) or 'aucun'}")


if __name__ == "__main__":
    main()
