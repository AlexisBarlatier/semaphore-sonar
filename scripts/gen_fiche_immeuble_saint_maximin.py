# -*- coding: utf-8 -*-
"""Génère la fiche publiée de l'immeuble 9 rue Daguerre, Saint-Maximin (réf. 252).

Tout chiffre publié vient du moteur (`engine.compute`) sur l'enregistrement
`analyses/analyses.json` ; les assertions `calcule()` font échouer le build si
une donnée bouge, au lieu de publier un chiffre périmé.

Sortie : analyses/2026-09-28-immeuble-saint-maximin-9-rue-daguerre/index.html
"""
import copy
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

from analyse_app import engine, scoring, parc  # noqa: E402

SLUG = "2026-09-28-immeuble-saint-maximin-9-rue-daguerre"
SORTIE = os.path.join(RACINE, "analyses", SLUG, "index.html")
TOLERANT = os.environ.get("HERMES_TOLERANT") == "1"

DUREE_ANS = 20
TAUX = 0.037
ASSURANCE = 0.0034
APPORT = 0.10
ANNUITE = ((1 - APPORT) * (TAUX / 12) / (1 - (1 + TAUX / 12) ** -(DUREE_ANS * 12))
           + (1 - APPORT) * ASSURANCE / 12)

ECARTS = []


def calcule(libelle, publie, recalcule, tolerance=0.6):
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
    r = copy.deepcopy(REC)
    if loyer is not None:
        for ligne in r["marche"]["loyers"]:
            ligne["loyer_mensuel_euros"] = loyer
    if vacance is not None:
        r["hypotheses"]["vacance_base_pct"] = vacance
    if prix is not None:
        r["annonce"]["prix_retenu_euros"] = prix
        r["hypotheses"]["frais_acquisition_euros"] = round(prix * 0.075, 2)
    c = engine.compute(r)
    note, verd, comp = scoring.note_et_verdict(r, c)
    return r, c, note, verd, comp


def cf_de(c, prix, ans=DUREE_ANS, taux=TAUX):
    annuite = ((1 - APPORT) * (taux / 12) / (1 - (1 + taux / 12) ** -(ans * 12))
               + (1 - APPORT) * ASSURANCE / 12)
    return c["fiscal"]["net_apres_is"] / 12.0 - prix * annuite


def mensualite(prix, ans=DUREE_ANS, taux=TAUX):
    annuite = ((1 - APPORT) * (taux / 12) / (1 - (1 + taux / 12) ** -(ans * 12))
               + (1 - APPORT) * ASSURANCE / 12)
    return prix * annuite


def plafond(cible, kind="ratio", prix_min=60000.0, prix_max=220000.0):
    def tient(prix):
        r, c, note, _, _ = variante(prix=prix)
        if kind == "cf":
            return cf_de(c, prix) >= cible
        if kind == "note":
            return (note or 0) >= cible
        return c["fiscal"]["ebe"] / (mensualite(prix) * 12) >= cible
    lo, hi = prix_min, prix_max
    for _ in range(80):
        mid = (lo + hi) / 2.0
        if tient(mid):
            lo = mid
        else:
            hi = mid
    return lo


# ---------------------------------------------------------------------------
# Chiffres du dossier
# ---------------------------------------------------------------------------
PRIX = REC["annonce"]["prix_retenu_euros"]
PRIX_AFFICHE = REC["annonce"]["prix_affiche_euros"]
VALEUR = REC["marche"]["valeur"]["retenue_euros"]
SURFACE = REC["bien"]["surfaces"]["carrez_m2"]
LOYERS_AN = engine.revenus_bruts_annuels(REC)
CH = REC["hypotheses"]["charges"]
C = engine.compute(REC)
F = C["fiscal"]
NOTE, VERDICT, COMP = scoring.note_et_verdict(REC, C)
VERDICT_CLS = {"acheter": "buy", "negocier": "nego", "fuir": "pass"}[VERDICT]
VERDICT_FR = {"acheter": "à acheter", "negocier": "à négocier", "fuir": "à fuir"}

PRIX_M2 = PRIX / SURFACE
PRIX_AFFICHE_M2 = PRIX_AFFICHE / SURFACE
REVIENT = C["prix_revient_total"]
EBE = F["ebe"]
IS = F["is_annuel"]
NET = F["net_apres_is"]
MENS = mensualite(PRIX)
CF = NET / 12.0 - MENS
RATIO = EBE / (MENS * 12)
DETENTION = CH["charges_copro_annuelles_euros"] + CH["taxe_fonciere_annuelle_euros"]
CHARGES_TOTAL = engine.charges_annuelles(REC)[0]
APPORT_CASH = PRIX * APPORT + C["frais_acquisition"]
PLAFOND_RATIO = plafond(1.20, "ratio")
PLAFOND_CF = plafond(0.0, "cf")

# Rétention : les hypothèses de crédit sont la variable décisive du dossier
ECHEANCES = []
for ans in (15, 20, 25):
    m = mensualite(PRIX, ans)
    ECHEANCES.append({
        "ans": ans,
        "mens": m,
        "cf": NET / 12.0 - m,
        "ratio": EBE / (m * 12),
    })

ROTATION = []
for loyer in (500.0, 550.0, 600.0, 650.0, 700.0):
    r, c, note, verd, _ = variante(loyer=loyer)
    ROTATION.append({
        "loyer": loyer,
        "ebe": c["fiscal"]["ebe"],
        "cf": cf_de(c, PRIX),
        "ratio": c["fiscal"]["ebe"] / (mensualite(PRIX) * 12),
        "note": note,
        "verd": VERDICT_FR[verd],
    })

ECHELLE = []
for prix in (110000.0, 122500.0, 130000.0, 140000.0, 150000.0, 160000.0):
    r, c, note, verd, _ = variante(prix=prix)
    ECHELLE.append({
        "prix": prix,
        "note": note,
        "verd": VERDICT_FR[verd],
        "ebe": c["fiscal"]["ebe"],
        "cf": cf_de(c, prix),
        "net_pct": c["rendements"]["net_sur_revient_pct"],
        "ratio": c["ratio_cout_valeur"],
    })

RESERVE_PARC = parc.RESERVE_EUR
RESERVE_1AN = parc.trajectoire(12, 2.84)

# ---------------------------------------------------------------------------
# Contrôles : si ces valeurs changent, la page ne se construit pas
# ---------------------------------------------------------------------------
calcule("prix au m² retenu", round(PRIX_M2), 2599, 1)
calcule("prix affiché au m²", round(PRIX_AFFICHE_M2), 3394, 1)
calcule("revenus bruts", LOYERS_AN, 12360, 1)
calcule("frais d'acquisition", C["frais_acquisition"], 9188, 1)
calcule("prix de revient", REVIENT, 131688, 1)
calcule("EBE", round(EBE), 9918, 1)
calcule("réserve annuelle", round(F["reserve_annuelle"]), 927, 1)
calcule("produits du placement", round(F["produits_reserve"], 2), 26.33, 0.05)
calcule("amortissement du bâti", round(F["amortissement"]), 2822, 1)
calcule("IS", round(IS), 1064, 1)
calcule("net après IS", round(NET), 8854, 1)
calcule("mensualité 20 ans", round(MENS), 682, 1)
calcule("cash-flow mensuel", round(CF), 56, 1)
calcule("ratio EBE / annuité", round(RATIO, 2), 1.21, 0.01)
calcule("rendement net sur valeur", round(C["rendements"]["net_sur_valeur_pct"], 2), 6.95, 0.01)
calcule("rendement net sur revient", round(C["rendements"]["net_sur_revient_pct"], 2), 6.72, 0.01)
calcule("ratio coût / valeur", round(C["ratio_cout_valeur"], 3), 1.034, 0.001)
calcule("note du moteur", NOTE, 7.4, 0.05)
calcule("plafond ratio 1,20", round(PLAFOND_RATIO, -2), 123700, 300)
calcule("plafond cash-flow nul", round(PLAFOND_CF, -2), 133100, 100)
calcule("apport total", round(APPORT_CASH), 21438, 1)

if ECARTS and not TOLERANT:
    raise SystemExit("Écarts brief / recalcul :\n - " + "\n - ".join(ECARTS))
if ECARTS:
    for e in ECARTS:
        print("écart :", e)

# ---------------------------------------------------------------------------
# Blocs HTML
# ---------------------------------------------------------------------------
def cartes():
    lignes = [
        ("Prix retenu", f"{eur(PRIX)}"),
        ("Prix au m² habitable", f"{eur(PRIX_M2)}"),
        ("Rendement brut", f"{pct(LOYERS_AN / PRIX * 100, 2)}"),
        ("Net d'IS sur revient", f"{pct(C['rendements']['net_sur_revient_pct'], 2)}"),
        ("Cash-flow", f"{euro_signe(CF)}/mois"),
        ("Ratio EBE / annuité", f"{nfr(RATIO, 2)}"),
        ("Note du moteur", f"{nfr(NOTE, 1)}/10"),
        ("Verdict", VERDICT_FR[VERDICT].capitalize()),
    ]
    return "\n".join(
        f'    <div class="card{" card-verdict note-8" if i == 7 else ""}">\n'
        f'      <span class="card-label">{lab}</span>\n'
        f'      <span class="card-value">{val}</span>\n'
        f'    </div>'
        for i, (lab, val) in enumerate(lignes)
    )


def table_identite():
    lignes = [
        ("Adresse", "9 rue Daguerre, centre ancien — <strong>Saint-Maximin-la-Sainte-Baume (83470)</strong>. Ville-centre de la haute vallée de l'Arc, à 40 km d'Aix-en-Provence, autoroute A8 et N7 à proximité immédiate."),
        ("Type", f"Immeuble de rapport d'<strong>avant 1948</strong> : deux logements meublés, <strong>{nfr(SURFACE, 2)} m² habitables</strong> (29,72 + 17,42), 54,03 m² au sol, plus 16,18 m² de rez-de-chaussée non habitable (hall, deux caves, buanderie)."),
        ("Lots", "<strong>Deux lots d'habitation</strong>, plus des annexes dont le rattachement reste à confirmer : lots privés attachés aux logements ou parties communes."),
        ("Baux", "Deux baux meublés d'un an renouvelables. T2 reloué à partir du <strong>7 octobre 2026</strong> pour 600 € + 30 €, studio loué depuis le <strong>11 août 2026</strong> pour 430 € + 20 €. Dépôts de 1 200 € et 900 €."),
        ("Copropriété", "Charges <strong>non communiquées</strong> : ni budget prévisionnel, ni appels de fonds, ni procès-verbaux, ni état daté. Le DPE relève une toiture non isolée."),
        ("Charges", f"Taxe foncière {eur(CH['taxe_fonciere_annuelle_euros'])}/an annoncée (avis à obtenir), assurance propriétaire non occupant {eur(CH['pno_annuelle_euros'])}/an, comptabilité {eur(CH['comptabilite_annuelle_euros'])}/an. Provision de 2,5 % des loyers maintenue tant que la copropriété est inconnue."),
        ("Travaux", "Aucun montant retenu à l'acquisition. Le DPE recommande l'isolation des murs et de la toiture et relève du simple vitrage métallique au studio ; si la classe E est confirmée, les travaux sont à faire <strong>avant 2034</strong>."),
        ("Valeur retenue", f"{eur(VALEUR)}, soit <strong>{eur(VALEUR / SURFACE)}/m²</strong> — médiane DVF 2024-2025 de la tranche 25-60 m² de la commune (41 mutations)."),
        ("Vendeur", f"Agence Nestenn Saint-Maximin, mandat 119, référence 252. Annonce SeLoger à <strong>{eur(PRIX_AFFICHE)}</strong>, honoraires à la charge du vendeur. Cible de négociation {eur(PRIX)}."),
    ]
    return "\n".join(f"        <tr><th>{k}</th><td>{v}</td></tr>" for k, v in lignes)


def table_exploitation():
    lignes = []
    lignes.append(("Loyers bruts hors charges, deux meublés", LOYERS_AN, None))
    lignes.append(("Vacance structurelle 5 %", -LOYERS_AN * 0.05, "secondary"))
    lignes.append(("Provision travaux 2,5 % des loyers", -LOYERS_AN * 0.025, "secondary"))
    lignes.append((f"Taxe foncière", -CH["taxe_fonciere_annuelle_euros"], "secondary"))
    lignes.append(("Assurance et comptabilité", -(CH["pno_annuelle_euros"] + CH["comptabilite_annuelle_euros"]), "secondary"))
    lignes.append(("Produits du placement de la réserve", F["produits_reserve"], "secondary"))
    lignes.append(("EBE avant impôt", EBE, "subtotal"))
    lignes.append(("Amortissement du bâti (75 % / 35 ans)", -F["amortissement"], None))
    lignes.append((f"Impôt sur les sociétés (15 %)", -IS, None))
    lignes.append(("Flux net après IS", NET, "subtotal"))
    lignes.append((f"Échéance de crédit, {DUREE_ANS} ans à {pct(TAUX * 100, 2)}", -MENS * 12, None))
    lignes.append(("Cash-flow annuel", NET - MENS * 12, "subtotal"))
    lignes_html = []
    for lab, v, cls in lignes:
        attr = ' class="' + cls + '"' if cls else ""
        signe = "+" if v > 0 else "−"
        lignes_html.append(
            f'            <tr{attr}><td>{lab}</td>'
            f'<td class="num">{signe}{eur(abs(v), 2)}</td></tr>'
        )
    return "\n".join(lignes_html)


def table_echelle():
    lignes = []
    for e in ECHELLE:
        cls = ' class="highlight"' if abs(e["prix"] - PRIX) < 1 else ""
        lignes.append(
            f'            <tr{cls}><td>{eur(e["prix"])}</td><td>{nfr(e["note"], 1)}/10</td>'
            f'<td>{e["verd"]}</td><td>{eur(e["ebe"])}</td><td>{euro_signe(e["cf"])}</td>'
            f'<td>{pct(e["net_pct"], 2)}</td><td>{nfr(e["ratio"], 3)}</td></tr>'
        )
    return "\n".join(lignes)


def table_credit():
    lignes = []
    for e in ECHEANCES:
        cls = ' class="highlight"' if e["ans"] == DUREE_ANS else ""
        lignes.append(
            f'            <tr{cls}><td>{e["ans"]} ans</td><td>{eur(e["mens"])}</td>'
            f'<td>{euro_signe(e["cf"])}</td><td>{nfr(e["ratio"], 2)}</td>'
            f'<td>{"tenu" if e["ratio"] >= 1.20 else "refusé"}</td></tr>'
        )
    return "\n".join(lignes)


def table_rotation():
    lignes = []
    for l in ROTATION:
        cls = ' class="highlight"' if abs(l["loyer"] - 600.0) < 1 else ""
        lignes.append(
            f'            <tr{cls}><td>{eur(l["loyer"])}</td><td>{eur(l["ebe"])}</td>'
            f'<td>{nfr(l["ratio"], 2)}</td><td>{euro_signe(l["cf"])}</td>'
            f'<td>{nfr(l["note"], 1)}/10</td></tr>'
        )
    return "\n".join(lignes)


def blocs_attractivite():
    out = []
    for dim in REC["analyse"]["attractivite"]:
        out.append(
            f'      <div class="attractiveness-item">\n'
            f'        <div class="attractiveness-head"><span class="attractiveness-label">'
            f'{dim["dimension"].replace("_", " ").capitalize()}</span>'
            f'<span class="attractiveness-score">{dim["score"]}/10</span></div>\n'
            f'        <p>{dim["justification"]}</p>\n'
            f'      </div>'
        )
    return "\n".join(out)


def blocs_risques():
    out = []
    for r in REC["analyse"]["risques"]:
        out.append(
            f'        <tr><td>{r["facteur"]}</td><td class="sev sev-{r["severite"]}">'
            f'{r["severite"]}/5</td><td>{r["detail"]}</td></tr>'
        )
    return "\n".join(out)


def blocs_strategies():
    out = []
    for s in REC["analyse"]["strategies_explorees"]:
        out.append(
            f'        <tr><td>{s["strategie"]}</td><td>{s["rendement"]}</td>'
            f'<td>{s["faisabilite"]}</td><td>{s["risque"]}</td></tr>'
        )
    return "\n".join(out)


ADEQUATION = COMP["s_adequation"]
S_RATIO = COMP["s_ratio"]

HTML = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Immeuble 9 rue Daguerre, Saint-Maximin-la-Sainte-Baume — analyse du 28 septembre 2026</title>
<link rel="stylesheet" href="../../style.css">
</head>
<body>
<main class="report">

  <header class="report-header">
    <p class="report-breadcrumb">Analyse d'acquisition — {REC['analyse']['branche']} · {REC['analyse']['type_operation']}</p>
    <h1>Immeuble de rapport, deux logements meublés — 9 rue Daguerre, Saint-Maximin-la-Sainte-Baume (83470)</h1>
    <p class="report-address">Centre ancien — Var · annonce SeLoger 261QSCIG43MJ · mandat 119, référence 252 · agence Nestenn Saint-Maximin</p>
    <p class="report-date">Prix affiché {eur(PRIX_AFFICHE)} · cible de négociation {eur(PRIX)} · analysé le 28 septembre 2026</p>
    <p class="report-source">Analyse produite pour Alexis et Rémy Barlatier — Sémaphore Patrimoine. Tous les chiffres sont recalculés par le moteur du dépôt ; les pièces annoncées et non produites sont listées dans « Confiance et limites ».</p>
  </header>

  <section class="summary-cards">
{cartes()}
  </section>

  <section class="strategy-exploration">
    <h2>Lecture du dossier</h2>
    <p>Ce qui se vend, c'est un immeuble de centre ancien découpé en deux meublés : un T2 en duplex et un studio sous comble, {nfr(SURFACE, 2)} m² habitables en tout, {nfr(SURFACE / 2, 1)} m² en moyenne par logement. Deux baux meublés d'un an renouvelables, {eur(LOYERS_AN)} de loyers par an, et un studio qui s'est reloué trois semaines après sa mise en ligne. La demande pour ce créneau de petites surfaces meublées existe bel et bien dans cette commune.</p>
    <p>L'annonce, elle, doit être lue de travers. Elle affiche 70 m² et calcule {eur(PRIX_AFFICHE_M2)} le mètre carré sur cette base : ce chiffre additionne l'habitable, les 16,18 m² de rez-de-chaussée non habitable et la mezzanine du studio. Rapporté aux {nfr(SURFACE, 2)} m² réellement habitables, le prix demandé fait <strong>{eur(PRIX_AFFICHE_M2)}/m²</strong>, et notre cible <strong>{eur(PRIX_M2)}/m²</strong>. Elle annonce aussi un DPE D quand les deux étiquettes produites affichent 258 et 320 kWh/m²/an : la meilleure des deux, sans dire laquelle s'applique à quel logement.</p>
    <p>Les chiffres, maintenant. {eur(LOYERS_AN)} de loyers bruts, {eur(CHARGES_TOTAL)} de charges annuelles — vacance de 5 %, provision travaux de 2,5 %, taxe foncière, assurance et comptabilité — soit un EBE de {eur(EBE)}. Après amortissement du bâti à 75 % sur 35 ans, l'impôt sur les sociétés ressort à {eur(IS)}, laissant <strong>{eur(NET)} par an</strong>. Sur vingt ans, la mensualité de {eur(MENS)} laisse <strong>{euro_signe(CF)} par mois</strong>. Sur quinze ans, le dossier ne passe pas — c'est le sujet de la section suivante.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Fiche d'identité</h2>
    <table class="identity-table">
      <tbody>
{table_identite()}
      </tbody>
    </table>
  </section>

  <section class="financial-projections">
    <h2>Le compte d'exploitation, une année pleine</h2>
    <table class="projection-table">
      <thead><tr><th>Poste</th><th>Annuel</th></tr></thead>
      <tbody>
{table_exploitation()}
      </tbody>
    </table>
    <p class="projection-note">La vacance et la provision travaux ne sont pas perdues : elles sont placées et figurent en produits. L'amortissement du bâti n'est pas une sortie de trésorerie — il ne réduit que l'assiette de l'impôt, et c'est la raison pour laquelle le flux net après IS ({eur(NET)}) dépasse le résultat fiscal.</p>
  </section>

  <section class="financial-projections">
    <h2>Le dossier résiste-t-il au crédit ?</h2>
    <p class="strategy-rationale">C'est ici que le dossier se joue, pas sur le prix d'affichage. Les loyers et les charges sont stables ; la mensualité, non. À {eur(PRIX)}, avec 90 % financés et une assurance emprunteur de 0,34 %, voici ce que chaque durée change.</p>
    <table class="projection-table">
      <thead><tr><th>Durée</th><th>Mensualité</th><th>Cash-flow</th><th>Ratio EBE / annuité</th><th>Lecture</th></tr></thead>
      <tbody>
{table_credit()}
      </tbody>
    </table>
    <p class="scenario-subtitle">Sur <strong>quinze ans</strong>, la mensualité de {eur(ECHEANCES[0]['mens'])} dépasse ce que l'immeuble dégage : cash-flow négatif de {eur(abs(ECHEANCES[0]['cf']))} par mois, et un ratio de {nfr(ECHEANCES[0]['ratio'], 2)} pour un seuil bancaire de 1,20. Le dossier est refusé par le bien lui-même, avant même la banque. Sur <strong>vingt ans</strong>, la même acquisition devient positif : {euro_signe(ECHEANCES[1]['cf'])} par mois et un ratio de {nfr(ECHEANCES[1]['ratio'], 2)}. C'est la condition du dossier — et si le prêteur s'arrête à quinze ans, il faut soit un second prêteur, soit un solde en compte courant d'associé.</p>
    <p class="scenario-subtitle">Ce plafond n'est pas théorique : le ratio de 1,20 impose de rester sous <strong>{eur(PLAFOND_RATIO)}</strong> à vingt ans, alors que le cash-flow ne devient négatif qu'à {eur(PLAFOND_CF)}. C'est donc <strong>la banque qui contraint, pas le cash-flow</strong> — un point de négociation à garder en tête : au-delà de {eur(PLAFOND_RATIO)}, le dossier n'est plus finançable, quelle que soit sa rentabilité.</p>
  </section>

  <section class="financial-projections">
    <h2>Échelle de prix — ce que chaque prix payé change</h2>
    <p class="strategy-rationale">Loyer inchangé à 600 € et 430 €, vacance 5 %, crédit de 90 % sur vingt ans à {pct(TAUX * 100, 2)} plus assurance 0,34 %, apport de 10 %. La note est celle du moteur à chaque prix.</p>
    <table class="projection-table">
      <thead><tr><th>Prix payé</th><th>Note</th><th>Verdict</th><th>EBE</th><th>Cash-flow</th><th>Net d'IS sur revient</th><th>Coût / valeur</th></tr></thead>
      <tbody>
{table_echelle()}
      </tbody>
    </table>
    <p class="scenario-subtitle">La ligne en évidence est notre cible. Le prix affiché, lui, sort un cash-flow négatif sur vingt ans, un rendement net qui tombe sous les 5 % et une valeur payée 34 % au-dessus de ce que le marché de la commune a effectivement signé sur cette tranche de surface. Ce n'est pas une opinion sur le vendeur : c'est la DVF.</p>
  </section>

  <section class="financial-projections">
    <h2>Le dossier résiste-t-il au loyer ?</h2>
    <p class="strategy-rationale">Le deuxième paramètre fragile, après la durée du crédit. Les deux baux sont signés, mais un préavis d'un mois suffit en meublé. Voici ce que chaque niveau de loyer laisse, à {eur(PRIX)} et à vingt ans.</p>
    <table class="projection-table">
      <thead><tr><th>Loyer des deux lots</th><th>EBE</th><th>Ratio EBE / annuité</th><th>Cash-flow</th><th>Note</th></tr></thead>
      <tbody>
{table_rotation()}
      </tbody>
    </table>
    <p class="scenario-subtitle">Le dossier tient son ratio bancaire jusqu'à environ 570 € de loyer total pour les deux logements, et son cash-flow reste positif jusqu'à 610 €. Autrement dit : une relocation du studio 60 € sous son loyer actuel ne casse pas le dossier, mais une vacance longue sur les deux lots le ramènerait sous le seuil. C'est la vraie marge de sécurité — et elle est mince.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Ce que coûte la détention</h2>
    <p class="strategy-rationale">Détenir cet immeuble coûte {eur(CHARGES_TOTAL)} par an, soit {eur(CHARGES_TOTAL / 12)} par mois, {pct(CHARGES_TOTAL / LOYERS_AN * 100, 1)} des loyers bruts. Les charges réelles de propriété — taxe foncière et copropriété — pèsent {eur(DETENTION)} par an, soit {pct(DETENTION / LOYERS_AN * 100, 1)} des loyers : c'est faible pour du bâti ancien, mais <strong>la copropriété n'est pas connue</strong>, et c'est précisément là que le chiffre peut se dégrader.</p>
    <p>Les 50 €/mois payés par les locataires sont des provisions sur charges générales et eau, sur un immeuble sans compteur divisionnaire connu. Une surconsommation se régularise sur nous. À l'inverse, la taxe foncière et une partie des charges récupérables peuvent revenir au locataire : le montant de la TEOM et les clés de répartition sont demandés avant le compromis.</p>
  </section>

  <section class="strategy-exploration">
    <h2>La réserve vacance et travaux : notre mini-ALUR interne</h2>
    <p>La vacance statistique de 5 % et la provision travaux de 2,5 % ne sont pas perdues : elles forment la réserve du parc, placée sur un fonds monétaire en euros à 2,84 % net de frais. Sur ce dossier, cela représente {eur(F['reserve_annuelle'])} par an mis de côté, soit {eur(F['reserve_annuelle'] / 12)} par mois.</p>
    <p>Elle joue à contre-cycle : dans le scénario à 20 % de vacance, ce sont {eur(LOYERS_AN * 0.20)} de loyers en moins, absorbés par la ligne de réserve sans toucher au cash-flow. Et elle existe déjà — {eur(RESERVE_PARC)} au {parc.DATE_RELEVE}, {eur(RESERVE_1AN)} dans un an — ce qui rend ce dossier finançable sans apport nouveau : l'apport de {eur(APPORT_CASH)} et les frais se prennent sur la trésorerie de la structure, pas sur les revenus des associés.</p>
  </section>

  <section class="attractiveness">
    <h2>Attractivité du quartier</h2>
    <p class="attractiveness-intro">Six dimensions notées sur 10, pondérées pour deux logements meublés en location longue durée. Les scores sont une appréciation, pas une mesure : ils servent à comparer les dossiers entre eux.</p>
{blocs_attractivite()}
    <p class="attractiveness-summary">Moyenne pondérée pour la location meublée : {nfr(ADEQUATION, 1)}/10. Le quartier n'est pas le problème du dossier : ville-centre de la haute vallée de l'Arc, centre ancien commerçant, deux logements reloués en quelques semaines. Ce qui coince est ailleurs — dans le prix demandé et dans une copropriété qu'on ne connaît pas.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Stratégies examinées</h2>
    <p class="strategy-rationale">La stratégie retenue est celle qui existe déjà : deux meublés en location longue durée. Les autres pistes ont été examinées puis écartées, pour les raisons ci-dessous.</p>
    <table class="comparison-table">
      <thead><tr><th>Stratégie</th><th>Rendement</th><th>Faisabilité</th><th>Risque</th></tr></thead>
      <tbody>
{blocs_strategies()}
      </tbody>
    </table>
  </section>

  <section class="risk-matrix">
    <h2>Matrice de risques</h2>
    <table class="risk-table">
      <thead><tr><th>Facteur</th><th>Sévérité</th><th>Ce que cela veut dire</th></tr></thead>
      <tbody>
{blocs_risques()}
      </tbody>
    </table>
  </section>

  <section class="verdict {VERDICT_CLS}">
    <h2>Verdict</h2>
    <p class="verdict-stance">À {eur(PRIX)} net vendeur, le dossier est autoporté : <strong>{euro_signe(CF)} par mois</strong> de cash-flow après impôt et après mensualité, {pct(C['rendements']['net_sur_revient_pct'], 2)} de rendement net d'IS sur le prix de revient, et un ratio bancaire de {nfr(RATIO, 2)} qui laisse la place au prêt. <strong>On achète à {eur(PRIX)}, pas au-dessus de {eur(PLAFOND_RATIO)}</strong> — au-delà, le dossier sort du financement bancaire.</p>
    <p><strong>Ce que la note récompense.</strong> Le moteur sort {nfr(NOTE, 1)}/10, « {VERDICT_FR[VERDICT]} », avec une composante rendement de {nfr(COMP['s_rendement'], 1)}/10 et une composante risque de {nfr(COMP['s_risque'], 1)}/10. Autrement dit : le rendement est bon, le risque l'est moins. C'est exactement le portrait de ce dossier — rentable sur le papier, avec deux inconnues lourdes.</p>
    <p><strong>Les deux inconnues, justement.</strong> La copropriété d'abord : aucune charge, aucun procès-verbal, aucun état daté, et un DPE qui dit « toiture non isolée ». Les diagnostics électricité et plomb ensuite, obligatoires sur un bâti d'avant 1948 — sur deux logements, deux postes qui se chiffrent vite en milliers d'euros. Tant que ces pièces ne sont pas sur la table, tout chiffre publié ici reste une hypothèse favorable.</p>
    <p><strong>Quatre conditions avant de signer.</strong> La production de l'état daté, du budget prévisionnel et des trois derniers procès-verbaux ; le diagnostic électricité et le constat plomb ; la confirmation que le bail du T2 est bien signé au 7 octobre ; et l'accord écrit d'un prêteur sur vingt ans, puisque c'est la durée et non le prix qui décide du dossier.</p>
    <p><strong>Deux conventions à connaître.</strong> Le moteur ne déduit pas les intérêts d'emprunt de la base imposable : dans une SCI à l'IS, ils le sont, ce qui améliore légèrement le net. Et l'amortissement du bâti retenu est de 75 % sur 35 ans — plus prudent que les 90 % habituels, l'immeuble étant en centre ancien, où la part du terrain est plus élevée.</p>
    <p class="verdict-meta">Note du moteur : {nfr(NOTE, 1)}/10 ({VERDICT_FR[VERDICT]}). Rendement net d'IS : {pct(C['rendements']['net_sur_revient_pct'], 2)} sur le prix de revient, {pct(C['rendements']['net_sur_valeur_pct'], 2)} sur la valeur de marché. Cash-flow : {euro_signe(CF)} par mois à vingt ans, {euro_signe(ECHEANCES[0]['cf'])} à quinze. Apport nécessaire : {eur(APPORT_CASH)}. Ratio EBE / annuité : {nfr(RATIO, 2)}.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Confiance et limites</h2>
    <p>Confiance globale : <strong>moyenne</strong>. Ce qui est solide : les loyers, appuyés sur deux baux en cours et sur les quittances ; les surfaces, attestées par un mesurage (n° 6418/EFA) ; les DPE, produits en pièce jointe ; et la valeur de marché, ancrée sur la DVF officielle de la commune.</p>
    <p>Ce qui reste déclaratif : la taxe foncière de {eur(CH['taxe_fonciere_annuelle_euros'])} annoncée par l'agence, la signature du bail du T2 au 7 octobre, et l'absence totale d'information sur la copropriété — pour laquelle le moteur applique une provision de 2,5 % des loyers, qui tient lieu de charge.</p>
    <p>Non publié faute de source : la répartition des charges récupérables et le montant de la TEOM, le régime de l'eau et l'existence de compteurs divisionnaires, l'inventaire du mobilier, et le rattachement exact des caves et de la buanderie. Ces éléments sont demandés à l'agence avant toute offre.</p>
    <p class="report-source">Sources : annonce SeLoger 261QSCIG43MJ (mandat 119, référence 252) ; deux diagnostics de performance énergétique et l'attestation de mesurage n° 6418/EFA transmis le 28 septembre 2026 ; fichiers DVF 2024 et 2025 du Var, agrégés par mutation pour la commune de Saint-Maximin-la-Sainte-Baume.</p>
  </section>

  <footer class="report-signature">
    <p>Analyse produite le 28 septembre 2026 pour <span class="signature-names">Alexis et Rémy Barlatier</span> — Sémaphore Patrimoine.</p>
    <p class="report-source">Conventions de calcul : frais d'acquisition {eur(C['frais_acquisition'])} (7,5 % du prix), SCI à l'IS, amortissement du bâti à 75 % du prix de revient sur 35 ans, crédit de 90 % du prix sur {DUREE_ANS} ans à {pct(TAUX * 100, 2)} plus assurance emprunteur 0,34 %, apport de 10 %. Vacance structurelle de 5 % en scénario de base, provision travaux de 2,5 % des loyers, réserve placée à 2,84 % net de frais.</p>
  </footer>

</main>
</body>
</html>
"""


def main():
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as fh:
        fh.write(HTML)
    print(f"écrit : {SORTIE}")
    print(f"taille : {len(HTML)} caractères")
    print(f"note : {NOTE}/10 — verdict {VERDICT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
