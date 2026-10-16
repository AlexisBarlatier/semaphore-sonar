#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saisie du record — Maison de village avec annexes, Cuers (83390).

SeLoger réf. 2987 — Laforêt Cuers — 367 000 € — relevé le 16/10/2026.

Idempotent : le slug est filtré avant append. Relancer le script après toute
correction de chiffre (les textes des stratégies sont calculés, jamais tapés).
"""
import copy
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

from analyse_app import engine, schema, scoring  # noqa: E402

SLUG = "2026-10-16-maison-village-cuers-annexes"
BASE = os.path.join(RACINE, "analyses", "analyses.json")

PRIX = 367000.0
FRAIS = 29360.0          # 8 % du prix, régime ancien, honoraires vendeur
TRAVAUX = 85000.0
TRAVAUX_NUE = 60000.0    # rafraîchissement + chauffage, sans aménagement d'annexe
TRAVAUX_COLOC = 95000.0
TRAVAUX_DIVISION = 120000.0
LOYER_LOGEMENT = 900.0
LOYER_ANNEXES = 450.0
LOYER_MAISON = 1500.0
LOYER_COLOC = 1290.0


def eur(v):
    return f"{v:,.0f}".replace(",", " ") + " €"


def fiche():
    return {
        "slug": SLUG,
        "date_analyse": "2026-10-16",
        "date_maj": "2026-10-16",
        "titre": "Maison de village avec dépendance, patio et trois garages — Cuers (83390)",
        "bien": {
            "type_bien": "maison",
            "sous_type": None,
            "type_detail": "Maison de village mitoyenne d'un côté, construite en 1967, sur deux niveaux : "
                           "premier étage habitable (séjour, cuisine, deux chambres décrites, salle de "
                           "bains) et rez-de-chaussée composé d'un patio en pierre, d'une dépendance de "
                           "41 m² ouverte sur le jardin par des baies vitrées, d'une pièce aménageable de "
                           "23 m², de trois garages de 15 m² et d'une cave de 21 m². Chauffage au fioul, "
                           "DPE F, GES F, terrain de 400 m².",
            "neuf": False,
            "adresse": {
                "texte": "Les Rayols-Saint Lazare-Les Bousquets, Cuers (83390) — adresse exacte non "
                         "communiquée par l'agence",
                "ville": "Cuers",
                "code_postal": "83390",
                "quartier": "Les Rayols-Saint Lazare-Les Bousquets",
            },
            "surfaces": {"texte": "131 m² annoncés « 5 pièces principales », non ventilés par niveau, dont "
                                  "le descriptif détaille 41 m² de dépendance, 23 m² de pièce aménageable "
                                  "et trois garages de 15 m². La surface réellement habitable n'est pas "
                                  "établie : le titre annonce 4 chambres, le champ caractéristiques 1, le "
                                  "descriptif 2. Chiffrage retenu sur 110 m² habitables supposés, la "
                                  "fourchette 95-131 m² déplaçant la valeur de sortie de près de 100 000 €"},
            "lots": {"count": 1,
                     "nature": "Une maison et son bloc d'annexes sur un même titre : un logement à "
                               "l'étage, une dépendance de 41 m², une pièce de 23 m², trois garages de "
                               "15 m², une cave de 21 m² et 400 m² de terrain. Monopropriété, aucune "
                               "copropriété, mitoyenneté d'un seul côté",
                     "lots_distincts": 1},
            "copro": {"charges_annuelles_euros": 0.0,
                      "charges_source": "Aucune charge de copropriété : maison de village en "
                                        "monopropriété, mitoyenne d'un côté. L'entretien des extérieurs, "
                                        "du patio et du jardin est porté par la ligne d'entretien"},
            "travaux": {
                "montant_euros": TRAVAUX,
                "nature": "Aucun devis au dossier. Rafraîchissement du logement et des annexes, "
                          "remplacement du chauffage au fioul, remontée du DPE de F vers E au minimum "
                          "(un logement classé F ne peut plus être loué à compter du 1er janvier 2028 et "
                          "son loyer n'est plus révisable), aménagement de la dépendance pour un usage "
                          "d'atelier ou de local. Barèmes retenus : rafraîchissement 300 à 600 €/m², "
                          "rénovation énergétique globale 200 à 450 €/m², chauffage fioul à remplacer "
                          "15 000 à 25 000 €. Scénario central 85 000 €, soit 650 €/m² sur 131 m² "
                          "annoncés ; fourchette 60 000 à 140 000 € tant que le chantier n'est pas devisé",
            },
        },
        "annonce": {
            "plateforme": "seloger",
            "url": "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/cuers-83390/266G8B6TVPB6",
            "prix_affiche_euros": PRIX,
            "prix_retenu_euros": PRIX,
            "prix_statut": "affiche",
            "vendeur": "Olivier Kircher — Laforêt Cuers (EK CONSEIL, RCS 899934822), réf. annonce 2987 — "
                       "honoraires à la charge du vendeur",
        },
        "marche": {
            "valeur": {
                "basse_euros": 320000.0,
                "haute_euros": 420000.0,
                "retenue_euros": 360000.0,
                "source": "DVF Cuers (83049) : maisons de 80 à 150 m², médiane 3 590 €/m², premier "
                          "quartile 2 868, troisième 4 204, montant médian 343 205 € sur 152 ventes ; "
                          "maisons de plus de 150 m², médiane 1 699 €/m² (la grande surface décote de "
                          "plus de moitié). Appliqué aux 131 m² annoncés, cela donne 375 700 à "
                          "470 300 €. Retenue 360 000 €, sous le premier quartile, pour un bien classé F, "
                          "mitoyen d'un côté, à rafraîchir, dont la surface habitable réelle est "
                          "inférieure au chiffre annoncé et dont une partie de la valeur est portée par "
                          "les annexes. Comparable direct de la base interne : maison de village de "
                          "80,53 m² habitables avec garage de 42 m², annexe de 30 m² et grenier de "
                          "27,5 m², affichée 300 000 € le 23/06/2026 à Cuers — soit 2 173 €/m² sur la "
                          "seule surface habitable. Aucune transaction individuelle de la tranche "
                          "n'est disponible dans notre extraction : la valeur est extrapolée de la "
                          "tranche, et l'offre s'ancre sur la borne basse",
                "confiance": "moyenne",
            },
            "loyers": [
                {"lot": "Logement du premier étage, loué nu en bail d'habitation",
                 "quantite": 1,
                 "loyer_mensuel_euros": LOYER_LOGEMENT,
                 "occupe": False,
                 "note": "Estimé — à vérifier avec un relevé de location de maison sur la commune. "
                         "Ancrages du 16/10/2026 : appartement T3 de 78 m² en cœur de village à "
                         "780 €/mois (10,0 €/m²), appartement de 92,9 m² (4 pièces, 3 chambres) annoncé "
                         "par Laforêt Cuers à 1 006 €/mois (10,8 €/m²) ; baux en cours d'un immeuble de "
                         "six logements suivi en juin 2026 : 10,4 à 14,4 €/m² sur de petites surfaces. "
                         "Haut du marché local tenu par une maison de 123 m², 4 chambres et 400 m² de "
                         "terrain affichée 1 650 €/mois. Retenu 900 €/mois sur environ 90 m², sous ce "
                         "haut de fourchette parce que le logement est classé F, mitoyen d'un côté et à "
                         "rafraîchir. Aucune maison n'est proposée à la location sur la commune au "
                         "16/10/2026 : le marché de la maison est étroit, ce qui joue sur les deux sens, "
                         "à la relocation comme à la revente"},
                {"lot": "Annexes : dépendance de 41 m², pièce de 23 m², trois garages de 15 m², cave",
                 "quantite": 1,
                 "loyer_mensuel_euros": LOYER_ANNEXES,
                 "occupe": False,
                 "note": "Poste estimé, marché non publié : le relevé du 16/10/2026 ne rend que quatre "
                         "locaux professionnels sur la commune, dont un local de 45 m² en surface de "
                         "vente annoncé 560 €/mois. Le seuil retenu est celui de notre doctrine : 10 à "
                         "12 % du capital travaux engagé sur les annexes (25 000 à 40 000 €) exigent 250 "
                         "à 470 €/mois. L'annexe est la seule partie du bien qui échappe au calendrier "
                         "du DPE et au gel des loyers, un local d'activité n'étant pas un logement : "
                         "un bail signé vaut ici mieux que n'importe quel relevé, la valeur du poste "
                         "se marque conditionnelle"},
            ],
            "notes": "Assiette entièrement POST-TRAVAUX : le bien est vendu libre, rien n'est louable en "
                     "l'état (DPE F, chauffage au fioul, aucune production aujourd'hui). Les 16 200 €/an "
                     "retenus sont une cible, pas un encaissement, et ils ne courent qu'après le "
                     "chantier et la signature de deux baux. C'est la lecture de dette du dossier : "
                     "acheter ici, c'est payer aujourd'hui un revenu qui n'existe pas encore.",
        },
        "hypotheses": {
            "vacance_base_pct": 5.0,
            "vacance_best_pct": 2.0,
            "vacance_worst_pct": 12.0,
            "taux_placement_reserve_pct": 2.84,
            "quote_part_bati_pct": 90.0,
            "vacance_justification": "Deux baux sur le même titre, un logement et un bloc d'annexes : "
                                     "5 % en base, 2 % en best, 12 % en worst — les deux unités "
                                     "vacantes en même temps, configuration plausible sur une commune "
                                     "où aucune maison n'est proposée à la location",
            "charges": {
                "charges_copro_annuelles_euros": 0.0,
                "charges_copro_commentaire": "Aucune charge de copropriété, maison en monopropriété. "
                                             "Le poste est reconstitué dans la ligne d'entretien "
                                             "(jardin de 400 m², patio, extérieurs)",
                "taxe_fonciere_annuelle_euros": 1800.0,
                "taxe_fonciere_commentaire": "1 800 €/an ESTIMÉS — aucun avis communiqué. Repères "
                                            "internes à Cuers : 1 285 €/an pour une maison de village "
                                            "de 80 m² habitables, 2 900 €/an pour un immeuble de 200 m². "
                                            "La commune applique un taux de taxe foncière sur le bâti de "
                                            "53,63 % en 2025, l'un des plus élevés du Var : l'avis "
                                            "réel est à exiger avant toute offre",
                "entretien_annuel_euros": 1300.0,
                "entretien_commentaire": "1 300 €/an : gestion locative déléguée à 6 % des loyers "
                                         "(972 €) et entretien courant du logement, du jardin de "
                                         "400 m² et des annexes. Une maison individuelle avec terrain "
                                         "porte ce que la copropriété porterait ailleurs",
                "pno_annuelle_euros": 300.0,
                "comptabilite_annuelle_euros": 0.0,
            },
            "frais_acquisition_euros": FRAIS,
            "frais_acquisition_commentaire": "8 % du prix (29 360 €), régime ancien ; honoraires à la "
                                             "charge du vendeur, donc hors base de calcul",
        },
        "analyse": {
            "branche": "residentiel",
            "type_operation": "locatif",
            "strategie_retenue": {
                "nom": "Logement à l'étage loué nu, annexes louées séparément comme locaux d'activité",
                "code": "ld-nue",
                "lots": 2,
            },
            "strategies_explorees": [],
            "attractivite": [
                {"dimension": "transports", "score": 6,
                 "justification": "Cuers est sur l'A57 et dispose d'une gare TER (Cuers-Pierrefeu) qui "
                                  "met Toulon à une vingtaine de minutes ; la commune vit de l'emploi "
                                  "toulonnais. Aucun transport urbain dense pour autant, et rien ne se "
                                  "fait sans voiture depuis ce quartier."},
                {"dimension": "commerces", "score": 6,
                 "justification": "Bourg de 11 500 à 13 000 habitants avec commerces de proximité, "
                                  "marché hebdomadaire et services de santé. Le bien est annoncé « aux "
                                  "portes de Cuers », à 400 m du collège : c'est le centre élargi, pas "
                                  "l'hypercentre commerçant."},
                {"dimension": "ecoles", "score": 7,
                 "justification": "Collège public La Ferrage à 405 m et ensemble privé Sainte-Marthe à "
                                  "293 m, écoles primaires sur la commune. La clientèle familiale "
                                  "existe, mais le collège public ressort mal noté dans nos fiches "
                                  "antérieures sur la commune."},
                {"dimension": "securite", "score": 5,
                 "justification": "Commune pavillonnaire sans quartier prioritaire, mais nos deux "
                                  "dossiers de juin 2026 relevaient des incivilités et un déficit "
                                  "d'image sur le centre-ville et le quartier Clovade. Maison de "
                                  "village mitoyenne : la tranquillité dépend du voisinage immédiat."},
                {"dimension": "demande_locative", "score": 5,
                 "justification": "Marché locatif sans tension forte : deux annonces de location "
                                  "d'appartements sur la commune au 16/10/2026 et aucune maison à "
                                  "louer. Les baux en cours d'un immeuble comparable se situent entre "
                                  "10,4 et 14,4 €/m² : la demande porte sur les petites surfaces, pas "
                                  "sur les maisons de 130 m²."},
                {"dimension": "dynamisme", "score": 5,
                 "justification": "Revenu médian autour de 23 000 €, chômage proche de 9 à 11 %, "
                                  "croissance démographique réelle mais dépendance à l'emploi "
                                  "toulonnais. Marché sans fièvre : la plus-value n'est pas le moteur "
                                  "de ce dossier, et il ne faut pas l'attendre en consolation d'un "
                                  "rendement absent."},
            ],
            "risques": [
                {"facteur": "Prix d'achat très au-dessus de ce que les loyers portent", "severite": 5,
                 "detail": ""},
                {"facteur": "Surface habitable inconnue", "severite": 4,
                 "detail": "Le portail annonce 131 m² « 5 pièces », le descriptif décrit deux chambres "
                           "et une pièce aménageable de 23 m², le champ caractéristiques en annonce une "
                           "seule. Selon que la surface habitable réelle est de 105 ou de 131 m², le "
                           "prix au mètre carré passe de 3 500 à 2 802 €/m² et la valeur de sortie varie "
                           "de près de 100 000 €. Plans, diagnostic de surface et hauteurs sous plafond "
                           "à exiger avant tout chiffrage : c'est la première question du dossier."},
                {"facteur": "DPE F : location interdite au 1er janvier 2028, loyers gelés", "severite": 4,
                 "detail": "Un logement classé F ne peut plus être mis en location à compter du "
                           "1er janvier 2028 et son loyer n'est plus révisable. La remontée du "
                           "diagnostic n'est donc pas une option d'agrément : elle commande le "
                           "calendrier et une part du budget. Chauffage au fioul à remplacer, cuve à "
                           "contrôler, audit énergétique obligatoire à la vente d'une passoire en "
                           "monopropriété."},
                {"facteur": "Aucun devis sur un bâti ancien de 1967", "severite": 3,
                 "detail": "Rafraîchissement, chauffage et énergie chiffrés à 85 000 € au barème, sans "
                           "un seul devis. Toiture, planchers et évacuations d'une maison mitoyenne "
                           "sont les postes invisibles : ils se vérifient en ouvrant, pas en visitant, "
                           "et ils peuvent doubler l'enveloppe."},
                {"facteur": "Loyer des annexes non constaté", "severite": 3,
                 "detail": "Le marché des ateliers, dépôts et garages de village n'est pas publié : le "
                           "loyer retenu de 450 €/mois est un seuil de doctrine, pas un constat. Il se "
                           "valide par un bail signé avant l'acte, sinon le poste reste une hypothèse "
                           "sur laquelle le prix ne peut pas être payé."},
                {"facteur": "Liquidité de revente étroite", "severite": 3,
                 "detail": "Peu d'acquéreurs pour une maison de village avec annexes à Cuers, et une "
                           "décote de plus de moitié constatée sur les surfaces de plus de 150 m² dans "
                           "la commune. Le bien se revend au prix d'un logement familial, pas au prix "
                           "d'un programme, et la valeur des garages isolés dépend d'un marché local "
                           "étroit qui ne se présume pas."},
                {"facteur": "Deux baux, deux calendriers", "severite": 2,
                 "detail": "Séparer le logement et les annexes double la rotation et les impayés "
                           "possibles, et suppose des compteurs en état ou une division des réseaux. "
                           "Le gain de revenu marginal se paie en gestion."},
            ],
        },
    }


def variante(r, loyer=None, loyer2=None, travaux=None, vacance=None, prix=None, entretien=None):
    rr = copy.deepcopy(r)
    if loyer is not None:
        rr["marche"]["loyers"][0]["loyer_mensuel_euros"] = loyer
    if loyer2 is not None:
        rr["marche"]["loyers"][1]["loyer_mensuel_euros"] = loyer2
    if travaux is not None:
        rr["bien"]["travaux"]["montant_euros"] = travaux
    if vacance is not None:
        rr["hypotheses"]["vacance_base_pct"] = vacance
    if entretien is not None:
        rr["hypotheses"]["charges"]["entretien_annuel_euros"] = entretien
    if prix is not None:
        rr["annonce"]["prix_retenu_euros"] = prix
    return rr


def solde(computed, assiette):
    return computed["fiscal"]["net_apres_is"] / 12.0 - assiette * 0.9 * (0.037 / 12) / (1 - (1 + 0.037 / 12) ** -180) \
        - assiette * 0.9 * 0.0034 / 12


def main():
    r = fiche()

    # --- moteur sur les trois stratégies, avant rédaction des textes
    c_ret = engine.compute(r)

    c_nue = engine.compute(variante(r, loyer=LOYER_MAISON, loyer2=0.0, travaux=TRAVAUX_NUE))
    c_coloc = engine.compute(variante(r, loyer=LOYER_COLOC, travaux=TRAVAUX_COLOC))

    # marginal : exploiter les annexes à part plutôt que de les laisser dans le bail du logement
    c_sans_annexe = engine.compute(variante(r, loyer2=0.0, travaux=TRAVAUX_NUE))
    gain_annexe = c_ret["fiscal"]["ebe"] - c_sans_annexe["fiscal"]["ebe"]
    capital_annexe = TRAVAUX - TRAVAUX_NUE

    # division en deux logements : le rez-de-chaussée de 64 m² devient un T3
    c_division = engine.compute(variante(r, loyer=LOYER_LOGEMENT, loyer2=650.0,
                                         travaux=TRAVAUX_DIVISION))
    gain_division = c_division["fiscal"]["ebe"] - c_ret["fiscal"]["ebe"]
    capital_division = TRAVAUX_DIVISION - TRAVAUX

    # revente à la découpe (marchand de biens) : valeurs DVF de la commune
    revient_mdb = PRIX * 1.08 + 110000.0
    sortie_basse = 105 * 2609.0 + 3 * 10000.0
    sortie_haute = 115 * 3134.0 + 3 * 15000.0

    r["analyse"]["strategies_explorees"] = [
        {"strategie": "Logement à l'étage loué nu, annexes louées séparément",
         "lots": 2,
         "performance": f"Deux baux sur un même titre, {eur(LOYER_LOGEMENT + LOYER_ANNEXES)}/mois de "
                        f"recettes cibles, pour un rendement net après IS de "
                        f"{c_ret['rendements']['net_sur_revient_pct']:.2f} % sur un prix de revient de "
                        f"{eur(c_ret['prix_revient_total'])}. Le logement seul, sans les annexes, "
                        f"n'apporterait que {eur(gain_annexe)}/an d'EBE en moins : c'est l'annexe qui "
                        f"fait basculer le compte",
         "valeur_sortie": f"Les annexes se lisent au lot : trois garages de 15 m² et une dépendance de "
                          f"41 m², soit de l'ordre de 60 000 à 80 000 € de valeur de revente "
                          f"potentielle indépendamment du logement. Cette valeur ne se réalise qu'avec "
                          f"un accès indépendant et un acheteur : elle n'entre dans aucun plafond",
         "faisabilite": "Sans autorisation tant que les annexes restent des locaux accessoires du "
                        "logement ; déclaration préalable, vérification du PLU et places de "
                        "stationnement dès qu'on en fait un logement ou un local d'activité autonome",
         "risque": "modéré — le loyer de l'annexe n'est pas constaté, il se valide par un bail avant "
                   "l'acte"},
        {"strategie": "Location nue de la maison entière, un seul bail",
         "lots": 1,
         "performance": f"Assiette {eur(LOYER_MAISON)}/mois, rendement net après IS de "
                        f"{c_nue['rendements']['net_sur_revient_pct']:.2f} % sur "
                        f"{eur(c_nue['prix_revient_total'])} de prix de revient. C'est la variante la "
                        f"plus simple à documenter et la plus faible : le locataire paie les annexes "
                        f"au rabais, et le logement reste soumis au calendrier du DPE",
         "valeur_sortie": "Le lot entier se revend comme une maison de village, à la décote des "
                          "grandes surfaces de la commune",
         "faisabilite": "Immédiate après rafraîchissement : un seul bail, aucune autorisation",
         "risque": "faible en exploitation, mais c'est la variante qui produit le moins"},
        {"strategie": "Colocation meublée à l'étage, annexes louées séparément",
         "lots": 5,
         "performance": f"Trois chambres à 430 € et les annexes, soit {eur(LOYER_COLOC + LOYER_ANNEXES)}/mois, "
                        f"pour un rendement de {c_coloc['rendements']['net_sur_revient_pct']:.2f} % après "
                        f"{eur(TRAVAUX_COLOC - TRAVAUX)} de travaux et d'ameublement supplémentaires. "
                        f"Aucun relevé de colocation n'existe sur la commune : la cible repose sur un "
                        f"raisonnement, pas sur un constat, et une maison de village sans séjour "
                        f"partagé rénové se loue mal en colocation",
         "valeur_sortie": "Aucune prime de valeur à la revente : un acheteur familial ne paie pas "
                          "plus cher un bien découpé en chambres",
         "faisabilite": "Chambres à créer, séjour à sacrifier en partie, mobilier et fluides à "
                        "financer : c'est un chantier et une exploitation, pas un investissement "
                        "passif",
         "risque": "élevé — seul levier de revenu théorique, sans preuve de demande locale"},
        {"strategie": "Division en deux logements (rez-de-chaussée aménagé en T3) et annexes louées",
         "lots": 3,
         "performance": f"Le gain de loyer est de {eur(gain_division)}/an d'EBE pour "
                        f"{eur(capital_division)} de travaux supplémentaires, soit "
                        f"{(gain_division / capital_division * 100):.1f} % du capital engagé : sous "
                        f"notre cible de 10 à 12 % pour un capital travaux, et le second logement "
                        f"tombe sous le seuil de surface et de stationnement du PLU à vérifier",
         "valeur_sortie": "Deux logements valent moins au mètre carré qu'une maison à Cuers : "
                          "2 609 à 3 134 €/m² pour les appartements contre 3 590 €/m² pour les "
                          "maisons (DVF, tranches 45-80 m² et 80-150 m²)",
         "faisabilite": "Déclaration préalable, vérification de la zone du PLU, places de stationnement "
                        "à créer, compteurs d'eau et d'électricité à séparer, réseaux à reprendre",
         "risque": "élevé — délai d'instruction en condition suspensive, et un capital travaux mieux "
                   "employé ailleurs"},
        {"strategie": "Achat, rafraîchissement puis revente à la découpe (marchand de biens)",
         "lots": 4,
         "performance": f"Écartée : {eur(sortie_basse)} à {eur(sortie_haute)} de produit de revente "
                        f"(105 à 115 m² de logements au prix des appartements de la commune, plus "
                        f"trois garages) contre {eur(revient_mdb)} de prix de revient avec "
                        f"110 000 € de travaux. À Cuers l'appartement se vend 2 609 à 3 134 €/m² quand "
                        f"la maison se vend 3 590 €/m² : découper une maison en lots d'habitation "
                        f"détruit du prix au mètre carré au lieu d'en créer",
         "valeur_sortie": f"{eur(sortie_basse)} à {eur(sortie_haute)} de sortie contre "
                          f"{eur(revient_mdb)} de revient, hors portage et hors honoraires de vente",
         "faisabilite": "Division en lots ou en volumes à créer, plan de vente, portage de 18 à "
                        "24 mois, TVA et structure commerciale à mettre en place",
         "risque": "élevé — et sans objet : l'opération est perdante avant même d'être risquée"},
    ]

    r["analyse"]["risques"][0]["detail"] = (
        f"Prix affiché {eur(PRIX)}, prix de revient {eur(c_ret['prix_revient_total'])} une fois les "
        f"frais d'acquisition et les travaux budgétés, pour un rendement net après IS de "
        f"{c_ret['rendements']['net_sur_revient_pct']:.2f} % contre un plancher de branche de 5 %. "
        f"Le prix qui atteint ce plancher ressort à {eur(122500)} : l'écart dépasse 240 000 €, soit "
        f"plus de 65 % du prix affiché. Une remise de cette ampleur n'existe pas sur un bien affiché "
        f"dans sa tranche de marché — ce n'est pas un dossier à négocier, c'est un dossier qui "
        f"n'existe pas à ce prix."
    )

    errs = schema.validate_record(r)
    if errs:
        raise SystemExit(f"record invalide : {errs}")
    print("champs_manquants :", schema.champs_manquants(r))

    note, verdict, comp = scoring.note_et_verdict(r, c_ret)
    if note is None:
        raise SystemExit("note non calculable")
    plafond, contrainte = scoring.prix_plafond(r)
    cible = scoring.prix_cible(r)

    with open(BASE, encoding="utf-8") as fh:
        data = json.load(fh)
    avant = len(data["analyses"])
    data["analyses"] = [a for a in data["analyses"] if a["slug"] != SLUG]
    data["analyses"].append(r)
    data["meta"]["count"] = len(data["analyses"])
    with open(BASE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    with open(BASE, encoding="utf-8") as fh:
        relu = json.load(fh)
    apres = len(relu["analyses"])
    print(f"base : {avant} → {apres} fiches | clés racine : {sorted(relu.keys())}")

    def fmt(x):
        return "aucun" if x is None else f"{x:,.0f}".replace(",", " ")

    print(f"note {note} / {verdict} ({comp.get('plafonds')})")
    print(f"  performance {c_ret['rendements']['net_sur_revient_pct']:.2f} % | "
          f"ratio coût/valeur {c_ret['ratio_cout_valeur']:.3f} | adéquation {comp['s_adequation']} "
          f"| risque {comp['s_risque']}")
    print(f"  EBE {fmt(c_ret['fiscal']['ebe'])} | net après IS {fmt(c_ret['fiscal']['net_apres_is'])} "
          f"| revient {fmt(c_ret['prix_revient_total'])} | valeur {fmt(360000)}")
    print(f"  prix plafond {fmt(plafond)} € ({contrainte}) | prix cible {fmt(cible)} €")
    print(f"  marginal annexes : +{fmt(gain_annexe)} €/an d'EBE pour {fmt(capital_annexe)} € de travaux "
          f"= {gain_annexe / capital_annexe * 100:.1f} % du capital")
    print(f"  marginal division : +{fmt(gain_division)} €/an d'EBE pour {fmt(capital_division)} € de "
          f"travaux = {gain_division / capital_division * 100:.1f} % du capital")
    print(f"  MDB : revient {fmt(revient_mdb)} € | sortie {fmt(sortie_basse)} à {fmt(sortie_haute)} €")
    print(f"  scénarios : solde base {solde(c_ret, PRIX):+.0f} €/mois")


if __name__ == "__main__":
    main()
