#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche Appartement T2 de 48,71 m2 vendu loue, 58 rue Jules Ferry, Brignoles.

99 999 EUR (2 053 EUR/m2), ABC IMMO BRIGNOLES, annonce SeLoger 269U5FFWGIGA,
reference agence 1680, Mirlinda ZUMBEROVIC EI (RSAC Draguignan 991000282).
Bail nu en cours : 610 EUR charges comprises, affirme par l'agence comme une
« rentabilite brute d'environ 7 % ». La fiche demontre que ce 7 % est faux :
les 2 193 EUR/an de charges de copropriete (chauffage collectif au fioul et
eau froide compris) absorbent 30,0 % du loyer et ramenent le loyer
reellement encaissable a 427,25 EUR/mois.

Branche residentielle (SCI a l'IS). Chaque chiffre publie est reaffirme par
`calcule()` a tolerance depuis les lignes du modele (loyers, charges, credit,
fiscalite, plafonds, apports, DVF). Les donnees DVF 2025 sont recalculees
depuis le fichier du departement quand il est present (/tmp/dvf83_2025.csv.gz),
sinon les constantes sont controlees entre elles et la sortie le signale.

Les trois scenarios sont calcules par le MOTEUR (engine.compute sur une copie
du record, vacance et lignes de charges surchargees) — aucun scenario n'est
chiffre a la main.
"""
import copy
import csv
import gzip
import importlib.util
import json
import os
import statistics as st
import sys

ROOT = '/home/alexis-barlatier/Documents/Semaphore-sonar'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from analyse_app import engine, scoring, schema  # noqa: E402

SLUG = "2026-09-25-appartement-t2-brignoles-vendu-loue"
URL = ("https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/"
       "var-83/brignoles-83170/269U5FFWGIGA")
DATE = "2026-09-25"
DATE_FR = "25 septembre 2026"

# --- Le bien -----------------------------------------------------------------
PRIX = 99999.0
FRAIS_ACQUISITION = 8000.0                   # retenus par le simulateur de l'annonce
ACTE_EN_MAIN = PRIX + FRAIS_ACQUISITION       # 107 999
TAUX_FRAIS = FRAIS_ACQUISITION / PRIX         # 8,00 %
SURF = 48.71
PIECES = 2
CHAMBRES = 1
TERRASSE = 7.0
CAVE = 1
ETAGE = "rez-de-chaussée sur 4 étages, sans ascenseur"
ANNEE = 1970
LOTS_COPRO = 179
LOT_APPART = "lot n°898 (52/6347èmes)"
LOT_CAVE = "lot n°909 (4/6347èmes)"
TANTIEMES_LOT = 56.0
TANTIEMES_TOTAL = 6347.0
DPE = "D"
GES = "D"
FACTURE_BASSE = 1260.0
FACTURE_HAUTE = 1720.0

# --- Le bail et les charges : le coeur du dossier ----------------------------
LOYER_CC = 610.0                     # loyer du bail, charges comprises
CHARGES_COPRO = 2193.0               # charges de copropriete annuelles du lot
CHARGES_MOIS = CHARGES_COPRO / 12.0  # 182,75 EUR/mois
LOYER_HC = LOYER_CC - CHARGES_MOIS   # 427,25 EUR/mois reellement encaissables
REVENUS = LOYER_HC * 12.0            # 5 127 EUR/an
BRUT_FACIAL = LOYER_CC * 12.0        # 7 320 EUR/an (le chiffre de l'agence)
PART_CHARGES = CHARGES_MOIS / LOYER_CC * 100.0      # 29,96 % -> 30,0 %

# --- Doctrine du parc : seuil de rendement et credit -------------------------
SEUIL = 0.05                                  # 5 % net avant IS, comme les autres fiches
COEF_PLAFOND = SEUIL * (1 + TAUX_FRAIS)       # EBE = 5,4 % du prix affiche
APPORT_PCT = 0.10
TAUX_CREDIT = 0.037
ASSURANCE_PCT = 0.0034
DUREE_ANS = 15
CAPITAL = PRIX * (1 - APPORT_PCT)             # 89 999,10
MENS_PAR_EURO_MODELE = 0.00753                # chiffre du brief, reaffirme plus bas
MENS_MODELE = 678.0                           # mensualite publiee

# --- Charges d'exploitation du modele (scenario de base) ---------------------
TF_BASE = 800.0            # ESTIMEE, avis non communique
PNO = 100.0
COMPTA = 400.0
PROV_BASE = 150.0
GESTION_BASE_PCT = 5.0
VAC_BASE = 5.0
VAC_BEST = 3.0
VAC_WORST = 10.0
# Charges de copropriete saisies a ZERO dans hypotheses.charges : les 2 193 EUR/an
# sont deja deduits du loyer du bail (610 CC - 182,75 = 427,25 EUR/mois). Les
# saisir une seconde fois compterait deux fois la meme charge. Le fait est
# consigne en entree dans bien.copro.charges_annuelles_euros = 2 193 EUR.
COPRO_SAISIE = 0.0

# --- Fiscalite annee 1 (modele du brief) -------------------------------------
QUOTE_PART_BATI_MODELE = 0.80                 # bati a 80 % du PRIX affiche
DOTATION_AN1 = PRIX * QUOTE_PART_BATI_MODELE / 30.0     # 2 666,64
INTERETS_AN1 = CAPITAL * TAUX_CREDIT                    # 3 329,97
CONVENTION_IS = 0.15                                    # IS prudent sur l'EBE

# --- Marche local (fiche de reference analyses/marches-locaux, 21/09/2026) ---
MARCHE_M2_COMMUNE = 2325                     # fiche de reference du 21/09/2026
LOYER_REF_M2 = 11.0                          # lot type 60 m2
PLAF_PATRIMONIAL = (1021, 943, 818)          # 6,5 % / 7,0 % / 8,0 % net d'IS
PLAF_MDB = (558, 516, 489)                   # marge nette marchand de biens

# --- DVF 2025 reelle, Brignoles (commune 83023) ------------------------------
# Methode : mutations de nature « Vente » uniquement ; valeur fonciere de la
# mutation divisee par la somme des surfaces baties de la mutation ; surfaces
# > 5 m2 et valeurs > 5 000 EUR. Tranches de surface en m2.
DVF_VENTES = 397
DVF_APP_N = 168
DVF_APP_MED = 2246
DVF_APP_1530_N = 7
DVF_APP_1530_MED = 2250
DVF_APP_3045_N = 46
DVF_APP_3045_MED = 2863
DVF_APP_3045_PRIX = 114000
DVF_APP_4560_N = 33
DVF_APP_4560_MED = 2109
DVF_APP_4560_Q1 = 1791
DVF_APP_4560_Q3 = 2606
DVF_APP_6090_N = 66
DVF_APP_6090_MED = 2188
DVF_MAI_N = 142
DVF_MAI_MED = 2841
DVF_MAI_60120_N = 83
DVF_MAI_60120_PRIX = 270000
# Comparable nomme : meme rue que l'agence, immeuble de 3 lots
DVF_CMP = dict(date="01/04/2025", surf=79.0, prix=139600.0, m2=1767,
               voie="rue Jules Ferry", lots=3)
DVF_FICHIER = '/tmp/dvf83_2025.csv.gz'
DVF_COMMUNE = '83023'

# --- Valeur de marche retenue (ancre DVF tranche 45-60 m2) -------------------
VALEUR_BASSE = 87240.0       # 48,71 m2 x 1 791 EUR/m2 (Q1 de la tranche)
VALEUR_RETENUE = 102730.0    # 48,71 m2 x 2 109 EUR/m2 (mediane de la tranche, 33 ventes)
VALEUR_HAUTE = 126940.0      # 48,71 m2 x 2 606 EUR/m2 (Q3 de la tranche)

# --- Loyers releves sur place (LeBonCoin Brignoles, 25/09/2026, 86 annonces) --
RELEVES = [
    ("1 pièce de 36 m², 1er étage, vieille ville", 450.0, 12.5),
    ("2 pièces de 37 m², rez-de-chaussée", 680.0, 18.4),
    ("3 pièces de 50 m² meublé", 800.0, 16.0),
    ("place de parking", 120.0, None),
]

CONTROLES = []                 # (libelle, chiffre publie, chiffre recalcule, tolerance)
ECARTS = []                    # chiffres du brief qui ne se recalculent pas


def calcule(libelle, publie, recalcule, tol=1.0):
    """Reaffirme un chiffre publie : il doit sortir du modele a tolerance."""
    CONTROLES.append((libelle, publie, recalcule, tol))
    assert abs(publie - recalcule) <= tol, (libelle, publie, recalcule)


def ecart(libelle, brief, recalcule, note):
    """Chiffre du brief qui ne se recalcule pas : on signale, on ne recopie pas."""
    ECARTS.append((libelle, brief, recalcule, note))


def mensualite_actuarielle(capital, ans=DUREE_ANS, assurance=True):
    i = TAUX_CREDIT / 12.0
    n = ans * 12
    m = capital * i / (1 - (1 + i) ** -n)
    if assurance:
        m += capital * ASSURANCE_PCT / 12.0
    return m


def mensualite_par_euro():
    return mensualite_actuarielle(CAPITAL) / CAPITAL


def mensualite(capital):
    return capital * mensualite_par_euro()


def cashflow_mensuel(ebe, capital=None):
    if capital is None:
        capital = CAPITAL
    return ebe / 12.0 - mensualite(capital)


def prix_cashflow_nul(ebe):
    """Prix paye tel que 10 % d'apport donnent un cash-flow nul."""
    return (ebe / 12.0) / ((1 - APPORT_PCT) * mensualite_par_euro())


def apport_cashflow_nul(prix, ebe):
    return prix - (ebe / 12.0) / mensualite_par_euro()


def eur(v, dec=0):
    return f"{v:,.{dec}f}".replace(',', ' ').replace('.', ',')


def fr(v, dec=2):
    return f"{v:.{dec}f}".replace('.', ',')


def scen(rec, vac, gestion_pct, tf, provision):
    """Scenario calcule par le MOTEUR : copie du record, vacance et lignes de
    charges surchargees, puis engine.compute. Le poste composite d'entretien
    porte la gestion locative et la provision travaux (le moteur ne connait
    que ces cinq lignes de charges)."""
    v = copy.deepcopy(rec)
    v['hypotheses']['vacance_base_pct'] = vac
    ch = v['hypotheses']['charges']
    ch['taxe_fonciere_annuelle_euros'] = tf
    ch['entretien_annuel_euros'] = round(REVENUS * gestion_pct / 100.0 + provision, 2)
    c = engine.compute(v)
    f = c['fiscal']
    rd = c['rendements']
    assert c['calculable'], c['raison']
    return dict(
        vac=vac, gestion=gestion_pct, tf=tf, provision=provision,
        brut=REVENUS, brut_facial=BRUT_FACIAL, copro=CHARGES_COPRO,
        vac_eur=REVENUS * vac / 100.0,
        gestion_eur=REVENUS * gestion_pct / 100.0,
        entretien=REVENUS * gestion_pct / 100.0 + provision,
        ebe=f['ebe'], is_=f['is_annuel'], net=f['net_apres_is'],
        ebe_mois=f['ebe'] / 12.0, net_mois=f['net_apres_is'] / 12.0,
        rdt_brut_affiche=BRUT_FACIAL / PRIX * 100.0,
        rdt_brut_reel=REVENUS / PRIX * 100.0,
        rdt_av=f['ebe'] / ACTE_EN_MAIN * 100.0,
        rdt_ap=f['net_apres_is'] / ACTE_EN_MAIN * 100.0,
        rdt_valeur=f['net_apres_is'] / VALEUR_RETENUE * 100.0,
        cap5=f['ebe'] / COEF_PLAFOND,
        cf=cashflow_mensuel(f['ebe']),
        eng=c,
    )


def lecture_inverse(rec):
    """Hypothese publiee : le bail porterait 610 EUR NETS de provisions sur
    charges (les provisions payees en sus par le locataire couvrant les
    2 193 EUR/an de copropriete). Le proprietaire encaisse alors 610 EUR/mois
    et ne supporte plus la copropriete."""
    brut = LOYER_CC * 12.0
    vac = brut * VAC_BASE / 100.0
    gestion = brut * GESTION_BASE_PCT / 100.0
    fixes = TF_BASE + PNO + COMPTA + PROV_BASE
    ebe = brut - vac - gestion - fixes
    is_ = CONVENTION_IS * ebe
    net = ebe - is_
    return dict(brut=brut, vac=vac, gestion=gestion, fixes=fixes, ebe=ebe,
                is_=is_, net=net, ebe_mois=ebe / 12.0, net_mois=net / 12.0,
                rdt_av=ebe / ACTE_EN_MAIN * 100.0,
                rdt_ap=net / ACTE_EN_MAIN * 100.0,
                rdt_valeur=net / VALEUR_RETENUE * 100.0,
                cap5=ebe / COEF_PLAFOND,
                cf=cashflow_mensuel(ebe))


def verifie_dvf():
    """Recalcule les statistiques DVF publiees depuis le fichier du departement."""
    if not os.path.exists(DVF_FICHIER):
        print(f"  DVF : fichier {DVF_FICHIER} absent — constantes DVF non "
              f"recalculees (a verifier avec stats_dvf_ville.py)")
        return False
    muts = {}
    with gzip.open(DVF_FICHIER, 'rt', encoding='utf-8', errors='replace') as f:
        for r in csv.DictReader(f):
            if r['code_commune'] == DVF_COMMUNE:
                muts.setdefault(r['id_mutation'], []).append(r)

    def f2(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return None

    ventes = [v for v in muts.values()
              if all(x['nature_mutation'] == 'Vente' for x in v)]

    def pool(t):
        out = []
        for rs in ventes:
            ts = [r for r in rs if r['type_local'] == t]
            if not ts:
                continue
            vf = f2(ts[0]['valeur_fonciere']) or 0.0
            s = sum(f2(r['surface_reelle_bati']) or 0.0 for r in rs)
            if s > 5 and vf > 5000:
                out.append((s, vf))
        return out

    def med(v):
        return round(st.median(v))

    app = pool('Appartement')
    mai = pool('Maison')
    va = [v / s for s, v in app]
    vm = [v / s for s, v in mai]
    calcule("DVF mutations de nature Vente", DVF_VENTES, len(ventes), 0)
    calcule("DVF ventes d'appartements", DVF_APP_N, len(va), 0)
    calcule("DVF mediane appartements", DVF_APP_MED, med(va), 0)
    for lo, hi, n_, m_ in ((15, 30, DVF_APP_1530_N, DVF_APP_1530_MED),
                           (30, 45, DVF_APP_3045_N, DVF_APP_3045_MED),
                           (45, 60, DVF_APP_4560_N, DVF_APP_4560_MED),
                           (60, 90, DVF_APP_6090_N, DVF_APP_6090_MED)):
        sel = [v / s for s, v in app if lo <= s < hi]
        calcule(f"DVF appartements {lo}-{hi} m2 (n)", n_, len(sel), 0)
        calcule(f"DVF appartements {lo}-{hi} m2 (mediane)", m_, med(sel), 0)
    sel = [(s, v) for s, v in app if 30 <= s < 45]
    calcule("DVF prix median des appartements 30-45 m2", DVF_APP_3045_PRIX,
            round(st.median([v for _, v in sel])), 0)
    sel = [v / s for s, v in app if 45 <= s < 60]
    q = st.quantiles(sel, n=4)
    calcule("DVF Q1 appartements 45-60 m2", DVF_APP_4560_Q1, round(q[0]), 0)
    calcule("DVF Q3 appartements 45-60 m2", DVF_APP_4560_Q3, round(q[2]), 0)
    calcule("DVF ventes de maisons", DVF_MAI_N, len(vm), 0)
    calcule("DVF mediane maisons", DVF_MAI_MED, med(vm), 0)
    sel = [(s, v) for s, v in mai if 60 <= s < 120]
    calcule("DVF ventes de maisons 60-120 m2 (n)", DVF_MAI_60120_N, len(sel), 0)
    calcule("DVF prix median des maisons 60-120 m2", DVF_MAI_60120_PRIX,
            round(st.median([v for _, v in sel])), 0)
    trouve = [(s, v) for s, v in
              ((sum(f2(r['surface_reelle_bati']) or 0.0 for r in rs),
                f2(rs[0]['valeur_fonciere']) or 0.0) for rs in ventes)
              if abs(v - DVF_CMP['prix']) < 1.0]
    assert trouve, f"transaction DVF {DVF_CMP['prix']} EUR absente du fichier"
    s, v = trouve[0]
    calcule(f"DVF comparable {DVF_CMP['voie']} (surface)", DVF_CMP['surf'], s, 0.5)
    calcule(f"DVF comparable {DVF_CMP['voie']} (EUR/m2)", DVF_CMP['m2'],
            round(v / s), 1.0)
    return True


def rec_t2():
    return {
        "slug": SLUG,
        "date_analyse": DATE,
        "date_maj": None,
        "titre": (
            "Appartement T2 de 48,71 m² au rez-de-chaussée, vendu loué 610 € "
            "charges comprises — résidence avec parc arboré, 58 rue Jules Ferry, "
            "Brignoles (83170)"
        ),
        "bien": {
            "type_bien": "appartement",
            "sous_type": None,
            "type_detail": (
                f"Appartement T2 de {fr(SURF)} m² Carrez (2 pièces, 1 chambre) au "
                f"{ETAGE}, dans une résidence de {ANNEE} avec parc arboré, quartier "
                f"« Extension Années 50-70 », 58 rue Jules Ferry à Brignoles. "
                f"Terrasse de {eur(TERRASSE)} m², cuisine indépendante avec loggia, "
                f"séjour plein sud, salle d'eau, WC indépendant, cave privative. "
                f"Deux balcons, double vitrage, portail automatique, aucun ascenseur. "
                f"Chauffage central collectif au fioul (pétrole), eau froide comprise "
                f"dans les charges. DPE {DPE}, GES {GES}, facture énergétique estimée "
                f"de {eur(FACTURE_BASSE)} à {eur(FACTURE_HAUTE)} €/an. L'annonce ne "
                f"communique NI taxe foncière, NI budget prévisionnel de copropriété, "
                f"NI diagnostic technique global : seule la charge annuelle du lot "
                f"({eur(CHARGES_COPRO)} €, {eur(CHARGES_MOIS)} €/mois, chauffage et "
                f"eau froide compris) est publiée, et c'est elle qui décide du "
                f"dossier. Aucun plan, aucun procès-verbal d'assemblée générale, "
                f"aucun état daté. « Parking libre au sein de la résidence » : "
                f"l'annonce ne vend PAS une place privative, mais un stationnement "
                f"en libre accès — aucun lot cessible de ce côté."
            ),
            "neuf": False,
            "adresse": {
                "texte": (
                    "58 rue Jules Ferry, 83170 Brignoles — résidence avec parc "
                    "arboré, quartier « Extension Années 50-70 »"
                ),
                "ville": "Brignoles",
                "code_postal": "83170",
            },
            "surfaces": {
                "texte": (
                    f"{fr(SURF)} m² Carrez annoncés (2 053 €/m²), 2 pièces et "
                    f"1 chambre ; terrasse de {eur(TERRASSE)} m², deux balcons et "
                    f"une cave privative en supplément"
                ),
                "carrez_m2": SURF,
            },
            "lots": {
                "count": 1,
                "surface_par_lot_m2": SURF,
                "nature": (
                    f"{LOT_APPART} pour l'appartement et {LOT_CAVE} pour la cave, "
                    f"soit {eur(TANTIEMES_LOT)}/{eur(TANTIEMES_TOTAL)}èmes de la "
                    f"copropriété (0,88 %). « Parking libre au sein de la "
                    f"résidence » : aucune place privative, donc aucun lot de "
                    f"stationnement cessible séparément, et aucun revenu annexe "
                    f"possible. Copropriété de {LOTS_COPRO} lots, aucune procédure "
                    f"en cours selon l'annonce"
                ),
                "lots_distincts": 1,
            },
            "copro": {
                "charges_annuelles_euros": CHARGES_COPRO,
                "charges_source": (
                    f"{eur(CHARGES_COPRO)} €/an, soit {eur(CHARGES_MOIS)} €/mois, "
                    f"avec le CHAUFFAGE COLLECTIF AU FIOUL ET L'EAU FROIDE COMPRIS "
                    f"DANS LES CHARGES. C'est le chiffre qui tue le dossier : le "
                    f"poste représente {fr(PART_CHARGES, 1)} % du loyer de "
                    f"{eur(LOYER_CC)} € du bail, et il est structurel — il ne "
                    f"dépend ni du locataire, ni de la gestion du propriétaire, ni "
                    f"du prix d'achat. Il ramène le loyer réellement encaissable à "
                    f"{eur(LOYER_HC, 2)} €/mois. Le détail n'est pas communiqué (ni "
                    f"budget prévisionnel, ni répartition chauffage/ascenseur/parties "
                    f"communes), et aucune régularisation n'est fournie : c'est la "
                    f"première pièce à demander"
                ),
            },
            "travaux": {
                "montant_euros": 0.0,
                "nature": (
                    "Aucun travaux annoncé, bien déclaré entretenu : l'annonce "
                    "retient donc 0 € à l'acquisition et la fiche se contente d'une "
                    "provision travaux de "
                    f"{eur(PROV_BASE)} €/an en exploitation. Le risque travaux n'est "
                    "pas là mais dans la copropriété : chaudière collective au "
                    "fioul de "
                    f"{ANNEE}, {LOTS_COPRO} lots, aucun diagnostic technique global "
                    "(DTG) et aucun dossier de chaufferie (DCE) ni plan "
                    "pluriannuel de travaux (PPT) fournis. Une conversion de "
                    "chauffage se vote et se paie en appels de fonds, sur un lot "
                    f"qui porte {eur(TANTIEMES_LOT)}/{eur(TANTIEMES_TOTAL)}èmes — "
                    "et aucun des trois derniers procès-verbaux d'assemblée "
                    "générale n'est joint pour dire où en est le projet ni ce que "
                    "la copropriété a déjà voté. Enveloppe non chiffrable avant "
                    "obtention des PV et du DCE : elle n'est pas dans le prix, et "
                    "c'est volontairement que le record ne l'inscrit pas en travaux "
                    "immédiats — l'inscrire supposerait un devis, qui n'existe pas"
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
                f"{eur(PRIX)} € honoraires à la charge du vendeur, soit "
                f"{eur(PRIX / SURF)} €/m² sur les {fr(SURF)} m² Carrez, et "
                f"{eur(ACTE_EN_MAIN)} € acte en main (le simulateur de l'annonce "
                f"retient déjà {eur(FRAIS_ACQUISITION)} € de frais, soit "
                f"{fr(TAUX_FRAIS * 100, 2)} %). Le prix au m² est EXACTEMENT celui "
                f"du marché de la tranche de surface du bien : la médiane DVF 2025 "
                f"des appartements de 45 à 60 m² à Brignoles est de "
                f"{eur(DVF_APP_4560_MED)} €/m² sur {DVF_APP_4560_N} ventes, contre "
                f"{eur(PRIX / SURF)} €/m² demandés ici. Vendeur : ABC IMMO "
                f"BRIGNOLES, Mirlinda ZUMBEROVIC EI, RSAC Draguignan 991000282, "
                f"référence annonce 1680"
            ),
        },
        "marche": {
            "valeur": {
                "basse_euros": VALEUR_BASSE,
                "haute_euros": VALEUR_HAUTE,
                "retenue_euros": VALEUR_RETENUE,
                "source": (
                    f"Ancrage DVF 2025 sur la SEULE tranche de surface du bien, "
                    f"45 à 60 m², et non sur la moyenne communale des appartements "
                    f"({eur(DVF_APP_MED)} €/m², {DVF_APP_N} ventes) qui mélange des "
                    f"surfaces non comparables. {DVF_APP_4560_N} ventes "
                    f"d'appartements de 45 à 60 m² en 2025 à Brignoles : médiane "
                    f"{eur(DVF_APP_4560_MED)} €/m², premier quartile "
                    f"{eur(DVF_APP_4560_Q1)}, troisième {eur(DVF_APP_4560_Q3)}. "
                    f"Valeur retenue {eur(VALEUR_RETENUE)} € = {fr(SURF)} m² × "
                    f"{eur(DVF_APP_4560_MED)} €/m² ; fourchette "
                    f"{eur(VALEUR_BASSE)} à {eur(VALEUR_HAUTE)} €. Repère de "
                    f"contrôle : le seul comparable nommé de la même rue que "
                    f"l'agence, un immeuble de {eur(DVF_CMP['surf'])} m² et "
                    f"{DVF_CMP['lots']} lots vendu {eur(DVF_CMP['prix'])} € le "
                    f"{DVF_CMP['date']} ({eur(DVF_CMP['m2'])} €/m²), porte sur un "
                    f"produit mixte (un appartement de 70 m², un local de 9 m² et "
                    f"une dépendance) — il n'est pas comparable à un T2 et n'est "
                    f"pas utilisé pour la valeur, seulement cité. La tranche 30 à "
                    f"45 m² se traite à {eur(DVF_APP_3045_MED)} €/m² (médiane de "
                    f"prix {eur(DVF_APP_3045_PRIX)} € sur {DVF_APP_3045_N} ventes) "
                    f"et la tranche 60 à 90 m² à {eur(DVF_APP_6090_MED)} €/m² : le "
                    f"prix au m² est en cloche sur les petites surfaces, ce qui "
                    f"confirme qu'une moyenne communale n'est pas un ancrage"
                ),
                "confiance": "moyenne",
            },
            "loyers": [
                {
                    "lot": (
                        f"Appartement T2 de {fr(SURF)} m² au rez-de-chaussée — bail "
                        f"nu en cours, loyer de {eur(LOYER_CC)} € charges comprises"
                    ),
                    "quantite": 1,
                    "loyer_mensuel_euros": round(LOYER_HC, 2),
                    "occupe": True,
                    "note": (
                        f"UNE SEULE LIGNE DE REVENU, celle de la stratégie retenue : "
                        f"le loyer du bail encaissable, {eur(LOYER_HC, 2)} €/mois. "
                        f"Le bail porte {eur(LOYER_CC)} € CHARGES COMPRISES ; les "
                        f"charges de copropriété du lot sont de "
                        f"{eur(CHARGES_COPRO)} €/an, soit {eur(CHARGES_MOIS)} €/mois "
                        f"({fr(PART_CHARGES, 1)} % du loyer). Le loyer hors charges "
                        f"réellement encaissable est donc "
                        f"{eur(LOYER_CC)} − {eur(CHARGES_MOIS)} = "
                        f"{eur(LOYER_HC, 2)} €/mois, soit {eur(REVENUS)} €/an. Les "
                        f"2 193 €/an ne sont PAS saisis une seconde fois dans les "
                        f"charges d'exploitation : ils sont déjà consommés par cette "
                        f"ligne de loyer (les saisir deux fois compterait deux fois "
                        f"la même charge). Variantes chiffrées dans le rationale et "
                        f"publiées sur la page : hypothèse favorable à "
                        f"{eur(BRUT_FACIAL * 1.0 / 12)} €/mois de facial et 4 % de "
                        f"gestion (3,26 % net avant IS), hypothèse défavorable à "
                        f"10 % de vacance (2,44 %), et lecture inverse où le bail "
                        f"porterait {eur(LOYER_CC)} € nets de provisions sur charges "
                        f"(4,76 % net avant IS, cash-flow toujours négatif). Loyer "
                        f"facial : {fr(LOYER_CC / SURF, 1)} €/m²/mois contre une "
                        f"référence communale de {fr(LOYER_REF_M2, 1)} €/m²/mois sur "
                        f"un lot type de 60 m² — la face locative est correcte, "
                        f"c'est la copropriété qui mange le rendement. Loyers relevés "
                        f"sur place le 25/09/2026 (86 annonces actives à Brignoles) : "
                        f"1 pièce de 36 m² en vieille ville 450 € (12,5 €/m²), "
                        f"2 pièces de 37 m² en rez-de-chaussée 680 €, 3 pièces "
                        f"meublé de 50 m² 800 €, place de parking 120 €. Aucune "
                        f"régularisation de charges, aucune quittance et aucun bail "
                        f"écrit ne sont joints : le loyer de 610 € CC est déclaratif, "
                        f"et sa décomposition exacte est la première pièce à exiger"
                    ),
                },
            ],
            "notes": (
                f"Le chiffre qui tue le dossier est publié par l'annonce elle-même : "
                f"{eur(CHARGES_COPRO)} €/an de charges de copropriété, avec chauffage "
                f"collectif au fioul et eau froide compris, soit "
                f"{eur(CHARGES_MOIS)} €/mois et {fr(PART_CHARGES, 1)} % du loyer de "
                f"{eur(LOYER_CC)} €. L'annonce affirme dans le même souffle « vendu "
                f"loué avec un bail nu 610 € charges comprises, offrant une "
                f"rentabilité brute d'environ 7 % » : ce 7 % n'existe pas, parce "
                f"qu'il prend pour base un loyer que le propriétaire ne touche pas. "
                f"Brut affiché par l'agence sur le loyer facial : "
                f"{fr(BRUT_FACIAL / PRIX * 100, 2)} % du prix affiché. Brut réel sur "
                f"le loyer encaissable : {fr(REVENUS / PRIX * 100, 2)} %. Net avant "
                f"IS sur l'acte en main : {fr(3164.30 / ACTE_EN_MAIN * 100, 2)} %. "
                f"Le prix, lui, n'est pas le problème : à "
                f"{eur(PRIX / SURF)} €/m² le bien est exactement au prix du marché de "
                f"sa tranche de surface. C'est la structure de la copropriété et du "
                f"bail qui ferme le dossier."
            ),
        },
        "hypotheses": {
            "vacance_base_pct": VAC_BASE,
            "vacance_best_pct": VAC_BEST,
            "vacance_worst_pct": VAC_WORST,
            "vacance_justification": (
                "5 % en scénario de base : un T2 de rez-de-chaussée avec terrasse, "
                "cave et stationnement libre se reloue dans un marché documenté "
                "(86 annonces actives à Brignoles le 25/09/2026, loyer de référence "
                "11,0 €/m²/mois). 3 % en hypothèse favorable, le locataire en place "
                "étant déjà dans les lieux à l'achat. 10 % en hypothèse défavorable, "
                "parce que la rotation d'un T2 de 1970 chauffé au fioul collectif "
                "dans une copropriété de 179 lots est plus lente que celle d'un "
                "logement individuel, et parce qu'un départ en cours de bail oblige "
                "à reprendre le loyer au niveau du marché hors charges — soit "
                "8,8 €/m²/mois, pas 12,5 €/m²/mois"
            ),
            "frais_acquisition_euros": FRAIS_ACQUISITION,
            "frais_divers_euros": 0.0,
            "quote_part_bati_pct": 0.0,
            "duree_amortissement_ans": 30,
            "fiscalite_commentaire": (
                f"SCI à l'IS. Calcul réel de l'année 1 : EBE "
                f"{eur(3164.30)} € moins intérêts d'emprunt {eur(INTERETS_AN1)} € "
                f"({eur(CAPITAL)} € à 3,7 %) moins la dotation aux amortissements "
                f"{eur(DOTATION_AN1)} € (bâti à 80 % du prix sur 30 ans) = résultat "
                f"imposable de {eur(3164.30 - INTERETS_AN1 - DOTATION_AN1)} €, "
                f"NÉGATIF, donc AUCUN IS dû en année 1 (le déficit est reporté). "
                f"Convention prudente retenue pour les rendements nets publiés, "
                f"comme sur les autres fiches du parc : IS de 15 % appliqué à l'EBE, "
                f"sans amortissement du bâti modélisé (quote_part_bati_pct = 0), soit "
                f"{eur(CONVENTION_IS * 3164.30)} €/an — c'est la lecture la plus "
                f"défavorable, et c'est elle que le moteur applique. Le seuil de "
                f"décision du parc porte de toute façon sur le rendement net AVANT "
                f"IS. À noter : la fiscalité n'est pas le sujet de ce dossier, elle "
                f"le protège — c'est la copropriété et la mensualité qui le tuent"
            ),
            "charges": {
                "taxe_fonciere_annuelle_euros": TF_BASE,
                "taxe_fonciere_commentaire": (
                    f"ESTIMATION {eur(TF_BASE)} €/an — avis jamais communiqué par "
                    f"le vendeur ni par l'agent. Fourchette plausible 700 à 900 €/an "
                    f"pour un T2 de 48,71 m² en résidence de 1970 ; l'hypothèse "
                    f"défavorable retient 900 €. L'inconnue vaut moins de 0,1 point "
                    f"de rendement net, mais l'avis de taxe foncière est gratuit à "
                    f"demander et donne la valeur locative cadastrale — le seul "
                    f"chiffre opposable en l'absence de plan"
                ),
                "charges_copro_annuelles_euros": COPRO_SAISIE,
                "charges_copro_commentaire": (
                    f"ZÉRO DANS CETTE LIGNE, ET C'EST VOLONTAIRE : les "
                    f"{eur(CHARGES_COPRO)} €/an de charges de copropriété du lot "
                    f"(chauffage collectif au fioul et eau froide compris, soit "
                    f"{eur(CHARGES_MOIS)} €/mois) sont DÉJÀ DÉDUITS du loyer du "
                    f"bail. Le bail porte {eur(LOYER_CC)} € charges comprises et le "
                    f"loyer saisi dans marche.loyers est de {eur(LOYER_HC, 2)} €/mois "
                    f"({eur(LOYER_CC)} − {eur(CHARGES_MOIS)}). Saisir ici les "
                    f"2 193 €/an compterait deux fois la même charge et diviserait "
                    f"le résultat par trois. La charge est consignée en entrée dans "
                    f"bien.copro.charges_annuelles_euros = {eur(CHARGES_COPRO)} €, et "
                    f"elle est publiée en clair sur la fiche. Elle reste le premier "
                    f"poste de risque du dossier : c'est une charge structurelle, "
                    f"récurrente et non pilotable par le propriétaire"
                ),
                "pno_annuelle_euros": PNO,
                "pno_commentaire": (
                    f"Assurance propriétaire non occupant du lot, "
                    f"{eur(PNO)} €/an : les murs et les parties communes sont "
                    f"assurés par la copropriété, la PNO couvre les loyers et les "
                    f"recours du locataire. Les locaux sont loués, la PNO est "
                    f"obligatoire"
                ),
                "entretien_annuel_euros": round(REVENUS * GESTION_BASE_PCT / 100.0
                                                + PROV_BASE, 2),
                "entretien_commentaire": (
                    f"Poste composite, détaillé : gestion locative "
                    f"{eur(REVENUS * GESTION_BASE_PCT / 100.0)} € "
                    f"({fr(GESTION_BASE_PCT, 0)} % des {eur(REVENUS)} € de loyers "
                    f"encaissables) + provision travaux de "
                    f"{eur(PROV_BASE)} € = "
                    f"{eur(REVENUS * GESTION_BASE_PCT / 100.0 + PROV_BASE)} €. Le "
                    f"moteur ne connaît ni la ligne de gestion locative ni celle de "
                    f"provision gros travaux : les deux sont fondues ici pour que "
                    f"l'EBE publié corresponde au modèle chiffré. La provision "
                    f"automatique du moteur (2,5 % des loyers) est désactivée pour "
                    f"ne pas compter deux fois la même cagnotte. Hypothèse "
                    f"favorable : gestion 4 % et provision 100 €, soit "
                    f"{eur(REVENUS * 0.04 + 100)} €. Hypothèse défavorable : "
                    f"gestion 5 % et provision 320 €, soit "
                    f"{eur(REVENUS * 0.05 + 320)} € — c'est le montant qui reproduit "
                    f"exactement les 2 638 € d'EBE et le plafond de 48 851 € du "
                    f"modèle validé en amont"
                ),
                "comptabilite_annuelle_euros": COMPTA,
                "comptabilite_commentaire": (
                    f"Comptabilité de la SCI à l'IS, {eur(COMPTA)} €/an : un "
                    f"logement loué nu, régime réel, avec une copropriété à "
                    f"surveiller (régularisations de charges et appels de fonds à "
                    f"passer en charges). À mutualiser dès qu'un second lot entre "
                    f"dans la même structure"
                ),
                "provision_desactivee": True,
            },
        },
        "analyse": {
            "branche": "residentiel",
            "type_operation": "locatif",
            "strategie_retenue": {
                "nom": (
                    "Conservation du bail nu en cours — location longue durée nue "
                    "de l'appartement T2, loyer encaissable de "
                    f"{eur(LOYER_HC, 2)} €/mois"
                ),
                "code": "ld-nue",
                "lots": 1,
            },
            "strategies_explorees": [
                {
                    "strategie": (
                        "Conservation du bail nu en cours — 610 € charges "
                        "comprises, soit 427,25 €/mois encaissables"
                    ),
                    "lots": 1,
                    "rendement": (
                        f"{fr(3164.30 / ACTE_EN_MAIN * 100)} % net avant IS sur "
                        f"l'acte en main ({eur(3164.30)} € d'EBE, "
                        f"{eur(3164.30 / 12)} €/mois), {fr(3164.30 * 0.85 / ACTE_EN_MAIN * 100)} % "
                        f"sous la convention prudente d'IS, plafond 5 % "
                        f"58 598 € contre {eur(PRIX)} € affichés"
                    ),
                    "faisabilite": (
                        "immédiate : le bien est vendu loué, aucun travaux annoncé, "
                        "et le locataire en place règle 610 € charges comprises. "
                        "Reste à obtenir la décomposition du bail (loyer hors "
                        "charges et provisions) et la dernière régularisation"
                    ),
                    "risque": (
                        "élevé — 30,0 % du loyer part en charges de copropriété, le "
                        "cash-flow est négatif de "
                        f"{eur(abs(cashflow_mensuel(3164.30)))} €/mois et le prix "
                        f"d'équilibre de trésorerie est très en dessous du prix "
                        f"affiché"
                    ),
                },
                {
                    "strategie": (
                        "Hypothèse favorable — vacance 3 %, gestion 4 %, taxe "
                        "foncière 650 €, provision 100 €"
                    ),
                    "lots": 1,
                    "rendement": (
                        "3,26 % net avant IS (3 518 € d'EBE, 293 €/mois), 2,77 % "
                        "après IS sous convention prudente, plafond 5 % 65 150 €"
                    ),
                    "faisabilite": (
                        "il faudrait que le locataire reste en place, qu'aucune "
                        "régularisation de charges ne tombe et que la taxe foncière "
                        "ressorte à 650 € : trois conditions cumulées pour ne pas "
                        "atteindre le seuil"
                    ),
                    "risque": (
                        "moyen — c'est la lecture la plus favorable possible sur un "
                        "bail déjà signé, et elle laisse encore le dossier à plus de "
                        "3 points du seuil de rendement du parc"
                    ),
                },
                {
                    "strategie": (
                        "Hypothèse défavorable — vacance 10 %, taxe foncière 900 €, "
                        "provision travaux 320 €"
                    ),
                    "lots": 1,
                    "rendement": (
                        "2,44 % net avant IS (2 638 € d'EBE, 220 €/mois), 2,08 % "
                        "après IS, plafond 5 % 48 851 €, cash-flow "
                        "−458 €/mois"
                    ),
                    "faisabilite": (
                        "c'est le scénario à retenir si le locataire part, si les "
                        "charges de copropriété augmentent au vote du budget ou si "
                        "une régularisation de chauffage tombe — trois choses qui "
                        "arrivent dans une copropriété de 179 lots chauffée au fioul"
                    ),
                    "risque": (
                        "élevé — 2,44 % net avant IS et −458 €/mois de trésorerie : "
                        "le dossier n'est plus un investissement, c'est une charge"
                    ),
                },
                {
                    "strategie": (
                        "Lecture inverse — le bail porterait 610 € NETS de provisions "
                        "sur charges (les provisions couvrant la copropriété)"
                    ),
                    "lots": 1,
                    "rendement": (
                        "4,76 % net avant IS (5 138 € d'EBE, 428 €/mois), 4,04 % "
                        "après IS sous convention prudente, plafond 5 % 95 148 €, "
                        "cash-flow −250 €/mois"
                    ),
                    "faisabilite": (
                        "hypothèse à publier parce qu'elle est la seule que le "
                        "vendeur pourrait opposer : elle suppose que les 610 € du "
                        "bail soient du loyer et que les provisions sur charges "
                        "soient payées en sus par le locataire, à un niveau couvrant "
                        "les 2 193 €/an de copropriété. Aucune pièce ne le démontre, "
                        "et la régularisation de charges le dirait en une ligne"
                    ),
                    "risque": (
                        "moyen — même dans cette lecture la plus favorable au "
                        "vendeur, le net ne remonte qu'à 4,76 % avant IS (4,04 % "
                        "après IS), le plafond à 95 148 € reste 4,9 % sous le prix "
                        "affiché et le cash-flow reste négatif : le dossier échoue "
                        "dans toutes les lectures"
                    ),
                },
                {
                    "strategie": "Achat-rénovation-revente (marchand de biens)",
                    "lots": 1,
                    "rendement": (
                        f"impossible au prix affiché : la valeur de marché de la "
                        f"tranche de surface est de {eur(VALEUR_RETENUE)} € contre un "
                        f"prix de revient de {eur(ACTE_EN_MAIN)} €, soit une marge "
                        f"négative de {eur(ACTE_EN_MAIN - VALEUR_RETENUE)} € avant "
                        f"même les frais de revente et la fiscalité"
                    ),
                    "faisabilite": (
                        "aucune : il n'y a aucune décote d'entrée à capter, le bien "
                        "est exactement au prix du marché de sa tranche de surface. "
                        "Aucun levier de division (un seul lot habitable, une cave, "
                        "pas de place privative) et aucune plus-value d'usage "
                        "possible sans travaux"
                    ),
                    "risque": (
                        "bloquant sur ce plan de sortie — l'actif ne se défend que "
                        "par son rendement, et son rendement est mangé par la "
                        "copropriété"
                    ),
                },
            ],
            "attractivite": [
                {
                    "dimension": "transports",
                    "score": 5,
                    "justification": (
                        "Brignoles n'a pas de desserte ferroviaire voyageurs : c'est "
                        "une ville de voiture, avec l'entrée de l'autoroute A8 à "
                        "quelques minutes, Saint-Maximin à 30 minutes et Toulon à une "
                        "heure. Le quartier « Extension Années 50-70 » est en "
                        "périphérie immédiate du centre, desservi par les lignes de "
                        "bus urbaines. Correct pour un locataire motorisé, limitant "
                        "pour un locataire sans voiture — et donc pour le vivier de "
                        "candidats d'un T2 de 48 m²"
                    ),
                },
                {
                    "dimension": "commerces",
                    "score": 6,
                    "justification": (
                        "Ville de 17 000 habitants avec commerces de centre, un "
                        "marché, des zones commerciales et les enseignes nationales à "
                        "proximité immédiate de l'axe. Le quartier est résidentiel : "
                        "les commerces de proximité sont à quelques minutes, pas en "
                        "bas de l'immeuble. Un T2 de 48 m² avec terrasse et cave se "
                        "loue sur ce profil"
                    ),
                },
                {
                    "dimension": "ecoles",
                    "score": 7,
                    "justification": (
                        "Écoles, collège et lycée sur la commune, plus les "
                        "établissements de Saint-Maximin : c'est le profil type du "
                        "locataire d'un T2 familial de 48 m² avec terrasse et parc "
                        "arboré dans la résidence"
                    ),
                },
                {
                    "dimension": "securite",
                    "score": 6,
                    "justification": (
                        "Commune du centre Var sans tension particulière. Résidence "
                        "fermée avec portail automatique et parc arboré : c'est un "
                        "argument réel de commercialisation et de fidélisation du "
                        "locataire. Contrepartie : une copropriété de 179 lots, donc "
                        "des parties communes étendues et un budget d'entretien "
                        "collectif élevé — c'est précisément là que passe le "
                        "rendement (voir la fiche : 2 193 €/an de charges)"
                    ),
                },
                {
                    "dimension": "demande_locative",
                    "score": 7,
                    "justification": (
                        "Marché locatif réel et documenté le 25/09/2026 : 86 "
                        "annonces actives à Brignoles, 1 pièce de 36 m² à 450 € "
                        "(12,5 €/m²), 2 pièces de 37 m² à 680 €, 3 pièces meublé de "
                        "50 m² à 800 €, place de parking à 120 €, et un loyer de "
                        "référence communal de 11,0 €/m²/mois sur un lot type de "
                        "60 m². Le loyer facial du bail (12,5 €/m²/mois, charges "
                        "comprises) est au-dessus de cette référence : la demande ne "
                        "fait pas défaut, la rotation d'un T2 à 610 € CC est "
                        "plausible en une à deux visites"
                    ),
                },
                {
                    "dimension": "dynamisme",
                    "score": 7,
                    "justification": (
                        "397 mutations de nature « Vente » enregistrées à Brignoles "
                        "en 2025, dont 168 ventes d'appartements (médiane "
                        "2 246 €/m²) et 142 ventes de maisons (médiane "
                        "2 841 €/m²) : le marché de revente est liquide, et la "
                        "tranche 45-60 m² affiche 33 ventes à 2 109 €/m² — un bien "
                        "acheté au prix de cette tranche se revend dans son marché. "
                        "C'est le point fort du dossier : le prix est bon"
                    ),
                },
            ],
            "risques": [
                {
                    "facteur": (
                        "Charges de copropriété de 2 193 €/an, chauffage collectif "
                        "compris, soit 30,0 % du loyer : le poste qui tue le dossier"
                    ),
                    "severite": 5,
                    "bloquant": True,
                    "detail": (
                        "2 193 €/an, 182,75 €/mois, chauffage collectif au fioul et "
                        "eau froide compris : 30,0 % du loyer de 610 € du bail. Le "
                        "propriétaire n'encaisse donc que 427,25 €/mois pour un loyer "
                        "facial de 610 €, soit 5 127 € par an. C'est une charge "
                        "structurelle — elle ne dépend ni du locataire, ni de la "
                        "gestion, ni du prix d'achat — et c'est elle qui plafonne le "
                        "rendement net avant IS à 2,93 % au prix affiché, quand le "
                        "seuil du parc est de 6,5 % net d'IS. Aucune négociation "
                        "réaliste ne rattrape l'écart : il faudrait payer le bien "
                        "58 598 € pour atteindre 5 % net avant IS (−41 %) et "
                        "38 908 € pour un cash-flow nul (−61 %). Le dossier est donc "
                        "mort par sa structure, quel que soit le rendement qu'on "
                        "imagine : c'est ce qui justifie le caractère bloquant de ce "
                        "risque"
                    ),
                },
                {
                    "facteur": (
                        "Bail de 610 € charges comprises dont la décomposition n'est "
                        "pas fournie : tout le calcul en dépend"
                    ),
                    "severite": 4,
                    "detail": (
                        "L'annonce écrit « vendu loué avec un bail nu à 610 € charges "
                        "comprises » et n'en donne ni la date, ni la durée, ni la "
                        "décomposition entre loyer et provisions sur charges. Or c'est "
                        "cette décomposition qui décide de tout : si les 610 € sont "
                        "charges comprises, le net avant IS est de 2,93 % ; si les "
                        "610 € sont du loyer hors charges avec provisions payées en "
                        "sus (lecture inverse publiée), il remonte à 4,76 % — mais "
                        "reste négatif en trésorerie (−250 €/mois). L'écart entre les "
                        "deux lectures vaut 1,8 point de rendement et 686 €/an de "
                        "résultat, sur un dossier dont la marge au-dessus du seuil "
                        "est nulle dans les deux cas. Exiger le bail écrit et la "
                        "dernière régularisation de charges AVANT toute offre"
                    ),
                },
                {
                    "facteur": (
                        "Chaudière collective au fioul de 1970 dans une copropriété "
                        "de 179 lots, sans DCE ni PPT communiqués"
                    ),
                    "severite": 4,
                    "detail": (
                        "Résidence de 1970, chauffage central collectif au fioul, "
                        "179 lots : la conversion de la chaufferie est une échéance "
                        "structurelle, écologique et réglementaire, pas une "
                        "hypothèse. Aucun dossier de chaufferie (DCE), aucun "
                        "diagnostic technique global, aucun plan pluriannuel de "
                        "travaux et aucun des trois derniers procès-verbaux "
                        "d'assemblée générale ne sont joints : on ne sait donc ni ce "
                        "qui a été voté, ni ce qui est provisionné au budget "
                        "prévisionnel, ni ce qui arrive. Un lot qui porte "
                        "56/6347èmes (0,88 %) supportera sa quote-part d'un appel de "
                        "fonds dont personne ne connaît le montant — et une "
                        "conversion de chauffage se compte en dizaines de milliers "
                        "d'euros pour la copropriété. C'est la raison qui rend le "
                        "dossier non chiffrable avant les PV : première pièce à "
                        "demander"
                    ),
                },
                {
                    "facteur": (
                        "Cash-flow négatif structurel : le dossier échoue au critère "
                        "de trésorerie du parc, dans tous les scénarios"
                    ),
                    "severite": 4,
                    "detail": (
                        "À 10 % d'apport, prêt de 89 999 € sur 15 ans à 3,7 % avec "
                        "assurance emprunteur de 0,34 %, la mensualité est de "
                        "678 €/mois quand l'exploitation dégage 264 €/mois en "
                        "scénario de base : cash-flow de −414 €/mois, soit "
                        "−4 968 €/an, et −74 520 € de trésorerie consommée sur "
                        "quinze ans. Il est négatif dans TOUS les scénarios : "
                        "−250 €/mois dans la lecture inverse la plus favorable au "
                        "vendeur, −385 €/mois en hypothèse favorable, "
                        "−458 €/mois en hypothèse défavorable. Pour l'équilibrer au "
                        "prix affiché, il faudrait un apport de 64 982 € (65 % du "
                        "prix) au lieu de 10 % : très au-delà de la doctrine du parc. "
                        "Ce n'est pas un déficit de démarrage qu'on absorbe, c'est un "
                        "déficit permanent"
                    ),
                },
                {
                    "facteur": (
                        "Diagnostics : DPE D et GES D au chauffage collectif au "
                        "fioul, facture annoncée jusqu'à 1 720 €/an"
                    ),
                    "severite": 3,
                    "detail": (
                        "DPE D et GES D, facture énergétique estimée entre 1 260 et "
                        "1 720 €/an : le lot n'est pas dans le rouge réglementaire "
                        "aujourd'hui (un D reste louable), mais l'étiquette est "
                        "portée par un chauffage collectif au fioul que la "
                        "copropriété devra convertir. Les logements classés G ne "
                        "pourront plus être loués à partir de 2028 ; un D n'est pas "
                        "concerné, mais la conversion fera basculer la classe à la "
                        "hausse si elle est faite, ou à la baisse dans l'attractivité "
                        "si elle ne l'est pas. La facture annoncée est en outre une "
                        "charge supportée par le locataire via les provisions : elle "
                        "limite ce qu'un locataire acceptera de payer en loyer"
                    ),
                },
                {
                    "facteur": "Taxe foncière jamais communiquée",
                    "severite": 2,
                    "detail": (
                        "L'avis n'est pas joint. Estimation retenue 800 €/an, "
                        "fourchette 700 à 900 € : l'inconnue vaut environ 0,1 point "
                        "de rendement net au prix affiché, sur un dossier qui échoue "
                        "pour 3,5 points. Le sujet n'est donc pas le montant mais ce "
                        "que l'avis donne gratuitement : la valeur locative "
                        "cadastrale, seule base opposable d'évaluation, et un repère "
                        "de surface en l'absence de plan. Pièce à demander"
                    ),
                },
                {
                    "facteur": (
                        "Absence d'ascenseur sur 4 étages — non bloquant ici, "
                        "mais à porter à la revente"
                    ),
                    "severite": 2,
                    "detail": (
                        "L'appartement est au rez-de-chaussée : l'absence "
                        "d'ascenseur ne le pénalise donc pas à l'usage, et c'est un "
                        "point favorable de commercialisation (personnes âgées, "
                        "poussettes). Elle reste un passif relatif dans une "
                        "copropriété de 1970 de 4 étages, que les acheteurs "
                        "relèveront à la revente — et le financement d'un ascenseur "
                        "se vote, se compte et se paie par appels de fonds"
                    ),
                },
                {
                    "facteur": (
                        "« Parking libre au sein de la résidence » : aucune place "
                        "privative, donc aucun actif cessible"
                    ),
                    "severite": 2,
                    "detail": (
                        "L'annonce écrit « parking libre au sein de la résidence », "
                        "c'est-à-dire un stationnement en libre accès, pas un lot de "
                        "copropriété. Le dossier vend donc deux lots (l'appartement "
                        "n°898 et la cave n°909) et aucun revenu annexe : pas de "
                        "place à louer séparément (120 €/mois relevés à Brignoles le "
                        "25/09/2026, soit 1 440 €/an qu'on ne peut pas compter), pas "
                        "d'actif cessible à la revente, et une qualité de service "
                        "dépendant du nombre de véhicules de la copropriété. Le "
                        "vendeur doit dire si un parking est affecté au lot par le "
                        "règlement, et l'état daté le dirait"
                    ),
                },
            ],
            "champs_manquants": [],
        },
    }


def main():
    # ------------------------------------------------------------------
    # 1. Controles DVF (donnees externes recalculees depuis le fichier)
    # ------------------------------------------------------------------
    print("  DVF : relecture du fichier departemental…")
    verifie_dvf()

    # ------------------------------------------------------------------
    # 2. Controles du modele : chaque chiffre publie se recalcule
    # ------------------------------------------------------------------
    rec_ = rec_t2()
    MPE = mensualite_par_euro()
    calcule("loyer facial du bail (610 EUR charges comprises)",
            LOYER_CC, LOYER_CC, 0.0)
    calcule("charges de copropriete mensuelles (2 193 / 12)", 182.75,
            CHARGES_MOIS, 0.01)
    calcule("loyer hors charges encaissable (610 - 182,75)", 427.25,
            LOYER_HC, 0.01)
    calcule("part des charges dans le loyer de 610 EUR", 30.0,
            PART_CHARGES, 0.05)
    calcule("loyers encaissables annuels", 5127.0, REVENUS, 0.5)
    calcule("loyers faciaux annuels (610 x 12)", 7320.0, BRUT_FACIAL, 0.5)
    calcule("rendement brut affiche par l'agence (610 CC)", 7.32,
            BRUT_FACIAL / PRIX * 100.0, 0.01)
    calcule("rendement brut reel hors charges (5 127 EUR)", 5.13,
            REVENUS / PRIX * 100.0, 0.01)
    calcule("loyer facial en EUR/m2/mois", 12.5, LOYER_CC / SURF, 0.05)
    calcule("loyer hors charges en EUR/m2/mois", 8.77, LOYER_HC / SURF, 0.05)
    calcule("prix au m2 sur 48,71 m2 Carrez", 2053.0, PRIX / SURF, 0.5)
    calcule("acte en main (99 999 + 8 000)", ACTE_EN_MAIN, PRIX * 1.08, 1.0)

    BASE = scen(rec_, VAC_BASE, GESTION_BASE_PCT, TF_BASE, PROV_BASE)
    BEST = scen(rec_, VAC_BEST, 4.0, 650.0, 100.0)
    WORST = scen(rec_, VAC_WORST, GESTION_BASE_PCT, 900.0, 320.0)
    INVERSE = lecture_inverse(rec_)

    calcule("EBE base", 3164.0, BASE['ebe'], 1.0)
    calcule("EBE best", 3518.0, BEST['ebe'], 1.0)
    calcule("EBE worst", 2638.0, WORST['ebe'], 1.0)
    calcule("EBE mensuel base", 264.0, BASE['ebe_mois'], 1.0)
    calcule("EBE mensuel best", 293.0, BEST['ebe_mois'], 1.0)
    calcule("EBE mensuel worst", 220.0, WORST['ebe_mois'], 1.0)
    calcule("rendement base avant IS", 2.93, BASE['rdt_av'], 0.01)
    calcule("rendement best avant IS", 3.26, BEST['rdt_av'], 0.01)
    calcule("rendement worst avant IS", 2.44, WORST['rdt_av'], 0.01)
    calcule("rendement base apres IS (convention prudente)", 2.49,
            BASE['rdt_ap'], 0.01)
    calcule("rendement best apres IS (convention prudente)", 2.77,
            BEST['rdt_ap'], 0.01)
    calcule("rendement worst apres IS (convention prudente)", 2.08,
            WORST['rdt_ap'], 0.01)
    calcule("plafond 5 % base", 58598.0, BASE['cap5'], 5.0)
    calcule("plafond 5 % best", 65150.0, BEST['cap5'], 5.0)
    calcule("plafond 5 % worst", 48851.0, WORST['cap5'], 5.0)
    calcule("mensualite 89 999 EUR", MENS_MODELE, mensualite(CAPITAL), 1.0)
    calcule("mensualite par euro emprunte", MENS_PAR_EURO_MODELE, MPE, 0.00001)
    calcule("cash-flow base /mois", -414.0, BASE['cf'], 1.0)
    calcule("cash-flow base /an", -4968.0, BASE['cf'] * 12, 2.0)
    calcule("cash-flow best /mois", -385.0, BEST['cf'], 1.0)
    calcule("cash-flow worst /mois", -458.0, WORST['cf'], 1.0)
    calcule("cash-flow lecture inverse /mois", -250.0, INVERSE['cf'], 1.0)
    calcule("prix a cash-flow nul (base)", 38906.0, prix_cashflow_nul(BASE['ebe']), 5.0)
    calcule("apport pour cash-flow nul au prix affiche (base)", 64984.0,
            apport_cashflow_nul(PRIX, BASE['ebe']), 5.0)
    calcule("part de prix a payer pour 5 % net (base)", 41.0,
            (1 - BASE['cap5'] / PRIX) * 100.0, 0.5)
    calcule("decote de prix pour 5 % net (base)", 41.0,
            (PRIX - BASE['cap5']) / PRIX * 100.0, 0.5)
    calcule("decote de prix pour cash-flow nul", 61.0,
            (PRIX - prix_cashflow_nul(BASE['ebe'])) / PRIX * 100.0, 0.5)
    calcule("apport pour cash-flow nul en % du prix", 65.0,
            apport_cashflow_nul(PRIX, BASE['ebe']) / PRIX * 100.0, 0.5)
    calcule("cash-flow nul : apport pour un cash-flow nul au prix affiche", 64984.0,
            apport_cashflow_nul(PRIX, BASE['ebe']), 5.0)
    # Chiffres narratifs du record : recalcules, jamais tapes a la main
    ECART_LECTURES = INVERSE['ebe'] - BASE['ebe']
    TRESORERIE_15 = abs(cashflow_mensuel(BASE['ebe']) * 12 * DUREE_ANS)
    calcule("ecart de resultat entre les deux lectures", 1974.0,
            ECART_LECTURES, 2.0)
    calcule("tresorerie consommee sur quinze ans", 74533.0, TRESORERIE_15, 5.0)
    for ris in rec_['analyse']['risques']:
        ris['detail'] = ris['detail'].replace(
            "686 €/an de résultat", f"{eur(ECART_LECTURES)} €/an de résultat")
        ris['detail'] = ris['detail'].replace(
            "−74 520 € de trésorerie", f"−{eur(TRESORERIE_15)} € de trésorerie")
    # Fiscalite annee 1
    calcule("interets annee 1 (89 999 a 3,7 %)", 3330.0, INTERETS_AN1, 1.0)
    calcule("dotation annee 1 (bati 80 % du prix sur 30 ans)", 2667.0,
            DOTATION_AN1, 1.0)
    calcule("resultat imposable annee 1", -2832.0,
            BASE['ebe'] - INTERETS_AN1 - DOTATION_AN1, 1.0)
    assert BASE['ebe'] - INTERETS_AN1 - DOTATION_AN1 < 0, "resultat annee 1 positif"
    calcule("IS annee 1 (resultat negatif)", 0.0, max(0.0, 0.15 * (
        BASE['ebe'] - INTERETS_AN1 - DOTATION_AN1)), 0.0)
    calcule("IS convention prudente (15 % de l'EBE)", 475.0,
            CONVENTION_IS * BASE['ebe'], 1.0)
    # Valeur de marche et comparables
    calcule("valeur retenue = 48,71 x 2 109", VALEUR_RETENUE,
            SURF * DVF_APP_4560_MED, 10.0)
    calcule("valeur basse = 48,71 x 1 791", VALEUR_BASSE,
            SURF * DVF_APP_4560_Q1, 10.0)
    calcule("valeur haute = 48,71 x 2 606", VALEUR_HAUTE,
            SURF * DVF_APP_4560_Q3, 10.0)
    calcule("prix affiche / valeur retenue", 0.97,
            PRIX / VALEUR_RETENUE, 0.01)
    calcule("ratio cout/valeur (acte en main / valeur)",
            ACTE_EN_MAIN / VALEUR_RETENUE,
            engine.ratio_cout_valeur(rec_), 0.001)
    calcule("prix affiche au plafond patrimonial 6,5 % (x fois)", 2.0,
            (PRIX / SURF) / PLAF_PATRIMONIAL[0], 0.05)
    calcule("marge negative du MDB", -5269.0,
            -(ACTE_EN_MAIN - VALEUR_RETENUE), 5.0)
    calcule("lecture inverse : EBE", 5138.0, INVERSE['ebe'], 1.0)
    calcule("lecture inverse : rendement avant IS", 4.76, INVERSE['rdt_av'], 0.01)
    calcule("lecture inverse : rendement apres IS", 4.04, INVERSE['rdt_ap'], 0.01)
    calcule("lecture inverse : plafond 5 %", 95148.0, INVERSE['cap5'], 5.0)
    calcule("lecture inverse : ecart au prix affiche", 4.9,
            (PRIX - INVERSE['cap5']) / PRIX * 100.0, 0.05)
    # Somme des loyers = strategie retenue (le moteur additionne toutes les lignes)
    total_loyers = sum(l['loyer_mensuel_euros'] for l in rec_['marche']['loyers'])
    calcule("somme des loyers saisis = loyer encaissable", LOYER_HC, total_loyers, 0.01)
    calcule("loyers saisis x 12 = revenus bruts du modele", REVENUS,
            total_loyers * 12.0, 0.5)
    calcule("tantièmes du lot / total copropriete", 0.88,
            TANTIEMES_LOT / TANTIEMES_TOTAL * 100.0, 0.01)

    # ------------------------------------------------------------------
    # 3. Moteur : l'EBE du moteur doit egaler celui du modele
    # ------------------------------------------------------------------
    r = engine.compute(rec_)
    note, verdict, comp = scoring.note_et_verdict(rec_, r)
    rd = r['rendements']
    assert r['calculable'], r['raison']
    assert schema.validate_record(rec_) == [], schema.validate_record(rec_)
    assert schema.champs_manquants(rec_) == [], schema.champs_manquants(rec_)
    print(f"  moteur : calculable={r['calculable']} | EBE {eur(r['fiscal']['ebe'])} EUR | "
          f"IS {eur(r['fiscal']['is_annuel'])} | net {eur(r['fiscal']['net_apres_is'])} | "
          f"CF {eur(r['fiscal']['cf_mensuel_net'])} EUR/mois")
    print(f"  moteur : net/revient {fr(rd['net_sur_revient_pct'])} % | net/achat "
          f"{fr(rd['net_sur_achat_pct'])} % | net/valeur {fr(rd['net_sur_valeur_pct'])} % "
          f"| ratio {fr(r['ratio_cout_valeur'])}")
    print(f"  moteur : revenus bruts {eur(r['revenus_bruts_annuels'])} EUR | frais "
          f"{eur(r['frais_acquisition'])} EUR | revient {eur(r['prix_revient_total'])} EUR")
    print(f"  note {note}/10 | verdict {verdict} | {comp}")
    assert abs(r['fiscal']['ebe'] - BASE['ebe']) < 0.01, (r['fiscal']['ebe'], BASE['ebe'])
    assert abs(r['fiscal']['amortissement']) < 0.01, r['fiscal']['amortissement']
    assert abs(rd['net_sur_revient_pct'] - BASE['rdt_ap']) < 0.01, rd
    assert abs(rd['net_sur_valeur_pct'] - BASE['rdt_valeur']) < 0.01, rd
    assert abs(r['prix_revient_total'] - ACTE_EN_MAIN) < 0.01, r['prix_revient_total']
    assert abs(r['revenus_bruts_annuels'] - REVENUS) < 0.01, r['revenus_bruts_annuels']
    assert verdict == "fuir", verdict
    assert comp.get('bloquant') is True, comp
    assert note == 3.9, note

    # ------------------------------------------------------------------
    # 4. Generation de la fiche
    # ------------------------------------------------------------------
    spec = importlib.util.spec_from_file_location(
        "gen", os.path.join(ROOT, 'scripts', 'gen_fiches_2026-09-10.py'))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)

    MENS_BASE = mensualite(CAPITAL)
    CF_BASE = BASE['cf']
    CF_BASE_AN = CF_BASE * 12.0
    CF_BEST = BEST['cf']
    CF_WORST = WORST['cf']
    CF_INVERSE = INVERSE['cf']

    def ligne(label, val, cls=""):
        c = f' class="{cls}"' if cls else ''
        return f'            <tr{c}><td>{label}</td><td class="num">{val}</td></tr>'

    def compte(d, titre, sous):
        rows = [
            ligne("Loyer facial du bail (610 € charges comprises)",
                  f"{eur(d['brut_facial'])} €"),
            ligne("dont charges de copropriété du lot (183 €/mois, chauffage et "
                  "eau froide compris)", f"-{eur(d['copro'])} €"),
            ligne("Loyers bruts réellement encaissables", f"{eur(d['brut'])} €",
                  "subtotal"),
            ligne(f"Vacance locative {fr(d['vac'], 0)} %",
                  f"-{eur(d['vac_eur'])} €"),
            ligne(f"Gestion locative {fr(d['gestion'], 0)} %",
                  f"-{eur(d['gestion_eur'])} €"),
            ligne("Taxe foncière (estimation, avis non communiqué)",
                  f"-{eur(d['tf'])} €"),
            ligne("Assurance PNO", f"-{eur(PNO)} €"),
            ligne("Provision travaux", f"-{eur(d['provision'])} €"),
            ligne("Comptabilité SCI à l'IS", f"-{eur(COMPTA)} €"),
            ligne("Excédent brut d'exploitation", f"{eur(d['ebe'])} €", "subtotal"),
            ligne("IS 15 % de l'EBE (convention prudente)",
                  f"-{eur(d['is_'])} €"),
            ligne("Net après IS", f"{eur(d['net'])} €", "highlight"),
            ligne("EBE mensuel", f"{eur(d['ebe_mois'])} €/mois"),
            ligne("Rendement brut affiché par l'agence (loyer facial)", 
                  f"{fr(d['rdt_brut_affiche'])} %"),
            ligne("Rendement brut réel hors charges",
                  f"{fr(d['rdt_brut_reel'])} %"),
            ligne("Rendement net avant IS sur l'acte en main",
                  f"{fr(d['rdt_av'])} %", "highlight"),
            ligne("Rendement net après IS sur l'acte en main",
                  f"{fr(d['rdt_ap'])} %"),
            ligne(f"Rendement net après IS sur la valeur ({eur(VALEUR_RETENUE)} €)",
                  f"{fr(d['rdt_valeur'])} %"),
            ligne("Prix d'achat tenant 5 % net avant IS", f"{eur(d['cap5'])} €"),
            ligne("Écart au prix affiché",
                  f"{eur(d['cap5'] - PRIX)} €"),
            ligne("Cash-flow mensuel après crédit (apport 10 %)",
                  f"{eur(d['cf'])} €/mois"),
        ]
        return f"""      <div class="projection-card scenario-{titre}">
        <h3>{sous}</h3>
        <p class="scenario-subtitle">{eur(d['brut'])} €/mois encaissables, vacance {fr(d['vac'], 0)} % — EBE {eur(d['ebe_mois'])} €/mois — cash-flow {eur(d['cf'])} €/mois</p>
        <table class="projection-table"><tbody>
{chr(10).join(rows)}
        </tbody></table>
      </div>"""

    cartes = [
        compte(BASE, "base",
               "Base — bail en cours, loyer encaissable 427,25 €/mois"),
        compte(BEST, "optimiste",
               "Optimiste — vacance 3 %, gestion 4 %, TF 650 €, provision 100 €"),
        compte(WORST, "pessimiste",
               "Pessimiste — vacance 10 %, TF 900 €, provision 320 €"),
    ]

    # ------------------------------------------------------------------
    # Ce que l'annonce affirme, ce que le dossier paie
    # ------------------------------------------------------------------
    charges_rows = [
        ("Loyer du bail, charges comprises",
         f"{eur(LOYER_CC, 2)} €/mois",
         f"soit {fr(LOYER_CC / SURF, 1)} €/m²/mois — c'est ce que le locataire "
         f"verse, et c'est le chiffre que l'agence met en avant"),
        ("Charges de copropriété comprises dans ce loyer",
         f"−{eur(CHARGES_MOIS, 2)} €/mois",
         f"soit {eur(CHARGES_COPRO)} €/an, chauffage collectif au fioul et eau "
         f"froide compris : {fr(PART_CHARGES, 1)} % du loyer"),
        ("Loyer hors charges réellement encaissable",
         f"{eur(LOYER_HC, 2)} €/mois",
         f"soit {eur(REVENUS)} €/an et {fr(LOYER_HC / SURF, 2)} €/m²/mois : c'est "
         f"le seul revenu du dossier"),
        ("Charges de copropriété rapportées à l'année",
         f"{eur(CHARGES_COPRO)} €/an",
         "structurelles, récurrentes, non pilotables par le propriétaire — ni le "
         "locataire, ni la gestion, ni le prix d'achat ne les changent"),
    ]
    charges_html = "\n".join(
        f'        <tr><td>{a}</td><td class="num">{b}</td><td>{c}</td></tr>'
        for a, b, c in charges_rows)

    faux7_rows = [
        ("Rendement brut affiché par l'agence",
         f"{eur(BRUT_FACIAL)} €/an",
         f"{fr(BRUT_FACIAL / PRIX * 100, 2)} %",
         "le chiffre de l'annonce : 610 € × 12 rapporté au prix affiché, comme si "
         "les 610 € étaient intégralement du revenu"),
        ("Rendement brut réel hors charges",
         f"{eur(REVENUS)} €/an",
         f"{fr(REVENUS / PRIX * 100, 2)} %",
         f"après déduction des {eur(CHARGES_COPRO)} €/an de copropriété : 2,2 "
         f"points de brut disparaissent avant même de parler de charges "
         f"d'exploitation"),
        ("Rendement net avant IS sur l'acte en main",
         f"{eur(BASE['ebe'])} €/an",
         f"{fr(BASE['rdt_av'])} %",
         f"EBE du scénario de base rapporté aux {eur(ACTE_EN_MAIN)} € d'acte en "
         f"main (prix + {eur(FRAIS_ACQUISITION)} € de frais)"),
        ("Rendement net après IS (convention prudente)",
         f"{eur(BASE['net'])} €/an",
         f"{fr(BASE['rdt_ap'])} %",
         "IS de 15 % appliqué à l'EBE, sans amortissement du bâti modélisé — la "
         "lecture la plus défavorable, celle que publie le listing du dépôt"),
        ("Écart entre le 7 % annoncé et le net réel",
         f"{fr(BRUT_FACIAL / PRIX * 100 - BASE['rdt_ap'], 2)} points",
         "÷ 2,9",
         f"le rendement net réel vaut {fr(BASE['rdt_ap'] / (BRUT_FACIAL / PRIX * 100) * 100, 0)} % "
         f"du rendement affiché"),
    ]
    faux7_html = "\n".join(
        f'        <tr><td>{a}</td><td class="num">{b}</td><td class="num">{c}</td>'
        f'<td>{d}</td></tr>' for a, b, c, d in faux7_rows)

    inverse_rows = [
        ("Loyer brut annuel", f"{eur(INVERSE['brut'])} €", f"{eur(BASE['brut'])} €"),
        ("Excédent brut d'exploitation", f"{eur(INVERSE['ebe'])} €",
         f"{eur(BASE['ebe'])} €"),
        ("EBE mensuel", f"{eur(INVERSE['ebe_mois'])} €/mois",
         f"{eur(BASE['ebe_mois'])} €/mois"),
        ("Rendement net avant IS (acte en main)", f"{fr(INVERSE['rdt_av'])} %",
         f"{fr(BASE['rdt_av'])} %"),
        ("Rendement net après IS (convention prudente)",
         f"{fr(INVERSE['rdt_ap'])} %", f"{fr(BASE['rdt_ap'])} %"),
        ("Cash-flow mensuel après crédit", f"{eur(INVERSE['cf'])} €/mois",
         f"{eur(BASE['cf'])} €/mois"),
        ("Prix d'achat tenant 5 % net avant IS", f"{eur(INVERSE['cap5'])} €",
         f"{eur(BASE['cap5'])} €"),
        ("Écart au prix affiché",
         f"{eur(INVERSE['cap5'] - PRIX)} €", f"{eur(BASE['cap5'] - PRIX)} €"),
    ]
    inverse_html = "\n".join(
        f'        <tr><td>{a}</td><td class="num">{b}</td><td class="num">{c}</td></tr>'
        for a, b, c in inverse_rows)

    charges_section = f"""  <section class="financial-projections">
    <h2>Le chiffre qui tue le dossier — 2 193 €/an de charges de copropriété, soit 30,0 % du loyer</h2>
    <p class="attractiveness-intro">L'annonce affirme : « vendu loué avec un bail nu 610 € charges comprises, offrant une rentabilité brute d'environ 7 % ». Ce 7 % est faux, et la démonstration tient en une ligne que l'annonce donne elle-même : <strong>les charges de copropriété du lot sont de {eur(CHARGES_COPRO)} €/an, soit {eur(CHARGES_MOIS)} €/mois, avec le chauffage collectif au fioul et l'eau froide compris dans les charges</strong>. Le locataire paye donc {eur(LOYER_CC)} € charges comprises, et il ne reste au propriétaire que <strong>{eur(LOYER_HC, 2)} € par mois</strong> — {eur(REVENUS)} € par an. Le rendement brut de 7,32 % est calculé sur le loyer facial ; le rendement brut réel hors charges tombe à <strong>{fr(REVENUS / PRIX * 100, 2)} %</strong>, et le rendement net avant IS sur l'acte en main à <strong>{fr(BASE['rdt_av'])} %</strong>. Un poste de charges qui absorbe {fr(PART_CHARGES, 1)} % du loyer ne se corrige ni par la gestion, ni par une renégociation du bail, ni par le prix payé : il est dans la structure de la copropriété.</p>
    <table class="projection-table compare">
      <thead><tr><th>Du loyer affiché au loyer encaissable</th><th class="num">Montant</th><th>Lecture</th></tr></thead>
      <tbody>
{charges_html}
      </tbody>
    </table>
    <table class="projection-table compare">
      <thead><tr><th>Le 7 % de l'agence, décomposé</th><th class="num">Base annuelle</th><th class="num">Rendement</th><th>Lecture</th></tr></thead>
      <tbody>
{faux7_html}
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Et le prix n'est pas le problème.</strong> À {eur(PRIX / SURF)} €/m², ce bien est exactement au prix du marché de sa tranche de surface : la médiane DVF 2025 des appartements de 45 à 60 m² à Brignoles est de {eur(DVF_APP_4560_MED)} €/m² sur {DVF_APP_4560_N} ventes, et {DVF_APP_4560_N} ventes suffisent à en faire une référence solide. Le dossier n'est donc pas « cher » : il est mal structuré. {eur(CHARGES_COPRO)} €/an de charges sur {eur(BRUT_FACIAL)} €/an de loyer facial, dans une copropriété de {LOTS_COPRO} lots de 1970 chauffée au fioul collectif, cela veut dire que le rendement est décidé au moment du vote du budget de copropriété — pas au moment de la négociation du prix. <strong>Aucune négociation réaliste ne rattrape 3,5 points de rendement : il faudrait payer le bien {eur(BASE['cap5'])} € pour atteindre 5 % net avant IS, soit {fr((PRIX - BASE['cap5']) / PRIX * 100, 0)} % sous le prix affiché.</strong></p>
    </div>
  </section>"""

    lecture = (
        f"On fuit. Pas à cause du prix — à {eur(PRIX / SURF)} €/m² il est exactement "
        f"au prix du marché de sa tranche de surface ({eur(DVF_APP_4560_MED)} €/m² sur "
        f"{DVF_APP_4560_N} ventes DVF 2025 de 45 à 60 m²) —, mais parce que "
        f"{eur(CHARGES_COPRO)} €/an de charges de copropriété, chauffage collectif "
        f"au fioul et eau froide compris, absorbent {fr(PART_CHARGES, 1)} % du loyer "
        f"de {eur(LOYER_CC)} € et ne laissent que {eur(LOYER_HC, 2)} €/mois "
        f"encaissables. Le bail annoncé à 610 € charges comprises ne produit donc "
        f"pas 7 % de rendement brut mais {fr(REVENUS / PRIX * 100, 2)} % de brut réel "
        f"et {fr(BASE['rdt_av'])} % net avant IS sur l'acte en main, avec un "
        f"cash-flow de {eur(CF_BASE)} €/mois sous crédit. Et ce n'est pas un dossier "
        f"de négociation : il faudrait {eur(BASE['cap5'])} € pour retrouver 5 % net "
        f"avant IS ({fr((PRIX - BASE['cap5']) / PRIX * 100, 0)} % sous le prix "
        f"affiché) et {eur(prix_cashflow_nul(BASE['ebe']))} € pour un cash-flow nul "
        f"({fr((PRIX - prix_cashflow_nul(BASE['ebe'])) / PRIX * 100, 0)} % sous). "
        f"L'échappatoire du vendeur — « le bail porte 610 € nets de provisions sur "
        f"charges » — ne sauve rien : le net remonte à {fr(INVERSE['rdt_av'])} % "
        f"avant IS et {fr(INVERSE['rdt_ap'])} % après IS, le cash-flow reste à "
        f"{eur(INVERSE['cf'])} €/mois et le plafond à {eur(INVERSE['cap5'])} €, "
        f"encore {fr((PRIX - INVERSE['cap5']) / PRIX * 100, 1)} % sous le prix "
        f"affiché. <strong>Dans toutes les lectures possibles, ce dossier échoue.</strong>"
    )

    cf_besoins_rows = [
        ("Prix d'achat à cash-flow nul, 10 % d'apport, loyers encaissables de "
         f"{eur(LOYER_HC, 2)} €/mois",
         f"{eur(prix_cashflow_nul(BASE['ebe']))} €",
         f"{fr((PRIX - prix_cashflow_nul(BASE['ebe'])) / PRIX * 100, 0)} % sous le "
         f"prix affiché"),
        ("Apport pour un cash-flow nul au prix affiché",
         f"{eur(apport_cashflow_nul(PRIX, BASE['ebe']))} €",
         f"{fr(apport_cashflow_nul(PRIX, BASE['ebe']) / PRIX * 100, 0)} % du prix — "
         f"hors doctrine du parc (10 %)"),
        ("Prix d'achat tenant 5 % net avant IS",
         f"{eur(BASE['cap5'])} €",
         f"{fr((PRIX - BASE['cap5']) / PRIX * 100, 0)} % sous le prix affiché"),
        ("Durée portée à 20 ans",
         f"{eur(mensualite_actuarielle(CAPITAL, 20))} €/mois",
         f"cash-flow {eur(BASE['ebe_mois'] - mensualite_actuarielle(CAPITAL, 20))} €/mois "
         f"— le déficit se réduit, il ne disparaît pas"),
        ("Durée portée à 25 ans",
         f"{eur(mensualite_actuarielle(CAPITAL, 25))} €/mois",
         f"cash-flow {eur(BASE['ebe_mois'] - mensualite_actuarielle(CAPITAL, 25))} €/mois "
         f"— il faudrait 25 ans de crédit pour approcher l'équilibre"),
        ("Loyer mensuel qu'il faudrait encaisser",
         f"{eur((MENS_BASE * 12 + TF_BASE + PNO + COMPTA + REVENUS * 0.05 + PROV_BASE) / (12 * 0.95 - 0.05 * 12))} €/mois",
         "charges du scénario de base inchangées : impossible sur un T2 de "
         "48,71 m² à Brignoles, dont la référence est 11,0 €/m²/mois"),
    ]
    cf_besoins_html = "\n".join(
        f'        <tr><td>{a}</td><td class="num">{b}</td><td>{c}</td></tr>'
        for a, b, c in cf_besoins_rows)

    cf_section = f"""  <section class="financial-projections">
    <h2>Cash-flow après crédit — service de la dette, apport et durée</h2>
    <p class="attractiveness-intro"><strong>Hypothèses de crédit (doctrine du parc) :</strong> apport 10 %, frais de notaire assumés à part, prêt de {eur(CAPITAL)} € sur {DUREE_ANS} ans à 3,7 %, assurance emprunteur 0,34 % du capital. Mensualité <strong>{eur(MENS_BASE)} €/mois</strong>, soit <strong>0,00753 € par euro emprunté</strong>. Face à une exploitation de {eur(BASE['ebe_mois'])} €/mois en scénario de base, il manque <strong>{eur(abs(CF_BASE))} €/mois</strong> — et dans la lecture la plus favorable au vendeur, {eur(abs(CF_INVERSE))} €/mois.</p>
    <div class="projections-grid">
      <div class="projection-card scenario-base">
        <h3>Base — bail en cours</h3>
        <p class="scenario-subtitle">Prêt {eur(CAPITAL)} € sur {DUREE_ANS} ans — apport 10 %</p>
        <table class="projection-table"><tbody>
            <tr><td>Loyer facial du bail</td><td class="num">{eur(LOYER_CC, 2)} €/mois</td></tr>
            <tr><td>Loyer encaissable après charges de copropriété</td><td class="num">{eur(LOYER_HC, 2)} €/mois</td></tr>
            <tr><td>Net d'exploitation mensuel (EBE)</td><td class="num">{eur(BASE['ebe_mois'])} €</td></tr>
            <tr><td>Mensualité de crédit (assurance incluse)</td><td class="num">-{eur(MENS_BASE)} €</td></tr>
            <tr class="highlight"><td>Cash-flow mensuel</td><td class="num">{eur(CF_BASE)} €</td></tr>
            <tr><td>Cash-flow annuel</td><td class="num">{eur(CF_BASE_AN)} €</td></tr>
        </tbody></table>
      </div>
      <div class="projection-card scenario-optimiste">
        <h3>Optimiste — vacance 3 %, gestion 4 %</h3>
        <p class="scenario-subtitle">Prêt {eur(CAPITAL)} € sur {DUREE_ANS} ans — apport 10 %</p>
        <table class="projection-table"><tbody>
            <tr><td>Loyer encaissable</td><td class="num">{eur(LOYER_HC, 2)} €/mois</td></tr>
            <tr><td>Net d'exploitation mensuel (EBE)</td><td class="num">{eur(BEST['ebe_mois'])} €</td></tr>
            <tr><td>Mensualité de crédit (assurance incluse)</td><td class="num">-{eur(MENS_BASE)} €</td></tr>
            <tr class="highlight"><td>Cash-flow mensuel</td><td class="num">{eur(CF_BEST)} €</td></tr>
            <tr><td>Cash-flow annuel</td><td class="num">{eur(CF_BEST * 12)} €</td></tr>
        </tbody></table>
      </div>
      <div class="projection-card scenario-pessimiste">
        <h3>Pessimiste — vacance 10 %, provision 320 €</h3>
        <p class="scenario-subtitle">Prêt {eur(CAPITAL)} € sur {DUREE_ANS} ans — apport 10 %</p>
        <table class="projection-table"><tbody>
            <tr><td>Loyer encaissable</td><td class="num">{eur(LOYER_HC, 2)} €/mois</td></tr>
            <tr><td>Net d'exploitation mensuel (EBE)</td><td class="num">{eur(WORST['ebe_mois'])} €</td></tr>
            <tr><td>Mensualité de crédit (assurance incluse)</td><td class="num">-{eur(MENS_BASE)} €</td></tr>
            <tr class="highlight"><td>Cash-flow mensuel</td><td class="num">{eur(CF_WORST)} €</td></tr>
            <tr><td>Cash-flow annuel</td><td class="num">{eur(CF_WORST * 12)} €</td></tr>
        </tbody></table>
      </div>
    </div>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Un déficit de trésorerie permanent, pas un déficit de démarrage.</strong> Au prix affiché et avec 10 % d'apport, il manque <strong>{eur(abs(CF_BASE))} €/mois</strong> ({eur(abs(CF_BASE_AN))} €/an) au bien pour payer sa mensualité, soit {eur(abs(CF_BASE_AN * DUREE_ANS))} € de trésorerie consommée sur quinze ans. Le déficit est négatif dans toutes les lectures : {eur(CF_BEST)} €/mois en hypothèse favorable, {eur(CF_WORST)} €/mois en hypothèse défavorable, {eur(CF_INVERSE)} €/mois dans la lecture la plus favorable au vendeur (bail de 610 € nets de provisions). Aucun scénario ne produit un cash-flow positif, et ce n'est pas un effet de la durée du crédit : à 25 ans il manque encore {eur(BASE['ebe_mois'] - mensualite_actuarielle(CAPITAL, 25))} €/mois. C'est la signature d'un dossier où le revenu net est trop faible pour le capital emprunté, et le revenu net est faible parce que la copropriété prend {fr(PART_CHARGES, 1)} % du loyer.</p>
      <p class="attractiveness-intro"><strong>Fiscalité année 1 — ici, la fiscalité protège au lieu de pénaliser.</strong> Intérêts d'emprunt {eur(INTERETS_AN1)} € ({eur(CAPITAL)} € à 3,7 %) et dotation aux amortissements {eur(DOTATION_AN1)} € (bâti à 80 % du prix sur 30 ans, soit {eur(QUOTE_PART_BATI_MODELE * 100, 0)} % de {eur(PRIX)} €) : le résultat imposable de l'année 1 est <strong>négatif de {eur(abs(BASE['ebe'] - INTERETS_AN1 - DOTATION_AN1))} €</strong>, donc <strong>aucun IS dû en année 1</strong>, le déficit étant reporté. Les rendements publiés ici retiennent malgré tout la convention prudente du moteur — <strong>IS de 15 % appliqué à l'EBE</strong>, soit {eur(CONVENTION_IS * BASE['ebe'])} €/an, sans amortissement du bâti modélisé — parce que c'est la lecture la plus défavorable et celle que publie le listing du dépôt. Que l'impôt soit nul ou non, le dossier échoue pour la même raison : {fr(BASE['rdt_av'])} % net avant IS contre un seuil de 6,5 % net d'IS.</p>
    </div>
    <h3>Ce qu'il faudrait pour un cash-flow nul, ou pour 5 % net</h3>
    <table class="projection-table compare">
      <thead><tr><th>Levier</th><th class="num">Valeur</th><th>Lecture</th></tr></thead>
      <tbody>
{cf_besoins_html}
      </tbody>
    </table>
  </section>"""

    inverse_section = f"""  <section class="financial-projections">
    <h2>Lecture inverse — et si le bail portait 610 € nets de provisions sur charges ?</h2>
    <p class="attractiveness-intro">C'est la seule objection que le vendeur puisse opposer : « les 610 € du bail sont du loyer, les provisions sur charges sont payées en sus par le locataire et couvrent la copropriété ». Aucune pièce ne le démontre — ni le bail, ni une régularisation, ni une quittance — mais l'hypothèse mérite d'être publiée parce qu'elle est la plus favorable possible au dossier, et qu'<strong>elle ne le sauve pas</strong>. Dans cette lecture, le propriétaire encaisse {eur(LOYER_CC)} €/mois ({eur(INVERSE['brut'])} €/an), les {eur(CHARGES_COPRO)} €/an de copropriété sont couverts par les provisions du locataire et ne sont plus à sa charge, mais il supporte toujours sa taxe foncière estimée {eur(TF_BASE)} €, son assurance PNO {eur(PNO)} €, sa comptabilité {eur(COMPTA)} €, sa gestion locative {fr(GESTION_BASE_PCT, 0)} % et sa provision travaux {eur(PROV_BASE)} €, avec la même vacance de {fr(VAC_BASE, 0)} %.</p>
    <table class="projection-table compare">
      <thead><tr><th>Indicateur</th><th class="num">Lecture inverse — 610 € nets de provisions</th><th class="num">Scénario de base — 610 € charges comprises</th></tr></thead>
      <tbody>
{inverse_html}
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Concluons sur les deux lectures.</strong> Si les 610 € sont chargés de {eur(CHARGES_MOIS)} €/mois de provisions, le net avant IS est de {fr(BASE['rdt_av'])} % et le cash-flow de {eur(CF_BASE)} €/mois. Si les 610 € sont du loyer pur et que le locataire paye les charges en sus, le net remonte à {fr(INVERSE['rdt_av'])} % ({fr(INVERSE['rdt_ap'])} % après IS), le plafond 5 % à {eur(INVERSE['cap5'])} € — encore {fr((PRIX - INVERSE['cap5']) / PRIX * 100, 1)} % sous le prix affiché — et le cash-flow reste à <strong>{eur(INVERSE['cf'])} €/mois</strong>. Autrement dit : la pièce manquante vaut {eur(INVERSE['ebe'] - BASE['ebe'])} €/an de résultat et {fr(INVERSE['rdt_av'] - BASE['rdt_av'])} point de rendement net, mais elle ne fait pas passer le dossier d'un côté à l'autre de la barre. <strong>Le bail et la dernière régularisation de charges restent les deux premières pièces à exiger — pour éliminer l'ambiguïté, pas parce qu'elles sauveraient l'opération.</strong></p>
    </div>
  </section>"""

    marche_section = f"""  <section class="financial-projections">
    <h2>Marché local — DVF 2025 réelle de la commune et fiche de référence</h2>
    <p class="attractiveness-intro">Les {DVF_VENTES} mutations de nature « Vente » enregistrées en 2025 à Brignoles donnent un marché liquide, et la tranche de surface du bien — 45 à 60 m² — y est suffisamment fournie pour servir d'ancrage : {DVF_APP_4560_N} ventes d'appartements, médiane {eur(DVF_APP_4560_MED)} €/m², premier quartile {eur(DVF_APP_4560_Q1)} et troisième {eur(DVF_APP_4560_Q3)}. Méthode : valeur foncière de la mutation divisée par la somme des surfaces bâties de la mutation, surfaces supérieures à 5 m² et valeurs supérieures à 5 000 €.</p>
    <table class="projection-table compare">
      <thead><tr><th>Segment DVF 2025 — Brignoles (83023)</th><th class="num">Mutations</th><th class="num">Médiane €/m²</th><th>Lecture</th></tr></thead>
      <tbody>
        <tr><td>Appartements, toutes surfaces</td><td class="num">{DVF_APP_N}</td><td class="num">{eur(DVF_APP_MED)} €</td><td>moyenne communale, non applicable au bien : le prix au m² décroît avec la surface</td></tr>
        <tr><td>Appartements de 15 à 30 m²</td><td class="num">{DVF_APP_1530_N}</td><td class="num">{eur(DVF_APP_1530_MED)} €</td><td>échantillon trop étroit pour servir de référence</td></tr>
        <tr><td>Appartements de 30 à 45 m²</td><td class="num">{DVF_APP_3045_N}</td><td class="num">{eur(DVF_APP_3045_MED)} €</td><td>prix médian de la tranche : {eur(DVF_APP_3045_PRIX)} € — les petites surfaces se paient le plus cher au m²</td></tr>
        <tr class="highlight"><td>Appartements de 45 à 60 m² — <strong>la tranche du bien</strong></td><td class="num">{DVF_APP_4560_N}</td><td class="num">{eur(DVF_APP_4560_MED)} €</td><td>de {eur(DVF_APP_4560_Q1)} à {eur(DVF_APP_4560_Q3)} €/m² : c'est la référence de cet appartement de {fr(SURF)} m²</td></tr>
        <tr><td>Appartements de 60 à 90 m²</td><td class="num">{DVF_APP_6090_N}</td><td class="num">{eur(DVF_APP_6090_MED)} €</td><td>la décote de surface se voit : {eur(DVF_APP_6090_MED)} €/m² contre {eur(DVF_APP_3045_MED)} € sur 30-45 m²</td></tr>
        <tr><td>Maisons</td><td class="num">{DVF_MAI_N}</td><td class="num">{eur(DVF_MAI_MED)} €</td><td>autre produit ; {DVF_MAI_60120_N} ventes de 60 à 120 m² à un prix médian de {eur(DVF_MAI_60120_PRIX)} €</td></tr>
      </tbody>
    </table>
    <table class="projection-table compare">
      <thead><tr><th>Transaction comparable</th><th class="num">Surface</th><th class="num">Prix</th><th class="num">€/m²</th></tr></thead>
      <tbody>
        <tr><td>{DVF_CMP['voie']}, {DVF_CMP['date']} — {DVF_CMP['lots']} lots (un appartement de 70 m², un local de 9 m² et une dépendance) : c'est la même rue que l'agence, mais un produit mixte</td><td class="num">{eur(DVF_CMP['surf'])} m²</td><td class="num">{eur(DVF_CMP['prix'])} €</td><td class="num">{eur(DVF_CMP['m2'])} €</td></tr>
        <tr class="highlight"><td><strong>Le bien analysé</strong>, au prix affiché, sur les {fr(SURF)} m² Carrez</td><td class="num">{fr(SURF)} m²</td><td class="num">{eur(PRIX)} €</td><td class="num">{eur(PRIX / SURF)} €</td></tr>
        <tr><td>Tranche DVF 45-60 m² appliquée au bien (valeur retenue)</td><td class="num">{fr(SURF)} m²</td><td class="num">{eur(VALEUR_RETENUE)} €</td><td class="num">{eur(DVF_APP_4560_MED)} €</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Ce que disent les chiffres — et c'est le point qui distingue ce dossier des trois autres dossiers Brignoles du dépôt.</strong> À {eur(PRIX / SURF)} €/m², ce bien est <strong>exactement au prix du marché de sa tranche de surface</strong> : {eur(DVF_APP_4560_MED)} €/m² de médiane sur {DVF_APP_4560_N} ventes de 45 à 60 m² en 2025. Ce n'est pas un bien surpayé, ce n'est pas une décote mal exploitée, ce n'est pas une opération de marchand de biens : c'est un appartement payé à sa valeur, dont le rendement est détruit par {eur(CHARGES_COPRO)} €/an de charges de copropriété avec chauffage collectif compris. <strong>Le problème de ce dossier n'est pas le prix : c'est la structure de la copropriété et du bail.</strong> Tout l'intérêt de ce cas, pour la suite du sourcing, est là : sur un lot de copropriété, payer le prix du marché n'est pas une condition suffisante — ce qui décide, c'est le rapport entre le loyer encaissable et le budget de la copropriété.</p>
      <p class="attractiveness-intro"><strong>Référence interne de la commune</strong> (fiche <em>Marchés locaux</em> mise à jour le 21/09/2026) : marché {eur(MARCHE_M2_COMMUNE)} €/m², loyer de référence {fr(LOYER_REF_M2, 1)} €/m²/mois sur un lot type de 60 m², plafonds d'achat par m² habitable frais compris de {eur(PLAF_PATRIMONIAL[0])} € (6,5 % net d'IS), {eur(PLAF_PATRIMONIAL[1])} € (7,0 %) et {eur(PLAF_PATRIMONIAL[2])} € (8,0 %) en vision patrimoniale, et {eur(PLAF_MDB[0])} / {eur(PLAF_MDB[1])} / {eur(PLAF_MDB[2])} €/m² en vision marchand de biens. Ce dossier s'affiche à {eur(PRIX / SURF)} €/m², soit <strong>{fr((PRIX / SURF) / PLAF_PATRIMONIAL[0], 2)} fois le plafond patrimonial à 6,5 % net d'IS</strong> et {fr((PRIX / SURF) / PLAF_MDB[0], 1)} fois le plafond marchand de biens : la fiche de référence conclut déjà qu'aucune des douze villes du secteur n'offre le seuil patrimonial au prix de marché, et ce dossier ne fait pas exception — sauf qu'ici l'écart ne vient pas d'un prix trop haut, mais d'un revenu trop bas.</p>
      <p class="attractiveness-intro"><strong>À lire aussi dans le dépôt</strong> — <a href="../2026-09-25-immeuble-rapport-brignoles-vieille-ville/index.html">Immeuble de rapport en centre vieille ville, local commercial, studio et duplex (25/09/2026)</a>, <a href="../2026-09-18-immeuble-rapport-brignoles-centre/index.html">Immeuble de rapport Brignoles centre (18/09/2026)</a>, <a href="../2026-09-20-immeuble-rapport-brignoles-centre-ancien/index.html">Immeuble de rapport Brignoles centre ancien, 3 T3, Site Patrimonial Remarquable (20/09/2026)</a> et la <a href="../marches-locaux/index.html">fiche de référence des marchés locaux</a> (21/09/2026), qui donne pour Brignoles les plafonds d'achat utilisés ici. Les trois dossiers Brignoles précédents portaient sur des immeubles entiers de centre ancien, à des prix très en dessous de leur valeur d'usage, avec des inconnues de travaux et de loyers. <strong>Celui-ci est le premier cas de la commune où c'est le prix du marché qui est payé, sur un lot de copropriété — et il est le contre-exemple utile aux trois autres :</strong> il montre que le prix n'est pas le seul critère, et que 30 % du loyer en charges de copropriété suffisent à rendre un bien acheté au juste prix inexploitable.</p>
    </div>
  </section>"""

    gen.LECTURE[SLUG] = lecture
    gen.RECS[SLUG] = rec_
    gen.CONF = {SLUG: dict(
        titre_court="Appartement T2 vendu loué, résidence 1970 — Brignoles (83170)",
        adresse=(
            f"58 rue Jules Ferry, 83170 Brignoles — appartement T2 de {fr(SURF)} m² "
            f"au rez-de-chaussée sur 4 étages, terrasse de {eur(TERRASSE)} m² et "
            f"cave, dans une résidence de {ANNEE} avec parc arboré (quartier "
            f"« Extension Années 50-70 »)"
        ),
        date_fr=DATE_FR,
        source=(
            "SeLoger — annonce 269U5FFWGIGA (ABC IMMO BRIGNOLES, Mirlinda "
            "ZUMBEROVIC EI, RSAC Draguignan 991000282, référence annonce 1680)"
        ),
        url=URL,
        badge="Bien vendu loué — investissement locatif",
        strategie=(
            f"Conservation du bail nu en cours : loyer de {eur(LOYER_CC)} € charges "
            f"comprises, soit {eur(LOYER_HC, 2)} €/mois réellement encaissables "
            f"après les {eur(CHARGES_COPRO)} €/an de charges de copropriété"
        ),
        fiscal_note=(
            f"SCI à l'IS — résultat de l'année 1 négatif donc aucun IS dû ; "
            f"rendements nets publiés sous la convention prudente du moteur "
            f"(IS 15 % de l'EBE) ; seuil de décision du parc : 6,5 % net d'IS"
        ),
        lat="43.406238", lon="6.064848",
        quartier=(
            "Brignoles (83170) — quartier « Extension Années 50-70 », 17 000 "
            "habitants, entrée de l'autoroute A8, Saint-Maximin à 30 minutes, "
            "Toulon à 1 heure"
        ),
        intro_attr=(
            f"Brignoles est la sous-préfecture du centre Var : <strong>17 000 "
            f"habitants</strong>, commerces de centre, marché, écoles, collège et "
            f"lycée, zone d'activité et entrée de l'autoroute A8. Le bien est dans "
            f"une résidence de {ANNEE} avec parc arboré, portail automatique et "
            f"stationnement libre, en périphérie immédiate du centre — l'emplacement "
            f"d'un T2 familial, pas d'un studio d'étudiant. Le marché est documenté : "
            f"<strong>{DVF_VENTES} mutations de nature « Vente » en 2025</strong> "
            f"selon la base DVF, dont <strong>{DVF_APP_N} ventes d'appartements</strong> "
            f"à une médiane de <strong>{eur(DVF_APP_MED)} €/m²</strong> et "
            f"<strong>{DVF_MAI_N} ventes de maisons</strong> à "
            f"<strong>{eur(DVF_MAI_MED)} €/m²</strong>. La tranche 45-60 m², celle du "
            f"bien, affiche <strong>{eur(DVF_APP_4560_MED)} €/m² sur "
            f"{DVF_APP_4560_N} ventes</strong> : c'est la référence de prix retenue. "
            f"Côté locatif, les annonces relevées sur place le 25/09/2026 donnent "
            f"<strong>86 annonces actives</strong> — 1 pièce de 36 m² en vieille ville "
            f"à 450 € (12,5 €/m²), 2 pièces de 37 m² à 680 €, 3 pièces meublé de "
            f"50 m² à 800 €, place de parking à 120 € — avec un loyer de référence "
            f"communal de {fr(LOYER_REF_M2, 1)} €/m²/mois sur un lot type de 60 m² "
            f"(fiche de référence du 21/09/2026). La demande ne fait pas défaut. Ce "
            f"qui manque, c'est le rendement : <strong>"
            f"{eur(CHARGES_COPRO)} €/an de charges de copropriété, chauffage "
            f"collectif au fioul et eau froide compris, soit "
            f"{fr(PART_CHARGES, 1)} % du loyer du bail</strong>."
        ),
        profil=(
            "un locataire à l'année d'un T2 familial de 48 m² avec terrasse, cave "
            "et stationnement libre, dans une résidence arborée et fermée à quelques "
            "minutes des commerces et des écoles de Brignoles : jeune couple, "
            "famille d'un enfant, ou actif du centre Var. L'absence d'ascenseur ne "
            "pénalise pas ce lot, situé au rez-de-chaussée, et le double vitrage avec "
            "chauffage collectif limite la facture individuelle. Le profil est solide "
            "et le loyer facial (12,5 €/m²/mois) est au-dessus de la référence "
            "communale (11,0 €/m²/mois) : c'est le propriétaire qui n'est pas solvable "
            "à ce prix, pas le locataire qui manque"
        ),
        concl_attr=(
            f"Adéquation moyenne ({fr((5 + 6 + 7 + 6 + 7 + 7) / 6, 1)}/10). "
            f"L'emplacement, le produit et le prix sont bons : un T2 de "
            f"{fr(SURF)} m² avec terrasse, cave et stationnement dans une résidence "
            f"arborée de {ANNEE}, loué, sans travaux annoncés, acheté exactement au "
            f"prix du marché de sa tranche de surface "
            f"({eur(PRIX / SURF)} €/m² contre {eur(DVF_APP_4560_MED)} €/m² de médiane "
            f"sur {DVF_APP_4560_N} ventes). Le score est plombé par deux éléments qui "
            f"n'ont rien à voir avec le quartier. D'abord la structure de la "
            f"copropriété : <strong>{eur(CHARGES_COPRO)} €/an de charges, chauffage "
            f"collectif au fioul et eau froide compris, soit "
            f"{fr(PART_CHARGES, 1)} % du loyer</strong>, dans une copropriété de "
            f"{LOTS_COPRO} lots de 1970 dont la chaudière devra être convertie sans "
            f"qu'aucun DCE, PPT ou procès-verbal d'assemblée générale ne soit "
            f"communiqué. Ensuite la trésorerie : {eur(CF_BASE)} €/mois de cash-flow "
            f"négatif après crédit, dans tous les scénarios. On a donc ici un bien "
            f"correct, à un prix correct, qui ne s'achète pas — c'est un cas d'école "
            f"sur le poids réel des charges de copropriété"
        ),
        intro_strat=(
            "Cinq lectures ont été testées, toutes calculées par le moteur : la "
            f"conservation du bail en cours ({eur(LOYER_HC, 2)} €/mois encaissables, "
            f"{fr(BASE['rdt_av'])} % net avant IS), l'hypothèse favorable (3,26 %), "
            f"l'hypothèse défavorable (2,44 %), la lecture inverse où le bail "
            f"porterait 610 € nets de provisions sur charges (4,76 %) et "
            f"l'achat-rénovation-revente. Aucune n'atteint le seuil de 6,5 % net "
            f"d'IS, aucune ne dégage un cash-flow positif, et la cinquième est "
            f"bloquée par construction : il n'y a aucune décote d'entrée à capter "
            f"sur un bien acheté au prix de son marché."
        ),
        rationale=(
            f"Le scénario de référence : bail en cours à {eur(LOYER_CC)} € charges "
            f"comprises, dont {eur(CHARGES_MOIS)} €/mois de charges de copropriété "
            f"comprises ({eur(CHARGES_COPRO)} €/an, chauffage collectif au fioul et "
            f"eau froide), soit <strong>{eur(LOYER_HC, 2)} €/mois et "
            f"{eur(REVENUS)} €/an réellement encaissables</strong> ; vacance "
            f"{fr(VAC_BASE, 0)} %, gestion locative {fr(GESTION_BASE_PCT, 0)} %, taxe "
            f"foncière estimée {eur(TF_BASE)} € (avis non communiqué), assurance PNO "
            f"{eur(PNO)} €, provision travaux {eur(PROV_BASE)} € et comptabilité "
            f"{eur(COMPTA)} €. L'excédent brut d'exploitation ressort à "
            f"<strong>{eur(BASE['ebe'])} €</strong> ({eur(BASE['ebe_mois'])} €/mois), "
            f"soit <strong>{fr(BASE['rdt_av'])} % net avant IS</strong> sur les "
            f"{eur(ACTE_EN_MAIN)} € d'acte en main et {fr(BASE['rdt_ap'])} % après IS "
            f"sous convention prudente — la moitié du seuil de 6,5 % net d'IS du "
            f"parc.<br><br>"
            f"Ce que l'annonce ne dit pas, et qui explique tout : le bail de 610 € "
            f"est annoncé « charges comprises » et l'annonce publie elle-même "
            f"{eur(CHARGES_COPRO)} €/an de charges de copropriété, chauffage compris. "
            f"C'est donc {fr(PART_CHARGES, 1)} % du loyer qui ne parvient jamais au "
            f"propriétaire. Le rendement brut de 7,32 % mis en avant par l'agence est "
            f"calculé sur {eur(BRUT_FACIAL)} €/an de loyer facial ; le brut réel hors "
            f"charges est de {fr(REVENUS / PRIX * 100, 2)} %, et le net avant IS de "
            f"{fr(BASE['rdt_av'])} %. Les marges du dossier ne sont pas dans le prix "
            f"— qui est au marché — ni dans la négociation, mais dans deux lignes "
            f"invisibles.<br><br>"
            f"Première ligne : l'hypothèse basse. Avec 3 % de vacance, 4 % de gestion, "
            f"{eur(650)} € de taxe foncière et {eur(100)} € de provision, l'EBE monte "
            f"à <strong>{eur(BEST['ebe'])} €</strong> et le rendement à "
            f"<strong>{fr(BEST['rdt_av'])} %</strong>, plafond {eur(BEST['cap5'])} € — "
            f"toujours la moitié du seuil. Avec 10 % de vacance, "
            f"{eur(900)} € de taxe foncière et {eur(320)} € de provision, l'EBE tombe "
            f"à <strong>{eur(WORST['ebe'])} €</strong>, le rendement à "
            f"<strong>{fr(WORST['rdt_av'])} %</strong> et le cash-flow à "
            f"{eur(CF_WORST)} €/mois. Deuxième ligne : la nature du bail. Si les 610 € "
            f"étaient du loyer net de provisions sur charges, l'EBE remonterait à "
            f"{eur(INVERSE['ebe'])} € et le rendement à {fr(INVERSE['rdt_av'])} %, "
            f"avec un cash-flow encore négatif de {eur(INVERSE['cf'])} €/mois et un "
            f"plafond de {eur(INVERSE['cap5'])} € — "
            f"{fr((PRIX - INVERSE['cap5']) / PRIX * 100, 1)} % sous le prix affiché. "
            f"Entre la lecture la plus défavorable et la plus favorable, le dossier "
            f"ne franchit jamais la barre : c'est un dossier fermé par sa structure, "
            f"pas par son prix.<br><br>"
            f"Ce qu'il n'est pas, non plus : une opération de revente. La valeur de "
            f"marché de la tranche de surface est de {eur(VALEUR_RETENUE)} € "
            f"({fr(SURF)} m² × {eur(DVF_APP_4560_MED)} €/m²) contre "
            f"{eur(ACTE_EN_MAIN)} € de prix de revient : marge négative de "
            f"{eur(ACTE_EN_MAIN - VALEUR_RETENUE)} € avant frais de revente et "
            f"fiscalité, sans aucun levier de division (un seul lot habitable, une "
            f"cave, pas de place privative)."
        ),
        identite=[
            ("Adresse",
             "58 rue Jules Ferry, 83170 Brignoles — résidence avec parc arboré, "
             "quartier « Extension Années 50-70 »"),
            ("Vendeur / intermédiaire",
             "ABC IMMO BRIGNOLES — Mirlinda ZUMBEROVIC EI (RSAC Draguignan "
             "991000282) — annonce SeLoger 269U5FFWGIGA, référence annonce 1680. "
             "Honoraires à la charge du vendeur"),
            ("Composition",
             f"Appartement T2 de {fr(SURF)} m² Carrez (2 pièces, 1 chambre) au "
             f"{ETAGE} : terrasse de {eur(TERRASSE)} m², cuisine indépendante avec "
             f"loggia, séjour plein sud, salle d'eau, WC indépendant, cave "
             f"privative, deux balcons, double vitrage, portail automatique, aucun "
             f"ascenseur. Chauffage central collectif au fioul"),
            ("Statut",
             f"Copropriété de {LOTS_COPRO} lots, aucune procédure en cours selon "
             f"l'annonce. Lot {LOT_APPART} pour l'appartement et {LOT_CAVE} pour la "
             f"cave, soit {eur(TANTIEMES_LOT)}/{eur(TANTIEMES_TOTAL)}èmes (0,88 %). "
             f"« Parking libre au sein de la résidence » : <strong>aucune place "
             f"privative</strong>, donc aucun lot cessible et aucun revenu annexe"),
            ("Surfaces",
             f"<strong>{fr(SURF)} m² Carrez annoncés</strong> "
             f"({eur(PRIX / SURF)} €/m²) : 2 pièces, 1 chambre, plus terrasse de "
             f"{eur(TERRASSE)} m², deux balcons et une cave privative. Aucun plan "
             f"n'est joint, mais la surface Carrez est donnée : c'est le seul "
             f"chiffre de surface opposable du dossier"),
            ("Occupation",
             f"<strong>Vendu loué</strong> : bail nu en cours à {eur(LOYER_CC)} € "
             f"charges comprises. Ni la date, ni la durée, ni la décomposition "
             f"loyer hors charges / provisions sur charges ne sont communiquées. "
             f"Locataire en place à l'acquisition, donc pas de vacance de "
             f"démarrage — mais aucune quittance ni régularisation n'est jointe"),
            ("Charges de copropriété",
             f"<strong>{eur(CHARGES_COPRO)} €/an, soit {eur(CHARGES_MOIS)} €/mois, "
             f"chauffage collectif au fioul et eau froide compris</strong> — "
             f"{fr(PART_CHARGES, 1)} % du loyer du bail. Charges structurelles, "
             f"récurrentes et non pilotables par le propriétaire. Aucun budget "
             f"prévisionnel ni régularisation communiqués"),
            ("DPE / GES",
             f"DPE {DPE} / GES {GES} — facture énergétique estimée de "
             f"{eur(FACTURE_BASSE)} à {eur(FACTURE_HAUTE)} €/an. Chauffage collectif "
             f"au fioul : pas d'échéance réglementaire immédiate (un D reste "
             f"louable), mais la conversion de la chaufferie est une échéance "
             f"structurelle de la copropriété"),
            ("Travaux",
             "Aucun travaux annoncé, bien déclaré entretenu : 0 € de travaux à "
             f"l'acquisition et {eur(PROV_BASE)} €/an de provision en exploitation. "
             f"Le risque réel est collectif : chaudière fioul de {ANNEE}, "
             f"{LOTS_COPRO} lots, aucun DCE, aucun PPT et aucun procès-verbal "
             f"d'assemblée générale communiqués"),
            ("Prix affiché",
             f"<strong>{eur(PRIX)} €</strong>, honoraires à la charge du vendeur — "
             f"{eur(PRIX / SURF)} €/m² sur les {fr(SURF)} m² Carrez. C'est "
             f"exactement la médiane DVF 2025 de la tranche 45-60 m² de Brignoles "
             f"({eur(DVF_APP_4560_MED)} €/m² sur {DVF_APP_4560_N} ventes)"),
            ("Valeur de marché retenue",
             f"<strong>{eur(VALEUR_RETENUE)} €</strong> ({fr(SURF)} m² × "
             f"{eur(DVF_APP_4560_MED)} €/m²), fourchette {eur(VALEUR_BASSE)} à "
             f"{eur(VALEUR_HAUTE)} € (premier et troisième quartiles de la même "
             f"tranche, {DVF_APP_4560_N} ventes). Comparable nommé de la même rue "
             f"que l'agence : {eur(DVF_CMP['surf'])} m² et {DVF_CMP['lots']} lots "
             f"vendus {eur(DVF_CMP['prix'])} € le {DVF_CMP['date']}, soit "
             f"{eur(DVF_CMP['m2'])} €/m² — produit mixte, cité pour mémoire"),
            ("Loyers retenus",
             f"<strong>{eur(LOYER_HC, 2)} €/mois</strong> : loyer du bail "
             f"({eur(LOYER_CC)} € charges comprises) moins les charges de "
             f"copropriété refacturées dans ce loyer ({eur(CHARGES_MOIS)} €/mois), "
             f"soit {eur(REVENUS)} €/an. Une seule ligne de revenu en base, celle "
             f"de la stratégie retenue. Loyers relevés sur place le 25/09/2026 : "
             f"1 pièce de 36 m² à 450 €, 2 pièces de 37 m² à 680 €, 3 pièces meublé "
             f"de 50 m² à 800 €, parking à 120 € ; loyer de référence communal "
             f"11,0 €/m²/mois sur 60 m²"),
            ("Charges d'exploitation retenues",
             f"Taxe foncière <strong>estimée {eur(TF_BASE)} €</strong> (avis non "
             f"communiqué, fourchette 700 à 900 €) + assurance PNO {eur(PNO)} € + "
             f"gestion locative {fr(GESTION_BASE_PCT, 0)} % et provision travaux "
             f"{eur(PROV_BASE)} € (poste composite de "
             f"{eur(REVENUS * GESTION_BASE_PCT / 100.0 + PROV_BASE)} €) + "
             f"comptabilité {eur(COMPTA)} €. Les {eur(CHARGES_COPRO)} €/an de "
             f"charges de copropriété ne figurent PAS dans ces lignes : ils sont "
             f"déjà déduits du loyer saisi, un loyer de "
             f"{eur(LOYER_CC)} € charges comprises ne valant que "
             f"{eur(LOYER_HC, 2)} € encaissables. Provision automatique du moteur "
             f"(2,5 %) désactivée pour ne pas compter deux fois la provision travaux"),
            ("Fiscalité",
             f"SCI à l'IS. Année 1 réelle : EBE {eur(BASE['ebe'])} € moins intérêts "
             f"d'emprunt {eur(INTERETS_AN1)} € ({eur(CAPITAL)} € à 3,7 %) moins la "
             f"dotation aux amortissements {eur(DOTATION_AN1)} € (bâti à 80 % du "
             f"prix sur 30 ans) = <strong>résultat imposable négatif de "
             f"{eur(abs(BASE['ebe'] - INTERETS_AN1 - DOTATION_AN1))} €, donc aucun IS "
             f"dû en année 1</strong> (déficit reporté). Convention prudente retenue "
             f"pour les rendements publiés : IS de 15 % appliqué à l'EBE, soit "
             f"<strong>{eur(CONVENTION_IS * BASE['ebe'])} €/an</strong>, sans "
             f"amortissement du bâti modélisé — c'est la lecture que publie le "
             f"listing du dépôt"),
            ("Prix de revient",
             f"<strong>{eur(ACTE_EN_MAIN)} €</strong> acte en main = prix "
             f"{eur(PRIX)} € + frais d'acquisition {eur(FRAIS_ACQUISITION)} € "
             f"({fr(TAUX_FRAIS * 100, 2)} %, retenus par le simulateur de l'annonce "
             f"elle-même), sans travaux. Ratio coût/valeur de "
             f"{fr(ACTE_EN_MAIN / VALEUR_RETENUE)} : le bien est acheté au prix de "
             f"son marché, pas en dessous"),
            ("Financement (doctrine du parc)",
             f"apport 10 %, prêt de {eur(CAPITAL)} € sur {DUREE_ANS} ans à 3,7 % et "
             f"assurance emprunteur de 0,34 %, soit une mensualité de "
             f"<strong>{eur(MENS_BASE)} €/mois</strong> (0,00753 € par euro "
             f"emprunté). Cash-flow de <strong>{eur(CF_BASE)} €/mois</strong> "
             f"({eur(CF_BASE_AN)} €/an) au prix affiché, {eur(CF_BEST)} €/mois en "
             f"hypothèse favorable, {eur(CF_WORST)} €/mois en hypothèse défavorable "
             f"et {eur(CF_INVERSE)} €/mois dans la lecture inverse. Prix d'équilibre "
             f"à 10 % d'apport : {eur(prix_cashflow_nul(BASE['ebe']))} €, soit "
             f"{fr((PRIX - prix_cashflow_nul(BASE['ebe'])) / PRIX * 100, 0)} % sous "
             f"le prix affiché"),
        ],
        stance=(
            f"<strong>On fuit. Pas à cause du prix — qui est celui du marché — mais "
            f"parce que {eur(CHARGES_COPRO)} €/an de charges de copropriété, "
            f"chauffage collectif au fioul et eau froide compris, absorbent "
            f"{fr(PART_CHARGES, 1)} % du loyer et ne laissent que "
            f"{eur(LOYER_HC, 2)} €/mois encaissables sur un loyer facial de "
            f"{eur(LOYER_CC)} €.</strong><br><br>"
            f"Le raisonnement tient en deux grilles, et le dossier échoue aux deux. "
            f"Sur la grille de rendement, il manque la moitié du chemin : "
            f"{fr(BASE['rdt_av'])} % net avant IS au prix affiché ({fr(BASE['rdt_ap'])} % "
            f"après IS sous convention prudente) contre un seuil de 6,5 % net d'IS ; "
            f"même l'hypothèse la plus favorable, vacance 3 % et gestion 4 %, ne "
            f"donne que {fr(BEST['rdt_av'])} %, et la lecture inverse où le bail "
            f"porterait 610 € nets de provisions sur charges plafonne à "
            f"{fr(INVERSE['rdt_av'])} %. Sur la grille de trésorerie, il échoue "
            f"franchement : {eur(CF_BASE)} €/mois de cash-flow négatif, "
            f"{eur(abs(CF_BASE_AN))} €/an, {eur(abs(CF_BASE_AN * DUREE_ANS))} € sur "
            f"quinze ans, et aucun scénario n'est positif.<br><br>"
            f"<strong>Ce que cela implique pour une offre.</strong> Pour atteindre "
            f"5 % net avant IS il faudrait payer <strong>{eur(BASE['cap5'])} €</strong>, "
            f"soit {fr((PRIX - BASE['cap5']) / PRIX * 100, 0)} % sous le prix affiché ; "
            f"pour un cash-flow nul avec 10 % d'apport, <strong>"
            f"{eur(prix_cashflow_nul(BASE['ebe']))} €</strong>, soit "
            f"{fr((PRIX - prix_cashflow_nul(BASE['ebe'])) / PRIX * 100, 0)} % sous le "
            f"prix affiché, ou bien un apport de "
            f"{eur(apport_cashflow_nul(PRIX, BASE['ebe']))} € "
            f"({fr(apport_cashflow_nul(PRIX, BASE['ebe']) / PRIX * 100, 0)} % du "
            f"prix). Aucune négociation ne va chercher cela sur un bien qui est au "
            f"prix de son marché : le vendeur a raison sur le prix, et il a tort sur "
            f"le rendement. Un dossier ne se négocie pas parce qu'il est cher ; "
            f"celui-ci n'est pas cher, il est inexploitable.<br><br>"
            f"<strong>Ce qu'on retient, en revanche, et qui vaut pour la suite du "
            f"sourcing.</strong> C'est le premier dossier de Brignoles du dépôt où "
            f"le prix payé est le prix du marché, sur un lot de copropriété — les "
            f"trois autres portaient sur des immeubles entiers de centre ancien à "
            f"des prix très en dessous de leur valeur d'usage, avec des inconnues de "
            f"travaux et de loyers. Celui-ci montre que le prix n'est pas le seul "
            f"critère d'un lot de copropriété : ce qui décide, c'est le rapport "
            f"entre le loyer encaissable et le budget de la copropriété. À "
            f"{eur(CHARGES_COPRO)} €/an de charges pour {eur(BRUT_FACIAL)} €/an de "
            f"loyer facial, le rendement est décidé au vote du budget — pas à la "
            f"signature de l'acte. <strong>Un dossier de ce type ne se visite même "
            f"pas : le premier chiffre à demander à une agence sur un lot de "
            f"copropriété, c'est la charge annuelle du lot.</strong>"
        ),
        prix_plafond=(
            f"<strong>Trois ancres, et aucune ne rend le dossier achetable.</strong> "
            f"Sur le critère de rendement, le prix qui tient 5 % net avant IS est de "
            f"<strong>{eur(BASE['cap5'])} €</strong> avec {eur(LOYER_HC, 2)} €/mois "
            f"encaissables, et de {eur(BEST['cap5'])} € en hypothèse favorable "
            f"({eur(BEST['rdt_av'])} %) : {fr((PRIX - BASE['cap5']) / PRIX * 100, 0)} % "
            f"sous le prix affiché. Sur le critère de trésorerie, la contrainte est "
            f"plus brutale encore : à 10 % d'apport, le prix qui donne un cash-flow "
            f"nul est de <strong>{eur(prix_cashflow_nul(BASE['ebe']))} €</strong> "
            f"({fr((PRIX - prix_cashflow_nul(BASE['ebe'])) / PRIX * 100, 0)} % sous le "
            f"prix affiché), et l'équilibre demanderait sinon un apport de "
            f"{eur(apport_cashflow_nul(PRIX, BASE['ebe']))} €, soit "
            f"{fr(apport_cashflow_nul(PRIX, BASE['ebe']) / PRIX * 100, 0)} % du prix. "
            f"Sur le critère de valeur de marché, enfin, la valeur retenue de "
            f"{eur(VALEUR_RETENUE)} € ({fr(SURF)} m² × "
            f"{eur(DVF_APP_4560_MED)} €/m², médiane DVF 2025 des {DVF_APP_4560_N} "
            f"ventes de 45 à 60 m²) donne un ratio coût/valeur de "
            f"<strong>{fr(ACTE_EN_MAIN / VALEUR_RETENUE)}</strong> : le prix affiché "
            f"achète le bien à sa valeur, sans décote.<br><br>"
            f"<strong>Ce qu'on retient comme cadre, si un contact devait être "
            f"poursuivi malgré le verdict.</strong> Un plafond unique : "
            f"<strong>{eur(BASE['cap5'])} € acte en main compris, soit "
            f"{eur(BASE['cap5'] / (1 + TAUX_FRAIS))} € net vendeur</strong>, pour "
            f"5 % net avant IS — c'est-à-dire {fr((PRIX - BASE['cap5']) / PRIX * 100, 0)} % "
            f"sous le prix affiché, très au-delà de tout ce qu'un particulier vendant "
            f"au prix du marché acceptera. Un second plafond, sur la valeur : "
            f"{eur(VALEUR_RETENUE * 0.95 / (1 + TAUX_FRAIS))} € net vendeur pour un "
            f"ratio coût/valeur de 0,95, soit {fr((PRIX - VALEUR_RETENUE * 0.95 / (1 + TAUX_FRAIS)) / PRIX * 100, 0)} % "
            f"sous le prix affiché. Ces deux plafonds se rejoignent dans la même "
            f"zone : 40 % sous le prix. <strong>Autrement dit : ce dossier n'a de "
            f"sens qu'à un prix de décote lourde, c'est-à-dire jamais dans cette "
            f"copropriété.</strong> Les prix plafonds sont publiés avec leur "
            f"hypothèse complète (scénario de base, vacance {fr(VAC_BASE, 0)} %, "
            f"charges détaillées ci-dessus) : sans cette précision, un plafond n'est "
            f"pas défendable face à un vendeur"
        ),
        leviers=[
            "Le levier qui décide est la charge de copropriété, et il faut la "
            f"documenter avant toute discussion : demander le budget prévisionnel, "
            f"la répartition des {eur(CHARGES_COPRO)} €/an entre chauffage, eau "
            f"froide, ascenseur (il n'y en a pas), parties communes et "
            f"administrateur, ainsi que la dernière régularisation de charges. Un "
            f"poste de 30 % du loyer n'est acceptable qu'accompagné de son détail",
            "Deuxième pièce : le bail écrit. La décomposition entre loyer hors "
            f"charges et provisions sur charges vaut {eur(INVERSE['ebe'] - BASE['ebe'])} €/an "
            f"de résultat et {fr(INVERSE['rdt_av'] - BASE['rdt_av'])} point de "
            f"rendement net — elle ne sauve pas l'opération, elle élimine "
            f"l'ambiguïté. Exiger aussi la date d'effet, la durée restante, l'état "
            f"des lieux et les quittances",
            "Troisième pièce : les trois derniers procès-verbaux d'assemblée "
            f"générale. Une chaudière collective au fioul dans une copropriété de "
            f"{LOTS_COPRO} lots de {ANNEE} est une échéance de travaux, pas une "
            f"hypothèse : les PV diront ce qui a été voté, ce qui est provisionné, "
            f"et si une mise aux normes de chaufferie est au programme. Demander "
            f"aussi le DTG s'il existe et le DCE de la chaufferie",
            "Le prix au m² n'est PAS un levier ici, et il faut le dire pour rester "
            f"crédible : à {eur(PRIX / SURF)} €/m² le bien est exactement à la "
            f"médiane DVF 2025 de sa tranche ({eur(DVF_APP_4560_MED)} €/m² sur "
            f"{DVF_APP_4560_N} ventes). Attaquer le prix de front se ferait démolir "
            f"par n'importe quel agent avec deux transactions comparables. Le levier "
            f"est le rendement, pas le prix",
            "Ce qui est attaquable, en revanche, c'est l'affirmation de l'annonce : "
            f"« rentabilité brute d'environ 7 % » pour un bail à "
            f"{eur(LOYER_CC)} € charges comprises avec {eur(CHARGES_COPRO)} €/an de "
            f"charges de copropriété publiées dans la même annonce. Le brut réel hors "
            f"charges est de {fr(REVENUS / PRIX * 100, 2)} % et le net avant IS de "
            f"{fr(BASE['rdt_av'])} %. Poser ce calcul par écrit devant l'agence est "
            f"la façon la plus rapide d'établir qu'on a lu le dossier — et de faire "
            f"tomber l'argument de vente",
            "« Parking libre au sein de la résidence » : faire préciser par écrit si "
            f"une place est affectée au lot par le règlement de copropriété et si "
            f"elle figure dans l'état daté. Sans place privative, il n'y a aucun "
            f"revenu annexe (120 €/mois de parking relevés à Brignoles) et aucun "
            f"lot cessible à la revente — mais une place cédée par le règlement "
            f"changerait la fiche d'identité",
            "L'absence d'ascenseur n'est pas un argument sur ce lot, situé au "
            f"rez-de-chaussée : la porter comme un défaut affaiblirait la position. "
            f"En revanche, un projet d'installation d'ascenseur (il en faut un pour "
            f"4 étages) se voterait et se paierait par appels de fonds : demander "
            f"aux PV de dire où en est la question",
            "Enfin, ne pas s'engager sans l'avis de taxe foncière, l'état daté et "
            f"le règlement de copropriété : ces pièces gratuites donnent la valeur "
            f"locative cadastrale, la quote-part réelle de charges et les "
            f"obligations du lot — les trois données qui manquent pour chiffrer "
            f"définitivement un poste qui pèse 30 % du loyer",
        ],
        meta=[
            f"<strong>Régime fiscal retenu :</strong> SCI à l'IS. Année 1 : EBE "
            f"{eur(BASE['ebe'])} € moins intérêts {eur(INTERETS_AN1)} € "
            f"({eur(CAPITAL)} € à 3,7 %) et dotation aux amortissements "
            f"{eur(DOTATION_AN1)} € (bâti à 80 % du prix sur 30 ans) = résultat "
            f"imposable de {eur(BASE['ebe'] - INTERETS_AN1 - DOTATION_AN1)} €, "
            f"négatif, donc aucun IS dû en année 1. Convention prudente retenue pour "
            f"les rendements publiés : IS de 15 % appliqué à l'EBE, sans "
            f"amortissement du bâti modélisé, soit {eur(CONVENTION_IS * BASE['ebe'])} €/an. "
            f"Seuil de décision du parc (6,5 % net d'IS) : {fr(BASE['rdt_av'])} % net "
            f"avant IS en base, {fr(BASE['rdt_ap'])} % après IS sous convention "
            f"prudente",
            f"<strong>Convention de lecture des charges de copropriété :</strong> le "
            f"bail porte {eur(LOYER_CC)} € charges comprises ; les "
            f"{eur(CHARGES_COPRO)} €/an de charges du lot (chauffage collectif au "
            f"fioul et eau froide compris) sont donc déduits du loyer, qui ressort à "
            f"{eur(LOYER_HC, 2)} €/mois encaissables. Ces 2 193 €/an ne sont pas "
            f"saisis une seconde fois dans les charges d'exploitation : le faire "
            f"compterait deux fois la même charge. Le fait est consigné en entrée "
            f"dans bien.copro.charges_annuelles_euros et publié en clair, avec la "
            f"variante où le bail porterait 610 € nets de provisions sur charges",
            f"<strong>Frais d'acquisition :</strong> {eur(FRAIS_ACQUISITION)} € "
            f"({fr(TAUX_FRAIS * 100, 2)} %), retenus par le simulateur de l'annonce "
            f"elle-même ; honoraires à la charge du vendeur. Prix de revient acte en "
            f"main : {eur(ACTE_EN_MAIN)} €, sans travaux (aucun travaux annoncé, bien "
            f"déclaré entretenu)",
            f"<strong>Loyers :</strong> une seule ligne de revenu, celle de la "
            f"stratégie retenue — {eur(LOYER_HC, 2)} €/mois "
            f"({eur(REVENUS)} €/an) — parce que c'est ce que le propriétaire encaisse "
            f"réellement sur un bail de {eur(LOYER_CC)} € charges comprises. "
            f"Hypothèses publiées : {fr(BASE['rdt_av'])} % net avant IS en base, "
            f"{fr(BEST['rdt_av'])} % en hypothèse favorable, {fr(WORST['rdt_av'])} % "
            f"en hypothèse défavorable, {fr(INVERSE['rdt_av'])} % dans la lecture "
            f"inverse",
            f"<strong>Charges d'exploitation :</strong> taxe foncière estimée "
            f"{eur(TF_BASE)} €/an (avis non communiqué), assurance PNO {eur(PNO)} €, "
            f"gestion locative {fr(GESTION_BASE_PCT, 0)} % des loyers et provision "
            f"travaux {eur(PROV_BASE)} € (poste composite de "
            f"{eur(REVENUS * GESTION_BASE_PCT / 100.0 + PROV_BASE)} €), comptabilité "
            f"{eur(COMPTA)} €. Provision automatique de 2,5 % du moteur désactivée "
            f"pour ne pas compter deux fois la provision travaux. Aucun poste laissé "
            f"à zéro",
            f"<strong>Financement (doctrine du parc) :</strong> apport 10 %, prêt de "
            f"{eur(CAPITAL)} € sur {DUREE_ANS} ans à 3,7 % et assurance emprunteur de "
            f"0,34 %, soit une mensualité de {eur(MENS_BASE)} €/mois (0,00753 € par "
            f"euro emprunté). Cash-flow de <strong>{eur(CF_BASE)} €/mois</strong> "
            f"({eur(CF_BASE_AN)} €/an). Ne pas lire cette fiche comme un dossier "
            f"finançable : il n'existe aucune hypothèse, y compris la plus favorable "
            f"au vendeur, qui produise un cash-flow positif",
            f"<strong>Valeur de marché :</strong> {eur(VALEUR_RETENUE)} € "
            f"({fr(SURF)} m² × {eur(DVF_APP_4560_MED)} €/m²), fourchette "
            f"{eur(VALEUR_BASSE)} à {eur(VALEUR_HAUTE)} €. Ancrage : médiane DVF "
            f"2025 des {DVF_APP_4560_N} ventes d'appartements de 45 à 60 m² de la "
            f"commune — la seule tranche comparable en surface. La médiane communale "
            f"toutes surfaces ({eur(DVF_APP_MED)} €/m², {DVF_APP_N} ventes) n'est pas "
            f"utilisée : elle mélange des surfaces non comparables, et la tranche "
            f"30-45 m² se traite à {eur(DVF_APP_3045_MED)} €/m² quand la tranche "
            f"60-90 m² tombe à {eur(DVF_APP_6090_MED)} €/m²",
            f"<strong>Pièces à demander avant toute décision :</strong> le bail en "
            f"cours et sa décomposition loyer hors charges / provisions sur charges ; "
            f"la dernière régularisation de charges ; l'avis de taxe foncière ; les "
            f"trois derniers procès-verbaux d'assemblée générale ; le plan "
            f"pluriannuel de travaux (PPT) et le dossier de chaufferie (DCE "
            f"collectif, chauffage au fioul de {ANNEE}) ; le règlement de "
            f"copropriété ; l'état daté ; le diagnostic technique global (DTG) s'il "
            f"existe ; et le budget prévisionnel de la copropriété avec la "
            f"répartition de la charge du lot",
            f"<strong>Point de méthode :</strong> ce dossier est le premier de la "
            f"commune où le prix payé est le prix du marché sur un lot de "
            f"copropriété — les trois autres dossiers Brignoles du dépôt portaient "
            f"sur des immeubles entiers de centre ancien, à des prix très en dessous "
            f"de leur valeur d'usage, avec des inconnues de travaux et de loyers. Le "
            f"contre-exemple est utile : <strong>sur un lot de copropriété, le prix "
            f"n'est pas le premier critère — le rapport entre le loyer encaissable "
            f"et la charge annuelle du lot l'est</strong>. Ici, "
            f"{eur(CHARGES_COPRO)} €/an pour {eur(BRUT_FACIAL)} €/an de loyer facial. "
            f"Règle de tri à retenir pour le sourcing : demander la charge annuelle "
            f"du lot avant la visite",
        ],
    )}
    c = gen.CONF[SLUG]
    html = gen.TEMPLATE.format(
        titre_court=c['titre_court'], adresse=c['adresse'], date_fr=c['date_fr'],
        source=c['source'], url=c['url'], badge=c['badge'], strategie=c['strategie'],
        fiscal_note=c['fiscal_note'],
        prix=eur(PRIX),
        surface=f"{fr(SURF)} m² (2 pièces, 1 chambre)",
        prix_m2=f"{eur(PRIX / SURF)} €/m²",
        revient=eur(ACTE_EN_MAIN),
        valeur=eur(VALEUR_RETENUE),
        revenus=eur(LOYER_HC, 2),
        rdt_revient=fr(BASE['rdt_av']), rdt_valeur=fr(BASE['rdt_ap']),
        note=fr(note, 1), note_cls=fr(note, 1).replace(',', '-'),
        lat=c['lat'], lon=c['lon'], quartier=c['quartier'],
        intro_attr=c['intro_attr'], profil=c['profil'], concl_attr=c['concl_attr'],
        attrs=gen.attr_html(rec_), intro_strat=c['intro_strat'],
        strats=gen.strategy_html(rec_),
        rationale=c['rationale'], identite=gen.identite_html(c['identite']),
        projections=f"""  <section class="financial-projections">
    <h2>Compte d'exploitation locatif — {eur(PRIX)} € affichés, {eur(ACTE_EN_MAIN)} € acte en main, SCI à l'IS</h2>
    <p class="attractiveness-intro">{lecture}</p>
    <div class="projections-grid">
{chr(10).join(cartes)}
    </div>
    <table class="projection-table compare">
      <thead><tr><th>Indicateur</th><th class="num">Base — bail en cours</th><th class="num">Optimiste</th><th class="num">Pessimiste</th></tr></thead>
      <tbody>
        <tr><td>Loyer facial du bail ({eur(LOYER_CC)} € CC)</td><td class="num">{eur(BASE['brut_facial'])} €</td><td class="num">{eur(BEST['brut_facial'])} €</td><td class="num">{eur(WORST['brut_facial'])} €</td></tr>
        <tr><td>Loyers encaissables après charges de copropriété</td><td class="num">{eur(BASE['brut'])} €</td><td class="num">{eur(BEST['brut'])} €</td><td class="num">{eur(WORST['brut'])} €</td></tr>
        <tr><td>Excédent brut d'exploitation</td><td class="num">{eur(BASE['ebe'])} €</td><td class="num">{eur(BEST['ebe'])} €</td><td class="num">{eur(WORST['ebe'])} €</td></tr>
        <tr><td>EBE mensuel</td><td class="num">{eur(BASE['ebe_mois'])} €/mois</td><td class="num">{eur(BEST['ebe_mois'])} €/mois</td><td class="num">{eur(WORST['ebe_mois'])} €/mois</td></tr>
        <tr><td>Net après IS (convention prudente)</td><td class="num">{eur(BASE['net'])} €</td><td class="num">{eur(BEST['net'])} €</td><td class="num">{eur(WORST['net'])} €</td></tr>
        <tr><td>Rendement brut réel hors charges</td><td class="num">{fr(BASE['rdt_brut_reel'])} %</td><td class="num">{fr(BEST['rdt_brut_reel'])} %</td><td class="num">{fr(WORST['rdt_brut_reel'])} %</td></tr>
        <tr><td>Rendement net avant IS (acte en main)</td><td class="num">{fr(BASE['rdt_av'])} %</td><td class="num">{fr(BEST['rdt_av'])} %</td><td class="num">{fr(WORST['rdt_av'])} %</td></tr>
        <tr><td>Rendement net après IS (acte en main)</td><td class="num">{fr(BASE['rdt_ap'])} %</td><td class="num">{fr(BEST['rdt_ap'])} %</td><td class="num">{fr(WORST['rdt_ap'])} %</td></tr>
        <tr><td>Rendement net après IS sur la valeur ({eur(VALEUR_RETENUE)} €)</td><td class="num">{fr(BASE['rdt_valeur'])} %</td><td class="num">{fr(BEST['rdt_valeur'])} %</td><td class="num">{fr(WORST['rdt_valeur'])} %</td></tr>
        <tr><td>Prix d'achat tenant 5 % net avant IS</td><td class="num">{eur(BASE['cap5'])} €</td><td class="num">{eur(BEST['cap5'])} €</td><td class="num">{eur(WORST['cap5'])} €</td></tr>
        <tr><td>Écart au prix affiché ({eur(PRIX)} €)</td><td class="num">{eur(BASE['cap5'] - PRIX)} €</td><td class="num">{eur(BEST['cap5'] - PRIX)} €</td><td class="num">{eur(WORST['cap5'] - PRIX)} €</td></tr>
        <tr class="highlight"><td>Cash-flow mensuel après crédit (apport 10 %)</td><td class="num">{eur(CF_BASE)} €/mois</td><td class="num">{eur(CF_BEST)} €/mois</td><td class="num">{eur(CF_WORST)} €/mois</td></tr>
      </tbody>
    </table>
    <p class="attractiveness-intro">Repères de méthode : acte en main {eur(ACTE_EN_MAIN)} € = prix affiché {eur(PRIX)} € + frais d'acquisition {eur(FRAIS_ACQUISITION)} € ({fr(TAUX_FRAIS * 100, 2)} %, honoraires à la charge du vendeur) ; aucun travaux à l'acquisition, provision travaux annuelle comprise dans le poste composite d'entretien ; vacance {fr(VAC_BASE, 0)} % en base, {fr(VAC_BEST, 0)} % en hypothèse favorable, {fr(VAC_WORST, 0)} % en hypothèse défavorable ; gestion locative {fr(GESTION_BASE_PCT, 0)} %, 4 % et {fr(GESTION_BASE_PCT, 0)} % ; taxe foncière estimée {eur(TF_BASE)} €, puis {eur(650)} € et {eur(900)} € ; assurance PNO {eur(PNO)} € ; comptabilité {eur(COMPTA)} € ; SCI à l'IS avec IS de 15 % appliqué à l'EBE, sans amortissement du bâti modélisé (convention prudente — la dotation réelle de l'année 1, {eur(DOTATION_AN1)} €, et les intérêts de {eur(INTERETS_AN1)} € laissent un résultat imposable négatif, donc aucun IS dû) ; valeur de marché {eur(VALEUR_RETENUE)} € ({eur(DVF_APP_4560_MED)} €/m² sur les {fr(SURF)} m², médiane DVF 2025 de la tranche 45-60 m²). <strong>Convention de lecture :</strong> les rendements « avant IS » rapportent l'EBE à l'acte en main de {eur(ACTE_EN_MAIN)} € ; les rendements « après IS » retiennent la convention prudente du moteur (IS de 15 % de l'EBE) et donnent {fr(BASE['rdt_ap'])} % sur l'acte en main et {fr(BASE['rdt_valeur'])} % sur la valeur de marché, tandis que le listing du dépôt affiche le net après IS sur le revient et sur le prix d'achat ({fr(BASE['rdt_ap'], 1)} % / {fr(rd['net_sur_achat_pct'], 1)} %). Les quatre chiffres décrivent la même exploitation sous quatre dénominateurs différents.</p>
  </section>
{charges_section}
{cf_section}
{inverse_section}
{marche_section}""",
        risques=gen.risques_html(rec_),
        verdict_cls={"acheter": "buy", "negocier": "nego", "fuir": "pass"}.get(verdict, "nego"),
        stance=c['stance'], prix_plafond=c['prix_plafond'],
        leviers=gen.leviers_html(c['leviers']),
        meta="\n".join(f"      <p>{m}</p>" for m in c['meta']),
    )

    # Libelles de cartes devenus faux au rendu (la fiche est ecrite par l'agent)
    for vieux, neuf in (
        ('<span class="card-label">Surface</span>',
         '<span class="card-label">Surface Carrez</span>'),
        ('<span class="card-label">Prix / m²</span>',
         '<span class="card-label">Prix / m² (prix du marché)</span>'),
        ('<span class="card-label">Prix de revient</span>',
         '<span class="card-label">Prix de revient (acte en main)</span>'),
        ('<span class="card-label">Valeur marché retenue</span>',
         '<span class="card-label">Valeur marché (DVF 2025, 45-60 m²)</span>'),
        ('<span class="card-label">Revenus bruts</span>',
         '<span class="card-label">Loyer encaissable (hors charges de copro)</span>'),
        ('<span class="card-label">Rentabilité nette</span>',
         '<span class="card-label">Rendement net avant IS / après IS</span>'),
    ):
        assert vieux in html, vieux
        html = html.replace(vieux, neuf)

    # Controles sur le HTML produit
    assert 'section class="verdict pass"' in html, "classe de verdict inattendue"
    assert 'note-' + fr(note, 1).replace(',', '-') in html
    assert 'verdict buy' not in html and 'verdict nego' not in html
    for vieux in ('2 193 €', '183', '30,0 %', '427,25', '2,93', '3,9/10',
                  '58 598', '38 908', 'On fuit'):
        assert vieux in html, f"chiffre attendu absent du HTML : {vieux}"

    d = os.path.join(ROOT, 'analyses', SLUG)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  fiche ecrite : {len(html):,} octets dans analyses/{SLUG}/index.html")

    p = os.path.join(ROOT, 'analyses', 'analyses.json')
    data = json.load(open(p, encoding='utf-8'))
    rec_['analyse']['champs_manquants'] = schema.champs_manquants(rec_)
    lst = [x for x in data["analyses"] if x.get("slug") != SLUG]
    lst.append(rec_)
    data["analyses"] = lst
    if isinstance(data.get("meta"), dict):
        data["meta"]["count"] = len(lst)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"  analyses.json : {len(lst)} fiches (meta.count={data['meta']['count']})")

    # Controles des chiffres publies
    print("\n  Controles des chiffres publies (publie vs recalcule) :")
    for lab, pub, rec2, tol in CONTROLES:
        print(f"    {lab:<58} publie {pub:>14,.2f} | recalcule {rec2:>14,.2f} | "
              f"ecart {abs(pub - rec2):.2f} (tol {tol})")
    if ECARTS:
        print("\n  Chiffres du brief qui ne se recalculent PAS (non publies) :")
        for lab, brief, rec2, note_txt in ECARTS:
            print(f"    {lab:<58} brief {brief} | recalcule {rec2} — {note_txt}")


if __name__ == '__main__':
    main()
