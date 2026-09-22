#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche Saint-Maximin-la-Sainte-Baume — immeuble de 400 m2 en centre-ville a renover,
local commercial + 2 etages + grenier, 235 000 EUR (Logic-Immo 26X26XJ4E4WY, Patrice Russo).

Branche mdb : le compte d'exploitation remplace les projections locatives, et les trois
scenarios se jouent sur l'enveloppe travaux (aucun devis, aucun plan, pas de DPE publie).
"""
import copy
import importlib.util
import json
import os
import sys

ROOT = '/home/alexis-barlatier/Documents/Semaphore-sonar'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from analyse_app import engine, scoring  # noqa: E402

SLUG = "2026-09-22-immeuble-centre-saint-maximin-la-sainte-baume"
URL = "https://www.logic-immo.com/detail-annonce/vente/provence-alpes-cote-d-azur/var-83/saint-maximin-la-sainte-baume-83470/26X26XJ4E4WY"

PRIX = 235000.0
HONORAIRES = 15000.0          # a la charge de l'acquereur, inclus dans les 235 000
NOTAIRE = 0.08
RDC, ET1, ET2, GRENIER, CAVE = 117, 93, 94, 96, 56
HAB = ET1 + ET2 + GRENIER
# marche DVF 2025 (statistiques reelles, Saint-Maximin 83116)
PRIX_M2_APP = 2746
PRIX_M2_MAISON = 2275
LOYER_M2 = 13.8
PORTAGE_MOIS = 24
TAUX = 0.037
FRAIS_VENTE = 0.05

REVENTE_CENTRALE = ET1 * PRIX_M2_APP + ET2 * PRIX_M2_APP + GRENIER * 2400 + RDC * 900


def eur(v):
    return f"{v:,.0f}".replace(',', ' ')


def fr(v, dec=1):
    return f"{v:.{dec}f}".replace('.', ',')


def revient(travaux, mois=PORTAGE_MOIS):
    frais = PRIX * NOTAIRE
    base = PRIX + frais + travaux
    portage = base * TAUX * mois / 12 + 3600 * mois / 12
    return base + portage, frais, portage


def mdb(travaux, revente):
    rev, frais, portage = revient(travaux)
    net = revente * (1 - FRAIS_VENTE)
    pv = net - rev
    is_ = max(0.0, pv) * 0.15
    return dict(revient=rev, frais=frais, portage=portage, net_vente=net, pv=pv,
                is_=is_, nette=pv - is_, roi=(pv - is_) / rev * 100)


def patrimonial(travaux, loyers_mensuels):
    rev, _, _ = revient(travaux)
    brut = loyers_mensuels * 12
    charges = brut * 0.19 + 3200
    ebe = brut - charges
    amort = rev * 0.9 / 30
    is_ = max(0.0, ebe - amort) * 0.15
    return dict(revient=rev, brut=brut, ebe=ebe, net=ebe - is_, net_mois=(ebe - is_) / 12,
                rdt=ebe / rev * 100)


def rec_saint_maximin():
    return {
        "slug": SLUG,
        "date_analyse": "2026-09-22",
        "date_maj": None,
        "titre": "Immeuble de 400 m² en centre-ville à rénover — deux locaux commerciaux, deux étages et grenier (283 m² habitables) — Saint-Maximin-la-Sainte-Baume (83470)",
        "bien": {
            "type_bien": "immeuble",
            "sous_type": None,
            "type_detail": (
                "Immeuble de 1900 en plein centre-ville, 3 étages sur rez-de-chaussée, 400 m² au total : "
                "au rez-de-chaussée deux locaux commerciaux prêts à être mis en location, deux réserves et un "
                "atelier donnant accès à une cave de 56 m² ; aux premier et deuxième étages deux plateaux de "
                "93 m² et 94 m² à diviser en appartements ; au troisième étage un grenier de 96 m² "
                "transformable en habitation sous réserve d'autorisations. L'agence annonce elle-même "
                "« d'importants travaux de rénovation ». Aucun DPE n'est publié, aucun plan, aucun diagnostic "
                "technique joint."
            ),
            "neuf": False,
            "adresse": {
                "texte": "Centre-ville, Saint-Maximin-la-Sainte-Baume (83470) — adresse exacte non communiquée",
                "ville": "Saint-Maximin-la-Sainte-Baume",
                "code_postal": "83470",
            },
            "surfaces": {
                "texte": (
                    "400 m² annoncés, soit la somme exacte des niveaux : 117 m² de rez-de-chaussée "
                    "(locaux commerciaux, réserves, atelier), 93 + 94 m² d'étages, 96 m² de grenier. La cave de "
                    "56 m² vient en plus. Surface habitable après travaux : 283 m². Aucune surface Carrez, "
                    "aucune surface utile par local"
                ),
                "carrez_m2": 283.0,
            },
            "lots": {
                "count": 12,
                "surface_par_lot_m2": None,
                "nature": (
                    "Immeuble déclaré en copropriété de 12 lots (fiche Logic-Immo) : l'état descriptif de "
                    "division existe donc déjà, ce qui autorise une revente lot par lot sans payer les 5 000 à "
                    "10 000 € d'une division à créer. Aucun détail des 12 lots, aucun état daté, aucun procès-verbal "
                    "d'assemblée, aucun montant de charges communiqué"
                ),
                "lots_distincts": 12,
            },
            "copro": {
                "charges_annuelles_euros": 0.0,
                "charges_source": (
                    "Copropriété de 12 lots (fiche Logic-Immo), sans syndic connu ni charges communiquées. "
                    "Si l'acquéreur devient propriétaire des 12 lots, il porte l'entretien de la structure, de la "
                    "toiture et de la façade seul, ce qui est le cas de figure le plus probable ici. Charges du "
                    "bien portées en direct : convention assumée, signalée au lecteur"
                ),
            },
            "travaux": {
                "montant_euros": 350000.0,
                "nature": (
                    "« Importants travaux de rénovation » annoncés sans un chiffre, sur un immeuble de 1900 de "
                    "400 m². Rénovation complète à créer : les réseaux (électricité, plomberie, chauffage "
                    "individuel), les menuiseries, l'isolation, les sols, la redistribution des plateaux en "
                    "appartements (cloisons, cuisines, salles d'eau), la reprise des parties communes et de "
                    "l'escalier, la toiture, la façade et la structure à vérifier. Fourchette retenue 250 000 à "
                    "480 000 € (890 à 1 700 €/m² de surface récente), estimation centrale 350 000 €. Aucun devis, "
                    "aucun plan, aucun diagnostic technique, aucun DPE : c'est la seule variable qui décide du "
                    "dossier et elle est inconnue"
                ),
            },
        },
        "annonce": {
            "plateforme": "Logic-Immo",
            "url": URL,
            "prix_affiche_euros": PRIX,
            "prix_retenu_euros": None,
            "prix_statut": "affiche",
            "prix_commentaire": (
                "235 000 € honoraires inclus, mais 15 000 € TTC (6,82 %) à la charge de l'acquéreur : le prix "
                "hors honoraires est de 220 000 €. Le ratio affiché de 588 €/m² porte sur les 400 m² totaux, dont "
                "96 m² de grenier non habitable et 117 m² de locaux. Rapporté aux 283 m² réellement habitables "
                "après travaux, le prix ressort à 830 €/m², dans un marché d'appartements à 2 746 €/m². "
                "Vendeur en exclusivité chez Patrice Russo Immobilier, référence VIM10001311"
            ),
        },
        "marche": {
            "valeur": {
                "basse_euros": 750000.0,
                "haute_euros": 950000.0,
                "retenue_euros": round(REVENTE_CENTRALE),
                "source": (
                    "Valorisation par composant après rénovation, ancrée sur les mutations DVF 2025 de "
                    "Saint-Maximin (commune 83116) : appartements, 59 ventes, médiane 2 746 €/m², dont 2 941 €/m² "
                    "sur la tranche 45-60 m² et 3 196 €/m² sur 60-80 m² (les tranches qui correspondent aux lots "
                    "à créer) ; les deux étages de 187 m² à 2 746 €/m², le grenier de 96 m² à 2 400 €/m² (combles "
                    "aménagés, décote de 13 %), le rez-de-chaussée de 117 m² à 900 €/m² (locaux commerciaux de "
                    "centre-ville). Total 849 000 €, fourchette 750 000 à 950 000 € selon la qualité de la "
                    "rénovation et le nombre de lots créés"
                ),
                "confiance": "moyenne",
            },
            "loyers": [
                {
                    "lot": "Appartement à créer, 1er étage (93 m², divisible en deux)",
                    "quantite": 1,
                    "loyer_mensuel_euros": 1100.0,
                    "occupe": False,
                    "note": (
                        "Lot à créer : aucun loyer en place, loyer retenu après rénovation. Comparables relevés "
                        "le 22/09/2026 à Saint-Maximin : T3 de 67,39 m² à 910 €, T3 de 63 m² à 897 €, T3 de "
                        "68 m² à 700 €, T2 à 713 € charges comprises. Le loyer mesuré de la commune est de "
                        "13,8 €/m²/mois (ANIL 2025), soit environ 11,8 €/m² après minoration prudente. "
                        "93 m² en un seul logement familial se louent moins cher au m² que deux petites surfaces"
                    ),
                },
                {
                    "lot": "Appartement à créer, 2e étage (94 m², divisible en deux)",
                    "quantite": 1,
                    "loyer_mensuel_euros": 1100.0,
                    "occupe": False,
                    "note": "Idem : lot à créer, loyer retenu après rénovation, sur la même base de comparables.",
                },
                {
                    "lot": "Grenier de 96 m² à aménager en logement",
                    "quantite": 1,
                    "loyer_mensuel_euros": 950.0,
                    "occupe": False,
                    "note": (
                        "Aménagement soumis à autorisation d'urbanisme (création de surface de plancher, donc "
                        "taxe d'aménagement). Les combles aménagés se louent avec une décote : 950 € pour 96 m², "
                        "soit 9,9 €/m²"
                    ),
                },
                {
                    "lot": "Deux locaux commerciaux, rez-de-chaussée (environ 60 m²)",
                    "quantite": 2,
                    "loyer_mensuel_euros": 400.0,
                    "occupe": False,
                    "note": (
                        "Locaux annoncés « prêts à être mis en location », donc vides aujourd'hui. Comparables "
                        "relevés le 22/09/2026 : local de 50 m² à 390 €/mois en centre-ville, 50 m² à 405 €, "
                        "58,72 m² sous bail commercial à 1 008 €, 92 m² au premier étage à 1 444 €. "
                        "Attention : 13 locaux commerciaux sont disponibles à la location dans la commune, "
                        "l'offre est abondante et la vacance peut durer"
                    ),
                },
            ],
            "notes": (
                "Le bien ne produit aucun revenu aujourd'hui : les locaux commerciaux sont à mettre en location, "
                "les étages sont des plateaux nus et le grenier n'est pas habitable. Toutes les projections sont "
                "donc des projections après travaux, jamais des revenus acquis. Le rendement brut de la commune, "
                "calculé sur les mutations DVF 2025 et le loyer mesuré ANIL, est de 6,0 % : c'est un marché "
                "d'usage, pas un marché de rendement, et la valeur du dossier ne vient pas du loyer mais de "
                "l'écart entre le prix d'achat et la valeur après rénovation."
            ),
            "revente": {
                "prix_euros": round(REVENTE_CENTRALE),
                "frais_vente_euros": round(REVENTE_CENTRALE * FRAIS_VENTE, 2),
                "duree_mois": PORTAGE_MOIS,
                "portage_mensuel_euros": 2200.0,
            },
        },
        "hypotheses": {
            "vacance_base_pct": 8.0,
            "vacance_best_pct": 4.0,
            "vacance_worst_pct": 15.0,
            "vacance_justification": (
                "Le bien est vide : la vacance ne mesure pas un risque de relocation mais le délai de "
                "commercialisation des lots créés. 8 % correspond à un mois de vide par lot et par an sur "
                "quatre lots, 15 % à la difficulté de louer les deux locaux commerciaux dans une commune où "
                "13 sont déjà disponibles."
            ),
            "frais_acquisition_euros": round(PRIX * NOTAIRE, 2),
            "frais_divers_euros": 0.0,
            "charges": {
                "taxe_fonciere_annuelle_euros": 3500.0,
                "taxe_fonciere_commentaire": (
                    "ESTIMATION 3 500 €/an pour 400 m² dont 117 m² de locaux commerciaux — la taxe n'est pas "
                    "communiquée. À vérifier sur l'avis réel avant toute offre : sur un immeuble de cette taille, "
                    "l'écart entre 2 500 et 5 000 € vaut 200 €/mois de cash flow"
                ),
                "charges_copro_annuelles_euros": 0.0,
                "charges_copro_commentaire": (
                    "Aucune charge de copropriété communiquée. Convention assumée : l'acquéreur des 12 lots "
                    "porte la toiture, la façade, l'escalier et les réseaux, provisionnés dans le poste entretien"
                ),
                "pno_annuelle_euros": 700.0,
                "pno_commentaire": "Assurance de l'immeuble et de ses locaux, bâtiment de 1900 en travaux puis en exploitation.",
                "entretien_annuel_euros": 3000.0,
                "entretien_commentaire": (
                    "Entretien courant, TEOM non récupérable, frais bancaires, provision d'impayés et provision "
                    "gros travaux sur un bâtiment de 1900. Immeuble de 400 m², donc poste supérieur à un "
                    "appartement : calibrage 3 000 €/an, soit 7 % des loyers bruts attendus"
                ),
                "comptabilite_annuelle_euros": 1500.0,
                "comptabilite_commentaire": "Comptabilité de la structure (SAS ou SCI à l'IS) avec un chantier de rénovation à suivre.",
            },
        },
        "analyse": {
            "branche": "mdb",
            "type_operation": "renovation",
            "strategie_retenue": {
                "nom": "Rénovation complète puis revente des lots (marchand de biens)",
                "code": "mdb",
                "lots": 4,
            },
            "strategies_explorees": [
                {
                    "strategie": "Marchand de biens : rénover et revendre",
                    "lots": 4,
                    "rendement": "ROI de 1 à 40 % selon l'enveloppe travaux — 19,6 % à 350 000 €, 1,2 % à 480 000 €",
                    "faisabilite": "24 mois de travaux et de portage, 12 lots déjà divisés donc revente lot par lot possible",
                    "risque": "élevé — tout dépend d'un chiffrage de travaux inexistant sur un immeuble de 1900",
                },
                {
                    "strategie": "Rénover puis conserver en location (patrimonial, SCI à l'IS)",
                    "lots": 4,
                    "rendement": "5,2 à 6,3 % net avant IS selon les loyers et l'enveloppe travaux",
                    "faisabilite": "24 mois de travaux avant le premier loyer, trésorerie à porter",
                    "risque": "moyen — le rendement tient, mais 139 000 € de travaux supplémentaires font tomber sous 4,3 %",
                },
                {
                    "strategie": "Achat en l'état, mise en location des locaux commerciaux seuls",
                    "lots": 2,
                    "rendement": "environ 9 600 €/an de loyers pour 253 000 € engagés, soit 3,8 % brut",
                    "faisabilite": "immédiate, mais l'immeuble reste en travaux et les étages vides",
                    "risque": "élevé — revenu insuffisant pour couvrir la moindre charge de structure",
                },
                {
                    "strategie": "Découpage en appartements et vente à la découpe sans rénovation lourde",
                    "lots": 6,
                    "rendement": "dépend entièrement du coût de redistribution des plateaux",
                    "faisabilite": "les 12 lots sont déjà divisés, mais les plateaux ne sont pas cloisonnés",
                    "risque": "élevé — vendre des plateaux nus dans une commune de 17 000 habitants est un pari",
                },
            ],
            "attractivite": [
                {
                    "dimension": "transports",
                    "score": 7,
                    "justification": (
                        "Saint-Maximin est à l'entrée de l'autoroute A8, à 35 minutes d'Aix-en-Provence et "
                        "45 minutes de Marseille, avec un bassin d'emploi propre (la Sainte-Baume, la vallée de "
                        "l'Arc, la zone de la Barque). C'est l'une des communes les mieux desservies du "
                        "centre-Var : c'est ce qui soutient la demande locative et la revente"
                    ),
                },
                {
                    "dimension": "commerces",
                    "score": 7,
                    "justification": (
                        "Bourg de 17 000 habitants avec une rue commerçante active, un marché, un hypermarché et "
                        "toutes les chaînes. Le bien est en plein centre, ce qui est la meilleure adresse "
                        "possible. Réserve : 13 locaux commerciaux sont déjà disponibles à la location dans la "
                        "commune, c'est le point faible du lot de rez-de-chaussée"
                    ),
                },
                {
                    "dimension": "ecoles",
                    "score": 7,
                    "justification": "Écoles, collège et lycée sur la commune, plus les établissements d'Aix à 35 minutes.",
                },
                {
                    "dimension": "securite",
                    "score": 6,
                    "justification": (
                        "Bourg de la Sainte-Baume, sans tension particulière, avec un centre ancien qui se "
                        "repeuple progressivement"
                    ),
                },
                {
                    "dimension": "demande_locative",
                    "score": 7,
                    "justification": (
                        "Marché locatif liquide et documenté : T3 de 63 à 68 m² entre 700 et 950 €, une dizaine "
                        "d'annonces actives, un loyer mesuré de 13,8 €/m²/mois et un bassin d'emploi qui fait "
                        "vivre la commune à l'année. C'est un vrai marché de locataires, pas un marché "
                        "saisonnier"
                    ),
                },
                {
                    "dimension": "dynamisme",
                    "score": 7,
                    "justification": (
                        "233 ventes enregistrées en 2025 (59 appartements et 174 maisons), un prix médian de "
                        "2 746 €/m² pour les appartements et 2 275 €/m² pour les maisons, des tranches 45-80 m² "
                        "qui se traitent autour de 3 000 €/m². La profondeur du marché est le principal atout "
                        "du dossier : une opération de quatre lots peut se revendre ici, ce qui n'est pas vrai "
                        "partout dans le Var"
                    ),
                },
            ],
            "risques": [
                {
                    "facteur": "Aucun DPE publié sur un immeuble de 1900 annoncé à rénover",
                    "severite": 4,
                    "detail": (
                        "L'annonce se contente d'un « demandez la performance énergétique » : le DPE est "
                        "obligatoire dans toute annonce de vente, son absence est en soi une information et une "
                        "irrégularité. Sur un bâti de 1900 à rénover entièrement, l'étiquette attendue se situe "
                        "entre E et G. Or la location des G est déjà interdite et celle des F le sera en 2028 : "
                        "un classement G condamne la location des étages tant qu'ils ne sont pas rénovés, et "
                        "ajoute un passif de rénovation énergétique au chantier. À exiger avant toute offre, "
                        "comme les diagnostics électricité, plomb et amiante"
                    ),
                },
                {
                    "facteur": "Rénovation complète d'un immeuble de 1900, sans devis, sans plan, sans diagnostic",
                    "severite": 5,
                    "detail": (
                        "C'est le dossier entier. L'agence écrit « importants travaux de rénovation » et rien "
                        "d'autre : les réseaux, les menuiseries, l'isolation, la redistribution des plateaux en "
                        "appartements, les cuisines et salles d'eau, l'escalier, la toiture, la façade et la "
                        "structure sont à chiffrer. La fourchette réaliste va de 250 000 à 480 000 € sur 400 m² "
                        "et l'écart entre les deux bornes vaut la totalité de la marge de l'opération. "
                        "Le prix d'achat qui laisse 20 % de ROI tombe de 325 000 € avec 250 000 € de travaux à "
                        "113 000 € avec 480 000 €, en passant par 233 000 € avec 350 000 € : autrement dit, "
                        "au-delà de 350 000 € de chantier, l'achat à 235 000 € n'est plus un marchand de biens "
                        "et il faut soit renégocier de l'écart, soit passer"
                    ),
                },
                {
                    "facteur": "Toiture, charpente et structure d'un immeuble de 1900 sur trois niveaux",
                    "severite": 4,
                    "detail": (
                        "Aucun diagnostic technique, aucun gros travaux documenté. Sur un immeuble de 1900 en "
                        "centre ancien, la couverture, la charpente, les planchers et l'humidité des caves "
                        "commandent la moitié du budget. La visite d'un homme de l'art est la condition d'une "
                        "offre, pas une formalité : c'est la même règle que sur les dossiers Solliès-Pont et "
                        "Pierrefeu"
                    ),
                },
                {
                    "facteur": "Deux locaux commerciaux vides dans une commune à 13 locaux disponibles",
                    "severite": 3,
                    "detail": (
                        "Le rez-de-chaussée est annoncé « prêt à être mis en location », donc vide. Les "
                        "comparables relevés affichent 390 à 405 € pour 50 m² et l'offre communale est "
                        "abondante : la vacance commerciale peut durer des mois et peser sur la trésorerie "
                        "pendant les travaux. Ne pas compter plus de 400 € par local dans les projections, "
                        "et prévoir un an de vide au démarrage"
                    ),
                },
                {
                    "facteur": "Aucune information sur la copropriété de 12 lots",
                    "severite": 3,
                    "detail": (
                        "L'annonce mentionne 12 lots sans dire lesquels, sans charges, sans procès-verbal "
                        "d'assemblée et sans état daté. Il faut établir si l'acquéreur prend les 12 lots (donc "
                        "devient seul propriétaire de l'immeuble) ou une partie seulement, ce que cela implique "
                        "de travaux de copropriété à voter, et si le règlement autorise la division des plateaux "
                        "et l'aménagement du grenier. La revente lot par lot n'est possible que si l'état "
                        "descriptif de division est propre"
                    ),
                },
                {
                    "facteur": "Honoraires de 15 000 € à la charge de l'acquéreur",
                    "severite": 2,
                    "detail": (
                        "Le prix affiché de 235 000 € inclut 15 000 € TTC d'honoraires acquéreur (6,82 %), pour "
                        "un net vendeur de 220 000 €. Les frais de notaire se calculent sur 235 000 €, et le "
                        "prix affiché ne doit jamais être comparé à un prix net vendeur d'annonces concurrentes : "
                        "l'écart réel est de 15 000 €, soit plus de six mois de loyer des deux étages"
                    ),
                },
            ],
            "champs_manquants": [
                "DPE, diagnostics électricité, plomb et amiante de l'immeuble",
                "devis de rénovation par corps d'état, plan des niveaux et surfaces par local",
                "détail des 12 lots de copropriété, état daté, charges et procès-verbaux d'assemblée",
                "avis de taxe foncière réel et valeur locative cadastrale",
                "état de la toiture, de la charpente, des planchers et des caves",
                "statut fiscal du vendeur et situation d'occupation de chaque lot",
                "faisabilité de la division des plateaux et de l'aménagement du grenier (PLU, taxe d'aménagement)",
            ],
        },
    }


def main():
    spec = importlib.util.spec_from_file_location(
        "gen", os.path.join(ROOT, 'scripts', 'gen_fiches_2026-09-10.py'))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)

    rec = rec_saint_maximin()
    r = engine.compute(rec)
    base = r
    note, verdict, _ = scoring.note_et_verdict(rec, base)

    scen = [("base", 350000.0, "Rénovation lourde à 350 000 € (1 237 €/m² habitable)"),
            ("optimiste", 250000.0, "Rénovation maîtrisée à 250 000 € (883 €/m² habitable)"),
            ("pessimiste", 480000.0, "Rénovation complète à 480 000 € (1 696 €/m² habitable)")]
    res = {}
    for cle, trav, lab in scen:
        res[cle] = (trav, lab, mdb(trav, REVENTE_CENTRALE))
    rb, ro, rp = res['base'][2], res['optimiste'][2], res['pessimiste'][2]

    print(f"  revente centrale retenue : {eur(REVENTE_CENTRALE)} EUR")
    for cle, trav, lab in scen:
        m = res[cle][2]
        print(f"  {cle:<11} travaux {eur(trav):>9} -> revient {eur(m['revient']):>9} | PV nette {eur(m['nette']):>9} | ROI {fr(m['roi'])} %")

    def ligne(label, val, cls=""):
        c = f' class="{cls}"' if cls else ''
        return f'            <tr{c}><td>{label}</td><td class="num">{val}</td></tr>'

    def compte(trav, rev):
        rows = [
            ligne("Prix d'achat (honoraires acquéreur inclus)", f"{eur(PRIX)} €"),
            ligne("dont honoraires à la charge de l'acquéreur", f"{eur(HONORAIRES)} €"),
            ligne("Frais d'acquisition (8 %)", f"{eur(rev['frais'])} €"),
            ligne(f"Rénovation ({eur(trav)} €, {eur(trav/HAB)} €/m² habitable)", f"{eur(trav)} €"),
            ligne("Portage 24 mois (intérêts, TF, assurances)", f"{eur(rev['portage'])} €"),
            ligne("Prix de revient total", f"{eur(rev['revient'])} €", "subtotal"),
            ligne("Revente après rénovation", f"{eur(REVENTE_CENTRALE)} €"),
            ligne("Honoraires de vente (5 %)", f"-{eur(REVENTE_CENTRALE*FRAIS_VENTE)} €"),
            ligne("Plus-value brute", f"{eur(rev['pv'])} €", "subtotal"),
            ligne("IS (15 %)", f"-{eur(rev['is_'])} €"),
            ligne("Plus-value nette après IS", f"{eur(rev['nette'])} €", "highlight"),
            ligne("ROI sur le prix de revient", f"{fr(rev['roi'])} %"),
            ligne("Revient / revente", f"{fr(rev['revient']/REVENTE_CENTRALE, 2)}"),
        ]
        return "\n".join(rows)

    cartes = []
    for cle, trav, lab in scen:
        m = res[cle][2]
        cartes.append(f"""      <div class="projection-card scenario-{cle}">
        <h3>Scénario {cle.capitalize()}</h3>
        <p class="scenario-subtitle">{lab} — ROI {fr(m['roi'])} %</p>
        <table class="projection-table"><tbody>
{compte(trav, m)}
        </tbody></table>
      </div>""")

    # grille : ROI selon travaux et revente
    grille = []
    for trav in (200000.0, 250000.0, 300000.0, 350000.0, 400000.0, 480000.0):
        cells = []
        for rev in (750000.0, 849000.0, 950000.0):
            m = mdb(trav, rev)
            cells.append(f'<td class="num">{fr(m["roi"])} %</td>')
        grille.append(f'        <tr><td>{eur(trav)} € ({eur(trav/HAB)} €/m²)</td>' + "".join(cells) + '</tr>')
    grille_html = "\n".join(grille)

    # plafonds d'achat : prix max pour 20 % de ROI, par tranche de travaux
    # nette = 0,85 x (net_vente - revient) = 0,20 x revient  =>  revient_max = 0,85 x net / 1,05
    # revient = P x 1,08 + W + 0,074 x (P x 1,08 + W) + 7 200
    net = REVENTE_CENTRALE * (1 - FRAIS_VENTE)
    rev_max = 0.85 * net / 1.05
    plafonds = []
    plafonds_vals = []
    for trav in (200000.0, 250000.0, 300000.0, 350000.0, 400000.0, 480000.0):
        prix_max = ((rev_max - 7200.0) / (1 + TAUX * PORTAGE_MOIS / 12) - trav) / (1 + NOTAIRE)
        plafonds_vals.append(prix_max)
        plafonds.append(f'        <tr><td>{eur(trav)} €</td><td class="num">{eur(prix_max)} €</td>'
                        f'<td class="num">{eur(prix_max-PRIX)} €</td></tr>')
    plafonds_html = "\n".join(plafonds)

    pat = []
    for trav in (250000.0, 350000.0, 480000.0):
        for loy, lab in ((3800.0, "loyers prudents"), (4570.0, "loyers au marché")):
            p = patrimonial(trav, loy)
            pat.append(f'        <tr><td>{eur(trav)} €</td><td>{lab}</td><td class="num">{eur(p["brut"])} €</td>'
                       f'<td class="num">{eur(p["ebe"])} €</td><td class="num">{fr(p["rdt"],2)} %</td>'
                       f'<td class="num">{eur(p["net_mois"])} €</td></tr>')
    pat_html = "\n".join(pat)

    lecture = (
        "588 €/m² dans une commune où les appartements se vendent 2 746 €/m² : le réflexe est de voir une "
        "aubaine. Il faut le corriger tout de suite, parce que les 400 m² annoncés ne sont pas 400 m² de "
        "logement. Il y a 117 m² de rez-de-chaussée commercial, 96 m² de grenier non habitable et une cave de "
        "56 m². La surface habitable après travaux est de 283 m², et le prix ressort alors à 830 €/m², ce qui "
        "reste bas mais n'est plus le même chiffre. Le vrai sujet est ailleurs : l'agence annonce « d'importants "
        "travaux de rénovation » sans un devis, sur un immeuble de 1900, et sans publier de DPE. "
        "Avec 250 000 € de chantier, l'opération dégage 220 000 € de plus-value nette et 40 % de ROI. "
        "À 350 000 €, elle tombe à 128 000 € et 19,6 %. À 480 000 €, il ne reste que 9 500 € pour 24 mois de "
        "travaux et de portage : le dossier est mort. Le prix d'achat qui laisse 20 % de ROI passe de 258 000 € "
        "avec 250 000 € de travaux à 45 000 € avec 480 000 €. Autrement dit, tout se joue entre 250 000 et "
        "300 000 € de rénovation, et personne ne sait aujourd'hui de quel côté de cette ligne le bâtiment se "
        "trouve. Le dossier est bon sur le papier — le marché de Saint-Maximin est profond, 233 ventes en 2025, "
        "et les 12 lots sont déjà divisés — mais il est illisible tant qu'un homme de l'art n'a pas chiffré "
        "la toiture, la charpente et les réseaux."
    )

    gen.LECTURE[SLUG] = lecture
    gen.RECS[SLUG] = rec
    gen.CONF[SLUG] = dict(
        titre_court="Immeuble centre-ville à rénover, Saint-Maximin (83470)",
        adresse="Saint-Maximin-la-Sainte-Baume (83470), centre-ville — immeuble de 1900, 400 m² sur 3 étages "
                "et rez-de-chaussée : locaux commerciaux, deux plateaux de 93 et 94 m², grenier de 96 m² — "
                "adresse exacte non communiquée",
        date_fr="22 septembre 2026",
        source="Logic-Immo — annonce 26X26XJ4E4WY (Patrice Russo Immobilier, 9 avenue Albert 1er à "
               "Saint-Maximin, SIRET 80929519900024, réf. VIM10001311), bien présenté en exclusivité",
        url=URL,
        badge="Marchand de biens",
        strategie="Achat, rénovation complète et revente des lots — variante conservation chiffrée",
        fiscal_note="SAS à l'IS (15 % sur la plus-value), financement intégral du prix de revient",
        lat="43.4528", lon="5.8619",
        quartier="Saint-Maximin-la-Sainte-Baume (83470) — 17 000 habitants, A8 à 5 minutes, Aix à 35 minutes",
        intro_attr=(
            "Saint-Maximin-la-Sainte-Baume est un bourg de <strong>17 000 habitants</strong> à l'entrée de "
            "l'autoroute A8, à 35 minutes d'Aix-en-Provence : un vrai bassin de vie avec sa rue commerçante, "
            "ses écoles, son collège et son lycée. Le marché est l'un des plus profonds du centre-Var : "
            "<strong>233 ventes enregistrées en 2025</strong> selon la base DVF, dont 59 appartements et "
            "174 maisons. Les appartements se traitent à <strong>2 746 €/m²</strong> en médiane, avec des "
            "tranches 45 à 80 m² qui partent entre <strong>2 941 et 3 196 €/m²</strong> — précisément les "
            "formats que produirait une division des plateaux. Le loyer mesuré est de 13,8 €/m²/mois et le "
            "rendement brut communal ressort à 6,0 % : un marché d'usage, pas de rendement, où la valeur se "
            "crée par la rénovation et non par le loyer."
        ),
        profil=(
            "un marchand de biens ou un investisseur patrimonial qui sait porter un chantier de 24 mois : "
            "l'immeuble est vendu vide, sans loyer, avec 283 m² habitables à créer et 117 m² de commerce à "
            "remettre en location. Ce n'est ni un dossier de rendement immédiat, ni un dossier de débutant : "
            "il demande un devis par corps d'état avant l'offre et une trésorerie capable d'avancer 600 000 € "
            "de prix de revient"
        ),
        concl_attr=(
            "Adéquation bonne (7,4/10). L'emplacement est le meilleur possible dans une commune qui compte : "
            "plein centre, rue commerçante, autoroute à cinq minutes, marché locatif et marché de revente tous "
            "les deux liquides. Les 12 lots existent déjà, donc la revente à la découpe est ouverte sans "
            "payer de division. Et le prix d'entrée est bas : 830 €/m² habitable après travaux contre "
            "2 746 €/m² pour les appartements du marché. Deux éléments plombent le score. D'abord "
            "<strong>l'absence de DPE</strong> dans une annonce où il est obligatoire, sur un bâtiment de 1900 "
            "annoncé à rénover. Ensuite, et surtout, <strong>l'absence totale de chiffrage des travaux</strong> : "
            "sur 400 m², la fourchette 250 000 à 480 000 € vaut la totalité de la marge."
        ),
        intro_strat=(
            "Quatre lectures ont été testées : la rénovation complète suivie d'une revente (marchand de biens), "
            "la rénovation suivie d'une conservation en location, la mise en location des seuls locaux "
            "commerciaux en l'état, et une découpe rapide sans rénovation lourde. C'est la première qui porte "
            "la décision, parce que c'est celle que l'écart entre le prix d'achat et la valeur du marché "
            "rémunère."
        ),
        rationale=(
            "Le dossier a un vrai ressort : <strong>un immeuble entier de 400 m² en plein centre pour "
            "235 000 €</strong>, soit 830 €/m² sur les 283 m² habitables après travaux, dans une commune où "
            "les appartements se vendent 2 746 €/m² et où 233 mutations ont été enregistrées en 2025. "
            "Les 12 lots sont déjà divisés, ce qui ouvre la revente à la découpe sans formalité préalable.<br><br>"
            "Mais tout dépend d'un chiffre qui n'existe pas. <strong>À 250 000 € de travaux</strong>, la "
            "revente à 849 000 € dégage <strong>219 528 € de plus-value nette, soit 40 % de ROI</strong> sur "
            "24 mois. <strong>À 350 000 €</strong> : 128 402 € et 19,6 %. <strong>À 480 000 €</strong> : "
            "9 725 € et 1,2 %, c'est-à-dire rien pour deux ans de chantier et de portage. Le prix d'achat "
            "maximum qui laisse 20 % de ROI tombe de <strong>325 000 €</strong> avec 250 000 € de travaux à "
            "<strong>113 000 €</strong> avec 480 000 €, en passant par <strong>233 000 €</strong> avec "
            "350 000 € : autrement dit, le prix affiché de 235 000 € se tient tout juste si le chantier "
            "tient dans 350 000 €, et il ne se tient plus du tout au-delà de 400 000 €."
            "La variante conservation tient mieux qu'on ne pourrait le croire. Avec 350 000 € de travaux et "
            "des loyers prudents — 3 800 €/mois pour les trois logements et les deux locaux — l'excédent brut "
            "d'exploitation ressort à <strong>33 736 €</strong> et le rendement net avant IS à "
            "<strong>5,2 %</strong>, au-dessus de notre seuil. Aux loyers du marché : "
            "<strong>6,3 %</strong>. C'est même le seul dossier de la semaine qui atteint la doctrine sans "
            "attendre l'IRL. Mais il faut avancer 604 000 € de prix de revient, et 480 000 € de travaux le "
            "font tomber à 4,2 %."
        ),
        identite=[
            ("Adresse", "Saint-Maximin-la-Sainte-Baume (83470), plein centre-ville, rue commerçante — "
                        "adresse exacte non communiquée"),
            ("Vendeur / intermédiaire", "Patrice Russo Immobilier, 9 avenue Albert 1er à Saint-Maximin "
                                        "(SIRET 80929519900024) — annonce Logic-Immo 26X26XJ4E4WY, "
                                        "référence VIM10001311"),
            ("Composition", "Immeuble de 1900 sur trois étages et rez-de-chaussée, 400 m² : au rez-de-chaussée "
                            "deux locaux commerciaux, deux réserves et un atelier avec accès à une cave de "
                            "56 m² ; au premier et au deuxième étage deux plateaux de 93 et 94 m² ; au "
                            "troisième un grenier de 96 m²"),
            ("Statut", "<strong>Copropriété de 12 lots</strong> (fiche Logic-Immo) : l'état descriptif de "
                       "division existe, la revente lot par lot est donc possible sans créer de division. "
                       "Aucun détail des lots, aucune charge, aucun procès-verbal communiqué"),
            ("Surfaces", "400 m² annoncés = 117 m² de rez-de-chaussée + 93 + 94 m² d'étages + 96 m² de grenier. "
                         "<strong>283 m² habitables après travaux</strong>, plus la cave de 56 m². "
                         "Aucune surface Carrez ni utile par local"),
            ("DPE / GES", "<strong>Aucun DPE publié</strong> : l'annonce renvoie à une demande auprès de "
                          "l'agence, alors que le DPE est obligatoire dans toute annonce de vente. Sur un "
                          "bâti de 1900 à rénover entièrement, l'étiquette attendue est E, F ou G — un G "
                          "interdit déjà la location des logements. Diagnostics électricité, plomb et "
                          "amiante non joints"),
            ("Prix affiché", "<strong>235 000 € honoraires inclus</strong>, dont <strong>15 000 € TTC "
                             "d'honoraires à la charge de l'acquéreur</strong> (6,82 %), soit un net vendeur "
                             "de 220 000 €. 588 €/m² sur les 400 m², mais <strong>830 €/m²</strong> sur les "
                             "283 m² habitables après travaux"),
            ("Valeur après rénovation", "<strong>849 000 €</strong>, fourchette 750 000 à 950 000 € : "
                                        "187 m² d'étages à 2 746 €/m² (médiane DVF 2025 des appartements de "
                                        "Saint-Maximin), grenier de 96 m² à 2 400 €/m², rez-de-chaussée de "
                                        "117 m² à 900 €/m²"),
            ("Loyers attendus après travaux", "<strong>3 800 €/mois prudents</strong> : T3 de 93 m² à 1 100 €, "
                                              "T3 de 94 m² à 1 100 €, logement de 96 m² sous combles à 950 €, "
                                              "et deux locaux commerciaux à 400 € chacun. Comparables relevés "
                                              "le 22/09/2026 : T3 de 63 à 68 m² entre 700 et 950 €, locaux "
                                              "de 50 m² à 390-405 €. Loyers du marché : 4 570 €/mois"),
            ("Travaux", "<strong>350 000 € retenus (1 237 €/m² habitable)</strong>, fourchette 250 000 à "
                        "480 000 €. Aucun devis, aucun plan, aucun diagnostic technique. Réseaux, menuiseries, "
                        "isolation, redistribution en appartements, cuisines et salles d'eau, escalier, "
                        "toiture, façade et structure à chiffrer"),
            ("Taxe foncière", "<strong>Estimée 3 500 €/an</strong> — avis non communiqué. À vérifier : sur "
                              "400 m² dont 117 m² de locaux commerciaux, l'écart entre 2 500 et 5 000 € vaut "
                              "200 €/mois de cash flow"),
            ("Prix de revient", "<strong>604 000 €</strong> avec 350 000 € de travaux (prix, frais d'acquisition "
                                "et portage de 24 mois), 504 000 € avec 250 000 €, 734 000 € avec 480 000 €"),
        ],
        stance=(
            "<strong>On instruit, et on signe sous devis : offre 215 000 €, plafond 235 000 € (le prix "
            "affiché), uniquement si le chantier tient dans 350 000 €.</strong> Le raisonnement tient en deux "
            "chiffres. À 235 000 €, l'opération laisse 19,6 % de ROI si la rénovation coûte 350 000 €, 40 % si "
            "elle en coûte 250 000, 1,2 % si elle en coûte 480 000. Le prix affiché n'est donc pas une "
            "anomalie : pour une rénovation lourde correctement chiffrée, il tombe exactement sur notre seuil "
            "de 20 % — le prix d'achat maximum pour ce budget de travaux est de 233 000 €. Mais rien ne prouve "
            "aujourd'hui que ces 350 000 € soient tenables sur un immeuble de 1900 dont personne n'a publié "
            "le DPE, les plans ni un seul diagnostic. Acheter au prix sans devis, c'est acheter un chiffre "
            "qu'on n'a pas vu.<br><br>"
            "<strong>Trois conditions suspensives, non négociables.</strong> D'abord le <strong>DPE et les "
            "diagnostics techniques</strong> : leur absence dans une annonce est une irrégularité, et une "
            "étiquette F ou G ajoute 40 000 à 60 000 € de rénovation énergétique au chantier. Ensuite le "
            "<strong>devis par corps d'état plafonné à 350 000 €, toiture et charpente comprises</strong> : "
            "c'est ce chiffre, et lui seul, qui décide du dossier. Enfin le <strong>détail des 12 lots</strong> "
            "et la position du PLU sur la division des plateaux et l'aménagement du grenier.<br><br>"
            "<strong>Ce qui rend le dossier intéressant malgré tout.</strong> Le marché de Saint-Maximin est "
            "profond — 233 ventes en 2025, dont 59 appartements, et les tranches de 45 à 80 m² partent entre "
            "2 941 et 3 196 €/m² — et les 12 lots sont déjà divisés, donc la revente à la découpe est ouverte "
            "sans formalité préalable. Une opération de trois logements et deux locaux se revend ici, ce qui "
            "n'est vrai ni à Pierrefeu ni à Cuers. Et la variante conservation atteint 5,2 % net avant IS à "
            "350 000 € de travaux avec des loyers prudents, 6,3 % aux loyers du marché : c'est, sur le "
            "papier, le meilleur rendement patrimonial de la semaine."
        ),
        prix_plafond=(
            "<strong>235 000 €, le prix affiché</strong> — et uniquement avec un devis de rénovation plafonné "
            "à 350 000 € toiture comprise, un DPE connu et des diagnostics propres. Repères pour 20 % de ROI "
            "sur une revente à 849 000 € : <strong>325 000 €</strong> avec 250 000 € de travaux, "
            "<strong>279 000 €</strong> avec 300 000 €, <strong>233 000 €</strong> avec 350 000 €, "
            "<strong>187 000 €</strong> avec 400 000 €, <strong>113 000 €</strong> avec 480 000 €. "
            "Chaque tranche de 50 000 € de travaux coûte 46 000 € de capacité de prix. <strong>Une offre à "
            "215 000 € achète la marge d'erreur</strong> : elle fait tenir le dossier jusqu'à 375 000 € de "
            "chantier. Si le DPE révèle un classement F ou G, retirer le coût de la rénovation énergétique, "
            "soit 40 000 à 60 000 € de capacité de prix."
        ),
        leviers=[
            "Le DPE n'est pas publié, alors qu'il est obligatoire dans toute annonce de vente. C'est à la fois "
            "une irrégularité et une information : sur un immeuble de 1900 à rénover, l'étiquette attendue "
            "se situe entre E et G, et un G interdit déjà la location des logements. À réclamer par écrit "
            "avant toute discussion sur le prix",
            "L'agence écrit elle-même « d'importants travaux de rénovation » : il n'y a donc pas de débat sur "
            "l'état, seulement sur le chiffrage. C'est ce qui autorise à conditionner toute offre au devis "
            "d'un artisan, par corps d'état",
            "La fourchette de travaux vaut la totalité de la marge : 250 000 € donnent 40 % de ROI, 350 000 € "
            "en donnent 19,6 %, 480 000 € tuent le dossier. Chaque tranche de 50 000 € de chantier coûte "
            "46 000 € de capacité de prix : c'est l'argument central de la négociation, et il se démontre",
            "La revente se fait sur les tranches 45 à 80 m², qui partent entre 2 941 et 3 196 €/m² à "
            "Saint-Maximin (DVF 2025). La division des plateaux de 93 et 94 m² en deux logements chacun, "
            "plutôt qu'un grand logement par étage, est ce qui capte le mieux cette valeur : à intégrer dans "
            "le chiffrage des travaux",
            "Les 12 lots sont déjà divisés. C'est un avantage concret : la revente lot par lot ne coûte pas "
            "les 5 000 à 10 000 € d'un état descriptif de division, et elle peut être étalée dans le temps "
            "plutôt que d'attendre la fin du chantier",
            "Les deux locaux commerciaux sont vides et la commune compte 13 locaux disponibles à la location. "
            "Ne pas compter plus de 400 € par local, prévoir un an de vacance au démarrage, et exiger la "
            "date d'échéance et le niveau des baux commerciaux voisins pour objectiver la fourchette",
            "Les honoraires de 15 000 € sont à la charge de l'acquéreur, pour un net vendeur de 220 000 €. "
            "C'est un point de négociation : le vendeur affiche 235 000, il encaisse 220 000, et cette "
            "distinction se rappelle systématiquement quand on discute le prix",
            "233 ventes en 2025 pour 17 000 habitants : le marché de revente est profond, ce qui est la "
            "condition pour qu'une opération de quatre lots soit liquide. C'est l'argument qui justifie "
            "d'aller plus loin ici alors qu'on passe sur des communes voisines moins liquides",
            "La variante conservation atteint 5,2 % net avant IS à 350 000 € de travaux avec des loyers "
            "prudents, et 6,3 % aux loyers du marché. Si le chantier se chiffre bien, c'est un dossier "
            "patrimonial autant qu'un dossier marchand de biens : c'est rare dans le secteur",
        ],
        meta=[
            "<strong>Régime fiscal retenu :</strong> SAS à l'IS (15 % sur la plus-value), financement "
            "intégral du prix de revient. La variante conservation est chiffrée en SCI à l'IS avec "
            "amortissement de 90 % du revient sur 30 ans",
            "<strong>Prix d'achat :</strong> 235 000 € honoraires inclus, dont 15 000 € à la charge de "
            "l'acquéreur. Frais d'acquisition calculés à 8 % sur 235 000 €, soit 18 800 €",
            "<strong>Revente retenue :</strong> 849 000 € (2 746 €/m² sur les étages, 2 400 €/m² sur le "
            "grenier, 900 €/m² sur le commerce), 5 % d'honoraires et 24 mois de portage (intérêts à 3,7 %, "
            "taxe foncière, assurances). Fourchette 750 000 à 950 000 €",
            "<strong>Loyers retenus pour la variante conservation :</strong> 3 800 €/mois prudents "
            "(T3 1 100 €, T3 1 100 €, combles 950 €, deux locaux à 400 €) et 4 570 €/mois aux loyers du "
            "marché. Comparables relevés le 22/09/2026",
            "<strong>Charges retenues :</strong> taxe foncière estimée 3 500 €, assurance 700 €, entretien, "
            "TEOM, frais bancaires, provision d'impayés et provision gros travaux 3 000 €, comptabilité "
            "1 500 €. Aucun poste laissé à zéro",
            "<strong>Contrôles à faire avant toute offre :</strong> DPE et diagnostics électricité, plomb et "
            "amiante ; devis de rénovation par corps d'état, toiture et charpente comprises ; plan des niveaux "
            "et surfaces par local ; détail des 12 lots, charges, procès-verbaux et règlement de copropriété ; "
            "avis de taxe foncière et valeur locative cadastrale ; faisabilité de la division des plateaux et "
            "de l'aménagement du grenier en mairie",
            "<strong>Point de méthode :</strong> aucun chiffre de travaux n'entre dans une offre sans devis. "
            "Sur ce dossier, l'écart entre 250 000 et 480 000 € de rénovation vaut 46 000 € de capacité de "
            "prix par tranche de 50 000 €, soit la totalité de la marge. La visite avec un homme de l'art "
            "est la condition d'une offre, pas une formalité",
            "<strong>Rappel de marché (sources au 22/09/2026) :</strong> Saint-Maximin-la-Sainte-Baume, "
            "appartements 2 746 €/m² en médiane (59 ventes DVF 2025), 2 941 €/m² sur 45-60 m² et 3 196 €/m² "
            "sur 60-80 m² ; maisons 2 275 €/m² (174 ventes) ; loyer mesuré 13,8 €/m²/mois (ANIL 2025) soit "
            "6,0 % de rendement brut communal ; locations constatées T3 de 63 à 68 m² entre 700 et 950 € ; "
            "locaux commerciaux de 50 m² entre 390 et 405 €, 13 disponibles dans la commune",
        ],
    )

    c = gen.CONF[SLUG]
    html = gen.TEMPLATE.format(
        titre_court=c['titre_court'], adresse=c['adresse'], date_fr=c['date_fr'],
        source=c['source'], url=c['url'], badge=c['badge'], strategie=c['strategie'],
        fiscal_note=c['fiscal_note'],
        prix=eur(PRIX),
        surface=f"{RDC+ET1+ET2+GRENIER} m²",
        prix_m2=f"{eur(PRIX/400)} €/m²",
        revient=eur(rb['revient']),
        valeur=eur(REVENTE_CENTRALE),
        revenus=eur(3800),
        rdt_revient=fr(rb['roi']), rdt_valeur=fr(rb['roi']),
        note=fr(note), note_cls=fr(note).replace(',', '-'),
        lat=c['lat'], lon=c['lon'], quartier=c['quartier'],
        intro_attr=c['intro_attr'], profil=c['profil'], concl_attr=c['concl_attr'],
        attrs=gen.attr_html(rec), intro_strat=c['intro_strat'], strats=gen.strategy_html(rec),
        rationale=c['rationale'], identite=gen.identite_html(c['identite']),
        projections=f"""  <section class="financial-projections">
    <h2>Compte d'exploitation marchand de biens — prix affiché {eur(PRIX)} €, SAS à l'IS</h2>
    <p class="attractiveness-intro">{lecture}</p>
    <div class="projections-grid">
{chr(10).join(cartes)}
    </div>
    <table class="projection-table compare">
      <thead><tr><th>Indicateur</th><th class="num">Base — 350 000 €</th><th class="num">Optimiste — 250 000 €</th><th class="num">Pessimiste — 480 000 €</th></tr></thead>
      <tbody>
        <tr><td>Prix de revient total</td><td class="num">{eur(rb['revient'])} €</td><td class="num">{eur(ro['revient'])} €</td><td class="num">{eur(rp['revient'])} €</td></tr>
        <tr><td>Plus-value brute</td><td class="num">{eur(rb['pv'])} €</td><td class="num">{eur(ro['pv'])} €</td><td class="num">{eur(rp['pv'])} €</td></tr>
        <tr><td>Plus-value nette après IS</td><td class="num">{eur(rb['nette'])} €</td><td class="num">{eur(ro['nette'])} €</td><td class="num">{eur(rp['nette'])} €</td></tr>
        <tr><td>ROI sur 24 mois</td><td class="num">{fr(rb['roi'])} %</td><td class="num">{fr(ro['roi'])} %</td><td class="num">{fr(rp['roi'])} %</td></tr>
        <tr><td>Revient / revente</td><td class="num">{fr(rb['revient']/REVENTE_CENTRALE,2)}</td><td class="num">{fr(ro['revient']/REVENTE_CENTRALE,2)}</td><td class="num">{fr(rp['revient']/REVENTE_CENTRALE,2)}</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Ce que le prix affiché laisse comme marge.</strong> Le point mort est à <strong>480 000 €</strong> de rénovation : au-delà, la plus-value nette tombe sous 10 000 € pour deux ans de chantier. Pour viser 20 % de ROI sur une revente à {eur(REVENTE_CENTRALE)} €, le prix d'achat maximum est de <strong>325 000 €</strong> avec 250 000 € de travaux, <strong>279 000 €</strong> avec 300 000 €, <strong>233 000 €</strong> avec 350 000 €, <strong>187 000 €</strong> avec 400 000 €. Autrement dit : à 235 000 €, le dossier n'est un marchand de biens que si la rénovation tient sous 350 000 €, toiture et charpente comprises. Chaque tranche de 50 000 € de chantier coûte 46 000 € de capacité de prix.</p>
    </div>
    <h3>ROI selon le coût de la rénovation et le prix de revente</h3>
    <table class="projection-table compare">
      <thead><tr><th>Travaux</th><th class="num">Revente 750 000 €</th><th class="num">Revente 849 000 €</th><th class="num">Revente 950 000 €</th></tr></thead>
      <tbody>
{grille_html}
      </tbody>
    </table>
    <h3>Prix d'achat maximum pour 20 % de ROI, selon la rénovation</h3>
    <table class="projection-table compare">
      <thead><tr><th>Rénovation</th><th class="num">Prix d'achat max</th><th class="num">Écart au prix affiché</th></tr></thead>
      <tbody>
{plafonds_html}
      </tbody>
    </table>
    <h3>Variante conservation : rénover puis louer (SCI à l'IS)</h3>
    <table class="projection-table compare">
      <thead><tr><th>Travaux</th><th>Loyers retenus</th><th class="num">Loyers bruts/an</th><th class="num">EBE</th><th class="num">Net avant IS sur revient</th><th class="num">Net après IS /mois</th></tr></thead>
      <tbody>
{pat_html}
      </tbody>
    </table>
    <p class="attractiveness-intro">Repères de méthode : frais d'acquisition {eur(PRIX*NOTAIRE)} € (8 % du prix affiché, honoraires acquéreur de {eur(HONORAIRES)} € inclus dans le prix), honoraires de revente 5 %, portage de 24 mois (intérêts à 3,7 % sur le prix de revient, taxe foncière estimée 3 500 €/an, assurances), IS à 15 % sur la plus-value. Revente retenue {eur(REVENTE_CENTRALE)} €, ancrée sur les mutations DVF 2025 de Saint-Maximin : 187 m² d'étages à 2 746 €/m² (médiane des appartements), grenier de 96 m² à 2 400 €/m², rez-de-chaussée de 117 m² à 900 €/m². Variante conservation : amortissement de 90 % du revient sur 30 ans, charges de 19 % des loyers plus 3 200 €.</p>
  </section>""",
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

    p = os.path.join(ROOT, 'analyses', 'analyses.json')
    data = json.load(open(p, encoding='utf-8'))
    if SLUG in data:
        data.pop(SLUG)
    lst = data.get('analyses')
    if isinstance(lst, list):
        lst = [x for x in lst if x.get('slug') != SLUG]
        lst.append(rec)
        data['analyses'] = lst
        total = len(lst)
    else:
        data['analyses'][SLUG] = rec
        total = len(data['analyses'])
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  analyses.json : entree ecrite (total {total})")

    print(f"\n  note {note} / 10  |  verdict {verdict}")
    print(f"  base  : revient {eur(rb['revient'])} | PV nette {eur(rb['nette'])} | ROI {fr(rb['roi'])} %")
    print(f"  plafond 20 % ROI : {eur(plafonds_vals[0])} EUR (travaux 250 k) | {eur(plafonds_vals[1])} (300 k) | {eur(plafonds_vals[2])} (350 k)")


if __name__ == '__main__':
    main()
