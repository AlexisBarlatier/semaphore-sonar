#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saisie de deux dossiers Toulon du 13/10/2026 dans la base.

A. 2026-10-13-t4-75m2-champs-de-mars-toulon — SeLoger 264PZD3FK11R, 170 000 €, coloc.
B. 2026-10-13-t5-83m2-toulon-ouest — SeLoger 26N62U1XVPP3, 176 000 €, location nue.

Entrées seulement : aucun résultat de calcul n'est stocké. Les deux slugs sont
filtrés avant append (relancer ne fabrique pas de doublon).
"""
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

from analyse_app import schema  # noqa: E402

BASE = os.path.join(RACINE, "analyses", "analyses.json")

RECORDS = [
    {
        "slug": "2026-10-13-t4-75m2-champs-de-mars-toulon",
        "date_analyse": "2026-10-13",
        "date_maj": "2026-10-13",
        "titre": "T4 de 75 m² aménagé en colocation — Champs de Mars, Toulon",
        "bien": {
            "type_bien": "appartement",
            "sous_type": None,
            "type_detail": "T4 de 75 m² aménagé en colocation : 3 chambres de plus de 11 m², séjour-cuisine de 27 m² — 3e étage sur 6 avec ascenseur",
            "neuf": False,
            "adresse": {
                "texte": "Quartier Champs de Mars, Toulon (83000) — adresse exacte non communiquée par l'agence",
                "ville": "Toulon",
                "code_postal": "83000",
                "quartier": "Champs de Mars",
            },
            "surfaces": {"texte": "75 m² annoncés (Carrez non précisé), balcon 2 m², exposition nord-ouest, garage mentionné dans les caractéristiques"},
            "lots": {
                "count": 1,
                "nature": "1 appartement (le garage et le balcon figurent dans les caractéristiques, sans statut de lot précisé)",
                "lots_distincts": None,
            },
            "copro": {
                "charges_annuelles_euros": 2012.0,
                "charges_source": "2 012 €/an annoncés par l'agence (SeLoger) — copropriété de 88 lots, aucune procédure syndicale en cours",
            },
            "travaux": {
                "montant_euros": 0.0,
                "nature": "Déjà aménagé en colocation (3 chambres de plus de 11 m², séjour de 27 m²). Le mobilier d'exploitation est à reprendre ou à amortir, provisionné dans les charges",
            },
        },
        "annonce": {
            "plateforme": "seloger",
            "url": "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/toulon-83000/264PZD3FK11R",
            "prix_affiche_euros": 170000.0,
            "prix_retenu_euros": 170000.0,
            "prix_statut": "affiche",
            "vendeur": "BRETTE IMMOBILIER (réf. 3839, contact Thomas Duval) — honoraires à la charge du vendeur, prix ramené de 180 000 € à 170 000 €",
        },
        "marche": {
            "valeur": {
                "basse_euros": 160000.0,
                "haute_euros": 195000.0,
                "retenue_euros": 180000.0,
                "source": "DVF 2024-2025, Toulon (83137), appartements 4 pièces — mutations d'un seul lot, n = 1 053, médiane 2 458 €/m² (Q1 1 985 / Q3 3 171) ; tranche 60-80 m², n = 1 542, médiane 2 448 €/m². Valeur retenue 2 400 €/m² pour un bien de quartier central à aménager en colocation, soit 180 000 € pour 75 m².",
                "confiance": "moyenne",
            },
            "loyers": [
                {
                    "lot": "3 chambres meublées — colocation",
                    "quantite": 1,
                    "loyer_mensuel_euros": 1350.0,
                    "occupe": False,
                    "note": "Loyer retenu 1 350 €/mois (3 × 450 €) — médiane du relevé toulonnais du 28/09/2026 (plancher 345 €, plafond 550 €, masse principale 420 à 520 € charges comprises par chambre). L'annonce annonce 400 € par chambre (1 200 €) sans bail : c'est le bas de la fourchette relevée, il ne fonde pas un prix.",
                }
            ],
            "notes": "Relevés de colocation Toulon : 28/09/2026 (13 annonces identifiées, médiane 450 € CC/chambre ; comparable strict T3 de 3 chambres à Saint-Roch à 450 €) et 22/09/2026 (secteur facultés 430-480 € CC, médiane 460 € ; Champ de Mars 480 € CC pour une chambre de 11 m²). Environ 66 à 183 annonces de colocation en concurrence selon les portails.",
        },
        "hypotheses": {
            "vacance_base_pct": 5.0,
            "vacance_best_pct": 2.0,
            "vacance_worst_pct": 15.0,
            "taux_placement_reserve_pct": 2.84,
            "quote_part_bati_pct": 90.0,
            "vacance_justification": "Colocation meublée à trois chambres : rotation des baux et relocation concentrée sur la rentrée universitaire. 5 % en base, 15 % en worst (les trois chambres ne se relouent pas au même rythme).",
            "charges": {
                "charges_copro_annuelles_euros": 2012.0,
                "charges_copro_commentaire": "2 012 €/an annoncés (26,8 €/m²/an, fourchette haute du barème d'attente pour un immeuble avec ascenseur) — budget prévisionnel à exiger",
                "taxe_fonciere_annuelle_euros": 1400.0,
                "taxe_fonciere_commentaire": "1 400 €/an estimés (taux global de Toulon 49,76 % en 2025) — avis de taxe foncière à exiger",
                "entretien_annuel_euros": 4120.0,
                "entretien_commentaire": "Poste composite : fluides et internet 2 500 €/an (eau, électricité, gaz — bail meublé charges comprises) + provision mobilier 1 620 €/an (10 % des loyers). La provision travaux automatique du moteur (2,5 % des loyers) s'y ajoute.",
                "pno_annuelle_euros": 250.0,
                "comptabilite_annuelle_euros": 0.0,
            },
            "frais_acquisition_euros": 13600.0,
            "frais_acquisition_commentaire": "8 % du prix, estimation du portail (13 600 €) ; honoraires à la charge du vendeur",
        },
        "analyse": {
            "branche": "residentiel",
            "type_operation": "locatif",
            "strategie_retenue": {"nom": "Colocation meublée à trois chambres", "code": "colocation", "lots": 3},
            "strategies_explorees": [
                {"strategie": "Colocation meublée à trois chambres (aménagement existant)", "lots": 3,
                 "faisabilite": "Immédiate — l'appartement est déjà agencé pour la colocation", "risque": "modéré"},
                {"strategie": "Location nue du T4", "lots": 1,
                 "faisabilite": "Immédiate, sans mobilier à entretenir", "risque": "modéré"},
                {"strategie": "Revente à l'unité / arbitrage", "lots": 1,
                 "faisabilite": "Frais de mutation 8 % à l'entrée, marché profond à Toulon", "risque": "élevé sur un horizon court"},
            ],
            "attractivite": [
                {"dimension": "transports", "score": 8,
                 "justification": "Quartier central de Toulon, à quelques minutes des bus du centre et de la gare ; accès direct aux axes de la ville."},
                {"dimension": "commerces", "score": 8,
                 "justification": "Centre-ville dense : commerces, marché, services et santé à pied."},
                {"dimension": "ecoles", "score": 9,
                 "justification": "Cœur du secteur étudiant revendiqué par l'annonce : faculté de droit, ISEN, campus Chalucet et école paramédicale annoncés à quelques minutes — c'est le moteur de la demande en colocation."},
                {"dimension": "securite", "score": 6,
                 "justification": "Immeuble des années 50 en quartier dense du centre : cadre de vie correct, mais le centre toulonnais reste hétérogène et le bâti voisin inégal."},
                {"dimension": "demande_locative", "score": 7,
                 "justification": "Demande étudiante réelle et récurrente, mais offre abondante : 66 à 183 annonces de colocation en concurrence à Toulon, dont une vingtaine seulement de 3 chambres avec loyer par chambre."},
                {"dimension": "dynamisme", "score": 7,
                 "justification": "Toulon, préfecture du Var, métropole TPM : 5 095 ventes d'appartements en 24 mois, marché profond et liquide à la revente."},
            ],
            "risques": [
                {"facteur": "Loyer de colocation à créer, annoncé au bas de la fourchette",
                 "detail": "L'annonce annonce 400 € par chambre (1 200 €/mois) sans bail, quand la médiane relevée à Toulon est de 450 € CC et le secteur facultés de 430 à 480 €. Retenir 400 € ferait porter au dossier un rendement trop faible pour être financé ; retenir 450 € fait dépendre le prix d'un loyer que personne n'a signé. Aucun bail, aucune quittance, aucun locataire n'est produit.",
                 "severite": 3},
                {"facteur": "Charges de détention lourdes",
                 "detail": "2 012 €/an de copropriété (26,8 €/m²/an, haut du barème d'attente) plus 1 400 € de taxe foncière estimée et 250 € d'assurance : 3 662 €/an avant les fluides et le mobilier, soit 22,6 % des loyers retenus. Le budget prévisionnel et trois PV d'assemblée sont à exiger.",
                 "severite": 3},
                {"facteur": "Meublé : mobilier, fluides et rotation à la charge du bailleur",
                 "detail": "En colocation meublée charges comprises, le bailleur porte l'eau, l'électricité, le gaz et internet (provisionnés à 2 500 €/an) et renouvelle le mobilier (1 620 €/an). L'annonce ne dit ni ce qui reste dans l'appartement, ni qui paie quoi : deux ans de loyers peuvent partir dans un ameublement à refaire.",
                 "severite": 3},
                {"facteur": "Surface Carrez et statut du garage non établis",
                 "detail": "75 m² annoncés sans certificat Carrez ; le garage figure dans les caractéristiques mais n'apparaît ni dans la description ni dans les détails de prix. Un garage en lot distinct change la valeur et le revenu ; une surface utile de 70 m² déplacerait tous les ratios.",
                 "severite": 3},
                {"facteur": "Risques d'impayés et de vacance en colocation",
                 "detail": "Trois baux meublés à rotation étudiante : provision d'impayés et de gestion portée à 4 % des loyers dans les charges, et vacance de 15 % dans le scénario dégradé. Les digicodes, la garantie Visale et l'usage effectif des chambres sont à vérifier sur place.",
                 "severite": 3},
                {"facteur": "Copropriété de 88 lots des années 50",
                 "detail": "Ascenseur (positif) mais pas de diagnostic technique global connu, aucune procédure en cours annoncée, et à 1948 le bâti porte les postes que les annonces taisent : façade, toiture, colonnes, électricité des communs. Un appel de fonds voté efface un an de loyer.",
                 "severite": 3},
                {"facteur": "Écart au plancher de rendement",
                 "detail": "Au prix affiché, le rendement net après IS sur prix de revient ressort à 3,80 % (loyer retenu 1 350 €) pour un plancher de branche de 5 % : le dossier est sous son seuil de tout le dossier, indépendamment de la négociation sur les quelques milliers d'euros.",
                 "severite": 3},
                {"facteur": "DPE C — pas de contrainte réglementaire",
                 "detail": "DPE C et GES C, chauffage central au gaz : aucune échéance d'interdiction de location, aucune rénovation énergétique imposée à court terme. C'est le principal atout technique du lot.",
                 "severite": 1},
            ],
        },
    },
    {
        "slug": "2026-10-13-t5-83m2-toulon-ouest",
        "date_analyse": "2026-10-13",
        "date_maj": "2026-10-13",
        "titre": "T5 de 83 m² avec cave, parking et balcon — Toulon Ouest",
        "bien": {
            "type_bien": "appartement",
            "sous_type": None,
            "type_detail": "T5 de 83,36 m² : salon, salle à manger, 3 chambres (4e possible), cuisine, salle de bain, WC séparés — 3e et dernier étage sans ascenseur",
            "neuf": False,
            "adresse": {
                "texte": "Toulon Ouest (83200) — adresse exacte non communiquée par l'agence",
                "ville": "Toulon",
                "code_postal": "83200",
                "quartier": "Toulon Ouest",
            },
            "surfaces": {"texte": "83,36 m² annoncés (Carrez non précisé), grand balcon, loggia, cave, place de parking privative"},
            "lots": {
                "count": 1,
                "nature": "1 lot principal + cave + parking privatif (statut de lot non précisé dans l'annonce)",
                "lots_distincts": None,
            },
            "copro": {
                "charges_annuelles_euros": 1200.0,
                "charges_source": "1 200 €/an de budget prévisionnel annoncé par l'agence — copropriété de 72 lots",
            },
            "travaux": {
                "montant_euros": 0.0,
                "nature": "Appartement annoncé lumineux et traversant en bon état ; mention « possibilité d'une 4e chambre » = cloisonnement à créer, non chiffré et non retenu dans l'offre",
            },
        },
        "annonce": {
            "plateforme": "seloger",
            "url": "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/toulon-83000/26N62U1XVPP3",
            "prix_affiche_euros": 176000.0,
            "prix_retenu_euros": 176000.0,
            "prix_statut": "affiche",
            "vendeur": "CENTURY 21 OUEST IMMO (réf. 3717) — honoraires à la charge du vendeur, annonce publiée le jour de l'analyse",
        },
        "marche": {
            "valeur": {
                "basse_euros": 165000.0,
                "haute_euros": 195000.0,
                "retenue_euros": 180000.0,
                "source": "DVF 2024-2025, Toulon (83137) : 5 pièces — mutations d'un seul lot, n = 228, médiane 2 552 €/m² ; tranche 80-95 m², n = 388, médiane 2 622 €/m² (Q1 2 083 / Q3 3 238). Toulon Ouest se négocie sous la moyenne communale (Saint-Roch relevé 18 % en dessous) : valeur retenue 2 160 €/m², soit 180 000 € pour 83,36 m².",
                "confiance": "moyenne",
            },
            "loyers": [
                {
                    "lot": "location nue du 5 pièces",
                    "quantite": 1,
                    "loyer_mensuel_euros": 1050.0,
                    "occupe": False,
                    "note": "Loyer retenu 1 050 €/mois pour 83 m². Relevés Toulon 09/2026 : 890 € pour 69 m², 1 000 € de médiane sur les T4 toutes surfaces, 1 220 € pour 71 m² à Valbertrand. Aucun bail en place. La variante colocation (3 chambres à 430 €, ou 4 chambres à 430 € après cloisonnement) est chiffrée à part : elle ne sauve pas le dossier.",
                }
            ],
            "notes": "Colocation Toulon, médiane 450 € CC/chambre (relevé 28/09/2026), plancher 345 €, plafond 550 €. Le logement est annoncé non meublé : une exploitation en colocation demanderait l'ameublement complet des chambres, non chiffré ici et hors offre.",
        },
        "hypotheses": {
            "vacance_base_pct": 5.0,
            "vacance_best_pct": 2.0,
            "vacance_worst_pct": 12.0,
            "taux_placement_reserve_pct": 2.84,
            "quote_part_bati_pct": 90.0,
            "vacance_justification": "Location nue d'un 5 pièces au dernier étage sans ascenseur : 5 % en base, 2 % en best, 12 % en worst — le marché locatif toulonnais est abondant (une centaine de T4 en concurrence) et un 3e étage sans ascenseur se reloue plus lentement.",
            "charges": {
                "charges_copro_annuelles_euros": 1200.0,
                "charges_copro_commentaire": "1 200 €/an (budget prévisionnel annoncé, 72 lots, soit 14,4 €/m²/an — sous le barème d'attente, à confirmer par l'appel de charges)",
                "taxe_fonciere_annuelle_euros": 1300.0,
                "taxe_fonciere_commentaire": "1 300 €/an estimés (taux global de Toulon 49,76 % en 2025) — avis de taxe foncière à exiger",
                "entretien_annuel_euros": 0.0,
                "pno_annuelle_euros": 250.0,
                "comptabilite_annuelle_euros": 0.0,
            },
            "frais_acquisition_euros": 14080.0,
            "frais_acquisition_commentaire": "8 % du prix, estimation du portail (14 080 €) ; honoraires à la charge du vendeur",
        },
        "analyse": {
            "branche": "residentiel",
            "type_operation": "locatif",
            "strategie_retenue": {"nom": "Location nue du 5 pièces", "code": "ld-nue", "lots": 1},
            "strategies_explorees": [
                {"strategie": "Location nue du T5 (3 chambres)", "lots": 1,
                 "faisabilite": "Immédiate, sans travaux ni mobilier", "risque": "modéré"},
                {"strategie": "Colocation meublée (3 chambres, ou 4 après cloisonnement)", "lots": 4,
                 "faisabilite": "Ameublement et cloisonnement à financer, non chiffrés", "risque": "élevé"},
                {"strategie": "Revente à l'unité / arbitrage", "lots": 1,
                 "faisabilite": "Frais de mutation 8 % à l'entrée", "risque": "élevé sur un horizon court"},
            ],
            "attractivite": [
                {"dimension": "transports", "score": 7,
                 "justification": "Toulon Ouest correctement desservi (bus, axes vers le centre et l'autoroute) sans être au pied de la gare."},
                {"dimension": "commerces", "score": 7,
                 "justification": "Quartier résidentiel avec commerces de proximité, écoles et services annoncés à proximité."},
                {"dimension": "ecoles", "score": 7,
                 "justification": "Secteur familial bien doté (écoles, collèges) : c'est le profil qui loue un 5 pièces, pas l'étudiant."},
                {"dimension": "securite", "score": 6,
                 "justification": "Copropriété annoncée « au calme et bien entretenue » : le cadre immédiat est bon, dans un secteur ouest hétérogène."},
                {"dimension": "demande_locative", "score": 6,
                 "justification": "Demande réelle pour les grands logements familiaux aux prix du marché, mais offre abondante et non tendue, et le 3e étage sans ascenseur réduit la cible."},
                {"dimension": "dynamisme", "score": 6,
                 "justification": "Toulon Ouest est un secteur populaire et stable, en retrait des quartiers centraux et littoraux : marché profond mais prix au m² contenu."},
            ],
            "risques": [
                {"facteur": "3e et dernier étage sans ascenseur",
                 "detail": "C'est le défaut qui commande tout le dossier : il écarte les locataires familiaux avec enfants en bas âge et les seniors, donc réduit le loyer atteignable et allonge la relocation. Un 5 pièces sans ascenseur se reloue lentement et se revend avec la même décote.",
                 "severite": 3},
                {"facteur": "4e chambre à créer, non chiffrée",
                 "detail": "L'annonce mentionne une « possibilité d'une 4e chambre » : cloisonnement, électricité, menuiserie, ventilation à financer, et 83 m² divisés en quatre chambres donnent des chambres de 9 à 11 m², sous le seuil de confort que le marché étudiant toulonnais paie. Aucun devis, aucun chiffrage : hors offre.",
                 "severite": 3},
                {"facteur": "Charges annoncées très basses pour un immeuble de 72 lots",
                 "detail": "1 200 €/an de budget prévisionnel (14,4 €/m²/an) pour un immeuble de 72 lots avec chauffage annoncé à 1 040-1 470 €/an d'énergie par logement : c'est un budget de dépenses courantes, sans provision de gros travaux. Le plan pluriannuel de travaux et trois PV d'AG sont à exiger avant l'offre.",
                 "severite": 3},
                {"facteur": "Rendement sous le plancher de la branche",
                 "detail": "Au prix affiché et au loyer de 1 050 €/mois, le rendement net après IS sur prix de revient ressort à 4,44 % pour un plancher de 5 %. La distance n'est pas rhétorique : elle chiffre la marge de négociation qu'il faut aller chercher, ou l'absence de dossier.",
                 "severite": 3},
                {"facteur": "Surface Carrez non établie",
                 "detail": "83,36 m² annoncés sans certificat : le chiffre est celui qui produit les 2 111 €/m² affichés. Un carrez à 79 m² ferait passer le prix à 2 228 €/m² et déplacerait tous les ratios.",
                 "severite": 2},
                {"facteur": "DPE D et chauffage individuel",
                 "detail": "DPE D, GES D, énergie estimée 1 040 à 1 470 €/an : aucune contrainte réglementaire aujourd'hui, mais le poste chauffage pèse sur l'attractivité et sur le reste à vivre du locataire. Le mode de chauffage n'est pas précisé dans l'annonce.",
                 "severite": 2},
                {"facteur": "Atouts à confirmer : cave, parking, balcon, loggia",
                 "detail": "Le parking privatif et la cave sont des différenciateurs réels dans ce secteur (stationnement rare), mais leur statut de lot et l'accès effectif (portail, attribution) ne sont pas documentés. Ils font la différence à la relocation.",
                 "severite": 2},
                {"facteur": "Bien mis en vente au prix du marché bas",
                 "detail": "À 176 000 €, soit 2 111 €/m², le bien est annoncé sous la médiane communale des 5 pièces (2 552 €/m²) : il n'y a pas de décote manifeste à exploiter, la marge viendra de la négociation, pas de la lecture de l'annonce.",
                 "severite": 2},
            ],
        },
    },
]


def main():
    with open(BASE, encoding="utf-8") as fh:
        data = json.load(fh)
    assert isinstance(data.get("analyses"), list), "analyses.json n'est pas un conteneur"
    avant = len(data["analyses"])
    slugs = [r["slug"] for r in RECORDS]

    for rec in RECORDS:
        err = schema.validate_record(rec)
        if err:
            raise SystemExit(f"record invalide ({rec['slug']}) : {err}")

    data["analyses"] = [r for r in data["analyses"] if r.get("slug") not in slugs]
    data["analyses"].extend(RECORDS)
    data["meta"]["count"] = len(data["analyses"])

    with open(BASE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)

    with open(BASE, encoding="utf-8") as fh:
        relu = json.load(fh)
    parasites = [k for k in relu if k not in ("meta", "analyses")]
    print(f"meta.count={relu['meta']['count']} | fiches {avant} → {len(relu['analyses'])}")
    print(f"clés racine parasites : {parasites or 'aucune'}")
    for rec in RECORDS:
        print(f"  {rec['slug']} — présent : {any(r['slug'] == rec['slug'] for r in relu['analyses'])} | "
              f"champs manquants : {schema.champs_manquants(rec) or 'aucun'}")


if __name__ == "__main__":
    main()
