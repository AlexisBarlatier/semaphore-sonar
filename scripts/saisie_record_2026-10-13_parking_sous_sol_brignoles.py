#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saisie du record « 2026-10-13-parking-sous-sol-brignoles-extension » dans la base.

Annonce : leboncoin 3135454276 — place de parking en sous-sol, Brignoles (83170),
résidence livrée il y a 18 mois, 11 500 € (baisse de prix, « urgent »), vendue libre.

Entrées seulement : aucun résultat de calcul n'est stocké. Le record est filtré par
slug avant append (relancer le script ne fabrique pas de doublon).
"""
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

from analyse_app import schema  # noqa: E402

SLUG = "2026-10-13-parking-sous-sol-brignoles-extension"
BASE = os.path.join(RACINE, "analyses", "analyses.json")

RECORD = {
    "slug": SLUG,
    "date_analyse": "2026-10-13",
    "date_maj": "2026-10-13",
    "titre": "Place de parking en sous-sol, Brignoles — résidence récente",
    "bien": {
        "type_bien": "parking",
        "sous_type": "sous-sol",
        "type_detail": "1 place de stationnement en sous-sol sécurisé (n° 1015), résidence livrée il y a 18 mois",
        "neuf": False,
        "adresse": {
            "texte": "Brignoles 83170 — quartier Extension années 80-90 — résidence livrée il y a 18 mois",
            "ville": "Brignoles",
            "code_postal": "83170",
            "quartier": "Extension années 80-90",
        },
        "surfaces": {"texte": "1 place — dimensions non communiquées"},
        "lots": {
            "count": 1,
            "nature": "1 place — lot de copropriété distinct ou rattaché à un logement : non communiqué par le vendeur",
            "lots_distincts": None,
        },
        "copro": {
            "charges_annuelles_euros": 80.0,
            "charges_source": "80 €/an estimé (sous-sol résidence récente, fourchette 50-150 €/an) — non communiqué dans l'annonce, à vérifier par l'appel de charges",
        },
        "travaux": {
            "montant_euros": 0.0,
            "nature": "Aucun — place en état dans une résidence de 18 mois. Boxage éventuel (porte) hors offre, non autorisé à ce jour",
        },
    },
    "annonce": {
        "plateforme": "leboncoin",
        "url": "https://www.leboncoin.fr/ad/ventes_immobilieres/3135454276",
        "prix_affiche_euros": 11500.0,
        "prix_retenu_euros": 11500.0,
        "prix_statut": "affiche",
        "vendeur": "Particulier (profil « surace ») — vente directe sans honoraires d'agence",
    },
    "marche": {
        "valeur": {
            "basse_euros": 10000.0,
            "haute_euros": 12500.0,
            "retenue_euros": 11500.0,
            "source": "Comparables places en sous-sol à Brignoles : 11 000 à 13 000 €/place (fiche place Caramy, relevé 27/08/2026, médiane 12 000 €) — décote retenue pour une place vendue seule hors centre. Annonces voisines de vente 10/2026 : garage 16 m² 17 500 €, garage 60 m² 56 000 €.",
            "confiance": "moyenne",
        },
        "loyers": [
            {
                "lot": "place sous-sol n° 1015",
                "quantite": 1,
                "loyer_mensuel_euros": 75.0,
                "occupe": False,
                "note": "Place vendue libre, sans locataire : revenu encaissé nul à l'achat. Loyer de marché retenu 75 €/mois — haut de la bande relevée (50-80 €/mois) pour un sous-sol sécurisé récent. Les 100 €/mois annoncés par le vendeur ne sont adossés à aucun bail.",
            }
        ],
        "notes": "Relevés de location 10/2026 : 50 € (Zimo, sous-sol sécurisé avec télécommande), 55 € (SeLoger, agence REX, centre), 80 € CC (Foncia, Ramba Liberté), 80 € (leboncoin). Fiche place Caramy 30/06/2026 (Brignoles, sous-sol sécurisé, résidence neuve) : 8 baux écrits à 55 €, 9e place signée à 70 €, loyer de marché retenu 75 €.",
    },
    "hypotheses": {
        "vacance_base_pct": 10.0,
        "vacance_best_pct": 5.0,
        "vacance_worst_pct": 25.0,
        "taux_placement_reserve_pct": 2.84,
        "quote_part_bati_pct": 90.0,
        "vacance_justification": "Place vide à l'achat : la première année part de zéro, la relocation est à trouver. Vacance structurelle de 10 % en base (règle parking), 5 % en best, 25 % en worst — trois mois de vide par an sur un produit binaire.",
        "charges": {
            "charges_copro_annuelles_euros": 80.0,
            "charges_copro_commentaire": "80 €/an estimé (sous-sol, 50-150 €/an) — non communiqué, à vérifier par l'appel de charges",
            "taxe_fonciere_annuelle_euros": 80.0,
            "taxe_fonciere_commentaire": "80 €/an — montant saisi par le vendeur dans l'annonce, à recouper avec l'avis de taxe foncière",
            "entretien_annuel_euros": 0.0,
            "pno_annuelle_euros": 0.0,
            "comptabilite_annuelle_euros": 0.0,
        },
        "frais_acquisition_euros": 1925.0,
        "frais_acquisition_commentaire": "Barème du dépôt pour un lot parking unitaire en ancien : 1 275 € + 100 €/1 000 € au-delà de 5 000 €. À confirmer : droit réduit (0,715 %) si le lot est vendu par son premier acquéreur dans les cinq ans, soit environ 600 € de moins.",
    },
    "analyse": {
        "branche": "parking",
        "type_operation": "locatif",
        "strategie_retenue": {"nom": "Location longue durée de la place", "code": "parking-ld", "lots": None},
        "strategies_explorees": [
            {"strategie": "Location longue durée de la place", "lots": 1,
             "faisabilite": "Relocation à trouver (place vide)", "risque": "modéré"},
            {"strategie": "Boxage puis location (affirmation du vendeur, AG à passer)", "lots": 1,
             "faisabilite": "Non acquise : vote d'AG, poutre et canalisations à respecter", "risque": "élevé"},
            {"strategie": "Revente à l'unité (arbitrage)", "lots": 1,
             "faisabilite": "Immédiate si lot distinct", "risque": "12 % de friction à l'entrée, 20 à 25 % sur un aller-retour"},
        ],
        "attractivite": [
            {"dimension": "tension_stationnement", "score": 6,
             "justification": "Stationnement payant en enclos et en souterrain depuis 2025 (1,70 €/h) dans une commune de 17 000 habitants, mais quartier d'extension où les résidences récentes disposent de leurs propres parkings : tension réelle, pas pénurie."},
            {"dimension": "densite_residentielle", "score": 8,
             "justification": "Résidence livrée il y a 18 mois et tissu collectif dense des extensions 1980-1990 : vivier de locataires sur place."},
            {"dimension": "accessibilite", "score": 8,
             "justification": "Sous-sol avec bip, place située près de l'ascenseur : entrée et sortie à pied directes, manœuvre sans contrainte signalée."},
            {"dimension": "securite_acces", "score": 7,
             "justification": "Sous-sol sécurisé avec bip, circulations éclairées en commun. Ni vidéo ni gardiennage annoncés."},
            {"dimension": "protection", "score": 9,
             "justification": "Sous-sol : ni intempéries ni dégradations, hauteur sous poutre et canalisations à respecter. Bâti amortissable en SCI à l'IS."},
            {"dimension": "demande_locative", "score": 5,
             "justification": "Marché locatif relevé étroit (50 à 80 €/mois), place vide depuis la livraison, aucun bail ni locataire produit par le vendeur, délai de relocation inconnu."},
        ],
        "risques": [
            {"facteur": "Loyer de 100 €/mois annoncé sans aucun bail",
             "detail": "« Peut facilement se louer dans les 100 € » : aucun locataire, aucun bail, aucune annonce locative produite. La bande relevée à Brignoles est de 50 à 80 €/mois, sous-sol sécurisé inclus. Le prix se calcule sur le marché, pas sur la phrase du vendeur.",
             "severite": 3},
            {"facteur": "Poids des charges fixes sur 900 € de loyers",
             "detail": "Charges de copropriété non communiquées (80 €/an estimés) et taxe foncière de 80 €/an affichée : 160 €/an, soit 17,8 % des loyers annuels — au-dessus du seuil de 15 % au-delà duquel un petit lot se refuse. Appel de charges et avis de taxe foncière à exiger avant toute offre.",
             "severite": 3},
            {"facteur": "Lot distinct ou rattaché au logement, et règlement de copropriété",
             "detail": "L'annonce ne donne ni numéro de lot, ni tantièmes, ni le caractère autonome de la place. Un lot rattaché à un logement ne se loue pas séparément et ne se revend pas seul ; le règlement doit confirmer la location à un non-résident.",
             "severite": 3},
            {"facteur": "Appel de fonds de copropriété — résidence de 18 mois",
             "detail": "Les résidences récentes votent souvent les travaux de parachèvement (étanchéité de dalle, ventilation, éclairage) dans leurs premières assemblées. Un appel de 500 à 1 500 € par place efface un à deux ans de loyer.",
             "severite": 3},
            {"facteur": "Vacance d'entrée et marché locatif étroit",
             "detail": "Place vendue vide : aucun revenu avant la relocation, et le délai n'est pas connu. Le produit est binaire — trois mois de vide représentent 25 % de l'année. Rien ne prouve que le haut de la bande se signe ici.",
             "severite": 3},
            {"facteur": "Boxage annoncé par le vendeur",
             "detail": "« Il sera sans doute boxable, il suffira de faire passer cela en AG » : affirmation non vérifiée. La photo montre trois côtés fermés (favorable à une porte) mais une poutre porteuse en travers et des canalisations à laisser accessibles. On n'achète pas sur une autorisation à venir ; le budget d'une porte (3 000 à 5 000 €) reste hors offre.",
             "severite": 2},
            {"facteur": "Droits de mutation : première mutation ou revente",
             "detail": "Résidence achevée depuis 18 mois : le droit réduit n'est attaché qu'à la première mutation dans les cinq ans. Si le vendeur tient son lot d'un précédent acquéreur, le droit commun s'applique — environ 600 € d'écart sur ce ticket.",
             "severite": 2},
            {"facteur": "Liquidité à la revente",
             "detail": "Frais d'acquisition de l'ordre de 17 % du prix sur ce ticket, et 20 à 25 % sur un aller-retour : un parking s'achète pour la rente, jamais pour une marge de revente.",
             "severite": 3},
        ],
    },
}


def main():
    erreurs = schema.validate_record(RECORD)
    if erreurs:
        raise SystemExit(f"record invalide : {erreurs}")

    with open(BASE, encoding="utf-8") as fh:
        data = json.load(fh)

    # Contrôle de structure : conteneur, pas dictionnaire de fiches
    assert isinstance(data.get("analyses"), list), "analyses.json n'est pas un conteneur"
    avant = len(data["analyses"])

    data["analyses"] = [r for r in data["analyses"] if r.get("slug") != SLUG]
    data["analyses"].append(RECORD)

    manquants = schema.champs_manquants(RECORD)
    data["meta"]["count"] = len(data["analyses"])

    with open(BASE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)

    # Relecture
    with open(BASE, encoding="utf-8") as fh:
        relu = json.load(fh)
    assert isinstance(relu.get("analyses"), list)
    assert "analyses" in relu and relu["meta"]["count"] == len(relu["analyses"])
    parasites = [k for k in relu if k not in ("meta", "analyses")]
    print(f"meta.count relu : {relu['meta']['count']} | fiches avant → après : {avant} → {len(relu['analyses'])}")
    print(f"clés racine parasites : {parasites or 'aucune'}")
    print(f"champs manquants : {manquants or 'aucun'}")
    print(f"slug présent : {any(r['slug'] == SLUG for r in relu['analyses'])}")


if __name__ == "__main__":
    main()
