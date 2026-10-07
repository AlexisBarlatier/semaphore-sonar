# -*- coding: utf-8 -*-
"""Génère la page de référence « Résultats des ventes aux enchères — Var ».

Relevé tenu à la main à partir des pages de résultats publiées : chaque ligne est
une vente passée, avec sa mise à prix, son prix d'adjudication et l'écart.

Règle de lecture : la mise à prix est fixée par le créancier et n'a aucun rapport
avec la valeur du bien. C'est l'écart au marché qui compte, pas l'écart à la mise
à prix.

Sortie : analyses/encheres-var/index.html
"""
import os
import re

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "analyses", "encheres-var", "index.html")

# bien, ville, date, surface, mise a prix, resultat, occupation, source
VENTES = [
    ("Appartement F3 + emplacement de stationnement", "Toulon", "10 septembre 2026", 64.98, 56000., 104000.,
     "Occupé par la partie saisie", "Résidence l'Amazonite, 6e étage, quartier de l'Escaillon"),
    ("Maison type BP1 + jardin + parking", "Tourrettes", "4 septembre 2026", None, 23000., 103000.,
     "Occupé par la propriétaire, résidence principale", "Ensemble Les Grandes Terrasses, secteur résidentiel avec golf"),
    ("Appartement T3 + compartiment de cave", "Draguignan", "18 septembre 2026", None, 50000., 71000.,
     "Libre", "68 Les Matins Clairs, place Jean Piquemal"),
    ("Appartement dans une maison de village, 2 niveaux", "Carcès", "4 septembre 2026", 65.0, 30000., 31000.,
     "Occupé, bail d'habitation", "3 rue du Maréchal Foch, lots 8 et 9, avec grenier"),
    ("Deux locaux commerciaux + courette de service", "Saint-Raphaël", "4 septembre 2026", 113.63, 68000., None,
     "Restaurant fermé depuis 3 ans (lot 57), autre en exploitation (lot 56)",
     "Ensemble Port Santa Lucia, avenue Raymond Poincaré. 35,29 m² et 78,34 m² + courette 28 m²"),
    ("Local commercial + cave, loué par bail commercial", "Vidauban", "16 septembre 2026", 94.91, 30000., 78000.,
     "Occupé, bail commercial depuis 2011, loyer 715 €/mois",
     "3 avenue Maximin Martin. 42,90 m² + local 1,50 m² + cave 50,51 m². Tribunal de Marseille"),
]

LECTURES = [
    ("La mise à prix ne dit rien de la valeur",
     "Cinq ventes du même département, de +3 % à +348 % sur les quatre qui ont trouvé preneur. La mise à prix est "
     "fixée par le créancier sur sa créance, pas sur le bien. Elle ne rentre dans aucun de nos calculs."),
    ("Un lot peut ne pas se vendre, et c'est l'information la plus utile",
     "Saint-Raphaël, deux locaux commerciaux dont un restaurant fermé depuis trois ans : 68 000 € de mise à prix, "
     "aucun enchérisseur. Quand la mise à prix dépasse ce que la salle accepte de payer, le lot reste au créancier."),
    ("Une mise à prix basse est un appât, pas une aubaine",
     "Tourrettes : 23 000 € affichés, 103 000 € adjugés — le prix de marché d'une maisonnette avec jardin dans un secteur "
     "touristique. Tout le monde a vu l'aubaine, personne n'en a eu."),
    ("La marge est dans les lots où personne ne se bat",
     "Carcès : +3,3 %, soit une seule main levée. Un appartement occupé par un bail dans un village ne fait rêver personne. "
     "C'est là que le prix reste près de la mise à prix."),
    ("La consignation est un plancher, pas un pourcentage",
     "10 % de la mise à prix, avec un minimum de 3 000 € à Draguignan. À Tourrettes, mise à prix 23 000 € : c'est le minimum "
     "qui s'applique, pas les 2 300 €. Chèque de banque à l'ordre du Bâtonnier."),
    ("La surenchère est un risque réel",
     "Une surenchère du dixième reste possible pendant dix jours après l'adjudication, par ministère d'avocat du barreau "
     "concerné. On peut gagner l'audience et perdre le bien."),
]

A_VENIR = [
    ("22 octobre 2026", "Toulon", "Appartement T3 de 56,30 m² + cave, 7 avenue Franklin Roosevelt",
     "Mise à prix 25 500 €. Libre de toute occupation. Plafond calculé : 37 000 €."),
    ("12 novembre 2026", "Toulon", "Appartement T3 + cave", "Mise à prix 30 000 €."),
    ("12 novembre 2026", "La Seyne-sur-Mer", "Appartement T3 de 56,30 m² + box à scooters", "Mise à prix 50 000 €."),
    ("9 novembre 2026", "Signes", "Maison à usage d'habitation de 115,94 m²", "Mise à prix 300 000 €."),
]


def nfr(v, dec=0):
    ent, _, frac = ("%.*f" % (dec, float(v))).partition(".")
    return re.sub(r"(?<=\d)(?=(\d{3})+$)", "\u202f", ent) + ("," + frac if dec else "")


def eur(v, dec=0):
    return nfr(v, dec) + " €"


def main():
    lignes, ecarts = [], []
    for nom, ville, date, surf, mise, res, occ, note in VENTES:
        if res:
            ecart = (res / mise - 1) * 100
            ecarts.append(ecart)
            col_res = "<strong>%s</strong>" % eur(res)
            col_ecart = "+%s %%" % nfr(ecart, 1)
            pm2 = (res / surf) if surf else None
        else:
            col_res = "aucun enchérisseur"
            col_ecart = "<strong>non requise</strong>"
            pm2 = None
        lignes.append(
            "        <tr><td><strong>%s</strong><br><span class=\"ville\">%s — %s</span>"
            "<br><span class=\"note\">%s</span></td>"
            "<td class=\"num\">%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
            "<td class=\"num\">%s</td><td class=\"num\">%s</td><td>%s</td></tr>"
            % (nom, ville, date, note, eur(mise), col_res, col_ecart,
               eur(pm2) if pm2 else "n. c.", eur(surf, 2) if surf else "n. c.", occ or "—")
        )
    lectures = "\n".join(
        "      <li><strong>%s</strong> — %s</li>" % (t, d) for t, d in LECTURES)
    avenir = "\n".join(
        "        <tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (d, v, b, n)
        for d, v, b, n in A_VENIR)
    vendus = [v for v in VENTES if v[5]]
    mini = min(vendus, key=lambda x: x[5] / x[4])
    maxi = max(vendus, key=lambda x: x[5] / x[4])

    html = TEMPLATE.format(
        lignes="\n".join(lignes), lectures=lectures, avenir=avenir,
        nb=len(VENTES), e_min=nfr(min(ecarts), 1), e_max=nfr(max(ecarts), 0),
        v_min=mini[1], v_max=maxi[1],
    )
    reste = re.search(r"\{[a-z_]{3,}\}", html)
    if reste:
        raise SystemExit("placeholder non remplace : %s" % reste.group(0))
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("page ecrite : %s (%d lignes, %d ventes)" % (SORTIE, html.count("\n") + 1, len(VENTES)))


TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ventes aux enchères dans le Var — relevé des résultats</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<main class="report">
  <header class="report-header">
    <p class="report-breadcrumb">Page de référence — Sémaphore Patrimoine</p>
    <h1>Ventes aux enchères dans le Var — relevé des résultats</h1>
    <p class="report-address">Tribunaux judiciaires de Toulon et Draguignan · relevé au 7 octobre 2026</p>
    <p class="report-source">Ce relevé se construit audience après audience. Chaque ligne est une vente passée, avec sa mise à prix et son prix d'adjudication réels. Il ne dit pas ce qu'il faut acheter : il dit ce que le marché des enchères paie réellement dans le Var.</p>
  </header>

  <section class="strategy-exploration">
    <h2>L'essentiel en une ligne</h2>
    <p>Sur les <strong>{nb} ventes relevées</strong>, <strong>une n'a trouvé aucun preneur</strong> et les autres sont parties de <strong>+{e_min} %</strong> ({v_min}) à <strong>+{e_max} %</strong> ({v_max}) au-dessus de leur mise à prix. Autrement dit : <strong>la mise à prix ne dit rien de la valeur du bien</strong>, ni dans un sens ni dans l'autre. Elle est fixée par le créancier sur sa créance. Ce qui compte, c'est ce que la salle accepte de payer — et quand elle n'accepte pas, le lot reste invendu.</p>
  </section>

  <section class="financial-projections">
    <h2>Les ventes relevées</h2>
    <table class="projection-table">
      <thead><tr><th>Bien</th><th>Mise à prix</th><th>Résultat</th><th>Écart</th><th>€/m²</th><th>Surface</th><th>Occupation</th></tr></thead>
      <tbody>
{lignes}
      </tbody>
    </table>
    <p class="scenario-subtitle">L'écart affiché est le rapport au prix d'adjudication sur la mise à prix. Il mesure la concurrence que le lot a attirée, pas sa qualité. Un écart faible signale un lot que personne ne s'est disputé — c'est là que se trouvent les opportunités, quand le calcul tient.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Ce que le relevé enseigne</h2>
    <ul>
{lectures}
    </ul>
    <p class="strategy-rationale">Règle maison : <strong>on ne se rend jamais à une audience sans avoir posé son plafond par écrit</strong>. Il se calcule sur le loyer, les charges et le rendement visé — jamais sur le prix affiché. La mise à prix ne rentre dans aucun de nos calculs, et l'émotion d'une salle non plus.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Les ventes à venir</h2>
    <table class="projection-table">
      <thead><tr><th>Date</th><th>Ville</th><th>Bien</th><th>Repère</th></tr></thead>
      <tbody>
{avenir}
      </tbody>
    </table>
    <p class="scenario-subtitle">La donnée la plus instructive du relevé est désormais là : <strong>un lot qui ne part pas</strong>. Il dit l'inverse des autres lignes — qu'une mise à prix peut être trop haute, et que la salle le fait savoir en restant muette. À chaque audience, on relève donc trois choses : le prix d'adjudication, le nombre de mains levées, et les lots qui restent sans preneur.</p>
  </section>

  <footer class="report-footer">
    <p>Page de référence produite pour Alexis et Rémy Barlatier — Sémaphore Patrimoine, 7 octobre 2026. Relevé tenu à partir des pages de résultats publiques ; il s'enrichit à chaque audience observée.</p>
  </footer>
</main>
</body>
</html>
"""

if __name__ == "__main__":
    main()
