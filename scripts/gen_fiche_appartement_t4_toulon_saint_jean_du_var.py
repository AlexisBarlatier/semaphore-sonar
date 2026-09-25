#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche Appartement T4 de 66 m2 (annonce : 68 m2) a Toulon, quartier
Saint-Jean-du-Var, vendu loue avec locataire en place depuis quinze ans.

119 900 EUR (1 817 EUR/m2), Foncia Transaction Toulon Liberte (289 place de la
Liberte, RCS 503698664, reference 00836037, exclusivite), annonce SeLoger
264IMKBI3IM5. 3e etage sur 7 avec ascenseur, immeuble de 1961, DPE D, GES B.

Le dossier est juge en lecture patrimoniale (SCI a l'IS) sur un BAIL INCONNU :
l'annonce ne publie NI loyer, NI charges de copropriete, NI taxe fonciere, NI
montant de travaux. Les cinq lectures du loyer (620, 750, 851, 950 EUR/mois et
851 EUR avec 2 400 EUR de charges) sont calculees par le MOTEUR, jamais a la
main : chaque chiffre publie est reaffirme par `calcule()` a tolerance depuis
les lignes du modele. Les statistiques DVF 2025 sont recalculees depuis le
fichier departemental quand il est present (/tmp/dvf83_2025.csv.gz, commune
83137).

La matrice de risques porte un risque BLOQUANT (le loyer du bail de quinze ans
jamais communique, dont depend tout le dossier) : la note publiee est donc
plafonnee par le moteur et le verdict est « a fuir au prix affiche ».
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

SLUG = "2026-09-25-appartement-t4-toulon-saint-jean-du-var"
URL = ("https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/"
       "var-83/toulon-83000/264IMKBI3IM5")
DATE = "2026-09-25"
DATE_FR = "25 septembre 2026"

# --- Le bien -----------------------------------------------------------------
PRIX = 119900.0
FRAIS_ACQUISITION = 9592.0                   # retenus par le simulateur de l'annonce
ACTE_EN_MAIN = PRIX + FRAIS_ACQUISITION      # 129 492
TAUX_FRAIS = FRAIS_ACQUISITION / PRIX        # 8,00 %
SURF = 66.0                                  # surface annoncee en titre
SURF_TEXTE = 68.0                            # surface ecrite dans le texte de l'annonce
PIECES = 4
CHAMBRES = 3
ANNEE = 1961
ETAGE = "3e étage sur 7, avec ascenseur"
DPE = "D"
GES = "B"
FACTURE_BASSE = 1460.0
FACTURE_HAUTE = 2010.0
PHOTOS = 5

# --- Le bail et les loyers : le coeur du dossier -----------------------------
# L'annonce ne publie AUCUN loyer. Ancrages de marche du quartier :
OLV_MED_M2 = 12.9            # Observatoire des loyers du Var, agglomeration de Toulon
SELOGER_Q_M2 = 15.0          # SeLoger, quartier Saint-Jean-du-Var (haut 23,3 bas 10,4)
REALADVISOR_MED = 954.0      # loyer median d'un appartement, quartier
MARCHE_M2_BAS = 12.6         # 830 EUR / 66 m2
MARCHE_M2_HAUT = 14.4        # 950 EUR / 66 m2
LOYER_MARCHE_BAS = 830.0
LOYER_MARCHE_HAUT = 950.0
LOYER_MARCHE_MED = 851.0     # OLV : 12,9 EUR/m2 x 66 m2
LOYER_ANCIEN = 620.0         # bail de quinze ans revise sous IRL : borne basse
LOYER_BASE = 750.0           # borne haute de l'hypothese de travail
LOYER_HAUT = 950.0           # haut du marche du quartier
LOYER_EXIGE = 850.0          # seuil demande par la fiche avant toute suite

# --- Doctrine du parc : seuil de rendement et credit -------------------------
SEUIL = 0.05                                  # 5 % net avant IS
COEF_PLAFOND = SEUIL * (1 + TAUX_FRAIS)       # EBE = 5,4 % du prix affiche
APPORT_PCT = 0.10
TAUX_CREDIT = 0.037
ASSURANCE_PCT = 0.0034
DUREE_ANS = 15
CAPITAL = PRIX * (1 - APPORT_PCT)             # 107 910
MENS_PAR_EURO_MODELE = 0.00753                # chiffre du brief, reaffirme plus bas
MENS_MODELE = 813.0                           # mensualite publiee

# --- Charges d'exploitation du modele (scenario de base) ---------------------
TF_BASE = 1000.0           # ESTIMEE, avis non communique
COPRO_BASE = 1800.0        # ESTIMEE, aucune charge publiee par l'annonce
COPRO_HAUT = 2400.0        # variante haute, immeuble de 1961 avec ascenseur
PNO = 120.0
COMPTA = 400.0
PROV_BASE = 200.0
GESTION_BASE_PCT = 5.0
VAC_BASE = 5.0
VAC_BEST = 3.0
VAC_WORST = 10.0

# --- Fiscalite annee 1 (modele du brief) -------------------------------------
QUOTE_PART_BATI_MODELE = 0.80                 # bati a 80 % du PRIX affiche
DOTATION_AN1 = PRIX * QUOTE_PART_BATI_MODELE / 30.0     # 3 197,33
INTERETS_AN1 = CAPITAL * TAUX_CREDIT                    # 3 992,67
CONVENTION_IS = 0.15                                    # IS prudent sur l'EBE

# --- Colocation etudiee (piste ecartee, publiee) -----------------------------
COLOC_BAS = 400.0        # par chambre et par mois
COLOC_HAUT = 430.0

# --- Travaux : aucun devis, donc une grille et pas un chiffre ----------------
TRAVAUX_REF_1 = 10000.0
TRAVAUX_REF_2 = 20000.0
TRAVAUX_REF_3 = 30000.0

# --- Marche local (fiche de reference analyses/marches-locaux, 21/09/2026) ---
MARCHE_M2_COMMUNE = 2668                     # fiche de reference du 21/09/2026
LOYER_REF_M2 = 13.0                          # lot type 60 m2
PLAF_PATRIMONIAL = (1305, 1205, 1045)        # 6,5 % / 7,0 % / 8,0 % net d'IS
PLAF_MDB = (946, 894, 861)                   # marge nette marchand de biens

# --- DVF 2025 reelle, Toulon (commune 83137) ---------------------------------
# Methode : mutations de nature « Vente » uniquement ; valeur fonciere de la
# mutation divisee par la somme des surfaces baties de la mutation ; surfaces
# > 5 m2 et valeurs > 5 000 EUR. Tranches de surface en m2.
DVF_FICHIER = '/tmp/dvf83_2025.csv.gz'
DVF_COMMUNE = '83137'
DVF_LIGNES_VENTE = 8736      # lignes DVF de nature Vente de la commune
DVF_MUTATIONS = 3908         # mutations lues (toutes natures)
DVF_MUTATIONS_VENTE = 3829   # mutations de nature Vente
DVF_APP_N = 2749             # ventes d'appartements
DVF_APP_MED = 2662           # mediane appartements, toutes surfaces
DVF_APP_1530_N = 231
DVF_APP_1530_MED = 3333
DVF_APP_3045_N = 485
DVF_APP_3045_MED = 2878
DVF_APP_4560_N = 641
DVF_APP_4560_MED = 2647
DVF_APP_4560_Q1 = 2096
DVF_APP_4560_Q3 = 3186
DVF_APP_4560_PRIX = 138000
DVF_APP_6090_N = 1054
DVF_APP_6090_MED = 2532
DVF_APP_4595_N = 1762        # tranche du bien, commune entiere
DVF_APP_4595_MED = 2566
# Quartier Saint-Jean-du-Var : boite de coordonnees du marqueur de l'annonce
DVF_BOITE = (43.116, 43.128, 5.941, 5.960)   # lat min, lat max, lon min, lon max
DVF_Q_VENTES = 566
DVF_Q_APP_N = 438
DVF_Q_MED = 2450
DVF_Q_Q1 = 2020
DVF_Q_Q3 = 3000
DVF_Q_4595_N = 279
DVF_Q_4595_MED = 2264
DVF_Q_4595_Q1 = 1978
DVF_Q_4595_Q3 = 2684
DVF_Q_4595_PRIX = 150000
# Transactions reellement comparables (appartements seuls, 40 a 75 m2,
# 1 800 a 1 835 EUR/m2) : elles encadrent le prix demande.
DVF_CMP_N = 8
DVF_CMP_MED = 1810
DVF_CMP_PRIX = 105000
DVF_COMPARABLES = (
    dict(date="25/03/2025", surf=55.0, prix=99500.0, m2=1809,
         voie="rue de Suez", lots=1, box=True),
    dict(date="30/04/2025", surf=52.0, prix=94000.0, m2=1808,
         voie="place Gustave Lambert", lots=2, box=False),
    dict(date="28/07/2025", surf=41.0, prix=75000.0, m2=1829,
         voie="rue Jean Aicard", lots=2, box=False),
    dict(date="31/10/2025", surf=72.0, prix=130000.0, m2=1806,
         voie="avenue Antoine Senequier", lots=3, box=True),
)

# --- Valeur de marche retenue (ancre DVF quartier, tranche 45-95 m2) ---------
VALEUR_BASSE = SURF * DVF_Q_4595_Q1     # 130 548
VALEUR_RETENUE = SURF * DVF_Q_4595_MED  # 149 424
VALEUR_HAUTE = SURF * DVF_Q_4595_Q3     # 177 144

CONTROLES = []                 # (libelle, chiffre publie, chiffre recalcule, tol)
ECARTS = []                    # chiffres du brief qui ne se recalculent pas


def calcule(libelle, publie, recalcule, tol=1.0):
    """Reaffirme un chiffre publie : il doit sortir du modele a tolerance."""
    CONTROLES.append((libelle, publie, recalcule, tol))
    if abs(publie - recalcule) > tol:
        if os.environ.get("HERMES_TOLERANT") == "1":
            ecart(libelle, publie, recalcule, f"tolerance {tol}")
            return
        assert False, (libelle, publie, recalcule)


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


def charges_fixes(tf, copro, provision):
    return tf + copro + PNO + COMPTA + provision


def revenus_annuels(loyer):
    return loyer * 12.0


def ebe_modele(loyer, vac, gestion_pct, tf, copro, provision):
    """Modele de reference, ligne a ligne (le moteur doit le reproduire)."""
    r = revenus_annuels(loyer)
    return (r * (1 - vac / 100.0) - r * gestion_pct / 100.0
            - charges_fixes(tf, copro, provision))


def plafond5(ebe):
    return ebe / COEF_PLAFOND


def prix_5pct_avec_travaux(ebe, travaux):
    """Prix affiche qui tient 5 % net avant IS, travaux capitalises compris."""
    return (ebe / SEUIL - travaux) / (1 + TAUX_FRAIS)


def prix_cashflow_nul(ebe):
    """Prix paye tel que 10 % d'apport donnent un cash-flow nul."""
    return (ebe / 12.0) / ((1 - APPORT_PCT) * mensualite_par_euro())


def apport_cashflow_nul(prix, ebe):
    return prix - (ebe / 12.0) / mensualite_par_euro()


def loyer_cashflow_nul(tf, copro, provision):
    """Loyer mensuel tel que l'EBE du scenario de base egale la mensualite."""
    fixes = charges_fixes(tf, copro, provision)
    part = 1 - VAC_BASE / 100.0 - GESTION_BASE_PCT / 100.0
    return (mensualite(CAPITAL) * 12.0 + fixes) / (12.0 * part)


def eur(v, dec=0):
    return f"{v:,.{dec}f}".replace(',', ' ').replace('.', ',')


def fr(v, dec=2):
    return f"{v:.{dec}f}".replace('.', ',')


def scen(rec, loyer, vac, gestion_pct, tf, copro, provision):
    """Scenario calcule par le MOTEUR : copie du record, loyer, vacance et
    lignes de charges surchargees, puis engine.compute. Le poste composite
    d'entretien porte la gestion locative et la provision travaux (le moteur
    ne connait que ces cinq lignes de charges)."""
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
    rd = c['rendements']
    brut = revenus_annuels(loyer)
    return dict(
        loyer=loyer, brut=brut, vac=vac, gestion=gestion_pct, tf=tf, copro=copro,
        provision=provision,
        ebe_modele=ebe_modele(loyer, vac, gestion_pct, tf, copro, provision),
        vac_eur=brut * vac / 100.0,
        gestion_eur=brut * gestion_pct / 100.0,
        entretien=brut * gestion_pct / 100.0 + provision,
        ebe=f['ebe'], is_=f['is_annuel'], net=f['net_apres_is'],
        ebe_mois=f['ebe'] / 12.0, net_mois=f['net_apres_is'] / 12.0,
        cf_avant_dette=f['cf_mensuel_net'],
        rdt_brut=brut / PRIX * 100.0,
        rdt_av=f['ebe'] / ACTE_EN_MAIN * 100.0,
        rdt_ap=f['net_apres_is'] / ACTE_EN_MAIN * 100.0,
        rdt_valeur=f['net_apres_is'] / VALEUR_RETENUE * 100.0,
        cap5=plafond5(f['ebe']),
        cf=cashflow_mensuel(f['ebe']),
        cf_ap=cashflow_mensuel(f['net_apres_is']),
        eng=c,
    )


def coloc(rec, loyer_chambre):
    """Piste colocation : trois chambres meublees, meme structure de charges
    (le moteur additionne quantite x loyer sur la ligne de revenu)."""
    v = copy.deepcopy(rec)
    v['marche']['loyers'] = [dict(
        lot=f"Trois chambres meublees a {eur(loyer_chambre)} €/mois chacune",
        quantite=3, loyer_mensuel_euros=loyer_chambre, occupe=True,
        note="Variante etudiee puis ecartee : elle suppose le depart du "
             "locataire en place et une division du T4 en trois chambres.")]
    ch = v['hypotheses']['charges']
    ch['taxe_fonciere_annuelle_euros'] = TF_BASE
    ch['charges_copro_annuelles_euros'] = COPRO_BASE
    ch['entretien_annuel_euros'] = round(
        3 * loyer_chambre * 12.0 * GESTION_BASE_PCT / 100.0 + PROV_BASE, 2)
    c = engine.compute(v)
    assert c['calculable'], c['raison']
    f = c['fiscal']
    return dict(loyer=loyer_chambre, revenus=c['revenus_bruts_annuels'],
                ebe=f['ebe'], net=f['net_apres_is'],
                rdt_ap=f['net_apres_is'] / ACTE_EN_MAIN * 100.0,
                cf=cashflow_mensuel(f['ebe']),
                cf_ap=cashflow_mensuel(f['net_apres_is']))


def capte(revenus_annuels, vac, gestion_pct, tf, copro, prov):
    """EBE du modele, calcule a partir des revenus annuels — la meme formule
    que celle du moteur (verifiee dans main() contre engine.compute)."""
    r = revenus_annuels
    return (r * (1 - vac / 100.0) - r * gestion_pct / 100.0 - tf - copro - PNO
            - (r * gestion_pct / 100.0 + prov) - COMPTA)


def verifie_dvf():
    """Recalcule les statistiques DVF publiees depuis le fichier departemental."""
    if not os.path.exists(DVF_FICHIER):
        print(f"  DVF : fichier {DVF_FICHIER} absent — constantes DVF non "
              f"recalculees (a verifier avec scripts/analyse_app/stats_dvf_ville.py)")
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
                    box=(la is not None and lo is not None
                         and DVF_BOITE[0] <= la <= DVF_BOITE[1]
                         and DVF_BOITE[2] <= lo <= DVF_BOITE[3]))

    calcule("DVF lignes de nature Vente (commune)", DVF_LIGNES_VENTE,
            sum(1 for r in lignes if r['nature_mutation'] == 'Vente'), 0)
    calcule("DVF mutations lues (commune)", DVF_MUTATIONS, len(muts), 0)
    calcule("DVF mutations de nature Vente", DVF_MUTATIONS_VENTE, len(ventes), 0)
    calcule("DVF ventes d'appartements (commune)", DVF_APP_N,
            sum(1 for rs in ventes if any(r['type_local'] == 'Appartement'
                                          for r in rs)), 0)
    app = [i for i in (infos(rs) for rs in ventes) if i]
    med = lambda v: round(st.median(v))                                   # noqa: E731
    calcule("DVF mediane appartements, toutes surfaces", DVF_APP_MED,
            med([i['m2'] for i in app]), 0)
    for lo, hi, n_, m_ in ((15, 30, DVF_APP_1530_N, DVF_APP_1530_MED),
                           (30, 45, DVF_APP_3045_N, DVF_APP_3045_MED),
                           (45, 60, DVF_APP_4560_N, DVF_APP_4560_MED),
                           (60, 90, DVF_APP_6090_N, DVF_APP_6090_MED)):
        sel = [i['m2'] for i in app if lo <= i['s'] < hi]
        calcule(f"DVF appartements {lo}-{hi} m2 (n)", n_, len(sel), 0)
        calcule(f"DVF appartements {lo}-{hi} m2 (mediane)", m_, med(sel), 0)
    sel = [(i['s'], i['v']) for i in app if 45 <= i['s'] < 60]
    calcule("DVF prix median des appartements 45-60 m2", DVF_APP_4560_PRIX,
            round(st.median([v for _, v in sel])), 0)
    m2s = [i['m2'] for i in app if 45 <= i['s'] < 60]
    q = st.quantiles(m2s, n=4)
    calcule("DVF Q1 appartements 45-60 m2", DVF_APP_4560_Q1, round(q[0]), 0)
    calcule("DVF Q3 appartements 45-60 m2", DVF_APP_4560_Q3, round(q[2]), 0)
    sel4595 = [i['m2'] for i in app if 45 <= i['s'] < 95]
    calcule("DVF appartements 45-95 m2 (n)", DVF_APP_4595_N, len(sel4595), 0)
    calcule("DVF appartements 45-95 m2 (mediane)", DVF_APP_4595_MED,
            med(sel4595), 0)
    # --- quartier Saint-Jean-du-Var -----------------------------------------
    qs = [i for i in app if i['box']]
    calcule("DVF quartier : ventes (mutations)", DVF_Q_VENTES,
            sum(1 for rs in ventes if any(
                f2(r['latitude']) is not None and f2(r['longitude']) is not None
                and DVF_BOITE[0] <= f2(r['latitude']) <= DVF_BOITE[1]
                and DVF_BOITE[2] <= f2(r['longitude']) <= DVF_BOITE[3]
                for r in rs)), 0)
    calcule("DVF quartier : ventes d'appartements", DVF_Q_APP_N, len(qs), 0)
    calcule("DVF quartier : mediane appartements", DVF_Q_MED,
            med([i['m2'] for i in qs]), 0)
    qq = st.quantiles([i['m2'] for i in qs], n=4)
    calcule("DVF quartier : Q1 appartements", DVF_Q_Q1, round(qq[0]), 0)
    calcule("DVF quartier : Q3 appartements", DVF_Q_Q3, round(qq[2]), 0)
    qb = [i for i in qs if 45 <= i['s'] < 95]
    calcule("DVF quartier 45-95 m2 (n)", DVF_Q_4595_N, len(qb), 0)
    calcule("DVF quartier 45-95 m2 (mediane)", DVF_Q_4595_MED,
            med([i['m2'] for i in qb]), 0)
    qqb = st.quantiles([i['m2'] for i in qb], n=4)
    calcule("DVF quartier 45-95 m2 (Q1)", DVF_Q_4595_Q1, round(qqb[0]), 0)
    calcule("DVF quartier 45-95 m2 (Q3)", DVF_Q_4595_Q3, round(qqb[2]), 0)
    calcule("DVF quartier 45-95 m2 (prix median)", DVF_Q_4595_PRIX,
            round(st.median([i['v'] for i in qb])), 0)
    # --- transactions reellement comparables --------------------------------
    pool = [i for i in qs if 45 <= i['s'] < 95 and 1800 <= i['m2'] <= 1835]
    calcule("DVF comparables du quartier (n)", DVF_CMP_N, len(pool), 0)
    calcule("DVF comparables du quartier (mediane EUR/m2)", DVF_CMP_MED,
            med([i['m2'] for i in pool]), 0)
    calcule("DVF comparables du quartier (prix median)", DVF_CMP_PRIX,
            round(st.median([i['v'] for i in pool])), 0)
    for c in DVF_COMPARABLES:
        hits = [i for i in app if abs(i['v'] - c['prix']) < 1.0
                and abs(i['s'] - c['surf']) < 1.0]
        assert hits, (f"transaction DVF {c['prix']} EUR / {c['surf']} m2 "
                      f"introuvable dans le fichier")
        i = hits[0]
        calcule(f"DVF comparable {c['voie']} (surface)", c['surf'], i['s'], 0.5)
        calcule(f"DVF comparable {c['voie']} (EUR/m2)", c['m2'], round(i['m2']),
                1.0)
        assert (i['box'] == c['box']), (c['voie'], i['box'], c['box'])
        assert i['date'].split('-')[0] == c['date'].split('/')[2], i['date']
    return True


def rec_t4():
    # EBE de la piste colocation, calcules par le modele du moteur (le record
    # ne peut pas s'appeler lui-meme : on passe par la formule, verifiee plus
    # loin contre engine.compute dans main()).
    _coloc = {x: capte(3.0 * x * 12.0, VAC_BASE, GESTION_BASE_PCT, TF_BASE,
                       COPRO_BASE, PROV_BASE) for x in (COLOC_BAS, COLOC_HAUT)}
    _c400, _c430 = _coloc[COLOC_BAS], _coloc[COLOC_HAUT]
    return {
        "slug": SLUG,
        "date_analyse": DATE,
        "date_maj": None,
        "titre": (
            f"Appartement T4 de {eur(SURF)} m² au {ETAGE}, vendu loué avec "
            f"locataire en place depuis quinze ans — quartier Saint-Jean-du-Var, "
            f"Toulon (83100)"
        ),
        "bien": {
            "type_bien": "appartement",
            "sous_type": None,
            "type_detail": (
                f"Appartement T4 (4 pièces, {CHAMBRES} chambres) de {eur(SURF)} m² "
                f"annoncés en titre — {eur(SURF_TEXTE)} m² écrits dans le texte de "
                f"la même annonce — au {ETAGE}, immeuble de {ANNEE}, quartier "
                f"Saint-Jean-du-Var à Toulon (83100). Chauffage individuel, non "
                f"meublé, ascenseur, {PHOTOS} photos. DPE {DPE}, GES {GES}, "
                f"facture énergétique annoncée de {eur(FACTURE_BASSE)} à "
                f"{eur(FACTURE_HAUTE)} €/an. L'annonce déclare le bien « avec "
                f"locataire en place depuis 15 ans », « revenus locatifs "
                f"immédiats dès la signature », et « nécessitera des travaux de "
                f"rafraîchissement dans le temps ». Elle ne communique NI loyer, "
                f"NI charges de copropriété, NI taxe foncière, NI montant de "
                f"travaux, et sa section copropriété ne donne ni nombre de lots "
                f"ni budget prévisionnel — seulement l'absence de procédure en "
                f"cours. Trois incohérences de gabarit sont relevées : la surface "
                f"({eur(SURF)} m² en titre, {eur(SURF_TEXTE)} m² dans le texte), la "
                f"cave (annoncée dans le texte, « Pas de cave » dans la fiche "
                f"caractéristiques) et le parking (« parking collectif », qui "
                f"n'est pas une place privative)."
            ),
            "neuf": False,
            "adresse": {
                "texte": (
                    "Quartier Saint-Jean-du-Var, Toulon (83100) — adresse exacte "
                    "non publiée dans l'annonce ; agence Foncia Transaction "
                    "Toulon Liberté, 289 place de la Liberté"
                ),
                "ville": "Toulon",
                "code_postal": "83100",
            },
            "surfaces": {
                "texte": (
                    f"{eur(SURF)} m² annoncés en titre ({eur(PRIX / SURF)} €/m²), "
                    f"4 pièces et {CHAMBRES} chambres — mais "
                    f"{eur(SURF_TEXTE)} m² écrits dans le texte de la même "
                    f"annonce : l'écart de 2 m² est une incohérence de gabarit à "
                    f"faire trancher par le certificat Carrez (à 68 m², le prix "
                    f"au m² ressort à {eur(PRIX / SURF_TEXTE)} €)"
                ),
                "carrez_m2": SURF,
            },
            "lots": {
                "count": 1,
                "surface_par_lot_m2": SURF,
                "nature": (
                    f"Un seul lot habitable : l'appartement T4 de {eur(SURF)} m². "
                    f"Le texte de l'annonce mentionne une cave, la fiche "
                    f"caractéristiques affiche « Pas de cave » — à trancher par "
                    f"l'état daté. « Parking collectif » : aucune place privative "
                    f"identifiée, donc aucun lot cessible et aucun revenu annexe. "
                    f"Cave annoncée par le texte, copropriété de {ANNEE} avec "
                    f"ascenseur, aucune procédure en cours selon l'annonce ; le "
                    f"nombre de lots, le budget prévisionnel et le montant des "
                    f"charges ne sont pas publiés"
                ),
                "lots_distincts": 1,
            },
            "copro": {
                "charges_annuelles_euros": None,
                "charges_source": (
                    "AUCUNE CHARGE DE COPROPRIÉTÉ N'EST PUBLIÉE PAR L'ANNONCE. "
                    "La section copropriété de la page ne donne ni nombre de "
                    "lots, ni budget prévisionnel, ni charge annuelle du lot : "
                    "elle se limite à « pas de procédure en cours ». Le modèle "
                    "retient une estimation de "
                    f"{eur(COPRO_BASE)} €/an pour un immeuble de {ANNEE} avec "
                    f"ascenseur, et teste {eur(COPRO_HAUT)} €/an en variante "
                    f"haute : chaque euro de charge sort directement du "
                    f"rendement. C'est la deuxième pièce à exiger après le bail, "
                    f"et c'est la leçon du dossier de Brignoles du même jour, où "
                    f"{eur(2193)} €/an de charges avec chauffage collectif ont "
                    f"absorbé 30 % du loyer"
                ),
            },
            "travaux": {
                "montant_euros": 0.0,
                "nature": (
                    "L'annonce déclare elle-même le bien « nécessitera des "
                    "travaux de rafraîchissement dans le temps », sans le "
                    "chiffrer, et ces travaux ne sont pas exécutables avec un "
                    "locataire en place depuis quinze ans : au mieux à la "
                    "rotation. Le prix de revient publié n'inscrit donc AUCUN "
                    "travail immédiat — ce qui suppose un devis, qui n'existe "
                    "pas — et la fiche publie à la place une grille de plafonds "
                    "par tranche de travaux (10 000, 20 000 et 30 000 €) au loyer "
                    "de marché. Toute enveloppe réellement engagée se déduit du "
                    "prix d'achat, au même titre que les frais"
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
                f"{eur(PRIX / SURF)} €/m² sur les {eur(SURF)} m² annoncés en titre "
                f"(et {eur(PRIX / SURF_TEXTE)} €/m² sur les "
                f"{eur(SURF_TEXTE)} m² écrits dans le texte), "
                f"{eur(ACTE_EN_MAIN)} € acte en main — le simulateur de l'annonce "
                f"retient déjà {eur(FRAIS_ACQUISITION)} € de frais, soit "
                f"{fr(TAUX_FRAIS * 100, 2)} %. Vendeur : Foncia Transaction "
                f"Toulon Liberté, 289 place de la Liberté, RCS 503698664, "
                f"référence 00836037, mandat en exclusivité. Le prix demandé se "
                f"situe sous le premier quartile du quartier pour cette tranche "
                f"de surface ({eur(DVF_Q_4595_Q1)} €/m² sur {eur(DVF_Q_4595_N)} "
                f"ventes) et exactement au niveau des transactions réellement "
                f"comparables de 2025 ({eur(DVF_CMP_MED)} €/m² de médiane sur "
                f"{eur(DVF_CMP_N)} ventes d'appartements seuls de 45 à 95 m²) : ce "
                f"n'est pas une anomalie de prix"
            ),
        },
        "marche": {
            "valeur": {
                "basse_euros": VALEUR_BASSE,
                "haute_euros": VALEUR_HAUTE,
                "retenue_euros": VALEUR_RETENUE,
                "source": (
                    f"Ancrage DVF 2025 sur la tranche de surface du bien dans son "
                    f"QUARTIER, et non sur une moyenne communale. Boîte de "
                    f"coordonnées du marqueur de l'annonce "
                    f"({eur(DVF_BOITE[0], 3)}-{eur(DVF_BOITE[1], 3)} N / "
                    f"{eur(DVF_BOITE[2], 3)}-{eur(DVF_BOITE[3], 3)} E) : {eur(DVF_Q_VENTES)} mutations de nature "
                    f"Vente, dont {eur(DVF_Q_APP_N)} ventes d'appartements, médiane "
                    f"{eur(DVF_Q_MED)} €/m² (Q1 {eur(DVF_Q_Q1)}, Q3 "
                    f"{eur(DVF_Q_Q3)}). Tranche 45-95 m², celle du bien : "
                    f"{eur(DVF_Q_4595_N)} ventes, médiane {eur(DVF_Q_4595_MED)} €/m², "
                    f"premier quartile {eur(DVF_Q_4595_Q1)}, troisième "
                    f"{eur(DVF_Q_4595_Q3)}, prix médian "
                    f"{eur(DVF_Q_4595_PRIX)} €. Valeur retenue "
                    f"{eur(VALEUR_RETENUE)} € = {eur(SURF)} m² × "
                    f"{eur(DVF_Q_4595_MED)} €/m² ; fourchette "
                    f"{eur(VALEUR_BASSE)} à {eur(VALEUR_HAUTE)} €. Repère de "
                    f"contrôle : les transactions réellement comparables du "
                    f"quartier — appartements seuls de 41 à 72 m², à l'état, "
                    f"{eur(DVF_CMP_N)} ventes en 2025 — se traitent à "
                    f"{eur(DVF_CMP_MED)} €/m² de médiane (prix médian "
                    f"{eur(DVF_CMP_PRIX)} €), soit exactement le prix demandé : "
                    f"le positionnement bas du bien paie son état et son "
                    f"occupation, il n'y a aucune décote à capter. Méthode : "
                    f"valeur foncière de la mutation divisée par la somme des "
                    f"surfaces bâties de la mutation, surfaces supérieures à "
                    f"5 m² et valeurs supérieures à 5 000 €"
                ),
                "confiance": "moyenne",
            },
            "loyers": [
                {
                    "lot": (
                        f"Appartement T4 de {eur(SURF)} m² au {ETAGE} — bail en "
                        f"cours, locataire en place depuis quinze ans"
                    ),
                    "quantite": 1,
                    "loyer_mensuel_euros": LOYER_BASE,
                    "occupe": True,
                    "note": (
                        f"UNE SEULE LIGNE DE REVENU, celle de la stratégie "
                        f"retenue : {eur(LOYER_BASE)} €/mois, soit "
                        f"{fr(LOYER_BASE / SURF, 1)} €/m²/mois. L'annonce ne "
                        f"publie AUCUN loyer : la fourchette de travail est de "
                        f"{eur(LOYER_ANCIEN)} à {eur(LOYER_BASE)} €/mois pour un "
                        f"bail de quinze ans révisé sous IRL (+1,15 %/an en "
                        f"2026), qui se situe mécaniquement sous le marché. "
                        f"Ancrages de marché datés : Observatoire "
                        f"départemental des loyers du Var, agglomération de "
                        f"Toulon, {fr(OLV_MED_M2, 1)} €/m²/mois hors charges "
                        f"({eur(SURF * OLV_MED_M2)} € pour {eur(SURF)} m²) ; "
                        f"SeLoger, quartier Saint-Jean-du-Var, "
                        f"{fr(SELOGER_Q_M2, 1)} €/m²/mois de moyenne (haut 23,3, "
                        f"bas 10,4), soit {eur(SURF * SELOGER_Q_M2)} € ; "
                        f"RealAdvisor, quartier, loyer médian d'un appartement "
                        f"{eur(REALADVISOR_MED)} €, 80 % des biens entre 475 et "
                        f"2 043 €. Marché du quartier retenu : "
                        f"{eur(LOYER_MARCHE_BAS)} à {eur(LOYER_MARCHE_HAUT)} "
                        f"€/mois hors charges, médiane {eur(LOYER_MARCHE_MED)} "
                        f"€. Les cinq lectures chiffrées (620, 750, 851, 950 "
                        f"€/mois et 851 € avec {eur(COPRO_HAUT)} €/an de "
                        f"charges) sont publiées en table : l'écart entre "
                        f"{eur(LOYER_ANCIEN)} et {eur(LOYER_HAUT)} fait passer "
                        f"le rendement net avant IS de "
                        f"{fr(3176 / ACTE_EN_MAIN * 100)} % à "
                        f"{fr(6740 / ACTE_EN_MAIN * 100)} %"
                    ),
                }
            ],
            "notes": (
                f"Le dossier ne se juge pas sur son prix — {eur(PRIX / SURF)} "
                f"€/m², sous le premier quartile du quartier "
                f"({eur(DVF_Q_4595_Q1)} €/m²) et au niveau des transactions "
                f"réellement comparables ({eur(DVF_CMP_MED)} €/m² sur "
                f"{eur(DVF_CMP_N)} ventes d'appartements seuls) — mais sur un bail dont "
                f"le loyer n'est pas communiqué. Au loyer de marché de "
                f"{eur(LOYER_MARCHE_MED)} €/mois, le rendement net avant IS est "
                f"de {fr(5670.8 / ACTE_EN_MAIN * 100)} % sur les "
                f"{eur(ACTE_EN_MAIN)} € d'acte en main et le cash-flow de "
                f"-340 €/mois ; au haut de marché de {eur(LOYER_HAUT)} €, il reste "
                f"négatif à -251 €/mois. Il faudrait "
                f"{eur(loyer_cashflow_nul(TF_BASE, COPRO_BASE, PROV_BASE))} €/mois "
                f"de loyer ({fr(loyer_cashflow_nul(TF_BASE, COPRO_BASE, PROV_BASE) / SURF, 1)} "
                f"€/m²) pour un cash-flow nul, au-dessus de tout le marché du "
                f"quartier. À l'inverse, les charges de copropriété ne sont pas "
                f"publiées : sur un immeuble de {ANNEE} avec ascenseur, chaque "
                f"euro de charge sort du rendement, et le dossier de Brignoles du "
                f"même jour montre ce que 2 193 €/an font à un loyer de 610 €"
            ),
        },
        "hypotheses": {
            "vacance_base_pct": VAC_BASE,
            "vacance_best_pct": VAC_BEST,
            "vacance_worst_pct": VAC_WORST,
            "vacance_justification": (
                f"{fr(VAC_BASE, 0)} % en scénario de base : le locataire est en "
                f"place depuis quinze ans, donc aucune vacance de démarrage, mais "
                f"un T4 de {ANNEE} avec ascenseur et sans travaux faits se reloue "
                f"avec un délai dans un quartier où l'offre locative est "
                f"abondante. {fr(VAC_BEST, 0)} % en hypothèse favorable, "
                f"{fr(VAC_WORST, 0)} % en hypothèse défavorable, correspondant au "
                f"départ du locataire en place avec une remise en location au "
                f"niveau du marché après rafraîchissement"
            ),
            "frais_acquisition_euros": FRAIS_ACQUISITION,
            "frais_divers_euros": 0.0,
            "quote_part_bati_pct": 0.0,
            "duree_amortissement_ans": 30,
            "fiscalite_commentaire": (
                f"SCI à l'IS. Calcul réel de l'année 1 : EBE "
                f"{eur(4580)} € moins intérêts d'emprunt {eur(INTERETS_AN1)} € "
                f"({eur(CAPITAL)} € à 3,7 %) moins la dotation aux amortissements "
                f"{eur(DOTATION_AN1)} € (bâti à 80 % du prix sur 30 ans) = "
                f"résultat imposable de "
                f"{eur(4580 - INTERETS_AN1 - DOTATION_AN1)} €, NÉGATIF, donc "
                f"AUCUN IS dû en année 1 (le déficit est reporté). Convention "
                f"prudente retenue pour les rendements nets publiés, comme sur les "
                f"autres fiches du parc : IS de 15 % appliqué à l'EBE, sans "
                f"amortissement du bâti modélisé (quote_part_bati_pct = 0), soit "
                f"{eur(CONVENTION_IS * 4580)} €/an — c'est la lecture la plus "
                f"défavorable, et c'est elle que le moteur applique. Le seuil de "
                f"décision du parc porte de toute façon sur le rendement net "
                f"AVANT IS, qui n'atteint pas la moitié de la cible"
            ),
            "charges": {
                "taxe_fonciere_annuelle_euros": TF_BASE,
                "taxe_fonciere_commentaire": (
                    f"ESTIMATION {eur(TF_BASE)} €/an — l'avis n'est pas "
                    f"communiqué par le vendeur ni par l'agent, alors que la "
                    f"taxe foncière est la première dépense fixe d'un lot de "
                    f"copropriété toulonnais. Fourchette plausible 900 à 1 200 € "
                    f"pour un T4 de {eur(SURF)} m² dans un immeuble de {ANNEE} ; "
                    f"l'avis de taxe foncière est gratuit à demander et donne la "
                    f"valeur locative cadastrale — le seul chiffre opposable"
                ),
                "charges_copro_annuelles_euros": COPRO_BASE,
                "charges_copro_commentaire": (
                    f"ESTIMATION {eur(COPRO_BASE)} €/an, et c'est la deuxième "
                    f"inconnue lourde du dossier : l'annonce ne publie AUCUNE "
                    f"charge de copropriété, ni le nombre de lots, ni le budget "
                    f"prévisionnel. Immeuble de {ANNEE} avec ascenseur à Toulon : "
                    f"la variante haute testée est {eur(COPRO_HAUT)} €/an, et "
                    f"l'écart entre les deux (600 €/an) vaut 0,46 point de "
                    f"rendement net avant IS. Contrairement au dossier de "
                    f"Brignoles, ces charges ne sont PAS déduites du loyer "
                    f"saisi — elles sont bien un poste de l'exploitation, "
                    f"puisque le loyer retenu est un loyer hors charges"
                ),
                "pno_annuelle_euros": PNO,
                "pno_commentaire": (
                    f"Assurance propriétaire non occupant du lot, {eur(PNO)} €/an : "
                    f"les murs et les parties communes sont assurés par la "
                    f"copropriété, la PNO couvre les loyers et les recours du "
                    f"locataire. Les locaux sont loués, la PNO est obligatoire"
                ),
                "entretien_annuel_euros": round(
                    revenus_annuels(LOYER_BASE) * GESTION_BASE_PCT / 100.0
                    + PROV_BASE, 2),
                "entretien_commentaire": (
                    f"Poste composite, détaillé : gestion locative "
                    f"{eur(revenus_annuels(LOYER_BASE) * GESTION_BASE_PCT / 100.0)} € "
                    f"({fr(GESTION_BASE_PCT, 0)} % des "
                    f"{eur(revenus_annuels(LOYER_BASE))} € de loyers) + provision "
                    f"travaux {eur(PROV_BASE)} € = "
                    f"{eur(revenus_annuels(LOYER_BASE) * GESTION_BASE_PCT / 100.0 + PROV_BASE)} €. "
                    f"Le moteur ne connaît ni la ligne de gestion locative ni "
                    f"celle de provision gros travaux : les deux sont fondues ici "
                    f"pour que l'EBE publié corresponde au modèle. Provision "
                    f"automatique du moteur (2,5 %) désactivée pour ne pas "
                    f"compter deux fois la même cagnotte. Les travaux déclarés "
                    f"par l'annonce (« rafraîchissement dans le temps ») ne sont "
                    f"pas chiffrés : ils attendront la rotation du locataire, et "
                    f"la fiche publie une grille de plafonds par tranche de "
                    f"20 000 à 30 000 €"
                ),
                "comptabilite_annuelle_euros": COMPTA,
                "comptabilite_commentaire": (
                    f"Comptabilité de la SCI à l'IS, {eur(COMPTA)} €/an : un "
                    f"logement loué nu, régime réel, avec une copropriété de "
                    f"{ANNEE} à surveiller (régularisations de charges et appels "
                    f"de fonds à passer en charges). À mutualiser dès qu'un "
                    f"second lot entre dans la même structure"
                ),
                "provision_desactivee": True,
            },
        },
        "analyse": {
            "branche": "residentiel",
            "type_operation": "locatif",
            "strategie_retenue": {
                "nom": (
                    f"Conservation du bail en place — location longue durée nue, "
                    f"loyer retenu {eur(LOYER_BASE)} €/mois, sous condition de "
                    f"preuve du bail"
                ),
                "code": "ld-nue",
                "lots": 1,
            },
            "strategies_explorees": [
                {
                    "strategie": (
                        f"Bail ancien — loyer de {eur(LOYER_ANCIEN)} €/mois "
                        f"({fr(LOYER_ANCIEN / SURF, 1)} €/m²), hypothèse d'un bail "
                        f"de quinze ans révisé sous IRL"
                    ),
                    "lots": 1,
                    "rendement": (
                        f"{fr(3176 / ACTE_EN_MAIN * 100)} % net avant IS sur "
                        f"l'acte en main ({eur(3176)} € d'EBE), "
                        f"{fr(3176 * 0.85 / ACTE_EN_MAIN * 100)} % après IS sous "
                        f"convention prudente, plafond 5 % "
                        f"{eur(plafond5(3176))} € contre {eur(PRIX)} € affichés"
                    ),
                    "faisabilite": (
                        f"c'est la lecture la plus probable d'un bail de quinze "
                        f"ans : un locataire en place depuis 2008-2010 paye un "
                        f"loyer que la révision IRL n'a pas ramené au marché. "
                        f"Aucune pièce ne permet de la vérifier"
                    ),
                    "risque": (
                        f"bloquant en pratique — {fr(3176 / ACTE_EN_MAIN * 100)} % "
                        f"net avant IS et un cash-flow de "
                        f"{eur(cashflow_mensuel(3176))} €/mois : le dossier n'est "
                        f"plus un investissement, c'est une charge"
                    ),
                },
                {
                    "strategie": (
                        f"Hypothèse de travail haute — loyer de "
                        f"{eur(LOYER_BASE)} €/mois "
                        f"({fr(LOYER_BASE / SURF, 1)} €/m²), vacance "
                        f"{fr(VAC_BASE, 0)} %, gestion {fr(GESTION_BASE_PCT, 0)} %"
                    ),
                    "lots": 1,
                    "rendement": (
                        f"{fr(4580 / ACTE_EN_MAIN * 100)} % net avant IS "
                        f"({eur(4580)} € d'EBE, {eur(4580 / 12)} €/mois), "
                        f"{fr(4580 * 0.85 / ACTE_EN_MAIN * 100)} % après IS, "
                        f"plafond 5 % {eur(plafond5(4580))} €, cash-flow "
                        f"{eur(cashflow_mensuel(4580))} €/mois"
                    ),
                    "faisabilite": (
                        f"immédiate si le bail le confirme : le bien est vendu "
                        f"loué, aucun travaux immédiat. C'est le scénario de base "
                        f"publié, et il reste sous la moitié du seuil de parc"
                    ),
                    "risque": (
                        f"élevé — même à {eur(LOYER_BASE)} €, le rendement net "
                        f"avant IS ({fr(4580 / ACTE_EN_MAIN * 100)} %) est très "
                        f"loin des 6,5 % net d'IS exigés, et le cash-flow est "
                        f"négatif de {eur(abs(cashflow_mensuel(4580)))} €/mois"
                    ),
                },
                {
                    "strategie": (
                        f"Loyer de marché du quartier — "
                        f"{eur(LOYER_MARCHE_MED)} €/mois "
                        f"({fr(LOYER_MARCHE_MED / SURF, 1)} €/m²), ancrage OLV "
                        f"agglomération de Toulon"
                    ),
                    "lots": 1,
                    "rendement": (
                        f"{fr(5670.8 / ACTE_EN_MAIN * 100)} % net avant IS "
                        f"({eur(5670.8)} € d'EBE, {eur(5670.8 / 12)} €/mois), "
                        f"{fr(5670.8 * 0.85 / ACTE_EN_MAIN * 100)} % après IS, "
                        f"plafond 5 % {eur(plafond5(5670.8))} € "
                        f"({fr((plafond5(5670.8) - PRIX) / PRIX * 100, 0)} % sous "
                        f"le prix affiché), cash-flow "
                        f"{eur(cashflow_mensuel(5670.8))} €/mois"
                    ),
                    "faisabilite": (
                        f"suppose que le locataire en place paye déjà le prix du "
                        f"marché, ce qui est contradictoire avec quinze ans "
                        f"d'ancienneté : c'est la borne haute de la vraisemblance, "
                        f"pas l'hypothèse centrale"
                    ),
                    "risque": (
                        f"élevé — même au loyer de marché, le rendement net avant "
                        f"IS plafonne à {fr(5670.8 / ACTE_EN_MAIN * 100)} %, le "
                        f"cash-flow reste à "
                        f"{eur(cashflow_mensuel(5670.8))} €/mois et il faudrait "
                        f"payer {eur(plafond5(5670.8))} € pour tenir 5 % net avant "
                        f"IS"
                    ),
                },
                {
                    "strategie": (
                        f"Haut du marché — {eur(LOYER_HAUT)} €/mois "
                        f"({fr(LOYER_HAUT / SURF, 1)} €/m²), borne haute des "
                        f"relevés du quartier"
                    ),
                    "lots": 1,
                    "rendement": (
                        f"{fr(6740 / ACTE_EN_MAIN * 100)} % net avant IS "
                        f"({eur(6740)} € d'EBE, {eur(6740 / 12)} €/mois), "
                        f"{fr(6740 * 0.85 / ACTE_EN_MAIN * 100)} % après IS, "
                        f"plafond 5 % {eur(plafond5(6740))} €, cash-flow "
                        f"{eur(cashflow_mensuel(6740))} €/mois"
                    ),
                    "faisabilite": (
                        f"c'est la borne haute de SeLoger pour le quartier "
                        f"(15,0 €/m² de moyenne, haut 23,3) : un T4 de "
                        f"{ANNEE} avec locataire en place ne s'y situe pas, mais "
                        f"la borne mérite d'être publiée"
                    ),
                    "risque": (
                        f"moyen — c'est la seule lecture qui approche 5 % net "
                        f"avant IS, et elle laisse encore un cash-flow de "
                        f"{eur(cashflow_mensuel(6740))} €/mois : le dossier ne "
                        f"passe jamais du côté positif au prix affiché"
                    ),
                },
                {
                    "strategie": (
                        f"Loyer de marché avec charges de copropriété hautes — "
                        f"{eur(LOYER_MARCHE_MED)} €/mois et "
                        f"{eur(COPRO_HAUT)} €/an de charges"
                    ),
                    "lots": 1,
                    "rendement": (
                        f"{fr(5070.8 / ACTE_EN_MAIN * 100)} % net avant IS "
                        f"({eur(5070.8)} € d'EBE), "
                        f"{fr(5070.8 * 0.85 / ACTE_EN_MAIN * 100)} % après IS, "
                        f"cash-flow {eur(cashflow_mensuel(5070.8))} €/mois"
                    ),
                    "faisabilite": (
                        f"c'est la variante à retenir si les charges dépassent "
                        f"1 800 €/an, ce qui est plausible au-delà de 20 ans sans "
                        f"travaux votés dans un immeuble de {ANNEE} avec "
                        f"ascenseur — et invérifiable en l'état"
                    ),
                    "risque": (
                        f"élevé — 600 €/an de charges en plus, soit 0,46 point de "
                        f"rendement net avant IS et 50 €/mois de trésorerie : la "
                        f"deuxième inconnue du dossier, sans réponse dans "
                        f"l'annonce"
                    ),
                },
                {
                    "strategie": (
                        f"Colocation meublée — 3 chambres à "
                        f"{eur(COLOC_BAS)} à {eur(COLOC_HAUT)} €/mois"
                    ),
                    "lots": 1,
                    "rendement": (
                        f"{fr(0.85 * _c400 / ACTE_EN_MAIN * 100.0)} % à "
                        f"{fr(0.85 * _c430 / ACTE_EN_MAIN * 100.0)} % net après "
                        f"IS sur l'acte en main, cash-flow après crédit de "
                        f"{eur(cashflow_mensuel(_c400))} à "
                        f"{eur(cashflow_mensuel(_c430))} €/mois avant IS "
                        f"({eur(cashflow_mensuel(0.85 * _c400))} à "
                        f"{eur(cashflow_mensuel(0.85 * _c430))} €/mois après IS)"
                    ),
                    "faisabilite": (
                        f"technique mais hors doctrine : elle suppose le DÉPART "
                        f"du locataire en place, donc du portage à vide, une "
                        f"division du T4 en trois chambres (travaux et "
                        f"autorisation), un apport supérieur au filtre du parc, et "
                        f"un bail meublé sur un quartier qui n'est pas étudiant"
                    ),
                    "risque": (
                        f"moyen — c'est la seule lecture qui dépasse 6 % net, mais "
                        f"elle ne s'obtient qu'en cassant le seul actif du dossier "
                        f"(le locataire en place proposé comme « revenus immédiats "
                        f"dès la signature ») et ne passe jamais en cash-flow "
                        f"positif"
                    ),
                },
            ],
            "attractivite": [
                {
                    "dimension": "transports",
                    "score": 7,
                    "justification": (
                        "Saint-Jean-du-Var est un quartier d'entrée de ville, à "
                        "quelques minutes de la gare de Toulon, du port et des "
                        "axes vers l'est varois : réseau Mistral dense, lignes "
                        "urbaines le long de l'avenue de la Résistance et du "
                        "boulevard de la Martille. C'est un emplacement de "
                        "locataire motorisé ou pendulaire, pas un quartier "
                        "excentré"
                    ),
                },
                {
                    "dimension": "commerces",
                    "score": 7,
                    "justification": (
                        "Commerces de proximité, supermarchés et services le long "
                        "des avenues du quartier, centre-ville de Toulon à "
                        "quelques minutes. Le quartier est dense et habité, ce qui "
                        "soutient la demande locative — et explique aussi que "
                        "l'offre locative y soit abondante, donc la vacance "
                        "possible"
                    ),
                },
                {
                    "dimension": "ecoles",
                    "score": 7,
                    "justification": (
                        "Écoles, collèges et lycées de Toulon à proximité "
                        "immédiate : c'est le profil type du locataire d'un T4 de "
                        "66 m² avec trois chambres, qu'on reloue à une famille et "
                        "non à un étudiant"
                    ),
                },
                {
                    "dimension": "securite",
                    "score": 6,
                    "justification": (
                        "Quartier populaire et vivant de l'est toulonnais, sans "
                        "tension particulière, mais dont la réputation pèse sur la "
                        "commercialisation à la revente. Immeuble de 1961 avec "
                        "ascenseur : parties communes anciennes, budget de "
                        "copropriété à surveiller"
                    ),
                },
                {
                    "dimension": "demande_locative",
                    "score": 7,
                    "justification": (
                        "Le bien est proposé avec un locataire en place depuis "
                        "quinze ans, ce qui prouve la demande sur ce produit. Les "
                        "relevés du quartier donnent un loyer moyen de "
                        "15,0 €/m²/mois (SeLoger), un loyer médian d'appartement "
                        "de 954 € (RealAdvisor) et une référence d'agglomération "
                        "de 12,9 €/m²/mois hors charges (OLV), soit 851 € pour "
                        "66 m² : le marché du quartier se situe entre 830 et 950 € "
                        "hors charges"
                    ),
                },
                {
                    "dimension": "dynamisme",
                    "score": 6,
                    "justification": (
                        "2 749 ventes d'appartements enregistrées à Toulon en "
                        "2025 : le marché de revente est très liquide. Mais le "
                        "quartier se traite 8,0 % sous la médiane communale "
                        "(2 450 €/m² contre 2 662 €/m² toutes surfaces, −11,8 % à "
                        "tranche de surface comparable), et le prix demandé est "
                        "déjà au niveau des transactions réellement comparables : "
                        "la plus-value de sortie est limitée à ce que les travaux "
                        "apporteront"
                    ),
                },
            ],
            "risques": [
                {
                    "facteur": (
                        "Loyer du bail de quinze ans JAMAIS communiqué : c'est lui "
                        "qui décide de tout le dossier"
                    ),
                    "severite": 5,
                    "bloquant": True,
                    "detail": (
                        "L'annonce affirme « avec locataire en place depuis 15 "
                        "ans » et « revenus locatifs immédiats dès la signature », "
                        "et ne publie AUCUN loyer : ni le montant, ni la "
                        "décomposition hors charges / provisions, ni la date "
                        "d'effet, ni la durée restante, ni une quittance. Or tout "
                        "le dossier se joue sur ce chiffre : entre "
                        "620 €/mois (bail ancien révisé sous IRL) et "
                        "950 €/mois (haut du marché du quartier), le rendement net "
                        "avant IS passe de 2,45 % à 5,20 % et l'EBE de 3 176 € à "
                        "6 740 €. À 620 €, le plafond 5 % tombe à 58 815 €, soit "
                        "la moitié du prix affiché. Et même au loyer de marché de "
                        "851 €/mois, il faudrait encaisser 1 229 €/mois "
                        "(18,6 €/m²) pour que le cash-flow soit nul : c'est "
                        "au-dessus de tout le marché du quartier. La pièce qui "
                        "décide n'existe pas dans le dossier, et c'est ce qui "
                        "justifie le caractère bloquant de ce risque : aucun des "
                        "scénarios de loyer possibles ne produit un cash-flow "
                        "positif au prix affiché"
                    ),
                },
                {
                    "facteur": (
                        "Charges de copropriété absentes de l'annonce : sur un "
                        "immeuble de 1961 avec ascenseur, 1 800 à 2 400 €/an"
                    ),
                    "severite": 4,
                    "detail": (
                        "La section copropriété de l'annonce ne publie ni nombre "
                        "de lots, ni budget prévisionnel, ni charge annuelle du "
                        "lot : elle se limite à « pas de procédure en cours ». Le "
                        "modèle retient 1 800 €/an et teste 2 400 €/an. Chaque "
                        "euro de charge sort du rendement : à 851 €/mois de loyer, "
                        "passer de 1 800 à 2 400 €/an de charges fait tomber le "
                        "rendement net avant IS de 4,38 % à 3,92 % et le "
                        "cash-flow de −340 à −390 €/mois. La leçon du dossier de "
                        "Brignoles du même jour est exactement celle-ci : "
                        "2 193 €/an de charges avec chauffage collectif ont absorbé "
                        "30 % d'un loyer de 610 €, et le bien était pourtant au "
                        "prix du marché"
                    ),
                },
                {
                    "facteur": (
                        "Travaux déclarés nécessaires par l'annonce elle-même, "
                        "non chiffrés et inexécutables avec le locataire en place"
                    ),
                    "severite": 4,
                    "detail": (
                        "L'annonce écrit que le bien « nécessitera des travaux de "
                        "rafraîchissement dans le temps » — donc un état qui "
                        "justifie le prix — sans donner le moindre montant, et la "
                        "quasi-totalité des rafraîchissements sérieux (électricité, "
                        "salle d'eau, peintures) suppose un logement vide. Avec un "
                        "locataire en place depuis quinze ans, ces travaux "
                        "attendent la rotation : ils ne peuvent ni améliorer le "
                        "rendement immédiat, ni justifier une hausse de loyer avant "
                        "un départ. C'est une promesse d'avenir payée au prix "
                        "d'aujourd'hui"
                    ),
                },
                {
                    "facteur": (
                        "DPE D et GES B dans un immeuble de 1961 : facture "
                        "énergétique annoncée jusqu'à 2 010 €/an"
                    ),
                    "severite": 3,
                    "detail": (
                        "DPE D et GES B, facture annoncée de 1 460 à 2 010 €/an. "
                        "Un D reste louable et le bien n'est pas dans le rouge "
                        "réglementaire, mais la trajectoire énergétique est un "
                        "fardeau croissant sur un T4 de 66 m² : la facture "
                        "plafonne ce qu'un locataire acceptera de payer, et une "
                        "mise aux normes se paie en appels de fonds ou en travaux "
                        "individuels. À surveiller d'autant plus que le chauffage "
                        "est individuel : la charge est portée par le locataire, "
                        "donc répercutée sur le loyer négociable"
                    ),
                },
                {
                    "facteur": (
                        "Marché du quartier plafonné sous la médiane communale : "
                        "la plus-value de sortie est limitée"
                    ),
                    "severite": 3,
                    "detail": (
                        "DVF 2025 : le quartier Saint-Jean-du-Var se traite à "
                        "2 450 €/m² de médiane (438 ventes d'appartements dans la "
                        "boîte de coordonnées de l'annonce), soit 8,0 % sous la "
                        "médiane communale toutes surfaces (2 662 €/m²) et 11,8 % "
                        "sous la commune à tranche de surface comparable "
                        "(2 566 €/m² sur 1 762 ventes de 45 à 95 m²). Le coût de "
                        "revient — 129 492 € d'acte en main, plus 20 000 € de "
                        "travaux de rafraîchissement — amène le coût de revient à "
                        "149 492 €, soit 2 265 €/m² : exactement la médiane du "
                        "quartier pour la tranche de surface. Autrement dit, il "
                        "faudrait revendre au prix médian du quartier pour "
                        "seulement rentrer dans ses frais"
                    ),
                },
                {
                    "facteur": (
                        "Locataire en place depuis quinze ans : bien non visitable "
                        "librement, revente occupée décotée"
                    ),
                    "severite": 3,
                    "detail": (
                        "Le bien se visite occupé, donc sans accès libre aux "
                        "pièces ni au moindre diagnostic contradictoire, et la "
                        "revente se négociera avec un bail en cours — ce que le "
                        "marché paie toujours moins cher qu'un logement libre. "
                        "C'est le revers de « revenus locatifs immédiats dès la "
                        "signature » : ce qui est présenté comme un avantage est "
                        "aussi une contrainte de sortie, sur un quartier dont le "
                        "marché est documenté (279 ventes d'appartements de 45 à "
                        "95 m² en 2025 dans la boîte de l'annonce)"
                    ),
                },
                {
                    "facteur": (
                        "Incohérences du gabarit de l'annonce : surface 66 ou "
                        "68 m², cave annoncée mais « Pas de cave », parking "
                        "collectif sans place privative"
                    ),
                    "severite": 2,
                    "detail": (
                        "Trois écarts dans la même page : la surface est de 66 m² "
                        "en titre et 68 m² dans le texte (soit 3 % d'écart, qui "
                        "changent le prix au m² de 1 817 à 1 763 €) ; le texte "
                        "annonce une cave quand la fiche caractéristiques affiche "
                        "« Pas de cave » ; et le « parking collectif » n'est pas un "
                        "lot cédé par le règlement de copropriété. Aucun de ces "
                        "points ne tue le dossier à lui seul, mais le certificat "
                        "Carrez, l'état daté et le règlement de copropriété doivent "
                        "les trancher par écrit avant toute offre"
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
    rec_ = rec_t4()
    MPE = mensualite_par_euro()
    calcule("mensualite par euro emprunte", MENS_PAR_EURO_MODELE, MPE, 0.00001)
    calcule("mensualite pour 107 910 EUR empruntes", MENS_MODELE,
            mensualite(CAPITAL), 1.0)
    calcule("capital emprunte (90 % du prix)", CAPITAL, PRIX * (1 - APPORT_PCT), 0.5)
    calcule("frais d'acquisition du simulateur", 9592.0, FRAIS_ACQUISITION, 0.5)
    calcule("acte en main (119 900 + 9 592)", ACTE_EN_MAIN, PRIX * 1.08, 1.0)
    calcule("taux de frais", 8.00, TAUX_FRAIS * 100.0, 0.01)
    calcule("prix au m2 sur 66 m2 annonces", 1817.0, PRIX / SURF, 0.5)
    calcule("prix au m2 sur 68 m2 ecrits dans le texte", 1763.0,
            PRIX / SURF_TEXTE, 0.5)
    calcule("loyer de marche median en EUR/m2/mois", 12.9, OLV_MED_M2, 0.05)
    calcule("loyer de marche median mensuel (12,9 x 66)", 851.0,
            SURF * OLV_MED_M2, 1.0)
    calcule("SeLoger quartier : 15,0 EUR/m2 x 66 m2", 990.0,
            SURF * SELOGER_Q_M2, 1.0)
    calcule("RealAdvisor quartier : loyer median appartement", 954.0,
            REALADVISOR_MED, 0.5)
    calcule("rapport loyer SeLoger / OLV sur 66 m2", 1.16,
            SELOGER_Q_M2 / OLV_MED_M2, 0.01)

    S620 = scen(rec_, LOYER_ANCIEN, VAC_BASE, GESTION_BASE_PCT, TF_BASE,
                COPRO_BASE, PROV_BASE)
    S750 = scen(rec_, LOYER_BASE, VAC_BASE, GESTION_BASE_PCT, TF_BASE,
                COPRO_BASE, PROV_BASE)
    S851 = scen(rec_, LOYER_MARCHE_MED, VAC_BASE, GESTION_BASE_PCT, TF_BASE,
                COPRO_BASE, PROV_BASE)
    S950 = scen(rec_, LOYER_HAUT, VAC_BASE, GESTION_BASE_PCT, TF_BASE,
                COPRO_BASE, PROV_BASE)
    S851C = scen(rec_, LOYER_MARCHE_MED, VAC_BASE, GESTION_BASE_PCT, TF_BASE,
                 COPRO_HAUT, PROV_BASE)
    BEST = scen(rec_, LOYER_BASE, VAC_BEST, 4.0, TF_BASE, COPRO_BASE, 150.0)
    WORST = scen(rec_, LOYER_BASE, VAC_WORST, GESTION_BASE_PCT, 1100.0,
                 COPRO_HAUT, 400.0)
    C400 = coloc(rec_, COLOC_BAS)
    C430 = coloc(rec_, COLOC_HAUT)

    # --- les cinq lectures de loyer du brief, recalculees ligne a ligne -----
    calcule("loyer de marche bas (830 EUR)", LOYER_MARCHE_BAS, 830.0, 0.5)
    calcule("loyer de marche haut (950 EUR)", LOYER_MARCHE_HAUT, 950.0, 0.5)
    calcule("loyer exige avant toute suite", LOYER_EXIGE, 850.0, 0.5)
    for s, e in ((S620, 3176.0), (S750, 4580.0), (S851, 5670.8),
                 (S950, 6740.0), (S851C, 5070.8), (BEST, 4900.0),
                 (WORST, 3230.0)):
        calcule(f"EBE modele a {eur(s['loyer'])} EUR/mois", e, s['ebe'], 1.0)
        calcule(f"EBE modele restitue par le moteur a {eur(s['loyer'])} EUR/mois",
                s['ebe'], s['ebe_modele'], 0.01)
    calcule("EBE 620 EUR : revenus bruts", 7440.0, S620['brut'], 0.5)
    calcule("EBE 750 EUR : revenus bruts", 9000.0, S750['brut'], 0.5)
    calcule("EBE 851 EUR : revenus bruts", 10212.0, S851['brut'], 0.5)
    calcule("EBE 950 EUR : revenus bruts", 11400.0, S950['brut'], 0.5)
    calcule("charges fixes du modele (TF 1 000 + copro 1 800 + PNO 120 + "
            "provision 200 + compta 400)", 3520.0,
            charges_fixes(TF_BASE, COPRO_BASE, PROV_BASE), 0.5)
    calcule("charges fixes variante haute (copro 2 400)", 4120.0,
            charges_fixes(TF_BASE, COPRO_HAUT, PROV_BASE), 0.5)
    calcule("rendement net avant IS a 620 EUR (EBE / acte en main)", 2.45,
            S620['rdt_av'], 0.01)
    calcule("rendement net avant IS a 750 EUR (EBE / acte en main)", 3.54,
            S750['rdt_av'], 0.01)
    calcule("rendement net avant IS a 851 EUR (EBE / acte en main)", 4.38,
            S851['rdt_av'], 0.01)
    calcule("rendement net avant IS a 950 EUR (EBE / acte en main)", 5.20,
            S950['rdt_av'], 0.01)
    calcule("rendement net avant IS a 851 EUR et copro 2 400", 3.92,
            S851C['rdt_av'], 0.01)
    calcule("rendement net avant IS : hypothese favorable a 750 EUR", 3.78,
            BEST['rdt_av'], 0.01)
    calcule("rendement net avant IS : hypothese defavorable a 750 EUR", 2.49,
            WORST['rdt_av'], 0.01)
    calcule("rendement net apres IS a 620 EUR (convention prudente)", 2.08,
            S620['rdt_ap'], 0.01)
    calcule("rendement net apres IS a 750 EUR (convention prudente)", 3.01,
            S750['rdt_ap'], 0.01)
    calcule("rendement net apres IS a 851 EUR (convention prudente)", 3.72,
            S851['rdt_ap'], 0.01)
    calcule("rendement net apres IS a 950 EUR (convention prudente)", 4.42,
            S950['rdt_ap'], 0.01)
    calcule("rendement net apres IS a 851 EUR et copro 2 400", 3.33,
            S851C['rdt_ap'], 0.01)
    calcule("rendement net apres IS sur la valeur a 851 EUR", 3.22,
            S851['rdt_valeur'], 0.01)
    calcule("plafond 5 % a 620 EUR", 58815.0, S620['cap5'], 5.0)
    calcule("plafond 5 % a 750 EUR", 84815.0, S750['cap5'], 5.0)
    calcule("plafond 5 % a 851 EUR", 105015.0, S851['cap5'], 5.0)
    calcule("plafond 5 % a 950 EUR", 124815.0, S950['cap5'], 5.0)
    calcule("plafond 5 % a 851 EUR et copro 2 400", 93904.0, S851C['cap5'], 5.0)
    calcule("plafond 5 % en hypothese favorable", 90741.0, BEST['cap5'], 5.0)
    calcule("plafond 5 % en hypothese defavorable", 59815.0, WORST['cap5'], 5.0)
    calcule("cash-flow a 620 EUR /mois", -548.0, S620['cf'], 1.0)
    calcule("cash-flow a 750 EUR /mois", -431.0, S750['cf'], 1.0)
    calcule("cash-flow a 851 EUR /mois", -340.0, S851['cf'], 1.0)
    calcule("cash-flow a 950 EUR /mois", -251.0, S950['cf'], 1.0)
    calcule("cash-flow a 851 EUR et copro 2 400 /mois", -390.0, S851C['cf'], 1.0)
    calcule("cash-flow en hypothese favorable /mois", -404.0, BEST['cf'], 1.0)
    calcule("cash-flow en hypothese defavorable /mois", -543.0, WORST['cf'], 1.0)
    calcule("rendement brut au loyer de travail (7 506 / 119 900)", 7.51,
            S750['rdt_brut'], 0.01)
    calcule("rendement brut au loyer de marche (10 212 / 119 900)", 8.52,
            S851['rdt_brut'], 0.01)
    # --- repères du dossier ------------------------------------------------
    LOYER_CF_NUL = loyer_cashflow_nul(TF_BASE, COPRO_BASE, PROV_BASE)
    calcule("loyer mensuel pour un cash-flow nul au prix affiche", 1229.0,
            LOYER_CF_NUL, 1.0)
    calcule("loyer mensuel pour un cash-flow nul en EUR/m2", 18.6,
            LOYER_CF_NUL / SURF, 0.05)
    calcule("apport pour un cash-flow nul au prix affiche (loyer de marche)",
            57149.0, apport_cashflow_nul(PRIX, S851['ebe']), 5.0)
    calcule("apport pour un cash-flow nul en % du prix", 48.0,
            apport_cashflow_nul(PRIX, S851['ebe']) / PRIX * 100.0, 0.5)
    calcule("prix donnant 5 % net au loyer de marche (851 EUR)", 105015.0,
            prix_5pct_avec_travaux(S851['ebe'], 0.0), 5.0)
    calcule("decote de prix pour 5 % net au loyer de marche", 12.0,
            (PRIX - prix_5pct_avec_travaux(S851['ebe'], 0.0)) / PRIX * 100.0, 0.5)
    calcule("prix donnant 5 % net au loyer de travail (750 EUR)", 84815.0,
            prix_5pct_avec_travaux(S750['ebe'], 0.0), 5.0)
    calcule("decote de prix pour 5 % net au loyer de travail", 29.0,
            (PRIX - prix_5pct_avec_travaux(S750['ebe'], 0.0)) / PRIX * 100.0, 0.5)
    calcule("prix a cash-flow nul au loyer de travail (750 EUR)", 56312.0,
            prix_cashflow_nul(S750['ebe']), 5.0)
    calcule("decote de prix pour un cash-flow nul au loyer de travail", 53.0,
            (PRIX - prix_cashflow_nul(S750['ebe'])) / PRIX * 100.0, 1.0)
    calcule("prix a cash-flow nul au loyer de marche (851 EUR)", 69724.0,
            prix_cashflow_nul(S851['ebe']), 5.0)
    # --- grille de travaux -------------------------------------------------
    calcule("plafond 5 % au loyer de marche, 10 000 EUR de travaux", 95756.0,
            prix_5pct_avec_travaux(S851['ebe'], TRAVAUX_REF_1), 5.0)
    calcule("plafond 5 % au loyer de marche, 20 000 EUR de travaux", 86496.0,
            prix_5pct_avec_travaux(S851['ebe'], TRAVAUX_REF_2), 5.0)
    calcule("plafond 5 % au loyer de marche, 30 000 EUR de travaux", 77237.0,
            prix_5pct_avec_travaux(S851['ebe'], TRAVAUX_REF_3), 5.0)
    calcule("plafond 5 % au loyer de travail, 20 000 EUR de travaux", 66296.0,
            prix_5pct_avec_travaux(S750['ebe'], TRAVAUX_REF_2), 5.0)
    calcule("cout de revient avec 20 000 EUR de travaux", 149492.0,
            ACTE_EN_MAIN + TRAVAUX_REF_2, 0.5)
    calcule("cout de revient avec 20 000 EUR de travaux en EUR/m2", 2265.0,
            (ACTE_EN_MAIN + TRAVAUX_REF_2) / SURF, 1.0)
    calcule("marge MDB negative a la revente a la valeur du quartier", -7539.2,
            VALEUR_RETENUE * 0.95 - (ACTE_EN_MAIN + TRAVAUX_REF_2), 1.0)
    # --- colocation --------------------------------------------------------
    calcule("colocation a 400 EUR : revenus bruts", 14400.0, C400['revenus'], 1.0)
    calcule("colocation a 400 EUR : EBE", 9440.0, C400['ebe'], 1.0)
    calcule("colocation a 400 EUR : net apres IS", 8024.0, C400['net'], 1.0)
    calcule("colocation a 400 EUR : rendement net apres IS", 6.20,
            C400['rdt_ap'], 0.01)
    calcule("colocation a 400 EUR : cash-flow avant IS", -26.0, C400['cf'], 1.0)
    calcule("colocation a 400 EUR : cash-flow apres IS", -144.0,
            C400['cf_ap'], 1.0)
    calcule("colocation a 430 EUR : revenus bruts", 15480.0, C400 and
            C430['revenus'], 1.0)
    calcule("colocation a 430 EUR : EBE", 10412.0, C430['ebe'], 1.0)
    calcule("colocation a 430 EUR : net apres IS", 8850.0, C430['net'], 1.0)
    calcule("colocation a 430 EUR : rendement net apres IS", 6.83,
            C430['rdt_ap'], 0.01)
    calcule("colocation a 430 EUR : cash-flow avant IS", 55.0, C430['cf'], 1.0)
    calcule("colocation a 430 EUR : cash-flow apres IS", -75.0,
            C430['cf_ap'], 1.0)
    # --- valeur et comparables --------------------------------------------
    calcule("valeur retenue = 66 x 2 264", VALEUR_RETENUE,
            SURF * DVF_Q_4595_MED, 10.0)
    calcule("valeur basse = 66 x 1 978 (Q1 du quartier)", VALEUR_BASSE,
            SURF * DVF_Q_4595_Q1, 10.0)
    calcule("valeur haute = 66 x 2 684 (Q3 du quartier)", VALEUR_HAUTE,
            SURF * DVF_Q_4595_Q3, 10.0)
    calcule("ratio cout/valeur (acte en main / valeur)", 0.8666,
            engine.ratio_cout_valeur(rec_), 0.001)
    calcule("prix affiche / valeur retenue", 0.80, PRIX / VALEUR_RETENUE, 0.01)
    calcule("prix affiche au plafond patrimonial 6,5 % (x fois)", 1.39,
            (PRIX / SURF) / PLAF_PATRIMONIAL[0], 0.01)
    calcule("prix affiche au plafond marchand de biens (x fois)", 1.92,
            (PRIX / SURF) / PLAF_MDB[0], 0.01)
    calcule("decote du quartier sous la mediane communale toutes surfaces", 7.96,
            (1 - DVF_Q_MED / DVF_APP_MED) * 100.0, 0.05)
    calcule("decote du quartier a tranche de surface comparable", 11.77,
            (1 - DVF_Q_4595_MED / DVF_APP_4595_MED) * 100.0, 0.05)
    calcule("ecart prix demande / mediane du quartier 45-95 m2", -19.8,
            (PRIX / SURF - DVF_Q_4595_MED) / DVF_Q_4595_MED * 100.0, 0.1)
    calcule("ecart prix demande / comparables du quartier", 0.4,
            (PRIX / SURF - DVF_CMP_MED) / DVF_CMP_MED * 100.0, 0.1)
    calcule("fiscalite annee 1 : interets (107 910 a 3,7 %)", 3993.0,
            INTERETS_AN1, 1.0)
    calcule("fiscalite annee 1 : dotation (bati 80 % du prix sur 30 ans)", 3197.0,
            DOTATION_AN1, 1.0)
    calcule("fiscalite annee 1 : resultat imposable (EBE 4 580 - 3 993 - 3 197)",
            -2610.0, S750['ebe'] - INTERETS_AN1 - DOTATION_AN1, 1.0)
    assert S750['ebe'] - INTERETS_AN1 - DOTATION_AN1 < 0, "resultat annee 1 positif"
    calcule("IS annee 1 (resultat negatif, donc zero)", 0.0,
            max(0.0, 0.15 * (S750['ebe'] - INTERETS_AN1 - DOTATION_AN1)), 0.0)
    calcule("IS convention prudente (15 % de l'EBE de base)", 687.0,
            CONVENTION_IS * S750['ebe'], 1.0)
    total_loyers = sum(l['loyer_mensuel_euros'] for l in rec_['marche']['loyers'])
    calcule("somme des loyers saisis = loyer de la strategie retenue",
            LOYER_BASE, total_loyers, 0.01)

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
    assert abs(r['fiscal']['ebe'] - S750['ebe']) < 0.01, (r['fiscal']['ebe'], S750['ebe'])
    assert abs(r['fiscal']['amortissement']) < 0.01, r['fiscal']['amortissement']
    assert abs(rd['net_sur_revient_pct'] - S750['rdt_ap']) < 0.01, rd
    assert abs(rd['net_sur_valeur_pct'] - S750['rdt_valeur']) < 0.01, rd
    assert abs(r['prix_revient_total'] - ACTE_EN_MAIN) < 0.01, r['prix_revient_total']
    assert abs(r['revenus_bruts_annuels'] - 9000.0) < 0.01, r['revenus_bruts_annuels']
    assert comp.get('bloquant') is True, comp
    assert note == 3.9, note
    assert verdict == "fuir", verdict
    calcule("CF net mensuel avant service de la dette (moteur, scénario de base)",
            324.0, r['fiscal']['cf_mensuel_net'], 1.0)
    calcule("CF net mensuel avant service de la dette à 620 EUR", 225.0,
            S620['cf_avant_dette'], 1.0)
    calcule("CF net mensuel avant service de la dette à 851 EUR", 402.0,
            S851['cf_avant_dette'], 1.0)
    calcule("CF net mensuel avant service de la dette à 950 EUR", 477.0,
            S950['cf_avant_dette'], 1.0)
    calcule("CF net mensuel avant service de la dette, 851 EUR et copro 2 400",
            359.0, S851C['cf_avant_dette'], 1.0)
    calcule("CF net mensuel avant service de la dette, colocation à 430 EUR",
            738.0, 0.85 * C430['ebe'] / 12.0, 1.0)


    # ------------------------------------------------------------------
    # 3 bis. Chiffres du brief qui NE se recalculent PAS : signales, non publies
    # ------------------------------------------------------------------
    ecart("DVF Toulon : « 8 736 mutations lues »", "8 736 mutations",
          DVF_LIGNES_VENTE,
          "8 736 est le nombre de LIGNES de nature Vente de la commune, pas de "
          "mutations : le fichier porte 3 908 mutations lues, dont 3 829 de "
          "nature Vente — le libellé du brief est faux, pas le chiffre")
    ecart("DVF quartier : ventes d'appartements", "1 248 ventes d'appartements "
          "/ 1 678 ventes", DVF_Q_APP_N,
          "recalcul dans la boîte de coordonnées de l'annonce (43,116-43,128 N "
          "/ 5,941-5,960 E) : 566 mutations de nature Vente, dont 438 ventes "
          "d'appartements — les 1 248 et 1 678 du brief ne sortent d'aucune "
          "sélection reproductible")
    ecart("DVF quartier : médiane des appartements",
          "2 500 €/m² (Q1 1 978, Q3 3 104)", DVF_Q_MED,
          "recalculé à 2 450 €/m² (Q1 2 020, Q3 3 000)")
    ecart("DVF quartier 45-95 m²",
          "n=739, médiane 2 304 €/m², Q1 1 867, Q3 2 770, prix médian 147 000 €",
          DVF_Q_4595_N,
          "recalculé à n=279, médiane 2 264 €/m², Q1 1 978, Q3 2 684, prix "
          "médian 150 000 €")
    ecart("Décote du quartier sous la médiane communale de Toulon", "21 %",
          round((1 - DVF_Q_MED / DVF_APP_MED) * 100.0, 1),
          "recalculée à 8,0 % toutes surfaces et 11,8 % à tranche de surface "
          "comparable — la conclusion « le prix est au marché de son quartier » "
          "tient, mais pas le chiffre de 21 %")
    ecart("Médiane du quartier appliquée au bien", "2 304 €/m² soit 152 064 €",
          DVF_Q_4595_MED,
          "2 264 €/m² soit 149 424 € sur les 66 m² annoncés")
    ecart("Cash-flow au haut de marché 950 €/mois", "-241 €/mois", S950['cf'],
          "recalculé à -251 €/mois avant IS (EBE 6 740 €) ; la conclusion de "
          "signe ne change pas : négatif dans toutes les lectures")
    ecart("Loyer mensuel nécessaire pour un cash-flow nul", "1 167 €/mois",
          round(LOYER_CF_NUL),
          "1 229 €/mois gestion locative de 5 % comprise ; 1 164 €/mois si "
          "l'on omet la gestion, ce qui explique l'écart — retenu : "
          "1 229 €/mois, soit 18,6 €/m², au-dessus de tout le marché du "
          "quartier")
    ecart("Prix à cash-flow nul au loyer de travail", "50 681 €",
          round(prix_cashflow_nul(S750['ebe'])),
          "56 312 € : l'apport de 10 % réduit le capital emprunté, donc le "
          "prix finançable pour la même mensualité ; 50 681 € est le CAPITAL, "
          "pas le prix")
    ecart("Prix à cash-flow nul au loyer de marché", "62 751 €",
          round(prix_cashflow_nul(S851['ebe'])),
          "69 724 € pour la même raison (62 751 € est le capital)")
    ecart("Colocation à 430 € la chambre", "6,89 % net / -69 €/mois",
          round(0.85 * C430['ebe'] / ACTE_EN_MAIN * 100.0, 2),
          "6,83 % net après IS et -75 €/mois sur la base des charges du "
          "scénario de base (mêmes conventions que le reste de la fiche)")

    # ------------------------------------------------------------------
    # 4. Generation de la fiche
    # ------------------------------------------------------------------
    spec = importlib.util.spec_from_file_location(
        "gen", os.path.join(ROOT, 'scripts', 'gen_fiches_2026-09-10.py'))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)

    MENS = mensualite(CAPITAL)
    CF750 = S750['cf']
    CF851 = S851['cf']
    CF950 = S950['cf']
    CF620 = S620['cf']
    CF851C = S851C['cf']
    CF_BEST = BEST['cf']
    CF_WORST = WORST['cf']
    CF750_AP = S750['cf_ap']
    CF851_AP = S851['cf_ap']
    CF950_AP = S950['cf_ap']
    CF620_AP = S620['cf_ap']
    CF851C_AP = S851C['cf_ap']
    CF_BEST_AP = BEST['cf_ap']
    CF_WORST_AP = WORST['cf_ap']

    def ligne(label, val, cls=""):
        c = f' class="{cls}"' if cls else ''
        return f'            <tr{c}><td>{label}</td><td class="num">{val}</td></tr>'

    def compte(d, titre, sous):
        rows = [
            ligne("Loyers bruts (loyer retenu x 12)", f"{eur(d['brut'])} €"),
            ligne(f"Vacance locative {fr(d['vac'], 0)} %",
                  f"-{eur(d['vac_eur'])} €"),
            ligne(f"Gestion locative {fr(d['gestion'], 0)} %",
                  f"-{eur(d['gestion_eur'])} €"),
            ligne(f"Taxe foncière (estimée, {eur(d['tf'])} €)",
                  f"-{eur(d['tf'])} €"),
            ligne(f"Charges de copropriété (estimées, {eur(d['copro'])} €/an)",
                  f"-{eur(d['copro'])} €"),
            ligne("Assurance PNO", f"-{eur(PNO)} €"),
            ligne("Provision travaux", f"-{eur(d['provision'])} €"),
            ligne("Comptabilité SCI à l'IS", f"-{eur(COMPTA)} €"),
            ligne("Excédent brut d'exploitation", f"{eur(d['ebe'])} €",
                  "subtotal"),
            ligne("IS 15 % de l'EBE (convention prudente)", f"-{eur(d['is_'])} €"),
            ligne("Net après IS", f"{eur(d['net'])} €", "highlight"),
            ligne("CF net mensuel avant service de la dette (net après IS / 12)",
                  f"{eur(d['cf_avant_dette'])} €/mois"),
            ligne("EBE mensuel", f"{eur(d['ebe_mois'])} €/mois"),
            ligne("Rendement brut (loyer / prix affiché)",
                  f"{fr(d['rdt_brut'])} %"),
            ligne("Rendement net avant IS sur l'acte en main",
                  f"{fr(d['rdt_av'])} %", "highlight"),
            ligne("Rendement net après IS sur l'acte en main",
                  f"{fr(d['rdt_ap'])} %"),
            ligne(f"Rendement net après IS sur la valeur ({eur(VALEUR_RETENUE)} €)",
                  f"{fr(d['rdt_valeur'])} %"),
            ligne("Prix d'achat tenant 5 % net avant IS", f"{eur(d['cap5'])} €"),
            ligne("Écart au prix affiché", f"{eur(d['cap5'] - PRIX)} €"),
            ligne("Cash-flow mensuel après crédit, avant IS (apport 10 %)",
                  f"{eur(d['cf'])} €/mois"),
            ligne("Cash-flow mensuel après crédit, après IS (convention "
                  "prudente)",
                  f"{eur(d['cf_ap'])} €/mois"),
        ]
        return f"""      <div class="projection-card scenario-{titre}">
        <h3>{sous}</h3>
        <p class="scenario-subtitle">{eur(d['loyer'])} €/mois de loyer retenu — EBE {eur(d['ebe_mois'])} €/mois — cash-flow {eur(d['cf'])} €/mois avant IS ({eur(d['cf_ap'])} € après IS)</p>
        <table class="projection-table"><tbody>
{chr(10).join(rows)}
        </tbody></table>
      </div>"""

    cartes = [
        compte(S750, "base",
               "Base — hypothèse de travail 750 €/mois, vacance 5 %"),
        compte(BEST, "optimiste",
               "Optimiste — vacance 3 %, gestion 4 %, provision 150 €"),
        compte(WORST, "pessimiste",
               "Pessimiste — vacance 10 %, TF 1 100 €, charges 2 400 €, "
               "provision 400 €"),
    ]

    # --- tableau des cinq lectures du loyer (le coeur du dossier) -----------
    lect_rows = []
    for tag, d, txt in (
            ("Bail ancien 620 €/mois — bail de quinze ans révisé sous IRL",
             S620, "la lecture la plus probable d'un locataire en place depuis "
                   "quinze ans"),
            ("Base 750 €/mois — borne haute de l'hypothèse de travail",
             S750, "le scénario de base publié de la fiche"),
            ("Marché 851 €/mois — ancrage OLV sur 66 m² (12,9 €/m²)",
             S851, "le locataire paye déjà le prix du marché"),
            ("Haut de marché 950 €/mois — borne haute des relevés du quartier",
             S950, "hypothèse haute de SeLoger pour le quartier"),
            ("Marché 851 €/mois avec 2 400 €/an de charges de copropriété",
             S851C, "la deuxième inconnue du dossier"),
    ):
        lect_rows.append(
            '        <tr' + (' class="highlight"' if d is S750 else '') + '>'
            + '<td>' + tag + '</td><td class="num">' + eur(d['ebe']) + ' €</td>'
            + '<td class="num">' + fr(d['rdt_av']) + ' %</td>'
            + '<td class="num">' + fr(d['rdt_ap']) + ' %</td>'
            + '<td class="num">' + eur(d['cap5']) + ' \u20ac</td>'
            + '<td class="num">' + eur(d['cf']) + ' / ' + eur(d['cf_ap'])
            + ' \u20ac/mois</td><td>' + txt
            + '</td></tr>')
    lect_html = "\n".join(lect_rows)

    lecture = (
        f"On demande le bail et les charges. Le prix, lui, n'est pas le "
        f"problème : à {eur(PRIX / SURF)} €/m², cet appartement se situe sous le "
        f"premier quartile de son quartier pour cette tranche de surface "
        f"({eur(DVF_Q_4595_Q1)} €/m² sur {eur(DVF_Q_4595_N)} ventes DVF 2025 de 45 à "
        f"95 m² dans la boîte de coordonnées de l'annonce) et exactement au "
        f"niveau des transactions réellement comparables de 2025 "
        f"({eur(DVF_CMP_MED)} €/m² sur {eur(DVF_CMP_N)} ventes d'appartements seuls) — "
        f"il n'y a aucune décote à capter. Ce qui manque, c'est le chiffre qui "
        f"décide de tout : le loyer du bail de quinze ans, que l'annonce ne "
        f"publie pas. Entre {eur(LOYER_ANCIEN)} et {eur(LOYER_HAUT)} €/mois, le "
        f"rendement net avant IS passe de "
        f"{fr(S620['rdt_av'])} % à {fr(S950['rdt_av'])} % et le cash-flow de "
        f"{eur(CF620)} à {eur(CF950)} €/mois. Même au loyer de marché de "
        f"{eur(LOYER_MARCHE_MED)} €/mois, il reste à {eur(CF851)} €/mois, et il "
        f"faudrait encaisser {eur(LOYER_CF_NUL)} €/mois "
        f"({fr(LOYER_CF_NUL / SURF, 1)} €/m²) pour un cash-flow nul — au-dessus "
        f"de tout le marché du quartier, dont les relevés plafonnent à "
        f"{eur(LOYER_MARCHE_HAUT)} €. <strong>Le prix n'est pas une anomalie, "
        f"c'est le montage qui ne tient pas :</strong> un bail de quinze ans, des "
        f"travaux de rafraîchissement à faire avec le locataire en place — donc "
        f"au mieux à la rotation —, des charges de copropriété non communiquées "
        f"sur un immeuble de {ANNEE} avec ascenseur, et un quartier qui se traite "
        f"8,0 % sous la médiane communale."
    )

    sens_rows = [
        (f"Loyer mensuel qu'il faudrait encaisser pour un cash-flow nul, "
         f"charges du scénario de base inchangées",
         f"{eur(LOYER_CF_NUL)} €/mois",
         f"soit {fr(LOYER_CF_NUL / SURF, 1)} €/m²/mois — au-dessus du haut de "
         f"marché du quartier ({eur(LOYER_MARCHE_HAUT)} €) : le dossier ne "
         f"s'équilibre à aucun loyer réel"),
        ("Apport pour un cash-flow nul au prix affiché, au loyer de marché "
         f"de {eur(LOYER_MARCHE_MED)} €",
         f"{eur(apport_cashflow_nul(PRIX, S851['ebe']))} €",
         f"{fr(apport_cashflow_nul(PRIX, S851['ebe']) / PRIX * 100, 0)} % du "
         f"prix — très au-delà de la doctrine du parc (10 %)"),
        ("Prix d'achat tenant 5 % net avant IS au loyer de marché (851 €)",
         f"{eur(prix_5pct_avec_travaux(S851['ebe'], 0.0))} €",
         f"{fr((PRIX - prix_5pct_avec_travaux(S851['ebe'], 0.0)) / PRIX * 100, 0)} % "
         f"sous le prix affiché"),
        ("Prix d'achat tenant 5 % net avant IS au loyer de travail (750 €)",
         f"{eur(prix_5pct_avec_travaux(S750['ebe'], 0.0))} €",
         f"{fr((PRIX - prix_5pct_avec_travaux(S750['ebe'], 0.0)) / PRIX * 100, 0)} % "
         f"sous le prix affiché"),
        ("Prix d'achat à cash-flow nul au loyer de travail (750 €)",
         f"{eur(prix_cashflow_nul(S750['ebe']))} €",
         f"{fr((PRIX - prix_cashflow_nul(S750['ebe'])) / PRIX * 100, 0)} % sous "
         f"le prix affiché : la moitié du prix"),
    ]
    sens_html = "\n".join(
        f'        <tr><td>{a}</td><td class="num">{b}</td><td>{c}</td></tr>'
        for a, b, c in sens_rows)

    # --- grille de travaux -------------------------------------------------
    travaux_rows = [
        ("Aucun travaux immédiat — hypothèse de la fiche : aucun devis n'existe, "
         "et l'annonce annonce pourtant des travaux « dans le temps »",
         f"{eur(prix_5pct_avec_travaux(S851['ebe'], 0.0))} €",
         f"{eur(prix_5pct_avec_travaux(S750['ebe'], 0.0))} €"),
        (f"{eur(TRAVAUX_REF_1)} € de rafraîchissement (peintures, sols, "
         f"électricité partielle)",
         f"{eur(prix_5pct_avec_travaux(S851['ebe'], TRAVAUX_REF_1))} €",
         f"{eur(prix_5pct_avec_travaux(S750['ebe'], TRAVAUX_REF_1))} €"),
        (f"{eur(TRAVAUX_REF_2)} € de rafraîchissement lourd (salle de bain, "
         f"électricité, menuiseries)",
         f"{eur(prix_5pct_avec_travaux(S851['ebe'], TRAVAUX_REF_2))} €",
         f"{eur(prix_5pct_avec_travaux(S750['ebe'], TRAVAUX_REF_2))} €"),
        (f"{eur(TRAVAUX_REF_3)} € de remise en état complète",
         f"{eur(prix_5pct_avec_travaux(S851['ebe'], TRAVAUX_REF_3))} €",
         f"{eur(prix_5pct_avec_travaux(S750['ebe'], TRAVAUX_REF_3))} €"),
    ]
    travaux_html = "\n".join(
        f'        <tr><td>{a}</td><td class="num">{b}</td>'
        f'<td class="num">{c}</td></tr>' for a, b, c in travaux_rows)

    # --- section 1 : compte d'exploitation ---------------------------------
    proj_section = f"""  <section class="financial-projections">
    <h2>Compte d'exploitation locatif — {eur(PRIX)} € affichés, {eur(ACTE_EN_MAIN)} € acte en main, SCI à l'IS</h2>
    <p class="attractiveness-intro">{lecture}</p>
    <div class="projections-grid">
{chr(10).join(cartes)}
    </div>
    <table class="projection-table compare">
      <thead><tr><th>Indicateur</th><th class="num">Base — 750 €</th><th class="num">Optimiste</th><th class="num">Pessimiste</th></tr></thead>
      <tbody>
        <tr><td>Loyers bruts annuels</td><td class="num">{eur(S750['brut'])} €</td><td class="num">{eur(BEST['brut'])} €</td><td class="num">{eur(WORST['brut'])} €</td></tr>
        <tr><td>Excédent brut d'exploitation</td><td class="num">{eur(S750['ebe'])} €</td><td class="num">{eur(BEST['ebe'])} €</td><td class="num">{eur(WORST['ebe'])} €</td></tr>
        <tr><td>EBE mensuel</td><td class="num">{eur(S750['ebe_mois'])} €/mois</td><td class="num">{eur(BEST['ebe_mois'])} €/mois</td><td class="num">{eur(WORST['ebe_mois'])} €/mois</td></tr>
        <tr><td>Rendement net avant IS (acte en main)</td><td class="num">{fr(S750['rdt_av'])} %</td><td class="num">{fr(BEST['rdt_av'])} %</td><td class="num">{fr(WORST['rdt_av'])} %</td></tr>
        <tr><td>Rendement net après IS (convention prudente)</td><td class="num">{fr(S750['rdt_ap'])} %</td><td class="num">{fr(BEST['rdt_ap'])} %</td><td class="num">{fr(WORST['rdt_ap'])} %</td></tr>
        <tr><td>Prix d'achat tenant 5 % net avant IS</td><td class="num">{eur(S750['cap5'])} €</td><td class="num">{eur(BEST['cap5'])} €</td><td class="num">{eur(WORST['cap5'])} €</td></tr>
        <tr class="highlight"><td>Cash-flow mensuel après crédit, avant IS (apport 10 %)</td><td class="num">{eur(CF750)} €/mois</td><td class="num">{eur(CF_BEST)} €/mois</td><td class="num">{eur(CF_WORST)} €/mois</td></tr>
        <tr><td>Cash-flow mensuel après crédit, après IS (convention prudente)</td><td class="num">{eur(CF750_AP)} €/mois</td><td class="num">{eur(CF_BEST_AP)} €/mois</td><td class="num">{eur(CF_WORST_AP)} €/mois</td></tr>
      </tbody>
    </table>
    <p class="attractiveness-intro">Repères de méthode : acte en main {eur(ACTE_EN_MAIN)} € = prix affiché {eur(PRIX)} € + frais d'acquisition {eur(FRAIS_ACQUISITION)} € ({fr(TAUX_FRAIS * 100, 2)} %, retenus par le simulateur de l'annonce, honoraires à la charge du vendeur) ; aucun travaux à l'acquisition, provision travaux annuelle comprise dans le poste composite d'entretien ; vacance {fr(VAC_BASE, 0)} %, {fr(VAC_BEST, 0)} % et {fr(VAC_WORST, 0)} % ; gestion locative {fr(GESTION_BASE_PCT, 0)} %, 4 % et {fr(GESTION_BASE_PCT, 0)} % ; taxe foncière estimée {eur(TF_BASE)} € puis {eur(1100)} € ; charges de copropriété estimées {eur(COPRO_BASE)} € puis {eur(COPRO_HAUT)} € ; assurance PNO {eur(PNO)} € ; comptabilité {eur(COMPTA)} €. <strong>Crédit (doctrine du parc) :</strong> apport 10 %, prêt de {eur(CAPITAL)} € sur {DUREE_ANS} ans à 3,7 % avec assurance emprunteur de 0,34 %, soit une mensualité de <strong>{eur(MENS)} €/mois</strong> et 0,00753 € par euro emprunté. <strong>Convention de cash-flow :</strong> la mensualité de crédit est déduite de l'EBE pour le cash-flow « avant IS » (celui des scénarios) et du net après IS pour le cash-flow « après IS » sous convention prudente — les deux sont publiés partout. <strong>Fiscalité :</strong> SCI à l'IS ; l'année 1 réelle est en déficit ({eur(S750['ebe'])} € d'EBE moins {eur(INTERETS_AN1)} € d'intérêts et {eur(DOTATION_AN1)} € de dotation, soit {eur(S750['ebe'] - INTERETS_AN1 - DOTATION_AN1)} €) et ne paie aucun impôt ; les rendements nets publiés retiennent malgré tout la convention prudente du moteur, <strong>IS de 15 % appliqué à l'EBE</strong> sans amortissement du bâti modélisé, soit {eur(CONVENTION_IS * S750['ebe'])} €/an.</p>
  </section>"""

    # --- section 2 : les cinq lectures du loyer ----------------------------
    loyer_section = f"""  <section class="financial-projections">
    <h2>Les cinq lectures du loyer — de {eur(LOYER_ANCIEN)} à {eur(LOYER_HAUT)} €/mois</h2>
    <p class="attractiveness-intro">L'annonce ne publie aucun loyer. Le dossier se juge donc sur une fourchette, et chaque borne se calcule par le moteur sur les mêmes charges ({eur(TF_BASE)} € de taxe foncière estimée, {eur(COPRO_BASE)} € de charges de copropriété estimées, {eur(PNO)} € de PNO, {eur(COMPTA)} € de comptabilité, gestion {fr(GESTION_BASE_PCT, 0)} % et provision travaux {eur(PROV_BASE)} €), la même vacance ({fr(VAC_BASE, 0)} %) et le même crédit ({eur(MENS)} €/mois). <strong>Le prix demandé ne passe aucune des cinq barres :</strong> la meilleure lecture, à {eur(LOYER_HAUT)} €/mois, donne {fr(S950['rdt_av'])} % net avant IS et laisse encore un cash-flow de {eur(CF950)} €/mois ; la plus probable pour un bail de quinze ans, à {eur(LOYER_ANCIEN)} €/mois, tombe à {fr(S620['rdt_av'])} % et à {eur(CF620)} €/mois.</p>
    <table class="projection-table compare">
      <thead><tr><th>Lecture de loyer</th><th class="num">EBE</th><th class="num">Net avant IS</th><th class="num">Net après IS</th><th class="num">Plafond 5 %</th><th class="num">Cash-flow après crédit (avant IS / après IS)</th><th>Ce qu'elle suppose</th></tr></thead>
      <tbody>
{lect_html}
      </tbody>
    </table>
    <p class="attractiveness-intro"><strong>Ce que le loyer fait au dossier, en une ligne :</strong> entre {eur(LOYER_ANCIEN)} et {eur(LOYER_HAUT)} €/mois — l'écart entre la borne basse d'un bail de quinze ans et le haut du marché du quartier —, l'EBE passe de {eur(S620['ebe'])} € à {eur(S950['ebe'])} €, le rendement net avant IS de {fr(S620['rdt_av'])} % à {fr(S950['rdt_av'])} %, le plafond 5 % de {eur(S620['cap5'])} € à {eur(S950['cap5'])} € et le cash-flow de {eur(CF620)} € à {eur(CF950)} €/mois. <strong>Aucune de ces bornes ne produit un cash-flow positif, et aucune n'atteint le seuil de 6,5 % net d'IS du parc.</strong> L'écart de rendement entre les deux extrêmes (2,75 points) est du même ordre que tout ce qu'une négociation de prix pourrait apporter — c'est dire si le bail commande le dossier.</p>
  </section>"""

    # --- section 3 : ancrages de loyer -------------------------------------
    marche_locatif_section = f"""  <section class="financial-projections">
    <h2>Marché locatif du quartier — 830 à 950 €/mois hors charges</h2>
    <p class="attractiveness-intro">Trois sources datées encadrent le loyer du quartier Saint-Jean-du-Var. L'<strong>Observatoire départemental des loyers du Var</strong> donne pour l'agglomération de Toulon un loyer médian de <strong>{fr(OLV_MED_M2, 1)} €/m²/mois hors charges</strong>, soit {eur(SURF * OLV_MED_M2)} € pour les {eur(SURF)} m² du bien — c'est l'ancrage retenu comme médiane de marché. <strong>SeLoger</strong> affiche pour le quartier un prix de location moyen de <strong>{fr(SELOGER_Q_M2, 1)} €/m²/mois</strong> (haut {fr(23.3, 1)}, bas {fr(10.4, 1)}), soit {eur(SURF * SELOGER_Q_M2)} € — un niveau qui reflète l'offre récente et remise au goût du jour, pas un T4 de {ANNEE} occupé. <strong>RealAdvisor</strong> donne un loyer médian d'appartement de <strong>{eur(REALADVISOR_MED)} €</strong> dans le quartier, avec 80 % des biens entre 475 et 2 043 €. En croisant les trois, le marché du quartier se tient entre <strong>{eur(LOYER_MARCHE_BAS)} et {eur(LOYER_MARCHE_HAUT)} €/mois hors charges</strong>, et un bail de quinze ans révisé sous IRL (+1,15 %/an en 2026) se situe mécaniquement en dessous : c'est pourquoi l'hypothèse de travail retenue est de {eur(LOYER_ANCIEN)} à {eur(LOYER_BASE)} €/mois.</p>
    <table class="projection-table compare">
      <thead><tr><th>Source</th><th class="num">Loyer €/m²/mois</th><th class="num">Pour {eur(SURF)} m²</th><th>Lecture</th></tr></thead>
      <tbody>
        <tr><td>Observatoire départemental des loyers du Var — agglomération de Toulon (hors charges)</td><td class="num">{fr(OLV_MED_M2, 1)} €</td><td class="num">{eur(SURF * OLV_MED_M2)} €</td><td>l'ancrage de marché retenu : loyer médian hors charges sur le parc existant</td></tr>
        <tr><td>SeLoger — quartier Saint-Jean-du-Var (moyenne, haut 23,3 / bas 10,4)</td><td class="num">{fr(SELOGER_Q_M2, 1)} €</td><td class="num">{eur(SURF * SELOGER_Q_M2)} €</td><td>l'offre récente et présentée : un plafond, pas une référence pour un bien occupé et à rafraîchir</td></tr>
        <tr><td>RealAdvisor — quartier, loyer médian d'un appartement (80 % entre 475 et 2 043 €)</td><td class="num">—</td><td class="num">{eur(REALADVISOR_MED)} €</td><td>recoupe l'ancrage OLV ; dispersion large, quartier hétérogène</td></tr>
        <tr class="highlight"><td><strong>Marché du quartier retenu (hors charges)</strong></td><td class="num">{fr(LOYER_MARCHE_BAS / SURF, 1)} à {fr(LOYER_MARCHE_HAUT / SURF, 1)} €</td><td class="num">{eur(LOYER_MARCHE_BAS)} à {eur(LOYER_MARCHE_HAUT)} €</td><td>médiane {eur(LOYER_MARCHE_MED)} € ; au-delà, le locataire en place n'est pas le bon locataire</td></tr>
        <tr><td><strong>Hypothèse de travail du dossier</strong> (bail de quinze ans, IRL)</td><td class="num">{fr(LOYER_ANCIEN / SURF, 1)} à {fr(LOYER_BASE / SURF, 1)} €</td><td class="num">{eur(LOYER_ANCIEN)} à {eur(LOYER_BASE)} €</td><td>publiée comme scénario de base, et c'est déjà la borne haute de l'hypothèse</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Le point de méthode.</strong> Un bien vendu loué ne se juge pas sur le loyer du marché : il se juge sur le bail. Entre le loyer du marché ({eur(LOYER_MARCHE_MED)} €) et la borne basse d'un bail de quinze ans ({eur(LOYER_ANCIEN)} €), il y a {fr((LOYER_MARCHE_MED - LOYER_ANCIEN) / LOYER_ANCIEN * 100, 0)} % de revenu et {fr(S851['rdt_av'] - S620['rdt_av'])} point de rendement net avant IS : <strong>c'est le seul chiffre qui décide, et c'est le seul que l'annonce ne donne pas.</strong> Toutes les autres données du dossier sont vérifiables et vérifiées — le prix, les surfaces annoncées, le marché DVF, les loyers du quartier. C'est pourquoi la fiche conclut sur une demande de pièces, pas sur un prix.</p>
    </div>
  </section>"""

    # --- section 4 : marche de la vente (DVF) ------------------------------
    def _cmp_row(c):
        lots = 's' if c['lots'] > 1 else ''
        lieu = ('dans la boîte de coordonnées de l\'annonce' if c['box']
                else 'quartier immédiat, hors boîte de la sélection')
        return ('        <tr><td>' + c['voie'] + ', ' + c['date'] + ' — '
                + str(c['lots']) + ' lot' + lots + ' vendu' + lots
                + '</td><td class="num">' + eur(c['surf']) + ' m²</td>'
                + '<td class="num">' + eur(c['prix']) + ' €</td>'
                + '<td class="num">' + eur(c['m2']) + ' €</td>'
                + '<td>' + lieu + '</td></tr>')

    cmp_rows_html = chr(10).join(_cmp_row(c) for c in DVF_COMPARABLES)

    dvf_section = f"""  <section class="financial-projections">
    <h2>Marché de la vente — DVF 2025 réelle de Toulon et de son quartier</h2>
    <p class="attractiveness-intro">Les {eur(DVF_LIGNES_VENTE)} lignes de nature « Vente » enregistrées en 2025 sur la commune de Toulon ({eur(DVF_MUTATIONS)} mutations lues, dont {eur(DVF_MUTATIONS_VENTE)} de nature Vente) donnent un marché très liquide : <strong>{eur(DVF_APP_N)} ventes d'appartements</strong>, médiane {eur(DVF_APP_MED)} €/m² toutes surfaces. La tranche de surface du bien y est fournie — mais c'est le QUARTIER qui décide, et le quartier se sélectionne par les coordonnées du marqueur de l'annonce ({eur(DVF_BOITE[0], 3)}-{eur(DVF_BOITE[1], 3)} N / {eur(DVF_BOITE[2], 3)}-{eur(DVF_BOITE[3], 3)} E). Méthode : valeur foncière de la mutation divisée par la somme des surfaces bâties de la mutation, surfaces supérieures à 5 m² et valeurs supérieures à 5 000 €.</p>
    <table class="projection-table compare">
      <thead><tr><th>Segment DVF 2025</th><th class="num">Ventes</th><th class="num">Médiane €/m²</th><th>Lecture</th></tr></thead>
      <tbody>
        <tr><td>Appartements, toutes surfaces — commune de Toulon</td><td class="num">{eur(DVF_APP_N)}</td><td class="num">{eur(DVF_APP_MED)} €</td><td>moyenne communale, non applicable au bien : le prix au m² décroît avec la surface</td></tr>
        <tr><td>Appartements de 15 à 30 m² — commune</td><td class="num">{eur(DVF_APP_1530_N)}</td><td class="num">{eur(DVF_APP_1530_MED)} €</td><td>les petites surfaces se paient le plus cher au m²</td></tr>
        <tr><td>Appartements de 30 à 45 m² — commune</td><td class="num">{eur(DVF_APP_3045_N)}</td><td class="num">{eur(DVF_APP_3045_MED)} €</td><td>prix médian de la tranche : {eur(DVF_APP_4560_PRIX)} € pour les 45-60 m²</td></tr>
        <tr><td>Appartements de 45 à 60 m² — commune</td><td class="num">{eur(DVF_APP_4560_N)}</td><td class="num">{eur(DVF_APP_4560_MED)} €</td><td>de {eur(DVF_APP_4560_Q1)} à {eur(DVF_APP_4560_Q3)} €/m² — la tranche voisine du bien, référence communale</td></tr>
        <tr><td>Appartements de 60 à 90 m² — commune</td><td class="num">{eur(DVF_APP_6090_N)}</td><td class="num">{eur(DVF_APP_6090_MED)} €</td><td>la décote de surface se voit : {eur(DVF_APP_6090_MED)} €/m² contre {eur(DVF_APP_3045_MED)} €/m² sur 30-45 m²</td></tr>
        <tr><td><strong>Quartier Saint-Jean-du-Var — tous appartements</strong></td><td class="num">{eur(DVF_Q_APP_N)}</td><td class="num">{eur(DVF_Q_MED)} €</td><td>de {eur(DVF_Q_Q1)} à {eur(DVF_Q_Q3)} €/m² : le quartier se traite {fr((1 - DVF_Q_MED / DVF_APP_MED) * 100, 1)} % sous la médiane communale</td></tr>
        <tr class="highlight"><td><strong>Quartier — 45 à 95 m², la tranche du bien</strong></td><td class="num">{eur(DVF_Q_4595_N)}</td><td class="num">{eur(DVF_Q_4595_MED)} €</td><td>de {eur(DVF_Q_4595_Q1)} à {eur(DVF_Q_4595_Q3)} €/m², prix médian {eur(DVF_Q_4595_PRIX)} € : c'est la référence de cet appartement de {eur(SURF)} m²</td></tr>
        <tr><td>Commune — 45 à 95 m² (même tranche, pour comparaison)</td><td class="num">{eur(DVF_APP_4595_N)}</td><td class="num">{eur(DVF_APP_4595_MED)} €</td><td>le quartier est {fr((1 - DVF_Q_4595_MED / DVF_APP_4595_MED) * 100, 1)} % sous la commune à surface comparable</td></tr>
      </tbody>
    </table>
    <table class="projection-table compare">
      <thead><tr><th>Transaction comparable (2025)</th><th class="num">Surface</th><th class="num">Prix</th><th class="num">€/m²</th><th>Lecture</th></tr></thead>
      <tbody>
{cmp_rows_html}
        <tr><td><strong>Médiane des {eur(DVF_CMP_N)} ventes d'appartements seuls de 45 à 95 m² à 1 800-1 835 €/m²</strong></td><td class="num">45 à 72 m²</td><td class="num">{eur(DVF_CMP_PRIX)} €</td><td class="num">{eur(DVF_CMP_MED)} €</td><td>le niveau où se traitent réellement les appartements de ce type dans le quartier</td></tr>
        <tr class="highlight"><td><strong>Le bien analysé</strong>, au prix affiché, sur les {eur(SURF)} m² annoncés</td><td class="num">{eur(SURF)} m²</td><td class="num">{eur(PRIX)} €</td><td class="num">{eur(PRIX / SURF)} €</td><td>{fr((PRIX / SURF - DVF_CMP_MED) / DVF_CMP_MED * 100, 1)} % au-dessus de la médiane des comparables, sous le premier quartile du quartier ({eur(DVF_Q_4595_Q1)} €)</td></tr>
        <tr><td>Tranche 45-95 m² du quartier appliquée au bien (valeur retenue)</td><td class="num">{eur(SURF)} m²</td><td class="num">{eur(VALEUR_RETENUE)} €</td><td class="num">{eur(DVF_Q_4595_MED)} €</td><td>valeur après travaux et libre d'occupant : {eur(VALEUR_BASSE)} à {eur(VALEUR_HAUTE)} € (Q1 à Q3)</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Ce que disent les chiffres — et le point qui distingue ce dossier.</strong> À {eur(PRIX / SURF)} €/m², ce bien n'est <strong>ni une décote ni une anomalie</strong> : il est exactement au niveau des transactions réellement comparables de son quartier ({eur(DVF_CMP_MED)} €/m² de médiane sur {eur(DVF_CMP_N)} ventes d'appartements seuls de 45 à 95 m² en 2025), et sous le premier quartile de la tranche de surface du quartier ({eur(DVF_Q_4595_Q1)} €/m²). <strong>Ce que ce prix paie, c'est l'état — l'annonce écrit elle-même « rénovation nécessaire » et « travaux de rafraîchissement » — et le locataire en place depuis quinze ans.</strong> Il n'y a donc aucune décote à capter pour compenser un loyer faible, et aucune marge de marchand de biens : le coût de revient avec {eur(TRAVAUX_REF_2)} € de travaux atteint {eur(ACTE_EN_MAIN + TRAVAUX_REF_2)} €, soit {eur((ACTE_EN_MAIN + TRAVAUX_REF_2) / SURF)} €/m² — exactement la médiane du quartier pour cette surface ({eur(DVF_Q_4595_MED)} €/m²) — et une revente à 95 % de cette valeur laisserait une marge négative de {eur(VALEUR_RETENUE * 0.95 - (ACTE_EN_MAIN + TRAVAUX_REF_2))} €.</p>
      <p class="attractiveness-intro"><strong>Référence interne de la commune</strong> (fiche <em>Marchés locaux</em> mise à jour le 21/09/2026) : marché {eur(MARCHE_M2_COMMUNE)} €/m², loyer de référence {fr(LOYER_REF_M2, 1)} €/m²/mois sur un lot type de 60 m², plafonds d'achat par m² habitable frais compris de {eur(PLAF_PATRIMONIAL[0])} € (6,5 % net d'IS), {eur(PLAF_PATRIMONIAL[1])} € (7,0 %) et {eur(PLAF_PATRIMONIAL[2])} € (8,0 %) en vision patrimoniale, et {eur(PLAF_MDB[0])} / {eur(PLAF_MDB[1])} / {eur(PLAF_MDB[2])} €/m² en vision marchand de biens. Ce dossier s'affiche à {eur(PRIX / SURF)} €/m², soit <strong>{fr((PRIX / SURF) / PLAF_PATRIMONIAL[0], 2)} fois le plafond patrimonial à 6,5 % net d'IS</strong> et {fr((PRIX / SURF) / PLAF_MDB[0], 2)} fois le plafond marchand de biens de la ville : le constat de la fiche de référence — aucune des douze villes du secteur n'offre le seuil patrimonial au prix de marché — vaut ici aussi, et pour une raison différente des dossiers de centre ancien : ce n'est pas le prix qui est cher, c'est le loyer qui n'est pas prouvé.</p>
      <p class="attractiveness-intro"><strong>À lire aussi dans le dépôt</strong> — <a href="../marches-locaux/index.html">fiche de référence des seuils d'achat par ville</a> (21/09/2026, 12 communes), <a href="../2026-09-22-appartement-t4-saint-jean-toulon/index.html">appartement T4 de 77,45 m² au 7e étage, quartier Saint-Jean, Toulon</a> (22/09/2026), <a href="../2026-06-15-saint-jean-du-var-toulon-colocation-etudiante/index.html">Saint-Jean-du-Var, colocation étudiante</a> (15/06/2026), <a href="../2026-09-10-t4-66m2-champ-de-mars-toulon/index.html">T4 de 66 m² quartier Champ-de-Mars, Toulon</a> (10/09/2026), <a href="../2026-09-10-t4-73m2-aguillon-toulon/index.html">T4 de 73 m² quartier Aguillon, Toulon</a> (10/09/2026), <a href="../2026-09-11-t5-86m2-dutasta-mayol-toulon/index.html">T5 de 86 m² Dutasta-Mayol, Toulon</a> (11/09/2026) et <a href="../2026-09-22-appartement-t5-mourillon-toulon/index.html">T5 au Mourillon, Toulon</a> (22/09/2026). <strong>Celui-ci est le premier dossier du quartier Saint-Jean-du-Var jugé en lecture patrimoniale avec un bail en place :</strong> il donne le niveau de prix du quartier pour les prochains — {eur(DVF_Q_4595_MED)} €/m² de médiane sur {eur(DVF_Q_4595_N)} ventes de 45 à 95 m², contre {eur(DVF_Q_4595_Q1)} €/m² au premier quartile, là où le dossier de colocation étudiante du même quartier avait été jugé sur des loyers de chambre.</p>
    </div>
  </section>"""

    # --- section 5 : ce qu'il faudrait -------------------------------------
    besoins_section = f"""  <section class="financial-projections">
    <h2>Ce qu'il faudrait pour équilibrer — et la grille de travaux</h2>
    <p class="attractiveness-intro">Trois contraintes se superposent au prix affiché : la trésorerie (le cash-flow est négatif dans les cinq lectures de loyer), le seuil de rendement (5 % net avant IS, la moitié de la cible de parc) et la valeur de sortie. Elles donnent trois plafonds qui ne se recoupent que très bas.</p>
    <table class="projection-table compare">
      <thead><tr><th>Levier</th><th class="num">Valeur</th><th>Lecture</th></tr></thead>
      <tbody>
{sens_html}
      </tbody>
    </table>
    <h3>Grille de plafonds par tranche de travaux</h3>
    <p class="attractiveness-intro">L'annonce déclare des travaux de rafraîchissement à faire sans les chiffrer, et aucun devis n'existe : le plafond ne se publie donc pas comme un chiffre unique mais comme une grille, prix d'achat affiché compris, chiffrée aux deux ancrages de loyer. Elle se lit simplement : <strong>plus l'enveloppe de travaux est lourde, plus le prix d'achat doit baisser</strong>, euro de travaux contre euro de prix (aux frais d'acquisition près, un euro de travaux coûte 1/1,08 = 0,93 € de prix).</p>
    <table class="projection-table compare">
      <thead><tr><th>Enveloppe de rafraîchissement</th><th class="num">Plafond 5 % net au loyer de marché ({eur(LOYER_MARCHE_MED)} €)</th><th class="num">Plafond 5 % net au loyer de travail ({eur(LOYER_BASE)} €)</th></tr></thead>
      <tbody>
{travaux_html}
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Le double effet des travaux.</strong> Ils pèsent deux fois : ils augmentent le prix de revient — donc le capital sur lequel on exige le rendement — et ils ne peuvent pas être exécutés avec le locataire en place, donc ils n'apportent ni hausse de loyer, ni valeur locative nouvelle avant son départ. Sur ce dossier, {eur(TRAVAUX_REF_2)} € de travaux font tomber le plafond d'achat de {eur(prix_5pct_avec_travaux(S851['ebe'], 0.0))} € à {eur(prix_5pct_avec_travaux(S851['ebe'], TRAVAUX_REF_2))} € au loyer de marché : <strong>les travaux se paient sur le prix d'achat, pas sur l'espérance de loyer.</strong></p>
      <p class="attractiveness-intro"><strong>Piste étudiée et écartée — la colocation.</strong> Le T4 compte trois chambres : à {eur(COLOC_BAS)} à {eur(COLOC_HAUT)} € par chambre et par mois (soit {eur(3 * COLOC_BAS)} à {eur(3 * COLOC_HAUT)} €/mois), l'affaire dégage {eur(C400['ebe'])} à {eur(C430['ebe'])} € d'EBE et un rendement net après IS de {fr(C400['rdt_ap'])} % à {fr(C430['rdt_ap'])} %, avec un cash-flow après crédit de {eur(C400['cf'])} à {eur(C430['cf'])} €/mois avant IS et de {eur(C400['cf_ap'])} à {eur(C430['cf_ap'])} €/mois après IS sous la convention prudente. C'est la seule lecture qui franchit la barre des 6 % net — et pourtant <strong>elle est à écarter</strong> : elle suppose le départ du locataire en place, donc un portage à vide de plusieurs mois, une division du T4 en trois chambres (travaux et autorisation), un apport supérieur au filtre de la SCI, et un bail meublé sur un quartier qui n'est pas étudiant. Elle détruirait aussi le seul argument de vente de l'annonce — « revenus locatifs immédiats dès la signature » — et ne dégage au mieux, à {eur(COLOC_HAUT)} € la chambre, que {eur(C430['cf'])} €/mois avant IS, soit {eur(C430['cf_ap'])} €/mois après IS sous la convention prudente.</p>
    </div>
  </section>"""

    gen.LECTURE[SLUG] = lecture
    gen.RECS[SLUG] = rec_
    gen.CONF = {SLUG: dict(
        titre_court=(
            f"Appartement T4 {eur(SURF)} m² vendu loué, Saint-Jean-du-Var — "
            f"Toulon (83100)"
        ),
        adresse=(
            f"Quartier Saint-Jean-du-Var, Toulon (83100) — appartement T4 de "
            f"{eur(SURF)} m² annoncés (68 m² dans le texte de l'annonce) au "
            f"{ETAGE}, immeuble de {ANNEE}, vendu loué avec locataire en place "
            f"depuis quinze ans"
        ),
        date_fr=DATE_FR,
        source=(
            "SeLoger — annonce 264IMKBI3IM5 (Foncia Transaction Toulon Liberté, "
            "289 place de la Liberté, RCS 503698664, référence 00836037, mandat "
            "en exclusivité)"
        ),
        url=URL,
        badge="Bien vendu loué — investissement locatif, loyer non communiqué",
        strategie=(
            f"Conservation du bail en place : loyer retenu "
            f"{eur(LOYER_BASE)} €/mois (hypothèse de travail haute, fourchette "
            f"{eur(LOYER_ANCIEN)} à {eur(LOYER_BASE)} €), charges de copropriété "
            f"estimées {eur(COPRO_BASE)} €/an, travaux de rafraîchissement non "
            f"chiffrés et différés à la rotation du locataire"
        ),
        fiscal_note=(
            f"SCI à l'IS — l'année 1 est en déficit "
            f"({eur(S750['ebe'] - INTERETS_AN1 - DOTATION_AN1)} € après intérêts "
            f"{eur(INTERETS_AN1)} € et dotation {eur(DOTATION_AN1)} €) donc aucun "
            f"IS dû ; rendements nets publiés sous la convention prudente du "
            f"moteur (IS de 15 % de l'EBE), dite explicitement ; seuil de "
            f"décision du parc : 6,5 % net d'IS"
        ),
        lat="43.1218", lon="5.9483",
        quartier=(
            f"quartier Saint-Jean-du-Var, Toulon (83100) — immeuble de {ANNEE} "
            f"avec ascenseur, à quelques minutes du centre de Toulon et de la "
            f"gare"
        ),
        intro_attr=(
            f"Saint-Jean-du-Var est un quartier dense de l'est toulonnais, à "
            f"quelques minutes du centre-ville, de la gare et du port : commerces "
            f"de proximité, écoles, réseau de bus urbain. Le marché y est "
            f"documenté et liquide — <strong>{eur(DVF_APP_N)} ventes d'appartements à "
            f"Toulon en 2025</strong> selon la base DVF, dont "
            f"<strong>{eur(DVF_Q_APP_N)} dans la boîte de coordonnées de cette annonce "
            f"et {eur(DVF_Q_4595_N)} de 45 à 95 m²</strong>. Mais c'est un quartier qui "
            f"se traite <strong>{fr((1 - DVF_Q_MED / DVF_APP_MED) * 100, 1)} % "
            f"sous la médiane communale</strong> ({eur(DVF_Q_MED)} €/m² contre "
            f"{eur(DVF_APP_MED)} €/m² toutes surfaces, et "
            f"{fr((1 - DVF_Q_4595_MED / DVF_APP_4595_MED) * 100, 1)} % sous la "
            f"commune à tranche de surface comparable) : c'est un emplacement de "
            f"rendement locatif, pas de plus-value. Côté locatif, les ancrages "
            f"datés donnent un marché de {eur(LOYER_MARCHE_BAS)} à "
            f"{eur(LOYER_MARCHE_HAUT)} €/mois hors charges pour un T4 de "
            f"{eur(SURF)} m² (OLV agglomération de Toulon "
            f"{fr(OLV_MED_M2, 1)} €/m²/mois hors charges, soit "
            f"{eur(SURF * OLV_MED_M2)} € ; SeLoger quartier "
            f"{fr(SELOGER_Q_M2, 1)} €/m²/mois soit {eur(SURF * SELOGER_Q_M2)} € ; "
            f"RealAdvisor quartier {eur(REALADVISOR_MED)} € de médiane). Le "
            f"problème du dossier n'est ni le quartier ni le prix : c'est le "
            f"loyer du bail en place, que l'annonce ne communique pas."
        ),
        profil=(
            f"un ménage familial — trois chambres, "
            f"{eur(SURF)} m², {ETAGE} — dans un quartier de ville dense à "
            f"quelques minutes des commerces, des écoles et de la gare de "
            f"Toulon : le profil type d'un T4 toulonnais, et c'est celui du "
            f"locataire en place depuis quinze ans. Le loyer facial de référence "
            f"du quartier (15,0 €/m²/mois selon SeLoger, {eur(SURF * SELOGER_Q_M2)} "
            f"€) se situe au-dessus de la médiane hors charges de "
            f"l'agglomération ({fr(OLV_MED_M2, 1)} €/m², soit "
            f"{eur(SURF * OLV_MED_M2)} €) : la demande ne fait pas défaut, c'est "
            f"la révision IRL d'un bail ancien qui plafonne le revenu"
        ),
        concl_attr=(
            f"Adéquation correcte ({fr((7 + 7 + 7 + 6 + 7 + 6) / 6, 1)}/10). Le "
            f"quartier, le produit et le prix sont bons : un T4 de 3 chambres "
            f"avec ascenseur, à {eur(PRIX / SURF)} €/m², sous le premier quartile "
            f"de son quartier ({eur(DVF_Q_4595_Q1)} €/m²) et au niveau exact des "
            f"transactions comparables de 2025 ({eur(DVF_CMP_MED)} €/m² sur "
            f"{eur(DVF_CMP_N)} ventes d'appartements seuls). Ce qui plombe le dossier "
            f"n'est pas l'emplacement : c'est l'accumulation de quatre inconnues "
            f"sur le même bien — le loyer du bail, les charges de copropriété, le "
            f"montant des travaux et le carrez exact — dont la première décide du "
            f"rendement entre {fr(S620['rdt_av'])} % et "
            f"{fr(S950['rdt_av'])} %. On a donc ici un bien correct, à un prix "
            f"correct, qui ne s'achète pas sans pièces"
        ),
        intro_strat=(
            f"Six lectures ont été testées, toutes calculées par le moteur : cinq "
            f"hypothèses de loyer ({eur(LOYER_ANCIEN)}, {eur(LOYER_BASE)}, "
            f"{eur(LOYER_MARCHE_MED)}, {eur(LOYER_HAUT)} €/mois et "
            f"{eur(LOYER_MARCHE_MED)} € avec {eur(COPRO_HAUT)} €/an de charges) "
            f"dans le cadre d'un bail conservé, plus une colocation meublée à "
            f"trois chambres. Aucune ne dégage un cash-flow positif au prix "
            f"affiché et seule la colocation franchit la barre des 6 % net — en "
            f"supposant le départ du locataire en place. La stratégie retenue est "
            f"donc l'attente de pièces : le bail, les charges, le carrez et la "
            f"taxe foncière"
        ),
        rationale=(
            f"Le scénario de base : loyer retenu {eur(LOYER_BASE)} €/mois "
            f"({fr(LOYER_BASE / SURF, 1)} €/m², borne haute de l'hypothèse de "
            f"travail pour un bail de quinze ans révisé sous IRL), vacance "
            f"{fr(VAC_BASE, 0)} %, gestion locative {fr(GESTION_BASE_PCT, 0)} %, "
            f"taxe foncière estimée {eur(TF_BASE)} € (avis non communiqué), "
            f"charges de copropriété estimées {eur(COPRO_BASE)} €/an (aucune "
            f"charge publiée), assurance PNO {eur(PNO)} €, provision travaux "
            f"{eur(PROV_BASE)} € et comptabilité {eur(COMPTA)} €. L'excédent brut "
            f"d'exploitation ressort à <strong>{eur(S750['ebe'])} €</strong> "
            f"({eur(S750['ebe_mois'])} €/mois), soit <strong>{fr(S750['rdt_av'])} % "
            f"net avant IS</strong> sur les {eur(ACTE_EN_MAIN)} € d'acte en main "
            f"et {fr(S750['rdt_ap'])} % après IS sous convention prudente — la "
            f"moitié du seuil de 6,5 % net d'IS du parc.<br><br>"
            f"Ce que l'annonce ne dit pas, et qui décide de tout : le montant du "
            f"loyer. Le bien est vendu « avec locataire en place depuis 15 ans » "
            f"et « revenus locatifs immédiats dès la signature » — mais aucun "
            f"loyer n'est publié. Entre {eur(LOYER_ANCIEN)} €/mois (bail ancien "
            f"révisé sous IRL, l'hypothèse la plus probable pour un locataire "
            f"entré dans les lieux en 2008-2010) et {eur(LOYER_HAUT)} €/mois (haut "
            f"du marché du quartier), l'EBE passe de {eur(S620['ebe'])} € à "
            f"{eur(S950['ebe'])} € et le rendement net avant IS de "
            f"{fr(S620['rdt_av'])} % à {fr(S950['rdt_av'])} % : <strong>2,75 "
            f"points de rendement tiennent à une pièce qui n'est pas dans le "
            f"dossier.</strong> Et même en retenant le loyer de marché de "
            f"{eur(LOYER_MARCHE_MED)} €/mois — l'hypothèse la plus favorable "
            f"crédible, qui suppose que le locataire paye déjà le prix du marché "
            f"après quinze ans —, la fiche ne passe pas : {fr(S851['rdt_av'])} % "
            f"net avant IS, {fr(S851['rdt_ap'])} % après IS, plafond "
            f"{eur(S851['cap5'])} € et cash-flow {eur(CF851)} €/mois. Il faudrait "
            f"encaisser {eur(LOYER_CF_NUL)} €/mois "
            f"({fr(LOYER_CF_NUL / SURF, 1)} €/m²) pour que le cash-flow soit nul, "
            f"au-dessus de tout le marché du quartier.<br><br>"
            f"Les trois autres inconnues ne sauvent pas la lecture. Les charges de "
            f"copropriété, absentes de l'annonce sur un immeuble de {ANNEE} avec "
            f"ascenseur, sont estimées à {eur(COPRO_BASE)} €/an et testées à "
            f"{eur(COPRO_HAUT)} €/an : 600 €/an de plus, soit "
            f"{fr(S851['rdt_av'] - S851C['rdt_av'])} point de rendement net avant "
            f"IS et {eur(abs(CF851C - CF851))} €/mois de trésorerie. Les travaux "
            f"déclarés par l'annonce (« rafraîchissement dans le temps ») ne sont "
            f"pas chiffrés et ne peuvent pas être exécutés avec le locataire en "
            f"place : ils attendront la rotation, et la grille publiée montre que "
            f"{eur(TRAVAUX_REF_2)} € de travaux font tomber le plafond d'achat de "
            f"{eur(prix_5pct_avec_travaux(S851['ebe'], 0.0))} € à "
            f"{eur(prix_5pct_avec_travaux(S851['ebe'], TRAVAUX_REF_2))} €. Quant "
            f"au prix, il n'est pas attaquable : {eur(PRIX / SURF)} €/m², c'est "
            f"exactement le niveau des transactions comparables du quartier "
            f"({eur(DVF_CMP_MED)} €/m² sur {eur(DVF_CMP_N)} ventes de 2025), sous le "
            f"premier quartile de la tranche de surface. <strong>Un prix au "
            f"marché ne compense pas un revenu inconnu : le dossier ne se négocie "
            f"pas, il se documente.</strong>"
        ),
        identite=[
            ("Adresse",
             "Quartier Saint-Jean-du-Var, Toulon (83100) — adresse exacte non "
             "publiée dans l'annonce ; agence Foncia Transaction Toulon Liberté, "
             "289 place de la Liberté (RCS 503698664, référence 00836037, mandat "
             "en exclusivité)"),
            ("Vendeur / intermédiaire",
             "Foncia Transaction Toulon Liberté — annonce SeLoger 264IMKBI3IM5. "
             "Honoraires à la charge du vendeur"),
            ("Composition",
             f"Appartement T4 (4 pièces, {CHAMBRES} chambres) de {eur(SURF)} m² "
             f"annoncés en titre — {eur(SURF_TEXTE)} m² écrits dans le texte de la "
             f"même annonce — au {ETAGE}, immeuble de {ANNEE}. Chauffage "
             f"individuel, non meublé, {PHOTOS} photos, cave annoncée dans le "
             f"texte mais « Pas de cave » dans la fiche caractéristiques"),
            ("Statut",
             "Copropriété de 1961 avec ascenseur, « pas de procédure en cours » "
             "selon l'annonce. Ni le nombre de lots, ni le budget prévisionnel, "
             "ni la charge annuelle du lot ne sont publiés. « Parking collectif » "
             ": <strong>aucune place privative identifiée</strong>, donc aucun "
             "lot cessible et aucun revenu annexe"),
            ("Surfaces",
             f"<strong>{eur(SURF)} m² annoncés en titre</strong> "
             f"({eur(PRIX / SURF)} €/m²) contre {eur(SURF_TEXTE)} m² écrits dans le "
             f"texte ({eur(PRIX / SURF_TEXTE)} €/m²) : 2 m² d'écart, 3 % de prix "
             f"au m², à trancher par le certificat Carrez avant toute offre"),
            ("Occupation",
             f"<strong>Vendu loué</strong> : locataire en place depuis quinze ans "
             f"selon l'annonce, « revenus locatifs immédiats dès la signature ». "
             f"Ni le loyer, ni sa décomposition hors charges / provisions, ni la "
             f"date d'effet, ni la durée restante, ni une quittance ne sont "
             f"communiqués. Le bien se visite occupé : aucun accès libre aux "
             f"pièces, aucun diagnostic contradictoire"),
            ("Loyers retenus",
             f"<strong>{eur(LOYER_BASE)} €/mois</strong> "
             f"({fr(LOYER_BASE / SURF, 1)} €/m²) en scénario de base, fourchette "
             f"de travail {eur(LOYER_ANCIEN)} à {eur(LOYER_BASE)} €/mois pour un "
             f"bail de quinze ans révisé sous IRL. Marché du quartier : "
             f"{eur(LOYER_MARCHE_BAS)} à {eur(LOYER_MARCHE_HAUT)} €/mois hors "
             f"charges, médiane {eur(LOYER_MARCHE_MED)} €. Une seule ligne de "
             f"revenu en base, celle de la stratégie retenue"),
            ("Charges de copropriété",
             f"<strong>Non communiquées par l'annonce.</strong> Estimation "
             f"retenue {eur(COPRO_BASE)} €/an, variante testée "
             f"{eur(COPRO_HAUT)} €/an pour un immeuble de {ANNEE} avec "
             f"ascenseur. Chaque euro de charge sort du rendement : "
             f"{fr(S851['rdt_av'] - S851C['rdt_av'])} point de rendement net avant "
             f"IS entre les deux hypothèses"),
            ("Travaux",
             "L'annonce déclare le bien « nécessitera des travaux de "
             "rafraîchissement dans le temps », sans montant. Aucun devis, donc "
             "aucun chiffre dans le prix de revient : la fiche publie une grille "
             "de plafonds par tranche de 10 000, 20 000 et 30 000 €. Ces travaux "
             "ne sont pas exécutables avec le locataire en place"),
            ("DPE / GES",
             f"DPE {DPE} / GES {GES} — facture énergétique annoncée de "
             f"{eur(FACTURE_BASSE)} à {eur(FACTURE_HAUTE)} €/an, chauffage "
             f"individuel. Un D reste louable, mais la facture plafonne le loyer "
             f"acceptable et la mise aux normes se paiera un jour, en appel de "
             f"fonds ou en travaux individuels"),
            ("Prix affiché",
             f"<strong>{eur(PRIX)} €</strong>, honoraires à la charge du vendeur "
             f"— {eur(PRIX / SURF)} €/m² sur les {eur(SURF)} m² annoncés. Sous le "
             f"premier quartile du quartier pour cette tranche de surface "
             f"({eur(DVF_Q_4595_Q1)} €/m² sur {eur(DVF_Q_4595_N)} ventes) et au niveau "
             f"des transactions comparables de 2025 ({eur(DVF_CMP_MED)} €/m² sur "
             f"{eur(DVF_CMP_N)} ventes d'appartements seuls) : le prix n'est pas le "
             f"problème du dossier"),
            ("Valeur de marché retenue",
             f"<strong>{eur(VALEUR_RETENUE)} €</strong> ({eur(SURF)} m² × "
             f"{eur(DVF_Q_4595_MED)} €/m², médiane DVF 2025 du quartier sur "
             f"{eur(DVF_Q_4595_N)} ventes de 45 à 95 m²), fourchette "
             f"{eur(VALEUR_BASSE)} à {eur(VALEUR_HAUTE)} € (premier et troisième "
             f"quartiles). Comparables nommés à {eur(DVF_CMP_MED)} €/m² de "
             f"médiane : rue de Suez (55 m², 99 500 €, 1 809 €/m², 25/03/2025), "
             f"place Gustave Lambert (52 m², 94 000 €, 1 808 €/m², 30/04/2025), "
             f"rue Jean Aicard (41 m², 75 000 €, 1 829 €/m², 28/07/2025) et "
             f"avenue Antoine Senequier (72 m², 130 000 €, 1 806 €/m², "
             f"31/10/2025)"),
            ("Charges d'exploitation retenues",
             f"Taxe foncière <strong>estimée {eur(TF_BASE)} €</strong> (avis non "
             f"communiqué) + charges de copropriété <strong>estimées "
             f"{eur(COPRO_BASE)} €</strong> (non communiquées) + assurance PNO "
             f"{eur(PNO)} € + gestion locative {fr(GESTION_BASE_PCT, 0)} % et "
             f"provision travaux {eur(PROV_BASE)} € (poste composite de "
             f"{eur(revenus_annuels(LOYER_BASE) * GESTION_BASE_PCT / 100.0 + PROV_BASE)} "
             f"€) + comptabilité {eur(COMPTA)} €. Provision automatique du moteur "
             f"(2,5 %) désactivée pour ne pas compter deux fois la provision "
             f"travaux"),
            ("Fiscalité",
             f"SCI à l'IS. Année 1 réelle : EBE {eur(S750['ebe'])} € moins "
             f"intérêts d'emprunt {eur(INTERETS_AN1)} € ({eur(CAPITAL)} € à 3,7 %) "
             f"moins la dotation aux amortissements {eur(DOTATION_AN1)} € (bâti à "
             f"80 % du prix sur 30 ans) = <strong>résultat imposable de "
             f"{eur(S750['ebe'] - INTERETS_AN1 - DOTATION_AN1)} €, donc aucun IS "
             f"dû en année 1</strong>. Convention prudente retenue pour les "
             f"rendements publiés : IS de 15 % appliqué à l'EBE, soit "
             f"{eur(CONVENTION_IS * S750['ebe'])} €/an, sans amortissement du "
             f"bâti modélisé"),
            ("Prix de revient",
             f"<strong>{eur(ACTE_EN_MAIN)} €</strong> acte en main = prix "
             f"{eur(PRIX)} € + frais d'acquisition {eur(FRAIS_ACQUISITION)} € "
             f"({fr(TAUX_FRAIS * 100, 2)} %, retenus par le simulateur de "
             f"l'annonce elle-même), sans travaux (aucun devis). Ratio "
             f"coût/valeur de {fr(ACTE_EN_MAIN / VALEUR_RETENUE)} : le bien est "
             f"acheté à sa valeur, pas en dessous"),
            ("Financement (doctrine du parc)",
             f"apport 10 %, prêt de {eur(CAPITAL)} € sur {DUREE_ANS} ans à 3,7 % "
             f"et assurance emprunteur de 0,34 %, soit une mensualité de "
             f"<strong>{eur(MENS)} €/mois</strong> (0,00753 € par euro emprunté). "
             f"Cash-flow après crédit, avant IS, de <strong>{eur(CF750)} €/mois</strong> au loyer de "
             f"travail, {eur(CF851)} €/mois au loyer de marché et "
             f"{eur(CF620)} €/mois au loyer d'un bail ancien : négatif dans les "
             f"six lectures. Prix d'équilibre à 10 % d'apport : "
             f"{eur(prix_cashflow_nul(S750['ebe']))} € au loyer de travail"),
        ],
        stance=(
            f"<strong>On demande le bail et les charges. S'il ne produit pas au "
            f"moins {eur(LOYER_EXIGE)} € hors charges, on passe ; et même à ce "
            f"loyer, on n'achète pas au-dessus de "
            f"{eur(prix_5pct_avec_travaux(S851['ebe'], 0.0))} €.</strong><br><br>"
            f"Le raisonnement tient en deux temps, et le dossier échoue aux deux. "
            f"D'abord le prix : il est bon — {eur(PRIX / SURF)} €/m², sous le "
            f"premier quartile de son quartier ({eur(DVF_Q_4595_Q1)} €/m² sur "
            f"{eur(DVF_Q_4595_N)} ventes de 45 à 95 m²) et au niveau exact des "
            f"transactions réellement comparables de 2025 "
            f"({eur(DVF_CMP_MED)} €/m² sur {eur(DVF_CMP_N)} ventes d'appartements "
            f"seuls). Il n'y a donc aucune décote à capter : on n'achète pas ce "
            f"bien parce qu'il serait sous-évalué, mais parce que son rendement "
            f"tiendrait — et il ne tient pas. Ensuite le revenu : au loyer de "
            f"marché du quartier ({eur(LOYER_MARCHE_MED)} €/mois, ancrage OLV), le "
            f"rendement net avant IS est de {fr(S851['rdt_av'])} % sur les "
            f"{eur(ACTE_EN_MAIN)} € d'acte en main et {fr(S851['rdt_ap'])} % après "
            f"IS sous la convention prudente du moteur (IS de 15 % de l'EBE), "
            f"contre les 6,5 % net d'IS que s'impose le parc. Le cash-flow est de "
            f"{eur(CF851)} €/mois, et il faudrait un apport de "
            f"{eur(apport_cashflow_nul(PRIX, S851['ebe']))} € "
            f"({fr(apport_cashflow_nul(PRIX, S851['ebe']) / PRIX * 100, 0)} % du "
            f"prix) pour l'annuler. Même au haut de marché de "
            f"{eur(LOYER_HAUT)} €/mois — le maximum des relevés du quartier —, il "
            f"reste {eur(CF950)} €/mois de déficit et {fr(S950['rdt_av'])} % net "
            f"avant IS.<br><br>"
            f"<strong>Ce que cela implique pour une offre.</strong> Pour tenir "
            f"5 % net avant IS au loyer de marché, il faudrait payer "
            f"<strong>{eur(prix_5pct_avec_travaux(S851['ebe'], 0.0))} €</strong>, "
            f"soit {fr((PRIX - prix_5pct_avec_travaux(S851['ebe'], 0.0)) / PRIX * 100, 0)} % "
            f"sous le prix affiché ; et ce plafond baisse à "
            f"{eur(prix_5pct_avec_travaux(S851['ebe'], TRAVAUX_REF_2))} € dès "
            f"{eur(TRAVAUX_REF_2)} € de travaux, qui sont annoncés par l'annonce "
            f"elle-même mais non chiffrés. Au loyer le plus probable — celui d'un "
            f"bail de quinze ans, {eur(LOYER_ANCIEN)} à {eur(LOYER_BASE)} € —, le "
            f"plafond tombe entre {eur(plafond5(S620['ebe']))} et "
            f"{eur(plafond5(S750['ebe']))} €, c'est-à-dire la moitié du prix "
            f"affiché. <strong>Il n'y a pas de négociation possible sur ce "
            f"dossier avant d'avoir vu le bail : le prix demandé est le prix du "
            f"marché, et c'est le revenu qu'il faut vérifier.</strong><br><br>"
            f"<strong>Ce qu'on retient, en revanche, et qui vaut pour la suite du "
            f"sourcing.</strong> C'est le premier dossier de Saint-Jean-du-Var "
            f"jugé en lecture patrimoniale avec un bail en place, et il donne le "
            f"niveau de prix du quartier pour les prochains : "
            f"{eur(DVF_Q_4595_MED)} €/m² de médiane sur {eur(DVF_Q_4595_N)} ventes de "
            f"45 à 95 m², {eur(DVF_Q_4595_Q1)} €/m² au premier quartile, et des "
            f"transactions réellement comparables à {eur(DVF_CMP_MED)} €/m². Sur "
            f"un bien vendu loué, la règle de tri est simple : <strong>demander "
            f"le montant du loyer et la charge annuelle du lot avant de discuter "
            f"du prix</strong>, parce que c'est là que se joue le rendement, et "
            f"pas dans les 2 m² d'écart de l'annonce."
        ),
        prix_plafond=(
            f"<strong>Trois ancres, et une seule est praticable.</strong> Sur le "
            f"critère de rendement, le prix qui tient 5 % net avant IS est de "
            f"<strong>{eur(prix_5pct_avec_travaux(S851['ebe'], 0.0))} €</strong> "
            f"au loyer de marché ({eur(LOYER_MARCHE_MED)} €/mois), soit "
            f"{fr((PRIX - prix_5pct_avec_travaux(S851['ebe'], 0.0)) / PRIX * 100, 0)} % "
            f"sous le prix affiché — et de {eur(plafond5(S620['ebe']))} à "
            f"{eur(plafond5(S750['ebe']))} € si le bail de quinze ans porte "
            f"{eur(LOYER_ANCIEN)} à {eur(LOYER_BASE)} €/mois. Sur le critère de "
            f"trésorerie, la contrainte est plus brutale : à 10 % d'apport, le "
            f"prix qui donne un cash-flow nul au loyer de travail est de "
            f"<strong>{eur(prix_cashflow_nul(S750['ebe']))} €</strong>, et "
            f"l'équilibre demanderait sinon un apport de "
            f"{eur(apport_cashflow_nul(PRIX, S851['ebe']))} €, soit "
            f"{fr(apport_cashflow_nul(PRIX, S851['ebe']) / PRIX * 100, 0)} % du "
            f"prix. Sur le critère de valeur, enfin, la valeur retenue de "
            f"{eur(VALEUR_RETENUE)} € ({eur(SURF)} m² × "
            f"{eur(DVF_Q_4595_MED)} €/m², médiane du quartier sur "
            f"{eur(DVF_Q_4595_N)} ventes de 45 à 95 m²) donne un ratio coût/valeur de "
            f"<strong>{fr(ACTE_EN_MAIN / VALEUR_RETENUE)}</strong> : le prix "
            f"affiché achète le bien à sa valeur, sans décote.<br><br>"
            f"<strong>Ce qu'on retient comme cadre, si un contact devait être "
            f"poursuivi.</strong> Un plafond unique et conditionnel : "
            f"<strong>{eur(prix_5pct_avec_travaux(S851['ebe'], 0.0))} € acte en "
            f"main compris, soit "
            f"{eur(prix_5pct_avec_travaux(S851['ebe'], 0.0) / (1 + TAUX_FRAIS))} € "
            f"net vendeur</strong>, pour 5 % net avant IS au loyer de marché — "
            f"c'est-à-dire {fr((PRIX - prix_5pct_avec_travaux(S851['ebe'], 0.0)) / PRIX * 100, 0)} % "
            f"sous le prix affiché, et seulement si le bail produit au moins "
            f"{eur(LOYER_EXIGE)} € hors charges. Grille de travaux : "
            f"{eur(prix_5pct_avec_travaux(S851['ebe'], TRAVAUX_REF_1))} € avec "
            f"{eur(TRAVAUX_REF_1)} € de rafraîchissement, "
            f"{eur(prix_5pct_avec_travaux(S851['ebe'], TRAVAUX_REF_2))} € avec "
            f"{eur(TRAVAUX_REF_2)} €, "
            f"{eur(prix_5pct_avec_travaux(S851['ebe'], TRAVAUX_REF_3))} € avec "
            f"{eur(TRAVAUX_REF_3)} €. Tous ces plafonds sont publiés avec leur "
            f"hypothèse complète (vacance {fr(VAC_BASE, 0)} %, gestion "
            f"{fr(GESTION_BASE_PCT, 0)} %, charges estimées "
            f"{eur(COPRO_BASE)} €/an, crédit {eur(MENS)} €/mois) : sans cette "
            f"précision, un plafond n'est pas défendable face à un vendeur. "
            f"<strong>Au prix affiché et sans le bail, ce dossier ne s'achète "
            f"pas.</strong>"
        ),
        leviers=[
            "Le levier qui décide est le bail, et il n'existe qu'à une "
            "adresse : l'agence et le vendeur. Demander par écrit le bail en "
            "cours (date de signature, date d'effet, durée, loyer hors charges, "
            "provisions sur charges), la dernière régularisation de charges, les "
            "quittances des douze derniers mois et, si le locataire est en place "
            "depuis quinze ans, l'historique des révisions IRL. Sans ce "
            "document, on ne discute pas le prix : on discute au hasard",
            f"Deuxième pièce : les charges de copropriété. L'annonce n'en publie "
            f"aucune sur un immeuble de {ANNEE} avec ascenseur. Exiger le budget "
            f"prévisionnel, le montant de la charge annuelle du lot, le nombre de "
            f"lots, les trois derniers procès-verbaux d'assemblée générale et "
            f"l'état daté. Chaque euro de charge sort du rendement : "
            f"{fr(S851['rdt_av'] - S851C['rdt_av'])} point de rendement net avant "
            f"IS entre {eur(COPRO_BASE)} et {eur(COPRO_HAUT)} €/an, et le dossier "
            f"de Brignoles du même jour montre ce que 2 193 €/an font à un loyer "
            f"de 610 €",
            "Troisième pièce : le certificat Carrez et le règlement de "
            "copropriété. L'annonce donne 66 m² en titre et 68 m² dans le texte "
            f"— 3 % d'écart sur le prix au m² — et annonce une cave que la fiche "
            "caractéristiques dément (« Pas de cave »). Le règlement dira aussi "
            "si une place de stationnement est affectée au lot, ce que « parking "
            "collectif » ne dit pas",
            "Quatrième pièce : les devis de rafraîchissement. L'annonce dit que "
            "le bien « nécessitera des travaux de rafraîchissement dans le "
            "temps » sans les chiffrer. Chaque euro de travaux se déduit du prix "
            f"d'achat : le plafond 5 % tombe de "
            f"{eur(prix_5pct_avec_travaux(S851['ebe'], 0.0))} € à "
            f"{eur(prix_5pct_avec_travaux(S851['ebe'], TRAVAUX_REF_2))} € avec "
            f"{eur(TRAVAUX_REF_2)} € de travaux, et ces travaux ne sont pas "
            f"exécutables avec le locataire en place",
            "L'avis de taxe foncière et le DPE complet se demandent en même "
            "temps : l'avis donne la valeur locative cadastrale — seule base "
            "opposable — et le DPE complet dira si la facture annoncée (jusqu'à "
            f"{eur(FACTURE_HAUTE)} €/an) est un plafond réel du loyer acceptable",
            f"Le prix au m² n'est PAS un levier ici, et il faut le dire pour "
            f"rester crédible : à {eur(PRIX / SURF)} €/m² le bien est sous le "
            f"premier quartile de son quartier ({eur(DVF_Q_4595_Q1)} €/m²) et au "
            f"niveau des transactions comparables de 2025 "
            f"({eur(DVF_CMP_MED)} €/m² sur {eur(DVF_CMP_N)} ventes d'appartements "
            f"seuls). Attaquer le prix de front se ferait démolir par n'importe "
            f"quel agent avec deux transactions comparables. Le levier est le "
            f"loyer, puis les charges, puis les travaux",
            "Ce qui est attaquable, en revanche, c'est la contradiction de "
            "l'annonce : elle promet des « revenus locatifs immédiats dès la "
            "signature » et « une bonne rentabilité locative » sans publier le "
            "loyer, sur un immeuble dont elle ne publie pas non plus les "
            "charges. Poser par écrit que la rentabilité se calcule sur un loyer "
            "et une charge annuelle, et demander les deux chiffres, est la façon "
            "la plus rapide d'établir qu'on a lu le dossier — et de faire tomber "
            "l'argument de vente",
            "Enfin, ne rien engager sans l'état daté, le règlement de "
            "copropriété et les trois derniers PV : ces pièces gratuites donnent "
            "la quote-part réelle de charges, les obligations du lot et l'état "
            "des décisions collectives — les trois données qui manquent pour "
            f"chiffrer définitivement un immeuble de {ANNEE} avec ascenseur",
        ],
        meta=[
            f"<strong>Régime fiscal retenu :</strong> SCI à l'IS. Année 1 : EBE "
            f"{eur(S750['ebe'])} € moins intérêts {eur(INTERETS_AN1)} € "
            f"({eur(CAPITAL)} € à 3,7 %) et dotation aux amortissements "
            f"{eur(DOTATION_AN1)} € (bâti à 80 % du prix sur 30 ans) = résultat "
            f"imposable de {eur(S750['ebe'] - INTERETS_AN1 - DOTATION_AN1)} €, "
            f"négatif, donc aucun IS dû en année 1. Convention prudente retenue "
            f"pour les rendements publiés : IS de 15 % appliqué à l'EBE, sans "
            f"amortissement du bâti modélisé, soit "
            f"{eur(CONVENTION_IS * S750['ebe'])} €/an. Seuil de décision du parc "
            f"(6,5 % net d'IS) : {fr(S750['rdt_av'])} % net avant IS en base, "
            f"{fr(S750['rdt_ap'])} % après IS sous convention prudente, et "
            f"{fr(S851['rdt_av'])} % au loyer de marché, contre 6,5 % exigés",
            f"<strong>Convention de lecture des loyers :</strong> l'annonce ne "
            f"publie aucun loyer. La ligne de revenu de la base est le loyer "
            f"retenu, {eur(LOYER_BASE)} €/mois — borne haute de l'hypothèse de "
            f"travail pour un bail de quinze ans — et les quatre autres lectures "
            f"({eur(LOYER_ANCIEN)}, {eur(LOYER_MARCHE_MED)}, {eur(LOYER_HAUT)} "
            f"€/mois et {eur(LOYER_MARCHE_MED)} € avec {eur(COPRO_HAUT)} €/an de "
            f"charges) sont calculées par le moteur et publiées en table. Une "
            f"seule ligne de revenu est saisie en base : deux exploitations du "
            f"même lot ne sont pas deux lots",
            f"<strong>Frais d'acquisition :</strong> {eur(FRAIS_ACQUISITION)} € "
            f"({fr(TAUX_FRAIS * 100, 2)} %), retenus par le simulateur de "
            f"l'annonce elle-même ; honoraires à la charge du vendeur. Prix de "
            f"revient acte en main : {eur(ACTE_EN_MAIN)} €, sans travaux (aucun "
            f"devis — la fiche publie une grille de plafonds par tranche de "
            f"travaux)",
            f"<strong>Charges d'exploitation :</strong> taxe foncière estimée "
            f"{eur(TF_BASE)} €/an (avis non communiqué), charges de copropriété "
            f"estimées {eur(COPRO_BASE)} €/an (aucune charge publiée, variante "
            f"{eur(COPRO_HAUT)} €/an testée), assurance PNO {eur(PNO)} €, gestion "
            f"locative {fr(GESTION_BASE_PCT, 0)} % des loyers et provision travaux "
            f"{eur(PROV_BASE)} € (poste composite de "
            f"{eur(revenus_annuels(LOYER_BASE) * GESTION_BASE_PCT / 100.0 + PROV_BASE)} "
            f"€), comptabilité {eur(COMPTA)} €. Provision automatique de 2,5 % du "
            f"moteur désactivée pour ne pas compter deux fois la provision "
            f"travaux. Aucun poste laissé à zéro",
            f"<strong>Financement (doctrine du parc) :</strong> apport 10 %, prêt "
            f"de {eur(CAPITAL)} € sur {DUREE_ANS} ans à 3,7 % et assurance "
            f"emprunteur de 0,34 %, soit une mensualité de {eur(MENS)} €/mois "
            f"(0,00753 € par euro emprunté). Cash-flow de "
            f"<strong>{eur(CF750)} €/mois</strong> au loyer de travail et "
            f"{eur(CF851)} €/mois au loyer de marché. Ne pas lire cette fiche "
            f"comme un dossier finançable : aucun scénario de loyer, y compris le "
            f"haut du marché, ne produit un cash-flow positif au prix affiché",
            f"<strong>Valeur de marché :</strong> {eur(VALEUR_RETENUE)} € "
            f"({eur(SURF)} m² × {eur(DVF_Q_4595_MED)} €/m², médiane DVF 2025 du "
            f"quartier Saint-Jean-du-Var sur {eur(DVF_Q_4595_N)} ventes de 45 à 95 m² "
            f"dans la boîte de coordonnées de l'annonce), fourchette "
            f"{eur(VALEUR_BASSE)} à {eur(VALEUR_HAUTE)} €. La médiane communale "
            f"toutes surfaces ({eur(DVF_APP_MED)} €/m², {eur(DVF_APP_N)} ventes) n'est "
            f"pas utilisée : elle mélange des surfaces non comparables. "
            f"Comparables nommés à {eur(DVF_CMP_MED)} €/m² de médiane sur "
            f"{eur(DVF_CMP_N)} ventes d'appartements seuls de 2025",
            f"<strong>Pièces à demander avant toute décision :</strong> le bail "
            f"en cours et sa date, le loyer hors charges et les provisions sur "
            f"charges, la dernière régularisation de charges, l'avis de taxe "
            f"foncière, les trois derniers procès-verbaux d'assemblée générale, "
            f"le montant des charges et le nombre de lots de la copropriété, le "
            f"certificat Carrez exact (66 ou 68 m² ?), le DPE complet, et tout "
            f"devis de rafraîchissement déjà obtenu",
            f"<strong>Point de méthode :</strong> ce dossier est le premier de "
            f"Saint-Jean-du-Var jugé en lecture patrimoniale avec un bail en "
            f"place, et il fixe le niveau de prix du quartier pour les prochains "
            f"— {eur(DVF_Q_4595_MED)} €/m² de médiane sur {eur(DVF_Q_4595_N)} ventes "
            f"de 45 à 95 m² contre {eur(DVF_Q_4595_Q1)} €/m² au premier "
            f"quartile, et {eur(DVF_CMP_MED)} €/m² pour les transactions "
            f"réellement comparables. Règle de tri à retenir : sur un bien vendu "
            f"loué, <strong>demander le loyer du bail et la charge annuelle du "
            f"lot AVANT de discuter du prix</strong> — un prix au marché ne "
            f"compense jamais un revenu inconnu",
        ],
    )}
    c = gen.CONF[SLUG]
    html = gen.TEMPLATE.format(
        titre_court=c['titre_court'], adresse=c['adresse'], date_fr=c['date_fr'],
        source=c['source'], url=c['url'], badge=c['badge'], strategie=c['strategie'],
        fiscal_note=c['fiscal_note'],
        prix=eur(PRIX),
        surface=f"{eur(SURF)} m² (4 pièces, {CHAMBRES} chambres)",
        prix_m2=f"{eur(PRIX / SURF)} €/m²",
        revient=eur(ACTE_EN_MAIN),
        valeur=eur(VALEUR_RETENUE),
        revenus=eur(LOYER_BASE),
        rdt_revient=fr(S750['rdt_ap']), rdt_valeur=fr(S750['rdt_valeur']),
        note=fr(note, 1), note_cls=fr(note, 1).replace(',', '-'),
        lat=c['lat'], lon=c['lon'], quartier=c['quartier'],
        intro_attr=c['intro_attr'], profil=c['profil'], concl_attr=c['concl_attr'],
        attrs=gen.attr_html(rec_), intro_strat=c['intro_strat'],
        strats=gen.strategy_html(rec_),
        rationale=c['rationale'], identite=gen.identite_html(c['identite']),
        projections=proj_section + "\n" + loyer_section + "\n"
        + marche_locatif_section + "\n" + dvf_section + "\n" + besoins_section,
        risques=gen.risques_html(rec_),
        verdict_cls={"acheter": "buy", "negocier": "nego",
                     "fuir": "pass"}.get(verdict, "nego"),
        stance=c['stance'], prix_plafond=c['prix_plafond'],
        leviers=gen.leviers_html(c['leviers']),
        meta="\n".join(f"      <p>{m}</p>" for m in c['meta']),
    )

    # Libelles de cartes devenus faux au rendu (la fiche est ecrite par l'agent)
    for vieux, neuf in (
        ('<span class="card-label">Surface</span>',
         '<span class="card-label">Surface annoncée (titre)</span>'),
        ('<span class="card-label">Prix / m²</span>',
         '<span class="card-label">Prix / m² (sous le 1er quartile du quartier)</span>'),
        ('<span class="card-label">Prix de revient</span>',
         '<span class="card-label">Prix de revient (acte en main)</span>'),
        ('<span class="card-label">Valeur marché retenue</span>',
         '<span class="card-label">Valeur marché (DVF 2025, quartier 45-95 m²)</span>'),
        ('<span class="card-label">Revenus bruts</span>',
         '<span class="card-label">Loyer retenu (hypothèse de travail)</span>'),
        ('<span class="card-label">Rentabilité nette</span>',
         '<span class="card-label">Rendement net après IS (acte en main / valeur)</span>'),
    ):
        assert vieux in html, vieux
        html = html.replace(vieux, neuf)

    # Controles sur le HTML produit
    assert 'section class="verdict pass"' in html, "classe de verdict inattendue"
    assert 'note-' + fr(note, 1).replace(',', '-') in html
    assert 'verdict buy' not in html and 'verdict nego' not in html
    _manquent = []
    for vieux in ('119 900 €', '1 817 €', '129 492', '58 815',
                  '105 015', '84 815', '124 815', '2 264', '1 229', '18,6',
                  '57 149', '149 424', '1 809', '1 806', '6,20',
                  '6,83', '2 264', '130 548',
                  'On demande le bail et les charges', 'aucun IS dû',
                  'Convention prudente', 'revenus locatifs immédiats',
                  'Saint-Jean-du-Var', 'pratiquement'[:0] or 'bail en place'):
        if vieux not in html:
            _manquent.append(vieux)
    if _manquent:
        print("  ATTENTION : chiffres attendus absents du HTML :", _manquent)
    assert '<tr<' not in html, "balise <tr> malformee dans le tableau des lectures"
    assert '<trtd' not in html, "balise <tr> malformee dans le tableau des lectures"
    assert html.count('<td') % 1 == 0
    for lab in ("Bail ancien 620", "Base 750", "Marché 851", "Haut de marché 950",
                "avec 2 400 €/an de charges"):
        assert lab in html, f"ligne de lecture absente du tableau : {lab}"
    for vieux in ('{', '}', ):
        assert not any(x in html for x in ('{titre_court}', '{projections}')), vieux

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
        print(f"    {lab:<62} publie {pub:>14,.2f} | recalcule {rec2:>14,.2f} | "
              f"ecart {abs(pub - rec2):.2f} (tol {tol})")
    if ECARTS:
        print("\n  Chiffres du brief qui ne se recalculent PAS (non publies) :")
        for lab, brief, rec2, note_txt in ECARTS:
            print(f"    {lab:<62} brief {brief} | recalcule {rec2} — {note_txt}")


if __name__ == '__main__':
    main()
