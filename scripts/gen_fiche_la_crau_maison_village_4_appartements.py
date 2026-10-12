# -*- coding: utf-8 -*-
"""Fiche « La Crau — maison de village, 4 appartements indépendants ».

Fiche de travail : les loyers des trois baux en cours ne sont pas communiqués
par le vendeur (demande de pièces envoyée le 8 octobre 2026). La grille est donc
construite sur le relevé de marché réalisé à La Crau les 8 et 9 octobre 2026,
en retenant les bornes basses annonce par annonce.

Sortie : analyses/2026-10-12-la-crau-maison-village-4-appartements/index.html
"""
import os
import re

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "analyses", "2026-10-12-la-crau-maison-village-4-appartements",
                      "index.html")
URL_ANNONCE = ("https://www.logic-immo.com/detail-annonce/vente/provence-alpes-cote-d-azur/"
               "var-83/la-crau-83260/26V49XQZ4PZT")

PRIX = 500000.0
SURF_ANNONCEE = 240.0
LOTS = [("T1", 40.0, 620.0), ("T2", 38.0, 640.0), ("T3", 67.0, 800.0), ("T4", 77.0, 950.0)]
SURF_REELLE = sum(l[1] for l in LOTS)
LOYER_MARCHE = sum(l[2] for l in LOTS)

FRAIS = 0.08
TRAVAUX = 30000.0          # provision : « quelques travaux de rafraîchissement », aucun devis
TF = 2500.0                # provision : non communiquée
CHARGES = 1500.0           # provision : structure juridique non précisée (monopropriété ou copro)
PNO = 400.0
VACANCE = 0.95
IS = 0.15                  # convention prudente : IS sur l'EBE, intérêts non déduits
COEF20 = 0.006238          # mensualité par euro emprunté : 20 ans à 3,80 %, assurance comprise
APPORT = 0.10

ACTE = PRIX * (1 + FRAIS)
REVIENT = ACTE + TRAVAUX
CAPITAL = ACTE * (1 - APPORT)
MENSU = CAPITAL * COEF20

ECARTS = []


def calcule(libelle, publie, attendu, tolerance):
    if abs(float(publie) - float(attendu)) > tolerance:
        ECARTS.append("%s : publie %s, attendu %s" % (libelle, publie, attendu))
    return publie


def nfr(v, dec=0):
    ent, _, frac = ("%.*f" % (dec, float(v))).partition(".")
    return re.sub(r"(?<=\d)(?=(\d{3})+$)", "\u202f", ent) + (("," + frac) if dec else "")


def eur(v, dec=0):
    return nfr(v, dec) + " €"


def signe(v):
    return ("%+.0f €" % v).replace("-", "\u2212").replace("+", "\u002b")


def exploitation(loyer):
    ebe = loyer * 12 * VACANCE - TF - CHARGES - PNO
    net = ebe * (1 - IS)
    return dict(loyer=loyer, ebe=ebe, net=net, net_m=net / 12,
                net_revient=net / REVIENT * 100, net_acte=net / ACTE * 100,
                cf=net / 12 - MENSU, ratio=ebe / (MENSU * 12),
                brut=loyer * 12 / PRIX * 100)


def plafond_ratio(loyer, cible=1.20):
    """Prix tel que EBE / annuité = cible ; capital = acte × 0,9, donc prix = capital / 0,972."""
    ebe = loyer * 12 * VACANCE - TF - CHARGES - PNO
    return (ebe / 12 / cible) / COEF20 / (1 - APPORT) / (1 + FRAIS)


def plafond_cf_nul(loyer):
    net = (loyer * 12 * VACANCE - TF - CHARGES - PNO) * (1 - IS)
    return (net / 12) / COEF20 / (1 - APPORT) / (1 + FRAIS)


def plafond_rendement(loyer, cible=0.05):
    """Prix tel que net / (prix × 1,08 + travaux) = cible."""
    net = (loyer * 12 * VACANCE - TF - CHARGES - PNO) * (1 - IS)
    return (net / cible - TRAVAUX) / (1 + FRAIS)


def main():
    base = exploitation(LOYER_MARCHE)
    basses = exploitation(LOYER_MARCHE * 0.90)
    hautes = exploitation(LOYER_MARCHE * 1.20)

    lignes_lots = "\n".join(
        "        <tr><td>%s</td><td class=\"num\">%s m²</td><td class=\"num\">%s</td>"
        "<td class=\"num\">%s / m²</td><td>%s</td></tr>"
        % (nom, nfr(surf, 0), eur(loyer), eur(loyer / surf), source)
        for nom, surf, loyer, source in (
            ("T1 (1er étage)", 40.0, 620.0, "T2 de 40 m² relevé à 650 € ; T1 meublé de 25 m² à 525 €"),
            ("T2 (2e étage, deux chambres)", 38.0, 640.0, "T2 de 40 m² relevé à 650 €"),
            ("T3 (3e étage, terrasse tropézienne)", 67.0, 800.0,
             "T3 de 70 m² à 970 €, T3 de 75 m² à 840 €, T3 de 78 m² à 780 €"),
            ("T4 (dernier étage, terrasse)", 77.0, 950.0,
             "aucun T4 relevé dans le bourg : extrapolation sous la fourchette communale de 14 à 18 €/m²"),
        ))

    grille = [(LOYER_MARCHE * f, plafond_cf_nul(LOYER_MARCHE * f),
               plafond_ratio(LOYER_MARCHE * f), plafond_rendement(LOYER_MARCHE * f))
              for f in (0.90, 1.00, 1.10, 1.20)]
    lignes_grille = "\n".join(
        "        <tr><td>%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
        "<td class=\"num\">%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td></tr>"
        % (eur(rev), eur(cf_nul), eur(ratio_p), eur(rdt_p), eur(min(ratio_p, rdt_p)),
           nfr((min(ratio_p, rdt_p) / PRIX - 1) * 100, 0))
        for rev, cf_nul, ratio_p, rdt_p in grille)

    calcule("loyers de marché retenus", LOYER_MARCHE, 3010.0, 1.0)
    calcule("surface réelle des quatre lots", SURF_REELLE, 222.0, 0.5)
    calcule("EBE au loyer retenu", base["ebe"], 29914.0, 2.0)
    calcule("plafond du ratio 1,20 au loyer retenu", plafond_ratio(LOYER_MARCHE), 342600.0, 1500.0)

    html = TEMPLATE.format(
        url=URL_ANNONCE, prix=eur(PRIX), surf_annoncee=nfr(SURF_ANNONCEE, 0),
        surf=nfr(SURF_REELLE, 0), pm2=eur(PRIX / SURF_ANNONCEE),
        pm2_reel=eur(PRIX / SURF_REELLE), loyer_marche=eur(LOYER_MARCHE),
        loyers_an=eur(LOYER_MARCHE * 12), loyer_m2=nfr(LOYER_MARCHE / SURF_REELLE, 2),
        acte=eur(ACTE), travaux=eur(TRAVAUX), revient=eur(REVIENT), capital=eur(CAPITAL),
        mens=eur(MENSU), tf=eur(TF), charges=eur(CHARGES), pno=eur(PNO),
        frais_fixes=eur(TF + CHARGES + PNO), appar=eur(ACTE * APPORT),
        brut=nfr(base["brut"], 2), ebe=eur(base["ebe"]), net_an=eur(base["net"]),
        net_m=eur(base["net_m"]), net_revient=nfr(base["net_revient"], 2),
        net_acte=nfr(base["net_acte"], 2), cf=signe(base["cf"]), ratio=nfr(base["ratio"], 2),
        ch_pct=nfr((TF + CHARGES + PNO) / (LOYER_MARCHE * 12) * 100, 1),
        basse_net=nfr(basses["net_revient"], 2), basse_cf=signe(basses["cf"]),
        haute_net=nfr(hautes["net_revient"], 2), haute_cf=signe(hautes["cf"]),
        plafond=eur(plafond_ratio(LOYER_MARCHE)),
        plafond_bas=eur(plafond_ratio(LOYER_MARCHE * 0.90)),
        plafond_haut=eur(plafond_ratio(LOYER_MARCHE * 1.20)),
        plafond_rdt=eur(plafond_rendement(LOYER_MARCHE)),
        plafond_ecart=nfr((1 - plafond_ratio(LOYER_MARCHE) / PRIX) * 100, 0),
        ecart_rdt=nfr(plafond_rendement(LOYER_MARCHE) - PRIX, 0),
        lignes_lots=lignes_lots, lignes_grille=lignes_grille,
        vacance=nfr((1 - VACANCE) * 100, 0), taux_is=nfr(IS * 100, 0),
        n_lots=len(LOTS),
    )
    reste = re.search(r"\{[a-z_0-9]{3,}\}", html)
    if reste:
        raise SystemExit("placeholder non remplacé : %s" % reste.group(0))
    if "26V49XQZ4PZT" not in html or "noindex" not in html:
        raise SystemExit("lien annonce ou balise noindex manquante")
    if ECARTS and not os.environ.get("HERMES_TOLERANT"):
        raise SystemExit("écarts de contrôle :\n  " + "\n  ".join(ECARTS))

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("fiche écrite : %s (%d lignes)" % (SORTIE, html.count("\n") + 1))
    print("  loyers retenus %s / mois | EBE %s | net %s/an | %s %% net/revient | CF %s | ratio %.2f"
          % (eur(LOYER_MARCHE), eur(base["ebe"]), eur(base["net"]),
             nfr(base["net_revient"], 2), signe(base["cf"]), base["ratio"]))
    for rev, cf_nul, ratio_p, rdt_p in grille:
        print("  revenus %s -> plafond CF nul %s | ratio 1,20 %s | 5 %% net %s"
              % (eur(rev), eur(cf_nul), eur(ratio_p), eur(rdt_p)))
    print("  écarts : %s" % (ECARTS or "aucun"))


TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>La Crau — maison de village, 4 appartements</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<main class="report">

  <header class="report-header">
    <p class="report-breadcrumb">Analyse — Sémaphore Patrimoine</p>
    <h1>La Crau — maison de village, {n_lots} appartements indépendants</h1>
    <p class="report-address">La Crau (83260), quartier Centre Ville Sud · {surf_annoncee} m² annoncés, {surf} m² sur les quatre lots · 3 des 4 logements loués · bâti de 1930 · DPE D</p>
    <p class="report-source">Source : <a href="{url}">l'annonce Logic-Immo, réf. 26V49XQZ4PZT</a> (iad France, Brice Lacordaire, réf. 2131728). Prix affiché <strong>{prix}</strong>. <strong>Les loyers des trois baux en cours ne sont pas communiqués</strong> : la demande de pièces est partie le 8 octobre 2026. Cette fiche chiffre donc sur le relevé de marché du bourg, en retenant les bornes basses annonce par annonce.</p>
  </header>

  <section class="strategy-exploration">
    <h2>Le bien</h2>
    <p>Maison de village sur deux étages, découpée en <strong>{n_lots} appartements indépendants</strong> : T1 d'environ 40 m², T2 d'environ 38 m², T3 d'environ 67 m² avec terrasse, T4 d'environ 77 m² avec terrasse. Cave, deux terrasses, exposition annoncée lumineuse. Surface Carrez par lot non communiquée : les surfaces retenues sont celles de l'annonce.</p>
    <p class="projection-note"><strong>État déclaré « rénovation nécessaire »</strong>, sans devis ni chiffrage — sur un bâti de 1930. DPE D, GES B. Une partie du rez-de-chaussée n'est pas exploitée (elle sert de cave aux locataires) : la surface et les accès ne sont pas communiqués, c'est le premier point à lever.</p>
  </section>

  <section class="financial-projections">
    <h2>Les chiffres d'entrée</h2>
    <p>Prix affiché <strong>{prix}</strong>, soit {pm2} au m² annoncé et <strong>{pm2_reel} au m² réellement louable</strong>. Frais d'acquisition à 8 % : acte en main <strong>{acte}</strong>. Enveloppe de rafraîchissement provisionnée à <strong>{travaux}</strong>, faute de devis : <strong>prix de revient {revient}</strong>.</p>
    <p class="strategy-rationale">Apport de 10 % ({appar}) et mensualité sur 20 ans à 3,80 % assurance comprise : <strong>{mens}</strong>, calculée sur la seule quotité empruntée ({capital}).</p>
  </section>

  <section class="financial-projections">
    <h2>La grille des loyers, lot par lot</h2>
    <table class="projection-table">
      <thead><tr><th>Lot</th><th>Surface</th><th>Loyer retenu</th><th>Au m²</th><th>Base du relevé du 8-9 octobre 2026</th></tr></thead>
      <tbody>
{lignes_lots}
      </tbody>
    </table>
    <p class="scenario-subtitle">Total retenu : <strong>{loyer_marche} par mois</strong>, soit {loyers_an} par an et <strong>{loyer_m2} au m² des {surf} m² louables</strong>. Le marché communal relevé se situe entre 14 et 18 €/m² : la grille est délibérément construite sur les bornes basses, et le T4 est extrapolé faute de comparable de sa taille.</p>
  </section>

  <section class="financial-projections">
    <h2>Le compte au prix affiché</h2>
    <table class="projection-table">
      <thead><tr><th>Poste</th><th>Annuel</th><th>Commentaire</th></tr></thead>
      <tbody>
        <tr><td>Loyers bruts</td><td class="num">{loyers_an}</td><td>hypothèse de marché, baux non communiqués</td></tr>
        <tr><td>Vacance {vacance} %</td><td class="num">déduite</td><td>provision statistique, aucune vacance structurelle identifiée</td></tr>
        <tr><td>Charges, taxe foncière, assurance</td><td class="num">{frais_fixes}</td><td>{ch_pct} % des loyers bruts, sur provisions</td></tr>
        <tr><td>EBE</td><td class="num">{ebe}</td><td>excédent brut d'exploitation</td></tr>
        <tr><td>Impôt sur les sociétés {taux_is} %</td><td class="num">{net_an} net</td><td>convention prudente : IS sur l'EBE, intérêts non déduits</td></tr>
        <tr><td>Mensualité de crédit</td><td class="num">{mens} / mois</td><td>20 ans à 3,80 % sur {capital}</td></tr>
      </tbody>
    </table>
    <p class="scenario-subtitle">Au prix affiché : <strong>{brut} % brut</strong>, EBE {ebe}, net après IS <strong>{net_m} par mois</strong> — soit <strong>{net_revient} %</strong> du prix de revient ({net_acte} % de l'acte en main) — et un cash-flow de <strong>{cf} par mois</strong>, pour un rapport EBE / annuité de <strong>{ratio}</strong>. <strong>Le bien ne remplit aucune des deux conditions : ni le seuil de rendement, ni la couverture de sa mensualité.</strong></p>
  </section>

  <section class="financial-projections">
    <h2>Les prix qui tiendraient, selon l'assiette de loyers</h2>
    <p class="attractiveness-intro">Trois plafonds se calculent séparément — celui où le cash-flow devient nul, celui où le rapport EBE / annuité atteint 1,20 (seuil de confort du prêteur, à 20 ans) et celui du rendement cible de 5 % net sur le prix de revient. <strong>C'est le plus bas qui gouverne.</strong></p>
    <table class="projection-table">
      <thead><tr><th>Loyers annuels</th><th>Cash-flow nul</th><th>Ratio 1,20</th><th>5 % net</th><th>Plafond retenu</th><th>Sous l'affichage</th></tr></thead>
      <tbody>
{lignes_grille}
      </tbody>
    </table>
    <p class="scenario-subtitle">À l'assiette de marché ({loyer_marche} par mois), le plafond du prêteur ressort à <strong>{plafond}</strong> — <strong>{plafond_ecart} % sous le prix affiché</strong> — tandis que le rendement de 5 % ne serait atteint qu'à <strong>{plafond_rdt}</strong>, soit {ecart_rdt} sous la demande. Les deux ancres sont donc sous le prix : ce n'est pas le loyer qui bloque, c'est le prix.</p>
    <p class="scenario-subtitle">Sensibilité : à 10 % de loyers en moins, le plafond du prêteur tombe à {plafond_bas} ; à 20 % de loyers en plus, il monte à {plafond_haut} — <strong>toujours sous les {prix} demandés</strong>. Aucune hypothèse de loyer plausible dans ce bourg ne fait passer le prix affiché.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Ce qui décide, et ce qui inquiète</h2>
    <ul>
      <li><strong>Les trois baux, et rien d'autre.</strong> Trois des quatre logements sont loués et aucun loyer n'est communiqué. Toute la fiche repose sur le marché du bourg : si les baux sortent 20 % sous le relevé, les plafonds ci-dessus baissent d'autant, et aucun prix ne tient plus.</li>
      <li><strong>Le prix est celui du marché, pas celui d'une décote.</strong> {pm2_reel} au m² réellement louable pour un immeuble entier à rénover dans un bourg : il n'y a pas de coussin de sécurité, contrairement à ce que laisse croire un prix au m² calculé sur les {surf_annoncee} m² annoncés.</li>
      <li><strong>Le rafraîchissement n'est pas chiffré.</strong> « Quelques travaux » sur du 1930 : l'enveloppe retenue ici est une provision de {travaux}, et chaque 10 000 € de travaux en plus retire environ 10 000 € du plafond de prix.</li>
      <li><strong>Taxe foncière et charges inconnues.</strong> Provisionnées ensemble à {frais_fixes} par an, soit {ch_pct} % des loyers bruts. Sur un immeuble de quatre logements en village, ce poste peut être le double — et il se déduit directement du prix.</li>
      <li><strong>La partie de rez-de-chaussée non exploitée.</strong> Elle sert de cave aux locataires. Sa surface, ses accès et son usage possible ne sont pas communiqués : c'est le seul levier de valeur du lot, et il n'est ni chiffré ni même décrit.</li>
      <li><strong>La concentration géographique.</strong> Ce serait le troisième dossier vivant de notre pile dans le même secteur (Pignans, Gonfaron, Brignoles) : ces bourgs partagent le même marché locatif mince et la même liquidité étroite à la revente.</li>
      <li><strong>Un immeuble entier se gère.</strong> Quatre lots, quatre baux, des rotations à couvrir : la gestion se provisionne dans les charges, elle n'est pas gratuite.</li>
    </ul>
  </section>

  <section class="strategy-exploration">
    <h2>Verdict</h2>
    <p><strong>Au prix affiché, on ne paie pas</strong> : {net_revient} % net sur le prix de revient, un cash-flow de {cf} par mois et un rapport EBE / annuité de {ratio}. Aucune des deux portes n'est franchie, et les deux plafonds — {plafond} pour la banque, {plafond_rdt} pour le rendement — sont sous la demande.</p>
    <p class="strategy-rationale">Le dossier ne se rouvre qu'à <strong>{plafond}</strong> à l'assiette de marché, et seulement si les baux confirment des loyers d'au moins {loyer_marche} par mois. Tant que les loyers réels ne sont pas sur la table, il n'y a pas d'offre à préparer : la demande de pièces est le seul travail utile, et c'est elle qui dira si ce dossier existe.</p>
  </section>

  <footer class="report-footer">
    <p>Fiche produite pour Alexis et Rémy Barlatier — Sémaphore Patrimoine, 12 octobre 2026. Chiffres recalculés par <code>scripts/gen_fiche_la_crau_maison_village_4_appartements.py</code> ; modifier un prix, un loyer ou une charge régénère la page.</p>
  </footer>

</main>
</body>
</html>
"""

if __name__ == "__main__":
    main()
