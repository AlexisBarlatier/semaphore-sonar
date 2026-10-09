# -*- coding: utf-8 -*-
"""Fiche « Toulon Aguillon — T4 73 m², potentiel colocation ».

Tous les chiffres sont calculés ici. Le loyer n'étant pas annoncé, la fiche
raisonne en grille : location nue contre colocation, sur le relevé de marché
réellement effectué le 8 octobre 2026.

Sortie : analyses/2026-10-08-toulon-aguillon-t4-73m2/index.html
"""
import os
import re

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "analyses", "2026-10-08-toulon-aguillon-t4-73m2", "index.html")

PRIX = 150360.0 * 0.90   # scénario de négociation : 10 % sous le prix affiché, soit 135 324 €
SURF = 73.37
CHARGES = 960.0
TF = 1200.0          # hypothese, non communiquee
FRAIS = 0.08
VACANCE = 0.95
IS = 0.15
COEF20 = 0.006238    # 20 ans a 3,80 %, assurance comprise
APPORT = 0.10
CHAMBRES = 3
PRIX_M2_TOULON_T4 = 2901.0   # moyenne T4 et plus a Toulon (Capital, 2026)


def nfr(v, dec=0):
    ent, _, frac = ("%.*f" % (dec, float(v))).partition(".")
    return re.sub(r"(?<=\d)(?=(\d{3})+$)", "\u202f", ent) + (("," + frac) if dec else "")


def eur(v, dec=0):
    return nfr(v, dec) + " €"


ACTE = PRIX * (1 + FRAIS)
MENSU = ACTE * (1 - APPORT) * COEF20


def scenario(loyer):
    ebe = loyer * 12 * VACANCE - CHARGES - TF
    net = ebe * (1 - IS)
    return dict(loyer=loyer, ebe=ebe, net=net, net_m=net / 12,
                brut=loyer * 12 / PRIX * 100, net_acte=net / ACTE * 100,
                cf=net / 12 - MENSU, ratio=ebe / (MENSU * 12),
                brut_m2=loyer * 12 / 12 / SURF)


def loyer_cible(taux):
    return (taux * ACTE / (1 - IS) + CHARGES + TF) / 12 / VACANCE


def main():
    nu = [scenario(l) for l in (950.0, 1100.0)]
    coloc = [scenario(3 * c) for c in (400.0, 420.0, 450.0, 470.0, 490.0)]
    seuils = [(t, loyer_cible(t)) for t in (0.05, 0.06, 0.07)]

    def lignes(scs, par_chambre=False):
        out = []
        for s in scs:
            lab = ("3 × %s" % eur(s["loyer"] / CHAMBRES)) if par_chambre else eur(s["loyer"])
            out.append(
                "        <tr><td>%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
                "<td class=\"num\">%s %%</td><td class=\"num\">%s %%</td>"
                "<td class=\"num\">%s</td><td class=\"num\">%.2f</td></tr>"
                % (lab, eur(s["loyer"]), eur(s["net_m"]), nfr(s["brut"], 2),
                   nfr(s["net_acte"], 2),
                   ("%+.0f €" % s["cf"]).replace("-", "−"), s["ratio"]))
        return "\n".join(out)

    lignes_nu = lignes(nu)
    lignes_coloc = lignes(coloc, par_chambre=True)
    lignes_seuil = "\n".join(
        "        <tr><td>%d %% net sur acte</td><td class=\"num\">%s / mois</td>"
        "<td class=\"num\">%s</td><td class=\"num\">%s</td></tr>"
        % (t * 100, eur(l), eur(l / CHAMBRES) + " / chambre",
           eur(l / SURF, 1) + " / m²")
        for t, l in seuils)

    coloc450 = scenario(3 * 450.0)
    coloc470 = scenario(3 * 470.0)
    nu950 = nu[0]

    html = TEMPLATE.format(
        prix=eur(PRIX), surf=nfr(SURF, 2), pm2=eur(PRIX / SURF),
        acte=eur(ACTE), mens=eur(MENSU), charges=eur(CHARGES), tf=eur(TF),
        m2_toulon=eur(PRIX_M2_TOULON_T4), decote=nfr((1 - (PRIX / SURF) / PRIX_M2_TOULON_T4) * 100, 0),
        lignes_nu=lignes_nu, lignes_coloc=lignes_coloc, lignes_seuil=lignes_seuil,
        coloc450_net=eur(coloc450["net_m"]), coloc450_pct=nfr(coloc450["net_acte"], 2),
        coloc450_cf=("%+.0f €" % coloc450["cf"]).replace("-", "−"), coloc450_ratio=nfr(coloc450["ratio"], 2),
        coloc470_net=eur(coloc470["net_m"]), coloc470_pct=nfr(coloc470["net_acte"], 2),
        coloc470_cf=("%+.0f €" % coloc470["cf"]).replace("-", "−"),
        nu950_net=eur(nu950["net_m"]), nu950_pct=nfr(nu950["net_acte"], 2),
        nu950_cf=("%+.0f €" % nu950["cf"]).replace("-", "−"), nu950_ratio=nfr(nu950["ratio"], 2),
        ch_ratio=nfr(CHARGES / (3 * 450.0 * 12) * 100, 1),
        seuil5=eur(seuils[0][1]), seuil5_ch=eur(seuils[0][1] / CHAMBRES),
    )
    reste = re.search(r"\{[a-z_0-9]{3,}\}", html)
    if reste:
        raise SystemExit("placeholder non remplace : %s" % reste.group(0))
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("fiche ecrite : %s (%d lignes)" % (SORTIE, html.count("\n") + 1))
    for lab, s in (("nu 950", nu950), ("coloc 3x450", coloc450), ("coloc 3x470", coloc470)):
        print("  %-12s net %4.0f EUR/mois | net/acte %4.2f %% | CF %+.0f | ratio %.2f"
              % (lab, s["net_m"], s["net_acte"], s["cf"], s["ratio"]))


TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Toulon Aguillon — T4 73 m², potentiel colocation</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<main class="report">

  <header class="report-header">
    <p class="report-breadcrumb">Analyse — Sémaphore Patrimoine</p>
    <h1>Toulon Aguillon — T4 de 73,37 m², potentiel colocation</h1>
    <p class="report-address">Toulon (83000), quartier Aguillon · 4 pièces, 3 chambres, 1er étage avec ascenseur · terrasse · DPE E</p>
    <p class="report-source">Source : SeLoger, réf. 268HPZBNXGLW. Prix affiché <strong>150 360 €</strong>. <strong>Cette fiche est calculée sur un scénario de négociation : 135 324 €, soit 10 % sous le prix affiché.</strong> Aucun loyer n'étant annoncé par le vendeur, la fiche raisonne en grille, à partir du relevé de marché réalisé le 8 octobre 2026.</p>
  </header>

  <section class="strategy-exploration">
    <h2>Le bien</h2>
    <p>Trois chambres dont <strong>une avec dressing et balcon privatif</strong>, pièce de vie ouverte sur terrasse, cuisine ouverte équipée, salle d'eau et WC indépendant. Ascenseur, exposition lumineuse. <strong>Charges de copropriété de {charges}/an</strong> pour 77 lots — c'est un point fort du dossier. <strong>Pas de cave</strong>, et la fiche est contradictoire sur le balcon (« chambre avec balcon privatif » d'un côté, « pas de balcon » dans les caractéristiques de l'autre) : à vérifier.</p>
    <p class="projection-note"><strong>DPE E</strong>, GES B, facture énergétique annoncée entre 1 465 et 1 981 €/an. L'interdiction de louer porte sur les logements E en 2034 : ce n'est pas une urgence, mais c'est un bien dont le coût de chauffage pèsera sur le locataire.</p>
  </section>

  <section class="financial-projections">
    <h2>Les chiffres d'entrée</h2>
    <p>Acte en main <strong>{acte}</strong> (frais à 8 %), mensualité sur 20 ans à 3,80 % assurance comprise : <strong>{mens}</strong>. La taxe foncière n'est pas communiquée : elle est prise ici à <strong>{tf}/an</strong>, à confirmer par l'avis d'imposition.</p>
    <p class="strategy-rationale">Le prix au m² ressort à {pm2}. <strong>La moyenne des T4 et plus à Toulon est de {m2_toulon}/m²</strong> : le bien est <strong>{decote} % en dessous</strong>. C'est cette décote qui rend l'opération possible, et c'est elle qui porte tout le dossier.</p>
  </section>

  <section class="financial-projections">
    <h2>Lecture 1 — en location nue, le dossier ne passe pas</h2>
    <p class="attractiveness-intro">Relevé du quartier Aguillon : T3 de 53 m² à 665 € CC, T4 de 102 m² à 1 499 €, studios de 390 à 570 €. Un T4 de 73 m² se situe donc entre 950 et 1 100 €/mois.</p>
    <table class="projection-table">
      <thead><tr><th>Loyer mensuel</th><th>Loyer</th><th>Net / mois</th><th>Brut</th><th>Net / acte</th><th>Cash-flow 20 ans</th><th>Ratio</th></tr></thead>
      <tbody>
{lignes_nu}
      </tbody>
    </table>
    <p class="scenario-subtitle">À 950 €/mois, le net après IS ressort à <strong>{nu950_net}</strong>, soit <strong>{nu950_pct} %</strong> du capital engagé, avec un cash-flow de <strong>{nu950_cf}</strong> et un ratio de {nu950_ratio}. <strong>En location nue, le bien ne couvre pas sa mensualité, à aucune hypothèse de loyer réaliste.</strong></p>
  </section>

  <section class="financial-projections">
    <h2>Lecture 2 — en colocation, le dossier passe</h2>
    <p class="attractiveness-intro">Relevé de colocation à Toulon, chambres : 400 · 450 · 450 · 469 · 470 · 490 · 490 · 495 · 550 €. Sources : Locservice, Appartager, La Carte des Colocs, Colocatère, Leboncoin, SeLoger (coloc de 3 chambres de 67 m² affichée 450 €). <strong>La bande dense est 450-490 €, la médiane autour de 470 €.</strong></p>
    <table class="projection-table">
      <thead><tr><th>Loyer par chambre</th><th>Loyer total</th><th>Net / mois</th><th>Brut</th><th>Net / acte</th><th>Cash-flow 20 ans</th><th>Ratio</th></tr></thead>
      <tbody>
{lignes_coloc}
      </tbody>
    </table>
    <p class="scenario-subtitle">À 450 € la chambre, le net après IS est de <strong>{coloc450_net}</strong> par mois, soit <strong>{coloc450_pct} %</strong> net sur acte, cash-flow <strong>{coloc450_cf}</strong> et ratio {coloc450_ratio}. À 470 € — la médiane du marché — on passe à <strong>{coloc470_net}</strong> par mois, <strong>{coloc470_pct} %</strong> et un cash-flow de <strong>{coloc470_cf}</strong>.</p>
    <p class="strategy-rationale">Le seuil de 5 % net sur acte correspond à <strong>{seuil5}</strong> par mois, soit <strong>{seuil5_ch} la chambre</strong> sur trois chambres. Le marché relevé est au-dessus. <strong>C'est le seul mode d'exploitation qui rend ce bien finançable.</strong></p>
  </section>

  <section class="financial-projections">
    <h2>Les seuils, loyer hors charges</h2>
    <table class="projection-table">
      <thead><tr><th>Objectif</th><th>Loyer mensuel</th><th>Par chambre</th><th>Au m²</th></tr></thead>
      <tbody>
{lignes_seuil}
      </tbody>
    </table>
    <p class="strategy-rationale">Sur la base d'un acte en main de {acte}, d'une taxe foncière de {tf} et d'une vacance de 5 %.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Ce qui décide, et ce qui inquiète</h2>
    <ul>
      <li><strong>Le prix.</strong> {decote} % sous la moyenne des T4 de Toulon : c'est l'argument central du dossier, sans lui il n'y a pas de discussion.</li>
      <li><strong>Les charges.</strong> 960 €/an pour 77 lots, c'est très bas. Rapporté aux loyers de colocation, cela reste sous <strong>{ch_ratio} %</strong> — largement dans notre zone de confort, là où le T3 de Brignoles examiné le même jour sortait à 13,3 %.</li>
      <li><strong>Une seule salle d'eau pour trois colocataires.</strong> C'est le vrai plafond du loyer par chambre : une colocation avec deux salles d'eau se loue plus cher. À voir en visite.</li>
      <li><strong>Les surfaces des trois chambres.</strong> Une chambre de 8 m² et deux de 14 m² ne se louent pas au même prix. La grille ci-dessus suppose des chambres comparables.</li>
      <li><strong>Pas de cave, et pas de parking mentionné.</strong> Sur une colocation de trois actifs, trois véhicules, c'est un point à vérifier.</li>
      <li><strong>DPE E.</strong> Pas d'urgence réglementaire, mais un bien qui continuera de coûter cher à chauffer.</li>
      <li><strong>La colocation est un métier, pas un rendement.</strong> Trois baux, des départs à gérer, du mobilier, des charges refacturées. Le 7 % se paie en gestion et en temps.</li>
    </ul>
  </section>

  <section class="strategy-exploration">
    <h2>Verdict</h2>
    <p><strong>On avance, à une condition : le chiffrer en colocation, jamais en location nue.</strong> En nu, le bien ressort à 4,5 à 5,4 % net sur acte avec un cash-flow négatif à toutes les hypothèses. En colocation, à la médiane du marché relevé — 470 € la chambre — il sort à <strong>{coloc470_pct} % net</strong> avec un cash-flow positif.</p>
    <p class="strategy-rationale">Le travail à faire avant toute visite : vérifier la surface réelle des trois chambres, la salle d'eau, et l'existence d'un stationnement. Et obtenir de l'agence une estimation de loyer locatif réel, pour confronter sa réponse au relevé ci-dessus.</p>
  </section>

  <footer class="report-footer">
    <p>Fiche produite pour Alexis et Rémy Barlatier — Sémaphore Patrimoine, 8 octobre 2026. Tous les chiffres sont recalculés par <code>scripts/gen_fiche_toulon_aguillon_t4.py</code> ; modifier un prix, un loyer ou une charge régénère la page.</p>
  </footer>

</main>
</body>
</html>
"""

if __name__ == "__main__":
    main()
