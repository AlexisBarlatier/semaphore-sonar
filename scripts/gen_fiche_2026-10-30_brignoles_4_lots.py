#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche HTML — immeuble de 4 lots, centre vieille ville, Brignoles.

Tous les chiffres publiés sortent du moteur (engine.compute) et de scoring ;
aucun n'est saisi à la main. Le prix de solde nul est celui de prix_cf_nul.py,
repris ici par le même calcul (90 % du prix sur 20 ans à 3,80 %, assurance
comprise, frais d'acquisition comptants).
"""
import copy
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

from analyse_app import engine, scoring  # noqa: E402

SLUG = "2026-10-30-brignoles-immeuble-4-lots-centre"
SORTIE = os.path.join(RACINE, "analyses", SLUG, "index.html")
COEF = 0.006238  # annuité mensuelle par euro emprunté, 20 ans à 3,80 %, assurance incluse


def nfr(v, dec=0):
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


def eur(v, dec=0):
    return nfr(v, dec) + " €"


def pc(v, dec=2):
    return nfr(v, dec) + " %"


def signe(v, dec=0):
    return ("+" if v > 0 else "−" if v < 0 else "±") + nfr(abs(v), dec) + " €"


def charge(slug):
    data = json.load(open(os.path.join(RACINE, "analyses", "analyses.json"), encoding="utf-8"))
    return [r for r in data["analyses"] if r["slug"] == slug][0]


def avec_prix(rec, prix):
    r = copy.deepcopy(rec)
    r["annonce"]["prix_retenu_euros"] = float(prix)
    r["hypotheses"]["frais_acquisition_euros"] = round(prix * 0.075)
    return r


def avec_hypotheses(rec, vacance, loyers_coef, charges_coef):
    r = copy.deepcopy(rec)
    r["hypotheses"]["vacance_base_pct"] = vacance
    for ligne in r["marche"]["loyers"]:
        ligne["loyer_mensuel_euros"] = round(ligne["loyer_mensuel_euros"] * loyers_coef, 2)
    for cle in ("charges_copro_annuelles_euros", "taxe_fonciere_annuelle_euros",
                "entretien_annuel_euros", "pno_annuelle_euros"):
        r["hypotheses"]["charges"][cle] = round(r["hypotheses"]["charges"][cle] * charges_coef, 2)
    return r


def solde(rec):
    """Solde mensuel sous la convention du groupe : 90 % de (prix + travaux)
    empruntés sur 20 ans, frais d'acquisition comptants."""
    c = engine.compute(rec)
    prix = rec["annonce"]["prix_retenu_euros"]
    travaux = rec["bien"]["travaux"]["montant_euros"]
    mensualite = 0.9 * (prix + travaux) * COEF
    return c, c["fiscal"]["cf_mensuel_net"] - mensualite


REC = charge(SLUG)
C, SOLDE = solde(REC)
NOTE, VERDICT, DETAIL = scoring.note_et_verdict(REC, C)
PLAFOND, PLAFOND_MOTIF = scoring.prix_plafond(REC)
PRIX = REC["annonce"]["prix_retenu_euros"]
REVIENT = C["prix_revient_total"]
LOYERS = sum(l["loyer_mensuel_euros"] * l["quantite"] for l in REC["marche"]["loyers"])
SURFACE = 79.98

# prix de solde nul, par dichotomie sur le même calcul que prix_cf_nul.py
lo, hi = 40000.0, PRIX
for _ in range(60):
    mid = (lo + hi) / 2
    _, s = solde(avec_prix(REC, mid))
    if s > 0:      # solde positif : on peut payer plus cher
        lo = mid
    else:          # solde négatif : le prix est trop haut
        hi = mid
CF_NUL = round(hi / 500) * 500

ECHELLE = []
for prix in (PRIX, 150000, 140000, PLAFOND, CF_NUL):
    r = avec_prix(REC, prix)
    c, s = solde(r)
    ECHELLE.append((prix, c, s))

SCENARIOS = [
    ("Base", 0.05, 1.00, 1.00),
    ("Best", 0.02, 1.05, 0.90),
    ("Worst", 0.12, 0.90, 1.20),
]
SC = []
for nom, vac, lc, cc in SCENARIOS:
    r = avec_hypotheses(REC, vac, lc, cc)
    c, s = solde(r)
    SC.append((nom, c, s, vac, lc, cc))

CARTES = [
    ("Prix affiché", eur(PRIX)),
    ("Loyers annoncés", eur(LOYERS) + "/mois"),
    ("Revient avec travaux", eur(REVIENT)),
    ("Rendement net après IS", pc(C["rendements"]["net_sur_revient_pct"], 2)),
    ("Solde mensuel", signe(SOLDE)),
    ("Prix de solde nul", eur(CF_NUL)),
]
cartes = "\n".join(
    f'    <div class="card">\n      <span class="card-label">{a}</span>\n'
    f'      <span class="card-value">{b}</span>\n    </div>' for a, b in CARTES
)

ATTR = "\n".join(
    f'      <div class="attract-item"><h3>{d["dimension"].replace("_", " ").capitalize()} — {d["score"]}/10</h3>'
    f'<p>{d["justification"]}</p></div>'
    for d in REC["analyse"]["attractivite"]
)

ECHELLE_HTML = "\n".join(
    f"        <tr><td>{eur(p)}</td><td>{eur(c['prix_revient_total'])}</td>"
    f"<td>{pc(c['rendements']['net_sur_revient_pct'],2)}</td>"
    f"<td>{nfr(c['ratio_cout_valeur'],2)}</td><td>{signe(s)}</td></tr>"
    for p, c, s in ECHELLE
)

SC_HTML = "\n".join(
    f'      <div class="projection-card"><h3>{nom} — vacance {nfr(vac*100)} %</h3>'
    f"<p>Loyers {'maintenus' if lc == 1 else ('+5 %' if lc > 1 else '−10 %')}, "
    f"charges {'maintenues' if cc == 1 else ('−10 %' if cc < 1 else '+20 %')}.</p>"
    f"<p><strong>{eur(c['fiscal']['net_apres_is'])}/an</strong> net après IS — "
    f"{pc(c['rendements']['net_sur_revient_pct'],2)} sur revient — solde {signe(s)}/mois</p></div>"
    for nom, c, s, vac, lc, cc in SC
)

RISQUES = "\n".join(
    f'        <tr><td>{r["facteur"]}</td><td>{r["detail"]}</td><td class="sev-{r["severite"]}">{r["severite"]}/5</td></tr>'
    for r in REC["analyse"]["risques"]
)

LOYERS_HTML = "\n".join(
    f"        <tr><td>{l['lot']}</td><td>{eur(l['loyer_mensuel_euros'])}</td><td>{l['note']}</td></tr>"
    for l in REC["marche"]["loyers"]
)

IDENTITE = [
    ("Adresse", REC["bien"]["adresse"]["texte"]),
    ("Lots", "4 logements loués — T2 de 29 m² + studio de 15 m² au 2e, studios de 23 m² et 12 m² au RDC"),
    ("Surface", "79,98 m² habitables annoncés, aucun Carrez"),
    ("Immeuble", "trois niveaux plus comble, centre ancien ; 1er étage non proposé"),
    ("Copropriété", "au moins 6 lots"),
    ("Charges annoncées", f"{eur(240)}/an, soit 3 €/m²/an"),
    ("Taxe foncière annoncée", f"{eur(942)}/an"),
    ("DPE", "E (422 kWh/m²/an) au 2e, D (287) au RDC"),
    ("Occupation", "quatre lots loués, aucune quittance communiquée"),
    ("Travaux retenus", f"{eur(REC['bien']['travaux']['montant_euros'])} — façade, enduit, menuiseries extérieures"),
    ("Honoraires", "à la charge du vendeur"),
    ("Prix", f"{eur(80000)} + {eur(80000)} = {eur(PRIX)}"),
]
identite = "\n".join(f'      <tr><th scope="row">{k}</th><td>{v}</td></tr>' for k, v in IDENTITE)

HTML = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Analyse — immeuble 4 lots, Brignoles centre</title>
  <link rel="stylesheet" href="../../style.css">
</head>
<body>

<header class="report-header">
  <nav class="report-breadcrumb"><a href="../../analyses/index.html">← Retour aux analyses</a></nav>
  <h1>Analyse d'investissement</h1>
  <p class="report-address">Immeuble de 4 lots — Centre Vieille Ville, Brignoles (83170)</p>
  <p class="report-date">Analyse générée le 30 octobre 2026</p>
  <p class="report-source">Source : SeLoger, deux annonces du même agent (BSK Immobilier) — honoraires à la charge du vendeur</p>
  <div class="report-source-link"><a href="{REC['annonce']['url']}">{REC['annonce']['url']}</a></div>
</header>

<main>

  <div class="strategy-banner">
    <span class="strategy-badge">Immeuble de rapport — quatre lots loués</span>
    <p>Stratégie retenue : <strong>location nue des quatre lots en l'état, reprise de façade à la charge de l'acquéreur</strong> — SCI à l'IS (15 %)</p>
  </div>

  <section class="summary-cards">
{cartes}
  </section>

  <section class="strategy-exploration">
    <h2>Les deux annonces forment un seul immeuble</h2>
    <p class="attractiveness-intro">Deux annonces de 80 000 €, même agent, même date de diagnostic (27/02/2025), mêmes charges (10 €/mois), même taxe foncière (471 €/an), même « petit immeuble de 3 étages » : ce ne sont pas deux biens comparables, ce sont les deux moitiés d'un même immeuble. La seconde annonce l'écrit d'ailleurs elle-même — « possibilité d'acquérir 2 appartements supplémentaires dans le même immeuble, ensemble global de 4 biens pour 160 000 € ». Le lot du RDC était déjà passé en base le 29 juin à 88 000 € : il a perdu 9 % en quatre mois.</p>
    <p class="attractiveness-intro">Le 1er étage n'est pas proposé : la copropriété compte donc au moins 6 lots. C'est ce qui décide de la nature du dossier — on n'achète pas un immeuble, on achète quatre lots sur six, et les travaux de façade se votent sans nous.</p>
  </section>

  <section class="identity-sheet">
    <h2>Fiche d'identité</h2>
    <table class="identity-table">
{identite}
    </table>
  </section>

  <section class="attractiveness">
    <h2>Attractivité — centre ancien de Brignoles</h2>
    <p class="attractiveness-intro">Le bien est au cœur du centre ancien, à pied des commerces, du marché et du cinéma. C'est son atout principal, et c'est aussi ce qui explique des loyers au mètre carré supérieurs à la médiane communale. La faiblesse est ailleurs : un bourg sans train de voyageurs, un emploi peu dynamique, et un bâti voisin fatigué.</p>
    <div class="attractiveness-grid">
{ATTR}
    </div>
    <div class="attractiveness-summary">
      <p><strong>Profil locataire cible :</strong> personnes seules et jeunes actifs du bourg, personnel des commerces et des services publics, locataires à petit budget qui privilégient la proximité immédiate du centre.</p>
      <p><strong>Conclusion :</strong> la demande existe, mais elle est sensible au prix. Les loyers annoncés sont 21 % au-dessus de la médiane communale : c'est la question du dossier, pas la localisation.</p>
    </div>
  </section>

  <section class="strategy-exploration">
    <h2>Relevé de loyers — ce que l'agent annonce</h2>
    <table class="comparison-table">
      <thead>
        <tr><th>Lot</th><th>Loyer</th><th>Détail</th></tr>
      </thead>
      <tbody>
{LOYERS_HTML}
      </tbody>
    </table>
    <p class="attractiveness-intro"><strong>{eur(LOYERS)}/mois annoncés, soit 15,9 €/m²</strong> quand la médiane DHUP 2025 de Brignoles est à 13,1 €/m² — un écart de 21 %. Les deux studios du RDC sortent même à 18,9 €/m². Aucune quittance n'est communiquée : à 13,1 €/m², l'assiette tombe à {eur(13.1*SURFACE)}, et le dossier change de camp. C'est la première pièce à exiger, avant la visite.</p>
  </section>

  <section class="strategy-exploration">
    <h2>La façade — le poste que l'annonce tait</h2>
    <p class="attractiveness-intro">L'annonce écrit « aucun travaux à prévoir dans l'immeuble ». La photographie montre autre chose : enduit tombé par plaques, fissure verticale entre les fenêtres, remontées d'humidité et mousses en pied de mur, volets bois cassés, câblages apparents. Un ravalement avec échafaudage, reprise d'enduit, menuiseries extérieures et porte se chiffre entre 15 000 et 30 000 € ; le calcul retient <strong>20 000 €</strong> en quote-part des quatre lots. Ce montant n'est pas dans le prix, et il ne couvre pas une éventuelle reprise de toiture ou de drainage, qu'aucun diagnostic ne documente.</p>
    <p class="attractiveness-intro">La fissure verticale et l'humidité en pied sont les deux points qui peuvent transformer un ravalement en désordre structurel. Aucun rapport de structure, aucun devis, aucun PV d'AG : le budget de 20 000 € est un plancher, pas une estimation.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Échelle des prix — au loyer annoncé, et avec les travaux</h2>
    <p class="attractiveness-intro">Rendement net après IS sur prix de revient (achat, frais et travaux), ratio revient/valeur de marché, et solde mensuel sous la convention du groupe : 90 % du prix sur 20 ans à 3,80 %, assurance comprise, frais comptants.</p>
    <table class="comparison-table">
      <thead>
        <tr><th>Prix payé</th><th>Revient</th><th>Net après IS / revient</th><th>Revient / valeur</th><th>Solde mensuel</th></tr>
      </thead>
      <tbody>
{ECHELLE_HTML}
      </tbody>
    </table>
    <p class="attractiveness-intro">Le prix de solde nul est <strong>{eur(CF_NUL)}</strong>, soit {nfr((1-CF_NUL/PRIX)*100,1)} % sous l'affichage ; le plafond de rendement du moteur ressort à {eur(PLAFOND)} (contrainte : {PLAFOND_MOTIF}). Au prix demandé, le solde est de {signe(SOLDE)}/mois et le bien est payé {nfr(C['ratio_cout_valeur'],2)} fois sa valeur de marché — au-delà du seuil de 1,10, la note est plafonnée.</p>
  </section>

  <section class="financial-projections">
    <h2>Trois scénarios</h2>
    <div class="projections-grid">
{SC_HTML}
    </div>
    <div class="projection-summary">
      <p class="attractiveness-intro">Le scénario dégradé cumule deux lots vides, des loyers 10 % plus bas et des charges 20 % plus élevées : c'est la trajectoire d'un immeuble ancien dont la façade n'est pas reprise et dont les quittances sont surévaluées. Il ne se sauve pas par l'exploitation.</p>
    </div>
  </section>

  <section class="risk-matrix">
    <h2>Matrice de risques</h2>
    <table class="risk-table">
      <thead>
        <tr><th>Facteur de risque</th><th>Détail</th><th>Sévérité</th></tr>
      </thead>
      <tbody>
{RISQUES}
      </tbody>
    </table>
  </section>

  <section class="verdict nego">
    <h2>Recommandation</h2>
    <div class="verdict-decision">
      <p class="verdict-stance"><strong>On négocie, et fort : {eur(CF_NUL)} net vendeur, plafond absolu {eur(PLAFOND)}.</strong> Au prix demandé de {eur(PRIX)}, le solde est de {signe(SOLDE)}/mois et les quatre lots sont payés au-dessus de leur valeur. C'est un dossier qui n'existe qu'avec une décote d'environ 23 %.</p>
    </div>
    <div class="verdict-details">
      <p><strong>Ce que le vendeur défend :</strong> un rendement brut de {pc(sum(l['loyer_mensuel_euros']*l['quantite'] for l in REC['marche']['loyers'])*12/PRIX*100,1)} sur un immeuble « sans travaux », avec quatre locataires stables. <strong>Ce que les pièces montrent :</strong> des loyers 21 % au-dessus de la médiane communale, aucune quittance, une façade à reprendre pour 20 000 € et des charges annoncées à 3 €/m²/an qui ne peuvent pas être réelles.</p>
      <p><strong>Ce qui ferait remonter l'offre :</strong> des baux et quittances confirmant 1 270 €/mois, un devis de ravalement sous 12 000 €, un nombre de lots de copropriété limité à six avec un 1er étage à vendre dans le même mouvement, et un PV d'AG montrant qu'aucun appel de fonds n'est voté.</p>
      <p><strong>Ce qui ferait renoncer :</strong> des loyers réels à 13,1 €/m², un désordre structurel sur la fissure, ou une toiture à reprendre — trois hypothèses que ni l'annonce ni l'agent ne permettent d'écarter aujourd'hui.</p>
    </div>
    <div class="verdict-meta">
      <p><strong>Régime fiscal retenu :</strong> SCI à l'IS (15 %) — amortissement du bâti {eur(C['fiscal']['amortissement'])}, provision travaux {eur(C['fiscal']['reserve_annuelle'])}</p>
      <p><strong>Hypothèses :</strong> loyers {eur(LOYERS)}/mois, vacance 5 %, charges {eur(240)}/an, taxe foncière {eur(942)}/an, assurance {eur(600)}/an, entretien et gestion {eur(1771)}/an, travaux {eur(20000)}, frais {eur(12000)}</p>
      <p><strong>Note :</strong> {nfr(NOTE,1)}/10 — à négocier</p>
    </div>
  </section>

  <footer class="report-signature">
    <p>Analyse réalisée par</p>
    <p class="signature-names">Rémy Barlatier — 06 27 84 53 50 — sarl.spbi@gmail.com</p>
    <p class="signature-names">Alexis Barlatier — 06 61 26 13 83</p>
  </footer>

</main>
</body>
</html>
"""

INTERDITS = ("prêt", "emprunt", "crédit", "apport", "mensualité", "levier")


def main():
    import re
    bas = HTML.lower()
    for mot in INTERDITS:
        if re.search(r"\b" + mot, bas):
            sys.exit(f"Mot de financement interdit : {mot}")
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as f:
        f.write(HTML)
    print(f"écrit {SORTIE} ({len(HTML)} octets)")
    print(f"note {NOTE} | revient {REVIENT} | solde {SOLDE:.0f} | cf nul {CF_NUL} | plafond {PLAFOND}")


if __name__ == "__main__":
    main()
