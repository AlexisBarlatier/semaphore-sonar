# -*- coding: utf-8 -*-
"""État du parc : la réserve vacance et travaux, notre « mini-ALUR » interne.

Source : déclaration de Rémy Barlatier du 28/09/2026 — 4 529,11 € en réserve ce
jour, portée par un effort de 500 €/mois tant qu'aucun nouveau dossier ne se
matérialise, hors intérêts. Le taux de placement vit dans la fiche
(`hypotheses.taux_placement_reserve_pct`) : les produits sont bruts d'IS, la
société étant à l'IS.

Un seul endroit pour ce solde : deux fiches qui citeraient deux montants
différents de la même réserve à la même date se contrediraient. Mettre à jour le
solde ET la date à chaque relevé — une fiche publiée porte le solde de sa date
d'analyse, et le dit.
"""
DATE_RELEVE = "28 septembre 2026"
RESERVE_EUR = 4529.11           # solde de la réserve à la date ci-dessus
EFFORT_MENSUEL_EUR = 500.0      # effort mensuel du parc, hors intérêts
IS_RATE = 0.15                  # produits imposés à l'IS avant d'être replacés

# --- Coûts de structure de la SCI (relevé du 28/09/2026) ---------------------
# Charges mensuelles connues : 104 EUR/mois, soit 1 248 EUR/an, 6,4 % des loyers
# de la Verrerie. L'assurance propriétaire non occupant et une éventuelle
# gestion locative ne sont pas encore chiffrées ici.
BANQUE_MENSUEL_EUR = 20.0
COMPTABLE_MENSUEL_EUR = 84.0     # abonnement du cabinet pour la SCI entière :
                                 # le marginal par lot reste à ~150 EUR/an

# --- Verrerie : 13 places acquises 85 800 EUR en 04/2026 ----------------------
LOYER_VERRERIE_MENSUEL_EUR = 1624.0
TF_VERRERIE_ANNUELLE_EUR = 784.0  # refacturée au locataire : neutre en résultat,
                                  # ne pas la compter deux fois

# --- La Garde : 2 places extérieures, prêt Crédit Mutuel ----------------------
# 70 002 EUR d'encours, 546,79 EUR/mois. Le couple encours/mensualité implique
# un taux de 4,98 % si le prêt court jusqu'à fin 2041, de 3,7 % s'il s'arrête
# vers fin 2040 : les intérêts de la première année vont de 2 590 à 3 490 EUR.
# À confirmer sur le tableau d'amortissement — plus le taux est bas, plus le
# résultat imposable est haut.
PRET_LA_GARDE_ENCOURS_EUR = 70002.0
PRET_LA_GARDE_MENSUALITE_EUR = 546.79

# --- IS : reconstitution, pas un chiffre du fisc ------------------------------
# Base = loyers − charges − amortissements − intérêts. Une place de surface n'a
# presque rien d'amortissable (le terrain ne s'amortit pas) : que la part bâtie
# soit de 0 ou de 90 %, et selon le taux du prêt La Garde, l'IS de la Verrerie
# ressort entre 1 800 et 2 300 EUR/an, soit 150 à 195 EUR/mois, 9 à 12 % des
# loyers. Le vrai chiffre tombera au premier arrêté de comptes ; la provision de
# 100 EUR/mois en couvre la moitié.
IS_ESTIME_MIN_ANNUEL_EUR = 1800.0
IS_ESTIME_MAX_ANNUEL_EUR = 2300.0


def ebe_verrerie(pno_annuelle=200.0):
    """EBE annuel de la Verrerie, hors IS et hors service de la dette."""
    return (LOYER_VERRERIE_MENSUEL_EUR * 12
            - (BANQUE_MENSUEL_EUR + COMPTABLE_MENSUEL_EUR) * 12
            - pno_annuelle)


def is_estime_verrerie(amortissement_annuel=0.0, taux_pret=0.0498):
    """IS estimé sur la Verrerie seule, intérêts du prêt La Garde déduits.

    Reste une reconstitution : le vrai chiffre tombe au premier arrêté de comptes.
    """
    interets = PRET_LA_GARDE_ENCOURS_EUR * taux_pret
    return IS_RATE * max(0.0, ebe_verrerie() - amortissement_annuel - interets)


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
