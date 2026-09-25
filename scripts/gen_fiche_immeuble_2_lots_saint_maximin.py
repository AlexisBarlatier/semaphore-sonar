#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche Immeuble de 2 lots en centre-ville, Saint-Maximin-la-Sainte-Baume (83470).

160 000 EUR, agence Nestenn Saint-Maximin (SeLoger 261QSCIG43MJ) : T2 en duplex de
30 m2 + studio meuble de 17 m2 au 3e etage, deux caves, les deux lots loues.
Branche residentielle (SCI a l'IS). Tout se joue sur la doctrine de rendement du
parc (5 % net avant IS) et sur le montant des deux baux, qui n'est pas communique.
"""
import importlib.util
import json
import os
import sys

ROOT = '/home/alexis-barlatier/Documents/Semaphore-sonar'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from analyse_app import engine, scoring  # noqa: E402

SLUG = "2026-09-24-immeuble-2-lots-centre-saint-maximin"
URL = ("https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/"
       "saint-maximin-la-sainte-baume-83470/261QSCIG43MJ")
DATE = "2026-09-24"
DATE_FR = "24 septembre 2026"

PRIX = 160000.0
NOTAIRE = 0.08
ACTE_EN_MAIN = PRIX * (1 + NOTAIRE)          # 172 800
SURF_ANNONCEE = 70.0
SURF_HAB = 47.0                              # hypothese : 30 (T2 duplex) + 17 (studio)
SEUIL = 0.05                                 # doctrine du parc : 5 % net avant IS
COEF_PLAFOND = SEUIL * (1 + NOTAIRE)         # EBE = 5 % du prix de revient = 5,4 % du prix
# marche DVF 2025 (statistiques reelles, commune 83116)
PRIX_M2_MEDIANE_APP = 2679
PRIX_M2_TRANCHE_30_50 = 2722
VALEUR_RETENUE = round(SURF_HAB * PRIX_M2_TRANCHE_30_50)   # 47 x 2 722 = 127 934
VALEUR_BASSE = 120000.0
VALEUR_HAUTE = 138000.0

# --- Credit (doctrine du parc) : chiffres du modele valide en amont -------------
APPORT_PCT = 0.10
TAUX_CREDIT = 0.037
ASSURANCE_PCT = 0.0034           # assurance emprunteur, sur le capital emprunte
DUREE_ANS = 15
MENS_144 = 1084.42               # mensualite du pret de 144 000 EUR (15 ans, 3,7 %, assurance)
MENS_PAR_EURO = MENS_144 / 144000.0        # 0,00753 EUR/mois par euro emprunte
CHARGES_FIXES_BASE = 2150.0      # TF 900 + charges 400 + PNO 150 + provision 200 + compta 500
PENTE_EBE = 10.8                 # EBE annuel = 10,8 x loyer mensuel - charges fixes (base)
CONTROLES = []                   # (libelle, chiffre du modele, chiffre recalcule, tolerance)


def calcule(libelle, modele, recalcule, tol=1.0):
    """Controle de coherence : le chiffre publie doit sortir du modele."""
    CONTROLES.append((libelle, modele, recalcule, tol))
    assert abs(modele - recalcule) <= tol, (libelle, modele, recalcule)


def mensualite(capital):
    return capital * MENS_PAR_EURO


def mensualite_actuarielle(capital, ans):
    i = TAUX_CREDIT / 12.0
    n = ans * 12
    return capital * i / (1 - (1 + i) ** -n) + capital * ASSURANCE_PCT / 12.0


def cashflow_mensuel(ebe, capital):
    return ebe / 12.0 - mensualite(capital)


def prix_cashflow_nul(ebe):
    """Prix paye tel que 10 % d'apport donnent un cash-flow nul."""
    return (ebe / 12.0) / ((1 - APPORT_PCT) * MENS_PAR_EURO)


def loyer_cashflow_nul(capital, charges_fixes=CHARGES_FIXES_BASE):
    """Loyer mensuel tel que l'EBE couvre l'annuite (charges du scenario de base)."""
    return (12.0 * mensualite(capital) + charges_fixes) / PENTE_EBE


def apport_cashflow_nul(prix, ebe):
    return prix - (ebe / 12.0) / MENS_PAR_EURO


def eur(v, dec=0):
    return f"{v:,.{dec}f}".replace(',', ' ').replace('.', ',')


def fr(v, dec=2):
    return f"{v:.{dec}f}".replace('.', ',')


def calc(loyer, vac, gestion, tf, charges, pno, provision, comptable, imprevu=0.0):
    """Modele valide en amont (chat). Charges = lignes du moteur : TV + charges
    d'immeuble + PNO + (gestion locative + provision travaux) + comptabilite.
    Le seuil de 5 % net avant IS porte sur l'acte en main (prix + 8 % de frais)."""
    brut = loyer * 12.0
    v = brut * vac / 100.0
    g = brut * gestion / 100.0
    fixes = tf + charges + pno + provision + comptable + imprevu
    ebe = brut - v - g - fixes
    is_ = 0.15 * ebe
    net = ebe - is_
    return dict(brut=brut, vac=v, gestion=g, fixes=fixes, provision=provision,
                imprevu=imprevu, ebe=ebe, ebe_mois=ebe / 12.0,
                revient=ACTE_EN_MAIN, is_=is_, net=net, net_mois=net / 12.0,
                rdt_av=ebe / ACTE_EN_MAIN * 100.0, rdt_ap=net / ACTE_EN_MAIN * 100.0,
                rdt_valeur=net / VALEUR_RETENUE * 100.0,
                rdt_av_valeur=ebe / VALEUR_RETENUE * 100.0,
                cap5=ebe / COEF_PLAFOND)


BASE = calc(1070.0, 5.0, 5.0, 900.0, 400.0, 150.0, 200.0, 500.0)
BEST = calc(1200.0, 4.0, 4.0, 800.0, 400.0, 150.0, 100.0, 500.0)
WORST = calc(920.0, 10.0, 6.0, 1100.0, 700.0, 150.0, 300.0, 500.0, 1000.0)


def rec_immeuble_sm():
    nm = eur(SURF_HAB)
    return {
        "slug": SLUG,
        "date_analyse": DATE,
        "date_maj": None,
        "titre": (
            "Immeuble de 2 lots en centre-ville — studio meublé de 17 m² avec mezzanine et T2 en "
            "duplex de 30 m², deux caves — Saint-Maximin-la-Sainte-Baume (83470)"
        ),
        "bien": {
            "type_bien": "immeuble",
            "sous_type": None,
            "type_detail": (
                "Immeuble en centre-ville composé d'un appartement T2 en duplex de 30 m² et, au "
                "3e étage, d'un studio d'environ 17 m² avec mezzanine ; deux caves au niveau de "
                "l'entrée. Les deux logements ont des baux en cours et des compteurs individuels. "
                "L'agence annonce « ne nécessite aucun travaux ». DPE D, GES B, facture énergétique "
                "annoncée entre 670 et 920 €/an. L'annonce ne communique ni le montant d'un seul "
                "loyer, ni la taxe foncière, ni les charges, ni la date d'un diagnostic, ni une "
                "surface Carrez par lot, ni un plan. Immeuble vraisemblablement détenu en totalité "
                "par un seul propriétaire, donc sans copropriété : la structure, la couverture et "
                "la façade sont entièrement à la charge de l'acquéreur"
            ),
            "neuf": False,
            "adresse": {
                "texte": (
                    "Centre-ville, Saint-Maximin-la-Sainte-Baume (83470) — adresse exacte non "
                    "communiquée"
                ),
                "ville": "Saint-Maximin-la-Sainte-Baume",
                "code_postal": "83470",
            },
            "surfaces": {
                "texte": (
                    f"{nm} m² habitables retenus (30 + 17 m²) sur 70 m² annoncés — les deux caves "
                    f"comptent pour le solde"
                ),
                "carrez_m2": SURF_HAB,
            },
            "lots": {
                "count": 2,
                "surface_par_lot_m2": None,
                "nature": (
                    "Deux lots d'habitation : un T2 en duplex de 30 m² et un studio d'environ "
                    "17 m² avec mezzanine au 3e étage, plus deux caves au niveau de l'entrée. "
                    "Compteurs individuels. Aucune surface Carrez par lot, aucun plan, aucun "
                    "diagnostic daté"
                ),
                "lots_distincts": 2,
            },
            "copro": {
                "charges_annuelles_euros": 400.0,
                "charges_source": (
                    "Pas de copropriété : l'immeuble est vraisemblablement détenu en totalité par "
                    "un seul propriétaire. Conséquence directe, et c'est un point du dossier : "
                    "aucune mutualisation des travaux de structure (couverture, façade, réseaux) "
                    "et aucun budget prévisionnel, aucun procès-verbal d'assemblée, aucun état daté "
                    "à examiner — et personne avec qui les partager. Le poste saisi (400 €/an) "
                    "couvre le nettoyage et l'entretien courant des parties communes et des caves, "
                    "portés seuls par le propriétaire"
                ),
            },
            "travaux": {
                "montant_euros": 0.0,
                "nature": (
                    "L'agence annonce « ne nécessite aucun travaux », sans devis, sans diagnostic "
                    "électrique, sans état de la couverture ni de l'humidité des caves. Aucune "
                    "enveloppe n'est donc engagée à l'acquisition : la fiche chiffre le dossier en "
                    "l'état, une provision de 200 €/an est portée au compte d'exploitation, et le "
                    "risque travaux est porté à la matrice de risques — « aucun travaux » est une "
                    "déclaration d'agence, pas un constat de l'acquéreur"
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
                f"160 000 € honoraires à la charge du vendeur, soit 2 286 €/m² sur les 70 m² "
                f"annoncés mais {eur(PRIX/SURF_HAB)} €/m² sur les {nm} m² habitables retenus : "
                f"l'écart entre les deux chiffres, c'est le prix des deux caves comptées comme de "
                f"la surface habitable. La médiane DVF 2025 des appartements de la commune est de "
                f"{eur(PRIX_M2_MEDIANE_APP)} €/m², soit 27 % sous le prix au m² habitable demandé. "
                f"L'annonce vend « une rentabilité immédiate » sans communiquer le montant d'un "
                f"seul loyer. Agence Nestenn Saint-Maximin (SAS IA IMMO, RCS 937733145), mandat "
                f"n°119, référence annonce 252"
            ),
        },
        "marche": {
            "valeur": {
                "basse_euros": VALEUR_BASSE,
                "haute_euros": VALEUR_HAUTE,
                "retenue_euros": VALEUR_RETENUE,
                "source": (
                    f"Mutations DVF 2025 de Saint-Maximin-la-Sainte-Baume : 276 mutations valides "
                    f"dans la commune, dont 59 ventes d'appartements, médiane "
                    f"{eur(PRIX_M2_MEDIANE_APP)} €/m² (premier quartile 2 023, troisième 3 462). "
                    f"Les deux logements (30 et 17 m²) tombent dans la tranche 30-50 m², qui compte "
                    f"5 ventes pour une médiane de {eur(PRIX_M2_TRANCHE_30_50)} €/m² : c'est cette "
                    f"médiane qui est appliquée aux {nm} m² habitables, soit "
                    f"{eur(VALEUR_RETENUE)} €. Sous 30 m² il n'existe que 2 ventes dans l'année "
                    f"(2 609 et 3 462 €/m²) : les valoriser au milieu de cette fourchette "
                    f"ajouterait environ 5 000 € à la valeur du studio, ce qui ne déplace aucune "
                    f"conclusion. Fourchette retenue {eur(VALEUR_BASSE)} à {eur(VALEUR_HAUTE)} €. "
                    f"Le prix affiché est donc à 35 % au-dessus de la valeur de marché des deux "
                    f"lots : il n'y a aucune espérance de plus-value, c'est un actif de rendement pur"
                ),
                "confiance": "moyenne",
            },
            "loyers": [
                {
                    "lot": "Studio d'environ 17 m² avec mezzanine, 3e étage (meublé)",
                    "quantite": 1,
                    "loyer_mensuel_euros": 480.0,
                    "occupe": True,
                    "note": (
                        "Bail en cours, montant non communiqué par l'annonce : 480 € retenus par "
                        "comparaison des annonces relevées le 24/09/2026 à Saint-Maximin-la-Sainte-"
                        "Baume, dont un studio meublé de 18 m² en centre-ville à 485 €. Variantes "
                        "de sensibilité : 520 € en hypothèse favorable, 400 € en hypothèse "
                        "défavorable"
                    ),
                },
                {
                    "lot": "T2 en duplex de 30 m²",
                    "quantite": 1,
                    "loyer_mensuel_euros": 590.0,
                    "occupe": True,
                    "note": (
                        "Bail en cours, montant non communiqué : 590 € retenus. Comparables relevés "
                        "le 24/09/2026 dans la commune : 2 pièces de 33 m² à 680 €, de 45 m² à "
                        "640 €, de 47 m² à 817 € charges comprises, de 56 m² à 660 €, 3 pièces de "
                        "68 m² à 713 €. Le bien est annoncé en duplex, ce qui joue contre la "
                        "surface utile réelle du logement. Variantes : 680 € en hypothèse "
                        "favorable, 520 € en hypothèse défavorable"
                    ),
                },
            ],
            "notes": (
                f"Aucun loyer n'est communiqué par l'annonce, alors qu'elle vend une « rentabilité "
                f"immédiate » : tout le chiffrage repose sur des loyers reconstruits à partir du "
                f"marché. Loyers relevés sur place le 24/09/2026 (annonces actives LeBonCoin, "
                f"Vizzit et SeLoger à Saint-Maximin-la-Sainte-Baume) : studio meublé de 18 m² en "
                f"centre-ville 485 € ; 2 pièces de 33 m² 680 € ; 2 pièces de 45 m² 640 € ; "
                f"2 pièces de 47 m² 817 € charges comprises ; 2 pièces de 56 m² 660 € ; 3 pièces "
                f"de 68 m² 713 € ; maison meublée de 63 m² 772 € ; parking 125 €. Scénario de base "
                f"retenu : studio meublé 480 € et T2 duplex 590 €, soit 1 070 €/mois. Hypothèse "
                f"favorable : 1 200 €/mois (520 + 680). Hypothèse défavorable : 920 €/mois "
                f"(400 + 520). À ce niveau de loyer, la doctrine du parc — 5 % net avant IS — est "
                f"tenue de 5 points près selon la seule ligne des loyers : {fr(BASE['rdt_av'])} % "
                f"avant IS en base, {fr(BEST['rdt_av'])} % en hypothèse favorable, "
                f"{fr(WORST['rdt_av'])} % en hypothèse défavorable. C'est le montant des deux baux "
                f"en cours qui décide du dossier, et il n'est pas dans l'annonce"
            ),
        },
        "hypotheses": {
            "vacance_base_pct": 5.0,
            "vacance_best_pct": 4.0,
            "vacance_worst_pct": 10.0,
            "vacance_justification": (
                "5 % en scénario de base : deux logements de 30 et 17 m² occupés par des baux en "
                "cours, dont la rotation est plus rapide que celle d'un logement familial — le "
                "studio est vraisemblablement loué meublé, et un meublé tourne plus vite qu'un "
                "nue. 10 % en hypothèse défavorable, parce que deux petites surfaces peuvent se "
                "libérer la même année et qu'un studio meublé vide se reloue en quelques semaines "
                "mais avec un budget d'ameublement à renouveler, non chiffré ici et signalé en "
                "risque"
            ),
            "frais_acquisition_euros": round(PRIX * NOTAIRE, 2),
            "frais_divers_euros": 0.0,
            "quote_part_bati_pct": 0.0,
            "fiscalite_commentaire": (
                "Fiscalité année 1 : EBE 9 406 € moins intérêts d'emprunt 5 328 € et dotation aux "
                "amortissements 4 267 € (bâti à 80 % sur 30 ans) : le résultat imposable est un "
                "déficit de 189 €, donc aucun IS l'année 1 et déficit reporté. Convention prudente "
                "retenue pour les rendements nets publiés : IS de 15 % appliqué à l'EBE, sans "
                "amortissement du bâti modélisé, soit 1 411 €/an — c'est la lecture la plus "
                "défavorable. Le seuil de décision de la doctrine du parc porte de toute façon sur "
                "le rendement net AVANT IS"
            ),
            "charges": {
                "taxe_fonciere_annuelle_euros": 900.0,
                "taxe_fonciere_commentaire": (
                    "ESTIMATION 900 €/an — avis non communiqué. Fourchette 700 à 1 100 €/an pour "
                    "un immeuble de deux lots de 47 m² habitables en centre-ville. Le scénario "
                    "défavorable retient 1 100 € : l'inconnue vaut 200 €/an de rendement, soit "
                    "0,7 % brut"
                ),
                "charges_copro_annuelles_euros": 400.0,
                "charges_copro_commentaire": (
                    "Pas de copropriété : aucun budget prévisionnel, aucune charge votée, aucune "
                    "mutualisation. 400 €/an provisionnés pour l'entretien courant des parties "
                    "communes et des caves, porté seul par le propriétaire. Le scénario défavorable "
                    "retient 700 €"
                ),
                "pno_annuelle_euros": 150.0,
                "pno_commentaire": (
                    "Assurance propriétaire non occupant de l'immeuble et de ses deux lots. "
                    "Immeuble ancien en centre-ville, deux logements loués"
                ),
                "entretien_annuel_euros": 842.0,
                "entretien_commentaire": (
                    f"Poste composite, détaillé : gestion locative 642 € (5 % des 12 840 € de "
                    f"loyers bruts) + provision travaux 200 €. Le moteur ne connaît ni la ligne de "
                    f"gestion ni celle de provision gros travaux : les deux sont fondues ici pour "
                    f"que l'EBE publié corresponde au modèle chiffré. La provision automatique du "
                    f"moteur (2,5 % des loyers, soit 321 €/an) est désactivée : l'additionner à la "
                    f"provision explicite compterait deux fois la même cagnotte. Hypothèse "
                    f"favorable : gestion 4 % et provision 100 €, soit 676 €. Hypothèse "
                    f"défavorable : gestion 6 %, provision 300 € et 1 000 € d'imprévu, soit "
                    f"1 962 €"
                ),
                "comptabilite_annuelle_euros": 500.0,
                "comptabilite_commentaire": (
                    "Comptabilité de la SCI à l'IS, deux lots et deux baux : à mutualiser si "
                    "d'autres lots entrent dans la même structure"
                ),
                "provision_desactivee": True,
            },
        },
        "analyse": {
            "branche": "residentiel",
            "type_operation": "locatif",
            "strategie_retenue": {
                "nom": "Conservation en location longue durée des deux lots, avec les baux en cours",
                "code": "ld-nue",
                "lots": 2,
            },
            "strategies_explorees": [
                {
                    "strategie": "Location longue durée des deux lots avec les baux en cours (base)",
                    "lots": 2,
                    "rendement": (
                        f"{fr(BASE['rdt_av'])} % net avant IS sur l'acte en main "
                        f"({eur(BASE['ebe'])} € d'EBE, {eur(BASE['ebe_mois'])} €/mois), "
                        f"{fr(BASE['rdt_ap'])} % après IS"
                    ),
                    "faisabilite": (
                        "immédiate : les deux logements sont loués, compteurs individuels, aucun "
                        "travail annoncé. Il faut obtenir les deux baux avant l'offre"
                    ),
                    "risque": (
                        f"moyen — la doctrine de 5 % n'est tenue qu'avec 1 070 €/mois de loyers ; à "
                        f"920 € elle tombe à {fr(WORST['rdt_av'])} %"
                    ),
                },
                {
                    "strategie": "Location longue durée, loyers hauts de la fourchette (optimiste)",
                    "lots": 2,
                    "rendement": (
                        f"{fr(BEST['rdt_av'])} % net avant IS ({eur(BEST['ebe'])} € d'EBE), "
                        f"{fr(BEST['rdt_ap'])} % après IS, plafond {eur(BEST['cap5'])} €"
                    ),
                    "faisabilite": (
                        "relocation du studio à 520 € et du T2 à 680 €, au niveau des comparables "
                        "les plus chers relevés dans la commune"
                    ),
                    "risque": (
                        "moyen — suppose de relouer les deux lots au haut du marché, avec un "
                        "budget d'ameublement pour le studio"
                    ),
                },
                {
                    "strategie": "Location longue durée, loyers bas et charges lourdes (pessimiste)",
                    "lots": 2,
                    "rendement": (
                        f"{fr(WORST['rdt_av'])} % net avant IS ({eur(WORST['ebe'])} € d'EBE), "
                        f"{fr(WORST['rdt_ap'])} % après IS, plafond {eur(WORST['cap5'])} €"
                    ),
                    "faisabilite": (
                        "loyers 920 €/mois, vacance 10 %, taxe foncière à 1 100 € et 1 000 € "
                        "d'imprévu : c'est le scénario à retenir si un bail est sous-évalué"
                    ),
                    "risque": "élevé — 3,20 % avant IS, sous la doctrine de 5 % : le prix ne passe plus",
                },
                {
                    "strategie": "Achat-rénovation-revente (marchand de biens)",
                    "lots": 2,
                    "rendement": (
                        f"impossible au prix affiché : la valeur de marché des deux lots est de "
                        f"{eur(VALEUR_RETENUE)} € contre un prix de revient de "
                        f"{eur(ACTE_EN_MAIN)} €, soit une marge négative de "
                        f"{eur(ACTE_EN_MAIN - VALEUR_RETENUE)} € avant même les frais de revente"
                    ),
                    "faisabilite": (
                        "deux lots séparés exigeraient un état descriptif de division, payant, "
                        "sur un immeuble aujourd'hui hors copropriété"
                    ),
                    "risque": (
                        "bloquant sur ce plan de sortie — l'actif n'a aucune décote d'entrée à "
                        "capter, il ne se défend que par le rendement"
                    ),
                },
            ],
            "attractivite": [
                {
                    "dimension": "transports",
                    "score": 8,
                    "justification": (
                        "Saint-Maximin-la-Sainte-Baume est à l'entrée de l'autoroute A8, à "
                        "35 minutes d'Aix-en-Provence et 45 minutes de Marseille, avec un bassin "
                        "d'emploi propre (Sainte-Baume, vallée de l'Arc, zone de la Barque) : "
                        "c'est l'une des communes les mieux desservies du centre-Var, et c'est ce "
                        "qui soutient une demande locative à l'année plutôt que saisonnière"
                    ),
                },
                {
                    "dimension": "commerces",
                    "score": 7,
                    "justification": (
                        "Bourg de 17 000 habitants avec une rue commerçante active, un marché, un "
                        "hypermarché et les chaînes nationales. Le bien est en centre-ville, donc "
                        "à la meilleure adresse possible pour deux petites surfaces"
                    ),
                },
                {
                    "dimension": "ecoles",
                    "score": 7,
                    "justification": (
                        "Écoles, collège et lycée sur la commune, plus les établissements d'Aix à "
                        "35 minutes : le profil type du locataire de studio et de T2 en centre-ville"
                    ),
                },
                {
                    "dimension": "securite",
                    "score": 6,
                    "justification": (
                        "Bourg de la Sainte-Baume sans tension particulière, centre ancien en "
                        "cours de repeuplement. Deux caves et un immeuble sans parties communes "
                        "partagées limitent les nuisances de voisinage"
                    ),
                },
                {
                    "dimension": "demande_locative",
                    "score": 6,
                    "justification": (
                        f"Marché locatif réel et documenté le 24/09/2026 : studio meublé de 18 m² "
                        f"à 485 €, 2 pièces de 33 à 56 m² entre 640 et 817 €, 3 pièces de 68 m² à "
                        f"713 €, parking à 125 €. Mais l'offre de 2 pièces est abondante dans la "
                        f"commune, et sept annonces relevées un même jour pour 17 000 habitants "
                        f"signalent un marché locatif fluide, pas tendu : la rotation d'un studio et "
                        f"d'un T2 de 30 m² sera plus fréquente que celle d'un logement familial"
                    ),
                },
                {
                    "dimension": "dynamisme",
                    "score": 6,
                    "justification": (
                        f"276 mutations valides enregistrées dans la commune en 2025, dont "
                        f"59 ventes d'appartements, médiane {eur(PRIX_M2_MEDIANE_APP)} €/m² : la "
                        f"profondeur du marché de revente est un vrai atout de sortie. Mais le "
                        f"prix d'entrée est déjà 35 % au-dessus de la valeur de marché des deux "
                        f"lots, donc sans espérance de plus-value : c'est un actif de rendement pur"
                    ),
                },
            ],
            "risques": [
                {
                    "facteur": "Cash-flow négatif sous crédit : le dossier échoue au critère du parc",
                    "severite": 5,
                    "detail": (
                        f"Le dossier passe la grille de rendement (5,44 % net avant IS) mais pas le "
                        f"critère de cash-flow. À 10 % d'apport, prêt de 144 000 € sur 15 ans à "
                        f"3,7 % avec assurance emprunteur de 0,34 %, la mensualité est de 1 084 €/mois "
                        f"quand l'exploitation dégage 784 €/mois en scénario de base : le cash-flow "
                        f"est de -301 €/mois, soit -3 607 €/an, et il reste négatif dans les trois "
                        f"scénarios (-143 €/mois en hypothèse favorable, -624 €/mois en hypothèse "
                        f"défavorable). Pour que le bien couvre sa mensualité au prix affiché, il "
                        f"faudrait 1 404 €/mois de loyers — 31 % de plus que notre base — ou un prix "
                        f"de 115 649 €, ou un apport de 55 916 € (35 %). L'opération s'enrichit "
                        f"(4,63 % après IS contre 3,7 % de taux d'intérêt) mais elle consomme "
                        f"54 108 € de trésorerie sur quinze ans : elle ne se finance pas seule"
                    ),
                },
                {
                    "facteur": "Les montants des deux baux ne sont pas communiqués",
                    "severite": 5,
                    "detail": (
                        f"C'est le risque numéro un, et il porte tout le dossier. L'annonce vend "
                        f"« une rentabilité immédiate » sans donner un seul loyer, en s'appuyant sur "
                        f"des baux en cours dont le montant, la date, la durée et le type (nue ou "
                        f"meublé) sont inconnus. Le chiffrage publié repose donc sur des loyers "
                        f"reconstruits à partir du marché : {fr(BASE['rdt_av'])} % net avant IS à "
                        f"1 070 €/mois, {fr(BEST['rdt_av'])} % à 1 200 €, {fr(WORST['rdt_av'])} % à "
                        f"920 €. Notre seuil est de 5 % : l'écart entre les deux hypothèses vaut "
                        f"une recommandation. Exiger les deux baux, les dates d'échéance et les "
                        f"dernières quittances AVANT l'offre — s'il s'agit de baux anciens sous le "
                        f"marché, c'est le premier levier de négociation et la réponse au vendeur "
                        f"est non"
                    ),
                },
                {
                    "facteur": "Prix affiché 35 % au-dessus de la valeur de marché des deux lots",
                    "severite": 4,
                    "detail": (
                        f"3 404 €/m² habitables demandés contre une médiane communale de "
                        f"{eur(PRIX_M2_MEDIANE_APP)} €/m² pour les appartements (59 ventes DVF "
                        f"2025) et {eur(PRIX_M2_TRANCHE_30_50)} €/m² sur la tranche 30-50 m² où "
                        f"tombent les deux lots : le rapport coût/valeur ressort à "
                        f"{fr(ACTE_EN_MAIN / VALEUR_RETENUE)}. Aucune espérance de plus-value, donc "
                        f"aucun coussin de sécurité : l'actif ne rend que ce qu'il loue, et il "
                        f"achète au-dessus de sa valeur"
                    ),
                },
                {
                    "facteur": "« Aucun travaux » non vérifié et non documenté",
                    "severite": 4,
                    "detail": (
                        "L'agence affirme qu'aucun travaux n'est nécessaire, sans devis, sans "
                        "diagnostic électrique, sans état de la couverture ni de l'humidité des "
                        "caves — sur un immeuble ancien de centre-ville dont l'acquéreur porte "
                        "seul la structure, la toiture et la façade. Une couverture à reprendre ou "
                        "une façade à ravaler sur cet immeuble coûte plusieurs années de loyer net, "
                        "et rien de tout cela ne figure dans le prix. Visite d'un homme de l'art "
                        "avant l'offre, et devis écrit sur les trois postes qui dérapent : "
                        "électricité, couverture, traitement de l'humidité des caves"
                    ),
                },
                {
                    "facteur": "Pas de copropriété : aucun budget prévisionnel, aucune mutualisation",
                    "severite": 3,
                    "detail": (
                        "L'immeuble est vraisemblablement détenu en totalité par un seul "
                        "propriétaire : il n'existe donc ni charges votées, ni procès-verbal "
                        "d'assemblée, ni état daté, ni budget prévisionnel à examiner — et "
                        "surtout aucun copropriétaire avec qui partager la couverture, la façade "
                        "et les réseaux. Le poste travaux de structure est à 100 % pour "
                        "l'acquéreur, ce qui est le vrai coût caché de cette structure juridique. "
                        "À chiffrer dans la négociation, pas après l'achat"
                    ),
                },
                {
                    "facteur": "Surfaces minuscules : 17 m² et 30 m²",
                    "severite": 3,
                    "detail": (
                        "Deux petites surfaces, c'est une rotation locative élevée : un studio "
                        "change de locataire tous les 12 à 24 mois, avec les frais de relocation, "
                        "les petites vacances et le risque d'impayé qui vont avec. La vacance "
                        "structurelle y est supérieure à celle d'un logement familial, et le "
                        "scénario défavorable retient 10 %. À vérifier aussi : les 30 m² du T2 "
                        "sont annoncés en duplex, ce qui mange de la surface utile au sol"
                    ),
                },
                {
                    "facteur": "Studio vraisemblablement meublé : vacance 8 % et ameublement non chiffré",
                    "severite": 3,
                    "detail": (
                        "Le studio de 17 m² se loue meublé dans ce marché (studio meublé de 18 m² "
                        "à 485 € relevé le 24/09/2026). Un meublé se reloue plus vite mais tourne "
                        "plus vite aussi : la vacance de ce lot est de l'ordre de 8 %, supérieure "
                        "à celle du T2, et le renouvellement du mobilier n'est chiffré nulle part "
                        "(2 000 à 4 000 € par rotation complète). À intégrer dans la provision "
                        "travaux et dans le budget d'entrée"
                    ),
                },
                {
                    "facteur": "Taxe foncière inconnue",
                    "severite": 3,
                    "detail": (
                        "L'avis n'est pas communiqué. Estimation retenue 900 €/an, fourchette 700 "
                        "à 1 100 € pour un immeuble de deux lots de 47 m² habitables. L'écart vaut "
                        "200 €/an, soit 0,7 % brut de rendement : l'avis de taxe foncière est une "
                        "pièce à demander avec les baux, et à vérifier sur la fiche d'imposition "
                        "réelle avant de signer"
                    ),
                },
                {
                    "facteur": "Immeuble ancien en centre-ville, DPE D",
                    "severite": 2,
                    "detail": (
                        "DPE D / GES B : le logement reste louable sans échéance réglementaire "
                        "avant 2034, et la facture énergétique annoncée (670 à 920 €/an) est "
                        "cohérente avec un bâti déjà partiellement rénové. C'est le point "
                        "rassurant du dossier : pas de passif énergétique à porter, pas "
                        "d'interdiction de louer à l'horizon du plan. Reste à obtenir la date du "
                        "diagnostic et à exiger les diagnostics électricité, plomb et amiante, "
                        "non joints à l'annonce"
                    ),
                },
            ],
            "champs_manquants": [
                "les deux baux en cours : montant, date de signature, échéance, type (nue ou meublé)",
                "avis de taxe foncière réel et valeur locative cadastrale",
                "surfaces Carrez par lot et plan des deux logements",
                "diagnostics datés : DPE, électricité, plomb, amiante, état de la couverture et des caves",
                "état descriptif de division ou statut de propriété de l'immeuble (détention en totalité à confirmer)",
                "date d'effet des baux et état des lieux des deux logements",
            ],
        },
    }


def main():
    spec = importlib.util.spec_from_file_location(
        "gen", os.path.join(ROOT, 'scripts', 'gen_fiches_2026-09-10.py'))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)

    rec = rec_immeuble_sm()
    r = engine.compute(rec)
    note, verdict, comp = scoring.note_et_verdict(rec, r)
    rd = r['rendements']

    print(f"  moteur : calculable={r['calculable']} {r['raison']}")
    print(f"  moteur : EBE {eur(r['fiscal']['ebe'])} EUR | IS {eur(r['fiscal']['is_annuel'])} | "
          f"net {eur(r['fiscal']['net_apres_is'])} | CF {eur(r['fiscal']['cf_mensuel_net'])} EUR/mois")
    print(f"  moteur : net/revient {fr(rd['net_sur_revient_pct'])} % | net/achat "
          f"{fr(rd['net_sur_achat_pct'])} % | net/valeur {fr(rd['net_sur_valeur_pct'])} % | "
          f"ratio {fr(r['ratio_cout_valeur'])}")
    print(f"  modele : base  EBE {eur(BASE['ebe'])} | av {fr(BASE['rdt_av'])} % | ap "
          f"{fr(BASE['rdt_ap'])} % | plafond {eur(BASE['cap5'])}")
    print(f"  modele : best  EBE {eur(BEST['ebe'])} | av {fr(BEST['rdt_av'])} % | ap "
          f"{fr(BEST['rdt_ap'])} % | plafond {eur(BEST['cap5'])}")
    print(f"  modele : worst EBE {eur(WORST['ebe'])} | av {fr(WORST['rdt_av'])} % | ap "
          f"{fr(WORST['rdt_ap'])} % | plafond {eur(WORST['cap5'])}")
    print(f"  note {note}/10 | verdict {verdict} | {comp}")

    # Controle de calibration : le moteur doit rendre exactement l'EBE du modele
    assert abs(r['fiscal']['ebe'] - BASE['ebe']) < 0.01, (r['fiscal']['ebe'], BASE['ebe'])
    assert round(BASE['ebe']) == 9406 and round(BEST['ebe']) == 11298 and round(WORST['ebe']) == 5524
    assert round(BASE['cap5']) == 174185 and round(BEST['cap5']) == 209222 and round(WORST['cap5']) == 102289
    assert round(BASE['rdt_av'] * 100) == 544 and round(BASE['rdt_ap'] * 100) == 463
    assert verdict == "negocier", verdict

    def ligne(label, val, cls=""):
        c = f' class="{cls}"' if cls else ''
        return f'            <tr{c}><td>{label}</td><td class="num">{val}</td></tr>'

    def compte(d, vac, gestion, tf, charges, pno, provision, comptable, imprevu, titre, sous):
        rows = [
            ligne("Loyers bruts annuels", f"{eur(d['brut'])} €"),
            ligne(f"Vacance locative {fr(vac, 0)} %", f"-{eur(d['vac'])} €"),
            ligne(f"Gestion locative {fr(gestion, 0)} %", f"-{eur(d['gestion'])} €"),
            ligne("Taxe foncière (estimation)", f"-{eur(tf)} €"),
            ligne("Charges d'immeuble (pas de copropriété)", f"-{eur(charges)} €"),
            ligne("Assurance PNO", f"-{eur(pno)} €"),
            ligne("Provision travaux et ameublement", f"-{eur(provision)} €"),
            ligne("Comptabilité SCI à l'IS", f"-{eur(comptable)} €"),
        ]
        if imprevu:
            rows.append(ligne("Imprévu travaux", f"-{eur(imprevu)} €"))
        rows += [
            ligne("Excédent brut d'exploitation", f"{eur(d['ebe'])} €", "subtotal"),
            ligne("IS 15 % sur l'EBE (aucun amortissement modélisé)", f"-{eur(d['is_'])} €"),
            ligne("Net après IS", f"{eur(d['net'])} €", "highlight"),
            ligne("EBE mensuel", f"{eur(d['ebe_mois'])} €/mois"),
            ligne("Rendement net avant IS sur l'acte en main", f"{fr(d['rdt_av'])} %", "highlight"),
            ligne("Rendement net après IS sur l'acte en main", f"{fr(d['rdt_ap'])} %"),
            ligne(f"Rendement net après IS sur la valeur ({eur(VALEUR_RETENUE)} €)",
                  f"{fr(d['rdt_valeur'])} %"),
            ligne("Prix d'achat tenant 5 % net avant IS", f"{eur(d['cap5'])} €"),
        ]
        return f"""      <div class="projection-card scenario-{titre}">
        <h3>{sous}</h3>
        <p class="scenario-subtitle">{eur(d['brut']/12)} €/mois de loyers, vacance {fr(vac,0)} % — EBE {eur(d['ebe_mois'])} €/mois</p>
        <table class="projection-table"><tbody>
{chr(10).join(rows)}
        </tbody></table>
      </div>"""

    cartes = [
        compte(BASE, 5.0, 5.0, 900.0, 400.0, 150.0, 200.0, 500.0, 0.0, "base",
               "Base — loyers reconstruits 1 070 €/mois"),
        compte(BEST, 4.0, 4.0, 800.0, 400.0, 150.0, 100.0, 500.0, 0.0, "optimiste",
               "Optimiste — loyers 1 200 €/mois (520 + 680)"),
        compte(WORST, 10.0, 6.0, 1100.0, 700.0, 150.0, 300.0, 500.0, 1000.0, "pessimiste",
               "Pessimiste — loyers 920 €/mois (400 + 520)"),
    ]

    # Sensibilite du plafond d'achat aux seuls loyers (charges de base)
    sens_rows = []
    for loy, lab in ((900.0, "hypothèse basse"), (1000.0, "sous la base"),
                     (1070.0, "scénario de base"), (1150.0, "hypothèse haute")):
        d = calc(loy, 5.0, 5.0, 900.0, 400.0, 150.0, 200.0, 500.0)
        sens_rows.append(
            f'        <tr><td>{eur(loy)} €/mois</td><td>{lab}</td>'
            f'<td class="num">{eur(d["ebe"])} €</td><td class="num">{fr(d["rdt_av"])} %</td>'
            f'<td class="num">{eur(d["cap5"])} €</td>'
            f'<td class="num">{eur(d["cap5"] - PRIX)} €</td></tr>')
    sens_html = "\n".join(sens_rows)

    # ------------------------------------------------------------------
    # Cash-flow apres credit (doctrine du parc) : chiffres du modele amont
    # ------------------------------------------------------------------
    CAP_BASE = PRIX * (1 - APPORT_PCT)                  # 144 000
    MENS_BASE = mensualite(CAP_BASE)
    CF_BASE = cashflow_mensuel(BASE['ebe'], CAP_BASE)
    CF_BASE_AN = CF_BASE * 12.0
    CALC = {
        'affiche': (PRIX, CAP_BASE, BASE['ebe'], CF_BASE, CF_BASE_AN),
        'offre': (148000.0, 148000.0 * (1 - APPORT_PCT), BASE['ebe'], None, None),
        'plafond': (165000.0, 165000.0 * (1 - APPORT_PCT), BASE['ebe'], None, None),
    }
    for k in ('offre', 'plafond'):
        p_, cap_, ebe_, _, _ = CALC[k]
        cf_ = cashflow_mensuel(ebe_, cap_)
        CALC[k] = (p_, cap_, ebe_, cf_, cf_ * 12.0)
    CF_BEST = cashflow_mensuel(BEST['ebe'], CAP_BASE)
    CF_WORST = cashflow_mensuel(WORST['ebe'], CAP_BASE)

    # Controles : chaque chiffre publie doit sortir du modele
    calcule("mensualite 144 000", 1084.0, MENS_BASE, 1.0)
    calcule("cash-flow base /mois", -301.0, CF_BASE, 1.0)
    calcule("cash-flow base /an", -3607.0, CF_BASE_AN, 1.0)
    calcule("cash-flow a l'offre 148 000", -219.0, CALC['offre'][3], 1.0)
    calcule("cash-flow au plafond 165 000", -334.0, CALC['plafond'][3], 1.0)
    calcule("cash-flow optimistic", -143.0, CF_BEST, 1.0)
    calcule("cash-flow pessimiste", -624.0, CF_WORST, 1.0)
    calcule("loyers cash-flow nul (prix affiche)", 1404.0, loyer_cashflow_nul(CAP_BASE), 1.0)
    calcule("prix cash-flow nul a 1 070 EUR", 115649.0, prix_cashflow_nul(BASE['ebe']), 5.0)
    calcule("prix cash-flow nul a 1 200 EUR", 132911.0,
            prix_cashflow_nul(calc(1200.0, 5.0, 5.0, 900.0, 400.0, 150.0, 200.0, 500.0)['ebe']), 10.0)
    calcule("apport cash-flow nul a 148 000", 43916.0, apport_cashflow_nul(148000.0, BASE['ebe']), 5.0)
    calcule("apport cash-flow nul a 160 000", 55916.0, apport_cashflow_nul(PRIX, BASE['ebe']), 5.0)
    calcule("apport cash-flow nul a 165 000", 60916.0, apport_cashflow_nul(165000.0, BASE['ebe']), 5.0)
    calcule("mensualite 20 ans", 891.0, mensualite_actuarielle(CAP_BASE, 20), 1.0)
    calcule("mensualite 25 ans", 777.0, mensualite_actuarielle(CAP_BASE, 25), 2.0)
    calcule("tresorerie consommee sur 15 ans", -54108.0, CF_BASE_AN * 15, 15.0)
    calcule("service de la dette / capital (%)", 9.0,
            12 * MENS_BASE / CAP_BASE * 100.0, 0.1)
    calcule("rendement sur le capital emprunte (%)", 6.5, BASE['ebe'] / CAP_BASE * 100.0, 0.1)

    def cf_carte(d, titre, sous):
        return f"""      <div class="projection-card scenario-{titre}">
        <h3>{sous}</h3>
        <p class="scenario-subtitle">Prêt {eur(CAP_BASE)} € sur 15 ans — apport 10 %</p>
        <table class="projection-table"><tbody>
            <tr><td>Loyers bruts mensuels</td><td class="num">{eur(d['brut']/12)} €</td></tr>
            <tr><td>Net d'exploitation mensuel (EBE)</td><td class="num">{eur(d['ebe_mois'])} €</td></tr>
            <tr><td>Mensualité de crédit (assurance incluse)</td><td class="num">-{eur(MENS_BASE)} €</td></tr>
            <tr class="highlight"><td>Cash-flow mensuel</td><td class="num">{eur(d['ebe']/12 - MENS_BASE)} €</td></tr>
            <tr><td>Cash-flow annuel</td><td class="num">{eur((d['ebe']/12 - MENS_BASE) * 12)} €</td></tr>
        </tbody></table>
      </div>"""

    cf_cartes = [
        cf_carte(BASE, "base", "Base — loyers 1 070 €/mois"),
        cf_carte(BEST, "optimiste", "Optimiste — loyers 1 200 €/mois"),
        cf_carte(WORST, "pessimiste", "Pessimiste — loyers 920 €/mois"),
    ]

    cf_prix_rows = []
    for cle, lab in (('offre', "148 000 € — notre offre"),
                     ('affiche', "160 000 € — prix affiché"),
                     ('plafond', "165 000 € — plafond de négociation")):
        p_, cap_, ebe_, cf_, cf_an = CALC[cle]
        cf_prix_rows.append(
            f'        <tr><td>{lab}</td><td class="num">{eur(cap_)} €</td>'
            f'<td class="num">{eur(mensualite(cap_))} €</td>'
            f'<td class="num">{eur(cf_)} €/mois</td><td class="num">{eur(cf_an)} €/an</td>'
            f'<td class="num">{eur(loyer_cashflow_nul(cap_))} €/mois</td></tr>')
    cf_prix_html = "\n".join(cf_prix_rows)

    cf_besoins_rows = [
        ("Loyers mensuels pour un cash-flow nul au prix affiché",
         f"{eur(loyer_cashflow_nul(CAP_BASE))} €/mois",
         f"contre {eur(1070)} €/mois retenus, soit +{fr(loyer_cashflow_nul(CAP_BASE)/1070.0*100.0 - 100.0, 0)} %"),
        ("Prix d'achat à cash-flow nul, 10 % d'apport, loyers de 1 070 €/mois",
         f"{eur(prix_cashflow_nul(BASE['ebe']))} €",
         f"{fr(prix_cashflow_nul(BASE['ebe'])/PRIX*100.0 - 100.0, 1)} % sous le prix affiché"),
        ("Prix d'achat à cash-flow nul, 10 % d'apport, loyers de 1 200 €/mois",
         f"{eur(prix_cashflow_nul(calc(1200.0, 5.0, 5.0, 900.0, 400.0, 150.0, 200.0, 500.0)['ebe']))} €",
         "charges du scénario de base, loyers de l'hypothèse favorable"),
        ("Apport pour un cash-flow nul à 148 000 €",
         f"{eur(apport_cashflow_nul(148000.0, BASE['ebe']))} €",
         f"{fr(apport_cashflow_nul(148000.0, BASE['ebe'])/148000.0*100.0, 0)} % du prix"),
        ("Apport pour un cash-flow nul à 160 000 €",
         f"{eur(apport_cashflow_nul(PRIX, BASE['ebe']))} €",
         f"{fr(apport_cashflow_nul(PRIX, BASE['ebe'])/PRIX*100.0, 0)} % du prix"),
        ("Apport pour un cash-flow nul à 165 000 €",
         f"{eur(apport_cashflow_nul(165000.0, BASE['ebe']))} €",
         f"{fr(apport_cashflow_nul(165000.0, BASE['ebe'])/165000.0*100.0, 0)} % du prix"),
        ("Durée 15 ans (plafond de la banque)",
         f"{eur(mensualite_actuarielle(CAP_BASE, 15))} €/mois",
         f"cash-flow {eur(BASE['ebe']/12 - mensualite_actuarielle(CAP_BASE, 15))} €/mois"),
        ("Durée 20 ans",
         f"{eur(mensualite_actuarielle(CAP_BASE, 20))} €/mois",
         f"cash-flow {eur(BASE['ebe']/12 - mensualite_actuarielle(CAP_BASE, 20))} €/mois"),
        ("Durée 25 ans",
         f"{eur(mensualite_actuarielle(CAP_BASE, 25))} €/mois",
         f"cash-flow {eur(BASE['ebe']/12 - mensualite_actuarielle(CAP_BASE, 25))} €/mois"),
    ]
    cf_besoins_html = "\n".join(
        f'        <tr><td>{a}</td><td class="num">{b}</td><td>{c}</td></tr>'
        for a, b, c in cf_besoins_rows)

    INTERETS_AN1 = CAP_BASE * TAUX_CREDIT
    # Fiscalite annee 1, recalculee depuis l'EBE du modele :
    #   9 406 (loyers 12 840 - vacance 642 - gestion 642 - charges 2 150)
    #   - 5 328 d'interets - 4 267 de dotation = deficit de 189 EUR -> aucun IS.
    IS_AMORT_MODELE = 4267.0
    IS_RESULTAT_MODELE = round(BASE['ebe'] - INTERETS_AN1 - IS_AMORT_MODELE, 2)
    IS_IMPOT_MODELE = 0.0
    IS_CONVENTION_EBE = round(BASE['ebe'] * 0.15, 2)
    cf_section = f"""  <section class="financial-projections">
    <h2>Cash-flow après crédit — service de la dette, apport et durée</h2>
    <p class="attractiveness-intro"><strong>Hypothèses de crédit (doctrine du parc) :</strong> apport 10 %, frais de notaire assumés à part, prêt de {eur(CAP_BASE)} € sur 15 ans à 3,7 %, assurance emprunteur 0,34 % du capital. Mensualité <strong>{eur(MENS_BASE)} €/mois</strong>, soit <strong>0,00753 € par euro emprunté</strong>. Comparée au net d'exploitation de {eur(BASE['ebe_mois'])} €/mois du scénario de base, cette mensualité ne peut pas être couverte.</p>
    <div class="projections-grid">
{chr(10).join(cf_cartes)}
    </div>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>La conclusion est nette : ce dossier n'est pas finançable en l'état.</strong> Au prix affiché et avec 10 % d'apport, il manque <strong>{eur(abs(CF_BASE))} €/mois</strong> ({eur(abs(CF_BASE_AN))} €/an) au bien pour payer sa mensualité, et le déficit subsiste dans les trois scénarios de loyers : {eur(CF_BEST)} €/mois en hypothèse favorable, {eur(CF_WORST)} €/mois en hypothèse défavorable. Le rendement de {fr(BASE['rdt_ap'])} % après IS reste supérieur au taux du crédit de 3,7 %, donc l'opération s'enrichit — mais elle consomme {eur(abs(CF_BASE_AN * DUREE_ANS))} € de trésorerie sur quinze ans, et c'est la trésorerie qui décide d'un achat.</p>
    </div>
    <table class="projection-table compare">
      <thead><tr><th>Prix payé</th><th class="num">Capital emprunté (90 %)</th><th class="num">Mensualité</th><th class="num">Cash-flow</th><th class="num">Cash-flow annuel</th><th class="num">Loyers requis pour un cash-flow nul</th></tr></thead>
      <tbody>
{cf_prix_html}
      </tbody>
    </table>
    <h3>Ce qu'il faudrait pour un cash-flow nul</h3>
    <table class="projection-table compare">
      <thead><tr><th>Levier</th><th class="num">Valeur</th><th>Lecture</th></tr></thead>
      <tbody>
{cf_besoins_html}
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Fiscalité année 1 — l'amortissement ne crée pas de trésorerie.</strong> Intérêts d'emprunt {eur(INTERETS_AN1)} €, dotation aux amortissements {eur(IS_AMORT_MODELE)} €, le résultat imposable de l'année 1 est un <strong>déficit de {eur(abs(IS_RESULTAT_MODELE))} €</strong> : <strong>aucun impôt l'année 1</strong>, et le déficit se reporte. Le moteur retient par ailleurs, pour les rendements nets publiés, la convention la plus prudente : IS de 15 % appliqué à l'EBE, soit {eur(IS_CONVENTION_EBE)} €/an, sans aucun amortissement du bâti. Dans les deux lectures, l'impôt n'est pas le sujet — il ne paie pas la mensualité, et c'est la première confusion à éviter sur un dossier d'exploitation. L'amortissement non plus ne fait pas disparaître l'impôt : il le reporte sur la plus-value de sortie, calculée sur la valeur nette comptable.</p>
      <p class="attractiveness-intro"><strong>Le service de la dette vaut 9,0 % du capital emprunté par an</strong> (intérêts, capital et assurance) alors que le bien rapporte <strong>6,5 % sur ce même capital</strong> : l'écart de 2,5 points, c'est la mensualité que le bien ne couvre pas. Ce n'est pas un dossier mort — l'actif s'apprécie et la dette se rembourse —, mais c'est un dossier qui demande {eur(abs(CF_BASE_AN * DUREE_ANS))} € de trésorerie sur quinze ans, ou un apport de {fr(apport_cashflow_nul(PRIX, BASE['ebe'])/PRIX*100.0, 0)} % au lieu de 10 %, ou un prix de {eur(prix_cashflow_nul(BASE['ebe']))} € au lieu de {eur(PRIX)} €. Trois réponses possibles, aucune gratuite.</p>
    </div>
  </section>"""

    print("\n  Controles des chiffres de cash-flow (modele amont vs recalcul du script) :")
    for lab, mod, rec_, tol in CONTROLES:
        print(f"    {lab:<50} amont {mod:>12,.2f} | recalcule {rec_:>12,.2f} | "
              f"ecart {abs(mod - rec_):.2f} (tol {tol})")
    print(f"  Fiscalite annee 1 : EBE {eur(BASE['ebe'])} - interets {eur(INTERETS_AN1)} "
          f"- dotation {eur(IS_AMORT_MODELE)} = {eur(IS_RESULTAT_MODELE)} EUR, soit un deficit "
          f"et aucun IS l'annee 1. Convention prudente publiee par ailleurs : IS de 15 % sur "
          f"l'EBE = {eur(IS_CONVENTION_EBE)} EUR/an.")

    lecture = (
        f"C'est l'adresse qui est bonne, et le prix qui ne l'est pas. Un immeuble entier en "
        f"centre-ville de Saint-Maximin, deux logements déjà loués, des compteurs individuels, un "
        f"DPE D qui ne porte aucune échéance avant 2034 et des caves : sur le papier, c'est le "
        f"profil du dossier de rendement qu'on cherche. Sauf que les 70 m² annoncés à 160 000 € "
        f"comprennent les deux caves. La surface habitable est de 47 m², et le prix passe alors à "
        f"{eur(PRIX/SURF_HAB)} €/m² là où la médiane DVF 2025 des appartements de la commune est de "
        f"{eur(PRIX_M2_MEDIANE_APP)} €/m² : 27 % au-dessus, sans aucune décote d'entrée à capter. "
        f"Reste le rendement, qui est la seule raison d'acheter ce bien — et il se joue sur une "
        f"ligne que l'annonce ne donne pas. Avec 1 070 €/mois de loyers reconstruits à partir du "
        f"marché relevé sur place, l'excédent brut d'exploitation ressort à {eur(BASE['ebe'])} €, "
        f"soit {fr(BASE['rdt_av'])} % net avant IS sur l'acte en main : le seuil de 5 % de la "
        f"doctrine est tenu, de 44 points de base. À 920 €/mois, la même opération tombe à "
        f"{fr(WORST['rdt_av'])} % et le plafond d'achat à {eur(WORST['cap5'])} €, sous le prix "
        f"affiché. À 1 200 €/mois, elle monte à {fr(BEST['rdt_av'])} % et le plafond à "
        f"{eur(BEST['cap5'])} €. Autrement dit, toute la marge du dossier est dans deux baux que "
        f"personne n'a vus : l'annonce vend une « rentabilité immédiate » sans en donner le "
        f"chiffre, et c'est exactement la première pièce à exiger."
    )

    gen.LECTURE[SLUG] = lecture
    gen.RECS[SLUG] = rec
    gen.CONF[SLUG] = dict(
        titre_court="Immeuble 2 lots, centre-ville — Saint-Maximin (83470)",
        adresse=(
            "Centre-ville, Saint-Maximin-la-Sainte-Baume (83470) — immeuble de 2 lots : T2 en "
            "duplex de 30 m² et studio d'environ 17 m² avec mezzanine au 3e étage, deux caves — "
            "adresse exacte non communiquée"
        ),
        date_fr=DATE_FR,
        source=(
            "SeLoger — annonce 261QSCIG43MJ (agence Nestenn Saint-Maximin, SAS IA IMMO, "
            "RCS 937733145 — mandat n°119, référence annonce 252)"
        ),
        url=URL,
        badge="Investissement locatif",
        strategie=(
            "Conservation en location longue durée des deux lots, avec les baux en cours — "
            "hypothèses haute et basse de loyers chiffrées en comparaison"
        ),
        fiscal_note=(
            "SCI à l'IS : IS de 15 % appliqué à l'EBE, sans amortissement du bâti modélisé "
            "(aucune ventilation par composant établie) — seuil de décision : 5 % net avant IS"
        ),
        lat="43.4528", lon="5.8619",
        quartier=(
            "Saint-Maximin-la-Sainte-Baume (83470) — centre-ville, 17 000 habitants, autoroute A8 "
            "à 5 minutes, Aix-en-Provence à 35 minutes"
        ),
        intro_attr=(
            f"Saint-Maximin-la-Sainte-Baume est un bourg de <strong>17 000 habitants</strong> à "
            f"l'entrée de l'autoroute A8, à 35 minutes d'Aix-en-Provence : rue commerçante, "
            f"marché, écoles, collège et lycée, et un bassin d'emploi qui fait vivre la commune à "
            f"l'année. Le marché est documenté : <strong>276 mutations valides en 2025</strong> "
            f"selon la base DVF, dont <strong>59 ventes d'appartements</strong> à une médiane de "
            f"<strong>{eur(PRIX_M2_MEDIANE_APP)} €/m²</strong> (premier quartile 2 023, troisième "
            f"3 462). La tranche 30-50 m², où tombent les deux lots, affiche une médiane de "
            f"<strong>{eur(PRIX_M2_TRANCHE_30_50)} €/m² sur 5 ventes</strong> ; sous 30 m², il "
            f"n'existe que deux ventes dans l'année (2 609 et 3 462 €/m²). Côté locatif, les "
            f"annonces relevées sur place le 24/09/2026 donnent un studio meublé de 18 m² à 485 €, "
            f"des 2 pièces de 640 à 817 € et des 3 pièces de 68 m² à 713 € : un marché fluide, "
            f"avec de l'offre, mais un vrai marché de locataires à l'année."
        ),
        profil=(
            "un investisseur de rendement qui cherche un actif déjà loué, sans travaux, à tenir "
            "dans la durée : deux logements de 30 et 17 m², deux baux en cours, des compteurs "
            "individuels et une structure sans copropriété. Ce n'est pas un dossier de plus-value "
            "— le prix est 35 % au-dessus de la valeur de marché des deux lots — ni un dossier de "
            "promotion : c'est un dossier de loyer, et il ne vaut que par le montant des baux"
        ),
        concl_attr=(
            f"Adéquation moyenne (6,7/10). L'emplacement, la structure et l'état déclaré sont de "
            f"vrais atouts : plein centre, deux logements déjà loués donc aucun délai de "
            f"commercialisation, DPE D sans échéance avant 2034, compteurs individuels et pas de "
            f"copropriété à financer. Deux éléments plombent le score. D'abord le prix : "
            f"{eur(PRIX/SURF_HAB)} €/m² habitables contre {eur(PRIX_M2_MEDIANE_APP)} €/m² de "
            f"médiane communale, soit 35 % au-dessus de la valeur de marché des deux lots une "
            f"fois les frais d'acquisition comptés — il n'y a aucune marge à capter à la revente. "
            f"Ensuite et surtout l'inconnue des loyers : "
            f"l'annonce vend une « rentabilité immédiate » sans communiquer un seul montant, et "
            f"c'est cette ligne qui décide si le dossier est conforme à notre seuil de 5 % ou non"
        ),
        intro_strat=(
            "Quatre lectures ont été testées : la conservation en location longue durée dans trois "
            "hypothèses de loyers (base à 1 070 €/mois, optimiste à 1 200 €, pessimiste à 920 €) et "
            "l'achat-rénovation-revente. C'est la première qui porte le dossier, et c'est la "
            "quatrième qui le condamne : il n'y a aucune décote d'entrée à capter."
        ),
        rationale=(
            f"Le scénario de référence : loyers reconstruits à partir du marché relevé sur place le "
            f"24/09/2026 — studio meublé 480 € et T2 duplex 590 €, soit 1 070 €/mois —, vacance "
            f"5 %, gestion locative 5 %, taxe foncière estimée 900 €, charges d'immeuble 400 €, "
            f"assurance 150 €, provision travaux 200 € et comptabilité 500 €. L'excédent brut "
            f"d'exploitation ressort à <strong>{eur(BASE['ebe'])} €</strong> "
            f"({eur(BASE['ebe_mois'])} €/mois) et le rendement net avant IS sur l'acte en main de "
            f"<strong>{fr(BASE['rdt_av'])} %</strong> : la doctrine du parc, 5 % net avant IS, est "
            f"tenue — mais de 44 points de base seulement, et le rendement après IS tombe à "
            f"{fr(BASE['rdt_ap'])} %.<br><br>"
            f"Toute la marge tient dans la ligne des loyers, qui n'est pas documentée. À "
            f"<strong>920 €/mois</strong> — un bail sous-évalué, une vacance de 10 %, une taxe "
            f"foncière à 1 100 € et 1 000 € d'imprévu — l'EBE tombe à {eur(WORST['ebe'])} €, le "
            f"rendement à <strong>{fr(WORST['rdt_av'])} %</strong> et le prix qui tiendrait notre "
            f"seuil à <strong>{eur(WORST['cap5'])} €</strong>, très en dessous du prix affiché. À "
            f"<strong>1 200 €/mois</strong> — studio à 520 €, T2 à 680 €, au niveau des "
            f"comparables les plus chers de la commune — l'EBE monte à {eur(BEST['ebe'])} €, le "
            f"rendement à <strong>{fr(BEST['rdt_av'])} %</strong> et le plafond à "
            f"<strong>{eur(BEST['cap5'])} €</strong>. Entre les deux hypothèses, "
            f"{eur(BEST['cap5'] - WORST['cap5'])} € de capacité de prix : c'est le montant exact "
            f"de l'inconnue que porte cette annonce.<br><br>"
            f"Ce que le dossier n'est pas, en revanche : une opération de revente. Avec un prix de "
            f"revient de {eur(ACTE_EN_MAIN)} € (acte en main) pour une valeur de marché de "
            f"{eur(VALEUR_RETENUE)} € sur les deux lots, l'achat-rénovation-revente affiche une "
            f"marge négative de {eur(ACTE_EN_MAIN - VALEUR_RETENUE)} € avant même les frais de "
            f"revente. C'est un actif de rendement pur, à son prix ou au-dessus de son prix."
        ),
        identite=[
            ("Adresse", "Centre-ville, Saint-Maximin-la-Sainte-Baume (83470) — adresse exacte non "
                        "communiquée"),
            ("Vendeur / intermédiaire", "Agence Nestenn Saint-Maximin (SAS IA IMMO, "
                                        "RCS 937733145) — annonce SeLoger 261QSCIG43MJ, mandat "
                                        "n°119, référence annonce 252"),
            ("Composition", "Immeuble de deux lots : appartement T2 en duplex de 30 m² et, au "
                            "3e étage, studio d'environ 17 m² avec mezzanine ; deux caves au "
                            "niveau de l'entrée. Compteurs individuels"),
            ("Statut", "<strong>Pas de copropriété</strong> : immeuble vraisemblablement détenu en "
                       "totalité par un seul propriétaire. Aucune charge votée, aucun budget "
                       "prévisionnel, aucun procès-verbal — et aucune mutualisation des travaux de "
                       "structure, de couverture et de façade, entièrement à la charge de "
                       "l'acquéreur"),
            ("Surfaces", f"70 m² annoncés (2 286 €/m²), dont les deux caves. <strong>{eur(SURF_HAB)} m² "
                         f"habitables retenus</strong> (30 + 17 m²), soit "
                         f"<strong>{eur(PRIX/SURF_HAB)} €/m² habitable</strong>. Aucune surface Carrez "
                         f"par lot, aucun plan"),
            ("Occupation", "Les deux logements sont <strong>loués</strong> (baux en cours annoncés). "
                           "<strong>Montants, dates de signature et échéances non communiqués</strong> — "
                           "c'est l'inconnue centrale du dossier"),
            ("DPE / GES", "DPE D / GES B — facture énergétique annoncée 670 à 920 €/an. Le logement "
                          "reste louable sans échéance avant 2034 : pas de passif énergétique à porter. "
                          "Date du diagnostic non communiquée, diagnostics électricité, plomb et "
                          "amiante non joints"),
            ("Travaux", "« Ne nécessite aucun travaux » selon l'agence, <strong>sans devis, sans "
                        "diagnostic et sans état de la couverture ni des caves</strong>. Le chiffrage "
                        "retient 0 € de travaux à l'acquisition, une provision de 200 €/an en "
                        "exploitation et le risque en matrice : à vérifier par un homme de l'art"),
            ("Prix affiché", f"<strong>160 000 €</strong>, honoraires à la charge du vendeur — "
                             f"2 286 €/m² sur les 70 m² annoncés, "
                             f"<strong>{eur(PRIX/SURF_HAB)} €/m² sur les {eur(SURF_HAB)} m² "
                             f"habitables</strong>"),
            ("Valeur de marché retenue", f"<strong>{eur(VALEUR_RETENUE)} €</strong> "
                                         f"({eur(PRIX_M2_TRANCHE_30_50)} €/m² sur 47 m²), fourchette "
                                         f"{eur(VALEUR_BASSE)} à {eur(VALEUR_HAUTE)} € — médiane DVF "
                                         f"2025 de la tranche 30-50 m² de la commune, 5 ventes ; "
                                         f"médiane communale des appartements "
                                         f"{eur(PRIX_M2_MEDIANE_APP)} €/m² sur 59 ventes"),
            ("Loyers retenus", f"<strong>1 070 €/mois</strong> : studio meublé de 17 m² à 480 € et T2 "
                               f"duplex de 30 m² à 590 €. Aucun loyer communiqué par l'annonce — "
                               f"relevés du 24/09/2026 : studio meublé 18 m² à 485 €, 2 pièces de "
                               f"33 m² à 680 €, de 45 m² à 640 €, de 47 m² à 817 € CC, de 56 m² à "
                               f"660 €, 3 pièces de 68 m² à 713 €, maison meublée 63 m² à 772 €, "
                               f"parking à 125 €"),
            ("Charges annuelles", "Taxe foncière <strong>estimée 900 €</strong> (avis non communiqué, "
                                  "fourchette 700 à 1 100 €) + charges d'immeuble 400 € (pas de "
                                  "copropriété) + PNO 150 € + gestion locative et provision travaux "
                                  "842 € + comptabilité 500 €. Aucun poste laissé à zéro"),
            ("Fiscalité", "SCI à l'IS. Calcul réel de l'année 1 : intérêts d'emprunt 5 328 € et "
                           "dotation aux amortissements 4 267 € déduits de l'EBE, soit un "
                           "<strong>déficit de 189 € et aucun impôt</strong>, le déficit étant "
                           "reporté. Convention prudente retenue par ailleurs pour les rendements "
                           "publiés : IS de 15 % appliqué à l'EBE, <strong>sans amortissement du "
                           "bâti modélisé</strong>. Le seuil de décision de la doctrine du parc "
                           "porte sur le rendement net avant IS"),
            ("Prix de revient", f"<strong>{eur(ACTE_EN_MAIN)} €</strong> acte en main = prix "
                                f"{eur(PRIX)} € + frais d'acquisition {eur(PRIX*NOTAIRE)} € (8 %), "
                                f"sans travaux (aucun travaux annoncé)"),
        ],
        stance=(
            f"<strong>À négocier — sous condition de preuve des baux. Au rendement prudent de "
            f"1 070 €/mois, il faudrait acheter 115 000 € pour que le bien couvre sa mensualité, "
            f"ce qui n'est pas atteignable sur un bien loué affiché pour sa rentabilité. Si les "
            f"deux baux ne produisent pas près de 1 400 €/mois, on passe.</strong><br><br>"
            f"Le raisonnement tient en deux grilles, et le dossier en passe une sur deux. Sur la "
            f"grille de rendement, il est conforme : avec les loyers reconstruits à partir du "
            f"marché — 1 070 €/mois — l'exploitation dégage {eur(BASE['ebe'])} € d'EBE, soit "
            f"{fr(BASE['rdt_av'])} % net avant IS sur l'acte en main, au-dessus du seuil de 5 %, "
            f"et {fr(BASE['rdt_ap'])} % après IS contre 3,7 % de taux d'intérêt : l'opération "
            f"s'enrichit. Sur la grille de cash-flow, il échoue : à 10 % d'apport, la mensualité "
            f"est de 1 084 €/mois pour 784 €/mois d'exploitation, soit <strong>-301 €/mois</strong> "
            f"(-3 607 €/an), et il reste négatif dans les trois scénarios. Pour que le bien couvre "
            f"sa mensualité au prix affiché, il faudrait <strong>1 404 €/mois de loyers</strong> "
            f"— 31 % de plus que notre base —, ou un prix de {eur(prix_cashflow_nul(BASE['ebe']))} €, "
            f"ou un apport de {eur(apport_cashflow_nul(PRIX, BASE['ebe']))} € (35 % du prix). "
            f"Au-delà de 30 000 € d'apport, le dossier sort de la doctrine du parc.<br><br>"
            f"<strong>Ce que cela fixe comme cadre d'offre.</strong> À 148 000 €, le cash-flow reste "
            f"négatif de 219 €/mois et il faudrait 43 916 € d'apport (30 %) pour l'équilibrer ; à "
            f"165 000 € il est de -334 €/mois et il faudrait 60 916 € (37 %). Autrement dit, "
            f"l'offre de 148 000 € et le plafond de 165 000 € ne tiennent que sur la grille de "
            f"rendement, avec un apport hors doctrine : ils ne rendent pas ce bien finançable en "
            f"l'état. <strong>Trois pièces suspensives, non négociables :</strong> les deux baux en "
            f"cours (montant, date, échéance, type et quittances) — c'est la seule donnée qui "
            f"décide, et son absence dans une annonce qui parle de rentabilité immédiate est en soi "
            f"un signal ; l'avis de taxe foncière réel ; les diagnostics datés (DPE, électricité, "
            f"plomb, amiante) et une visite d'homme de l'art sur les trois postes que « aucun "
            f"travaux » ne couvre — couverture, électricité et humidité des caves, sur un immeuble "
            f"dont l'acquéreur porte seul la structure.<br><br>"
            f"<strong>Ce qui reste bon dans ce dossier.</strong> Il est loué, il est en centre-ville, "
            f"il n'y a rien à faire : pas de copropriété à financer, pas de chantier, pas de passif "
            f"énergétique (DPE D, aucune échéance avant 2034), des compteurs individuels. Et il "
            f"passe le seuil de 5 % net avant IS en scénario de base. Mais un dossier qui passe le "
            f"rendement sans passer le cash-flow ne s'achète pas : il se négocie, et il ne se "
            f"négocie que sur les baux, qui ne sont pas dans l'annonce."
        ),
        prix_plafond=(
            f"<strong>Deux ancres, et c'est la plus basse qui décide.</strong> Sur le seul critère "
            f"de rendement, le prix qui tient 5 % net avant IS est de {eur(BASE['cap5'])} € avec "
            f"1 070 €/mois de loyers — un seuil, pas une cible, dont on garde une marge pour les "
            f"inconnues du dossier (taxe foncière, couverture et caves, ameublement du studio), "
            f"d'où le plafond de négociation de 165 000 € et l'offre d'ouverture à 148 000 €, soit "
            f"{fr((PRIX - 148000.0) / PRIX * 100, 1)} % sous le prix affiché. Sur le critère de "
            f"cash-flow, le plafond tombe à <strong>{eur(prix_cashflow_nul(BASE['ebe']))} €</strong> "
            f"à 10 % d'apport — c'est le prix auquel le bien couvre sa mensualité de 1 084 €/mois — "
            f"et à "
            f"{eur(prix_cashflow_nul(calc(1200.0, 5.0, 5.0, 900.0, 400.0, 150.0, 200.0, 500.0)['ebe']))} € "
            f"si les loyers montent à 1 200 €/mois. Les deux ancres sont séparées de "
            f"{eur(BASE['cap5'] - prix_cashflow_nul(BASE['ebe']))} € : c'est le coût du service de "
            f"la dette sur quinze ans, et c'est lui qui commande. Sensibilité du plafond de "
            f"rendement aux seuls loyers, charges de base inchangées : à 900 €/mois "
            f"{eur(calc(900.0, 5.0, 5.0, 900.0, 400.0, 150.0, 200.0, 500.0)['cap5'])} €, à "
            f"1 000 €/mois {eur(calc(1000.0, 5.0, 5.0, 900.0, 400.0, 150.0, 200.0, 500.0)['cap5'])} €, "
            f"à 1 070 €/mois {eur(BASE['cap5'])} €, à 1 150 €/mois "
            f"{eur(calc(1150.0, 5.0, 5.0, 900.0, 400.0, 150.0, 200.0, 500.0)['cap5'])} €. Chaque "
            f"tranche de 100 €/mois de loyer vaut 20 000 € de capacité de prix. Si les baux "
            f"révèlent 920 €/mois, le plafond de rendement tombe à {eur(WORST['cap5'])} € et la "
            f"réponse est non. Et pour un cash-flow nul au prix affiché, il faut "
            f"<strong>{eur(loyer_cashflow_nul(144000.0))} €/mois de loyers</strong> — c'est le "
            f"chiffre à mettre en face du vendeur."
        ),
        leviers=[
            f"Les montants des deux baux sont l'argument central, et l'annonce elle-même le "
            f"fournit : elle vend une « rentabilité immédiate » sans donner un seul loyer. "
            f"Demander les baux, les échéances et les quittances avant toute discussion de prix, et "
            f"faire constater par écrit que le dossier n'est pas chiffrable sans eux",
            f"Le prix au m² habitable est le deuxième levier : 3 404 €/m² demandés contre "
            f"{eur(PRIX_M2_MEDIANE_APP)} €/m² de médiane communale (59 ventes DVF 2025) et "
            f"{eur(PRIX_M2_TRANCHE_30_50)} €/m² sur la tranche 30-50 m² qui contient les deux lots. "
            f"Les 70 m² annoncés incluent les caves : c'est la première correction à faire "
            f"accepter par le vendeur",
            f"Chaque tranche de 100 €/mois de loyer vaut 20 000 € de capacité de prix : c'est le "
            f"taux de change de cette négociation, et il se démontre en trois lignes (900 €/mois → "
            f"{eur(calc(900.0, 5.0, 5.0, 900.0, 400.0, 150.0, 200.0, 500.0)['cap5'])} €, 1 070 €/mois "
            f"→ {eur(BASE['cap5'])} €, 1 150 €/mois → "
            f"{eur(calc(1150.0, 5.0, 5.0, 900.0, 400.0, 150.0, 200.0, 500.0)['cap5'])} €)",
            "« Ne nécessite aucun travaux » est une déclaration d'agence, pas un diagnostic : "
            "demander les dates de DPE et les rapports électricité, plomb et amiante, et faire "
            "visiter la couverture et les caves par un homme de l'art. Sur un immeuble sans "
            "copropriété, une couverture à reprendre est à 100 % pour l'acquéreur",
            "L'absence de copropriété se retourne contre nous et doit se chiffrer : aucune "
            "mutualisation des travaux de structure, aucun budget prévisionnel, aucun "
            "copropriétaire avec qui partager une toiture ou une façade. C'est un argument de "
            "négociation légitime pour demander une décote sur le prix, ou du moins une garantie",
            "La taxe foncière n'est pas communiquée : demander l'avis réel et la valeur locative "
            "cadastrale. L'écart entre 700 et 1 100 €/an vaut 0,7 % de rendement brut, soit plus "
            "que la marge dont le dossier dispose au-dessus du seuil de 5 %",
            "Le studio de 17 m² est vraisemblablement loué meublé : demander l'état du mobilier et "
            "la provision de renouvellement (2 000 à 4 000 € par rotation complète), et vérifier "
            "la surface réelle du T2, annoncé en duplex, où l'escalier mange de la surface utile "
            "au sol",
            "Le marché de revente est liquide — 276 mutations en 2025 —, mais le dossier n'a "
            "aucune espérance de plus-value à ce prix : ne pas se laisser vendre un argument "
            "patrimonial qui n'existe pas, et le dire. Cette sincérité est aussi ce qui rend "
            "crédible la demande de baisse",
        ],
        meta=[
            f"<strong>Régime fiscal retenu :</strong> SCI à l'IS. Année 1 : EBE {eur(BASE['ebe'])} € "
            f"moins intérêts {eur(144000*0.037)} € et dotation aux amortissements 4 267 € = déficit "
            f"de 189 €, donc aucun impôt à payer, déficit reporté. Convention prudente retenue pour "
            f"les rendements publiés : IS de 15 % sur l'EBE, sans amortissement du bâti modélisé. "
            f"Seuil de décision du parc (5 % net avant IS) : {fr(BASE['rdt_av'])} % en base, "
            f"{fr(BASE['rdt_ap'])} % sous convention prudente",
            f"<strong>Frais d'acquisition :</strong> {eur(PRIX*NOTAIRE)} € (8 %), honoraires à la "
            f"charge du vendeur. Prix de revient acte en main : {eur(ACTE_EN_MAIN)} €, sans "
            f"travaux (aucun travaux annoncé)",
            f"<strong>Loyers :</strong> 1 070 €/mois reconstruits (studio meublé 480 € + T2 duplex "
            f"590 €) — aucun loyer communiqué par l'annonce, les deux baux en cours ne sont pas "
            f"chiffrés. Hypothèses de sensibilité : 1 200 €/mois (520 + 680) et 920 €/mois "
            f"(400 + 520)",
            f"<strong>Charges retenues :</strong> taxe foncière estimée 900 €/an (avis non "
            f"communiqué), charges d'immeuble 400 €/an (pas de copropriété), PNO 150 €, gestion "
            f"locative 5 % des loyers et provision travaux 200 € (poste composite de 842 €), "
            f"comptabilité 500 €. Provision automatique de 2,5 % du moteur désactivée pour ne pas "
            f"compter deux fois la provision travaux. Aucun poste laissé à zéro",
            f"<strong>Financement (doctrine du parc) :</strong> apport 10 %, prêt de "
            f"{eur(PRIX * (1 - APPORT_PCT))} € sur 15 ans à 3,7 % et assurance emprunteur de "
            f"0,34 %, soit une mensualité de 1 084 €/mois (0,00753 € par euro emprunté). Cash-flow "
            f"de <strong>-301 €/mois</strong> (-3 607 €/an) au prix affiché, -219 €/mois à "
            f"148 000 €, -334 €/mois à 165 000 €, -143 €/mois en hypothèse favorable de loyers et "
            f"-624 €/mois en hypothèse défavorable. Le dossier passe la grille de rendement mais "
            f"échoue au critère de cash-flow : 1 404 €/mois de loyers seraient nécessaires pour "
            f"équilibrer au prix affiché, ou un prix de 115 649 €, ou un apport de 30 à 37 % du "
            f"prix. Ne pas lire cette fiche comme un dossier finançable en l'état",
            f"<strong>Valeur de marché :</strong> {eur(VALEUR_RETENUE)} € "
            f"({eur(PRIX_M2_TRANCHE_30_50)} €/m² sur les 47 m² habitables), fourchette "
            f"{eur(VALEUR_BASSE)} à {eur(VALEUR_HAUTE)} €. Ancrage : médiane DVF 2025 de la "
            f"tranche 30-50 m² de Saint-Maximin, 5 ventes ; médiane communale des appartements "
            f"{eur(PRIX_M2_MEDIANE_APP)} €/m² sur 59 ventes et 276 mutations valides dans l'année",
            f"<strong>Contrôles à faire avant toute offre :</strong> les deux baux (montant, date, "
            f"échéance, type) et les dernières quittances ; surfaces Carrez des deux lots et plan "
            f"des logements ; diagnostics datés (DPE, électricité, plomb, amiante) ; état de la "
            f"couverture, des façades et de l'humidité des caves par un homme de l'art ; avis de "
            f"taxe foncière et valeur locative cadastrale ; statut de propriété de l'immeuble "
            f"(détention en totalité à confirmer)",
            f"<strong>Point de méthode :</strong> sur ce dossier, le seul paramètre qui déplace la "
            f"décision est le loyer. Le prix de revient est connu ({eur(ACTE_EN_MAIN)} €), les "
            f"travaux sont annoncés nuls, la valeur de marché est ancrée sur des ventes "
            f"comparables — mais les loyers, qui font basculer le rendement de "
            f"{fr(WORST['rdt_av'])} % à {fr(BEST['rdt_av'])} % et la capacité de prix de "
            f"{eur(WORST['cap5'])} € à {eur(BEST['cap5'])} €, ne sont pas dans l'annonce. Aucune "
            f"offre ne doit être signée avant de les avoir vus",
            f"<strong>Comparaison — l'autre dossier Saint-Maximin :</strong> l'immeuble de 400 m² "
            f"et 12 lots du centre-ville affiché 235 000 € chez Patrice Russo Immobilier "
            f"(réf. VIM10001311) exige une rénovation lourde chiffrée à 450 000 € : son coût de "
            f"revient ressort à 2 695 €/m² face à une médiane communale de 2 746 €/m² (analyse du "
            f"22/09/2026), soit un écart de 2 % qui condamne l'opération de promotion au prix "
            f"demandé. Le présent dossier est l'exact inverse : aucun travaux à porter, deux "
            f"logements loués, et un rendement qui passe le seuil de 5 %. Entre les deux, c'est "
            f"lui qui mérite la négociation — mais à condition d'obtenir les baux, parce que la "
            f"marge y est de 44 points de base quand celle de l'autre dossier n'existe pas",
        ],
    )

    c = gen.CONF[SLUG]
    html = gen.TEMPLATE.format(
        titre_court=c['titre_court'], adresse=c['adresse'], date_fr=c['date_fr'],
        source=c['source'], url=c['url'], badge=c['badge'], strategie=c['strategie'],
        fiscal_note=c['fiscal_note'],
        prix=eur(PRIX),
        surface=f"{eur(SURF_HAB)} m² habitables",
        prix_m2=f"{eur(PRIX/SURF_HAB)} €/m²",
        revient=eur(ACTE_EN_MAIN),
        valeur=eur(VALEUR_RETENUE),
        revenus=eur(1070),
        rdt_revient=fr(BASE['rdt_av']), rdt_valeur=fr(BASE['rdt_ap']),
        note=fr(note, 1), note_cls=fr(note, 1).replace(',', '-'),
        lat=c['lat'], lon=c['lon'], quartier=c['quartier'],
        intro_attr=c['intro_attr'], profil=c['profil'], concl_attr=c['concl_attr'],
        attrs=gen.attr_html(rec), intro_strat=c['intro_strat'], strats=gen.strategy_html(rec),
        rationale=c['rationale'], identite=gen.identite_html(c['identite']),
        projections=f"""  <section class="financial-projections">
    <h2>Compte d'exploitation locatif — prix affiché {eur(PRIX)} €, acte en main {eur(ACTE_EN_MAIN)} €, SCI à l'IS</h2>
    <p class="attractiveness-intro">{lecture}</p>
    <div class="projections-grid">
{chr(10).join(cartes)}
    </div>
    <table class="projection-table compare">
      <thead><tr><th>Indicateur</th><th class="num">Base — 1 070 €/mois</th><th class="num">Optimiste — 1 200 €/mois</th><th class="num">Pessimiste — 920 €/mois</th></tr></thead>
      <tbody>
        <tr><td>Loyers bruts annuels</td><td class="num">{eur(BASE['brut'])} €</td><td class="num">{eur(BEST['brut'])} €</td><td class="num">{eur(WORST['brut'])} €</td></tr>
        <tr><td>Excédent brut d'exploitation</td><td class="num">{eur(BASE['ebe'])} €</td><td class="num">{eur(BEST['ebe'])} €</td><td class="num">{eur(WORST['ebe'])} €</td></tr>
        <tr><td>EBE mensuel</td><td class="num">{eur(BASE['ebe_mois'])} €/mois</td><td class="num">{eur(BEST['ebe_mois'])} €/mois</td><td class="num">{eur(WORST['ebe_mois'])} €/mois</td></tr>
        <tr><td>Net après IS</td><td class="num">{eur(BASE['net'])} €</td><td class="num">{eur(BEST['net'])} €</td><td class="num">{eur(WORST['net'])} €</td></tr>
        <tr><td>Rendement net avant IS (acte en main)</td><td class="num">{fr(BASE['rdt_av'])} %</td><td class="num">{fr(BEST['rdt_av'])} %</td><td class="num">{fr(WORST['rdt_av'])} %</td></tr>
        <tr><td>Rendement net après IS (acte en main)</td><td class="num">{fr(BASE['rdt_ap'])} %</td><td class="num">{fr(BEST['rdt_ap'])} %</td><td class="num">{fr(WORST['rdt_ap'])} %</td></tr>
        <tr><td>Rendement net après IS sur la valeur ({eur(VALEUR_RETENUE)} €)</td><td class="num">{fr(BASE['rdt_valeur'])} %</td><td class="num">{fr(BEST['rdt_valeur'])} %</td><td class="num">{fr(WORST['rdt_valeur'])} %</td></tr>
        <tr><td>Prix d'achat tenant 5 % net avant IS</td><td class="num">{eur(BASE['cap5'])} €</td><td class="num">{eur(BEST['cap5'])} €</td><td class="num">{eur(WORST['cap5'])} €</td></tr>
        <tr><td>Écart au prix affiché ({eur(PRIX)} €)</td><td class="num">{eur(BASE['cap5'] - PRIX)} €</td><td class="num">{eur(BEST['cap5'] - PRIX)} €</td><td class="num">{eur(WORST['cap5'] - PRIX)} €</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Le seuil, et la seule ligne qui le fait bouger.</strong> La doctrine du parc exige 5 % net avant IS sur le prix de revient, ici {eur(ACTE_EN_MAIN)} € d'acte en main (prix affiché {eur(PRIX)} € + {eur(PRIX*NOTAIRE)} € de frais, aucun travaux annoncé). En scénario de base, avec 1 070 €/mois de loyers reconstruits, l'excédent brut d'exploitation ressort à <strong>{eur(BASE['ebe'])} €</strong> — <strong>{fr(BASE['rdt_av'])} % net avant IS</strong>, soit {fr((BASE['rdt_av'] - 5.0) * 100, 0)} points de base au-dessus du seuil — et {fr(BASE['rdt_ap'])} % après IS. Ce résultat ne tient pas au prix, qui est 35 % trop haut, mais à la seule ligne des loyers : à 920 €/mois le dossier tombe à {fr(WORST['rdt_av'])} % (« à fuir » sur le critère du rendement), à 1 200 €/mois il monte à {fr(BEST['rdt_av'])} %. L'annonce vend une « rentabilité immédiate » sans communiquer un seul loyer : c'est la pièce à obtenir avant toute offre.</p>
    </div>
    <h3>Sensibilité du plafond d'achat aux seuls loyers (charges du scénario de base)</h3>
    <table class="projection-table compare">
      <thead><tr><th>Loyers mensuels</th><th>Hypothèse</th><th class="num">EBE</th><th class="num">Rendement net avant IS</th><th class="num">Achat max (5 % net avant IS)</th><th class="num">Écart au prix affiché</th></tr></thead>
      <tbody>
{sens_html}
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Comparaison avec l'autre dossier Saint-Maximin.</strong> Le second immeuble du centre-ville, 400 m² et 12 lots affichés 235 000 € chez Patrice Russo Immobilier (réf. VIM10001311), exige une rénovation lourde chiffrée à 450 000 € : son coût de revient ressort à <strong>2 695 €/m²</strong> face à une médiane communale de <strong>2 746 €/m²</strong> retenue dans son analyse du 22/09/2026, soit 2 % d'écart — une opération de promotion morte au prix demandé, où il faut renégocier le prix de 100 000 € ou passer. Le présent dossier joue dans une autre catégorie : <strong>aucun travaux à porter</strong>, deux logements déjà loués, un prix d'entrée de {eur(ACTE_EN_MAIN)} € d'acte en main et un rendement de {fr(BASE['rdt_av'])} % net avant IS qui passe le seuil de 5 % — mais avec 44 points de base de marge, quand l'autre dossier n'en a aucun. C'est donc bien celui-ci qui mérite la négociation, et la négociation se joue sur les baux, pas sur le prix.</p>
    </div>
    <p class="attractiveness-intro">Repères de méthode : acte en main {eur(ACTE_EN_MAIN)} € = prix affiché {eur(PRIX)} € + frais d'acquisition {eur(PRIX*NOTAIRE)} € (8 %, honoraires à la charge du vendeur) ; aucun travaux à l'acquisition (aucun travaux annoncé), provision travaux et ameublement de 200 €/an en exploitation ; vacance 5 % en base, 4 % en hypothèse favorable, 10 % en hypothèse défavorable ; gestion locative 5 %, 4 % et 6 % selon les scénarios ; taxe foncière estimée 900 € (avis non communiqué) ; charges d'immeuble 400 € ; assurance PNO 150 € ; comptabilité 500 € ; SCI à l'IS avec IS de 15 % appliqué à l'EBE, sans amortissement du bâti modélisé ; valeur de marché {eur(VALEUR_RETENUE)} € ({eur(PRIX_M2_TRANCHE_30_50)} €/m², médiane DVF 2025 de la tranche 30-50 m² sur 5 ventes).</p>
  </section>
{cf_section}""",
        risques=gen.risques_html(rec),
        verdict_cls={"acheter": "buy", "negocier": "nego", "fuir": "pass"}.get(verdict, "nego"),
        stance=c['stance'], prix_plafond=c['prix_plafond'],
        leviers=gen.leviers_html(c['leviers']),
        meta="\n".join(f"      <p>{m}</p>" for m in c['meta']),
    )

    # Libelles de cartes devenus faux au rendu (la fiche est ecrite par l'agent)
    for vieux, neuf in (
        ('<span class="card-label">Surface</span>',
         '<span class="card-label">Surface habitable retenue</span>'),
        ('<span class="card-label">Prix / m²</span>',
         '<span class="card-label">Prix / m² habitable</span>'),
        ('<span class="card-label">Prix de revient</span>',
         '<span class="card-label">Prix de revient (acte en main)</span>'),
        ('<span class="card-label">Valeur marché retenue</span>',
         '<span class="card-label">Valeur marché (DVF 2025)</span>'),
        ('<span class="card-label">Revenus bruts</span>',
         '<span class="card-label">Loyers retenus (baux en cours)</span>'),
        ('<span class="card-label">Rentabilité nette</span>',
         '<span class="card-label">Rendement net avant IS / après IS</span>'),
    ):
        assert vieux in html, vieux
        html = html.replace(vieux, neuf)

    d = os.path.join(ROOT, 'analyses', SLUG)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  fiche ecrite : {len(html):,} octets dans {SLUG}")

    p = os.path.join(ROOT, 'analyses', 'analyses.json')
    data = json.load(open(p, encoding='utf-8'))
    lst = [x for x in data["analyses"] if x.get("slug") != SLUG]
    lst.append(rec)
    data["analyses"] = lst
    if isinstance(data.get("meta"), dict):
        data["meta"]["count"] = len(lst)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"  analyses.json : {len(lst)} fiches")


if __name__ == '__main__':
    main()
