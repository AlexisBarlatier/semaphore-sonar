# -*- coding: utf-8 -*-
"""Génère la fiche « Mail de questions à l'agence — local de stockage, Saint-Raphaël ».

Page de copie : elle ne contient que le texte à envoyer, sans aucun chiffre de
négociation. Elle est donc publiable telle quelle, le dossier restant interne.

Sortie : analyses/modele-mail-questions-agence/index.html
"""
import os
import re

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "analyses", "modele-mail-questions-agence", "index.html")

OBJET = "Local de stockage 32 m², Saint-Raphaël — questions avant visite"

PARAGRAPHES = [
    "Bonjour,",
    "Nous étudions le local de stockage d'environ 32 m² que vous proposez à Saint-Raphaël, "
    "dans une résidence sécurisée, et nous souhaiterions quelques précisions avant d'aller plus loin.",
]

QUESTIONS = [
    "Quel est le montant de la taxe foncière, et pour quelle année ?",
    "Le local génère-t-il une cotisation foncière des entreprises (CFE) à la charge du "
    "propriétaire, et pour quel montant ?",
    "Que couvrent exactement les 120 €/an de charges de copropriété, et quelle est la "
    "taille de la copropriété ?",
    "Le règlement de copropriété autorise-t-il expressément un usage de stockage, y compris "
    "par une entreprise ? Le local est-il identifié comme local d'habitation, cave ou local "
    "commercial au règlement ?",
    "L'électrification du local a-t-elle été chiffrée ? Est-elle réalisable depuis les parties "
    "communes, et à quel coût approximatif ?",
    "Quelles sont les dimensions de l'accès : largeur de la porte, hauteur, et accès voiture "
    "jusqu'à la porte ?",
    "Quels diagnostics sont disponibles : amiante, électricité, et le cas échéant plomb ?",
    "Le local a-t-il déjà été loué, et à quel loyer ? À quel usage ?",
    "Depuis combien de temps est-il en vente, et quel est le motif de la vente ?",
]

CLOTURE = [
    "Nous vous remercions par avance de ces éléments, qui nous permettront d'avancer sur le dossier.",
    "Bien cordialement,",
]

SIGNATURE = ["Rémy Barlatier", "06 27 84 53 50", "sarl.spbi@gmail.com"]

TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mail de questions à l'agence — local de stockage, Saint-Raphaël</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<main class="report">
  <header class="report-header">
    <p class="report-breadcrumb">Courrier — Sémaphore Patrimoine</p>
    <h1>Mail de questions à l'agence</h1>
    <p class="report-address">Local de stockage, 32 m², Saint-Raphaël (83700) — agence B et B Immobilier</p>
    <p class="report-source">Texte à copier tel quel dans la messagerie SeLoger. Il ne contient aucun élément de négociation : uniquement les questions dont les réponses conditionnent le calcul.</p>
  </header>

  <section class="strategy-exploration">
    <h2>Objet</h2>
    <p><strong>{objet}</strong></p>
    <h2>Corps du message</h2>
    <div style="border:1px solid #d8d8d8;border-radius:6px;padding:16px 18px;background:#fbfbfb;line-height:1.65">
{corps}
    </div>
    <p class="projection-note">Copier tout ce qui se trouve dans l'encadré, objet compris si la messagerie le permet, sinon coller l'objet dans le champ prévu et le reste dans le message.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Pourquoi ces questions et pas d'autres</h2>
    <ul>
      <li><strong>La taxe foncière et la CFE</strong> — ce sont les deux seules charges que nous ne connaissons pas, et ce sont elles qui décident du loyer minimum acceptable. Sans elles, aucun chiffrage n'est solide.</li>
      <li><strong>Le règlement de copropriété</strong> — un local identifié comme cave ou comme local commercial ne se loue pas de la même façon. C'est la question qui peut arrêter le dossier à elle seule.</li>
      <li><strong>L'électrification</strong> — l'annonce écrit « pouvant être électrifié ». Cela veut dire qu'il ne l'est pas. C'est un coût à intégrer, pas un détail.</li>
      <li><strong>Les diagnostics</strong> — le local échappe au diagnostic de performance énergétique, mais pas à l'amiante ni à l'électricité.</li>
      <li><strong>L'ancienneté de la mise en vente et le motif</strong> — deux informations qui pèsent dans une négociation, et qui se demandent sans jamais parler de prix.</li>
    </ul>
    <p class="strategy-rationale">Ce qui n'est pas demandé, volontairement : rien sur le prix, rien sur notre financement, rien sur notre projet d'exploitation. Un acheteur qui pose des questions techniques passe pour sérieux ; un acheteur qui parle de prix ouvre une négociation avant d'avoir les pièces.</p>
  </section>

  <footer class="report-footer">
    <p>Fiche générée par <code>scripts/gen_fiche_mail_questions_agence.py</code> pour Alexis et Rémy Barlatier — 4 octobre 2026.</p>
  </footer>
</main>
</body>
</html>
"""


def main():
    corps = []
    for p in PARAGRAPHES:
        corps.append("      <p style=\"margin:0 0 12px\">%s</p>" % p)
    corps.append("      <ul style=\"margin:0 0 12px;padding-left:22px\">")
    for q in QUESTIONS:
        corps.append("        <li style=\"margin-bottom:6px\">%s</li>" % q)
    corps.append("      </ul>")
    for p in CLOTURE:
        corps.append("      <p style=\"margin:0 0 12px\">%s</p>" % p)
    for i, s in enumerate(SIGNATURE):
        style = "margin:0 0 4px;font-weight:700" if i == 0 else "margin:0 0 4px"
        corps.append("      <p style=\"%s\">%s</p>" % (style, s))

    html = TEMPLATE.format(objet=OBJET, corps="\n".join(corps))
    reste = re.search(r"\{[a-z_]{3,}\}", html)
    if reste:
        raise SystemExit("placeholder non remplace : %s" % reste.group(0))
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("fiche ecrite : %s (%d lignes, %d questions)" % (SORTIE, html.count("\n") + 1, len(QUESTIONS)))


if __name__ == "__main__":
    main()
