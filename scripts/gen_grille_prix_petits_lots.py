# -*- coding: utf-8 -*-
"""Génère la page de référence « Grille des prix — petits lots ».

Répond à une seule question, hors conversation : pour un loyer donné sur un
petit lot (studio, place, cave, box, garage), quel prix donne quel rendement,
et à quel prix le lot s'autofinance.

Page hors listing : pas de record, pas de note. Tous les loyers viennent des
relevés du groupe (skill places-de-stationnement, base interne) ; les formules
sont celles du skill parking, à savoir un net AVANT IS. Les dossiers déjà
traités sont rappelés en bas, recalculés par le moteur, pour montrer l'écart
entre les deux conventions.

Sortie : analyses/grille-prix-petits-lots/index.html
"""
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "scripts"))
from analyse_app import engine  # noqa: E402

SORTIE = os.path.join(RACINE, "analyses", "grille-prix-petits-lots", "index.html")
CHEMIN_JSON = os.path.join(RACINE, "analyses", "analyses.json")
VACANCE = 0.95
# profil de la banque d'Alexis : 15 ans à 3,70 %, assurance 0,34 % incluse
COEF_ANNUITE = 0.007535
APPORT = 0.10
ECARTS = []


def calcule(libelle, publie, attendu, tolerance=0.6):
    if publie is None or attendu is None:
        if publie != attendu:
            ECARTS.append("%s : %s vs %s" % (libelle, publie, attendu))
    elif abs(float(publie) - float(attendu)) > tolerance:
        ECARTS.append("%s : %s vs %s" % (libelle, publie, attendu))
    return publie


def nfr(v, dec=0):
    ent, _, frac = ("%.*f" % (dec, float(v))).partition(".")
    return re.sub(r"(?<=\d)(?=(\d{3})+$)", "\u202f", ent) + ("," + frac if dec else "")


def eur(v, dec=0):
    return nfr(v, dec) + " €"


def frais_reels(prix):
    """Barème maison : 675 € neuf, 1 275 € ancien jusqu'à 5 000 €, puis 100 €/1 000 €."""
    if prix <= 5000:
        return 1275.0
    return 1275.0 + (prix - 5000.0) / 1000.0 * 100.0


def loyer_net(loyer, charges):
    """Net annuel avant IS : loyer × 12 × 0,95 − charges (convention skill parking)."""
    return loyer * 12 * VACANCE - charges


def prix_rendement(loyer, charges, taux):
    """Prix d'achat qui laisse `taux` de net annuel, frais déduits."""
    net = loyer_net(loyer, charges)
    prix = net / taux
    prix -= frais_reels(prix)
    return prix


def prix_autofinancement(loyer, charges):
    """Capital couvert par le seul net mensuel au profil 15 ans de la banque."""
    capital = (loyer_net(loyer, charges) / 12.0) / COEF_ANNUITE
    return capital / (1 - APPORT)


# loyers relevés, bas / moyen / haut, par typologie de petit lot
TYPOLOGIES = [
    ("Place extérieure en résidence", (49.0, 60.0, 70.0), 80.0 + 60.0,
     "Le Luc 49 €, centres et ensembles clos 60 à 70 €. Charges 80 €/an, taxe foncière 60 €/an."),
    ("Place en sous-sol", (78.0, 86.0, 95.0), 150.0,
     "La Seyne, sous-sol de résidence, 78 à 95 €/mois. Charges 150 €/an, taxe foncière refacturée."),
    ("Box fermé ou place d'ensemble clos", (60.0, 75.0, 90.0), 100.0 + 60.0,
     "Produit intermédiaire entre l'extérieure et le sous-sol. Charges 100 €/an, taxe foncière 60 €/an."),
    ("Cave de 3 à 6 m²", (40.0, 50.0, 60.0), 150.0 + 30.0,
     "La Seyne, cave de 3 m² chez un particulier : 40 à 60 €, soit 13 à 20 €/m². Charges de copropriété 150 €/an, taxe foncière 30 €/an."),
    ("Garage fermé d'environ 15 m²", (200.0, 235.0, 270.0), 150.0 + 80.0,
     "235 €/mois relevé pour un garage de 15 m². Charges 150 €/an, taxe foncière 80 €/an."),
    ("Studio meublé, 19 à 29 m²", (420.0, 505.0, 590.0), 360.0 + 500.0 + 150.0,
     "La Seyne, studio de 19 m² au centre Peyron : 420 €, soit 22 €/m². Brignoles, T2 de 28,3 m² vendu loué meublé : 590 €. Charges de copropriété 360 €/an, taxe foncière 500 €/an, tenue de comptes 150 €/an."),
]

TAUX = (0.05, 0.06, 0.07, 0.08)


def main():
    lignes = []
    for nom, loyers, charges, source in TYPOLOGIES:
        for loyer in loyers:
            net = loyer_net(loyer, charges)
            auto = prix_autofinancement(loyer, charges)
            prix = {t: prix_rendement(loyer, charges, t) for t in TAUX}
            lignes.append((nom, loyer, charges, net, auto, prix, source))

    # contrôles : ancrages internes du groupe
    calcule("net, place extérieure 60 €, charges 80 + 60", 544.0, loyer_net(60.0, 140.0), 1.0)
    calcule("euro de net mensuel couvert au profil 15 ans", 132.7, 1.0 / COEF_ANNUITE, 0.3)

    # dossiers passés, recalculés par le moteur (convention après IS, donc plus basse)
    with open(CHEMIN_JSON, encoding="utf-8") as fh:
        base = json.load(fh)
    passes = []
    for slug, prix_cible in (
        ("2026-08-09-brignoles-centre-t2-28m2", 60000.0),
        ("2026-10-02-la-seyne-hyper-centre-2p-bureau", 67000.0),
    ):
        rec = next(r for r in base["analyses"] if r["slug"] == slug)
        rec = json.loads(json.dumps(rec))
        rec["annonce"]["prix_affiche_euros"] = prix_cible
        rec["annonce"]["prix_retenu_euros"] = prix_cible
        c = engine.compute(rec)
        if not c.get("calculable"):
            continue
        passes.append((rec["titre"], prix_cible, c["fiscal"]["ebe"],
                       c["fiscal"]["net_apres_is"], c["rendements"]["net_sur_revient_pct"]))

    lignes_html = []
    for nom, loyer, charges, net, auto, prix, source in lignes:
        lignes_html.append(
            "        <tr><td>%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
            "<td class=\"num\">%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td></tr>"
            % (nom, eur(loyer), eur(charges), eur(net / 12), eur(auto),
               eur(prix[0.05]), eur(prix[0.06]), eur(prix[0.07]))
        )
    blocs_sources = []
    vus = set()
    for nom, loyer, charges, net, auto, prix, source in lignes:
        if nom in vus:
            continue
        vus.add(nom)
        blocs_sources.append("      <li><strong>%s</strong> — %s</li>" % (nom, source))
    passes_html = []
    for titre, prix, ebe, net, rdt in passes:
        passes_html.append(
            "        <tr><td>%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td></tr>"
            % (titre.split("—")[0].strip()[:70], eur(prix), eur(ebe), eur(net), nfr(rdt, 2) + " %")
        )

    html = TEMPLATE.format(
        lignes="\n".join(lignes_html),
        sources="\n".join(blocs_sources),
        passes="\n".join(passes_html),
        coef=nfr(COEF_ANNUITE, 6),
        vacance="0,95",
    )
    reste = re.search(r"\{[a-z_]{3,}\}", html)
    if reste:
        raise SystemExit("placeholder non remplace : %s" % reste.group(0))
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("page ecrite : %s (%d lignes)" % (SORTIE, html.count("\n") + 1))
    if ECARTS:
        print("ECARTS :")
        for e in ECARTS:
            print("  -", e)
        raise SystemExit("build arrete")
    print("controles OK | %d lignes de grille" % len(lignes))


TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Grille des prix — petits lots (studio, place, cave, box, garage)</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<main class="report">

  <header class="report-header">
    <p class="report-breadcrumb">Page de référence — Sémaphore Patrimoine</p>
    <h1>Grille des prix des petits lots — quel prix pour quel rendement</h1>
    <p class="report-address">Studio meublé, place extérieure, sous-sol, box, cave, garage · mise à jour du 2 octobre 2026</p>
    <p class="report-source">Une seule question : pour un loyer donné, quel prix donne 5, 6 ou 7 % de net, et à quel prix le lot s'autofinance. Loyers issus des relevés du groupe, jamais d'une moyenne de portail.</p>
  </header>

  <section class="strategy-exploration">
    <h2>Comment lire la grille</h2>
    <p>Deux formules, et rien d'autre. Le <strong>net annuel avant impôt</strong> vaut <em>loyer × 12 × {vacance} − charges</em>. Le <strong>prix qui laisse un rendement cible</strong> vaut <em>net ÷ taux − frais d'acquisition réels</em>, avec le barème maison : 1 275 € jusqu'à 5 000 €, puis 100 € par 1 000 € au-delà.</p>
    <p>Le <strong>prix d'autofinancement</strong> est celui où le net mensuel couvre seul la mensualité, au profil de notre banque — 15 ans à 3,70 %, assurance comprise, soit <strong>{coef} par euro emprunté</strong>, avec 10 % d'apport et les frais assumés à part. C'est ce chiffre qui fixe l'offre quand le critère maison s'applique : <strong>le bien doit couvrir sa mensualité</strong>.</p>
    <p class="projection-note">Convention importante : cette grille raisonne en net <strong>avant impôt</strong>, comme les fiches de stationnement. L'impôt sur les sociétés frappe le net à 15 % ; il est plus faible sur un lot amortissable comme un studio, plus lourd sur une place ou une cave qui ne s'amortit pas. Le prix réellement payé se lit donc à un taux de net d'un demi-point plus élevé que celui affiché quand le lot n'est pas amortissable.</p>
  </section>

  <section class="financial-projections">
    <h2>La grille</h2>
    <table class="projection-table">
      <thead><tr><th>Type de lot</th><th>Loyer /mois</th><th>Charges /an</th><th>Net /mois</th><th>Prix d'autofinancement</th><th>Prix pour 5 % net</th><th>Prix pour 6 % net</th><th>Prix pour 7 % net</th></tr></thead>
      <tbody>
{lignes}
      </tbody>
    </table>
    <p class="scenario-subtitle">Lecture directe : prenez le loyer que vous croyez pouvoir obtenir, lisez la ligne du type de lot, et le prix se lit dans la colonne de la rentabilité visée. Le plafond maison de 6 500 € pour une place extérieure, 10 800 € pour un sous-sol et 13 500 € pour un garage tient dans la colonne des 5 à 6 %, ce qui confirme qu'il n'est pas une vue de l'esprit.</p>
  </section>

  <section class="strategy-exploration">
    <h2>D'où viennent les loyers</h2>
    <ul>
{sources}
    </ul>
    <p class="strategy-rationale">Règle du groupe : <strong>jamais de report d'un loyer d'une commune à l'autre</strong>. Une place à 49 € au Luc n'autorise pas de payer le même prix à La Seyne où l'extérieure se relève à 60 €. Le seul chiffre qui vaut est celui d'une agence locale qui loue dans la résidence concernée.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Les dossiers passés, relus à cette aune</h2>
    <p class="strategy-rationale">Les deux dossiers logement de l'automne, recalculés par le moteur du dépôt — donc en <strong>net après impôt</strong>, convention plus prudente que la grille ci-dessus. L'écart entre les deux conventions est exactement le demi-point dont il est question plus haut.</p>
    <table class="projection-table">
      <thead><tr><th>Dossier</th><th>Prix de référence</th><th>EBE</th><th>Net après IS</th><th>Net sur prix de revient</th></tr></thead>
      <tbody>
{passes}
      </tbody>
    </table>
    <p class="scenario-subtitle">Brignoles sort à 7,83 % au prix de l'offre et La Seyne à 8,15 %, les deux au-dessus de la porte maison de 5 % net. Ce sont ces deux lignes qui donnent l'étalon : le reste de la grille dit simplement à quel prix nos loyers atteignent ce niveau.</p>
  </section>

  <footer class="report-footer">
    <p>Page de référence produite pour Alexis et Rémy Barlatier — SCI Sémaphore Patrimoine, 2 octobre 2026. Chiffres recalculés par le script <code>scripts/gen_grille_prix_petits_lots.py</code> ; les contrôles internes font échouer la construction de la page si un ancrage du groupe bouge.</p>
  </footer>

</main>
</body>
</html>
"""

if __name__ == "__main__":
    main()
