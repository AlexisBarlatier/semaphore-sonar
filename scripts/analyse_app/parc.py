# -*- coding: utf-8 -*-
"""État du parc au 28/09/2026 : les biens, la dette, la réserve et l'IS.

Deux biens :
• **La Verrerie** (La Valentine, Marseille) — 13 parkings loués en bloc à SCHINDLER,
  acte du 23/04/2026, financés par un prêt Crédit Mutuel dédié.
• **La Garde** — 2 places extérieures (« Le Dionysos », lots 80/81) achetées sur
  fonds personnels des associés et prêtées à la SCI en compte courant.

Un seul endroit pour ces chiffres : deux fiches qui citeraient deux montants
différents du même loyer ou de la même dette se contrediraient. Mettre à jour à
chaque relevé, et dater — une fiche publiée porte les chiffres de sa date.
"""
DATE_RELEVE = "28 septembre 2026"

# --- Réserve vacance et travaux (« mini-ALUR » interne) -----------------------
# Déclaration de Rémy Barlatier : 4 529,11 € en réserve, portée par un effort de
# 500 €/mois tant qu'aucun nouveau dossier ne se matérialise, hors intérêts. Le
# taux de placement vit dans la fiche (`hypotheses.taux_placement_reserve_pct`) :
# les produits sont bruts d'IS, la société étant à l'IS.
RESERVE_EUR = 4529.11
EFFORT_MENSUEL_EUR = 500.0
IS_RATE = 0.15                  # produits imposés à l'IS avant d'être replacés

# --- Coûts de structure de la SCI (relevé du 28/09/2026) ----------------------
# 104 €/mois, soit 1 248 €/an. Le cabinet facture la SCI entière : le marginal
# par lot reste à ~150 €/an. Ni assurance ni taxe foncière à ajouter pour la
# Verrerie : les deux sont refacturées au locataire, donc neutres en résultat
# (les compter serait les compter deux fois).
BANQUE_MENSUEL_EUR = 20.0
COMPTABLE_MENSUEL_EUR = 84.0

# --- La Verrerie : 13 parkings, acte du 23/04/2026 ----------------------------
# Locataire SCHINDLER (bail commercial). Loyer HT, révisé : 4 651,30 €/trimestre
# pour 2026 (factures T2 et T3 au dossier). Refacturés au preneur : taxe
# foncière 784 €/an et PNO 598,91 €/an — neutralisées dans le résultat.
LOYER_VERRERIE_TRIMESTRIEL_EUR = 4651.30
TF_VERRERIE_ANNUELLE_EUR = 784.0            # refacturée : neutre
PNO_VERRERIE_ANNUELLE_EUR = 598.91          # refacturée : neutre
# Prêt Crédit Mutuel dédié : 71 500 € (prix HT) à 3,70 % fixe sur 180 mois,
# TEG 5,64 %, échéance 546,79 €/mois assurance comprise (1re 05/05/2026,
# dernière 05/04/2041), assurance emprunteur 374 €/an, cautions solidaires
# d'Alexis et Rémy Barlatier. Reste dû au 28/09/2026 : 70 002 €.
PRET_VERRERIE_EUR = 71500.0
PRET_VERRERIE_TAUX = 0.0370
PRET_VERRERIE_MENSUALITE_EUR = 546.79
PRET_VERRERIE_ENCOURS_EUR = 70002.0
ASSURANCE_EMPRUNTEUR_ANNUELLE_EUR = 374.0

# --- La Garde : 2 places extérieures, achetées sur fonds personnels -----------
# 11 400 € (5 700 € la place), avancés par Alexis et Rémy et prêtés à la SCI en
# compte courant d'associé. Objectif locatif : 50 à 60 € par place et par mois
# hors charges, soit 1 200 à 1 440 €/an et 10,5 à 12,6 % brut sur les 11 400 €.
# Pas de PNO : place extérieure, aucune assurance obligatoire — décision de Rémy
# (le conducteur couvre son véhicule, la copropriété porte sa RC sur les parties
# communes). Reste à chiffrer : les charges de copropriété et la taxe foncière.
# Convention de prêt : in fine
# à 3 %, refonte prévue en amortissable sur 240 mois. À 0 % la SCI ne déduit
# rien et les associés ne paient rien : c'est neutre, et c'est plus simple.
PRET_ASSOCIES_LA_GARDE_EUR = 11400.0
PRET_ASSOCIES_LA_GARDE_TAUX = 0.0
LOYER_LA_GARDE_CIBLE_MIN_EUR = 50.0
LOYER_LA_GARDE_CIBLE_MAX_EUR = 60.0

# --- IS : reconstitution, pas un chiffre du fisc ------------------------------
# Base = loyers − structure − assurance emprunteur − intérêts − amortissements.
# Année pleine : 18 605 € de loyers, 1 248 € de structure, 374 € d'assurance et
# 2 646 € d'intérêts. Reste 1 829 € d'IS si le cabinet amortit la part bâtie des
# places, 2 151 € sinon — soit 152 à 179 €/mois. La provision de 100 €/mois en
# couvre 56 à 66 %. Le vrai chiffre tombera au premier arrêté de comptes.
IS_ESTIME_MIN_ANNUEL_EUR = 1830.0
IS_ESTIME_MAX_ANNUEL_EUR = 2150.0


def loyers_verrerie_annuels():
    """Loyers Schindler sur une année pleine (4 trimestres)."""
    return LOYER_VERRERIE_TRIMESTRIEL_EUR * 4


def ebe_verrerie(pno_annuelle=0.0):
    """EBE annuel de la Verrerie, hors IS et hors service de la dette.

    `pno_annuelle` vaut 0 : l'assurance et la taxe foncière sont refacturées en
    totalité au locataire, les porter ici les compterait deux fois.
    """
    return (loyers_verrerie_annuels()
            - (BANQUE_MENSUEL_EUR + COMPTABLE_MENSUEL_EUR) * 12
            - pno_annuelle)


def interets_verrerie_annee1(taux=None):
    """Intérêts de la première année pleine du prêt Crédit Mutuel."""
    return PRET_VERRERIE_ENCOURS_EUR * (PRET_VERRERIE_TAUX if taux is None else taux)


def is_estime_verrerie(amortissement_annuel=0.0, taux_pret=None):
    """IS estimé sur la Verrerie seule, intérêts et assurance emprunteur déduits.

    Reste une reconstitution : le vrai chiffre tombe à l'arrêté de comptes.
    """
    return IS_RATE * max(0.0, ebe_verrerie()
                         - ASSURANCE_EMPRUNTEUR_ANNUELLE_EUR
                         - interets_verrerie_annee1(taux_pret)
                         - amortissement_annuel)


def flux_verrerie_mensuel(is_annuel=None, amortissement_annuel=0.0):
    """Ce qui reste chaque mois après structure, IS, assurance et échéance.

    C'est le flux qui doit recouper la somme retenue par Rémy (700 €/mois).
    """
    if is_annuel is None:
        is_annuel = is_estime_verrerie(amortissement_annuel)
    return (loyers_verrerie_annuels() / 12
            - BANQUE_MENSUEL_EUR - COMPTABLE_MENSUEL_EUR
            - ASSURANCE_EMPRUNTEUR_ANNUELLE_EUR / 12
            - is_annuel / 12
            - PRET_VERRERIE_MENSUALITE_EUR)


def trajectoire(mois, taux_pct, solde=None, effort=None, is_rate=IS_RATE):
    """Solde de la réserve après `mois` mois d'effort et de produits replacés."""
    s = RESERVE_EUR if solde is None else solde
    e = EFFORT_MENSUEL_EUR if effort is None else effort
    for _ in range(int(mois)):
        produits = s * (taux_pct / 100.0) / 12.0
        s = s + e + produits * (1 - is_rate)
    return s


def mois_pour(cible, taux_pct, solde=None, effort=None, is_rate=IS_RATE, plafond=1200):
    """Nombre de mois nécessaires pour porter la réserve à `cible`."""
    s = RESERVE_EUR if solde is None else solde
    e = EFFORT_MENSUEL_EUR if effort is None else effort
    mois = 0
    while s < cible and mois < plafond:
        produits = s * (taux_pct / 100.0) / 12.0
        s = s + e + produits * (1 - is_rate)
        mois += 1
    return mois
