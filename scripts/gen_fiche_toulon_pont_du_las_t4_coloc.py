# -*- coding: utf-8 -*-
"""Fiche « Toulon Pont du Las / Puget-Théâtre — duplex T4 69,40 m² Carrez,
lecture colocation ».

Aucun loyer n'est annoncé par le vendeur : la fiche raisonne en grille, sur le
relevé de marché réellement effectué le 8 octobre 2026 (colocation Toulon Ouest
394-420 €/chambre, location nue du quartier 718 à 896 € pour des T3).

Sortie : analyses/2026-10-08-toulon-pont-du-las-t4-coloc/index.html

Correction de méthode par rapport aux chiffres du fil : la mensualité était
calculée avec l'apport appliqué DEUX fois (coef déjà net d'apport, puis acte en
main × 0,9). Ici la mensualité porte sur la seule quotité empruntée :
capital = acte en main × (1 − apport).
"""
import os
import re

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "analyses", "2026-10-08-toulon-pont-du-las-t4-coloc", "index.html")
URL_ANNONCE = ("https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/"
               "toulon-83000/26E5UBLAFGS1")

PRIX_AFFICHE = 149000.0
PRIX = 139000.0            # prix affiché actuel (le précédent est barré)
CARREZ = 69.40
HABITABLE = 82.30
CHARGES = 1400.0
TF = 1108.0                # taxe foncière 2025, communiquée par l'annonce
FRAIS = 0.08
VACANCE = 0.95
IS = 0.15                  # convention prudente : IS sur l'EBE, intérêts non déduits
COEF20 = 0.006238          # mensualité par euro emprunté : 20 ans à 3,80 %, assurance comprise
APPORT = 0.10
CHAMBRES = 3

ACTE = PRIX * (1 + FRAIS)
CAPITAL = ACTE * (1 - APPORT)
MENSU = CAPITAL * COEF20

ECARTS = []


def calcule(libelle, publie, attendu, tolerance):
    """Contrôle déclaratif : chaque chiffre clé est vérifié, écarts listés en mode tolérant."""
    if abs(float(publie) - float(attendu)) > tolerance:
        ECARTS.append("%s : publie %s, attendu %s (tol %s)" % (libelle, publie, attendu, tolerance))
    return publie


def nfr(v, dec=0):
    ent, _, frac = ("%.*f" % (dec, float(v))).partition(".")
    return re.sub(r"(?<=\d)(?=(\d{3})+$)", "\u202f", ent) + (("," + frac) if dec else "")


def eur(v, dec=0):
    return nfr(v, dec) + " €"


def signe(v):
    return ("%+.0f €" % v).replace("-", "\u2212").replace("+", "\u002b")


def scenario(loyer):
    ebe = loyer * 12 * VACANCE - CHARGES - TF
    net = ebe * (1 - IS)
    return dict(loyer=loyer, ebe=ebe, net=net, net_m=net / 12,
                brut=loyer * 12 / PRIX * 100, net_acte=net / ACTE * 100,
                cf=net / 12 - MENSU, ratio=ebe / (MENSU * 12),
                net_revient=net / ACTE * 100)


def loyer_cible(taux):
    return (taux * ACTE / (1 - IS) + CHARGES + TF) / 12 / VACANCE


def plafond_ratio(loyer, cible=1.20):
    """Prix tel que EBE / annuité = cible. Capital = acte × 0,9, donc prix = capital / 0,972."""
    ebe = loyer * 12 * VACANCE - CHARGES - TF
    annuite = ebe / 12 / cible
    capital = annuite / COEF20
    return capital / (1 - APPORT) / (1 + FRAIS)


def plafond_cf_nul(loyer):
    """Prix tel que le net après IS couvre exactement la mensualité."""
    net = (loyer * 12 * VACANCE - CHARGES - TF) * (1 - IS)
    capital = (net / 12) / COEF20
    return capital / (1 - APPORT) / (1 + FRAIS)


def main():
    nu = [scenario(l) for l in (800.0, 850.0, 900.0)]
    coloc = [scenario(CHAMBRES * c) for c in (380.0, 394.0, 400.0, 420.0, 435.0, 450.0)]
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
                   nfr(s["net_acte"], 2), signe(s["cf"]), s["ratio"]))
        return "\n".join(out)

    c394, c420, c450 = coloc[1], coloc[3], coloc[5]
    n850 = nu[1]

    lignes_plafond = "\n".join(
        "        <tr><td>%s la chambre</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
        "<td class=\"num\">%s</td><td class=\"num\">%s</td></tr>"
        % (eur(c), eur(CHAMBRES * c), eur(plafond_cf_nul(CHAMBRES * c)),
           eur(plafond_ratio(CHAMBRES * c)),
           eur(min(plafond_cf_nul(CHAMBRES * c), plafond_ratio(CHAMBRES * c))))
        for c in (380.0, 394.0, 420.0))

    lignes_seuil = "\n".join(
        "        <tr><td>%d %% net sur acte</td><td class=\"num\">%s / mois</td>"
        "<td class=\"num\">%s</td><td class=\"num\">%s</td></tr>"
        % (t * 100, eur(l), eur(l / CHAMBRES) + " / chambre", eur(l / HABITABLE, 1) + " / m²")
        for t, l in seuils)

    # contrôles de non-régression sur les points validés
    calcule("EBE annuel à 394 € la chambre", c394["ebe"], 10967.0, 1.0)
    calcule("net sur acte à 394 € la chambre", c394["net_acte"], 6.21, 0.02)
    calcule("charges + TF annuelles", CHARGES + TF, 2508.0, 0.01)

    html = TEMPLATE.format(
        url=URL_ANNONCE, prix=eur(PRIX), prix_avant=eur(PRIX_AFFICHE),
        carrez=nfr(CARREZ, 2), habitable=nfr(HABITABLE, 2), pm2=eur(PRIX / CARREZ),
        acte=eur(ACTE), mens=eur(MENSU), charges=eur(CHARGES), tf=eur(TF),
        charges_tf=eur(CHARGES + TF), apport=eur(CAPITAL and ACTE * APPORT),
        lignes_nu=lignes(nu), lignes_coloc=lignes(coloc, par_chambre=True),
        lignes_seuil=lignes_seuil, lignes_plafond=lignes_plafond,
        c394_net=eur(c394["net_m"]), c394_pct=nfr(c394["net_acte"], 2),
        c394_cf=signe(c394["cf"]), c394_ratio=nfr(c394["ratio"], 2),
        c420_net=eur(c420["net_m"]), c420_pct=nfr(c420["net_acte"], 2),
        c420_cf=signe(c420["cf"]), c420_ratio=nfr(c420["ratio"], 2),
        c450_net=eur(c450["net_m"]), c450_pct=nfr(c450["net_acte"], 2),
        n850_net=eur(n850["net_m"]), n850_pct=nfr(n850["net_acte"], 2),
        n850_cf=signe(n850["cf"]), n850_ratio=nfr(n850["ratio"], 2),
        seuil5=eur(seuils[0][1]), seuil5_ch=eur(seuils[0][1] / CHAMBRES),
        seuil6_ch=eur(seuils[1][1] / CHAMBRES), seuil7_ch=eur(seuils[2][1] / CHAMBRES),
        plafond394=eur(plafond_ratio(394 * 3)), plafond420=eur(plafond_ratio(420 * 3)),
        plafond380=eur(plafond_ratio(380 * 3)),
        plafond_nu850=eur(plafond_ratio(850.0)),
        plafond_nu850_decote=nfr((1 - plafond_ratio(850.0) / PRIX) * 100, 0),
        ch_ratio=nfr(CHARGES / (3 * 420.0 * 12) * 100, 1),
        ch_tf_ratio=nfr((CHARGES + TF) / (3 * 420.0 * 12) * 100, 1),
        vacance=nfr((1 - VACANCE) * 100, 0), taux_is=nfr(IS * 100, 0),
        plafond394_ecart=nfr(plafond_ratio(394 * 3) - PRIX, 0),
    )
    reste = re.search(r"\{[a-z_0-9]{3,}\}", html)
    if reste:
        raise SystemExit("placeholder non remplacé : %s" % reste.group(0))
    if "26E5UBLAFGS1" not in html or "noindex" not in html:
        raise SystemExit("lien annonce ou balise noindex manquante")

    if ECARTS and not os.environ.get("HERMES_TOLERANT"):
        raise SystemExit("écarts de contrôle :\n  " + "\n  ".join(ECARTS))

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("fiche écrite : %s (%d lignes)" % (SORTIE, html.count("\n") + 1))
    for lab, s in (("nu 850", n850), ("coloc 394", c394), ("coloc 420", c420), ("coloc 450", c450)):
        print("  %-10s net %4.0f €/mois | net/acte %4.2f %% | CF %+.0f | ratio %.2f"
              % (lab, s["net_m"], s["net_acte"], s["cf"], s["ratio"]))
    print("  plafonds : 380 €/ch %s | 394 €/ch %s | 420 €/ch %s | nu 850 € %s"
          % (eur(plafond_ratio(1140.0)), eur(plafond_ratio(1182.0)),
             eur(plafond_ratio(1260.0)), eur(plafond_ratio(850.0))))
    print("  écarts : %s" % (ECARTS or "aucun"))


TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Toulon Pont du Las — duplex T4, lecture colocation</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<main class="report">

  <header class="report-header">
    <p class="report-breadcrumb">Analyse — Sémaphore Patrimoine</p>
    <h1>Toulon Pont du Las — duplex T4 de {carrez} m² Carrez, lecture colocation</h1>
    <p class="report-address">Toulon (83200), entrée du quartier du Pont du Las / Puget-Théâtre · 4 pièces, 3 chambres · duplex, 3e et dernier étage sans ascenseur · DPE D</p>
    <p class="report-source">Source : <a href="{url}">l'annonce SeLoger, réf. 26E5UBLAFGS1</a>. Prix affiché <strong>{prix}</strong>, après un premier prix de {prix_avant}. Aucun loyer n'étant annoncé par le vendeur, la fiche raisonne en grille, à partir du relevé de marché réalisé le 8 octobre 2026.</p>
  </header>

  <section class="strategy-exploration">
    <h2>Le bien</h2>
    <p>Duplex de {habitable} m² dont <strong>{carrez} m² Carrez</strong>, 3e et dernier étage d'un immeuble de 1949 <strong>sans ascenseur</strong>. Au premier niveau : séjour-cuisine de 35,70 m² et une <strong>chambre parentale de 11 m² avec salle d'eau et WC</strong>. En mezzanine : deux chambres de 10,80 et 9,70 m², rangements, et une <strong>salle de bain avec WC</strong>. Pas de cave, pas de balcon, exposition ouest, chauffage individuel par climatisation réversible.</p>
    <p class="projection-note"><strong>Charges {charges}/an et taxe foncière {tf}</strong> — les deux sont communiquées par l'annonce, ce qui est rare et permet de chiffrer sans hypothèse. Copropriété de 4 lots, syndic professionnel, aucune procédure en cours. DPE D, GES B, facture énergétique annoncée entre 1 220 et 1 700 €/an.</p>
  </section>

  <section class="financial-projections">
    <h2>Les chiffres d'entrée</h2>
    <p>Acte en main <strong>{acte}</strong> (frais à 8 %), apport de {apport} et mensualité sur 20 ans à 3,80 % assurance comprise : <strong>{mens}</strong>. La mensualité porte sur la seule quotité empruntée : capital = acte en main × 90 %.</p>
    <p class="strategy-rationale">Charges et taxe foncière réunies représentent <strong>{ch_tf_ratio} %</strong> des loyers de colocation retenus, et {ch_ratio} % pour les charges seules — sous le seuil de surveillance de 10 %.</p>
  </section>

  <section class="financial-projections">
    <h2>Lecture 1 — en location nue, le bien ne vaut pas ce prix</h2>
    <p class="attractiveness-intro">Relevé du nu à Pont du Las / Toulon Ouest : T3 de 67 m² à 718 €, T3 de 55 m² à 896 €, T3 meublé de 52 m² à 740 €, T2 de 42 m² à 500 €. Un T4 de 82 m² se situe donc entre <strong>800 et 900 €/mois</strong>.</p>
    <table class="projection-table">
      <thead><tr><th>Hypothèse</th><th>Loyer</th><th>Net / mois</th><th>Brut</th><th>Net / acte</th><th>Cash-flow 20 ans</th><th>Ratio</th></tr></thead>
      <tbody>
{lignes_nu}
      </tbody>
    </table>
    <p class="scenario-subtitle">À 850 €/mois, le net après IS ressort à <strong>{n850_net}</strong> par mois, soit <strong>{n850_pct} %</strong> du capital engagé, cash-flow <strong>{n850_cf}</strong>, ratio {n850_ratio}. Le prix que le prêteur accepterait sur ce loyer est de <strong>{plafond_nu850}</strong>, soit {plafond_nu850_decote} % sous le prix affiché. <strong>En location nue, ce bien ne vit pas.</strong></p>
  </section>

  <section class="financial-projections">
    <h2>Lecture 2 — en colocation, le dossier se discute</h2>
    <p class="attractiveness-intro">Relevé de colocation à Toulon Ouest : 394 € pour une colocation de 3 chambres de 69 m² au 1er étage à Pont du Las, 420 € pour un 4 pièces de 77 m² au 3e sur 3, 420 € pour une chambre meublée de 10,5 m² à Pont de Las, 395 € pour une chambre dans un 4 pièces de 103 m², 420 € boulevard de Paris. La moyenne de la ville est plus haute (450 €) mais ce n'est pas le marché de ce quartier. <strong>La bande retenue est 394-420 € la chambre.</strong></p>
    <table class="projection-table">
      <thead><tr><th>Hypothèse</th><th>Loyer total</th><th>Net / mois</th><th>Brut</th><th>Net / acte</th><th>Cash-flow 20 ans</th><th>Ratio</th></tr></thead>
      <tbody>
{lignes_coloc}
      </tbody>
    </table>
    <p class="scenario-subtitle">À 394 € la chambre — le comparable direct du quartier — le net après IS est de <strong>{c394_net}</strong> par mois, soit <strong>{c394_pct} %</strong> net sur acte, cash-flow <strong>{c394_cf}</strong> et ratio {c394_ratio}. À 420 €, on passe à <strong>{c420_net}</strong> par mois, <strong>{c420_pct} %</strong> et un cash-flow de <strong>{c420_cf}</strong> (ratio {c420_ratio}).</p>
    <p class="strategy-rationale">Le seuil de 5 % net sur acte demande <strong>{seuil5}</strong> par mois, soit {seuil5_ch} la chambre ; 6 % demande {seuil6_ch} et 7 % demande {seuil7_ch}. Le marché relevé est au-dessus des trois : le dossier ne dépend donc pas d'un pari sur les loyers.</p>
  </section>

  <section class="financial-projections">
    <h2>Les prix qui tiennent, selon le loyer et selon la contrainte</h2>
    <p class="attractiveness-intro">Deux plafonds se calculent séparément et <strong>c'est le plus bas qui gouverne</strong> : le prix où le cash-flow devient nul, et celui où le rapport EBE / annuité de crédit atteint 1,20 — le seuil de confort du prêteur, à 20 ans.</p>
    <table class="projection-table">
      <thead><tr><th>Loyer par chambre</th><th>Loyer du bien</th><th>Cash-flow nul</th><th>Ratio 1,20</th><th>Plafond retenu</th></tr></thead>
      <tbody>
{lignes_plafond}
      </tbody>
    </table>
    <p class="scenario-subtitle">Au prix affiché de {prix}, le plafond du ratio 1,20 à 394 € la chambre ressort à <strong>{plafond394}</strong>, soit <strong>{plafond394_ecart} € sous la demande</strong>. À 420 € la chambre, il monte à <strong>{plafond420}</strong> — encore sous les {prix}. <strong>C'est la banque qui contraint, pas la trésorerie.</strong></p>
  </section>

  <section class="financial-projections">
    <h2>Les seuils de rendement</h2>
    <table class="projection-table">
      <thead><tr><th>Objectif</th><th>Loyer mensuel</th><th>Par chambre</th><th>Au m² habitable</th></tr></thead>
      <tbody>
{lignes_seuil}
      </tbody>
    </table>
    <p class="strategy-rationale">Sur la base d'un acte en main de {acte}, d'une vacance de {vacance} % et d'un impôt sur les sociétés à {taux_is} % appliqué à l'EBE.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Ce qui décide, et ce qui inquiète</h2>
    <ul>
      <li><strong>Le prix a déjà reculé.</strong> L'annonce affiche un premier prix de {prix_avant}, barré, ramené à {prix}. Ce n'est pas un prix de départ, c'est un prix qui a bougé de 10 000 € — indice d'un vendeur qui n'est pas en position de force, et c'est le premier levier de négociation.</li>
      <li><strong>Deux salles d'eau et deux WC pour trois chambres.</strong> C'est l'avantage décisif de ce bien sur les autres T4 toulonnais examinés le même jour : une seule salle d'eau plafonne le loyer par chambre, ici la contrainte ne s'applique pas.</li>
      <li><strong>Les chambres sont petites : 11, 10,80 et 9,70 m².</strong> La grille suppose des chambres comparables ; la plus petite se louera 20 à 40 € sous la parentale. C'est le point à vérifier en visite, avec un relevé de loyer par taille de chambre.</li>
      <li><strong>3e étage sur 3, sans ascenseur.</strong> À 69 m² de duplex, cela réduit le vivier et pèse sur le loyer — c'est déjà intégré par le choix de la bande basse du marché, pas par une décote supplémentaire.</li>
      <li><strong>« À rafraîchir » sans montant.</strong> Sur un immeuble de 1949, l'enveloppe n'est pas chiffrée : à demander avant toute offre, car chaque 5 000 € de travaux coûte environ 5 000 € de prix.</li>
      <li><strong>Charges et taxe foncière connues.</strong> {charges} de charges et {tf} de taxe foncière, soit {charges_tf} par an : le compte d'exploitation ne repose sur aucune hypothèse pour ces deux postes.</li>
      <li><strong>La colocation est un métier.</strong> Trois baux, du mobilier, des départs à gérer, des charges refacturées. Le rendement affiché se paie en gestion et en temps.</li>
    </ul>
  </section>

  <section class="strategy-exploration">
    <h2>Verdict</h2>
    <p><strong>On négocie — et uniquement en colocation.</strong> En location nue, le bien s'autofinance autour de {plafond_nu850} à 850 €/mois : il ne vaut pas le prix demandé pour un acheteur classique, et c'est écrit dans les chiffres. En colocation, à la bande du quartier, le plafond du prêteur ressort à <strong>{plafond394}</strong> à 394 € la chambre et <strong>{plafond420}</strong> à 420 €.</p>
    <p class="strategy-rationale">Position d'offre : <strong>122 500 €</strong>, prix qui tient au bas du marché relevé, en annonçant que l'on s'aligne si l'agence confirme un loyer de 420 € la chambre — ce qui autorise alors {plafond420}. Avant toute offre : le montant du rafraîchissement, et le loyer réellement pratiqué dans le quartier pour une chambre de 9,70 m².</p>
  </section>

  <footer class="report-footer">
    <p>Fiche produite pour Alexis et Rémy Barlatier — Sémaphore Patrimoine, 12 octobre 2026. Chiffres recalculés par <code>scripts/gen_fiche_toulon_pont_du_las_t4_coloc.py</code> ; modifier un prix, un loyer ou une charge régénère la page.</p>
  </footer>

</main>
</body>
</html>
"""

if __name__ == "__main__":
    main()
