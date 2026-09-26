#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche Appartement T3/F3 de 48 m2 (2 chambres + mezzanine), Brignoles,
quartier Centre Vieille Ville, 2e etage sans ascenseur, immeuble de 1948.

84 000 EUR (1 750 EUR/m2), SAFTI — Coralie MARCELIN EI, annonce SeLoger
2665KPL9U1PX (identifiant interne 280702235). Bien libre, non meuble, a
rafraichir ; 6 lots de copropriete, 540 EUR/an de charges et une PROCEDURE
SYNDICALE EN COURS (art. L. 721-1 du code de la construction et de
l'habitation) declaree par l'annonce elle-meme.

L'ANALYSE DE PRIX, qui est le coeur de cette fiche :
- prix affiche 1 750 EUR/m2, soit 10 a 17 % SOUS les trois ancres de marche
  de 2025 (mediane DVF du quartier Centre Vieille Ville sur la tranche
  45-60 m2 : 2 032 EUR/m2 -> 97 536 EUR pour 48 m2 ; mediane DVF communale de
  la meme tranche : 2 109 EUR/m2 -> 101 232 EUR ; prix moyen SeLoger du
  quartier : 1 953 EUR/m2 -> 93 744 EUR) et 19,5 % au-dessus du premier
  quartile du quartier (1 465 EUR/m2 -> 70 320 EUR) ;
- ce que ce prix achete : un rendement net avant IS de 4,65 % et un cash-flow
  negatif, le plafond 5 % net etant 78 148 EUR (-7,0 %) et le seuil de 6,5 %
  net d'IS du parc, 60 114 EUR (-28,4 %) ;
- ce qu'il ne dit pas : l'objet exact de la procedure de copropriete, qui
  commande a la fois les appels de fonds a venir et la revente.

Branche residentielle (SCI a l'IS). Chaque chiffre publie est reaffirme par
`calcule()` a tolerance depuis les lignes du modele (loyers, charges, credit,
fiscalite, plafonds, apports, DVF). Les donnees DVF 2025 sont recalculees
depuis le fichier du departement quand il est present (/tmp/dvf83_2025.csv.gz),
sinon les constantes sont controlees entre elles et la sortie le signale.

Les scenarios sont calcules par le MOTEUR (engine.compute sur une copie du
record, loyer, vacance et lignes de charges surchargees) — aucun scenario
n'est chiffre a la main.
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

SLUG = "2026-09-25-appartement-t3-brignoles-centre-vieille-ville"
URL = ("https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/"
       "var-83/brignoles-83170/2665KPL9U1PX")
DATE = "2026-09-25"
DATE_FR = "25 septembre 2026"

# --- Le bien -----------------------------------------------------------------
PRIX = 84000.0
FRAIS_ACQUISITION = 6720.0                    # 8 %, simulateur de l'annonce
ACTE_EN_MAIN = PRIX + FRAIS_ACQUISITION       # 90 720
TAUX_FRAIS = FRAIS_ACQUISITION / PRIX         # 8,00 %
SURF = 48.0
PIECES = 3
CHAMBRES = 2
ETAGE = "2e étage sur 6 étages, sans ascenseur"
ANNEE = 1948
LOTS_COPRO = 6
CHARGES_COPRO = 540.0                 # annoncées par l'annonce, 540 EUR/an
CHARGES_COPRO_HAUT = 1080.0           # variante testée : le double
PROCEDURE = True                      # procédure syndicale L. 721-1 en cours
DPE = "D"
GES = "B"
FACTURE_BASSE = 620.0
FACTURE_HAUTE = 880.0
PHOTOS = 6
MEZZANINE = True

# --- Loyers de marche (les trois ancres datees) ------------------------------
# Fiche de reference interne (analyses/marches-locaux, 21/09/2026) : 11,0 EUR/m2.
# Trackstone, appartements Brignoles : 12,0 EUR/m2 (8,1 a 18,1). SeLoger ville,
# estimation de location : 13 EUR/m2 (9 a 20). Annonces reelles de T3 du secteur :
# 70 m2 a 786 EUR/mois (11,2) et 70 m2 a 855 EUR CC (12,2).
LOYER_M2_BAS = 11.0
LOYER_M2_MED = 12.0
LOYER_M2_HAUT = 13.0
LOYER_BASE = SURF * LOYER_M2_MED          # 576 EUR/mois
LOYER_BAS = SURF * LOYER_M2_BAS           # 528 EUR/mois
LOYER_HAUT = SURF * LOYER_M2_HAUT         # 624 EUR/mois
LOYER_EXIGE = 600.0
REALADVISOR_MED = 828.0                   # loyer médian d'un appartement, quartier

# --- Doctrine du parc : seuil de rendement et credit -------------------------
SEUIL = 0.05                           # 5 % net avant IS, comme les autres fiches
COEF_PLAFOND = SEUIL * (1 + TAUX_FRAIS)     # EBE = 5,4 % du prix affiché
APPORT_PCT = 0.10
TAUX_CREDIT = 0.037
ASSURANCE_PCT = 0.0034
DUREE_ANS = 15
CAPITAL = PRIX * (1 - APPORT_PCT)             # 75 600
MENS_PAR_EURO_MODELE = 0.00753
MENS_MODELE = 569.0                           # mensualité publiée

# --- Charges d'exploitation du modèle (scénario de base) ---------------------
TF_BASE = 800.0               # ESTIMEE, avis de taxe foncière non communiqué
COPRO_BASE = CHARGES_COPRO    # 540 EUR/an, ANNONCEE par l'annonce
COPRO_HAUT = CHARGES_COPRO_HAUT
PNO = 100.0
COMPTA = 400.0
PROV_BASE = 150.0
GESTION_BASE_PCT = 5.0
VAC_BASE = 5.0
VAC_BEST = 3.0
VAC_WORST = 10.0

# --- Piste etudiee puis ecartee : colocation de deux chambres ----------------
COLOC_BAS = 420.0        # par chambre et par mois
COLOC_HAUT = 450.0

# --- Fiscalité année 1 (modèle du brief) -------------------------------------
QUOTE_PART_BATI_MODELE = 0.80                 # bâti à 80 % du PRIX affiché
DOTATION_AN1 = PRIX * QUOTE_PART_BATI_MODELE / 30.0     # 2 240,00
INTERETS_AN1 = CAPITAL * TAUX_CREDIT                    # 2 797,20
CONVENTION_IS = 0.15                                    # IS prudent sur l'EBE

# --- Travaux : aucun devis, donc une grille et pas un chiffre ----------------
TRAVAUX_REF_1 = 10000.0
TRAVAUX_REF_2 = 20000.0
TRAVAUX_REF_3 = 30000.0

# --- Marché local (fiche de référence analyses/marches-locaux, 21/09/2026) ---
MARCHE_M2_COMMUNE = 2325                # fiche de référence du 21/09/2026
LOYER_REF_M2 = 11.0                     # lot type 60 m2 de la fiche de reference
PLAF_PATRIMONIAL = (1021, 943, 818)     # 6,5 % / 7,0 % / 8,0 % net d'IS
PLAF_MDB = (558, 516, 489)              # marge nette marchand de biens

# --- DVF 2025 réelle, Brignoles (commune 83023) ------------------------------
# Méthode : mutations de nature « Vente » uniquement ; valeur foncière de la
# mutation divisée par la somme des surfaces bâties de la mutation ; surfaces
# > 5 m2 et valeurs > 5 000 EUR. Tranches de surface en m2.
DVF_FICHIER = '/tmp/dvf83_2025.csv.gz'
DVF_COMMUNE = '83023'
DVF_LIGNES_VENTE = 883        # lignes DVF de nature Vente de la commune
DVF_MUTATIONS = 447           # mutations lues (toutes natures)
DVF_MUTATIONS_VENTE = 397     # mutations de nature Vente
DVF_APP_N = 168               # ventes d'appartements exploitables
DVF_APP_MED = 2246            # médiane appartements, toutes surfaces
DVF_APP_1530_N = 7
DVF_APP_1530_MED = 2250
DVF_APP_3045_N = 46
DVF_APP_3045_MED = 2863
DVF_APP_3045_PRIX = 114000
DVF_APP_4560_N = 33           # la tranche du bien (48 m2)
DVF_APP_4560_MED = 2109
DVF_APP_4560_Q1 = 1791
DVF_APP_4560_Q3 = 2606
DVF_APP_4560_PRIX = 116000
DVF_APP_6090_N = 66
DVF_APP_6090_MED = 2188
DVF_MAI_N = 142
DVF_MAI_MED = 2841
DVF_MAI_60120_N = 83
DVF_MAI_60120_PRIX = 270000
# Quartier Centre Vieille Ville : boîte de coordonnées du centre ancien.
DVF_BOITE = (43.398, 43.412, 6.050, 6.072)   # lat min, lat max, lon min, lon max
DVF_Q_APP_N = 116             # ventes d'appartements dans la boîte
DVF_Q_MED = 2081              # médiane toutes surfaces du quartier
DVF_Q_4560_N = 24             # quartier, tranche 45-60 m2
DVF_Q_4560_MED = 2032
DVF_Q_4560_Q1 = 1465
DVF_Q_4560_Q3 = 2295
DVF_Q_4560_PRIX = 103050
# Population des appartements seuls du centre ancien sur 45 a 56 m2 en 2025,
# puis les six transactions nommees qui encadrent le plus serre le bien.
DVF_Q_4556_N = 22
DVF_Q_4556_MIN = 1132
DVF_Q_4556_MAX = 4422
DVF_CMP_N = 6
DVF_CMP_MED = 1824
DVF_CMP_PRIX = 91000
DVF_COMPARABLES = (
    dict(date="03/12/2025", surf=45.0, prix=84000.0, m2=1867, lots=1,
         voie="rue Jules Ferry", box=True),
    dict(date="05/12/2025", surf=55.0, prix=98000.0, m2=1782, lots=1,
         voie="avenue des Berges", box=True),
    dict(date="19/12/2025", surf=50.0, prix=70000.0, m2=1400, lots=1,
         voie="rue Jules Ferry", box=True),
    dict(date="12/03/2025", surf=46.0, prix=68000.0, m2=1478, lots=1,
         voie="rue de la Poissonnerie", box=True),
    dict(date="30/04/2025", surf=54.0, prix=125000.0, m2=2315, lots=1,
         voie="rue Petit Paradis", box=True),
    dict(date="25/02/2025", surf=55.0, prix=116000.0, m2=2109, lots=2,
         voie="place Jean Raynaud", box=True),
)

# --- Valeur de marché retenue (ancre DVF quartier, tranche 45-60 m2) ---------
VALEUR_BASSE = SURF * DVF_Q_4560_Q1     # 70 320
VALEUR_RETENUE = SURF * DVF_Q_4560_MED  # 97 536
VALEUR_HAUTE = SURF * DVF_Q_4560_Q3     # 110 160
VALEUR_COMMUNE = SURF * DVF_APP_4560_MED    # 101 232
VALEUR_SELOGER = SURF * 1953.0              # 93 744 (prix moyen du quartier)


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




# ---------------------------------------------------------------------------
# 1 bis. Hypotheses chiffrees AVANT le record : la meme formule que le moteur
# (ebe_modele pour l'EBE, IS de 15 % de l'EBE pour la convention prudente du
# moteur). main() verifie chaque ligne contre engine.compute via scen().
# ---------------------------------------------------------------------------
def hypo(loyer, vac=None, gestion=None, tf=None, copro=None, prov=None):
    vac = VAC_BASE if vac is None else vac
    gestion = GESTION_BASE_PCT if gestion is None else gestion
    tf = TF_BASE if tf is None else tf
    copro = COPRO_BASE if copro is None else copro
    prov = PROV_BASE if prov is None else prov
    ebe = ebe_modele(loyer, vac, gestion, tf, copro, prov)
    net = ebe * (1.0 - CONVENTION_IS)
    return dict(
        loyer=loyer, brut=revenus_annuels(loyer), ebe=ebe, net=net,
        fixes=charges_fixes(tf, copro, prov), vac_eur=revenus_annuels(loyer) * vac / 100.0,
        gestion_eur=revenus_annuels(loyer) * gestion / 100.0,
        is_=ebe * CONVENTION_IS,
        rdt_av=ebe / ACTE_EN_MAIN * 100.0, rdt_ap=net / ACTE_EN_MAIN * 100.0,
        rdt_valeur=net / VALEUR_RETENUE * 100.0, rdt_brut=revenus_annuels(loyer) / PRIX * 100.0,
        cap5=plafond5(ebe), cf=cashflow_mensuel(ebe), cf_ap=cashflow_mensuel(net),
        cf_mois=ebe / 12.0, net_mois=net / 12.0,
    )


def plafond_is(ebe, seuil=0.065):
    """Prix affiche qui tient un rendement NET D'IS cible, frais compris."""
    return ebe / (seuil * (1 + TAUX_FRAIS))


def coloc_n(rec, loyer_chambre, nb):
    """Piste colocation : nb chambres meublees (moteur)."""
    v = copy.deepcopy(rec)
    v['marche']['loyers'] = [dict(
        lot=f"{nb} chambres meublees a {eur(loyer_chambre)} EUR/mois chacune",
        quantite=nb, loyer_mensuel_euros=loyer_chambre, occupe=True,
        note="Variante etudiee puis ecartee : elle suppose de meubler et de "
             "decouper le logement, un reglement de copropriete qui "
             "l'autorise et un marche de la colocation qui n'existe pas ici.")]
    ch = v['hypotheses']['charges']
    ch['taxe_fonciere_annuelle_euros'] = TF_BASE
    ch['charges_copro_annuelles_euros'] = COPRO_BASE
    ch['entretien_annuel_euros'] = round(
        nb * loyer_chambre * 12.0 * GESTION_BASE_PCT / 100.0 + PROV_BASE, 2)
    c = engine.compute(v)
    assert c['calculable'], c['raison']
    f = c['fiscal']
    return dict(loyer=loyer_chambre, nb=nb, revenus=c['revenus_bruts_annuels'],
                ebe=f['ebe'], net=f['net_apres_is'],
                rdt_ap=f['net_apres_is'] / ACTE_EN_MAIN * 100.0,
                cf=cashflow_mensuel(f['ebe']),
                cf_ap=cashflow_mensuel(f['net_apres_is']))



# ---------------------------------------------------------------------------
# 2. Verificateur DVF : chaque statistique publiee est recalculee
# ---------------------------------------------------------------------------
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
    for lo_, hi_, n_, m_ in ((15, 30, DVF_APP_1530_N, DVF_APP_1530_MED),
                             (30, 45, DVF_APP_3045_N, DVF_APP_3045_MED),
                             (45, 60, DVF_APP_4560_N, DVF_APP_4560_MED),
                             (60, 90, DVF_APP_6090_N, DVF_APP_6090_MED)):
        sel = [i['m2'] for i in app if lo_ <= i['s'] < hi_]
        calcule(f"DVF appartements {lo_}-{hi_} m2 (n)", n_, len(sel), 0)
        calcule(f"DVF appartements {lo_}-{hi_} m2 (mediane)", m_, med(sel), 0)
    calcule("DVF prix median des appartements 30-45 m2", DVF_APP_3045_PRIX,
            round(st.median([i['v'] for i in app if 30 <= i['s'] < 45])), 0)
    sel = [(i['s'], i['v']) for i in app if 45 <= i['s'] < 60]
    calcule("DVF prix median des appartements 45-60 m2", DVF_APP_4560_PRIX,
            round(st.median([v for _, v in sel])), 0)
    m2s = [i['m2'] for i in app if 45 <= i['s'] < 60]
    q = st.quantiles(m2s, n=4)
    calcule("DVF Q1 appartements 45-60 m2", DVF_APP_4560_Q1, round(q[0]), 0)
    calcule("DVF Q3 appartements 45-60 m2", DVF_APP_4560_Q3, round(q[2]), 0)
    calcule("DVF maisons 60-120 m2 (n)", DVF_MAI_60120_N,
            sum(1 for rs in ventes if any(r['type_local'] == 'Maison'
                                          for r in rs)
                and 60 <= sum(f2(r['surface_reelle_bati']) or 0.0 for r in rs)
                < 120), 0)
    calcule("DVF prix median des maisons 60-120 m2", DVF_MAI_60120_PRIX,
            round(st.median([f2(rs[0]['valeur_fonciere']) or 0.0 for rs in ventes
                             if any(x['type_local'] == 'Maison' for x in rs)
                             and 60 <= sum(f2(x['surface_reelle_bati']) or 0.0
                                           for x in rs) < 120])), 0)
    # --- quartier Centre Vieille Ville (boite de coordonnees) ---------------
    qs = [i for i in app if i['box']]
    calcule("DVF quartier Centre Vieille Ville : ventes d'appartements",
            DVF_Q_APP_N, len(qs), 0)
    calcule("DVF quartier : mediane appartements", DVF_Q_MED,
            med([i['m2'] for i in qs]), 0)
    qb = [i for i in qs if 45 <= i['s'] < 60]
    calcule("DVF quartier 45-60 m2 (n)", DVF_Q_4560_N, len(qb), 0)
    calcule("DVF quartier 45-60 m2 (mediane)", DVF_Q_4560_MED,
            med([i['m2'] for i in qb]), 0)
    qqb = st.quantiles([i['m2'] for i in qb], n=4)
    calcule("DVF quartier 45-60 m2 (Q1)", DVF_Q_4560_Q1, round(qqb[0]), 0)
    calcule("DVF quartier 45-60 m2 (Q3)", DVF_Q_4560_Q3, round(qqb[2]), 0)
    calcule("DVF quartier 45-60 m2 (prix median)", DVF_Q_4560_PRIX,
            round(st.median([i['v'] for i in qb])), 0)
    # --- transactions nommement comparables ---------------------------------
    # Population large : appartements du centre ancien de 45 a 56 m2 en 2025.
    large = [i for i in qs if 45 <= i['s'] <= 56]
    calcule("DVF 45-56 m2 du centre ancien (n)", DVF_Q_4556_N, len(large), 0)
    calcule("DVF 45-56 m2 du centre ancien (EUR/m2 le plus bas)",
            DVF_Q_4556_MIN, round(min(i['m2'] for i in large)), 0)
    calcule("DVF 45-56 m2 du centre ancien (EUR/m2 le plus haut)",
            DVF_Q_4556_MAX, round(max(i['m2'] for i in large)), 0)
    # Population retenue : les SIX transactions nommees de la fiche.
    def _cmp(i):
        return any(abs(i['v'] - c['prix']) < 1.0 and abs(i['s'] - c['surf']) < 1.0
                   for c in DVF_COMPARABLES)
    pool = [i for i in qs if _cmp(i)]
    assert len(pool) == len(DVF_COMPARABLES), (len(pool), len(DVF_COMPARABLES))
    calcule("DVF comparables (n)", DVF_CMP_N, len(pool), 0)
    calcule("DVF comparables (mediane EUR/m2)", DVF_CMP_MED,
            round(st.median([i['m2'] for i in pool])), 1)
    calcule("DVF comparables (prix median)", DVF_CMP_PRIX,
            round(st.median([i['v'] for i in pool])), 1)
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


# ---------------------------------------------------------------------------
# 3. Le record : tout ce que l'annonce dit, et tout ce qu'elle ne dit pas
# ---------------------------------------------------------------------------
def rec_t3():
    SBAS = hypo(LOYER_BAS)
    SBASE = hypo(LOYER_BASE)
    SHAUT = hypo(LOYER_HAUT)
    SCOPRO = hypo(LOYER_BASE, copro=COPRO_HAUT)
    SBEST = hypo(LOYER_BASE, vac=VAC_BEST, gestion=4.0)
    SWORST = hypo(LOYER_BASE, vac=VAC_WORST, tf=1100.0, copro=COPRO_HAUT,
                  prov=400.0)
    C420 = hypo(2.0 * COLOC_BAS)
    C450 = hypo(2.0 * COLOC_HAUT)
    return {
        "slug": SLUG,
        "date_analyse": DATE,
        "date_maj": None,
        "titre": (
            f"Appartement T3 de {eur(SURF)} m² avec mezzanine au {ETAGE}, "
            f"à rafraîchir — quartier Centre Vieille Ville, Brignoles (83170)"
        ),
        "bien": {
            "type_bien": "appartement",
            "sous_type": None,
            "type_detail": (
                f"Appartement T3/F3 (3 pièces, {CHAMBRES} chambres) de "
                f"{eur(SURF)} m², « espace supplémentaire » en mezzanine non "
                f"compté dans la surface annoncée, au {ETAGE}, immeuble de "
                f"{ANNEE}, quartier Centre Vieille Ville à Brignoles (83170). "
                f"Non meublé, cuisine ouverte, chauffage individuel "
                f"électrique, ni cave ni balcon ni terrasse, 1 lot détenu dans "
                f"une copropriété de {LOTS_COPRO} lots, {PHOTOS} photos. DPE "
                f"{DPE}, GES {GES}, facture énergétique annoncée de "
                f"{eur(FACTURE_BASSE)} à {eur(FACTURE_HAUTE)} €/an. Honoraires "
                f"à la charge du vendeur, simulateur d'acquisition de l'annonce "
                f"à {eur(FRAIS_ACQUISITION)} € (8,0 %). "
                f"LE POINT QUI COMMANDE TOUT : l'annonce déclare elle-même que "
                f"« le syndicat des copropriétaires fait l'objet d'une procédure "
                f"citée à l'article L. 721-1 du code de la construction et de "
                f"l'habitation ». Une copropriété de {LOTS_COPRO} lots avec "
                f"procédure, c'est un budget prévisionnel insuffisant, des "
                f"travaux à financer et un acheteur qui se demande pourquoi un "
                f"bien se vend 14 % sous la médiane de son quartier. Aucun des "
                f"quatre documents qui répondraient (procès-verbaux des trois "
                f"dernières assemblées, état daté, appels de fonds votés, "
                f"diagnostics complets) n'est joint."
            ),
            "neuf": False,
            "adresse": {
                "texte": (
                    "Quartier Centre Vieille Ville, Brignoles (83170) — adresse "
                    "exacte non publiée dans l'annonce ; agence SAFTI, "
                    "Coralie Marcelin EI (RSAC Draguignan), secteur Brignoles"
                ),
                "ville": "Brignoles",
                "code_postal": "83170",
            },
            "surfaces": {
                "texte": (
                    f"{eur(SURF)} m² annoncés ({eur(PRIX / SURF)} €/m²), "
                    f"3 pièces et {CHAMBRES} chambres, plus une mezzanine "
                    f"présentée comme « espace supplémentaire » : cette surface "
                    f"n'entre pas dans le Carrez, donc elle ne se paie pas au "
                    f"prix du m² habitable et elle ne se loue pas comme une "
                    f"pièce — mais elle explique qu'un T3 de {eur(SURF)} m² "
                    f"tienne {CHAMBRES} chambres. Le certificat Carrez de la "
                    f"mezzanine et des combles reste à obtenir"
                ),
                "carrez_m2": SURF,
            },
            "lots": {
                "count": 1,
                "surface_par_lot_m2": SURF,
                "nature": (
                    f"Un seul lot : l'appartement T3 de {eur(SURF)} m², dans "
                    f"une copropriété de {LOTS_COPRO} lots (source : annonce). "
                    f"Ni cave, ni grenier, ni place de stationnement dans la "
                    f"fiche caractéristiques — donc aucun lot annexe cessible et "
                    f"aucun revenu annexe. La copropriété de {LOTS_COPRO} lots "
                    f"est petite : c'est là que les travaux votés se partagent "
                    f"le plus mal, et c'est là qu'une procédure de l'article "
                    f"L. 721-1 pèse le plus lourd"
                ),
                "lots_distincts": 1,
            },
            "copro": {
                "charges_annuelles_euros": COPRO_BASE,
                "charges_source": (
                    f"{eur(COPRO_BASE)} €/an, ANNONCÉS par l'annonce — la "
                    f"seule charge d'exploitation du dossier qui ne soit pas une "
                    f"estimation. Au loyer de marché retenu "
                    f"({eur(LOYER_BASE)} €/mois), elle absorbe "
                    f"{fr(COPRO_BASE / (LOYER_BASE * 12) * 100)} % des revenus : "
                    f"c'est quatre fois moins que le dossier de Brignoles du "
                    f"même jour (2 193 €/an, 30 % du loyer, chauffage collectif "
                    f"au fioul) et c'est le meilleur point du dossier. MAIS elle "
                    f"n'est PAS sanctuarisée : une copropriété de {LOTS_COPRO} "
                    f"lots sous procédure L. 721-1, c'est précisément le "
                    f"scénario dans lequel la charge annuelle double en deux ans. "
                    f"Le modèle teste donc la variante {eur(COPRO_HAUT)} €/an"
                ),
            },
            "travaux": {
                "montant_euros": 0.0,
                "nature": (
                    "Aucun devis, donc aucun montant retenu : le modèle publie "
                    "une GRILLE par enveloppe (10 000, 20 000, 30 000 €) et non "
                    "un chiffre. Le bien est de 1948, en DPE D, non meublé, "
                    "« à rafraîchir » — mais l'annonce ne décrit aucune "
                    "dégradation, aucune photo ne montre de désordre et le "
                    "chauffage comme la cuisine sont donnés pour récents. "
                    "À l'inverse, une copropriété sous procédure peut apporter "
                    "des travaux d'office sur les parties communes (toiture, "
                    "façade, réseaux) qu'aucune expertise individuelle ne "
                    "révèle : c'est exactement ce que l'état daté et les trois "
                    "derniers PV doivent chiffrer"
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
                f"{eur(PRIX / SURF)} €/m² sur {eur(SURF)} m² — et "
                f"{eur(ACTE_EN_MAIN)} € d'acte en main avec les "
                f"{eur(FRAIS_ACQUISITION)} € de frais affichés par le "
                f"simulateur de l'annonce. L'annonce écrit elle-même que le "
                f"bien est « moins cher que des biens comparables dans la "
                f"région » : le calcul lui donne raison sur le prix, et tort "
                f"sur l'implication. Sous la médiane du quartier, il n'y a pas "
                f"de décote à capter — il y a un prix de marché qui intègre "
                f"déjà la procédure de copropriété, l'absence d'ascenseur et un "
                f"T3 de {eur(SURF)} m² dont une partie de la surface utile est "
                f"une mezzanine"
            ),
        },
        "marche": {
            "valeur": {
                "basse_euros": VALEUR_BASSE,
                "haute_euros": VALEUR_HAUTE,
                "retenue_euros": VALEUR_RETENUE,
                "source": (
                    f"DVF 2025, ancrage sur le QUARTIER et non sur la commune : "
                    f"{DVF_Q_4560_N} ventes d'appartements de 45 à 60 m² dans le "
                    f"centre ancien de Brignoles, médiane "
                    f"{eur(DVF_Q_4560_MED)} €/m², premier quartile "
                    f"{eur(DVF_Q_4560_Q1)} €/m², troisième quartile "
                    f"{eur(DVF_Q_4560_Q3)} €/m², prix médian "
                    f"{eur(DVF_Q_4560_PRIX)} €. Contrôle par deux sources "
                    f"indépendantes : SeLoger donne le quartier Centre Vieille "
                    f"Ville à 1 953 €/m² de moyenne (bornes 1 465 à 2 930 — la "
                    f"borne basse est exactement le Q1 DVF) et Meilleurs Agents "
                    f"l'appartement brignolais à 2 250 €/m² toutes surfaces. "
                    f"Valeur retenue = {eur(SURF)} m² × {eur(DVF_Q_4560_MED)} "
                    f"€/m² = {eur(VALEUR_RETENUE)} €"
                ),
                "confiance": "moyenne",
            },
            "loyers": [
                {
                    "lot": (
                        f"Appartement T3 de {eur(SURF)} m² — bien libre, "
                        f"non meublé, à rafraîchir"
                    ),
                    "quantite": 1,
                    "loyer_mensuel_euros": LOYER_BASE,
                    "occupe": False,
                    "note": (
                        f"UNE SEULE LIGNE DE REVENU, à {eur(LOYER_BASE)} €/mois "
                        f"({fr(LOYER_M2_MED)} €/m²), soit "
                        f"{eur(LOYER_BASE * 12)} €/an bruts. Trois ancrages "
                        f"datés convergent : la fiche de référence interne du "
                        f"21/09/2026 retient {fr(LOYER_REF_M2)} €/m² pour un lot "
                        f"type de 60 m² (soit {eur(SURF * LOYER_REF_M2)} €) ; "
                        f"Trackstone donne {fr(LOYER_M2_MED)} €/m² pour "
                        f"l'appartement brignolais ({eur(SURF * LOYER_M2_MED)} "
                        f"€) ; SeLoger estime la ville à {fr(LOYER_M2_HAUT)} "
                        f"€/m² ({eur(SURF * LOYER_M2_HAUT)} €). Les annonces "
                        f"réelles du secteur confirment : 70 m² affichés à "
                        f"786 €/mois (11,2 €/m²) et 70 m² à 855 € charges "
                        f"comprises (12,2 €/m²). LA FOURCHETTE PUBLIÉE EST DONC "
                        f"{eur(LOYER_BAS)} À {eur(LOYER_HAUT)} €/MOIS, et c'est "
                        f"un loyer nu hors charges : dans une copropriété de "
                        f"{LOTS_COPRO} lots, les charges locatives récupérables "
                        f"se refacturent au locataire, mais une provision sur "
                        f"charges mal calibrée sur un immeuble de {ANNEE} se "
                        f"retourne toujours contre le bailleur à la "
                        f"régularisation"
                    ),
                },
            ],
            "notes": (
                f"LE DOSSIER NE SE JUGE PAS SUR SON PRIX, ET C'EST EXACTEMENT "
                f"L'INVERSE DU RÉFLEXE : à {eur(PRIX / SURF)} €/m², le bien est "
                f"{fr(abs((PRIX / SURF - DVF_Q_4560_MED) / DVF_Q_4560_MED * 100), 1)} % "
                f"SOUS la médiane de son quartier pour sa tranche de surface et "
                f"{fr(abs((PRIX / SURF - DVF_APP_4560_MED) / DVF_APP_4560_MED * 100), 1)} % "
                f"sous la médiane communale de la même tranche — un écart qui "
                f"ne se trouve pas sur un marché où la fiche de référence "
                f"montre qu'aucune des douze villes du secteur n'atteint le "
                f"seuil patrimonial au prix de marché. Ce prix bas s'explique "
                f"et s'assume : procédure de copropriété en cours, 2e étage "
                f"sans ascenseur dans un immeuble de {ANNEE}, T3 de "
                f"{eur(SURF)} m² dont la troisième pièce utile est une "
                f"mezzanine hors Carrez. Ce qui décide de l'affaire n'est donc "
                f"pas le prix affiché, mais les deux inconnues qui l'ont "
                f"produit : le coût réel de la procédure de copropriété et le "
                f"montant des travaux à venir. Le rendement net avant IS au "
                f"loyer médian est de {fr(SBASE['rdt_av'])} % pour un plafond 5 % à "
                f"{eur(SBASE['cap5'])} € : le prix est "
                f"{fr((PRIX - SBASE['cap5']) / PRIX * 100, 1)} % trop cher pour "
                f"la doctrine, "
                f"mais il n'est pas absurde — c'est un dossier de pièces, pas "
                f"un dossier mort"
            ),
        },
        "hypotheses": {
            "vacance_base_pct": VAC_BASE,
            "vacance_best_pct": VAC_BEST,
            "vacance_worst_pct": VAC_WORST,
            "vacance_justification": (
                f"{fr(VAC_BASE)} % en scénario de base : le bien est libre, donc "
                f"il n'y a ni loyer acquis ni vacance héritée — mais il y a une "
                f"vacance de mise en location au départ (annonces, visites, "
                f"travaux) et un marché locatif brignolais peu tendu, où un T3 "
                f"sans ascenseur au 2e étage se reloue en quelques semaines, pas "
                f"en quelques jours. À 3 % en hypothèse favorable (locataire "
                f"trouvé et en place dès le premier mois) et 10 % en hypothèse "
                f"défavorable, avec une remise en état, un repaint et une "
                f"recherche longue sur un bien atypique"
            ),
            "frais_acquisition_euros": FRAIS_ACQUISITION,
            "frais_divers_euros": 0.0,
            "quote_part_bati_pct": 0.0,
            "duree_amortissement_ans": 30,
            "fiscalite_commentaire": (
                f"SCI à l'IS. Calcul réel de l'année 1 : EBE "
                f"{eur(4230)} moins intérêts d'emprunt {eur(INTERETS_AN1)} "
                f"({eur(CAPITAL)} à 3,7 %) moins dotation aux amortissements "
                f"{eur(DOTATION_AN1)} (bâti à 80 % du prix affiché sur 30 ans) = "
                f"{eur(4230 - INTERETS_AN1 - DOTATION_AN1)}, soit un DÉFICIT : "
                f"aucun IS dû en année 1, et le résultat se reconduit tant que "
                f"les intérêts et la dotation dépassent l'EBE. Les rendements "
                f"nets publiés restent sous la convention prudente du moteur (IS "
                f"de 15 % de l'EBE), dite explicitement — c'est la lecture la "
                f"plus défavorable, donc celle qui décide. Seuil de décision du "
                f"parc : 6,5 % net d'IS"
            ),
            "charges": {
                "taxe_fonciere_annuelle_euros": TF_BASE,
                "taxe_fonciere_commentaire": (
                    f"ESTIMATION {eur(TF_BASE)} €/an — l'avis de taxe foncière "
                    f"n'est pas communiqué par le vendeur ni par l'agence, et "
                    f"c'est la deuxième pièce à exiger. Repère de calcul : "
                    f"l'ancienne base départementale du Var taxe environ 50 % de "
                    f"la valeur locative cadastrale, et une valeur locative "
                    f"cadastrale de T3 ancien à Brignoles tourne autour de "
                    f"3 000 € : l'ordre de grandeur de 800 € tient, mais il se "
                    f"vérifie par l'avis, pas par l'estimation"
                ),
                "charges_copro_annuelles_euros": COPRO_BASE,
                "charges_copro_commentaire": (
                    f"{eur(COPRO_BASE)} €/an ANNONCÉS (45 €/mois), soit "
                    f"{fr(COPRO_BASE / (LOYER_BASE * 12) * 100)} % du loyer "
                    f"brut de marché : c'est un rapport sain pour un immeuble "
                    f"de {ANNEE} sans ascenseur, et c'est la seule donnée "
                    f"d'exploitation que l'annonce fournit. Deux réserves, "
                    f"toutes deux comptables : une copropriété de {LOTS_COPRO} "
                    f"lots sous procédure L. 721-1 peut voter demain une "
                    f"augmentation du budget ou un emprunt de travaux, et une "
                    f"charge annoncée à 540 € pour six lots (3 240 € de budget "
                    f"annuel) est un budget de copropriété très maigre — "
                    f"précisément le profil d'une copropriété qui n'a pas "
                    f"provisionné"
                ),
                "pno_annuelle_euros": PNO,
                "pno_commentaire": (
                    f"Assurance propriétaire non occupant du lot, {eur(PNO)} €/an "
                    f": le logement est libre à la vente, donc assuré en PNO "
                    f"jusqu'à sa mise en location, puis en assurance "
                    f"propriétaire bailleur"
                ),
                "entretien_annuel_euros": 496.0,
                "entretien_commentaire": (
                    f"Poste composite, détaillé : gestion locative "
                    f"{eur(LOYER_BASE * 12 * GESTION_BASE_PCT / 100)} € "
                    f"({fr(GESTION_BASE_PCT)} % des {eur(LOYER_BASE * 12)} € de "
                    f"loyers bruts, même en gestion directe, le temps passé se "
                    f"paie en heures) plus une provision de travaux et de "
                    f"renouvellement de {eur(PROV_BASE)} €/an (peintures, "
                    f"chauffe-eau, VMC, robinetterie : un appartement de 1948 "
                    f"consomme cette provision, pas moins). Le moteur ajoute "
                    f"par ailleurs une provision de rénovation automatique de "
                    f"2,5 % des loyers ({eur(SBASE['brut'] * 0.025)} €/an) : "
                    f"elle est DÉSACTIVÉE sur cette fiche "
                    f"(provision_desactivee) parce que la ligne ci-dessus la "
                    f"couvre déjà — la compter deux fois serait compter deux "
                    f"fois la même dépense"
                ),
                "comptabilite_annuelle_euros": COMPTA,
                "comptabilite_commentaire": (
                    f"Comptabilité de la SCI à l'IS, {eur(COMPTA)} €/an : un "
                    f"logement loué nu au régime réel, avec amortissements, "
                    f"tableaux d'amortissement et liasse fiscale. C'est le coût "
                    f"du régime qui rend l'année 1 déficitaire et qui protège "
                    f"l'EBE de l'impôt"
                ),
                "provision_desactivee": True,
            },
        },
        "analyse": {
            "branche": "residentiel",
            "type_operation": "locatif",
            "strategie_retenue": {
                "nom": (
                    f"Location nue longue durée au prix de marché — loyer "
                    f"retenu {eur(LOYER_BASE)} €/mois ({fr(LOYER_M2_MED)} "
                    f"€/m²), sous conditions suspensives de pièces"
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
                        f"{fr(SBAS['rdt_av'])} % net avant IS sur l'acte en main "
                        f"({eur(SBAS['ebe'])} € d'EBE), {fr(SBAS['rdt_ap'])} % "
                        f"après IS sous convention prudente"
                    ),
                    "faisabilite": (
                        f"c'est le prix qu'un locataire de Brignoles acceptera "
                        f"de payer sans négocier pour un T3 de {eur(SURF)} m² "
                        f"sans ascenseur : le loyer s'ajuste, mais il s'ajuste "
                        f"vers le bas"
                    ),
                    "risque": (
                        f"{eur(SBAS['cf'])} €/mois de cash-flow avant IS et un "
                        f"plafond 5 % à {eur(SBAS['cap5'])} € : la lecture qui "
                        f"ne pardonnerait aucun imprévu de travaux"
                    ),
                },
                {
                    "strategie": (
                        f"Scénario de base — loyer de {eur(LOYER_BASE)} €/mois "
                        f"({fr(LOYER_M2_MED)} €/m²), ancrage Trackstone, "
                        f"charges de copropriété telles qu'annoncées "
                        f"({eur(COPRO_BASE)} €/an)"
                    ),
                    "lots": 1,
                    "rendement": (
                        f"{fr(SBASE['rdt_av'])} % net avant IS, "
                        f"{fr(SBASE['rdt_ap'])} % après IS, "
                        f"{fr(SBASE['rdt_valeur'])} % sur la valeur de marché"
                    ),
                    "faisabilite": (
                        f"la seule lecture que la doctrine du parc accepte de "
                        f"regarder en face : 48 m² en centre ancien de "
                        f"Brignoles se louent à ce niveau, et les charges "
                        f"annoncées le permettent"
                    ),
                    "risque": (
                        f"le rendement net avant IS reste à {fr(SBASE['rdt_av'])} "
                        f"% pour un seuil de parc à 6,5 % : "
                        f"{eur(SBASE['cf'])} €/mois de cash-flow avant IS au "
                        f"prix affiché, et il faudrait payer "
                        f"{eur(SBASE['cap5'])} € pour atteindre 5 % net"
                    ),
                },
                {
                    "strategie": (
                        f"Haut de marché — loyer de {eur(LOYER_HAUT)} €/mois "
                        f"({fr(LOYER_M2_HAUT)} €/m²), ancrage SeLoger ville"
                    ),
                    "lots": 1,
                    "rendement": (
                        f"{fr(SHAUT['rdt_av'])} % net avant IS ({eur(SHAUT['ebe'])} "
                        f"€ d'EBE), {fr(SHAUT['rdt_ap'])} % après IS"
                    ),
                    "faisabilite": (
                        f"tenable seulement si le bien est remis en état et "
                        f"reloué à un ménage venant de l'extérieur : c'est le "
                        f"haut de la fourchette constatée, pas la moyenne"
                    ),
                    "risque": (
                        f"même à {eur(LOYER_HAUT)} €/mois la trésorerie reste "
                        f"négative ({eur(SHAUT['cf'])} €/mois avant IS) : "
                        f"l'écart au seuil n'est pas un problème de loyer"
                    ),
                },
                {
                    "strategie": (
                        f"Variante de risque — loyer de base "
                        f"({eur(LOYER_BASE)} €/mois) et charges de copropriété "
                        f"doublées à {eur(COPRO_HAUT)} €/an, ce qu'un budget "
                        f"mal provisionné produit en deux ans"
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
                        f"de {eur(SURF)} m² n'est pas une hypothèse de "
                        f"catastrophe, c'est une hypothèse de copropriété de "
                        f"6 lots"
                    ),
                    "risque": (
                        f"chaque euro de charge annuelle en plus retire "
                        f"{eur(1 / 0.054)} € de prix acceptable : le plafond "
                        f"5 % tombe de {eur(SBASE['cap5'])} € à "
                        f"{eur(SCOPRO['cap5'])} €, soit "
                        f"{fr((SBASE['cap5'] - SCOPRO['cap5']) / SBASE['cap5'] * 100, 1)} % "
                        f"de prix en moins pour la même exigence de rendement"
                    ),
                },
                {
                    "strategie": (
                        f"Piste étudiée et écartée — colocation meublée à deux "
                        f"chambres, {eur(COLOC_BAS)} à {eur(COLOC_HAUT)} € par "
                        f"chambre et par mois"
                    ),
                    "lots": 1,
                    "rendement": (
                        f"{fr(C420['rdt_ap'])} à {fr(C450['rdt_ap'])} % net après "
                        f"IS, {eur(C420['ebe'])} à {eur(C450['ebe'])} € d'EBE"
                    ),
                    "faisabilite": (
                        f"c'est la seule lecture qui franchit le seuil du parc — "
                        f"mais elle suppose de meubler deux chambres, un "
                        f"règlement de copropriété qui l'autorise, et un marché "
                        f"de la colocation qui n'existe pas à Brignoles (aucune "
                        f"demande étudiante structurelle) ; la mezzanine hors "
                        f"Carrez ne se loue pas comme une chambre"
                    ),
                    "risque": (
                        f"un bail meublé sur un T3 de {eur(SURF)} m² en centre "
                        f"ancien se reloue mal et se vide vite : c'est la "
                        f"stratégie qui transforme un revenu modeste mais "
                        f"certain en revenu élevé mais discontinu, sur un bien "
                        f"déjà atypique"
                    ),
                },
            ],
            "attractivite": [
                {
                    "dimension": "transports",
                    "score": 6,
                    "justification": (
                        f"Brignoles est une sous-préfecture du Var reliée par "
                        f"l'A8 et la D554, avec une gare sur la ligne "
                        f"Carnoules-Gardanne et un réseau de bus urbain : on "
                        f"rejoint Toulon et Aix par la route, pas par un train "
                        f"cadencé. Pour un T3 de centre ancien, c'est suffisant "
                        f"— la cible est locale — mais ce n'est pas un "
                        f"emplacement de navetteur pendulaire, et cela plafonne "
                        f"la demande extérieure"
                    ),
                },
                {
                    "dimension": "commerces",
                    "score": 7,
                    "justification": (
                        f"Centre Vieille Ville commerçant : boutiques, marchés, "
                        f"services publics et professions de santé à pied, "
                        f"hypermarchés en périphérie. C'est le point fort "
                        f"objectif de l'emplacement, et c'est ce qui fait qu'un "
                        f"T3 de {eur(SURF)} m² se reloue ici à "
                        f"{fr(LOYER_M2_MED)} €/m² sans miracle commercial"
                    ),
                },
                {
                    "dimension": "ecoles",
                    "score": 7,
                    "justification": (
                        f"Brignoles concentre les établissements de la "
                        f"couronne (écoles, collèges, lycée Raynouard, "
                        f"formations post-bac) à quelques minutes à pied du "
                        f"centre ancien : la ville est un pôle scolaire local, "
                        f"ce qui soutient la demande de logements familiaux et "
                        f"de petites surfaces"
                    ),
                },
                {
                    "dimension": "securite",
                    "score": 6,
                    "justification": (
                        f"Aucune tension spécifique documentée sur le quartier "
                        f"dans les sources consultées, et aucun élément de "
                        f"l'annonce ne signale de désordre. Réserve de méthode : "
                        f"un bâti ancien très dense et des parties communes "
                        f"d'immeuble de {ANNEE} demandent des portes et une "
                        f"serrurerie en état — poste à vérifier lors de la "
                        f"visite, pas à supposer"
                    ),
                },
                {
                    "dimension": "demande_locative",
                    "score": 6,
                    "justification": (
                        f"Trois ancrages datés donnent un loyer de "
                        f"{eur(LOYER_BAS)} à {eur(LOYER_HAUT)} €/mois pour "
                        f"{eur(SURF)} m², et les annonces réelles du secteur "
                        f"confirment (70 m² à 786 €/mois, 70 m² à 855 € charges "
                        f"comprises). La demande existe, mais elle n'est ni "
                        f"tendue ni étudiante : seuls {CHAMBRES} chambres pour "
                        f"3 pièces, une mezzanine hors Carrez comme troisième "
                        f"espace, pas d'ascenseur. Un T3 de centre ancien se "
                        f"reloue, il ne s'arrache pas"
                    ),
                },
                {
                    "dimension": "dynamisme",
                    "score": 5,
                    "justification": (
                        f"Marché de sous-préfecture : "
                        f"{DVF_APP_N} ventes d'appartements en 2025 à l'échelle "
                        f"communale et {DVF_Q_APP_N} dans la boîte du centre "
                        f"ancien, avec un prix médian de l'ancien autour de "
                        f"2 500 €/m² et une progression annuelle faible. Les "
                        f"prix montent moins vite que l'inflation : dans ce "
                        f"dossier le rendement locatif est le seul moteur de "
                        f"performance, la plus-value n'en est pas un"
                    ),
                },
            ],
            "risques": [
                {
                    "facteur": (
                        "Procédure de copropriété en cours (art. L. 721-1 du "
                        "code de la construction et de l'habitation) sans aucun "
                        "document communiqué"
                    ),
                    "severite": 4,
                    "bloquant": False,
                    "detail": (
                        f"L'annonce déclare elle-même que « le syndicat des "
                        f"copropriétaires fait l'objet d'une procédure citée à "
                        f"l'article L. 721-1 ». Ce que la mention ne dit pas : "
                        f"l'objet de la procédure, les travaux votés et non "
                        f"payés, l'existence d'un emprunt de copropriété, le "
                        f"montant des impayés et le budget prévisionnel réel. "
                        f"Sur une copropriété de {LOTS_COPRO} lots, un seul "
                        f"copropriétaire défaillant pèse jusqu'à un sixième des "
                        f"charges — et les appels de fonds exceptionnels "
                        f"tombent sur les copropriétaires solvables, c'est-à-dire "
                        f"sur l'acheteur. Ce risque n'est pas encore bloquant "
                        f"parce qu'il n'est pas quantifié : il le devient "
                        f"dès que l'état daté et les trois derniers "
                        f"procès-verbaux le chiffrent. Condition suspensive "
                        f"obligatoire"
                    ),
                },
                {
                    "facteur": (
                        "Le prix bas est le prix du risque : rien ne prouve que "
                        "la décote de "
                        f"{fr(abs((PRIX / SURF - DVF_Q_4560_MED) / DVF_Q_4560_MED * 100), 1)} % "
                        "soit suffisante"
                    ),
                    "severite": 4,
                    "bloquant": False,
                    "detail": (
                        f"À {eur(PRIX / SURF)} €/m², le bien est sous les "
                        f"{DVF_Q_4560_N} ventes de sa tranche dans le centre "
                        f"ancien (médiane {eur(DVF_Q_4560_MED)} €/m²). Sur un "
                        f"marché où cette décote n'existe pas par accident, elle "
                        f"paie quelque chose : procédure, ascenseur absent, "
                        f"mezzanine comptée dans le gabarit. La vraie question "
                        f"n'est pas « est-ce moins cher que le quartier ? » "
                        f"mais « est-ce assez moins cher pour absorber le "
                        f"travaux et les charges qui viennent ? ». Si la "
                        f"copropriété annonce 20 000 € d'appels de fonds au "
                        f"nom du lot, la décote est intégralement consommée"
                    ),
                },
                {
                    "facteur": (
                        "Rendement structurellement sous le seuil du parc : "
                        f"{fr(SBASE['rdt_av'])} % net avant IS pour 6,5 % visés"
                    ),
                    "severite": 3,
                    "bloquant": False,
                    "detail": (
                        f"Au loyer médian de marché ({eur(LOYER_BASE)} €/mois) et "
                        f"avec les charges annoncées, l'affaire dégage "
                        f"{eur(SBASE['ebe'])} € d'EBE, soit "
                        f"{fr(SBASE['rdt_av'])} % net avant IS sur l'acte en "
                        f"main — et {fr(SHAUT['rdt_av'])} % seulement en montant "
                        f"au haut de la fourchette de loyer. Le seuil de parc "
                        f"est 6,5 % net d'IS : il faudrait payer "
                        f"{eur(plafond_is(SBASE['ebe'], 0.065))} € (soit "
                        f"{fr((PRIX - plafond_is(SBASE['ebe'], 0.065)) / PRIX * 100, 1)} % "
                        f"de moins) pour "
                        f"l'atteindre. Ce n'est pas un mauvais dossier, c'est un "
                        f"dossier qui ne s'achète pas pour son rendement"
                    ),
                },
                {
                    "facteur": (
                        f"Mezzanine hors Carrez et T3 de {eur(SURF)} m² : "
                        f"gabarit atypique, surface utile surestimée"
                    ),
                    "severite": 3,
                    "bloquant": False,
                    "detail": (
                        f"L'annonce vend un T3 de {eur(SURF)} m² et décrit un "
                        f"« espace supplémentaire » en mezzanine : cette surface "
                        f"n'est pas comptée dans le Carrez, ne se loue pas comme "
                        f"une pièce habitable et ne se revend pas au prix du m². "
                        f"Le prix au m² affiché ({eur(PRIX / SURF)} €) est donc "
                        f"plutôt un prix haut de gamme du gabarit réel : ramenée "
                        f"à une surface utile de 55 m², l'opération ressort à "
                        f"{eur(PRIX / 55)} €/m². Faire trancher par le certificat "
                        f"Carrez et par le règlement de copropriété "
                        f"(mezzanine déclarée en surface habitable ou non)"
                    ),
                },
                {
                    "facteur": (
                        f"Immeuble de {ANNEE}, 2e étage sans ascenseur, DPE "
                        f"{DPE} : cible locative et acheteurs réduits"
                    ),
                    "severite": 3,
                    "bloquant": False,
                    "detail": (
                        f"DPE {DPE} et GES {GES} avec une facture annoncée de "
                        f"{eur(FACTURE_BASSE)} à {eur(FACTURE_HAUTE)} € — ce "
                        f"n'est pas une passoire thermique et le bien reste "
                        f"louable, mais la trajectoire réglementaire et la perte "
                        f"de pouvoir d'achat des locataires pèsent sur le loyer "
                        f"négociable. Un 2e étage sans ascenseur retire les "
                        f"locataires âgés ou chargés d'enfants en bas âge, et "
                        f"réduit la cible à la revente. À Brignoles, où le centre "
                        f"ancien est bâti en hauteur, c'est une contrainte "
                        f"durable, pas un détail"
                    ),
                },
                {
                    "facteur": (
                        "Travaux non chiffrés et estimation d'exploitation non "
                        "vérifiable (taxe foncière, charges futures)"
                    ),
                    "severite": 2,
                    "bloquant": False,
                    "detail": (
                        f"Trois chiffres du modèle sont des ESTIMATIONS, dites "
                        f"explicitement : la taxe foncière ({eur(TF_BASE)} €/an, "
                        f"avis non communiqué), la provision de travaux "
                        f"({eur(PROV_BASE)} €/an) et l'enveloppe de "
                        f"rafraîchissement (publiée en grille de 10 000 à "
                        f"30 000 €). Seules les charges de copropriété "
                        f"({eur(COPRO_BASE)} €/an) sont annoncées. Ce n'est pas "
                        f"un risque de perte sèche, c'est un risque de "
                        f"précision : demander l'avis de taxe foncière, le "
                        f"dernier appel de charges et un devis de rafraîchissement "
                        f"avant toute offre"
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
    # 2. Le record et les controles du modele
    # ------------------------------------------------------------------
    rec_ = rec_t3()
    MPE = mensualite_par_euro()
    calcule("mensualite par euro emprunte", MENS_PAR_EURO_MODELE, MPE, 0.00001)
    calcule("mensualite pour 75 600 EUR empruntes", MENS_MODELE,
            mensualite(CAPITAL), 1.0)
    calcule("capital emprunte (90 % du prix affiche)", CAPITAL,
            PRIX * (1 - APPORT_PCT), 0.5)
    calcule("frais d'acquisition du simulateur (8 %)", FRAIS_ACQUISITION,
            PRIX * 0.08, 0.5)
    calcule("acte en main (84 000 + 6 720)", ACTE_EN_MAIN, PRIX * 1.08, 1.0)
    calcule("taux de frais", 8.00, TAUX_FRAIS * 100.0, 0.01)
    calcule("prix au m2 sur 48 m2 annonces", 1750.0, PRIX / SURF, 0.5)
    calcule("prix au m2 si la mezzanine porte la surface utile a 55 m2", 1527.0,
            PRIX / 55.0, 0.5)
    calcule("loyer de marche retenu en EUR/m2/mois", 12.00, LOYER_M2_MED, 0.01)
    calcule("loyer de marche retenu mensuel (12,0 x 48)", 576.0, LOYER_BASE, 0.5)
    calcule("loyer plancher (11,0 x 48)", 528.0, LOYER_BAS, 0.5)
    calcule("loyer haut (13,0 x 48)", 624.0, LOYER_HAUT, 0.5)
    calcule("loyer annuel brut (576 x 12)", 6912.0, revenus_annuels(LOYER_BASE),
            0.5)
    calcule("loyer de reference interne (11,0 x 48)", 528.0,
            SURF * LOYER_REF_M2, 0.5)
    calcule("Trackstone (12,0 x 48)", 576.0, SURF * LOYER_M2_MED, 0.5)
    calcule("SeLoger ville (13,0 x 48)", 624.0, SURF * LOYER_M2_HAUT, 0.5)

    S1 = dict(
        bas=scen(rec_, LOYER_BAS, VAC_BASE, GESTION_BASE_PCT, TF_BASE,
                 COPRO_BASE, PROV_BASE),
        base=scen(rec_, LOYER_BASE, VAC_BASE, GESTION_BASE_PCT, TF_BASE,
                  COPRO_BASE, PROV_BASE),
        haut=scen(rec_, LOYER_HAUT, VAC_BASE, GESTION_BASE_PCT, TF_BASE,
                  COPRO_BASE, PROV_BASE),
        copro=scen(rec_, LOYER_BASE, VAC_BASE, GESTION_BASE_PCT, TF_BASE,
                   COPRO_HAUT, PROV_BASE),
        best=scen(rec_, LOYER_BASE, VAC_BEST, 4.0, TF_BASE, COPRO_BASE, 150.0),
        worst=scen(rec_, LOYER_BASE, VAC_WORST, GESTION_BASE_PCT, 1100.0,
                   COPRO_HAUT, 400.0),
    )
    SBAS, SBASE = S1['bas'], S1['base']
    SHAUT, SCOPRO = S1['haut'], S1['copro']
    SBEST, SWORST = S1['best'], S1['worst']
    C420M = coloc_n(rec_, COLOC_BAS, 2)
    C450M = coloc_n(rec_, COLOC_HAUT, 2)

    # --- la formule publiee contre le moteur, ligne a ligne ---------------
    for lbl, h, s in (("bas", hypo(LOYER_BAS), SBAS),
                      ("base", hypo(LOYER_BASE), SBASE),
                      ("haut", hypo(LOYER_HAUT), SHAUT),
                      ("copro doublee", hypo(LOYER_BASE, copro=COPRO_HAUT),
                       SCOPRO),
                      ("favorable", hypo(LOYER_BASE, vac=VAC_BEST, gestion=4.0),
                       SBEST),
                      ("defavorable", hypo(LOYER_BASE, vac=VAC_WORST,
                                           tf=1100.0, copro=COPRO_HAUT,
                                           prov=400.0), SWORST)):
        calcule(f"formule vs moteur : EBE {lbl}", h['ebe'], s['ebe'], 0.05)
        calcule(f"formule vs moteur : net apres IS {lbl}", h['net'], s['net'],
                0.05)
        calcule(f"formule vs moteur : cash-flow {lbl}", h['cf'], s['cf'], 0.05)
    calcule("colocation 2 chambres a 420 EUR : EBE", C420M['ebe'],
            hypo(2.0 * COLOC_BAS)['ebe'], 0.5)
    calcule("colocation 2 chambres a 450 EUR : EBE", C450M['ebe'],
            hypo(2.0 * COLOC_HAUT)['ebe'], 0.5)

    # --- compte d'exploitation du scenario de base, chiffre par chiffre ---
    calcule("EBE de base (6 912 x 0,95 - 345,6 - 1 990)", 4230.80,
            SBASE['ebe'], 1.0)
    calcule("EBE de base restitue par le moteur", SBASE['ebe'],
            SBASE['ebe_modele'], 0.05)
    calcule("vacance du scenario de base (5 % de 6 912)", 345.60,
            SBASE['vac_eur'], 0.5)
    calcule("gestion locative du scenario de base (5 % de 6 912)", 345.60,
            SBASE['gestion_eur'], 0.5)
    calcule("poste entretien (gestion 345,60 + provision 150)", 495.60,
            SBASE['entretien'], 0.5)
    calcule("charges fixes (TF 800 + copro 540 + PNO 100 + compta 400 + "
            "provision 150)", 1990.0, charges_fixes(TF_BASE, COPRO_BASE,
                                                    PROV_BASE), 0.5)
    calcule("charges fixes, copro doublee", 2530.0,
            charges_fixes(TF_BASE, COPRO_HAUT, PROV_BASE), 0.5)
    calcule("EBE plancher de loyer (528 EUR)", 3712.40, SBAS['ebe'], 1.0)
    calcule("EBE haut de loyer (624 EUR)", 4749.20, SHAUT['ebe'], 1.0)
    calcule("EBE copro doublee (576 EUR)", 3690.80, SCOPRO['ebe'], 1.0)
    calcule("EBE hypothese favorable", 4438.16, SBEST['ebe'], 1.0)
    calcule("EBE hypothese defavorable", 2795.20, SWORST['ebe'], 1.0)
    calcule("poids des charges annoncees (540 / 6 912)", 7.81,
            COPRO_BASE / (LOYER_BASE * 12) * 100.0, 0.05)

    # --- rendements, plafonds, cash-flow publies --------------------------
    calcule("rendement net avant IS au loyer de base", 4.66, SBASE['rdt_av'],
            0.01)
    calcule("rendement net apres IS au loyer de base", 3.96, SBASE['rdt_ap'],
            0.01)
    calcule("rendement net sur valeur au loyer de base", 3.69,
            SBASE['rdt_valeur'], 0.01)
    calcule("rendement brut au loyer de base", 8.23, SBASE['rdt_brut'], 0.01)
    calcule("rendement net avant IS au loyer plancher", 4.09, SBAS['rdt_av'],
            0.01)
    calcule("rendement net apres IS au loyer plancher", 3.48, SBAS['rdt_ap'],
            0.01)
    calcule("rendement net avant IS au loyer haut", 5.24, SHAUT['rdt_av'], 0.01)
    calcule("rendement net apres IS au loyer haut", 4.45, SHAUT['rdt_ap'], 0.01)
    calcule("rendement net avant IS avec copro doublee", 4.07, SCOPRO['rdt_av'],
            0.01)
    calcule("rendement net apres IS avec copro doublee", 3.46, SCOPRO['rdt_ap'],
            0.01)
    calcule("rendement net avant IS en hypothese favorable", 4.89,
            SBEST['rdt_av'], 0.01)
    calcule("rendement net avant IS en hypothese defavorable", 3.08,
            SWORST['rdt_av'], 0.01)
    calcule("IS convention prudente au loyer de base (15 % de l'EBE)", 634.62,
            SBASE['is_'], 1.0)
    calcule("net apres IS au loyer de base", 3596.18, SBASE['net'], 1.0)
    calcule("plafond 5 % net au loyer de base", 78348.0, SBASE['cap5'], 5.0)
    calcule("plafond 5 % net au loyer plancher", 68748.0, SBAS['cap5'], 5.0)
    calcule("plafond 5 % net au loyer haut", 87948.0, SHAUT['cap5'], 5.0)
    calcule("plafond 5 % net avec copro doublee", 68348.0, SCOPRO['cap5'], 5.0)
    calcule("decote de prix pour 5 % net au loyer de base", 6.73,
            (PRIX - SBASE['cap5']) / PRIX * 100.0, 0.05)
    calcule("plafond 6,5 % net d'IS au loyer de base", 60268.0,
            plafond_is(SBASE['ebe'], 0.065), 5.0)
    calcule("decote de prix pour 6,5 % net d'IS", 28.25,
            (PRIX - plafond_is(SBASE['ebe'], 0.065)) / PRIX * 100.0, 0.05)
    calcule("cash-flow mensuel au loyer de base (avant IS)", -216.70,
            SBASE['cf'], 1.0)
    calcule("cash-flow mensuel au loyer de base (apres IS)", -269.60,
            SBASE['cf_ap'], 1.0)
    calcule("cash-flow mensuel au loyer plancher", -259.90, SBAS['cf'], 1.0)
    calcule("cash-flow mensuel au loyer haut", -173.50, SHAUT['cf'], 1.0)
    calcule("cash-flow mensuel avec copro doublee", -261.70, SCOPRO['cf'], 1.0)
    calcule("cash-flow mensuel en hypothese favorable", -199.80, SBEST['cf'],
            1.0)
    calcule("cash-flow mensuel en hypothese defavorable", -336.37, SWORST['cf'],
            1.0)
    # --- colocation (piste ecartee) ---------------------------------------
    calcule("colocation 2 chambres a 420 EUR : revenus bruts", 10080.0,
            C420M['revenus'], 1.0)
    calcule("colocation 2 chambres a 420 EUR : EBE", 7082.0, C420M['ebe'], 1.0)
    calcule("colocation 2 chambres a 420 EUR : rendement net apres IS", 6.64,
            C420M['rdt_ap'], 0.02)
    calcule("colocation 2 chambres a 420 EUR : cash-flow avant IS", 20.87,
            C420M['cf'], 1.0)
    calcule("colocation 2 chambres a 450 EUR : revenus bruts", 10800.0,
            C450M['revenus'], 1.0)
    calcule("colocation 2 chambres a 450 EUR : EBE", 7730.0, C450M['ebe'], 1.0)
    calcule("colocation 2 chambres a 450 EUR : rendement net apres IS", 7.24,
            C450M['rdt_ap'], 0.02)
    calcule("colocation 2 chambres a 450 EUR : cash-flow avant IS", 74.87,
            C450M['cf'], 1.0)
    # --- points morts et plafonds inverses --------------------------------
    LOYER_CF_NUL = loyer_cashflow_nul(TF_BASE, COPRO_BASE, PROV_BASE)
    calcule("loyer mensuel pour un cash-flow nul au prix affiche", 816.80,
            LOYER_CF_NUL, 1.0)
    calcule("loyer mensuel pour un cash-flow nul en EUR/m2", 17.02,
            LOYER_CF_NUL / SURF, 0.05)
    calcule("rapport loyer exigé / loyer de marche", 1.42,
            LOYER_CF_NUL / LOYER_BASE, 0.01)
    calcule("prix a cash-flow nul au loyer de base", 52019.0,
            prix_cashflow_nul(SBASE['ebe']), 10.0)
    calcule("capital finançable a cash-flow nul = 90 % de ce prix", 46817.0,
            prix_cashflow_nul(SBASE['ebe']) * (1 - APPORT_PCT), 10.0)
    calcule("decote de prix pour un cash-flow nul", 38.07,
            (PRIX - prix_cashflow_nul(SBASE['ebe'])) / PRIX * 100.0, 0.05)
    calcule("apport pour un cash-flow nul au prix affiche", 37182.0,
            apport_cashflow_nul(PRIX, SBASE['ebe']), 10.0)
    calcule("apport pour un cash-flow nul, en % du prix", 44.26,
            apport_cashflow_nul(PRIX, SBASE['ebe']) / PRIX * 100.0, 0.1)
    calcule("plafond 5 % au loyer de base, 10 000 EUR de travaux", 69089.0,
            prix_5pct_avec_travaux(SBASE['ebe'], TRAVAUX_REF_1), 10.0)
    calcule("plafond 5 % au loyer de base, 20 000 EUR de travaux", 59830.0,
            prix_5pct_avec_travaux(SBASE['ebe'], TRAVAUX_REF_2), 10.0)
    calcule("plafond 5 % au loyer de base, 30 000 EUR de travaux", 50570.0,
            prix_5pct_avec_travaux(SBASE['ebe'], TRAVAUX_REF_3), 10.0)
    calcule("cout de revient avec 20 000 EUR de travaux", 110720.0,
            ACTE_EN_MAIN + TRAVAUX_REF_2, 0.5)
    calcule("marge de marchand de biens a la revente a la valeur du quartier",
            -18060.80, VALEUR_RETENUE * 0.95 - (ACTE_EN_MAIN + TRAVAUX_REF_2),
            1.0)
    # --- valeur, ancres et ecarts de prix ---------------------------------
    calcule("valeur retenue = 48 x 2 032 (mediane DVF du quartier 45-60 m2)",
            97536.0, SURF * DVF_Q_4560_MED, 10.0)
    calcule("valeur basse = 48 x 1 465 (Q1 du quartier)", 70320.0,
            SURF * DVF_Q_4560_Q1, 10.0)
    calcule("valeur haute = 48 x 2 295 (Q3 du quartier)", 110160.0,
            SURF * DVF_Q_4560_Q3, 10.0)
    calcule("valeur a la mediane communale 45-60 m2 = 48 x 2 109", 101232.0,
            VALEUR_COMMUNE, 10.0)
    calcule("valeur au prix moyen SeLoger du quartier = 48 x 1 953", 93744.0,
            VALEUR_SELOGER, 10.0)
    calcule("prix affiche / valeur retenue (le bien s'achete sous sa valeur)",
            0.8612, PRIX / VALEUR_RETENUE, 0.001)
    calcule("ratio cout / valeur (acte en main / valeur)", 0.9301,
            engine.ratio_cout_valeur(rec_), 0.001)
    calcule("ecart du prix demande a la mediane du quartier 45-60 m2", -13.88,
            (PRIX / SURF - DVF_Q_4560_MED) / DVF_Q_4560_MED * 100.0, 0.05)
    calcule("ecart du prix demande a la mediane communale 45-60 m2", -17.02,
            (PRIX / SURF - DVF_APP_4560_MED) / DVF_APP_4560_MED * 100.0, 0.05)
    calcule("ecart du prix demande au Q1 du quartier", 19.45,
            (PRIX / SURF - DVF_Q_4560_Q1) / DVF_Q_4560_Q1 * 100.0, 0.05)
    calcule("ecart du prix demande aux comparables", -4.06,
            (PRIX / SURF - DVF_CMP_MED) / DVF_CMP_MED * 100.0, 0.05)
    calcule("decote du quartier sous la mediane communale toutes surfaces",
            7.35, (1 - DVF_Q_MED / DVF_APP_MED) * 100.0, 0.05)
    calcule("decote du quartier a tranche de surface comparable", 3.65,
            (1 - DVF_Q_4560_MED / DVF_APP_4560_MED) * 100.0, 0.05)
    calcule("prix affiche au plafond patrimonial 6,5 % (x fois)", 1.71,
            (PRIX / SURF) / PLAF_PATRIMONIAL[0], 0.01)
    calcule("prix affiche au plafond marchand de biens (x fois)", 3.14,
            (PRIX / SURF) / PLAF_MDB[0], 0.01)
    # --- fiscalite de l'annee 1 -------------------------------------------
    calcule("fiscalite annee 1 : interets (75 600 a 3,7 %)", 2797.20,
            INTERETS_AN1, 1.0)
    calcule("fiscalite annee 1 : dotation (bati 80 % du prix sur 30 ans)",
            2240.00, DOTATION_AN1, 1.0)
    calcule("fiscalite annee 1 : resultat imposable", -806.40,
            SBASE['ebe'] - INTERETS_AN1 - DOTATION_AN1, 1.0)
    assert SBASE['ebe'] - INTERETS_AN1 - DOTATION_AN1 < 0, \
        "annee 1 benefique : la fiscalite publiee serait fausse"
    calcule("IS annee 1 (resultat negatif, donc zero)", 0.0,
            max(0.0, 0.15 * (SBASE['ebe'] - INTERETS_AN1 - DOTATION_AN1)), 0.0)

    # ------------------------------------------------------------------
    # 3. Note et verdict
    # ------------------------------------------------------------------
    r = engine.compute(rec_)
    assert r['calculable'], r.get('raison')
    note, verdict, comp = scoring.note_et_verdict(rec_, r)
    print(f"  note {note} / 10 → verdict {verdict}  composantes {comp}")
    assert note is not None, comp
    assert note == 6.1, note
    assert verdict == "negocier", verdict
    assert not comp.get("bloquant"), comp

    # ------------------------------------------------------------------
    # 4. Sections de la fiche
    # ------------------------------------------------------------------
    def td(v, cls=""):
        c = f' class="{cls}"' if cls else ''
        return f"<td{c}>{v}</td>"

    proj_section = f"""  <section class="financial-projections">
    <h2>Compte d'exploitation au loyer de marché</h2>
    <p class="attractiveness-intro">Le bien est <strong>libre</strong> : aucun bail à hériter, donc aucun revenu acquis et aucun risque de sous-loyer. Le loyer est une hypothèse que l'on choisit, et le modèle en publie trois : le plancher de la fiche de référence ({eur(LOYER_BAS)} €/mois), le scénario de base au loyer médian ({eur(LOYER_BASE)} €/mois) et le haut de la fourchette observée ({eur(LOYER_HAUT)} €/mois). Tout le reste — charges de copropriété annoncées, taxe foncière estimée, provision, comptabilité de SCI — est identique dans les trois colonnes.</p>
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
        <tr><td>Rendement net après IS / valeur de marché</td><td class="num">{fr(SBAS['net'] / VALEUR_RETENUE * 100, 2)} %</td><td class="num">{fr(SBASE['rdt_valeur'])} %</td><td class="num">{fr(SHAUT['net'] / VALEUR_RETENUE * 100, 2)} %</td></tr>
      </tbody>
    </table>
    <h3>Service de la dette : {eur(CAPITAL)} € empruntés sur {DUREE_ANS} ans à {fr(TAUX_CREDIT * 100)} % + assurance {fr(ASSURANCE_PCT * 100)} %</h3>
    <p class="attractiveness-intro">Mensualité <strong>{eur(mensualite(CAPITAL))} €</strong>, soit {fr(MENS_PAR_EURO_MODELE * 100, 3)} % du capital emprunté par mois. L'apport est de {APPORT_PCT * 100:.0f} % — les frais d'acquisition ({eur(FRAIS_ACQUISITION)} €) restent à financer en plus, comme sur les autres dossiers du parc.</p>
    <table class="projection-table compare">
      <thead><tr><th>Trésorerie mensuelle</th><th class="num">Favorable</th><th class="num">Base</th><th class="num">Défavorable</th></tr></thead>
      <tbody>
        <tr><td>Loyer retenu</td><td class="num">{eur(SBEST['loyer'])}</td><td class="num">{eur(SBASE['loyer'])}</td><td class="num">{eur(SWORST['loyer'])}</td></tr>
        <tr><td>Vacance</td><td class="num">{fr(SBEST['vac'])} %</td><td class="num">{fr(SBASE['vac'])} %</td><td class="num">{fr(SWORST['vac'])} %</td></tr>
        <tr><td>Charges de copropriété</td><td class="num">{eur(COPRO_BASE)}/an</td><td class="num">{eur(COPRO_BASE)}/an</td><td class="num">{eur(COPRO_HAUT)}/an</td></tr>
        <tr><td>Taxe foncière</td><td class="num">{eur(TF_BASE)}/an</td><td class="num">{eur(TF_BASE)}/an</td><td class="num">1 100 €/an</td></tr>
        <tr><td>EBE mensuel</td><td class="num">{eur(SBEST['ebe_mois'], 2)}</td><td class="num">{eur(SBASE['ebe_mois'], 2)}</td><td class="num">{eur(SWORST['ebe_mois'], 2)}</td></tr>
        <tr><td>Mensualité de crédit</td><td class="num">−{eur(mensualite(CAPITAL))}</td><td class="num">−{eur(mensualite(CAPITAL))}</td><td class="num">−{eur(mensualite(CAPITAL))}</td></tr>
        <tr class="highlight"><td><strong>Cash-flow avant IS</strong></td><td class="num"><strong>{eur(SBEST['cf'])}</strong></td><td class="num"><strong>{eur(SBASE['cf'])}</strong></td><td class="num"><strong>{eur(SWORST['cf'])}</strong></td></tr>
        <tr><td>Cash-flow après IS (convention prudente)</td><td class="num">{eur(SBEST['cf_ap'])}</td><td class="num">{eur(SBASE['cf_ap'])}</td><td class="num">{eur(SWORST['cf_ap'])}</td></tr>
        <tr><td>Rendement net avant IS</td><td class="num">{fr(SBEST['rdt_av'])} %</td><td class="num">{fr(SBASE['rdt_av'])} %</td><td class="num">{fr(SWORST['rdt_av'])} %</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Sur la piste minorante, le rendement net avant IS est de {fr(SBASE['rdt_av'])} % et le plafond à 5 % net s'établit à {eur(SBASE['cap5'])} €.</strong> C'est {fr((PRIX - SBASE['cap5']) / PRIX * 100, 1)} % sous le prix affiché. Autrement dit : <strong>le prix demandé n'est pas le problème du dossier, c'est le loyer qu'il finance</strong> — {eur(SBASE['brut'])} € annuels pour {eur(ACTE_EN_MAIN)} € d'acte en main, sur un bien dont la troisième pièce utile est une mezzanine hors Carrez.</p>
    </div>
  </section>"""

    loyer_section = f"""  <section class="financial-projections">
    <h2>Le loyer : quatre ancrages, une seule fourchette</h2>
    <table class="projection-table compare">
      <thead><tr><th>Source datée ({DATE_FR})</th><th class="num">€/m²/mois</th><th class="num">Pour 48 m²</th><th>Nature</th></tr></thead>
      <tbody>
        <tr><td>Fiche de référence interne (21/09/2026, lot type 60 m²)</td><td class="num">{fr(LOYER_REF_M2)}</td><td class="num">{eur(SURF * LOYER_REF_M2)}</td><td>plancher de la doctrine du parc</td></tr>
        <tr><td>Trackstone, appartements Brignoles (8,1 à 18,1 €/m²)</td><td class="num">{fr(LOYER_M2_MED)}</td><td class="num">{eur(SURF * LOYER_M2_MED)}</td><td>loyer moyen constaté</td></tr>
        <tr class="highlight"><td><strong>SeLoger, estimation de location, ville de Brignoles (9 à 20 €/m²)</strong></td><td class="num"><strong>{fr(LOYER_M2_HAUT)}</strong></td><td class="num"><strong>{eur(SURF * LOYER_M2_HAUT)}</strong></td><td>haut de la fourchette</td></tr>
        <tr><td>Annonces réelles du secteur : 70 m² à 786 €/mois</td><td class="num">11,23</td><td class="num">539</td><td>surface supérieure, prix au m² plus bas</td></tr>
        <tr><td>Annonces réelles du secteur : 70 m² à 855 €/mois charges comprises</td><td class="num">12,21</td><td class="num">586</td><td>charges comprises</td></tr>
        <tr><td>RealAdvisor : loyer médian d'un appartement (toutes surfaces)</td><td class="num">—</td><td class="num">{eur(REALADVISOR_MED)}</td><td>toutes surfaces, donc non comparable</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>La fourchette retenue est {eur(LOYER_BAS)} à {eur(LOYER_HAUT)} €/mois hors charges, et le scénario de base s'établit à {eur(LOYER_BASE)} €/mois.</strong> Attention à un piège de lecture : {eur(REALADVISOR_MED)} € de loyer médian et {eur(LOYER_HAUT)} €/m² pour 48 m² ne disent pas la même chose — le premier chiffre porte sur des surfaces bien plus grandes. Ce qui compte pour un T3 de {eur(SURF)} m² sans ascenseur, c'est la borne basse tenue par la doctrine du parc ({eur(SURF * LOYER_REF_M2)} €) : c'est le loyer qu'il faut savoir encaisser sans casser la trésorerie.</p>
    </div>
  </section>"""

    dvf_cmp_rows = "\n".join(
        "        <tr><td>{}</td><td>{}</td><td class=\"num\">{}</td><td class=\"num\">{}</td><td class=\"num\">{}</td><td class=\"num\">{}</td></tr>".format(
            c['date'], c['voie'], eur(c['surf'], 0), eur(c['prix']), eur(c['m2']),
            c['lots']) for c in DVF_COMPARABLES)

    dvf_section = f"""  <section class="financial-projections">
    <h2>Analyse de prix : la valeur du bien en DVF 2025</h2>
    <p class="attractiveness-intro">Méthode : mutations de nature « Vente » de 2025 dans la commune de Brignoles (INSEE {DVF_COMMUNE}), valeur foncière de la mutation divisée par la somme des surfaces bâties, surfaces supérieures à 5 m² et valeurs supérieures à 5 000 €. Le quartier est délimité par la boîte de coordonnées du centre ancien ({DVF_BOITE[0]} à {DVF_BOITE[1]} N, {DVF_BOITE[2]} à {DVF_BOITE[3]} E), parce qu'à Brignoles la géographie du prix compte plus que la moyenne communale.</p>
    <table class="projection-table compare">
      <thead><tr><th>Population de référence (DVF 2025)</th><th class="num">Ventes</th><th class="num">Médiane €/m²</th><th class="num">Q1</th><th class="num">Q3</th><th class="num">Prix médian</th><th class="num">Valeur de 48 m²</th></tr></thead>
      <tbody>
        <tr class="highlight"><td><strong>Quartier Centre Vieille Ville, 45 à 60 m² — l'ancre retenue</strong></td><td class="num"><strong>{DVF_Q_4560_N}</strong></td><td class="num"><strong>{eur(DVF_Q_4560_MED)}</strong></td><td class="num"><strong>{eur(DVF_Q_4560_Q1)}</strong></td><td class="num"><strong>{eur(DVF_Q_4560_Q3)}</strong></td><td class="num"><strong>{eur(DVF_Q_4560_PRIX)}</strong></td><td class="num"><strong>{eur(VALEUR_RETENUE)}</strong></td></tr>
        <tr><td>Commune de Brignoles, 45 à 60 m²</td><td class="num">{DVF_APP_4560_N}</td><td class="num">{eur(DVF_APP_4560_MED)}</td><td class="num">{eur(DVF_APP_4560_Q1)}</td><td class="num">{eur(DVF_APP_4560_Q3)}</td><td class="num">{eur(DVF_APP_4560_PRIX)}</td><td class="num">{eur(VALEUR_COMMUNE)}</td></tr>
        <tr><td>Quartier Centre Vieille Ville, toutes surfaces</td><td class="num">{DVF_Q_APP_N}</td><td class="num">{eur(DVF_Q_MED)}</td><td class="num">—</td><td class="num">—</td><td class="num">—</td><td class="num">—</td></tr>
        <tr><td>Commune de Brignoles, toutes surfaces</td><td class="num">{DVF_APP_N}</td><td class="num">{eur(DVF_APP_MED)}</td><td class="num">—</td><td class="num">—</td><td class="num">—</td><td class="num">—</td></tr>
        <tr><td>Repère externe : prix moyen SeLoger du quartier (bornes 1 465 à 2 930)</td><td class="num">—</td><td class="num">1 953</td><td class="num">—</td><td class="num">—</td><td class="num">—</td><td class="num">{eur(VALEUR_SELOGER)}</td></tr>
      </tbody>
    </table>
    <h3>Les six transactions qui encadrent le bien</h3>
    <p class="attractiveness-intro">Appartements seuls vendus dans le centre ancien en 2025, de 45 à 56 m² — la population la plus proche du bien. Le prix demandé, 1 750 €/m², se place <strong>{fr(abs((PRIX / SURF - DVF_CMP_MED) / DVF_CMP_MED * 100), 1)} % sous leur médiane</strong> ({eur(DVF_CMP_MED)} €/m²) et <strong>{fr(abs((PRIX - DVF_CMP_PRIX) / DVF_CMP_PRIX * 100), 1)} % sous leur prix médian absolu</strong> ({eur(DVF_CMP_PRIX)} € pour les transactions comparables, contre {eur(PRIX)} € demandés).</p>
    <table class="projection-table compare">
      <thead><tr><th>Date</th><th>Voie</th><th class="num">Surface</th><th class="num">Prix</th><th class="num">€/m²</th><th class="num">Lots</th></tr></thead>
      <tbody>
{dvf_cmp_rows}
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Ce que l'analyse de prix dit, et ce qu'elle ne dit pas.</strong> Elle dit que le bien est <strong>bon marché pour son marché</strong> : {fr(abs((PRIX / SURF - DVF_Q_4560_MED) / DVF_Q_4560_MED * 100), 1)} % sous la médiane de sa tranche dans le centre ancien, {fr(abs((PRIX / SURF - DVF_APP_4560_MED) / DVF_APP_4560_MED * 100), 1)} % sous la médiane communale de la même tranche, {fr(abs((PRIX / SURF - DVF_CMP_MED) / DVF_CMP_MED * 100), 1)} % sous les transactions comparables — et au-dessus du premier quartile du quartier ({eur(DVF_Q_4560_Q1)} €/m²), donc pas au prix d'un lot en ruine. Sur ce marché-là, cette conjonction est rare. Elle ne dit pas que la décote est gratuite : sur une ville où la fiche de référence des marchés locaux montre qu'aucune commune du secteur ne dégage le seuil patrimonial au prix de marché, un prix sous la médiane paie presque toujours quelque chose. Ici, la liste est écrite noir sur blanc dans l'annonce : <strong>une procédure de copropriété en cours</strong>, un 2e étage sans ascenseur dans un immeuble de {ANNEE}, et un T3 dont la surface utile repose pour partie sur une mezzanine hors Carrez.</p>
      <p class="attractiveness-intro"><strong>La conséquence pratique.</strong> La valeur retenue — {eur(VALEUR_RETENUE)} €, 48 m² × {eur(DVF_Q_4560_MED)} €/m² — n'est pas un prix d'achat : c'est le prix de marché du quartier. La fourchette du quartier sur cette tranche de surface va de <strong>{eur(VALEUR_BASSE)} €</strong> (premier quartile) à <strong>{eur(VALEUR_HAUTE)} €</strong> (troisième quartile), et le prix demandé — {eur(PRIX)} € — se place dans le tiers bas de cette fourchette. L'acte en main à {eur(ACTE_EN_MAIN)} € laisse {eur(VALEUR_RETENUE - ACTE_EN_MAIN)} € de marge théorique sur la valeur. Mais cette marge ne se réalise qu'à la revente, sur un bien de centre ancien qui se revend lentement, et elle disparaît entièrement si la copropriété appelle 20 000 € de travaux : le prix de revient passerait alors à {eur(ACTE_EN_MAIN + TRAVAUX_REF_2)} € pour une valeur de {eur(VALEUR_RETENUE)} €, soit une marge de marchand de biens de {eur(VALEUR_RETENUE * 0.95 - (ACTE_EN_MAIN + TRAVAUX_REF_2))} € — négative.</p>
    </div>
  </section>"""

    proj_marge_section = f"""  <section class="financial-projections">
    <h2>Prix d'achat : les plafonds opposables</h2>
    <table class="projection-table compare">
      <thead><tr><th>Règle de prix</th><th class="num">Prix d'achat maximum</th><th class="num">Écart au prix affiché</th><th>Lecture</th></tr></thead>
      <tbody>
        <tr><td>Plafond 5 % net avant IS au loyer de base ({eur(SBASE['ebe'])} € d'EBE)</td><td class="num">{eur(SBASE['cap5'])}</td><td class="num">{fr((SBASE['cap5'] - PRIX) / PRIX * 100, 1)} %</td><td>la règle du parc, ressources propres</td></tr>
        <tr><td>Plafond 5 % net au loyer plancher</td><td class="num">{eur(SBAS['cap5'])}</td><td class="num">{fr((SBAS['cap5'] - PRIX) / PRIX * 100, 1)} %</td><td>si le loyer s'ajuste vers le bas</td></tr>
        <tr><td>Plafond 5 % net au loyer haut</td><td class="num">{eur(SHAUT['cap5'])}</td><td class="num">{fr((SHAUT['cap5'] - PRIX) / PRIX * 100, 1)} %</td><td>si le bien part au loyer du haut</td></tr>
        <tr><td>Plafond 5 % net avec charges doublées</td><td class="num">{eur(SCOPRO['cap5'])}</td><td class="num">{fr((SCOPRO['cap5'] - PRIX) / PRIX * 100, 1)} %</td><td>si la copropriété augmente son budget</td></tr>
        <tr><td>Plafond 5 % net avec 10 000 € de travaux</td><td class="num">{eur(prix_5pct_avec_travaux(SBASE['ebe'], TRAVAUX_REF_1))}</td><td class="num">{fr((prix_5pct_avec_travaux(SBASE['ebe'], TRAVAUX_REF_1) - PRIX) / PRIX * 100, 1)} %</td><td>rafraîchissement léger</td></tr>
        <tr><td>Plafond 5 % net avec 20 000 € de travaux</td><td class="num">{eur(prix_5pct_avec_travaux(SBASE['ebe'], TRAVAUX_REF_2))}</td><td class="num">{fr((prix_5pct_avec_travaux(SBASE['ebe'], TRAVAUX_REF_2) - PRIX) / PRIX * 100, 1)} %</td><td>électricité, salle d'eau, peintures</td></tr>
        <tr><td>Plafond 5 % net avec 30 000 € de travaux</td><td class="num">{eur(prix_5pct_avec_travaux(SBASE['ebe'], TRAVAUX_REF_3))}</td><td class="num">{fr((prix_5pct_avec_travaux(SBASE['ebe'], TRAVAUX_REF_3) - PRIX) / PRIX * 100, 1)} %</td><td>rénovation réelle</td></tr>
        <tr><td>Plafond 6,5 % net d'IS (seuil de rendement du parc)</td><td class="num">{eur(plafond_is(SBASE['ebe'], 0.065))}</td><td class="num">{fr((plafond_is(SBASE['ebe'], 0.065) - PRIX) / PRIX * 100, 1)} %</td><td>le seuil que le parc exige</td></tr>
        <tr class="highlight"><td><strong>Prix à cash-flow nul (apport de 10 %)</strong></td><td class="num"><strong>{eur(prix_cashflow_nul(SBASE['ebe']))}</strong></td><td class="num"><strong>{fr((prix_cashflow_nul(SBASE['ebe']) - PRIX) / PRIX * 100, 1)} %</strong></td><td>le prix où la trésorerie ne saigne plus</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Traduction en une phrase.</strong> Pour tenir 5 % net avant IS, il faut payer <strong>{eur(SBASE['cap5'])} €</strong> — soit {fr((PRIX - SBASE['cap5']) / PRIX * 100, 1)} % sous le prix affiché, ce qui reste dans l'épaisseur normale d'une négociation. Pour que la trésorerie soit nulle dès la première mensualité, il faudrait payer <strong>{eur(prix_cashflow_nul(SBASE['ebe']))} €</strong> ou apporter <strong>{eur(apport_cashflow_nul(PRIX, SBASE['ebe']))} €</strong> ({fr(apport_cashflow_nul(PRIX, SBASE['ebe']) / PRIX * 100, 1)} % du prix) — c'est hors doctrine du parc : l'apport filtre est de {APPORT_PCT * 100:.0f} %. Enfin, au loyer de base, la trésorerie ne s'équilibre qu'à un loyer de <strong>{eur(LOYER_CF_NUL)} €/mois</strong> ({fr(LOYER_CF_NUL / SURF, 1)} €/m²), soit {fr(LOYER_CF_NUL / LOYER_BASE * 100 - 100, 0)} % au-dessus du marché même haut : <strong>le cash-flow nul ne s'achète pas ici par le loyer, seulement par le prix</strong>.</p>
    </div>
  </section>"""

    charges_section = f"""  <section class="financial-projections">
    <h2>Fiscalité et charges d'exploitation : ce qui est su, ce qui est estimé</h2>
    <table class="projection-table compare">
      <thead><tr><th>Poste</th><th class="num">Montant retenu</th><th>Source</th></tr></thead>
      <tbody>
        <tr><td>Charges de copropriété du lot</td><td class="num">{eur(COPRO_BASE)} / an</td><td>annoncées par l'annonce (45 €/mois)</td></tr>
        <tr><td>Taxe foncière</td><td class="num">{eur(TF_BASE)} / an</td><td>ESTIMÉE — avis non communiqué</td></tr>
        <tr><td>Assurance propriétaire non occupant</td><td class="num">{eur(PNO)} / an</td><td>estimation de place</td></tr>
        <tr><td>Gestion locative et provision</td><td class="num">{eur(SBASE['entretien'])} / an</td><td>{fr(GESTION_BASE_PCT)} % des loyers plus {eur(PROV_BASE)} de provision</td></tr>
        <tr><td>Comptabilité SCI à l'IS</td><td class="num">{eur(COMPTA)} / an</td><td>estimation de place</td></tr>
        <tr><td>Travaux de remise en état</td><td class="num">0 € retenu</td><td>aucun devis : publié en grille (10 000 / 20 000 / 30 000 €)</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Fiscalité, année 1 :</strong> EBE {eur(SBASE['ebe'])} € moins intérêts d'emprunt {eur(INTERETS_AN1)} € ({eur(CAPITAL)} à {fr(TAUX_CREDIT * 100)} %) moins dotation aux amortissements {eur(DOTATION_AN1)} € (bâti à 80 % du prix affiché amorti sur 30 ans) = <strong>{eur(SBASE['ebe'] - INTERETS_AN1 - DOTATION_AN1)} €, soit un déficit</strong>. Aucun IS n'est dû en année 1, et le déficit se reconduit tant que le couple intérêts-plus-dotation dépasse l'EBE. Les rendements nets publiés restent néanmoins calculés sous la convention prudente du moteur (IS de 15 % de l'EBE, soit {eur(SBASE['is_'])} €) : c'est la lecture la plus défavorable, celle qui décide.</p>
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
      <p class="attractiveness-intro">Aucune lecture de location nue ne dégage un cash-flow positif au prix affiché, et seule la colocation meublée franchit 6 % net après IS — elle suppose de meubler, de découper et un marché qui n'existe pas ici. La strat<strong>égie retenue est la location nue au loyer de marché, sous conditions suspensives de pièces</strong> : c'est la seule lecture compatible avec la doctrine du parc, et elle se joue sur le prix d'entrée, pas sur le loyer.</p>
    </div>
  </section>"""

    inverse_section = f"""  <section class="financial-projections">
    <h2>Le prix d'équilibre, dans les trois sens</h2>
    <table class="projection-table compare">
      <thead><tr><th>Question inverse</th><th class="num">Réponse</th><th>Ce que cela veut dire</th></tr></thead>
      <tbody>
        <tr><td>Quel loyer pour un cash-flow nul au prix affiché ?</td><td class="num">{eur(LOYER_CF_NUL)} / mois</td><td>{fr(LOYER_CF_NUL / SURF, 1)} €/m² — au-dessus du haut de fourchette ({eur(LOYER_HAUT)}) : impossible à tenir</td></tr>
        <tr><td>Quel apport pour un cash-flow nul au prix affiché ?</td><td class="num">{eur(apport_cashflow_nul(PRIX, SBASE['ebe']))}</td><td>{fr(apport_cashflow_nul(PRIX, SBASE['ebe']) / PRIX * 100, 1)} % du prix — hors doctrine du parc</td></tr>
        <tr class="highlight"><td><strong>Quel prix pour un cash-flow nul ?</strong></td><td class="num"><strong>{eur(prix_cashflow_nul(SBASE['ebe']))}</strong></td><td><strong>{fr((prix_cashflow_nul(SBASE['ebe']) - PRIX) / PRIX * 100, 1)} % sous le prix affiché : la seule voie praticable</strong></td></tr>
        <tr><td>Quel prix pour 5 % net avant IS ?</td><td class="num">{eur(SBASE['cap5'])}</td><td>l'objectif de négociation, seuil de la doctrine</td></tr>
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
        <tr><td>Plafond patrimonial du parc (6,5 % net d'IS, fiche de référence)</td><td class="num">{eur(PLAF_PATRIMONIAL[0])}</td><td class="num">{fr((PRIX / SURF) / PLAF_PATRIMONIAL[0])} ×</td><td>le seul repère qui commande la décision</td></tr>
        <tr><td>Plafond marchand de biens (fiche de référence, rénovation à 1 200 €/m²)</td><td class="num">{eur(PLAF_MDB[0])}</td><td class="num">{fr((PRIX / SURF) / PLAF_MDB[0])} ×</td><td>hors sujet ici : pas de projet de revente rapide</td></tr>
        <tr><td>Médiane DVF 2025 du quartier, tranche 45-60 m²</td><td class="num">{eur(DVF_Q_4560_MED)}</td><td class="num">{fr((PRIX / SURF) / DVF_Q_4560_MED)} ×</td><td>le bien s'achète {fr(abs((PRIX / SURF - DVF_Q_4560_MED) / DVF_Q_4560_MED * 100), 1)} % sous sa médiane</td></tr>
        <tr><td>Médiane DVF 2025 communale, tranche 45-60 m²</td><td class="num">{eur(DVF_APP_4560_MED)}</td><td class="num">{fr((PRIX / SURF) / DVF_APP_4560_MED)} ×</td><td>{fr(abs((PRIX / SURF - DVF_APP_4560_MED) / DVF_APP_4560_MED * 100), 1)} % sous la médiane communale de la tranche</td></tr>
        <tr><td>Premier quartile DVF 2025 du quartier, tranche 45-60 m²</td><td class="num">{eur(DVF_Q_4560_Q1)}</td><td class="num">{fr((PRIX / SURF) / DVF_Q_4560_Q1)} ×</td><td>{fr((PRIX / SURF - DVF_Q_4560_Q1) / DVF_Q_4560_Q1 * 100, 1)} % au-dessus : pas le prix d'un lot dégradé</td></tr>
      </tbody>
    </table>
  </section>"""

    gen_spec = importlib.util.spec_from_file_location(
        "gen", os.path.join(ROOT, 'scripts', 'gen_fiches_2026-09-10.py'))
    gen = importlib.util.module_from_spec(gen_spec)
    gen_spec.loader.exec_module(gen)

    gen.LECTURE[SLUG] = lecture
    gen.RECS[SLUG] = rec_
    gen.CONF = {SLUG: dict(
        titre_court=(
            f"Appartement T3 {eur(SURF)} m², Centre Vieille Ville — Brignoles "
            f"(83170)"
        ),
        adresse=(
            f"Quartier Centre Vieille Ville, Brignoles (83170) — appartement "
            f"T3 de {eur(SURF)} m² avec mezzanine hors Carrez au {ETAGE}, "
            f"immeuble de {ANNEE}, à rafraîchir, copropriété de {LOTS_COPRO} "
            f"lots sous procédure"
        ),
        date_fr=DATE_FR,
        source=(
            "SeLoger — annonce 2665KPL9U1PX (référence interne 280702235), "
            "SAFTI, Coralie Marcelin EI, secteur Brignoles"
        ),
        url=URL,
        badge=(
            f"Bien libre, prix sous la médiane de son quartier — mais "
            f"procédure de copropriété en cours et rendement à "
            f"{fr(SBASE['rdt_av'])} % net avant IS"
        ),
        strategie=(
            f"Location nue longue durée au loyer de marché : "
            f"{eur(LOYER_BASE)} €/mois ({fr(LOYER_M2_MED)} €/m²), fourchette "
            f"testée de {eur(LOYER_BAS)} à {eur(LOYER_HAUT)} €. Aucun bail à "
            f"hériter, charges de copropriété annoncées {eur(COPRO_BASE)} €/an, "
            f"travaux non chiffrés publiés en grille. Stratégie conditionnée à "
            f"la production des procès-verbaux de copropriété et de l'état daté"
        ),
        fiscal_note=(
            f"SCI à l'IS — année 1 en déficit "
            f"({eur(SBASE['ebe'] - INTERETS_AN1 - DOTATION_AN1)} € après "
            f"intérêts {eur(INTERETS_AN1)} € et dotation {eur(DOTATION_AN1)} €), "
            f"donc aucun IS dû. Les rendements nets publiés restent sous la "
            f"convention prudente du moteur (IS de 15 % de l'EBE, "
            f"{eur(SBASE['is_'])} €), dite explicitement. Seuil de décision du "
            f"parc : 6,5 % net d'IS"
        ),
        lat="43.4056", lon="6.0616",
        quartier=(
            f"quartier Centre Vieille Ville, Brignoles (83170) — centre ancien "
            f"de la sous-préfecture du Var, commerces et services à pied, "
            f"immeuble de {ANNEE} sans ascenseur"
        ),
        intro_attr=(
            f"Le dossier se joue sur deux terrains opposés. Le premier est "
            f"favorable : <strong>le prix est bon</strong>. À "
            f"{eur(PRIX / SURF)} €/m², le bien se place "
            f"{fr(abs((PRIX / SURF - DVF_Q_4560_MED) / DVF_Q_4560_MED * 100), 1)} "
            f"% sous la médiane DVF 2025 de sa tranche de surface dans le "
            f"centre ancien ({DVF_Q_4560_N} ventes à "
            f"{eur(DVF_Q_4560_MED)} €/m²), "
            f"{fr(abs((PRIX / SURF - DVF_APP_4560_MED) / DVF_APP_4560_MED * 100), 1)} "
            f"% sous la médiane communale de la même tranche et "
            f"{fr(abs((PRIX / SURF - DVF_CMP_MED) / DVF_CMP_MED * 100), 1)} % sous "
            f"les six transactions comparables de 2025 "
            f"({eur(DVF_CMP_MED)} €/m²), tout en restant au-dessus du premier "
            f"quartile du quartier ({eur(DVF_Q_4560_Q1)} €/m²). Sur un marché "
            f"où la fiche de référence des marchés locaux montre qu'aucune "
            f"commune du secteur n'atteint le seuil patrimonial au prix "
            f"affiché, acheter sous la médiane est un événement rare. Le second "
            f"terrain est hostile : <strong>le revenu ne suit pas</strong>. Au "
            f"loyer médian de {eur(LOYER_BASE)} €/mois, l'affaire dégage un EBE "
            f"de {eur(SBASE['ebe'])} €, soit {fr(SBASE['rdt_av'])} % net avant "
            f"IS et un cash-flow de {eur(SBASE['cf'])} €/mois. Et l'annonce "
            f"déclare elle-même une <strong>procédure de copropriété en "
            f"cours</strong> au titre de l'article L. 721-1 du code de la "
            f"construction et de l'habitation, sur une copropriété de "
            f"{LOTS_COPRO} lots"
        ),
        profil=(
            f"un ménage de deux ou trois personnes, ou un jeune couple, dans un "
            f"T3 de {eur(SURF)} m² au centre ancien de Brignoles : commerces, "
            f"écoles et administrations à pied, deux chambres plus une "
            f"mezzanine. C'est le profil type de la demande locative locale, "
            f"et c'est aussi sa limite — la troisième pièce utile du bien n'est "
            f"pas une chambre au sens du Carrez, donc l'appartement ne peut pas "
            f"se vendre comme un T3 familial. Les loyers de marché "
            f"({fr(LOYER_M2_MED)} €/m², soit {eur(LOYER_BASE)} €/mois) sont "
            f"tenables, mais la demande n'est pas tendue : il faut une remise "
            f"en état correcte pour tenir le haut de la fourchette"
        ),
        concl_attr=(
            f"Adéquation moyenne ({fr((6 + 7 + 7 + 6 + 6 + 5) / 6, 1)}/10). Le "
            f"prix est l'atout du dossier et son rendement est sa limite : "
            f"acheter {fr(abs((PRIX / SURF - DVF_Q_4560_MED) / DVF_Q_4560_MED * 100), 1)} "
            f"% sous la médiane de son quartier ne compense pas un plafond 5 % "
            f"à {eur(SBASE['cap5'])} € quand le bien se vend {eur(PRIX)} €. Ce "
            f"dossier n'est pas un dossier mort : c'est un dossier de pièces. "
            f"Les questions qui décident sont écrites noir sur blanc — que "
            f"contient la procédure de copropriété, que votent les "
            f"procès-verbaux, que coûtent réellement les travaux, et que dit "
            f"l'avis de taxe foncière. Sans ces quatre réponses, on ne "
            f"s'engage pas ; avec elles, la négociation se chiffre"
        ),
        intro_strat=(
            f"Cinq lectures ont été testées, toutes calculées par le moteur : "
            f"trois hypothèses de loyer ({eur(LOYER_BAS)}, {eur(LOYER_BASE)} et "
            f"{eur(LOYER_HAUT)} €/mois), une variante où les charges de "
            f"copropriété doublent ({eur(COPRO_HAUT)} €/an), et une colocation "
            f"meublée à deux chambres ({eur(COLOC_BAS)} à {eur(COLOC_HAUT)} € "
            f"par chambre). Aucune lecture de location nue ne dégage un "
            f"cash-flow positif au prix affiché ; seule la colocation franchit "
            f"6 % net après IS, et elle suppose un marché qui n'existe pas à "
            f"Brignoles. La stratégie retenue est donc la location nue au loyer "
            f"de marché, sous condition suspensive de production des pièces de "
            f"copropriété"
        ),
        rationale=(
            f"<p><strong>Pourquoi la lecture patrimoniale s'impose ici.</strong> "
            f"Le bien est libre, sans bail à hériter, dans une ville où le "
            f"marché de la revente est étroit : ni la plus-value ni le "
            f"marchand de biens ne peuvent porter le dossier. Ce qui reste, "
            f"c'est le loyer. Or au loyer de marché, l'affaire rend "
            f"{fr(SBASE['rdt_av'])} % net avant IS et {fr(SBASE['rdt_ap'])} % "
            f"après IS sur l'acte en main — sous le seuil de 6,5 % du parc, et "
            f"sous le seuil de 5 % de la doctrine à un prix de "
            f"{eur(SBASE['cap5'])} €.</p>"
            f"<p><strong>Pourquoi le prix ne suffit pas à sauver le dossier.</strong> "
            f"La décote face au quartier est réelle "
            f"({fr(abs((PRIX / SURF - DVF_Q_4560_MED) / DVF_Q_4560_MED * 100), 1)} % "
            f"sous la médiane de la tranche), mais elle est l'exacte mesure du "
            f"risque : procédure de copropriété, 2e étage sans ascenseur, "
            f"mezzanine hors Carrez. Une décote qui paie un risque non chiffré "
            f"n'est pas une décote, c'est un pari. Le pari devient un calcul "
            f"le jour où les trois derniers procès-verbaux et l'état daté "
            f"chiffrent la procédure et les travaux votés.</p>"
            f"<p><strong>Ce qu'on demande, dans l'ordre.</strong> Les trois "
            f"derniers procès-verbaux d'assemblée générale, l'état daté et le "
            f"dernier appel de charges, le budget prévisionnel et le montant "
            f"des impayés de la copropriété, l'avis de taxe foncière, le "
            f"certificat Carrez incluant ou excluant la mezzanine, le "
            f"règlement de copropriété et le DPE complet. Rien de tout cela "
            f"n'est joint à l'annonce, et sur une copropriété de "
            f"{LOTS_COPRO} lots sous procédure, aucune de ces pièces n'est un "
            f"détail administratif.</p>"
        ),
        identite=[
            ("Ville", "Brignoles (83170), Var — sous-préfecture, 18 000 habitants environ"),
            ("Quartier", f"Centre Vieille Ville — centre ancien, boîte de coordonnées {DVF_BOITE[0]} à {DVF_BOITE[1]} N"),
            ("Type de bien", f"Appartement T3/F3, {PIECES} pièces, {CHAMBRES} chambres, {eur(SURF)} m² Carrez + mezzanine hors Carrez"),
            ("Étage et immeuble", f"{ETAGE}, immeuble de {ANNEE}"),
            ("Copropriété", f"{LOTS_COPRO} lots, charges annoncées {eur(COPRO_BASE)} €/an, PROCÉDURE EN COURS (art. L. 721-1 CCH)"),
            ("Diagnostics", f"DPE {DPE}, GES {GES}, facture annoncée {eur(FACTURE_BASSE)} à {eur(FACTURE_HAUTE)} €/an"),
            ("Prix affiché", f"{eur(PRIX)} € — {eur(PRIX / SURF)} €/m², honoraires à la charge du vendeur"),
            ("Acte en main", f"{eur(ACTE_EN_MAIN)} € (frais {eur(FRAIS_ACQUISITION)} €, simulateur de l'annonce)"),
            ("Valeur de marché", f"{eur(VALEUR_RETENUE)} € (médiane DVF du quartier, tranche 45-60 m², 48 m²)"),
            ("Loyer de marché", f"{eur(LOYER_BAS)} à {eur(LOYER_HAUT)} €/mois hors charges, base {eur(LOYER_BASE)} €/mois"),
            ("Rendement net", f"{fr(SBASE['rdt_av'])} % avant IS, {fr(SBASE['rdt_ap'])} % après IS sur l'acte en main"),
            ("Cash-flow", f"{eur(SBASE['cf'])} €/mois avant IS avec {APPORT_PCT * 100:.0f} % d'apport"),
            ("Prix maximum (doctrine 5 %)", f"{eur(SBASE['cap5'])} €"),
        ],
        stance=(
            f"<p><strong>Le prix n'est pas le problème de ce dossier, le revenu "
            f"l'est.</strong> À {eur(PRIX / SURF)} €/m², le bien se place "
            f"{fr(abs((PRIX / SURF - DVF_Q_4560_MED) / DVF_Q_4560_MED * 100), 1)} % "
            f"sous la médiane de son quartier pour sa tranche de surface, "
            f"{fr(abs((PRIX / SURF - DVF_CMP_MED) / DVF_CMP_MED * 100), 1)} % sous "
            f"les transactions comparables de 2025, et au-dessus du premier "
            f"quartile : c'est un vrai prix de marché, pas un prix d'appel. "
            f"Mais au loyer médian de {eur(LOYER_BASE)} €/mois, l'acte en main "
            f"de {eur(ACTE_EN_MAIN)} € ne rend que "
            f"{fr(SBASE['rdt_av'])} % net avant IS, et la trésorerie est "
            f"négative de {eur(abs(SBASE['cf']))} €/mois.</p>"
            f"<p><strong>Deux inconnues commandent tout, et aucune n'est dans "
            f"l'annonce.</strong> La première est la procédure de copropriété "
            f"citée à l'article L. 721-1 : elle explique probablement l'écart "
            f"de prix, et sur une copropriété de {LOTS_COPRO} lots, un seul "
            f"copropriétaire défaillant pèse jusqu'à un sixième des appels de "
            f"fonds. La seconde est le coût réel des travaux — l'annonce écrit "
            f"« à rafraîchir » sans chiffrer, et un appartement de {ANNEE} en "
            f"DPE {DPE} dans un immeuble sous procédure n'est pas un "
            f"rafraîchissement par défaut.</p>"
            f"<p><strong>Position : on négocie, à {eur(SBASE['cap5'])} € "
            f"maximum, sous conditions suspensives de pièces.</strong> "
            f"Le plafond que donne la doctrine du parc à 5 % net avant IS est "
            f"{eur(SBASE['cap5'])} €, soit "
            f"{fr((PRIX - SBASE['cap5']) / PRIX * 100, 1)} % sous le prix "
            f"affiché — une négociation crédible sur un dossier qui porte une "
            f"procédure. Offre d'ouverture à {eur(75000)} €. Si les "
            f"procès-verbaux révèlent des appels de fonds supérieurs à "
            f"{eur(TRAVAUX_REF_2)} au nom du lot, le plafond tombe à "
            f"{eur(prix_5pct_avec_travaux(SBASE['ebe'], TRAVAUX_REF_2))} € et "
            f"le dossier se referme. Si l'état daté est propre et que les "
            f"travaux restent sous 10 000 €, on peut défendre "
            f"{eur(prix_5pct_avec_travaux(SBASE['ebe'], TRAVAUX_REF_1))} € — "
            f"pas au-delà.</p>"
        ),
        prix_plafond=f"{eur(SBASE['cap5'])} €",
        leviers=[
            f"<strong>Négocier sur les pièces, pas sur le prix</strong> — "
                         f"Le prix est déjà sous la médiane du quartier : attaquer le prix "
             f"de front se ferait démolir par l'argument « moins cher que des "
             f"biens comparables ». En revanche, demander les trois derniers "
             f"procès-verbaux, l'état daté, les appels de fonds votés et le "
             f"budget prévisionnel est incontestable — et chaque pièce "
             f"défavorable se monétise en euros de prix. "
             f"{eur(TRAVAUX_REF_2)} € de travaux votés font tomber le prix "
             f"maximum à "
             f"{eur(prix_5pct_avec_travaux(SBASE['ebe'], TRAVAUX_REF_2))} €, soit "
             f"{eur(SBASE['cap5'] - prix_5pct_avec_travaux(SBASE['ebe'], TRAVAUX_REF_2))} € "
             f"de moins que le plafond actuel ({eur(SBASE['cap5'])} €).",
            f"<strong>Faire confirmer la surface et le statut de la mezzanine</strong> — "
                         f"Le prix au m² n'est flatteur que si la surface utile est bien "
             f"{eur(SURF)} m². Si la mezzanine entre ou sort du Carrez selon "
             f"le certificat, le prix au m² bouge de "
             f"{fr((PRIX / 55 - PRIX / SURF) / (PRIX / SURF) * 100, 1)} % : "
             f"c'est un levier de négociation à documenter, pas un argument "
             f"d'humeur.",
            f"<strong>Verrouiller le plafond de travaux dans le compromis</strong> — "
                         f"Exiger une clause suspensive chiffrée : si les appels de fonds "
             f"votés au nom du lot dépassent {eur(TRAVAUX_REF_1)}, le prix se "
             f"réduit d'autant, euro pour euro, frais d'acquisition compris "
             f"(soit 1 € de travaux = 0,93 € de prix). C'est la seule "
             f"protection qui tienne si les procès-verbaux arrivent après le "
             f"compromis.",
            f"<strong>Assumer la lecture « actif à rendement, pas à plus-value »</strong> — "
                         f"Le centre ancien de Brignoles se traite "
             f"{fr((1 - DVF_Q_MED / DVF_APP_MED) * 100, 1)} % sous la médiane "
             f"communale toutes surfaces : on n'achète pas ici une "
             f"appréciation, on achète un revenu. Toute décision se juge sur "
             f"le net après IS par euro engagé, et rien d'autre.",
        ],
        meta=[
            f"<strong>Méthode de prix.</strong> Toutes les statistiques DVF "
            f"2025 sont recalculées depuis le fichier départemental au moment "
            f"de la génération de cette fiche : {DVF_MUTATIONS} mutations lues "
            f"sur la commune de Brignoles (INSEE {DVF_COMMUNE}), dont "
            f"{DVF_MUTATIONS_VENTE} de nature Vente, {DVF_APP_N} ventes "
            f"d'appartements exploitables. Le quartier est délimité par une "
            f"boîte de coordonnées, méthode identique pour toutes les fiches "
            f"du parc afin que les chiffres restent comparables.",
            f"<strong>Ce qui est annoncé, ce qui est estimé.</strong> Sont "
            f"annoncés : le prix (84 000 €), la surface (48 m²), les charges de "
            f"copropriété (540 €/an), le nombre de lots (6), le DPE (D), le "
            f"GES (B), la facture énergétique (620 à 880 €/an) et la procédure "
            f"de copropriété. Sont estimés et signalés comme tels : la taxe "
            f"foncière ({eur(TF_BASE)} €/an), la provision travaux "
            f"({eur(PROV_BASE)} €/an), l'assurance PNO ({eur(PNO)} €/an), la "
            f"comptabilité ({eur(COMPTA)} €/an) et l'enveloppe de travaux, "
            f"publiée en grille de 10 000 à 30 000 €.",
            f"<strong>Point de méthode :</strong> ce dossier est le premier de "
            f"Brignoles jugé en lecture patrimoniale sur un bien LIBRE, et il "
            f"fixe le niveau de prix du centre ancien pour les prochains — "
            f"{eur(DVF_Q_4560_MED)} €/m² de médiane sur {DVF_Q_4560_N} ventes "
            f"de 45 à 60 m² contre {eur(DVF_Q_4560_Q1)} €/m² au premier "
            f"quartile et {eur(DVF_Q_4560_Q3)} €/m² au troisième. Règle à "
            f"retenir, valable pour tout bien de centre ancien : "
            f"<strong>quand un prix est nettement sous la médiane de sa "
            f"tranche, le prix n'est pas l'atout du dossier, c'est la facture "
            f"des risques</strong> — et ces risques s'exigent en pièces avant "
            f"de s'exiger en euros.",
            f"<strong>Réserve.</strong> Les loyers retenus proviennent "
            f"d'ancrages datés (fiche de référence interne du 21/09/2026, "
            f"Trackstone, SeLoger, annonces réelles du secteur) et non d'un "
            f"relevé d'annonces exhaustif sur ce quartier ; aucune des quatre "
            f"sources ne publie de loyer pour un T3 de 48 m² sans ascenseur en "
            f"centre ancien de Brignoles. Le loyer est donc l'hypothèse la "
            f"mieux documentée du dossier, pas une certitude — et c'est "
            f"précisément pour cela que le scénario plancher "
            f"({eur(LOYER_BAS)} €/mois) est publié au même rang que le "
            f"scénario de base.",
        ],
    )}
    c = gen.CONF[SLUG]
    html = gen.TEMPLATE.format(
        titre_court=c['titre_court'], adresse=c['adresse'], date_fr=c['date_fr'],
        source=c['source'], url=c['url'], badge=c['badge'],
        strategie=c['strategie'], fiscal_note=c['fiscal_note'],
        prix=eur(PRIX),
        surface=f"{eur(SURF)} m² (3 pièces, {CHAMBRES} chambres, mezzanine)",
        prix_m2=f"{eur(PRIX / SURF)} €/m²",
        revient=eur(ACTE_EN_MAIN),
        valeur=eur(VALEUR_RETENUE),
        revenus=eur(LOYER_BASE),
        rdt_revient=fr(SBASE['rdt_ap']), rdt_valeur=fr(SBASE['rdt_valeur']),
        note=fr(note, 1), note_cls=fr(note, 1).replace(',', '-'),
        lat=c['lat'], lon=c['lon'], quartier=c['quartier'],
        intro_attr=c['intro_attr'], profil=c['profil'], concl_attr=c['concl_attr'],
        attrs=gen.attr_html(rec_), intro_strat=c['intro_strat'],
        strats=gen.strategy_html(rec_),
        rationale=c['rationale'], identite=gen.identite_html(c['identite']),
        projections=(proj_section + "\n" + loyer_section + "\n"
                     + dvf_section + "\n" + proj_marge_section + "\n"
                     + charges_section + "\n" + lecture + "\n"
                     + inverse_section + "\n" + marche_section),
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
         '<span class="card-label">Prix / m² (sous la médiane du quartier)</span>'),
        ('<span class="card-label">Prix de revient</span>',
         '<span class="card-label">Prix de revient (acte en main, 8 % de frais)</span>'),
        ('<span class="card-label">Valeur marché retenue</span>',
         '<span class="card-label">Valeur marché (DVF 2025, quartier 45-60 m²)</span>'),
        ('<span class="card-label">Revenus bruts</span>',
         '<span class="card-label">Loyer retenu (12,0 €/m², bien libre)</span>'),
        ('<span class="card-label">Rentabilité nette</span>',
         '<span class="card-label">Rendement net après IS (acte en main / valeur)</span>'),
    ):
        assert vieux in html, vieux
        html = html.replace(vieux, neuf)

    assert 'section class="verdict nego"' in html, "classe de verdict inattendue"
    assert 'note-' + fr(note, 1).replace(',', '-') in html
    assert 'verdict buy' not in html and 'verdict pass' not in html
    _manquent = []
    for cle in ('84 000 €', '1 750 €', '90 720', '78 348', '97 536', '70 320',
                '110 160', '4 231', '4,66', '3,96', '60268'[:0] or '60 268',
                '2 032', '1 465', '116 000', '103 050', 'Centre Vieille Ville',
                'L. 721-1', 'mezzanine', 'SAFTI'):
        if cle not in html:
            _manquent.append(cle)
    if _manquent:
        print("  ATTENTION : chiffres attendus absents du HTML :", _manquent)
    assert not _manquent, _manquent
    assert '<tr<' not in html, "balise <tr> malformee"
    assert '<trtd' not in html, "balise <tr> malformee"
    assert not any(x in html for x in ('{titre_court}', '{projections}',
                                       '{note}', '{stance}')), "placeholder non substitue"

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
        print("\n  Chiffres signales en ecart (tolerance depassee) :")
        for lab, brief, rec2, note_txt in ECARTS:
            print(f"    {lab:<64} publie {brief} | recalcule {rec2} — {note_txt}")


if __name__ == '__main__':
    main()
