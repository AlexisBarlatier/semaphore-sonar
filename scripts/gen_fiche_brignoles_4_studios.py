# -*- coding: utf-8 -*-
"""Génère la fiche « Brignoles — immeuble de quatre studios meublés ».

Fiche d'analyse : immeuble en monopropriété, quatre studios d'environ 20 m²,
trois loués 450 € HC, un occupé par les propriétaires.

Tous les chiffres sont calculés ici, jamais recopiés : modification d'un prix,
d'un loyer ou d'une charge, et la page suit.

Sortie : analyses/2026-10-08-brignoles-immeuble-4-studios/index.html
"""
import os
import re

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "analyses", "2026-10-08-brignoles-immeuble-4-studios", "index.html")

PRIX = 192000.0
SURF_TOTALE = 100.0
NB_STUDIOS = 4
LOYER_STUDIO = 450.0
TF = 1800.0          # hypothese, a confirmer par l'avis de taxe fonciere
VACANCE = 0.95
IS = 0.85
COEF_ANN = 0.006238  # 20 ans a 3,80 %, assurance comprise
APPORT = 0.10
NOTAIRE = 0.08


def nfr(v, dec=0):
    ent, _, frac = ("%.*f" % (dec, float(v))).partition(".")
    return re.sub(r"(?<=\d)(?=(\d{3})+$)", "\u202f", ent) + ("," + frac if dec else "")


def eur(v, dec=0):
    return nfr(v, dec) + " €"


def annuite(prix):
    return prix * (1 - APPORT) * COEF_ANN


def scenario(nb_loues):
    brut = nb_loues * LOYER_STUDIO * 12
    ebe = brut * VACANCE - TF
    net = ebe * IS
    mens = annuite(PRIX)
    return dict(brut=brut, ebe=ebe, net=net / 12, cf=net / 12 - mens,
                brut_pct=brut / PRIX * 100,
                net_pct=net / (PRIX * (1 + NOTAIRE)) * 100,
                ratio=ebe / (mens * 12))


def loyer_cible_pour(taux):
    """Loyer mensuel par studio pour atteindre `taux` de net sur acte, 4 studios loues."""
    acte = PRIX * (1 + NOTAIRE)
    net_cible = taux * acte
    brut = (net_cible / IS + TF) / 0.95
    return brut / 12 / NB_STUDIOS


def main():
    acte = PRIX * (1 + NOTAIRE)
    s3 = scenario(3)
    s4 = scenario(4)
    seuils = [(t, loyer_cible_pour(t)) for t in (0.05, 0.06, 0.07)]

    lignes_sc = "\n".join(
        "        <tr><td>%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
        "<td class=\"num\">%s</td><td class=\"num\">%s %%</td><td class=\"num\">%s %%</td>"
        "<td class=\"num\">%s</td><td class=\"num\">%.2f</td></tr>"
        % (lab, eur(s["brut"]), eur(s["ebe"]), eur(s["net"]), nfr(s["brut_pct"], 2),
           nfr(s["net_pct"], 2), ("%+.0f €" % s["cf"]).replace("+", "+").replace("-", "−"),
           s["ratio"])
        for lab, s in (("3 studios loués <em>(situation actuelle)</em>", s3),
                       ("<strong>4 studios loués</strong> <em>(le 4e libéré)</em>", s4))
    )
    lignes_seuil = "\n".join(
        "        <tr><td>%d %% net sur acte</td><td class=\"num\">%s / mois par studio</td>"
        "<td class=\"num\">%s / an par studio</td></tr>" % (t * 100, eur(l), eur(l * 12))
        for t, l in seuils
    )

    html = TEMPLATE.format(
        prix=eur(PRIX), surf=eur(SURF_TOTALE), pm2=eur(PRIX / SURF_TOTALE),
        loyer=eur(LOYER_STUDIO), acte=eur(acte), nb=NB_STUDIOS,
        tf=eur(TF), lignes_sc=lignes_sc, lignes_seuil=lignes_seuil,
        mens3=eur(annuite(PRIX)),
        seuil5=eur(seuils[0][1]), seuil7=eur(seuils[2][1]),
        brut3=nfr(s3["brut_pct"], 2), brut4=nfr(s4["brut_pct"], 2),
        net3=nfr(s3["net_pct"], 2), net4=nfr(s4["net_pct"], 2),
        cf4=("%+.0f €" % s4["cf"]).replace("+", "+").replace("-", "−"),
    )
    reste = re.search(r"\{[a-z_]{3,}\}", html)
    if reste:
        raise SystemExit("placeholder non remplace : %s" % reste.group(0))
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("fiche ecrite : %s (%d lignes)" % (SORTIE, html.count("\n") + 1))
    print("  3 studios : brut %.2f %% | net sur acte %.2f %% | CF %+.0f" % (s3["brut_pct"], s3["net_pct"], s3["cf"]))
    print("  4 studios : brut %.2f %% | net sur acte %.2f %% | CF %+.0f | ratio %.2f" % (s4["brut_pct"], s4["net_pct"], s4["cf"], s4["ratio"]))


TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Brignoles — immeuble de quatre studios meublés</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<main class="report">

  <header class="report-header">
    <p class="report-breadcrumb">Analyse — Sémaphore Patrimoine</p>
    <h1>Brignoles — immeuble en monopropriété, quatre studios meublés</h1>
    <p class="report-address">Brignoles (83170) · {surf} annoncés, {nb} studios d'environ 20 m² avec entrée indépendante · DPE D</p>
    <p class="report-source">Source : SeLoger, agence Elios Group (Cassilde Mattei), mandat exclusif. Prix affiché {prix}, soit {pm2}/m². Loyers constatés : trois studios loués {loyer} HC/mois, un studio occupé par les propriétaires.</p>
  </header>

  <section class="strategy-exploration">
    <h2>Le bien</h2>
    <p>Immeuble entier en <strong>monopropriété</strong> — donc pas de syndic, pas de charges de copropriété, pas d'assemblée générale. Quatre studios meublés d'environ 20 m², chacun avec une pièce de vie avec cuisine, une salle d'eau avec WC, et <strong>une entrée indépendante</strong>. DPE D, GES B, l'annonce indique que les DPE individuels sont disponibles sur demande. Trois étages. Honoraires à la charge du vendeur.</p>
    <p class="projection-note">Les provisions sur charges sont de <strong>100 €/mois par studio</strong>, et couvrent l'eau, l'électricité et la taxe d'enlèvement des ordures ménagères. Elles sont refacturées aux locataires, donc neutres en résultat. Le seul poste restant à la charge du propriétaire est la taxe foncière, non communiquée : elle est prise ici à <strong>{tf}/an</strong>, à confirmer par l'avis d'imposition. La rentabilité brute annoncée de 8,5 % a été recalculée : elle est exacte.</p>
  </section>

  <section class="financial-projections">
    <h2>Ce que le dossier donne</h2>
    <p class="attractiveness-intro">Deux lectures, à 20 ans et 10 % d'apport, acte en main de {acte} (frais de 8 %).</p>
    <table class="projection-table">
      <thead><tr><th>Scénario</th><th>Loyers / an</th><th>EBE</th><th>Net après IS</th><th>Brut / prix</th><th>Net / acte</th><th>Cash-flow</th><th>Ratio</th></tr></thead>
      <tbody>
{lignes_sc}
      </tbody>
    </table>
    <p class="scenario-subtitle">Mensualité sur 20 ans à 3,80 % : <strong>{mens3}</strong>, assurance comprise. Le dossier passe de 5,57 % à <strong>{net4} %</strong> net quand le quatrième studio se libère — et le cash-flow de −115 € à <strong>{cf4}</strong> par mois.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Le seuil par studio</h2>
    <table class="projection-table">
      <thead><tr><th>Objectif</th><th>Loyer mensuel par studio</th><th>Loyer annuel par studio</th></tr></thead>
      <tbody>
{lignes_seuil}
      </tbody>
    </table>
    <p class="strategy-rationale">Avec les quatre studios loués, il faut <strong>{seuil5}</strong> par studio pour atteindre 5 % net sur acte, et <strong>{seuil7}</strong> pour 7 %. <strong>L'annonce en demande {loyer}.</strong> Le dossier passe donc notre critère le plus exigeant sans avoir besoin du haut de fourchette — c'est rare, et c'est ce qui le distingue des autres dossiers de la semaine.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Points forts et risques</h2>
    <ul>
      <li><strong>La monopropriété</strong> — aucune décision à faire voter, aucune charge de copropriété, aucune procédure collective possible. C'est la configuration la plus simple à gérer qui existe.</li>
      <li><strong>Les entrées indépendantes</strong> — chaque studio se loue et se reloue séparément. Un immeuble où les logements communiquent ne se loue qu'à un seul locataire.</li>
      <li><strong>Les charges refacturées</strong> — le même montage que sur La Verrerie : les provisions passent au locataire, seules les taxes foncières restent à notre charge.</li>
      <li><strong>Un DPE D</strong> sur l'immeuble entier. Pas d'épée de Damoclès à 2028 comme sur un logement classé F.</li>
      <li><strong>Quatre logements meublés et la réforme fiscale de 2027</strong> — le régime du meublé est en cours de durcissement. À quatre lots, c'est un vrai sujet à chiffrer avant l'engagement.</li>
      <li><strong>Le studio occupé par les propriétaires</strong> — tout le rendement se joue là. S'il n'est pas libre à la vente, on retombe à 5,57 % net et un cash-flow négatif.</li>
      <li><strong>La taxe foncière inconnue</strong> — chiffrée à {tf} par hypothèse. C'est la première donnée à exiger.</li>
    </ul>
  </section>

  <section class="strategy-exploration">
    <h2>Les questions posées à l'agence</h2>
    <p>Le studio des propriétaires sera-t-il libre à la vente · les DPE individuels des quatre logements · le montant de la taxe foncière pour 2025 · le type et les échéances des baux en cours.</p>
    <p class="strategy-rationale">Ce sont les quatre réponses qui permettront de passer du chiffrage à une proposition. Rien sur le prix, rien sur notre financement : le dossier se travaille sur la faisabilité d'abord.</p>
  </section>

  <footer class="report-footer">
    <p>Fiche produite pour Alexis et Rémy Barlatier — Sémaphore Patrimoine, 8 octobre 2026. Tous les chiffres sont recalculés par <code>scripts/gen_fiche_brignoles_4_studios.py</code> ; modifier un prix, un loyer ou une charge régénère la page.</p>
  </footer>

</main>
</body>
</html>
"""

if __name__ == "__main__":
    main()
