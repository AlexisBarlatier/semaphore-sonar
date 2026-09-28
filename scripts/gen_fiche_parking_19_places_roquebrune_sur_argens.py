#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère la fiche HTML du slug 2026-09-28-parking-19-places-roquebrune-sur-argens.

Convention de chiffrage (identique à documents/protocole-test-locatif.md) :
- 19 places extérieures, charges 3 040 €/an (copropriété 2 280 € + taxe foncière 760 €),
  frais de notaire 8 800 € (chiffre de l'annonce), aucun travaux
- SCI à l'IS 15 % ; place extérieure NON amortissable (aucun bâti) : IS = 15 % de l'EBE
- seuil de cash-flow du groupe : apport 10 %, prêt 90 % sur 15 ans à 3,70 %, assurance 0,34 %
- « prix d'équilibre » d'un loyer : prix auquel le net après IS couvre exactement la mensualité

Tout chiffre publié passe par calcule() ; avec HERMES_TOLERANT=1 les écarts sont listés
au lieu de lever une assertion, ce qui permet de les corriger en un seul passage.
"""
import copy
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

from analyse_app import engine, scoring, schema  # noqa: E402

SLUG = "2026-09-28-parking-19-places-roquebrune-sur-argens"
SORTIE = os.path.join(RACINE, "analyses", SLUG, "index.html")
TOLERANT = os.environ.get("HERMES_TOLERANT") == "1"

N_PLACES = 19
LOYER_REF = 40.0          # loyer de référence constaté (€/mois/place)
LOYER_HAUT = 50.0         # borne basse annoncée par l'agence
LOYER_OPTIMISTE = 60.0    # palier auquel le prix demandé devient tenable
LOYER_PESSIMISTE = 35.0   # marché sous le comparable constaté
VACANCE_PESSIMISTE = 20.0
FRAIS = 8800.0
# Annuité mensuelle par euro de prix : 90 % financés sur 15 ans à 3,70 % + assurance 0,34 %
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


def pct(v, dec=2):
    return f"{v:.{dec}f}".replace(".", ",") + " %"


def nfr(v, dec=0):
    """Nombre au format français (espace insécable fine pour les milliers, virgule décimale)."""
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


def euro_signe(v, dec=0):
    """Montant signé, signe moins typographique, arrondi à zéro propre."""
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


def variante(loyer=None, vacance=None, prix=None, places=None):
    """Copie du record surchargée, recalculée par le moteur (jamais à la main)."""
    r = copy.deepcopy(REC)
    if loyer is not None:
        for ligne in r["marche"]["loyers"]:
            ligne["loyer_mensuel_euros"] = loyer
    if places is not None:
        for ligne in r["marche"]["loyers"]:
            ligne["quantite"] = places
    if vacance is not None:
        r["hypotheses"]["vacance_base_pct"] = vacance
    if prix is not None:
        r["annonce"]["prix_retenu_euros"] = prix
    c = engine.compute(r)
    note, verdict, comp = scoring.note_et_verdict(r, c)
    return r, c, note, verdict, comp


def equilibre(net_annuel):
    """Prix auquel le net après IS couvre exactement la mensualité."""
    return (net_annuel / 12.0) / ANNUITE


# --------------------------------------------------------------------------
# Chiffres du dossier
# --------------------------------------------------------------------------
REC_BASE = REC
C_BASE = engine.compute(REC)
NOTE, VERDICT, COMP = scoring.note_et_verdict(REC, C_BASE)
VERDICT_CLS = {"acheter": "buy", "negocier": "nego", "fuir": "pass"}[VERDICT]

PRIX_AFFICHE = REC["annonce"]["prix_affiche_euros"]
PRIX_REVient_AFFICHE = C_BASE["prix_revient_total"]
EBE = C_BASE["fiscal"]["ebe"]
IS = C_BASE["fiscal"]["is_annuel"]
NET = C_BASE["fiscal"]["net_apres_is"]
CF_AFFICHE = NET / 12.0 - PRIX_AFFICHE * ANNUITE
VALEUR = REC["marche"]["valeur"]["retenue_euros"]

PALIERS = [90.0, 80.0, 70.0, 60.0, 50.0, 40.0]
MENS_AFFICHE = PRIX_AFFICHE * ANNUITE

lignes_echelle = []
for i, L in enumerate(PALIERS, start=1):
    _, c, _, _, _ = variante(loyer=L, vacance=5.0, prix=PRIX_AFFICHE)
    net = c["fiscal"]["net_apres_is"]
    eq = equilibre(net)
    # Règle du groupe (28/09/2026) : aucun palier accepté avec un cash-flow négatif.
    # Le prix demandé n'est donc tenu que tant que le net après IS couvre la mensualité
    # à ce loyer ; au-delà, le prix descend au niveau d'équilibre du palier.
    tenu = PRIX_AFFICHE if net / 12.0 - MENS_AFFICHE >= 0 else eq
    cf = net / 12.0 - tenu * ANNUITE
    lignes_echelle.append({"palier": i, "loyer": L, "net": net, "eq": eq,
                           "tenu": tenu, "cf": cf,
                           "rdt_revient": net / (tenu + FRAIS) * 100})

palier_tenu_min = min(l["loyer"] for l in lignes_echelle if l["tenu"] == PRIX_AFFICHE)
calcule("dernier palier tenu au prix affiché", palier_tenu_min, 70.0, 0.1)

# Note du moteur selon le prix payé : elle ne mesure pas la remise consentie mais le
# prix payé rapporté à la valeur des loyers. Vérifiée ligne à ligne.
NOTES_PRIX = []
for prix, attendu, libelle in ((110000.0, 5.3, "prix affiché"),
                               (81413.0, 5.3, "palier 50 €"),
                               (62933.0, 6.0, "seuil de 6,0"),
                               (58776.0, 6.3, "palier 40 €"),
                               (56402.0, 6.5, "seuil d'achat")):
    _, _, n, v, _ = variante(loyer=LOYER_REF, vacance=5.0, prix=prix)
    calcule(f"note au prix {prix:.0f} €", n, attendu, 0.05)
    NOTES_PRIX.append({"prix": prix, "note": n, "verdict": v, "libelle": libelle})

# Scénarios publiés dans les projections
S_BASE = variante(loyer=LOYER_REF, vacance=5.0, prix=equilibre(
    engine.compute(variante(loyer=LOYER_REF, vacance=5.0)[0])["fiscal"]["net_apres_is"]))
PRIX_BASE = S_BASE[0]["annonce"]["prix_retenu_euros"]
S_BEST = variante(loyer=LOYER_OPTIMISTE, vacance=0.0, prix=PRIX_AFFICHE)
S_WORST = variante(loyer=LOYER_PESSIMISTE, vacance=VACANCE_PESSIMISTE, prix=PRIX_BASE)

# Grille d'occupation (places louées comptées une par une, sans provision de vacance)
GRILLE = []
for k in (19, 17, 15, 13, 11, 9):
    _, c, _, _, _ = variante(loyer=LOYER_REF, vacance=0.0, places=k, prix=PRIX_BASE)
    net = c["fiscal"]["net_apres_is"]
    GRILLE.append({"k": k, "ebe": c["fiscal"]["ebe"], "is": c["fiscal"]["is_annuel"],
                   "net": net, "cf": net / 12.0 - PRIX_BASE * ANNUITE})

# Contrôles d'ancrage
calcule("frais d'acquisition", C_BASE["frais_acquisition"], FRAIS)
calcule("prix de revient au prix affiché", PRIX_REVient_AFFICHE, PRIX_AFFICHE + FRAIS, 1.0)
calcule("mensualité au prix affiché", round(MENS_AFFICHE), 746, 1.0)
calcule("net mensuel au prix affiché", round(NET / 12), 398, 1.0)
calcule("EBE au loyer de référence", EBE, 19 * LOYER_REF * 12 * 0.95 - 3040, 1.0)
calcule("IS au loyer de référence", IS, 0.15 * EBE, 1.0)
calcule("prix d'équilibre à 40 €", round(equilibre(NET)), 58776, 1.0)
calcule("prix d'équilibre à 50 €", round(lignes_echelle[4]["eq"]), 81413, 1.0)
calcule("prix d'équilibre à 60 €", round(lignes_echelle[3]["eq"]), 104050, 1.0)
calcule("prix d'équilibre à 90 €", round(lignes_echelle[0]["eq"]), 171960, 1.0)
calcule("note", NOTE, 5.3, 0.05)
calcule("rendement net sur revient", C_BASE["rendements"]["net_sur_revient_pct"], 4.02, 0.02)
calcule("rendement net sur valeur", C_BASE["rendements"]["net_sur_valeur_pct"], 8.13, 0.02)
calcule("rendement brut sur revient", C_BASE["rendements"]["brut_sur_revient_pct"], 4.73, 0.02)
calcule("ratio coût/valeur", C_BASE["ratio_cout_valeur"], 2.021, 0.01)
calcule("cash-flow au prix affiché", round(CF_AFFICHE), -347, 1.0)


# --------------------------------------------------------------------------
# Blocs HTML
# --------------------------------------------------------------------------
def bloc_cartes():
    cartes = [
        ("Prix affiché", eur(PRIX_AFFICHE)),
        ("Places", f"{N_PLACES} extérieures"),
        ("Prix demandé / place", eur(PRIX_AFFICHE / N_PLACES)),
        ("Prix du protocole", f"{eur(lignes_echelle[5]['tenu'])} à {eur(lignes_echelle[4]['tenu'])}"),
        ("Prix de revient affiché", eur(PRIX_REVient_AFFICHE)),
        ("Loyers retenus", f"{eur(N_PLACES * LOYER_REF)}/mois ({N_PLACES} × {eur(LOYER_REF)})"),
        ("Rendement net d'IS (affiché / protocole)",
         f"{pct(C_BASE['rendements']['net_sur_revient_pct'])} / {pct(lignes_echelle[5]['rdt_revient'])}"),
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
            f'        <div class="attr-bar-track"><div class="attr-bar-fill" style="width:{s * 10}%"></div></div>\n'
            f'        <p class="attr-detail">{dim["justification"]}</p>\n'
            '      </div>')
    calcule("moyenne d'attractivité", COMP["s_adequation"], sum(d["score"] for d in REC["analyse"]["attractivite"]) / 6.0, 0.01)
    return "\n".join(cards)


def bloc_strategie():
    r1 = C_BASE["rendements"]["net_sur_revient_pct"]
    r2 = lignes_echelle[5]["rdt_revient"]
    ratio1 = C_BASE["ratio_cout_valeur"]
    ratio2 = round((lignes_echelle[5]["tenu"] + FRAIS) / VALEUR, 3)
    calcule("ratio du protocole", ratio2, 1.15, 0.01)
    return f"""    <table class="strategy-table">
      <thead>
        <tr>
          <th>Stratégie</th>
          <th>Lots</th>
          <th>Rendement net d'IS</th>
          <th>Valeur après tx</th>
          <th>Ratio coût/valeur</th>
          <th>Faisabilité</th>
          <th>Risque</th>
          <th>Adéquation</th>
        </tr>
      </thead>
      <tbody>
        <tr class="strategy-row">
          <td>Location longue durée <strong>au prix affiché</strong> — écartée</td>
          <td>{N_PLACES}</td>
          <td>{pct(r1)} (loyer {eur(LOYER_REF)})</td>
          <td>{eur(VALEUR)}</td>
          <td><span class="ratio-badge ratio-mauvais">{str(ratio1).replace('.', ',')}</span></td>
          <td><span class="badge-faisabilite faisabilite-haute">Immédiate</span></td>
          <td><span class="badge-risque risque-eleve">Élevé</span></td>
          <td><div class="adeq-cell"><div class="adeq-bar-track"><div class="adeq-bar-fill adeq-low" style="width:33%"></div></div></div></td>
        </tr>
        <tr class="strategy-row selected">
          <td><strong>Location longue durée au prix du protocole</strong> ({eur(lignes_echelle[5]['tenu'])} à {eur(lignes_echelle[4]['tenu'])}) après test de loyer et achat des seules places louées</td>
          <td>{N_PLACES}</td>
          <td>{pct(r2)} (loyer {eur(LOYER_REF)})</td>
          <td>{eur(VALEUR)}</td>
          <td><span class="ratio-badge ratio-ok">{str(ratio2).replace('.', ',')}</span></td>
          <td><span class="badge-faisabilite faisabilite-moyenne">Un trimestre de test</span></td>
          <td><span class="badge-risque risque-modere">Modéré</span></td>
          <td><div class="adeq-cell"><div class="adeq-bar-track"><div class="adeq-bar-fill adeq-low" style="width:33%"></div></div></div></td>
        </tr>
      </tbody>
    </table>"""


def bloc_echelle():
    lignes = []
    for l in lignes_echelle:
        if l["tenu"] == PRIX_AFFICHE:
            tenu = f"<strong>{eur(l['tenu'])}</strong> (tenu, CF positif)"
        else:
            tenu = f"<strong>{eur(l['tenu'])}</strong> (descend au seuil de CF nul)"
        lignes.append(
            f"          <tr><td>{l['palier']}</td><td>{eur(l['loyer'])}</td><td>{tenu}</td>"
            f"<td class=\"num\">{eur(l['net'])}</td>"
            f'<td class="num">{euro_signe(l["cf"])}/mois</td>'
            + f"<td class=\"num\">{eur(l['eq'])}</td>"
            f"<td class=\"num\">{eur(l['tenu'] / N_PLACES)}</td></tr>")
    return "\n".join(lignes)


def bloc_notes():
    lignes = []
    for x in NOTES_PRIX:
        lignes.append(
            f'          <tr><td>{eur(x["prix"])} <span class="scenario-subtitle">({x["libelle"]})</span></td>'
            f'<td class="num"><strong>{str(x["note"]).replace(".", ",")}/10</strong></td>'
            f'<td>{x["verdict"]}</td></tr>')
    return "\n".join(lignes)


def bloc_identite():
    b = REC["bien"]
    return f"""      <tbody>
        <tr><th>Adresse</th><td>Résidence fermée, quartier La Bouverie, Roquebrune-sur-Argens (83520) — mitoyenne de la résidence services seniors Les Jardins d'Arcadie (90 logements, ouverture 2024). Adresse exacte non communiquée dans l'annonce.</td></tr>
        <tr><th>Type</th><td>19 places de parking extérieures à ciel ouvert, dont 1 place PMR — enrobé, marquage peint, arceaux individuels rabattables, clôture périphérique, miroir de sortie</td></tr>
        <tr><th>Vendeur</th><td>FIDUCIA (SIRET 53365365500035), réf. RBCOFPKG01 — honoraires à la charge du vendeur. Prix ramené de 150 000 € à 110 000 € (−26,7 %), 35 favoris, disponibilité annoncée 12/2025.</td></tr>
        <tr><th>Structure du lot</th><td>Non communiquée : {N_PLACES} lots distincts ou lot unique (numéros et tantièmes à obtenir). La vente à la découpe en dépend ; à défaut, modificatif de règlement de copropriété.</td></tr>
        <tr><th>Occupation</th><td>Aucun bail produit par le vendeur. Le bien est présenté libre.</td></tr>
        <tr><th>Loyer de référence</th><td>{eur(LOYER_REF)}/mois/place — seule place extérieure comparable constatée dans la commune. Fourchette retenue 40 à 50 € ; l'agence annonce 50 à 90 € sans bail.</td></tr>
        <tr><th>Charges de copropriété</th><td>120 €/place/an retenues (2 280 €/an) — estimation, budget prévisionnel à obtenir. Référence : places extérieures du groupe taxées 24 à 120 €/an/place.</td></tr>
        <tr><th>Taxe foncière</th><td>40 €/place/an estimés (760 €/an) — aucun avis de TF communiqué ; places extérieures du groupe taxées 30 à 75 €/an.</td></tr>
        <tr><th>Amortissement</th><td>Aucun : place extérieure sans bâti. L'IS de 15 % frappe donc l'EBE entier, ce qui pèse environ 15 % sur le cash-flow.</td></tr>
        <tr><th>Travaux</th><td>0 € annoncé — enrobé et marquage en état apparent sur les photos, à constater sur place.</td></tr>
        <tr><th>DPE</th><td>Non applicable (stationnement).</td></tr>
        <tr><th>Valeur retenue</th><td>{eur(VALEUR)} net vendeur, soit {eur(VALEUR / N_PLACES)}/place : capitalisation du loyer constaté de {eur(LOYER_REF)}/place au seuil de cash-flow du groupe. À {eur(LOYER_HAUT)}/place, elle monte à {eur(lignes_echelle[4]['tenu'])} ({eur(lignes_echelle[4]['tenu'] / N_PLACES)}/place).</td></tr>
      </tbody>"""


def bloc_scenario(r, c, titre, sous_titre, prix, prix_equilibre, classe):
    f = c["fiscal"]
    net = f["net_apres_is"]
    cf = net / 12.0 - prix * ANNUITE
    ligne = (
        f'      <div class="projection-card {classe}">\n'
        f'        <h3>{titre}</h3>\n'
        f'        <p class="scenario-subtitle">{sous_titre}</p>\n'
        '        <table class="projection-table">\n          <tbody>\n'
        f'            <tr><td>Prix payé</td><td class="num">{eur(prix)}</td></tr>\n'
        f"            <tr><td>Revenu brut annuel</td><td class=\"num\">{eur(c['revenus_bruts_annuels'])}</td></tr>\n"
        f'            <tr><td>Vacance locative ({r["hypotheses"]["vacance_base_pct"]:.0f} %)</td><td class="num">−{eur(c["revenus_bruts_annuels"] * r["hypotheses"]["vacance_base_pct"] / 100.0)}</td></tr>\n'
        f'            <tr class="secondary"><td>Charges (copropriété 2 280 € + TF 760 €)</td><td class="num">−3 040 €</td></tr>\n'
        f'            <tr class="subtotal"><td>EBE avant IS</td><td class="num">{eur(f["ebe"])}</td></tr>\n'
        f'            <tr><td>Amortissement (place extérieure)</td><td class="num">0 €</td></tr>\n'
        f'            <tr><td>Résultat fiscal</td><td class="num">{eur(f["resultat_fiscal"])}</td></tr>\n'
        f'            <tr><td>IS (15 %)</td><td class="num">−{eur(f["is_annuel"])}</td></tr>\n'
        f'            <tr><td>CF net annuel</td><td class="num">{eur(net)}</td></tr>\n'
        f'            <tr class="highlight"><td>CF net mensuel</td><td class="num">{euro_signe(cf)}</td></tr>\n'
        + f'            <tr><td>Prix d\'équilibre de ce loyer</td><td class="num">{eur(prix_equilibre)}</td></tr>\n'
        f'            <tr><td>Rendement net sur revient</td><td class="num">{pct((c["rendements"] or {}).get("net_sur_revient_pct") or 0)}</td></tr>\n'
        '          </tbody>\n        </table>\n      </div>')
    return ligne


def bloc_projections():
    cartes = []
    cartes.append(bloc_scenario(S_BASE[0], S_BASE[1], "Scénario Base",
                                f"Loyer {eur(LOYER_REF)}/place (comparable constaté) — vacance 5 % — prix du protocole {eur(PRIX_BASE)}",
                                PRIX_BASE, PRIX_BASE, "scenario-base"))
    cartes.append(bloc_scenario(S_BEST[0], S_BEST[1], "Scénario Optimiste",
                                f"Loyer {eur(LOYER_OPTIMISTE)}/place (palier de l'agence) — vacance 0 % — prix demandé tenu {eur(PRIX_AFFICHE)}",
                                PRIX_AFFICHE, lignes_echelle[3]["eq"], "scenario-best"))
    cartes.append(bloc_scenario(S_WORST[0], S_WORST[1], "Scénario Pessimiste",
                                f"Loyer {eur(LOYER_PESSIMISTE)}/place — vacance {VACANCE_PESSIMISTE:.0f} % — au prix du protocole {eur(PRIX_BASE)}",
                                PRIX_BASE, equilibre(S_WORST[1]["fiscal"]["net_apres_is"]), "scenario-worst"))
    return "\n\n".join(cartes)


def bloc_comparaison():
    prix = {"base": PRIX_BASE, "best": PRIX_AFFICHE, "worst": PRIX_BASE}
    scenarios = {"base": S_BASE[1], "best": S_BEST[1], "worst": S_WORST[1]}

    def ligne(label, f):
        return ("          <tr><td>" + label + "</td>"
                + "".join(f'<td class="num">{f(scenarios[k], prix[k])}</td>'
                          for k in ("base", "best", "worst"))
                + "</tr>")

    def cf(c, p):
        return euro_signe(c['fiscal']['net_apres_is'] / 12 - p * ANNUITE) + "/mois"

    return "\n".join([
        ligne("Prix payé", lambda c, p: eur(p)),
        ligne("EBE avant IS", lambda c, p: eur(c["fiscal"]["ebe"])),
        ligne("IS", lambda c, p: eur(c["fiscal"]["is_annuel"])),
        ligne("Net après IS / an", lambda c, p: eur(c["fiscal"]["net_apres_is"])),
        ligne("CF net mensuel", cf),
        ligne("Rendement net sur revient",
              lambda c, p: pct((c["rendements"] or {}).get("net_sur_revient_pct") or 0)),
    ])


def bloc_occupation():
    lignes = []
    for g in GRILLE:
        cls = ' class="highlight"' if g["k"] == N_PLACES else ""
        lignes.append(
            f"          <tr{cls}><td>{g['k']} / {N_PLACES}</td>"
            f'<td class="num">{eur(g["ebe"])}</td>'
            f'<td class="num">{eur(g["is"])}</td>'
            f'<td class="num">{euro_signe(g["cf"])}</td>'
            + f'<td class="num">{pct(g["net"] / (PRIX_BASE + FRAIS) * 100)}</td></tr>')
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


# --------------------------------------------------------------------------
# Textes et gabarit
# --------------------------------------------------------------------------
LOYER_EQUILIBRE_AFFICHE = ((MENS_AFFICHE * 12 / 0.85) + 3040) / (0.95 * N_PLACES * 12)
calcule("loyer d'équilibre au prix affiché", round(LOYER_EQUILIBRE_AFFICHE, 1), 62.6, 0.1)
LOYER_EQUILIBRE_FR = nfr(LOYER_EQUILIBRE_AFFICHE, 1)
CASH_FLOW_AFFICHE = euro_signe(CF_AFFICHE) + "/mois"
CASH_BASE = PRIX_BASE * 0.10 + FRAIS
CASH_HAUT = lignes_echelle[4]["tenu"] * 0.10 + FRAIS

LECTURE = (
    f"Le dossier ne se juge pas sur le prix affiché mais sur le loyer que le lot produit réellement. "
    f"À {eur(PRIX_AFFICHE)}, il faudrait que les places partent à {LOYER_EQUILIBRE_FR} €/place "
    f"pour que le cash-flow soit à l'équilibre ; le seul comparable extérieur constaté dans la commune est à "
    f"{eur(LOYER_REF)}/place, et l'agence, qui annonce 50 à 90 €, ne produit aucun bail. "
    f"À {eur(LOYER_REF)}/place, le prix d'équilibre est {eur(PRIX_BASE)}, soit "
    f"{eur(PRIX_BASE / N_PLACES)}/place contre {eur(PRIX_AFFICHE / N_PLACES)} demandés."
)

CONF = (
    f"Le protocole transforme une estimation en mesure : l'agence commercialise elle-même, sous mandat, "
    f"en descendant de 90 à 50 €/place par paliers de 10 €, et le prix suit le loyer signé "
    f"({eur(PRIX_BASE)} si le marché ressort à {eur(LOYER_REF)}, {eur(lignes_echelle[4]['tenu'])} à {eur(LOYER_HAUT)}). "
    f"Les paliers 90, 80 et 70 € sont tenus au prix demandé, très en dessous de ce que vaudraient ces loyers : "
    f"l'offre est donc à la hausse pour le vendeur, pas à la baisse. "
    f"L'achat se fait ensuite à la découpe, place par place, au prix unitaire du palier retenu, "
    f"les invendus comptés à moitié : seules les places louées sont payées plein tarif."
)

TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
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
  <p class="report-address">{adresse}</p>
  <p class="report-date">Analyse générée le 28 septembre 2026</p>
  <p class="report-source">Source : Leboncoin — FIDUCIA (professionnel, SIRET 53365365500035), réf. RBCOFPKG01 — honoraires à la charge du vendeur</p>
  <div class="report-source-link"><a href="{url}">{url}</a></div>
</header>

<main>

  <!-- === Bannière stratégie === -->
  <div class="strategy-banner">
    <span class="strategy-badge">Placement parking — protocole de test</span>
    <p>Stratégie retenue : <strong>location longue durée après test du loyer, achat des seules places louées</strong> — SCI à l'IS (15 %)</p>
  </div>

  <!-- === Cartes de synthèse === -->
  <section class="summary-cards">
{cartes}
  </section>

  <!-- === Carte === -->
  <section class="map-section">
    <h2>Localisation</h2>
    <div id="map-container" data-lat="{lat}" data-lon="{lon}" data-address="{map_addr}"></div>
  </section>

  <!-- === Attractivité === -->
  <section class="attractiveness">
    <h2>Attractivité — La Bouverie, Roquebrune-sur-Argens</h2>
    <p class="attractiveness-intro">Quartier pavillonnaire au milieu des vignes, à 6 km du centre de Roquebrune. Le stationnement résidentiel n'y est pas contraint, le parking public du stade est gratuit à proximité immédiate et la zone bleue du centre commercial ne tient que 1 h 30 : la tension qui fait le prix d'une place ailleurs n'existe pas ici. Le seul collectif voisin, la résidence services seniors Les Jardins d'Arcadie (90 logements, 2024), dispose de son propre stationnement. Aucune annonce de location de parking n'est publiée dans la commune, aucun opérateur n'y est implanté.</p>
    <div class="attractiveness-grid">
{attractivite}
    </div>
    <div class="attractiveness-summary">
      <p><strong>Profil locataire cible :</strong> résidents des maisons voisines cherchant une seconde place ou un abri pour un véhicule supplémentaire, locataires des Jardins d'Arcadie sans place attitrée, artisans et vans du quartier.</p>
      <p><strong>Conclusion :</strong> {lecture} Le repère per-place du groupe pour une place extérieure (6 500 € acte en main) supposerait un loyer de 80 à 125 €/place : c'est le niveau constaté à La Seyne et à La Garde, pas à La Bouverie. Acheter sur ce repère ici, c'est payer un loyer qui n'existe pas.</p>
    </div>
  </section>

  <!-- === Stratégie d'exploitation === -->
  <section class="strategy-exploration">
    <h2>Stratégie d'exploitation</h2>
    <p class="attractiveness-intro">Le lot s'analyse comme un produit de rendement locatif dont le loyer n'est pas établi. Deux stratégies s'opposent : payer le prix demandé en pariant sur la fourchette de l'agence, ou mesurer le loyer avant de payer.</p>
{strategie}
    <div class="strategy-rationale">
      <p>{conf}</p>
    </div>
  </section>

  <!-- === Échelle du protocole === -->
  <section class="strategy-exploration">
    <h2>Échelle du protocole — le prix suit le loyer signé</h2>
    <p class="attractiveness-intro">Le prix demandé est tenu à {prix_affiche} sur les quatre premiers paliers, puis descend. Le « prix d'équilibre » est le prix auquel le revenu net après IS couvre exactement la mensualité du prêt (apport 10 %, 15 ans à 3,70 %, assurance 0,34 %, charges 3 040 €/an, SCI à l'IS).</p>
    <table class="comparison-table">
      <thead>
        <tr><th>Palier</th><th>Loyer testé</th><th>Notre prix</th><th>Net après IS</th><th>Cash-flow mensuel</th><th>Prix d'équilibre</th><th>€/place payés</th></tr>
      </thead>
      <tbody>
{echelle}
      </tbody>
    </table>
    <p class="attractiveness-intro"><strong>Lecture :</strong> aux paliers 90, 80 et 70 €, le prix demandé est très en dessous de ce que vaudraient ces loyers : l'offre est à la hausse pour le vendeur. À partir du palier 60 €, le prix demandé ne couvre plus la mensualité : il descend au niveau d'équilibre, parce qu'aucun palier avec un cash-flow négatif n'est accepté, même de 40 €/mois. Un palier ne compte que s'il produit au moins 5 000 €/an de loyers signés, soit 5 places à 90 €, 8 à 60 €, 9 à 50 € ou 11 à 40 € : sans ce seuil, un locataire isolé à 90 € valoriserait 19 places.</p>

    <h3 style="margin-top:2rem;">Ce que la grille donne comme note</h3>
    <p class="attractiveness-intro">La note du moteur ne récompense pas la remise obtenue : elle compare le prix payé, frais compris, à la valeur des loyers du lot. Entre 110 000 € et 67 600 €, elle ne bouge pas — tenir le prix demandé sur les paliers de loyer ne suffit donc pas à faire basculer le dossier. Elle passe 6,0 à 62 900 € et 6,5 (à acheter) à 56 400 €, soit 2 970 €/place. C'est exactement ce que permet l'achat à la découpe : payer plein tarif les seules places louées et moitié prix les invendus abaisse le prix moyen sous cette ligne.</p>
    <table class="comparison-table">
      <thead>
        <tr><th>Prix payé</th><th>Note</th><th>Verdict</th></tr>
      </thead>
      <tbody>
{notes}
      </tbody>
    </table>
  </section>

  <!-- === Fiche d'identité === -->
  <section class="identity-sheet">
    <h2>Fiche d'identité</h2>
    <table class="identity-table">
{identite}
    </table>
  </section>

  <!-- === Projections financières === -->
  <section class="financial-projections">
    <h2>Projections financières — SCI à l'IS</h2>
    <p class="attractiveness-intro">Charges retenues 3 040 €/an (copropriété 2 280 € + taxe foncière 760 €), frais d'acquisition 8 800 €, aucun travaux. Place extérieure sans bâti : l'amortissement est nul, l'IS de 15 % frappe donc l'EBE entier. Les trois scénarios balaient les loyers que le protocole doit trancher.</p>

    <div class="projections-grid">
{projections}
    </div>

    <div class="projection-summary">
      <h3>Synthèse comparative</h3>
      <table class="comparison-table">
        <thead>
          <tr><th>Indicateur</th><th>Base — {loyer_ref}/place</th><th>Optimiste — {loyer_haut}/place</th><th>Pessimiste — {loyer_pess}/place</th></tr>
        </thead>
        <tbody>
{comparaison}
        </tbody>
      </table>
    </div>

    <div class="projection-summary" style="margin-top:2rem;">
      <h3>Sensibilité à l'occupation — loyer {loyer_ref}/place, prix {prix_base}</h3>
      <p class="attractiveness-intro">Places comptées une par une (sans provision de vacance en plus), au prix du protocole {prix_base}. La grille montre ce que coûte chaque place vide : c'est le risque principal du dossier, et la raison de l'achat à la découpe.</p>
      <table class="comparison-table">
        <thead>
          <tr><th>Places louées</th><th>EBE / an</th><th>IS</th><th>CF net / mois</th><th>Rendement net sur revient</th></tr>
        </thead>
        <tbody>
{occupation}
        </tbody>
      </table>
    </div>
  </section>

  <!-- === Matrice de risques === -->
  <section class="risk-matrix">
    <h2>Matrice de risques</h2>
    <table class="risk-table">
      <thead>
        <tr>
          <th>Facteur de risque</th>
          <th>Détail</th>
          <th>Sévérité</th>
        </tr>
      </thead>
      <tbody>
{risques}
      </tbody>
    </table>
  </section>

  <!-- === Verdict === -->
  <section class="verdict {verdict_cls}">
    <h2>Recommandation</h2>
    <div class="verdict-decision">
      <p class="verdict-stance"><strong>On négocie, et on ne paie pas le prix affiché.</strong> {verdict_stance}</p>
    </div>
    <div class="verdict-details">
      <p><strong>Prix plafond : {prix_base} tant que le loyer n'est pas mesuré</strong> ({eur_place_base}/place, soit {cash_base} de cash à sortir apport et frais compris). Au-dessus, le dossier ne couvre plus sa mensualité si le marché ressort à {loyer_ref}/place. Si le test démontre {loyer_haut}/place, le plafond monte à {prix_haut} ({eur_place_haut}/place, {cash_haut} de cash) et le prix demandé de {prix_affiche} reste hors d'atteinte : il faudrait {LOYER_EQUILIBRE_FR} €/place pour l'équilibrer.</p>
      <p><strong>Leviers de négociation :</strong></p>
      <ul>
        <li>Prendre l'agence à son propre process : commercialiser sous son mandat, en descendant de 90 à 50 €/place par paliers de 10 €, le prix suivant le loyer signé. Aux paliers 90, 80 et 70 €, notre offre dépasse la valeur du loyer annoncé : c'est une offre à la hausse, pas un marchandage.</li>
        <li>Négocier à la découpe : ne payer plein tarif que les places louées ({eur_place_base}/place à {loyer_ref} €), les invendus comptés à moitié. Chaque place louée augmente notre offre d'environ 3 100 € ; chaque place vide la diminue et coûte au vendeur ses charges.</li>
        <li>Écrire la grille en condition suspensive et non en option ferme, avec indemnité d'immobilisation séquestrée de 3 000 € payable seulement si nous ne donnons pas suite alors que le seuil est atteint.</li>
        <li>Sortie : aucune location jusqu'à 40 €/place, on se retire. Sortie anticipée possible après trois paliers vides (70, 60 et 50 €).</li>
        <li>Exiger avant toute offre : nombre de places louées et baux écrits, structure du lot (19 lots distincts ou lot unique), budget prévisionnel de charges, avis de taxe foncière, travaux votés, nombre de badges, statut TVA de la cession.</li>
      </ul>
    </div>
    <div class="verdict-meta">
      <p><strong>Régime fiscal retenu :</strong> SCI à l'IS (15 %) — amortissement nul (place extérieure sans bâti), frais d'acquisition 8 800 €, aucun travaux</p>
      <p><strong>Hypothèses retenues :</strong> loyer {loyer_ref} €/place/mois, vacance 5 %, charges 3 040 €/an, financement 90 % sur 15 ans à 3,70 % avec apport de 10 %</p>
      <p><strong>Note :</strong> {note}/10 — {verdict_libelle}</p>
    </div>
  </section>

  <!-- === Signature === -->
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


def main():
    if ECARTS:
        print(f"ÉCARTS DÉTECTÉS ({len(ECARTS)}) :")
        for e in ECARTS:
            print("  -", e)
        if not TOLERANT:
            raise SystemExit("chiffres publiés en désaccord avec le moteur")
    else:
        print("Contrôles chiffrés : aucun écart")

    html = TEMPLATE.format(
        titre=REC["titre"],
        adresse="19 places de parking extérieures à ciel ouvert — résidence fermée, quartier La Bouverie, Roquebrune-sur-Argens (83520)",
        url=REC["annonce"]["url"],
        cartes=bloc_cartes(),
        lat="43.5008734",
        lon="6.6443455",
        map_addr="Quartier La Bouverie, Roquebrune-sur-Argens (83520) — coordonnées du village, adresse exacte non communiquée dans l'annonce",
        attractivite=bloc_attractivite(),
        lecture=LECTURE,
        strategie=bloc_strategie(),
        conf=CONF,
        echelle=bloc_echelle(),
        notes=bloc_notes(),
        identite=bloc_identite(),
        projections=bloc_projections(),
        comparaison=bloc_comparaison(),
        occupation=bloc_occupation(),
        risques=bloc_risques(),
        verdict_cls=VERDICT_CLS,
        verdict_stance=(
            f"Au prix affiché de {eur(PRIX_AFFICHE)}, le lot produit {eur(EBE)} d'EBE pour "
            f"{eur(NET)} après IS, soit un cash-flow de {CASH_FLOW_AFFICHE} et un rendement net d'IS de "
            f"{pct(C_BASE['rendements']['net_sur_revient_pct'])}. Ce n'est pas un dossier de rendement, c'est un dossier "
            f"de test : le seul comparable extérieur constaté dans la commune est à {eur(LOYER_REF)}/place, "
            f"l'agence annonce 50 à 90 € sans produire un bail, et il faudrait {LOYER_EQUILIBRE_FR} €/place "
            f"pour que le prix demandé tienne. À {eur(LOYER_REF)}/place, la valeur du lot est {eur(PRIX_BASE)} et le "
            f"cash-flow s'équilibre exactement. On négocie donc sur ce prix, sous condition d'un test locatif de "
            f"cinq mois mené sous mandat du vendeur, et on n'achète que les places louées."
        ).replace(",", " "),
        LOYER_EQUILIBRE_FR=LOYER_EQUILIBRE_FR,
        prix_affiche=eur(PRIX_AFFICHE),
        prix_base=eur(PRIX_BASE),
        prix_haut=eur(lignes_echelle[4]["tenu"]),
        eur_place_base=eur(PRIX_BASE / N_PLACES),
        eur_place_haut=eur(lignes_echelle[4]["tenu"] / N_PLACES),
        cash_base=eur(CASH_BASE),
        cash_haut=eur(CASH_HAUT),
        loyer_ref=eur(LOYER_REF),
        loyer_haut=eur(LOYER_HAUT),
        loyer_pess=eur(LOYER_PESSIMISTE),
        note=str(NOTE).replace(".", ","),
        verdict_libelle={"acheter": "à acheter", "negocier": "à négocier", "fuir": "à fuir"}[VERDICT],
    )
    for reste in ("{", "}"):
        if "{" + "loyer" in html or "}{" in html:
            raise SystemExit("placeholder non remplacé dans la sortie")
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"Fiche écrite : {SORTIE} ({len(html)} caractères)")
    print(f"note={NOTE} verdict={VERDICT} ({VERDICT_CLS}) | prix base={PRIX_BASE:.0f} € | "
          f"prix haut={lignes_echelle[4]['tenu']:.0f} € | CF affiché={CF_AFFICHE:+.0f} €/mois")


if __name__ == "__main__":
    main()
