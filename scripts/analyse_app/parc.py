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
# de la Verrerie. Aucune assurance ni taxe foncière à ajouter pour la Verrerie :
# les deux sont refacturées au locataire, donc neutres en résultat (les compter
# serait les compter deux fois). Une éventuelle gestion locative reste à chiffrer.
BANQUE_MENSUEL_EUR = 20.0
COMPTABLE_MENSUEL_EUR = 84.0     # abonnement du cabinet pour la SCI entière :
                                 # le marginal par lot reste à ~150 EUR/an

# --- Verrerie : 13 places acquises 85 800 EUR en 04/2026 ----------------------
# Bail net : loyer hors charges, taxe foncière et assurance refacturées
# intégralement, charges locatives au preneur. L'EBE est donc presque le loyer.
LOYER_VERRERIE_MENSUEL_EUR = 1624.0
TF_VERRERIE_ANNUELLE_EUR = 784.0  # refacturée : neutre en résultat,
                                  # ne pas la compter deux fois
ASSURANCE_VERRERIE_REFACTUREE = True

# --- La Garde : 2 places extérieures, PROJET NON DÉMARRÉ au 28/09/2026 --------
# Offre de prêt Crédit Mutuel, pas encore mobilisée : aucun intérêt à déduire
# tant que l'acquisition n'est pas faite et le prêt tiré. Le loyer ne sera
# facturé qu'après l'achat. 70 002 EUR / 546,79 EUR/mois : le couple implique
# 4,98 % si le prêt court jusqu'à fin 2041, 3,7 % s'il s'arrête vers fin 2040.
# Quand il démarrera : les intérêts (2 590 à 3 490 EUR/an) allégeront l'IS de
# 390 à 525 EUR/an. Une franchise faisant courir les intérêts conserve cette
# déduction ; une franchise « gratuite » qui les supprime la fait perdre.
PRET_LA_GARDE_ENCOURS_EUR = 70002.0
PRET_LA_GARDE_MENSUALITE_EUR = 546.79
PRET_LA_GARDE_DEMARRE = False

# --- IS : reconstitution, pas un chiffre du fisc ------------------------------
# Base = loyers − charges − amortissements − intérêts. La Garde n'ayant pas
# démarré, il n'y a AUCUN intérêt à déduire aujourd'hui : que la part bâtie des
# 13 places soit de 0 ou de 90 %, l'IS ressort entre 2 350 et 2 740 EUR/an, soit
# 196 à 228 EUR/mois, 12 à 14 % des loyers. Quand La Garde démarrera, la
# fourchette descend vers 1 830-2 350. La provision de 100 EUR/mois en couvre
# 44 à 51 % : c'est la première ligne à corriger. Le vrai chiffre tombera au
# premier arrêté de comptes.
# À OBTENIR : la mensualité du prêt d'acquisition de la Verrerie (85 800 EUR en
# 04/2026). Sans elle le flux ne se recoupe pas : 1 624 € de loyers − 104 € de
# structure − ~228 € d'IS = 1 292 €/mois, là où le dossier retient 840 €/mois.
# L'écart de ~452 €/mois (5 424 €/an) n'a pas d'explication au dossier.
IS_ESTIME_MIN_ANNUEL_EUR = 2350.0
IS_ESTIME_MAX_ANNUEL_EUR = 2740.0


def ebe_verrerie(pno_annuelle=0.0):
    """EBE annuel de la Verrerie, hors IS et hors service de la dette.

    `pno_annuelle` vaut 0 par défaut : l'assurance est refacturée en totalité au
    locataire, la porter ici la compterait deux fois. La taxe foncière, également
    refacturée, n'entre pas non plus dans le compte.
    """
    return (LOYER_VERRERIE_MENSUEL_EUR * 12
            - (BANQUE_MENSUEL_EUR + COMPTABLE_MENSUEL_EUR) * 12
            - pno_annuelle)


def is_estime_verrerie(amortissement_annuel=0.0, taux_pret=0.0):
    """IS estimé sur la Verrerie seule.

    `taux_pret` vaut 0 par défaut parce que le prêt La Garde n'est pas mobilisé :
    dès qu'il le sera, passer le taux réel (les intérêts se déduisent). Reste une
    reconstitution : le vrai chiffre tombe au premier arrêté de comptes.
    """
    interets = PRET_LA_GARDE_ENCOURS_EUR * taux_pret if PRET_LA_GARDE_DEMARRE else 0.0
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
