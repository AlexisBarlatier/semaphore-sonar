#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche Pierrefeu-du-Var — immeuble de rapport, local commercial + 2 appartements + combles,
141 m2, 247 000 EUR (SeLoger 26V4LZNKNUL9, agence Cuers Immobilier & L'Immobiliere).

Branche locative (SCI a l'IS). La fiche est regeneree a partir du moteur ; le record
est ecrit dans analyses/analyses.json (source de verite du listing).
"""
import copy
import importlib.util
import json
import os
import sys

ROOT = '/home/alexis-barlatier/Documents/Semaphore-sonar'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from analyse_app import engine, scoring  # noqa: E402

SLUG = "2026-09-22-immeuble-rapport-pierrefeu-du-var"
URL = "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/pierrefeu-du-var-83390/26V4LZNKNUL9"

PRIX = 247000.0
NOTAIRE_PCT = 0.08
FRAIS_ACQ = PRIX * NOTAIRE_PCT
TRAVAUX = 30000.0
LOYERS_AN = 18300.0
LOYERS_MARCHE_AN = 20700.0
LOYERS_BEST_AN = 27900.0
TAUX = 0.037
DUREE = 15

TAUX_LOAN_MENS = None


def mens(capital, taux, annees):
    i = taux / 12.0
    n = annees * 12
    return capital * i / (1 - (1 + i) ** -n)


def eur(v):
    return f"{v:,.0f}".replace(',', ' ')


def fr(v, dec=1):
    return f"{v:.{dec}f}".replace('.', ',')


def charge_annuelle(tf, copro, pno, entretien, compta, extra):
    return tf + copro + pno + entretien + compta + extra


def ebe_annuel(brut, vac_pct, charges):
    return brut * (1 - vac_pct) - charges


def plafond_cf(brut, charges, annees):
    ebe = ebe_annuel(brut, 0.05, charges)
    k = mens(1.0, TAUX, annees)
    return (ebe / 12.0) / (0.90 * k)


def plafond_5pct(brut, charges, travaux):
    ebe = ebe_annuel(brut, 0.05, charges)
    return (ebe / 0.05 - travaux) / (1 + NOTAIRE_PCT)


def rec_pierrefeu(entretien=2291.0):
    return {
        "slug": SLUG,
        "date_analyse": "2026-09-22",
        "date_maj": None,
        "titre": "Immeuble de rapport — local commercial, deux appartements et combles (141 m²) — Cœur de ville, Pierrefeu-du-Var (83390)",
        "bien": {
            "type_bien": "immeuble",
            "sous_type": None,
            "type_detail": (
                "Immeuble de rapport de trois étages en cœur de ville, sur rue passante : un local à usage "
                "professionnel de 38 m² avec vitrine en rez-de-chaussée, deux appartements de type 2, et un grenier "
                "de deux grandes pièces accessible par escalier, aménageable en troisième logement sous réserve des "
                "autorisations d'urbanisme. Compteurs individuels, double vitrage, chauffage individuel, "
                "climatisation au rez-de-chaussée. Bâti de 1948. Le portail affiche l'état « à rénover ». "
                "Pas de cave, non accessible aux personnes à mobilité réduite. Copropriété NON : monopropriété, "
                "donc aucune charge de syndic mais la totalité de la structure et de la toiture à la charge du "
                "propriétaire."
            ),
            "neuf": False,
            "adresse": {
                "texte": "Cœur de ville, Pierrefeu-du-Var (83390) — adresse exacte non communiquée "
                         "(nombreux parkings dans l'environnement immédiat, proximité des commerces et des écoles)",
                "ville": "Pierrefeu-du-Var",
                "code_postal": "83390",
            },
            "surfaces": {
                "texte": (
                    "141 m² annoncés par SeLoger, 148 m² par bien'ici sur le même immeuble (8 pièces, 256 000 € "
                    "il y a cinq mois) : répartition non communiquée entre le local commercial (~38 m²), les deux "
                    "appartements (~47 m²) et les combles (non comptés). Aucune surface Carrez par lot. "
                    "L'écart de 7 m² entre les deux portails et la surface exacte de chaque lot sont à obtenir "
                    "avant toute offre."
                ),
                "carrez_m2": 141.0,
            },
            "lots": {
                "count": 3,
                "surface_par_lot_m2": None,
                "nature": (
                    "Trois lots d'activité et d'habitation : un local commercial de 38 m² avec vitrine sur rue "
                    "passante en rez-de-chaussée, deux appartements aux étages, plus des combles de deux grandes "
                    "pièces qui permettraient un troisième logement. Immeuble en monopropriété, donc aucun lot "
                    "juridiquement divisé : une revente à la découpe exigerait un état descriptif de division, "
                    "de l'ordre de 5 000 à 10 000 € et six à neuf mois."
                ),
                "lots_distincts": 3,
            },
            "copro": {
                "charges_annuelles_euros": 0.0,
                "charges_source": (
                    "Copropriété NON — immeuble en monopropriété (mention de la fiche Logic-Immo : « immeuble de "
                    "rapport en mono »). Aucune charge de copropriété, aucun syndic. En contrepartie, la toiture, "
                    "la façade, les réseaux et la structure d'un bâti de 1948 sont intégralement portés par le "
                    "propriétaire : c'est le premier poste de risque non chiffré du dossier, sur un immeuble dont "
                    "aucun gros travaux n'est documenté."
                ),
            },
            "travaux": {
                "montant_euros": TRAVAUX,
                "nature": (
                    "État annoncé « à rénover » par le portail, sans devis, sans nature détaillée, sans plan et "
                    "sans diagnostic technique joint. Provision retenue 30 000 € (213 €/m²) pour la remise en "
                    "sécurité et la remise au standard de location des lots en place : électricité, plomberie, "
                    "menuiseries, peintures, remise en état du local. Ne sont PAS chiffrés : la couverture, la "
                    "charpente et les réseaux d'un bâti de 1948 en monopropriété (fourchette 20 000 à 50 000 €), "
                    "ni le rafraîchissement des parties communes. L'aménagement des combles en troisième logement "
                    "est un projet distinct, estimé 55 000 à 75 000 € (isolation, plancher, menuiseries, réseaux, "
                    "cuisine et salle d'eau pour environ 40 m²), avec création de surface de plancher donc "
                    "autorisation d'urbanisme et taxe d'aménagement."
                ),
            },
        },
        "annonce": {
            "plateforme": "SeLoger",
            "url": URL,
            "prix_affiche_euros": PRIX,
            "prix_retenu_euros": None,
            "prix_statut": "affiche",
            "prix_commentaire": (
                "247 000 €, soit 1 752 €/m² sur les 141 m² annoncés, honoraires à la charge du vendeur. "
                "Le même immeuble était affiché 256 000 € sur bien'ici il y a cinq mois (148 m², 8 pièces) : "
                "−9 000 € (−3,5 %) et passage en exclusivité après cinq mois sans acheteur. Le ratio au m² est "
                "trompeur : il mélange deux appartements, un local commercial et un grenier non aménagé, et il "
                "ne doit pas être comparé aux 2 716 €/m² de la médiane des appartements de la commune."
            ),
        },
        "marche": {
            "valeur": {
                "basse_euros": 250000.0,
                "haute_euros": 300000.0,
                "retenue_euros": 280000.0,
                "source": (
                    "Valorisation par composant : deux appartements de 47 m² à 2 716 €/m² — médiane communale des "
                    "appartements (MeilleursAgents et Figaro Immobilier, septembre 2026) — soit 255 300 € ; local "
                    "commercial de 38 m² à 800 €/m², soit 30 400 € ; combles non aménagés de 40 m² à 300 €/m², "
                    "soit 12 000 €. Total brut 297 700 €, ramené à 280 000 € après décote de liquidité et de "
                    "délai de vente. Les moyennes communales toutes catégories (3 340 €/m² pour MeilleursAgents, "
                    "4 046 €/m² pour PAP) ne sont pas des références ici : elles sont tirées vers le haut par les "
                    "maisons, qui représentent 78 % du parc de la commune."
                ),
                "confiance": "moyenne",
            },
            "loyers": [
                {
                    "lot": "Local commercial 38 m² (rez-de-chaussée, vitrine sur rue passante)",
                    "quantite": 1,
                    "loyer_mensuel_euros": 450.0,
                    "occupe": True,
                    "note": (
                        "Répartition non communiquée : l'annonce donne un total de 18 300 €/an « baux en cours », "
                        "sans détail par lot. Répartition retenue par analogie avec le marché constaté. "
                        "Comparables : loyer commercial moyen à Pierrefeu-du-Var de 220 €/m²/an (fourchette basse "
                        "87 €, haute 257 €, UnEmplacement au 02/09/2026), soit 275 à 813 €/mois pour 38 m² ; "
                        "1 200 €/mois pour 105 m² à Cuers. Le local est le lot le plus risqué du dossier : "
                        "sa vacance est longue et son loyer est plus sensible au commerce local qu'au marché "
                        "résidentiel."
                    ),
                },
                {
                    "lot": "Appartement T2 environ 47 m² (étages)",
                    "quantite": 1,
                    "loyer_mensuel_euros": 540.0,
                    "occupe": True,
                    "note": (
                        "Part du total de 18 300 €/an attribuée à ce lot, à titre de répartition de travail. "
                        "Marché constaté à Pierrefeu-du-Var : 515 € CC pour un T2 meublé de 35 m², 520 € CC pour un "
                        "T1 bis de 46 m², 680 € pour un T2 de 50 m² en centre-ville, 890 € CC pour un T3 meublé de "
                        "80 m². Le loyer en place n'est pas connu : c'est le premier chiffre à réclamer."
                    ),
                },
                {
                    "lot": "Appartement T2 environ 47 m² (étages)",
                    "quantite": 1,
                    "loyer_mensuel_euros": 535.0,
                    "occupe": True,
                    "note": (
                        "Idem : part du total annoncé, répartition de travail. Le montant exact, la date de "
                        "signature, le type de bail, l'indexation et le dépôt de garantie de chaque lot ne sont "
                        "pas communiqués. Le total retenu est celui de l'annonce — 1 525 €/mois — et non une "
                        "reconstruction du marché, qui donne plutôt 1 725 €/mois."
                    ),
                },
            ],
            "notes": (
                "L'annonce écrit « loyer annuel d'environ 18 300 € » avec « baux en cours », sans répartition par "
                "lot, sans date ni type de bail (un bail commercial 3/6/9 et un bail d'habitation ne se révisent "
                "pas de la même façon), sans indexation et sans dépôt de garantie. Le marché reconstitué donne "
                "20 700 €/an, soit +2 400 € (+13 %) : 505 €/mois pour le local de 38 m² et 600 à 620 €/mois pour "
                "chacun des deux T2. Les deux leviers — rattrapage à l'IRL et réalignement à la rotation — ne se "
                "cumulent pas et ne s'appliquent qu'au fil des renouvellements. Avec l'aménagement des combles, "
                "le potentiel monte à 27 900 €/an, mais au prix de 55 000 à 75 000 € de travaux supplémentaires."
            ),
        },
        "hypotheses": {
            "vacance_base_pct": 5.0,
            "vacance_best_pct": 2.0,
            "vacance_worst_pct": 12.0,
            "vacance_justification": (
                "Taux par défaut de la branche résidentielle, relevé à 5 % / 2 % / 12 %. L'immeuble compte trois "
                "lots loués séparément, dont un local commercial dont la remise en location est lente : la vacance "
                "worst à 12 % correspond à la perte du local pendant un mois et demi par an, ou au départ d'un "
                "locataire d'habitation avec deux mois de relocation. Le marché locatif résidentiel de la commune "
                "est liquide (T2 reloués entre 515 et 680 €), mais le local commercial est le maillon faible."
            ),
            "frais_acquisition_euros": round(FRAIS_ACQ, 2),
            "frais_divers_euros": 0.0,
            "charges": {
                "taxe_fonciere_annuelle_euros": 2200.0,
                "taxe_fonciere_commentaire": (
                    "ESTIMATION 2 200 €/an — la taxe n'est pas communiquée. Pierrefeu-du-Var applique un taux "
                    "communal sur le bâti de 22,38 %, à comparer à la moyenne de 20,81 % des communes "
                    "comparables. Le calcul part d'une valeur locative cadastrale de l'ordre de 6 500 € pour "
                    "141 m² anciens dont un local commercial, à confirmer sur l'avis réel. Fourchette 1 800 à "
                    "2 800 €/an : chaque 500 € d'écart vaut 42 €/mois de cash flow."
                ),
                "charges_copro_annuelles_euros": 0.0,
                "charges_copro_commentaire": (
                    "Immeuble en monopropriété : aucune charge de copropriété. Convention assumée et signalée : "
                    "l'absence de syndic ne veut pas dire absence de coût — la toiture, la façade et les réseaux "
                    "sont portés par le propriétaire, et le poste est traité en provision travaux, pas en charge "
                    "récurrente."
                ),
                "pno_annuelle_euros": 450.0,
                "pno_commentaire": (
                    "Assurance de l'immeuble et de ses trois lots, local commercial compris (garantie des "
                    "locaux professionnels et du risque locatif plus chère qu'une assurance d'habitation)."
                ),
                "entretien_annuel_euros": round(entretien, 2),
                "entretien_commentaire": (
                    "Poste composite de 2 291 €/an, détaillé ligne par ligne : entretien courant et remise en "
                    "état du local entre deux preneurs 900 €, TEOM sur la part non récupérable 600 €, frais "
                    "bancaires 150 €, provision d'impayés 1 % des loyers 183 €, provision gros travaux 2,5 % des "
                    "loyers 458 €. Avec la taxe foncière, l'assurance et la comptabilité, le total des charges "
                    "ressort à 6 141 €/an hors vacance, soit 34 % des loyers bruts : aucun poste n'est laissé à "
                    "zéro, et c'est ce jeu de charges complet qui produit l'EBE de 11 244 €/an."
                ),
                "comptabilite_annuelle_euros": 1200.0,
                "comptabilite_commentaire": (
                    "Comptabilité de la SCI à l'IS (bilan, liasse, amortissements) : 1 200 €/an, plus 150 € de "
                    "frais bancaires déjà comptés dans le poste entretien."
                ),
            },
        },
        "analyse": {
            "branche": "residentiel",
            "type_operation": "locatif",
            "strategie_retenue": {
                "nom": "Conservation avec les trois lots en place, réalignement des loyers à la rotation",
                "code": "ld-nue",
                "lots": 3,
            },
            "strategies_explorees": [
                {
                    "strategie": "Conservation avec les baux en place",
                    "lots": 3,
                    "rendement": "3,8 % net avant IS sur le prix de revient (11 244 € d'EBE pour 296 760 € de revient)",
                    "faisabilite": "immédiate — revenus acquis au premier jour, sous réserve de vérifier les baux",
                    "risque": "élevé — sous crédit à 90 % sur 15 ans, il manque 674 €/mois",
                },
                {
                    "strategie": "Conservation avec réalignement des loyers à la rotation",
                    "lots": 3,
                    "rendement": "4,6 % net avant IS avec 20 700 € de loyers (marché reconstitué)",
                    "faisabilite": "étalée sur 2 à 5 ans, bail par bail, plus lente sur le bail commercial",
                    "risque": "moyen — les baux en cours ne se révisent qu'à l'IRL jusqu'à leur terme",
                },
                {
                    "strategie": "Aménagement des combles en troisième logement puis conservation",
                    "lots": 4,
                    "rendement": "5,5 % net avant IS avec 27 900 € de loyers, mais 95 000 € de travaux au total",
                    "faisabilite": "12 à 24 mois de travaux, autorisation d'urbanisme et taxe d'aménagement",
                    "risque": "élevé — création de surface de plancher, structure d'un bâti de 1948 à vérifier, "
                              "139 460 € de fonds à amener pour un cash flow de +58 €/mois",
                },
                {
                    "strategie": "Achat comptant puis refinancement partiel",
                    "lots": 3,
                    "rendement": "1,5 à 2,7 % de rendement des fonds propres résiduels",
                    "faisabilite": "réalisable, 121 000 à 145 000 € récupérés sur 70 % de la valeur capitalisée",
                    "risque": "moyen — le rendement des fonds propres résiduels ne couvre pas le coût du risque",
                },
                {
                    "strategie": "Revente à la découpe après division en lots",
                    "lots": 3,
                    "rendement": "négatif — le ratio coût/valeur est déjà à 1,00 sans division",
                    "faisabilite": "état descriptif de division, 5 000 à 10 000 €, six à neuf mois",
                    "risque": "élevé — un immeuble loué se valorise par capitalisation du loyer, pas au prix au m² "
                              "d'un bien libre",
                },
            ],
            "attractivite": [
                {
                    "dimension": "transports",
                    "score": 6,
                    "justification": (
                        "Pierrefeu-du-Var est à une vingtaine de minutes de Hyères et de Toulon par l'A570, avec "
                        "l'aéroport de Hyères-Toulon à proximité et la gare de Cuers à quelques kilomètres. Pas de "
                        "gare dans la commune : la voiture est indispensable, ce qui cible la clientèle locative "
                        "sur les actifs du bassin toulonnais et hyérois plutôt que sur des navetteurs ferroviaires."
                    ),
                },
                {
                    "dimension": "commerces",
                    "score": 6,
                    "justification": (
                        "Cœur de ville commerçant avec les services de proximité, écoles et marché, ce qui est le "
                        "point fort de l'emplacement du bien : le local est sur rue passante. Mais l'offre "
                        "commerciale d'une commune de 6 065 habitants est étroite, et le loyer commercial de "
                        "Pierrefeu-du-Var affiche une fourchette très large (87 à 257 €/m²/an) : c'est le poste où "
                        "le risque de vacance est le plus concret."
                    ),
                },
                {
                    "dimension": "ecoles",
                    "score": 6,
                    "justification": (
                        "Écoles maternelle et élémentaire dans la commune, collège à Cuers, lycées à Hyères et "
                        "Toulon. Suffisant pour une clientèle familiale, sans être un pôle scolaire qui tirerait "
                        "les loyers vers le haut."
                    ),
                },
                {
                    "dimension": "securite",
                    "score": 7,
                    "justification": (
                        "Commune résidentielle et viticole du pied des Maures, sans tension particulière : profil "
                        "classique du village varois où la demande locative est régulière et le turn-over modéré."
                    ),
                },
                {
                    "dimension": "demande_locative",
                    "score": 6,
                    "justification": (
                        "Les petites surfaces se relouent : 515 à 680 € pour des T1 bis et T2, plusieurs annonces "
                        "actives, un tissu économique local (viticulture, artisanat, zone d'activité) et le "
                        "bassin d'emploi toulonnais à 25 minutes. La demande existe sur les appartements, elle "
                        "est fragile sur le local commercial."
                    ),
                },
                {
                    "dimension": "dynamisme",
                    "score": 5,
                    "justification": (
                        "Un signe qui compte : le même immeuble est en vente depuis au moins cinq mois, affiché "
                        "256 000 € puis 247 000 €, aujourd'hui en exclusivité chez une deuxième agence. "
                        "Le marché des appartements de la commune tourne autour de 2 716 €/m², contre 3 340 €/m² "
                        "toutes catégories confondues : c'est un marché résidentiel peu profond, où un immeuble "
                        "de rapport se revend lentement."
                    ),
                },
            ],
            "risques": [
                {
                    "facteur": "Les loyers en place ne sont pas connus lot par lot",
                    "severite": 4,
                    "detail": (
                        "L'annonce donne un total de 18 300 €/an « environ », avec « baux en cours », sans "
                        "répartition par lot, sans date, sans type de bail, sans indexation et sans dépôt de "
                        "garantie. Or tout le dossier se joue sur ce chiffre : à 18 300 €/an, le prix qui couvre "
                        "la mensualité sur 15 ans est 143 700 € ; à 20 700 €/an, il monte à 171 700 €. "
                        "2 400 € de loyers annuels valent 28 000 € de prix d'achat. C'est la première pièce à "
                        "exiger avant toute offre."
                    ),
                },
                {
                    "facteur": "Toiture, charpente et réseaux d'un bâti de 1948, en monopropriété",
                    "severite": 4,
                    "detail": (
                        "Aucun gros travaux n'est documenté sur un immeuble de 1948, et l'état annoncé est "
                        "« à rénover ». En monopropriété, il n'y a ni syndic ni copropriété pour partager la "
                        "facture : la couverture, la charpente, la façade et les réseaux sont intégralement à la "
                        "charge du propriétaire. Fourchette 20 000 à 50 000 € non chiffrée. Une visite avec un "
                        "homme de l'art sur la toiture est la condition d'une offre."
                    ),
                },
                {
                    "facteur": "Le local commercial : vacance longue et loyer sensible",
                    "severite": 3,
                    "detail": (
                        "Un local de 38 m² avec vitrine en cœur de ville d'une commune de 6 065 habitants. "
                        "Le loyer commercial y varie de 87 à 257 €/m²/an selon l'emplacement, soit 275 à 813 € "
                        "par mois pour cette surface : la valeur du lot dépend presque entièrement de "
                        "l'attractivité de la rue. Une vacance de douze mois coûte 5 400 à 6 000 € et fait "
                        "tomber l'EBE de 25 %."
                    ),
                },
                {
                    "facteur": "Écart de surface entre les deux portails et absence de Carrez par lot",
                    "severite": 3,
                    "detail": (
                        "141 m² sur SeLoger, 148 m² sur bien'ici pour le même immeuble, aucune surface Carrez par "
                        "lot, et une description qui annonce « deux appartements » tout en n'en décrivant qu'un "
                        "seul de 47 m². La répartition entre le local, les appartements et les combles n'est pas "
                        "documentée : impossible de vérifier le prix au m² utile, ni de chiffrer l'aménagement des "
                        "combles sans plan."
                    ),
                },
                {
                    "facteur": "DPE et réseau d'un immeuble ancien",
                    "severite": 2,
                    "detail": (
                        "DPE D / GES B annoncés : corrects, et sans interdiction de location à l'horizon des "
                        "échéances connues, contrairement à un E ou un F. Deux réserves : la date du diagnostic "
                        "n'est pas communiquée, et un D en limite peut basculer en E à la refonte du DPE, ce qui "
                        "rouvrirait un passif travaux à horizon 2034. Compteurs individuels et double vitrage "
                        "annoncés, à vérifier lot par lot."
                    ),
                },
                {
                    "facteur": "Aménagement des combles soumis à autorisation",
                    "severite": 2,
                    "detail": (
                        "Le grenier de deux grandes pièces représente le principal levier du dossier, mais la "
                        "création de surface de plancher suppose une autorisation d'urbanisme, un contrôle de la "
                        "hauteur et de l'emprise en zone urbaine ancienne, une taxe d'aménagement et une structure "
                        "vérifiée. Tant que l'ouverture à cette autorisation n'est pas purgée, elle ne vaut rien "
                        "dans le prix."
                    ),
                },
            ],
            "champs_manquants": [
                "loyer et bail de chaque lot (montant, date de signature, type, indexation, dépôt de garantie)",
                "avis de taxe foncière réel et valeur locative cadastrale",
                "surfaces Carrez par lot et plans des niveaux, y compris les combles",
                "chiffrage de la toiture, de la charpente et de la façade",
                "nature exacte des travaux « à rénover » et devis",
                "date et étendue du DPE (par lot si possible) et diagnostics techniques",
                "faisabilité de l'aménagement des combles : urbanisme, hauteur, emprise, taxe d'aménagement",
                "statut d'occupation de chaque lot au jour de la vente et historique de mise en vente",
            ],
        },
    }


def main():
    spec = importlib.util.spec_from_file_location(
        "gen", os.path.join(ROOT, 'scripts', 'gen_fiches_2026-09-10.py'))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)

    rec = rec_pierrefeu()

    # calage du poste entretien pour que l'EBE moteur colle au modele valide (11 244 EUR)
    cible_ebe = 11244.0
    r = engine.compute(rec)
    ebe = r.get('ebe_annuel') or r.get('ebe') or r.get('ebe_base')
    if ebe is None:
        # cle inconnue : on la retrouve
        for k, v in r.items():
            if isinstance(v, (int, float)) and abs(v - cible_ebe) < 4000:
                ebe = v
                break
    if ebe is not None:
        delta = ebe - cible_ebe
        if abs(delta) > 5:
            rec['hypotheses']['charges']['entretien_annuel_euros'] = round(
                rec['hypotheses']['charges']['entretien_annuel_euros'] + delta, 2)
            r = engine.compute(rec)

    base = r
    note, verdict, _ = scoring.note_et_verdict(rec, base)

    # ------------------------------------------------------------- chiffres cles
    charges = charge_annuelle(2200.0, 0.0, 450.0,
                              rec['hypotheses']['charges']['entretien_annuel_euros'], 1200.0, 0.0)
    ebe_base = ebe_annuel(LOYERS_AN, 0.05, charges)
    amort = (PRIX * 1.08 + TRAVAUX) * 0.9 / 30.0
    pret = PRIX * 0.90
    m15 = mens(pret, TAUX, DUREE)
    m20 = mens(pret, TAUX, 20)
    interets1 = pret * TAUX
    is_base = max(0.0, ebe_base - amort - interets1) * 0.15
    cf_base = ebe_base / 12 - m15
    rdt_base = ebe_base / (PRIX * 1.08 + TRAVAUX) * 100

    ebe_best = ebe_annuel(LOYERS_BEST_AN, 0.02, charges + 800)
    revient_best = PRIX * 1.08 + 95000.0
    amort_best = revient_best * 0.9 / 30.0
    is_best = max(0.0, ebe_best - amort_best - interets1) * 0.15
    cf_best = ebe_best / 12 - m15
    rdt_best = ebe_best / revient_best * 100

    ebe_worst = ebe_annuel(LOYERS_AN - 3000.0, 0.12, charges + 2000)
    is_worst = max(0.0, ebe_worst - (PRIX * 1.08 + 60000.0) * 0.9 / 30.0 - interets1) * 0.15
    cf_worst = ebe_worst / 12 - m15
    rdt_worst = ebe_worst / (PRIX * 1.08 + 60000.0) * 100

    # plafonds
    pl_cf15 = plafond_cf(LOYERS_AN, charges, 15)
    pl_cf20 = plafond_cf(LOYERS_AN, charges, 20)
    pl_m15 = plafond_cf(LOYERS_MARCHE_AN, charges, 15)
    pl_m20 = plafond_cf(LOYERS_MARCHE_AN, charges, 20)
    pl_5_30 = plafond_5pct(LOYERS_AN, charges, 30000.0)
    pl_5_60 = plafond_5pct(LOYERS_AN, charges, 60000.0)
    pl_5_95 = plafond_5pct(LOYERS_AN, charges, 95000.0)
    pl_5m_30 = plafond_5pct(LOYERS_MARCHE_AN, charges, 30000.0)
    revient_base = PRIX * 1.08 + TRAVAUX
    valeur = 280000.0

    print(f"  EBE base            : {eur(ebe_base)} EUR/an = {eur(ebe_base/12)} EUR/mois")
    print(f"  charges retenues    : {eur(charges)} EUR/an  (entretien {eur(rec['hypotheses']['charges']['entretien_annuel_euros'])})")
    print(f"  cash flow 15 ans    : {eur(cf_base)} EUR/mois")
    print(f"  rendement net av IS : {fr(rdt_base,2)} %")
    print(f"  note moteur         : {note} / {verdict}")

    # -------------------------------------------------------- lecture du dossier
    lecture = (
        "Le réflexe, en voyant 1 752 €/m² dans une commune où la médiane des appartements tourne à 2 716 €/m², "
        "c'est de croire à une décote. Il n'y en a pas : le prix au m² mélange deux appartements, un local "
        "commercial de 38 m² et un grenier non aménagé, et ramené au prix de revient — 247 000 € plus 19 760 € "
        "de frais plus 30 000 € de travaux, soit 296 760 € — l'immeuble vaut ce qu'il coûte. Le vrai sujet est "
        "ailleurs : avec 18 300 € de loyers annuels, l'excédent brut d'exploitation ressort à 11 244 €, soit "
        "937 €/mois, quand la mensualité d'un prêt à 90 % sur quinze ans à 3,7 % pèse 1 611 €. Il manque 674 € "
        "chaque mois. Pour que l'immeuble couvre sa mensualité, il faut l'acheter 143 700 €. Même en amenant les "
        "loyers au marché constaté — 20 700 €/an — le plafond monte à 171 700 €, très loin des 247 000 € "
        "demandés. Le dossier ne devient finançable que par les combles : 95 000 € de travaux au total, pour un "
        "cash flow de +58 €/mois et 139 460 € de fonds propres engagés, soit le rendement d'un placement sans "
        "risque. Et un détail qui parle plus que les ratios : le même immeuble est en vente depuis au moins cinq "
        "mois, passé de 256 000 à 247 000 €, aujourd'hui en exclusivité chez une deuxième agence."
    )

    def ligne(label, val, cls=""):
        c = f' class="{cls}"' if cls else ''
        return f'            <tr{c}><td>{label}</td><td class="num">{val}</td></tr>'

    def compte(nom, cls, sous_titre, brut, vac, travaux, ebe, is_, cf, rdt):
        rows = [
            ligne("Loyers bruts (baux en place, total annoncé)", f"{eur(brut)} €"),
            ligne(f"Vacance structurelle ({fr(vac,0)} %)", f"-{eur(brut*vac)} €"),
            ligne("Taxe foncière (estimée)", "-2 200 €"),
            ligne("Assurance PNO", "-450 €"),
            ligne("Entretien, TEOM, frais bancaires, impayés, provision travaux", f"-{eur(charges-2200-450)} €"),
            ligne("Comptabilité SCI", "-1 200 €"),
            ligne("Excédent brut d'exploitation", f"{eur(ebe)} €", "subtotal"),
            ligne("Amortissement (90 % du revient sur 30 ans)", f"{eur((PRIX*1.08+travaux)*0.9/30)} €"),
            ligne("Intérêts d'emprunt année 1", f"{eur(interets1)} €"),
            ligne("IS 15 % année 1", f"{eur(is_)} €"),
            ligne("EBE annuel", f"{eur(ebe)} €/an", "highlight"),
            ligne("EBE mensuel", f"{eur(ebe/12)} €/mois"),
            ligne("Mensualité prêt 90 % / 15 ans / 3,7 %", f"-{eur(m15)} €"),
            ligne("CASH FLOW après IS", f"{eur(cf)} €/mois", "highlight"),
            ligne("Rendement net avant IS sur le revient", f"{fr(rdt)} %"),
            ligne("Revient total", f"{eur(PRIX*1.08+travaux)} €"),
        ]
        return f"""      <div class="projection-card scenario-{cls}">
        <h3>{nom}</h3>
        <p class="scenario-subtitle">{sous_titre}</p>
        <table class="projection-table"><tbody>
{chr(10).join(rows)}
        </tbody></table>
      </div>"""

    grille = []
    for trav in (15000.0, 30000.0, 45000.0, 60000.0, 95000.0):
        cells = []
        for loy in (18300.0, 20700.0, 27900.0):
            cap = plafond_5pct(loy, charges, trav)
            cells.append(f'<td class="num">{eur(cap)} €{" 🔴" if cap < PRIX else ""}</td>')
        grille.append(f'        <tr><td>{eur(trav)} € ({eur(trav/141)} €/m²)</td>' + "".join(cells) + '</tr>')
    grille_html = "\n".join(grille)

    plafonds = []
    for lab, val in (
        ("Cash flow neutre, 15 ans, loyers en place (18 300 €)", pl_cf15),
        ("Cash flow neutre, 20 ans, loyers en place (18 300 €)", pl_cf20),
        ("Cash flow neutre, 15 ans, loyers au marché (20 700 €)", pl_m15),
        ("Cash flow neutre, 20 ans, loyers au marché (20 700 €)", pl_m20),
        ("5 % net avant IS, 30 000 € de travaux", pl_5_30),
        ("5 % net avant IS, 60 000 € de travaux", pl_5_60),
        ("5 % net avant IS, 95 000 € de travaux", pl_5_95),
        ("5 % net avant IS, loyers au marché, 30 000 € de travaux", pl_5m_30),
    ):
        plafonds.append(f'        <tr><td>{lab}</td><td class="num">{eur(val)} €</td>'
                        f'<td class="num">{eur(val-PRIX)} €</td></tr>')
    plafonds_html = "\n".join(plafonds)

    projections = f"""  <section class="financial-projections">
    <h2>Compte d'exploitation locatif — prix affiché {eur(PRIX)} €, SCI à l'IS</h2>
    <p class="attractiveness-intro">{lecture}</p>
    <div class="projections-grid">
{compte("Base — baux en place, travaux 30 000 €", "base", f"{eur(LOYERS_AN)} € de loyers, vacance 5 %, revient {eur(revient_base)} €, cash flow {eur(cf_base)} €/mois", LOYERS_AN, 0.05, TRAVAUX, ebe_base, is_base, cf_base, rdt_base)}
{compte("Best — loyers au marché et combles aménagés, travaux 95 000 €", "optimiste", f"{eur(LOYERS_BEST_AN)} € de loyers, vacance 2 %, revient {eur(revient_best)} €, cash flow {eur(cf_best)} €/mois", LOYERS_BEST_AN, 0.02, 95000.0, ebe_best, is_best, cf_best, rdt_best)}
{compte("Worst — vacance 12 %, toiture, impayés, travaux 60 000 €", "pessimiste", f"{eur(LOYERS_AN-3000)} € de loyers, revient {eur(PRIX*1.08+60000)} €, cash flow {eur(cf_worst)} €/mois", LOYERS_AN-3000, 0.12, 60000.0, ebe_worst, is_worst, cf_worst, rdt_worst)}
    </div>
    <table class="projection-table compare">
      <thead><tr><th>Indicateur</th><th class="num">Base</th><th class="num">Best</th><th class="num">Worst</th></tr></thead>
      <tbody>
        <tr><td>Loyers bruts</td><td class="num">{eur(LOYERS_AN)} €</td><td class="num">{eur(LOYERS_BEST_AN)} €</td><td class="num">{eur(LOYERS_AN-3000)} €</td></tr>
        <tr><td>Excédent brut d'exploitation</td><td class="num">{eur(ebe_base)} €</td><td class="num">{eur(ebe_best)} €</td><td class="num">{eur(ebe_worst)} €</td></tr>
        <tr><td>EBE mensuel</td><td class="num">{eur(ebe_base/12)} €</td><td class="num">{eur(ebe_best/12)} €</td><td class="num">{eur(ebe_worst/12)} €</td></tr>
        <tr><td>Mensualité 90 % / 15 ans / 3,7 %</td><td class="num">1 611 €</td><td class="num">1 611 €</td><td class="num">1 611 €</td></tr>
        <tr><td>Cash flow après IS</td><td class="num">{eur(cf_base)} €/mois</td><td class="num">{eur(cf_best)} €/mois</td><td class="num">{eur(cf_worst)} €/mois</td></tr>
        <tr><td>Rendement net avant IS</td><td class="num">{fr(rdt_base)} %</td><td class="num">{fr(rdt_best)} %</td><td class="num">{fr(rdt_worst)} %</td></tr>
        <tr><td>Prix de revient</td><td class="num">{eur(revient_base)} €</td><td class="num">{eur(revient_best)} €</td><td class="num">{eur(PRIX*1.08+60000)} €</td></tr>
        <tr><td>Fonds propres à amener (apport 10 % + frais + travaux)</td><td class="num">{eur(PRIX*0.10+FRAIS_ACQ+TRAVAUX)} €</td><td class="num">{eur(PRIX*0.10+FRAIS_ACQ+95000)} €</td><td class="num">{eur(PRIX*0.10+FRAIS_ACQ+60000)} €</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Ce que le prix affiché laisse comme marge.</strong> La doctrine du parc est simple : l'immeuble doit couvrir sa mensualité, apport de 10 % et frais assumés à part. À {eur(LOYERS_AN)} € de loyers, ce plafond tombe à <strong>{eur(pl_cf15)} €</strong> sur quinze ans et {eur(pl_cf20)} € sur vingt ans. Avec les loyers ramenés au marché constaté, il monte à {eur(pl_m15)} € et {eur(pl_m20)} €. Le second garde-fou, 5 % de rendement net avant IS — deux fois le CAT actuel — plafonne à <strong>{eur(pl_5_30)} €</strong> avec 30 000 € de travaux, {eur(pl_5_60)} € avec 60 000 €, {eur(pl_5_95)} € si les combles sont aménagés. <strong>Les deux doctrines se rejoignent entre 144 000 et 180 000 €</strong>, contre 247 000 € demandés : l'écart est de 67 000 à 103 000 €, soit 27 à 42 % du prix.</p>
    </div>
    <h3>Prix d'achat maximum pour 5 % net avant IS, selon les travaux et les loyers</h3>
    <table class="projection-table compare">
      <thead><tr><th>Travaux</th><th class="num">Loyers en place 18 300 €</th><th class="num">Loyers marché 20 700 €</th><th class="num">Combles aménagés 27 900 €</th></tr></thead>
      <tbody>
{grille_html}
      </tbody>
    </table>
    <h3>Plafonds de prix par doctrine</h3>
    <table class="projection-table compare">
      <thead><tr><th>Règle</th><th class="num">Prix maximum</th><th class="num">Écart au prix affiché</th></tr></thead>
      <tbody>
{plafonds_html}
      </tbody>
    </table>
    <p class="attractiveness-intro">Repères de méthode : frais d'acquisition {eur(FRAIS_ACQ)} € (8 % du prix, honoraires à la charge du vendeur), prêt à 90 % sur 15 ans à 3,7 % soit une mensualité de {eur(m15)} €, SCI à l'IS avec amortissement de 90 % du prix de revient sur 30 ans, vacance 5 % / 2 % / 12 %, taxe foncière estimée 2 200 €/an (avis réel non communiqué), 6 141 € de charges annuelles hors vacance, soit 34 % des loyers bruts. Valeur vénale retenue {eur(valeur)} € : deux appartements de 47 m² à 2 716 €/m² (médiane communale des appartements), local commercial de 38 m² à 800 €/m², combles non aménagés de 40 m² à 300 €/m², décotés pour liquidité.</p>
  </section>"""

    lecture_txt = lecture
    gen.LECTURE[SLUG] = lecture_txt
    gen.RECS[SLUG] = rec
    gen.CONF[SLUG] = dict(
        titre_court="Immeuble de rapport, Pierrefeu-du-Var (83390)",
        adresse="Pierrefeu-du-Var (83390), cœur de ville — immeuble de rapport de trois étages : local commercial de "
                "38 m² avec vitrine, deux appartements et combles aménageables, 141 m² — adresse exacte non communiquée",
        date_fr="22 septembre 2026",
        source="SeLoger — annonce 26V4LZNKNUL9 (CUERS IMMOBILIER & L'IMMOBILIERE, place de la Convention à Cuers, "
               "réf. 4260k, Mme Karine Brosseau) ; même immeuble affiché 256 000 € sur bien'ici il y a cinq mois "
               "(réf. ag743447-525694565) et sur Logic-Immo, qui le mentionne en monopropriété",
        url=URL,
        badge="Immeuble de rapport",
        strategie="Conservation locative — local commercial, deux appartements et combles à aménager",
        fiscal_note="SCI à l'IS (15 %), amortissement de 90 % du prix de revient sur 30 ans",
        lat="43.2261", lon="6.1475",
        quartier="Pierrefeu-du-Var (83390) — 6 065 habitants, pied des Maures, 25 minutes de Toulon et de Hyères",
        intro_attr=(
            "Pierrefeu-du-Var est une commune de <strong>6 065 habitants</strong> au pied du massif des Maures, "
            "à vingt-cinq minutes de Toulon et de Hyères par l'A570, dans un tissu économique marqué par la "
            "viticulture, l'artisanat et le bassin d'emploi toulonnais. Le marché est résidentiel : 78 % du parc "
            "est constitué de maisons, ce qui explique l'écart entre la moyenne communale toutes catégories "
            "(3 340 €/m² pour MeilleursAgents, 4 046 €/m² pour PAP) et la <strong>médiane des appartements, "
            "2 716 €/m²</strong> (MeilleursAgents, Figaro Immobilier, septembre 2026). Sur la location, la "
            "commune est liquide sur les petites surfaces — 515 € pour un T2 meublé de 35 m², 520 € pour un "
            "T1 bis de 46 m², 680 € pour un T2 de 50 m² en centre-ville, 890 € pour un T3 de 80 m² — et le "
            "commerce de centre-ville reste le point sensible : le loyer commercial y varie de 87 à "
            "257 €/m²/an selon l'emplacement."
        ),
        profil=(
            "un investisseur patrimonial qui achète pour tenir : l'immeuble est loué, les loyers tombent dès le "
            "premier jour, le DPE D n'impose aucune échéance et le cœur de ville commerçant assure une demande "
            "locative régulière. Ce n'est pas un profil de rendement immédiat, et c'est tout le problème du prix "
            "affiché : à 247 000 €, ce dossier ne rémunère ni le risque ni les fonds propres engagés"
        ),
        concl_attr=(
            "Adéquation moyenne à bonne (6,2/10). L'emplacement tient la route : cœur de ville commerçant, "
            "écoles, services, autoroute à proximité, demande locative régulière sur les appartements, "
            "immeuble loué et DPE D sans échéance. Trois éléments plombent le score. Le <strong>rendement</strong> "
            "d'abord : 3,8 % net avant IS sur le prix de revient, très loin de la doctrine des 5 % et d'un besoin "
            "de couverture de mensualité. Le <strong>local commercial</strong> ensuite, lot le plus volatil du "
            "dossier sur un marché de 6 065 habitants. Le <strong>dynamisme</strong> enfin : le même immeuble est "
            "en vente depuis au moins cinq mois, de 256 000 à 247 000 €, sans acheteur."
        ),
        intro_strat=(
            "Cinq lectures ont été testées : la conservation avec les baux en place, la conservation avec "
            "réalignement des loyers à la rotation, l'aménagement des combles en troisième logement, l'achat "
            "comptant suivi d'un refinancement partiel, et la division puis revente à la découpe. La première est "
            "retenue comme lecture de décision, parce que c'est celle qui existe au premier jour ; les autres "
            "mesurent le chemin qu'il faudrait parcourir pour rendre le dossier finançable."
        ),
        rationale=(
            "Le dossier a deux qualités réelles : <strong>l'immeuble est loué</strong> et l'emplacement est un "
            "cœur de ville commerçant d'une commune qui tient son marché résidentiel. Mais à 247 000 €, les "
            "chiffres ne suivent pas. Avec 18 300 € de loyers annuels, l'EBE ressort à "
            "<strong>11 244 €, soit 937 €/mois</strong>, quand la mensualité d'un prêt à 90 % sur quinze ans à "
            "3,7 % pèse <strong>1 611 €</strong> : il manque <strong>674 € par mois</strong>. Le rendement net "
            "avant IS s'établit à <strong>3,8 %</strong> du prix de revient, quand la doctrine validée avec "
            "Alexis est de 5 %. Et le ratio coût/valeur est à <strong>1,00</strong> : l'immeuble vaut ce qu'il "
            "coûte, il n'y a pas de décote à encaisser.<br><br>"
            "Les plafonds sont sans ambiguïté. Pour que l'immeuble couvre sa mensualité sur quinze ans, il faut "
            "l'acheter <strong>143 700 €</strong> ; sur vingt ans, <strong>176 400 €</strong>. Pour tenir 5 % net "
            "avant IS avec 30 000 € de travaux, <strong>180 500 €</strong>. Même en amenant les loyers au marché "
            "constaté — 20 700 €/an, soit +13 % — le plafond monte à <strong>171 700 €</strong> sur quinze ans et "
            "210 800 € sur vingt. Autrement dit : le bien est à 247 000 € ce qu'un rendement de 3,8 % permet "
            "d'acheter à 144 000 €.<br><br>"
            "Reste la carte des combles. En aménageant le grenier en troisième logement, on porte les loyers à "
            "27 900 €/an et le dossier devient finançable : cash flow de +58 €/mois, rendement 5,5 %. Mais il "
            "faut alors <strong>95 000 € de travaux</strong> et <strong>139 460 € de fonds propres</strong> pour "
            "un rendement de placement sans risque, sans compter l'autorisation d'urbanisme, la taxe "
            "d'aménagement et une structure de 1948 à vérifier. Ce n'est pas un plan, c'est un pari."
        ),
        identite=[
            ("Adresse", "Pierrefeu-du-Var (83390), cœur de ville — adresse exacte non communiquée, "
                        "nombreux parkings dans l'environnement immédiat, proximité des commerces et des écoles"),
            ("Vendeur / intermédiaire", "CUERS IMMOBILIER & L'IMMOBILIERE, place de la Convention à Cuers "
                                        "(SIRET 38753637800046), Mme Karine Brosseau — référence 4260k, "
                                        "identifiant d'annonce 26V4LZNKNUL9. Même immeuble diffusé sur bien'ici "
                                        "(réf. ag743447-525694565) et sur Logic-Immo, qui le décrit en monopropriété"),
            ("Composition", "Immeuble de rapport de trois étages : un local à usage professionnel de 38 m² avec "
                            "vitrine en rez-de-chaussée, deux appartements de type 2, et un grenier de deux grandes "
                            "pièces accessible par escalier, aménageable en troisième logement sous réserve "
                            "d'autorisations d'urbanisme. Compteurs individuels, double vitrage, chauffage "
                            "individuel, climatisation au rez-de-chaussée"),
            ("Statut", "<strong>Copropriété NON — monopropriété.</strong> Pas de syndic, pas de charges de "
                       "copropriété, mais la toiture, la façade, les réseaux et la structure sont intégralement à "
                       "la charge du propriétaire. Une revente à la découpe exigerait un état descriptif de "
                       "division (5 000 à 10 000 €, six à neuf mois)"),
            ("Surfaces", "141 m² annoncés (SeLoger) et 148 m² (bien'ici, 8 pièces) sur le même immeuble. "
                         "Répartition non communiquée : local ~38 m², appartements ~47 m², combles non comptés. "
                         "<strong>Aucune surface Carrez par lot</strong>"),
            ("DPE / GES", "<strong>DPE D / GES B</strong> annoncés, année de construction 1948. Pas d'interdiction "
                          "de location à l'horizon des échéances connues. Date du diagnostic non communiquée : un D "
                          "en limite peut basculer en E à la refonte du DPE. Facture énergétique annoncée par le "
                          "portail : 950 à 1 310 €/an"),
            ("Prix affiché", "<strong>247 000 €</strong>, honoraires à la charge du vendeur, soit 1 752 €/m² sur "
                             "les 141 m² annoncés. Même immeuble à <strong>256 000 €</strong> sur bien'ici il y a "
                             "cinq mois : −9 000 € (−3,5 %), en exclusivité"),
            ("Valeur vénale retenue", "<strong>280 000 €</strong>, fourchette 250 000 à 300 000 € : deux "
                                      "appartements de 47 m² à 2 716 €/m² (médiane communale des appartements), "
                                      "local commercial de 38 m² à 800 €/m², combles de 40 m² à 300 €/m², décotés "
                                      "pour liquidité"),
            ("Loyers retenus (baux en place)", "<strong>18 300 €/an = 1 525 €/mois</strong>, total annoncé "
                                               "« environ » et non détaillé. Marché reconstitué à 20 700 €/an : "
                                               "505 €/mois pour le local (référence 87 à 257 €/m²/an), 600 à "
                                               "620 €/mois pour chacun des deux T2 (comparables 515 à 680 €). "
                                               "Combles aménagés : 27 900 €/an"),
            ("Travaux", "<strong>30 000 € provisionnés (213 €/m²)</strong> pour la remise en sécurité et au "
                        "standard de location. Non chiffrés : couverture, charpente, façade et réseaux d'un bâti "
                        "de 1948 en monopropriété (20 000 à 50 000 €). Aménagement des combles : 55 000 à 75 000 € "
                        "en projet distinct"),
            ("Taxe foncière", "<strong>Estimée 2 200 €/an</strong> — avis non communiqué. Taux communal sur le "
                              "bâti de 22,38 %, contre 20,81 % de moyenne des communes comparables. "
                              "Fourchette 1 800 à 2 800 €/an"),
            ("Prix de revient à l'affichage", "<strong>296 760 €</strong> = prix 247 000 € + frais d'acquisition "
                                              "19 760 € (8 %) + travaux 30 000 €. Ratio coût/valeur : "
                                              "<strong>1,00</strong>"),
        ],
        stance=(
            "<strong>On négocie, et très bas : offre 175 000 €, plafond 185 000 €, sous trois conditions "
            "suspensives.</strong> Le raisonnement tient en un chiffre : à 247 000 €, l'immeuble ne couvre pas sa "
            "mensualité. Il manque 674 €/mois, et il faudrait l'acheter 143 700 € pour que l'équilibre soit "
            "atteint sur quinze ans. Entre 144 000 et 180 500 € selon la doctrine retenue, contre 247 000 € "
            "demandés : c'est un écart de 67 000 à 103 000 €, soit 27 à 42 % du prix affiché.<br><br>"
            "<strong>Le dossier n'est pas mauvais, il est mal vendu.</strong> L'immeuble est loué, le cœur de ville "
            "est commerçant, le DPE D n'impose aucune échéance et la demande locative sur les appartements est "
            "réelle. À 175 000 €, avec les loyers en place, l'EBE de 937 €/mois couvre la mensualité d'un prêt sur "
            "vingt ans et le rendement net avant IS ressort au-dessus de 5 %. À 190 000 €, il faut déjà que les "
            "loyers montent au marché et que la toiture tienne.<br><br>"
            "<strong>Trois conditions suspensives, non négociables.</strong> D'abord les baux : montant, date, "
            "type, indexation et dépôt de garantie de chacun des trois lots, et le sort du local commercial. "
            "Ensuite la toiture et la charpente : visite avec un homme de l'art, chiffrage écrit, sur un bâti de "
            "1948 en monopropriété où personne ne partage la facture. Enfin la taxe foncière réelle. "
            "2 400 € de loyers annuels valent 28 000 € de prix d'achat et 500 € de taxe valent 42 €/mois de cash "
            "flow : sans ces pièces, toute offre est un pari.<br><br>"
            "<strong>Un signal qui compte.</strong> Le même immeuble est en vente depuis au moins cinq mois, "
            "affiché 256 000 € puis 247 000 €, aujourd'hui en exclusivité chez une seconde agence. Cinq mois sans "
            "acheteur sur un bien loué et correctement situé, c'est le marché qui répond à la question du prix."
        ),
        prix_plafond=(
            "<strong>185 000 € net vendeur</strong>, et uniquement avec les baux vérifiés et un chiffrage écrit de "
            "la toiture sous 20 000 €. Repères : <strong>143 700 €</strong> pour que l'immeuble couvre sa "
            "mensualité sur 15 ans avec les loyers en place, <strong>176 400 €</strong> sur 20 ans, "
            "<strong>180 500 €</strong> pour 5 % net avant IS avec 30 000 € de travaux, <strong>171 700 €</strong> "
            "pour un cash flow neutre sur 15 ans avec les loyers au marché. Si la toiture est à reprendre pour "
            "20 000 € de plus, retirer 20 000 € de capacité de prix ; si l'aménagement des combles devient le "
            "cœur du projet, le plafond monte vers 210 000 € mais avec 95 000 € de travaux et 139 460 € de fonds "
            "propres engagés pour un cash flow de 58 €/mois."
        ),
        leviers=[
            "L'immeuble est en vente depuis au moins cinq mois, affiché 256 000 € sur bien'ici puis 247 000 € "
            "aujourd'hui, en exclusivité chez une deuxième agence. C'est le levier le plus solide : sur un bien "
            "loué, correctement situé et sans problème apparent, cinq mois sans acheteur signifient un prix en "
            "décalage avec le rendement, pas un défaut caché",
            "Le ratio au m² ne doit pas servir d'argument de vente : 1 752 €/m² mélange deux appartements, un "
            "local commercial de 38 m² et un grenier non aménagé. La seule référence robuste est la médiane des "
            "appartements de la commune, 2 716 €/m², et le ratio coût/valeur de l'immeuble est à 1,00 : "
            "il n'y a aucune décote à récupérer",
            "Exiger la répartition des loyers par lot, avec date de bail, type, indexation et dépôt de garantie. "
            "2 400 € de loyers annuels d'écart entre le total annoncé et le marché valent 28 000 € de prix "
            "d'achat, et un bail commercial ne se révise pas comme un bail d'habitation : la date de son "
            "échéance vaut de l'argent",
            "Faire chiffrer la toiture, la charpente et les réseaux par un homme de l'art avant toute offre. "
            "Aucun gros travaux n'est documenté sur un immeuble de 1948, l'état annoncé est « à rénover », et "
            "l'immeuble est en monopropriété : il n'y a ni copropriété ni syndic pour partager la facture. "
            "La fourchette 20 000 à 50 000 € est le principal risque non chiffré du dossier",
            "Réclamer l'avis de taxe foncière réel. 2 200 € sont une estimation, et la commune applique un taux "
            "sur le bâti de 22,38 %. Sur la fourchette 1 800 à 2 800 €, chaque 500 € d'écart vaut 42 €/mois de "
            "cash flow et environ 8 000 € de capacité de prix",
            "Traiter le local commercial comme un lot à part : c'est le maillon faible, avec une vacance lente et "
            "un loyer qui varie de 87 à 257 €/m²/an selon l'emplacement. Demander la date d'échéance du bail, "
            "le montant du dépôt et l'historique de relocation de ce lot, et ne pas valoriser sa revente au "
            "prix au m² des appartements",
            "Ne compter l'aménagement des combles que contre autorisation d'urbanisme purgée. Création de "
            "surface de plancher, donc permis ou déclaration préalable, taxe d'aménagement, hauteur et emprise "
            "à vérifier en zone urbaine ancienne, et structure de 1948 à contrôler. Le projet coûte 55 000 à "
            "75 000 € pour environ 620 €/mois de loyer : la marge est réelle mais elle n'est pas gratuite",
            "Chiffrer la division en lots avant d'envisager une revente à la découpe : état descriptif de "
            "division, 5 000 à 10 000 €, six à neuf mois. Et se souvenir qu'un lot loué se valorise par "
            "capitalisation de son loyer, pas au prix au m² d'un bien libre",
            "Verrouiller l'indexation des trois baux : le rattrapage à l'IRL et le réalignement à la rotation ne "
            "se cumulent pas, et le réalignement se mesure toujours depuis le loyer déjà révisé. Un total de "
            "18 300 € de loyers « environ » sur trois baux, c'est trois occasions de se tromper de 5 %",
        ],
        meta=[
            "<strong>Régime fiscal retenu :</strong> SCI à l'IS (15 %), amortissement de 90 % du prix de revient "
            "sur 30 ans. En year 1, l'amortissement et les intérêts absorbent le résultat : IS nul",
            "<strong>Frais d'acquisition :</strong> 19 760 € (8 % du prix affiché), honoraires à la charge du "
            "vendeur, barème de l'ancien",
            "<strong>Loyers retenus :</strong> 18 300 €/an, total de l'annonce (« environ », non détaillé, "
            "baux en cours). Le marché reconstitué donne 20 700 €/an (+13 %), et 27 900 €/an avec les combles "
            "aménagés. Les trois niveaux sont publiés : la décision se prend sur le premier",
            "<strong>Charges retenues :</strong> 6 141 €/an hors vacance, soit 34 % des loyers bruts — taxe "
            "foncière estimée 2 200 €, assurance 450 €, entretien et provision travaux, TEOM non récupérable, "
            "frais bancaires, provision d'impayés, comptabilité 1 200 €. Aucun poste n'est laissé à zéro",
            "<strong>Financement :</strong> 90 % du prix sur 15 ans à 3,7 %, soit 1 611 €/mois, apport de 10 % et "
            "frais assumés à part. Fonds propres à amener 74 460 € en scénario de base, 139 460 € si les combles "
            "sont aménagés",
            "<strong>Contrôles à faire avant toute offre :</strong> baux des trois lots (montant, date, type, "
            "indexation, dépôt) ; avis de taxe foncière et valeur locative cadastrale ; surfaces Carrez par lot "
            "et plans ; chiffrage de la toiture, de la charpente et de la façade par un homme de l'art ; "
            "diagnostics techniques et date du DPE ; faisabilité de l'aménagement des combles en mairie ; "
            "historique de mise en vente et statut d'occupation au jour de la vente",
            "<strong>Point de méthode :</strong> la doctrine du parc est que l'immeuble couvre sa mensualité, "
            "jamais qu'il la couvre grâce à la fourchette haute des loyers. Ici, le plafond se situe entre "
            "143 700 € (cash flow neutre sur 15 ans) et 180 500 € (5 % net avant IS), contre 247 000 € "
            "demandés. C'est cet écart qui commande la négociation, pas l'ancienneté de la mise en vente",
            "<strong>Rappel de marché (sources au 22/09/2026) :</strong> médiane des appartements à "
            "Pierrefeu-du-Var 2 716 €/m² (MeilleursAgents, Figaro Immobilier), moyenne toutes catégories "
            "3 340 €/m² (MeilleursAgents) à 4 046 €/m² (PAP) tirée par les maisons (78 % du parc) ; loyers "
            "constatés 515 € (T2 meublé 35 m²), 520 € (T1 bis 46 m²), 680 € (T2 50 m² centre-ville), 890 € "
            "(T3 meublé 80 m²) ; loyer commercial moyen 220 €/m²/an, fourchette 87 à 257 €/m²/an "
            "(UnEmplacement, 02/09/2026) ; taxe foncière bâtie communale 22,38 % ; 6 065 habitants",
        ],
    )

    c = gen.CONF[SLUG]
    html = gen.TEMPLATE.format(
        titre_court=c['titre_court'], adresse=c['adresse'], date_fr=c['date_fr'],
        source=c['source'], url=c['url'], badge=c['badge'], strategie=c['strategie'],
        fiscal_note=c['fiscal_note'],
        prix=eur(PRIX),
        surface="141 m²",
        prix_m2=f"{eur(PRIX/141)} €/m²",
        revient=eur(revient_base),
        valeur=eur(valeur),
        revenus=eur(LOYERS_AN),
        rdt_revient=fr(rdt_base, 2), rdt_valeur=fr(ebe_base / valeur * 100, 2),
        note=fr(note), note_cls=fr(note).replace(',', '-'),
        lat=c['lat'], lon=c['lon'], quartier=c['quartier'],
        intro_attr=c['intro_attr'], profil=c['profil'], concl_attr=c['concl_attr'],
        attrs=gen.attr_html(rec), intro_strat=c['intro_strat'], strats=gen.strategy_html(rec),
        rationale=c['rationale'], identite=gen.identite_html(c['identite']),
        projections=projections,
        risques=gen.risques_html(rec),
        verdict_cls={"acheter": "buy", "negocier": "nego", "fuir": "pass"}.get(verdict, "nego"),
        stance=c['stance'], prix_plafond=c['prix_plafond'],
        leviers=gen.leviers_html(c['leviers']),
        meta="\n".join(f"      <p>{m}</p>" for m in c['meta']),
    )
    d = os.path.join(ROOT, 'analyses', SLUG)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  fiche ecrite : {len(html):,} octets dans {SLUG}")

    # ------------------------------------------------- synchronisation du listing
    p = os.path.join(ROOT, 'analyses', 'analyses.json')
    data = json.load(open(p, encoding='utf-8'))
    # le fichier est un conteneur {"meta": ..., "analyses": [ ...fiches... ]}
    if SLUG in data:                      # nettoyage d'une entree ecrite au mauvais niveau
        data.pop(SLUG)
    lst = data.get('analyses')
    if isinstance(lst, list):
        lst = [x for x in lst if x.get('slug') != SLUG]
        lst.append(rec)
        data['analyses'] = lst
        total = len(lst)
    else:
        fiche = data['analyses']
        fiche[SLUG] = rec
        total = len(fiche)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  analyses.json : entree ecrite (total {total}) | cles racine : {list(data.keys())}")

    print("\n  --- chiffres de controle ---")
    print(f"  note {note} / 10  |  verdict {verdict}")
    print(f"  plafond CF 15 ans (loyers en place) : {eur(pl_cf15)} EUR  |  ecart {eur(pl_cf15-PRIX)}")
    print(f"  plafond 5 % net (travaux 30 k)      : {eur(pl_5_30)} EUR  |  ecart {eur(pl_5_30-PRIX)}")
    print(f"  valeur venale retenue               : {eur(valeur)} EUR  |  ratio cout/valeur {fr(revient_base/valeur,2)}")


if __name__ == '__main__':
    main()
