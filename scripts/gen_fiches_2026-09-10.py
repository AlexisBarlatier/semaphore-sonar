#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genere les fiches HTML des 3 analyses du 10/09/2026 (chiffres du moteur)."""
import copy, json, os, sys

sys.path.insert(0, '/home/alexis-barlatier/Documents/Semaphore-sonar/scripts')
from analyse_app import engine, scoring

ROOT = '/home/alexis-barlatier/Documents/Semaphore-sonar'
BASE = os.path.join(ROOT, 'analyses', 'analyses.json')
RECS = {r['slug']: r for r in json.load(open(BASE))['analyses']}


def eur(v):
    return f"{v:,.0f}".replace(',', ' ')


def scen(rec, vac, loyers=None):
    v = copy.deepcopy(rec)
    v['hypotheses']['vacance_base_pct'] = vac
    if loyers:
        for l, m in zip(v['marche']['loyers'], loyers):
            l['loyer_mensuel_euros'] = m
    r = engine.compute(v)
    note, verdict, comp = scoring.note_et_verdict(v, r)
    return r, note, verdict, comp


def sc_html(r):
    f = r['fiscal']
    return f"""            <tr><td>Revenu brut annuel</td><td class="num">{eur(r['revenus_bruts_annuels'])} €</td></tr>
            <tr><td>Vacance locative</td><td class="num">-{eur(r['revenus_bruts_annuels'] - f['ebe'] and 0)} €</td></tr>
            <tr class="subtotal"><td>EBE avant IS</td><td class="num">{eur(f['ebe'])} €</td></tr>
            <tr><td>Amortissement</td><td class="num">{eur(f['amortissement'])} €</td></tr>
            <tr><td>IS (15 %)</td><td class="num">-{eur(f['is_annuel'])} €</td></tr>
            <tr class="highlight"><td>CF net mensuel</td><td class="num">{eur(f['cf_mensuel_net'])} €</td></tr>"""


def bloc_scenarios(rec, titre, intro, loyers_base=None):
    rb, nb, vb, _ = scen(rec, rec['hypotheses']['vacance_base_pct'], loyers_base)
    ro, no, vo, _ = scen(rec, rec['hypotheses']['vacance_best_pct'], loyers_base)
    rp, np_, vp, _ = scen(rec, rec['hypotheses']['vacance_worst_pct'], loyers_base)
    sbd = round(rb['rendements']['net_sur_revient_pct'], 1)
    sbv = round(rb['rendements']['net_sur_valeur_pct'], 1)
    sod = round(ro['rendements']['net_sur_revient_pct'], 1)
    sodv = round(ro['rendements']['net_sur_valeur_pct'], 1)
    spd = round(rp['rendements']['net_sur_revient_pct'], 1)
    spdv = round(rp['rendements']['net_sur_valeur_pct'], 1)
    return f"""  <section class="financial-projections">
    <h2>{titre}</h2>
    <p class="attractiveness-intro">{intro}</p>
    <div class="projections-grid">
      <div class="projection-card scenario-base">
        <h3>Scénario Base</h3>
        <p class="scenario-subtitle">Vacance {rec['hypotheses']['vacance_base_pct']:.0f} % - hypothèses retenues</p>
        <table class="projection-table"><tbody>
{sc_html(rb)}
        </tbody></table>
      </div>
      <div class="projection-card scenario-optimiste">
        <h3>Scénario Optimiste</h3>
        <p class="scenario-subtitle">Vacance {rec['hypotheses']['vacance_best_pct']:.0f} % - relocation rapide</p>
        <table class="projection-table"><tbody>
{sc_html(ro)}
        </tbody></table>
      </div>
      <div class="projection-card scenario-pessimiste">
        <h3>Scénario Pessimiste</h3>
        <p class="scenario-subtitle">Vacance {rec['hypotheses']['vacance_worst_pct']:.0f} % - tension locative</p>
        <table class="projection-table"><tbody>
{sc_html(rp)}
        </tbody></table>
      </div>
    </div>
    <table class="projection-table compare">
      <thead><tr><th>Indicateur</th><th class="num">Base</th><th class="num">Optimiste</th><th class="num">Pessimiste</th></tr></thead>
      <tbody>
        <tr><td>EBE avant IS</td><td class="num">{eur(rb['fiscal']['ebe'])} €</td><td class="num">{eur(ro['fiscal']['ebe'])} €</td><td class="num">{eur(rp['fiscal']['ebe'])} €</td></tr>
        <tr><td>CF net mensuel</td><td class="num">{eur(rb['fiscal']['cf_mensuel_net'])} €</td><td class="num">{eur(ro['fiscal']['cf_mensuel_net'])} €</td><td class="num">{eur(rp['fiscal']['cf_mensuel_net'])} €</td></tr>
        <tr><td>Rendement net (revient)</td><td class="num">{sbd} %</td><td class="num">{sod} %</td><td class="num">{spd} %</td></tr>
        <tr><td>Rendement net (valeur)</td><td class="num">{sbv} %</td><td class="num">{sodv} %</td><td class="num">{spdv} %</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix"><p class="attractiveness-intro">{LECTURE[rec['slug']]}</p></div>
  </section>"""


def attr_html(rec):
    out = []
    for a in rec['analyse']['attractivite']:
        s = a['score']
        out.append(f"""      <div class="attr-card">
        <span class="attr-label">{LABELS[a['dimension']]}</span>
        <span class="attr-score"><strong>{s}/10</strong></span>
        <div class="attr-bar-track"><div class="attr-bar-fill" style="width:{s*10}%"></div></div>
        <p class="attr-detail">{a['justification']}</p>
      </div>""")
    return "\n".join(out)


def risques_html(rec):
    out = []
    for r in rec['analyse']['risques']:
        sev = r['severite']
        out.append(f"""        <tr>
          <td>{r['facteur']}</td>
          <td>{r['detail']}</td>
          <td><span class="severity severity-{sev}">{sev}/5</span></td>
        </tr>""")
    return "\n".join(out)


def strategy_html(rec):
    out = []
    for i, s in enumerate(rec['analyse']['strategies_explorees']):
        cls = ' class="strategy-row selected"' if i == 0 else ''
        out.append(f"""        <tr{cls}>
          <td><strong>{s['strategie']}</strong></td>
          <td>{s['lots']}</td>
          <td>{s.get('rendement', '')}</td>
          <td>{s.get('faisabilite', '')}</td>
          <td>{s.get('risque', '')}</td>
        </tr>""")
    return "\n".join(out)


TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Analyse - {titre_court}</title>
  <link rel="stylesheet" href="../../style.css">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
</head>
<body>

<header class="report-header">
  <nav class="report-breadcrumb"><a href="../../analyses/index.html">← Retour aux analyses</a></nav>
  <h1>Analyse d'investissement</h1>
  <p class="report-address">{adresse}</p>
  <p class="report-date">Analyse générée le {date_fr}</p>
  <p class="report-source">Source : {source}</p>
  <div class="report-source-link"><a href="{url}">{url}</a></div>
</header>

<main>

  <div class="strategy-banner">
    <span class="strategy-badge">{badge}</span>
    <p>Stratégie retenue : <strong>{strategie}</strong> - {fiscal_note}</p>
  </div>

  <section class="summary-cards">
    <div class="card"><span class="card-label">Prix affiché</span><span class="card-value">{prix} €</span></div>
    <div class="card"><span class="card-label">Surface</span><span class="card-value">{surface}</span></div>
    <div class="card"><span class="card-label">Prix / m²</span><span class="card-value">{prix_m2}</span></div>
    <div class="card"><span class="card-label">Prix de revient</span><span class="card-value">{revient} €</span></div>
    <div class="card"><span class="card-label">Valeur marché retenue</span><span class="card-value">{valeur} €</span></div>
    <div class="card"><span class="card-label">Revenus bruts</span><span class="card-value">{revenus} €/mois</span></div>
    <div class="card"><span class="card-label">Rentabilité nette</span><span class="card-value">{rdt_revient} % / {rdt_valeur} %</span></div>
    <div class="card card-verdict note-{note_cls}"><span class="card-label">Note</span><span class="card-value">{note}/10</span></div>
  </section>

  <section class="map-section">
    <h2>Localisation</h2>
    <div id="map-container" data-lat="{lat}" data-lon="{lon}" data-address="{adresse}"></div>
  </section>

  <section class="attractiveness">
    <h2>Attractivité - {quartier}</h2>
    <p class="attractiveness-intro">{intro_attr}</p>
    <div class="attractiveness-grid">
{attrs}
    </div>
    <div class="attractiveness-summary">
      <p><strong>Profil locataire cible :</strong> {profil}</p>
      <p><strong>Conclusion :</strong> {concl_attr}</p>
    </div>
  </section>

  <section class="strategy-exploration">
    <h2>Stratégie d'exploitation</h2>
    <p class="attractiveness-intro">{intro_strat}</p>
    <table class="strategy-table">
      <thead><tr><th>Stratégie</th><th>Lots</th><th>Rendement</th><th>Faisabilité</th><th>Risque</th></tr></thead>
      <tbody>
{strats}
      </tbody>
    </table>
    <div class="strategy-rationale"><p>{rationale}</p></div>
  </section>

  <section class="identity-sheet">
    <h2>Fiche d'identité</h2>
    <table class="identity-table">
      <tbody>
{identite}
      </tbody>
    </table>
  </section>

{projections}

  <section class="risk-matrix">
    <h2>Matrice de risques</h2>
    <table class="risk-table">
      <thead><tr><th>Facteur de risque</th><th>Détail</th><th>Sévérité</th></tr></thead>
      <tbody>
{risques}
      </tbody>
    </table>
  </section>

  <section class="verdict {verdict_cls}">
    <h2>Recommandation</h2>
    <div class="verdict-decision"><p class="verdict-stance">{stance}</p></div>
    <div class="verdict-details">
      <p><strong>Prix plafond recommandé :</strong> {prix_plafond}</p>
      <p><strong>Leviers de négociation :</strong></p>
      <ul>
{leviers}
      </ul>
    </div>
    <div class="verdict-meta">
{meta}
    </div>
  </section>

  <footer class="report-signature">
    <p>Analyse réalisée par</p>
    <p class="signature-names">Rémy Barlatier - 06 27 84 53 50 - sarl.spbi@gmail.com</p>
    <p class="signature-names">Alexis Barlatier</p>
  </footer>

</main>

<script>
  (function() {{
    var mapEl = document.getElementById('map-container');
    var lat  = parseFloat(mapEl.getAttribute('data-lat'));
    var lon  = parseFloat(mapEl.getAttribute('data-lon'));
    var addr = mapEl.getAttribute('data-address');
    if (isNaN(lat) || isNaN(lon)) {{
      mapEl.innerHTML = '<p class="map-fallback">Coordonnées non disponibles pour « ' + addr + ' »</p>';
      return;
    }}
    var map = L.map('map-container').setView([lat, lon], 15);
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      attribution: '&copy; OpenStreetMap contributors', maxZoom: 19
    }}).addTo(map);
    L.marker([lat, lon]).addTo(map).bindPopup(addr).openPopup();
  }})();
</script>

</body>
</html>
"""

LABELS = {
    'transports': 'Transports', 'commerces': 'Commerces & services', 'ecoles': 'Écoles & crèches',
    'securite': 'Sécurité & cadre de vie', 'demande_locative': 'Demande locative',
    'dynamisme': 'Dynamisme économique',
}

CONF = {}


def identite_html(pairs):
    return "\n".join(f"        <tr><th>{k}</th><td>{v}</td></tr>" for k, v in pairs)


def leviers_html(items):
    return "\n".join(f"        <li>{t}</li>" for t in items)


LECTURE = {
    "2026-09-10-t4-73m2-aguillon-toulon": "Le dossier ne vit pas par son rendement mais par son prix d'entrée. En location nue, le rendement net plafonne à 3,7 % sur le prix de revient et 3,6 % sur la valeur de marché : deux points et demi sous le seuil de 6,5 % que s'impose la SCI. Le coupable n'est pas le loyer (correct pour le quartier) mais la masse de charges fixes : copropriété avec ascenseur et taxe foncière toulonnaise absorbent 24 à 27 % du loyer brut, avant vacance et provision. En MDB, la revente crédible d'un bien qui reste en DPE E se situe entre 2 900 et 3 100 €/m² : la marge est nulle à l'affichage, et la rénovation énergétique (+25 k€) ne se rentabilise pas (elle rapporte 200 à 300 €/m² de revente). Prix d'équilibre : 116 000 à 126 000 € en MDB, 137 000 € pour une marge de 15 %.",
    "2026-09-10-lot-3-logements-rdc-toulon": "Le rendement brut paraît séduisant (7,9 % sur le prix de revient) parce que les petites surfaces se louent cher au m² : T2 et studios sont la meilleure adéquation du marché toulonnais. Mais trois logements, c'est trois impositions foncières, trois baux à gérer et une rotation plus fréquente : la vacance retenue est de 8 %, pas 5 %. Après charges et fiscalité, le rendement net tombe à 4,0 % sur le revient et 4,8 % sur la valeur. Le ratio coût/valeur de 1,19 confirme que le prix payé dépasse la valeur du bien en l'état : la marge ne peut venir que de la négociation. Surtout, ce chiffrage repose sur des loyers estimés : l'annonce n'en communique aucun.",
    "2026-09-10-t4-66m2-champ-de-mars-toulon": "Le principal défaut du dossier est son prix : 2 394 €/m² contre 2 228 €/m² de moyenne MeilleursAgents sur le secteur, soit environ 7 % au-dessus du marché. Il n'y a donc aucune décote d'entrée à capter, et tout le rendement devrait venir de la négociation. En location nue avec provision d'impayés, le rendement net ressort à 4,2 % sur le prix de revient et 4,9 % sur la valeur, contre un seuil de parc de 6,5 %. L'étude colocation menée sur ce bien est sans appel : le loyer brut progresse de 42 % mais les charges de gestion (fluides, ménage, mobilier) de 168 % - la colocation est moins rentable que le nu sur un 66 m² à trois petites chambres.",
}

CONF = {
    "2026-09-10-t4-73m2-aguillon-toulon": dict(
        titre_court="T4 73 m2, quartier Aguillon, Toulon",
        adresse="Quartier Aguillon, Toulon (83000) - T4 de 73 m², 1er étage avec ascenseur, DPE E",
        date_fr="10 septembre 2026",
        source="SeLoger - annonce 26ZBKX4HBQAP (agence Ibox Atlas Immobilier, Toulon)",
        url="https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/toulon-83000/26ZBKX4HBQAP",
        badge="Investissement locatif",
        strategie="Location longue durée nue",
        fiscal_note="SCI à l'IS (15 %), amortissement sur 90 % du prix de revient sur 30 ans",
        lat="43.1160", lon="5.9470",
        quartier="quartier Aguillon, Toulon (83000)",
        intro_attr="Le quartier Aguillon occupe l'est toulonnais, entre le centre-ville et la place du Mourillon. Les ventes réelles y ressortent à 3 162 €/m² (DVF, Lestimo 09/2026) et les offres en cours à 2 820 €/m² (efficity) : c'est un quartier de ville utile, résidentiel, correctement desservi, sans être le bord de mer. Le bien s'affiche à 2 240 €/m², soit 29 % sous les ventes réelles du quartier - mais cette décote paie exactement son état (salle de bain à moderniser) et son DPE E.",
        profil="couples et familles actives, demande locative stable sur un quartier résidentiel proche du Mourillon",
        concl_attr="Adéquation moyenne (7,0/10). Le quartier est un bon emplacement locatif de seconde couronne : commerces, écoles et desserte présents, valeurs stables. Le problème du dossier n'est pas le quartier, c'est la structure de charges de l'immeuble (ascenseur, copropriété de 77 lots) rapportée à un loyer de 950 €.",
        intro_strat="Deux lectures ont été testées : la conservation en location nue et l'achat-rénovation-revente (MDB). La seconde n'est crédible qu'à un prix d'entrée nettement inférieur.",
        rationale="La location nue est la stratégie retenue par défaut, mais elle ne passe pas le seuil de rendement de la SCI : 3,7 % net sur le prix de revient, contre 6,5 % exigés. Le MDB est la lecture qui donnerait un sens à ce prix : le bien s'affiche 29 % sous les ventes réelles du quartier, ce qui ressemble à une décote d'entrée. Vérification faite, ce n'est pas une aubaine : la revente crédible d'un bien qui reste en DPE E après remise en état se situe entre 2 900 et 3 100 €/m², pas à la moyenne du quartier. À l'affichage, la marge MDB est nulle (-1 300 à -5 700 €). Et traiter le DPE (isolation intérieure, menuiseries, chauffage : +25 k€) ne se rentabilise pas : cela rapporte 200 à 300 €/m² de revente, soit moins que l'euro investi. Conclusion : le dossier n'a de sens qu'à un prix d'entrée de 116 000 à 126 000 €.",
        identite=[
            ("Adresse", "Quartier Aguillon, Toulon (83000) - adresse exacte non communiquée dans l'annonce"),
            ("Type de bien", "Appartement T4 traversant de 73 m², 1er étage sur 7, ascenseur, 3 chambres, cuisine ouverte, salle de bain et WC séparés, 2 balcons (10 m²), pas de cave"),
            ("Immeuble", "Construit en 1980 - copropriété de 77 lots - chauffage individuel électrique - annoncé résidence calme et bien entretenue"),
            ("DPE / GES", "<strong>DPE E</strong> / GES B - interdiction de location en 2034 - facture énergétique annoncée 1 465 à 1 981 €/an (chauffage électrique)"),
            ("Prix affiché", "163 500 € soit 2 240 €/m² - honoraires à la charge du vendeur"),
            ("Valeur de marché retenue", "180 000 à 200 000 €, retenue <strong>190 000 €</strong> (2 600 €/m²) - ventes réelles du quartier 3 162 €/m² (DVF), offres 2 820 €/m² ; décote d'état (salle de bain vétuste) et de DPE E"),
            ("Loyer retenu", "950 €/mois charges comprises (13 €/m²), soit environ 880 € hors charges - marché local : T4 102 m² à 1 255 € CC, T3 67 m² à 900 €"),
            ("Travaux", "Modernisation de la salle de bain et rafraîchissement : <strong>8 000 €</strong> retenus (fourchette 6-12 k€, devis avant offre). Rénovation énergétique (15-30 k€) chiffrée séparément et jugée non rentable"),
            ("Charges annuelles", "Copropriété ~1 400 € (ascenseur, 77 lots) + taxe foncière ~1 250 € + PNO 180 € + entretien 300 € + comptabilité 400 € - <strong>estimations à confirmer</strong> sur budget prévisionnel et avis de taxe foncière"),
            ("Fiscalité", "SCI à l'IS : IS 15 % sur le résultat, amortissement de 90 % du prix de revient sur 30 ans"),
            ("Prix de revient", "<strong>184 580 €</strong> = prix 163 500 € + frais d'acquisition ~13 080 € (8 %) + travaux 8 000 €"),
        ],
        stance="<strong>À négocier - et seulement à 120 000 € environ</strong>. Le bien est correct, l'emplacement aussi : un T4 de 73 m² avec ascenseur et deux balcons dans un quartier résidentiel de l'est toulonnais, à 950 € de loyer, ce n'est pas un mauvais produit. Mais le rendement net plafonne à 3,7 % sur le prix de revient, très loin du seuil de 6,5 % de la SCI, et le MDB est nul à l'affichage : la revente crédible d'un logement qui reste en DPE E est de 2 900 à 3 100 €/m², pas la moyenne du quartier. La décote affichée de 29 % n'est donc pas une aubaine : elle paie l'état et le DPE. Seul un prix d'entrée autour de 120 000 € rendrait le dossier défendable en locatif comme en MDB.",
        prix_plafond="120 000 € en locatif et MDB, soit 16 % sous l'affichage. À ce prix, le rendement net ressort autour de 5 % en nue et la marge MDB atteint 15 % en revente à 3 300 €/m². Au-dessus de 137 000 €, le dossier n'a plus aucune raison d'être dans le parc.",
        leviers=[
            "Le DPE E est le premier levier : le logement reste louable jusqu'en 2034, donc le vendeur n'a aucune urgence réglementaire - mais l'acquéreur, lui, achète un actif dont la valeur de revente est amputée de 10 à 15 % par le classement énergétique, et une facture de 1 500 à 2 000 €/an qui pèse sur le loyer négociable",
            "Les charges de copropriété sont à vérifier pièce en pièce : un immeuble de 1980 de 77 lots avec ascenseur peut réserver des appels de fonds (toiture, ravalement, ascenseur). Exiger les trois derniers PV d'assemblée générale et le budget prévisionnel",
            "La salle de bain « à moderniser » n'est pas chiffrée : la fourchette est de 6 à 12 k€, et sur un immeuble de 1980 il faut prévoir de l'électricité et de la plomberie. Devis avant offre",
            "Le prix affiché est au-dessus de la valeur du bien en l'état : le vendeur ne peut pas ignorer que son bien est en DPE E avec une salle de bain d'origine. C'est l'argument central de la négociation",
        ],
        meta=[
            "<strong>Régime fiscal retenu :</strong> SCI à l'IS (15 %) - amortissement sur 90 % du prix de revient sur 30 ans",
            "<strong>Frais d'acquisition estimés :</strong> ~13 080 € (8 % du prix affiché)",
            "<strong>Enveloppe travaux :</strong> 8 000 € (salle de bain et rafraîchissement), hors rénovation énergétique chiffrée à 15-30 k€ et jugée non rentable",
            "<strong>Contrôle à faire avant toute offre :</strong> budget prévisionnel de copropriété, PV d'AG des trois derniers exercices, avis de taxe foncière, devis de la salle de bain, diagnostics complets",
        ],
    ),
}


CONF["2026-09-10-lot-3-logements-rdc-toulon"] = dict(
    titre_court="Lot de 3 logements RDC, Toulon",
    adresse="Toulon (83000) - lot complet de 3 logements en rez-de-chaussée : T2 32,76 m² + studio 19,81 m² + studio 21,39 m²",
    date_fr="10 septembre 2026",
    source="SeLoger - annonce 26C7IRSUZ172 (agence Illiz, Déborah Grifo) - bien en exclusivité",
    url="https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/toulon-83000/26C7IRSUZ172",
    badge="Investissement locatif",
    strategie="Location longue durée nue - trois logements conservés",
    fiscal_note="SCI à l'IS (15 %), amortissement sur 90 % du prix de revient sur 30 ans",
    lat="43.1242", lon="5.9280",
    quartier="Toulon (83000), quartier non précisé dans l'annonce",
    intro_attr="L'annonce ne communique ni l'adresse exacte ni le quartier : elle indique seulement « un secteur bien placé de Toulon, proche des commodités et des transports ». Les notes d'attractivité sont donc posées à dire d'expert, avec un quartier médian par défaut pour la sécurité, et devront être révisées dès l'obtention de l'adresse. Le bien est un lot complet de trois logements en rez-de-chaussée d'un immeuble de 1925 : T2 de 32,76 m², studio de 19,81 m², studio de 21,39 m², soit 73,96 m² habitables.",
    profil="jeunes actifs, étudiants et personnes seules - c'est le segment le plus demandé du marché toulonnais",
    concl_attr="Adéquation moyenne (6,7/10), mais note non vérifiable : l'absence de quartier dans l'annonce est en soi une information manquante de premier ordre. Les petites surfaces constituent en revanche le meilleur segment locatif de Toulon : demande structurellement forte, loyers au m² supérieurs aux grandes surfaces, rotation rapide.",
    intro_strat="Deux lectures testées : la conservation en location nue des trois lots, et l'achat-rénovation-revente avec revente à la découpe (les trois logements étant des lots distincts, la sortie séparée est possible).",
    rationale="La location nue est retenue : c'est la seule lecture qui exploite la force réelle du bien - trois petits logements, segment le plus liquide et le plus demandé du marché toulonnais. Le rendement brut paraît flatteur (7,9 % sur le prix de revient), mais il ne survit pas aux charges : trois copropriétés à financer, trois taxes foncières, trois baux à gérer, et une vacance plus fréquente qu'un lot unique. Net après charges, fiscalité et provision de rotation : 4,0 % sur le prix de revient et 4,8 % sur la valeur retenue. La revente à la découpe, testée en MDB, est franchement perdante : avec 45 k€ de travaux sur trois logements, le coût de revient atteint 257 000 € quand la revente à 3 000 €/m² n'en rapporte que 222 000 € (marge -46 000 €). C'est le prix d'entrée qui est trop haut, pas la stratégie de sortie.",
    identite=[
        ("Adresse", "Toulon (83000) - <strong>quartier et adresse non communiqués</strong> dans l'annonce : « secteur bien placé, proche commodités et transports ». Pointé sur le centre de Toulon sur la carte"),
        ("Composition", "Lot complet de 3 logements au rez-de-chaussée : T2 de 32,76 m², studio de 19,81 m², studio de 21,39 m² - immeuble de 1925, 6 étages, sans ascenseur, exposition sud, 3 WC séparés, pas de cave, pas de balcon"),
        ("Surfaces", "73,96 m² habitables (somme des trois lots) - <strong>l'annonce affiche 86,7 m², soit un écart de 12,74 m² à justifier</strong>. Conséquence : le prix au m² réel est de 2 555 €, pas 2 180 €"),
        ("Occupation", "Les trois logements sont <strong>loués en 3/6/9</strong> - échéances, loyers et profils des locataires non communiqués"),
        ("Prix affiché", "189 000 € - honoraires à la charge du vendeur"),
        ("Valeur de marché retenue", "195 000 à 225 000 €, retenue <strong>210 000 €</strong> (2 840 €/m² sur la surface réelle) - Toulon : ~3 200 €/m² en moyenne (MeilleursAgents 09/2026), décote pour le RDC d'immeuble ancien et l'état à rénover. Confiance faible : quartier inconnu"),
        ("Loyers", "<strong>Aucun loyer communiqué dans l'annonce.</strong> Hypothèses de marché retenues : T2 524 €/mois (16 €/m²), studio 19,81 m² 396 €/mois (20 €/m²), studio 21,39 m² 428 €/mois (20 €/m²), soit 1 348 €/mois au total. Les baux en cours peuvent être nettement inférieurs s'il s'agit de baux anciens"),
        ("Travaux", "« Travaux de rénovation à prévoir » - non chiffrés par le vendeur. Hypothèse retenue : <strong>45 000 €</strong> (15 k€ par logement : réseaux, cloisons, sols, salle d'eau, cuisine). Fourchette 30-60 k€"),
        ("Charges annuelles", "Copropriété ~1 100 € (3 lots, 22 lots au total, sans ascenseur) + taxe foncière ~1 800 € (trois impositions) + PNO 250 € + entretien 500 € + comptabilité 400 € - <strong>estimations à confirmer</strong>"),
        ("Fiscalité", "SCI à l'IS : IS 15 % sur le résultat, amortissement de 90 % du prix de revient sur 30 ans"),
        ("Prix de revient", "<strong>249 120 €</strong> = prix 189 000 € + frais d'acquisition ~15 120 € (8 %) + travaux 45 000 €"),
    ],
    stance="<strong>À négocier - 140 000 € maximum, et seulement après avoir obtenu les loyers réels.</strong> Le raisonnement est simple : trois petites surfaces dans une ville où la demande locative est structurellement forte, c'est un bon produit. Mais le dossier est vendu à un prix qui ne laisse aucune marge : le ratio coût/valeur ressort à 1,19, c'est-à-dire que l'acquéreur paie 19 % au-dessus de la valeur du bien dans son état actuel. Ajoutez trois impositions foncières, une vacance plus fréquente qu'un lot unique et 30 à 60 k€ de travaux non chiffrés, et le rendement net tombe à 4,0 %. Tant que les loyers réels et les surfaces Carrez ne sont pas communiqués, il n'y a pas de dossier : il y a une annonce.",
    prix_plafond="140 000 € (soit environ 1 890 €/m² sur la surface réelle), qui ramène le rendement net au-dessus de 5 % et laisse une marge en cas de travaux lourds. Au-dessus de 160 000 €, le dossier ne se défend plus du tout.",
    leviers=[
        "Les loyers en place sont la première exigence : sans eux, aucun chiffrage sérieux n'est possible. Demander les trois baux et les dernières quittances - s'il s'agit de baux anciens sous le marché, la décote est légitime et importante",
        "L'écart de surface (12,74 m² entre la somme des lots et la surface affichée) doit être tranché par les surfaces Carrez de chaque lot : c'est un point de négociation direct sur le prix au m²",
        "Les travaux ne sont pas chiffrés : exiger un devis ou faire chiffrer trois scénarios (remise en état légère, rénovation standard, rénovation lourde). Sur un immeuble de 1925, l'électricité et la plomberie sont les postes qui dérapent",
        "Le rez-de-chaussée d'un immeuble de 1925 justifie une visite technique : humidité, remontées capillaires, ventilation. Un RDC dégradé peut coûter 10 à 20 k€ de traitement",
        "Trois logements = trois baux : négocier l'échéancier des baux en cours, car une relocation simultanée des trois lots représenterait plusieurs mois de vacance cumulée",
    ],
    meta=[
        "<strong>Régime fiscal retenu :</strong> SCI à l'IS (15 %) - amortissement sur 90 % du prix de revient sur 30 ans",
        "<strong>Frais d'acquisition estimés :</strong> ~15 120 € (8 % du prix affiché)",
        "<strong>Enveloppe travaux :</strong> 45 000 € (hypothèse 15 k€ par logement), fourchette 30-60 k€ - à confirmer par devis",
        "<strong>Contrôle à faire avant toute offre :</strong> les trois baux et quittances, les surfaces Carrez par lot, les PV d'AG et le budget de copropriété, l'adresse exacte et le quartier, un devis de rénovation, un état des lieux technique du RDC",
    ],
)

CONF["2026-09-10-t4-66m2-champ-de-mars-toulon"] = dict(
    titre_court="T4 66 m2, Champ de Mars, Toulon",
    adresse="Quartier Champ de Mars, Toulon Est (83000) - T4 de 66 m², 2e étage sans ascenseur",
    date_fr="10 septembre 2026",
    source="SeLoger - annonce 26RTY777JQHN (annonce orientée investisseur / colocation)",
    url="https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/toulon-83000/26RTY777JQHN",
    badge="Investissement locatif",
    strategie="Location longue durée nue (colocation testée et écartée)",
    fiscal_note="SCI à l'IS (15 %), amortissement sur 90 % du prix de revient sur 30 ans, provision d'impayés 1 % (pas de GLI)",
    lat="43.1180", lon="5.9280",
    quartier="Champ de Mars, Toulon Est (83000)",
    intro_attr="Le secteur Jardin du Champ de Mars se situe dans l'est toulonnais, à proximité du bassin universitaire de La Garde : c'est ce que vend l'annonce, et la géographie le confirme. Les prix moyens du secteur ressortent à 2 228 €/m² (MeilleursAgents), avec une fourchette très large selon les biens. Le bien s'affiche à 2 394 €/m², soit environ 7 % au-dessus de cette moyenne : il n'y a pas de décote d'entrée sur ce dossier.",
    profil="étudiants et jeunes actifs du bassin universitaire de La Garde, puis couples en location nue",
    concl_attr="Adéquation moyenne (6,8/10). L'atout réel est la proximité de l'enseignement supérieur, qui soutient la demande locative. Le point faible est le prix : à 7 % au-dessus du marché du secteur, le dossier ne peut pas se réparer par l'exploitation, seulement par la négociation.",
    intro_strat="Deux usages ont été chiffrés : la location nue et la colocation meublée en trois chambres, angle mis en avant par l'annonce. Le second a été testé en détail puis écarté.",
    rationale="La location nue est retenue. La colocation a été chiffrée à la demande de Rémy, et le résultat est contre-intuitif : sur un 66 m² découpé en trois chambres de 9 à 11 m², le loyer brut progresse de 42 % (1 320 € contre 930 €) mais les charges de gestion - fluides, ménage, mobilier, provision de renouvellement - progressent de 168 %. Résultat : EBE de 651 €/mois en colocation contre 698 à 708 €/mois en location nue avec provision d'impayés. La colocation ne sauve pas ce dossier ; elle le dégrade. Le marché confirme : le comparable direct d'un T4 meublé de 67 m² à trois chambres se loue à partir de 450 € par chambre, pas 530. Reste la location nue : rendement net de 4,2 % sur le prix de revient, 4,9 % sur la valeur, contre un seuil de 6,5 %.",
    identite=[
        ("Adresse", "Quartier Champ de Mars, Toulon Est (83000) - adresse exacte non communiquée"),
        ("Composition", "T4 de 66 m² au 2e étage sur 4, sans ascenseur - 3 chambres, cuisine séparée, cellier, WC indépendant, salle de bain, pas de cave"),
        ("Copropriété", "20 lots - charges annoncées 960 €/an (80 €/mois), niveau faible : c'est un point positif du dossier"),
        ("DPE / GES", "DPE D / GES B - chauffage individuel électrique - aucun travaux annoncé"),
        ("Prix affiché", "158 000 € soit 2 394 €/m² - honoraires à la charge du vendeur - environ 7 % au-dessus de la moyenne du secteur (2 228 €/m²)"),
        ("Valeur de marché retenue", "140 000 à 154 000 €, retenue <strong>147 000 €</strong> (2 228 €/m²) - MeilleursAgents secteur Jardin du Champ de Mars"),
        ("Loyer retenu", "930 €/mois en location nue (14 €/m²) - marché local 860 à 950 € pour un T4 de ce type. En colocation : 3 chambres à 400-450 € maximum compte tenu de leur taille"),
        ("Travaux", "Aucun travaux annoncé - DPE D, pas de contrainte réglementaire avant 2034"),
        ("Charges annuelles", "Copropriété 960 € + taxe foncière ~950 € + PNO 200 € + entretien 300 € + comptabilité 400 € + provision d'impayés 1 % - <strong>estimations à confirmer</strong>"),
        ("Fiscalité", "SCI à l'IS : IS 15 % sur le résultat, amortissement de 90 % du prix de revient sur 30 ans. Pas de GLI : provision d'auto-assurance de 1 % du loyer annuel (doctrine du groupe)"),
        ("Prix de revient", "<strong>170 640 €</strong> = prix 158 000 € + frais d'acquisition ~12 640 € (8 %)"),
    ],
    stance="<strong>À négocier - 120 000 € environ, en location nue.</strong> Le dossier n'est pas mauvais : les charges de copropriété sont faibles (960 €/an), le DPE D ne pose aucune contrainte, le bien est libre et la proximité universitaire soutient la demande. Mais le prix affiché est 7 % au-dessus du marché du secteur, ce qui ne laisse aucune marge, et le rendement net plafonne à 4,2 % sur le prix de revient avec une provision d'impayés. L'angle colocation mis en avant par l'annonce a été chiffré et écarté : sur trois chambres de 9 à 11 m², les charges de gestion mangent tout le gain de loyer. Prix cible pour tenir le seuil de 6,5 % : 116 000 à 119 000 €.",
    prix_plafond="120 000 € (soit 1 818 €/m², environ 24 % sous l'affichage). À ce prix, le rendement net avec provision d'impayés ressort autour de 6,5 %.",
    leviers=[
        "Le prix est le seul levier réel : le bien s'affiche 7 % au-dessus de la moyenne MeilleursAgents du secteur, sans décote d'entrée à capter. C'est l'argument central, chiffres à l'appui",
        "L'étude colocation démontre que l'argument de vente de l'annonce ne tient pas : 42 % de loyer brut en plus pour 168 % de charges en plus. À présenter au vendeur comme la preuve que la valeur locative du bien est bornée",
        "La taille des chambres est le plafond du potentiel : 66 m² pour trois chambres signifie des chambres de 9 à 11 m², ce qui limite le loyer à 400-450 € par chambre. À vérifier sur plan",
        "L'absence de cave et l'absence d'ascenseur au 2e étage sont deux moins-values à faire valoir, notamment pour la revente",
        "La provision d'impayés de 1 % (pas de GLI, doctrine du groupe) est déjà intégrée au calcul : ne pas se laisser opposer l'argument d'une assurance à souscrire",
    ],
    meta=[
        "<strong>Régime fiscal retenu :</strong> SCI à l'IS (15 %) - amortissement sur 90 % du prix de revient sur 30 ans - provision d'impayés 1 % du loyer annuel, pas de GLI",
        "<strong>Frais d'acquisition estimés :</strong> ~12 640 € (8 % du prix affiché)",
        "<strong>Enveloppe travaux :</strong> aucun travaux annoncé, DPE D",
        "<strong>Contrôle à faire avant toute offre :</strong> plan du logement (surface réelle des trois chambres), PV d'AG et budget de copropriété, avis de taxe foncière, diagnostics complets, échéancier des charges",
    ],
)


def main():
    for slug, c in CONF.items():
        rec = RECS[slug]
        r, note, verdict, comp = scen(rec, rec['hypotheses']['vacance_base_pct'])
        rd = r['rendements']
        html = TEMPLATE.format(
            titre_court=c['titre_court'], adresse=c['adresse'], date_fr=c['date_fr'],
            source=c['source'], url=c['url'], badge=c['badge'], strategie=c['strategie'],
            fiscal_note=c['fiscal_note'],
            prix=eur(rec['annonce']['prix_affiche_euros']),
            surface=f"{rec['bien']['surfaces']['carrez_m2']:.0f} m²",
            prix_m2=f"{rec['annonce']['prix_affiche_euros'] / rec['bien']['surfaces']['carrez_m2']:,.0f} €/m²".replace(',', ' '),
            revient=eur(r['prix_revient_total']),
            valeur=eur(rec['marche']['valeur']['retenue_euros']),
            revenus=eur(r['revenus_bruts_annuels'] / 12),
            rdt_revient=f"{rd['net_sur_revient_pct']:.1f}".replace('.', ','),
            rdt_valeur=f"{rd['net_sur_valeur_pct']:.1f}".replace('.', ','),
            note=f"{note:.1f}".replace('.', ','),
            note_cls=f"{note:.1f}".replace('.', '-'),
            lat=c['lat'], lon=c['lon'], quartier=c['quartier'],
            intro_attr=c['intro_attr'], profil=c['profil'], concl_attr=c['concl_attr'],
            attrs=attr_html(rec), intro_strat=c['intro_strat'], strats=strategy_html(rec),
            rationale=c['rationale'], identite=identite_html(c['identite']),
            projections=bloc_scenarios(rec, f"Projections financières - prix affiché {eur(rec['annonce']['prix_affiche_euros'])} € (SCI IS)", c['intro_strat']),
            risques=risques_html(rec), verdict_cls='nego', stance=c['stance'],
            prix_plafond=c['prix_plafond'], leviers=leviers_html(c['leviers']),
            meta="\n".join(f"      <p>{m}</p>" for m in c['meta']),
        )
        d = os.path.join(ROOT, 'analyses', slug)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(html)
        print(f"{slug} : ecrit ({len(html):,} octets) | note {note:.1f} {verdict} | rdt revient {rd['net_sur_revient_pct']:.1f}% valeur {rd['net_sur_valeur_pct']:.1f}%")


if __name__ == '__main__':
    main()
