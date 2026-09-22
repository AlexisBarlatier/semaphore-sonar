#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche Toulon Saint-Jean — T4 de 77,45 m2, 160 000 EUR, DPE C, charges de copro communiquees.
Branche residentielle (SCI a l'IS). Le dossier ne passe pas en location nue, il passe en
colocation etudiante a quatre chambres : c'est la colonne qui decide du verdict.
"""
import importlib.util
import json
import os
import sys

ROOT = '/home/alexis-barlatier/Documents/Semaphore-sonar'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from analyse_app import engine, scoring  # noqa: E402

SLUG = "2026-09-22-appartement-t4-saint-jean-toulon"
URL = "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/toulon-83000/26HP2UMPWI2F"

PRIX = 160000.0
NOTAIRE = 0.08
SURF = 77.45
TRAVAUX = 20000.0
COPRO = 2500.0
TF = 1200.0
TAUX = 0.037


def eur(v):
    return f"{v:,.0f}".replace(',', ' ')


def fr(v, dec=1):
    return f"{v:.{dec}f}".replace('.', ',')


def mens(cap, taux, an):
    i = taux / 12
    n = an * 12
    return cap * i / (1 - (1 + i) ** -n)


def calc(loyer, vac=0.05, coloc=False, travaux=TRAVAUX):
    brut = loyer * 12
    autres = TF + 200 + 600 + (2500.0 if coloc else 0.0)
    charges = COPRO + autres + brut * 0.035
    e = brut * (1 - vac) - charges
    rev = PRIX * (1 + NOTAIRE) + travaux
    m = mens(PRIX * 0.9, TAUX, 15)
    is_ = max(0.0, e - rev * 0.9 / 30 - PRIX * 0.9 * TAUX) * 0.15
    return dict(ebe=e, revient=rev, rdt=e / rev * 100, cf=(e - is_) / 12 - m,
                cap5=(e / 0.05 - travaux) / (1 + NOTAIRE),
                cap15=(e / 12) / (0.9 * mens(1.0, TAUX, 15)))


def rec_toulon_sj():
    return {
        "slug": SLUG,
        "date_analyse": "2026-09-22",
        "date_maj": None,
        "titre": "Appartement T4 de 77,45 m² au 7e étage, quartier Saint-Jean — Toulon (83000)",
        "bien": {
            "type_bien": "appartement",
            "sous_type": None,
            "type_detail": (
                "T4 traversant de 77,45 m² au 7e étage d'une copropriété fermée de 144 lots, avec ascenseur "
                "et stationnement dans la résidence. Deux chambres plus un salon/salle à manger pouvant "
                "recevoir une troisième chambre, dressing, cuisine indépendante avec loggia, salle de bains, "
                "WC séparé, balcon. Double vitrage, chauffage central au gaz, immeuble de 1970, état déclaré "
                "« entretenu ». DPE C, GES C. Quartier Saint-Jean, à proximité des facultés, du campus Porte "
                "d'Italie et des commodités"
            ),
            "neuf": False,
            "adresse": {
                "texte": "Quartier Saint-Jean, Toulon (83000) — à proximité immédiate du campus Porte d'Italie "
                         "et de la faculté de droit, adresse exacte non communiquée",
                "ville": "Toulon",
                "code_postal": "83000",
            },
            "surfaces": {
                "texte": "77,45 m² annoncés, 4 pièces, 3 chambres possibles (2 chambres + un salon "
                         "transformable). Surface Carrez non précisée dans l'annonce",
                "carrez_m2": 77.45,
            },
            "lots": {
                "count": 1,
                "surface_par_lot_m2": None,
                "nature": "Un lot d'habitation dans une copropriété de 144 lots, avec stationnement",
                "lots_distincts": 1,
            },
            "copro": {
                "charges_annuelles_euros": COPRO,
                "charges_source": (
                    "Copropriété de 144 lots, charges COMMUNIQUÉES à 2 500 €/an et aucune procédure collective "
                    "en cours (fiche SeLoger). C'est une exception appréciable sur ce type de dossier : le "
                    "poste le plus incertain des autres dossiers est ici documenté. À confirmer sur les trois "
                    "derniers appels de fonds et le procès-verbal de la dernière assemblée, notamment pour les "
                    "travaux votés non encore appelés"
                ),
            },
            "travaux": {
                "montant_euros": TRAVAUX,
                "nature": (
                    "État déclaré « entretenu », DPE C : les gros postes (couverture, façade, réseaux de "
                    "l'immeuble) sont derrière, pas devant. Provision retenue 20 000 € (258 €/m²) pour une "
                    "remise au standard locatif — peintures, sols, cuisine, salle de bains, électricité "
                    "partielle. Aucun devis joint. En variante colocation, ajouter l'ameublement et "
                    "l'équipement des quatre chambres, soit 15 000 à 25 000 €"
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
                "160 000 €, soit 2 066 €/m², honoraires à la charge du vendeur, en exclusivité. La tranche "
                "60-80 m² de Toulon affiche 2 492 €/m² en médiane sur 857 ventes en 2025 : l'annonce est 17 % "
                "en dessous. Facture énergétique annoncée entre 1 180 et 1 650 €/an, soit la plus basse des "
                "dossiers toulonnais examinés cette semaine"
            ),
        },
        "marche": {
            "valeur": {
                "basse_euros": 180000.0,
                "haute_euros": 210000.0,
                "retenue_euros": 193000.0,
                "source": (
                    "Mutations DVF 2025 de Toulon (2 760 ventes d'appartements, médiane 2 668 €/m²). La tranche "
                    "60-80 m², qui correspond exactement au bien, compte 857 ventes pour une médiane de "
                    "2 492 €/m² et un premier quartile à 1 955 €/m². Valeur retenue 193 000 € (2 492 €/m²), "
                    "fourchette 180 000 à 210 000 € selon l'état. L'annonce à 2 066 €/m² se situe 17 % sous la "
                    "médiane de sa tranche, un écart qui s'explique par l'étage élevé et un T4 à rénover "
                    "légèrement, pas par un défaut de quartier"
                ),
                "confiance": "bonne",
            },
            "loyers": [
                {
                    "lot": "Quatre chambres meublées — colocation étudiante (stratégie retenue)",
                    "quantite": 4,
                    "loyer_mensuel_euros": 450.0,
                    "occupe": False,
                    "note": (
                        "Bien vide : ce loyer est un loyer retenu après remise au standard, pas un revenu "
                        "acquis. Chambres meublées dans un T4 proche des facultés : 410 à 480 € par chambre à "
                        "Toulon, avec de nombreuses colocations de trois et quatre chambres dans le secteur "
                        "Saint-Jean / Porte d'Italie / Saint-Roch. Retenu 450 € par chambre pour quatre "
                        "chambres, soit 1 800 €/mois. Une seule ligne de revenu est saisie : la variante "
                        "location nue du T4 entier ne se cumule pas avec celle-ci, elle s'y substitue — "
                        "à 1 000 à 1 100 €/mois, elle donne 3,4 à 3,9 % net avant IS et un plafond d'achat "
                        "de 101 000 à 122 000 €. La quatrième chambre suppose de sacrifier le séjour : "
                        "c'est la condition à vérifier sur le plan, et le point faible du scénario"
                    ),
                },
            ],
            "notes": (
                "Le dossier se joue entièrement sur la typologie d'exploitation. En location nue, un T4 de "
                "77 m² se loue 1 000 à 1 100 € par mois : l'excédent brut d'exploitation ressort entre 6 480 "
                "et 7 578 €, le rendement net avant IS entre 3,4 et 3,9 %, et le prix qui tient notre seuil "
                "de 5 % tombe à 101 000-122 000 €, très loin des 160 000 € demandés. En colocation meublée à "
                "quatre chambres à 450 €, le loyer brut passe à 21 600 € par an : le rendement net monte à "
                "5,6 %, le cash flow devient quasi neutre sous crédit, et le prix qui tient 5 % remonte à "
                "182 700 € — au-dessus du prix affiché. Le passage de l'un à l'autre n'est pas une nuance "
                "d'exploitation, c'est un changement de dossier"
            ),
        },
        "hypotheses": {
            "vacance_base_pct": 5.0,
            "vacance_best_pct": 3.0,
            "vacance_worst_pct": 12.0,
            "vacance_justification": (
                "Taux par défaut de la branche résidentielle pour la location nue. En colocation, la vacance "
                "est plus élevée : chaque chambre tourne séparément et l'été est un mois creux pour les "
                "étudiants, d'où le taux de 8 % retenu dans la variante colocation, et 12 % en hypothèse "
                "défavorable"
            ),
            "frais_acquisition_euros": round(PRIX * NOTAIRE, 2),
            "frais_divers_euros": 0.0,
            "charges": {
                "taxe_fonciere_annuelle_euros": TF,
                "taxe_fonciere_commentaire": "ESTIMATION 1 200 €/an — avis non communiqué, fourchette 900 à 1 500 €/an pour 77 m² à Toulon",
                "charges_copro_annuelles_euros": COPRO,
                "charges_copro_commentaire": (
                    "2 500 €/an COMMUNIQUÉS par l'annonce, copropriété de 144 lots, aucune procédure "
                    "collective en cours. C'est le chiffre le plus fiable de tous les dossiers toulonnais "
                    "examinés cette semaine : à confirmer sur les appels de fonds, mais il n'y a pas "
                    "d'inconnue majeure de ce côté"
                ),
                "pno_annuelle_euros": 200.0,
                "pno_commentaire": "Assurance du logement, propriétaire non occupant.",
                "entretien_annuel_euros": 600.0,
                "entretien_commentaire": (
                    "Entretien courant, TEOM non récupérable et frais bancaires, hors provisions d'impayés "
                    "et travaux qui sont calculées en pourcentage des loyers (3,5 %). En variante colocation, "
                    "ajouter l'ameublement et les fluides des parties communes, comptés à 2 500 €/an"
                ),
                "comptabilite_annuelle_euros": 1200.0,
                "comptabilite_commentaire": "Comptabilité de la SCI à l'IS. À mutualiser si plusieurs lots dans la même structure.",
            },
        },
        "analyse": {
            "branche": "residentiel",
            "type_operation": "locatif",
            "strategie_retenue": {
                "nom": "Colocation meublée à quatre chambres pour étudiants, proche des facultés",
                "code": "colocation",
                "lots": 4,
            },
            "strategies_explorees": [
                {
                    "strategie": "Location nue du T4 entier",
                    "lots": 1,
                    "rendement": "3,4 à 3,9 % net avant IS selon le loyer (1 000 à 1 100 €)",
                    "faisabilite": "immédiate après une remise au standard de 20 000 €",
                    "risque": "élevé — cash flow négatif de 412 à 504 €/mois sous crédit à 90 % sur 15 ans",
                },
                {
                    "strategie": "Colocation meublée à trois chambres",
                    "lots": 3,
                    "rendement": "3,5 % net avant IS : le meublement et les fluides absorbent le gain de loyer",
                    "faisabilite": "trois chambres sans toucher au séjour, configuration la plus confortable",
                    "risque": "moyen — cash flow encore négatif de 432 €/mois",
                },
                {
                    "strategie": "Colocation meublée à quatre chambres",
                    "lots": 4,
                    "rendement": "5,6 % net avant IS à 450 € la chambre, 6,2 % à 480 €",
                    "faisabilite": "suppose de sacrifier le séjour pour créer la quatrième chambre : à vérifier sur le plan",
                    "risque": "moyen — cash flow quasi neutre (−37 €/mois) à positif (+53 €/mois), mais rotation étudiante",
                },
                {
                    "strategie": "Location meublée d'un seul bail (bail mobilité ou étudiant)",
                    "lots": 1,
                    "rendement": "non retenu — le meublé d'un T4 entier ne franchit pas la barre des 4 %",
                    "faisabilite": "simple, un seul bail à gérer, vacance estivale assumée",
                    "risque": "élevé — la typologie T4 est déjà plafonnée en loyer, le meublé n'y change rien",
                },
            ],
            "attractivite": [
                {
                    "dimension": "transports",
                    "score": 8,
                    "justification": "Toulon : réseau de bus dense, gare TGV, aéroport de Hyères-Toulon, A50 et A57. Le quartier Saint-Jean est bien desservi et proche du campus.",
                },
                {
                    "dimension": "commerces",
                    "score": 7,
                    "justification": "Commerces de proximité du quartier Saint-Jean, centre-ville de Toulon à quelques minutes, et la vie étudiante du secteur Porte d'Italie.",
                },
                {
                    "dimension": "ecoles",
                    "score": 9,
                    "justification": "C'est le point fort du dossier : faculté de droit, campus Porte d'Italie, ISEN et écoles d'ingénieurs à proximité immédiate. La demande étudiante est structurelle et renouvelée chaque année.",
                },
                {
                    "dimension": "securite",
                    "score": 6,
                    "justification": "Quartier résidentiel avec copropriété fermée par portail automatique, mais Toulon reste une grande ville : la résidence fermée est un vrai atout pour une colocation.",
                },
                {
                    "dimension": "demande_locative",
                    "score": 8,
                    "justification": (
                        "Deux marchés superposés : la location nue familiale (1 000 à 1 100 € pour 75 m²) et la "
                        "colocation étudiante (410 à 480 € par chambre), cette dernière adossée à la faculté de "
                        "droit et au campus. C'est exactement le type de bien où la colocation se loue sans "
                        "difficulté"
                    ),
                },
                {
                    "dimension": "dynamisme",
                    "score": 6,
                    "justification": (
                        "857 ventes dans la tranche 60-80 m² en 2025 : la liquidité du marché toulonnais est un "
                        "atout réel pour la revente. L'annonce à 2 066 €/m² est 17 % sous la médiane de sa "
                        "tranche, ce qui s'explique par l'étage et l'état, pas par une décote de quartier"
                    ),
                },
            ],
            "risques": [
                {
                    "facteur": "La quatrième chambre suppose de sacrifier le séjour",
                    "severite": 4,
                    "detail": (
                        "Le scénario qui rend le dossier conforme est la colocation à quatre chambres, et elle "
                        "n'existe qu'en transformant le salon/salle à manger en chambre. L'annonce ne parle que "
                        "d'une possibilité de troisième chambre. Sans la quatrième, le rendement retombe à "
                        "3,5 %. C'est la vérification numéro un : le plan, la surface de chaque chambre, la "
                        "présence d'un espace commun résiduel, et l'accord de la copropriété sur la "
                        "transformation"
                    ),
                },
                {
                    "facteur": "Rotation étudiante et vacance estivale",
                    "severite": 3,
                    "detail": (
                        "Une colocation se vide par chambre et non d'un bloc : la vacance est plus fréquente "
                        "que sur un bail familial, et l'été est un mois creux. Le modèle retient 8 % de "
                        "vacance en colocation et 12 % en hypothèse défavorable, contre 5 % en location nue. "
                        "Prévoir aussi les impayés et les cautions, plus délicats sur une clientèle étudiante"
                    ),
                },
                {
                    "facteur": "Plafond de loyer de la typologie T4",
                    "severite": 3,
                    "detail": (
                        "En location nue, un T4 de 77 m² se loue 1 000 à 1 100 €, soit 13 à 14 €/m² : c'est le "
                        "plafond structurel de la typologie, et il ne progresse pas avec la rénovation. Toute "
                        "la valeur d'exploitation passe donc par la découpe en chambres, pas par le loyer au "
                        "mètre carré"
                    ),
                },
                {
                    "facteur": "Travaux et ameublement non chiffrés",
                    "severite": 2,
                    "detail": (
                        "20 000 € provisionnés pour la remise au standard, plus 15 000 à 25 000 € "
                        "d'ameublement et d'équipement en scénario colocation. Aucun devis joint. Le DPE C et "
                        "l'état « entretenu » limitent le risque structurel, mais l'électricité et la "
                        "plomberie d'un immeuble de 1970 restent à vérifier"
                    ),
                },
                {
                    "facteur": "Copropriété et règlement",
                    "severite": 2,
                    "detail": (
                        "144 lots, charges de 2 500 €/an communiquées et aucune procédure en cours : le dossier "
                        "est propre de ce côté. Reste à vérifier le règlement de copropriété sur l'exercice "
                        "d'une colocation et la transformation du séjour, ainsi que les travaux votés non "
                        "appelés"
                    ),
                },
            ],
            "champs_manquants": [
                "plan de l'appartement et surface de chaque pièce",
                "devis de remise au standard et état de l'électricité et de la plomberie",
                "règlement de copropriété : colocation et transformation du séjour",
                "trois derniers appels de fonds, procès-verbal d'assemblée, travaux votés non appelés",
                "avis de taxe foncière réel et date du DPE",
                "surface Carrez et statut d'occupation du logement",
            ],
        },
    }


def main():
    spec = importlib.util.spec_from_file_location(
        "gen", os.path.join(ROOT, 'scripts', 'gen_fiches_2026-09-10.py'))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)

    rec = rec_toulon_sj()
    r = engine.compute(rec)
    note, verdict, _ = scoring.note_et_verdict(rec, r)
    nu = calc(1050.0)
    coloc3 = calc(1350.0, 0.08, True, 35000.0)
    coloc4 = calc(1800.0, 0.08, True, 45000.0)
    coloc4h = calc(1920.0, 0.08, True, 45000.0)
    print(f"  nu        EBE {eur(nu['ebe'])} | net {fr(nu['rdt'],2)} % | CF {eur(nu['cf'])} | cap5 {eur(nu['cap5'])}")
    print(f"  coloc 3   EBE {eur(coloc3['ebe'])} | net {fr(coloc3['rdt'],2)} % | CF {eur(coloc3['cf'])} | cap5 {eur(coloc3['cap5'])}")
    print(f"  coloc 4   EBE {eur(coloc4['ebe'])} | net {fr(coloc4['rdt'],2)} % | CF {eur(coloc4['cf'])} | cap5 {eur(coloc4['cap5'])}")
    print(f"  coloc 4bis EBE {eur(coloc4h['ebe'])} | net {fr(coloc4h['rdt'],2)} % | CF {eur(coloc4h['cf'])}")
    print(f"  note {note} / 10 | verdict {verdict}")

    def ligne(label, val, cls=""):
        c = f' class="{cls}"' if cls else ''
        return f'            <tr{c}><td>{label}</td><td class="num">{val}</td></tr>'

    def compte(loyer, vac, coloc, travaux, titre, sous):
        d = calc(loyer, vac, coloc, travaux)
        brut = loyer * 12
        autres = TF + 200 + 600 + (2500.0 if coloc else 0.0)
        rows = [
            ligne("Loyers bruts annuels", f"{eur(brut)} €"),
            ligne(f"Vacance {fr(vac*100,0)} %", f"-{eur(brut*vac)} €"),
            ligne("Charges de copropriété (communiquées)", f"-{eur(COPRO)} €"),
            ligne("Taxe foncière (estimation)", f"-{eur(TF)} €"),
            ligne("Assurance, entretien, TEOM, frais bancaires", f"-{eur(autres-COPRO)} €"),
            ligne("Provisions impayés et travaux (3,5 %)", f"-{eur(brut*0.035)} €"),
            ligne("Excédent brut d'exploitation", f"{eur(d['ebe'])} €", "subtotal"),
            ligne("Amortissement (90 % du revient sur 30 ans)", f"{eur(d['revient']*0.9/30)} €"),
            ligne("Intérêts d'emprunt année 1", f"{eur(PRIX*0.9*TAUX)} €"),
            ligne("EBE mensuel", f"{eur(d['ebe']/12)} €/mois", "highlight"),
            ligne("Mensualité prêt 90 % / 15 ans / 3,7 %", f"-{eur(mens(PRIX*0.9,TAUX,15))} €"),
            ligne("CASH FLOW après IS", f"{eur(d['cf'])} €/mois", "highlight"),
            ligne("Rendement net avant IS sur le revient", f"{fr(d['rdt'],2)} %"),
            ligne("Prix d'achat tenant 5 % net", f"{eur(d['cap5'])} €"),
        ]
        return f"""      <div class="projection-card scenario-{titre}">
        <h3>{sous}</h3>
        <p class="scenario-subtitle">{'Loyer ' + eur(loyer) + ' €/mois, travaux ' + eur(travaux) + ' €' + (' , meublé' if coloc else '')}</p>
        <table class="projection-table"><tbody>
{chr(10).join(rows)}
        </tbody></table>
      </div>"""

    cartes = [compte(1050.0, 0.05, False, TRAVAUX, "base", "Location nue du T4 entier"),
              compte(1350.0, 0.08, True, 35000.0, "optimiste", "Colocation 3 chambres meublées"),
              compte(1800.0, 0.08, True, 45000.0, "pessimiste", "Colocation 4 chambres meublées")]

    plaf = []
    for loy, lab, coloc, trav in ((1000.0, "T4 entier nu", False, TRAVAUX),
                                  (1100.0, "T4 entier nu", False, TRAVAUX),
                                  (1350.0, "colocation 3 ch.", True, 35000.0),
                                  (1800.0, "colocation 4 ch.", True, 45000.0),
                                  (1920.0, "colocation 4 ch.", True, 45000.0)):
        d = calc(loy, 0.08 if coloc else 0.05, coloc, trav)
        plaf.append(f'        <tr><td>{eur(loy)} €/mois</td><td>{lab}</td><td class="num">{eur(d["ebe"])} €</td>'
                    f'<td class="num">{fr(d["rdt"],2)} %</td><td class="num">{eur(d["cf"])} €</td>'
                    f'<td class="num">{eur(d["cap5"])} €</td></tr>')
    plaf_html = "\n".join(plaf)

    lecture = (
        "2 066 €/m² dans la tranche 60-80 m² de Toulon, dont la médiane est à 2 492 €/m² sur 857 ventes : "
        "l'annonce est 17 % sous son marché, le DPE est en C, l'état est déclaré entretenu et — c'est rare "
        "dans les dossiers de cette semaine — les charges de copropriété sont communiquées, 2 500 € par an "
        "pour un immeuble de 144 lots sans procédure en cours. Tout cela plaide pour le bien. En location "
        "nue, pourtant, le dossier ne passe pas : un T4 de 77 m² se loue 1 000 à 1 100 €, l'excédent brut "
        "ressort à 6 480 à 7 578 €, le rendement net avant IS plafonne à 3,9 % et le prix qui tient notre "
        "seuil de 5 % tombe à 101 000-122 000 €. Le basculement vient de la typologie : en colocation "
        "meublée à quatre chambres à 450 €, le loyer brut monte à 21 600 € par an, le rendement passe à "
        "5,6 %, le cash flow devient quasi neutre et le prix qui tient 5 % remonte à 182 700 €, au-dessus "
        "du prix affiché. Une condition à cette bascule : la quatrième chambre n'existe qu'en transformant "
        "le séjour en chambre, et l'annonce ne parle que d'une troisième. C'est donc moins un dossier de "
        "prix qu'un dossier de plan, adossé à la faculté de droit et au campus Porte d'Italie qui sont à "
        "quelques minutes."
    )

    gen.LECTURE[SLUG] = lecture
    gen.RECS[SLUG] = rec
    gen.CONF[SLUG] = dict(
        titre_court="T4 de 77 m², 7e étage — Saint-Jean, Toulon (83000)",
        adresse="Quartier Saint-Jean, Toulon (83000) — T4 de 77,45 m² au 7e étage, copropriété fermée de "
                "144 lots avec ascenseur et stationnement, proche faculté de droit et campus Porte d'Italie "
                "— adresse exacte non communiquée",
        date_fr="22 septembre 2026",
        source="SeLoger — annonce 26HP2UMPWI2F (Gambetta Immobilier, 27 rue Gimelli à Toulon, "
               "SIRET 42327778900024, M. Jérôme Zimny, réf. 1178), présentée en exclusivité",
        url=URL,
        badge="Colocation",
        strategie="Colocation meublée à quatre chambres — location nue et colocation à trois chiffrées en comparaison",
        fiscal_note="SCI à l'IS (15 %), amortissement de 90 % du prix de revient sur 30 ans",
        lat="43.1185", lon="5.9250",
        quartier="Saint-Jean, Toulon (83000) — campus Porte d'Italie et faculté de droit à quelques minutes, centre-ville proche",
        intro_attr=(
            "Le quartier Saint-Jean est l'un des secteurs étudiants de Toulon : <strong>faculté de droit, "
            "campus Porte d'Italie, ISEN et écoles d'ingénieurs</strong> à quelques minutes, avec la demande "
            "locative qui se renouvelle chaque année. Le marché toulonnais est d'une profondeur rare en "
            "Provence : <strong>2 760 ventes d'appartements en 2025</strong>, médiane à 2 668 €/m², et sur la "
            "tranche 60-80 m² qui correspond exactement à ce bien, <strong>857 ventes et une médiane de "
            "2 492 €/m²</strong>. Le loyer mesuré est de 14,4 €/m²/mois. Deux marchés s'y superposent : la "
            "location nue familiale, où un T4 de 75 m² se loue 1 000 à 1 100 €, et la colocation étudiante, "
            "où les chambres se négocient 410 à 480 €. C'est cette deuxième qui porte le rendement."
        ),
        profil=(
            "un investisseur qui accepte d'exploiter en meublé et de gérer une colocation étudiante : "
            "quatre chambres, quatre baux, un renouvellement annuel, un été creux. En échange, le dossier "
            "franchit notre seuil de rendement à 160 000 €, ce qu'aucun des autres dossiers toulonnais de "
            "la semaine ne fait. Le même bien exploité en location nue familiale reste sous 4 %"
        ),
        concl_attr=(
            "Adéquation bonne (7,6/10). Le bien a tout ce qu'on cherche : prix 17 % sous la médiane de sa "
            "tranche, DPE C sans échéance, état entretenu donc pas de chantier lourd, <strong>charges de "
            "copropriété communiquées</strong> à 2 500 € par an dans un immeuble de 144 lots sans procédure, "
            "ascenseur, stationnement, immeuble fermé, et surtout un emplacement adossé à la faculté de droit "
            "et au campus. Le marché de la revente est très liquide. La réserve n'est pas le bien, c'est "
            "l'exploitation : tout repose sur la colocation à quatre chambres, donc sur la transformation du "
            "séjour, et le dossier ne vaut que par ce plan"
        ),
        intro_strat=(
            "Quatre lectures ont été testées : la location nue du T4 entier, la colocation meublée à trois "
            "chambres, la colocation meublée à quatre chambres, et la location meublée d'un seul bail. Seule "
            "la colocation à quatre chambres franchit notre seuil de 5 % net avant IS."
        ),
        rationale=(
            "Commençons par ce qui est bon, et il y en a : <strong>160 000 € pour 77,45 m² au 7e étage avec "
            "ascenseur et stationnement, soit 2 066 €/m²</strong>, quand la tranche 60-80 m² de Toulon "
            "affiche 2 492 €/m² en médiane sur 857 ventes en 2025. Un DPE C — le meilleur des dossiers "
            "toulonnais de la semaine —, un état déclaré entretenu, des charges de copropriété enfin "
            "communiquées à 2 500 €/an, aucune procédure collective, et la faculté de droit à quelques "
            "minutes. Le prix et l'emplacement ne sont pas le problème.<br><br>"
            "Le problème est le loyer. En location nue, un T4 de 77 m² se loue 1 000 à 1 100 € à Toulon — "
            "c'est le plafond de la typologie, et il ne monte pas avec une rénovation. L'excédent brut "
            "d'exploitation ressort alors entre <strong>6 480 et 7 578 €</strong>, soit 540 à 632 €/mois "
            "pour une mensualité de 1 044 € : le rendement net avant IS plafonne à <strong>3,9 %</strong> et "
            "le cash flow est négatif de 412 à 504 €/mois. Le prix qui tiendrait notre seuil de 5 % tombe à "
            "<strong>101 000-122 000 €</strong>.<br><br>"
            "Et puis il y a la colocation. Trois chambres meublées à 450 € ne changent rien : 1 350 € de "
            "loyer brut, mais l'ameublement, les fluides et la vacance estivale ramènent le net à 3,5 %. "
            "<strong>Quatre chambres changent tout</strong> : 1 800 € de loyer brut, un EBE de "
            "<strong>12 116 €</strong>, un rendement net de <strong>5,6 %</strong> — 6,2 % à 480 € la "
            "chambre —, un cash flow quasi neutre à −37 €/mois, et un prix d'achat qui tient 5 % à "
            "<strong>182 700 €</strong>, soit <strong>au-dessus des 160 000 € demandés</strong>. La même "
            "colocation à quatre chambres à 480 € porte même le cash flow à +53 €/mois. Voilà le dossier."
        ),
        identite=[
            ("Adresse", "Quartier Saint-Jean, Toulon (83000) — proche faculté de droit, campus Porte d'Italie, "
                        "commodités et transports urbains, adresse exacte non communiquée"),
            ("Vendeur / intermédiaire", "Gambetta Immobilier, 27 rue Gimelli à Toulon (SIRET 42327778900024), "
                                        "M. Jérôme Zimny — annonce SeLoger 26HP2UMPWI2F, référence 1178"),
            ("Composition", "T4 traversant de 77,45 m² au 7e étage : deux chambres, salon/salle à manger "
                            "pouvant recevoir une chambre supplémentaire, dressing, cuisine indépendante avec "
                            "loggia, salle de bains, WC séparé, balcon. Double vitrage, chauffage central gaz"),
            ("Statut", "<strong>Copropriété de 144 lots</strong>, fermée par portail automatique, ascenseur "
                       "et stationnement dans la résidence. Charges de 2 500 €/an communiquées, aucune "
                       "procédure collective en cours"),
            ("Surfaces", "77,45 m² annoncés, 4 pièces, 3 chambres possibles. Surface Carrez non précisée"),
            ("DPE / GES", "<strong>DPE C / GES C</strong>, immeuble de 1970, chauffage central au gaz, état "
                          "déclaré entretenu. Facture énergétique annoncée entre 1 180 et 1 650 €/an, la plus "
                          "basse des dossiers toulonnais examinés"),
            ("Prix affiché", "<strong>160 000 €</strong>, soit 2 066 €/m², honoraires à la charge du vendeur, "
                             "en exclusivité"),
            ("Valeur retenue", "<strong>193 000 €</strong> (2 492 €/m²), fourchette 180 000 à 210 000 € — "
                               "médiane DVF 2025 de la tranche 60-80 m² de Toulon, 857 ventes"),
            ("Loyers retenus", "<strong>1 050 €/mois</strong> en location nue du T4 entier (comparables : "
                               "1 000 € pour 75 m², 877 € pour un T4) ; <strong>1 800 €/mois</strong> en "
                               "colocation meublée à quatre chambres à 450 €, chambres relevées entre 410 et "
                               "480 € à Toulon"),
            ("Travaux", "<strong>20 000 € retenus (258 €/m²)</strong> pour la remise au standard locatif, "
                        "plus 15 000 à 25 000 € d'ameublement en scénario colocation. Aucun devis joint"),
            ("Taxe foncière", "<strong>Estimée 1 200 €/an</strong> — avis non communiqué, fourchette 900 à "
                              "1 500 €/an"),
            ("Charges de copropriété", "<strong>2 500 €/an communiquées</strong> par l'annonce, pour une "
                                       "copropriété de 144 lots sans procédure. À confirmer sur les appels de "
                                       "fonds et les travaux votés non appelés"),
        ],
        stance=(
            "<strong>On instruit, et on y va sous conditions : offre 150 000 €, plafond 165 000 €, uniquement "
            "si le plan autorise quatre chambres.</strong> Le raisonnement tient en une bascule. Exploité en "
            "location nue, ce bien vaut 122 000 € au maximum pour tenir notre seuil de 5 % — l'écart avec "
            "les 160 000 € demandés serait de 24 %. Exploité en colocation meublée à quatre chambres, le "
            "même bien vaut <strong>182 700 €</strong> : le prix affiché passe alors sous notre plafond, et "
            "c'est le premier dossier toulonnais de la semaine dans ce cas.<br><br>"
            "<strong>La condition n'est pas le prix, c'est le plan.</strong> La quatrième chambre n'existe "
            "qu'en transformant le salon/salle à manger, et l'annonce ne parle que d'une possibilité de "
            "troisième chambre. Il faut le plan, la surface de chaque pièce, l'accord du règlement de "
            "copropriété sur la colocation et la transformation, et une vérification de la demande locale : "
            "les comparables de colocation à trois et quatre chambres sont nombreux dans le secteur, ce qui "
            "est bon signe, mais cela se contrôle annonce par annonce. Sans la quatrième chambre, le dossier "
            "retombe à 3,5 % et l'offre ne doit pas dépasser <strong>130 000 €</strong>.<br><br>"
            "<strong>Les deux autres atouts à ne pas perdre de vue.</strong> Le DPE C et l'état entretenu "
            "signifient qu'il n'y a pas de chantier lourd à porter, contrairement aux trois autres dossiers "
            "de la semaine. Et les charges de copropriété sont communiquées — 2 500 €/an dans un immeuble "
            "de 144 lots sans procédure — ce qui retire l'inconnue qui a plombé le T5 du Mourillon examiné "
            "ce matin."
        ),
        prix_plafond=(
            "<strong>165 000 € en scénario colocation à quatre chambres</strong> — le prix qui tient 5 % net "
            "avant IS est de 182 700 € à 450 € la chambre et de 206 300 € à 480 €, mais il faut garder une "
            "marge pour le risque d'exécution du plan. En <strong>location nue, le plafond tombe à "
            "122 000 €</strong> avec un loyer de 1 100 €, 101 000 € à 1 000 €, et 96 000 € si l'on veut que "
            "le bien couvre sa mensualité sur quinze ans. Autrement dit : la différence entre les deux "
            "plafonds, <strong>60 000 €</strong>, est exactement la valeur de la quatrième chambre. "
            "Tant qu'elle n'est pas certaine, l'offre doit se tenir à 150 000 €."
        ),
        leviers=[
            "Les charges de copropriété sont communiquées — 2 500 € par an pour 144 lots, aucune procédure "
            "en cours — ce qui est rare. C'est le poste qui a plombé les dossiers toulonnais de la semaine : "
            "ici, il est documenté. Le faire confirmer par les trois derniers appels de fonds et la liste des "
            "travaux votés non appelés",
            "Le DPE est en C et l'état déclaré entretenu : pas de passif énergétique, pas d'interdiction de "
            "location à venir, pas de chantier structurel. Sur un immeuble de 1970, cela vaut plusieurs "
            "dizaines de milliers d'euros par rapport aux dossiers à rénover examinés cette semaine",
            "La valeur de la quatrième chambre est mesurable : 60 000 € de capacité de prix, soit la "
            "différence entre le plafond en location nue (122 000 €) et le plafond en colocation à quatre "
            "chambres (182 700 €). C'est l'argument central à vérifier et à négocier sur le plan, pas sur le "
            "prix affiché",
            "La quatrième chambre suppose de sacrifier le séjour : exiger le plan, la surface de chaque pièce, "
            "et vérifier que l'espace commun résiduel reste décent. Une colocation de quatre chambres sans "
            "séjour se loue mal et tourne plus vite",
            "Vérifier le règlement de copropriété sur deux points : l'exercice d'une colocation et la "
            "transformation d'une pièce de vie en chambre. Dans une copropriété de 144 lots, c'est le genre "
            "de clause qui se découvre trop tard",
            "Trois chambres ne suffisent pas : 1 350 € de loyer brut conduisent à 3,5 % net, à cause de "
            "l'ameublement, des fluides et de la vacance estivale. Le passage de trois à quatre chambres "
            "vaut à lui seul 1,6 point de rendement : c'est toute la différence entre un dossier sous "
            "doctrine et un dossier au-dessus",
            "La demande étudiante est adossée à la faculté de droit, au campus Porte d'Italie et à l'ISEN : "
            "vérifier le marché réel en relevant les colocations actives de trois et quatre chambres dans le "
            "secteur, avec leur loyer par chambre et leur date de mise en ligne",
            "Ne pas se laisser enfermer par le taux facial : 2 066 €/m² sous une médiane de tranche à "
            "2 492 €/m², c'est 17 % d'écart, mais l'écart ne rémunère pas l'exploitation. Ce sont les "
            "1 800 € de loyer en colocation qui font passer le dossier, pas la décote d'entrée",
        ],
        meta=[
            "<strong>Régime fiscal retenu :</strong> SCI à l'IS (15 %), amortissement de 90 % du prix de "
            "revient sur 30 ans. L'amortissement et les intérêts absorbent le résultat les premières années",
            "<strong>Frais d'acquisition :</strong> 12 800 € (8 %), honoraires à la charge du vendeur",
            "<strong>Loyers :</strong> 1 050 €/mois en location nue, 1 800 €/mois en colocation à quatre "
            "chambres meublées (450 € par chambre), 1 350 € à trois chambres. Aucun loyer en place, le bien "
            "est vide",
            "<strong>Charges retenues :</strong> copropriété 2 500 €/an communiqués, taxe foncière estimée "
            "1 200 €, assurance 200 €, entretien, TEOM et frais bancaires 600 €, provisions d'impayés et "
            "travaux 3,5 % des loyers, comptabilité 1 200 €. En colocation, ajouter 2 500 €/an de "
            "meublement et de fluides. Aucun poste laissé à zéro",
            "<strong>Financement :</strong> 90 % du prix sur 15 ans à 3,7 %, soit 1 044 €/mois. Fonds propres "
            "à amener 48 800 € en location nue, 73 800 € en colocation aménagée",
            "<strong>Contrôles à faire avant toute offre :</strong> plan et surface de chaque pièce avec "
            "faisabilité de la quatrième chambre ; règlement de copropriété sur la colocation et la "
            "transformation du séjour ; trois derniers appels de fonds, procès-verbal d'assemblée, travaux "
            "votés non appelés ; devis de remise au standard, ameublement et état de l'électricité ; avis de "
            "taxe foncière ; date du DPE et surface Carrez",
            "<strong>Point de méthode :</strong> sur un T4, le loyer au mètre carré est plafonné par la "
            "typologie : la rénovation n'y change rien, seule la découpe en chambres déplace le rendement. "
            "Le plafond d'achat passe ainsi de 122 000 € en location nue à 182 700 € en colocation à quatre "
            "chambres — c'est cette bascule, et non la décote de 17 % sur la médiane, qui décide du dossier",
            "<strong>Rappel de marché (sources au 22/09/2026) :</strong> Toulon, 2 760 ventes d'appartements "
            "en 2025, médiane 2 668 €/m² ; tranche 60-80 m², 857 ventes, médiane 2 492 €/m², premier "
            "quartile 1 955 €/m² ; loyer mesuré 14,4 €/m²/mois (ANIL 2025) ; T4/T5 relevés entre 877 et "
            "1 000 € pour 75 m² ; colocations étudiantes de 410 à 480 € par chambre, nombreuses autour de "
            "la faculté de droit et du campus Porte d'Italie",
        ],
    )

    c = gen.CONF[SLUG]
    ech = gen.TEMPLATE.format(
        titre_court=c['titre_court'], adresse=c['adresse'], date_fr=c['date_fr'],
        source=c['source'], url=c['url'], badge=c['badge'], strategie=c['strategie'],
        fiscal_note=c['fiscal_note'],
        prix=eur(PRIX),
        surface=f"{SURF:.0f} m²",
        prix_m2=f"{eur(PRIX/SURF)} €/m²",
        revient=eur(PRIX * 1.08 + TRAVAUX),
        valeur=eur(193000),
        revenus=eur(1050),
        rdt_revient=fr(nu['rdt'], 2), rdt_valeur=fr(nu['ebe'] / 193000 * 100, 2),
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
    <h3>Ce que chaque exploitation autorise comme prix d'achat</h3>
    <table class="projection-table compare">
      <thead><tr><th>Loyer brut mensuel</th><th>Exploitation</th><th class="num">EBE</th><th class="num">Net avant IS sur revient</th><th class="num">Cash flow 15 ans</th><th class="num">Achat max (5 % net)</th></tr></thead>
      <tbody>
{plaf_html}
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Le point de bascule.</strong> En location nue, le prix qui tient 5 % net avant IS est de <strong>{eur(nu['cap5'])} €</strong> à 1 050 € de loyer, et de 96 800 € si l'on veut que le bien couvre sa mensualité sur quinze ans. En colocation meublée à quatre chambres, le même seuil monte à <strong>{eur(coloc4['cap5'])} €</strong> et le cash flow devient quasi neutre. Les deux plafonds sont séparés par 60 000 € : c'est la valeur de la quatrième chambre, et c'est elle qui décide si le prix affiché passe ou non.</p>
    </div>
    <p class="attractiveness-intro">Repères de méthode : frais d'acquisition {eur(PRIX*NOTAIRE)} € (8 %), honoraires de revente 5 %, prêt à 90 % sur 15 ans à 3,7 % soit {eur(mens(PRIX*0.9,TAUX,15))} €/mois, SCI à l'IS avec amortissement de 90 % du prix de revient sur 30 ans, vacance 5 % en location nue et 8 % en colocation, provisions d'impayés et travaux 3,5 % des loyers, taxe foncière estimée {eur(TF)} €/an, charges de copropriété communiquées à {eur(COPRO)} €/an, meublement et fluides 2 500 €/an en colocation. Valeur retenue 193 000 € (2 492 €/m²), médiane DVF 2025 de la tranche 60-80 m² de Toulon.</p>
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
        f.write(ech)
    print(f"  fiche ecrite : {len(ech):,} octets dans {SLUG}")

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
