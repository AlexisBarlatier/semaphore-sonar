#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche Meyrargues — ancienne gare du village, 185 m2 en deux logements, 231 000 EUR.

Branche MDB : le compte d'exploitation remplace les projections locatives.
Le record vit dans analyses/analyses.json (source de verite) ; ce script ne fait
que regenerer la fiche HTML avec les chiffres du moteur.
"""
import copy
import importlib.util
import os
import sys

ROOT = '/home/alexis-barlatier/Documents/Semaphore-sonar'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from analyse_app import engine, scoring  # noqa: E402

SLUG = "2026-09-21-maison-ancienne-gare-meyrargues"
URL = "https://www.leboncoin.fr/ad/ventes_immobilieres/3202017908"

# Grille de scenarios : (libelle, cle, travaux, revente)
SCENARIOS = [
    ("Base", "base", 166500.0, 481000.0),
    ("Optimiste", "optimiste", 120000.0, 540000.0),
    ("Pessimiste", "pessimiste", 200000.0, 425000.0),
]


def eur(v):
    return f"{v:,.0f}".replace(',', ' ')


def fr(v, dec=1):
    return f"{v:.{dec}f}".replace('.', ',')


def mdb_rec(rec, travaux, revente, duree_mois=18, portage_mensuel=1500.0):
    v = copy.deepcopy(rec)
    v['bien']['travaux']['montant_euros'] = travaux
    v['marche']['revente'] = {
        "prix_euros": revente,
        "frais_vente_euros": round(revente * 0.05, 2),
        "duree_mois": duree_mois,
        "portage_mensuel_euros": portage_mensuel,
    }
    return v


def main():
    spec = importlib.util.spec_from_file_location(
        "gen", os.path.join(ROOT, 'scripts', 'gen_fiches_2026-09-10.py'))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)

    rec = gen.RECS[SLUG]
    base = engine.compute(rec)                       # scenario retenu dans la base
    note, verdict, _ = scoring.note_et_verdict(rec, base)
    pv = base['mdb']
    roi_18 = pv['roi_pct']
    roi_an = ((1 + roi_18 / 100.0) ** (12.0 / 18.0) - 1) * 100.0

    # ------------------------------------------------------------------ cards
    gen.TEMPLATE = gen.TEMPLATE.replace(
        '<span class="card-label">Revenus bruts</span>',
        '<span class="card-label">Loyers retenus (variante locative)</span>')
    gen.TEMPLATE = gen.TEMPLATE.replace(
        '<span class="card-label">Rentabilité nette</span>',
        '<span class="card-label">ROI net MDB (18 mois / an)</span>')

    # ------------------------------------------------------- projections MDB
    def ligne(label, val, cls=""):
        c = f' class="{cls}"' if cls else ''
        return f'            <tr{c}><td>{label}</td><td class="num">{val}</td></tr>'

    def compte_mdb(travaux, revente):
        v = mdb_rec(rec, travaux, revente)
        r = engine.compute(v)
        m = r['mdb']
        frais = v['marche']['revente']['frais_vente_euros']
        portage = m['portage_total']
        rows = [
            ligne("Prix d'achat net vendeur", f"{eur(231000)} €"),
            ligne("Frais d'acquisition (8 %)", f"{eur(r['frais_acquisition'])} €"),
            ligne(f"Rénovation complète ({eur(travaux)} €, {eur(travaux/185)} €/m²)",
                  f"{eur(travaux)} €"),
            ligne("Prix de revient total", f"{eur(m['prix_revient_total'])} €", "subtotal"),
            ligne("Revente après rénovation", f"{eur(revente)} €"),
            ligne("Honoraires de vente (5 %)", f"-{eur(frais)} €"),
            ligne("Portage 18 mois (intérêts, TF, assurance)", f"-{eur(portage)} €"),
            ligne("Plus-value brute", f"{eur(m['pv_brute'])} €", "subtotal"),
            ligne("IS (15 %)", f"-{eur(m['is_pv'])} €"),
            ligne("Plus-value nette après IS", f"{eur(m['pv_nette'])} €", "highlight"),
            ligne("ROI sur le prix de revient", f"{fr(m['roi_pct'])} %"),
            ligne("Revient / revente", f"{fr(m['prix_revient_total']/revente, 2)}"),
        ]
        return r, m, "\n".join(rows)

    res = {}
    for label, key, travaux, revente in SCENARIOS:
        res[key] = compte_mdb(travaux, revente)

    (rb, mb, rows_b), (ro, mo, rows_o), (rp, mp, rows_p) = (
        res["base"], res["optimiste"], res["pessimiste"])

    def carte(titre, cls, sous_titre, rows):
        return f"""      <div class="projection-card scenario-{cls}">
        <h3>Scénario {titre}</h3>
        <p class="scenario-subtitle">{sous_titre}</p>
        <table class="projection-table"><tbody>
{rows}
        </tbody></table>
      </div>"""

    # grille de sensibilite : ROI selon travaux et revente
    grille = []
    for trav in (120000.0, 150000.0, 166500.0, 185000.0, 200000.0):
        cells = []
        for rev in (425000.0, 481000.0, 540000.0):
            m = engine.compute(mdb_rec(rec, trav, rev))['mdb']
            cells.append(f'<td class="num">{fr(m["roi_pct"])} %</td>')
        grille.append(f'        <tr><td>{eur(trav)} € ({eur(trav/185)} €/m²)</td>'
                      + "".join(cells) + '</tr>')
    grille_html = "\n".join(grille)

    # plafond par tranche de travaux pour un ROI de 20 %
    net_vente = 481000.0 * 0.95
    portage = 27000.0
    revient_max = (0.85 * (net_vente - portage)) / (1 + 0.85 * 0.20)
    plafonds = []
    for trav in (100000.0, 120000.0, 150000.0, 180000.0, 200000.0):
        plafonds.append(f'        <tr><td>{eur(trav)} € ({eur(trav/185)} €/m²)</td>'
                        f'<td class="num">{eur(revient_max - 18480 - trav)} €</td>'
                        f'<td class="num">{fr((revient_max - 18480 - trav)/231000*100 - 100)} %</td></tr>')
    plafonds_html = "\n".join(plafonds)

    # point mort travaux au prix affiche
    point_mort = revient_max - 18480 - 231000
    # hmm : le point mort est le travaux max pour un ROI 20 % AU PRIX AFFICHE
    point_mort_trav = None
    for t in range(0, 400000, 500):
        m = engine.compute(mdb_rec(rec, float(t), 481000.0))['mdb']
        if m['roi_pct'] <= 20.0:
            point_mort_trav = t
            break
    point_mort_zero = None
    for t in range(0, 400000, 500):
        m = engine.compute(mdb_rec(rec, float(t), 481000.0))['mdb']
        if m['pv_nette'] <= 0:
            point_mort_zero = t
            break

    lecture_txt = (
        "Une ancienne gare, 185 m², 250 m² de terrain, à 1 249 €/m² quand la commune affiche 3 240 à 3 642 €/m² "
        "pour les maisons : le premier réflexe est de voir la décote du siècle. Le deuxième est de lire la phrase de "
        "l'agence, écrite noir sur blanc : « cette maison nécessite une rénovation complète ». Tout est là. Avec "
        "231 000 € d'achat et 18 480 € de frais, il reste environ 480 000 € de valeur potentielle, et c'est la "
        "rénovation qui arbitre entre la faire et ne pas la faire : 120 000 € de travaux donnent 99 000 € de "
        "plus-value nette, 150 000 € en donnent 26 000, et à partir de 180 000 € le dossier perd de l'argent. "
        "Le point mort est à 180 500 € de rénovation pour une revente à 481 000 €, soit 975 €/m² : c'est très "
        "exactement le haut de la fourchette d'une rénovation lourde, et personne ne sait aujourd'hui de quel côté "
        "de cette ligne le bien se situe. Ajoutez un DPE E dont la location sera interdite en 2034, une facture "
        "énergétique annoncée entre 3 990 et 5 450 €/an, un terrain de 250 m² qui interdit toute extension, et un "
        "marché en recul de 8 à 15 % sur un an dans un village qui vend 41 maisons par an. Le dossier n'est pas "
        "mauvais, il est illisible au prix demandé : tant que la rénovation n'est pas chiffrée par un artisan, "
        "l'offre à 231 000 € revient à acheter une promesse au prix d'un bien fini."
    )
    gen.LECTURE[SLUG] = lecture_txt

    projections = f"""  <section class="financial-projections">
    <h2>Compte d'exploitation marchand de biens — prix affiché {eur(231000)} €, SAS à l'IS</h2>
    <p class="attractiveness-intro">{lecture_txt}</p>
    <div class="projections-grid">
{carte("Base", "base", f"Rénovation complète à {eur(166500)} € (900 €/m²) et revente à {eur(481000)} €", rows_b)}
{carte("Optimiste", "optimiste", f"Rénovation maîtrisée à {eur(120000)} € (649 €/m²) et revente à {eur(540000)} €", rows_o)}
{carte("Pessimiste", "pessimiste", f"Rénovation à {eur(200000)} € (1 081 €/m²) et revente à {eur(425000)} €", rows_p)}
    </div>
    <table class="projection-table compare">
      <thead><tr><th>Indicateur</th><th class="num">Base</th><th class="num">Optimiste</th><th class="num">Pessimiste</th></tr></thead>
      <tbody>
        <tr><td>Prix de revient total</td><td class="num">{eur(mb['prix_revient_total'])} €</td><td class="num">{eur(mo['prix_revient_total'])} €</td><td class="num">{eur(mp['prix_revient_total'])} €</td></tr>
        <tr><td>Plus-value brute</td><td class="num">{eur(mb['pv_brute'])} €</td><td class="num">{eur(mo['pv_brute'])} €</td><td class="num">{eur(mp['pv_brute'])} €</td></tr>
        <tr><td>Plus-value nette après IS</td><td class="num">{eur(mb['pv_nette'])} €</td><td class="num">{eur(mo['pv_nette'])} €</td><td class="num">{eur(mp['pv_nette'])} €</td></tr>
        <tr><td>ROI sur 18 mois</td><td class="num">{fr(mb['roi_pct'])} %</td><td class="num">{fr(mo['roi_pct'])} %</td><td class="num">{fr(mp['roi_pct'])} %</td></tr>
        <tr><td>Revient / revente</td><td class="num">{fr(mb['prix_revient_total']/481000, 2)}</td><td class="num">{fr(mo['prix_revient_total']/540000, 2)}</td><td class="num">{fr(mp['prix_revient_total']/425000, 2)}</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix">
      <p class="attractiveness-intro"><strong>Ce que le prix affiché laisse comme marge.</strong> Le point mort de la rénovation, revente à {eur(481000)} €, tombe à <strong>{eur(point_mort_zero)} €</strong> : au-delà, la plus-value nette devient négative. Pour viser 20 % de ROI à ce même prix de revente, la rénovation doit tenir dans <strong>{eur(point_mort_trav)} €</strong>, soit {eur(point_mort_trav/185)} €/m². À 231 000 € d'achat, le dossier ne devient réellement intéressant qu'avec une rénovation sous 120 000 €, c'est-à-dire sans reprise lourde de la couverture, de la charpente et des réseaux.</p>
    </div>
    <h3>ROI selon le coût de la rénovation et le prix de revente</h3>
    <table class="projection-table compare">
      <thead><tr><th>Travaux</th><th class="num">Revente 425 000 €</th><th class="num">Revente 481 000 €</th><th class="num">Revente 540 000 €</th></tr></thead>
      <tbody>
{grille_html}
      </tbody>
    </table>
    <h3>Prix d'achat maximum pour un ROI de 20 %, selon la rénovation</h3>
    <table class="projection-table compare">
      <thead><tr><th>Rénovation</th><th class="num">Prix d'achat max</th><th class="num">Écart au prix affiché</th></tr></thead>
      <tbody>
{plafonds_html}
      </tbody>
    </table>
    <p class="attractiveness-intro">Repères de méthode : frais d'acquisition 18 480 € (8 %), honoraires de revente 5 %, portage de 18 mois à 1 500 €/mois (financement intégral du revient à 3,8 %, taxe foncière, assurance), IS à 15 % sur la plus-value. Valeur de revente retenue 481 000 €, soit 2 600 €/m², ancrée sur les transactions DVF de maisons de 87 à 112 m² de Meyrargues (3 750 à 5 114 €/m², terrains de 350 à 1 800 m²) avec décote de surface et de terrain, dans une commune dont les prix reculent de 8 à 15 % sur un an.</p>
  </section>"""

    gen.LECTURE[SLUG] = (
        "Une ancienne gare, 185 m², 250 m² de terrain, à 1 249 €/m² quand la commune affiche 3 240 à 3 642 €/m² "
        "pour les maisons : le premier réflexe est de voir la décote du siècle. Le deuxième est de lire la phrase de "
        "l'agence, écrite noir sur blanc : « cette maison nécessite une rénovation complète ». Tout est là. Avec "
        "231 000 € d'achat et 18 480 € de frais, il reste environ 480 000 € de valeur potentielle, et c'est la "
        "rénovation qui arbitre entre la faire et ne pas la faire : 120 000 € de travaux donnent 99 000 € de "
        "plus-value nette, 150 000 € en donnent 26 000, et à partir de 180 000 € le dossier perd de l'argent. "
        "Le point mort est à 180 500 € de rénovation pour une revente à 481 000 €, soit 975 €/m² : c'est très "
        "exactement le haut de la fourchette d'une rénovation lourde, et personne ne sait aujourd'hui de quel côté "
        "de cette ligne le bien se situe. Ajoutez un DPE E dont la location sera interdite en 2034, une facture "
        "énergétique annoncée entre 3 990 et 5 450 €/an, un terrain de 250 m² qui interdit toute extension, et un "
        "marché en recul de 8 à 15 % sur un an dans un village qui vend 41 maisons par an. Le dossier n'est pas "
        "mauvais, il est illisible au prix demandé : tant que la rénovation n'est pas chiffrée par un artisan, "
        "l'offre à 231 000 € revient à acheter une promesse au prix d'un bien fini."
    )

    gen.CONF = {SLUG: dict(
        titre_court="Ancienne gare, Meyrargues (13650)",
        adresse="Meyrargues (13650), cœur du village — ancienne gare divisée en deux logements, 185 m², terrain de 250 m² — adresse exacte non communiquée",
        date_fr="21 septembre 2026",
        source="LeBonCoin — annonce 3202017908 (L'Agence 3C, Les Pennes-Mirabeau, réseau Expertimo — réf. 1798_187) ; DPE E / GES B relevé sur la fiche SeLoger 26R7DHWFFHY4",
        url=URL,
        badge="Marchand de biens",
        strategie="Achat, rénovation complète et revente en marchand de biens",
        fiscal_note="SAS à l'IS (15 % sur la plus-value), financement intégral du prix de revient",
        lat="43.636776", lon="5.5288577",
        quartier="Meyrargues (13650) — 3 426 habitants, 15 minutes d'Aix-en-Provence, 20 minutes de Cadarache",
        intro_attr=(
            "Meyrargues est un village de 3 426 habitants de la vallée de la Durance, à quinze minutes d'Aix-en-Provence "
            "et vingt minutes du site de Cadarache, avec l'autoroute A51 à proximité immédiate. 68 % du parc est constitué "
            "de maisons, 62 % des habitants sont propriétaires et 89 % des logements sont des résidences principales : c'est "
            "un village résidentiel, pas un marché d'investisseurs. Les prix des maisons s'établissent à "
            "<strong>3 642 €/m²</strong> en DVF 2025 pour immovrai et <strong>3 240 €/m²</strong> pour PAP, mais avec un "
            "signal qu'il faut regarder en face : <strong>−8,3 % sur un an</strong> selon immovrai et <strong>−15,2 %</strong> "
            "selon PAP, et 41 ventes de maisons par an seulement pour 1 244 maisons. Le marché de la location est étroit, "
            "38 % de locataires, et les maisons relouées se traitent entre 10,6 et 16,4 €/m²/mois."
        ),
        profil=(
            "un acheteur de caractère, venu chercher le cachet et l'atypique plutôt que la surface : cadre ou retraité travaillant "
            "à Aix, à Cadarache ou dans la vallée, sensible à l'ancienne gare et aux volumes, avec un budget de travaux. Ce n'est "
            "pas le profil d'un investisseur locatif, et ce n'est pas non plus une famille à la recherche d'un grand terrain, "
            "250 m² ne le permettant pas"
        ),
        concl_attr=(
            "Adéquation moyenne (5,8/10). Le village a des atouts réels : situation dans la vallée d'Aix, bassin d'emploi solide, "
            "cadre résidentiel et prix des maisons parmi les plus élevés du secteur. Mais trois éléments plombent le score. "
            "Le premier est le <strong>dynamisme</strong> : 41 ventes de maisons par an, une construction neuve autorisée en recul "
            "de 68 % entre 2021 et 2025 et un prix qui recule de 8 à 15 % sur un an. Le deuxième est la <strong>demande "
            "locative</strong> : 38 % de locataires, un marché de la location de maisons étroit, et des loyers modestes au regard "
            "de la valeur des biens. Le troisième est la nature même du bien : <strong>185 m² atypiques sur 250 m² de terrain</strong>, "
            "c'est-à-dire une clientèle étroite et un délai de vente long, dans un marché où le temps coûte."
        ),
        intro_strat=(
            "Cinq lectures ont été testées : le marchand de biens (rénover et revendre), la location d'un seul bail familial, "
            "le découpage en deux locations indépendantes, la revente d'un seul des deux logements après division, et l'usage "
            "personnel. Le compte d'exploitation marchand de biens est retenu comme lecture principale, parce que c'est lui qui "
            "porte la décision : le bien vaut 1 249 €/m² à l'achat et 2 296 à 2 919 €/m² à la revente, et l'écart entre ces deux "
            "mondes se joue entièrement sur le coût de la rénovation."
        ),
        rationale=(
            "Le dossier a un vrai ressort : <strong>231 000 € pour 185 m² dans une commune où les maisons se traitent entre "
            "3 240 et 3 642 €/m²</strong>. Ramené au prix de revient, l'écart crée de la valeur à condition de tenir la rénovation. "
            "En scénario de base, 166 500 € de travaux (900 €/m²) donnent un prix de revient de <strong>415 980 €</strong> pour une "
            "revente de 481 000 € : plus-value nette après IS de <strong>11 874 €</strong>, soit un ROI de "
            "<strong>2,9 % sur 18 mois</strong>, environ 1,9 % par an. C'est insuffisant au regard du risque pris.<br><br>"
            "Le même bien avec 120 000 € de travaux et une revente à 540 000 € dégage <strong>99 042 € nets</strong>, un ROI de "
            "26,8 % : le dossier bascule complètement selon le devis. Le point mort de la rénovation, à 481 000 € de revente, "
            "tombe à <strong>180 500 €</strong> (975 €/m²). Au-delà, l'opération perd de l'argent, et le scénario pessimiste à "
            "200 000 € de travaux et 425 000 € de revente aboutit à une perte de 72 730 €.<br><br>"
            "Les deux autres lectures ferment la porte. En <strong>location</strong>, les deux logements retenus à 1 850 €/mois "
            "produisent un EBE de 16 013 €, un net après IS de 15 409 €, soit <strong>3,2 % de la valeur</strong> et 3,9 % du prix "
            "de revient : sous crédit, il manque près de 940 € par mois. En <strong>colocation de cinq chambres</strong>, la "
            "meilleure variante locative, le rendement net monte à 4,2 % : mieux, toujours pas finançable."
        ),
        identite=[
            ("Adresse", "Meyrargues (13650), cœur du village, à 15 minutes d'Aix-en-Provence et 20 minutes de Cadarache — adresse exacte non communiquée"),
            ("Vendeur / intermédiaire", "L'Agence 3C (220 avenue François Mitterrand, 13170 Les Pennes-Mirabeau, SIRET 98117531800022), réseau Expertimo — référence 1798_187. Annonce LeBonCoin 3202017908, également publiée sur SeLoger (26R7DHWFFHY4)"),
            ("Composition", "Ancienne gare du village divisée en <strong>deux logements indépendants</strong> : 185 m² habitables, 6 pièces, 5 chambres, <strong>deux niveaux</strong>, deux parkings, jardin et terrasse, exposition est-ouest, un mur mitoyen"),
            ("Statut", "<strong>Copropriété NON</strong> (fiche agence et SeLoger) : aucun lot juridiquement divisé. Revendre un seul des deux logements supposerait de créer un état descriptif de division, de l'ordre de 5 000 à 10 000 €"),
            ("Surfaces", "185 m² habitables et 185 m² Carrez annoncés, 6 pièces, 5 chambres. <strong>Terrain de 250 m²</strong> seulement, soit une emprise qui interdit toute extension"),
            ("DPE / GES", "<strong>DPE E / GES B</strong> (SeLoger). Facture énergétique annoncée entre <strong>3 990 et 5 450 €/an</strong>, soit 21 à 29 €/m²/an. Interdiction de location à horizon 2034 : passif estimé à 19 000 € de valeur actuelle nette (25 000 € dans 8 ans à 3,5 %)"),
            ("Prix affiché", "<strong>231 000 €</strong>, honoraires intégralement à la charge du vendeur, soit <strong>1 249 €/m²</strong>. Annonce portant la mention « baisse de prix », 215 favoris"),
            ("Valeur de revente retenue", "<strong>481 000 €</strong> (2 600 €/m²), fourchette 425 000 à 540 000 € : transactions DVF de maisons de 87 à 112 m² à Meyrargues entre octobre et décembre 2025 (3 750 à 5 114 €/m²) avec décote de surface et de terrain, aucune transaction dans la tranche 157 à 213 m². Moyenne communale des maisons : 3 642 €/m² (immovrai) et 3 240 €/m² (PAP)"),
            ("Loyers retenus (variante locative)", "<strong>1 850 €/mois</strong> (1 000 € + 850 €) pour les deux logements, soit 22 200 €/an et 9,6 % brut sur le prix affiché. Aucun loyer en place. Comparables : 1 610 € pour 152 m², 2 462 € CC pour 150 m², 1 700 € pour 115 m² à Villelaure"),
            ("Travaux", "<strong>166 500 € provisionnés (900 €/m²)</strong>, fourchette 111 000 à 222 000 € : électricité, plomberie, chauffage, isolation, menuiseries, deux cuisines, deux salles d'eau, sols, peintures, couverture et charpente à vérifier. Aucun devis, aucun plan, aucun diagnostic technique joint"),
            ("Taxe foncière", "<strong>Estimée 2 200 €/an</strong> — non communiquée. Taux communal sur le bâti de <strong>34,70 %</strong> en 2025, TEOM 14,00 %. Fourchette 1 800 à 2 800 €/an"),
            ("Prix de revient à l'affichage", "<strong>415 980 €</strong> = prix 231 000 € + frais d'acquisition 18 480 € (8 %) + rénovation 166 500 €"),
        ],
        stance=(
            "<strong>On négocie, et fort : offre 175 000 €, plafond 190 000 € sous condition d'un devis de rénovation sous "
            "150 000 €. Au-delà, on passe.</strong> Le raisonnement tient en une ligne : à 231 000 €, la marge est nulle au "
            "scénario de base et négative dès que la rénovation dépasse 180 500 €, soit 975 €/m², c'est-à-dire le haut de la "
            "fourchette annoncée par l'agence elle-même.<br><br>"
            "<strong>Trois chiffres commandent la décision.</strong> Rénovation à 166 500 € et revente à 481 000 € : plus-value "
            "nette de 11 874 €, ROI 2,9 % sur 18 mois. Rénovation à 120 000 € et revente à 540 000 € : 99 042 € et 26,8 %. "
            "Rénovation à 200 000 € et revente à 425 000 € : <strong>moins 72 730 €</strong>. Pour viser 20 % de ROI à 231 000 € "
            "d'achat, il faut une rénovation sous <strong>143 900 €</strong> ; pour 20 % de ROI avec 150 000 € de travaux, il faut "
            "acheter à <strong>143 900 €</strong>, soit 38 % sous l'affichage.<br><br>"
            "<strong>Ce que l'annonce ne dit pas est plus important que ce qu'elle dit.</strong> L'agence annonce une « rénovation "
            "complète » d'un bien de 1930 sur deux niveaux sans un seul devis, et SeLoger affiche « rénovation nécessaire » sans "
            "plus de précision. Sur 185 m², la fourchette 600 à 1 200 €/m² vaut 111 000 €, soit plus de la moitié du prix d'achat. "
            "Personne ne peut faire d'offre sérieuse avant d'avoir fait passer un artisan. La visite n'est pas une formalité sur "
            "ce dossier, c'est la seule source d'information qui manque.<br><br>"
            "<strong>Deux réserves de fond en plus.</strong> Le bien est une ancienne gare : voie ferrée, bruit, servitudes "
            "éventuelles et emprise à vérifier, c'est un point à contrôler en mairie et sur place. Et il est en DPE E, avec une "
            "location interdite en 2034 : 19 000 € de passif actualisé, à intégrer au devis de rénovation, pas à côté."
        ),
        prix_plafond=(
            "<strong>190 000 €</strong> net vendeur, et uniquement avec un devis de rénovation sous 150 000 € et une revente "
            "étayée au-dessus de 480 000 €. Repères : <strong>143 900 €</strong> pour viser 20 % de ROI avec 150 000 € de travaux, "
            "<strong>193 900 €</strong> avec 100 000 €, <strong>173 900 €</strong> avec 120 000 €, <strong>113 900 €</strong> avec "
            "180 000 €. En dessous de 150 000 € de rénovation, le dossier devient un vrai marchand de biens ; au-dessus de "
            "180 500 €, il détruit de la valeur à 231 000 € d'achat. Si le DPE E impose une rénovation énergétique lourde en plus "
            "de la rénovation, retirer 19 000 € de capacité de prix."
        ),
        leviers=[
            "L'argument central est écrit par le vendeur lui-même : « cette maison nécessite une rénovation complète ». Il n'y a donc pas de débat sur l'état, seulement sur le chiffrage. C'est ce qui autorise à conditionner toute offre au devis d'un artisan",
            "La fourchette de rénovation vaut plus de 110 000 € de prix d'achat : 600 €/m² donne un dossier à 20 % de ROI à 194 000 €, 900 €/m² le ramène à 144 000 €, 1 200 €/m² le tue. Exiger un devis par corps d'état avant de discuter du prix, jamais l'inverse",
            "Le prix facial est trompeur et il faut le dire : 1 249 €/m² contre 3 240 à 3 642 €/m² de moyenne communale laisse croire à 65 % de décote. Dans la tranche de surface du bien, aucune transaction comparable n'existe à Meyrargues, et le prix au m² décroît avec la surface. La décote réelle est celle des travaux, pas celle du marché",
            "Le marché recule : −8,3 % sur un an (immovrai) à −15,2 % (PAP), 41 ventes de maisons par an pour 1 244 maisons. Le portage de 18 mois à 1 500 €/mois pèse 27 000 € et chaque mois supplémentaire coûte 1 500 €. C'est un argument de délai, donc de prix",
            "Exiger l'avis de taxe foncière réel : la taxe estimée à 2 200 €/an n'est pas communiquée, et la commune applique un taux sur le bâti de 34,70 %. Chaque 500 € d'écart vaut 42 €/mois sur la variante locative, et fait bouger la marge MDB",
            "Vérifier l'emprise ferroviaire : le bien est l'ancienne gare du village. Bruit de la ligne, servitudes SNCF éventuelles, projets d'aménagement de la voie, tout cela se demande en mairie et ne se découvre pas après l'achat",
            "Le DPE E est un passif daté : interdiction de location en 2034, facture énergétique annoncée entre 3 990 et 5 450 €/an, et un GES B qui oriente vers l'isolation, c'est-à-dire vers le poste le plus cher. 19 000 € de valeur actualisée à intégrer au devis",
            "Le terrain de 250 m² pour 185 m² habitables limite la clientèle de revente à un acheteur de caractère, pas à une famille en quête d'espace. Cela se traduit par un délai de vente plus long : à intégrer dans le portage, et donc dans le prix d'achat",
            "Faire chiffrer séparément la division juridique en deux lots (état descriptif de division, notaire, 5 000 à 10 000 €, six à neuf mois) si l'idée est de vendre un logement et de garder l'autre : ce n'est pas un scénario gratuit",
        ],
        meta=[
            "<strong>Régime fiscal retenu :</strong> SAS à l'IS (15 % sur la plus-value de cession) — pas d'amortissement, le compte d'exploitation marchand de biens remplace les projections locatives",
            "<strong>Frais d'acquisition :</strong> 18 480 € (8 % du prix affiché, barème de l'ancien, confirmé par l'annonce)",
            "<strong>Enveloppe rénovation :</strong> 166 500 € retenus (900 €/m²), fourchette 111 000 à 222 000 €. Aucun devis, aucun plan, aucun diagnostic technique. C'est la variable qui décide du dossier",
            "<strong>Revente :</strong> 481 000 € retenus (2 600 €/m²), 5 % d'honoraires de vente et 18 mois de portage à 1 500 €/mois. Fourchette 425 000 à 540 000 €, ancrée sur les transactions DVF de maisons de 87 à 112 m² de Meyrargues",
            "<strong>Loyers :</strong> aucun loyer en place. La variante locative à 1 850 €/mois (deux logements) donne un net après IS de 15 409 €, soit 3,2 % de la valeur et 3,9 % du prix de revient, cash flow négatif de 940 €/mois sous crédit. La colocation de cinq chambres monte à 4,2 % : aucune des deux ne finance l'opération",
            "<strong>Contrôles à faire avant toute offre :</strong> devis de rénovation par corps d'état (électricité, plomberie, chauffage, isolation, menuiseries, couverture, charpente) ; diagnostic technique complet et DPE par logement avec facture énergétique ; avis de taxe foncière réel ; plans et surfaces par niveau ; emprise ferroviaire, servitudes et bruit ; conformité du PLU pour une éventuelle division ; état de la charpente et de la couverture",
            "<strong>Option de sortie à instruire :</strong> la division en deux lots pour vendre un logement rénové et conserver l'autre. La vente d'environ 92 m² à 2 600 €/m² dégagerait quelque 227 000 € net d'honoraires, qui effacent la plus grande part de la dette. Mais la division juridique n'existe pas et le prix d'un demi-bien atypique n'est étayé par aucune transaction comparable",
            "<strong>Point de méthode :</strong> aucun chiffre de travaux ne doit entrer dans l'offre sans devis. Sur ce dossier, l'écart entre 600 et 1 200 €/m² de rénovation vaut 110 000 € de prix d'achat, soit plus de la moitié du prix affiché. Une visite avec un artisan est la condition d'une offre",
            "<strong>Rappel de marché (sources au 21/09/2026) :</strong> maison Meyrargues 3 642 €/m² (immovrai DVF 2025) et 3 240 €/m² (PAP) ; évolution −8,3 % sur un an (immovrai), −15,2 % (PAP) ; 41 ventes de maisons et 17 appartements sur un an ; 3 % de passoires F ou G seulement, classe D majoritaire, année médiane de construction 1992 ; taxe foncière bâtie 34,70 % et TEOM 14,00 % ; loyers observés 1 610 € pour 152 m² et 2 462 € CC pour 150 m² ; loyer médian DHUP 15,81 €/m²/mois",
        ],
    )}

    # -------------------------------------------------- generation de la fiche
    c = gen.CONF[SLUG]
    html = gen.TEMPLATE.format(
        titre_court=c['titre_court'], adresse=c['adresse'], date_fr=c['date_fr'],
        source=c['source'], url=c['url'], badge=c['badge'], strategie=c['strategie'],
        fiscal_note=c['fiscal_note'],
        prix=eur(rec['annonce']['prix_affiche_euros']),
        surface=f"{rec['bien']['surfaces']['carrez_m2']:.0f} m²",
        prix_m2=f"{rec['annonce']['prix_affiche_euros'] / rec['bien']['surfaces']['carrez_m2']:,.0f} €/m²".replace(',', ' '),
        revient=eur(base['prix_revient_total']),
        valeur=eur(rec['marche']['valeur']['retenue_euros']),
        revenus=eur(1850),
        rdt_revient=fr(roi_18), rdt_valeur=fr(roi_an),
        note=fr(note), note_cls=fr(note).replace(',', '-'),
        lat=c['lat'], lon=c['lon'], quartier=c['quartier'],
        intro_attr=c['intro_attr'], profil=c['profil'], concl_attr=c['concl_attr'],
        attrs=gen.attr_html(rec), intro_strat=c['intro_strat'], strats=gen.strategy_html(rec),
        rationale=c['rationale'], identite=gen.identite_html(c['identite']),
        projections=projections,
        risques=gen.risques_html(rec),
        verdict_cls={"acheter": "buy", "negocier": "nego", "fuir": "pass"}.get(verdict, "nego"),
        stance=c['stance'], prix_plafond=c['prix_plafond'],
        leviers=gen.leviers_html(c['leviers']),
        meta="\n".join(f"      <p>{m}</p>" for m in c['meta']),
    )
    d = os.path.join(ROOT, 'analyses', SLUG)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(html)
    print(f"{SLUG} : ecrit ({len(html):,} octets) | note {note} {verdict} | ROI {roi_18} % sur 18 mois")


if __name__ == '__main__':
    main()
