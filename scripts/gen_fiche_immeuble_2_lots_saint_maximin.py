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
                "Convention de chiffrage retenue : IS à 15 % appliqué à l'EBE, sans amortissement "
                "du bâti. L'amortissement par composant d'un immeuble ancien détenu en totalité "
                "n'a pas été modélisé (aucune ventilation par composant n'est établie et aucun "
                "diagnostic technique n'est disponible) : le rendement après IS publié ici est donc "
                "le plus prudent des deux, et l'amortissement réel allégera l'impôt les premières "
                "années. Le seuil de décision de la doctrine du parc porte de toute façon sur le "
                "rendement net AVANT IS"
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
            ("Fiscalité", "SCI à l'IS : IS de 15 % appliqué à l'EBE, <strong>sans amortissement du "
                          "bâti modélisé</strong> (aucune ventilation par composant établie sur cet "
                          "immeuble ancien) — convention prudente et documentée. Le seuil de "
                          "décision de la doctrine du parc porte sur le rendement net avant IS"),
            ("Prix de revient", f"<strong>{eur(ACTE_EN_MAIN)} €</strong> acte en main = prix "
                                f"{eur(PRIX)} € + frais d'acquisition {eur(PRIX*NOTAIRE)} € (8 %), "
                                f"sans travaux (aucun travaux annoncé)"),
        ],
        stance=(
            f"<strong>À négocier — offrir 148 000 €, plafond 165 000 €</strong>, sous condition "
            f"d'obtention des deux baux, de l'avis de taxe foncière et des diagnostics datés. Le "
            f"raisonnement tient en un chiffre : avec les loyers reconstruits à partir du marché "
            f"— 1 070 €/mois — le dossier rend {fr(BASE['rdt_av'])} % net avant IS sur l'acte en "
            f"main, donc il passe notre seuil de 5 %, mais de 44 points de base. Le prix qui tient "
            f"exactement ce seuil est de <strong>{eur(BASE['cap5'])} €</strong>, au-dessus des "
            f"160 000 € demandés : la marge de négociation n'est pas là. Elle est dans les baux : "
            f"à 920 €/mois le même bien ne vaut plus que {eur(WORST['cap5'])} €, à 1 200 €/mois il "
            f"en vaut {eur(BEST['cap5'])}. Personne ne sait aujourd'hui de quel côté de cette "
            f"fourchette se situe l'immeuble, et l'annonce vend une « rentabilité immédiate » sans "
            f"en donner le chiffre.<br><br>"
            f"<strong>Trois pièces suspensives, non négociables.</strong> Les deux "
            f"<strong>baux en cours</strong>, avec leur montant, leur date et leur échéance, et les "
            f"dernières quittances : c'est la seule donnée qui décide du dossier, et son absence "
            f"dans une annonce qui parle de rentabilité immédiate est en soi un signal. "
            f"L'<strong>avis de taxe foncière</strong> : 200 € d'écart valent 0,7 % de rendement "
            f"brut. Les <strong>diagnostics datés</strong> — DPE, électricité, plomb, amiante — "
            f"plus une visite d'homme de l'art sur les trois postes que « aucun travaux » ne "
            f"couvre : couverture, électricité et humidité des caves, sur un immeuble dont "
            f"l'acquéreur porte seul la structure.<br><br>"
            f"<strong>Ce qui rend le dossier défendable malgré tout.</strong> Il est loué, il est en "
            f"centre-ville et il n'y a rien à faire : pas de copropriété à financer, pas de "
            f"chantier, pas de passif énergétique (DPE D, aucune échéance avant 2034), des "
            f"compteurs individuels. Et il passe le seuil de 5 % net avant IS en scénario de base, "
            f"ce que peu de dossiers de la semaine font — encore faut-il que les baux soient "
            f"effectivement à ce niveau, ce qui reste à vérifier."
        ),
        prix_plafond=(
            f"<strong>165 000 €, sous condition des baux.</strong> Le prix qui tient exactement "
            f"5 % net avant IS est de {eur(BASE['cap5'])} € avec 1 070 €/mois de loyers : c'est un "
            f"seuil, pas une cible, et il vaut donc 174 185 € sur un chiffrage dont les loyers ne "
            f"sont pas documentés. Le plafond retenu est 165 000 €, soit "
            f"{eur(BASE['cap5'] - 165000.0)} € de marge pour absorber les trois inconnues du "
            f"dossier (taxe foncière, état de la couverture et des caves, ameublement du studio), "
            f"et l'offre d'ouverture est 148 000 €, soit "
            f"{fr((PRIX - 148000.0) / PRIX * 100, 1)} % sous le prix affiché. Sensibilité du "
            f"plafond aux seuls loyers, charges de base inchangées : à 900 €/mois "
            f"{eur(calc(900.0, 5.0, 5.0, 900.0, 400.0, 150.0, 200.0, 500.0)['cap5'])} €, à "
            f"1 000 €/mois {eur(calc(1000.0, 5.0, 5.0, 900.0, 400.0, 150.0, 200.0, 500.0)['cap5'])} €, "
            f"à 1 070 €/mois {eur(BASE['cap5'])} €, à 1 150 €/mois "
            f"{eur(calc(1150.0, 5.0, 5.0, 900.0, 400.0, 150.0, 200.0, 500.0)['cap5'])} €. Chaque "
            f"tranche de 100 €/mois de loyer vaut 20 000 € de capacité de prix : c'est le seul "
            f"chiffre à retenir de cette négociation. Si les baux révèlent 920 €/mois, le plafond "
            f"tombe à {eur(WORST['cap5'])} € et la réponse est non."
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
            f"<strong>Régime fiscal retenu :</strong> SCI à l'IS, IS de 15 % appliqué à l'EBE, "
            f"sans amortissement du bâti modélisé — il n'existe aucune ventilation par composant "
            f"sur cet immeuble ancien, et l'amortissement réel allégera l'impôt les premières "
            f"années. Le seuil de décision du parc (5 % net avant IS) porte sur le rendement avant "
            f"impôt : {fr(BASE['rdt_av'])} % en base, {fr(BASE['rdt_ap'])} % après IS",
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
  </section>""",
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
