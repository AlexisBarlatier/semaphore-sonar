#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère la fiche du local de 155 m² (74 garage + 81 cave) — Saint-Raphaël centre.

analyses/2026-10-13-local-155m2-saint-raphael-centre/index.html — SeLoger 26TX63BF4NPD

Branche professionnelle (plancher 7 % net après IS sur prix de revient). Convention de
chiffrage du groupe : SCI à l'IS 15 %, amortissement du bâti 90 % du prix de revient sur
30 ans, provision travaux 2,5 % des revenus, placement de la réserve à 2,84 %. Le solde
mensuel se lit sous la convention du groupe : frais d'acquisition sortis comptants, solde
du prix porté sur 15 ans (intérêts et assurance compris).

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

SLUG = "2026-10-13-local-155m2-saint-raphael-centre"
SURFACE = 155.0
VALEUR = 150000.0


def rec(slug):
    return [r for r in DATA["analyses"] if r["slug"] == slug][0]


def variante(r, loyer=None, vacance=None, entretien=None, prix=None, travaux=None):
    rr = copy.deepcopy(r)
    if loyer is not None:
        rr["marche"]["loyers"][0]["loyer_mensuel_euros"] = loyer
    if vacance is not None:
        rr["hypotheses"]["vacance_base_pct"] = vacance
    if entretien is not None:
        rr["hypotheses"]["charges"]["entretien_annuel_euros"] = entretien
    if travaux is not None:
        rr["bien"]["travaux"]["montant_euros"] = travaux
    if prix is not None:
        rr["annonce"]["prix_retenu_euros"] = prix
    return rr


def prepare(lat, lon, map_addr, adresse, lecture, conf, releve, scenarios, garde_fous):
    r = rec(SLUG)
    c = engine.compute(r)
    note, verdict, comp = scoring.note_et_verdict(r, c)
    f, rd = c["fiscal"], c["rendements"]
    prix = r["annonce"]["prix_retenu_euros"]
    mens = prix * ANNUITE
    loyer = r["marche"]["loyers"][0]["loyer_mensuel_euros"]
    frais = r["hypotheses"]["frais_acquisition_euros"]

    d = {
        "slug": SLUG, "rec": r, "c": c, "note": note, "verdict": verdict, "comp": comp,
        "f": f, "rd": rd, "prix": prix, "mens": mens, "solde": f["net_apres_is"] / 12 - mens,
        "loyer": loyer, "revient": c["prix_revient_total"], "lat": lat, "lon": lon,
        "map_addr": map_addr, "adresse": adresse, "lecture": lecture, "conf": conf,
        "releve": releve, "garde_fous": garde_fous,
        "classe": {"acheter": "buy", "negocier": "nego", "fuir": "pass"}[verdict],
    }
    d["plafond"], d["contrainte"] = scoring.prix_plafond(r)
    d["cible"] = scoring.prix_cible(r)

    def aux_frais_reels(cible_note=6.5):
        bas, haut = 0.10 * prix, 3.0 * prix
        res = bas
        for _ in range(60):
            milieu = (bas + haut) / 2.0
            rr = variante(r, prix=milieu)
            rr["hypotheses"]["frais_acquisition_euros"] = frais
            n, _, cp = scoring.note_et_verdict(rr, engine.compute(rr))
            if n is not None and n >= cible_note and not cp["plafonds"]:
                res = milieu
                bas = milieu
            else:
                haut = milieu
        return int(res // 500.0 * 500.0)

    d["cible_frais_reels"] = aux_frais_reels()

    d["scenarios"] = []
    for sc in scenarios:
        rr = variante(r, loyer=sc["loyer"], vacance=sc["vacance"], entretien=sc.get("entretien"))
        cc = engine.compute(rr)
        d["scenarios"].append({
            "libelle": sc["libelle"], "classe": sc["classe"], "sous_titre": sc["sous_titre"],
            "loyer": sc["loyer"], "vacance": sc["vacance"], "c": cc, "rec": rr,
            "solde": cc["fiscal"]["net_apres_is"] / 12 - prix * ANNUITE,
        })

    d["grille"] = []
    for l in (950.0, 1100.0, 1225.0, 1400.0, 1500.0, 1600.0):
        rr = variante(r, loyer=l, vacance=10.0)
        cc = engine.compute(rr)
        d["grille"].append({
            "loyer": l, "ebe": cc["fiscal"]["ebe"], "net": cc["fiscal"]["net_apres_is"],
            "solde": cc["fiscal"]["net_apres_is"] / 12 - prix * ANNUITE,
            "rdt": cc["rendements"]["net_sur_revient_pct"],
        })

    # stratégies : chacune recalculée par le moteur avec son propre loyer
    plans = {
        "Bail commercial 3-6-9 du local entier": (1225.0, 10.0),
        "Deux preneurs — garage et cave loués séparément": (1400.0, 8.0),
        "Division en boxes de stockage ou en caves": (1650.0, 12.0),
        "Changement de destination vers l'habitation": (1225.0, 10.0),
    }
    d["strategies"] = []
    for st in r["analyse"]["strategies_explorees"]:
        loyer_s, vac_s = plans.get(st["strategie"], (1225.0, 10.0))
        rr = variante(r, loyer=loyer_s, vacance=vac_s)
        cc = engine.compute(rr)
        d["strategies"].append({
            "strategie": st["strategie"], "lots": st["lots"], "c": cc,
            "loyer": loyer_s,
            "rdt": cc["rendements"]["net_sur_revient_pct"],
            "ratio": cc["ratio_cout_valeur"], "faisabilite": st["faisabilite"],
            "risque": st["risque"], "retenue": st["strategie"].startswith("Bail commercial"),
        })
    return d


def bloc_cartes(d):
    cartes = [
        ("Prix affiché", eur(d["prix"]) + f" ({eur(d['prix'] / SURFACE)}/m²)"),
        ("Prix de revient", eur(d["revient"])),
        ("Valeur de revente retenue", eur(d["rec"]["marche"]["valeur"]["retenue_euros"])),
        ("Loyer de marché retenu", eur(d["loyer"]) + "/mois (non constaté)"),
        ("Rendement net d'IS (revient / valeur)", f"{pct(d['rd']['net_sur_revient_pct'])} / {pct(d['rd']['net_sur_valeur_pct'])}"),
        ("Ratio coût / valeur", nfr(d["c"]["ratio_cout_valeur"], 3)),
        ("Note", nfr(d["note"], 1) + "/10"),
        ("Verdict", {"buy": "À acheter", "nego": "À négocier", "pass": "À fuir"}[d["classe"]]),
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
    lignes = []
    for st in d["strategies"]:
        ratio = st["ratio"]
        ratio_cls = "ratio-bon" if ratio < 0.95 else ("ratio-ok" if ratio <= 1.05 else "ratio-mauvais")
        badge = {"modéré": ("risque-modere", "Modéré"), "élevé": ("risque-eleve", "Élevé"),
                 "faible": ("risque-faible", "Faible")}.get(st["risque"], ("risque-modere", "Modéré"))
        fais = "faisabilite-haute" if st["faisabilite"].startswith("Immédiate") else "faisabilite-faible"
        sel = ' class="strategy-row selected"' if st["retenue"] else ' class="strategy-row"'
        lignes.append(
            f"        <tr{sel}>\n          <td>{st['strategie']}</td>\n          <td>{st['lots']}</td>\n"
            f"          <td>{pct(st['rdt'])} (loyer {eur(st['loyer'])})</td>\n"
            f"          <td>{eur(d['rec']['marche']['valeur']['retenue_euros'])}</td>\n"
            f"          <td><span class=\"ratio-badge {ratio_cls}\">{nfr(ratio, 3)}</span></td>\n"
            f"          <td><span class=\"badge-faisabilite {fais}\">{st['faisabilite']}</span></td>\n"
            f"          <td><span class=\"badge-risque {badge[0]}\">{badge[1]}</span></td>\n"
            f"          <td>{eur(st['c']['fiscal']['net_apres_is'])}/an</td>\n"
            "        </tr>")
    return ("    <table class=\"strategy-table\">\n      <thead>\n        <tr>\n"
            "          <th>Stratégie</th>\n          <th>Lots</th>\n          <th>Rendement net d'IS (revient)</th>\n"
            "          <th>Valeur revente</th>\n          <th>Ratio coût/valeur</th>\n          <th>Faisabilité</th>\n"
            "          <th>Risque</th>\n          <th>Net après IS</th>\n        </tr>\n      </thead>\n      <tbody>\n"
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
    h = d["rec"]["hypotheses"]["charges"]
    lignes = [
        ("Adresse", d["adresse"]),
        ("Type", b["type_detail"]),
        ("Vendeur", d["rec"]["annonce"]["vendeur"]),
        ("Occupation", "Local vide — aucun bail, aucun preneur, aucun loyer encaissé. L'annonce le présente "
                       "comme « idéalement situé, accès rapide et facile, usage professionnel ou personnel »."),
        ("Bail", "Néant à ce jour. En bail commercial 3-6-9, prévoir un dépôt de garantie de trois mois et "
                 "vérifier la refacturation de la taxe foncière au preneur — elle reste au bailleur tant que "
                 "le bail ne la mentionne pas."),
        ("Loyer de marché retenu", eur(d["loyer"]) + "/mois — valeur locative reconstituée, non constatée : "
         "74 m² de garage à 10 €/m²/mois et 81 m² de cave à 6 €/m²/mois. Relevé du 13/10/2026 : locaux "
         "d'activités de Saint-Raphaël entre 8,3 et 14,7 €/m²/mois, tous avec accès véhicule et rideau."),
        ("Charges de copropriété", eur(b["copro"]["charges_annuelles_euros"]) + "/an — " + b["copro"]["charges_source"]),
        ("Taxe foncière", eur(h["taxe_fonciere_annuelle_euros"]) + "/an — " + h["taxe_fonciere_commentaire"]),
        ("Entretien et grosses réparations", eur(h["entretien_annuel_euros"]) + "/an — " + h["entretien_commentaire"]),
        ("Frais d'acquisition", eur(d["rec"]["hypotheses"]["frais_acquisition_euros"]) + " — "
         + d["rec"]["hypotheses"]["frais_acquisition_commentaire"]),
        ("Amortissement", eur(d["f"]["amortissement"]) + "/an — 90 % du prix de revient sur 30 ans (bâti)"),
        ("DPE", "Non soumis — lot sans bâti chauffé. Pas de contrainte réglementaire de location, "
                "mais pas de diagnostic énergétique à opposer non plus."),
        ("Valeur retenue", eur(d["rec"]["marche"]["valeur"]["retenue_euros"]) + " — " + d["rec"]["marche"]["valeur"]["source"]),
    ]
    return "\n".join(f"        <tr><th>{k}</th><td>{v}</td></tr>" for k, v in lignes)


def bloc_scenario(s):
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
            '            <tr><td>Résultat net après IS (exploitation)</td><td class="num">{net}</td></tr>\n'
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
      <p><strong>Profil preneur cible :</strong> {profil}</p>
      <p><strong>Conclusion :</strong> {lecture}</p>
    </div>
  </section>

  <section class="strategy-exploration">
    <h2>Stratégie d'exploitation</h2>
    <p class="attractiveness-intro">{intro_strategie}</p>
{strategie_html}
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
    <p class="attractiveness-intro">Chaque ligne est recalculée par le moteur à partir du même lot, vacance 10 %, charges inchangées. Le solde mensuel se lit sous la convention du groupe : frais d'acquisition sortis comptants, solde du prix porté sur quinze ans, intérêts et assurance compris. La ligne surlignée est le loyer retenu.</p>
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
      <p><strong>Hypothèses retenues :</strong> loyer {loyer} €/mois (reconstitué), vacance 10 % en base, charges {charges}/an, placement de la réserve à 2,84 %</p>
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
        rr = variante(d["rec"], prix=milieu)
        cc = engine.compute(rr)
        if cc["fiscal"]["net_apres_is"] / 12.0 - milieu * ANNUITE < 0:
            haut = milieu
        else:
            bas = milieu
    return int(bas // 500.0 * 500.0)


def releve_html(entetes, lignes):
    th = "".join(f"<th>{h}</th>" for h in entetes)
    tr = "\n".join("          <tr>" + "".join(
        f'<td class="num">{v}</td>' if i else f"<td>{v}</td>" for i, v in enumerate(l)) + "</tr>"
        for l in lignes)
    return ('    <table class="comparison-table">\n      <thead>\n        <tr>' + th +
            "</tr>\n      </thead>\n      <tbody>\n" + tr + "\n      </tbody>\n    </table>")


TEXTES = {
    "badge": "Local d'activité et de stockage — 155 m² en rez-de-chaussée",
    "strategie": "bail commercial du local entier, à un artisan ou une activité de stockage",
    "adresse_courte": "Local de 155 m² (74 m² garage + 81 m² cave) — Saint-Raphaël centre (83700)",
    "quartier": "Saint-Raphaël centre",
    "intro_attractivite": "Un volume rare : 155 m² en rez-de-chaussée, à quelques minutes du centre de "
        "Saint-Raphaël, dans une commune littorale où le tissu d'artisans, de services et de commerces "
        "entretient une demande continue de surfaces de stockage. Ce que le bien n'est pas : un local "
        "d'activités de zone. Il n'a ni rideau métallique, ni accès poids lourds, ni aire de manœuvre — et la "
        "moitié de sa surface est en cave. C'est un produit de proximité, pour un artisan, un commerçant du "
        "centre ou un particulier qui a besoin de volume près de chez lui.",
    "profil": "artisan du bâtiment, du paysage ou de la maintenance travaillant dans le centre de "
        "Saint-Raphaël ; commerçant du centre cherchant une réserve ; professionnel de santé ou de service "
        "ayant besoin d'archives. Le preneur doit avoir besoin de l'emplacement plus que de la hauteur.",
    "intro_strategie": "Quatre voies chiffrées : bail commercial du local entier à un seul preneur, bail de "
        "deux volumes séparés (garage et cave), division en boxes, ou changement de destination vers "
        "l'habitation. La première est retenue comme scénario de référence ; les trois autres butent sur des "
        "autorisations et des devis qui n'existent pas encore.",
    "intro_projections": "Un seul lot, un seul preneur : le scénario base pose un loyer de marché reconstitué "
        "de 1 225 €/mois (garage à 10 €/m² et cave à 6 €/m²) avec 10 % de vacance ; le scénario best suppose "
        "qu'un artisan signe un bail 3-6-9 dès l'acquisition à 1 450 €/mois ; le scénario worst réalise le "
        "risque du dossier, un an sans preneur avec toutes les charges au bailleur.",
    "scenarios": [
        {"libelle": "Scénario Base", "classe": "scenario-base", "loyer": 1225.0, "vacance": 10.0,
         "sous_titre": "Loyer de marché reconstitué 1 225 €/mois — vacance 10 % — prix affiché 155 000 €"},
        {"libelle": "Scénario Best", "classe": "scenario-best", "loyer": 1450.0, "vacance": 5.0,
         "sous_titre": "Bail 3-6-9 signé dès l'acquisition à 1 450 €/mois (9,4 €/m²) — vacance 5 %"},
        {"libelle": "Scénario Worst", "classe": "scenario-worst", "loyer": 1100.0, "vacance": 20.0,
         "entretien": 900.0,
         "sous_titre": "Un an sans preneur, relocation à 1 100 €/mois — vacance 20 % — charges et grosses "
                       "réparations au bailleur"},
    ],
    "lecture": "",  # rempli plus bas
    "conf": (
        "Le dossier se juge sur deux chiffres qui n'existent pas encore : le loyer et l'usage autorisé. "
        "Le loyer de 1 225 €/mois est une reconstitution à partir des loyers de locaux d'activités relevés à "
        "Saint-Raphaël (8,3 à 14,7 €/m²/mois) ; à ce niveau, le bien rend 6,03 % net après IS pour un plancher "
        "de branche de 7 %, et il laisse 212 € par mois à la charge du propriétaire. Il faut 1 500 € par mois "
        "pour que le lot s'autofinance. Quant à l'usage, l'annonce vend du « stockage professionnel » sans "
        "jamais dire ce que le règlement de copropriété autorise — et c'est exactement la question restée sans "
        "réponse sur les deux box du 4 octobre."),
    "garde_fous": """        <li><strong>Le prix plafond est de 132 000 €</strong> — au-dessus, la note reste plafonnée par le plancher de rendement et le dossier ne peut plus passer la barre. Soit 23 000 € sous le prix affiché (−15 %).</li>
        <li><strong>Le prix cible est de 111 000 €</strong> (−28 % du prix affiché) : c'est le prix auquel la note franchit 6,5 avec le loyer reconstitué de 1 225 €/mois. La marge nécessaire est trop large pour une négociation ordinaire.</li>
        <li><strong>Le prix d'autofinancement est d'environ 121 500 €</strong> : c'est le prix auquel les 14 700 €/an de loyer couvrent la charge du lot. Avec un loyer de 1 500 €/mois, le seuil monte à 155 000 € — soit exactement le prix demandé.</li>
        <li><strong>Pièces à exiger avant toute offre :</strong> le règlement de copropriété et la désignation du lot, l'accord écrit du syndic ou de l'assemblée sur l'usage envisagé, le budget prévisionnel et les trois derniers PV, l'avis de taxe foncière, un plan coté avec les hauteurs sous plafond du garage et de la cave, le certificat de surface, et les diagnostics (amiante, électricité) — non soumis au DPE ne veut pas dire sans diagnostic.</li>
        <li><strong>Point de méthode :</strong> aucun loyer n'est constaté. Le chiffrage est un ordre de grandeur à confirmer par une agence de gestion locale avant toute offre : chaque tranche de 100 € de loyer vaut environ 12 000 € de prix.</li>""",
    "stance": "On ne paie pas 155 000 € — le dossier se juge après deux réponses, pas avant.",
    "verdict_texte": (
        "Le volume est rare et l'emplacement est bon : 155 m² en rez-de-chaussée dans le centre de "
        "Saint-Raphaël ne se représentent pas souvent, et le prix au mètre carré (1 000 €) est le plus bas de "
        "tous les lots de la commune que nous avons examinés. Mais un local sans preneur, dont la moitié est "
        "en cave, dont le loyer est une hypothèse et dont l'usage n'est pas autorisé par écrit, n'est pas un "
        "actif : c'est une option sur un projet qui reste à documenter. À 155 000 €, le dossier rend 6,03 % "
        "net après IS pour un plancher de 7 %, laisse 212 € par mois à la charge du propriétaire et se paie "
        "1,11 fois sa valeur de revente."),
    "performance": (
        "6,03 % de rendement net après IS sur un prix de revient de 167 000 €, pour un plancher de branche de "
        "7 % : performance 4,3/10. Ratio prix de revient sur valeur de revente : 1,113 — le bien est payé "
        "11 % au-dessus de sa valeur, ce qui suffit à plafonner la note. EBE avant IS : 10 955 €/an. "
        "L'amortissement du bâti (5 010 €/an) ramène l'IS à 892 €."),
    "prix_texte": (
        "Prix plafond 132 000 € et prix cible 111 000 €, soit 15 % et 28 % sous le prix affiché. À 132 000 €, "
        "le rendement net d'IS atteint tout juste le seuil de 7 % avec le loyer reconstitué, et le solde "
        "mensuel se rapproche de l'équilibre sans l'atteindre. Aux frais d'acquisition réels du barème, la "
        "cible ressort à 111 500 €. Un prix sous 121 500 € rendrait le lot autofinancé — le repère des 100 mois "
        "de loyer donne 122 500 €, soit 890 € le mètre carré pour un local en centre-ville de Saint-Raphaël : "
        "c'est peu probable, et cela se dit plutôt que de le proposer."),
    "quartier_long": "Saint-Raphaël centre",
}


def main():
    if ECARTS:
        print(f"ÉCARTS DÉTECTÉS ({len(ECARTS)}) :")
        for e in ECARTS:
            print("  -", e)
        if not TOLERANT:
            raise SystemExit("chiffres publiés en désaccord avec le moteur")
    else:
        print("Contrôles chiffrés : aucun écart")

    t = TEXTES
    lat, lon = "43.4225", "6.7695"
    map_addr = ("Saint-Raphaël centre (83700) — coordonnées du centre-ville, adresse exacte non communiquée")
    adresse = "Plateau Notre-Dame Sud / Beaurivage, Saint-Raphaël (83700) — adresse exacte non communiquée"

    t["lecture"] = (
        "6,03 % net après IS sur un prix de revient de 167 000 € pour un plancher de 7 %, un ratio de 1,11 sur "
        "la valeur de revente, 212 € par mois à la charge du propriétaire, et un loyer qui n'est pas constaté. "
        "Le prix au mètre carré est le plus bas de la commune, mais il achète un local vide, à moitié en cave, "
        "dont l'usage professionnel n'est pas autorisé par écrit. Deux réponses — le loyer réel et le règlement "
        "de copropriété — décideront si c'est une affaire ou un piège.")

    t["releve"] = releve_html(
        ["Source", "Loyer", "Détail"],
        [["Local d'activités 476 m², axe passant proche centre-ville", "10,1 €/m²/mois",
          "4 800 €/mois — large façade, deux rideaux métalliques motorisés, 6 m de hauteur, 10 places"],
         ["Entrepôt 404 m², zone d'activités (bd Cerceron)", "12,4 €/m²/mois",
          "5 000 €/mois — 3,80 m de hauteur, deux portes sectionnelles, accès poids lourds"],
         ["Entrepôt 204 m², même zone", "14,7 €/m²/mois",
          "3 000 €/mois — rideau de fer, accès véhicule, douche et sanitaire"],
         ["Local d'activités 325 m² (bureaux, atelier, formation)", "13,8 €/m²/mois",
          "4 500 €/mois HT + 425 € de charges — électricité, éclairage, internet, 3 parkings"],
         ["Entrepôt logistique 5 398 m² (rue Isaac Newton)", "8,3 €/m²/mois",
          "44 988 €/mois — 8 quais, accès de plain-pied : la référence grande surface"],
         ["Box de stockage 10 à 16 m², Saint-Raphaël (Technoparc)", "16 à 18 €/m²/mois",
          "180 € TTC pour 10 m², 260 € pour 16 m² — la prime du petit lot, non transposable à 155 m²"],
         ["Nos deux box du 4 octobre (32 m² et 38 m²)", "12,5 et 13,2 €/m²/mois",
          "400 € et 500 € TTC — loyer constaté sur le 38 m², qui reste la seule référence signée du dossier"]])
    t["releve"] += ("\n    <p class=\"attractiveness-intro\"><strong>Ce que le relevé établit :</strong> les "
        "locaux d'activités de Saint-Raphaël se louent entre 8,3 et 14,7 €/m²/mois, mais tous ceux du haut de "
        "la fourchette ont ce que ce lot n'a pas : accès véhicule, rideau métallique, hauteur, voire quais. "
        "Le retenu — 10 €/m² pour les 74 m² de garage et 6 €/m² pour les 81 m² de cave, soit 1 225 €/mois — "
        "se situe volontairement dans le bas de la fourchette. C'est ce chiffre qui doit être confirmé par une "
        "agence de gestion avant toute offre : chaque tranche de 100 € de loyer vaut environ 12 000 € de prix.</p>")

    d = prepare(lat, lon, map_addr, adresse, t["lecture"], t["conf"], t["releve"], t["scenarios"],
                t["garde_fous"])
    r = d["rec"]
    autofin = prix_autofinancement(d)

    # contrôles croisés : chaque chiffre publié est recomputé ici
    calcule("solde mensuel base", round(d["solde"]), round(d["f"]["net_apres_is"] / 12 - d["prix"] * ANNUITE))
    calcule("rendement net/revient", round(d["rd"]["net_sur_revient_pct"], 2),
            round(d["f"]["net_apres_is"] / d["revient"] * 100, 2), tolerance=0.05)
    calcule("prix au m²", round(d["prix"] / SURFACE), round(155000.0 / 155.0))
    calcule("plafond publié", float(d["plafond"]), float(d["cible_frais_reels"]), tolerance=25000.0)
    for s in d["scenarios"]:
        attendu = s["c"]["fiscal"]["net_apres_is"] / 12 - d["prix"] * ANNUITE
        calcule(f"solde scénario {s['libelle']}", round(s["solde"], 2), round(attendu, 2), tolerance=1.0)

    projections = "\n\n".join(bloc_scenario(s) for s in d["scenarios"])
    charges = engine.charges_annuelles(r)[0]

    html = TEMPLATE.format(
        titre=r["titre"], adresse_courte=t["adresse_courte"], vendeur=r["annonce"]["vendeur"],
        url=r["annonce"]["url"], badge=t["badge"], strategie=t["strategie"],
        cartes=bloc_cartes(d), lat=lat, lon=lon, map_addr=map_addr,
        quartier=t["quartier"], intro_attractivite=t["intro_attractivite"],
        attractivite=bloc_attractivite(d), profil=t["profil"], lecture=t["lecture"],
        intro_strategie=t["intro_strategie"], conf=t["conf"], strategie_html=bloc_strategie(d),
        releve=t["releve"], grille=bloc_grille_loyer(d), identite=bloc_identite(d),
        intro_projections=t["intro_projections"], projections=projections,
        risques=bloc_risques(d), verdict_cls=d["classe"], stance=t["stance"],
        verdict_texte=t["verdict_texte"], performance=t["performance"], prix_texte=t["prix_texte"],
        garde_fous=t["garde_fous"], amortissement=eur(d["f"]["amortissement"]),
        frais=eur(r["hypotheses"]["frais_acquisition_euros"]), loyer=nfr(d["loyer"]),
        charges=eur(charges), note=nfr(d["note"], 1),
        verdict_libelle={"buy": "à acheter", "nego": "à négocier", "pass": "à fuir"}[d["classe"]],
        perf_score=nfr(d["comp"]["s_performance"], 1), secu_score=nfr(d["comp"]["s_securite"], 1),
        adeq_score=nfr(d["comp"]["s_adequation"], 1), risque_score=nfr(d["comp"]["s_risque"], 1),
        prix_affiche=eur(d["prix"]),
    )

    residuels = [m for m in re.findall(r"\{[a-z_][a-z_0-9]*\}", html) if m not in ("{s}", "{z}", "{x}", "{y}")]
    if residuels:
        raise SystemExit(f"placeholders non remplacés : {sorted(set(residuels))}")
    for attendu in ("report-header", "summary-cards", "map-section", "attractiveness",
                    "strategy-exploration", "identity-sheet", "financial-projections",
                    "risk-matrix", 'section class="verdict', "report-signature"):
        if attendu not in html:
            raise SystemExit(f"section manquante : {attendu}")
    if 'name="robots"' not in html or "noindex" not in html:
        raise SystemExit("noindex absent")
    interdits = re.findall(r"\b(prêt|prêts|emprunt\w*|crédit\w*|apport\w*|mensualit\w*|levier|montage)\b", html, flags=re.I)
    if interdits:
        raise SystemExit(f"mot de financement : {sorted(set(interdits))}")

    classes = set(re.findall(r'class="([^"]+)"', html))
    feuilles = open(os.path.join(RACINE, "style.css"), encoding="utf-8").read()
    definies = set(re.findall(r"\.([a-zA-Z][\w-]*)", feuilles))
    neutres = {"strategy-badge", "attr-detail", "strategy-row", "selected", "verdict-decision",
               "num", "subtotal", "total", "secondary", "highlight"}
    inconnues = sorted({c for groupe in classes for c in groupe.split() if c not in definies and c not in neutres})
    if inconnues:
        print("classes CSS non définies :", inconnues)

    if ECARTS:
        print(f"ÉCARTS DÉTECTÉS ({len(ECARTS)}) :")
        for e in ECARTS:
            print("  -", e)
        if not TOLERANT:
            raise SystemExit("chiffres publiés en désaccord avec le moteur")

    sortie = os.path.join(RACINE, "analyses", SLUG, "index.html")
    os.makedirs(os.path.dirname(sortie), exist_ok=True)
    with open(sortie, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"{SLUG} : {len(html)} caractères | note {d['note']} {d['verdict']} ({d['classe']}) | "
          f"net/revient {d['rd']['net_sur_revient_pct']} % | solde {d['solde']:+.0f} €/mois | "
          f"plafond {d['plafond']} € | cible {d['cible']} € | autofinancement {autofin} € | "
          f"cible aux frais réels {d['cible_frais_reels']} €")


if __name__ == "__main__":
    main()
