#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère la fiche du duplex 3 pièces de 63 m² — Champ de Mars, Toulon.

analyses/2026-10-13-duplex-3p-63m2-champs-de-mars-toulon/index.html — SeLoger 26SXIFKHH1R3

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

SLUG = "2026-10-13-duplex-3p-63m2-champs-de-mars-toulon"
SURFACE = 63.0
VALEUR = 150000.0
TRAVAUX_COLOC = 8000.0
ENTRETIEN_COLOC = 2200.0


def rec(slug):
    return [r for r in DATA["analyses"] if r["slug"] == slug][0]


def variante(r, loyer=None, vacance=None, travaux=None, entretien=None, prix=None):
    rr = copy.deepcopy(r)
    if loyer is not None:
        rr["marche"]["loyers"][0]["loyer_mensuel_euros"] = loyer
    if vacance is not None:
        rr["hypotheses"]["vacance_base_pct"] = vacance
    if travaux is not None:
        rr["bien"]["travaux"]["montant_euros"] = travaux
    if entretien is not None:
        rr["hypotheses"]["charges"]["entretien_annuel_euros"] = entretien
    if prix is not None:
        rr["annonce"]["prix_retenu_euros"] = prix
    return rr


def prepare(lat, lon, map_addr, adresse, lecture, conf, releve, scenarios, garde_fous, textes):
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
        "releve": releve, "garde_fous": garde_fous, "textes": textes,
        "classe": {"acheter": "buy", "negocier": "nego", "fuir": "pass"}[verdict],
        "classe_note": scoring.classe_note(note),
    }
    d["plafond"], d["contrainte"] = scoring.prix_plafond(r)
    d["cible"] = scoring.prix_cible(r)
    calcule("prix plafond (moteur)", d["plafond"], d["plafond"])

    def aux_frais_reels(cible_note=6.5):
        """Prix auquel la note atteint la cible, frais d'acquisition laissés constants."""
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

    # scénarios : loyer, vacance, travaux éventuels
    d["scenarios"] = []
    for sc in scenarios:
        rr = variante(r, loyer=sc["loyer"], vacance=sc["vacance"],
                      travaux=sc.get("travaux", 0.0), entretien=sc.get("entretien"))
        cc = engine.compute(rr)
        assiette = prix + sc.get("travaux", 0.0)
        d["scenarios"].append({
            "libelle": sc["libelle"], "classe": sc["classe"], "sous_titre": sc["sous_titre"],
            "loyer": sc["loyer"], "vacance": sc["vacance"], "c": cc, "rec": rr,
            "solde": cc["fiscal"]["net_apres_is"] / 12 - assiette * ANNUITE,
        })

    # grille de loyer — la même à toutes les lignes, seuls loyer et vacance bougent
    d["grille"] = []
    for l in (650.0, 700.0, 750.0, 800.0, 850.0, 900.0, 1350.0):
        rr = variante(r, loyer=l, vacance=5.0)
        cc = engine.compute(rr)
        d["grille"].append({
            "loyer": l, "ebe": cc["fiscal"]["ebe"], "net": cc["fiscal"]["net_apres_is"],
            "solde": cc["fiscal"]["net_apres_is"] / 12 - prix * ANNUITE,
            "rdt": cc["rendements"]["net_sur_revient_pct"],
        })

    # stratégies : chacune recalculée par le moteur
    d["strategies"] = []
    for st in r["analyse"]["strategies_explorees"]:
        nom = st["strategie"]
        if nom.startswith("Portage"):
            rr = variante(r, loyer=800.0, vacance=5.0)
        elif nom.startswith("Colocation"):
            rr = variante(r, loyer=1350.0, vacance=5.0, travaux=TRAVAUX_COLOC, entretien=ENTRETIEN_COLOC)
        else:
            rr = variante(r, loyer=850.0, vacance=5.0)
        cc = engine.compute(rr)
        d["strategies"].append({
            "strategie": nom, "lots": st["lots"], "c": cc,
            "rdt": cc["rendements"]["net_sur_revient_pct"],
            "ratio": cc["ratio_cout_valeur"], "faisabilite": st["faisabilite"],
            "risque": st["risque"], "retenue": nom.startswith("Portage"),
        })
    return d


def bloc_cartes(d):
    cartes = [
        ("Prix affiché", eur(d["prix"]) + f" ({eur(d['prix'] / SURFACE)}/m²)"),
        ("Prix de revient", eur(d["revient"])),
        ("Valeur de revente retenue", eur(d["rec"]["marche"]["valeur"]["retenue_euros"])),
        ("Loyer encaissé", eur(d["loyer"]) + "/mois hors charges"),
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
        fais = "faisabilite-haute" if "Immédiate" in st["faisabilite"] else "faisabilite-basse"
        sel = ' class="strategy-row selected"' if st["retenue"] else ' class="strategy-row"'
        lignes.append(
            f"        <tr{sel}>\n          <td>{st['strategie']}</td>\n          <td>{st['lots']}</td>\n"
            f"          <td>{pct(st['rdt'])} (loyer {eur(st['c']['revenus_bruts_annuels'] / 12)})</td>\n"
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
        ("Occupation", "Locataire en place — bail 3/6/9 du 15 septembre 2020, loyer 800 € hors charges "
                       "(830 € charges comprises). Le bail a franchi son échéance triennale en septembre 2026 : "
                       "il court jusqu'en septembre 2029."),
        ("Loyer de marché retenu", eur(d["loyer"]) + "/mois — loyer encaissé, bail en place. Relevés de location "
         "nue à Toulon : 58 m² à 900 €, 63 m² à 840 € charges comprises, T4 de 67 m² à 1 020 €, moyenne communale "
         "12,02 €/m². Cible colocation : 3 × 450 € = 1 350 €/mois, hors calcul de prix."),
        ("Charges de copropriété", eur(b["copro"]["charges_annuelles_euros"]) + "/an — " + b["copro"]["charges_source"]),
        ("Taxe foncière", eur(h["taxe_fonciere_annuelle_euros"]) + "/an — " + h["taxe_fonciere_commentaire"]),
        ("Entretien et conservation", eur(h["entretien_annuel_euros"]) + "/an — " + h["entretien_commentaire"]),
        ("Frais d'acquisition", eur(d["rec"]["hypotheses"]["frais_acquisition_euros"]) + " — "
         + d["rec"]["hypotheses"]["frais_acquisition_commentaire"]),
        ("Amortissement", eur(d["f"][ "amortissement"]) + "/an — 90 % du prix de revient sur 30 ans (bâti)"),
        ("DPE", "D (180 kWh/m²/an) / GES B — facture annoncée entre 1 090 et 1 510 €/an, à la charge du locataire, "
                "climatisation réversible et menuiseries PVC double vitrage"),
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
    <p class="attractiveness-intro">Chaque ligne est recalculée par le moteur à partir du même lot, vacance 5 %, charges inchangées. Le solde mensuel se lit sous la convention du groupe : frais d'acquisition sortis comptants, solde du prix porté sur quinze ans, intérêts et assurance compris. La dernière ligne montre la cible de colocation, hors bail en place.</p>
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
      <p><strong>Hypothèses retenues :</strong> loyer {loyer} €/mois encaissé, vacance 5 % en base, charges {charges}/an, placement de la réserve à 2,84 %</p>
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
    "badge": "Portage du bail — bascule en colocation à l'échéance",
    "strategie": "portage du bail en place, puis bascule en colocation à l'échéance",
    "adresse_courte": "Duplex 3 pièces de 63 m² avec chambre mansardée — Champ de Mars, Toulon (83000)",
    "quartier": "Champ de Mars, Toulon",
    "intro_attractivite": "Champ de Mars II, dans la couronne immédiate du centre de Toulon : six arrêts de bus "
        "dans un rayon de 200 m, école maternelle à 100 m, collège à 700 m, et le secteur étudiant toulonnais "
        "(droit, Chalucet, paramédical) à quelques minutes. C'est un quartier où la demande locative ne se "
        "discute pas — le logement est loué depuis 2020 — mais c'est aussi un quartier de bâti hétérogène, "
        "où la valeur se joue rue par rue et où une copropriété de 1935 porte des postes collectifs que "
        "l'annonce ne détaille pas.",
    "profil": "aujourd'hui, un locataire en place en bail nu depuis septembre 2020 ; demain, si la chambre "
        "mansardée est louable en l'état, trois colocataires étudiants ou jeunes actifs.",
    "intro_strategie": "Trois lectures chiffrées du même lot : portage du bail en place, colocation meublée à "
        "trois chambres après le départ du locataire, ou location nue au marché après ce même départ. La seule "
        "qui produit du rendement est la colocation — et c'est aussi la seule que le bail en cours interdit.",
    "intro_projections": "Les trois scénarios partent du même lot et du même prix, seuls le loyer et la vacance "
        "changent ; le scénario de colocation porte en plus 8 000 € d'ameublement et 2 200 €/an de fluides et de "
        "renouvellement du mobilier, conformément à l'exploitation meublée.",
    "scenarios": [
        {"libelle": "Scénario Base", "classe": "scenario-base", "loyer": 800.0, "vacance": 5.0,
         "sous_titre": "Loyer encaissé 800 € hors charges — vacance 5 % — prix affiché 140 000 €"},
        {"libelle": "Scénario Best", "classe": "scenario-best", "loyer": 1350.0, "vacance": 5.0,
         "travaux": TRAVAUX_COLOC, "entretien": ENTRETIEN_COLOC,
         "sous_titre": "Colocation 3 × 450 € après départ du locataire — vacance 5 % — prix affiché 140 000 € "
                       "plus 8 000 € d'ameublement"},
        {"libelle": "Scénario Worst", "classe": "scenario-worst", "loyer": 800.0, "vacance": 15.0,
         "sous_titre": "Loyer 800 € — vacance 15 % — charges d'entretien relevées, départ du locataire non "
                       "remplacé dans les délais"},
    ],
    "lecture": ("Le produit est en place et le loyer rentre : 800 € hors charges, un locataire depuis septembre 2020, "
        "un 8e étage avec ascenseur, une véranda, un balcon, une cave, un DPE D. Ce qui ne tient pas, c'est le prix "
        "et le calendrier. À 140 000 €, le lot rend 3,90 % net d'IS pour un plancher de 5 % et laisse 457 € par "
        "mois à la charge du propriétaire ; la seule exploitation rentable — la colocation à trois chambres, "
        "1 350 €/mois — est interdite par un bail qui court jusqu'en septembre 2029."),
    "conf": (
        "Le dossier ne se juge pas sur le produit, qui est correct — 8e étage avec ascenseur, véranda, balcon, "
        "cave, DPE D, loyer en place — mais sur deux verrous. Le premier est le loyer : 800 € par mois, c'est le "
        "niveau du marché pour 63 m², il n'y a pas de rattrapage à espérer sans colocation. Le second est le bail : "
        "engagé jusqu'en septembre 2029, il ferme précisément la seule exploitation rentable du lot. Acheter ici, "
        "c'est payer 140 000 € pour encaisser 800 € et attendre trois ans — sauf à obtenir un prix qui rémunère "
        "cette attente."),
    "garde_fous": """        <li><strong>Le prix plafond est de 106 000 €</strong> — au-dessus, la note ne peut plus dépasser le seuil de rendement de branche (5 % net d'IS sur revient) et le dossier reste « à négocier » quoi qu'il arrive. Soit 34 000 € sous le prix affiché (−24 %).</li>
        <li><strong>Le prix cible est de 99 500 €</strong> (−29 % du prix affiché), et 96 500 € aux frais d'acquisition réels : c'est le prix auquel la note franchit 6,5. La marge de négociation nécessaire est trop large pour une discussion de couloir.</li>
        <li><strong>Le prix d'autofinancement est d'environ 68 500 €</strong> : c'est le prix auquel les 9 600 €/an de loyer couvrent la charge du lot. Le repère des 100 mois de loyer donne 80 000 €. Ce sont des prix qui n'existent pas dans ce quartier : ce n'est pas une négociation, c'est un constat de trésorerie.</li>
        <li><strong>Pièces à exiger avant toute offre :</strong> le bail en cours et les quittances (historique d'IRL, impayés), le certificat Carrez et la surface réelle de la chambre mansardée avec sa hauteur sous plafond, le statut de cette chambre (lot rattaché à l'appartement ou lot distinct), le budget prévisionnel et les trois derniers appels de fonds de copropriété, l'avis de taxe foncière, et le plan pluriannuel de travaux de l'immeuble de 1935.</li>
        <li><strong>Point de méthode :</strong> la cible de colocation (1 350 €/mois) n'entre dans aucun prix. Seul le loyer encaissé alimente l'EBE, les plafonds et le solde.</li>""",
    "stance": "On négocie — mais pas à 140 000 €, et ce n'est pas le loyer qui fera la différence.",
    "verdict_texte": (
        "Le produit est bon, le prix ne l'est pas. À 140 000 €, le lot rend 3,90 % net après IS sur un prix de "
        "revient de 151 200 €, pour un plancher de branche de 5 %, et il laisse un solde mensuel négatif de 457 € : "
        "il ne couvre pas sa propre charge. Le prix affiché est inférieur de 9 % à la médiane du marché toulonnais, "
        "ce qui suffit à séduire — mais c'est le loyer en place, fils de 2020 et bloqué jusqu'en 2029, qui fixe la "
        "valeur, et il ne porte pas ce montant."),
    "performance": (
        "3,90 % de rendement net après IS sur un prix de revient de 151 200 €, pour un plancher de branche de 5 % : "
        "performance 3,2/10. Ratio prix de revient sur valeur de revente : 1,008 — la marge de sécurité est nulle. "
        "EBE avant IS : 6 144 €/an. L'amortissement du bâti (4 536 €/an, la totalité du prix étant amortissable) "
        "ramène l'IS à 241 €, ce qui protège la trésorerie sans créer de rendement."),
    "prix_texte": (
        "Prix plafond 106 000 € et prix cible 99 500 €, soit 24 % et 29 % sous le prix affiché. À 106 000 €, le "
        "rendement net d'IS atteint péniblement le seuil de 5 % et le solde mensuel reste négatif d'environ "
        "240 €/mois : le dossier entrerait dans la doctrine de rendement sans entrer dans celle de trésorerie. "
        "Au prix d'autofinancement (environ 68 500 €), l'affaire serait bonne — un tel prix n'existe pas pour ce "
        "quartier, et cela se dit plutôt que de le proposer."),
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
    lat, lon = "43.1216", "5.9444"
    map_addr = ("Quartier Champ de Mars II, Toulon (83000) — coordonnées du quartier, "
                "adresse exacte non communiquée")
    adresse = "Quartier Champ de Mars II, Toulon (83000) — adresse exacte non communiquée par l'agence"

    t["releve"] = releve_html(
        ["Source", "Loyer", "Détail"],
        [["Loyer en place — bail 3/6/9 du 15/09/2020", "800 € HC (830 € CC)",
          "la seule assiette réelle du dossier ; 12,7 €/m², dans le marché haut de la surface"],
         ["Moyenne communale, appartements, Toulon (FNAIM 83)", "12,02 €/m²",
          "soit 757 €/mois pour 63 m² — un loyer en place au-dessus de la moyenne communale"],
         ["58 m², Champ de Mars", "900 €/mois", "annonce du 13/10/2026 — surface plus petite, même quartier"],
         ["63 m², Toulon", "840 € CC", "annonce de location du 13/10/2026"],
         ["T4 de 67 m², Toulon", "1 020 €/mois", "annonce de particulier du 13/10/2026"],
         ["Cible colocation — chambre meublée, Toulon", "450 € CC",
          "relevé du 28/09/2026 : 13 annonces, masse principale 420 à 520 € ; Champ de Mars 480 € pour 11 m²"]])
    t["releve"] += ("\n    <p class=\"attractiveness-intro\"><strong>Ce que le relevé établit :</strong> le loyer "
        "encaissé n'est pas sous le marché — il est au-dessus de la moyenne communale au mètre carré. Il n'y a "
        "donc pas de rattrapage à attendre d'une relocation nue (environ 850 à 900 €, une fois le bail terminé) : "
        "la seule voie de revenu supplémentaire est la colocation, chiffrée à 1 350 €/mois, et elle est verrouillée "
        "par le bail "
        "jusqu'en septembre 2029.</p>")

    d = prepare(lat, lon, map_addr, adresse, t["lecture"], t["conf"], t["releve"], t["scenarios"],
                t["garde_fous"], t)
    r = d["rec"]
    autofin = prix_autofinancement(d)

    # contrôles croisés : chaque chiffre publié dans les textes est recomputé ici
    calcule("solde mensuel base", round(d["solde"]), round(d["f"]["net_apres_is"] / 12 - d["prix"] * ANNUITE))
    calcule("rendement net/revient", round(d["rd"]["net_sur_revient_pct"], 2),
            round(d["f"]["net_apres_is"] / d["revient"] * 100, 2), tolerance=0.05)
    calcule("prix au m²", round(d["prix"] / SURFACE), round(140000.0 / 63.0))
    calcule("plafond publié", float(d["plafond"]), float(d["cible_frais_reels"]), tolerance=20000.0)
    calcule("EBE base", round(d["f"]["ebe"]), round(engine.compute(r)["fiscal"]["ebe"]))

    projections = "\n\n".join(bloc_scenario(s) for s in d["scenarios"])
    charges = engine.charges_annuelles(r)[0]
    # le solde publié dans les scénarios est recalculé une seconde fois
    for s in d["scenarios"]:
        attendu = s["c"]["fiscal"]["net_apres_is"] / 12 - (d["prix"] + (TRAVAUX_COLOC if s["loyer"] == 1350.0 else 0.0)) * ANNUITE
        calcule(f"solde scénario {s['libelle']}", round(s["solde"], 2), round(attendu, 2), tolerance=1.0)

    html = TEMPLATE.format(
        titre=r["titre"], adresse_courte=t["adresse_courte"], vendeur=r["annonce"]["vendeur"],
        url=r["annonce"]["url"], badge=t["badge"], strategie=t["strategie"],
        cartes=bloc_cartes(d), lat=lat, lon=lon, map_addr=map_addr,
        quartier=t["quartier"], intro_attractivite=t["intro_attractivite"],
        attractivite=bloc_attractivite(d), profil=t["profil"], lecture=t["lecture"],
        intro_strategie=t["intro_strategie"], conf=t["conf"],
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
    ).replace("{strategie}", bloc_strategie(d))

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
          f"plafond {d['plafond']} € | cible {d['cible']} € | autofinancement {autofin} €")


if __name__ == "__main__":
    main()
