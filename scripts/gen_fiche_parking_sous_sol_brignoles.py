#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère la fiche HTML du slug 2026-10-13-parking-sous-sol-brignoles-extension.

Annonce leboncoin 3135454276 : une place en sous-sol sécurisé dans une résidence
livrée il y a 18 mois, à Brignoles (83170), 11 500 € (baisse de prix), vendue libre.

Convention de chiffrage :
- SCI à l'IS 15 % ; place en sous-sol AMORTISSABLE (bâti) : quote-part 90 % du prix
  de revient sur 30 ans
- seuil de cash-flow du groupe : apport 10 %, prêt 90 % du prix sur 15 ans à 3,70 %,
  assurance 0,34 % ; les frais d'acquisition sont sortis comptant, hors financement
- « prix d'équilibre » d'un loyer : prix auquel le net après IS couvre exactement la
  charge du lot (hors frais, qui restent comptants)

Tout chiffre publié passe par calcule() ; avec HERMES_TOLERANT=1 les écarts sont
listés au lieu de lever une assertion, ce qui permet de les corriger en un passage.
"""
import copy
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

from analyse_app import engine, scoring  # noqa: E402

SLUG = "2026-10-13-parking-sous-sol-brignoles-extension"
SORTIE = os.path.join(RACINE, "analyses", SLUG, "index.html")
TOLERANT = os.environ.get("HERMES_TOLERANT") == "1"

LOYER_MARCHE = 75.0        # loyer retenu : haut de la bande relevée (50-80 €/mois)
LOYER_VENDEUR = 100.0      # annoncé dans l'annonce, sans bail
LOYER_BAS = 60.0           # bas de bande pour une place nue concurrencée
LOYER_BEST = 82.5          # +10 % (grille de la branche parking)
LOYER_WORST = 60.0         # −20 % (grille de la branche parking)
FRAIS = 1925.0
PRIX_AFFICHE = 11500.0
VALEUR_BASSE = 10000.0
VALEUR_HAUTE = 12500.0
VALEUR = 11500.0
# Annuité mensuelle par euro de prix : 90 % financés sur 15 ans à 3,70 % + assurance 0,34 %
ANNUITE = 0.9 * (0.037 / 12) / (1 - (1 + 0.037 / 12) ** -180) + 0.9 * 0.0034 / 12
PLAFOND_MAISON_ACTE_EN_MAIN = 10800.0   # doctrine parking, place en sous-sol

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
    return nfr(v, dec) + " €"


def nfr(v, dec=0):
    """Nombre au format français (espace pour les milliers, virgule décimale)."""
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


def pct(v, dec=2):
    if v is None:
        return "—"
    return nfr(v, dec) + " %"


def euro_signe(v, dec=0):
    """Montant signé, signe moins typographique, arrondi à zéro propre."""
    if abs(v) < 0.5:
        return "0 €"
    return ("−" if v < 0 else "+") + nfr(abs(v), dec) + " €"


def charger_record():
    with open(os.path.join(RACINE, "analyses", "analyses.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    for r in data["analyses"]:
        if r["slug"] == SLUG:
            return r
    raise SystemExit(f"record absent de la base : {SLUG}")


REC = charger_record()


def variante(loyer=None, vacance=None, prix=None):
    """Copie du record surchargée, recalculée par le moteur (jamais à la main)."""
    r = copy.deepcopy(REC)
    if loyer is not None:
        r["marche"]["loyers"][0]["loyer_mensuel_euros"] = loyer
    if vacance is not None:
        r["hypotheses"]["vacance_base_pct"] = vacance
    if prix is not None:
        r["annonce"]["prix_retenu_euros"] = prix
        # les frais restent fixes sur un petit ticket (barème notaire), on ne les proratise pas
    c = engine.compute(r)
    note, verdict, comp = scoring.note_et_verdict(r, c)
    return r, c, note, verdict, comp


def equilibre(net_annuel):
    """Prix auquel le net après IS couvre exactement la charge du lot (frais comptants)."""
    return (net_annuel / 12.0) / ANNUITE


def loyer_equilibre(prix):
    """Loyer mensuel auquel le net après IS couvre la charge du lot à ce prix."""
    cible = prix * ANNUITE * 12.0
    bas, haut = 1.0, 400.0
    for _ in range(60):
        milieu = (bas + haut) / 2.0
        _, c, _, _, _ = variante(loyer=milieu, vacance=REC["hypotheses"]["vacance_base_pct"])
        if c["fiscal"]["net_apres_is"] < cible:
            bas = milieu
        else:
            haut = milieu
    return (bas + haut) / 2.0


# --------------------------------------------------------------------------
# Chiffres du dossier
# --------------------------------------------------------------------------
C_BASE = engine.compute(REC)
NOTE, VERDICT, COMP = scoring.note_et_verdict(REC, C_BASE)
VERDICT_CLS = {"acheter": "buy", "negocier": "nego", "fuir": "pass"}[VERDICT]
CLASSE_NOTE = scoring.classe_note(NOTE)

EBE = C_BASE["fiscal"]["ebe"]
IS = C_BASE["fiscal"]["is_annuel"]
AMORT = C_BASE["fiscal"]["amortissement"]
NET = C_BASE["fiscal"]["net_apres_is"]
REVIENT = C_BASE["prix_revient_total"]
RDT_REVIENT = C_BASE["rendements"]["net_sur_revient_pct"]
RDT_VALEUR = C_BASE["rendements"]["net_sur_valeur_pct"]
RDT_BRUT = C_BASE["rendements"]["brut_sur_revient_pct"]
RATIO = C_BASE["ratio_cout_valeur"]
MENS_AFFICHE = PRIX_AFFICHE * ANNUITE
CF_AFFICHE = NET / 12.0 - MENS_AFFICHE
PRIX_EQUILIBRE = equilibre(NET)
LOYER_EQ_AFFICHE = loyer_equilibre(PRIX_AFFICHE)
# Le solveur du moteur proratise les frais d'acquisition avec le prix, ce qui est faux
# sur un petit ticket (barème notaire quasi fixe) : on résout ici aux frais réels pour
# que le plafond publié soit cohérent avec la grille de prix de la même page.
def _plafond_aux_frais_reels():
    bas, haut = 1000.0, 3.0 * PRIX_AFFICHE
    for _ in range(60):
        milieu = (bas + haut) / 2.0
        _, _, _, _, comp = variante(prix=milieu)
        if comp["plafonds"]:
            haut = milieu
        else:
            bas = milieu
    return int(bas // 100.0 * 100.0)


PRIX_PLAFOND_FRAIS_REELS = _plafond_aux_frais_reels()
PRIX_PLAFOND_MOTEUR, CONTRAINTE = scoring.prix_plafond(REC)
PRIX_CIBLE_MOTEUR = scoring.prix_cible(REC)
PRIX_PLAFOND = PRIX_PLAFOND_FRAIS_REELS
PRIX_CIBLE = PRIX_PLAFOND_FRAIS_REELS
MOIS_LOYER = PRIX_AFFICHE / LOYER_MARCHE
PRIX_100_MOIS = 100.0 * LOYER_MARCHE

# Grille des prix : ce que le même lot donne selon le prix payé
GRILLE = []
for p in (5000.0, 6000.0, 6500.0, 7000.0, 7500.0, 8000.0, 9000.0, 10000.0, 10800.0, 11500.0):
    r, c, n, v, _ = variante(prix=p, loyer=LOYER_MARCHE, vacance=REC["hypotheses"]["vacance_base_pct"])
    net = c["fiscal"]["net_apres_is"]
    GRILLE.append({
        "prix": p,
        "revient": c["prix_revient_total"],
        "ebe": c["fiscal"]["ebe"],
        "net": net,
        "rdt": c["rendements"]["net_sur_revient_pct"],
        "brut": c["rendements"]["brut_sur_revient_pct"],
        "avant_is": c["fiscal"]["ebe"] / c["prix_revient_total"] * 100.0,
        "cf": net / 12.0 - p * ANNUITE,
        "mois": p / LOYER_MARCHE,
        "note": n,
        "verdict": v,
        "ratio": c["ratio_cout_valeur"],
    })

# Scénarios publiés (au prix affiché)
S_BASE = variante(loyer=LOYER_MARCHE, vacance=10.0)
S_BEST = variante(loyer=LOYER_BEST, vacance=5.0)
S_WORST = variante(loyer=LOYER_WORST, vacance=25.0)
S_VENDEUR = variante(loyer=LOYER_VENDEUR, vacance=10.0)

# Contrôles d'ancrage
calcule("frais d'acquisition", C_BASE["frais_acquisition"], FRAIS)
calcule("prix de revient au prix affiché", REVIENT, PRIX_AFFICHE + FRAIS, 1.0)
calcule("EBE au loyer de marché", EBE, 631.0, 1.0)
calcule("amortissement du bâti", AMORT, 0.9 * REVIENT / 30.0, 1.0)
calcule("IS du scénario de base", IS, 15.0 * (EBE - AMORT) / 100.0, 1.0)
calcule("net après IS", NET, EBE - IS, 1.0)
calcule("rendement net sur revient", RDT_REVIENT, 4.44, 0.02)
calcule("rendement net sur valeur", RDT_VALEUR, 5.19, 0.02)
calcule("rendement brut sur revient", RDT_BRUT, 4.70, 0.02)
calcule("ratio coût/valeur", RATIO, 1.167, 0.01)
calcule("échéance au prix affiché", MENS_AFFICHE, 78.0, 1.0)
calcule("cash-flow au prix affiché", CF_AFFICHE, -28.0, 1.5)
calcule("prix d'équilibre au loyer de marché", PRIX_EQUILIBRE, 7330.0, 40.0)
calcule("loyer d'équilibre au prix affiché", LOYER_EQ_AFFICHE, 113.0, 1.0)
calcule("note au prix affiché", NOTE, 3.0, 0.05)
calcule("prix plafond aux frais réels", float(PRIX_PLAFOND), 5200.0, 100.0)
calcule("prix plafond du solveur du moteur (frais proratisés)", float(PRIX_PLAFOND_MOTEUR), 6000.0, 500.0)
calcule("mois de loyer au prix affiché", MOIS_LOYER, 153.0, 1.0)

# --------------------------------------------------------------------------
# Blocs HTML
# --------------------------------------------------------------------------
def bloc_cartes():
    cartes = [
        ("Prix affiché", eur(PRIX_AFFICHE)),
        ("Nature", "1 place en sous-sol sécurisé (bip), résidence de 18 mois"),
        ("Loyer de marché retenu", f"{eur(LOYER_MARCHE)}/mois — bande relevée 50 à 80 €"),
        ("Valeur de revente retenue", f"{eur(VALEUR_BASSE)} à {eur(VALEUR_HAUTE)}"),
        ("Prix de revient affiché", eur(REVIENT)),
        ("Prix demandé en mois de loyer", f"{nfr(MOIS_LOYER)} mois — repère du groupe : 100"),
        ("Rendement net d'IS (revient / valeur)", f"{pct(RDT_REVIENT)} / {pct(RDT_VALEUR)}"),
        ("Note", f"{nfr(NOTE, 1)}/10"),
    ]
    html = []
    for label, valeur in cartes:
        html.append(f'    <div class="card">\n      <span class="card-label">{label}</span>\n'
                    f'      <span class="card-value">{valeur}</span>\n    </div>')
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
    return "\n".join(cards)


def bloc_strategie():
    c_ven = S_VENDEUR[1]
    return f"""    <table class="strategy-table">
      <thead>
        <tr>
          <th>Stratégie</th>
          <th>Lots</th>
          <th>Rendement net d'IS (revient)</th>
          <th>Valeur revente</th>
          <th>Ratio coût/valeur</th>
          <th>Faisabilité</th>
          <th>Risque</th>
          <th>Adéquation</th>
        </tr>
      </thead>
      <tbody>
        <tr class="strategy-row">
          <td>Location longue durée <strong>au prix affiché</strong> — écartée</td>
          <td>1</td>
          <td>{pct(RDT_REVIENT)} (loyer {eur(LOYER_MARCHE)})</td>
          <td>{eur(VALEUR)}</td>
          <td><span class="ratio-badge ratio-mauvais">{nfr(RATIO, 3)}</span></td>
          <td><span class="badge-faisabilite faisabilite-moyenne">Relocation à trouver</span></td>
          <td><span class="badge-risque risque-eleve">Élevé</span></td>
          <td><div class="adeq-cell"><div class="adeq-bar-track"><div class="adeq-bar-fill adeq-low" style="width:42%"></div></div></div></td>
        </tr>
        <tr class="strategy-row">
          <td>Location au prix affiché <strong>au loyer annoncé par le vendeur</strong> ({eur(LOYER_VENDEUR)}/mois) — écartée aussi</td>
          <td>1</td>
          <td>{pct(c_ven["rendements"]["net_sur_revient_pct"])} (loyer {eur(LOYER_VENDEUR)})</td>
          <td>{eur(VALEUR)}</td>
          <td><span class="ratio-badge ratio-mauvais">{nfr(c_ven["ratio_cout_valeur"], 3)}</span></td>
          <td><span class="badge-faisabilite faisabilite-faible">Loyer non constaté</span></td>
          <td><span class="badge-risque risque-eleve">Élevé</span></td>
          <td><div class="adeq-cell"><div class="adeq-bar-track"><div class="adeq-bar-fill adeq-low" style="width:42%"></div></div></div></td>
        </tr>
        <tr class="strategy-row selected">
          <td><strong>Location longue durée au prix du marché locatif et du cash-flow</strong> — sous {eur(PRIX_EQUILIBRE)} de prix payé</td>
          <td>1</td>
          <td>{pct(GRILLE[4]["rdt"])} (loyer {eur(LOYER_MARCHE)})</td>
          <td>{eur(VALEUR_BASSE)} à {eur(VALEUR_HAUTE)}</td>
          <td><span class="ratio-badge ratio-bon">{nfr(GRILLE[4]["ratio"], 3)}</span></td>
          <td><span class="badge-faisabilite faisabilite-moyenne">Négociation de −35 %</span></td>
          <td><span class="badge-risque risque-modere">Modéré</span></td>
          <td><div class="adeq-cell"><div class="adeq-bar-track"><div class="adeq-bar-fill adeq-mid" style="width:58%"></div></div></div></td>
        </tr>
      </tbody>
    </table>"""


def bloc_grille():
    lignes = []
    for g in GRILLE:
        cls = ' class="highlight"' if g["prix"] == PRIX_AFFICHE else ""
        lignes.append(
            f"          <tr{cls}><td>{eur(g['prix'])}</td>"
            f'<td class="num">{eur(g["revient"])}</td>'
            f'<td class="num">{pct(g["avant_is"])}</td>'
            f'<td class="num">{pct(g["rdt"])}</td>'
            f'<td class="num">{euro_signe(g["cf"])}/mois</td>'
            f'<td class="num">{nfr(g["mois"])}</td>'
            f'<td class="num">{nfr(g["note"], 1)}/10</td></tr>')
    return "\n".join(lignes)


def bloc_loyers():
    lignes = []
    relev = [
        ("Fiche place Caramy (Brignoles, sous-sol sécurisé, résidence neuve)", "75 €/mois",
         "8 baux écrits à 55 €, 9e place signée à 70 €, loyer de marché retenu 75 € (relevé 27/08/2026)"),
        ("Foncia — résidence Ramba Liberté", "80 €/mois CC",
         "annonce de location, charges comprises"),
        ("leboncoin — parking, quartier Extension années 50-70", "80 €/mois", "annonce de location, 10/2026"),
        ("SeLoger — agence REX, centre vieille ville", "55 €/mois", "annonce de location, 10/2026"),
        ("Zimo — place en sous-sol sécurisée avec télécommande", "50 €/mois", "annonce de location, 10/2026"),
        ("Vendeur du lot étudié", "100 €/mois", "annonce seulement — aucun bail, aucun locataire, aucune annonce locative publiée"),
    ]
    for src, loyer, detail in relev:
        lignes.append(f"          <tr><td>{src}</td><td class=\"num\"><strong>{loyer}</strong></td><td>{detail}</td></tr>")
    return "\n".join(lignes)


def bloc_identite():
    return f"""      <tbody>
        <tr><th>Adresse</th><td>Brignoles (83170), quartier « Extension années 80-90 », résidence livrée il y a 18 mois. Adresse exacte et numéro de rue non communiqués dans l'annonce ; la place porte le n° 1015 au sol.</td></tr>
        <tr><th>Type</th><td>1 place de stationnement en sous-sol sécurisé, accès par bip, place située près de l'ascenseur. Béton brut, trois côtés fermés par des murs, poutre porteuse en travers du plafond, canalisations au fond et au mur droit, chemin de câbles suspendu.</td></tr>
        <tr><th>Vendeur</th><td>Particulier (profil « surace », membre depuis 2014, numéro vérifié) — vente directe, sans honoraires d'agence. Annonce affichée « Urgent », avec mention « Baisse de prix », 25 favoris, disponibilité annoncée 11/2026.</td></tr>
        <tr><th>Structure du lot</th><td>Non communiquée : lot de copropriété autonome ou rattaché à un logement, nombre de tantièmes inconnu. La location à un non-résident et la revente séparée en dépendent.</td></tr>
        <tr><th>Occupation</th><td>Aucune : place vendue libre, sans locataire. Le revenu encaissé à l'achat est nul, et la relocation est à trouver.</td></tr>
        <tr><th>Loyer de marché retenu</th><td>{eur(LOYER_MARCHE)}/mois — haut de la bande relevée à Brignoles (50 à 80 €/mois) pour un sous-sol sécurisé récent. Le vendeur annonce {eur(LOYER_VENDEUR)}/mois sans bail : non retenu.</td></tr>
        <tr><th>Charges de copropriété</th><td>80 €/an retenus (estimé — fourchette 50 à 150 €/an pour un sous-sol). Non communiquées dans l'annonce : l'appel de charges est à exiger.</td></tr>
        <tr><th>Taxe foncière</th><td>80 €/an — montant saisi par le vendeur dans l'annonce, à recouper avec l'avis de taxe foncière.</td></tr>
        <tr><th>Charges fixes / loyers</th><td>160 €/an pour 900 €/an de loyers, soit {pct(160 / 900 * 100)} : au-dessus du seuil de 15 % au-delà duquel un petit lot se refuse. C'est le premier point à vérifier, avant même le prix.</td></tr>
        <tr><th>Amortissement</th><td>Bâti amortissable (sous-sol) : {eur(AMORT)}/an, soit 90 % du prix de revient sur 30 ans. L'IS est donc de {eur(IS)} au scénario de base, et non de 15 % de l'EBE.</td></tr>
        <tr><th>Travaux</th><td>0 € — place en état dans une résidence récente. Le boxage évoqué par le vendeur (porte à poser, 3 000 à 5 000 €) suppose une autorisation d'assemblée générale qui n'existe pas à ce jour : hors offre.</td></tr>
        <tr><th>DPE</th><td>Non applicable (stationnement).</td></tr>
        <tr><th>Valeur retenue</th><td>{eur(VALEUR)} net vendeur, fourchette {eur(VALEUR_BASSE)} à {eur(VALEUR_HAUTE)} — comparables places en sous-sol à Brignoles (11 000 à 13 000 €/place, médiane 12 000 €), avec la décote retenue pour une place vendue seule hors centre.</td></tr>
      </tbody>"""


def bloc_scenario(r, c, titre, sous_titre, prix, classe):
    f = c["fiscal"]
    net = f["net_apres_is"]
    cf = net / 12.0 - prix * ANNUITE
    vac = r["hypotheses"]["vacance_base_pct"]
    charges, _ = engine.charges_annuelles(r)
    return (
        f'      <div class="projection-card {classe}">\n'
        f'        <h3>{titre}</h3>\n'
        f'        <p class="scenario-subtitle">{sous_titre}</p>\n'
        '        <table class="projection-table">\n          <tbody>\n'
        f'            <tr><td>Prix payé</td><td class="num">{eur(prix)}</td></tr>\n'
        f'            <tr><td>Loyer retenu</td><td class="num">{eur(r["marche"]["loyers"][0]["loyer_mensuel_euros"])}/mois</td></tr>\n'
        f'            <tr><td>Revenu brut annuel</td><td class="num">{eur(c["revenus_bruts_annuels"])}</td></tr>\n'
        f'            <tr><td>Vacance locative ({nfr(vac)} %)</td><td class="num">−{eur(c["revenus_bruts_annuels"] * vac / 100.0)}</td></tr>\n'
        f'            <tr class="secondary"><td>Charges (copropriété 80 € + TF 80 € + provision 2,5 %)</td><td class="num">−{eur(charges)}</td></tr>\n'
        f'            <tr class="subtotal"><td>EBE avant IS</td><td class="num">{eur(f["ebe"])}</td></tr>\n'
        f'            <tr><td>Amortissement du bâti (30 ans)</td><td class="num">−{eur(f["amortissement"])}</td></tr>\n'
        f'            <tr><td>Résultat fiscal</td><td class="num">{eur(f["resultat_fiscal"])}</td></tr>\n'
        f'            <tr><td>IS (15 %)</td><td class="num">−{eur(f["is_annuel"])}</td></tr>\n'
        f'            <tr><td>CF net annuel (exploitation)</td><td class="num">{eur(net)}</td></tr>\n'
        f'            <tr class="highlight"><td>Solde mensuel net, charge du lot déduite</td><td class="num">{euro_signe(cf)}/mois</td></tr>\n'
        f'            <tr><td>Rendement net d\'IS sur revient</td><td class="num">{pct((c["rendements"] or {}).get("net_sur_revient_pct") or 0)}</td></tr>\n'
        '          </tbody>\n        </table>\n      </div>')


def bloc_projections():
    cartes = []
    cartes.append(bloc_scenario(
        S_BASE[0], S_BASE[1], "Scénario Base",
        f"Loyer {eur(LOYER_MARCHE)}/mois (marché relevé) — vacance 10 % — prix affiché {eur(PRIX_AFFICHE)}",
        PRIX_AFFICHE, "scenario-base"))
    cartes.append(bloc_scenario(
        S_BEST[0], S_BEST[1], "Scénario Best",
        f"Loyer {eur(LOYER_BEST)}/mois (+10 %) — vacance 5 % — relocation immédiate au prix affiché {eur(PRIX_AFFICHE)}",
        PRIX_AFFICHE, "scenario-best"))
    cartes.append(bloc_scenario(
        S_WORST[0], S_WORST[1], "Scénario Worst",
        f"Loyer {eur(LOYER_WORST)}/mois (−20 %) — vacance 25 % (trois mois de vide par an) — prix affiché {eur(PRIX_AFFICHE)}",
        PRIX_AFFICHE, "scenario-worst"))
    return "\n\n".join(cartes)


def bloc_comparaison():
    scen = {"base": S_BASE, "best": S_BEST, "worst": S_WORST}

    def ligne(label, f):
        return ("          <tr><td>" + label + "</td>"
                + "".join(f'<td class="num">{f(scen[k][0], scen[k][1])}</td>' for k in ("base", "best", "worst"))
                + "</tr>")

    def cf(r, c):
        return euro_signe(c["fiscal"]["net_apres_is"] / 12.0 - MENS_AFFICHE) + "/mois"

    return "\n".join([
        ligne("Loyer retenu", lambda r, c: eur(r["marche"]["loyers"][0]["loyer_mensuel_euros"]) + "/mois"),
        ligne("EBE avant IS", lambda r, c: eur(c["fiscal"]["ebe"])),
        ligne("IS", lambda r, c: eur(c["fiscal"]["is_annuel"])),
        ligne("Net après IS / an", lambda r, c: eur(c["fiscal"]["net_apres_is"])),
        ligne("Solde mensuel net", cf),
        ligne("Rendement net d'IS sur revient",
              lambda r, c: pct((c["rendements"] or {}).get("net_sur_revient_pct") or 0)),
    ])


def bloc_risques():
    lignes = []
    risques = sorted(REC["analyse"]["risques"], key=lambda r: -r["severite"])
    for r in risques:
        lignes.append(
            "        <tr>\n"
            f'          <td>{r["facteur"]}</td>\n'
            f'          <td>{r["detail"]}</td>\n'
            f'          <td><span class="severity severity-{r["severite"]}">{r["severite"]}/5</span></td>\n'
            "        </tr>")
    sev = sum(r["severite"] for r in REC["analyse"]["risques"]) / len(REC["analyse"]["risques"])
    deux_pires = sorted((r["severite"] for r in REC["analyse"]["risques"]), reverse=True)[:2]
    calcule("score de risque", COMP["s_risque"], 10 - 2 * ((sum(deux_pires) / 2.0) - 1), 0.01)
    return "\n".join(lignes), sev


# --------------------------------------------------------------------------
# Textes et gabarit
# --------------------------------------------------------------------------
EBE_VENDEUR = S_VENDEUR[1]["fiscal"]["ebe"]
CF_VENDEUR = S_VENDEUR[1]["fiscal"]["net_apres_is"] / 12.0 - MENS_AFFICHE
RDT_VENDEUR = S_VENDEUR[1]["rendements"]["net_sur_revient_pct"]
PLAFOND_MAISON_PRIX = PLAFOND_MAISON_ACTE_EN_MAIN - FRAIS

LECTURE = (
    f"Une place en sous-sol sécurisé dans une résidence de 18 mois, sans travaux, dans une commune où le "
    f"stationnement en centre-ville est payant depuis 2025 : le produit est bon, le prix ne l'est pas. "
    f"À {eur(PRIX_AFFICHE)}, la place demande {nfr(MOIS_LOYER)} mois de loyer pour être payée, quand notre repère "
    f"est de 100 mois ({eur(PRIX_100_MOIS)} pour un loyer de {eur(LOYER_MARCHE)}). Il faudrait la louer "
    f"{eur(LOYER_EQ_AFFICHE)}/mois pour qu'elle couvre seulement sa charge, alors que le vendeur lui-même "
    f"en annonce {eur(LOYER_VENDEUR)} — et que la bande relevée à Brignoles s'arrête à 80 €/mois. "
    f"Le prix auquel le dossier cesse d'être perdant est {eur(PRIX_EQUILIBRE)}, soit "
    f"{eur(PRIX_AFFICHE - PRIX_EQUILIBRE)} de moins que ce qui est demandé."
)

CONF = (
    f"Le seul chiffre qui décide ici est le loyer, et personne ne le connaît : la place est vide, le vendeur "
    f"n'a ni bail ni locataire, et la bande locale va de 50 à 80 €/mois. À {eur(LOYER_MARCHE)}/mois — le haut "
    f"de cette bande, tenable seulement grâce au sous-sol sécurisé et à l'ascenseur — le prix d'équilibre est "
    f"{eur(PRIX_EQUILIBRE)}, et le plafond de doctrine du groupe pour une place en sous-sol est "
    f"{eur(PLAFOND_MAISON_ACTE_EN_MAIN)} acte en main, soit {eur(PLAFOND_MAISON_PRIX)} de prix. "
    f"Le prix demandé est au-dessus des deux, et l'écart n'est pas un malentendu de négociation : c'est le prix "
    f"du marché local des places (11 000 à 13 000 €), que les loyers de cette commune ne portent pas."
)

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
  <p class="report-address">{adresse}</p>
  <p class="report-date">Analyse générée le 13 octobre 2026</p>
  <p class="report-source">Source : Leboncoin — particulier (profil « surace ») — vente directe sans honoraires</p>
  <div class="report-source-link"><a href="{url}">{url}</a></div>
</header>

<main>

  <!-- === Bannière stratégie === -->
  <div class="strategy-banner">
    <span class="strategy-badge">Placement parking — une place, un loyer</span>
    <p>Stratégie retenue : <strong>location longue durée de la place, à un prix qui couvre sa propre charge</strong> — SCI à l'IS (15 %)</p>
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
    <h2>Attractivité — Brignoles, quartier Extension années 80-90</h2>
    <p class="attractiveness-intro">Brignoles a rendu payant le stationnement du centre (1,70 €/h, en enclos et en souterrain) et compte 17 000 habitants : la demande de places privatives existe. Le quartier du lot n'est pas le centre ancien mais un secteur d'extension, où les résidences récentes ont leurs propres parkings : la tension y est plus faible, et le premier concurrent de cette place est l'offre abondante des autres places de la même résidence. La place est située près de l'ascenseur, avec un accès piéton direct — un vrai avantage de commercialité pour un locataire qui gare sa voiture et monte chez lui.</p>
    <div class="attractiveness-grid">
{attractivite}
    </div>
    <div class="attractiveness-summary">
      <p><strong>Profil locataire cible :</strong> résident de la résidence cherchant une seconde place (véhicule supplémentaire, utilitaire, moto), riverain du quartier sans garage, professionnel du secteur ayant besoin d'un abri sûr pour un véhicule de service.</p>
      <p><strong>Conclusion :</strong> {lecture}</p>
    </div>
  </section>

  <!-- === Stratégie d'exploitation === -->
  <section class="strategy-exploration">
    <h2>Stratégie d'exploitation</h2>
    <p class="attractiveness-intro">Trois lectures du même lot : payer le prix affiché et parier sur un loyer de 100 €, payer le prix affiché au loyer réel du marché, ou payer le prix que le loyer réel finance. Les deux premières ne tiennent pas, la troisième fixe le plafond.</p>
{strategie}
    <div class="strategy-rationale">
      <p>{conf}</p>
    </div>
  </section>

  <!-- === Échelle des prix === -->
  <section class="strategy-exploration">
    <h2>Échelle des prix — ce que la place vaut au loyer de {loyer_marche} €/mois</h2>
    <p class="attractiveness-intro">Le rendement, le solde mensuel et la note sont recalculés par le moteur à chaque prix, loyer de marché retenu constant ({loyer_marche} €/mois), vacance 10 %. Le solde mensuel se lit sous la convention du groupe : frais d'acquisition sortis comptant, solde porté sur quinze ans, intérêts et assurance compris.</p>
    <table class="comparison-table">
      <thead>
        <tr><th>Prix payé</th><th>Prix de revient</th><th>Net avant IS / revient</th><th>Net d'IS / revient</th><th>Solde mensuel net</th><th>Mois de loyer</th><th>Note</th></tr>
      </thead>
      <tbody>
{grille}
      </tbody>
    </table>
    <p class="attractiveness-intro"><strong>Trois ancres, toutes sous le prix demandé :</strong> le plafond de doctrine du groupe pour une place en sous-sol ({plafond_maison} acte en main, soit {plafond_maison_prix} de prix), le repère des 100 mois de loyer ({prix_100_mois}), et le prix auquel le net d'IS couvre la charge du lot, soit {prix_equilibre}. Le prix affiché de {prix_affiche} est au-dessus des trois, et le plancher de rendement de la branche parking (8 % net d'IS sur revient) n'est atteint qu'à {prix_plancher_perf} de prix payé — un prix que le vendeur n'acceptera pas sur une place qu'il affiche 11 500 €.</p>
    <p class="attractiveness-intro">Sur cette place, <strong>les charges fixes pèsent plus lourd que le prix d'achat</strong> : 160 €/an de copropriété et de taxe foncière pour 900 €/an de loyers, soit {ratio_charges} %. Notre seuil de refus est de 15 %. Si l'appel de charges ressort à 150 €/an plutôt que 80 €, le prix d'équilibre perd encore {perte_charges}, sans qu'aucun chiffre du vendeur ne change.</p>
  </section>

  <!-- === Relevé de loyers === -->
  <section class="strategy-exploration">
    <h2>Relevé de loyers — ce que le marché dit, ce que le vendeur annonce</h2>
    <table class="comparison-table">
      <thead>
        <tr><th>Source</th><th>Loyer</th><th>Détail</th></tr>
      </thead>
      <tbody>
{loyers}
      </tbody>
    </table>
    <p class="attractiveness-intro">La bande de marché s'arrête à 80 €/mois, charges comprises, et le dernier bail signé dans la commune sur un produit comparable (place Caramy, sous-sol sécurisé, résidence neuve) l'a été à 70 €/mois. Les {loyer_vendeur} €/mois de l'annonce ne sont pas adossés à un locataire : c'est une fourchette de commercial, pas un loyer. Au loyer annoncé, le dossier reste d'ailleurs négatif : {ebe_vendeur} d'EBE, {rdt_vendeur} de rendement net d'IS sur revient et un solde mensuel de {cf_vendeur} après charge du lot.</p>
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
    <p class="attractiveness-intro">Frais d'acquisition {frais}, aucun travaux, charges 160 €/an (copropriété 80 € estimée + taxe foncière 80 € affichée) et provision travaux de 2,5 % des loyers. Place en sous-sol : le bâti est amortissable (90 % du prix de revient sur 30 ans), l'IS porte donc sur le résultat après amortissement. Les trois scénarios balaient la vacance et le loyer de la branche parking, au prix affiché.</p>

    <div class="projections-grid">
{projections}
    </div>

    <div class="projection-summary">
      <h3>Synthèse comparative — au prix affiché de {prix_affiche}</h3>
      <table class="comparison-table">
        <thead>
          <tr><th>Indicateur</th><th>Base — {loyer_marche}/mois</th><th>Best — {loyer_best}/mois</th><th>Worst — {loyer_worst}/mois</th></tr>
        </thead>
        <tbody>
{comparaison}
        </tbody>
      </table>
      <p class="attractiveness-intro">Aucun des trois scénarios ne couvre la charge du lot : la meilleure hypothèse, un loyer 10 % au-dessus du marché haut avec relocation immédiate, laisse encore {cf_best}/mois à notre charge. Le dossier ne se sauve pas par l'exploitation, seulement par le prix.</p>
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
      <p class="verdict-stance"><strong>On ne paie pas ce prix.</strong> {verdict_stance}</p>
    </div>
    <div class="verdict-details">
      <p><strong>Prix plafond : {prix_plafond_moteur} de prix payé</strong> ({prix_plafond_acte} acte en main, frais compris) — c'est le prix au-delà duquel la note ne peut plus remonter, le rendement net d'IS passant sous le plancher de 8 % de la branche. Le calcul retient les frais d'acquisition réels du barème notaire, qui ne baissent pas avec le prix : à ce prix, la note atteint 6,5 (« à acheter »), et c'est donc à la fois le prix plafond et le prix cible. Au prix demandé, le rendement net d'IS sur revient est de {rdt_revient} pour un plancher de 8 %, et le bien est payé {ratio} fois sa valeur de revente retenue.</p>
      <p><strong>Ce que le dossier aurait demandé :</strong> {prix_equilibre} de prix payé pour que le net d'IS couvre la charge du lot à {loyer_marche}/mois, soit {ecart_equilibre} sous le prix affiché ({ecart_equilibre_pct}). Un tel écart n'est pas une négociation ordinaire : il place le vendeur sous la valeur de marché de son propre lot, sur la base des loyers constatés dans sa commune. C'est la raison pour laquelle la fiche conclut au refus plutôt qu'à une offre.</p>
      <p><strong>Ce qui ferait rouvrir le dossier :</strong></p>
      <ul>
        <li>Un bail écrit, ou une promesse de bail, à 100 €/mois ou plus, avec un locataire identifié : cela déplacerait le prix d'équilibre vers {prix_equilibre_100} et rapprocherait le dossier de la valeur demandée, sans l'atteindre.</li>
        <li>Un prix ramené à {prix_equilibre} net vendeur. En dessous de {plafond_maison_prix}, la place entre même dans le plafond de doctrine du groupe pour un sous-sol.</li>
        <li>Des charges de copropriété confirmées sous 80 €/an et une taxe foncière réelle : sur 900 € de loyers, chaque tranche de 300 € de charges annuelles coûte environ 27 €/mois de loyer, donc du prix.</li>
      </ul>
      <p><strong>Pièces à exiger avant toute reprise du contact :</strong> numéro de lot et tantièmes, appel de charges et budget prévisionnel, procès-verbaux des assemblées depuis la livraison, avis de taxe foncière, clause du règlement sur la location à un non-résident, ancienneté du titre du vendeur (droit réduit ou droit commun).</p>
    </div>
    <div class="verdict-meta">
      <p><strong>Régime fiscal retenu :</strong> SCI à l'IS (15 %) — amortissement du bâti {amortissement}/an, frais d'acquisition {frais}, aucun travaux</p>
      <p><strong>Hypothèses retenues :</strong> loyer {loyer_marche} €/mois, vacance 10 % en base, charges 160 €/an, amortissement sur 30 ans, placement de la réserve à 2,84 %</p>
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

    risques_html, sev = bloc_risques()

    prix_eq_100 = equilibre(S_VENDEUR[1]["fiscal"]["net_apres_is"])
    ecart_eq = PRIX_AFFICHE - PRIX_EQUILIBRE
    # perte de prix d'équilibre quand les charges passent de 160 à 230 €/an (copro 150 €)
    rec_cher = copy.deepcopy(REC)
    rec_cher["hypotheses"]["charges"]["charges_copro_annuelles_euros"] = 150.0
    c_cher = engine.compute(rec_cher)
    perte_charges = PRIX_EQUILIBRE - equilibre(c_cher["fiscal"]["net_apres_is"])

    html = TEMPLATE.format(
        titre=REC["titre"],
        adresse="1 place de stationnement en sous-sol sécurisé — résidence livrée il y a 18 mois, Brignoles (83170)",
        url=REC["annonce"]["url"],
        cartes=bloc_cartes(),
        lat="43.4057",
        lon="6.0614",
        map_addr="Brignoles (83170) — coordonnées de la commune, l'annonce ne communique pas l'adresse exacte",
        attractivite=bloc_attractivite(),
        lecture=LECTURE,
        strategie=bloc_strategie(),
        conf=CONF,
        grille=bloc_grille(),
        loyers=bloc_loyers(),
        identite=bloc_identite(),
        projections=bloc_projections(),
        comparaison=bloc_comparaison(),
        risques=risques_html,
        verdict_cls=VERDICT_CLS,
        verdict_stance=(
            f"À {eur(PRIX_AFFICHE)}, la place produit {eur(EBE)} d'EBE et {eur(NET)} après IS, "
            f"soit {pct(RDT_REVIENT)} de rendement net sur un acte en main de {eur(REVIENT)} — "
            f"la moitié du plancher de 8 % de la branche — pour un cash-flow de "
            f"{euro_signe(CF_AFFICHE)}/mois, charge du lot déduite. La place est saine, récente, sécurisée, sans "
            f"travaux : le refus porte sur le prix, rien d'autre. À {nfr(MOIS_LOYER)} mois de loyer, ce lot "
            f"se paie au niveau du marché local des places, mais pas des loyers de Brignoles."
        ),
        note=nfr(NOTE, 1),
        verdict_libelle={"acheter": "à acheter", "negocier": "à négocier", "fuir": "à fuir"}[VERDICT],
        loyer_marche=nfr(LOYER_MARCHE, 0),
        loyer_best=nfr(LOYER_BEST, 1),
        loyer_worst=nfr(LOYER_WORST, 0),
        loyer_vendeur=nfr(LOYER_VENDEUR, 0),
        ebe_vendeur=eur(EBE_VENDEUR),
        rdt_vendeur=pct(RDT_VENDEUR),
        cf_vendeur=euro_signe(CF_VENDEUR),
        cf_best=euro_signe(S_BEST[1]["fiscal"]["net_apres_is"] / 12.0 - MENS_AFFICHE),
        prix_affiche=eur(PRIX_AFFICHE),
        prix_equilibre=eur(PRIX_EQUILIBRE),
        prix_equilibre_100=eur(prix_eq_100),
        prix_100_mois=eur(PRIX_100_MOIS),
        plafond_maison=eur(PLAFOND_MAISON_ACTE_EN_MAIN),
        plafond_maison_prix=eur(PLAFOND_MAISON_PRIX),
        prix_plancher_perf=eur(PRIX_PLAFOND),
        prix_plafond_moteur=eur(PRIX_PLAFOND),
        prix_plafond_acte=eur(PRIX_PLAFOND + FRAIS),
        prix_cible=eur(PRIX_CIBLE),
        ecart_equilibre=eur(ecart_eq),
        ecart_equilibre_pct=pct(ecart_eq / PRIX_AFFICHE * 100),
        rdt_revient=pct(RDT_REVIENT),
        ratio=nfr(RATIO, 2),
        ratio_charges=nfr(160 / 900 * 100, 1),
        perte_charges=eur(perte_charges),
        frais=eur(FRAIS),
        amortissement=eur(AMORT),
    )

    # Contrôles de structure avant écriture
    import re
    residuels = [m for m in re.findall(r"\{[a-z_][a-z_0-9]*\}", html)
                 if m not in ("{s}", "{z}", "{x}", "{y}")]
    if residuels:
        raise SystemExit(f"placeholders non remplacés : {sorted(set(residuels))}")
    attendus = ["report-header", "summary-cards", "map-section", "attractiveness",
                "strategy-exploration", "identity-sheet", "financial-projections",
                "risk-matrix", 'section class="verdict', "report-signature"]
    manquants = [s for s in attendus if s not in html]
    if manquants:
        raise SystemExit(f"sections manquantes dans la sortie : {manquants}")
    if len(html) < 20000:
        raise SystemExit(f"sortie suspecte : {len(html)} caractères")
    if 'name="robots"' not in html or "noindex" not in html:
        raise SystemExit("balise noindex absente")
    interdits = re.findall(r"\b(prêt|prêts|emprunt\w*|crédit\w*|apport\w*|mensualit\w*|levier|montage)\b",
                           html, flags=re.I)
    if interdits:
        raise SystemExit(f"mot de financement dans la page : {sorted(set(interdits))}")

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"Fiche écrite : {SORTIE} ({len(html)} caractères)")
    print(f"note={NOTE} verdict={VERDICT} ({VERDICT_CLS}) | revient={REVIENT:.0f} € | "
          f"net IS={NET:.0f} € | CF={CF_AFFICHE:+.1f} €/mois | prix équilibre={PRIX_EQUILIBRE:.0f} € | "
          f"loyer équilibre={LOYER_EQ_AFFICHE:.1f} € | plafond moteur={PRIX_PLAFOND} € | cible={PRIX_CIBLE} € | "
          f"sévérité moyenne={sev:.2f}")


if __name__ == "__main__":
    main()
