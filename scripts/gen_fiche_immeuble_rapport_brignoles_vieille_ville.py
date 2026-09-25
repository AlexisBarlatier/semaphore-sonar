#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche Immeuble de rapport en centre vieille ville, Brignoles (83170).

154 400 EUR, SAFTI (Maude MERRY, conseiller indépendant, EI, RCS Draguignan
522063833), annonce SeLoger 26UC8HRN61QJ, réf. agence 1699409.
Immeuble 1940 : RDC un local commercial de 20 m2 (avec salle d'eau et WC) et
une cave de 17 m2, 1er un studio de 20 m2, 2e un duplex T2 de 47 m2.
Branche residentielle (SCI a l'IS). Tout se joue sur le local commercial du
rez-de-chaussee et sur les loyers, qui ne sont pas dans l'annonce.

Chaque chiffre publie est reaffirme par `calcule()` a tolerance depuis les
lignes du modele (loyers, charges, credit, fiscalite, plafonds, apports).
Les donnees DVF 2025 sont recalculees depuis le fichier DVF du departement
quand il est present (/tmp/dvf83_2025.csv.gz), sinon les constantes sont
controlees entre elles et la sortie le signale.
"""
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

SLUG = "2026-09-25-immeuble-rapport-brignoles-vieille-ville"
URL = ("https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/"
       "brignoles-83170/26UC8HRN61QJ")
DATE = "2026-09-25"
DATE_FR = "25 septembre 2026"

# --- Le bien -----------------------------------------------------------------
PRIX = 154400.0
NOTAIRE = 0.08
ACTE_EN_MAIN = PRIX * (1 + NOTAIRE)          # 166 752
SURF_ANNONCEE = 90.0
SURF_HAB = 67.0        # deux logements (20 studio + 47 duplex) + local 20 m2
SURF_LOTS_BATIS = 87.0  # 20 + 20 + 47, hors cave de 17 m2
CAVE = 17.0
LOCAL = 20.0
STUDIO = 20.0
DUPLEX = 47.0
SEUIL = 0.05                                 # doctrine du parc : 5 % net avant IS
COEF_PLAFOND = SEUIL * (1 + NOTAIRE)         # EBE = 5 % du revient = 5,4 % du prix

# --- Marche local (fiche de reference analyses/marches-locaux, 21/09/2026) ----
MARCHE_M2_COMMUNE = 2325                     # fiche de reference du 21/09/2026
LOYER_REF_M2 = 11.0                          # lot type 60 m2
PLAF_PATRIMONIAL = (1021, 943, 818)          # 6,5 % / 7,0 % / 8,0 % net d'IS
PLAF_MDB = (558, 516, 489)                   # marge nette marchand de biens

# --- DVF 2025 reelle, Brignoles (commune 83023) ------------------------------
# Methode : mutations de nature « Vente » uniquement, valeur fonciere de la
# mutation divisee par la SOMME des surfaces baties de la mutation, surfaces
# > 5 m2 et valeurs > 5 000 EUR.
DVF_VENTES = 397
DVF_APP_N = 168
DVF_APP_MED = 2246
DVF_APP_Q1 = 1703
DVF_APP_Q3 = 2900
DVF_APP_PETIT_N = 8      # moins de 30 m2
DVF_APP_PETIT_MED = 2260
DVF_APP_3060_N = 79
DVF_APP_3060_MED = 2500
DVF_APP_60P_N = 81
DVF_APP_60P_MED = 2062
DVF_MAI_N = 142
DVF_MAI_MED = 2841
DVF_IMB_N = 41           # mutations comportant au moins deux logements
DVF_IMB_MED = 1410
DVF_IMB_MIN = 326
DVF_IMB_MAX = 2131
DVF_MIXTE_N = 10         # mutations avec au moins un logement ET un local
DVF_MIXTE_MIN = 789
DVF_MIXTE_MAX = 3593
# les deux transactions comparables de centre-ville, citees nommement
DVF_CMP1 = dict(date="30/01/2025", surf=127.0, prix=170000.0, m2=1339,
                voie="rue d'Entraigues", lots=4)
DVF_CMP2 = dict(date="01/04/2025", surf=79.0, prix=139600.0, m2=1767,
                voie="rue Jules Ferry", lots=3)
DVF_FICHIER = '/tmp/dvf83_2025.csv.gz'
DVF_COMMUNE = '83023'

# --- Valeur de marche retenue (ancre DVF immeuble de rapport) -----------------
VALEUR_BASSE = 116500.0      # 87 m2 x 1 339 EUR/m2 (rue d'Entraigues)
VALEUR_RETENUE = 122700.0    # 87 m2 x 1 410 EUR/m2 (mediane DVF des immeubles)
VALEUR_HAUTE = 153700.0      # 87 m2 x 1 767 EUR/m2 (rue Jules Ferry)

# --- Credit (doctrine du parc) : chiffres du modele valide en amont ----------
APPORT_PCT = 0.10
TAUX_CREDIT = 0.037
ASSURANCE_PCT = 0.0034
DUREE_ANS = 15
CAPITAL = PRIX * (1 - APPORT_PCT)            # 138 960
MENS_PAR_EURO_MODELE = 0.00753               # chiffre du brief, reaffirme plus bas
CHARGES_FIXES_BASE = 2150.0   # TF 900 + charges 400 + PNO 150 + provision 200 + compta 500
GESTION_BASE = 738.0          # 5 % des 14 760 EUR de loyers bruts
QUOTE_PART_BATI_MODELE = 0.80  # annee 1 : bati a 80 % du prix sur 30 ans
CONTROLES = []                 # (libelle, chiffre publie, chiffre recalcule, tolerance)


def calcule(libelle, publie, recalcule, tol=1.0):
    """Reaffirme un chiffre publie : il doit sortir du modele a tolerance."""
    CONTROLES.append((libelle, publie, recalcule, tol))
    assert abs(publie - recalcule) <= tol, (libelle, publie, recalcule)


def mensualite(capital):
    return capital * mensualite_par_euro()


def mensualite_actuarielle(capital, ans=DUREE_ANS, assurance=True):
    i = TAUX_CREDIT / 12.0
    n = ans * 12
    m = capital * i / (1 - (1 + i) ** -n)
    if assurance:
        m += capital * ASSURANCE_PCT / 12.0
    return m


def mensualite_par_euro():
    return mensualite_actuarielle(CAPITAL) / CAPITAL


def cashflow_mensuel(ebe, capital):
    return ebe / 12.0 - mensualite(capital)


def prix_cashflow_nul(ebe):
    """Prix paye tel que 10 % d'apport donnent un cash-flow nul."""
    return (ebe / 12.0) / ((1 - APPORT_PCT) * mensualite_par_euro())


def apport_cashflow_nul(prix, ebe):
    return prix - (ebe / 12.0) / mensualite_par_euro()


def loyer_cashflow_nul(capital, charges_fixes=CHARGES_FIXES_BASE,
                       gestion_pct=5.0, vacance_pct=8.0):
    """Loyers mensuels tels que l'EBE couvre l'annuite (charges du scenario de base)."""
    # EBE = 12 * L * (1 - vac) - gestion_pct * 12 * L - charges fixes
    coef = 12.0 * (1 - vacance_pct / 100.0) - gestion_pct / 100.0 * 12.0
    return (12.0 * mensualite(capital) + charges_fixes) / coef


def eur(v, dec=0):
    return f"{v:,.{dec}f}".replace(',', ' ').replace('.', ',')


def fr(v, dec=2):
    return f"{v:.{dec}f}".replace('.', ',')


def calc(loyer, vac, gestion, tf, charges, provision, pno=150.0, compta=500.0):
    """Modele valide en amont (chat). Charges du moteur : TV + charges d'immeuble
    + PNO + (gestion locative + provision travaux) + comptabilite.
    Le seuil de 5 % net avant IS porte sur l'acte en main (prix + 8 % de frais)."""
    brut = loyer * 12.0
    v = brut * vac / 100.0
    g = brut * gestion / 100.0
    fixes = tf + charges + pno + provision + compta
    ebe = brut - v - g - fixes
    is_ = 0.15 * ebe
    net = ebe - is_
    return dict(loyer=loyer, vac=vac, gestion=gestion, tf=tf, charges=charges,
                provision=provision, brut=brut, vac_eur=v, gestion_eur=g, fixes=fixes,
                ebe=ebe, ebe_mois=ebe / 12.0, revient=ACTE_EN_MAIN, is_=is_, net=net,
                net_mois=net / 12.0, rdt_av=ebe / ACTE_EN_MAIN * 100.0,
                rdt_ap=net / ACTE_EN_MAIN * 100.0,
                rdt_valeur=net / VALEUR_RETENUE * 100.0,
                cap5=ebe / COEF_PLAFOND)


BASE = calc(1230.0, 8.0, 5.0, 900.0, 400.0, 200.0)
BEST = calc(1480.0, 5.0, 4.0, 800.0, 400.0, 100.0)
WORST = calc(810.0, 15.0, 6.0, 1100.0, 700.0, 400.0)
VACANT = calc(930.0, 6.0, 5.0, 900.0, 400.0, 200.0)

# Annee 1 : EBE moins interets d'emprunt moins dotation aux amortissements
INTERETS_AN1 = CAPITAL * TAUX_CREDIT                       # 5 141,52
DOTATION_AN1 = PRIX * QUOTE_PART_BATI_MODELE / 30.0        # 4 117,33
RESULTAT_AN1 = BASE['ebe'] - INTERETS_AN1 - DOTATION_AN1   # 1 432,35 -> positif
IS_AN1 = max(0.0, 0.15 * RESULTAT_AN1)                     # 214,85
IS_CONVENTION_EBE = 0.15 * BASE['ebe']                     # 1 603,68 (prudent)


def verifie_dvf():
    """Recalcule les statistiques DVF publiees depuis le fichier du departement."""
    if not os.path.exists(DVF_FICHIER):
        print(f"  DVF : fichier {DVF_FICHIER} absent — constantes DVF non "
              f"recalculees (a verifier avec stats_dvf_ville.py)")
        return False
    rows = []
    with gzip.open(DVF_FICHIER, 'rt', encoding='utf-8', errors='replace') as f:
        for r in csv.DictReader(f):
            if r['code_commune'] == DVF_COMMUNE:
                rows.append(r)

    def f2(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return None

    muts = {}
    for r in rows:
        muts.setdefault(r['id_mutation'], []).append(r)
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
                out.append((s, vf / s))
        return out

    def med(v):
        return round(st.median(v))

    def q13(v):
        x = st.quantiles(v, n=4)
        return round(x[0]), round(x[2])

    app = pool('Appartement')
    mai = pool('Maison')
    va = [p for _, p in app]
    vm = [p for _, p in mai]
    calcule("DVF mutations de nature Vente", DVF_VENTES, len(ventes), 0)
    calcule("DVF ventes d'appartements", DVF_APP_N, len(va), 0)
    calcule("DVF mediane appartements", DVF_APP_MED, med(va), 0)
    calcule("DVF Q1 appartements", DVF_APP_Q1, q13(va)[0], 0)
    calcule("DVF Q3 appartements", DVF_APP_Q3, q13(va)[1], 0)
    for lo, hi, n_, m_ in ((0, 30, DVF_APP_PETIT_N, DVF_APP_PETIT_MED),
                           (30, 60, DVF_APP_3060_N, DVF_APP_3060_MED),
                           (60, 100000, DVF_APP_60P_N, DVF_APP_60P_MED)):
        sel = [p for s, p in app if lo <= s < hi]
        calcule(f"DVF appartements {lo}-{hi} m2 (n)", n_, len(sel), 0)
        calcule(f"DVF appartements {lo}-{hi} m2 (mediane)", m_, med(sel), 0)
    calcule("DVF ventes de maisons", DVF_MAI_N, len(vm), 0)
    calcule("DVF mediane maisons", DVF_MAI_MED, med(vm), 0)
    imb = [p for s, p in _immeubles(ventes, f2) if s > 5]
    calcule("DVF mutations 2+ logements (n)", DVF_IMB_N, len(imb), 0)
    calcule("DVF immeubles mediane", DVF_IMB_MED, med(imb), 0)
    calcule("DVF immeubles plancher", DVF_IMB_MIN, round(min(imb)), 0)
    calcule("DVF immeubles plafond", DVF_IMB_MAX, round(max(imb)), 0)
    mixte = [p for s, p in _mixtes(ventes, f2) if s > 5]
    calcule("DVF mutations mixtes logement+local (n)", DVF_MIXTE_N, len(mixte), 0)
    calcule("DVF mixtes plancher", DVF_MIXTE_MIN, round(min(mixte)), 0)
    calcule("DVF mixtes plafond", DVF_MIXTE_MAX, round(max(mixte)), 0)
    for cmp_ in (DVF_CMP1, DVF_CMP2):
        trouve = [(s, v / s) for s, v in _detail(ventes, f2, cmp_['prix'])]
        assert trouve, f"transaction DVF {cmp_['prix']} EUR absente du fichier"
        s, m2 = trouve[0]
        calcule(f"DVF comparable {cmp_['voie']} (surface)", cmp_['surf'], s, 0.5)
        calcule(f"DVF comparable {cmp_['voie']} (EUR/m2)", cmp_['m2'], m2, 1.0)
    return True


def _immeubles(ventes, f2):
    out = []
    for rs in ventes:
        lots = [r for r in rs if r['type_local'] in ('Appartement', 'Maison')]
        if len(lots) < 2:
            continue
        vf = f2(rs[0]['valeur_fonciere']) or 0.0
        s = sum(f2(r['surface_reelle_bati']) or 0.0 for r in rs)
        if vf > 5000:
            out.append((s, vf / s))
    return out


def _mixtes(ventes, f2):
    hab = ('Appartement', 'Maison')
    loc = 'Local industriel. commercial ou assimilé'
    out = []
    for rs in ventes:
        tl = {r['type_local'] for r in rs}
        if not (tl & set(hab)) or loc not in tl:
            continue
        vf = f2(rs[0]['valeur_fonciere']) or 0.0
        s = sum(f2(r['surface_reelle_bati']) or 0.0 for r in rs)
        if vf > 5000:
            out.append((s, vf / s))
    return out


def _detail(ventes, f2, prix):
    for rs in ventes:
        vf = f2(rs[0]['valeur_fonciere']) or 0.0
        if abs(vf - prix) < 1.0:
            s = sum(f2(r['surface_reelle_bati']) or 0.0 for r in rs)
            return [(s, vf)]
    return []


def rec_immeuble_brignoles():
    nm = eur(SURF_HAB)
    return {
        "slug": SLUG,
        "date_analyse": DATE,
        "date_maj": None,
        "titre": (
            "Immeuble de rapport en centre vieille ville — local commercial de 20 m², "
            "studio de 20 m² et duplex T2 de 47 m², cave de 17 m² — Brignoles (83170)"
        ),
        "bien": {
            "type_bien": "immeuble",
            "sous_type": None,
            "type_detail": (
                "Immeuble de rapport du centre vieille ville de Brignoles, construit en 1940, "
                "composé de trois lots bâtis et d'une cave : au rez-de-chaussée un local "
                "commercial de 20 m² (une pièce avec salle d'eau et WC, annoncé « peut être "
                "transformé en un studio ») et une cave de 17 m² dont l'accès se fait par un "
                "escalier intérieur au local ; au 1er étage un studio de 20 m² (pièce de vie avec "
                "cuisine, salle d'eau, WC) ; au 2e étage un duplex de 47 m² de type T2 (pièce de "
                "vie avec cuisine d'environ 18 m², salle d'eau et WC, puis à l'étage deux chambres "
                "d'environ 9,50 et 11 m² dont une avec fenêtre sur couloir). DPE D, GES B, facture "
                "énergétique annoncée entre 810 et 1 140 €/an. L'annonce ne communique AUCUN "
                "loyer, AUCUN bail, AUCUNE taxe foncière, AUCUNE charge et AUCUN travaux, et "
                "affirme seulement « idéal investissement locatif » : le chiffrage repose donc "
                "entièrement sur des loyers reconstruits. La fiche « caractéristiques » de "
                "l'annonce indique « Pas de cave » alors que le texte décrit une cave de 17 m² — "
                "incohérence à lever avant l'offre. Aucun plan n'est joint, 12 photographies sont "
                "publiées, une visite virtuelle est annoncée mais non liée dans l'annonce. Aucun "
                "diagnostic autre que le DPE n'est communiqué"
            ),
            "neuf": False,
            "adresse": {
                "texte": (
                    "Centre vieille ville, Brignoles (83170) — adresse exacte non communiquée "
                    "par l'agence"
                ),
                "ville": "Brignoles",
                "code_postal": "83170",
            },
            "surfaces": {
                "texte": (
                    f"90 m² annoncés (1 716 €/m²) ; {eur(SURF_LOTS_BATIS)} m² de lots bâtis "
                    f"({eur(LOCAL)} local + {eur(STUDIO)} studio + {eur(DUPLEX)} duplex) plus une "
                    f"cave de {eur(CAVE)} m². Base retenue : {nm} m² pour les deux logements "
                    f"(studio {eur(STUDIO)} m² + duplex {eur(DUPLEX)} m²), hors cave et hors "
                    f"local, soit {eur(PRIX/SURF_HAB)} €/m²"
                ),
                "carrez_m2": SURF_HAB,
            },
            "lots": {
                "count": 3,
                "surface_par_lot_m2": None,
                "nature": (
                    f"Trois lots bâtis : local commercial de {eur(LOCAL)} m² au RDC (une pièce "
                    f"avec salle d'eau et WC), studio de {eur(STUDIO)} m² au 1er, duplex T2 de "
                    f"{eur(DUPLEX)} m² au 2e (deux chambres d'environ 9,50 et 11 m²), plus une "
                    f"cave de {eur(CAVE)} m² accessible par l'escalier intérieur du local. Aucune "
                    f"surface Carrez par lot, aucun plan, aucun diagnostic daté autre que le DPE"
                ),
                "lots_distincts": 3,
            },
            "copro": {
                "charges_annuelles_euros": 400.0,
                "charges_source": (
                    "Aucune copropriété n'est mentionnée : l'immeuble est présumé détenu en "
                    "totalité par un seul propriétaire, donc sans charges votées, sans budget "
                    "prévisionnel et sans mutualisation des travaux de structure. Le poste saisi "
                    "(400 €/an) couvre l'entretien courant, porté seul par l'acquéreur. À "
                    "CONFIRMER : si l'immeuble relève d'une copropriété, le budget prévisionnel "
                    "doit être obtenu, ce qui augmenterait d'autant les charges"
                ),
            },
            "travaux": {
                "montant_euros": 0.0,
                "nature": (
                    "Aucun travaux annoncé et aucun devis communiqué. Immeuble de 1940 : "
                    "couverture, charpente, réseaux et humidité de la cave ne sont documentés par "
                    "aucune pièce, et le seul diagnostic joint est le DPE. Aucune enveloppe n'est "
                    "donc engagée à l'acquisition — le chiffrage se fait en l'état, avec une "
                    "provision de 200 €/an en exploitation et le risque porté à la matrice — mais "
                    "le risque travaux est réel et non chiffrable avant une visite d'homme de "
                    "l'art : sur une couverture, une charpente ou une électricité à reprendre, la "
                    "facture se compte en années de loyer net"
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
                f"154 400 € honoraires à la charge du vendeur, soit {eur(PRIX/SURF_ANNONCEE)} €/m² "
                f"sur les 90 m² annoncés, {eur(PRIX/SURF_LOTS_BATIS)} €/m² sur les "
                f"{eur(SURF_LOTS_BATIS)} m² de lots bâtis et {eur(PRIX/SURF_HAB)} €/m² sur la base "
                f"de {nm} m² (les deux logements, hors cave et hors local). La médiane DVF 2025 des "
                f"appartements de la commune est de {eur(DVF_APP_MED)} €/m² et celle des immeubles "
                f"de rapport (deux logements et plus) de {eur(DVF_IMB_MED)} €/m² : le prix affiché "
                f"se situe au-dessus du haut de la fourchette observée pour ce dernier marché. "
                f"Vendeur : SAFTI, Maude MERRY, conseiller indépendant (EI, RCS Draguignan "
                f"522063833), référence agence 1699409"
            ),
        },
        "marche": {
            "valeur": {
                "basse_euros": VALEUR_BASSE,
                "haute_euros": VALEUR_HAUTE,
                "retenue_euros": VALEUR_RETENUE,
                "source": (
                    f"Ancrage DVF 2025 sur le produit réellement comparable — l'immeuble de "
                    f"rapport — et non sur la moyenne communale des appartements. Deux "
                    f"transactions mixtes (logement + local commercial) du centre-ville : "
                    f"{eur(DVF_CMP1['surf'])} m² vendus {eur(DVF_CMP1['prix'])} € le "
                    f"{DVF_CMP1['date']} {DVF_CMP1['voie']}, soit "
                    f"{eur(DVF_CMP1['m2'])} €/m² ; et {eur(DVF_CMP2['surf'])} m² vendus "
                    f"{eur(DVF_CMP2['prix'])} € le {DVF_CMP2['date']} {DVF_CMP2['voie']}, soit "
                    f"{eur(DVF_CMP2['m2'])} €/m². Les {DVF_IMB_N} mutations de 2025 comportant au "
                    f"moins deux logements donnent une médiane de {eur(DVF_IMB_MED)} €/m² (de "
                    f"{DVF_IMB_MIN} à {eur(DVF_IMB_MAX)} €/m²) et les {DVF_MIXTE_N} mutations "
                    f"mêlant logement et local commercial de {DVF_MIXTE_MIN} à "
                    f"{eur(DVF_MIXTE_MAX)} €/m². Valeur retenue {eur(VALEUR_RETENUE)} € = "
                    f"{eur(SURF_LOTS_BATIS)} m² × {eur(DVF_IMB_MED)} €/m², fourchette "
                    f"{eur(VALEUR_BASSE)} à {eur(VALEUR_HAUTE)} €. La médiane communale des "
                    f"appartements ({eur(DVF_APP_MED)} €/m², {DVF_APP_N} ventes) n'est pas "
                    f"applicable : un immeuble entier avec local commercial et cave se traite avec "
                    f"une décote de rendement, et la fiche de référence du secteur le confirme"
                ),
                "confiance": "moyenne",
            },
            "loyers": [
                {
                    "lot": "Studio de 20 m², 1er étage (pièce de vie avec cuisine, salle d'eau, WC)",
                    "quantite": 1,
                    "loyer_mensuel_euros": 380.0,
                    "occupe": True,
                    "note": (
                        "Aucun bail communiqué : 380 €/mois retenus, reconstruits. Point de "
                        "prudence à porter au dossier : 380 € sur 20 m² ressortent à 19 €/m²/mois, "
                        "au-dessus du ratio de l'annonce de 1 pièce de 36 m² relevée à 450 € "
                        "(12,5 €/m²) — c'est l'hypothèse la plus généreuse du modèle, et la "
                        "variante défavorable la ramène à 280 €. Le loyer de référence de la "
                        "commune est de 11,0 €/m²/mois sur un lot type de 60 m² (fiche "
                        "marches-locaux du 21/09/2026)"
                    ),
                },
                {
                    "lot": "Duplex T2 de 47 m², 2e étage (deux chambres d'environ 9,50 et 11 m²)",
                    "quantite": 1,
                    "loyer_mensuel_euros": 550.0,
                    "occupe": True,
                    "note": (
                        "Aucun bail communiqué : 550 €/mois retenus, soit 11,7 €/m²/mois, "
                        "reconstruits à partir des annonces relevées le 25/09/2026 à Brignoles "
                        "(2 pièces de 37 m² à 680 € en zone d'activité, 3 pièces meublé de 50 m² à "
                        "800 €). La chambre d'environ 9,50 m² avec fenêtre sur couloir ne se "
                        "qualifie pas comme chambre de plein droit : à instruire avant de compter "
                        "le lot comme un vrai T2"
                    ),
                },
                {
                    "lot": "Local commercial de 20 m² au rez-de-chaussée (avec salle d'eau et WC)",
                    "quantite": 1,
                    "loyer_mensuel_euros": 300.0,
                    "occupe": True,
                    "note": (
                        "C'est la seule vraie inconnue du dossier : aucun bail, aucun preneur, "
                        "aucun loyer mentionné pour un lot qui représente 23 % de la surface bâtie "
                        "(20 m² sur 87 m²). 300 €/mois retenus en hypothèse de base, soit "
                        "15 €/m²/mois. La vacance locative du commerce n'est pas documentée dans "
                        "le centre ancien de Brignoles : la variante publiée « local vacant toute "
                        "l'année » chiffre le dossier à 930 €/mois de loyers au total, soit "
                        "4,67 % net avant IS et un plafond de 144 119 € sous le prix affiché"
                    ),
                },
            ],
            "notes": (
                f"L'annonce ne communique aucun loyer alors qu'elle affirme « idéal investissement "
                f"locatif » : les trois loyers sont donc reconstruits, et c'est l'annonce du local "
                f"commercial qui est la plus fragile — 300 €, aucun preneur mentionné. Loyers "
                f"relevés sur place le 25/09/2026 (86 annonces actives à Brignoles) : 1 pièce de "
                f"36 m² en centre vieille ville 450 € (12,5 €/m²) ; 2 pièces de 37 m² en "
                f"rez-de-chaussée de zone d'activité 680 € (18,4 €/m²) ; 3 pièces meublé de 50 m² "
                f"avec parking 800 € ; maison meublée de 4 pièces de 100 m² sur 800 m² de terrain "
                f"1 450 € ; place de parking 120 €. Le loyer de référence de la commune est de "
                f"11,0 €/m²/mois sur un lot type de 60 m² (fiche de référence du 21/09/2026). "
                f"Scénario de base : studio 380 € + duplex 550 € + local 300 € = 1 230 €/mois. "
                f"Hypothèse favorable : 1 480 €/mois. Hypothèse défavorable : 810 €/mois. "
                f"Variante local vacant : 930 €/mois. Entre l'hypothèse basse et l'hypothèse "
                f"haute, le rendement net avant IS passe de {fr(WORST['rdt_av'])} % à "
                f"{fr(BEST['rdt_av'])} % et le plafond d'achat de {eur(WORST['cap5'])} € à "
                f"{eur(BEST['cap5'])} € : c'est le montant exact de l'inconnue que porte cette "
                f"annonce, et le local du rez-de-chaussée en est le premier poste"
            ),
        },
        "hypotheses": {
            "vacance_base_pct": 8.0,
            "vacance_best_pct": 5.0,
            "vacance_worst_pct": 15.0,
            "vacance_justification": (
                "8 % en scénario de base : trois lots sur trois niveaux, dont un local commercial "
                "et un studio, dont la rotation est plus rapide que celle d'un logement familial. "
                "5 % en hypothèse favorable si les trois lots restent loués. 15 % en hypothèse "
                "défavorable, parce qu'un studio et un local commercial peuvent se libérer la même "
                "année et qu'un local vide se reloue en plusieurs mois, pas en plusieurs semaines. "
                "La variante « local vacant » retient 6 % de vacance sur les deux logements seuls, "
                "le local étant compté à zéro : une vacance structurelle n'est pas une provision "
                "statistique, elle s'ajoute lot à lot"
            ),
            "frais_acquisition_euros": round(PRIX * NOTAIRE, 2),
            "frais_divers_euros": 0.0,
            "quote_part_bati_pct": 0.0,
            "duree_amortissement_ans": 30,
            "fiscalite_commentaire": (
                f"SCI à l'IS. Calcul réel de l'année 1 : EBE {eur(BASE['ebe'])} € moins intérêts "
                f"d'emprunt {eur(INTERETS_AN1)} € ({eur(CAPITAL)} € à 3,7 %) moins la dotation aux "
                f"amortissements {eur(DOTATION_AN1)} € (bâti à 80 % sur 30 ans) = résultat "
                f"imposable de {eur(RESULTAT_AN1)} €, POSITIF, donc IS de 15 % soit "
                f"{eur(IS_AN1)} € — contrairement aux dossiers où l'amortissement crée un déficit. "
                f"Convention prudente retenue pour les rendements nets publiés : IS de 15 % "
                f"appliqué à l'EBE, sans amortissement du bâti modélisé, soit "
                f"{eur(IS_CONVENTION_EBE)} €/an — c'est la lecture la plus défavorable, et c'est "
                f"elle que le moteur applique ici (quote_part_bati_pct = 0). Le seuil de décision "
                f"de la doctrine du parc porte de toute façon sur le rendement net AVANT IS"
            ),
            "charges": {
                "taxe_fonciere_annuelle_euros": 900.0,
                "taxe_fonciere_commentaire": (
                    "ESTIMATION 900 €/an — avis non communiqué par le vendeur. Fourchette 700 à "
                    "1 100 €/an pour un immeuble de trois lots et 87 m² de lots bâtis en centre "
                    "ancien. Le scénario défavorable retient 1 100 € : l'inconnue vaut 200 €/an, "
                    "soit 0,13 % de rendement net avant IS sur l'acte en main"
                ),
                "charges_copro_annuelles_euros": 400.0,
                "charges_copro_commentaire": (
                    "Aucune copropriété mentionnée : aucun budget prévisionnel, aucune charge "
                    "votée. 400 €/an provisionnés pour l'entretien courant des parties communes et "
                    "de la cave, porté seul par le propriétaire. Le scénario défavorable retient "
                    "700 €"
                ),
                "pno_annuelle_euros": 150.0,
                "pno_commentaire": (
                    "Assurance propriétaire non occupant de l'immeuble et de ses trois lots. "
                    "Immeuble de 1940 en centre ancien, un local commercial et deux logements"
                ),
                "entretien_annuel_euros": round(GESTION_BASE + BASE['provision'], 2),
                "entretien_commentaire": (
                    f"Poste composite, détaillé : gestion locative {eur(GESTION_BASE)} € "
                    f"(5 % des {eur(BASE['brut'])} € de loyers bruts du scénario de base) + "
                    f"provision travaux {eur(BASE['provision'])} € = "
                    f"{eur(GESTION_BASE + BASE['provision'])} €. Le moteur ne connaît ni la ligne "
                    f"de gestion locative ni celle de provision gros travaux : les deux sont "
                    f"fondues ici pour que l'EBE publié corresponde au modèle chiffré. La "
                    f"provision automatique du moteur (2,5 % des loyers) est désactivée : "
                    f"l'additionner à la provision explicite compterait deux fois la même "
                    f"cagnotte. Hypothèse favorable : gestion 4 % et provision 100 €, soit "
                    f"{eur(BEST['gestion_eur'] + BEST['provision'])} €. Hypothèse défavorable : "
                    f"gestion 6 %, provision 400 €, soit "
                    f"{eur(WORST['gestion_eur'] + WORST['provision'])} €"
                ),
                "comptabilite_annuelle_euros": 500.0,
                "comptabilite_commentaire": (
                    "Comptabilité de la SCI à l'IS, trois lots dont un local commercial (TVA et "
                    "bail commercial) : à mutualiser si d'autres lots entrent dans la même "
                    "structure"
                ),
                "provision_desactivee": True,
            },
        },
        "analyse": {
            "branche": "residentiel",
            "type_operation": "locatif",
            "strategie_retenue": {
                "nom": ("Conservation en location longue durée des trois lots — studio, duplex T2 "
                        "et local commercial"),
                "code": "ld-nue",
                "lots": 3,
            },
            "strategies_explorees": [
                {
                    "strategie": "Location longue durée des trois lots (base)",
                    "lots": 3,
                    "rendement": (
                        f"{fr(BASE['rdt_av'])} % net avant IS sur l'acte en main "
                        f"({eur(BASE['ebe'])} € d'EBE, {eur(BASE['ebe_mois'])} €/mois), "
                        f"{fr(BASE['rdt_ap'])} % après IS sous convention prudente"
                    ),
                    "faisabilite": (
                        "immédiate si le local trouve preneur : deux logements louables sans "
                        "travaux annoncés. Il faut obtenir les baux et l'occupation du local avant "
                        "toute offre"
                    ),
                    "risque": (
                        f"moyen — le seuil de rendement est tenu, mais le cash-flow est négatif de "
                        f"{eur(abs(cashflow_mensuel(BASE['ebe'], CAPITAL)))} €/mois et le dossier "
                        f"échoue au critère de trésorerie du parc"
                    ),
                },
                {
                    "strategie": "Location longue durée, loyers hauts de la fourchette (optimiste)",
                    "lots": 3,
                    "rendement": (
                        f"{fr(BEST['rdt_av'])} % net avant IS ({eur(BEST['ebe'])} € d'EBE), "
                        f"{fr(BEST['rdt_ap'])} % après IS, plafond 5 % "
                        f"{eur(BEST['cap5'])} €"
                    ),
                    "faisabilite": (
                        "relocation du studio à 400 €, du duplex à 580 € et du local à 500 €, au "
                        "niveau haut du marché relevé : c'est le seul scénario où le cash-flow "
                        "redevient positif (+"
                        f"{eur(cashflow_mensuel(BEST['ebe'], CAPITAL))} €/mois)"
                    ),
                    "risque": (
                        "moyen — suppose de relouer les trois lots au haut du marché et que le "
                        "local commercial trouve un preneur durable, dans un centre ancien dont la "
                        "vacance commerciale n'est pas documentée"
                    ),
                },
                {
                    "strategie": ("Location longue durée, loyers bas, local en rotation et charges "
                                  "lourdes (pessimiste)"),
                    "lots": 3,
                    "rendement": (
                        f"{fr(WORST['rdt_av'])} % net avant IS ({eur(WORST['ebe'])} € d'EBE), "
                        f"{fr(WORST['rdt_ap'])} % après IS, plafond 5 % {eur(WORST['cap5'])} €"
                    ),
                    "faisabilite": (
                        "loyers 810 €/mois, vacance 15 %, taxe foncière à 1 100 €, charges 700 € "
                        "et provision 400 € : c'est le scénario à retenir si un bail est "
                        "sous-évalué ou si le local reste vide plusieurs mois par an"
                    ),
                    "risque": (
                        f"élevé — {fr(WORST['rdt_av'])} % net avant IS et un cash-flow de "
                        f"{eur(cashflow_mensuel(WORST['ebe'], CAPITAL))} €/mois : le prix ne passe "
                        f"plus, ni sur le rendement ni sur la trésorerie"
                    ),
                },
                {
                    "strategie": "Variante publiée — local commercial vacant toute l'année",
                    "lots": 2,
                    "rendement": (
                        f"{fr(VACANT['rdt_av'])} % net avant IS ({eur(VACANT['ebe'])} € d'EBE, "
                        f"{eur(VACANT['ebe_mois'])} €/mois) sur 930 €/mois de loyers, "
                        f"{fr(VACANT['rdt_ap'])} % après IS, plafond 5 % {eur(VACANT['cap5'])} €"
                    ),
                    "faisabilite": (
                        "hypothèse basse à retenir si aucun preneur ne se présente pour le local : "
                        "le studio et le duplex se relouent, le local de 20 m² du centre ancien non "
                        "— c'est la lecture la plus prudente du dossier"
                    ),
                    "risque": (
                        f"élevé — {eur(144119.0)} € de plafond contre {eur(PRIX)} € de prix "
                        f"affiché, soit {fr((PRIX - 144119.0) / PRIX * 100.0, 1)} % au-dessus : le "
                        f"local fait basculer le dossier du rendement acceptable à la décote "
                        f"obligatoire"
                    ),
                },
                {
                    "strategie": "Achat-rénovation-revente (marchand de biens)",
                    "lots": 3,
                    "rendement": (
                        f"impossible au prix affiché : la valeur de marché de l'immeuble ressort à "
                        f"{eur(VALEUR_RETENUE)} € contre un prix de revient de "
                        f"{eur(ACTE_EN_MAIN)} €, soit une marge négative de "
                        f"{eur(ACTE_EN_MAIN - VALEUR_RETENUE)} € avant même les frais de revente "
                        f"et la fiscalité"
                    ),
                    "faisabilite": (
                        "aucune : l'immeuble n'a aucune décote d'entrée à capter, et le marché de "
                        "revente des immeubles de rapport de la commune est étroit — "
                        f"{DVF_IMB_N} mutations de deux logements et plus en 2025, "
                        f"{DVF_MIXTE_N} seulement mêlant logement et local commercial"
                    ),
                    "risque": (
                        "bloquant sur ce plan de sortie — l'actif ne se défend que par son "
                        "rendement, et la division en lots ne se présume pas"
                    ),
                },
            ],
            "attractivite": [
                {
                    "dimension": "transports",
                    "score": 6,
                    "justification": (
                        "Brignoles est à l'entrée de l'autoroute A8, à 30 minutes de Saint-"
                        "Maximin et une heure de Toulon, avec un bassin d'emploi propre et une "
                        "gare routière en centre-ville. La commune n'a pas de desserte ferroviaire "
                        "voyageurs : c'est une ville de voiture, ce qui limite la cible locataire "
                        "au premier chef un local commercial et un studio de centre ancien"
                    ),
                },
                {
                    "dimension": "commerces",
                    "score": 7,
                    "justification": (
                        "Ville de 17 000 habitants avec une vie commerçante de centre ancien, un "
                        "marché, une zone d'activité et les chaînes nationales. Le bien est dans "
                        "la vieille ville, c'est-à-dire à l'adresse la plus passante du centre "
                        "pour le local du rez-de-chaussée — mais la vacance commerciale du centre "
                        "ancien n'est pas documentée et doit être vérifiée rue par rue"
                    ),
                },
                {
                    "dimension": "ecoles",
                    "score": 7,
                    "justification": (
                        "Écoles, collège et lycée sur la commune, plus les établissements de "
                        "Saint-Maximin et de Toulon : c'est le profil type du locataire d'un "
                        "studio et d'un T2 de centre ancien"
                    ),
                },
                {
                    "dimension": "securite",
                    "score": 6,
                    "justification": (
                        "Commune du centre Var sans tension particulière, centre ancien en cours "
                        "de repeuplement. Un immeuble entier en monopropriété limite les nuisances "
                        "de voisinage, mais la cave donne sur un escalier intérieur au local : la "
                        "sécurité d'accès du commerce et de la cave est à vérifier sur place"
                    ),
                },
                {
                    "dimension": "demande_locative",
                    "score": 6,
                    "justification": (
                        f"Marché locatif réel et documenté le 25/09/2026 : 86 annonces actives à "
                        f"Brignoles, 1 pièce de 36 m² à 450 €, 2 pièces de 37 m² à 680 €, 3 pièces "
                        f"meublé de 50 m² à 800 €, maison meublée de 100 m² à 1 450 €, parking à "
                        f"120 €. Mais le loyer de référence de la commune est de 11,0 €/m²/mois sur "
                        f"un lot type de 60 m² (fiche du 21/09/2026) : l'hypothèse de 19 €/m²/mois "
                        f"retenue sur le studio de 20 m² est au-dessus de ce que le marché "
                        f"démontre, et c'est un point de négociation, pas un acquis"
                    ),
                },
                {
                    "dimension": "dynamisme",
                    "score": 7,
                    "justification": (
                        f"{DVF_VENTES} mutations de nature « Vente » enregistrées dans la commune "
                        f"en 2025, dont {DVF_APP_N} ventes d'appartements (médiane "
                        f"{eur(DVF_APP_MED)} €/m²) et {DVF_MAI_N} ventes de maisons (médiane "
                        f"{eur(DVF_MAI_MED)} €/m²) : le marché de revente est liquide. Le marché "
                        f"de l'immeuble de rapport l'est beaucoup moins — {DVF_IMB_N} mutations de "
                        f"deux logements et plus, médiane {eur(DVF_IMB_MED)} €/m² — et c'est "
                        f"celui-ci qui commande la sortie"
                    ),
                },
            ],
            "risques": [
                {
                    "facteur": ("Local commercial de 20 m² sans preneur ni bail : 23 % de la "
                                "surface bâtie"),
                    "severite": 5,
                    "detail": (
                        f"C'est le poste qui décide du dossier, et il n'est documenté nulle part : "
                        f"aucun bail, aucun preneur, aucun loyer, aucune durée. Le local représente "
                        f"{eur(LOCAL)} m² sur {eur(SURF_LOTS_BATIS)} m² de lots bâtis, soit "
                        f"{fr(LOCAL / SURF_LOTS_BATIS * 100, 0)} %. Selon qu'il est loué ou vide, "
                        f"le rendement net avant IS passe de {fr(BASE['rdt_av'])} % à "
                        f"{fr(VACANT['rdt_av'])} %, le plafond d'achat de {eur(BASE['cap5'])} € à "
                        f"{eur(VACANT['cap5'])} € et le cash-flow de "
                        f"{eur(cashflow_mensuel(BASE['ebe'], CAPITAL))} €/mois à "
                        f"{eur(cashflow_mensuel(VACANT['ebe'], CAPITAL))} €/mois. La vacance "
                        f"commerciale du centre ancien de Brignoles n'est pas documentée : à "
                        f"vérifier en mairie et par un relevé des locaux vides de la rue AVANT "
                        f"toute offre"
                    ),
                },
                {
                    "facteur": "Aucun loyer, aucun bail, aucune taxe foncière, aucune charge",
                    "severite": 5,
                    "detail": (
                        f"L'annonce affirme « idéal investissement locatif » et ne donne pas un "
                        f"seul chiffre d'exploitation : ni loyer, ni bail, ni date d'échéance, ni "
                        f"taxe foncière, ni charge, ni travaux. Le chiffrage publié repose donc "
                        f"sur des loyers reconstruits à partir du marché relevé le 25/09/2026 : "
                        f"{fr(BASE['rdt_av'])} % net avant IS à 1 230 €/mois, "
                        f"{fr(BEST['rdt_av'])} % à 1 480 €, {fr(WORST['rdt_av'])} % à 810 €. "
                        f"L'écart entre les hypothèses vaut une recommandation. Exiger les trois "
                        f"baux ou attestations de location, les quittances et l'avis de taxe "
                        f"foncière AVANT l'offre : une annonce qui vend de la rentabilité sans en "
                        f"donner le chiffre dit quelque chose du dossier"
                    ),
                },
                {
                    "facteur": "Immeuble de 1940 : couverture, charpente et réseaux non documentés",
                    "severite": 4,
                    "detail": (
                        "Aucun devis, aucun diagnostic électricité, plomb ou amiante, aucun état "
                        "de la couverture, de la charpente ni de l'humidité de la cave — seul le "
                        "DPE est joint. Sur un immeuble entier en monopropriété, ces postes sont à "
                        "100 % pour l'acquéreur : une couverture à reprendre ou une électricité à "
                        "mettre aux normes sur trois niveaux coûte plusieurs années de loyer net, "
                        "et rien de tout cela n'est dans le prix. Visite d'un homme de l'art et "
                        "devis écrits avant l'offre, sur les trois postes qui dérapent : "
                        "électricité, couverture, humidité de la cave"
                    ),
                },
                {
                    "facteur": "Cash-flow négatif sous crédit : le dossier échoue au critère du parc",
                    "severite": 4,
                    "detail": (
                        f"Le dossier passe la grille de rendement ({fr(BASE['rdt_av'])} % net "
                        f"avant IS au prix affiché) mais pas le critère de trésorerie. À 10 % "
                        f"d'apport, prêt de {eur(CAPITAL)} € sur 15 ans à 3,7 % avec assurance "
                        f"emprunteur de 0,34 %, la mensualité est de {eur(mensualite(CAPITAL))} €/mois "
                        f"quand l'exploitation dégage {eur(BASE['ebe_mois'])} €/mois en scénario de "
                        f"base : le cash-flow est de "
                        f"{eur(cashflow_mensuel(BASE['ebe'], CAPITAL))} €/mois, soit "
                        f"{eur(cashflow_mensuel(BASE['ebe'], CAPITAL) * 12)} €/an, et il ne "
                        f"redevient positif que dans l'hypothèse favorable "
                        f"(+{eur(cashflow_mensuel(BEST['ebe'], CAPITAL))} €/mois). Si le local "
                        f"reste vide, il faut {eur(apport_cashflow_nul(PRIX, VACANT['ebe']))} € "
                        f"d'apport ({fr(apport_cashflow_nul(PRIX, VACANT['ebe']) / PRIX * 100, 0)} % "
                        f"du prix) pour équilibrer — très au-delà de la doctrine du parc"
                    ),
                },
                {
                    "facteur": "Marché de revente de l'immeuble de rapport très étroit",
                    "severite": 3,
                    "detail": (
                        f"Le marché résidentiel de la commune est liquide ({DVF_VENTES} mutations "
                        f"en 2025), mais celui de l'immeuble de rapport ne l'est pas : "
                        f"{DVF_IMB_N} mutations de deux logements et plus dans l'année, médiane "
                        f"{eur(DVF_IMB_MED)} €/m², et seulement {DVF_MIXTE_N} transactions mêlant "
                        f"logement et local commercial. La sortie se fera donc sur un marché "
                        f"d'acquéreurs de rendement, à un prix dicté par le rendement obtenu, et "
                        f"non par la valeur des lots pris séparément. À ce prix d'entrée, la "
                        f"revente suppose de retrouver le même acquéreur — c'est un actif qui se "
                        f"garde, pas qui se retourne"
                    ),
                },
                {
                    "facteur": "Cave de 17 m² annoncée, puis contredite par la fiche « Pas de cave »",
                    "severite": 3,
                    "detail": (
                        "Le texte de l'annonce décrit une cave de 17 m² avec accès par escalier "
                        "intérieur au local commercial ; la fiche « caractéristiques » du même "
                        "bien indique « Pas de cave ». Les deux documents portent sur le même lot "
                        "et ne peuvent pas être vrais en même temps. L'enjeu n'est pas la surface "
                        "de la cave mais ce que la contradiction dit du dossier : aucune pièce "
                        "n'a été vérifiée avant publication, ni les surfaces, ni les diagnostics. "
                        "À lever par écrit avant l'offre — et à vérifier au titre de "
                        "l'exposition à l'humidité et de l'usage réel du volume"
                    ),
                },
                {
                    "facteur": ("Chambre du duplex avec fenêtre sur couloir : défaut de jour, "
                                "9,50 m² à qualifier"),
                    "severite": 3,
                    "detail": (
                        "Sur les deux chambres du duplex (environ 9,50 et 11 m²), une a une "
                        "fenêtre sur couloir. Une pièce qui ne prend pas le jour sur l'extérieur "
                        "n'est pas une chambre de plein droit au sens du règlement sanitaire "
                        "départemental, et le logement ne se commercialise pas comme un T3 : au "
                        "mieux comme un T2 avec pièce annexe. Cela réduit la valeur locative du "
                        "lot et complique la revente à un acquéreur familial. À qualifier par le "
                        "règlement de copropriété, le PLU et le règlement sanitaire avant de "
                        "compter le lot comme un T2 — et à faire baisser le loyer cible en "
                        "conséquence"
                    ),
                },
                {
                    "facteur": ("Transformation du local en studio annoncée mais non instruite "
                                "(changement d'usage)"),
                    "severite": 3,
                    "detail": (
                        "L'annonce écrit que le local « peut être transformé en un studio » : "
                        "c'est une hypothèse d'agence, pas une autorisation. Passer un local "
                        "commercial en habitation suppose de vérifier le changement d'usage, le "
                        "destinataire de l'autorisation d'urbanisme, les règles du PLU et du "
                        "secteur sauvegardé, la desserte en réseau et le chiffrage des travaux "
                        "(création d'une cuisine, d'une salle d'eau aux normes, isolation, "
                        "électricité). Aucun de ces points n'est documenté. La transformation "
                        "partirait en surcoût sans bouquet de diagnostics et sans devis — et "
                        "c'est le seul levier du dossier, puisque le local est la variable qui "
                        "décide"
                    ),
                },
                {
                    "facteur": "Taxe foncière inconnue",
                    "severite": 2,
                    "detail": (
                        "L'avis n'est pas communiqué. Estimation retenue 900 €/an, fourchette "
                        "700 à 1 100 € pour un immeuble de trois lots en centre ancien. L'écart "
                        "vaut 200 €/an, soit 0,12 % de rendement net avant IS sur l'acte en main "
                        "— modeste en soi, mais à demander : c'est une pièce gratuite, et l'avis "
                        "donne la valeur locative cadastrale d'un bien dont aucune surface Carrez "
                        "par lot n'est publiée"
                    ),
                },
                {
                    "facteur": "Aucun plan, aucune surface Carrez par lot, visite virtuelle non liée",
                    "severite": 2,
                    "detail": (
                        "L'annonce repose sur 12 photographies et une visite virtuelle annoncée "
                        "mais non liée dans la page. Aucun plan n'est joint et aucune surface "
                        "Carrez n'est donnée par lot : or c'est la surface par lot qui détermine "
                        "le loyer réglementaire de chaque logement et l'article de surface "
                        "carrez. Les 90 m² annoncés comprennent la cave et le local, ce qui les "
                        "compare à tort aux surfaces habitables de la commune. Le dossier n'est "
                        "pas vérifiable à distance : tout chiffrage publié ici repose sur des "
                        "surfaces déclaratives"
                    ),
                },
            ],
            "champs_manquants": [
                "les loyers et les baux en cours des trois lots : montant, date de signature, échéance, type (nue, meublé ou commercial)",
                "l'occupation réelle du local commercial : bail, preneur, durée et loyer",
                "avis de taxe foncière réel et valeur locative cadastrale",
                "surfaces Carrez par lot, plan des trois niveaux et de la cave",
                "diagnostics datés : DPE, électricité, plomb, amiante, état de la couverture, de la charpente et de l'humidité de la cave",
                "statut de propriété de l'immeuble : monopropriété ou copropriété, et état descriptif de division s'il existe",
                "pièces d'urbanisme si la transformation du local en studio est envisagée : changement d'usage, PLU et règlement du secteur sauvegardé",
                "date d'effet et état des lieux des locations en cours",
            ],
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
    MPE = mensualite_par_euro()
    calcule("acte en main 154 400 + 8 %", ACTE_EN_MAIN, PRIX * (1.08), 0.5)
    calcule("mensualite 138 960 EUR", 1046.0, mensualite(CAPITAL), 1.0)
    calcule("prix de revient par euro emprunte", MENS_PAR_EURO_MODELE, MPE, 0.00001)
    calcule("EBE base", 10691.0, BASE['ebe'], 1.0)
    calcule("EBE best", 14212.0, BEST['ebe'], 1.0)
    calcule("EBE worst", 4829.0, WORST['ebe'], 1.0)
    calcule("EBE variante local vacant", 7782.0, VACANT['ebe'], 1.0)
    calcule("EBE mensuel base", 891.0, BASE['ebe_mois'], 1.0)
    calcule("EBE mensuel variante vacant", 649.0, VACANT['ebe_mois'], 1.0)
    calcule("rendement base avant IS", 0.0641, BASE['rdt_av'] / 100.0, 0.0002)
    calcule("rendement best avant IS", 0.0852, BEST['rdt_av'] / 100.0, 0.0002)
    calcule("rendement worst avant IS", 0.0290, WORST['rdt_av'] / 100.0, 0.0002)
    calcule("rendement variante vacant avant IS", 0.0467, VACANT['rdt_av'] / 100.0, 0.0002)
    calcule("plafond 5 % base", 197985.0, BASE['cap5'], 5.0)
    calcule("plafond 5 % best", 263178.0, BEST['cap5'], 5.0)
    calcule("plafond 5 % worst", 89422.0, WORST['cap5'], 5.0)
    calcule("plafond 5 % variante vacant", 144119.0, VACANT['cap5'], 5.0)
    calcule("cash-flow base /mois", -156.0, cashflow_mensuel(BASE['ebe'], CAPITAL), 1.0)
    calcule("cash-flow base /an", -1867.0, cashflow_mensuel(BASE['ebe'], CAPITAL) * 12, 2.0)
    calcule("cash-flow best /mois", 138.0, cashflow_mensuel(BEST['ebe'], CAPITAL), 1.0)
    calcule("cash-flow worst /mois", -644.0, cashflow_mensuel(WORST['ebe'], CAPITAL), 1.0)
    calcule("cash-flow variante vacant /mois", -398.0,
            cashflow_mensuel(VACANT['ebe'], CAPITAL), 1.0)
    calcule("cash-flow variante vacant /an", -4775.0,
            cashflow_mensuel(VACANT['ebe'], CAPITAL) * 12, 2.0)
    calcule("prix a cash-flow nul (base)", 131451.0, prix_cashflow_nul(BASE['ebe']), 5.0)
    calcule("prix a cash-flow nul (best)", 174735.0, prix_cashflow_nul(BEST['ebe']), 5.0)
    calcule("prix a cash-flow nul (local vacant)", 95686.0,
            prix_cashflow_nul(VACANT['ebe']), 5.0)
    calcule("apport cash-flow nul au prix affiche (base)", 36094.0,
            apport_cashflow_nul(PRIX, BASE['ebe']), 5.0)
    calcule("apport cash-flow nul au prix affiche (local vacant)", 68282.0,
            apport_cashflow_nul(PRIX, VACANT['ebe']), 5.0)
    calcule("loyers requis pour cash-flow nul au prix affiche", 1404.0,
            loyer_cashflow_nul(CAPITAL), 6.0)
    calcule("rendement a l'offre 130 000", 7.61, BASE['ebe'] / (130000.0 * 1.08) * 100.0, 0.01)
    calcule("cash-flow a l'offre 130 000", 9.8,
            cashflow_mensuel(BASE['ebe'], 130000.0 * (1 - APPORT_PCT)), 0.5)
    calcule("rendement au plafond 140 000", 7.07, BASE['ebe'] / (140000.0 * 1.08) * 100.0, 0.01)
    calcule("cash-flow au plafond 140 000", -58.0,
            cashflow_mensuel(BASE['ebe'], 140000.0 * (1 - APPORT_PCT)), 1.0)
    calcule("mensualite a l'offre 130 000", 881.0,
            mensualite(130000.0 * (1 - APPORT_PCT)), 1.0)
    calcule("mensualite au plafond 140 000", 949.0,
            mensualite(140000.0 * (1 - APPORT_PCT)), 1.0)
    # Fiscalite annee 1 : le resultaT est POSITIF, donc IS du
    calcule("interets annee 1", 5142.0, INTERETS_AN1, 1.0)
    calcule("dotation annee 1 (bati 80 % sur 30 ans)", 4117.0, DOTATION_AN1, 1.0)
    calcule("resultat imposable annee 1", 1432.0, RESULTAT_AN1, 1.0)
    assert RESULTAT_AN1 > 0, RESULTAT_AN1
    calcule("IS annee 1", 215.0, IS_AN1, 1.0)
    calcule("IS convention prudente (15 % de l'EBE)", 1604.0, IS_CONVENTION_EBE, 1.0)
    # Valeur de marche et surfaces
    calcule("prix / m2 sur 90 m2 annonces", 1716.0, PRIX / SURF_ANNONCEE, 1.0)
    calcule("prix / m2 sur 87 m2 de lots batis", 1775.0, PRIX / SURF_LOTS_BATIS, 1.0)
    calcule("prix / m2 sur 67 m2 retenus", 2304.0, PRIX / SURF_HAB, 1.0)
    calcule("part du local dans la surface batie (%)", 23.0,
            LOCAL / SURF_LOTS_BATIS * 100.0, 0.05)
    calcule("valeur retenue = 87 m2 x mediane immeubles", VALEUR_RETENUE,
            SURF_LOTS_BATIS * DVF_IMB_MED, 50.0)
    calcule("valeur basse = 87 m2 x comparable Entraigues", VALEUR_BASSE,
            SURF_LOTS_BATIS * DVF_CMP1['m2'], 100.0)
    calcule("valeur haute = 87 m2 x comparable Jules Ferry", VALEUR_HAUTE,
            SURF_LOTS_BATIS * DVF_CMP2['m2'], 100.0)
    calcule("ecart plafond local vacant au prix affiche (%)", 6.7,
            (PRIX - VACANT['cap5']) / PRIX * 100.0, 0.05)
    calcule("ratio cout/valeur", ACTE_EN_MAIN / VALEUR_RETENUE,
            engine.ratio_cout_valeur(rec_immeuble_brignoles()), 0.001)
    # Somme des loyers = strategie retenue (le moteur additionne toutes les lignes)
    rec_ = rec_immeuble_brignoles()
    total_loyers = sum(l['loyer_mensuel_euros'] for l in rec_['marche']['loyers'])
    calcule("somme des loyers retenus", BASE['loyer'], total_loyers, 0.01)
    calcule("surfaces des lots = surface batie retenue",
            SURF_LOTS_BATIS, LOCAL + STUDIO + DUPLEX, 0.01)
    calcule("surface retenue = deux logements (studio + duplex)",
            SURF_HAB, STUDIO + DUPLEX, 0.01)

    # ------------------------------------------------------------------
    # 3. Moteur : l'EBE du moteur doit egaler celui du modele
    # ------------------------------------------------------------------
    r = engine.compute(rec_)
    note, verdict, comp = scoring.note_et_verdict(rec_, r)
    rd = r['rendements']
    assert r['calculable'], r['raison']
    assert schema.validate_record(rec_) == [], schema.validate_record(rec_)
    print(f"  moteur : calculable={r['calculable']} | EBE {eur(r['fiscal']['ebe'])} EUR | "
          f"IS {eur(r['fiscal']['is_annuel'])} | net {eur(r['fiscal']['net_apres_is'])} | "
          f"CF {eur(r['fiscal']['cf_mensuel_net'])} EUR/mois")
    print(f"  moteur : net/revient {fr(rd['net_sur_revient_pct'])} % | net/achat "
          f"{fr(rd['net_sur_achat_pct'])} % | net/valeur {fr(rd['net_sur_valeur_pct'])} % | "
          f"ratio {fr(r['ratio_cout_valeur'])}")
    print(f"  moteur : revenus bruts {eur(r['revenus_bruts_annuels'])} EUR | frais "
          f"{eur(r['frais_acquisition'])} EUR | revient {eur(r['prix_revient_total'])} EUR")
    print(f"  note {note}/10 | verdict {verdict} | {comp}")
    assert abs(r['fiscal']['ebe'] - BASE['ebe']) < 0.01, (r['fiscal']['ebe'], BASE['ebe'])
    assert abs(r['fiscal']['is_annuel'] - IS_CONVENTION_EBE) < 0.01, \
        (r['fiscal']['is_annuel'], IS_CONVENTION_EBE)
    assert abs(r['fiscal']['amortissement']) < 0.01, r['fiscal']['amortissement']
    assert abs(rd['net_sur_revient_pct'] - BASE['rdt_ap']) < 0.01, rd
    assert abs(rd['net_sur_valeur_pct'] - BASE['rdt_valeur']) < 0.01, rd
    assert abs(r['prix_revient_total'] - ACTE_EN_MAIN) < 0.01, r['prix_revient_total']
    assert verdict == "negocier", verdict
    assert schema.champs_manquants(rec_) == [], schema.champs_manquants(rec_)

    # ------------------------------------------------------------------
    # 4. Generation de la fiche
    # ------------------------------------------------------------------
    spec = importlib.util.spec_from_file_location(
        "gen", os.path.join(ROOT, 'scripts', 'gen_fiches_2026-09-10.py'))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)

    def ligne(label, val, cls=""):
        c = f' class="{cls}"' if cls else ''
        return f'            <tr{c}><td>{label}</td><td class="num">{val}</td></tr>'

    def compte(d, titre, sous):
        rows = [
            ligne("Loyers bruts annuels", f"{eur(d['brut'])} €"),
            ligne(f"Vacance locative {fr(d['vac'], 0)} %", f"-{eur(d['vac_eur'])} €"),
            ligne(f"Gestion locative {fr(d['gestion'], 0)} %", f"-{eur(d['gestion_eur'])} €"),
            ligne("Taxe foncière (estimation)", f"-{eur(d['tf'])} €"),
            ligne("Charges d'immeuble (pas de copropriété)", f"-{eur(d['charges'])} €"),
            ligne("Assurance PNO", "-150 €"),
            ligne("Provision travaux", f"-{eur(d['provision'])} €"),
            ligne("Comptabilité SCI à l'IS", "-500 €"),
            ligne("Excédent brut d'exploitation", f"{eur(d['ebe'])} €", "subtotal"),
            ligne(f"IS 15 % de l'EBE (convention prudente)", f"-{eur(d['is_'])} €"),
            ligne("Net après IS", f"{eur(d['net'])} €", "highlight"),
            ligne("EBE mensuel", f"{eur(d['ebe_mois'])} €/mois"),
            ligne("Rendement net avant IS sur l'acte en main", f"{fr(d['rdt_av'])} %",
                  "highlight"),
            ligne("Rendement net après IS sur l'acte en main", f"{fr(d['rdt_ap'])} %"),
            ligne(f"Rendement net après IS sur la valeur ({eur(VALEUR_RETENUE)} €)",
                  f"{fr(d['rdt_valeur'])} %"),
            ligne("Prix d'achat tenant 5 % net avant IS", f"{eur(d['cap5'])} €"),
        ]
        return f"""      <div class="projection-card scenario-{titre}">
        <h3>{sous}</h3>
        <p class="scenario-subtitle">{eur(d['loyer'])} €/mois de loyers, vacance {fr(d['vac'], 0)} % — EBE {eur(d['ebe_mois'])} €/mois</p>
        <table class="projection-table"><tbody>
{chr(10).join(rows)}
        </tbody></table>
      </div>"""

    cartes = [
        compte(BASE, "base", "Base — loyers reconstruits 1 230 €/mois (380 + 550 + 300)"),
        compte(BEST, "optimiste", "Optimiste — loyers 1 480 €/mois"),
        compte(WORST, "pessimiste", "Pessimiste — loyers 810 €/mois"),
    ]

    # Sensibilite du plafond aux seuls loyers (charges du scenario de base)
    sens_rows = []
    for loy, lab in ((900.0, "hypothèse basse"), (1100.0, "local en rotation"),
                     (1230.0, "scénario de base"), (1400.0, "hypothèse haute")):
        d = calc(loy, 8.0, 5.0, 900.0, 400.0, 200.0)
        sens_rows.append(
            f'        <tr><td>{eur(loy)} €/mois</td><td>{lab}</td>'
            f'<td class="num">{eur(d["ebe"])} €</td><td class="num">{fr(d["rdt_av"])} %</td>'
            f'<td class="num">{eur(d["cap5"])} €</td>'
            f'<td class="num">{eur(d["cap5"] - PRIX)} €</td></tr>')
    sens_html = "\n".join(sens_rows)

    # ------------------------------------------------------------------
    # Cash-flow apres credit (doctrine du parc)
    # ------------------------------------------------------------------
    MENS_BASE = mensualite(CAPITAL)
    CF_BASE = cashflow_mensuel(BASE['ebe'], CAPITAL)
    CF_BASE_AN = CF_BASE * 12.0
    CF_BEST = cashflow_mensuel(BEST['ebe'], CAPITAL)
    CF_WORST = cashflow_mensuel(WORST['ebe'], CAPITAL)
    CF_VACANT = cashflow_mensuel(VACANT['ebe'], CAPITAL)
    CALC = {}
    for cle, p_ in (('offre', 130000.0), ('affiche', PRIX), ('plafond', 140000.0)):
        cap_ = p_ * (1 - APPORT_PCT)
        cf_ = cashflow_mensuel(BASE['ebe'], cap_)
        CALC[cle] = (p_, cap_, cf_, cf_ * 12.0)

    def cf_carte(d, titre, sous):
        return f"""      <div class="projection-card scenario-{titre}">
        <h3>{sous}</h3>
        <p class="scenario-subtitle">Prêt {eur(CAPITAL)} € sur 15 ans — apport 10 %</p>
        <table class="projection-table"><tbody>
            <tr><td>Loyers bruts mensuels</td><td class="num">{eur(d['brut'] / 12)} €</td></tr>
            <tr><td>Net d'exploitation mensuel (EBE)</td><td class="num">{eur(d['ebe_mois'])} €</td></tr>
            <tr><td>Mensualité de crédit (assurance incluse)</td><td class="num">-{eur(MENS_BASE)} €</td></tr>
            <tr class="highlight"><td>Cash-flow mensuel</td><td class="num">{eur(d['ebe'] / 12 - MENS_BASE)} €</td></tr>
            <tr><td>Cash-flow annuel</td><td class="num">{eur((d['ebe'] / 12 - MENS_BASE) * 12)} €</td></tr>
        </tbody></table>
      </div>"""

    cf_cartes = [
        cf_carte(BASE, "base", "Base — loyers 1 230 €/mois"),
        cf_carte(BEST, "optimiste", "Optimiste — loyers 1 480 €/mois"),
        cf_carte(WORST, "pessimiste", "Pessimiste — loyers 810 €/mois"),
    ]

    cf_prix_rows = []
    for cle, lab in (('offre', "130 000 € — notre offre"),
                     ('affiche', "154 400 € — prix affiché"),
                     ('plafond', "140 000 € — plafond de négociation")):
        p_, cap_, cf_, cf_an = CALC[cle]
        cf_prix_rows.append(
            f'        <tr><td>{lab}</td><td class="num">{eur(cap_)} €</td>'
            f'<td class="num">{eur(mensualite(cap_))} €</td>'
            f'<td class="num">{eur(cf_)} €/mois</td><td class="num">{eur(cf_an)} €/an</td>'
            f'<td class="num">{eur(loyer_cashflow_nul(cap_))} €/mois</td></tr>')
    cf_prix_html = "\n".join(cf_prix_rows)

    cf_besoins_rows = [
        ("Loyers mensuels pour un cash-flow nul au prix affiché",
         f"{eur(loyer_cashflow_nul(CAPITAL))} €/mois",
         f"contre {eur(BASE['loyer'])} €/mois retenus, soit "
         f"+{fr(loyer_cashflow_nul(CAPITAL) / BASE['loyer'] * 100.0 - 100.0, 0)} %"),
        ("Prix d'achat à cash-flow nul, 10 % d'apport, loyers de 1 230 €/mois",
         f"{eur(prix_cashflow_nul(BASE['ebe']))} €",
         f"{fr(prix_cashflow_nul(BASE['ebe']) / PRIX * 100.0 - 100.0, 1)} % sous le prix affiché"),
        ("Prix d'achat à cash-flow nul, 10 % d'apport, loyers de 1 480 €/mois",
         f"{eur(prix_cashflow_nul(BEST['ebe']))} €",
         "charges du scénario de base, loyers de l'hypothèse favorable"),
        ("Prix d'achat à cash-flow nul si le local reste vide",
         f"{eur(prix_cashflow_nul(VACANT['ebe']))} €",
         f"{fr(prix_cashflow_nul(VACANT['ebe']) / PRIX * 100.0 - 100.0, 1)} % sous le prix "
         f"affiché — hors doctrine"),
        ("Apport pour un cash-flow nul au prix affiché",
         f"{eur(apport_cashflow_nul(PRIX, BASE['ebe']))} €",
         f"{fr(apport_cashflow_nul(PRIX, BASE['ebe']) / PRIX * 100.0, 0)} % du prix"),
        ("Apport pour un cash-flow nul au prix affiché, local vide",
         f"{eur(apport_cashflow_nul(PRIX, VACANT['ebe']))} €",
         f"{fr(apport_cashflow_nul(PRIX, VACANT['ebe']) / PRIX * 100.0, 0)} % du prix"),
        ("Apport pour un cash-flow nul à 130 000 €",
         f"{eur(apport_cashflow_nul(130000.0, BASE['ebe']))} €",
         f"{fr(apport_cashflow_nul(130000.0, BASE['ebe']) / 130000.0 * 100.0, 0)} % du prix "
         f"— l'offre équilibre la trésorerie à apport quasi nul"),
        ("Apport pour un cash-flow nul à 140 000 €",
         f"{eur(apport_cashflow_nul(140000.0, BASE['ebe']))} €",
         f"{fr(apport_cashflow_nul(140000.0, BASE['ebe']) / 140000.0 * 100.0, 0)} % du prix"),
        ("Durée 20 ans",
         f"{eur(mensualite_actuarielle(CAPITAL, 20))} €/mois",
         f"cash-flow {eur(BASE['ebe'] / 12 - mensualite_actuarielle(CAPITAL, 20))} €/mois"),
        ("Durée 25 ans",
         f"{eur(mensualite_actuarielle(CAPITAL, 25))} €/mois",
         f"cash-flow {eur(BASE['ebe'] / 12 - mensualite_actuarielle(CAPITAL, 25))} €/mois"),
    ]
    cf_besoins_html = "\n".join(
        f'        <tr><td>{a}</td><td class="num">{b}</td><td>{c}</td></tr>'
        for a, b, c in cf_besoins_rows)

    cf_section = f"""  <section class="financial-projections">
    <h2>Cash-flow après crédit — service de la dette, apport et durée</h2>
    <p class="attractiveness-intro"><strong>Hypothèses de crédit (doctrine du parc) :</strong> apport 10 %, frais de notaire assumés à part, prêt de {eur(CAPITAL)} € sur 15 ans à 3,7 %, assurance emprunteur 0,34 % du capital. Mensualité <strong>{eur(MENS_BASE)} €/mois</strong>, soit <strong>0,00753 € par euro emprunté</strong>. Comparée au net d'exploitation de {eur(BASE['ebe_mois'])} €/mois du scénario de base, cette mensualité ne peut pas être couverte : il manque <strong>{eur(abs(CF_BASE))} €/mois</strong>.</p>
    <div class="projections-grid">
{chr(10).join(cf_cartes)}
    </div>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Le dossier passe la grille de rendement, pas le critère de trésorerie.</strong> Au prix affiché et avec 10 % d'apport, il manque <strong>{eur(abs(CF_BASE))} €/mois</strong> ({eur(abs(CF_BASE_AN))} €/an) au bien pour payer sa mensualité. Le déficit ne disparaît que dans l'hypothèse favorable de loyers (+{eur(CF_BEST)} €/mois) ; il s'aggrave à {eur(CF_WORST)} €/mois dans l'hypothèse défavorable et reste à {eur(CF_VACANT)} €/mois si le local commercial ne trouve pas preneur. Le rendement net après IS ({fr(BASE['rdt_ap'])} % sur l'acte en main) reste supérieur au taux du crédit de 3,7 %, donc l'opération s'enrichit à terme — mais elle consomme {eur(abs(CF_BASE_AN * DUREE_ANS))} € de trésorerie sur quinze ans, et c'est la trésorerie qui décide d'un achat.</p>
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
      <p class="attractiveness-intro"><strong>Fiscalité année 1 — ici, l'amortissement ne suffit pas à effacer l'impôt.</strong> Intérêts d'emprunt {eur(INTERETS_AN1)} € ({eur(CAPITAL)} € à 3,7 %), dotation aux amortissements {eur(DOTATION_AN1)} € (bâti à 80 % sur 30 ans) : le résultat imposable de l'année 1 est <strong>positif, {eur(RESULTAT_AN1)} €</strong>, soit <strong>{eur(IS_AN1)} € d'IS à 15 %</strong>. C'est une différence avec les dossiers où la dotation crée un déficit : ici l'exploitation dégage assez pour être imposée dès la première année. Le moteur retient par ailleurs, pour les rendements nets publiés, la convention la plus prudente : IS de 15 % appliqué à l'EBE, soit <strong>{eur(IS_CONVENTION_EBE)} €/an</strong>, sans amortissement du bâti modélisé. Dans les deux lectures, l'impôt n'est pas le sujet du dossier — il ne représente que {fr(IS_CONVENTION_EBE / BASE['ebe'] * 100, 0)} % de l'EBE, et c'est la mensualité qui décide.</p>
      <p class="attractiveness-intro"><strong>Le service de la dette vaut {fr(12 * MENS_BASE / CAPITAL * 100, 1)} % du capital emprunté par an</strong> (intérêts, capital et assurance) alors que le bien rapporte <strong>{fr(BASE['ebe'] / CAPITAL * 100, 1)} % sur ce même capital</strong> : l'écart, c'est la mensualité que le bien ne couvre pas. Ce n'est pas un dossier mort — l'actif s'apprécie, la dette se rembourse et le rendement passe le seuil de 5 % —, mais c'est un dossier qui demande {eur(abs(CF_BASE_AN * DUREE_ANS))} € de trésorerie sur quinze ans, ou un apport de {fr(apport_cashflow_nul(PRIX, BASE['ebe']) / PRIX * 100.0, 0)} % au lieu de 10 %, ou un prix de {eur(prix_cashflow_nul(BASE['ebe']))} € au lieu de {eur(PRIX)} €. Trois réponses possibles, aucune gratuite. Au-delà de 30 000 € d'apport, le dossier sort de la doctrine du parc.</p>
    </div>
  </section>"""

    # ------------------------------------------------------------------
    # Variante local vacant, marche DVF et renvois aux analyses Brignoles
    # ------------------------------------------------------------------
    variante_section = f"""  <section class="financial-projections">
    <h2>Variante publiée — le local commercial reste vide</h2>
    <p class="attractiveness-intro">C'est la seule vraie inconnue du dossier : l'annonce ne mentionne <strong>aucun preneur, aucun bail et aucun loyer</strong> pour le local de {eur(LOCAL)} m² du rez-de-chaussée, qui représente {fr(LOCAL / SURF_LOTS_BATIS * 100, 0)} % de la surface bâtie. La variante ci-dessous le compte <strong>vacant toute l'année</strong> : seuls le studio (380 €) et le duplex (550 €) produisent un loyer, soit <strong>930 €/mois</strong>, avec une vacance ramenée à 6 % sur les deux logements — un local structurellement vide n'est pas une provision statistique, c'est un revenu absent, et l'additionner au taux de vacance compterait deux fois la même perte.</p>
    <table class="projection-table compare">
      <thead><tr><th>Indicateur</th><th class="num">Scénario de base — 1 230 €/mois</th><th class="num">Local vacant — 930 €/mois</th><th class="num">Écart</th></tr></thead>
      <tbody>
        <tr><td>Loyers bruts annuels</td><td class="num">{eur(BASE['brut'])} €</td><td class="num">{eur(VACANT['brut'])} €</td><td class="num">{eur(VACANT['brut'] - BASE['brut'])} €</td></tr>
        <tr><td>Excédent brut d'exploitation</td><td class="num">{eur(BASE['ebe'])} €</td><td class="num">{eur(VACANT['ebe'])} €</td><td class="num">{eur(VACANT['ebe'] - BASE['ebe'])} €</td></tr>
        <tr><td>EBE mensuel</td><td class="num">{eur(BASE['ebe_mois'])} €/mois</td><td class="num">{eur(VACANT['ebe_mois'])} €/mois</td><td class="num">{eur(VACANT['ebe_mois'] - BASE['ebe_mois'])} €/mois</td></tr>
        <tr><td>Rendement net avant IS (acte en main)</td><td class="num">{fr(BASE['rdt_av'])} %</td><td class="num">{fr(VACANT['rdt_av'])} %</td><td class="num">{fr(VACANT['rdt_av'] - BASE['rdt_av'])} pt</td></tr>
        <tr><td>Rendement net après IS (acte en main)</td><td class="num">{fr(BASE['rdt_ap'])} %</td><td class="num">{fr(VACANT['rdt_ap'])} %</td><td class="num">{fr(VACANT['rdt_ap'] - BASE['rdt_ap'])} pt</td></tr>
        <tr class="highlight"><td>Prix d'achat tenant 5 % net avant IS</td><td class="num">{eur(BASE['cap5'])} €</td><td class="num">{eur(VACANT['cap5'])} €</td><td class="num">{eur(VACANT['cap5'] - BASE['cap5'])} €</td></tr>
        <tr><td>Écart au prix affiché ({eur(PRIX)} €)</td><td class="num">+{eur(BASE['cap5'] - PRIX)} €</td><td class="num">{eur(VACANT['cap5'] - PRIX)} €</td><td class="num">{eur(VACANT['cap5'] - BASE['cap5'])} €</td></tr>
        <tr class="highlight"><td>Cash-flow mensuel après crédit</td><td class="num">{eur(CF_BASE)} €/mois</td><td class="num">{eur(CF_VACANT)} €/mois</td><td class="num">{eur(CF_VACANT - CF_BASE)} €/mois</td></tr>
        <tr><td>Prix d'achat à cash-flow nul</td><td class="num">{eur(prix_cashflow_nul(BASE['ebe']))} €</td><td class="num">{eur(prix_cashflow_nul(VACANT['ebe']))} €</td><td class="num">{eur(prix_cashflow_nul(VACANT['ebe']) - prix_cashflow_nul(BASE['ebe']))} €</td></tr>
        <tr><td>Apport pour un cash-flow nul au prix affiché</td><td class="num">{eur(apport_cashflow_nul(PRIX, BASE['ebe']))} €</td><td class="num">{eur(apport_cashflow_nul(PRIX, VACANT['ebe']))} €</td><td class="num">{eur(apport_cashflow_nul(PRIX, VACANT['ebe']) - apport_cashflow_nul(PRIX, BASE['ebe']))} €</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Le local fait basculer le dossier.</strong> Sans lui, le plafond d'achat tenant 5 % net avant IS tombe à <strong>{eur(VACANT['cap5'])} €</strong>, soit <strong>{fr((PRIX - VACANT['cap5']) / PRIX * 100.0, 1)} % sous le prix affiché</strong>, et il faudrait un apport de {eur(apport_cashflow_nul(PRIX, VACANT['ebe']))} € ({fr(apport_cashflow_nul(PRIX, VACANT['ebe']) / PRIX * 100.0, 0)} % du prix) pour équilibrer la trésorerie — hors doctrine. Autrement dit : acheter ce dossier sans preuve de l'occupation du local, c'est acheter un rendement de {fr(VACANT['rdt_av'])} % au prix d'un rendement de {fr(BASE['rdt_av'])} %. <strong>Aucun engagement sans le bail du local ou, à défaut, une décote de 20 000 € qui paie sa vacance.</strong></p>
    </div>
  </section>"""

    marche_section = f"""  <section class="financial-projections">
    <h2>Marché local — DVF 2025 réelle de la commune et fiche de référence</h2>
    <p class="attractiveness-intro">Les {DVF_VENTES} mutations de nature « Vente » enregistrées en 2025 à Brignoles donnent un marché résidentiel liquide et un marché d'immeuble de rapport beaucoup plus étroit. Méthode : valeur foncière de la mutation divisée par la somme des surfaces bâties de la mutation, surfaces supérieures à 5 m² et valeurs supérieures à 5 000 €.</p>
    <table class="projection-table compare">
      <thead><tr><th>Segment DVF 2025 — Brignoles (83023)</th><th class="num">Mutations</th><th class="num">Médiane €/m²</th><th>Lecture</th></tr></thead>
      <tbody>
        <tr><td>Appartements, toutes surfaces</td><td class="num">{DVF_APP_N}</td><td class="num">{eur(DVF_APP_MED)} €</td><td>premier quartile {eur(DVF_APP_Q1)}, troisième {eur(DVF_APP_Q3)}</td></tr>
        <tr><td>Appartements de moins de 30 m²</td><td class="num">{DVF_APP_PETIT_N}</td><td class="num">{eur(DVF_APP_PETIT_MED)} €</td><td>tranche du studio de 20 m² — échantillon étroit</td></tr>
        <tr><td>Appartements de 30 à 60 m²</td><td class="num">{DVF_APP_3060_N}</td><td class="num">{eur(DVF_APP_3060_MED)} €</td><td>tranche du duplex de 47 m²</td></tr>
        <tr><td>Appartements de 60 m² et plus</td><td class="num">{DVF_APP_60P_N}</td><td class="num">{eur(DVF_APP_60P_MED)} €</td><td>le prix au m² décroît avec la surface</td></tr>
        <tr><td>Maisons</td><td class="num">{DVF_MAI_N}</td><td class="num">{eur(DVF_MAI_MED)} €</td><td>autre produit, cité pour situer le marché</td></tr>
        <tr class="highlight"><td>Immeubles de rapport — deux logements et plus</td><td class="num">{DVF_IMB_N}</td><td class="num">{eur(DVF_IMB_MED)} €</td><td>de {DVF_IMB_MIN} à {eur(DVF_IMB_MAX)} €/m² — c'est le produit comparable</td></tr>
        <tr><td>Immeubles mêlant logement et local commercial</td><td class="num">{DVF_MIXTE_N}</td><td class="num">—</td><td>de {DVF_MIXTE_MIN} à {eur(DVF_MIXTE_MAX)} €/m² : marché très étroit</td></tr>
      </tbody>
    </table>
    <table class="projection-table compare">
      <thead><tr><th>Transaction comparable</th><th class="num">Surface</th><th class="num">Prix</th><th class="num">€/m²</th></tr></thead>
      <tbody>
        <tr><td>{DVF_CMP1['voie']}, {DVF_CMP1['date']} — {DVF_CMP1['lots']} lignes (deux appartements et un local commercial)</td><td class="num">{eur(DVF_CMP1['surf'])} m²</td><td class="num">{eur(DVF_CMP1['prix'])} €</td><td class="num">{eur(DVF_CMP1['m2'])} €</td></tr>
        <tr><td>{DVF_CMP2['voie']}, {DVF_CMP2['date']} — {DVF_CMP2['lots']} lignes (un appartement, un local et une dépendance)</td><td class="num">{eur(DVF_CMP2['surf'])} m²</td><td class="num">{eur(DVF_CMP2['prix'])} €</td><td class="num">{eur(DVF_CMP2['m2'])} €</td></tr>
        <tr class="highlight"><td><strong>Le bien analysé</strong>, au prix affiché, sur les {eur(SURF_LOTS_BATIS)} m² de lots bâtis</td><td class="num">{eur(SURF_LOTS_BATIS)} m²</td><td class="num">{eur(PRIX)} €</td><td class="num">{eur(PRIX / SURF_LOTS_BATIS)} €</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Ce que disent les chiffres.</strong> À {eur(PRIX / SURF_LOTS_BATIS)} €/m² sur les lots bâtis, le prix affiché se situe au-dessus du haut de la fourchette observée sur le produit comparable ({eur(DVF_IMB_MED)} €/m² de médiane sur {DVF_IMB_N} mutations, jusqu'à {eur(DVF_IMB_MAX)} €/m²) et très au-dessus de la transaction mixte la plus proche ({eur(DVF_CMP1['m2'])} €/m² rue d'Entraigues). Sur la base retenue de {eur(SURF_HAB)} m² (les deux logements, hors cave et hors local), il ressort à {eur(PRIX / SURF_HAB)} €/m², à comparer aux {eur(DVF_APP_MED)} €/m² de médiane communale toutes surfaces — mais cette comparaison est trop favorable, parce qu'un immeuble entier avec local commercial et cave se traite avec une décote de rendement, pas au prix de l'appartement moyen. La valeur de marché retenue ici est donc <strong>{eur(VALEUR_RETENUE)} €</strong>, fourchette {eur(VALEUR_BASSE)} à {eur(VALEUR_HAUTE)} € : elle est ancrée sur le produit réellement comparable, pas sur la moyenne communale.</p>
      <p class="attractiveness-intro"><strong>Référence interne de la commune</strong> (fiche <em>Marchés locaux</em> mise à jour le 21/09/2026) : marché {eur(MARCHE_M2_COMMUNE)} €/m², loyer de référence {fr(LOYER_REF_M2, 1)} €/m²/mois sur un lot type de 60 m², plafonds d'achat par m² habitable frais compris de {eur(PLAF_PATRIMONIAL[0])} € (6,5 % net d'IS), {eur(PLAF_PATRIMONIAL[1])} € (7,0 %) et {eur(PLAF_PATRIMONIAL[2])} € (8,0 %) en vision patrimoniale, et {eur(PLAF_MDB[0])} / {eur(PLAF_MDB[1])} / {eur(PLAF_MDB[2])} €/m² en vision marchand de biens. La fiche conclut qu'aucune des douze villes du secteur n'offre le seuil patrimonial au prix de marché et que c'est la lecture marchand de biens qui est praticable : ce dossier n'échappe pas à la règle, puisque son prix d'entrée ({eur(ACTE_EN_MAIN)} € d'acte en main) est très au-dessus de tous ces plafonds.</p>
      <p class="attractiveness-intro"><strong>À lire aussi dans le dépôt</strong> — <a href="../2026-09-18-immeuble-rapport-brignoles-centre/index.html">Immeuble de rapport Brignoles centre (18/09/2026)</a>, <a href="../2026-09-20-immeuble-rapport-brignoles-centre-ancien/index.html">Immeuble de rapport Brignoles centre ancien, 3 T3, Site Patrimonial Remarquable (20/09/2026)</a> et la <a href="../marches-locaux/index.html">fiche de référence des marchés locaux</a> (mise à jour du 21/09/2026), qui donne pour Brignoles les plafonds d'achat utilisés ici. Les deux dossiers précédents portaient sur des immeubles de centre ancien sans local commercial ou avec réhabilitation lourde ; celui-ci est le seul du lot dont le rendement en l'état passe le seuil de 5 % net avant IS — et le seul dont la décision tient à un local commercial dont personne ne connaît l'occupation.</p>
    </div>
  </section>"""

    lecture = (
        f"C'est le seul dossier de Brignoles qui passe la grille de rendement, et il échoue à "
        f"celle de la trésorerie. L'immeuble fait {eur(SURF_LOTS_BATIS)} m² de lots bâtis pour "
        f"{eur(PRIX)} € : au prix affiché, {eur(PRIX / SURF_LOTS_BATIS)} €/m² sur les lots bâtis, "
        f"au-dessus du haut de la fourchette observée sur le produit comparable — les immeubles de "
        f"rapport de la commune se traitent à {eur(DVF_IMB_MED)} €/m² de médiane "
        f"({DVF_IMB_N} mutations de deux logements et plus en 2025) — et {eur(PRIX / SURF_HAB)} €/m² "
        f"sur la base de {eur(SURF_HAB)} m² retenus pour les deux logements, hors cave et hors local. "
        f"Avec des loyers reconstruits à partir du marché relevé le 25/09/2026 — studio 380 €, "
        f"duplex 550 €, local commercial 300 €, soit {eur(BASE['loyer'])} €/mois — l'excédent brut "
        f"d'exploitation ressort à {eur(BASE['ebe'])} €, soit {fr(BASE['rdt_av'])} % net avant IS "
        f"sur l'acte en main : le seuil de 5 % de la doctrine est tenu, de "
        f"{fr((BASE['rdt_av'] - 5.0) * 100, 0)} points de base. Le rendement est donc là. Le "
        f"problème est ailleurs, et il est dans le compte de trésorerie : à 10 % d'apport, la "
        f"mensualité est de {eur(MENS_BASE)} €/mois pour "
        f"{eur(BASE['ebe_mois'])} €/mois d'exploitation, soit un cash-flow de "
        f"{eur(cashflow_mensuel(BASE['ebe'], CAPITAL))} €/mois. Et surtout, tout le dossier tient "
        f"à un lot dont l'annonce ne dit rien : le local commercial de {eur(LOCAL)} m² du "
        f"rez-de-chaussée, {fr(LOCAL / SURF_LOTS_BATIS * 100, 0)} % de la surface bâtie, sans "
        f"preneur, sans bail et sans loyer. S'il reste vide, le dossier tombe à "
        f"{fr(VACANT['rdt_av'])} % net avant IS et le plafond d'achat passe sous le prix affiché. "
        f"Le prix n'est donc pas le problème principal — à {eur(BASE['cap5'])} € le rendement "
        f"tiendrait encore —, mais la preuve de l'occupation du local l'est entièrement."
    )

    gen.LECTURE[SLUG] = lecture
    gen.RECS[SLUG] = rec_
    gen.CONF[SLUG] = dict(
        titre_court="Immeuble de rapport, centre vieille ville — Brignoles (83170)",
        adresse=(
            "Centre vieille ville, Brignoles (83170) — immeuble de rapport de trois lots : local "
            "commercial de 20 m² et cave de 17 m² au rez-de-chaussée, studio de 20 m² au 1er, "
            "duplex T2 de 47 m² au 2e — adresse exacte non communiquée"
        ),
        date_fr=DATE_FR,
        source=(
            "SeLoger — annonce 26UC8HRN61QJ (SAFTI, Maude MERRY conseiller indépendant, EI, "
            "RCS Draguignan 522063833, référence agence 1699409)"
        ),
        url=URL,
        badge="Investissement locatif",
        strategie=(
            "Conservation en location longue durée des trois lots — studio, duplex T2 et local "
            "commercial — avec la variante « local vacant » chiffrée et publiée"
        ),
        fiscal_note=(
            "SCI à l'IS : IS de 15 % appliqué à l'EBE, sans amortissement du bâti modélisé "
            "(convention prudente) — seuil de décision : 5 % net avant IS sur l'acte en main"
        ),
        lat="43.4058", lon="6.0617",
        quartier=(
            "Brignoles (83170) — centre vieille ville, 17 000 habitants, autoroute A8 à "
            "10 minutes, Saint-Maximin à 30 minutes, Toulon à 1 heure"
        ),
        intro_attr=(
            f"Brignoles est la sous-préfecture du centre Var : <strong>17 000 habitants</strong>, "
            f"rue commerçante de centre ancien, marché, écoles, collège et lycée, zone d'activité "
            f"et entrée de l'autoroute A8 à dix minutes. Le marché est documenté : "
            f"<strong>{DVF_VENTES} mutations de nature « Vente » en 2025</strong> selon la base "
            f"DVF, dont <strong>{DVF_APP_N} ventes d'appartements</strong> à une médiane de "
            f"<strong>{eur(DVF_APP_MED)} €/m²</strong> (premier quartile {eur(DVF_APP_Q1)}, "
            f"troisième {eur(DVF_APP_Q3)}) et <strong>{DVF_MAI_N} ventes de maisons</strong> à "
            f"<strong>{eur(DVF_MAI_MED)} €/m²</strong>. La tranche 30-60 m², où tombe le duplex "
            f"de 47 m², affiche <strong>{eur(DVF_APP_3060_MED)} €/m² sur {DVF_APP_3060_N} "
            f"ventes</strong> ; la tranche des moins de 30 m², où tombe le studio de 20 m², "
            f"<strong>{eur(DVF_APP_PETIT_MED)} €/m² sur {DVF_APP_PETIT_N} ventes seulement</strong>. "
            f"Côté locatif, les annonces relevées sur place le 25/09/2026 donnent une pièce de "
            f"36 m² en centre vieille ville à 450 € (12,5 €/m²), des 2 pièces à 680 €, un 3 pièces "
            f"meublé de 50 m² à 800 € et une maison meublée de 100 m² à 1 450 € ; le loyer de "
            f"référence de la commune est de 11,0 €/m²/mois sur un lot type de 60 m² (fiche de "
            f"référence du 21/09/2026). C'est un marché de locataires à l'année, avec de l'offre — "
            f"et, pour l'immeuble de rapport, un marché d'acquéreurs bien plus étroit : "
            f"{DVF_IMB_N} mutations de deux logements et plus dans l'année."
        ),
        profil=(
            "un investisseur de rendement qui accepte un cash-flow légèrement négatif au départ "
            "contre un actif en centre-ville, déjà louable sans travaux annoncés (DPE D, aucune "
            "échéance réglementaire avant 2034) : un local commercial de 20 m² au rez-de-chaussée, "
            "un studio et un duplex en étages, dans un immeuble de 1940 en monopropriété. Ce n'est "
            "pas un dossier de plus-value : le prix affiché est au-dessus de la valeur de marché "
            "du produit comparable. C'est un dossier de loyer, et il ne vaut que par deux choses "
            "que l'annonce ne donne pas — le preneur du local et le montant des loyers"
        ),
        concl_attr=(
            f"Adéquation moyenne (6,5/10). L'emplacement, la structure et l'état déclaré sont de "
            f"vrais atouts : plein centre de la vieille ville, trois lots louables sans travaux "
            f"annoncés, DPE D sans échéance avant 2034, un local commercial qui apporte une source "
            f"de revenu que n'ont pas les deux autres dossiers Brignoles du dépôt. Deux éléments "
            f"plombent le score. D'abord le prix : {eur(PRIX / SURF_LOTS_BATIS)} €/m² sur les lots "
            f"bâtis contre {eur(DVF_IMB_MED)} €/m² de médiane sur les {DVF_IMB_N} immeubles de "
            f"rapport effectivement vendus en 2025 — le prix affiché est au-dessus du haut de la "
            f"fourchette observée. Ensuite et surtout l'inconnue du local commercial : il pèse "
            f"{fr(LOCAL / SURF_LOTS_BATIS * 100, 0)} % de la surface bâtie, aucun preneur n'est "
            f"mentionné, et c'est lui qui fait passer le rendement de {fr(BASE['rdt_av'])} % à "
            f"{fr(VACANT['rdt_av'])} % selon qu'il est loué ou non"
        ),
        intro_strat=(
            "Cinq lectures ont été testées : la conservation en location longue durée dans trois "
            "hypothèses de loyers (base à 1 230 €/mois, optimiste à 1 480 €, pessimiste à 810 €), "
            "la variante où le local commercial reste vacant toute l'année (930 €/mois) et "
            "l'achat-rénovation-revente. C'est la première qui porte le dossier, c'est la "
            "quatrième qui le fragilise et c'est la cinquième qui le condamne : il n'y a aucune "
            "décote d'entrée à capter."
        ),
        rationale=(
            f"Le scénario de référence : loyers reconstruits à partir du marché relevé sur place "
            f"le 25/09/2026 — studio 380 €, duplex T2 550 € et local commercial 300 €, soit "
            f"{eur(BASE['loyer'])} €/mois —, vacance 8 %, gestion locative 5 %, taxe foncière "
            f"estimée 900 € (avis non communiqué), charges d'immeuble 400 €, assurance 150 €, "
            f"provision travaux 200 € et comptabilité 500 €. L'excédent brut d'exploitation "
            f"ressort à <strong>{eur(BASE['ebe'])} €</strong> ({eur(BASE['ebe_mois'])} €/mois) et "
            f"le rendement net avant IS sur l'acte en main de <strong>{fr(BASE['rdt_av'])} %</strong> "
            f": la doctrine du parc, 5 % net avant IS, est tenue — mais de "
            f"{fr((BASE['rdt_av'] - 5.0) * 100, 0)} points de base seulement, et le rendement "
            f"après IS tombe à {fr(BASE['rdt_ap'])} %.<br><br>"
            f"Toute la marge du dossier tient dans deux lignes qui ne sont pas dans l'annonce. "
            f"Les loyers d'abord : à <strong>810 €/mois</strong> — un bail sous-évalué, une "
            f"vacance de 15 %, une taxe foncière à 1 100 € et une provision de 400 € — l'EBE tombe "
            f"à {eur(WORST['ebe'])} €, le rendement à <strong>{fr(WORST['rdt_av'])} %</strong> et "
            f"le prix qui tiendrait notre seuil à <strong>{eur(WORST['cap5'])} €</strong>. À "
            f"<strong>1 480 €/mois</strong>, l'EBE monte à {eur(BEST['ebe'])} €, le rendement à "
            f"<strong>{fr(BEST['rdt_av'])} %</strong> et le plafond à "
            f"<strong>{eur(BEST['cap5'])} €</strong>. Le local commercial ensuite, et c'est le "
            f"poste décisif : sans preneur, avec seulement le studio et le duplex, les loyers "
            f"tombent à 930 €/mois, l'EBE à {eur(VACANT['ebe'])} € et le plafond d'achat à "
            f"<strong>{eur(VACANT['cap5'])} €</strong>, soit "
            f"{fr((PRIX - VACANT['cap5']) / PRIX * 100.0, 1)} % sous le prix affiché. Entre "
            f"l'hypothèse basse et l'hypothèse haute, {eur(BEST['cap5'] - WORST['cap5'])} € de "
            f"capacité de prix : c'est le montant exact de l'inconnue que porte cette annonce.<br><br>"
            f"Ce que le dossier n'est pas, en revanche : une opération de revente. Avec un prix de "
            f"revient de {eur(ACTE_EN_MAIN)} € d'acte en main pour une valeur de marché retenue de "
            f"{eur(VALEUR_RETENUE)} €, l'achat-rénovation-revente affiche une marge négative de "
            f"{eur(ACTE_EN_MAIN - VALEUR_RETENUE)} € avant même les frais de revente — et le "
            f"marché de l'immeuble de rapport de la commune ne compte que {DVF_IMB_N} mutations "
            f"dans l'année. C'est un actif de rendement pur, à son prix ou au-dessus de son prix."
        ),
        identite=[
            ("Adresse", "Centre vieille ville, Brignoles (83170) — adresse exacte non "
                        "communiquée par l'agence"),
            ("Vendeur / intermédiaire", "SAFTI — Maude MERRY, conseiller indépendant (EI, RCS "
                                        "Draguignan 522063833) — annonce SeLoger 26UC8HRN61QJ, "
                                        "référence agence 1699409"),
            ("Composition", "Trois lots bâtis et une cave : local commercial de 20 m² au "
                            "rez-de-chaussée (une pièce avec salle d'eau et WC, annoncé "
                            "« peut être transformé en un studio ») et cave de 17 m² avec accès "
                            "par escalier intérieur au local ; studio de 20 m² au 1er étage ; "
                            "duplex T2 de 47 m² au 2e étage (deux chambres d'environ 9,50 et "
                            "11 m², dont une avec fenêtre sur couloir)"),
            ("Statut", "Aucune copropriété mentionnée : immeuble présumé en <strong>mono"
                       "propriété</strong>. Aucune charge votée, aucun budget prévisionnel, "
                       "aucune mutualisation des travaux de structure, de couverture et de "
                       "façade — entièrement à la charge de l'acquéreur. À confirmer"),
            ("Surfaces", f"<strong>90 m² annoncés</strong> ({eur(PRIX / SURF_ANNONCEE)} €/m²), "
                         f"comprenant la cave et le local. <strong>{eur(SURF_LOTS_BATIS)} m² de "
                         f"lots bâtis</strong> (20 + 20 + 47) plus la cave de 17 m², et "
                         f"<strong>{eur(SURF_HAB)} m² retenus</strong> pour les deux logements, "
                         f"hors cave et hors local, soit "
                         f"<strong>{eur(PRIX / SURF_HAB)} €/m²</strong>. Aucun plan, aucune "
                         f"surface Carrez par lot"),
            ("Occupation", "L'annonce ne mentionne <strong>ni locataire, ni bail, ni loyer</strong> "
                           "pour aucun des trois lots, et affirme « idéal investissement locatif » "
                           "sans un seul chiffre : l'occupation est l'inconnue centrale du dossier, "
                           "et elle porte d'abord sur le local commercial (23 % de la surface "
                           "bâtie)"),
            ("DPE / GES", "DPE D / GES B — facture énergétique annoncée 810 à 1 140 €/an. Pas "
                          "d'échéance réglementaire de location à l'horizon du plan : aucun "
                          "passif énergétique à porter. Date du diagnostic non communiquée, "
                          "diagnostics électricité, plomb et amiante non joints"),
            ("Travaux", "Aucun travaux annoncé, <strong>aucun devis et aucun diagnostic autre "
                        "que le DPE</strong> sur un immeuble de 1940 : couverture, charpente, "
                        "réseaux et humidité de la cave ne sont documentés par aucune pièce. Le "
                        "chiffrage retient 0 € de travaux à l'acquisition et une provision de "
                        "200 €/an en exploitation ; le risque est porté à la matrice, à lever par "
                        "une visite d'homme de l'art"),
            ("Prix affiché", f"<strong>154 400 €</strong>, honoraires à la charge du vendeur — "
                             f"{eur(PRIX / SURF_ANNONCEE)} €/m² sur les 90 m² annoncés, "
                             f"<strong>{eur(PRIX / SURF_LOTS_BATIS)} €/m² sur les "
                             f"{eur(SURF_LOTS_BATIS)} m² de lots bâtis</strong>, "
                             f"{eur(PRIX / SURF_HAB)} €/m² sur la base retenue de "
                             f"{eur(SURF_HAB)} m²"),
            ("Valeur de marché retenue", f"<strong>{eur(VALEUR_RETENUE)} €</strong> "
                                         f"({eur(SURF_LOTS_BATIS)} m² × {eur(DVF_IMB_MED)} €/m², "
                                         f"médiane DVF 2025 des {DVF_IMB_N} immeubles de rapport "
                                         f"de la commune), fourchette {eur(VALEUR_BASSE)} à "
                                         f"{eur(VALEUR_HAUTE)} € ancrée sur deux transactions "
                                         f"mixtes nommées du centre-ville "
                                         f"({eur(DVF_CMP1['m2'])} et {eur(DVF_CMP2['m2'])} €/m²)"),
            ("Loyers retenus", f"<strong>{eur(BASE['loyer'])} €/mois</strong> reconstruits : "
                               f"studio de 20 m² à 380 €, duplex T2 de 47 m² à 550 € et local "
                               f"commercial de 20 m² à 300 €. Aucun loyer communiqué par "
                               f"l'annonce — relevés du 25/09/2026 : 36 m² à 450 € (12,5 €/m²), "
                               f"2 pièces de 37 m² à 680 €, 3 pièces meublé de 50 m² à 800 €, "
                               f"maison meublée de 100 m² à 1 450 €, parking à 120 € ; loyer de "
                               f"référence communal 11,0 €/m²/mois sur 60 m²"),
            ("Charges annuelles", "Taxe foncière <strong>estimée 900 €</strong> (avis non "
                                  "communiqué, fourchette 700 à 1 100 €) + charges d'immeuble "
                                  "400 € (pas de copropriété) + PNO 150 € + gestion locative et "
                                  "provision travaux 938 € + comptabilité 500 €. Aucun poste "
                                  "laissé à zéro"),
            ("Fiscalité", f"SCI à l'IS. Calcul réel de l'année 1 : intérêts d'emprunt "
                          f"{eur(INTERETS_AN1)} € et dotation aux amortissements "
                          f"{eur(DOTATION_AN1)} € (bâti à 80 % sur 30 ans) déduits de l'EBE, "
                          f"soit un <strong>résultat imposable positif de "
                          f"{eur(RESULTAT_AN1)} € et un IS de {eur(IS_AN1)} €</strong> — "
                          f"l'amortissement ne suffit pas à effacer l'impôt sur ce dossier. "
                          f"Convention prudente retenue pour les rendements publiés : IS de 15 % "
                          f"appliqué à l'EBE (<strong>{eur(IS_CONVENTION_EBE)} €/an</strong>), "
                          f"sans amortissement du bâti modélisé. Le seuil de décision porte sur "
                          f"le rendement net avant IS"),
            ("Prix de revient", f"<strong>{eur(ACTE_EN_MAIN)} €</strong> acte en main = prix "
                                f"{eur(PRIX)} € + frais d'acquisition {eur(PRIX * NOTAIRE)} € "
                                f"(8 %), sans travaux (aucun travaux annoncé)"),
            ("Financement (doctrine du parc)", f"apport 10 %, prêt de {eur(CAPITAL)} € sur 15 ans "
                                               f"à 3,7 % et assurance emprunteur de 0,34 %, soit "
                                               f"une mensualité de {eur(MENS_BASE)} €/mois "
                                               f"(0,00753 € par euro emprunté). Cash-flow de "
                                               f"<strong>{eur(CF_BASE)} €/mois</strong> "
                                               f"({eur(CF_BASE_AN)} €/an) au prix affiché, "
                                               f"+{eur(CF_BEST)} €/mois en hypothèse favorable, "
                                               f"{eur(CF_WORST)} €/mois en hypothèse défavorable "
                                               f"et {eur(CF_VACANT)} €/mois si le local reste vide"),
        ],
        stance=(
            f"<strong>À négocier — offrir 130 000 €, plafond 140 000 €. Au-delà de ce plafond, le "
            f"dossier ne se finance plus : il faut un apport de "
            f"{eur(apport_cashflow_nul(PRIX, BASE['ebe']))} € pour équilibrer la trésorerie au "
            f"prix affiché, et {eur(apport_cashflow_nul(PRIX, VACANT['ebe']))} € si le local "
            f"commercial ne trouve pas preneur.</strong><br><br>"
            f"Le raisonnement tient en deux grilles, et le dossier en passe une sur deux. Sur la "
            f"grille de rendement, il est conforme : avec les loyers reconstruits à partir du "
            f"marché — {eur(BASE['loyer'])} €/mois — l'exploitation dégage {eur(BASE['ebe'])} € "
            f"d'EBE, soit {fr(BASE['rdt_av'])} % net avant IS sur l'acte en main, au-dessus du "
            f"seuil de 5 %, et {fr(BASE['rdt_ap'])} % après IS contre 3,7 % de taux d'intérêt : "
            f"l'opération s'enrichit. Sur la grille de trésorerie, il échoue : à 10 % d'apport, la "
            f"mensualité est de {eur(MENS_BASE)} €/mois pour {eur(BASE['ebe_mois'])} €/mois "
            f"d'exploitation, soit <strong>{eur(CF_BASE)} €/mois</strong> "
            f"({eur(CF_BASE_AN)} €/an). Pour équilibrer au prix affiché, il faudrait "
            f"<strong>{eur(loyer_cashflow_nul(CAPITAL))} €/mois de loyers</strong> — "
            f"{fr(loyer_cashflow_nul(CAPITAL) / BASE['loyer'] * 100.0 - 100.0, 0)} % de plus "
            f"que notre base —, ou un prix de {eur(prix_cashflow_nul(BASE['ebe']))} €, ou un "
            f"apport de {eur(apport_cashflow_nul(PRIX, BASE['ebe']))} € "
            f"({fr(apport_cashflow_nul(PRIX, BASE['ebe']) / PRIX * 100.0, 0)} % du prix). "
            f"Au-delà de 30 000 € d'apport, le dossier sort de la doctrine du parc.<br><br>"
            f"<strong>Ce que cela fixe comme cadre d'offre.</strong> À <strong>130 000 €</strong>, "
            f"le rendement monte à {fr(BASE['ebe'] / 130000.0 / 1.08 * 100.0)} % net avant IS et le "
            f"cash-flow revient à l'équilibre (+{eur(cashflow_mensuel(BASE['ebe'], 130000.0 * 0.9))} €/mois) "
            f"avec la mensualité de {eur(mensualite(130000.0 * 0.9))} €/mois : c'est le prix qui "
            f"tient les deux grilles à la fois. À <strong>140 000 €</strong> — notre plafond — le "
            f"rendement est de {fr(BASE['ebe'] / 140000.0 / 1.08 * 100.0)} % et le déficit mensuel "
            f"est ramené de {eur(abs(CF_BASE))} € à {eur(abs(cashflow_mensuel(BASE['ebe'], 140000.0 * 0.9)))} €. "
            f"Entre les deux, la négociation se joue sur un montant qui reste dans la doctrine du "
            f"parc. <strong>Trois pièces suspensives, non négociables :</strong> le bail du local "
            f"commercial ou, à défaut, une décote d'au moins 20 000 € qui paie sa vacance — c'est "
            f"la seule donnée qui décide, et s'il est libre depuis plus de six mois la réponse "
            f"change ; les loyers des deux logements avec leurs quittances ; l'avis de taxe "
            f"foncière et les diagnostics datés (électricité, plomb, amiante, état de la "
            f"couverture, de la charpente et de l'humidité de la cave), sur un immeuble de 1940 "
            f"dont l'acquéreur porte seul la structure.<br><br>"
            f"<strong>Ce qui reste bon dans ce dossier.</strong> C'est le seul des immeubles de "
            f"rapport Brignoles du dépôt dont le rendement en l'état passe le seuil de 5 % net "
            f"avant IS, sans travaux annoncés et sans passif énergétique (DPE D, aucune échéance "
            f"avant 2034). Il apporte une source de revenu que n'ont ni l'immeuble du 18/09/2026 "
            f"ni celui du 20/09/2026 : un local commercial de 20 m² en rez-de-chaussée de la "
            f"vieille ville. Mais un dossier qui passe le rendement sans passer la trésorerie ne "
            f"s'achète pas au prix affiché : il se négocie, et il ne se négocie pas en aveugle — "
            f"sans preuve des baux et de l'occupation du local, on ne s'engage pas."
        ),
        prix_plafond=(
            f"<strong>Trois ancres, et c'est la trésorerie qui commande.</strong> Sur le seul "
            f"critère de rendement, le prix qui tient 5 % net avant IS est de "
            f"{eur(BASE['cap5'])} € avec {eur(BASE['loyer'])} €/mois de loyers — un seuil, pas une "
            f"cible, et il est très au-dessus du prix affiché : la grille de rendement n'est donc "
            f"pas contraignante ici, ce qui est rare et ce qui explique la tentation. Sur le "
            f"critère de trésorerie, la contrainte est brutale : à 10 % d'apport, le prix qui "
            f"donne un cash-flow nul est de <strong>{eur(prix_cashflow_nul(BASE['ebe']))} €</strong> "
            f"— c'est le prix auquel le bien couvre sa mensualité de {eur(MENS_BASE)} €/mois — et "
            f"il tombe à <strong>{eur(prix_cashflow_nul(VACANT['ebe']))} €</strong> si le local "
            f"commercial reste vide toute l'année : {eur(prix_cashflow_nul(BASE['ebe']) - prix_cashflow_nul(VACANT['ebe']))} € "
            f"de capacité de prix, littéralement le prix du local. Sur le critère de valeur de "
            f"marché, enfin, la valeur retenue est de {eur(VALEUR_RETENUE)} € "
            f"({eur(SURF_LOTS_BATIS)} m² × {eur(DVF_IMB_MED)} €/m², médiane DVF 2025 des "
            f"immeubles de rapport de la commune) : un ratio coût/valeur de 0,95 plafonnerait le "
            f"prix à {eur(VALEUR_RETENUE * 0.95 / (1 + NOTAIRE))} €, et le prix affiché ressort à "
            f"un ratio de {fr(ACTE_EN_MAIN / VALEUR_RETENUE)}. C'est dire que le prix affiché "
            f"achète au-dessus de ce que le produit vaut sur son propre marché.<br><br>"
            f"<strong>Ce qu'on propose.</strong> Une offre à <strong>130 000 €</strong>, qui rend "
            f"les deux grilles conformes à la fois (rendement "
            f"{fr(BASE['ebe'] / 130000.0 / 1.08 * 100.0)} %, cash-flow à l'équilibre, apport "
            f"{eur(apport_cashflow_nul(130000.0, BASE['ebe']))} €), et un "
            f"<strong>plafond de 140 000 €</strong> au-delà duquel on passe. Ce plafond de "
            f"140 000 € n'est pas un confort : à ce prix, le rendement est de "
            f"{fr(BASE['ebe'] / 140000.0 / 1.08 * 100.0)} % net avant IS mais le cash-flow reste "
            f"négatif de {eur(abs(cashflow_mensuel(BASE['ebe'], 140000.0 * 0.9)))} €/mois, et il "
            f"faut {eur(apport_cashflow_nul(140000.0, BASE['ebe']))} € d'apport pour le ramener à "
            f"zéro — encore dans la doctrine, mais juste. Sensibilité du plafond de rendement aux "
            f"seuls loyers, charges de base inchangées : à 900 €/mois "
            f"{eur(calc(900.0, 8.0, 5.0, 900.0, 400.0, 200.0)['cap5'])} €, à 1 100 €/mois "
            f"{eur(calc(1100.0, 8.0, 5.0, 900.0, 400.0, 200.0)['cap5'])} €, à 1 230 €/mois "
            f"{eur(BASE['cap5'])} €, à 1 400 €/mois "
            f"{eur(calc(1400.0, 8.0, 5.0, 900.0, 400.0, 200.0)['cap5'])} €. Chaque tranche de "
            f"100 €/mois de loyer vaut environ 18 500 € de capacité de prix : c'est le taux de "
            f"change de cette négociation. Et si le local commercial reste vide, le plafond tombe "
            f"à {eur(VACANT['cap5'])} € et la réponse est non, sauf décote de 20 000 €."
        ),
        leviers=[
            "Le local commercial est l'argument central, et l'annonce le fournit elle-même : elle "
            "vend « idéal investissement locatif » sans donner un seul loyer, pour un lot qui pèse "
            "23 % de la surface bâtie. Demander le bail, le preneur, la durée et les quittances du "
            "local AVANT toute discussion de prix, et faire constater par écrit que le dossier "
            "n'est pas chiffrable sans eux",
            "Le prix au m² est le deuxième levier, mais il faut le poser sur la bonne base : "
            f"1 716 €/m² ne se compare à rien, puisque les 90 m² annoncés comprennent la cave. Sur "
            f"les 87 m² de lots bâtis, le prix affiché ressort à 1 775 €/m², au-dessus du haut de "
            f"la fourchette des immeubles de rapport réellement vendus dans la commune en 2025 "
            f"(médiane 1 410 €/m², 41 mutations), et au-dessus de la transaction mixte de la rue "
            f"Jules Ferry (1 767 €/m²). Deux pièces de DVF suffisent à le démontrer",
            "Le défaut de jour de la chambre du duplex (environ 9,50 m² avec fenêtre sur couloir) "
            "doit être qualifié avant l'offre : une pièce sans jour naturel sur l'extérieur n'est "
            "pas une chambre de plein droit, le lot ne se commercialise donc pas comme un T3 — et "
            "c'est un argument de baisse du loyer ou du prix, pas un détail de plan",
            "L'annonce se contredit elle-même sur la cave : le texte décrit 17 m² avec accès par "
            "escalier intérieur, la fiche « caractéristiques » indique « Pas de cave ». À faire "
            "lever par écrit par l'agence, avec la surface de chaque lot — c'est ce qui établit "
            "que rien du dossier n'a été vérifié avant publication",
            "Aucun diagnostic autre que le DPE n'est joint, sur un immeuble de 1940 en "
            "monopropriété où la couverture, la charpente et les réseaux sont à 100 % pour "
            "l'acquéreur : demander les diagnostics électricité, plomb et amiante, et faire "
            "visiter la couverture et la cave par un homme de l'art. Une toiture à reprendre coûte "
            "plusieurs années de loyer net",
            "La taxe foncière n'est pas communiquée : demander l'avis réel et la valeur locative "
            "cadastrale. L'écart entre 700 et 1 100 €/an vaut 200 €/an, soit plus de 40 % de la "
            "marge dont le dossier dispose au-dessus du seuil de 5 % — et l'avis, gratuit à "
            "demander, donne la seule surface opposable en l'absence de plan",
            "L'hypothèse de loyer du studio est la plus généreuse du modèle : 380 € pour 20 m² "
            "ressortent à 19 €/m²/mois quand l'annonce de 36 m² relevée le 25/09/2026 se loue "
            "450 €, soit 12,5 €/m². À faire confirmer par des annonces locatives comparables "
            "avant de considérer le rendement de base comme acquis",
            "L'absence de copropriété se retourne contre nous et doit se chiffrer : aucune "
            "mutualisation des travaux de structure, aucun budget prévisionnel, aucun "
            "copropriétaire avec qui partager une toiture ou une façade. C'est un argument de "
            "négociation légitime — et si une copropriété existe, exiger immédiatement le budget "
            "prévisionnel et les trois derniers procès-verbaux d'assemblée",
            "Le marché de revente est liquide (397 mutations en 2025) mais celui de l'immeuble de "
            "rapport ne l'est pas (41 mutations de deux logements et plus, 10 seulement mêlant "
            "logement et local commercial) : ne pas se laisser vendre un argument patrimonial à "
            f"ce prix d'entrée, où le ratio coût/valeur ressort à "
            f"{fr(ACTE_EN_MAIN / VALEUR_RETENUE)}. Cette sincérité est aussi ce qui rend crédible "
            f"la demande de baisse",
        ],
        meta=[
            f"<strong>Régime fiscal retenu :</strong> SCI à l'IS. Année 1 : EBE {eur(BASE['ebe'])} € "
            f"moins intérêts {eur(INTERETS_AN1)} € et dotation aux amortissements "
            f"{eur(DOTATION_AN1)} € (bâti à 80 % sur 30 ans) = résultat imposable de "
            f"{eur(RESULTAT_AN1)} €, positif, donc IS de 15 % soit {eur(IS_AN1)} €. Convention "
            f"prudente retenue pour les rendements publiés : IS de 15 % sur l'EBE, sans "
            f"amortissement du bâti modélisé, soit {eur(IS_CONVENTION_EBE)} €/an. Seuil de "
            f"décision du parc (5 % net avant IS) : {fr(BASE['rdt_av'])} % en base, "
            f"{fr(BASE['rdt_ap'])} % sous convention prudente",
            f"<strong>Frais d'acquisition :</strong> {eur(PRIX * NOTAIRE)} € (8 %), honoraires à "
            f"la charge du vendeur. Prix de revient acte en main : {eur(ACTE_EN_MAIN)} €, sans "
            f"travaux (aucun travaux annoncé)",
            f"<strong>Loyers :</strong> {eur(BASE['loyer'])} €/mois reconstruits (studio 380 € + "
            f"duplex 550 € + local commercial 300 €) — aucun loyer communiqué par l'annonce. "
            f"Hypothèses de sensibilité : 1 480 €/mois (favorable), 810 €/mois (défavorable) et "
            f"930 €/mois (local commercial vacant toute l'année)",
            f"<strong>Charges retenues :</strong> taxe foncière estimée 900 €/an (avis non "
            f"communiqué), charges d'immeuble 400 €/an (pas de copropriété), PNO 150 €, gestion "
            f"locative 5 % des loyers et provision travaux 200 € (poste composite de "
            f"{eur(GESTION_BASE + BASE['provision'])} €), comptabilité 500 €. Provision "
            f"automatique de 2,5 % du moteur désactivée pour ne pas compter deux fois la provision "
            f"travaux. Aucun poste laissé à zéro",
            f"<strong>Financement (doctrine du parc) :</strong> apport 10 %, prêt de "
            f"{eur(CAPITAL)} € sur 15 ans à 3,7 % et assurance emprunteur de 0,34 %, soit une "
            f"mensualité de {eur(MENS_BASE)} €/mois (0,00753 € par euro emprunté). Cash-flow de "
            f"<strong>{eur(CF_BASE)} €/mois</strong> ({eur(CF_BASE_AN)} €/an) au prix affiché, "
            f"+{eur(CF_BEST)} €/mois en hypothèse favorable, {eur(CF_WORST)} €/mois en hypothèse "
            f"défavorable, {eur(CF_VACANT)} €/mois si le local reste vide. Prix d'équilibre à "
            f"10 % d'apport : {eur(prix_cashflow_nul(BASE['ebe']))} € en base et "
            f"{eur(prix_cashflow_nul(VACANT['ebe']))} € local vide. Apport nécessaire pour un "
            f"cash-flow nul au prix affiché : {eur(apport_cashflow_nul(PRIX, BASE['ebe']))} € "
            f"({fr(apport_cashflow_nul(PRIX, BASE['ebe']) / PRIX * 100.0, 0)} % du prix), et "
            f"{eur(apport_cashflow_nul(PRIX, VACANT['ebe']))} € "
            f"({fr(apport_cashflow_nul(PRIX, VACANT['ebe']) / PRIX * 100.0, 0)} %) si le local "
            f"est vide. Ne pas lire cette fiche comme un dossier finançable en l'état",
            f"<strong>Valeur de marché :</strong> {eur(VALEUR_RETENUE)} € "
            f"({eur(SURF_LOTS_BATIS)} m² de lots bâtis × {eur(DVF_IMB_MED)} €/m²), fourchette "
            f"{eur(VALEUR_BASSE)} à {eur(VALEUR_HAUTE)} €. Ancrage : médiane DVF 2025 des "
            f"{DVF_IMB_N} mutations d'immeubles de rapport de la commune, encadrée par deux "
            f"transactions mixtes nommées du centre-ville ({eur(DVF_CMP1['m2'])} €/m² rue "
            f"d'Entraigues le {DVF_CMP1['date']}, {eur(DVF_CMP2['m2'])} €/m² rue Jules Ferry le "
            f"{DVF_CMP2['date']}). La médiane communale des appartements "
            f"({eur(DVF_APP_MED)} €/m²) n'est pas applicable à un immeuble entier avec local et "
            f"cave. Le prix affiché ressort à un ratio coût/valeur de "
            f"{fr(ACTE_EN_MAIN / VALEUR_RETENUE)}",
            f"<strong>Contrôles à faire avant toute offre :</strong> le bail du local commercial "
            f"et son occupation réelle ; les loyers des deux logements, leurs baux, échéances et "
            f"quittances ; avis de taxe foncière et valeur locative cadastrale ; diagnostics datés "
            f"(DPE, électricité, plomb, amiante) et état de la couverture, de la charpente et de "
            f"l'humidité de la cave par un homme de l'art ; surfaces Carrez par lot et plan des "
            f"trois niveaux ; statut de propriété (monopropriété ou copropriété) ; pièces "
            f"d'urbanisme si la transformation du local en studio est envisagée",
            f"<strong>Point de méthode :</strong> sur ce dossier, le seul paramètre qui déplace la "
            f"décision n'est pas le prix — la grille de rendement tiendrait jusqu'à "
            f"{eur(BASE['cap5'])} € — mais l'occupation du local commercial et le montant réel des "
            f"loyers. Le local représente {fr(LOCAL / SURF_LOTS_BATIS * 100, 0)} % de la surface "
            f"bâtie et fait passer le rendement de {fr(BASE['rdt_av'])} % à "
            f"{fr(VACANT['rdt_av'])} %, le plafond d'{eur(BASE['cap5'])} € à "
            f"{eur(VACANT['cap5'])} € et le cash-flow de {eur(CF_BASE)} €/mois à "
            f"{eur(CF_VACANT)} €/mois. Aucune offre ne doit être signée avant d'avoir vu le bail "
            f"ou l'état de vacance de ce lot",
            f"<strong>Comparaison — les autres dossiers Brignoles du dépôt :</strong> l'immeuble "
            f"de rapport du centre ({eur(230000.0)} € affichés le 20/09/2026, trois T3 de "
            f"196 m² en Site Patrimonial Remarquable) exigeait une rénovation lourde et un DPE "
            f"absent ; celui du 18/09/2026 portait sur le centre-ville également. Le présent "
            f"dossier est le seul dont le rendement en l'état passe le seuil de 5 % net avant IS "
            f"({fr(BASE['rdt_av'])} %), sans travaux annoncés et sans passif énergétique — mais "
            f"c'est aussi le seul dont la décision tient à un local commercial dont personne ne "
            f"connaît l'occupation, et c'est ce qui doit décider de l'ordre de priorité : celui-ci "
            f"se négocie en premier, à condition d'obtenir les baux",
        ],
    )

    c = gen.CONF[SLUG]
    html = gen.TEMPLATE.format(
        titre_court=c['titre_court'], adresse=c['adresse'], date_fr=c['date_fr'],
        source=c['source'], url=c['url'], badge=c['badge'], strategie=c['strategie'],
        fiscal_note=c['fiscal_note'],
        prix=eur(PRIX),
        surface=f"{eur(SURF_HAB)} m² (2 logements, hors cave)",
        prix_m2=f"{eur(PRIX / SURF_HAB)} €/m²",
        revient=eur(ACTE_EN_MAIN),
        valeur=eur(VALEUR_RETENUE),
        revenus=eur(BASE['loyer']),
        rdt_revient=fr(BASE['rdt_av']), rdt_valeur=fr(BASE['rdt_ap']),
        note=fr(note, 1), note_cls=fr(note, 1).replace(',', '-'),
        lat=c['lat'], lon=c['lon'], quartier=c['quartier'],
        intro_attr=c['intro_attr'], profil=c['profil'], concl_attr=c['concl_attr'],
        attrs=gen.attr_html(rec_), intro_strat=c['intro_strat'],
        strats=gen.strategy_html(rec_),
        rationale=c['rationale'], identite=gen.identite_html(c['identite']),
        projections=f"""  <section class="financial-projections">
    <h2>Compte d'exploitation locatif — prix affiché {eur(PRIX)} €, acte en main {eur(ACTE_EN_MAIN)} €, SCI à l'IS</h2>
    <p class="attractiveness-intro">{lecture}</p>
    <div class="projections-grid">
{chr(10).join(cartes)}
    </div>
    <table class="projection-table compare">
      <thead><tr><th>Indicateur</th><th class="num">Base — 1 230 €/mois</th><th class="num">Optimiste — 1 480 €/mois</th><th class="num">Pessimiste — 810 €/mois</th><th class="num">Local vacant — 930 €/mois</th></tr></thead>
      <tbody>
        <tr><td>Loyers bruts annuels</td><td class="num">{eur(BASE['brut'])} €</td><td class="num">{eur(BEST['brut'])} €</td><td class="num">{eur(WORST['brut'])} €</td><td class="num">{eur(VACANT['brut'])} €</td></tr>
        <tr><td>Excédent brut d'exploitation</td><td class="num">{eur(BASE['ebe'])} €</td><td class="num">{eur(BEST['ebe'])} €</td><td class="num">{eur(WORST['ebe'])} €</td><td class="num">{eur(VACANT['ebe'])} €</td></tr>
        <tr><td>EBE mensuel</td><td class="num">{eur(BASE['ebe_mois'])} €/mois</td><td class="num">{eur(BEST['ebe_mois'])} €/mois</td><td class="num">{eur(WORST['ebe_mois'])} €/mois</td><td class="num">{eur(VACANT['ebe_mois'])} €/mois</td></tr>
        <tr><td>Net après IS (convention prudente)</td><td class="num">{eur(BASE['net'])} €</td><td class="num">{eur(BEST['net'])} €</td><td class="num">{eur(WORST['net'])} €</td><td class="num">{eur(VACANT['net'])} €</td></tr>
        <tr><td>Rendement net avant IS (acte en main)</td><td class="num">{fr(BASE['rdt_av'])} %</td><td class="num">{fr(BEST['rdt_av'])} %</td><td class="num">{fr(WORST['rdt_av'])} %</td><td class="num">{fr(VACANT['rdt_av'])} %</td></tr>
        <tr><td>Rendement net après IS (acte en main)</td><td class="num">{fr(BASE['rdt_ap'])} %</td><td class="num">{fr(BEST['rdt_ap'])} %</td><td class="num">{fr(WORST['rdt_ap'])} %</td><td class="num">{fr(VACANT['rdt_ap'])} %</td></tr>
        <tr><td>Rendement net après IS sur la valeur ({eur(VALEUR_RETENUE)} €)</td><td class="num">{fr(BASE['rdt_valeur'])} %</td><td class="num">{fr(BEST['rdt_valeur'])} %</td><td class="num">{fr(WORST['rdt_valeur'])} %</td><td class="num">{fr(VACANT['rdt_valeur'])} %</td></tr>
        <tr><td>Prix d'achat tenant 5 % net avant IS</td><td class="num">{eur(BASE['cap5'])} €</td><td class="num">{eur(BEST['cap5'])} €</td><td class="num">{eur(WORST['cap5'])} €</td><td class="num">{eur(VACANT['cap5'])} €</td></tr>
        <tr><td>Écart au prix affiché ({eur(PRIX)} €)</td><td class="num">{eur(BASE['cap5'] - PRIX)} €</td><td class="num">{eur(BEST['cap5'] - PRIX)} €</td><td class="num">{eur(WORST['cap5'] - PRIX)} €</td><td class="num">{eur(VACANT['cap5'] - PRIX)} €</td></tr>
        <tr><td>Cash-flow mensuel après crédit (apport 10 %)</td><td class="num">{eur(CF_BASE)} €/mois</td><td class="num">+{eur(CF_BEST)} €/mois</td><td class="num">{eur(CF_WORST)} €/mois</td><td class="num">{eur(CF_VACANT)} €/mois</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Le seuil est tenu, de peu, et c'est le local qui le tient.</strong> La doctrine du parc exige 5 % net avant IS sur le prix de revient, ici {eur(ACTE_EN_MAIN)} € d'acte en main (prix affiché {eur(PRIX)} € + {eur(PRIX * NOTAIRE)} € de frais, aucun travaux annoncé). En scénario de base, avec {eur(BASE['loyer'])} €/mois de loyers reconstruits, l'excédent brut d'exploitation ressort à <strong>{eur(BASE['ebe'])} €</strong> — <strong>{fr(BASE['rdt_av'])} % net avant IS</strong>, soit {fr((BASE['rdt_av'] - 5.0) * 100, 0)} points de base au-dessus du seuil — et {fr(BASE['rdt_ap'])} % après IS. Ce résultat ne tient pas au prix mais à une ligne invisible dans l'annonce : le local commercial de 20 m², sans preneur, dont le loyer de 300 €/mois est une reconstruction. Sans lui, le dossier tombe à {fr(VACANT['rdt_av'])} % et le plafond de 5 % descend à {eur(VACANT['cap5'])} €, <strong>{fr((PRIX - VACANT['cap5']) / PRIX * 100.0, 1)} % sous le prix affiché</strong>. À l'inverse, un bail sous-évalué le 15 % de vacance fait tomber le rendement à {fr(WORST['rdt_av'])} % et le plafond à {eur(WORST['cap5'])} €.</p>
    </div>
    <h3>Sensibilité du plafond d'achat aux seuls loyers (charges du scénario de base)</h3>
    <table class="projection-table compare">
      <thead><tr><th>Loyers mensuels</th><th>Hypothèse</th><th class="num">EBE</th><th class="num">Rendement net avant IS</th><th class="num">Achat max (5 % net avant IS)</th><th class="num">Écart au prix affiché</th></tr></thead>
      <tbody>
{sens_html}
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Deuxième lecture : ce que le dossier vaut sur son propre marché.</strong> Le prix affiché de {eur(PRIX)} € ressort à {eur(PRIX / SURF_LOTS_BATIS)} €/m² sur les {eur(SURF_LOTS_BATIS)} m² de lots bâtis (20 m² de local + 20 m² de studio + 47 m² de duplex, hors cave). Les immeubles de rapport réellement vendus à Brignoles en 2025 — {DVF_IMB_N} mutations de deux logements et plus — se traitent à une médiane de {eur(DVF_IMB_MED)} €/m², de {DVF_IMB_MIN} à {eur(DVF_IMB_MAX)} €/m², et la transaction mixte la plus proche de ce bien (logement + local commercial, rue d'Entraigues) s'est faite à {eur(DVF_CMP1['m2'])} €/m². Le prix affiché est donc au-dessus du haut de la fourchette de son propre marché : valeur retenue <strong>{eur(VALEUR_RETENUE)} €</strong>, ratio coût/valeur de <strong>{fr(ACTE_EN_MAIN / VALEUR_RETENUE)}</strong>. Sur la base de {eur(SURF_HAB)} m² retenus (les deux logements, hors cave et hors local) le prix ressort à {eur(PRIX / SURF_HAB)} €/m², à comparer aux {eur(DVF_APP_MED)} €/m² de la médiane communale des appartements ({DVF_APP_N} ventes) : le rapprochement est trompeur dans les deux sens — un immeuble entier avec local commercial et cave se traite avec une décote de rendement, mais les petites surfaces de ce marché se vendent au-dessus de la médiane ({eur(DVF_APP_3060_MED)} €/m² sur la tranche 30-60 m²).</p>
    </div>
    <p class="attractiveness-intro">Repères de méthode : acte en main {eur(ACTE_EN_MAIN)} € = prix affiché {eur(PRIX)} € + frais d'acquisition {eur(PRIX * NOTAIRE)} € (8 %, honoraires à la charge du vendeur) ; aucun travaux à l'acquisition (aucun travaux annoncé), provision travaux de 200 €/an en exploitation ; vacance 8 % en base, 5 % en hypothèse favorable, 15 % en hypothèse défavorable, 6 % dans la variante local vacant ; gestion locative 5 %, 4 % et 6 % selon les scénarios ; taxe foncière estimée 900 € (avis non communiqué) ; charges d'immeuble 400 € ; assurance PNO 150 € ; comptabilité 500 € ; SCI à l'IS avec IS de 15 % appliqué à l'EBE, sans amortissement du bâti modélisé (convention prudente — la dotation réelle de l'année 1, {eur(DOTATION_AN1)} €, laisse un résultat imposable positif de {eur(RESULTAT_AN1)} € et un IS de {eur(IS_AN1)} €) ; valeur de marché {eur(VALEUR_RETENUE)} € ({eur(DVF_IMB_MED)} €/m² sur les {eur(SURF_LOTS_BATIS)} m² de lots bâtis, médiane DVF 2025 des immeubles de rapport de la commune). <strong>Convention de lecture :</strong> le seuil de la doctrine du parc s'entend <em>avant</em> IS sur le prix de revient, soit {fr(BASE['rdt_av'])} % ici ; le même rendement <em>après</em> IS ressort à {fr(BASE['rdt_ap'])} % sur l'acte en main et {fr(BASE['rdt_valeur'])} % sur la valeur de marché retenue, tandis que le listing du dépôt affiche le net après IS sur le revient et sur le prix d'achat ({fr(BASE['rdt_ap'], 1)} % / {fr(rd['net_sur_achat_pct'], 1)} %). Les quatre chiffres décrivent la même exploitation sous quatre dénominateurs différents.</p>
  </section>
{cf_section}
{variante_section}
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
         '<span class="card-label">Surface retenue (2 logements)</span>'),
        ('<span class="card-label">Prix / m²</span>',
         '<span class="card-label">Prix / m² hors cave</span>'),
        ('<span class="card-label">Prix de revient</span>',
         '<span class="card-label">Prix de revient (acte en main)</span>'),
        ('<span class="card-label">Valeur marché retenue</span>',
         '<span class="card-label">Valeur marché (DVF 2025)</span>'),
        ('<span class="card-label">Revenus bruts</span>',
         '<span class="card-label">Loyers retenus (reconstruits)</span>'),
        ('<span class="card-label">Rentabilité nette</span>',
         '<span class="card-label">Rendement net avant IS / après IS</span>'),
    ):
        assert vieux in html, vieux
        html = html.replace(vieux, neuf)

    # Controles sur le HTML produit
    assert 'section class="verdict nego"' in html, "classe de verdict inattendue"
    assert 'note-' + fr(note, 1).replace(',', '-') in html
    assert 'verdict buy' not in html and 'verdict pass' not in html

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


if __name__ == '__main__':
    main()
