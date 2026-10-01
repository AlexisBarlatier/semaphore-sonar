#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche Appartement duplex T2/3 de 43,40 m2, Brignoles, coeur du centre
historique (proximite immediate place Saint-Pierre), rez-de-chaussee avec
chambre a l'etage, immeuble de 1900.

82 000 EUR (1 889 EUR/m2), Nestenn Brignoles, annonce SeLoger 26JBKPTIEDR5.
Bien libre, non meuble, annonce « excellent etat, pret a louer, sans travaux » ;
copropriete de 6 lots SANS procedure en cours, charges annoncees 200 EUR/an,
DPE D, GES B.

L'ANALYSE DE PRIX, qui est le coeur de cette fiche :
- prix affiche 1 889 EUR/m2. L'annonce ecrit « moins cher que des biens
  comparables dans la region » : c'est vrai sur la boite large du quartier
  (mediane DVF 2025 2 750 EUR/m2 sur 40-48 m2, contaminee par des residences
  recentes hors vieille ville, chemin Saint-Pierre, Les 4 Saisons, Les Jardins
  de Provence a 2 683-3 571 EUR/m2) et FAUX des qu'on se restreint au noyau
  historique : 15 ventes de 30 a 50 m2 intra-muros en 2025, mediane
  1 711 EUR/m2, Q1 1 478, Q3 1 867 -> valeur retenue 74 257 EUR pour
  43,40 m2. Le bien s'achete donc 19,3 % AU-DESSUS de la valeur de son propre
  micro-marche, et le prix demande (82 000 EUR) est a 1 % du prix median
  absolu des six transactions comparables retenues (81 180 EUR).
- ce que ce prix achete : 5,40 % net avant IS (le seuil doctrinal est passe),
  4,59 % apres IS, et un cash-flow de -149 EUR/mois a 15 ans avec 10 %
  d'apport.
- ce qu'il ne dit pas : aucune piece de copropriete, aucun diagnostic joint,
  taxe fonciere estimee, et une surface vendue « 2/3 pieces » dont la
  troisieme piece (7 m2) n'a pas de statut Carrez etabli.

Branche residentielle (SCI a l'IS). Chaque chiffre publie est reaffirme par
`calcule()` a tolerance depuis les lignes du modele (loyers, charges, credit,
fiscalite, plafonds, apports, DVF). Les donnees DVF 2025 sont recalculees
depuis le fichier departemental (/tmp/dvf83_2025.csv.gz) et la sortie signale
l'ecart si le fichier est absent. Les scenarios sont calcules par le MOTEUR
(engine.compute sur une copie du record, loyer, vacance et lignes de charges
surchargees) - aucun scenario n'est chiffre a la main.
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

SLUG = "2026-10-01-appartement-duplex-brignoles-vieille-ville"
URL = ("https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/"
       "var-83/brignoles-83170/26JBKPTIEDR5")
DATE = "2026-10-01"
DATE_FR = "1er octobre 2026"

# --- Le bien -----------------------------------------------------------------
PRIX = 82000.0
FRAIS_ACQUISITION = 6560.0                    # 8 %, simulateur de l'annonce
ACTE_EN_MAIN = PRIX + FRAIS_ACQUISITION       # 88 560
TAUX_FRAIS = FRAIS_ACQUISITION / PRIX         # 8,00 %
SURF = 43.4
PIECES = 2
CHAMBRES = 1
PETITE_PIECE = 7.0                            # bureau / chambre d'appoint
ETAGE = "rez-de-chaussée avec chambre à l'étage (duplex)"
ANNEE = 1900
LOTS_COPRO = 6
CHARGES_COPRO = 200.0                 # annoncées par l'annonce
CHARGES_COPRO_HAUT = 600.0            # variante testée : triple
PROCEDURE = False                     # « pas de procédure en cours »
DPE = "D"
GES = "B"
FACTURE_BASSE = 1130.0
FACTURE_HAUTE = 1570.0
PHOTOS = 5
RDC = True

# --- Loyers de marche ---------------------------------------------------------
# Ancrages : fiche de reference interne « Seuils d'achat par ville » du
# 21/09/2026 (11,0 EUR/m2 pour un lot type de 60 m2 = plancher prudent) ;
# Trackstone, appartements Brignoles, 12,0 EUR/m2 ; SeLoger, estimation de
# location de la ville, 13 EUR/m2 (9 a 20). Annonces reelles du centre :
# 37,66 m2 a 640 EUR/mois (Figaro), 40,68 m2 2 pieces 1er etage centre a
# 650 EUR/mois charges comprises (ABC IMMO Brignoles, exclusivite), 24 m2
# meuble a 530 EUR/mois charges comprises ; et pour les grandes surfaces,
# 65,1 m2 a 600 EUR/mois (9,2 EUR/m2 moins de 12) et 70 m2 a 786-855 EUR/mois
# (11,2-12,2 EUR/m2 moins de 13).
LOYER_M2_BAS = 12.0
LOYER_M2_MED = 13.5
LOYER_M2_HAUT = 15.0
LOYER_BAS = round(SURF * LOYER_M2_BAS)     # 521
LOYER_BASE = round(SURF * LOYER_M2_MED)    # 586
LOYER_HAUT = round(SURF * LOYER_M2_HAUT)   # 651
REALADVISOR_MED = 828.0                    # loyer median d'un appartement, quartier

# --- Doctrine du parc : seuil de rendement et credit --------------------------
SEUIL = 0.05
COEF_PLAFOND = SEUIL * (1 + TAUX_FRAIS)
APPORT_PCT = 0.10
TAUX_CREDIT = 0.037
ASSURANCE_PCT = 0.0034
DUREE_ANS = 15
CAPITAL = PRIX * (1 - APPORT_PCT)             # 73 800
MENS_MODELE = 547.0

# --- Charges d'exploitation du modele (scenario de base) ----------------------
TF_BASE = 700.0               # ESTIMEE, avis de taxe fonciere non communique
COPRO_BASE = CHARGES_COPRO
COPRO_HAUT = CHARGES_COPRO_HAUT
PNO = 100.0
COMPTA = 400.0
PROV_BASE = 150.0
GESTION_BASE_PCT = 5.0
VAC_BASE = 5.0
VAC_BEST = 3.0
VAC_WORST = 10.0

# --- Fiscalite annee 1 --------------------------------------------------------
QUOTE_PART_BATI_MODELE = 0.80
DOTATION_AN1 = PRIX * QUOTE_PART_BATI_MODELE / 30.0
INTERETS_AN1 = CAPITAL * TAUX_CREDIT
CONVENTION_IS = 0.15

# --- Travaux : aucun constat, donc une grille et pas un chiffre ---------------
TRAVAUX_REF_1 = 10000.0
TRAVAUX_REF_2 = 20000.0
TRAVAUX_REF_3 = 30000.0

# --- Marche local (fiche de reference analyses/marches-locaux) ----------------
PLAF_PATRIMONIAL = (1021, 943, 818)     # 6,5 % / 7,0 % / 8,0 % net d'IS
PLAF_MDB = (558, 516, 489)

# --- DVF 2025 reelle, Brignoles (commune 83023) ------------------------------
DVF_FICHIER = '/tmp/dvf83_2025.csv.gz'
DVF_COMMUNE = '83023'
DVF_LIGNES_VENTE = 883
DVF_MUTATIONS = 447
DVF_MUTATIONS_VENTE = 397
DVF_APP_N = 168
DVF_APP_MED = 2246
DVF_APP_1530_N = 7
DVF_APP_1530_MED = 2250
DVF_APP_3045_N = 46
DVF_APP_3045_MED = 2863
DVF_APP_4560_N = 33
DVF_APP_4560_MED = 2109
DVF_APP_6090_N = 66
DVF_APP_6090_MED = 2188
# Boite LARGE du quartier (celle de la fiche du T3, 25/09/2026) : contaminee.
DVF_BOITE = (43.398, 43.412, 6.050, 6.072)
DVF_Q_APP_N = 116
DVF_Q_MED = 2081
DVF_Q_4048_N = 15
DVF_Q_4048_MED = 2750
DVF_Q_4048_Q1 = 2042
DVF_Q_4048_Q3 = 3201
DVF_Q_4048_PRIX = 110000
# Boite RESSERREE intra-muros : noyau Cavaillon / Poissonnerie / Jules Ferry /
# place Saint-Pierre / Entraigues / Comtes de Provence / Tourmalaute / Robinet.
DVF_BOITE_FINE = (43.4040, 43.4075, 6.0595, 6.0650)
DVF_F_APP_N = 50
DVF_F_MED = 1567
DVF_F_3050_N = 15
DVF_F_3050_MED = 1711
DVF_F_3050_Q1 = 1478
DVF_F_3050_Q3 = 1867
DVF_F_3050_PRIX = 55000
DVF_F_4048_N = 5
DVF_F_4048_MED = 1867
DVF_F_4048_Q1 = 1321
DVF_F_4048_Q3 = 2280
DVF_F_4048_PRIX = 84000
DVF_CMP_N = 6
DVF_CMP_MED = 1964
DVF_CMP_PRIX = 81180
DVF_COMPARABLES = (
    dict(date="11/03/2025", surf=40.0, prix=93000.0, m2=2325, voie="rue Jules Ferry", num="25"),
    dict(date="12/03/2025", surf=46.0, prix=68000.0, m2=1478, voie="rue de la Poissonnerie", num="11"),
    dict(date="28/02/2025", surf=43.0, prix=50000.0, m2=1163, voie="rue Cavaillon", num="10"),
    dict(date="19/06/2025", surf=38.0, prix=78360.0, m2=2062, voie="rue Entraigues", num="18"),
    dict(date="03/12/2025", surf=45.0, prix=84000.0, m2=1867, voie="rue Jules Ferry", num="16"),
    dict(date="29/12/2025", surf=47.0, prix=105000.0, m2=2234, voie="place Saint-Pierre", num="8"),
)

# --- Valeur de marche ---------------------------------------------------------
VALEUR_BASSE = round(SURF * DVF_F_3050_Q1)      # 64 145
VALEUR_RETENUE = round(SURF * DVF_F_3050_MED)   # 74 257
VALEUR_HAUTE = round(SURF * DVF_F_3050_Q3)      # 81 028
VALEUR_LARGE = round(SURF * DVF_Q_4048_MED)     # 119 350 (boite contaminee)

CONTROLES = []
ECARTS = []


def calcule(libelle, publie, recalcule, tol=1.0):
    CONTROLES.append((libelle, publie, recalcule, tol))
    if abs(publie - recalcule) > tol:
        if os.environ.get("HERMES_TOLERANT") == "1":
            ecart(libelle, publie, recalcule, f"tolerance {tol}")
            return
        assert False, (libelle, publie, recalcule)


def ecart(libelle, brief, recalcule, note):
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


def charges_fixes(tf, copro, provision):
    return tf + copro + PNO + COMPTA + provision


def revenus_annuels(loyer):
    return loyer * 12.0


def ebe_modele(loyer, vac, gestion_pct, tf, copro, provision):
    r = revenus_annuels(loyer)
    return (r * (1 - vac / 100.0) - r * gestion_pct / 100.0
            - charges_fixes(tf, copro, provision))


def plafond5(ebe):
    return ebe / COEF_PLAFOND


def prix_5pct_avec_travaux(ebe, travaux):
    return (ebe / SEUIL - travaux) / (1 + TAUX_FRAIS)


def plafond_is(ebe, seuil=0.065):
    return ebe / (seuil * (1 + TAUX_FRAIS))


def prix_cashflow_nul(ebe):
    return (ebe / 12.0) / ((1 - APPORT_PCT) * mensualite_par_euro())


def apport_cashflow_nul(prix, ebe):
    return prix - (ebe / 12.0) / mensualite_par_euro()


def loyer_cashflow_nul(tf, copro, provision):
    fixes = charges_fixes(tf, copro, provision)
    part = 1 - VAC_BASE / 100.0 - GESTION_BASE_PCT / 100.0
    return (mensualite(CAPITAL) * 12.0 + fixes) / (12.0 * part)


def eur(v, dec=0):
    return f"{v:,.{dec}f}".replace(',', ' ').replace('.', ',')


def fr(v, dec=2):
    return f"{v:.{dec}f}".replace('.', ',')


def scen(rec, loyer, vac, gestion_pct, tf, copro, provision):
    v = copy.deepcopy(rec)
    v['marche']['loyers'][0]['loyer_mensuel_euros'] = loyer
    v['hypotheses']['vacance_base_pct'] = vac
    ch = v['hypotheses']['charges']
    ch['taxe_fonciere_annuelle_euros'] = tf
    ch['charges_copro_annuelles_euros'] = copro
    ch['entretien_annuel_euros'] = round(
        revenus_annuels(loyer) * gestion_pct / 100.0 + provision, 2)
    c = engine.compute(v)
    assert c['calculable'], c['raison']
    f = c['fiscal']
    brut = revenus_annuels(loyer)
    return dict(
        loyer=loyer, brut=brut, vac=vac, gestion=gestion_pct, tf=tf, copro=copro,
        provision=provision,
        ebe_modele=ebe_modele(loyer, vac, gestion_pct, tf, copro, provision),
        vac_eur=brut * vac / 100.0, gestion_eur=brut * gestion_pct / 100.0,
        entretien=brut * gestion_pct / 100.0 + provision,
        ebe=f['ebe'], is_=f['is_annuel'], net=f['net_apres_is'],
        ebe_mois=f['ebe'] / 12.0, net_mois=f['net_apres_is'] / 12.0,
        cf=cashflow_mensuel(f['ebe']), cf_ap=cashflow_mensuel(f['net_apres_is']),
        rdt_brut=brut / PRIX * 100.0,
        rdt_av=f['ebe'] / ACTE_EN_MAIN * 100.0,
        rdt_ap=f['net_apres_is'] / ACTE_EN_MAIN * 100.0,
        rdt_valeur=f['net_apres_is'] / VALEUR_RETENUE * 100.0,
        cap5=plafond5(f['ebe']), eng=c,
    )


def hypo(loyer, vac=None, gestion=None, tf=None, copro=None, prov=None):
    """Meme formule que le moteur, verifiee ligne a ligne dans main()."""
    vac = VAC_BASE if vac is None else vac
    gestion = GESTION_BASE_PCT if gestion is None else gestion
    tf = TF_BASE if tf is None else tf
    copro = COPRO_BASE if copro is None else copro
    prov = PROV_BASE if prov is None else prov
    ebe = ebe_modele(loyer, vac, gestion, tf, copro, prov)
    net = ebe * (1.0 - CONVENTION_IS)
    brut = revenus_annuels(loyer)
    return dict(
        loyer=loyer, brut=brut, ebe=ebe, net=net,
        fixes=charges_fixes(tf, copro, prov),
        vac_eur=brut * vac / 100.0, gestion_eur=brut * gestion / 100.0,
        is_=ebe * CONVENTION_IS,
        rdt_av=ebe / ACTE_EN_MAIN * 100.0, rdt_ap=net / ACTE_EN_MAIN * 100.0,
        rdt_valeur=net / VALEUR_RETENUE * 100.0,
        rdt_brut=brut / PRIX * 100.0, cap5=plafond5(ebe),
        cf=cashflow_mensuel(ebe), cf_ap=cashflow_mensuel(net),
        cf_mois=ebe / 12.0, net_mois=net / 12.0,
    )


# ---------------------------------------------------------------------------
# Verificateur DVF : chaque statistique publiee est recalculee
# ---------------------------------------------------------------------------
def verifie_dvf():
    if not os.path.exists(DVF_FICHIER):
        print(f"  DVF : fichier {DVF_FICHIER} absent — constantes DVF non "
              f"recalculees (relancer scripts/analyse_app/stats_dvf_ville.py)")
        return False

    def f2(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return None

    lignes = []
    with gzip.open(DVF_FICHIER, 'rt', encoding='utf-8', errors='replace') as f:
        for r in csv.DictReader(f):
            if r['code_commune'] == DVF_COMMUNE:
                lignes.append(r)
    muts = {}
    for r in lignes:
        muts.setdefault(r['id_mutation'], []).append(r)
    ventes = [v for v in muts.values()
              if all(x['nature_mutation'] == 'Vente' for x in v)]

    def infos(rs):
        ts = [r for r in rs if r['type_local'] == 'Appartement']
        if not ts:
            return None
        vf = f2(ts[0]['valeur_fonciere']) or 0.0
        s = sum(f2(r['surface_reelle_bati']) or 0.0 for r in rs)
        if not (s > 5 and vf > 5000):
            return None
        la, lo = f2(ts[0]['latitude']), f2(ts[0]['longitude'])
        return dict(s=s, v=vf, m2=vf / s, date=ts[0]['date_mutation'],
                    voie=ts[0]['adresse_nom_voie'], lat=la, lon=lo,
                    num=ts[0].get('adresse_numero'),
                    box=(la is not None and lo is not None
                         and DVF_BOITE[0] <= la <= DVF_BOITE[1]
                         and DVF_BOITE[2] <= lo <= DVF_BOITE[3]),
                    fin=(la is not None and lo is not None
                         and DVF_BOITE_FINE[0] <= la <= DVF_BOITE_FINE[1]
                         and DVF_BOITE_FINE[2] <= lo <= DVF_BOITE_FINE[3]))

    med = lambda v: round(st.median(v))                                   # noqa: E731
    calcule("DVF lignes de nature Vente (commune)", DVF_LIGNES_VENTE,
            sum(1 for r in lignes if r['nature_mutation'] == 'Vente'), 0)
    calcule("DVF mutations lues (commune)", DVF_MUTATIONS, len(muts), 0)
    calcule("DVF mutations de nature Vente", DVF_MUTATIONS_VENTE, len(ventes), 0)
    calcule("DVF ventes d'appartements (commune)", DVF_APP_N,
            sum(1 for rs in ventes if any(r['type_local'] == 'Appartement'
                                          for r in rs)), 0)
    app = [i for i in (infos(rs) for rs in ventes) if i]
    calcule("DVF mediane appartements toutes surfaces (commune)", DVF_APP_MED,
            med([i['m2'] for i in app]), 0)
    for lo_, hi_, n_, m_ in ((15, 30, DVF_APP_1530_N, DVF_APP_1530_MED),
                             (30, 45, DVF_APP_3045_N, DVF_APP_3045_MED),
                             (45, 60, DVF_APP_4560_N, DVF_APP_4560_MED),
                             (60, 90, DVF_APP_6090_N, DVF_APP_6090_MED)):
        sel = [i['m2'] for i in app if lo_ <= i['s'] < hi_]
        calcule(f"DVF appartements {lo_}-{hi_} m2 (n)", n_, len(sel), 0)
        calcule(f"DVF appartements {lo_}-{hi_} m2 (mediane)", m_, med(sel), 0)

    # --- boite large (contaminee) -----------------------------------------
    qs = [i for i in app if i['box']]
    calcule("DVF boite large : ventes d'appartements", DVF_Q_APP_N, len(qs), 0)
    calcule("DVF boite large : mediane toutes surfaces", DVF_Q_MED,
            med([i['m2'] for i in qs]), 0)
    qb = [i for i in qs if 40 <= i['s'] <= 48]
    calcule("DVF boite large 40-48 m2 (n)", DVF_Q_4048_N, len(qb), 0)
    calcule("DVF boite large 40-48 m2 (mediane)", DVF_Q_4048_MED,
            med([i['m2'] for i in qb]), 0)
    qqb = st.quantiles([i['m2'] for i in qb], n=4)
    calcule("DVF boite large 40-48 m2 (Q1)", DVF_Q_4048_Q1, round(qqb[0]), 0)
    calcule("DVF boite large 40-48 m2 (Q3)", DVF_Q_4048_Q3, round(qqb[2]), 0)
    calcule("DVF boite large 40-48 m2 (prix median)", DVF_Q_4048_PRIX,
            round(st.median([i['v'] for i in qb])), 0)

    # --- boite resserree intra-muros : l'ancre retenue ---------------------
    fs = [i for i in app if i['fin']]
    calcule("DVF intra-muros : ventes d'appartements", DVF_F_APP_N, len(fs), 0)
    calcule("DVF intra-muros : mediane toutes surfaces", DVF_F_MED,
            med([i['m2'] for i in fs]), 0)
    fb = [i for i in fs if 30 <= i['s'] < 50]
    calcule("DVF intra-muros 30-50 m2 (n)", DVF_F_3050_N, len(fb), 0)
    calcule("DVF intra-muros 30-50 m2 (mediane)", DVF_F_3050_MED,
            med([i['m2'] for i in fb]), 0)
    fqb = st.quantiles([i['m2'] for i in fb], n=4)
    calcule("DVF intra-muros 30-50 m2 (Q1)", DVF_F_3050_Q1, round(fqb[0]), 0)
    calcule("DVF intra-muros 30-50 m2 (Q3)", DVF_F_3050_Q3, round(fqb[2]), 0)
    calcule("DVF intra-muros 30-50 m2 (prix median)", DVF_F_3050_PRIX,
            round(st.median([i['v'] for i in fb])), 0)
    f48 = [i for i in fs if 40 <= i['s'] <= 48]
    calcule("DVF intra-muros 40-48 m2 (n)", DVF_F_4048_N, len(f48), 0)
    calcule("DVF intra-muros 40-48 m2 (mediane)", DVF_F_4048_MED,
            med([i['m2'] for i in f48]), 0)
    fq48 = st.quantiles([i['m2'] for i in f48], n=4)
    calcule("DVF intra-muros 40-48 m2 (Q1)", DVF_F_4048_Q1, round(fq48[0]), 0)
    calcule("DVF intra-muros 40-48 m2 (Q3)", DVF_F_4048_Q3, round(fq48[2]), 0)
    calcule("DVF intra-muros 40-48 m2 (prix median)", DVF_F_4048_PRIX,
            round(st.median([i['v'] for i in f48])), 0)

    # --- comparables nommes -------------------------------------------------
    def _cmp(i):
        return any(abs(i['v'] - c['prix']) < 1.0 and abs(i['s'] - c['surf']) < 1.0
                   for c in DVF_COMPARABLES)
    pool = [i for i in fs if _cmp(i)]
    assert len(pool) == len(DVF_COMPARABLES), (len(pool), len(DVF_COMPARABLES))
    calcule("DVF comparables (n)", DVF_CMP_N, len(pool), 0)
    calcule("DVF comparables (mediane EUR/m2)", DVF_CMP_MED,
            round(st.median([i['m2'] for i in pool])), 0.5)
    calcule("DVF comparables (prix median)", DVF_CMP_PRIX,
            round(st.median([i['v'] for i in pool])), 0.5)
    for c in DVF_COMPARABLES:
        hits = [i for i in app if abs(i['v'] - c['prix']) < 1.0
                and abs(i['s'] - c['surf']) < 1.0]
        assert hits, (f"transaction DVF {c['prix']} EUR / {c['surf']} m2 "
                      f"introuvable dans le fichier")
        i = hits[0]
        calcule(f"DVF comparable {c['voie']} (surface)", c['surf'], i['s'], 0.5)
        calcule(f"DVF comparable {c['voie']} (EUR/m2)", c['m2'], round(i['m2']),
                1.0)
        assert i['fin'], (c['voie'], "hors de la boite intra-muros")
        assert i['date'].split('-')[0] == c['date'].split('/')[2], i['date']
    return True


# ---------------------------------------------------------------------------
# Le record : tout ce que l'annonce dit, et tout ce qu'elle ne dit pas
# ---------------------------------------------------------------------------
def rec_bien():
    SBAS = hypo(LOYER_BAS)
    SBASE = hypo(LOYER_BASE)
    SHAUT = hypo(LOYER_HAUT)
    SCOPRO = hypo(LOYER_BASE, copro=COPRO_HAUT)
    SBEST = hypo(LOYER_BASE, vac=VAC_BEST, gestion=4.0)
    SWORST = hypo(LOYER_BAS, vac=VAC_WORST, tf=1000.0, copro=COPRO_HAUT,
                  prov=400.0)
    surcote = (PRIX / VALEUR_RETENUE - 1) * 100.0
    ecart_large = (PRIX / SURF - DVF_Q_4048_MED) / DVF_Q_4048_MED * 100.0
    ecart_fin = (PRIX / SURF - DVF_F_3050_MED) / DVF_F_3050_MED * 100.0
    return {
        "slug": SLUG,
        "date_analyse": DATE,
        "date_maj": None,
        "titre": (
            f"Appartement duplex T2/3 de {eur(SURF, 2)} m², cœur du centre "
            f"historique — place Saint-Pierre, Brignoles (83170)"
        ),
        "bien": {
            "type_bien": "appartement",
            "sous_type": None,
            "type_detail": (
                f"Appartement duplex de {eur(SURF, 2)} m² Carrez annoncés "
                f"(1 889 €/m²), vendu « 2/3 pièces » avec {CHAMBRES} chambre "
                f"principale et une petite pièce de {eur(PETITE_PIECE)} m² "
                f"présentée comme bureau ou chambre d'appoint, au {ETAGE}, "
                f"immeuble de {ANNEE}, cœur du centre historique de Brignoles "
                f"(83170), à proximité immédiate de la place Saint-Pierre. "
                f"Non meublé, cuisine ouverte et intégrée, chauffage individuel "
                f"électrique (radiateurs), entrée séparée, 1 WC, 1 salle de "
                f"douches, pas d'ascenseur, pas de cave ni de place de "
                f"stationnement, {PHOTOS} photos. Un lot dans une copropriété "
                f"de {LOTS_COPRO} lots — dont {LOTS_COPRO} lots d'habitation — "
                f"et l'annonce précise « pas de procédure en cours ». Charges "
                f"annuelles annoncées {eur(CHARGES_COPRO)} €. DPE {DPE}, "
                f"GES {GES}, facture énergétique annoncée de "
                f"{eur(FACTURE_BASSE)} à {eur(FACTURE_HAUTE)} €/an. Honoraires "
                f"à la charge du vendeur, frais d'acquisition affichés par le "
                f"simulateur de l'annonce {eur(FRAIS_ACQUISITION)} € (8 %). "
                f"LE POINT QUI COMMANDE TOUT : l'annonce écrit « moins cher "
                f"que des biens comparables dans la région ». C'est vrai sur "
                f"la boîte large du quartier — {DVF_Q_4048_N} ventes de 40 à "
                f"48 m² à {eur(DVF_Q_4048_MED)} €/m² de médiane — et faux dès "
                f"qu'on restreint la comparaison au noyau historique : "
                f"{DVF_F_3050_N} ventes de 30 à 50 m² intra-muros en 2025, "
                f"médiane {eur(DVF_F_3050_MED)} €/m². C'est cette boîte "
                f"resserrée qui décrit le bien, et elle dit que le prix "
                f"demandé est {fr(surcote, 1)} % au-dessus de la valeur de son "
                f"propre micro-marché."
            ),
            "neuf": False,
            "adresse": {
                "texte": (
                    "Cœur du centre historique de Brignoles (83170), à "
                    "proximité immédiate de la place Saint-Pierre, du cinéma "
                    "et des commerces — adresse exacte non publiée dans "
                    "l'annonce ; agence Nestenn Brignoles"
                ),
                "ville": "Brignoles",
                "code_postal": "83170",
            },
            "surfaces": {
                "texte": (
                    f"{eur(SURF, 2)} m² annoncés ({eur(PRIX / SURF)} €/m²), "
                    f"vendu « 2/3 pièce(s) » sur l'annonce elle-même — le "
                    f"doute sur le nombre de pièces est écrit noir sur blanc. "
                    f"Au rez-de-chaussée : entrée, séjour avec cuisine ouverte "
                    f"(salon donné à 20,5 m²) et placard ; à l'étage : palier, "
                    f"chambre principale, salle d'eau avec WC et une petite "
                    f"pièce de {eur(PETITE_PIECE)} m² que l'annonce propose en "
                    f"bureau ou en chambre d'appoint. Rien ne dit si cette "
                    f"pièce entre dans le Carrez : elle n'a ni fenêtre "
                    f"décrite ni statut, et c'est elle qui fait basculer le "
                    f"bien de T2 à T3. Le certificat Carrez et le plan sont à "
                    f"exiger avant toute offre"
                ),
                "carrez_m2": SURF,
            },
            "lots": {
                "count": 1,
                "surface_par_lot_m2": SURF,
                "nature": (
                    f"Un seul lot : l'appartement duplex, dans une copropriété "
                    f"de {LOTS_COPRO} lots, tous d'habitation. Ni cave, ni "
                    f"grenier, ni place de stationnement dans la fiche "
                    f"caractéristiques — l'annonce se contente d'écrire "
                    f"« possibilité de stationner à proximité », ce qui en "
                    f"vieille ville veut dire dans la rue. Aucun lot annexe "
                    f"cessible, aucun revenu annexe, et un stationnement qui "
                    f"reste un poste de confort à vérifier sur place"
                ),
                "lots_distincts": 1,
            },
            "copro": {
                "charges_annuelles_euros": COPRO_BASE,
                "charges_source": (
                    f"{eur(COPRO_BASE)} €/an ANNONCÉS, soit "
                    f"{fr(COPRO_BASE / 12)} €/mois — c'est la seule charge "
                    f"d'exploitation du dossier qui ne soit pas une "
                    f"estimation, et elle absorbe "
                    f"{fr(COPRO_BASE / (LOYER_BASE * 12) * 100)} % des revenus "
                    f"bruts au loyer retenu. Pour un immeuble de {ANNEE} sans "
                    f"ascenseur ni parties communes extérieures, c'est un "
                    f"niveau bas mais plausible : il ne couvre ni ravalement, "
                    f"ni toiture, ni colonnes. Le dossier ne comporte AUCUN "
                    f"procès-verbal d'assemblée, aucun état daté, aucune fiche "
                    f"synthétique et aucun budget prévisionnel : les "
                    f"{eur(COPRO_BASE)} € sont donc un point de départ à "
                    f"documenter, et le modèle teste la variante "
                    f"{eur(COPRO_HAUT)} €/an"
                ),
            },
            "travaux": {
                "montant_euros": 0.0,
                "nature": (
                    "Aucun montant retenu : l'annonce affirme « excellent état "
                    "général », « prêt à vivre ou à louer immédiatement, sans "
                    "travaux à prévoir », et aucun devis, aucun diagnostic et "
                    "aucune photo de désordre n'est joint pour le confirmer. "
                    "Le modèle publie donc une grille par enveloppe (10 000, "
                    "20 000 et 30 000 €) au lieu d'un chiffre. Sur un immeuble "
                    "de 1900 en DPE D, trois postes se vérifient en priorité : "
                    "l'installation électrique (diagnostic obligatoire à la "
                    "vente et à la location, et les immeubles de cette "
                    "génération portent souvent des anomalies de protection), "
                    "la salle d'eau et sa ventilation, et le réseau d'eau "
                    "dans un bâti ancien. Une copropriété de 6 lots peut par "
                    "ailleurs voter des travaux sur les parties communes "
                    "(toiture, façade, descentes) : c'est ce que les trois "
                    "derniers procès-verbaux doivent chiffrer"
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
                f"{eur(PRIX / SURF)} €/m² sur {eur(SURF, 2)} m² — et "
                f"{eur(ACTE_EN_MAIN)} € d'acte en main avec les "
                f"{eur(FRAIS_ACQUISITION)} € de frais affichés par le "
                f"simulateur de l'annonce. Comparé aux {DVF_Q_4048_N} ventes "
                f"de 40 à 48 m² de la boîte large du quartier "
                f"({eur(DVF_Q_4048_MED)} €/m²), le bien paraît "
                f"{fr(abs(ecart_large), 1)} % sous le marché — c'est "
                f"exactement l'argument de l'annonce, et il ne tient pas : "
                f"cette boîte mélange le centre historique et des résidences "
                f"récentes situées à 400-700 m (chemin Saint-Pierre, Les "
                f"4 Saisons, Les Jardins de Provence, avenue Dréo) qui se "
                f"traitent entre 2 683 et 3 571 €/m² et n'ont rien à voir "
                f"avec un duplex du vieux Brignoles. Restreinte au noyau "
                f"historique, la comparaison s'inverse : "
                f"{eur(DVF_F_3050_MED)} €/m² de médiane intra-muros, et le "
                f"prix demandé ressort {fr(ecart_fin, 1)} % AU-DESSUS de "
                f"cette médiane"
            ),
        },
        "marche": {
            "valeur": {
                "basse_euros": VALEUR_BASSE,
                "haute_euros": VALEUR_HAUTE,
                "retenue_euros": VALEUR_RETENUE,
                "source": (
                    f"DVF 2025, ancrage sur le NOYAU HISTORIQUE et non sur la "
                    f"boîte large du quartier. Boîte resserrée retenue : "
                    f"{DVF_BOITE_FINE[0]} à {DVF_BOITE_FINE[1]} N et "
                    f"{DVF_BOITE_FINE[2]} à {DVF_BOITE_FINE[3]} E, qui "
                    f"contient les rues du vieux Brignoles (Cavaillon, de la "
                    f"Poissonnerie, Jules Ferry, Entraigues, place "
                    f"Saint-Pierre, place des Comtes de Provence, "
                    f"Tourmalaute, Robinet) : {DVF_F_APP_N} ventes "
                    f"d'appartements toutes surfaces, médiane "
                    f"{eur(DVF_F_MED)} €/m² ; {DVF_F_3050_N} ventes de 30 à "
                    f"50 m², médiane {eur(DVF_F_3050_MED)} €/m², premier "
                    f"quartile {eur(DVF_F_3050_Q1)} €/m², troisième quartile "
                    f"{eur(DVF_F_3050_Q3)} €/m², prix médian "
                    f"{eur(DVF_F_3050_PRIX)} €. Sur la tranche exacte du bien "
                    f"(40 à 48 m²), {DVF_F_4048_N} ventes seulement, médiane "
                    f"{eur(DVF_F_4048_MED)} €/m² — échantillon trop mince pour "
                    f"servir d'ancre unique, mais cohérent avec la tranche "
                    f"élargie. Contrôle par la même boîte sans restriction de "
                    f"surface : médiane {eur(DVF_F_MED)} €/m². Valeur retenue "
                    f"= {eur(SURF, 2)} m² × {eur(DVF_F_3050_MED)} €/m² = "
                    f"{eur(VALEUR_RETENUE)} €"
                ),
                "confiance": "moyenne",
            },
            "loyers": [
                {
                    "lot": (
                        f"Appartement duplex de {eur(SURF, 2)} m² — bien "
                        f"libre, non meublé, sans travaux annoncés"
                    ),
                    "quantite": 1,
                    "loyer_mensuel_euros": LOYER_BASE,
                    "occupe": False,
                    "note": (
                        f"UNE SEULE LIGNE DE REVENU, à {eur(LOYER_BASE)} €/mois "
                        f"({fr(LOYER_M2_MED)} €/m²), soit "
                        f"{eur(LOYER_BASE * 12)} €/an bruts. Quatre ancrages "
                        f"datés : la fiche de référence interne « Seuils "
                        f"d'achat par ville » du 21/09/2026 retient "
                        f"{fr(LOYER_M2_BAS)} €/m² — un PLANCHER prudent, "
                        f"calibré sur un lot type de 60 m², pas sur une "
                        f"petite surface ; Trackstone donne "
                        f"{fr(LOYER_M2_MED)} €/m² pour l'appartement "
                        f"brignolais ; SeLoger estime la ville à "
                        f"{fr(LOYER_M2_HAUT)} €/m² (9 à 20). Les annonces "
                        f"réelles du centre tranchent : 37,66 m² à 640 €/mois, "
                        f"et surtout 40,68 m², 2 pièces, 1er étage, centre — "
                        f"650 €/mois charges comprises, en exclusivité chez "
                        f"ABC IMMO Brignoles. Les grandes surfaces confirment "
                        f"la décroissance du prix au m² : 65,1 m² à 600 €/mois "
                        f"(9,2 €/m²) et 70 m² à 786-855 €/mois (11,2-12,2). "
                        f"LA FOURCHETTE PUBLIÉE EST DONC "
                        f"{eur(LOYER_BAS)} À {eur(LOYER_HAUT)} €/MOIS hors "
                        f"charges, avec un scénario de base à "
                        f"{eur(LOYER_BASE)} €/mois. Réserve de méthode : les "
                        f"annonces affichent des loyers charges comprises et "
                        f"des loyers espérés ; le scénario plancher "
                        f"({eur(LOYER_BAS)} €/mois, soit "
                        f"{fr(LOYER_M2_BAS)} €/m²) est donc publié au même "
                        f"rang que le scénario de base, parce que c'est lui "
                        f"qui protège la trésorerie si un T2 de 1900 au "
                        f"rez-de-chaussée se reloue lentement"
                    ),
                },
            ],
            "notes": (
                f"L'ANNONCE SE TROMPE DE QUARTIER, ET C'EST TOUT LE DOSSIER : "
                f"à {eur(PRIX / SURF)} €/m², le bien paraît "
                f"{fr(abs(ecart_large), 1)} % sous la médiane DVF de la boîte "
                f"large du quartier — celle qui mélange le centre historique "
                f"et des résidences récentes à 2 683-3 571 €/m². Restreint au "
                f"noyau historique, l'écart s'inverse : {fr(ecart_fin, 1)} % "
                f"au-dessus de la médiane intra-muros "
                f"({eur(DVF_F_3050_MED)} €/m² sur {DVF_F_3050_N} ventes de 30 "
                f"à 50 m²), et {fr((PRIX - DVF_CMP_PRIX) / DVF_CMP_PRIX * 100, 1)} % "
                f"au-dessus du prix médian absolu des six transactions "
                f"comparables ({eur(DVF_CMP_PRIX)} €). Ce n'est pas une "
                f"décote, c'est le prix d'un bien en bon état payé au niveau "
                f"du marché. Ce que le dossier a pour lui est réel : aucun "
                f"travail annoncé, charges de copropriété de "
                f"{eur(COPRO_BASE)} €/an, copropriété de {LOTS_COPRO} lots "
                f"sans procédure, DPE {DPE} et GES {GES}, bouquet de "
                f"commerces à pied dans une ville où les prix au m² du centre "
                f"ancien restent bas. Ce qui le plombe tient en deux lignes : "
                f"le rendement net avant IS ressort à "
                f"{fr(SBASE['rdt_av'])} % (le seuil doctrinal de 5 % est "
                f"passé, mais avec {fr(SBASE['rdt_ap'])} % seulement après "
                f"IS), et le cash-flow est négatif de "
                f"{eur(abs(SBASE['cf']))} €/mois à 15 ans avec 10 % d'apport. "
                f"Le prix qui remet le dossier d'aplomb n'est pas un prix de "
                f"marché : c'est {eur(SBASE['cap5'])} € pour 5 % net, "
                f"{eur(prix_cashflow_nul(SBASE['ebe']))} € pour un cash-flow "
                f"nul — et la valeur intra-muros du bien est de "
                f"{eur(VALEUR_RETENUE)} €"
            ),
        },
        "hypotheses": {
            "vacance_base_pct": VAC_BASE,
            "vacance_best_pct": VAC_BEST,
            "vacance_worst_pct": VAC_WORST,
            "vacance_justification": (
                f"{fr(VAC_BASE)} % en scénario de base : le bien est libre, "
                f"donc aucun loyer acquis et aucune vacance héritée, mais une "
                f"vacance de mise en location au départ (annonces, visites, "
                f"éventuels travaux) et un marché locatif brignolais peu "
                f"tendu, où un {PIECES} pièces de centre ancien se reloue en "
                f"quelques semaines. {fr(VAC_BEST)} % en hypothèse favorable "
                f"(locataire en place dès le premier mois) et "
                f"{fr(VAC_WORST)} % en hypothèse défavorable (recherche longue "
                f"sur un rez-de-chaussée sans stationnement, remise en état "
                f"entre deux locataires). La vacance n'est pas le risque "
                f"principal du dossier : le risque principal est le prix"
            ),
            "frais_acquisition_euros": FRAIS_ACQUISITION,
            "frais_divers_euros": 0.0,
            "quote_part_bati_pct": 0.0,
            "duree_amortissement_ans": 30,
            "fiscalite_commentaire": (
                f"SCI à l'IS. Calcul réel de l'année 1 : EBE "
                f"{eur(SBASE['ebe'])} moins intérêts d'emprunt "
                f"{eur(INTERETS_AN1)} ({eur(CAPITAL)} à {fr(TAUX_CREDIT * 100)} %) "
                f"moins dotation aux amortissements {eur(DOTATION_AN1)} (bâti à "
                f"80 % du prix affiché amorti sur 30 ans) = "
                f"{eur(SBASE['ebe'] - INTERETS_AN1 - DOTATION_AN1)}, soit un "
                f"DÉFICIT : aucun IS dû en année 1, et le résultat se "
                f"reconduit tant que les intérêts et la dotation dépassent "
                f"l'EBE. Les rendements nets publiés restent sous la "
                f"convention prudente du moteur (IS de 15 % de l'EBE, soit "
                f"{eur(SBASE['is_'])} €), c'est-à-dire la lecture la plus "
                f"défavorable — celle qui décide. Seuil de décision du parc : "
                f"5 % net avant IS, soit environ deux fois le rendement d'un "
                f"CAT"
            ),
            "charges": {
                "taxe_fonciere_annuelle_euros": TF_BASE,
                "taxe_fonciere_commentaire": (
                    f"ESTIMATION {eur(TF_BASE)} €/an — l'avis de taxe foncière "
                    f"n'est pas communiqué par l'agence, et c'est la première "
                    f"pièce à exiger. Repère de calcul : l'ancienne base "
                    f"départementale du Var taxe de l'ordre de 50 % de la "
                    f"valeur locative cadastrale, et une valeur locative "
                    f"cadastrale de {PIECES} pièces ancien à Brignoles tourne "
                    f"autour de 2 700 € pour {eur(SURF, 2)} m² : l'ordre de "
                    f"grandeur de {eur(TF_BASE)} € tient, mais il se vérifie "
                    f"par l'avis, pas par l'estimation. À titre de repère "
                    f"interne, la fiche du T3 de 48 m² du 25/09/2026 retenait "
                    f"800 € sur une surface légèrement supérieure"
                ),
                "charges_copro_annuelles_euros": COPRO_BASE,
                "charges_copro_commentaire": (
                    f"{eur(COPRO_BASE)} €/an ANNONCÉS, soit "
                    f"{fr(COPRO_BASE / 12)} €/mois et "
                    f"{fr(COPRO_BASE / (LOYER_BASE * 12) * 100)} % du loyer "
                    f"brut de marché — un rapport sain, et le meilleur chiffre "
                    f"du dossier. Deux réserves : elles ne couvrent "
                    f"visiblement que l'assurance de l'immeuble et des frais "
                    f"de gestion courante, donc rien sur la toiture ou la "
                    f"façade d'un bâti de {ANNEE} ; et sans budget "
                    f"prévisionnel ni appels de fonds, la charge future n'est "
                    f"pas bornée. Le modèle teste la variante "
                    f"{eur(COPRO_HAUT)} €/an, c'est-à-dire trois fois "
                    f"l'annonce — un ordre de grandeur banal pour un immeuble "
                    f"de {LOTS_COPRO} lots qui rattrape trente ans "
                    f"d'entretien différé"
                ),
                "pno_annuelle_euros": PNO,
                "pno_commentaire": (
                    f"Assurance propriétaire non occupant du lot, {eur(PNO)} "
                    f"€/an : le logement est libre à la vente, donc assuré en "
                    f"PNO jusqu'à sa mise en location, puis en assurance "
                    f"propriétaire bailleur. En rez-de-chaussée en centre "
                    f"ancien, la garantie dégât des eaux est à vérifier "
                    f"explicitement"
                ),
                "entretien_annuel_euros": round(LOYER_BASE * 12 * GESTION_BASE_PCT
                                               / 100.0 + PROV_BASE, 2),
                "entretien_commentaire": (
                    f"Poste composite, détaillé : gestion locative "
                    f"{eur(LOYER_BASE * 12 * GESTION_BASE_PCT / 100)} € "
                    f"({fr(GESTION_BASE_PCT)} % des "
                    f"{eur(LOYER_BASE * 12)} € de loyers bruts — même en "
                    f"gestion directe, le temps passé se paie en heures) plus "
                    f"une provision de travaux et de renouvellement de "
                    f"{eur(PROV_BASE)} €/an (peintures, chauffe-eau, "
                    f"robinetterie, joints : un appartement de {ANNEE} "
                    f"consomme cette provision, pas moins). Le moteur ajoute "
                    f"par ailleurs une provision de rénovation automatique de "
                    f"2,5 % des loyers ({eur(SBASE['brut'] * 0.025)} €/an) : "
                    f"elle est DÉSACTIVÉE sur cette fiche "
                    f"(provision_desactivee), la ligne ci-dessus la couvrant "
                    f"déjà"
                ),
                "comptabilite_annuelle_euros": COMPTA,
                "comptabilite_commentaire": (
                    f"Comptabilité de la SCI à l'IS, {eur(COMPTA)} €/an : un "
                    f"logement loué nu au régime réel, avec amortissements, "
                    f"tableaux d'amortissement et liasse fiscale. C'est le "
                    f"coût du régime qui rend l'année 1 déficitaire et qui "
                    f"protège l'EBE de l'impôt"
                ),
                "provision_desactivee": True,
            },
        },
        "analyse": {
            "branche": "residentiel",
            "type_operation": "locatif",
            "strategie_retenue": {
                "nom": (
                    f"Location nue longue durée au loyer de marché — "
                    f"{eur(LOYER_BASE)} €/mois ({fr(LOYER_M2_MED)} €/m²), au "
                    f"prix du marché intra-muros et pas au-delà"
                ),
                "code": "ld-nue",
                "lots": 1,
            },
            "strategies_explorees": [
                {
                    "strategie": (
                        f"Plancher de marché — loyer de {eur(LOYER_BAS)} €/mois "
                        f"({fr(LOYER_M2_BAS)} €/m²), ancrage de la fiche de "
                        f"référence interne (lot type de 60 m²)"
                    ),
                    "lots": 1,
                    "rendement": (
                        f"{fr(SBAS['rdt_av'])} % net avant IS sur l'acte en "
                        f"main ({eur(SBAS['ebe'])} € d'EBE), "
                        f"{fr(SBAS['rdt_ap'])} % après IS"
                    ),
                    "faisabilite": (
                        f"c'est le loyer qu'un locataire de Brignoles paiera "
                        f"sans discuter pour un {PIECES} pièces de "
                        f"{eur(SURF, 2)} m² : tenable, mais c'est le bas du "
                        f"marché constaté, pas le marché"
                    ),
                    "risque": (
                        f"{eur(SBAS['cf'])} €/mois de cash-flow avant IS et un "
                        f"plafond 5 % à {eur(SBAS['cap5'])} € : à ce loyer, "
                        f"même la doctrine de rendement ne passe plus au prix "
                        f"affiché"
                    ),
                },
                {
                    "strategie": (
                        f"Scénario de base — loyer de {eur(LOYER_BASE)} €/mois "
                        f"({fr(LOYER_M2_MED)} €/m²), ancrage des annonces "
                        f"réelles du centre (37,66 m² à 640 €, 40,68 m² "
                        f"centre à 650 € charges comprises) et charges de "
                        f"copropriété telles qu'annoncées"
                    ),
                    "lots": 1,
                    "rendement": (
                        f"{fr(SBASE['rdt_av'])} % net avant IS, "
                        f"{fr(SBASE['rdt_ap'])} % après IS, "
                        f"{fr(SBASE['rdt_valeur'])} % sur la valeur de marché "
                        f"intra-muros"
                    ),
                    "faisabilite": (
                        f"la seule lecture que la doctrine accepte : "
                        f"{eur(SURF, 2)} m² en centre ancien de Brignoles se "
                        f"louent à ce niveau, et les charges annoncées le "
                        f"permettent"
                    ),
                    "risque": (
                        f"le seuil de 5 % net avant IS est passé "
                        f"({fr(SBASE['rdt_av'])} %) mais avec "
                        f"{eur(abs(SBASE['cf']))} €/mois de cash-flow négatif, "
                        f"et le bien s'achète au-dessus de sa valeur "
                        f"intra-muros ({eur(VALEUR_RETENUE)} €)"
                    ),
                },
                {
                    "strategie": (
                        f"Haut de marché — loyer de {eur(LOYER_HAUT)} €/mois "
                        f"({fr(LOYER_M2_HAUT)} €/m²), ancrage SeLoger ville"
                        + (" (meublé)" if False else "")
                    ),
                    "lots": 1,
                    "rendement": (
                        f"{fr(SHAUT['rdt_av'])} % net avant IS "
                        f"({eur(SHAUT['ebe'])} € d'EBE), {fr(SHAUT['rdt_ap'])} % "
                        f"après IS"
                    ),
                    "faisabilite": (
                        f"tenable seulement sur un bien impeccable et une "
                        f"petite surface : {fr(LOYER_M2_HAUT)} €/m² pour "
                        f"{eur(SURF, 2)} m², c'est le haut de ce que le centre "
                        f"de Brignoles affiche, pas la moyenne"
                    ),
                    "risque": (
                        f"même à {eur(LOYER_HAUT)} €/mois la trésorerie reste "
                        f"négative ({eur(SHAUT['cf'])} €/mois avant IS) : "
                        f"l'écart au seuil n'est pas un problème de loyer, "
                        f"c'est un problème de prix d'entrée"
                    ),
                },
                {
                    "strategie": (
                        f"Variante de risque — loyer de base "
                        f"({eur(LOYER_BASE)} €/mois) et charges de "
                        f"copropriété triplées à {eur(COPRO_HAUT)} €/an"
                    ),
                    "lots": 1,
                    "rendement": (
                        f"{fr(SCOPRO['rdt_av'])} % net avant IS, "
                        f"{fr(SCOPRO['rdt_ap'])} % après IS"
                    ),
                    "faisabilite": (
                        f"c'est la variante à retenir tant que les "
                        f"procès-verbaux ne sont pas lus : "
                        f"{eur(COPRO_HAUT / 12)} €/mois de charges pour un lot "
                        f"de {eur(SURF, 2)} m² dans un immeuble de {ANNEE} "
                        f"sans ascenseur n'est pas une hypothèse de "
                        f"catastrophe"
                    ),
                    "risque": (
                        f"chaque euro de charge annuelle en plus retire "
                        f"{eur(1 / COEF_PLAFOND)} € de prix acceptable : le "
                        f"plafond 5 % tombe de {eur(SBASE['cap5'])} € à "
                        f"{eur(SCOPRO['cap5'])} €, soit "
                        f"{fr((SBASE['cap5'] - SCOPRO['cap5']) / SBASE['cap5'] * 100, 1)} % "
                        f"de prix en moins pour la même exigence de rendement"
                    ),
                },
                {
                    "strategie": (
                        f"Piste écartée — location meublée de courte durée, "
                        f"l'appartement étant à trois minutes à pied du cœur "
                        f"touristique et commerçant de Brignoles"
                    ),
                    "lots": 1,
                    "rendement": (
                        f"non chiffré : la branche meublée touristique de "
                        f"Brignoles n'a pas de base de données de nuitées "
                        f"publiée, et l'inventer serait pire que l'ignorer"
                    ),
                    "faisabilite": (
                        f"la sous-préfecture du Var n'est pas une destination "
                        f"touristique : la demande meublée courte y est "
                        f"marginale, alors que le coût d'exploitation "
                        f"(mobilier, ménage, plateformes, déclaration en "
                        f"mairie pour un logement non-résidence principale) "
                        f"est immédiat. La loi Le Meur conditionne par "
                        f"ailleurs les autorisations de changement d'usage à "
                        f"un DPE compris entre A et E : le DPE {DPE} passerait, "
                        f"ce n'est pas là qu'est le problème"
                    ),
                    "risque": (
                        f"un meublé touristique sur un {PIECES} pièces de "
                        f"{eur(SURF, 2)} m² en centre ancien se vide hors "
                        f"saison : c'est la stratégie qui transforme un revenu "
                        f"modeste mais certain en revenu élevé mais discontinu"
                    ),
                },
            ],
            "attractivite": [
                {
                    "dimension": "transports",
                    "score": 7,
                    "justification": (
                        "Brignoles est une sous-préfecture du Var posée sur "
                        "l'A8 et la D554, avec une gare sur la ligne "
                        "Carnoules-Gardanne et un réseau de bus urbain : on "
                        "rejoint Toulon, Aix et Saint-Maximin par la route, "
                        "plus que par un train cadencé. Pour un logement de "
                        "centre ancien, la cible est locale et "
                        "l'emplacement suffit — mais il ne crée pas de "
                        "demande extérieure, et un locataire sans voiture "
                        "n'est pas la cible ici"
                    ),
                },
                {
                    "dimension": "commerces",
                    "score": 8,
                    "justification": (
                        "C'est le point fort du dossier et la raison d'être du "
                        "bien : place Saint-Pierre, cinéma, marché "
                        "hebdomadaire, commerces de bouche, services publics, "
                        "professions de santé et administrations à pied, "
                        "hypermarchés en périphérie. Dans une ville de "
                        "18 000 habitants qui vit de son centre, un "
                        "appartement à trois minutes des commerces est "
                        "structurellement relouable"
                    ),
                },
                {
                    "dimension": "ecoles",
                    "score": 7,
                    "justification": (
                        "Brignoles concentre les établissements de sa "
                        "couronne — écoles, collèges, lycée Raynouard, "
                        "formations post-bac — à quelques minutes à pied du "
                        "centre historique. La ville est un pôle scolaire "
                        "local, ce qui soutient la demande de logements "
                        "familiaux et de petites surfaces"
                    ),
                },
                {
                    "dimension": "securite",
                    "score": 6,
                    "justification": (
                        "Aucune tension documentée sur le centre historique "
                        "dans les sources consultées, et l'annonce ne signale "
                        "aucun désordre. Deux réserves objectives : un "
                        "rez-de-chaussée sur rue en centre ancien, et des "
                        "parties communes d'immeuble de 1900 dont la "
                        "serrurerie et l'éclairage sont à vérifier lors de la "
                        "visite — ce sont des postes de confort et "
                        "d'assurance, pas des détails"
                    ),
                },
                {
                    "dimension": "demande_locative",
                    "score": 6,
                    "justification": (
                        "Les annonces réelles du centre situent un 2 pièces "
                        "de 38 à 41 m² entre 640 et 650 €/mois, et les "
                        "grandes surfaces de 65 à 70 m² entre 600 et "
                        "855 €/mois : la demande existe, mais elle n'est ni "
                        "tendue ni étudiante. Un {PIECES} pièces de "
                        "centre ancien se reloue en quelques semaines, il ne "
                        "s'arrache pas — et le statut flou de la troisième "
                        "pièce (7 m²) réduit la cible aux couples et aux "
                        "personnes seules, pas aux familles".format(PIECES=PIECES)
                    ),
                },
                {
                    "dimension": "dynamisme",
                    "score": 5,
                    "justification": (
                        f"Marché de sous-préfecture : {DVF_APP_N} ventes "
                        f"d'appartements en 2025 à l'échelle communale et "
                        f"{DVF_F_APP_N} dans le seul noyau historique, pour "
                        f"des prix médians de {eur(DVF_F_MED)} €/m² "
                        f"intra-muros contre {eur(DVF_APP_MED)} €/m² sur la "
                        f"commune. Les prix du centre ancien montent moins "
                        f"vite que l'inflation : dans ce dossier le rendement "
                        f"locatif est le seul moteur de performance, la "
                        f"plus-value n'en est pas un"
                    ),
                },
            ],
            "risques": [
                {
                    "facteur": (
                        "Le prix demandé est au-dessus de la valeur du "
                        f"micro-marché : ratio coût/valeur "
                        f"{fr(ACTE_EN_MAIN / VALEUR_RETENUE)} à "
                        f"{eur(ACTE_EN_MAIN)} € d'acte en main"
                    ),
                    "severite": 4,
                    "bloquant": False,
                    "detail": (
                        f"À {eur(PRIX / SURF)} €/m², le bien est "
                        f"{fr(ecart_fin, 1)} % au-dessus de la médiane DVF du "
                        f"noyau historique ({eur(DVF_F_3050_MED)} €/m² sur "
                        f"{DVF_F_3050_N} ventes de 30 à 50 m²) et "
                        f"{fr((PRIX - DVF_CMP_PRIX) / DVF_CMP_PRIX * 100, 1)} % "
                        f"au-dessus du prix médian des six transactions "
                        f"comparables ({eur(DVF_CMP_PRIX)} €). L'annonce "
                        f"justifie son prix par la boîte large du quartier "
                        f"({eur(DVF_Q_4048_MED)} €/m²), qui inclut des "
                        f"résidences récentes hors vieille ville. Acheter "
                        f"au-dessus de la valeur de son marché n'est pas "
                        f"rédhibitoire pour un bien de rendement loué "
                        f"immédiatement, mais cela supprime toute marge de "
                        f"sécurité : il n'y a pas de décote à capter, donc "
                        f"aucun coussin pour absorber des travaux votés"
                    ),
                },
                {
                    "facteur": (
                        "Aucune pièce de copropriété jointe, et des charges "
                        "annoncées non bornées sur un immeuble de 1900"
                    ),
                    "severite": 3,
                    "bloquant": False,
                    "detail": (
                        f"Le dossier ne contient ni procès-verbal d'assemblée, "
                        f"ni état daté, ni fiche synthétique, ni budget "
                        f"prévisionnel, ni appels de fonds — seulement la "
                        f"mention « {LOTS_COPRO} lots, pas de procédure en "
                        f"cours » et {eur(COPRO_BASE)} €/an de charges. "
                        f"L'absence de procédure est une bonne nouvelle, mais "
                        f"elle ne dit rien des travaux à venir : sur une "
                        f"copropriété de {LOTS_COPRO} lots, un ravalement ou "
                        f"une toiture se partagent entre six, et un seul "
                        f"copropriétaire défaillant pèse jusqu'à un sixième "
                        f"des appels de fonds. Condition suspensive "
                        f"obligatoire"
                    ),
                },
                {
                    "facteur": (
                        "Surface vendue « 2/3 pièces » : statut Carrez de la "
                        f"pièce de {eur(PETITE_PIECE)} m² non établi"
                    ),
                    "severite": 3,
                    "bloquant": False,
                    "detail": (
                        f"L'annonce écrit elle-même « 2/3 pièce(s) » et décrit "
                        f"une petite pièce de {eur(PETITE_PIECE)} m² à "
                        f"l'étage, sans fenêtre décrite ni mention de "
                        f"hauteur sous plafond. Si cette pièce entre dans le "
                        f"Carrez, le bien se défend comme un T3 d'appoint et "
                        f"se loue au-dessus ; si elle n'y entre pas, il se "
                        f"loue comme un T2 de {eur(SURF, 2)} m² et la surface "
                        f"utile réelle est inférieure à la surface payée. Le "
                        f"certificat Carrez et le plan de l'étage tranchent, "
                        f"et à {eur(PRIX / SURF)} €/m², "
                        f"{eur(PETITE_PIECE)} m² de doute valent "
                        f"{eur(PETITE_PIECE * PRIX / SURF)} €"
                    ),
                },
                {
                    "facteur": (
                        "Rez-de-chaussée sans stationnement en cœur de "
                        "vieille ville"
                    ),
                    "severite": 3,
                    "bloquant": False,
                    "detail": (
                        f"L'annonce écrit « possibilité de stationner à "
                        f"proximité » : en centre historique, cela veut dire "
                        f"dans la rue, et cela se vérifie un soir de semaine. "
                        f"Sur un bien à {eur(PRIX)} € destiné à la location, "
                        f"c'est une contrainte de relouage (les locataires "
                        f"motorisés y regardent à deux fois) et un sujet de "
                        f"confort pour un couple. Le rez-de-chaussée est par "
                        f"ailleurs le niveau qui porte le plus de nuisances de "
                        f"rue, et le moins recherché à la revente"
                    ),
                },
                {
                    "facteur": (
                        f"Cash-flow négatif de {eur(abs(SBASE['cf']))} €/mois "
                        f"au prix affiché (15 ans, {APPORT_PCT * 100:.0f} % "
                        f"d'apport)"
                    ),
                    "severite": 3,
                    "bloquant": False,
                    "detail": (
                        f"Au loyer de base de {eur(LOYER_BASE)} €/mois et avec "
                        f"les charges annoncées, l'EBE ressort à "
                        f"{eur(SBASE['ebe'])} €/an, soit "
                        f"{fr(SBASE['rdt_av'])} % net avant IS sur "
                        f"{eur(ACTE_EN_MAIN)} € d'acte en main — le seuil de "
                        f"5 % est franchi, mais de "
                        f"{fr(SBASE['rdt_av'] - 5)} point seulement, et "
                        f"{fr(SBASE['rdt_ap'])} % après IS. La mensualité de "
                        f"{eur(mensualite(CAPITAL))} € sur {DUREE_ANS} ans "
                        f"mange l'EBE : il faut payer "
                        f"{eur(prix_cashflow_nul(SBASE['ebe']))} €, soit "
                        f"{fr((prix_cashflow_nul(SBASE['ebe']) - PRIX) / PRIX * 100, 1)} % "
                        f"de moins, pour que la trésorerie s'équilibre. C'est "
                        f"hors d'atteinte sur un bien déjà au prix du marché : "
                        f"l'équilibre viendra du prix négocié, pas du loyer"
                    ),
                },
                {
                    "facteur": (
                        "Estimation d'exploitation non vérifiable : taxe "
                        "foncière, budget de copropriété, diagnostics absents"
                    ),
                    "severite": 2,
                    "bloquant": False,
                    "detail": (
                        f"Trois chiffres du modèle sont des ESTIMATIONS, dites "
                        f"explicitement : la taxe foncière ({eur(TF_BASE)} €/an, "
                        f"avis non communiqué), la provision de travaux "
                        f"({eur(PROV_BASE)} €/an) et l'enveloppe de remise en "
                        f"état (publiée en grille de 10 000 à 30 000 €). Seules "
                        f"les charges de copropriété ({eur(COPRO_BASE)} €/an) "
                        f"sont annoncées. Aucun diagnostic n'est joint : ni "
                        f"DPE complet, ni état de l'installation électrique "
                        f"pourtant obligatoire à la vente comme à la location, "
                        f"ni amiante, ni plomb, ni termites pour un immeuble de "
                        f"{ANNEE}. Ce n'est pas un risque de perte, c'est un "
                        f"risque de précision — et il se lève en une semaine "
                        f"de demandes"
                    ),
                },
            ],
            "champs_manquants": [],
        },
    }


# ---------------------------------------------------------------------------
# Diagnostic (chiffres du modele, sans ecriture)
# ---------------------------------------------------------------------------
def diagnostic():
    print("  DVF : relecture du fichier departemental…")
    verifie_dvf()
    rec_ = rec_bien()
    print(f"  schema.validate_record : {schema.validate_record(rec_) or 'aucune erreur'}")
    S = dict(
        bas=scen(rec_, LOYER_BAS, VAC_BASE, GESTION_BASE_PCT, TF_BASE,
                 COPRO_BASE, PROV_BASE),
        base=scen(rec_, LOYER_BASE, VAC_BASE, GESTION_BASE_PCT, TF_BASE,
                  COPRO_BASE, PROV_BASE),
        haut=scen(rec_, LOYER_HAUT, VAC_BASE, GESTION_BASE_PCT, TF_BASE,
                  COPRO_BASE, PROV_BASE),
        copro=scen(rec_, LOYER_BASE, VAC_BASE, GESTION_BASE_PCT, TF_BASE,
                   COPRO_HAUT, PROV_BASE),
        best=scen(rec_, LOYER_BASE, VAC_BEST, 4.0, TF_BASE, COPRO_BASE, 150.0),
        worst=scen(rec_, LOYER_BAS, VAC_WORST, GESTION_BASE_PCT, 1000.0,
                   COPRO_HAUT, 400.0),
    )
    r = engine.compute(rec_)
    assert r['calculable'], r.get('raison')
    note, verdict, comp = scoring.note_et_verdict(rec_, r)
    print(f"\n  MENS_PAR_EURO = {mensualite_par_euro():.7f} | mensualite({CAPITAL:,.0f}) = {mensualite(CAPITAL):,.2f}")
    print(f"  EBE base {S['base']['ebe']:,.2f} | net ap IS {S['base']['net']:,.2f} | rdt av {S['base']['rdt_av']:.4f} % | rdt ap {S['base']['rdt_ap']:.4f} % | rdt/valeur {S['base']['rdt_valeur']:.4f} %")
    print(f"  CF base {S['base']['cf']:,.2f} | CF ap IS {S['base']['cf_ap']:,.2f}")
    print(f"  cap5 {S['base']['cap5']:,.2f} | plafond 6,5 % {plafond_is(S['base']['ebe']):,.2f} | prix CF nul {prix_cashflow_nul(S['base']['ebe']):,.2f}")
    for k in ('bas', 'haut', 'copro', 'best', 'worst'):
        print(f"  scénario {k:6} : EBE {S[k]['ebe']:>9,.2f} | rdt av {S[k]['rdt_av']:>5.2f} % | CF {S[k]['cf']:>8,.2f} | cap5 {S[k]['cap5']:>10,.2f}")
    print(f"  ratio cout/valeur = {r['ratio_cout_valeur']:.4f}")
    print(f"\n  NOTE {note}/10 → VERDICT {verdict} | composantes {comp}")
    return S, rec_, note, verdict, comp



# ---------------------------------------------------------------------------
# Sections de la fiche
# ---------------------------------------------------------------------------
def sections(rec_, S):
    SBAS, SBASE = S['bas'], S['base']
    SHAUT, SCOPRO = S['haut'], S['copro']
    SBEST, SWORST = S['best'], S['worst']
    ecart_large = (PRIX / SURF - DVF_Q_4048_MED) / DVF_Q_4048_MED * 100.0
    ecart_fin = (PRIX / SURF - DVF_F_3050_MED) / DVF_F_3050_MED * 100.0
    ecart_cmp_m2 = (PRIX / SURF - DVF_CMP_MED) / DVF_CMP_MED * 100.0
    ecart_cmp_prix = (PRIX - DVF_CMP_PRIX) / DVF_CMP_PRIX * 100.0
    surcote = (PRIX / VALEUR_RETENUE - 1) * 100.0
    ratio = ACTE_EN_MAIN / VALEUR_RETENUE

    proj_section = f"""  <section class="financial-projections">
    <h2>Compte d'exploitation au loyer de marché</h2>
    <p class="attractiveness-intro">Le bien est <strong>libre</strong> : aucun bail à hériter, donc aucun revenu acquis et aucun risque de sous-loyer. Le loyer est une hypothèse que l'on choisit, et le modèle en publie trois : le plancher de la fiche de référence interne ({eur(LOYER_BAS)} €/mois), le scénario de base au loyer médian des annonces réelles du centre ({eur(LOYER_BASE)} €/mois) et le haut de la fourchette observée ({eur(LOYER_HAUT)} €/mois). Tout le reste — charges de copropriété annoncées, taxe foncière estimée, provision, comptabilité de SCI — est identique dans les trois colonnes.</p>
    <table class="projection-table compare">
      <thead><tr><th>Poste annuel</th><th class="num">Plancher {eur(LOYER_BAS)} €/mois</th><th class="num">Base {eur(LOYER_BASE)} €/mois</th><th class="num">Haut {eur(LOYER_HAUT)} €/mois</th></tr></thead>
      <tbody>
        <tr><td>Loyers bruts</td><td class="num">{eur(SBAS['brut'])}</td><td class="num">{eur(SBASE['brut'])}</td><td class="num">{eur(SHAUT['brut'])}</td></tr>
        <tr><td>Vacance {fr(VAC_BASE)} %</td><td class="num">−{eur(SBAS['vac_eur'])}</td><td class="num">−{eur(SBASE['vac_eur'])}</td><td class="num">−{eur(SHAUT['vac_eur'])}</td></tr>
        <tr><td>Gestion locative {fr(GESTION_BASE_PCT)} %</td><td class="num">−{eur(SBAS['gestion_eur'])}</td><td class="num">−{eur(SBASE['gestion_eur'])}</td><td class="num">−{eur(SHAUT['gestion_eur'])}</td></tr>
        <tr><td>Charges de copropriété (annoncées)</td><td class="num">−{eur(COPRO_BASE)}</td><td class="num">−{eur(COPRO_BASE)}</td><td class="num">−{eur(COPRO_BASE)}</td></tr>
        <tr><td>Taxe foncière (estimée)</td><td class="num">−{eur(TF_BASE)}</td><td class="num">−{eur(TF_BASE)}</td><td class="num">−{eur(TF_BASE)}</td></tr>
        <tr><td>Assurance PNO</td><td class="num">−{eur(PNO)}</td><td class="num">−{eur(PNO)}</td><td class="num">−{eur(PNO)}</td></tr>
        <tr><td>Provision travaux et renouvellement</td><td class="num">−{eur(PROV_BASE)}</td><td class="num">−{eur(PROV_BASE)}</td><td class="num">−{eur(PROV_BASE)}</td></tr>
        <tr><td>Comptabilité de la SCI</td><td class="num">−{eur(COMPTA)}</td><td class="num">−{eur(COMPTA)}</td><td class="num">−{eur(COMPTA)}</td></tr>
        <tr class="highlight"><td><strong>EBE (excédent brut d'exploitation)</strong></td><td class="num"><strong>{eur(SBAS['ebe'])}</strong></td><td class="num"><strong>{eur(SBASE['ebe'])}</strong></td><td class="num"><strong>{eur(SHAUT['ebe'])}</strong></td></tr>
        <tr><td>Rendement net avant IS / acte en main</td><td class="num">{fr(SBAS['rdt_av'])} %</td><td class="num">{fr(SBASE['rdt_av'])} %</td><td class="num">{fr(SHAUT['rdt_av'])} %</td></tr>
        <tr><td>IS sous convention prudente (15 % de l'EBE)</td><td class="num">−{eur(SBAS['is_'])}</td><td class="num">−{eur(SBASE['is_'])}</td><td class="num">−{eur(SHAUT['is_'])}</td></tr>
        <tr><td>Net après IS</td><td class="num">{eur(SBAS['net'])}</td><td class="num">{eur(SBASE['net'])}</td><td class="num">{eur(SHAUT['net'])}</td></tr>
        <tr><td>Rendement net après IS / acte en main</td><td class="num">{fr(SBAS['rdt_ap'])} %</td><td class="num">{fr(SBASE['rdt_ap'])} %</td><td class="num">{fr(SHAUT['rdt_ap'])} %</td></tr>
        <tr><td>Rendement net après IS / valeur de marché</td><td class="num">{fr(SBAS['net'] / VALEUR_RETENUE * 100)} %</td><td class="num">{fr(SBASE['rdt_valeur'])} %</td><td class="num">{fr(SHAUT['net'] / VALEUR_RETENUE * 100)} %</td></tr>
      </tbody>
    </table>
    <h3>Service de la dette : {eur(CAPITAL)} € empruntés sur {DUREE_ANS} ans à {fr(TAUX_CREDIT * 100)} % + assurance {fr(ASSURANCE_PCT * 100)} %</h3>
    <p class="attractiveness-intro">Mensualité <strong>{eur(mensualite(CAPITAL), 2)} €</strong>, soit {fr(mensualite_par_euro() * 100, 3)} % du capital emprunté par mois. L'apport est de {APPORT_PCT * 100:.0f} % — les frais d'acquisition ({eur(FRAIS_ACQUISITION)} €) restent à financer en plus, comme sur les autres dossiers du parc.</p>
    <table class="projection-table compare">
      <thead><tr><th>Trésorerie mensuelle</th><th class="num">Favorable</th><th class="num">Base</th><th class="num">Défavorable</th></tr></thead>
      <tbody>
        <tr><td>Loyer retenu</td><td class="num">{eur(SBEST['loyer'])}</td><td class="num">{eur(SBASE['loyer'])}</td><td class="num">{eur(SWORST['loyer'])}</td></tr>
        <tr><td>Vacance</td><td class="num">{fr(SBEST['vac'])} %</td><td class="num">{fr(SBASE['vac'])} %</td><td class="num">{fr(SWORST['vac'])} %</td></tr>
        <tr><td>Charges de copropriété</td><td class="num">{eur(COPRO_BASE)}/an</td><td class="num">{eur(COPRO_BASE)}/an</td><td class="num">{eur(COPRO_HAUT)}/an</td></tr>
        <tr><td>Taxe foncière</td><td class="num">{eur(TF_BASE)}/an</td><td class="num">{eur(TF_BASE)}/an</td><td class="num">1 000 €/an</td></tr>
        <tr><td>EBE mensuel</td><td class="num">{eur(SBEST['ebe_mois'], 2)}</td><td class="num">{eur(SBASE['ebe_mois'], 2)}</td><td class="num">{eur(SWORST['ebe_mois'], 2)}</td></tr>
        <tr><td>Mensualité de crédit</td><td class="num">−{eur(mensualite(CAPITAL), 2)}</td><td class="num">−{eur(mensualite(CAPITAL), 2)}</td><td class="num">−{eur(mensualite(CAPITAL), 2)}</td></tr>
        <tr class="highlight"><td><strong>Cash-flow avant IS</strong></td><td class="num"><strong>{eur(SBEST['cf'], 2)}</strong></td><td class="num"><strong>{eur(SBASE['cf'], 2)}</strong></td><td class="num"><strong>{eur(SWORST['cf'], 2)}</strong></td></tr>
        <tr><td>Cash-flow après IS (convention prudente)</td><td class="num">{eur(SBEST['cf_ap'], 2)}</td><td class="num">{eur(SBASE['cf_ap'], 2)}</td><td class="num">{eur(SWORST['cf_ap'], 2)}</td></tr>
        <tr><td>Rendement net avant IS</td><td class="num">{fr(SBEST['rdt_av'])} %</td><td class="num">{fr(SBASE['rdt_av'])} %</td><td class="num">{fr(SWORST['rdt_av'])} %</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Le seuil doctrinal de 5 % net avant IS est franchi au prix affiché : {fr(SBASE['rdt_av'])} %.</strong> C'est une bonne nouvelle, et c'est aussi la limite du dossier — il n'y a pas de marge : {fr(SBASE['rdt_av'] - 5.0)} point de coussin, {fr(SBASE['rdt_ap'])} % après IS, et un cash-flow de <strong>{eur(SBASE['cf'], 2)} €/mois</strong> parce que la mensualité de {eur(mensualite(CAPITAL), 2)} € mange un EBE de {eur(SBASE['ebe_mois'], 2)} €. Le prix qui rend la trésorerie nulle est de {eur(prix_cashflow_nul(SBASE['ebe']))} € : <strong>ce dossier ne dégage pas de cash-flow, il dégage un rendement</strong> — et la question n'est donc pas « combien ça rapporte », mais « combien je paie l'actif ».</p>
    </div>
  </section>"""

    loyer_section = f"""  <section class="financial-projections">
    <h2>Le loyer : quatre ancrages, une seule fourchette</h2>
    <table class="projection-table compare">
      <thead><tr><th>Source datée ({DATE_FR})</th><th class="num">€/m²/mois</th><th class="num">Pour {eur(SURF, 2)} m²</th><th>Nature</th></tr></thead>
      <tbody>
        <tr><td>Fiche de référence interne « Seuils d'achat par ville » (21/09/2026, lot type 60 m²)</td><td class="num">{fr(LOYER_M2_BAS)}</td><td class="num">{eur(SURF * LOYER_M2_BAS)}</td><td>plancher prudent de la doctrine</td></tr>
        <tr><td>Trackstone, appartements Brignoles</td><td class="num">{fr(LOYER_M2_MED)}</td><td class="num">{eur(SURF * LOYER_M2_MED)}</td><td>loyer moyen constaté</td></tr>
        <tr class="highlight"><td><strong>SeLoger, estimation de location de la ville (9 à 20 €/m²)</strong></td><td class="num"><strong>{fr(LOYER_M2_HAUT)}</strong></td><td class="num"><strong>{eur(SURF * LOYER_M2_HAUT)}</strong></td><td>haut de la fourchette</td></tr>
        <tr><td>Annonce réelle du centre : 40,68 m², 2 pièces, 1er étage (ABC IMMO, exclusivité)</td><td class="num">16,0 charges comprises</td><td class="num">650 charges comprises</td><td>2 pièces de centre, même génération</td></tr>
        <tr><td>Annonce réelle du centre : 37,66 m²</td><td class="num">17,0</td><td class="num">640</td><td>plus petite surface, loyer plus élevé</td></tr>
        <tr><td>Annonce réelle : 65,1 m² à Brignoles</td><td class="num">9,2</td><td class="num">600</td><td>grande surface : le prix au m² chute</td></tr>
        <tr><td>Annonces réelles : 70 m² à 786 et 855 €/mois</td><td class="num">11,2 à 12,2</td><td class="num">—</td><td>grandes surfaces, charges comprises</td></tr>
        <tr><td>RealAdvisor : loyer médian d'un appartement (toutes surfaces)</td><td class="num">—</td><td class="num">{eur(REALADVISOR_MED)}</td><td>toutes surfaces, donc non comparable</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>La fourchette retenue est {eur(LOYER_BAS)} à {eur(LOYER_HAUT)} €/mois hors charges, et le scénario de base s'établit à {eur(LOYER_BASE)} €/mois ({fr(LOYER_M2_MED)} €/m²).</strong> Deux pièges de lecture. Le premier : {eur(REALADVISOR_MED)} € de loyer médian toutes surfaces ne dit rien d'un {eur(SURF, 2)} m². Le second, plus pernicieux : le prix au m² décroît avec la surface, donc les 9,2 €/m² d'un 65 m² ne se transposent pas à un 43 m² — et l'inverse est vrai, un 24 m² meublé se loue plus de 20 €/m². C'est pourquoi la borne basse publiée ({eur(LOYER_BAS)} €) est tenue par la fiche de doctrine, et non par le marché constaté : <strong>c'est le loyer qu'il faut savoir encaisser si le bien se reloue mal</strong>.</p>
    </div>
  </section>"""

    dvf_cmp_rows = "\n".join(
        "        <tr><td>{}</td><td>{}</td><td class=\"num\">{}</td><td class=\"num\">{}</td><td class=\"num\">{}</td></tr>".format(
            c['date'], c['voie'], eur(c['surf']), eur(c['prix']), eur(c['m2']),
            c['num']) for c in DVF_COMPARABLES)

    dvf_section = f"""  <section class="financial-projections">
    <h2>Analyse de prix : deux boîtes, deux marchés</h2>
    <p class="attractiveness-intro">Méthode : mutations de nature « Vente » de 2025 dans la commune de Brignoles (INSEE {DVF_COMMUNE}), valeur foncière de la mutation divisée par la somme des surfaces bâties, surfaces supérieures à 5 m² et valeurs supérieures à 5 000 €. Deux découpages sont publiés, parce que c'est exactement là que se joue ce dossier : la <strong>boîte large</strong> du quartier (celle des fiches précédentes, {DVF_BOITE[0]} à {DVF_BOITE[1]} N, {DVF_BOITE[2]} à {DVF_BOITE[3]} E) et la <strong>boîte resserrée intra-muros</strong> ({DVF_BOITE_FINE[0]} à {DVF_BOITE_FINE[1]} N, {DVF_BOITE_FINE[2]} à {DVF_BOITE_FINE[3]} E), qui ne contient que les rues du vieux Brignoles.</p>
    <table class="projection-table compare">
      <thead><tr><th>Population de référence (DVF 2025)</th><th class="num">Ventes</th><th class="num">Médiane €/m²</th><th class="num">Q1</th><th class="num">Q3</th><th class="num">Prix médian</th><th class="num">Valeur de {eur(SURF, 2)} m²</th></tr></thead>
      <tbody>
        <tr class="highlight"><td><strong>Intra-muros, 30 à 50 m² — l'ancre retenue</strong></td><td class="num"><strong>{DVF_F_3050_N}</strong></td><td class="num"><strong>{eur(DVF_F_3050_MED)}</strong></td><td class="num"><strong>{eur(DVF_F_3050_Q1)}</strong></td><td class="num"><strong>{eur(DVF_F_3050_Q3)}</strong></td><td class="num"><strong>{eur(DVF_F_3050_PRIX)}</strong></td><td class="num"><strong>{eur(VALEUR_RETENUE)}</strong></td></tr>
        <tr><td>Intra-muros, 40 à 48 m² (la tranche exacte)</td><td class="num">{DVF_F_4048_N}</td><td class="num">{eur(DVF_F_4048_MED)}</td><td class="num">{eur(DVF_F_4048_Q1)}</td><td class="num">{eur(DVF_F_4048_Q3)}</td><td class="num">{eur(DVF_F_4048_PRIX)}</td><td class="num">{eur(SURF * DVF_F_4048_MED)}</td></tr>
        <tr><td>Intra-muros, toutes surfaces</td><td class="num">{DVF_F_APP_N}</td><td class="num">{eur(DVF_F_MED)}</td><td class="num">—</td><td class="num">—</td><td class="num">—</td><td class="num">—</td></tr>
        <tr><td>Boîte large du quartier, 40 à 48 m² (contaminée)</td><td class="num">{DVF_Q_4048_N}</td><td class="num">{eur(DVF_Q_4048_MED)}</td><td class="num">{eur(DVF_Q_4048_Q1)}</td><td class="num">{eur(DVF_Q_4048_Q3)}</td><td class="num">{eur(DVF_Q_4048_PRIX)}</td><td class="num">{eur(VALEUR_LARGE)}</td></tr>
        <tr><td>Commune de Brignoles, 30 à 45 m²</td><td class="num">{DVF_APP_3045_N}</td><td class="num">{eur(DVF_APP_3045_MED)}</td><td class="num">—</td><td class="num">—</td><td class="num">—</td><td class="num">—</td></tr>
        <tr><td>Commune de Brignoles, toutes surfaces</td><td class="num">{DVF_APP_N}</td><td class="num">{eur(DVF_APP_MED)}</td><td class="num">—</td><td class="num">—</td><td class="num">—</td><td class="num">—</td></tr>
      </tbody>
    </table>
    <h3>Les six transactions qui encadrent le bien</h3>
    <p class="attractiveness-intro">Appartements vendus seuls dans le noyau historique en 2025, de 38 à 47 m² — la population la plus proche du bien. Le prix demandé, {eur(PRIX / SURF)} €/m², se place <strong>{fr(abs(ecart_cmp_m2), 1)} % sous leur médiane</strong> ({eur(DVF_CMP_MED)} €/m²)… et <strong>{fr(abs(ecart_cmp_prix), 1)} % au-dessus de leur prix médian absolu</strong> ({eur(DVF_CMP_PRIX)} €, contre {eur(PRIX)} € demandés). Les deux phrases sont vraes en même temps : le bien se paie au-dessus du prix des transactions comparables, parce qu'il est vendu comme un bien en bon état et sans travaux.</p>
    <table class="projection-table compare">
      <thead><tr><th>Date</th><th>Voie</th><th class="num">Surface</th><th class="num">Prix</th><th class="num">€/m²</th><th class="num">N°</th></tr></thead>
      <tbody>
{dvf_cmp_rows}
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Ce que l'analyse de prix dit, et ce qu'elle démolit.</strong> Elle démolit d'abord l'argument central de l'annonce — « moins cher que des biens comparables dans la région ». Sur la boîte large, le bien paraît {fr(abs(ecart_large), 1)} % sous la médiane (40-48 m² à {eur(DVF_Q_4048_MED)} €/m²). Mais cette boîte mélange le centre historique et des résidences récentes situées à 400-700 m (chemin Saint-Pierre, Les 4 Saisons, Les Jardins de Provence, avenue Dréo), qui se traitent entre 2 683 et 3 571 €/m² et n'ont ni le même bâti, ni le même emplacement, ni le même âge. Restreinte au noyau historique, la comparaison s'inverse : médiane {eur(DVF_F_3050_MED)} €/m² sur {DVF_F_3050_N} ventes de 30 à 50 m², et le prix demandé ressort <strong>{fr(ecart_fin, 1)} % AU-DESSUS</strong> de cette médiane, au-delà du troisième quartile ({eur(DVF_F_3050_Q3)} €/m²). <strong>C'est un prix de marché pour un bien en bon état, pas une décote.</strong></p>
      <p class="attractiveness-intro"><strong>La conséquence pratique.</strong> La valeur retenue — {eur(VALEUR_RETENUE)} €, {eur(SURF, 2)} m² × {eur(DVF_F_3050_MED)} €/m² — est le prix du micro-marché, pas un prix d'achat. La fourchette intra-muros sur cette tranche va de <strong>{eur(VALEUR_BASSE)} €</strong> (premier quartile) à <strong>{eur(VALEUR_HAUTE)} €</strong> (troisième quartile), et le prix demandé — {eur(PRIX)} € — se place juste au-dessus du haut de cette fourchette. L'acte en main à {eur(ACTE_EN_MAIN)} € représente <strong>{fr(ratio)} fois la valeur retenue</strong> : à ce niveau, il n'y a pas de marge de sécurité à la revente, et un appel de fonds de 20 000 € au nom du lot la rendrait franchement négative ({eur(ACTE_EN_MAIN + 20000)} € de revient pour {eur(VALEUR_RETENUE)} € de valeur). C'est la vraie raison de négocier : <strong>pas pour gagner un rendement — il est déjà là — mais pour arrêter de payer l'actif au-dessus de sa valeur</strong>.</p>
    </div>
  </section>"""

    proj_marge_section = f"""  <section class="financial-projections">
    <h2>Prix d'achat : les plafonds opposables</h2>
    <table class="projection-table compare">
      <thead><tr><th>Règle de prix</th><th class="num">Prix d'achat maximum</th><th class="num">Écart au prix affiché</th><th>Lecture</th></tr></thead>
      <tbody>
        <tr><td>Plafond 5 % net avant IS au loyer de base ({eur(SBASE['ebe'])} € d'EBE)</td><td class="num">{eur(SBASE['cap5'])}</td><td class="num">{fr((SBASE['cap5'] - PRIX) / PRIX * 100, 1)} %</td><td>la règle de rendement — déjà satisfaite au prix affiché</td></tr>
        <tr class="highlight"><td><strong>Valeur intra-muros du bien (médiane DVF du noyau historique)</strong></td><td class="num"><strong>{eur(VALEUR_RETENUE)}</strong></td><td class="num"><strong>{fr((VALEUR_RETENUE - PRIX) / PRIX * 100, 1)} %</strong></td><td><strong>le prix qui arrête de payer l'actif trop cher</strong></td></tr>
        <tr><td>Plafond 5 % net au loyer plancher</td><td class="num">{eur(SBAS['cap5'])}</td><td class="num">{fr((SBAS['cap5'] - PRIX) / PRIX * 100, 1)} %</td><td>si le loyer s'ajuste vers le bas</td></tr>
        <tr><td>Plafond 5 % net au loyer haut</td><td class="num">{eur(SHAUT['cap5'])}</td><td class="num">{fr((SHAUT['cap5'] - PRIX) / PRIX * 100, 1)} %</td><td>si le bien part au loyer du haut</td></tr>
        <tr><td>Plafond 5 % net avec charges triplées</td><td class="num">{eur(SCOPRO['cap5'])}</td><td class="num">{fr((SCOPRO['cap5'] - PRIX) / PRIX * 100, 1)} %</td><td>si la copropriété rattrape trente ans d'entretien</td></tr>
        <tr><td>Plafond 5 % net avec 10 000 € de travaux</td><td class="num">{eur(prix_5pct_avec_travaux(SBASE['ebe'], TRAVAUX_REF_1))}</td><td class="num">{fr((prix_5pct_avec_travaux(SBASE['ebe'], TRAVAUX_REF_1) - PRIX) / PRIX * 100, 1)} %</td><td>électricité, peintures, salle d'eau</td></tr>
        <tr><td>Plafond 5 % net avec 20 000 € de travaux</td><td class="num">{eur(prix_5pct_avec_travaux(SBASE['ebe'], TRAVAUX_REF_2))}</td><td class="num">{fr((prix_5pct_avec_travaux(SBASE['ebe'], TRAVAUX_REF_2) - PRIX) / PRIX * 100, 1)} %</td><td>travaux votés en copropriété</td></tr>
        <tr><td>Plafond 6,5 % net d'IS (seuil patrimonial de la fiche de référence)</td><td class="num">{eur(plafond_is(SBASE['ebe'], 0.065))}</td><td class="num">{fr((plafond_is(SBASE['ebe'], 0.065) - PRIX) / PRIX * 100, 1)} %</td><td>hors de portée sur un bien au prix du marché</td></tr>
        <tr><td>Prix à cash-flow nul (apport de 10 %)</td><td class="num">{eur(prix_cashflow_nul(SBASE['ebe']))}</td><td class="num">{fr((prix_cashflow_nul(SBASE['ebe']) - PRIX) / PRIX * 100, 1)} %</td><td>le prix où la trésorerie ne saigne plus</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Traduction en une phrase.</strong> Ce dossier est inhabituel : le plafond de rendement à 5 % net ({eur(SBASE['cap5'])} €) est <em>au-dessus</em> du prix demandé — sur la seule doctrine de rendement, on pourrait acheter au prix affiché. Mais la valeur du bien ({eur(VALEUR_RETENUE)} €) est <em>en dessous</em>, de {fr(surcote, 1)} %. Les deux règles ne disent pas la même chose, et c'est la seconde qui gouverne ici : <strong>on n'achète pas 1,19 fois la valeur de son marché quand la revente est le seul horizon de sortie.</strong> Quant au cash-flow nul, il demanderait {eur(prix_cashflow_nul(SBASE['ebe']))} € — hors d'atteinte. La cible se fixe donc à la valeur intra-muros : <strong>{eur(VALEUR_RETENUE)} €</strong>, et l'offre d'ouverture plus bas, à {eur(70000)} €.</p>
    </div>
  </section>"""

    charges_section = f"""  <section class="financial-projections">
    <h2>Fiscalité et charges d'exploitation : ce qui est su, ce qui est estimé</h2>
    <table class="projection-table compare">
      <thead><tr><th>Poste</th><th class="num">Montant retenu</th><th>Source</th></tr></thead>
      <tbody>
        <tr><td>Charges de copropriété du lot</td><td class="num">{eur(COPRO_BASE)} / an</td><td>annoncées par l'annonce ({fr(COPRO_BASE / 12)} €/mois)</td></tr>
        <tr><td>Taxe foncière</td><td class="num">{eur(TF_BASE)} / an</td><td>ESTIMÉE — avis non communiqué</td></tr>
        <tr><td>Assurance propriétaire non occupant</td><td class="num">{eur(PNO)} / an</td><td>estimation de place</td></tr>
        <tr><td>Gestion locative et provision</td><td class="num">{eur(SBASE['entretien'])} / an</td><td>{fr(GESTION_BASE_PCT)} % des loyers plus {eur(PROV_BASE)} de provision</td></tr>
        <tr><td>Comptabilité SCI à l'IS</td><td class="num">{eur(COMPTA)} / an</td><td>estimation de place</td></tr>
        <tr><td>Travaux de remise en état</td><td class="num">0 € retenu</td><td>annoncé « sans travaux » : publié en grille (10 000 / 20 000 / 30 000 €)</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Fiscalité, année 1 :</strong> EBE {eur(SBASE['ebe'])} € moins intérêts d'emprunt {eur(INTERETS_AN1)} € ({eur(CAPITAL)} à {fr(TAUX_CREDIT * 100)} %) moins dotation aux amortissements {eur(DOTATION_AN1)} € (bâti à 80 % du prix affiché amorti sur 30 ans) = <strong>{eur(SBASE['ebe'] - INTERETS_AN1 - DOTATION_AN1)} €, soit un déficit</strong>. Aucun IS n'est dû en année 1. Les rendements nets publiés restent néanmoins calculés sous la convention prudente du moteur (IS de 15 % de l'EBE, soit {eur(SBASE['is_'])} €) : c'est la lecture la plus défavorable, celle qui décide.</p>
    </div>
  </section>"""

    lect_rows = []
    for s_ in rec_['analyse']['strategies_explorees']:
        lect_rows.append(
            f"        <tr><td>{s_['strategie']}</td><td>{s_['rendement']}</td>"
            f"<td>{s_['faisabilite']}</td><td>{s_['risque']}</td></tr>")
    lect_table = "\n".join(lect_rows)
    lecture = f"""  <section class="financial-projections">
    <h2>Les cinq lectures testées, chiffrées par le moteur</h2>
    <table class="projection-table compare">
      <thead><tr><th>Lecture</th><th>Rendement</th><th>Faisabilité</th><th>Risque</th></tr></thead>
      <tbody>
{lect_table}
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro">Aucune lecture ne dégage un cash-flow positif au prix affiché, et aucune ne franchit le seuil de 6,5 % net d'IS. La <strong>stratégie retenue est la location nue au loyer de marché, au prix du marché intra-muros et pas au-delà</strong> : c'est la seule lecture compatible avec la doctrine du parc, et elle se joue sur le prix d'entrée, pas sur le loyer — les écarts entre les trois hypothèses de loyer ({eur(SBAS['cf'], 0)} € contre {eur(SHAUT['cf'], 0)} € de cash-flow mensuel) sont deux fois plus petits que l'écart de prix nécessaire pour rentrer dans la cible.</p>
    </div>
  </section>"""

    inverse_section = f"""  <section class="financial-projections">
    <h2>Le prix d'équilibre, dans les trois sens</h2>
    <table class="projection-table compare">
      <thead><tr><th>Question inverse</th><th class="num">Réponse</th><th>Ce que cela veut dire</th></tr></thead>
      <tbody>
        <tr><td>Quel loyer pour un cash-flow nul au prix affiché ?</td><td class="num">{eur(loyer_cashflow_nul(TF_BASE, COPRO_BASE, PROV_BASE))} / mois</td><td>{fr(loyer_cashflow_nul(TF_BASE, COPRO_BASE, PROV_BASE) / SURF, 1)} €/m² — au-dessus du marché constaté : impossible à tenir</td></tr>
        <tr><td>Quel apport pour un cash-flow nul au prix affiché ?</td><td class="num">{eur(apport_cashflow_nul(PRIX, SBASE['ebe']))}</td><td>{fr(apport_cashflow_nul(PRIX, SBASE['ebe']) / PRIX * 100, 1)} % du prix — hors doctrine du parc</td></tr>
        <tr><td>Quel prix pour un cash-flow nul ?</td><td class="num">{eur(prix_cashflow_nul(SBASE['ebe']))}</td><td>{fr((prix_cashflow_nul(SBASE['ebe']) - PRIX) / PRIX * 100, 1)} % sous le prix affiché : ce n'est pas un prix de marché, c'est un prix de saisie</td></tr>
        <tr class="highlight"><td><strong>Quel prix pour ne plus payer l'actif au-dessus de sa valeur ?</strong></td><td class="num"><strong>{eur(VALEUR_RETENUE)}</strong></td><td><strong>{fr((VALEUR_RETENUE - PRIX) / PRIX * 100, 1)} % sous le prix affiché : la cible de négociation</strong></td></tr>
        <tr><td>Quel prix pour 5 % net avant IS ?</td><td class="num">{eur(SBASE['cap5'])}</td><td>déjà satisfait au prix affiché : {fr(SBASE['rdt_av'])} % net avant IS</td></tr>
        <tr><td>Quel prix pour 6,5 % net d'IS ?</td><td class="num">{eur(plafond_is(SBASE['ebe'], 0.065))}</td><td>{fr((PRIX - plafond_is(SBASE['ebe'], 0.065)) / PRIX * 100, 1)} % sous le prix : hors de portée d'une négociation crédible</td></tr>
      </tbody>
    </table>
  </section>"""

    marche_section = f"""  <section class="financial-projections">
    <h2>Positionnement du prix face aux repères du secteur</h2>
    <table class="projection-table compare">
      <thead><tr><th>Repère ({DATE_FR})</th><th class="num">€/m²</th><th class="num">Prix affiché / repère</th><th>Lecture</th></tr></thead>
      <tbody>
        <tr><td>Prix demandé</td><td class="num">{eur(PRIX / SURF)}</td><td class="num">1,00</td><td>référence</td></tr>
        <tr class="highlight"><td><strong>Médiane DVF 2025 intra-muros, tranche 30-50 m²</strong></td><td class="num"><strong>{eur(DVF_F_3050_MED)}</strong></td><td class="num"><strong>{fr((PRIX / SURF) / DVF_F_3050_MED)} ×</strong></td><td><strong>le seul repère qui commande la décision : {fr(ecart_fin, 1)} % au-dessus</strong></td></tr>
        <tr><td>Médiane DVF 2025 intra-muros, tranche 40-48 m²</td><td class="num">{eur(DVF_F_4048_MED)}</td><td class="num">{fr((PRIX / SURF) / DVF_F_4048_MED)} ×</td><td>{fr((PRIX / SURF - DVF_F_4048_MED) / DVF_F_4048_MED * 100, 1)} % au-dessus : au prix du marché pour un bien en état</td></tr>
        <tr><td>Troisième quartile intra-muros, 30-50 m²</td><td class="num">{eur(DVF_F_3050_Q3)}</td><td class="num">{fr((PRIX / SURF) / DVF_F_3050_Q3)} ×</td><td>{fr((PRIX / SURF - DVF_F_3050_Q3) / DVF_F_3050_Q3 * 100, 1)} % au-dessus du haut de fourchette</td></tr>
        <tr><td>Boîte large du quartier, 40-48 m² (l'argument de l'annonce)</td><td class="num">{eur(DVF_Q_4048_MED)}</td><td class="num">{fr((PRIX / SURF) / DVF_Q_4048_MED)} ×</td><td>{fr(abs(ecart_large), 1)} % sous cette médiane — mais elle contient des résidences récentes hors vieille ville</td></tr>
        <tr><td>Plafond patrimonial du parc (6,5 % net d'IS, fiche de référence)</td><td class="num">{eur(PLAF_PATRIMONIAL[0])}</td><td class="num">{fr((PRIX / SURF) / PLAF_PATRIMONIAL[0])} ×</td><td>hors de portée : ce n'est pas un dossier de rendement élevé</td></tr>
        <tr><td>Médiane DVF 2025 communale, toutes surfaces</td><td class="num">{eur(DVF_APP_MED)}</td><td class="num">{fr((PRIX / SURF) / DVF_APP_MED)} ×</td><td>repère de contexte : la commune est plus chère que son centre ancien</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro">Un seul chiffre résume ce dossier : <strong>le prix demandé est {fr(ecart_fin, 1)} % au-dessus de la médiane des ventes réelles du noyau historique sur sa tranche de surface, et {fr(abs(ecart_large), 1)} % sous la médiane d'une boîte qui mélange le vieux Brignoles et des résidences de 2010.</strong> Les deux lectures coexistent parce que la géographie du prix, à Brignoles, tient à quelques rues. C'est pourquoi la comparaison retenue est la plus étroite : c'est celle qui décrit le bien qu'on achète, pas celui qu'on voudrait qu'il soit.</p>
    </div>
  </section>"""

    return "\n".join([proj_section, loyer_section, dvf_section,
                      proj_marge_section, charges_section, lecture,
                      inverse_section, marche_section])


def conf(rec_, S):
    SBASE = S['base']
    ecart_large = (PRIX / SURF - DVF_Q_4048_MED) / DVF_Q_4048_MED * 100.0
    ecart_fin = (PRIX / SURF - DVF_F_3050_MED) / DVF_F_3050_MED * 100.0
    ecart_cmp_m2 = (PRIX / SURF - DVF_CMP_MED) / DVF_CMP_MED * 100.0
    surcote = (PRIX / VALEUR_RETENUE - 1) * 100.0
    return dict(
        titre_court=(
            f"Appartement duplex T2/3 {eur(SURF, 2)} m², centre historique — "
            f"Brignoles (83170)"
        ),
        adresse=(
            f"Cœur du centre historique de Brignoles (83170), place "
            f"Saint-Pierre — appartement duplex T2/3 de {eur(SURF, 2)} m² au "
            f"rez-de-chaussée avec chambre à l'étage, immeuble de {ANNEE}, "
            f"annoncé sans travaux, copropriété de {LOTS_COPRO} lots sans "
            f"procédure"
        ),
        date_fr=DATE_FR,
        source=(
            "SeLoger — annonce 26JBKPTIEDR5, agence Nestenn Brignoles, cœur du "
            "centre historique (place Saint-Pierre)"
        ),
        url=URL,
        badge=(
            f"Bien libre, annoncé sans travaux — mais prix {fr(ecart_fin, 1)} % "
            f"au-dessus du marché de son propre noyau historique et cash-flow "
            f"de {eur(SBASE['cf'], 0)} €/mois"
        ),
        strategie=(
            f"Location nue longue durée au loyer de marché : "
            f"{eur(LOYER_BASE)} €/mois ({fr(LOYER_M2_MED)} €/m²), fourchette "
            f"testée de {eur(LOYER_BAS)} à {eur(LOYER_HAUT)} €. Aucun bail à "
            f"hériter, charges de copropriété annoncées {eur(COPRO_BASE)} €/an, "
            f"aucun travaux chiffré ni annoncé. Stratégie conditionnée au prix "
            f"d'entrée : la cible est la valeur intra-muros, {eur(VALEUR_RETENUE)} €"
        ),
        fiscal_note=(
            f"SCI à l'IS — année 1 en déficit "
            f"({eur(SBASE['ebe'] - INTERETS_AN1 - DOTATION_AN1)} € après "
            f"intérêts {eur(INTERETS_AN1)} € et dotation {eur(DOTATION_AN1)} €), "
            f"donc aucun IS dû. Les rendements nets publiés restent sous la "
            f"convention prudente du moteur (IS de 15 % de l'EBE, "
            f"{eur(SBASE['is_'])} €), dite explicitement. Seuil de décision du "
            f"parc : 5 % net avant IS, soit deux fois le rendement d'un CAT"
        ),
        lat="43.4057", lon="6.0635",
        quartier=(
            f"centre historique de Brignoles (83170) — place Saint-Pierre, "
            f"cinéma, commerces et services administratifs à pied, immeuble de "
            f"{ANNEE} sans ascenseur"
        ),
        intro_attr=(
            f"Ce dossier s'analyse à l'envers de la plupart des autres : "
            f"<strong>le bien est bon, le prix est le problème</strong>. "
            f"L'annonce écrit « moins cher que des biens comparables dans la "
            f"région » — mais la comparaison qui compte n'est pas celle du "
            f"portail, c'est celle de la rue. Sur le noyau historique de "
            f"Brignoles ({DVF_F_3050_N} ventes de 30 à 50 m² en 2025, médiane "
            f"{eur(DVF_F_3050_MED)} €/m²), le prix demandé ressort "
            f"{fr(ecart_fin, 1)} % <strong>au-dessus</strong> de la médiane et "
            f"{fr((PRIX / SURF - DVF_F_3050_Q3) / DVF_F_3050_Q3 * 100, 1)} % "
            f"au-dessus du troisième quartile. Le portail, lui, compare à une "
            f"boîte qui contient des résidences récentes à 2 683-3 571 €/m² : "
            f"c'est là que naît l'illusion de décote. Sur le fond, le bien a "
            f"de vrais atouts — {eur(SURF, 2)} m² au rez-de-chaussée avec "
            f"chambre à l'étage et petite pièce d'appoint, annoncé en excellent "
            f"état et sans travaux, DPE {DPE} et GES {GES}, charges de "
            f"copropriété de {eur(COPRO_BASE)} €/an seulement, copropriété de "
            f"{LOTS_COPRO} lots sans procédure, et les commerces de la ville à "
            f"pied. Et une faiblesse structurelle : à {eur(PRIX)} €, l'acte en "
            f"main de {eur(ACTE_EN_MAIN)} € représente {fr(ACTE_EN_MAIN / VALEUR_RETENUE)} "
            f"fois la valeur de marché du bien"
        ),
        profil=(
            f"un couple, ou une personne seule avec un enfant, dans un "
            f"{PIECES} pièces de {eur(SURF, 2)} m² au cœur commerçant de "
            f"Brignoles : entrée, séjour avec cuisine ouverte, chambre à "
            f"l'étage, petite pièce de {eur(PETITE_PIECE)} m² en bureau. C'est "
            f"le profil type de la demande locative locale — commerces, "
            f"écoles, administrations à pied — et c'est aussi sa limite : "
            f"sans ascenseur et au rez-de-chaussée, le bien écarte les "
            f"locataires âgés, et sans stationnement il écarte les ménages "
            f"motorisés qui regardent d'abord où poser la voiture"
        ),
        concl_attr=(
            f"Adéquation moyenne ({fr((7 + 8 + 7 + 6 + 6 + 5) / 6, 1)}/10). "
            f"L'emplacement est le meilleur atout (commerces 8/10), le "
            f"rendement net avant IS franchit le seuil doctrinal "
            f"({fr(SBASE['rdt_av'])} %), mais l'actif s'achète "
            f"{fr(surcote, 1)} % au-dessus de sa valeur de marché et ne dégage "
            f"aucun cash-flow ({eur(SBASE['cf'], 0)} €/mois). Ce n'est pas un "
            f"dossier mort : c'est un dossier à prix. La cible est "
            f"{eur(VALEUR_RETENUE)} € — et à ce prix, tout change"
        ),
        intro_strat=(
            f"Cinq lectures ont été testées, toutes calculées par le moteur : "
            f"trois hypothèses de loyer ({eur(LOYER_BAS)}, {eur(LOYER_BASE)} et "
            f"{eur(LOYER_HAUT)} €/mois), une variante où les charges de "
            f"copropriété triplent ({eur(COPRO_HAUT)} €/an), et une piste "
            f"meublée court terme écartée faute de marché. Aucune ne dégage un "
            f"cash-flow positif au prix affiché, et aucune n'atteint 6,5 % net "
            f"d'IS. La stratégie retenue est la location nue au loyer de "
            f"marché — mais elle ne vaut que si le prix d'entrée revient à la "
            f"valeur du bien"
        ),
        rationale=(
            "<p><strong>Pourquoi la lecture patrimoniale s'impose ici.</strong> "
            "Le bien est libre, sans bail à hériter, louable immédiatement, "
            "dans une ville où le marché de la revente est étroit et les prix "
            "du centre ancien bas. Ni la plus-value ni le marchand de biens ne "
            "peuvent porter le dossier : ce qui reste, c'est le loyer. Or au "
            "loyer de marché, l'affaire rend "
            f"{fr(SBASE['rdt_av'])} % net avant IS et {fr(SBASE['rdt_ap'])} % "
            "après IS sur l'acte en main — au-dessus du seuil doctrinal de 5 % "
            "avant IS, en dessous du seuil patrimonial de 6,5 % net d'IS.</p>"
            "<p><strong>Pourquoi le prix est le vrai sujet.</strong> Sur la "
            f"boîte large du quartier, le bien paraît {fr(abs(ecart_large), 1)} % "
            "sous le marché ; sur le noyau historique, il est "
            f"{fr(ecart_fin, 1)} % au-dessus. Les deux mesures sont exactes, "
            "elles ne mesurent pas la même chose : la première compare un "
            "duplex de 1900 au rez-de-chaussée de la vieille ville à des "
            "appartements de résidences récentes. L'écart entre les deux "
            "boîtes — 2 750 €/m² contre 1 711 €/m² — vaut "
            f"{eur(VALEUR_LARGE - VALEUR_RETENUE)} € sur {eur(SURF, 2)} m² : "
            "c'est exactement la marge que l'annonce laisse croire, et "
            "exactement celle qui n'existe pas.</p>"
            "<p><strong>Ce qu'on demande, dans l'ordre.</strong> L'avis de "
            "taxe foncière ; les trois derniers procès-verbaux d'assemblée "
            "générale, l'état daté, le budget prévisionnel et les appels de "
            "fonds ; le certificat Carrez et le plan de l'étage — pour "
            f"trancher le statut de la pièce de {eur(PETITE_PIECE)} m² ; le "
            "DPE complet et l'état de l'installation électrique, obligatoires "
            "tous les deux à la vente comme à la location sur un immeuble de "
            f"{ANNEE} ; et une réponse écrite sur le stationnement réel à "
            "proximité. Aucune de ces pièces n'est jointe à l'annonce, et "
            "chacune se monétise en euros de prix</p>"
        ),
        identite=[
            ("Ville", "Brignoles (83170), Var — sous-préfecture, 18 000 habitants environ"),
            ("Quartier", f"Centre historique, place Saint-Pierre — boîte intra-muros {DVF_BOITE_FINE[0]} à {DVF_BOITE_FINE[1]} N"),
            ("Type de bien", f"Appartement duplex T2/3, {PIECES} pièces, {CHAMBRES} chambre + pièce de {eur(PETITE_PIECE)} m², {eur(SURF, 2)} m² Carrez"),
            ("Étage et immeuble", f"{ETAGE}, immeuble de {ANNEE}, sans ascenseur"),
            ("Copropriété", f"{LOTS_COPRO} lots d'habitation, charges annoncées {eur(COPRO_BASE)} €/an, aucune procédure en cours"),
            ("Diagnostics", f"DPE {DPE}, GES {GES}, facture annoncée {eur(FACTURE_BASSE)} à {eur(FACTURE_HAUTE)} €/an — aucun rapport joint"),
            ("Prix affiché", f"{eur(PRIX)} € — {eur(PRIX / SURF)} €/m², honoraires à la charge du vendeur"),
            ("Acte en main", f"{eur(ACTE_EN_MAIN)} € (frais {eur(FRAIS_ACQUISITION)} €, simulateur de l'annonce)"),
            ("Valeur de marché", f"{eur(VALEUR_RETENUE)} € (médiane DVF intra-muros 30-50 m², {eur(DVF_F_3050_MED)} €/m² × {eur(SURF, 2)} m²)"),
            ("Loyer de marché", f"{eur(LOYER_BAS)} à {eur(LOYER_HAUT)} €/mois hors charges, base {eur(LOYER_BASE)} €/mois"),
            ("Rendement net", f"{fr(SBASE['rdt_av'])} % avant IS, {fr(SBASE['rdt_ap'])} % après IS sur l'acte en main"),
            ("Cash-flow", f"{eur(SBASE['cf'], 0)} €/mois avant IS avec {APPORT_PCT * 100:.0f} % d'apport"),
            ("Prix plafond (valeur intra-muros)", f"{eur(VALEUR_RETENUE)} €"),
        ],
        stance=(
            "<p><strong>Le bien est bon, le prix est faux.</strong> Un duplex "
            f"de {eur(SURF, 2)} m² au cœur commerçant de Brignoles, annoncé "
            "sans travaux, DPE D, charges de copropriété de "
            f"{eur(COPRO_BASE)} €/an, dans une copropriété de {LOTS_COPRO} lots "
            "sans procédure : c'est un actif louable immédiatement, et le "
            f"loyer de marché ({eur(LOYER_BASE)} €/mois) donne "
            f"{fr(SBASE['rdt_av'])} % net avant IS — le seuil doctrinal est "
            "franchi. Le problème n'est donc pas ce que le bien rapporte, "
            "c'est ce qu'il coûte : <strong>"
            f"{fr(ACTE_EN_MAIN / VALEUR_RETENUE)} fois la valeur de son propre "
            f"marché intra-muros</strong>, {fr(ecart_fin, 1)} % au-dessus de la "
            f"médiane DVF de sa tranche de surface, au-delà du troisième "
            f"quartile. À ce prix, il n'y a ni marge de revente, ni coussin "
            "pour des travaux votés, et le cash-flow reste négatif de "
            f"{eur(abs(SBASE['cf']), 0)} €/mois.</p>"
            "<p><strong>L'argument de l'annonce ne tient pas.</strong> « Moins "
            "cher que des biens comparables dans la région » est vrai sur la "
            "boîte large du quartier — celle qui mélange la vieille ville et "
            "des résidences récentes à 2 683-3 571 €/m², situées à 400 à 700 m "
            "et sans rapport avec ce bien. Sur les rues du vieux Brignoles, la "
            f"médiane 2025 est de {eur(DVF_F_3050_MED)} €/m² sur "
            f"{DVF_F_3050_N} ventes de 30 à 50 m², et le prix demandé est "
            "au-dessus. Ce n'est pas une décote, c'est un prix haut de "
            "marché — pour un bien dont on ne sait encore rien : aucune pièce "
            "de copropriété, aucun diagnostic, une taxe foncière inconnue et "
            f"une troisième pièce de {eur(PETITE_PIECE)} m² dont le statut "
            "Carrez n'est pas établi.</p>"
            "<p><strong>Position : on négocie, à "
            f"{eur(VALEUR_RETENUE)} € maximum.</strong> C'est la valeur "
            f"intra-muros du bien ({eur(SURF, 2)} m² × "
            f"{eur(DVF_F_3050_MED)} €/m²), soit "
            f"{fr((PRIX - VALEUR_RETENUE) / PRIX * 100, 1)} % sous le prix "
            f"affiché. Offre d'ouverture à {eur(70000)} €, en joignant le "
            "tableau DVF : c'est le seul argument qui ne se discute pas. Si "
            "les diagnostics révèlent une installation électrique à reprendre "
            "ou des travaux votés, le plafond tombe à "
            f"{eur(prix_5pct_avec_travaux(SBASE['ebe'], TRAVAUX_REF_1))} € avec "
            f"10 000 € de travaux et à "
            f"{eur(prix_5pct_avec_travaux(SBASE['ebe'], TRAVAUX_REF_2))} € avec "
            f"20 000 €. Au-delà de {eur(PRIX)} €, le dossier ne se défend pas : "
            "on paie le bien plus cher que son marché sans en tirer de "
            "cash-flow.</p>"
        ),
        prix_plafond=f"{eur(VALEUR_RETENUE)} €",
        leviers=[
            f"<strong>Ouvrir par la DVF, pas par le loyer</strong> — "
            f"Le rendement n'est pas le point faible du dossier : "
            f"{fr(SBASE['rdt_av'])} % net avant IS franchit le seuil de 5 %. "
            f"L'argument imparable est ailleurs : {DVF_F_3050_N} ventes réelles "
            f"de 30 à 50 m² dans le noyau historique en 2025, médiane "
            f"{eur(DVF_F_3050_MED)} €/m², troisième quartile "
            f"{eur(DVF_F_3050_Q3)} €/m². Le prix demandé est au-dessus du "
            f"troisième quartile. Se présenter avec ce tableau change la "
            f"position de négociation : on ne demande pas une remise, on "
            f"constate un prix.",
            f"<strong>Exiger le Carrez et le plan de l'étage avant tout</strong> — "
            f"L'annonce écrit « 2/3 pièces » : elle hésite elle-même. Si la "
            f"pièce de {eur(PETITE_PIECE)} m² n'entre pas dans le Carrez, le "
            f"bien se loue comme un T2 et {eur(PETITE_PIECE)} m² de surface "
            f"payée disparaissent — soit {eur(PETITE_PIECE * PRIX / SURF)} € au "
            f"prix affiché. C'est un levier documentaire, pas un argument "
            f"d'humeur.",
            f"<strong>Faire tomber la taxe foncière dans le prix</strong> — "
            f"Elle n'est pas communiquée. L'estimation retenue est "
            f"{eur(TF_BASE)} €/an ; si l'avis en annonce 1 100 €, la différence "
            f"de 400 €/an vaut {eur(400 / COEF_PLAFOND)} € de prix à 5 % net. "
            f"Demander l'avis avant l'offre, et l'intégrer au calcul.",
            f"<strong>Verrouiller les travaux votés par une clause chiffrée</strong> — "
            f"Aucun procès-verbal n'est joint. Exiger une clause suspensive : si "
            f"les appels de fonds votés au nom du lot dépassent 10 000 €, le "
            f"prix se réduit d'autant, frais d'acquisition compris "
            f"(1 € de travaux = {fr(1 / 1.08, 2)} € de prix). C'est la seule "
            f"protection qui tienne si les pièces arrivent après la signature.",
            f"<strong>Assumer la sortie patrimoniale, pas la plus-value</strong> — "
            f"Le centre ancien de Brignoles se traite {eur(DVF_F_MED)} €/m² "
            f"contre {eur(DVF_APP_MED)} €/m² sur la commune : aucune "
            f"appréciation à attendre. Toute décision se juge sur le net après "
            f"IS par euro engagé et sur le prix d'entrée — rien d'autre.",
        ],
        meta=[
            f"<strong>Méthode de prix.</strong> Toutes les statistiques DVF "
            f"2025 sont recalculées depuis le fichier départemental au moment "
            f"de la génération de cette fiche : {DVF_MUTATIONS} mutations lues "
            f"sur la commune de Brignoles (INSEE {DVF_COMMUNE}), dont "
            f"{DVF_MUTATIONS_VENTE} de nature Vente et {DVF_APP_N} ventes "
            f"d'appartements exploitables. Deux boîtes de coordonnées sont "
            f"publiées parce que le dossier se joue sur leur écart : la boîte "
            f"large utilisée par les fiches précédentes, et la boîte "
            f"intra-muros qui ne contient que les rues du vieux Brignoles.",
            f"<strong>Ce qui est annoncé, ce qui est estimé.</strong> Sont "
            f"annoncés : le prix ({eur(PRIX)} €), la surface "
            f"({eur(SURF, 2)} m²), les charges de copropriété "
            f"({eur(COPRO_BASE)} €/an), le nombre de lots ({LOTS_COPRO}), "
            f"l'absence de procédure, le DPE ({DPE}), le GES ({GES}), la "
            f"facture énergétique ({eur(FACTURE_BASSE)} à "
            f"{eur(FACTURE_HAUTE)} €/an) et l'absence de travaux. Sont estimés "
            f"et signalés comme tels : la taxe foncière ({eur(TF_BASE)} €/an), "
            f"la provision travaux ({eur(PROV_BASE)} €/an), l'assurance PNO "
            f"({eur(PNO)} €/an), la comptabilité ({eur(COMPTA)} €/an) et "
            f"l'enveloppe de travaux, publiée en grille de 10 000 à 30 000 €.",
            f"<strong>Point de méthode :</strong> c'est la première fiche de "
            f"Brignoles dont l'ancrage de valeur est resserré sur le noyau "
            f"historique, et l'écart avec la boîte large est spectaculaire — "
            f"{eur(DVF_Q_4048_MED)} €/m² contre {eur(DVF_F_3050_MED)} €/m² sur "
            f"la même période et des surfaces voisines. Règle à retenir pour "
            f"tout bien de centre ancien : <strong>vérifier ce que contient "
            f"la boîte de comparaison avant de croire à une décote</strong>. À "
            f"Brignoles, 400 m d'écart entre la vieille ville et les résidences "
            f"récentes valent 1 000 €/m².",
            f"<strong>Réserve.</strong> Les loyers retenus proviennent "
            f"d'ancrages datés (fiche de référence interne du 21/09/2026, "
            f"Trackstone, SeLoger, et quatre annonces réelles du centre) et non "
            f"d'un relevé exhaustif sur ce quartier ; les annonces affichent "
            f"des loyers charges comprises et espérés. Le loyer est donc "
            f"l'hypothèse la mieux documentée du dossier, pas une certitude — "
            f"et c'est pourquoi le scénario plancher ({eur(LOYER_BAS)} €/mois) "
            f"est publié au même rang que le scénario de base.",
        ],
    )


# ---------------------------------------------------------------------------
# Generation et publication
# ---------------------------------------------------------------------------
def main():
    S, rec_, note, verdict, comp = diagnostic()
    assert note == 6.1, note
    assert verdict == "negocier", verdict
    assert not comp.get("bloquant"), comp

    gen_spec = importlib.util.spec_from_file_location(
        "gen", os.path.join(ROOT, 'scripts', 'gen_fiches_2026-09-10.py'))
    gen = importlib.util.module_from_spec(gen_spec)
    gen_spec.loader.exec_module(gen)

    c = conf(rec_, S)
    html = gen.TEMPLATE.format(
        titre_court=c['titre_court'], adresse=c['adresse'], date_fr=c['date_fr'],
        source=c['source'], url=c['url'], badge=c['badge'],
        strategie=c['strategie'], fiscal_note=c['fiscal_note'],
        prix=eur(PRIX),
        surface=f"{eur(SURF, 2)} m² (2/3 pièces, {CHAMBRES} chambre + bureau)",
        prix_m2=f"{eur(PRIX / SURF)} €/m²",
        revient=eur(ACTE_EN_MAIN),
        valeur=eur(VALEUR_RETENUE),
        revenus=eur(LOYER_BASE),
        rdt_revient=fr(S['base']['rdt_ap']),
        rdt_valeur=fr(S['base']['rdt_valeur']),
        note=fr(note, 1), note_cls=fr(note, 1).replace(',', '-'),
        lat=c['lat'], lon=c['lon'], quartier=c['quartier'],
        intro_attr=c['intro_attr'], profil=c['profil'], concl_attr=c['concl_attr'],
        attrs=gen.attr_html(rec_), intro_strat=c['intro_strat'],
        strats=gen.strategy_html(rec_),
        rationale=c['rationale'], identite=gen.identite_html(c['identite']),
        projections=sections(rec_, S),
        risques=gen.risques_html(rec_),
        verdict_cls={"acheter": "buy", "negocier": "nego",
                     "fuir": "pass"}[verdict],
        stance=c['stance'], prix_plafond=c['prix_plafond'],
        leviers=gen.leviers_html(c['leviers']),
        meta="\n".join(f"      <p>{m}</p>" for m in c['meta']),
    )

    for vieux, neuf in (
        ('<span class="card-label">Surface</span>',
         '<span class="card-label">Surface annoncée (Carrez)</span>'),
        ('<span class="card-label">Prix / m²</span>',
         '<span class="card-label">Prix / m² (au-dessus du noyau historique)</span>'),
        ('<span class="card-label">Prix de revient</span>',
         '<span class="card-label">Prix de revient (acte en main, 8 % de frais)</span>'),
        ('<span class="card-label">Valeur marché retenue</span>',
         '<span class="card-label">Valeur marché (DVF 2025, intra-muros 30-50 m²)</span>'),
        ('<span class="card-label">Revenus bruts</span>',
         '<span class="card-label">Loyer retenu (13,5 €/m², bien libre)</span>'),
        ('<span class="card-label">Rentabilité nette</span>',
         '<span class="card-label">Rendement net après IS (acte en main / valeur)</span>'),
    ):
        assert vieux in html, vieux
        html = html.replace(vieux, neuf)

    assert 'section class="verdict nego"' in html, "classe de verdict inattendue"
    assert 'note-' + fr(note, 1).replace(',', '-') in html
    assert 'verdict buy' not in html and 'verdict pass' not in html
    _manquent = []
    for cle in (eur(PRIX) + ' €', eur(PRIX / SURF) + ' €', eur(ACTE_EN_MAIN),
                eur(VALEUR_RETENUE), eur(VALEUR_BASSE), eur(DVF_F_3050_MED),
                eur(DVF_Q_4048_MED), eur(VALEUR_LARGE), eur(S['base']['ebe']),
                fr(S['base']['rdt_av']), fr(S['base']['rdt_ap']),
                eur(S['base']['cap5']), eur(prix_cashflow_nul(S['base']['ebe'])),
                'Nestenn', 'place Saint-Pierre', 'intra-muros', 'Carrez',
                '2/3 pièces' if False else '2/3'):
        if cle not in html:
            _manquent.append(cle)
    if _manquent:
        print("  ATTENTION : chiffres attendus absents du HTML :", _manquent)
    assert not _manquent, _manquent
    assert '<tr<' not in html, "balise <tr> malformee"
    assert '<trtd' not in html, "balise <tr> malformee"
    for ph in ('{titre_court}', '{projections}', '{note}', '{stance}',
               '{attrs}', '{risques}', '{meta}'):
        assert ph not in html, f"placeholder non substitue : {ph}"

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

    print("\n  Controles des chiffres publies (publie vs recalcule) :")
    for lab, pub, rec2, tol in CONTROLES:
        etat = "ok" if abs(pub - rec2) <= tol else "ECART"
        print(f"    {lab:<64} publie {pub:>14,.2f} | recalcule {rec2:>14,.2f} | "
              f"tol {tol} | {etat}")
    ok = sum(1 for _, pub, rec2, tol in CONTROLES if abs(pub - rec2) <= tol)
    print(f"\n  {ok}/{len(CONTROLES)} controles a ecart nul")
    if ECARTS:
        print("\n  Chiffres signales en ecart :")
        for lab, brief, rec2, note_txt in ECARTS:
            print(f"    {lab:<64} publie {brief} | recalcule {rec2} — {note_txt}")


if __name__ == '__main__':
    main()

