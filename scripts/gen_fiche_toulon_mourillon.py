#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche Toulon Mourillon — T5 de 107,2 m2 dans une residence de standing avec gardien,
223 000 EUR (SeLoger 269Y5Y2G6A9A, Agence de l'Avenir).

Branche residentielle (SCI a l'IS). L'enjeu n'est pas le prix au m2, il est dans les
charges de copropriete d'une residence de 220 lots avec gardien et dans le loyer plafonne
d'un T5 : le bien est au Q1 de sa tranche de marche et pourtant hors doctrine.
"""
import importlib.util
import json
import os
import sys

ROOT = '/home/alexis-barlatier/Documents/Semaphore-sonar'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from analyse_app import engine, scoring  # noqa: E402

SLUG = "2026-09-22-appartement-t5-mourillon-toulon"
URL = "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/toulon-83000/269Y5Y2G6A9A"

PRIX = 223000.0
NOTAIRE = 0.08
SURF = 107.2
TRAVAUX = 60000.0
LOYER = 1600.0
COPRO = 3600.0
TF = 1500.0
TAUX = 0.037


def eur(v):
    return f"{v:,.0f}".replace(',', ' ')


def fr(v, dec=1):
    return f"{v:.{dec}f}".replace('.', ',')


def mens(cap, taux, an):
    i = taux / 12
    n = an * 12
    return cap * i / (1 - (1 + i) ** -n)


def ebe(loyer, copro=COPRO, travaux=TRAVAUX, vac=0.05):
    brut = loyer * 12
    charges = copro + TF + 1150.0
    return brut - brut * vac - charges - brut * 0.025 - brut * 0.01


def rec_toulon():
    return {
        "slug": SLUG,
        "date_analyse": "2026-09-22",
        "date_maj": None,
        "titre": "Appartement T5 de 107,2 m² dans une résidence de standing avec gardien — Mourillon-Centre, Toulon (83000)",
        "bien": {
            "type_bien": "appartement",
            "sous_type": None,
            "type_detail": (
                "Appartement de type 5 au premier étage d'une résidence de standing de 220 lots, avec gardien "
                "et ascenseur, quartier Mourillon-Centre. Hall d'entrée, séjour double ouvrant sur balcon, "
                "cuisine avec balcon, cellier, trois chambres dont deux donnant sur balcon, salle d'eau, WC "
                "séparé, cave. Exposition ouest, chauffage central au gaz, immeuble de 1961. L'annonce écrit "
                "elle-même « prévoir une rénovation ». DPE D, GES D"
            ),
            "neuf": False,
            "adresse": {
                "texte": "Mourillon-Centre, Toulon (83000) — adresse exacte non communiquée, à proximité "
                         "immédiate des plages du Mourillon et des commodités",
                "ville": "Toulon",
                "code_postal": "83000",
            },
            "surfaces": {
                "texte": "107,2 m² annoncés, 5 pièces, 3 chambres, 1er étage sur 20. Surface Carrez non "
                         "précisée dans l'annonce, à confirmer sur le diagnostic",
                "carrez_m2": 107.2,
            },
            "lots": {
                "count": 1,
                "surface_par_lot_m2": None,
                "nature": "Un seul lot d'habitation dans une copropriété de 220 lots (fiche SeLoger)",
                "lots_distincts": 1,
            },
            "copro": {
                "charges_annuelles_euros": COPRO,
                "charges_source": (
                    "Copropriété de 220 lots avec gardien et ascenseur — montant des charges NON communiqué. "
                    "Estimation retenue 3 600 €/an au titre d'une résidence de standing gardiennée, à vérifier "
                    "sur les trois derniers appels de fonds et le procès-verbal de la dernière assemblée "
                    "générale : c'est le premier poste de risque du dossier et il décide du rendement"
                ),
            },
            "travaux": {
                "montant_euros": TRAVAUX,
                "nature": (
                    "« Prévoir une rénovation » (annonce), non chiffrée : électricité, plomberie, salle de "
                    "bains, cuisine, sols, peintures, menuiseries. Provision retenue 60 000 €, soit 560 €/m², "
                    "au milieu d'une fourchette de rafraîchissement 400 à 800 €/m² pour un appartement de "
                    "1961 jamais repris. Aucun devis, aucun plan, aucun diagnostic technique joint"
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
                "223 000 €, soit 2 080 €/m², honoraires à la charge du vendeur. C'est le premier quartile de "
                "la tranche 80-150 m² de Toulon (450 ventes en 2025, médiane 2 685 €/m²) : le prix d'entrée est "
                "objectivement bas pour le Mourillon, et c'est bien un dossier à regarder. Mais un prix d'achat "
                "bas ne suffit pas : l'annonce annonce aussi « prévoir une rénovation » et une copropriété de "
                "220 lots avec gardien, deux postes qui décident du rendement. Facture énergétique annoncée "
                "entre 1 810 et 2 470 €/an"
            ),
        },
        "marche": {
            "valeur": {
                "basse_euros": 257000.0,
                "haute_euros": 311000.0,
                "retenue_euros": 288000.0,
                "source": (
                    "Mutations DVF 2025 de Toulon (commune 83137, 2 760 ventes d'appartements) : médiane "
                    "globale 2 668 €/m², et sur la tranche 80-150 m² qui correspond au bien, 450 ventes et une "
                    "médiane de 2 685 €/m², premier quartile à 2 086 €/m². Valeur retenue 288 000 € "
                    "(2 685 €/m²), fourchette 257 000 € (2 400 €/m², rafraîchissement léger) à 311 000 € "
                    "(2 900 €/m², rénovation complète). L'annonce à 2 080 €/m² se situe 22 % sous la médiane "
                    "de sa propre tranche"
                ),
                "confiance": "moyenne",
            },
            "loyers": [
                {
                    "lot": "T5 de 107,2 m² — logement entier loué vide",
                    "quantite": 1,
                    "loyer_mensuel_euros": LOYER,
                    "occupe": False,
                    "note": (
                        "Le bien n'est pas loué aujourd'hui : ce loyer est un loyer retenu après "
                        "rafraîchissement, pas un revenu acquis. Comparables relevés le 22/09/2026 à Toulon : "
                        "T5 de 3 chambres à 1 520 €, T5 à 1 609 € hors charges, T5 à 1 759 € (dont 150 € de "
                        "charges), T5 de 100 m² à 1 600 €. Le loyer mesuré de la commune est de 14,4 €/m²/mois "
                        "(ANIL 2025), soit 1 541 € pour cette surface : le loyer retenu de 1 600 € reste dans "
                        "le bas de la fourchette. Un T5 se loue structurellement moins cher au m² qu'un T2"
                    ),
                },
            ],
            "notes": (
                "Deux pistes alternatives ont été chiffrées. La colocation meublée à quatre chambres se "
                "commercialise 420 à 470 € par chambre au Mourillon, soit 1 800 à 1 880 € par mois : c'est "
                "15 % de loyer brut en plus, contre un investissement d'ameublement, une vacance plus "
                "fréquente et une gestion plus lourde — le rendement net ne change pas de camp. La revente "
                "après rafraîchissement ne fonctionne pas non plus : à 40 000 € de travaux et une revente au "
                "médian de la tranche (2 685 €/m²), l'opération perd 7 400 € et il faut atteindre 2 900 €/m² "
                "pour espérer 12 000 € de gain. Le dossier n'a donc ni lecture locative conforme à notre "
                "doctrine, ni lecture marchand de biens"
            ),
        },
        "hypotheses": {
            "vacance_base_pct": 5.0,
            "vacance_best_pct": 3.0,
            "vacance_worst_pct": 12.0,
            "vacance_justification": (
                "Taux par défaut de la branche résidentielle. Le marché locatif toulonnais est très liquide "
                "(2 760 ventes d'appartements par an, des dizaines d'annonces actives), mais un T5 familial est "
                "un produit plus rare qu'un T2 : la vacance worst à 12 % correspond à deux mois et demi de "
                "vide entre deux locataires, ce qui arrive sur cette typologie"
            ),
            "frais_acquisition_euros": round(PRIX * NOTAIRE, 2),
            "frais_divers_euros": 0.0,
            "charges": {
                "taxe_fonciere_annuelle_euros": TF,
                "taxe_fonciere_commentaire": (
                    "ESTIMATION 1 500 €/an — la taxe n'est pas communiquée. À vérifier sur l'avis réel : "
                    "sur un T5 de 107 m² à Toulon, la fourchette va de 1 100 à 1 900 €/an"
                ),
                "charges_copro_annuelles_euros": COPRO,
                "charges_copro_commentaire": (
                    "ESTIMATION 3 600 €/an — charges non communiquées, alors que la copropriété compte "
                    "220 lots et un gardien. C'est le poste qui fait basculer le dossier : à 2 800 € la "
                    "lecture résiste un peu, à 4 500 € elle s'effondre. À exiger avant toute offre : trois "
                    "derniers appels de fonds, budget prévisionnel, procès-verbal de la dernière assemblée, "
                    "état daté, et le montant des travaux votés non encore appelés"
                ),
                "pno_annuelle_euros": 250.0,
                "pno_commentaire": "Assurance du logement, propriétaire non occupant.",
                "entretien_annuel_euros": 900.0,
                "entretien_commentaire": (
                    "Entretien courant, TEOM non récupérable, frais bancaires, provision d'impayés 1 % et "
                    "provision travaux 2,5 % des loyers. Poste calibré pour un appartement de 107 m² "
                    "dans une copropriété qui entretient déjà les parties communes"
                ),
                "comptabilite_annuelle_euros": 1200.0,
                "comptabilite_commentaire": "Comptabilité de la SCI à l'IS, un seul lot.",
            },
        },
        "analyse": {
            "branche": "residentiel",
            "type_operation": "locatif",
            "strategie_retenue": {
                "nom": "Conservation locative après rafraîchissement, logement entier loué vide",
                "code": "ld-nue",
                "lots": 1,
            },
            "strategies_explorees": [
                {
                    "strategie": "Location du T5 entier après rafraîchissement",
                    "lots": 1,
                    "rendement": "3,8 % net avant IS sur le prix de revient à 1 600 €/mois, 4,3 % à 1 750 €",
                    "faisabilite": "immédiate après travaux, marché locatif liquide",
                    "risque": "élevé — cash flow négatif de 511 €/mois sous crédit à 90 % sur 15 ans",
                },
                {
                    "strategie": "Colocation meublée à quatre chambres",
                    "lots": 4,
                    "rendement": "environ 3,9 % net avant IS, loyer brut 1 800 à 1 880 €/mois",
                    "faisabilite": "ameublement et gestion locative partagée, vacance plus fréquente",
                    "risque": "moyen — loyer brut supérieur de 15 % mais meublement, charges et rotation en face",
                },
                {
                    "strategie": "Rafraîchissement puis revente",
                    "lots": 1,
                    "rendement": "négatif : −7 400 € au prix médian de la tranche, +12 300 € seulement à 2 900 €/m²",
                    "faisabilite": "12 mois de portage, marché de revente très liquide",
                    "risque": "élevé — la marge n'existe qu'en haut de fourchette de revente, sans coussin",
                },
                {
                    "strategie": "Division en deux appartements",
                    "lots": 2,
                    "rendement": "non chiffré faute de plans, mais la valeur au m² progresse de 2 492 à "
                                 "2 644 €/m² entre 60-80 m² et 45-60 m²",
                    "faisabilite": "autorisation de l'assemblée générale et modification de l'état descriptif "
                                   "dans une copropriété de 220 lots : lourd",
                    "risque": "élevé — délai et incertitude juridique pour un gain de valeur faible",
                },
            ],
            "attractivite": [
                {
                    "dimension": "transports",
                    "score": 8,
                    "justification": (
                        "Toulon : gare TGV, réseau de bus dense, aéroport de Hyères-Toulon, A50 et A57. Le "
                        "Mourillon est un quartier balnéaire à dix minutes du centre par le bord de mer. "
                        "La desserte est le point fort du dossier"
                    ),
                },
                {
                    "dimension": "commerces",
                    "score": 8,
                    "justification": (
                        "Mourillon-Centre dispose de tout le commerce de proximité du quartier, avec les plages "
                        "et le marché. Un T5 familial y trouve sa clientèle naturelle"
                    ),
                },
                {
                    "dimension": "ecoles",
                    "score": 8,
                    "justification": "Écoles et collèges du quartier, lycées et université à Toulon.",
                },
                {
                    "dimension": "securite",
                    "score": 6,
                    "justification": (
                        "Le Mourillon est un quartier résidentiel et balnéaire plutôt préservé, mais Toulon "
                        "reste une grande ville : la résidence avec gardien est un vrai plus sur ce plan"
                    ),
                },
                {
                    "dimension": "demande_locative",
                    "score": 7,
                    "justification": (
                        "2 760 ventes d'appartements en 2025 et un loyer mesuré de 14,4 €/m²/mois : la demande "
                        "est profonde et documentée. Réserve sur la typologie : un T5 de 107 m² à 1 600 €/mois "
                        "s'adresse à un ménage avec revenus solides, segment plus étroit que le T2"
                    ),
                },
                {
                    "dimension": "dynamisme",
                    "score": 5,
                    "justification": (
                        "Médiane communale à 2 668 €/m², quartier Mourillon recherché et proche des plages, "
                        "mais le prix de l'annonce se situe 22 % sous la médiane de sa tranche, ce qui "
                        "s'explique d'abord par l'état annoncé « à rénover ». Aucun signal de décote de "
                        "quartier, mais aucun signal de hausse non plus"
                    ),
                },
            ],
            "risques": [
                {
                    "facteur": "Charges de copropriété d'une résidence de 220 lots avec gardien",
                    "severite": 4,
                    "detail": (
                        "Le montant des charges n'est pas communiqué. Dans une résidence gardiennée de "
                        "220 lots, le gardien, les ascenseurs, le chauffage des communs et les parties "
                        "communes de standing portent facilement la charge d'un 107 m² entre 2 800 et "
                        "4 500 €/an. C'est le poste qui décide du dossier : à 2 800 € la lecture résiste, à "
                        "4 500 € elle s'effondre. À exiger avant toute offre : trois derniers appels de fonds, "
                        "budget prévisionnel, procès-verbal d'assemblée, état daté et travaux votés non appelés"
                    ),
                },
                {
                    "facteur": "Rénovation annoncée sans le moindre chiffre",
                    "severite": 3,
                    "detail": (
                        "« Prévoir une rénovation » sur un appartement de 1961 jamais repris : électricité, "
                        "plomberie, salle d'eau, cuisine, sols, peintures, menuiseries. Fourchette 400 à "
                        "800 €/m², soit 43 000 à 86 000 €. La provision de 60 000 € retenue déplace le "
                        "rendement de 0,8 point à elle seule"
                    ),
                },
                {
                    "facteur": "Cash flow négatif sous crédit",
                    "severite": 4,
                    "detail": (
                        "Avec un loyer de 1 600 € et des charges de copropriété de 3 600 €, l'excédent brut "
                        "d'exploitation ressort à 11 318 €/an, soit 943 €/mois, quand la mensualité d'un prêt "
                        "à 90 % sur quinze ans à 3,7 % pèse 1 611 €. Il manque 511 € chaque mois, soit "
                        "6 100 €/an à sortir de la poche pendant quinze ans. Ce n'est pas un dossier "
                        "d'autofinancement"
                    ),
                },
                {
                    "facteur": "Plafond de loyer d'un T5",
                    "severite": 3,
                    "detail": (
                        "Le loyer mesuré de Toulon est de 14,4 €/m²/mois toutes surfaces confondues, mais il "
                        "est tiré vers le haut par les petites surfaces : les comparables de T5 de 100 à "
                        "116 m² se traitent entre 1 520 et 1 759 €, soit 10 à 16 €/m². Le loyer retenu à "
                        "1 600 € se situe déjà dans le haut de la fourchette pour la typologie, et le plafond "
                        "à 1 750 € suppose une rénovation complète"
                    ),
                },
                {
                    "facteur": "Prix d'entrée au premier quartile : décote ou signal",
                    "severite": 2,
                    "detail": (
                        "2 080 €/m², quand la tranche 80-150 m² de Toulon affiche 2 685 €/m² en médiane et "
                        "2 086 €/m² au premier quartile : l'annonce est au ras du quartile bas. Un écart de "
                        "cette taille sur un quartier balnéaire s'explique par l'état, mais il faut le "
                        "documenter : diagnostics, plans, et visite avec un artisan pour vérifier qu'aucun "
                        "désordre structurel ou d'humidité ne justifie la décote"
                    ),
                },
            ],
            "champs_manquants": [
                "montant des charges de copropriété, budget prévisionnel, état daté et procès-verbal d'assemblée",
                "surface Carrez et plan de l'appartement",
                "devis de rénovation par corps d'état et diagnostics techniques",
                "avis de taxe foncière réel et date du DPE",
                "travaux votés en copropriété et non encore appelés",
                "statut d'occupation et date de disponibilité du logement",
            ],
        },
    }


def main():
    spec = importlib.util.spec_from_file_location(
        "gen", os.path.join(ROOT, 'scripts', 'gen_fiches_2026-09-10.py'))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)

    rec = rec_toulon()
    r = engine.compute(rec)
    base = r
    note, verdict, _ = scoring.note_et_verdict(rec, base)
    revient = PRIX * 1.08 + TRAVAUX
    m15 = mens(PRIX * 0.9, TAUX, 15)
    m20 = mens(PRIX * 0.9, TAUX, 20)

    print(f"  EBE central : {eur(ebe(LOYER))} EUR/an | net avant IS {fr(ebe(LOYER)/revient*100,2)} %")
    print(f"  CF 15 ans : {eur(ebe(LOYER)/12 - m15)} EUR/mois | 20 ans : {eur(ebe(LOYER)/12 - m20)} EUR/mois")
    print(f"  note {note} / 10 | verdict {verdict}")

    def ligne(label, val, cls=""):
        c = f' class="{cls}"' if cls else ''
        return f'            <tr{c}><td>{label}</td><td class="num">{val}</td></tr>'

    def compte(loyer, copro, travaux, mois=15):
        e = ebe(loyer, copro, travaux)
        rev = PRIX * 1.08 + travaux
        amort = rev * 0.9 / 30
        is_ = max(0.0, e - amort - PRIX * 0.9 * TAUX) * 0.15
        m = mens(PRIX * 0.9, TAUX, mois)
        rows = [
            ligne("Loyer retenu après rafraîchissement", f"{eur(loyer)} €/mois"),
            ligne("Loyers bruts annuels", f"{eur(loyer*12)} €"),
            ligne("Vacance 5 %", f"-{eur(loyer*12*0.05)} €"),
            ligne("Charges de copropriété (estimation)", f"-{eur(copro)} €"),
            ligne("Taxe foncière (estimation)", f"-{eur(TF)} €"),
            ligne("Assurance, entretien, TEOM, frais bancaires", "-1 150 €"),
            ligne("Provision impayés 1 % et travaux 2,5 %", f"-{eur(loyer*12*0.035)} €"),
            ligne("Excédent brut d'exploitation", f"{eur(e)} €", "subtotal"),
            ligne("Amortissement (90 % du revient sur 30 ans)", f"{eur(amort)} €"),
            ligne("Intérêts d'emprunt année 1", f"{eur(PRIX*0.9*TAUX)} €"),
            ligne("IS 15 % année 1", f"{eur(is_)} €"),
            ligne("EBE mensuel", f"{eur(e/12)} €/mois", "highlight"),
            ligne(f"Mensualité prêt 90 % / {mois} ans / 3,7 %", f"-{eur(m)} €"),
            ligne("CASH FLOW après IS", f"{eur((e-is_)/12 - m)} €/mois", "highlight"),
            ligne("Rendement net avant IS sur le revient", f"{fr(e/rev*100,2)} %"),
        ]
        return "\n".join(rows)

    cartes = []
    for cle, loy, copro, trav, sus in (
            ("base", 1600.0, 3600.0, 60000.0, "Loyer 1 600 €, charges de copropriété 3 600 €, travaux 60 000 €"),
            ("optimiste", 1800.0, 2800.0, 40000.0, "Loyer 1 800 €, charges 2 800 €, travaux 40 000 €"),
            ("pessimiste", 1450.0, 4500.0, 86000.0, "Loyer 1 450 €, charges 4 500 €, travaux 86 000 €")):
        e = ebe(loy, copro, trav)
        cartes.append(f"""      <div class="projection-card scenario-{cle}">
        <h3>Scénario {cle.capitalize()}</h3>
        <p class="scenario-subtitle">{sus}</p>
        <table class="projection-table"><tbody>
{compte(loy, copro, trav)}
        </tbody></table>
      </div>""")

    # plafonds par loyer et par charge
    plaf = []
    for loy in (1500.0, 1600.0, 1750.0, 1800.0):
        for copro in (2800.0, 3600.0, 4500.0):
            e = ebe(loy, copro, TRAVAUX)
            cap5 = (e / 0.05 - TRAVAUX) / (1 + NOTAIRE)
            cap15 = (e / 12) / (0.9 * mens(1.0, TAUX, 15))
            plaf.append(f'        <tr><td>{eur(loy)} €</td><td>{eur(copro)} €</td><td class="num">{eur(e)} €</td>'
                        f'<td class="num">{eur(cap5)} €</td><td class="num">{eur(cap15)} €</td></tr>')
    plaf_html = "\n".join(plaf)

    rev = []
    for trav in (40000.0, 60000.0, 86000.0):
        for tx in (2400.0, 2685.0, 2900.0):
            revient = PRIX * 1.08 + trav
            net = SURF * tx * 0.95
            pv = net - revient
            is_ = max(0.0, pv) * 0.15
            rev.append(f'        <tr><td>{eur(trav)} €</td><td>{tx:,.0f} €/m²</td>'.replace(',', ' ') +
                       f'<td class="num">{eur(SURF*tx)} €</td><td class="num">{eur(pv-is_)} €</td>'
                       f'<td class="num">{fr((pv-is_)/revient*100)} %</td></tr>')
    rev_html = "\n".join(rev)

    lecture = (
        "2 080 €/m² au Mourillon, quand la tranche 80 à 150 m² de Toulon affiche 2 685 €/m² en médiane : "
        "le prix d'entrée est objectivement bas, c'est le premier quartile du marché, et le dossier mérite "
        "d'être ouvert pour cette raison. Mais un achat bon marché ne fait pas un rendement, et c'est ici que "
        "le dossier se referme. Avec un loyer de 1 600 € — le haut de la fourchette des T5 de 100 à 116 m² "
        "relevés à Toulon — et des charges de copropriété de 3 600 €, l'excédent brut d'exploitation ressort à "
        "11 318 €/an, soit 943 €/mois, pour une mensualité de 1 611 € sur quinze ans. Il manque 511 € par "
        "mois, et le rendement net avant IS plafonne à 3,8 % du prix de revient. Pour tenir nos 5 %, il "
        "faudrait acheter 154 000 €, soit 69 000 € sous le prix affiché. Les deux portes de sortie sont "
        "fermées : la colocation à quatre chambres apporte 15 % de loyer brut en plus mais du meublement et "
        "de la rotation en face, sans changer de camp ; et la revente après rafraîchissement perd de l'argent "
        "au prix médian de la tranche. Reste une inconnue qui pèse plus que tout : le montant réel des charges "
        "de la copropriété de 220 lots avec gardien. Si elles sont à 2 800 €, la lecture résiste un peu ; à "
        "4 500 €, elle s'effondre. C'est la première pièce à réclamer."
    )

    gen.LECTURE[SLUG] = lecture
    gen.RECS[SLUG] = rec
    gen.CONF[SLUG] = dict(
        titre_court="T5 de 107 m², résidence de standing — Mourillon, Toulon (83000)",
        adresse="Mourillon-Centre, Toulon (83000) — appartement T5 de 107,2 m² au 1er étage d'une résidence "
                "de standing de 220 lots avec gardien et ascenseur — adresse exacte non communiquée",
        date_fr="22 septembre 2026",
        source="SeLoger — annonce 269Y5Y2G6A9A (Agence de l'Avenir, 249 boulevard de Bazeilles à Toulon, "
               "SIRET 41909558300011, M. Kévin Le Cocq, réf. va2026017)",
        url=URL,
        badge="Location nue",
        strategie="Rafraîchissement puis conservation locative — variante colocation et revente chiffrées",
        fiscal_note="SCI à l'IS (15 %), amortissement de 90 % du prix de revient sur 30 ans",
        lat="43.1140", lon="5.9380",
        quartier="Mourillon-Centre, Toulon (83000) — quartier balnéaire, plages et commerces à pied, centre-ville à 10 minutes",
        intro_attr=(
            "Le Mourillon est le quartier balnéaire de Toulon : plages, commerces de proximité, marché, "
            "et le centre-ville à dix minutes par le bord de mer. Toulon offre un marché d'une profondeur rare "
            "en Provence : <strong>2 760 ventes d'appartements en 2025</strong> selon la base DVF, une médiane "
            "à <strong>2 668 €/m²</strong>, et sur la tranche 80 à 150 m² qui correspond à ce bien, "
            "450 ventes et une médiane de <strong>2 685 €/m²</strong>. Le loyer mesuré est de "
            "<strong>14,4 €/m²/mois</strong>, pour un rendement brut communal de 6,5 %. C'est un marché "
            "d'usage : on y achète une adresse et une qualité de vie, pas un rendement. Ce bien s'affiche "
            "22 % sous la médiane de sa tranche, ce qui justifie de l'instruire — encore faut-il que les "
            "charges suivent."
        ),
        profil=(
            "un investisseur patrimonial qui cherche une adresse balnéaire solide pour un couple avec enfants, "
            "ou un acquéreur qui veut habiter le Mourillon : 107 m², trois chambres, deux balcons, une cave, "
            "un ascenseur, un gardien. Ce n'est pas un dossier de rendement : à 3,8 % net avant IS et un cash "
            "flow négatif de 511 €/mois sous crédit, il ne s'autofinance pas"
        ),
        concl_attr=(
            "Adéquation moyenne (6,5/10). Les atouts sont réels : première quartile de prix sur un quartier "
            "balnéaire, marché locatif et marché de revente très liquides, résidence gardiennée de standing, "
            "DPE D sans échéance réglementaire. Trois éléments ferment le dossier. D'abord les "
            "<strong>charges de copropriété</strong> : 220 lots avec gardien, un montant non communiqué qui "
            "peut aller de 2 800 à 4 500 €/an. Ensuite le <strong>loyer plafonné</strong> d'un T5 : les "
            "comparables de la typologie se traitent entre 1 520 et 1 759 €, et le loyer retenu à 1 600 € est "
            "déjà dans le haut de la fourchette. Enfin le <strong>cash flow</strong> : 943 € d'EBE mensuel "
            "contre 1 611 € de mensualité"
        ),
        intro_strat=(
            "Quatre lectures ont été testées : la location du T5 entier après rafraîchissement, la colocation "
            "meublée à quatre chambres, la revente après rafraîchissement, et la division en deux "
            "appartements. Aucune n'atteint notre seuil de 5 % net avant IS."
        ),
        rationale=(
            "Le dossier a un attrait évident : <strong>2 080 €/m² au Mourillon</strong>, quand la tranche "
            "80 à 150 m² de Toulon affiche 2 685 €/m² en médiane. Ramené à la valeur de marché, le bien paraît "
            "acheté 55 000 € sous sa valeur. Mais les chiffres d'exploitation ne suivent pas. Avec un loyer "
            "de 1 600 € et des charges de copropriété de 3 600 €, l'EBE ressort à "
            "<strong>11 318 €/an, soit 943 €/mois</strong>, pour une mensualité de <strong>1 611 €</strong> "
            "sur quinze ans : il manque <strong>511 € par mois</strong>, soit 6 100 €/an à sortir de la poche "
            "pendant quinze ans. Le rendement net avant IS plafonne à <strong>3,8 %</strong> du prix de "
            "revient, contre les 5 % de la doctrine, et à 4,3 % seulement avec un loyer de 1 750 €.<br><br>"
            "Les plafonds sont sans ambiguïté. Pour tenir 5 % net avec les loyers retenus, il faudrait "
            "acheter <strong>154 000 €</strong> ; pour que le bien couvre sa mensualité sur quinze ans, "
            "<strong>145 000 €</strong>, et 178 000 € sur vingt ans. Le prix affiché est donc 45 à 70 % "
            "au-dessus de notre capacité.<br><br>"
            "Les deux portes de sortie sont fermées. La <strong>colocation</strong> à quatre chambres se "
            "commercialise 420 à 470 € par chambre au Mourillon, soit 1 800 à 1 880 € par mois : 15 % de "
            "loyer brut en plus, mais du meublement, une vacance plus fréquente et une gestion plus lourde "
            "en face — le rendement net reste sous 4 %. La <strong>revente</strong> après rafraîchissement "
            "perd 7 400 € au prix médian de la tranche et ne dégage 12 300 € qu'à 2 900 €/m², c'est-à-dire "
            "en haut de fourchette : il n'y a aucun coussin."
        ),
        identite=[
            ("Adresse", "Mourillon-Centre, Toulon (83000) — quartier balnéaire, plages et commerces à pied, "
                        "adresse exacte non communiquée"),
            ("Vendeur / intermédiaire", "Agence de l'Avenir, 249 boulevard de Bazeilles à Toulon "
                                        "(SIRET 41909558300011, carte professionnelle 3518), M. Kévin Le Cocq "
                                        "— annonce SeLoger 269Y5Y2G6A9A, référence va2026017"),
            ("Composition", "T5 de 107,2 m² au 1er étage sur 20 : hall, séjour double ouvrant sur balcon, "
                            "cuisine avec balcon, cellier, trois chambres dont deux sur balcon, salle d'eau, "
                            "WC séparé, cave. Ascenseur, résidence avec gardien, exposition ouest"),
            ("Statut", "<strong>Copropriété de 220 lots</strong> avec gardien et ascenseur. Charges non "
                       "communiquées : c'est le poste à vérifier en priorité, avec les trois derniers appels "
                       "de fonds, le budget prévisionnel, l'état daté et les travaux votés non appelés"),
            ("Surfaces", "107,2 m² annoncés, 5 pièces, 3 chambres. Surface Carrez non précisée dans l'annonce"),
            ("DPE / GES", "<strong>DPE D / GES D</strong>, chauffage central au gaz, immeuble de 1961. "
                          "Aucune échéance réglementaire de location, mais la date du diagnostic n'est pas "
                          "communiquée. Facture énergétique annoncée entre 1 810 et 2 470 €/an"),
            ("Prix affiché", "<strong>223 000 €</strong>, soit 2 080 €/m², honoraires à la charge du vendeur. "
                             "Premier quartile de la tranche 80-150 m² de Toulon (médiane 2 685 €/m²)"),
            ("Valeur retenue", "<strong>288 000 €</strong> (2 685 €/m²), fourchette 257 000 € (2 400 €/m², "
                               "rafraîchissement léger) à 311 000 € (2 900 €/m², rénovation complète) — "
                               "mutations DVF 2025 de Toulon"),
            ("Loyers retenus", "<strong>1 600 €/mois</strong> (14,9 €/m²) après rafraîchissement. "
                               "Comparables : T5 de 3 chambres à 1 520 €, T5 à 1 609 € hors charges, T5 à "
                               "1 759 € dont 150 € de charges, T5 de 100 m² à 1 600 €. Loyer mesuré de la "
                               "commune : 14,4 €/m²/mois. Colocation : 420 à 470 € par chambre, soit 1 800 à "
                               "1 880 € pour quatre"),
            ("Travaux", "<strong>60 000 € retenus (560 €/m²)</strong>, fourchette 43 000 à 86 000 €. "
                        "« Prévoir une rénovation » selon l'annonce : électricité, plomberie, salle d'eau, "
                        "cuisine, sols, peintures. Aucun devis, aucun plan, aucun diagnostic joint"),
            ("Taxe foncière", "<strong>Estimée 1 500 €/an</strong> — avis non communiqué, fourchette 1 100 à "
                              "1 900 €/an pour un T5 de 107 m² à Toulon"),
            ("Charges de copropriété", "<strong>Estimées 3 600 €/an</strong> — non communiquées, alors que la "
                                       "copropriété compte 220 lots avec gardien. C'est le poste qui décide du "
                                       "dossier : à 2 800 € la lecture résiste, à 4 500 € elle s'effondre"),
            ("Prix de revient", "<strong>300 840 €</strong> = prix 223 000 € + frais 17 840 € + travaux "
                                "60 000 €, plus la mensualité de 1 611 € sur quinze ans"),
        ],
        stance=(
            "<strong>On fuit au prix affiché.</strong> Ce n'est pas une question de qualité du bien : le "
            "Mourillon, la résidence gardiennée, les 107 m², les trois chambres, le DPE D, tout cela tient "
            "debout, et le prix d'entrée au premier quartile de la tranche méritait qu'on l'ouvre. Mais "
            "l'exploitation ne passe pas. <strong>943 € d'excédent brut mensuel contre 1 611 € de "
            "mensualité</strong> : il manque 511 € chaque mois pendant quinze ans. Le rendement net avant IS "
            "plafonne à <strong>3,8 %</strong>, quand notre seuil est de 5 %, et il faudrait acheter "
            "<strong>154 000 €</strong> pour l'atteindre — 69 000 € sous le prix demandé.<br><br>"
            "<strong>Les deux sorties de secours sont fermées.</strong> La colocation à quatre chambres "
            "apporte 1 800 à 1 880 € de loyer brut, mais du meublement, de la rotation et une gestion "
            "partagée en face : le net reste sous 4 %. La revente après rafraîchissement perd 7 400 € au prix "
            "médian de la tranche et ne gagne 12 300 € qu'à 2 900 €/m², c'est-à-dire sans coussin. "
            "Il n'y a donc ni lecture patrimoniale conforme, ni lecture marchand de biens.<br><br>"
            "<strong>Une seule chose pourrait rouvrir le dossier</strong>, et elle vaut d'être demandée "
            "d'abord : le montant réel des charges de copropriété. Si elles sont à 2 800 € plutôt qu'à "
            "3 600 €, et si le loyer atteint 1 750 € après rénovation complète, le rendement net remonte à "
            "4,6 % — toujours sous la doctrine, mais l'écart ne serait plus rédhibitoire. En dessous de "
            "180 000 € et avec des charges documentées sous 3 000 €, on en reparlerait. À 223 000 €, non."
        ),
        prix_plafond=(
            "<strong>154 000 €</strong> pour tenir 5 % net avant IS avec un loyer de 1 600 € et des charges de "
            "copropriété de 3 600 €, <strong>145 000 €</strong> pour un cash flow neutre sur quinze ans et "
            "178 000 € sur vingt ans. Repères : <strong>134 000 €</strong> à 1 500 € de loyer, "
            "<strong>185 000 €</strong> à 1 750 €, <strong>195 000 €</strong> à 1 800 €. Et si les charges "
            "s'établissent à 2 800 € au lieu de 3 600 €, la capacité de prix remonte de 20 000 € environ. "
            "Aucun de ces plafonds n'approche les 223 000 € demandés."
        ),
        leviers=[
            "Le loyer est le vrai plafond du dossier : un T5 se loue moins cher au m² qu'un T2, et les "
            "comparables de 100 à 116 m² à Toulon se traitent entre 1 520 et 1 759 €, soit 10 à 16 €/m². "
            "Le loyer retenu de 1 600 € est déjà dans le haut de la fourchette avant même de parler travaux",
            "Les charges de copropriété sont l'inconnue qui décide de tout : 220 lots avec gardien et "
            "ascenseur, un montant non communiqué. Exiger les trois derniers appels de fonds, le budget "
            "prévisionnel, l'état daté, le procès-verbal de la dernière assemblée et la liste des travaux "
            "votés non encore appelés",
            "Le cash flow est négatif de 511 €/mois sous crédit à 90 % sur quinze ans, soit 6 100 €/an sur "
            "quinze ans. Ce n'est pas un dossier d'autofinancement, et il ne faut pas l'acheter en espérant "
            "que la hausse du marché le rattrape",
            "La colocation à quatre chambres ne change pas de camp : 1 800 à 1 880 € de loyer brut contre "
            "1 600 €, mais du meublement, une vacance plus fréquente, des charges locatives incluses et une "
            "gestion partagée. Le gain brut de 15 % se dissout dans l'exploitation",
            "La revente après rafraîchissement ne laisse aucun coussin : −7 400 € au prix médian de la "
            "tranche (2 685 €/m²) avec 40 000 € de travaux, +12 300 € seulement à 2 900 €/m², soit en haut "
            "de fourchette. Un marchand de biens n'achète pas sans coussin",
            "La division en deux appartements se heurte à la copropriété : autorisation de l'assemblée "
            "générale et modification de l'état descriptif dans un immeuble de 220 lots, pour un gain de "
            "valeur de 2 492 à 2 644 €/m² entre les tranches 60-80 m² et 45-60 m². Le jeu n'en vaut pas la "
            "chandelle",
            "Le prix d'entrée est au premier quartile de la tranche (2 080 €/m² contre 2 086 €/m² de Q1) : "
            "ce n'est pas une erreur d'annonce, c'est le prix que le marché donne à un T5 de 1961 à rénover. "
            "La décote n'est pas un levier de négociation, elle est le prix de l'état",
            "Si le dossier revient sur la table, la seule question à poser avant tout est celle des charges. "
            "Avec des charges sous 3 000 € et un prix sous 180 000 €, la lecture patrimoniale redevient "
            "défendable à 4,5 %. Au-dessus, non",
        ],
        meta=[
            "<strong>Régime fiscal retenu :</strong> SCI à l'IS (15 %), amortissement de 90 % du prix de "
            "revient sur 30 ans. L'amortissement et les intérêts absorbent le résultat les premières années",
            "<strong>Frais d'acquisition :</strong> 17 840 € (8 % du prix affiché), honoraires à la charge du "
            "vendeur",
            "<strong>Loyers :</strong> 1 600 €/mois retenus (14,9 €/m²), alors que le loyer mesuré de la "
            "commune est de 14,4 €/m² et que les comparables de la typologie vont de 1 520 à 1 759 €. "
            "Aucun loyer en place : le bien est vide",
            "<strong>Charges retenues :</strong> copropriété estimée 3 600 €/an (non communiquée), taxe "
            "foncière estimée 1 500 €, assurance 250 €, entretien, TEOM, frais bancaires et provisions "
            "1 150 €, comptabilité 1 200 €. Aucun poste laissé à zéro, et le poste copropriété est signalé "
            "comme la variable décisive",
            "<strong>Financement :</strong> 90 % du prix sur 15 ans à 3,7 %, soit 1 611 €/mois. Fonds propres "
            "à amener 81 640 € (apport 10 %, frais et travaux)",
            "<strong>Contrôles à faire avant toute offre :</strong> charges de copropriété sur trois exercices, "
            "budget prévisionnel, état daté, procès-verbal d'assemblée, travaux votés non appelés ; surface "
            "Carrez et plan ; devis de rénovation et diagnostics techniques ; avis de taxe foncière ; date du "
            "DPE ; statut d'occupation et date de disponibilité",
            "<strong>Point de méthode :</strong> le prix d'entrée sous la médiane du quartier ne suffit jamais "
            "à faire un rendement. Ici, acheter 22 % sous la médiane de la tranche laisse quand même un cash "
            "flow négatif de 511 €/mois : c'est le loyer et les charges qui commandent, pas la décote",
            "<strong>Rappel de marché (sources au 22/09/2026) :</strong> Toulon, 2 760 ventes d'appartements "
            "en 2025, médiane 2 668 €/m², Q1 2 093 €/m², Q3 3 406 €/m² ; tranche 80-150 m², 450 ventes, "
            "médiane 2 685 €/m² ; loyer mesuré 14,4 €/m²/mois (ANIL 2025), rendement brut communal 6,5 % ; "
            "T5 relevés entre 1 520 et 1 759 € ; colocation au Mourillon 420 à 470 € par chambre",
        ],
    )

    c = gen.CONF[SLUG]
    e_base = ebe(LOYER)
    html = gen.TEMPLATE.format(
        titre_court=c['titre_court'], adresse=c['adresse'], date_fr=c['date_fr'],
        source=c['source'], url=c['url'], badge=c['badge'], strategie=c['strategie'],
        fiscal_note=c['fiscal_note'],
        prix=eur(PRIX),
        surface=f"{SURF:.0f} m²",
        prix_m2=f"{eur(PRIX/SURF)} €/m²",
        revient=eur(revient),
        valeur=eur(288000),
        revenus=eur(LOYER),
        rdt_revient=fr(e_base / revient * 100, 2), rdt_valeur=fr(e_base / 288000 * 100, 2),
        note=fr(note), note_cls=fr(note).replace(',', '-'),
        lat=c['lat'], lon=c['lon'], quartier=c['quartier'],
        intro_attr=c['intro_attr'], profil=c['profil'], concl_attr=c['concl_attr'],
        attrs=gen.attr_html(rec), intro_strat=c['intro_strat'], strats=gen.strategy_html(rec),
        rationale=c['rationale'], identite=gen.identite_html(c['identite']),
        projections=f"""  <section class="financial-projections">
    <h2>Compte d'exploitation locatif — prix affiché {eur(PRIX)} €, SCI à l'IS</h2>
    <p class="attractiveness-intro">{lecture}</p>
    <div class="projections-grid">
{chr(10).join(cartes)}
    </div>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Ce que le prix affiché laisse comme marge.</strong> Le compte est simple : à {eur(LOYER)} € de loyer et {eur(COPRO)} € de charges de copropriété, l'excédent brut d'exploitation ressort à {eur(e_base)} €/an, soit {eur(e_base/12)} €/mois, pour une mensualité de {eur(m15)} € sur quinze ans. Il manque <strong>{eur(m15-e_base/12)} € par mois</strong>. Pour tenir 5 % net avant IS, il faudrait acheter <strong>{eur((e_base/0.05-TRAVAUX)/1.08)} €</strong> ; pour que le bien couvre sa mensualité sur quinze ans, <strong>{eur((e_base/12)/(0.9*mens(1.0,TAUX,15)))} €</strong>. Aucun de ces plafonds n'approche les 223 000 € demandés.</p>
    </div>
    <h3>Plafonds de prix selon le loyer et les charges de copropriété</h3>
    <table class="projection-table compare">
      <thead><tr><th>Loyer retenu</th><th>Charges copro</th><th class="num">EBE</th><th class="num">Achat max (5 % net)</th><th class="num">Achat max (cash flow neutre 15 ans)</th></tr></thead>
      <tbody>
{plaf_html}
      </tbody>
    </table>
    <h3>Piste revente : rafraîchir puis vendre</h3>
    <table class="projection-table compare">
      <thead><tr><th>Travaux</th><th>Prix de revente</th><th class="num">Prix de vente</th><th class="num">Plus-value nette après IS</th><th class="num">ROI</th></tr></thead>
      <tbody>
{rev_html}
      </tbody>
    </table>
    <p class="attractiveness-intro">Repères de méthode : frais d'acquisition {eur(PRIX*NOTAIRE)} € (8 %), honoraires de revente 5 %, prêt à 90 % sur 15 ans à 3,7 % soit {eur(m15)} €/mois, SCI à l'IS avec amortissement de 90 % du prix de revient sur 30 ans, vacance 5 % / 3 % / 12 %, provisions d'impayés 1 % et travaux 2,5 %, taxe foncière estimée {eur(TF)} €/an, charges de copropriété estimées {eur(COPRO)} €/an. Valeur retenue 288 000 € (2 685 €/m²), ancrée sur la médiane DVF 2025 de la tranche 80-150 m² de Toulon.</p>
  </section>""",
        risques=gen.risques_html(rec),
        verdict_cls={"acheter": "buy", "negocier": "nego", "fuir": "pass"}.get(verdict, "nego"),
        stance=c['stance'], prix_plafond=c['prix_plafond'],
        leviers=gen.leviers_html(c['leviers']),
        meta="\n".join(f"      <p>{m}</p>" for m in c['meta']),
    )
    d = os.path.join(ROOT, 'analyses', SLUG)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  fiche ecrite : {len(html):,} octets dans {SLUG}")

    p = os.path.join(ROOT, 'analyses', 'analyses.json')
    data = json.load(open(p, encoding='utf-8'))
    if SLUG in data:
        data.pop(SLUG)
    lst = data.get('analyses')
    if isinstance(lst, list):
        lst = [x for x in lst if x.get('slug') != SLUG]
        lst.append(rec)
        data['analyses'] = lst
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  analyses.json : {len(data['analyses'])} fiches")


if __name__ == '__main__':
    main()
