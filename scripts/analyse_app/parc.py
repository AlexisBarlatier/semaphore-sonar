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
