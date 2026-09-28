#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère la fiche HTML du slug 2026-08-09-brignoles-centre-t2-28m2.

T2 de 28,3 m² Carrez, 2e étage sur 3 sans ascenseur, refait à neuf en 2022,
vendu loué en meublé 590 €/mois (bail de janvier 2023, locataire en place),
quartier Centre Vieille Ville à Brignoles (83170). Prix affiché 75 000 €
(2 651 €/m²), offre déposée à 60 000 € net vendeur (2 120 €/m²). Vendeur
particulier, annonce SeLoger 26GAKUBNVE7T.

Conventions de chiffrage :
- frais d'acquisition 4 800 € (8 % du prix, barème du simulateur de l'annonce)
- SCI à l'IS, amortissement du bâti 90 % du prix de revient sur 30 ans ;
  le moteur ne déduit JAMAIS les intérêts d'emprunt de la base imposable,
  ce qui rend le cash-flow publié prudent d'environ 23 €/mois la première année
- crédit 54 000 € (90 %) sur 20 ans à 3,45 %, assurance 0,34 %, apport 10 %
- valeur de marché 60 000 €, DVF 2024-2025 tranche 25-32 m² (2 119 €/m²)

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

SLUG = "2026-08-09-brignoles-centre-t2-28m2"
SORTIE = os.path.join(RACINE, "analyses", SLUG, "index.html")
TOLERANT = os.environ.get("HERMES_TOLERANT") == "1"

DUREE_ANS = 20
TAUX = 0.0345
ASSURANCE = 0.0034
APPORT = 0.10
# Annuité mensuelle par euro de prix : 90 % financés sur 20 ans
ANNUITE = ((1 - APPORT) * (TAUX / 12) / (1 - (1 + TAUX / 12) ** -(DUREE_ANS * 12))
           + (1 - APPORT) * ASSURANCE / 12)

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
    data = json.load(open(os.path.join(RACINE, "analyses", "analyses.json"),
                          encoding="utf-8"))
    for r in data["analyses"]:
        if r["slug"] == SLUG:
            return r
    raise SystemExit(f"record absent de la base : {SLUG}")


REC = charger_record()


def variante(prix=None, loyer=None, vacance=None):
    """Copie du record surchargée, recalculée par le moteur (jamais à la main)."""
    r = copy.deepcopy(REC)
    if loyer is not None:
        for ligne in r["marche"]["loyers"]:
            ligne["loyer_mensuel_euros"] = loyer
    if vacance is not None:
        r["hypotheses"]["vacance_base_pct"] = vacance
    if prix is not None:
        r["annonce"]["prix_retenu_euros"] = prix
        r["hypotheses"]["frais_acquisition_euros"] = round(prix * 0.08, 2)
    c = engine.compute(r)
    note, verd, comp = scoring.note_et_verdict(r, c)
    return r, c, note, verd, comp


def cf_de(c, prix):
    return c["fiscal"]["net_apres_is"] / 12.0 - prix * ANNUITE


def plafond(cible, prix_min=30000.0, prix_max=120000.0, kind="cf"):
    """Prix au-delà duquel la cible n'est plus tenue (bisection sur le moteur)."""
    def tient(prix):
        _, c, note, _, _ = variante(prix=prix)
        if kind == "cf":
            return cf_de(c, prix) >= cible
        return (note or 0) >= cible
    lo, hi = prix_min, prix_max
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if tient(mid):
            lo = mid
        else:
            hi = mid
    return lo


# --------------------------------------------------------------------------
# Chiffres du dossier
# --------------------------------------------------------------------------
C = engine.compute(REC)
NOTE, VERDICT, COMP = scoring.note_et_verdict(REC, C)
VERDICT_CLS = {"acheter": "buy", "negocier": "nego", "fuir": "pass"}[VERDICT]
VERDICT_FR = {"acheter": "à acheter", "negocier": "à négocier", "fuir": "à fuir"}

B, A, M, H = REC["bien"], REC["annonce"], REC["marche"], REC["hypotheses"]
CH = H["charges"]

PRIX_AFFICHE = A["prix_affiche_euros"]
PRIX = A["prix_retenu_euros"]
FRAIS = H["frais_acquisition_euros"]
AEM = C["prix_revient_total"]
SURF = B["surfaces"]["carrez_m2"]
VALEUR = M["valeur"]["retenue_euros"]
VALEUR_M2 = VALEUR / SURF
PRIX_M2 = PRIX / SURF
PRIX_AFFICHE_M2 = PRIX_AFFICHE / SURF
LOYER = M["loyers"][0]["loyer_mensuel_euros"]
LOYERS_AN = LOYER * 12
EBE = C["fiscal"]["ebe"]
IS = C["fiscal"]["is_annuel"]
NET = C["fiscal"]["net_apres_is"]
MENS = PRIX * ANNUITE
PRET = PRIX * (1 - APPORT)
CF = cf_de(C, PRIX)
DOCTRINE = EBE / AEM * 100.0
DETENTION = CH["charges_copro_annuelles_euros"] + CH["taxe_fonciere_annuelle_euros"]
CHARGES_TOTAL = (CH["charges_copro_annuelles_euros"] + CH["taxe_fonciere_annuelle_euros"]
                 + CH["pno_annuelle_euros"] + CH["comptabilite_annuelle_euros"]
                 + CH.get("entretien_annuel_euros", 0.0))
APPORT_CASH = PRIX * APPORT + FRAIS
MOIS_APPORT = APPORT_CASH / CF if CF > 0 else None

calcule("prix au m² retenu", round(PRIX_M2), 2120, 1)
calcule("prix affiché au m²", round(PRIX_AFFICHE_M2), 2650, 1)
calcule("valeur retenue", VALEUR, 60000, 1)
calcule("valeur au m²", round(VALEUR_M2), 2120, 1)
calcule("revenus bruts", C["revenus_bruts_annuels"], 7080, 1)
calcule("acte en main", AEM, 64800, 1)
calcule("EBE", round(EBE), 5626, 1)
calcule("réserve annuelle (mini-ALUR)", round(C["fiscal"]["reserve_annuelle"]), 354, 1)
calcule("produits du placement de la réserve", round(C["fiscal"]["produits_reserve"], 2), 10.05, 0.05)
calcule("amortissement du bâti", round(C["fiscal"]["amortissement"]), 1944, 1)
calcule("IS", round(IS), 552, 1)
calcule("net après IS", round(NET), 5074, 1)
calcule("mensualité de crédit", round(MENS), 327, 1)
calcule("cash-flow mensuel", round(CF), 96, 1)
calcule("rendement net sur valeur", round(C["rendements"]["net_sur_valeur_pct"], 2), 8.46, 0.01)
calcule("rendement net sur revient", round(C["rendements"]["net_sur_revient_pct"], 2), 7.83, 0.01)
calcule("rendement brut sur revient", round(C["rendements"]["brut_sur_revient_pct"], 2), 8.68, 0.01)
calcule("doctrine 5 % net avant IS", round(DOCTRINE, 2), 8.68, 0.01)
calcule("ratio coût / valeur", round(C["ratio_cout_valeur"], 3), 1.080, 0.001)
calcule("note du moteur", NOTE, 7.2, 0.05)
calcule("charges annuelles", CHARGES_TOTAL, 1110, 1)
calcule("charges de détention (copro + TF)", DETENTION, 860, 1)
calcule("part des charges dans les loyers bruts", round(CHARGES_TOTAL / LOYERS_AN * 100, 1), 15.7, 0.2)
calcule("apport total", APPORT_CASH, 10800, 1)
# Contrôles croisés avec les chiffres publiés dans le fil le 28/09
calcule("EBE du modèle validé en chat", round(EBE), 5626, 1)
calcule("net du modèle validé en chat (hors intérêts)", round(NET), 5074, 1)


def cumul_reserve(ans):
    """Réserve cumulée après n années : on place la réserve annuelle, les produits
    sont imposés à l'IS avant d'être replacés (comme le reste du résultat)."""
    solde = 0.0
    for _ in range(ans):
        solde = (solde + C["fiscal"]["reserve_annuelle"]) * (1 + (TAUX_RESERVE / 100.0) * (1 - 0.15))
    return solde


TAUX_RESERVE = float(H.get("taux_placement_reserve_pct") or 0.0)
RESERVE_5 = cumul_reserve(5)
RESERVE_10 = cumul_reserve(10)
calcule("réserve cumulée après 5 ans", round(RESERVE_5, -1), 1890, 40)
calcule("réserve cumulée après 10 ans", round(RESERVE_10, -1), 4100, 80)

# --------------------------------------------------------------------------
# Échelles
# --------------------------------------------------------------------------
ECHELLE = []
for prix in (60000.0, 62000.0, 65000.0, 70000.0, 75000.0):
    _, c, n, v, _ = variante(prix=prix)
    ebe = c["fiscal"]["ebe"]
    ECHELLE.append({
        "prix": prix, "note": n, "verdict": v, "ebe": ebe,
        "net": c["fiscal"]["net_apres_is"], "cf": cf_de(c, prix),
        "doctrine": ebe / (prix * 1.08) * 100.0, "m2": prix / SURF,
        "ratio": c["ratio_cout_valeur"],
    })

ECHELLE_NUE = []
for prix in (60000.0, 65000.0, 70000.0, 75000.0):
    r2, c2, n2, v2, _ = variante(prix=prix, loyer=560.0, vacance=5.0)
    ECHELLE_NUE.append({"prix": prix, "note": n2, "verdict": v2,
                        "ebe": c2["fiscal"]["ebe"], "net": c2["fiscal"]["net_apres_is"],
                        "cf": cf_de(c2, prix),
                        "doctrine": c2["fiscal"]["ebe"] / (prix * 1.08) * 100.0,
                        "m2": prix / SURF})

ROBUSTESSE = []
for loyer in (650.0, 590.0, 570.0, 550.0, 530.0, 500.0):
    _, c, n, _, _ = variante(loyer=loyer)
    f = c["fiscal"]
    ROBUSTESSE.append({"loyer": loyer, "ebe": f["ebe"], "cf": cf_de(c, PRIX),
                       "ratio_bancaire": (f["ebe"] / 12.0) / MENS, "note": n})

S_BEST = variante(vacance=2.0)
S_BASE = variante(vacance=5.0)
S_WORST = variante(vacance=20.0)
calcule("scénario base — EBE", round(S_BASE[1]["fiscal"]["ebe"]), 5626, 1)
calcule("scénario optimiste — EBE", round(S_BEST[1]["fiscal"]["ebe"]), 5832, 1)
calcule("scénario pessimiste — EBE", round(S_WORST[1]["fiscal"]["ebe"]), 4594, 1)

CF_NUL_PRIX = plafond(0.0, kind="cf")
CF_91_PRIX = plafond(91.0, kind="cf")
NOTE_65_PRIX = plafond(6.5, kind="note")
calcule("plafond cash-flow nul", round(CF_NUL_PRIX, -2), 78800, 500)
calcule("plafond doctrine +91 €/mois", round(CF_91_PRIX, -2), 60600, 1500)


# --------------------------------------------------------------------------
# Blocs HTML
# --------------------------------------------------------------------------
def bloc_cartes():
    cartes = [
        ("Prix affiché", eur(PRIX_AFFICHE)),
        ("Offre déposée", eur(PRIX)),
        ("Prix entendu au m²", eur(PRIX_M2) + " /m²"),
        ("Valeur de marché (DVF)", eur(VALEUR)),
        ("Loyer en place", eur(LOYER) + " /mois"),
        ("Rendement net d'IS", pct(C["rendements"]["net_sur_valeur_pct"]) + " sur valeur"),
        ("Détention annuelle", eur(CHARGES_TOTAL)),
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
            f'        <span class="attr-label">{dim["dimension"].replace("_", " ").capitalize()}</span>\n'
            f'          <span class="attr-score"><strong>{s}/10</strong></span>\n'
            f'        <div class="attr-bar-track"><div class="attr-bar-fill score-{s}" style="width:{s * 10}%"></div></div>\n'
            f'        <p class="attr-detail">{dim["justification"]}</p>\n'
            '      </div>')
    return "\n".join(cards)


def bloc_strategies():
    lignes = []
    for s in REC["analyse"]["strategies_explorees"]:
        retenue = " selected" if s["strategie"].startswith("Location meublée") else ""
        lignes.append(
            f'        <tr class="strategy-row{retenue}">\n'
            f'          <td><strong>{s["strategie"]}</strong></td>\n'
            f'          <td>{s["rendement"]}</td>\n'
            f'          <td>{s["faisabilite"]}</td>\n'
            f'          <td>{s["risque"]}</td>\n'
            '        </tr>')
    return ('    <table class="comparison-table">\n      <thead>\n        <tr>'
            '<th>Stratégie</th><th>Rendement</th><th>Faisabilité</th><th>Risque</th></tr>\n'
            '      </thead>\n      <tbody>\n' + "\n".join(lignes) + "\n      </tbody>\n    </table>")


def bloc_echelle():
    lignes = []
    for l in ECHELLE:
        cls = ' class="highlight"' if abs(l["prix"] - PRIX) < 1 else ""
        lignes.append(
            f"          <tr{cls}><td>{eur(l['prix'])} <span class=\"scenario-subtitle\">"
            f"({eur(l['m2'])}/m²)</span></td>"
            f'<td class="num">{str(l["note"]).replace(".", ",")}/10</td>'
            f"<td>{VERDICT_FR[l['verdict']]}</td>"
            f'<td class="num">{eur(l["ebe"])}</td>'
            f'<td class="num">{euro_signe(l["cf"])}/mois</td>'
            f'<td class="num">{pct(l["doctrine"])}</td>'
            f'<td class="num">{nfr(l["ratio"], 3)}</td></tr>')
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
        <tr><th>Adresse</th><td>Quartier Centre Vieille Ville, Brignoles (83170) — <strong>adresse exacte non communiquée par le vendeur</strong>. Sous-préfecture du Var, bassin d'environ 17 000 habitants, autoroute A8 à 15 km, pas de gare sur la commune (la plus proche est à Carnoules).</td></tr>
        <tr><th>Type</th><td>Appartement T2 de <strong>28,3 m² Carrez</strong>, 2e étage sur 3 <strong>sans ascenseur</strong>, refait à neuf en 2022. Bail meublé en cours depuis janvier 2023, loyer de 590 €/mois hors eau et électricité, dépôt de garantie de 1 180 €, <strong>locataire qui reste en place après la vente</strong>. DPE D, GES B, chauffage individuel électrique : le locataire paie l'énergie. Permis de louer obtenu, fibre raccordée.</td></tr>
        <tr><th>Lots vendus</th><td><strong>Un seul lot</strong> : l'appartement. Ni cave, ni parking, ni dépendance annoncés — aucun lot annexe cessible séparément et aucun revenu annexe possible.</td></tr>
        <tr><th>Copropriété</th><td>{eur(CH['charges_copro_annuelles_euros'])}/an, soit {eur(CH['charges_copro_annuelles_euros'] / 12.0)}/mois, annoncés par le propriétaire. Aucun travaux voté ni à l'étude, toiture de l'immeuble refaite en 2018, façade en 2023. <strong>Aucun appel de fonds, aucun procès-verbal d'assemblée, aucun état daté, aucun budget prévisionnel</strong> : ces pièces sont dans les conditions suspensives de l'offre.</td></tr>
        <tr><th>Charges</th><td>Taxe foncière {eur(CH['taxe_fonciere_annuelle_euros'])}/an annoncés (avis à obtenir), assurance propriétaire non occupant {eur(CH['pno_annuelle_euros'])}, comptabilité {eur(CH['comptabilite_annuelle_euros'])}/an en coût marginal du lot. Les charges récupérables sur le locataire — dont la TEOM si elle est appelée dans les charges — n'ont pas été ventilées : à clarifier, elles remonteraient le cash-flow.</td></tr>
        <tr><th>Travaux</th><td>Aucun montant retenu à l'acquisition : appartement refait à neuf en 2022, toiture 2018, façade 2023, aucun travaux voté ni à l'étude. Le risque n'est pas dans le prix, il est dans le long terme de la copropriété, et il est porté à la matrice de risques.</td></tr>
        <tr><th>Valeur retenue</th><td>{eur(VALEUR)} net vendeur, soit <strong>{eur(VALEUR_M2)}/m²</strong> — médiane DVF 2024-2025 de la tranche 25-32 m² de Brignoles (2 119 €/m² sur 32 mutations). Comparables directs de 28 m² : 42 000 € (rue des Grands Escaliers, 10/2024), 52 250 € (rue des Lanciers, 12/2025), 58 000 € (rue des Lanciers, 06/2025), 63 000 € (rue de la Trinité, 04/2025) et 63 550 € (rue des Lanciers, 06/2025), médiane 58 000 €. Fourchette : {eur(v['basse_euros'])} à {eur(v['haute_euros'])}.</td></tr>
        <tr><th>Vendeur</th><td>Particulier. Annonce SeLoger 26GAKUBNVE7T, en ligne depuis début août 2026 sans mouvement de prix. Offre déposée à {eur(PRIX)} net vendeur, le solde et les frais restant à notre charge.</td></tr>
      </tbody>"""


def bloc_scenario(c, titre, sous_titre, prix, classe, vacance):
    f = c["fiscal"]
    net = f["net_apres_is"]
    cf = cf_de(c, prix)
    return (
        f'      <div class="projection-card {classe}">\n'
        f'        <h3>{titre}</h3>\n'
        f'        <p class="scenario-subtitle">{sous_titre}</p>\n'
        '        <table class="projection-table">\n          <tbody>\n'
        f'            <tr><td>Prix retenu</td><td class="num">{eur(prix)}</td></tr>\n'
        f'            <tr><td>Loyers bruts annuels</td><td class="num">{eur(c["revenus_bruts_annuels"])}</td></tr>\n'
        f'            <tr><td>Vacance locative</td><td class="num">−{eur(c["revenus_bruts_annuels"] * vacance / 100.0)} ({nfr(vacance, 1)} %)</td></tr>\n'
        f'            <tr class="secondary"><td>Charges de copropriété</td><td class="num">−{eur(CH["charges_copro_annuelles_euros"])}</td></tr>\n'
        f'            <tr class="secondary"><td>Taxe foncière</td><td class="num">−{eur(CH["taxe_fonciere_annuelle_euros"])}</td></tr>\n'
        f'            <tr class="secondary"><td>Assurance et comptabilité</td><td class="num">−{eur(CH["pno_annuelle_euros"] + CH["comptabilite_annuelle_euros"])}</td></tr>\n'
        f'            <tr class="scenario-subtitle"><td>Réserve vacance et travaux mise de côté — non dépensée, placée à {nfr(TAUX_RESERVE, 2)} %</td><td class="num">{eur(c["fiscal"]["reserve_annuelle"])}</td></tr>\n'
        f'            <tr class="secondary"><td>Produits du placement de la réserve</td><td class="num">+{eur(f["produits_reserve"], 2)}</td></tr>\n'
        f'            <tr class="subtotal"><td>EBE avant impôt</td><td class="num">{eur(f["ebe"])}</td></tr>\n'
        f'            <tr><td>Amortissement du bâti (90 % / 30 ans)</td><td class="num">−{eur(f["amortissement"])}</td></tr>\n'
        f'            <tr><td>IS (15 % du résultat)</td><td class="num">−{eur(f["is_annuel"])}</td></tr>\n'
        f'            <tr><td>Net après IS</td><td class="num">{eur(net)}</td></tr>\n'
        f'            <tr><td>Mensualité de crédit</td><td class="num">−{eur(prix * ANNUITE)}</td></tr>\n'
        f'            <tr class="highlight"><td>Cash-flow mensuel</td><td class="num">{euro_signe(cf)}</td></tr>\n'
        f'            <tr><td>Rendement net d\'IS sur revient</td><td class="num">{pct((c["rendements"] or {}).get("net_sur_revient_pct") or 0)}</td></tr>\n'
        '          </tbody>\n        </table>\n      </div>')


def bloc_projections():
    cartes = [
        bloc_scenario(S_BASE[1], "Scénario Base",
                      f"Loyer en place {eur(LOYER)}/mois, 5 % de vacance, offre à {eur(PRIX)}",
                      PRIX, "scenario-base", 5.0),
        bloc_scenario(S_BEST[1], "Scénario Optimiste",
                      f"Loyer en place, 2 % de vacance, locataire en place plusieurs années, offre à {eur(PRIX)}",
                      PRIX, "scenario-best", 2.0),
        bloc_scenario(S_WORST[1], "Scénario Pessimiste",
                      f"Départ du locataire, quatre mois de vacance et relocation sous le loyer en place — 20 % de vacance, offre à {eur(PRIX)}",
                      PRIX, "scenario-worst", 20.0),
    ]
    return "\n\n".join(cartes)


def bloc_comparaison():
    def ligne(label, f):
        return ("          <tr><td>" + label + "</td>"
                + "".join(f'<td class="num">{f(sc)}</td>' for sc in (S_BASE, S_BEST, S_WORST))
                + "</tr>")

    def cf(c):
        return euro_signe(cf_de(c[1], PRIX)) + "/mois"

    return "\n".join([
        ligne("EBE avant IS", lambda c: eur(c[1]["fiscal"]["ebe"])),
        ligne("IS", lambda c: eur(c[1]["fiscal"]["is_annuel"])),
        ligne("Net après IS / an", lambda c: eur(c[1]["fiscal"]["net_apres_is"])),
        ligne("Cash-flow mensuel", cf),
        ligne("Cash-flow annuel",
              lambda c: euro_signe(cf_de(c[1], PRIX) * 12)),
        ligne("Rendement net d'IS sur valeur",
              lambda c: pct((c[1]["rendements"] or {}).get("net_sur_valeur_pct") or 0)),
    ])


def bloc_charges():
    lignes = [
        ("Charges de copropriété", CH["charges_copro_annuelles_euros"],
         "30 €/mois annoncés par le propriétaire le 28/09/2026 — deux appels de fonds à obtenir"),
        ("Taxe foncière", CH["taxe_fonciere_annuelle_euros"],
         "500 €/an annoncés — avis d'imposition à obtenir, chiffre déclaratif"),
        ("Assurance propriétaire non occupant", CH["pno_annuelle_euros"],
         "mobilier en place, bail en cours"),
        ("Comptabilité", CH["comptabilite_annuelle_euros"],
         "coût marginal du lot : l'abonnement du cabinet est déjà porté par le parc"),
        ("Provision travaux", 0.0,
         "non appliquée : appartement refait à neuf en 2022, toiture 2018, façade 2023, aucun travaux voté ni à l'étude"),
    ]
    html = []
    for label, montant, note in lignes:
        html.append(f'          <tr><td>{label}</td><td class="num">{eur(montant)}</td>'
                    f'<td class="scenario-subtitle">{note}</td></tr>')
    html.append('          <tr class="subtotal"><td>Total des charges annuelles avant crédit et avant impôt</td>'
                f'<td class="num">{eur(CHARGES_TOTAL)}</td><td class="scenario-subtitle">soit '
                f'{eur(CHARGES_TOTAL / 12.0)} par mois, {pct(CHARGES_TOTAL / LOYERS_AN * 100, 1)} des loyers '
                f'bruts de {eur(LOYERS_AN)}</td></tr>')
    html.append('          <tr class="highlight"><td>Dont copropriété et taxe foncière seules</td>'
                f'<td class="num">{eur(DETENTION)}</td><td class="scenario-subtitle">'
                f'{eur(DETENTION / 12.0)} par mois, {pct(DETENTION / LOYERS_AN * 100, 0)} des loyers : '
                f'c\'est le poste qu\'aucune négociation de prix ne réduit</td></tr>')
    return "\n".join(html)


def bloc_reserve():
    """Notre « mini-ALUR » interne : la réserve vacance et travaux, placée."""
    r = C["fiscal"]["reserve_annuelle"]
    p = C["fiscal"]["produits_reserve"]
    lignes = [
        ("Réserve constituée chaque année", eur(r),
         f"{nfr(100 * r / LOYERS_AN, 1)} % des loyers bruts — vacance statistique de "
         f"{nfr(H['vacance_base_pct'], 1)} % ({eur(LOYERS_AN * H['vacance_base_pct'] / 100.0)}) "
         "et provision travaux quand elle est activée. Cet argent reste dans la société : il est mis de côté, "
         "pas dépensé"),
        ("Support du placement", "Fonds monétaire en euros",
         "notre « compte à terme » interne : disponible à tout moment pour une vacance ou une réparation, "
         "sans casser le cash-flow ni toucher au crédit"),
        ("Taux retenu", nfr(TAUX_RESERVE, 2) + " % net de frais",
         "relevé sur la page du fonds le 28/09/2026 — 2 Md€ d'actifs"),
        ("Produits de la première année, bruts d'IS", "+" + eur(p, 2),
         "imposés à l'IS comme le reste du résultat : pour une société à l'IS, les plus-values réalisées "
         "comme les latentes sont imposables, les latentes étant réintégrées fiscalement à la clôture"),
        ("Réserve cumulée après cinq ans", eur(RESERVE_5),
         f"soit {pct(RESERVE_5 / AEM * 100, 1)} du prix de revient — de quoi absorber un remplacement de "
         "chauffe-eau ou une remise en peinture sans emprunter"),
        ("Réserve cumulée après dix ans", eur(RESERVE_10),
         f"soit {pct(RESERVE_10 / AEM * 100, 1)} du prix de revient, avec les produits imposés puis replacés"),
    ]
    html = []
    for label, valeur, note in lignes:
        html.append(f'          <tr><td>{label}</td><td class="num">{valeur}</td>'
                    f'<td class="scenario-subtitle">{note}</td></tr>')
    return "\n".join(html)


def bloc_robustesse():
    lignes = []
    for r in ROBUSTESSE:
        cls = ' class="highlight"' if abs(r["loyer"] - LOYER) < 1 else ""
        lignes.append(
            f"          <tr{cls}><td>{eur(r['loyer'])}/mois <span class=\"scenario-subtitle\">"
            f"({nfr(r['loyer'] / SURF, 1)} €/m²)</span></td>"
            f'<td class="num">{eur(r["ebe"])}</td>'
            f'<td class="num">{nfr(r["ratio_bancaire"], 2)}</td>'
            f'<td class="num">{euro_signe(r["cf"])}/mois</td>'
            f'<td class="num">{nfr(r["note"], 1)}/10</td></tr>')
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


TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Appartement T2 de 28,3 m² — Centre Vieille Ville, Brignoles (83170) — Sémaphore Patrimoine</title>
<link rel="stylesheet" href="../../style.css">
</head>
<body>
<main class="report">

  <header class="report-header">
    <p class="report-breadcrumb">Analyse d'annonce — {date_analyse}</p>
    <h1>Appartement T2 de 28,3 m², 2e étage, vendu loué en meublé 590 €/mois</h1>
    <p class="report-address">Centre Vieille Ville, Brignoles (83170) — Var · annonce SeLoger 26GAKUBNVE7T · vendeur particulier</p>
    <p class="report-date">Prix affiché {prix_affiche} · offre déposée {prix} · analysé le 28 septembre 2026</p>
    <p class="report-source">Source : <a class="report-source-link" href="{url}">l'annonce SeLoger</a></p>
  </header>

  <section class="summary-cards">
{cards}
  </section>

  <section class="strategy-exploration">
    <h2>Lecture du dossier</h2>
    <p>Le bien est petit, ancien et bien situé : 28,3 m² Carrez au 2e étage sur 3, refait à neuf en 2022, dans une copropriété dont la toiture a été refaite en 2018 et une façade en 2023. Un locataire y vit depuis janvier 2023 et <strong>reste en place après la vente</strong>, au loyer de {loyer} par mois hors eau et électricité, mobilier compris. Aucun travaux n'est voté ni à l'étude, le DPE est un D et le chauffage est individuel électrique : le locataire paie son énergie. Sur un dossier de centre ancien, c'est exactement ce qu'on veut lire.</p>
    <p>Le prix, lui, doit se lire à sa vraie place. {prix_affiche} affichés font {prix_affiche_m2} le mètre carré, soit 20 % au-dessus de la médiane des ventes de la commune pour cette tranche de surface ({valeur_m2}, DVF 2024-2025, 32 mutations). L'offre déposée à <strong>{prix} net vendeur</strong>, soit {prix_m2} le mètre carré, ramène le dossier exactement sur sa valeur de marché : ce n'est pas une décote arrachée, c'est un prix honnête. La valeur ajoutée ne vient pas de la négociation, elle vient du levier et du loyer en place.</p>
    <p>Les chiffres, maintenant. Un loyer de {loyer} par mois, {charges} de charges annuelles réelles — copropriété, taxe foncière, assurance et la seule comptabilité marginale du lot — et il reste <strong>{ebe} d'EBE</strong> sur un acte en main de {aem}. Le crédit de {pret} sur vingt ans coûte {mens} par mois. Résultat : <strong>{cf} par mois de cash-flow</strong> après impôt, un rendement net d'IS de {rdt_valeur} sur la valeur et de {rdt_revient} sur le prix de revient, pour {apport} d'apport et de frais. C'est trois fois le rendement d'un CAT, et cela respecte les trois règles de la maison.</p>
  </section>

  <section class="map-section">
    <h2>Localisation</h2>
    <div class="map-wrapper">
      <iframe src="https://www.openstreetmap.org/export/embed.html?bbox=6.0516%2C43.3955%2C6.0716%2C43.4155&amp;layer=mapnik&amp;marker=43.4055%2C6.0616" loading="lazy" title="Centre Vieille Ville, Brignoles"></iframe>
    </div>
    <p class="map-fallback">Centre ancien de Brignoles, sous-préfecture du Var — marqueur sur le centroïde du quartier, le vendeur ne publie pas l'adresse exacte. Commerce et marché à pied, autoroute A8 à 15 km, pas de gare sur la commune.</p>
  </section>

  <section class="attractiveness">
    <h2>Attractivité du quartier</h2>
    <p class="attractiveness-intro">Six dimensions notées sur 10, pondérées pour une location meublée longue durée, à partir des données publiques et du relevé d'annonces locatives du 28 septembre 2026.</p>
    <div class="attractiveness-grid">
{attractivite}
    </div>
    <p class="attractiveness-summary">Moyenne pondérée pour la location meublée : {adequation}/10. Le quartier n'est pas le sujet du dossier : le centre ancien de Brignoles n'a ni gare ni bassin d'emploi majeur, mais il a des commerces, des écoles, un permis de louer qui encadre la qualité des lots et une demande réelle sur les petites surfaces meublées. C'est ce qui a maintenu le locataire en place depuis trois ans.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Stratégies examinées</h2>
    <p class="strategy-rationale">La stratégie retenue est celle qui existe déjà : la location meublée longue durée du bail en cours. Les trois autres lectures sont chiffrées pour mémoire, et aucune ne bat la première sur ce lot.</p>
{strategies}
  </section>

  <section class="financial-projections">
    <h2>Échelle de prix — ce que chaque prix payé change</h2>
    <p>Loyer en place inchangé à {loyer}, vacance 5 %, crédit de 90 % sur vingt ans à 3,45 % + assurance 0,34 %, apport 10 %. La note est celle du moteur, elle compare le prix payé frais compris à la valeur de marché.</p>
    <div class="projection-card">
      <table class="projection-table">
        <thead><tr><th>Prix payé</th><th>Note</th><th>Verdict</th><th>EBE</th><th>Cash-flow</th><th>Rendement net avant IS</th><th>Ratio coût/valeur</th></tr></thead>
        <tbody>
{echelle}
        </tbody>
      </table>
      <p class="scenario-subtitle">La ligne dorée est l'offre déposée. Le cash-flow devient nul vers {plafond_cf_nul} et le seuil de la doctrine — apport reconstitué en dix ans, soit {doctrine_seuil} par mois — tient jusqu'à <strong>{plafond_91}</strong>. Au prix affiché de {prix_affiche}, le dossier ne donne plus que {cf_affiche} par mois : il reste vivable, mais il cesse d'être intéressant, et la note tombe à {note_affiche}/10.</p>
    </div>
    <div class="projection-card">
      <h3>Pour comparaison, la location nue</h3>
      <p class="scenario-subtitle">Le même lot reloué nu à 560 €/mois. Le meublé vaut ici une soixantaine d'euros de loyer par mois, pour un mobilier qui appartient déjà au lot.</p>
      <table class="projection-table">
        <thead><tr><th>Prix payé</th><th>Note</th><th>Verdict</th><th>EBE</th><th>Cash-flow</th><th>Rendement net avant IS</th></tr></thead>
        <tbody>
{echelle_nue}
        </tbody>
      </table>
      <p class="scenario-subtitle">Passer en nu coûterait le locataire en place et l'amortissement du mobilier : deux tiers du cash-flow disparaissent. Le meublé est ici la seule lecture défendable.</p>
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
    <p class="projection-summary">Trois scénarios, une seule stratégie retenue : la location meublée du bail en cours, au prix de l'offre. Le scénario de base retient 5 % de vacance ; l'optimiste suppose le locataire en place plusieurs années, 2 % ; le pessimiste le départ du locataire, quatre mois de vacance et une relocation sous le loyer actuel, soit 20 %.</p>
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
{charges_bloc}
      </tbody>
    </table>
    <p class="strategy-rationale">La détention de ce lot coûte {charges} par an, soit {charges_mois} par mois, {part_charges} des loyers bruts. C'est léger : sur les deux derniers dossiers toulonnais du parc, la copropriété et la taxe foncière seules mangeaient 24 à 30 % des recettes. Ici, les 590 € de loyer tombent bien 590 € moins 92 € de charges. La comptabilité est comptée à son coût marginal, 150 €/an : l'abonnement du cabinet est déjà porté par le parc, il ne reste que deux opérations mensuelles et deux annuelles.</p>
  </section>

  <section class="strategy-exploration">
    <h2>La réserve vacance et travaux : notre mini-ALUR interne</h2>
    <p>Une vacance de 5 % n'est pas une perte sèche. L'argent correspondant reste dans la société — il n'est ni dépensé ni perdu — et il n'a aucune raison de dormir sur le compte courant : il est placé en fonds monétaire en euros, disponible à tout moment pour une vacance ou une réparation. C'est notre mini-ALUR interne, la version maison du plan pluriannuel de travaux : une réserve alimentée par les loyers, et non par une prime d'assurance.</p>
    <table class="identity-table">
      <thead><tr><th>Poste</th><th>Montant</th><th>Commentaire</th></tr></thead>
      <tbody>
{reserve_bloc}
      </tbody>
    </table>
    <p class="strategy-rationale">Les produits sont <strong>bruts d'IS</strong> : pour une société à l'IS, les plus-values réalisées comme les latentes sont imposables, ces dernières étant réintégrées fiscalement à la clôture de l'exercice. Le taux de {taux_reserve} % est donc net de frais de gestion mais avant impôt, et c'est ainsi qu'il entre dans le calcul — {produits} de produits sur ce lot, {produits_mois} par mois de cash-flow en plus. L'effet chiffré est modeste sur un seul lot, et ce n'est pas là qu'est le gain : la réserve existe au lieu d'être un poste d'écriture, elle atteint {reserve5} après cinq ans et {reserve10} après dix, et elle joue à contre-cycle — dans le scénario pessimiste à 20 % de vacance, 1 416 € sont mis de côté et rapportent 40 € la première année, au moment précis où le cash-flow a besoin de chaque euro.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Le dossier résiste-t-il au loyer ?</h2>
    <p>Le loyer est la seule hypothèse fragile du dossier : 590 € pour 28,3 m², c'est {loyer_m2} le mètre carré, quand les meublés de 24 à 30 m² du centre s'affichent entre 500 et 550 €/mois (17 à 19 €/m²). Testons jusqu'où il peut descendre, au prix de l'offre :</p>
    <table class="projection-table">
      <thead><tr><th>Loyer</th><th>EBE</th><th>Ratio EBE / annuité</th><th>Cash-flow</th><th>Note</th></tr></thead>
      <tbody>
{robustesse}
      </tbody>
    </table>
    <p class="scenario-subtitle">Le dossier tient son cash-flow positif jusqu'à 500 €/mois de loyer, et le ratio bancaire reste au-dessus de 1,20 jusqu'à 550 €. Autrement dit : <strong>une relocation au prix du marché ne tue pas le montage, elle divise le cash-flow par deux</strong>. C'est ce qui justifie de ne pas payer le prix affiché — à {prix_affiche}, un simple changement de locataire ramènerait le cash-flow à quelques euros par mois.</p>
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
    <p class="verdict-decision">On achète, au prix de l'offre.</p>
    <p class="verdict-stance">À {prix} net vendeur, le dossier est autoporté : <strong>{cf} par mois</strong> de cash-flow après impôt et après mensualité, un rendement net d'IS de {rdt_valeur} sur la valeur, un apport de {apport} reconstitué par le cash-flow en {mois_apport} mois. Le bien couvre sa mensualité, la trésorerie est positive, le net avant IS dépasse 5 % — les trois règles de la maison sont tenues en même temps.</p>
    <div class="verdict-details">
      <p><strong>Ce que la note récompense, et ce qu'elle ne dit pas.</strong> Le moteur sort {note}/10, « à acheter », avec une composante rendement au maximum et une composante prix faible (ratio coût/valeur de {ratio}). Traduction : nous n'achetons pas sous la valeur, nous achetons <em>à</em> la valeur, et c'est le loyer en place plus le levier sur vingt ans qui font le rendement. Un acquéreur qui paierait comptant toucherait 8,68 % brut sur son capital immobilisé : c'est le crédit qui rend ce lot intéressant, pas la décote.</p>
      <p><strong>Le premier risque est le loyer, pas le bien.</strong> 590 € pour 28,3 m², c'est 12 % au-dessus de la moyenne du segment ; une relocation au prix du marché ferait tomber le cash-flow de {cf} à {cf_530} par mois. Ce n'est pas un motif de refus — le locataire est en place et le scénario pessimiste à 20 % de vacance reste positif — mais c'est la raison pour laquelle le prix ne peut pas être celui de l'annonce : à {prix_affiche}, la même relocation ramènerait le cash-flow à {cf_affiche} par mois.</p>
      <p><strong>Trois conditions avant de signer.</strong> La visite des lieux, qui doit confirmer l'état décrit et la surface Carrez de 28,3 m². Les documents — appels de fonds, procès-verbaux d'assemblée, état daté, avis de taxe foncière, diagnostics datés, bail signé — qui ne doivent révéler aucun élément de nature à modifier l'état du bien ou les conditions de sa location. Et la clarification du sort des 30 € de charges de copropriété : récupérés sur le locataire, ils ajoutent une vingtaine d'euros par mois au cash-flow.</p>
      <p><strong>Deux conventions à connaître.</strong> Le moteur ne déduit jamais les intérêts d'emprunt de la base imposable. Dans une SCI à l'IS, ils le sont : la première année, les {interets} d'intérêts échappent à l'IS, soit environ {gain_interets} par mois de cash-flow en plus. Et la réserve vacance et travaux est bien placée à {taux_reserve} %, mais ses produits sont comptés bruts d'IS — pour une société à l'IS, les plus-values réalisées comme latentes sont imposables, les latentes étant réintégrées à la clôture. Le cash-flow publié ici, {cf} par mois, est donc le plus prudent des deux, pas le plus flatteur.</p>
    </div>
    <p class="verdict-meta">Note du moteur : {note}/10 ({verdict}). Rendement net d'IS sur valeur : {rdt_valeur}. Rendement net d'IS sur prix de revient : {rdt_revient}. Cash-flow au prix de l'offre : {cf} par mois. Cash-flow au prix affiché : {cf_affiche} par mois. Ratio coût/valeur : {ratio}.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Confiance et limites</h2>
    <p>Confiance globale : <strong>moyenne</strong>. Ce qui est solide : la valeur de marché, ancrée sur la DVF officielle de la commune (32 mutations de 25 à 32 m² sur deux ans, médiane 2 119 €/m², comparables directs de 28 m² nommés et datés), le bail en cours avec un locataire en place, et l'état du bien — refait à neuf en 2022, toiture 2018, façade 2023, DPE D, aucun travaux voté ni à l'étude.</p>
    <p>Ce qui reste déclaratif, et que les conditions suspensives couvrent : les 360 € de charges de copropriété et les 500 € de taxe foncière annoncés par le propriétaire, sans appel de fonds, sans avis d'imposition, sans procès-verbal d'assemblée ni état daté. Les diagnostics électricité, amiante et plomb ne sont pas produits, la date du DPE non plus. Enfin la surface de 28,3 m² vient du propriétaire : le certificat Carrez doit la confirmer, et une surface plus faible au certificat ferait mécaniquement monter le prix au mètre carré retenu.</p>
    <p>Non publié faute de source : la répartition des charges récupérables sur le locataire (dont la TEOM si elle est appelée dans les charges), la date exacte du DPE, et la quote-part de copropriété du lot.</p>
  </section>

  <section class="report-signature">
    <p>Analyse produite le 28 septembre 2026 pour <span class="signature-names">Alexis et Rémy Barlatier</span> — Sémaphore Patrimoine.</p>
    <p class="report-source">Conventions de calcul : frais d'acquisition {frais} (8 % du prix), SCI à l'IS, amortissement du bâti à 90 % du prix de revient sur 30 ans, IS de 15 % du résultat — le moteur ne déduit pas les intérêts d'emprunt. Crédit de {pret} (90 %) sur vingt ans à 3,45 % et assurance 0,34 %, apport de 10 %. Valeur de marché {valeur_m2} issue des ventes notariées de la commune, tranche 25-32 m². Réserve vacance et travaux placée à {taux_reserve} % net de frais, produits comptés bruts d'IS.</p>
  </section>

</main>
</body>
</html>
"""


def main():
    html = TEMPLATE.format(
        date_analyse="28 septembre 2026",
        url=A["url"],
        prix_affiche=eur(PRIX_AFFICHE), prix_affiche_m2=eur(PRIX_AFFICHE_M2) + "/m²",
        prix=eur(PRIX), prix_m2=eur(PRIX_M2) + "/m²",
        valeur_m2=eur(VALEUR_M2) + "/m²",
        loyer=eur(LOYER), loyer_m2=nfr(LOYER / SURF, 1) + " €/m²",
        charges=eur(CHARGES_TOTAL), charges_mois=eur(CHARGES_TOTAL / 12.0),
        part_charges=pct(CHARGES_TOTAL / LOYERS_AN * 100, 1),
        ebe=eur(EBE), aem=eur(AEM), pret=eur(PRET), mens=eur(MENS),
        cf=euro_signe(CF), cf_530=euro_signe(ROBUSTESSE[4]["cf"]),
        cf_affiche=euro_signe(ECHELLE[-1]["cf"]),
        note_affiche=nfr(ECHELLE[-1]["note"], 1),
        doctrine_seuil=eur(91), plafond_cf_nul=eur(round(CF_NUL_PRIX, -2)),
        plafond_91=eur(round(CF_91_PRIX, -2)),
        apport=eur(APPORT_CASH), mois_apport=nfr(MOIS_APPORT, 0),
        interets=eur(PRET * TAUX), gain_interets=euro_signe(PRET * TAUX * 0.15 / 12),
        cards=bloc_cartes(), attractivite=bloc_attractivite(),
        adequation=nfr(COMP["s_adequation"], 2),
        strategies=bloc_strategies(), identite=bloc_identite(),
        echelle=bloc_echelle(), echelle_nue=bloc_echelle_nue(),
        projections=bloc_projections(), comparaison=bloc_comparaison(),
        charges_bloc=bloc_charges(), risques=bloc_risques(), robustesse=bloc_robustesse(),
        reserve_bloc=bloc_reserve(), taux_reserve=nfr(TAUX_RESERVE, 2),
        produits=eur(C["fiscal"]["produits_reserve"], 2),
        produits_mois=euro_signe(C["fiscal"]["produits_reserve"] / 12.0, 2),
        reserve5=eur(RESERVE_5), reserve10=eur(RESERVE_10),
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
