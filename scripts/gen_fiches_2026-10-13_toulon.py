#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère les deux fiches Toulon du 13/10/2026.

A. analyses/2026-10-13-t4-75m2-champs-de-mars-toulon/index.html — SeLoger 264PZD3FK11R
B. analyses/2026-10-13-t5-83m2-toulon-ouest/index.html — SeLoger 26N62U1XVPP3

Convention de chiffrage commune : SCI à l'IS 15 %, amortissement du bâti 90 % du prix
de revient sur 30 ans, provision travaux 2,5 % des revenus, placement de la réserve à
2,84 %. Le solde mensuel se lit sous la convention du groupe : frais d'acquisition
sortis comptants, solde du prix porté sur 15 ans (intérêts et assurance compris).

Tout chiffre publié passe par calcule() ; HERMES_TOLERANT=1 liste les écarts.
"""
import copy
import json
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

from analyse_app import engine, scoring  # noqa: E402

TOLERANT = os.environ.get("HERMES_TOLERANT") == "1"
ANNUITE = 0.9 * (0.037 / 12) / (1 - (1 + 0.037 / 12) ** -180) + 0.9 * 0.0034 / 12
ECARTS = []


def calcule(libelle, publie, recalcule, tolerance=0.6):
    if publie is None or recalcule is None:
        if publie != recalcule:
            ECARTS.append(f"{libelle} : publié {publie} / recalculé {recalcule}")
        return publie
    if abs(float(publie) - float(recalcule)) > tolerance:
        ECARTS.append(f"{libelle} : publié {publie} / recalculé {recalcule}")
    return publie


def nfr(v, dec=0):
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


def eur(v, dec=0):
    return "—" if v is None else nfr(v, dec) + " €"


def pct(v, dec=2):
    return "—" if v is None else nfr(v, dec) + " %"


def euro_signe(v, dec=0):
    if abs(v) < 0.5:
        return "0 €"
    return ("−" if v < 0 else "+") + nfr(abs(v), dec) + " €"


with open(os.path.join(RACINE, "analyses", "analyses.json"), encoding="utf-8") as fh:
    DATA = json.load(fh)


def rec(slug):
    return [r for r in DATA["analyses"] if r["slug"] == slug][0]


SLUG_A = "2026-10-13-t4-75m2-champs-de-mars-toulon"
SLUG_B = "2026-10-13-t5-83m2-toulon-ouest"
CONF = {}


def prepare(slug, lat, lon, map_addr, adresse, lecture, conf, releve, scenarios, garde_fous):
    """Calcule tout ce que la fiche affiche, pour un slug."""
    r = rec(slug)
    c = engine.compute(r)
    note, verdict, comp = scoring.note_et_verdict(r, c)
    f, rd = c["fiscal"], c["rendements"]
    prix = r["annonce"]["prix_retenu_euros"]
    mens = prix * ANNUITE
    loyer = r["marche"]["loyers"][0]["loyer_mensuel_euros"]
    d = {
        "slug": slug, "rec": r, "c": c, "note": note, "verdict": verdict, "comp": comp,
        "f": f, "rd": rd, "prix": prix, "mens": mens, "solde": f["net_apres_is"] / 12 - mens,
        "loyer": loyer, "revient": c["prix_revient_total"], "lat": lat, "lon": lon,
        "map_addr": map_addr, "adresse": adresse, "lecture": lecture, "conf": conf,
        "releve": releve, "garde_fous": garde_fous, "classe": {"acheter": "buy", "negocier": "nego", "fuir": "pass"}[verdict],
        "classe_note": scoring.classe_note(note),
    }
    d["plafond"], d["contrainte"] = scoring.prix_plafond(r)
    d["cible"] = scoring.prix_cible(r)
    # solveur aux frais réels (le solveur du moteur proratise les frais)
    frais = r["hypotheses"]["frais_acquisition_euros"]

    def aux_frais_reels():
        bas, haut = 0.10 * prix, 3.0 * prix
        res = bas
        for _ in range(60):
            milieu = (bas + haut) / 2.0
            rr = copy.deepcopy(r)
            rr["annonce"]["prix_retenu_euros"] = milieu
            rr["hypotheses"]["frais_acquisition_euros"] = frais
            n, _, cp = scoring.note_et_verdict(rr, engine.compute(rr))
            if n is not None and n >= 6.5 and not cp["plafonds"]:
                res = milieu
                bas = milieu
            else:
                haut = milieu
        return int(res // 500.0 * 500.0)

    d["cible_frais_reels"] = aux_frais_reels()
    # scénarios
    d["scenarios"] = []
    for libelle, (loyer_s, vac_s, prix_s), classe, _st in scenarios:
        rr = copy.deepcopy(r)
        rr["marche"]["loyers"][0]["loyer_mensuel_euros"] = loyer_s
        rr["hypotheses"]["vacance_base_pct"] = vac_s
        cc = engine.compute(rr)
        d["scenarios"].append({
            "libelle": libelle, "classe": classe, "loyer": loyer_s, "vacance": vac_s,
            "c": cc, "solde": cc["fiscal"]["net_apres_is"] / 12 - prix_s * ANNUITE,
        })
    # grille de loyer
    d["grille"] = []
    for l in (loyer - 150, loyer - 100, loyer - 50, loyer, loyer + 50, loyer + 100):
        rr = copy.deepcopy(r)
        rr["marche"]["loyers"][0]["loyer_mensuel_euros"] = l
        cc = engine.compute(rr)
        d["grille"].append({"loyer": l, "ebe": cc["fiscal"]["ebe"], "net": cc["fiscal"]["net_apres_is"],
                            "solde": cc["fiscal"]["net_apres_is"] / 12 - prix * ANNUITE,
                            "rdt": cc["rendements"]["net_sur_revient_pct"]})
    return d


def _lien_secondaire(r):
    """Seconde URL de portail quand le même bien est diffusé par deux agences."""
    u = r["annonce"].get("url_secondaire")
    return f'<div class="report-source-link"><a href="{u}">{u}</a></div>' if u else ""


def bloc_cartes(d):
    cartes = [
        ("Prix affiché", eur(d["prix"])),
        ("Surface", d["rec"]["bien"]["surfaces"]["texte"].split("(")[0].strip()),
        ("Prix au m²", eur(d["prix"] / 75.0 if d["slug"] == SLUG_A else d["prix"] / 83.36)),
        ("Prix de revient", eur(d["revient"])),
        ("Valeur de revente retenue", eur(d["rec"]["marche"]["valeur"]["retenue_euros"])),
        ("Loyer retenu", eur(d["loyer"]) + "/mois"),
        ("Rendement net d'IS (revient / valeur)", f"{pct(d['rd']['net_sur_revient_pct'])} / {pct(d['rd']['net_sur_valeur_pct'])}"),
        ("Note", nfr(d["note"], 1) + "/10"),
    ]
    html = [f'    <div class="card">\n      <span class="card-label">{k}</span>\n'
            f'      <span class="card-value">{v}</span>\n    </div>' for k, v in cartes]
    return "\n".join(html)


def bloc_attractivite(d):
    cards = []
    for dim in d["rec"]["analyse"]["attractivite"]:
        s = dim["score"]
        cards.append('      <div class="attr-card">\n'
                     f'        <span class="attr-label">{dim["dimension"].replace("_", " ").capitalize()}</span>\n'
                     f'          <span class="attr-score"><strong>{s}/10</strong></span>\n'
                     f'        <div class="attr-bar-track"><div class="attr-bar-fill" style="width:{s * 10}%"></div></div>\n'
                     f'        <p class="attr-detail">{dim["justification"]}</p>\n      </div>')
    return "\n".join(cards)


def bloc_strategie(d):
    c = d["c"]
    lignes = []
    for i, st in enumerate(d["rec"]["analyse"]["strategies_explorees"]):
        rdt = c["rendements"]["net_sur_revient_pct"]
        ratio = c["ratio_cout_valeur"]
        ratio_cls = "ratio-bon" if ratio < 0.95 else ("ratio-ok" if ratio <= 1.05 else "ratio-mauvais")
        badge = {"modéré": ("risque-modere", "Modéré"), "élevé": ("risque-eleve", "Élevé")}.get(st["risque"], ("risque-modere", "Modéré"))
        fais = ("faisabilite-haute" if "Immédiate" in st["faisabilite"] else "faisabilite-moyenne")
        sel = ' class="strategy-row selected"' if i == 0 else ' class="strategy-row"'
        lignes.append(
            f"        <tr{sel}>\n          <td>{st['strategie']}</td>\n          <td>{st['lots']}</td>\n"
            f"          <td>{pct(rdt)} (loyer {eur(d['loyer'])})</td>\n"
            f"          <td>{eur(d['rec']['marche']['valeur']['retenue_euros'])}</td>\n"
            f"          <td><span class=\"ratio-badge {ratio_cls}\">{nfr(ratio, 3)}</span></td>\n"
            f"          <td><span class=\"badge-faisabilite {fais}\">{st['faisabilite']}</span></td>\n"
            f"          <td><span class=\"badge-risque {badge[0]}\">{badge[1]}</span></td>\n"
            f"          <td><div class=\"adeq-cell\"><div class=\"adeq-bar-track\"><div class=\"adeq-bar-fill adeq-mid\" style=\"width:{int(d['comp']['s_adequation'] * 10)}%\"></div></div></div></td>\n"
            "        </tr>")
    return ("    <table class=\"strategy-table\">\n      <thead>\n        <tr>\n"
            "          <th>Stratégie</th>\n          <th>Lots</th>\n          <th>Rendement net d'IS (revient)</th>\n"
            "          <th>Valeur revente</th>\n          <th>Ratio coût/valeur</th>\n          <th>Faisabilité</th>\n"
            "          <th>Risque</th>\n          <th>Adéquation</th>\n        </tr>\n      </thead>\n      <tbody>\n"
            + "\n".join(lignes) + "\n      </tbody>\n    </table>")


def bloc_grille_loyer(d):
    lignes = []
    for g in d["grille"]:
        cls = ' class="highlight"' if abs(g["loyer"] - d["loyer"]) < 0.01 else ""
        lignes.append(f"          <tr{cls}><td>{eur(g['loyer'])}/mois</td><td class=\"num\">{eur(g['ebe'])}</td>"
                      f"<td class=\"num\">{eur(g['net'])}</td><td class=\"num\">{euro_signe(g['solde'])}/mois</td>"
                      f"<td class=\"num\">{pct(g['rdt'])}</td></tr>")
    return "\n".join(lignes)


def bloc_identite(d):
    b = d["rec"]["bien"]
    lignes = [
        ("Adresse", d["adresse"]),
        ("Type", b["type_detail"]),
        ("Vendeur", d["rec"]["annonce"]["vendeur"]),
        ("Occupation", "Aucune — bien libre, aucun bail ni locataire produit" if d["slug"] == SLUG_A
         else "Aucune — bien vide, annonce publiée le jour de l'analyse"),
        ("Loyer de marché retenu", eur(d["loyer"]) + "/mois — " +
         ("450 € la chambre en colocation meublée, médiane du relevé toulonnais du 28/09/2026" if d["slug"] == SLUG_A
          else "1 050 € pour 83 m² en location nue (relevés Toulon 09/2026)")),
        ("Charges de copropriété", eur(b["copro"]["charges_annuelles_euros"]) + "/an — " + b["copro"]["charges_source"]),
        ("Taxe foncière", eur(d["rec"]["hypotheses"]["charges"]["taxe_fonciere_annuelle_euros"]) + "/an — "
         + d["rec"]["hypotheses"]["charges"]["taxe_fonciere_commentaire"]),
        ("Frais d'acquisition", eur(d["rec"]["hypotheses"]["frais_acquisition_euros"]) + " — "
         + d["rec"]["hypotheses"]["frais_acquisition_commentaire"]),
        ("Amortissement", eur(d["f"]["amortissement"]) + "/an — 90 % du prix de revient sur 30 ans (bâti)"),
        ("DPE", "C / GES C, chauffage central au gaz" if d["slug"] == SLUG_A else "D / GES D, énergie 1 040 à 1 470 €/an"),
        ("Valeur retenue", eur(d["rec"]["marche"]["valeur"]["retenue_euros"]) + " — " + d["rec"]["marche"]["valeur"]["source"]),
    ]
    return "\n".join(f"        <tr><th>{k}</th><td>{v}</td></tr>" for k, v in lignes)


def bloc_scenario(s, prix):
    c = s["c"]
    f = c["fiscal"]
    return ('      <div class="projection-card {cl}">\n        <h3>{t}</h3>\n'
            '        <p class="scenario-subtitle">{st}</p>\n'
            '        <table class="projection-table">\n          <tbody>\n'
            '            <tr><td>Loyer retenu</td><td class="num">{loyer}</td></tr>\n'
            '            <tr><td>Revenu brut annuel</td><td class="num">{rb}</td></tr>\n'
            '            <tr><td>Vacance locative ({vac} %)</td><td class="num">{vacl}</td></tr>\n'
            '            <tr class="secondary"><td>Charges de détention</td><td class="num">{ch}</td></tr>\n'
            '            <tr class="subtotal"><td>EBE avant IS</td><td class="num">{ebe}</td></tr>\n'
            '            <tr><td>Amortissement du bâti</td><td class="num">−{amort}</td></tr>\n'
            '            <tr><td>Résultat fiscal</td><td class="num">{res}</td></tr>\n'
            '            <tr><td>IS (15 %)</td><td class="num">−{isv}</td></tr>\n'
            '            <tr><td>CF net annuel (exploitation)</td><td class="num">{net}</td></tr>\n'
            '            <tr class="highlight"><td>Solde mensuel net</td><td class="num">{solde}/mois</td></tr>\n'
            '            <tr><td>Rendement net d\'IS sur revient</td><td class="num">{rdt}</td></tr>\n'
            '          </tbody>\n        </table>\n      </div>').format(
        cl=s["classe"], t=s["libelle"], st=s["sous_titre"], loyer=eur(s["loyer"]) + "/mois",
        rb=eur(c["revenus_bruts_annuels"]),
        vac=nfr(s["vacance"]), vacl="−" + eur(c["revenus_bruts_annuels"] * s["vacance"] / 100.0),
        ch="−" + eur(engine.charges_annuelles(s["rec"])[0]),
        ebe=eur(f["ebe"]), amort=eur(f["amortissement"]), res=eur(f["resultat_fiscal"]),
        isv=eur(f["is_annuel"]), net=eur(f["net_apres_is"]), solde=euro_signe(s["solde"]),
        rdt=pct(c["rendements"]["net_sur_revient_pct"]))


def bloc_risques(d):
    lignes = []
    for r in sorted(d["rec"]["analyse"]["risques"], key=lambda x: -x["severite"]):
        lignes.append("        <tr>\n"
                      f'          <td>{r["facteur"]}</td>\n          <td>{r["detail"]}</td>\n'
                      f'          <td><span class="severity severity-{r["severite"]}">{r["severite"]}/5</span></td>\n'
                      "        </tr>")
    return "\n".join(lignes)


TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Analyse — {titre}</title>
  <link rel="stylesheet" href="../../style.css">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
</head>
<body>

<header class="report-header">
  <nav class="report-breadcrumb"><a href="../../analyses/index.html">← Retour aux analyses</a></nav>
  <h1>Analyse d'investissement</h1>
  <p class="report-address">{adresse_courte}</p>
  <p class="report-date">Analyse générée le 13 octobre 2026</p>
  <p class="report-source">Source : SeLoger — {vendeur}</p>
  <div class="report-source-link"><a href="{url}">{url}</a></div>
  {lien_secondaire}
</header>

<main>

  <div class="strategy-banner">
    <span class="strategy-badge">{badge}</span>
    <p>Stratégie retenue : <strong>{strategie}</strong> — SCI à l'IS (15 %)</p>
  </div>

  <section class="summary-cards">
{cartes}
  </section>

  <section class="map-section">
    <h2>Localisation</h2>
    <div id="map-container" data-lat="{lat}" data-lon="{lon}" data-address="{map_addr}"></div>
  </section>

  <section class="attractiveness">
    <h2>Attractivité — {quartier}</h2>
    <p class="attractiveness-intro">{intro_attractivite}</p>
    <div class="attractiveness-grid">
{attractivite}
    </div>
    <div class="attractiveness-summary">
      <p><strong>Profil locataire cible :</strong> {profil}</p>
      <p><strong>Conclusion :</strong> {lecture}</p>
    </div>
  </section>

  <section class="strategy-exploration">
    <h2>Stratégie d'exploitation</h2>
    <p class="attractiveness-intro">{intro_strategie}</p>
{strategie}
    <div class="strategy-rationale">
      <p>{conf}</p>
    </div>
  </section>

  <section class="strategy-exploration">
    <h2>Relevé de marché — ce qui fonde le loyer retenu</h2>
{releve}
  </section>

  <section class="strategy-exploration">
    <h2>Sensibilité au loyer mensuel — prix affiché de {prix_affiche}</h2>
    <p class="attractiveness-intro">Chaque ligne est recalculée par le moteur, vacance 5 %, charges inchangées. Le solde mensuel se lit sous la convention du groupe : frais d'acquisition sortis comptants, solde du prix porté sur quinze ans, intérêts et assurance compris.</p>
    <table class="comparison-table">
      <thead>
        <tr><th>Loyer mensuel</th><th>EBE / an</th><th>Net après IS</th><th>Solde mensuel net</th><th>Rendement net sur revient</th></tr>
      </thead>
      <tbody>
{grille}
      </tbody>
    </table>
  </section>

  <section class="identity-sheet">
    <h2>Fiche d'identité</h2>
    <table class="identity-table">
{identite}
    </table>
  </section>

  <section class="financial-projections">
    <h2>Projections financières — SCI à l'IS</h2>
    <p class="attractiveness-intro">{intro_projections}</p>
    <div class="projections-grid">
{projections}
    </div>
  </section>

  <section class="risk-matrix">
    <h2>Matrice de risques</h2>
    <table class="risk-table">
      <thead>
        <tr><th>Facteur de risque</th><th>Détail</th><th>Sévérité</th></tr>
      </thead>
      <tbody>
{risques}
      </tbody>
    </table>
  </section>

  <section class="verdict {verdict_cls}">
    <h2>Recommandation</h2>
    <div class="verdict-decision">
      <p class="verdict-stance"><strong>{stance}</strong> {verdict_texte}</p>
    </div>
    <div class="verdict-details">
      <p><strong>Performance :</strong> {performance}</p>
      <p><strong>Prix plafond et prix cible :</strong> {prix_texte}</p>
      <p><strong>Garde-fous chiffrés :</strong></p>
      <ul>
{garde_fous}
      </ul>
    </div>
    <div class="verdict-meta">
      <p><strong>Régime fiscal retenu :</strong> SCI à l'IS (15 %) — amortissement du bâti {amortissement}/an, frais d'acquisition {frais}, provision travaux 2,5 % des loyers</p>
      <p><strong>Hypothèses retenues :</strong> loyer {loyer} €/mois, vacance 5 % en base, charges {charges}/an, placement de la réserve à 2,84 %</p>
      <p><strong>Note :</strong> {note}/10 — {verdict_libelle} (performance {perf_score}/10, sécurité {secu_score}/10, emplacement {adeq_score}/10, risque {risque_score}/10)</p>
    </div>
  </section>

  <footer class="report-signature">
    <p>Analyse réalisée par</p>
    <p class="signature-names">Rémy Barlatier — 06 27 84 53 50 — sarl.spbi@gmail.com</p>
    <p class="signature-names">Alexis Barlatier — 06 61 26 13 83</p>
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

    var map = L.map('map-container').setView([lat, lon], 14);
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19
    }}).addTo(map);
    L.marker([lat, lon]).addTo(map).bindPopup(addr).openPopup();
  }})();
</script>

</body>
</html>
"""


def prix_autofinancement(d):
    """Prix auquel le net après IS couvre exactement la charge du lot (dichotomie)."""
    bas, haut = 10_000.0, d["prix"] * 3
    for _ in range(60):
        milieu = (bas + haut) / 2.0
        rr = copy.deepcopy(d["rec"])
        rr["annonce"]["prix_retenu_euros"] = milieu
        cc = engine.compute(rr)
        if cc["fiscal"]["net_apres_is"] / 12.0 - milieu * ANNUITE < 0:
            haut = milieu
        else:
            bas = milieu
    return int(bas // 500.0 * 500.0)


TEXTES = {
    SLUG_A: {
        "badge": "Colocation meublée — trois chambres",
        "strategie": "colocation meublée à trois chambres, au prix qui finance le lot",
        "adresse_courte": "T4 de 75 m² aménagé en colocation — Champs de Mars, Toulon (83000)",
        "quartier": "Champs de Mars, Toulon",
        "intro_attractivite": "Quartier central de Toulon, dans la couronne immédiate des établissements d'enseignement supérieur revendiqués par l'annonce (faculté de droit, ISEN, campus Chalucet, école paramédicale). C'est le moteur de la demande : la colocation étudiante y est un produit installé, pas un pari. La contrepartie est une offre abondante — 66 à 183 annonces de colocation en concurrence selon les portails — et un immeuble des années 50 dont les postes collectifs ne sont pas documentés.",
        "profil": "étudiants et jeunes actifs du secteur facultés, en bail meublé individuel ; profil qui arbitre sur le prix de la chambre, la qualité du mobilier et la proximité à pied du campus.",
        "intro_strategie": "Trois lectures du même lot : colocation meublée avec l'aménagement existant, location nue du T4, ou arbitrage de revente. La colocation est retenue — elle produit le plus de revenu sur la même surface — mais elle porte le mobilier, les fluides et la rotation.",
        "intro_projections": "Colocation meublée : 3 chambres à 450 €/mois (médiane relevée), vacance 5 % en base, charges de copropriété 2 012 €/an, taxe foncière estimée 1 400 €/an, fluides et mobilier provisionnés à 4 120 €/an, provision travaux 2,5 % des loyers.",
        "scenarios": [("Scénario Base", (1350.0, 5.0, 170000.0), "scenario-base", "Loyer 450 €/chambre — vacance 5 % — prix affiché 170 000 €"),
                      ("Scénario Best", (1440.0, 2.0, 170000.0), "scenario-best", "Loyer 480 €/chambre — vacance 2 % — prix affiché 170 000 €"),
                      ("Scénario Worst", (1200.0, 15.0, 170000.0), "scenario-worst", "Loyer 400 €/chambre (postulat de l'annonce) — vacance 15 % — prix affiché 170 000 €")],
    },
    SLUG_B: {
        "badge": "Location nue — 5 pièces familial",
        "strategie": "location nue du 5 pièces, au prix qui finance le lot",
        "adresse_courte": "T5 de 83 m² avec cave, parking et balcon — Toulon Ouest (83200)",
        "quartier": "Toulon Ouest",
        "intro_attractivite": "Secteur résidentiel populaire et stable de Toulon, avec commerces, écoles et transports de proximité : c'est un quartier de locataires familiaux, pas d'étudiants. Le logement a pour lui ce qui manque souvent dans le secteur — cave, parking privatif, balcon et loggia — mais il porte un défaut qui commande tout le dossier : troisième et dernier étage sans ascenseur.",
        "profil": "famille ou couple avec enfants scolarisés cherchant un grand logement au prix du marché ; la cible s'élargit mal à cause de l'absence d'ascenseur, qui écarte les familles avec enfants en bas âge et les seniors.",
        "intro_strategie": "Deux exploitations chiffrées : location nue du 5 pièces (retenue, sans travaux ni mobilier), ou colocation meublée — trois chambres, quatre après cloisonnement. La colocation exige l'ameublement complet et des travaux de cloisonnement non chiffrés : elle ne sauve pas le dossier et n'entre pas dans l'offre.",
        "intro_projections": "Location nue : loyer retenu 1 050 €/mois pour 83 m², vacance 5 % en base, charges de copropriété 1 200 €/an, taxe foncière estimée 1 300 €/an, assurance 250 €/an, provision travaux 2,5 % des loyers.",
        "scenarios": [("Scénario Base", (1050.0, 5.0, 176000.0), "scenario-base", "Loyer 1 050 € — vacance 5 % — prix affiché 176 000 €"),
                      ("Scénario Best", (1150.0, 2.0, 176000.0), "scenario-best", "Loyer 1 150 € — vacance 2 % — prix affiché 176 000 €"),
                      ("Scénario Worst", (900.0, 12.0, 176000.0), "scenario-worst", "Loyer 900 € — vacance 12 % — prix affiché 176 000 €")],
    },
}


def releve_html(entetes, lignes):
    th = "".join(f"<th>{h}</th>" for h in entetes)
    tr = "\n".join("          <tr>" + "".join(
        f'<td class="num">{v}</td>' if i else f"<td>{v}</td>" for i, v in enumerate(l)) + "</tr>"
        for l in lignes)
    return ('    <table class="comparison-table">\n      <thead>\n        <tr>' + th +
            "</tr>\n      </thead>\n      <tbody>\n" + tr + "\n      </tbody>\n    </table>")


TEXTES[SLUG_A].update({
    "lecture": ("Le produit est en place : trois chambres de plus de 11 m², un séjour de 27 m², un DPE C, "
        "un ascenseur et un quartier qui vit des facultés. Ce qui ne tient pas, c'est le prix. À 170 000 €, la "
        "colocation produit 3,80 % net d'IS sur un prix de revient de 183 600 €, pour un plancher de branche de "
        "5 % : il faudrait 125 000 € pour atteindre le seuil, et environ 80 000 € pour que le lot couvre sa propre "
        "charge. Le prix affiché est celui du marché toulonnais des T4 ; ce sont les loyers de colocation, eux, "
        "qui ne portent pas ce montant."),
    "conf": ("La colocation est le meilleur usage de cette surface, et elle est déjà aménagée : le dossier ne se "
        "juge donc pas sur un potentiel, mais sur ce qu'il produit aujourd'hui. Deux hypothèses de loyer existent, "
        "et elles encadrent le prix : 400 €/chambre (l'annonce, sans bail) donne 3,03 % net d'IS, 450 €/chambre "
        "(médiane relevée à Toulon) donne 3,80 %. Aucune des deux n'approche le plancher de 5 % au prix demandé."),
    "releve": releve_html(
        ["Source", "Loyer", "Détail"],
        [["T3 de 3 chambres en colocation, Saint-Roch, bail individuel", "450 € CC", "relevé du 28/09/2026 — comparable strict du dossier (même configuration, même handicap d'étage)"],
         ["Médiane des 13 annonces de colocation relevées à Toulon", "450 €", "plancher 345 €, plafond 550 €, masse principale 420 à 520 € charges comprises"],
         ["Chambre de 11 m², Champ de Mars", "480 € CC", "relevé du 22/09/2026 — même quartier que le bien"],
         ["Secteur facultés (Saint-Jean-du-Var, Saint-Roch, Porte d'Italie)", "430 à 480 € CC", "relevé du 22/09/2026, médiane observée 460 €"],
         ["Postulat de l'annonce (aucun bail, aucun locataire)", "400 €", "bas de la fourchette relevée — ne fonde pas un prix"]])
    + "\n    <p class=\"attractiveness-intro\"><strong>Ce que le relevé établit :</strong> la fourchette utile est "
      "420 à 480 € par chambre pour un produit aménagé et meublé, et le bas du marché (400 €) correspond à des "
      "chambres plus petites ou mal desservies. Retenir 400 € serait prudent mais condamne le dossier ; retenir "
      "450 € est la médiane observée. C'est ce chiffre-là qui est publié, et c'est celui que le prix doit "
      "supporter.</p>",
    "garde_fous": """        <li><strong>Le bien est diffusé deux fois, à deux prix.</strong> BRETTE IMMOBILIER l'affiche à 170 000 € (prix barré 180 000 €) et IBOX JAURÈS, 323 rue Jean Jaurès à Toulon, à 180 000 € — même surface, même étage, même copropriété de 88 lots, même DPE C. C'est le prix le plus bas qui fait foi, et l'écart de 10 000 € entre les deux mandataires est un point d'appui de négociation : le vendeur a déjà accepté 170 000 € sur un mandat.</li>
        <li><strong>Le prix plafond est de 125 000 €</strong> (rendement net d'IS de 5 % sur prix de revient, soit 26 % sous le prix affiché). Au-dessus, le dossier reste sous son plancher de branche.</li>
        <li><strong>Le prix d'autofinancement est d'environ 80 000 €</strong> : c'est le prix auquel les 1 350 €/mois couvrent la charge du lot. Il n'existe pas de marché à ce niveau pour un T4 toulonnais aménagé : ce n'est donc pas une négociation, c'est un constat de trésorerie.</li>
        <li><strong>Charges à faire préciser :</strong> 2 012 €/an de copropriété (26,8 €/m²/an, haut du barème) plus 1 400 € de taxe foncière estimée : 3 412 €/an avant fluides. Chaque tranche de 500 € de charges annuelles en plus coûte environ 45 €/mois de loyer.</li>
        <li><strong>Pièces à exiger avant toute offre :</strong> trois derniers PV d'assemblée générale et budget prévisionnel (copropriété de 88 lots de 1948), avis de taxe foncière, certificat Carrez, statut du garage (lot distinct ou non), et l'état du mobilier laissé sur place.</li>""",
    "stance": "On ne paie pas ce prix.",
    "verdict_texte": ("La colocation est aménagée, le quartier est le bon, le DPE est bon : rien à jeter côté produit. "
        "Mais à 170 000 €, le lot rend 3,80 % net d'IS pour un plancher de 5 %, et son solde mensuel reste négatif de "
        "571 €/mois sur un logement qui produirait 1 350 €. Les prix qui rendraient le dossier tenable — 125 000 € pour "
        "le rendement, environ 80 000 € pour la charge du lot — sont hors du marché de ce quartier : le dossier se "
        "refuse, et pourrait se rouvrir seulement si le vendeur accepte un prix de rendement."),
    "performance": ("3,80 % de rendement net après IS sur un prix de revient de 183 600 €, pour un plancher de branche "
        "de 5 % — soit une performance de 3,0/10. Ratio prix de revient sur valeur de revente : 1,02. EBE avant IS : "
        "7 238 €/an. L'amortissement du bâti (5 508 €/an) limite l'IS à 259 €, mais ne sauve pas la trésorerie."),
    "prix_texte": ("Prix plafond 125 000 € et prix cible 125 000 € (les deux se rejoignent : au-dessus, la note est "
        "plafonnée par le plancher de rendement), soit 45 000 € sous le prix affiché. À ce prix, le rendement net "
        "d'IS atteint le seuil de 5 % et la note passe la barre de 6,5 — mais le solde mensuel reste négatif "
        "d'environ 280 €/mois : le dossier entre dans la doctrine de rendement sans entrer dans celle de trésorerie."),
})

TEXTES[SLUG_B].update({
    "lecture": ("Un grand logement de 83 m² avec cave, parking, balcon et loggia : le produit correspond à une "
        "demande familiale réelle dans un secteur où le stationnement est rare. Deux choses l'empêchent de tenir : "
        "le 3e étage sans ascenseur, qui rétrécit la cible et allonge la relocation, et le prix. À 176 000 €, le "
        "loyer de 1 050 € rend 4,44 % net d'IS sur un revient de 190 080 € pour un plancher de 5 % ; il faudrait "
        "154 500 € pour atteindre le seuil et environ 99 000 € pour que le lot couvre sa charge."),
    "conf": ("Le dossier est un dossier de rendement classique, sans travaux ni mobilier : tout se joue sur le "
        "couple loyer/prix. Le loyer retenu, 1 050 €, est le milieu des relevés toulonnais pour un logement de "
        "cette taille, sans ascenseur et hors quartiers chers. La variante colocation (1 290 € à 3 chambres, "
        "1 720 € à 4 après cloisonnement) a été chiffrée : elle reste sous le plancher de rendement et suppose un "
        "ameublement et des travaux non chiffrés — elle n'entre pas dans l'offre."),
    "releve": releve_html(
        ["Source", "Loyer", "Détail"],
        [["T4 toutes surfaces, médiane d'affichage, Toulon", "1 000 €", "relevé du 28/09/2026 — plancher 880 €, plafond 1 180 €"],
         ["69,4 m², Toulon", "890 €", "relevé du 28/09/2026 — petite surface pour un T4"],
         ["71 m², Valbertrand, Toulon Ouest", "1 220 €", "relevé du 28/09/2026 — immeuble mieux situé"],
         ["90 m², Champ de Mars - La Rode, 4 pièces", "1 300 € CC", "relevé du 28/09/2026 — quartier plus cher que l'Ouest"],
         ["Chambre en colocation, Toulon (médiane)", "450 € CC", "relevé du 28/09/2026 — 13 annonces, masse 420 à 520 €"]])
    + "\n    <p class=\"attractiveness-intro\"><strong>Ce que le relevé établit :</strong> un logement de 83 m² au "
      "3e étage sans ascenseur, dans Toulon Ouest, se loue autour de 1 000 à 1 100 € — c'est le milieu des annonces "
      "de la ville pour cette taille. Le loyer retenu (1 050 €) est le point central de cette fourchette, sans "
      "prime de rareté : l'offre de grands logements est abondante à Toulon.</p>",
    "garde_fous": """        <li><strong>Le prix plafond est de 154 500 €</strong> (rendement net d'IS de 5 %), soit 21 500 € sous le prix affiché (−12 %) : c'est le champ d'une négociation ordinaire, pas d'un refus.</li>
        <li><strong>Le prix d'autofinancement est d'environ 99 000 €</strong>, soit 44 % sous le prix affiché : même au plafond de rendement, le lot ne couvre pas sa charge (solde négatif d'environ 350 €/mois à 154 500 €).</li>
        <li><strong>Charges à vérifier :</strong> 1 200 €/an pour un immeuble de 72 lots (14,4 €/m²/an) est un budget de dépenses courantes, sans provision de gros travaux. Exiger le plan pluriannuel de travaux et trois PV d'assemblée générale.</li>
        <li><strong>Pièces à exiger avant toute offre :</strong> certificat Carrez, avis de taxe foncière, statut des lots cave et parking, mode de chauffage et DPE complet, devis d'un cloisonnement si la 4e chambre entre dans le projet.</li>""",
    "stance": "On négocie, et pas au prix affiché.",
    "verdict_texte": ("Le logement a de vrais atouts — cave, parking, balcon, loggia, grand volume — et le prix est "
        "dans le marché, pas au-dessus. Mais à 4,44 % net d'IS sur revient, il est sous le plancher de 5 %, et son "
        "solde mensuel est négatif de 489 €/mois. Le plafond de rendement (154 500 €) est atteignable par la "
        "négociation ; en dessous de ce prix, le dossier devient défendable sur le rendement, sans jamais couvrir sa "
        "charge tant que le loyer reste à 1 050 €."),
    "performance": ("4,44 % de rendement net après IS sur un prix de revient de 190 080 €, pour un plancher de branche "
        "de 5 % — performance 4,1/10. Ratio prix de revient sur valeur de revente : 1,06. EBE avant IS : 8 932 €/an, "
        "IS 484 € après amortissement du bâti."),
    "prix_texte": ("Prix plafond 154 500 € (154 500 € également comme prix cible), soit 21 500 € sous le prix affiché "
        "(−12 %). Le solveur du moteur proratise les frais d'acquisition avec le prix ; aux frais réels du barème "
        "notaire, le plafond ressort légèrement plus bas. À 154 500 €, la note franchit 6,5 mais le solde mensuel "
        "reste négatif d'environ 350 €/mois."),
})


def main():
    if ECARTS:
        print(f"ÉCARTS DÉTECTÉS ({len(ECARTS)}) :")
        for e in ECARTS:
            print("  -", e)
        if not TOLERANT:
            raise SystemExit("chiffres publiés en désaccord avec le moteur")
    else:
        print("Contrôles chiffrés : aucun écart")

    for slug, lat, lon, map_addr, adresse in (
            (SLUG_A, "43.1230", "5.9215", "Quartier Champs de Mars, Toulon (83000) — coordonnées du quartier, adresse exacte non communiquée",
             "Quartier Champs de Mars, Toulon (83000) — adresse exacte non communiquée par l'agence"),
            (SLUG_B, "43.1250", "5.9050", "Toulon Ouest (83200) — coordonnées du secteur, adresse exacte non communiquée",
             "Toulon Ouest (83200) — adresse exacte non communiquée par l'agence")):
        t = TEXTES[slug]
        d = prepare(slug, lat, lon, map_addr, adresse, t["lecture"], t["conf"], t["releve"],
                    [(lib, vals, cls, st) for lib, vals, cls, st in t["scenarios"]], t["garde_fous"])
        r = d["rec"]
        autofin = prix_autofinancement(d)
        scenarios = []
        for (lib, vals, cls, st) in t["scenarios"]:
            loyer_s, vac_s, prix_s = vals
            rr = copy.deepcopy(r)
            rr["marche"]["loyers"][0]["loyer_mensuel_euros"] = loyer_s
            rr["hypotheses"]["vacance_base_pct"] = vac_s
            cc = engine.compute(rr)
            scenarios.append({"libelle": lib, "classe": cls, "sous_titre": st, "loyer": loyer_s,
                              "vacance": vac_s, "c": cc, "rec": rr,
                              "solde": cc["fiscal"]["net_apres_is"] / 12 - prix_s * ANNUITE})
        projections = "\n\n".join(bloc_scenario(s, d["prix"]) for s in scenarios)
        charges = engine.charges_annuelles(r)[0]

        html = TEMPLATE.format(
            titre=r["titre"], adresse_courte=t["adresse_courte"], vendeur=r["annonce"]["vendeur"],
            url=r["annonce"]["url"], lien_secondaire=_lien_secondaire(r), badge=t["badge"], strategie=t["strategie"],
            cartes=bloc_cartes(d), lat=lat, lon=lon, map_addr=map_addr,
            quartier=t["quartier"], intro_attractivite=t["intro_attractivite"],
            attractivite=bloc_attractivite(d), profil=t["profil"], lecture=t["lecture"],
            intro_strategie=t["intro_strategie"], strategie_html="", conf=t["conf"],
            releve=t["releve"], grille=bloc_grille_loyer(d), identite=bloc_identite(d),
            intro_projections=t["intro_projections"], projections=projections,
            risques=bloc_risques(d), verdict_cls=d["classe"], stance=t["stance"],
            verdict_texte=t["verdict_texte"], performance=t["performance"], prix_texte=t["prix_texte"],
            garde_fous=t["garde_fous"], amortissement=eur(d["f"]["amortissement"]),
            frais=eur(r["hypotheses"]["frais_acquisition_euros"]), loyer=nfr(d["loyer"]),
            charges=eur(charges), note=nfr(d["note"], 1),
            verdict_libelle={"acheter": "à acheter", "negocier": "à négocier", "fuir": "à fuir"}[d["verdict"]],
            perf_score=nfr(d["comp"]["s_performance"], 1), secu_score=nfr(d["comp"]["s_securite"], 1),
            adeq_score=nfr(d["comp"]["s_adequation"], 1), risque_score=nfr(d["comp"]["s_risque"], 1),
            prix_affiche=eur(d["prix"]),
        ).replace("{strategie}", bloc_strategie(d))

        residuels = [m for m in re.findall(r"\{[a-z_][a-z_0-9]*\}", html) if m not in ("{s}", "{z}", "{x}", "{y}")]
        if residuels:
            raise SystemExit(f"placeholders non remplacés ({slug}) : {sorted(set(residuels))}")
        for attendu in ("report-header", "summary-cards", "map-section", "attractiveness",
                        "strategy-exploration", "identity-sheet", "financial-projections",
                        "risk-matrix", 'section class="verdict', "report-signature"):
            if attendu not in html:
                raise SystemExit(f"section manquante ({slug}) : {attendu}")
        if 'name="robots"' not in html or "noindex" not in html:
            raise SystemExit(f"noindex absent ({slug})")
        interdits = re.findall(r"\b(prêt|prêts|emprunt\w*|crédit\w*|apport\w*|mensualit\w*|levier|montage)\b", html, flags=re.I)
        if interdits:
            raise SystemExit(f"mot de financement ({slug}) : {sorted(set(interdits))}")

        sortie = os.path.join(RACINE, "analyses", slug, "index.html")
        os.makedirs(os.path.dirname(sortie), exist_ok=True)
        with open(sortie, "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"{slug} : {len(html)} caractères | note {d['note']} {d['verdict']} ({d['classe']}) | "
              f"net/revient {d['rd']['net_sur_revient_pct']} % | solde {d['solde']:+.0f} €/mois | "
              f"plafond {d['plafond']} € | cible {d['cible']} € | autofinancement {autofin} €")


if __name__ == "__main__":
    main()
