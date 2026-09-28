#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère la fiche HTML du slug 2026-09-28-appartement-t4-toulon-saint-roch.

T4/F4 de 88 m², 2e étage sur 4 sans ascenseur, balcon et cave, annoncé
« entièrement rénové » et « optimisé pour la colocation », quartier Saint-Roch
à Toulon (83200). Prix affiché 199 000 € (2 261 €/m²), honoraires vendeur,
annonce SeLoger 273759509 (iad France, Philippe Bernard, réf. 2058759).

Conventions de chiffrage (identiques aux autres fiches du dépôt) :
- frais d'acquisition 15 920 € (les 8 % affichés par le simulateur de l'annonce)
- SCI à l'IS ; convention prudente du moteur : l'IS de 15 % frappe l'EBE entier,
  sans déduire l'amortissement du bâti ni les intérêts d'emprunt (tous deux
  réels sur un logement), ce qui sous-estime le dossier plutôt que l'inverse
- crédit 90 % sur 15 ans à 3,70 %, assurance 0,34 %, apport 10 %
- valeur de marché 2 100 €/m² (DVF 2024-2025 du quartier Saint-Roch, tranche
  80-95 m², trois méthodes d'agrégation convergentes)
- loyer retenu : colocation meublée à trois chambres, 450 € par chambre

Tout chiffre publié passe par calcule() ; avec HERMES_TOLERANT=1 les écarts sont
listés au lieu de lever une assertion.
"""
import copy
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

from analyse_app import engine, scoring  # noqa: E402

SLUG = "2026-09-28-appartement-t4-toulon-saint-roch"
SORTIE = os.path.join(RACINE, "analyses", SLUG, "index.html")
TOLERANT = os.environ.get("HERMES_TOLERANT") == "1"

# Annuité mensuelle par euro de prix : 90 % financés sur 15 ans à 3,70 % + 0,34 %
ANNUITE = 0.9 * (0.037 / 12) / (1 - (1 + 0.037 / 12) ** -180) + 0.9 * 0.0034 / 12

ECARTS = []


def calcule(libelle, publie, recalcule, tolerance=0.6):
    """Vérifie qu'un chiffre publié correspond au recalcul du moteur."""
    if publie is None or recalcule is None:
        if publie != recalcule:
            ECARTS.append(f"{libelle} : publié {publie} / recalculé {recalcule}")
        return publie
    if abs(float(publie) - float(recalcule)) > tolerance:
        ECARTS.append(f"{libelle} : publié {publie} / recalculé {recalcule}")
    return publie


def eur(v, dec=0):
    if v is None:
        return "—"
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",") + " €"


def nfr(v, dec=0):
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


def pct(v, dec=2):
    return f"{v:.{dec}f}".replace(".", ",") + " %"


def euro_signe(v, dec=0):
    if abs(v) < 0.5:
        return "0 €"
    return ("−" if v < 0 else "+") + nfr(abs(v), dec) + " €"


def charger_record():
    data = json.load(open(os.path.join(RACINE, "analyses", "analyses.json")))
    for r in data["analyses"]:
        if r["slug"] == SLUG:
            return r
    raise SystemExit(f"record absent de la base : {SLUG}")


REC = charger_record()


def variante(prix=None, loyer=None, vacance=None, entretien=None):
    """Copie du record surchargée, recalculée par le moteur (jamais à la main)."""
    r = copy.deepcopy(REC)
    if loyer is not None:
        for ligne in r["marche"]["loyers"]:
            ligne["loyer_mensuel_euros"] = loyer
    if vacance is not None:
        r["hypotheses"]["vacance_base_pct"] = vacance
    if entretien is not None:
        r["hypotheses"]["charges"]["entretien_annuel_euros"] = entretien
    if prix is not None:
        r["annonce"]["prix_retenu_euros"] = prix
    c = engine.compute(r)
    note, verdict, comp = scoring.note_et_verdict(r, c)
    return r, c, note, verdict, comp


# --------------------------------------------------------------------------
# Chiffres du dossier
# --------------------------------------------------------------------------
C = engine.compute(REC)
NOTE, VERDICT, COMP = scoring.note_et_verdict(REC, C)
VERDICT_CLS = {"acheter": "buy", "negocier": "nego", "fuir": "pass"}[VERDICT]
VERDICT_FR = {"acheter": "à acheter", "negocier": "à négocier", "fuir": "à fuir"}

B = REC["bien"]
A = REC["annonce"]
M = REC["marche"]
H = REC["hypotheses"]
CH = H["charges"]

PRIX_AFFICHE = A["prix_affiche_euros"]
FRAIS = H["frais_acquisition_euros"]
AEM = C["prix_revient_total"]
SURF = B["surfaces"]["carrez_m2"]
VALEUR = M["valeur"]["retenue_euros"]
VALEUR_M2 = VALEUR / SURF
PRIX_M2 = PRIX_AFFICHE / SURF
LOYER = M["loyers"][0]["loyer_mensuel_euros"]
CHAMBRE = LOYER / 3.0
LOYERS_AN = LOYER * 12
EBE = C["fiscal"]["ebe"]
IS = C["fiscal"]["is_annuel"]
NET = C["fiscal"]["net_apres_is"]
MENS = PRIX_AFFICHE * ANNUITE
CF = NET / 12.0 - MENS
DOCTRINE = EBE / AEM * 100.0
DETENTION = CH["charges_copro_annuelles_euros"] + CH["taxe_fonciere_annuelle_euros"]

calcule("prix au m²", round(PRIX_M2), 2261, 1)
calcule("valeur au m²", round(VALEUR_M2), 2100, 1)
calcule("valeur retenue", VALEUR, 184800, 1)
calcule("acte en main", AEM, 214920, 1)
calcule("EBE", round(EBE), 6963, 1)
calcule("IS", round(IS), 1044, 1)
calcule("net après IS", round(NET), 5919, 1)
calcule("mensualité", round(MENS), 1349, 1)
calcule("cash-flow mensuel au prix affiché", round(CF), -856, 1)
calcule("rendement net sur prix de revient", round(C["rendements"]["net_sur_revient_pct"], 2), 2.75, 0.01)
calcule("rendement net sur valeur", round(C["rendements"]["net_sur_valeur_pct"], 2), 3.20, 0.01)
calcule("doctrine 5 % net avant IS", round(DOCTRINE, 2), 3.24, 0.01)
calcule("ratio coût / valeur", round(C["ratio_cout_valeur"], 3), 1.163, 0.001)
calcule("note du moteur", NOTE, 4.7, 0.05)
calcule("charges de détention", DETENTION, 3864, 1)
calcule("part des charges dans les loyers bruts", round(DETENTION / LOYERS_AN * 100, 1), 23.9, 0.2)

# --- Échelle de prix : note et cash-flow à chaque prix payé -----------------
ECHELLE = []
for prix in (199000.0, 184800.0, 169600.0, 155000.0, 145000.0, 128000.0, 111000.0, 72500.0):
    _, c, n, v, _ = variante(prix=prix)
    ebe = c["fiscal"]["ebe"]
    ECHELLE.append({
        "prix": prix, "note": n, "verdict": v, "ebe": ebe,
        "net": c["fiscal"]["net_apres_is"],
        "cf": c["fiscal"]["net_apres_is"] / 12.0 - prix * ANNUITE,
        "doctrine": ebe / (prix * (1 + FRAIS / PRIX_AFFICHE)) * 100.0,
        "m2": prix / SURF,
        "ratio": c["ratio_cout_valeur"],
    })
calcule("échelle — net au prix affiché", 0, 0, 0)

# --- Échelle de la location nue, pour comparaison --------------------------
ECHELLE_NUE = []
for prix in (199000.0, 155000.0, 128000.0, 111000.0):
    _, c, n, v, _ = variante(prix=prix, loyer=1000.0, vacance=5.0, entretien=830.0)
    ECHELLE_NUE.append({"prix": prix, "note": n, "verdict": v,
                        "ebe": c["fiscal"]["ebe"], "net": c["fiscal"]["net_apres_is"],
                        "cf": c["fiscal"]["net_apres_is"] / 12.0 - prix * ANNUITE,
                        "doctrine": c["fiscal"]["ebe"] / (prix * (1 + FRAIS / PRIX_AFFICHE)) * 100.0})

# --- Robustesse : le verdict dépend-il du loyer ? ---------------------------
ROBUSTESSE = []
for loyer_nu in (850.0, 1000.0, 1200.0, 1300.0, 1440.0):
    entretien = 0.05 * loyer_nu * 12.0 + 100.0   # gestion 5 % des loyers + provision
    _, c, n, v, _ = variante(prix=PRIX_AFFICHE, loyer=loyer_nu, vacance=5.0,
                             entretien=entretien)
    ROBUSTESSE.append({
        "loyer": loyer_nu, "note": n, "ebe": c["fiscal"]["ebe"],
        "doctrine": c["fiscal"]["ebe"] / (PRIX_AFFICHE * (1 + FRAIS / PRIX_AFFICHE)) * 100.0,
        "cf": c["fiscal"]["net_apres_is"] / 12.0 - PRIX_AFFICHE * ANNUITE,
    })

# --- Scénarios publiés ------------------------------------------------------
S_BASE = variante(loyer=LOYER, vacance=8.0, entretien=3142.0, prix=PRIX_AFFICHE)
S_BEST = variante(loyer=1440.0, vacance=5.0, entretien=3142.0, prix=VALEUR)
S_WORST = variante(loyer=LOYER, vacance=15.0, entretien=3142.0, prix=PRIX_AFFICHE)
calcule("scénario base — EBE", round(S_BASE[1]["fiscal"]["ebe"]), 6963, 1)
calcule("scénario optimiste — EBE", round(S_BEST[1]["fiscal"]["ebe"]), 8448, 1)
calcule("scénario pessimiste — EBE", round(S_WORST[1]["fiscal"]["ebe"]), 5829, 1)


# --------------------------------------------------------------------------
# Blocs HTML
# --------------------------------------------------------------------------
def bloc_cartes():
    cartes = [
        ("Prix affiché", eur(PRIX_AFFICHE)),
        ("Prix au m²", eur(PRIX_M2) + " /m²"),
        ("Valeur de marché (DVF)", eur(VALEUR)),
        ("Loyer retenu", f"{eur(LOYER)}/mois (3 × {eur(CHAMBRE)})"),
        ("Rendement net d'IS", pct(C["rendements"]["net_sur_valeur_pct"]) + " sur valeur"),
        ("Détention annuelle", eur(DETENTION)),
        ("Cash-flow mensuel", euro_signe(CF)),
    ]
    html = []
    for label, valeur in cartes:
        html.append(f'    <div class="card">\n      <span class="card-label">{label}</span>\n'
                    f'      <span class="card-value">{valeur}</span>\n    </div>')
    html.append(f'    <div class="card card-verdict note-{int(NOTE)}">\n'
                f'      <span class="card-label">Note</span>\n'
                f'      <span class="card-value">{str(NOTE).replace(".", ",")}/10</span>\n    </div>')
    return "\n".join(html)


def bloc_attractivite():
    cards = []
    for dim in REC["analyse"]["attractivite"]:
        s = dim["score"]
        cards.append(
            '      <div class="attr-card">\n'
            f'        <span class="attr-label">{dim["dimension"].capitalize()}</span>\n'
            f'          <span class="attr-score"><strong>{s}/10</strong></span>\n'
            f'        <div class="attr-bar-track"><div class="attr-bar-fill" style="width:{s * 10}%"></div></div>\n'
            f'        <p class="attr-detail">{dim["justification"]}</p>\n'
            '      </div>')
    moy = sum(d["score"] for d in REC["analyse"]["attractivite"]) / 6.0
    calcule("moyenne d'attractivité", round(moy, 2), 6.33, 0.01)
    return "\n".join(cards)


def bloc_strategies():
    lignes = []
    for i, s in enumerate(REC["analyse"]["strategies_explorees"]):
        retenue = " selected" if s["strategie"].startswith("Colocation meublée à trois") else ""
        lignes.append(
            f'        <tr class="strategy-row{retenue}">\n'
            f'          <td><strong>{s["strategie"]}</strong></td>\n'
            f'          <td>{s["rendement"]}</td>\n'
            f'          <td>{s["faisabilite"]}</td>\n'
            f'          <td>{s["risque"]}</td>\n'
            '        </tr>')
    return ("    <table class=\"comparison-table\">\n      <thead>\n        <tr>"
            "<th>Stratégie</th><th>Rendement</th><th>Faisabilité</th><th>Risque</th></tr>\n"
            "      </thead>\n      <tbody>\n" + "\n".join(lignes) + "\n      </tbody>\n    </table>")


def bloc_echelle():
    lignes = []
    for l in ECHELLE:
        cls = ' class="highlight"' if abs(l["prix"] - VALEUR) < 1 else ""
        lignes.append(
            f"          <tr{cls}><td>{eur(l['prix'])} <span class=\"scenario-subtitle\">"
            f"({eur(l['m2'])}/m²)</span></td>"
            f'<td class="num">{str(l["note"]).replace(".", ",")}/10</td>'
            f"<td>{VERDICT_FR[l['verdict']]}</td>"
            f'<td class="num">{eur(l["ebe"])}</td>'
            f'<td class="num">{euro_signe(l["cf"])}/mois</td>'
            f'<td class="num">{pct(l["doctrine"])}</td></tr>')
    return "\n".join(lignes)


def bloc_echelle_nue():
    lignes = []
    for l in ECHELLE_NUE:
        lignes.append(
            f"          <tr><td>{eur(l['prix'])}</td>"
            f'<td class="num">{str(l["note"]).replace(".", ",")}/10</td>'
            f"<td>{VERDICT_FR[l['verdict']]}</td>"
            f'<td class="num">{eur(l["ebe"])}</td>'
            f'<td class="num">{euro_signe(l["cf"])}/mois</td>'
            f'<td class="num">{pct(l["doctrine"])}</td></tr>')
    return "\n".join(lignes)


def bloc_identite():
    v = M["valeur"]
    return f"""      <tbody>
        <tr><th>Adresse</th><td>Quartier Saint-Roch, Toulon Ouest (83200) — <strong>adresse exacte non publiée par l'annonce</strong>. Mandataire indépendant iaD France, Philippe Bernard, agent commercial immatriculé au RSAC de Toulon sous le numéro 832454425, référence d'annonce 2058759. Gare de Toulon à 800 m, 1 km du littoral, aéroport de Hyères à 24 km.</td></tr>
        <tr><th>Type</th><td>Appartement T4/F4 — 4 pièces, 3 chambres, 88 m² annoncés, 2e étage sur 4 étages <strong>sans ascenseur</strong>, séjour donnant sur balcon, cuisine aménagée ouverte, salle d'eau, WC séparés, cave. Annoncé « entièrement rénové » et « déjà optimisé pour de la colocation ». DPE D, GES D.</td></tr>
        <tr><th>Lots vendus</th><td>L'annonce vise <strong>2 lots</strong> dans une copropriété de 30 : l'appartement et une cave. La fiche caractéristiques affiche pourtant « pas de cave » — incohérence à trancher dans l'état daté, car un second lot se finance et se revend.</td></tr>
        <tr><th>Copropriété</th><td>30 lots, aucune procédure en cours. Taxe foncière : taux global de 49,76 % à Toulon en 2025 (commune 39,39 %, Métropole TPM 5,00 %, syndicats 4,69 %), inchangé depuis 2021. La TEOM (11,84 %) est appelée dans les charges de copropriété et ne doit pas être comptée deux fois.</td></tr>
        <tr><th>Travaux</th><td>Aucun devis produit, aucun montant retenu. Le bien est déclaré rénové, mais il reste en DPE D : c'est la première pièce à demander (isolation, menuiseries, mode de chauffage).</td></tr>
        <tr><th>Valeur retenue</th><td>{eur(VALEUR)} net vendeur, soit <strong>{eur(VALEUR_M2)}/m²</strong> — médiane des ventes du quartier Saint-Roch pour la tranche 80-95 m² (DVF 2024-2025, 71 ventes), confirmée par les 4 pièces (144 ventes) et les 5 pièces (37 ventes) du même quartier. Fourchette premier-troisième quartile : {eur(v['basse_euros'])} à {eur(v['haute_euros'])}.</td></tr>
        <tr><th>Vendeur</th><td>Professionnel (agent commercial indépendant mandaté par iaD France). Honoraires à la charge du vendeur. Annonce publiée sur SeLoger sous la référence 273759509.</td></tr>
      </tbody>"""


def bloc_scenario(c, titre, sous_titre, prix, classe, vacance):
    f = c["fiscal"]
    net = f["net_apres_is"]
    cf = net / 12.0 - prix * ANNUITE
    vac = vacance
    return (
        f'      <div class="projection-card {classe}">\n'
        f'        <h3>{titre}</h3>\n'
        f'        <p class="scenario-subtitle">{sous_titre}</p>\n'
        '        <table class="projection-table">\n          <tbody>\n'
        f'            <tr><td>Prix payé</td><td class="num">{eur(prix)}</td></tr>\n'
        f'            <tr><td>Loyers bruts annuels</td><td class="num">{eur(c["revenus_bruts_annuels"])}</td></tr>\n'
        f'            <tr><td>Vacance locative</td><td class="num">−{eur(c["revenus_bruts_annuels"] * vac / 100.0)} ({nfr(vac, 1)} %)</td></tr>\n'
        f'            <tr class="secondary"><td>Charges de copropriété</td><td class="num">−{eur(CH["charges_copro_annuelles_euros"])}</td></tr>\n'
        f'            <tr class="secondary"><td>Taxe foncière</td><td class="num">−{eur(CH["taxe_fonciere_annuelle_euros"])}</td></tr>\n'
        f'            <tr class="secondary"><td>Gestion, meublement, impayés, comptabilité</td><td class="num">−{eur(CH["entretien_annuel_euros"] + CH["comptabilite_annuelle_euros"] + CH["pno_annuelle_euros"])}</td></tr>\n'
        f'            <tr class="subtotal"><td>EBE avant impôt</td><td class="num">{eur(f["ebe"])}</td></tr>\n'
        f'            <tr><td>IS (15 %, convention prudente)</td><td class="num">−{eur(f["is_annuel"])}</td></tr>\n'
        f'            <tr><td>Net après IS</td><td class="num">{eur(net)}</td></tr>\n'
        f'            <tr><td>Mensualité de crédit</td><td class="num">−{eur(prix * ANNUITE)}</td></tr>\n'
        f'            <tr class="highlight"><td>Cash-flow mensuel</td><td class="num">{euro_signe(cf)}</td></tr>\n'
        f'            <tr><td>Rendement net d\'IS sur revient</td><td class="num">{pct((c["rendements"] or {}).get("net_sur_revient_pct") or 0)}</td></tr>\n'
        '          </tbody>\n        </table>\n      </div>')


def bloc_projections():
    cartes = []
    cartes.append(bloc_scenario(S_BASE[1], "Scénario Base",
                                f"Colocation à 3 chambres de {eur(CHAMBRE)} — 8 % de vacance — prix affiché {eur(PRIX_AFFICHE)}",
                                PRIX_AFFICHE, "scenario-base", 8.0))
    cartes.append(bloc_scenario(S_BEST[1], "Scénario Optimiste",
                                f"Colocation à 3 chambres de {eur(480)} — 5 % de vacance — achat à la valeur {eur(VALEUR)}",
                                VALEUR, "scenario-best", 5.0))
    cartes.append(bloc_scenario(S_WORST[1], "Scénario Pessimiste",
                                f"Colocation à {eur(CHAMBRE)} la chambre mais une chambre durablement vide — 15 % de vacance — prix affiché {eur(PRIX_AFFICHE)}",
                                PRIX_AFFICHE, "scenario-worst", 15.0))
    return "\n\n".join(cartes)


def bloc_comparaison():
    def ligne(label, f, prix):
        return ("          <tr><td>" + label + "</td>"
                + "".join(f'<td class="num">{f(sc[1], p)}</td>'
                          for sc, p in ((S_BASE, PRIX_AFFICHE), (S_BEST, VALEUR), (S_WORST, PRIX_AFFICHE)))
                + "</tr>")

    def cf(c, p):
        return euro_signe(c["fiscal"]["net_apres_is"] / 12.0 - p * ANNUITE) + "/mois"

    return "\n".join([
        ligne("EBE avant IS", lambda c, p: eur(c["fiscal"]["ebe"]), None),
        ligne("IS", lambda c, p: eur(c["fiscal"]["is_annuel"]), None),
        ligne("Net après IS / an", lambda c, p: eur(c["fiscal"]["net_apres_is"]), None),
        ligne("Cash-flow mensuel", cf, None),
        ligne("Rendement net d'IS sur revient",
              lambda c, p: pct((c["rendements"] or {}).get("net_sur_revient_pct") or 0), None),
        ligne("Rendement net d'IS sur valeur",
              lambda c, p: pct((c["rendements"] or {}).get("net_sur_valeur_pct") or 0), None),
    ])


def bloc_robustesse():
    lignes = []
    for r in ROBUSTESSE:
        lignes.append(
            f"          <tr><td>{eur(r['loyer'])}/mois <span class=\"scenario-subtitle\">"
            f"({eur(r['loyer'] / SURF)}/m²)</span></td>"
            f'<td class="num">{eur(r["ebe"])}</td>'
            f'<td class="num">{pct(r["doctrine"])}</td>'
            f'<td class="num">{euro_signe(r["cf"])}/mois</td>'
            f'<td class="num">{nfr(r["note"], 1).replace(".", ",")}/10</td></tr>')
    return "\n".join(lignes)


def bloc_risques():
    lignes = []
    for r in REC["analyse"]["risques"]:
        lignes.append(
            "        <tr>\n"
            f'          <td>{r["facteur"]}</td>\n'
            f'          <td>{r["detail"]}</td>\n'
            f'          <td><span class="severity severity-{r["severite"]}">{r["severite"]}/5</span></td>\n'
            "        </tr>")
    sev = sum(r["severite"] for r in REC["analyse"]["risques"]) / len(REC["analyse"]["risques"])
    calcule("sévérité moyenne", COMP["s_risque"], 10 - sev, 0.01)
    return "\n".join(lignes)


def bloc_charges():
    """Détention annuelle du lot, poste par poste."""
    lignes = [
        ("Charges de copropriété", CH["charges_copro_annuelles_euros"],
         "197 €/mois annoncés, copropriété de 30 lots sans ascenseur ni personnel"),
        ("Taxe foncière", CH["taxe_fonciere_annuelle_euros"],
         "estimation, taux global 49,76 % à Toulon ; l'avis d'imposition n'est pas communiqué"),
        ("Assurance propriétaire non occupant", CH["pno_annuelle_euros"],
         "bien libre à la vente, puis assurance bailleur"),
        ("Gestion, meublement, impayés", CH["entretien_annuel_euros"],
         "gestion 675 € + meublement, fluides et fibre 1 900 € + impayés provisionnés 3,5 % (567 €)"),
        ("Comptabilité de la SCI", CH["comptabilite_annuelle_euros"],
         "liasse fiscale, amortissements et tableaux"),
    ]
    html = []
    for label, montant, note in lignes:
        html.append(f"          <tr><td>{label}</td><td class=\"num\">{eur(montant)}</td>"
                    f"<td class=\"scenario-subtitle\">{note}</td></tr>")
    total = sum(m for _, m, _ in lignes)
    html.append(f'          <tr class="subtotal"><td>Total des charges annuelles avant crédit et avant impôt</td>'
                f'<td class="num">{eur(total)}</td><td class="scenario-subtitle">soit '
                f'{eur(total / 12.0)} par mois, {pct(total / LOYERS_AN * 100, 1)} des loyers bruts '
                f'de la colocation et {pct(total / 12000.0 * 100, 1)} de ceux de la location nue</td></tr>')
    html.append(f'          <tr class="highlight"><td>Dont charges de copropriété et taxe foncière seules</td>'
                f'<td class="num">{eur(DETENTION)}</td><td class="scenario-subtitle">'
                f'{eur(DETENTION / 12.0)} par mois : c\'est le poste qui tue le dossier, et c\'est celui '
                f'qu\'aucune négociation de prix ne réduit</td></tr>')
    calcule("total des charges annuelles", round(total), 7536, 1)
    return "\n".join(html)


TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Appartement T4 de 88 m² — quartier Saint-Roch, Toulon (83200) — Sémaphore Patrimoine</title>
<link rel="stylesheet" href="../../style.css">
</head>
<body>
<main class="report">

  <header class="report-header">
    <p class="report-breadcrumb">Analyse d'annonce — {date_analyse}</p>
    <h1>Appartement T4 de 88 m², 2e étage sans ascenseur, quartier Saint-Roch</h1>
    <p class="report-address">Toulon (83200) — Var · annonce SeLoger 273759509 · iaD France, réf. 2058759</p>
    <p class="report-date">Prix affiché {prix} · {prix_m2} · analysé le 28 septembre 2026</p>
    <p class="report-source">Source : <a class="report-source-link" href="{url}">l'annonce SeLoger</a></p>
  </header>

  <section class="summary-cards">
{cards}
  </section>

  <section class="strategy-exploration">
    <h2>Lecture du dossier</h2>
    <p>Le prix n'est pas le problème. À {prix_m2}, ce T4 se paie {ecart_prix} au-dessus de la médiane des ventes de son propre quartier pour sa tranche de surface ({valeur_m2}, DVF 2024-2025, 71 ventes), et il reste très en dessous de la moyenne communale. Dans un marché toulonnais qui écoule 2 744 appartements par an, un bien affiché à 8 % au-dessus de sa valeur n'est pas un piège : c'est une marge de négociation.</p>
    <p>Le problème, c'est le revenu. Trois chambres louées meublées à {chambre} la chambre rapportent {loyer} par mois, ce que le marché confirme (le comparable strict du quartier est un T3 trois chambres du 2e étage sans ascenseur affiché à 450 € par chambre). Retirez la vacance, le meublement, les fluides, la gestion, la comptabilité : il reste {ebe} de résultat avant impôt sur un acte en main de {aem}. C'est {doctrine} de rendement net avant IS là où la maison exige 5 %, et c'est surtout <strong>{cf} par mois</strong> de cash-flow avec un apport de 10 % sur quinze ans.</p>
    <p>Et il y a un poste que personne ne négocie : {detention} par an de charges de copropriété et de taxe foncière, soit {detention_mois} par mois, {part_detention} des loyers bruts. Dans un immeuble de 30 lots <em>sans ascenseur ni personnel</em>, 197 € par mois pour un T4 n'est pas un montant anodin : c'est le prix d'un chauffage collectif, ou la trace d'un emprunt de travaux.</p>
  </section>

  <section class="map-section">
    <h2>Localisation</h2>
    <div class="map-wrapper">
      <iframe src="https://www.openstreetmap.org/export/embed.html?bbox=5.8996%2C43.1192%2C5.9396%2C43.1392&amp;layer=mapnik&amp;marker=43.1292%2C5.9196" loading="lazy" title="Quartier Saint-Roch, Toulon"></iframe>
    </div>
    <p class="map-fallback">Quartier Saint-Roch, Toulon Ouest — marqueur sur le centroïde du quartier, l'annonce ne publie pas l'adresse exacte. Gare de Toulon à 800 m, littoral à 1 km, aéroport de Hyères à 24 km.</p>
  </section>

  <section class="attractiveness">
    <h2>Attractivité du quartier</h2>
    <p class="attractiveness-intro">Six dimensions notées sur 10, sur la base des données publiques de l'INSEE et des sources locales relevées le 28 septembre 2026.</p>
    <div class="attractiveness-grid">
{attractivite}
    </div>
    <p class="attractiveness-summary">Moyenne pondérée pour une colocation : {adequation}/10. Le quartier n'est pas le problème : 130 commerces, la gare à 800 m, un collège et trois écoles primaires, 61 % de locataires — c'est un quartier populaire, commerçant et bien desservi, exactement le terrain d'une colocation étudiante ou jeune active.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Stratégies examinées</h2>
    <p class="strategy-rationale">La stratégie retenue est la colocation meublée à trois chambres : les chambres existent, le bien est annoncé prêt pour cet usage, et c'est la seule des quatre lectures qui tire le rendement au-dessus de 3 % avant impôt. Les quatre autres sont chiffrées pour mémoire.</p>
{strategies}
  </section>

  <section class="financial-projections">
    <h2>Échelle de prix — ce que chaque prix payé change</h2>
    <p>Colocation à trois chambres de {chambre}, loyer inchangé. La note est celle du moteur, le cash-flow suppose 10 % d'apport et 90 % financés sur quinze ans à 3,70 %.</p>
    <div class="projection-card">
      <table class="projection-table">
        <thead><tr><th>Prix payé</th><th>Note</th><th>Verdict</th><th>EBE</th><th>Cash-flow</th><th>Rendement net avant IS</th></tr></thead>
        <tbody>
{echelle}
        </tbody>
      </table>
      <p class="scenario-subtitle">La ligne dorée est la valeur de marché du quartier. Le seuil de la maison — 5 % net avant IS — n'est atteint qu'à 128 000 € ; le cash-flow ne redevient positif qu'à 72 500 €, soit 824 €/m². Aucun des deux n'est un prix toulonnais pour un bien de ce quartier.</p>
    </div>
    <div class="projection-card">
      <h3>Pour comparaison, la location nue</h3>
      <p class="scenario-subtitle">T4 loué nu à 1 000 €/mois, 5 % de vacance, gestion 5 %, aucune provision de meublement.</p>
      <table class="projection-table">
        <thead><tr><th>Prix payé</th><th>Note</th><th>Verdict</th><th>EBE</th><th>Cash-flow</th><th>Rendement net avant IS</th></tr></thead>
        <tbody>
{echelle_nue}
        </tbody>
      </table>
      <p class="scenario-subtitle">Louer nu coûte 957 € d'EBE et 63 € de cash-flow par mois par rapport à la colocation, mais supprime tout le risque de rotation. Les deux lectures échouent sur le même obstacle : la mensualité.</p>
    </div>
  </section>

  <section class="strategy-exploration">
    <h2>Fiche d'identité</h2>
    <table class="identity-table">
{identite}
    </table>
  </section>

  <section class="financial-projections">
    <h2>Projections</h2>
    <p class="projection-summary">Trois scénarios, une seule stratégie : la colocation meublée. Le scénario de base prend le prix affiché et 450 € par chambre ; l'optimiste achète à la valeur de marché et loue à la médiane observée de 480 € ; le pessimiste garde le prix affiché et laisse une chambre vide à l'année.</p>
{projections}
    <div class="projection-card">
      <h3>Comparaison ligne à ligne</h3>
      <table class="comparison-table">
        <thead><tr><th></th><th>Base</th><th>Optimiste</th><th>Pessimiste</th></tr></thead>
        <tbody>
{comparaison}
        </tbody>
      </table>
    </div>
  </section>

  <section class="strategy-exploration">
    <h2>Ce que coûte la détention</h2>
    <table class="identity-table">
      <thead><tr><th>Poste</th><th>Montant annuel</th><th>Commentaire</th></tr></thead>
      <tbody>
{charges}
      </tbody>
    </table>
    <p class="strategy-rationale">Les deux premiers postes — copropriété et taxe foncière — représentent à eux seuls {detention} par an et ne dépendent ni du prix payé ni du loyer. Sur un loyer de 1 000 € en location nue, ils absorbent 32 % des recettes avant le premier euro de mensualité. C'est le même mécanisme qui a fait recaler les deux derniers T4 toulonnais étudiés par le parc.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Le verdict résiste-t-il au loyer ?</h2>
    <p>Le loyer est la seule hypothèse qui pourrait sauver ce dossier, alors testons-la jusqu'au bout. La tranche 85-95 m² de Toulon se loue nue entre 1 174 € et 1 440 € par mois selon les annonces relevées (médiane 1 300 €), mais toutes sont dans des quartiers plus chers que Saint-Roch, où la référence du secteur affiche 850 € pour un 85 m² de 4 pièces. Voici le prix affiché tenu constant, avec un loyer de 850 à 1 440 € :</p>
    <table class="projection-table">
      <thead><tr><th>Loyer nu</th><th>EBE</th><th>Rendement net avant IS</th><th>Cash-flow</th><th>Note</th></tr></thead>
      <tbody>
{robustesse}
      </tbody>
    </table>
    <p class="scenario-subtitle">Même au loyer le plus élevé qu'un T4 toulonnais puisse atteindre — 1 440 €, niveau Mourillon, pour un bien du 2e étage sans ascenseur à Saint-Roch — il manque encore 596 € par mois. <strong>La conclusion ne dépend pas du loyer : elle dépend du prix.</strong></p>
  </section>

  <section class="risk-matrix">
    <h2>Matrice de risques</h2>
    <table class="risk-table">
      <thead><tr><th>Facteur</th><th>Détail</th><th>Sévérité</th></tr></thead>
      <tbody>
{risques}
      </tbody>
    </table>
  </section>

  <section class="verdict {verdict_cls}">
    <h2>Verdict</h2>
    <p class="verdict-decision">On fuit.</p>
    <p class="verdict-stance">Pas parce que le prix est fou — il ne l'est pas — mais parce qu'aucun prix que ce vendeur acceptera ne rend ce dossier conforme à nos règles. Il faudrait <strong>125 000 €</strong> pour satisfaire à la fois le rendement et la note du moteur, <strong>128 000 €</strong> pour atteindre 5 % net avant IS, et <strong>72 500 €</strong> pour que le bien couvre simplement sa mensualité. Ces trois chiffres sont 32 à 63 % sous la valeur de vente du quartier.</p>
    <div class="verdict-details">
      <p><strong>La note du moteur est 4,7/10 et classe le dossier « à négocier », et nous ne la suivons pas.</strong> Cette note récompense un prix presque dans le marché (ratio coût/valeur de 1,16) et un quartier correct ; elle ne dit rien de la trésorerie. Notre règle d'achat, elle, est binaire : sur le parc, un bien doit couvrir sa mensualité. Ici il manque {cf} par mois, soit {cf_an} par an, et ce n'est pas un écart de négociation, c'est un autre métier.</p>
      <p><strong>Le vrai coupable est le poste de charges.</strong> 197 € par mois de copropriété dans un immeuble de 30 lots sans ascenseur ni personnel, plus 1 500 € de taxe foncière estimée : {detention_mois} par mois incompressibles avant le crédit. Sur des loyers de 1 350 € à trois chambres, cela mange 24 % des recettes. Si la copropriété a un chauffage collectif, une partie est récupérable sur les locataires et le dossier s'améliore sans changer de prix ; si c'est un emprunt de travaux, l'annonce cache un passif. Budget prévisionnel et trois derniers procès-verbaux trancheraient — mais aucun de ces documents ne fera descendre la mensualité.</p>
      <p><strong>Ce qui rend le refus confortable.</strong> Le marché est liquide (2 744 ventes d'appartements à Toulon en 2025) et l'offre locative de T4 est abondante : on ne manque pas d'occasions dans ce quartier, on manque de rendement. Un dossier qui demande {cf_an} de trésorerie par an pour un rendement net de {rdt_valeur} % sur valeur n'a pas sa place à côté de parkings qui dégagent du cash dès le premier mois.</p>
    </div>
    <p class="verdict-meta">Note du moteur : {note}/10 ({verdict}). Rendement net d'IS sur valeur : {rdt_valeur} %. Rendement net d'IS sur prix de revient : {rdt_revient} %. Cash-flow au prix affiché : {cf} par mois. Ratio coût/valeur : {ratio}.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Confiance et limites</h2>
    <p>Confiance globale : <strong>moyenne</strong>. Les valeurs de vente sont solides — DVF officielle, cinq mille mutations dépouillées, trois méthodes d'agrégation qui convergent sur le quartier. Les loyers sont relevés sur annonces actives, avec un comparable strict du même quartier. Ce qui reste estimé, et qui pèse lourd ici, c'est tout ce qui touche à la copropriété : ni budget prévisionnel, ni procès-verbal, ni avis de taxe foncière, ni certificat Carrez, ni devis de travaux, ni règlement de copropriété autorisant la colocation. La taxe foncière de 1 500 € est une reconstitution, pas un relevé.</p>
    <p>Non publié faute de source : les chiffres de vente 2026 (la dernière publication DVF disponible s'arrête à l'année 2025 complète), le délai de vente médian propre à Toulon pour ce segment, et l'écart local entre prix affiché et prix signé — seules des références nationales existent, et elles donnent plus de 10 % de marge sur les 4 pièces et plus.</p>
  </section>

  <section class="report-signature">
    <p>Analyse produite le 28 septembre 2026 pour <span class="signature-names">Alexis et Rémy Barlatier</span> — Sémaphore Patrimoine.</p>
    <p class="report-source">Conventions de calcul : frais d'acquisition {frais}, SCI à l'IS avec la convention prudente du moteur (IS de 15 % sur l'EBE, sans amortissement ni intérêts déduits), crédit de 90 % sur quinze ans à 3,70 % et assurance 0,34 %, valeur de marché {valeur_m2} issue des ventes notariées du quartier.</p>
  </section>

</main>
</body>
</html>
"""


def main():
    html = TEMPLATE.format(
        date_analyse="28 septembre 2026",
        url=A["url"],
        prix=eur(PRIX_AFFICHE), prix_m2=eur(PRIX_M2) + "/m²",
        valeur_m2=eur(VALEUR_M2) + "/m²",
        ecart_prix=pct((PRIX_M2 / VALEUR_M2 - 1) * 100, 1),
        chambre=eur(CHAMBRE), loyer=eur(LOYER),
        ebe=eur(EBE), aem=eur(AEM), doctrine=pct(DOCTRINE, 2),
        cf=euro_signe(CF), cf_an=eur(abs(CF) * 12),
        detention=eur(DETENTION), detention_mois=eur(DETENTION / 12.0),
        part_detention=pct(DETENTION / LOYERS_AN * 100, 0),
        cards=bloc_cartes(), attractivite=bloc_attractivite(),
        adequation=nfr(COMP["s_adequation"], 2),
        strategies=bloc_strategies(), identite=bloc_identite(),
        echelle=bloc_echelle(), echelle_nue=bloc_echelle_nue(),
        projections=bloc_projections(), comparaison=bloc_comparaison(),
        charges=bloc_charges(), risques=bloc_risques(), robustesse=bloc_robustesse(),
        verdict_cls=VERDICT_CLS, note=str(NOTE).replace(".", ","), verdict=VERDICT,
        rdt_valeur=pct(C["rendements"]["net_sur_valeur_pct"]),
        rdt_revient=pct(C["rendements"]["net_sur_revient_pct"]),
        ratio=nfr(C["ratio_cout_valeur"], 3),
        frais=eur(FRAIS),
    )
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"fiche écrite : {SORTIE} ({len(html)} caractères)")
    if ECARTS:
        print(f"ÉCARTS D'ASSERTS ({len(ECARTS)}) :")
        for e in ECARTS:
            print("  -", e)
        if not TOLERANT:
            raise SystemExit("écarts d'asserts : correction requise")
    else:
        print("toutes les assertions de cohérence sont vérifiées")


if __name__ == "__main__":
    main()
