#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saisie du record — Immeuble de rapport 4 T2, cœur de village, Cuers (83390).

SeLoger 258VMUYNSNEA — Cuers Immobilier, réf. 4060v — 365 000 € — relevé le 24/10/2026.
Seconde diffusion : Capifrance, Luc Maridet, réf. 964187 (mêmes lots, mêmes charges, TF).
Idempotent : le slug est filtré avant append.
"""
import copy
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

from analyse_app import engine, schema, scoring  # noqa: E402

SLUG = "2026-10-24-immeuble-4-t2-cuers-centre"
BASE = os.path.join(RACINE, "analyses", "analyses.json")

PRIX = 365000.0
FRAIS = 29200.0          # 8 %, régime ancien, honoraires vendeur
TRAVAUX = 0.0            # « rien à prévoir », rénovation 2019 annoncée, aucun devis
LOYER_CC = 2516.88       # SeLoger / Cuers Immobilier, charges comprises, quatre lots
LOYER_HC = 2340.0        # Capifrance : même bien, hors charges
LOYER_LOT_CC = LOYER_CC / 4.0    # 629,22 €/mois par lot
LOYER_LOT_HC = LOYER_HC / 4.0    # 585,00 €/mois par lot
CHARGES_COPRO = 2800.0   # budget prévisionnel annoncé par Capifrance (233 €/mois)
TF = 2470.0              # avis annoncé par Capifrance
PNO = 600.0              # 4 lots x 150 €, estimé
ENTRETIEN = 3100.0       # gestion 6 % (1 812) + impayés 3 % (906) + entretien 400
SURFACE = 117.56
VALEUR = 345000.0        # 4 lots x 29,4 m² au 3e quartile DVF des 24-36 m²


def eur(v):
    return f"{v:,.0f}".replace(",", " ") + " €"


def fiche():
    return {
        "slug": SLUG,
        "date_analyse": "2026-10-24",
        "date_maj": "2026-10-24",
        "titre": "Immeuble de rapport, 4 T2 loués — cœur de village, Cuers (83390)",
        "bien": {
            "type_bien": "immeuble",
            "sous_type": "immeuble de rapport",
            "type_detail": "Immeuble de rapport sur 4 niveaux, construit en 1940 et entièrement rénové "
                           "intérieur et extérieur en 2019 : quatre appartements de type 2 d'environ "
                           "29 m² chacun, un par niveau, avec salon-cuisine ouverte équipée, une "
                           "chambre, une salle d'eau avec WC, climatisation réversible et menuiseries "
                           "PVC double vitrage. Copropriété de 4 lots, terrain de 80 m². Ni cave ni "
                           "parking. DPE C (162 kWh/m²/an), GES A (4 kg CO2/m²/an).",
            "neuf": False,
            "adresse": {
                "texte": "Cœur du village, Cuers (83390) — adresse exacte non communiquée par l'agence",
                "ville": "Cuers",
                "code_postal": "83390",
                "quartier": "Centre-ville",
            },
            "surfaces": {"texte": "117,56 m² annoncés par Cuers Immobilier, 118 m² Carrez par Capifrance "
                                  "pour la même copropriété : quatre lots d'environ 29,4 m², un par "
                                  "niveau. La cohérence des deux diffusions vaut mesurage à confirmer "
                                  "lot par lot sur les diagnostics"},
            "lots": {"count": 4,
                     "nature": "Quatre T2 d'environ 29 m², un par niveau, dans une copropriété de "
                               "4 lots dont le vendeur détient l'intégralité. Aucune cave, aucun "
                               "parking, aucun garage",
                     "lots_distincts": 4},
            "copro": {"charges_annuelles_euros": CHARGES_COPRO,
                      "charges_source": "Budget prévisionnel annoncé par Capifrance : 2 800 €/an, soit "
                                        "233 €/mois pour l'ensemble de la copropriété. Le loyer de "
                                        "Cuers Immobilier est donné charges comprises à 2 516,88 €/mois, "
                                        "contre 2 340 € hors charges chez Capifrance : l'écart de "
                                        "176,88 €/mois est la provision sur charges du locataire, soit "
                                        "2 123 €/an pour un budget de 2 800 €/an. Reste à la charge du "
                                        "bailleur environ 677 €/an, hors gros travaux"},
            "travaux": {
                "montant_euros": TRAVAUX,
                "nature": "Aucun devis au dossier. L'annonce affirme une rénovation intérieure et "
                          "extérieure complète en 2019 et « rien à prévoir » : c'est une déclaration du "
                          "vendeur, pas une pièce. Toiture, façade, évacuations et électricité des "
                          "communs d'un immeuble de 1940 se vérifient sur les PV d'AG, le carnet "
                          "d'entretien et le plan pluriannuel de travaux, aucun n'est fourni. Budget "
                          "retenu à zéro dans le scénario central, 5 000 € en Worst : c'est un choix de "
                          "lecture, pas un constat",
            },
        },
        "annonce": {
            "plateforme": "seloger",
            "url": "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/cuers-83390/258VMUYNSNEA",
            "prix_affiche_euros": PRIX,
            "prix_retenu_euros": PRIX,
            "prix_statut": "affiche",
            "vendeur": "Cuers Immobilier (Laetitia Martin), réf. 4060v — honoraires à la charge du "
                       "vendeur. Seconde diffusion : Capifrance, Luc Maridet, réf. 964187, même prix",
        },
        "marche": {
            "valeur": {
                "basse_euros": 320000.0,
                "haute_euros": 365000.0,
                "retenue_euros": VALEUR,
                "source": "DVF Cuers (83049), appartements de 24 à 36 m², mutations « Vente » "
                          "2021-2025 : 26 ventes, médiane 2 378 €/m², premier quartile 1 791, "
                          "troisième quartile 2 939, prix médian 66 600 € le lot. Sur la tranche "
                          "20-40 m² (40 ventes), médiane 2 617 €/m² et prix médian 76 950 €. La "
                          "tranche 30-45 m² affiche une médiane de 3 384 €/m² mais sa distribution est "
                          "tirée par une dizaine de ventes à 4 500-8 590 €/m², dont des lots neufs et "
                          "des lots avec garage : elle ne décrit pas ce produit. Les quatre lots sont "
                          "donc valorisés au troisième quartile de leur propre tranche, soit "
                          "2 939 €/m², pour tenir compte de la rénovation de 2019 et de la "
                          "climatisation : 4 x 29,4 m² x 2 939 = 345 600 €, retenus 345 000 €. Prix "
                          "affiché rapporté à cette valeur : 3 105 €/m², soit 5,7 % au-dessus du "
                          "troisième quartile de la tranche",
                "confiance": "moyenne",
            },
            "loyers": [
                {"lot": "Quatre T2 d'environ 29 m², loués nus, un par niveau",
                 "quantite": 4,
                 "loyer_mensuel_euros": round(LOYER_LOT_CC, 2),
                 "occupe": True,
                 "note": "Loyer encaissé, charges comprises, reconstitué : Cuers Immobilier annonce "
                         "2 516,88 €/mois CC, Capifrance 2 340 €/mois hors charges pour le même "
                         "immeuble, soit 585 € par lot. Le revenu encaissable retenu par le moteur est "
                         "le loyer CC moins les charges de copropriété (règle de la fiche "
                         "« charges comprises ») : 30 203 €/an moins 2 800 €/an. Confrontation au "
                         "marché du 24/10/2026, cinq annonces actives sur la commune : studio meublé de "
                         "30,19 m², 4 place Général de Gaulle, 560 à 620 €/mois CC selon la diffusion ; "
                         "studio non meublé de 29 m² en centre-ville, 550 €/mois CC (538 € HC), "
                         "septembre 2026 ; T2 de 42 m² rénové en 2023, 690 €/mois CC (635 € HC), soit "
                         "15,1 €/m² ; T2 meublé de 40 m² de caractère, 635 €/mois CC ; T2 de 53 m² "
                         "meublé avec garage de 26 m², 750 €/mois. Médiane DHUP 2025 de la commune : "
                         "13,9 €/m² (IC 95 % 10,7 à 18,0). Les 585 € hors charges par lot représentent "
                         "19,9 €/m² : au-dessus du haut de la fourchette des comparables de même "
                         "surface, et 43 % au-dessus de la médiane communale. Les loyers sont donc "
                         "encaissés au plafond du marché local, ce qui interdit d'en attendre une "
                         "progression : la relocation se ferait plutôt 8 à 12 % plus bas"},
            ],
            "notes": "Assiette encaissée : quatre baux en place, aucun lot vide annoncé. Le loyer est "
                     "donné CC par un mandataire et HC par l'autre ; la réconciliation des deux "
                     "diffusions est faite dans la ligne de loyers. Aucun bail, aucune quittance, "
                     "aucune régularisation de charges au dossier : le revenu est celui de l'annonce, "
                     "pas encore celui des pièces.",
        },
        "hypotheses": {
            "vacance_base_pct": 5.0,
            "vacance_best_pct": 2.0,
            "vacance_worst_pct": 12.0,
            "taux_placement_reserve_pct": 2.84,
            "quote_part_bati_pct": 90.0,
            "vacance_justification": "Quatre micro-lots de 29 m² : la rotation est structurellement "
                                     "plus élevée que sur des T3 familiaux, chaque départ coûte "
                                     "585 €/mois de loyer et remet un bail en jeu. 5 % en base (soit "
                                     "un lot vide deux mois et demi par an), 2 % en best, 12 % en worst "
                                     "(un lot vide six mois, ou deux lots en décalage)",
            "charges": {
                "charges_copro_annuelles_euros": CHARGES_COPRO,
                "charges_copro_commentaire": "2 800 €/an, budget prévisionnel annoncé par Capifrance "
                                             "(233 €/mois). Le locataire en paie 2 123 €/an par ses "
                                             "provisions : le solde de 677 €/an reste au bailleur. Le "
                                             "poste est saisi en charges et non déduit deux fois, le "
                                             "loyer étant pris charges comprises",
                "taxe_fonciere_annuelle_euros": TF,
                "taxe_fonciere_commentaire": "2 470 €/an, montant annoncé par Capifrance. La commune "
                                            "applique l'un des taux de taxe foncière sur le bâti les "
                                            "plus élevés du Var (53,63 % en 2025) : l'avis réel reste à "
                                            "exiger, c'est le deuxième poste de charges du dossier",
                "entretien_annuel_euros": ENTRETIEN,
                "entretien_commentaire": "3 100 €/an : gestion locative déléguée à 6 % des loyers "
                                         "(1 812 €), provision d'impayés à 3 % (906 €, distincte de la "
                                         "vacance) et 400 € d'entretien courant de l'immeuble. Quatre "
                                         "baux, quatre relocations potentielles : le poste de gestion "
                                         "n'est pas marginal sur ce format",
                "pno_annuelle_euros": PNO,
                "comptabilite_annuelle_euros": 0.0,
            },
            "frais_acquisition_euros": FRAIS,
            "frais_acquisition_commentaire": "8 % du prix (29 200 €), régime ancien ; honoraires à la "
                                             "charge du vendeur, donc hors base de calcul",
        },
        "analyse": {
            "branche": "residentiel",
            "type_operation": "locatif",
            "strategie_retenue": {
                "nom": "Conservation en bloc des quatre T2 loués nus",
                "code": "ld-nue",
                "lots": 4,
            },
            "strategies_explorees": [],
            "attractivite": [
                {"dimension": "transports", "score": 7,
                 "justification": "Cœur de village à quelques minutes à pied des arrêts, gare TER "
                                  "Cuers-Pierrefeu à environ trois kilomètres (Toulon à une vingtaine "
                                  "de minutes) et accès A57 immédiat. Quatre lots sans parking dans un "
                                  "bourg où la voiture reste nécessaire : la gare séduit un locataire "
                                  "toulonnais, l'absence de stationnement le retient."},
                {"dimension": "commerces", "score": 8,
                 "justification": "Hypercentre : place de la Convention, marché hebdomadaire, "
                                  "commerces de proximité, santé et services à pied. C'est le meilleur "
                                  "argument du bien et celui qui tient les loyers au plafond."},
                {"dimension": "ecoles", "score": 7,
                 "justification": "Écoles primaires, collège La Ferrage et ensemble privé "
                                  "Sainte-Marthe sur la commune. La clientèle existe, mais un T2 de "
                                  "29 m² en centre ne vise pas une famille : c'est un argument de "
                                  "revente, pas de location."},
                {"dimension": "securite", "score": 5,
                 "justification": "Commune pavillonnaire sans quartier prioritaire, mais nos dossiers "
                                  "antérieurs sur Cuers relevaient des incivilités et un déficit "
                                  "d'image du centre. Un immeuble de 1940 en cœur de bourg : la "
                                  "tranquillité dépend de la rue et du voisinage immédiat."},
                {"dimension": "demande_locative", "score": 6,
                 "justification": "Les petites surfaces se relouent : cinq annonces actives de 29 à "
                                  "53 m² au 24/10/2026, dont deux studios de 29-30 m² à 550 et "
                                  "620 €/mois. La demande porte sur ce format, pas sur les grands "
                                  "appartements. Le risque n'est pas l'absence de demande, c'est le "
                                  "niveau de loyer : les 585 € HC du dossier sont au-dessus du haut de "
                                  "la fourchette constatée."},
                {"dimension": "dynamisme", "score": 5,
                 "justification": "Bourg de 12 300 habitants, revenu médian autour de 23 000 €, "
                                  "dépendance à l'emploi toulonnais. Marché sans fièvre : à 3 105 €/m², "
                                  "la plus-value n'est pas le moteur du dossier, et il ne faut pas "
                                  "l'attendre en consolation d'un rendement moyen."},
            ],
            "risques": [
                {"facteur": "Prix au-dessus de la valeur de la tranche et du plancher de rendement",
                 "severite": 5, "detail": ""},
                {"facteur": "Quatre micro-lots de 29 m² : rotation et vacance", "severite": 4,
                 "detail": "Quatre baux de petites surfaces, quatre occasions de départ par cycle. "
                           "Chaque lot vide coûte 585 €/mois de loyer, plus sa part de charges fixes : "
                           "sur un an, un seul lot vacant trois mois efface un quart de l'EBE. Le "
                           "format se loue, mais il se loue vite et se vide vite, et la gestion de "
                           "quatre baux pèse plus lourd que sur un immeuble de trois lots familiaux."},
                {"facteur": "Loyers au plafond du marché, sans marge de relocation", "severite": 4,
                 "detail": "585 € hors charges pour 29 m², soit 19,9 €/m², contre 538 à 600 € charges "
                           "comprises pour des surfaces équivalentes relevées le 24/10/2026 et une "
                           "médiane communale DHUP de 13,9 €/m². Les loyers en place sont donc "
                           "au-dessus du marché, pas en dessous : aucune progression à attendre, et "
                           "une relocation se ferait 8 à 12 % plus bas. Un bail en cours ne se révise "
                           "pas au-delà de l'IRL, et un locataire qui part emporte le loyer avec lui."},
                {"facteur": "Charges « eau, électricité et parties communes » incluses dans le loyer",
                 "severite": 3,
                 "detail": "L'annonce de Cuers Immobilier précise que les charges comprises couvrent "
                           "l'eau, l'électricité et les parties communes. Or la provision du locataire "
                           "n'est que de 2 123 €/an pour quatre lots, quand la seule consommation "
                           "d'électricité estimée du bâtiment tourne autour de 2 900 à 3 570 €/an "
                           "(DPE). Si les compteurs individuels n'existent pas et que le bailleur paie "
                           "réellement l'électricité des locataires, le poste coûte 2 500 à 3 000 €/an "
                           "de plus que ce que la provision couvre, et l'EBE tombe de 18 900 à "
                           "16 000 €. Réponse à obtenir : compteurs individuels eau et électricité, "
                           "dernière régularisation de charges, décomposition des baux."},
                {"facteur": "« Rien à prévoir » sans aucune pièce sur un immeuble de 1940", "severite": 3,
                 "detail": "La rénovation de 2019 est une déclaration d'annonce. Aucun PV d'AG, aucun "
                           "carnet d'entretien, aucun plan pluriannuel de travaux, aucun devis, aucun "
                           "diagnostic daté au dossier. Sur un immeuble de 1940 en centre ancien, "
                           "toiture, façades, évacuations et électricité des communs sont les postes "
                           "que l'annonce tait, et un ravalement ou une réfection de toiture se paie "
                           "comptant, sans mutualisation possible puisque la copropriété ne compte que "
                           "quatre lots, tous détenus par le vendeur."},
                {"facteur": "Copro de 4 lots : aucun lissage possible", "severite": 3,
                 "detail": "Toute dépense de copropriété retombe à 25 % sur chaque lot, et l'acheteur "
                           "devient majoritaire de fait dans une copropriété sans historique. Les "
                           "trois derniers PV d'AG, les appels de fonds des trois dernières années et "
                           "le carnet d'entretien sont les pièces qui disent si l'immeuble a été "
                           "entretenu ou seulement repeint en 2019."},
                {"facteur": "Aucune cave, aucun parking, aucun extérieur", "severite": 2,
                 "detail": "Quatre lots sans annexe : rien à louer séparément, rien à valoriser à la "
                           "revente, et un frein à la relocation dans un bourg où le stationnement en "
                           "centre est contraint. C'est aussi ce qui plafonne le prix au mètre carré "
                           "face aux appartements vendus avec garage."},
            ],
        },
    }


def variante(r, loyer=None, vacance=None, travaux=None, prix=None, entretien=None,
             charges=None, loger_hc=None):
    rr = copy.deepcopy(r)
    if loyer is not None:
        rr["marche"]["loyers"][0]["loyer_mensuel_euros"] = loyer
    if vacance is not None:
        rr["hypotheses"]["vacance_base_pct"] = vacance
    if travaux is not None:
        rr["bien"]["travaux"]["montant_euros"] = travaux
    if entretien is not None:
        rr["hypotheses"]["charges"]["entretien_annuel_euros"] = entretien
    if charges is not None:
        rr["hypotheses"]["charges"]["charges_copro_annuelles_euros"] = charges
    if prix is not None:
        rr["annonce"]["prix_retenu_euros"] = prix
        rr["hypotheses"]["frais_acquisition_euros"] = round(prix * 0.08)
    return rr


def annuite(assiette, taux=0.037, mois=240, ass=0.0034):
    """Coefficient de remboursement mensuel du standard du groupe (90 % du prix + travaux)."""
    i = taux / 12.0
    return assiette * 0.9 * i / (1 - (1 + i) ** -mois) + assiette * 0.9 * ass / 12.0


def main():
    r = fiche()
    c = engine.compute(r)

    c_hc = engine.compute(variante(r, loyer=LOYER_LOT_HC, charges=(CHARGES_COPRO - 2123.0)))
    c_meuble = engine.compute(variante(r, loyer=LOYER_LOT_CC + 55.0, entretien=ENTRETIEN + 900.0))
    c_worst = engine.compute(variante(r, loyer=LOYER_LOT_CC * 0.88, vacance=12.0, travaux=5000.0,
                                      charges=CHARGES_COPRO + 500.0))

    # revente à la découpe : la copropriété de 4 lots existe déjà, aucune division à créer
    revient_decoupe = PRIX * 1.08
    sortie_basse = 4 * 29.39 * 2378.0
    sortie_haute = 4 * 29.39 * 2939.0
    frais_vente = (sortie_basse + sortie_haute) / 2 * 0.06

    r["analyse"]["strategies_explorees"] = [
        {"strategie": "Conservation en bloc des quatre T2 loués nus",
         "lots": 4,
         "performance": f"{eur(LOYER_LOT_CC)}/mois par lot charges comprises, soit {eur(LOYER_CC * 12)}/an pour les quatre, pour "
                        f"un rendement net après IS de {c['rendements']['net_sur_revient_pct']:.2f} % "
                        f"sur un prix de revient de {eur(c['prix_revient_total'])}. Le brut affiché "
                        f"est de 8,27 % ; c'est la lecture après charges, taxe foncière et vacance "
                        f"qui décide, et elle passe sous le plancher de 5 %",
         "valeur_sortie": f"Valeur de capitalisation à 8 % de l'EBE : {eur(c['fiscal']['ebe'] / 0.08)} "
                          f"contre {eur(c['prix_revient_total'])} de revient, soit une revente à "
                          f"l'équilibre au mieux. Valeur de marché par les lots : 345 000 €, sous le "
                          f"revient",
         "faisabilite": "Immédiate : quatre baux en place, aucun travaux annoncé, une copropriété de "
                        "quatre lots déjà constituée",
         "risque": "modéré en exploitation, élevé en prix — le bien produit, il ne produit pas assez "
                   "pour ce qu'il coûte"},
        {"strategie": "Relocation des quatre lots en meublé",
         "lots": 4,
         "performance": f"{eur(LOYER_LOT_CC + 55.0)}/mois par lot, soit +220 €/mois de recettes brutes, pour "
                        f"{eur(900.0 * 0)} de charges supplémentaires et l'ameublement des quatre lots "
                        f"(environ 16 000 €). Rendement net après IS de "
                        f"{c_meuble['rendements']['net_sur_revient_pct']:.2f} % : le gain de loyer est "
                        f"absorbé par la rotation plus rapide et le mobilier à remplacer",
         "valeur_sortie": "Aucune prime de valeur à la revente : le meublé se paie au loyer, pas au "
                          "mètre carré",
         "faisabilite": "Changement de nature de bail, ameublement complet de quatre lots, gestion des "
                        "entrées et sorties : c'est un métier, pas un aménagement",
         "risque": "élevé — le meublé sur 29 m² en bourg vise une clientèle de passage, celle qui part "
                   "le plus vite, et les loyers actuels sont déjà au plafond"},
        {"strategie": "Revente à la découpe des quatre lots",
         "lots": 4,
         "performance": f"La copropriété existe déjà, il n'y a rien à diviser : {eur(sortie_basse)} à "
                        f"{eur(sortie_haute)} de produit brut, moins environ {eur(frais_vente)} de "
                        f"frais de vente, contre {eur(revient_decoupe)} de revient. L'opération perd "
                        f"de l'argent avant portage",
         "valeur_sortie": f"{eur(sortie_basse)} à {eur(sortie_haute)} au troisième quartile de la "
                          f"tranche des 24-36 m² (DVF Cuers, 26 ventes 2021-2025)",
         "faisabilite": "Techniquement simple — quatre lots, quatre acquéreurs — mais 18 à 24 mois de "
                        "portage, deux jeux de frais et une structure commerciale",
         "risque": "élevé et sans objet : à ce prix d'entrée, la découpe ne crée pas de marge"},
    ]

    r["analyse"]["risques"][0]["detail"] = (
        f"Prix affiché {eur(PRIX)}, prix de revient {eur(c['prix_revient_total'])} pour un rendement "
        f"net après IS de {c['rendements']['net_sur_revient_pct']:.2f} %, sous le plancher de 5 % de la "
        f"branche. Ramené à la valeur de la tranche de surface — 2 939 €/m², troisième quartile des "
        f"24-36 m² à Cuers —, le bien vaut {eur(VALEUR)} : le prix affiché est 5,7 % au-dessus, et le "
        f"prix de revient 14,3 % au-dessus. Le prix qui atteint le plancher ressort à "
        f"{eur(scoring.prix_plafond(r)[0])}. Ce n'est pas un écart de 40 % qui rendrait le dossier "
        f"impossible : c'est un écart de 10 % sur un bien au prix du marché, qui se joue sur la "
        f"négociation ou ne se joue pas."
    )

    errs = schema.validate_record(r)
    if errs:
        raise SystemExit(f"record invalide : {errs}")
    print("champs_manquants :", schema.champs_manquants(r))

    note, verdict, comp = scoring.note_et_verdict(r, c)
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
    print(f"base : {avant} → {len(relu['analyses'])} fiches")

    def fmt(x):
        return "aucun" if x is None else f"{x:,.0f}".replace(",", " ")

    print(f"note {note} / {verdict} ({comp.get('plafonds')})")
    print(f"  performance {c['rendements']['net_sur_revient_pct']:.2f} % | brut "
          f"{LOYER_CC * 12 / PRIX * 100:.2f} % | ratio coût/valeur {c['ratio_cout_valeur']:.3f}")
    print(f"  EBE {fmt(c['fiscal']['ebe'])} | net après IS {fmt(c['fiscal']['net_apres_is'])} | "
          f"revient {fmt(c['prix_revient_total'])} | IS {fmt(c['fiscal']['is_annuel'])}")
    print(f"  prix plafond {fmt(plafond)} € ({contrainte}) | prix cible {fmt(cible)} €")
    print(f"  solde mensuel standard : {c['fiscal']['net_apres_is'] / 12 - annuite(PRIX):+.0f} €/mois")
    print(f"  variante loyers HC 2 340 : {c_hc['rendements']['net_sur_revient_pct']:.2f} % | "
          f"meublé : {c_meuble['rendements']['net_sur_revient_pct']:.2f} % | worst : "
          f"{c_worst['rendements']['net_sur_revient_pct']:.2f} %")
    print(f"  découpe : sortie {fmt(sortie_basse)} à {fmt(sortie_haute)} | revient {fmt(revient_decoupe)}")
    # prix d'équilibre du cash-flow (net après IS = échéance)
    p = PRIX
    for _ in range(60):
        rr = variante(r, prix=p)
        cc = engine.compute(rr)
        solde = cc["fiscal"]["net_apres_is"] / 12 - annuite(p)
        p += solde / 0.0056 * 0.5 if abs(solde) > 5 else 0
        if abs(solde) < 5:
            break
    print(f"  prix de cash-flow nul : {fmt(p)} €")


if __name__ == "__main__":
    main()
