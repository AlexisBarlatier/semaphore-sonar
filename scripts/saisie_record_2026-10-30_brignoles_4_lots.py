#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saisie du dossier : immeuble de 4 lots, centre vieille ville, Brignoles.

Deux annonces SeLoger du même agent (BSK Immobilier, réf. 331917 et 331939)
vendent les deux moitiés du même immeuble : T2 + studio au 2e étage (610 €/mois)
et deux studios au RDC (660 €/mois), soit 4 lots pour 160 000 €.

Le 1er étage n'est pas proposé : la copropriété compte donc au moins 6 lots.
"""
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

from analyse_app import engine, schema, scoring  # noqa: E402

CHEMIN = os.path.join(RACINE, "analyses", "analyses.json")
SLUG = "2026-10-30-brignoles-immeuble-4-lots-centre"

RECORD = {
    "slug": SLUG,
    "date_analyse": "2026-10-30",
    "date_maj": "2026-10-30",
    "titre": "Immeuble de 4 lots — T2 et 3 studios — Centre Vieille Ville, Brignoles (83170)",
    "bien": {
        "type_bien": "immeuble",
        "sous_type": "immeuble de rapport",
        "type_detail": (
            "Quatre logements dans un petit immeuble ancien de trois niveaux plus comble, "
            "au cœur du centre ancien : un T2 de 29 m² et un studio de 15 m² au 2e étage, "
            "deux studios de 23 m² et 12 m² au rez-de-chaussée. Les quatre lots sont loués. "
            "Façade fatiguée : enduit tombé par plaques, fissure verticale, humidité en pied, "
            "volets bois hors d'usage. Vendus par le même agent, en deux annonces de 80 000 €."
        ),
        "neuf": False,
        "adresse": {
            "texte": "Centre Vieille Ville, Brignoles (83170) — adresse exacte non communiquée par l'agence",
            "ville": "Brignoles",
            "code_postal": "83170",
            "quartier": "Centre Vieille Ville",
        },
        "surfaces": {
            "texte": (
                "79,98 m² habitables annoncés (44,99 m² pour le T2 et le studio du 2e, "
                "34,99 m² pour les deux studios du RDC). Aucun Carrez, aucun plan."
            )
        },
        "lots": {
            "count": 4,
            "nature": (
                "4 lots loués : T2 de 29 m² et studio de 15 m² au 2e étage ; studios de 23 m² "
                "et 12 m² au RDC. L'immeuble compte trois niveaux plus comble ; le 1er étage "
                "n'est pas proposé, donc la copropriété compte au moins 6 lots."
            ),
            "lots_distincts": 4,
        },
        "copro": {
            "charges_annuelles_euros": 240.0,
            "charges_source": (
                "10 €/mois annoncés par paire d'appartements, soit 240 €/an pour les 4 lots — "
                "3 €/m²/an, anormalement bas pour un immeuble ancien de trois niveaux. "
                "Ce montant ne peut couvrir ni l'assurance de l'immeuble, ni l'eau et l'électricité "
                "des communs, ni l'entretien : à faire justifier par les appels réels et le budget prévisionnel."
            ),
        },
        "travaux": {
            "montant_euros": 20000.0,
            "nature": (
                "Façade sur rue à reprendre : enduit tombé par plaques, fissure verticale entre les "
                "fenêtres, traces d'humidité et mousses en pied, volets bois cassés, câblages apparents. "
                "Ravalement avec échafaudage, reprise d'enduit, menuiseries extérieures et porte : "
                "20 000 € retenus, fourchette 15 000 à 30 000 € selon le traitement de l'humidité et "
                "l'état de la toiture. L'annonce écrit « aucun travaux à prévoir dans l'immeuble » : "
                "la photographie la contredit. Budget porté en quote-part de 4 lots, à revoir quand le "
                "nombre exact de lots de la copropriété sera connu."
            ),
        },
    },
    "annonce": {
        "plateforme": "seloger",
        "url": "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/brignoles-83170/26JTSKFDT2P7",
        "prix_affiche_euros": 160000.0,
        "prix_retenu_euros": 160000.0,
        "prix_statut": "affiche",
        "vendeur": (
            "BSK Immobilier — El Hasania Saidi (EI), réf. 331917 et 331939, honoraires à la charge "
            "du vendeur. Deux annonces de 80 000 € qui forment un ensemble de 4 lots à 160 000 €."
        ),
    },
    "marche": {
        "valeur": {
            "basse_euros": 130000.0,
            "haute_euros": 174000.0,
            "retenue_euros": 152000.0,
            "source": (
                "DVF Brignoles (83018), appartements de 45 à 80 m² : 13 ventes 2021-2025, médiane "
                "1 868 €/m², premier quartile 1 287, troisième quartile 2 173. Sur 79,98 m², la "
                "fourchette va de 103 000 € à 174 000 € ; valeur retenue 152 000 € à 1 900 €/m², "
                "entre la médiane et le troisième quartier, pour des lots de centre ancien après "
                "reprise de façade. En l'état, avant travaux, la valeur est plus proche de 135 000 €. "
                "Échantillon mince sur une commune étroite : repère, pas distribution."
            ),
            "confiance": "faible",
        },
        "loyers": [
            {
                "lot": "T2 de 29 m², 2e étage",
                "quantite": 1,
                "loyer_mensuel_euros": 400.0,
                "occupe": True,
                "note": "Répartition estimée : l'annonce ne donne que le total de la paire (610 €/mois pour le T2 et le studio de 15 m²).",
            },
            {
                "lot": "Studio de 15 m², 2e étage",
                "quantite": 1,
                "loyer_mensuel_euros": 210.0,
                "occupe": True,
                "note": "Répartition estimée sur le total de 610 €/mois annoncé pour la paire.",
            },
            {
                "lot": "Studio de 23 m², RDC",
                "quantite": 1,
                "loyer_mensuel_euros": 360.0,
                "occupe": True,
                "note": "Total annoncé de 660 €/mois pour les deux studios du RDC ; répartition estimée 360 / 300.",
            },
            {
                "lot": "Studio de 12 m², RDC",
                "quantite": 1,
                "loyer_mensuel_euros": 300.0,
                "occupe": True,
                "note": "Répartition estimée. 12 m² reste au-dessus du seuil de décence (9 m² et 20 m³).",
            },
        ],
        "notes": (
            "1 270 €/mois annoncés, quatre locataires en place, aucune quittance au dossier. "
            "15,9 €/m² contre une médiane DHUP 2025 de 13,1 €/m² à Brignoles, soit +21 % : "
            "les deux studios du RDC sortent à 18,9 €/m². C'est la première pièce à exiger — "
            "à 13,1 €/m², l'assiette tombe à 1 050 €/mois et le dossier change de camp."
        ),
    },
    "hypotheses": {
        "vacance_base_pct": 5.0,
        "vacance_best_pct": 2.0,
        "vacance_worst_pct": 12.0,
        "taux_placement_reserve_pct": 2.84,
        "quote_part_bati_pct": 90.0,
        "vacance_justification": (
            "Quatre petits lots : 5 % en base (rotation d'environ deux semaines et demie par lot et "
            "par an), 2 % en best, 12 % en worst avec deux lots vides en même temps sur un marché "
            "de bourg où l'offre de studios est abondante."
        ),
        "charges": {
            "charges_copro_annuelles_euros": 240.0,
            "charges_copro_commentaire": (
                "240 €/an annoncés (10 €/mois par paire). Poste invraisemblable pour un immeuble "
                "ancien : barème d'attente 18 à 22 €/m²/an en petite copropriété sans ascenseur, "
                "soit 1 440 à 1 760 €/an ici. Le calcul retient l'annonce, le risque porte l'écart."
            ),
            "taxe_fonciere_annuelle_euros": 942.0,
            "taxe_fonciere_commentaire": (
                "471 €/an par paire, annoncés sur chaque annonce, soit 942 €/an pour les 4 lots. "
                "Montant identique sur les deux annonces : à faire confirmer par les deux avis."
            ),
            "entretien_annuel_euros": 1771.0,
            "entretien_commentaire": (
                "1 771 €/an : gestion locative déléguée à 6 % des loyers (914 €), provision "
                "d'impayés à 3 % (457 €, distincte de la vacance) et 400 € d'entretien courant "
                "sur un bâti ancien."
            ),
            "pno_annuelle_euros": 600.0,
            "pno_annuelle_commentaire": "150 €/lot, quatre lots — assurance propriétaire non occupant.",
            "comptabilite_annuelle_euros": 0.0,
        },
        "frais_acquisition_euros": 12000.0,
        "frais_acquisition_commentaire": (
            "7,5 % du prix (12 000 €), régime ancien ; honoraires à la charge du vendeur, donc "
            "hors base de calcul."
        ),
    },
    "analyse": {
        "branche": "residentiel",
        "type_operation": "locatif",
        "strategie_retenue": {"nom": "Location nue en l'état, quatre lots", "code": "ld-nue", "lots": 4},
        "strategies_explorees": [],
        "attractivite": [
            {"dimension": "transports", "score": 6, "justification": "Brignoles est sur l'A8, à 30 km de Toulon, avec gare routière et accès autoroutier immédiat ; pas de train de voyageurs, la commune vit de la voiture."},
            {"dimension": "commerces", "score": 8, "justification": "Cœur du centre ancien : commerces, marché, cinéma, médecins et écoles à pied. C'est le principal atout du bien."},
            {"dimension": "ecoles", "score": 6, "justification": "Écoles et collèges du centre à proximité immédiate, mais la clientèle visée est celle des studios, pas des familles."},
            {"dimension": "securite", "score": 5, "justification": "Centre ancien passant, bâti voisin fatigué et façades dégradées : le cadre de vie est moyen, la rue est animée le jour et vide le soir."},
            {"dimension": "demande_locative", "score": 6, "justification": "Quatre lots loués et un marché de studios actif à Brignoles ; la demande existe, mais elle est sensible au loyer — les loyers annoncés sont 21 % au-dessus de la médiane communale."},
            {"dimension": "dynamisme", "score": 5, "justification": "Bourg administratif et commercial du centre Var, emploi stable mais peu dynamique ; pas de desserte ferroviaire voyageurs."},
        ],
        "risques": [
            {"facteur": "Loyers annoncés 21 % au-dessus de la médiane communale", "severite": 4, "detail": "1 270 €/mois sur 79,98 m² font 15,9 €/m², quand la médiane DHUP 2025 de Brignoles est à 13,1 €/m². Les studios du RDC sortent à 18,9 €/m². Aucune quittance au dossier : si les baux sont à 13,1 €/m², l'assiette tombe à 1 050 €/mois, soit 2 640 €/an de moins."},
            {"facteur": "Façade à reprendre, non chiffrée par devis", "severite": 4, "detail": "Enduit tombé, fissure verticale, humidité en pied, volets cassés. 20 000 € retenus, fourchette 15 000 à 30 000 €. L'annonce affirme « aucun travaux à prévoir » : la photographie la contredit, et ce budget n'est pas dans le prix."},
            {"facteur": "Charges de copropriété invraisemblables", "severite": 4, "detail": "240 €/an pour quatre lots, soit 3 €/m²/an. Le barème d'attente est de 18 à 22 €/m²/an, soit 1 440 à 1 760 €/an. L'écart, 1 200 à 1 500 €/an, retire 0,6 à 0,8 point de rendement s'il se confirme."},
            {"facteur": "Copropriété d'au moins 6 lots, travaux votés inconnus", "severite": 3, "detail": "Le 1er étage n'est pas proposé : la copropriété compte au moins 6 lots, donc les décisions de ravalement et de toiture ne nous appartiennent pas. PV d'AG et plan pluriannuel à exiger."},
            {"facteur": "Aucune quittance, occupation non prouvée", "severite": 3, "detail": "« Locataires sérieux et stables » selon l'agent, sans bail ni quittance. Quatre baux et les trois dernières quittances de chaque lot conditionnent l'offre."},
            {"facteur": "Bâti ancien : structure, toiture et humidité non expertisées", "severite": 4, "detail": "La fissure verticale et les remontées d'humidité peuvent signaler un désordre de structure ou de drainage. Aucun diagnostic structure ni rapport de toiture. Un devis de ravalement ne couvre pas ce risque."},
            {"facteur": "Prix au-dessus du marché du centre ancien", "severite": 3, "detail": "160 000 € pour 79,98 m² font 2 000 €/m², au-dessus de la médiane DVF de 1 868 €/m² et pour un bien qui demande une façade. Le prix de revient avec travaux atteint 2 400 €/m²."},
            {"facteur": "DPE E et D : pas d'échéance, mais une enveloppe à faire", "severite": 2, "detail": "422 kWh/m²/an pour la paire du 2e étage (E) et 287 pour le RDC (D). Aucune interdiction avant 2034, aucun gel de loyer. Le poste énergie reste un argument de relocation."},
            {"facteur": "Micro-lots : relocation et revente étroites", "severite": 2, "detail": "Un studio de 12 m² et un de 15 m² ne se relouent qu'à un public précis et ne se revendent qu'à un investisseur. La liquidité est celle d'un portefeuille de baux, pas d'un immeuble de rapport classique."},
        ],
    },
}


def main():
    erreurs = schema.validate_record(RECORD)
    if erreurs:
        print("SCHEMA:", erreurs)
        return 1
    data = json.load(open(CHEMIN, encoding="utf-8"))
    data["analyses"] = [r for r in data["analyses"] if r["slug"] != SLUG]
    data["analyses"].append(RECORD)
    data["meta"]["count"] = len(data["analyses"])
    with open(CHEMIN, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    c = engine.compute(RECORD)
    print("revient", c["prix_revient_total"], "| frais", c["frais_acquisition"])
    print("rendements", json.dumps(c["rendements"], ensure_ascii=False))
    print("fiscal", json.dumps(c["fiscal"], ensure_ascii=False))
    print("ratio", c["ratio_cout_valeur"])
    print("note", scoring.note_et_verdict(RECORD, c))
    print("plafond", scoring.prix_plafond(RECORD))
    print("cible", scoring.prix_cible(RECORD))
    print("enregistré :", len(data["analyses"]), "records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
