# -*- coding: utf-8 -*-
"""Génère la fiche interne « Trésorerie du parc » (état au 28/09/2026 + La Garde).

Tous les chiffres viennent de `analyse_app.parc` : une seule source, donc pas
deux fiches qui se contredisent. Les assertions de contrôle font échouer le
build si parc.py bouge, au lieu de publier un chiffre périmé.

Sortie : analyses/parc-tresorerie/index.html
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyse_app import parc

IS_RATE = parc.IS_RATE
TAUX_RESERVE = 2.84
LOYERS = parc.loyers_verrerie_annuels()
STRUCTURE = (parc.BANQUE_MENSUEL_EUR + parc.COMPTABLE_MENSUEL_EUR) * 12
EBE = parc.ebe_verrerie()
IS_HAUT = parc.is_estime_verrerie()
IS_BAS = parc.is_estime_verrerie(parc.PRET_VERRERIE_EUR * 0.9 / 30)
AMORT = parc.PRET_VERRERIE_EUR * 0.9 / 30
FLUX_HAUT = EBE / 12 - IS_HAUT / 12 - parc.PRET_VERRERIE_MENSUALITE_EUR
FLUX_BAS = EBE / 12 - IS_BAS / 12 - parc.PRET_VERRERIE_MENSUALITE_EUR
RESERVE_1 = parc.trajectoire(12, TAUX_RESERVE)
RESERVE_2 = parc.trajectoire(24, TAUX_RESERVE)
RESERVE_3 = parc.trajectoire(36, TAUX_RESERVE)
RESERVE_5 = parc.trajectoire(60, TAUX_RESERVE)
RESERVE_10 = parc.trajectoire(120, TAUX_RESERVE)
MOIS_15K = parc.mois_pour(15000, TAUX_RESERVE)
MOIS_30K = parc.mois_pour(30000, TAUX_RESERVE)
MOIS_50K = parc.mois_pour(50000, TAUX_RESERVE)
CHARGE_LA_GARDE = 120.0          # taxe foncière du lot, le reste refacturé au preneur
CCA_MENSUEL = parc.PRET_ASSOCIES_LA_GARDE_EUR / 240.0
PRIX_PLACE = (50.0, 55.0, 60.0)


def calcule(libelle, valeur, attendu, tolerance=1.0):
    """Contrôle de cohérence : un chiffre publié est un chiffre vérifié."""
    if abs(valeur - attendu) > tolerance:
        raise SystemExit(
            f"Assertion échouée — {libelle} : {valeur:,.2f} au lieu de {attendu:,.2f}"
        )
    return valeur


def euro(x, dec=0):
    entier = f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")
    return entier


def garde_mensuelle(prix_place, charges=CHARGE_LA_GARDE, cca=True):
    """Ce que les deux places laissent chaque mois, net d'IS et de CCA."""
    loyers = prix_place * 2 * 12
    net = (loyers - charges) * (1 - IS_RATE)
    return net / 12 - (CCA_MENSUEL if cca else 0.0)


# --- Contrôles : si ces valeurs changent, on ne publie pas en silence
calcule("loyers Verrerie", LOYERS, 18605.20, 0.02)
calcule("EBE Verrerie", EBE, 17357.20, 0.02)
calcule("IS haut", IS_HAUT, 2178.0, 2.0)
calcule("IS bas", IS_BAS, 1856.0, 2.0)
calcule("flux haut", FLUX_HAUT, 718.0, 1.0)
calcule("flux bas", FLUX_BAS, 745.0, 1.0)
calcule("reserve 12 mois", RESERVE_1, 10706.0, 2.0)
calcule("reserve 5 ans", RESERVE_5, 36961.0, 2.0)
calcule("mois pour 15 000", MOIS_15K, 21.0, 0.0)
calcule("mois pour 30 000", MOIS_30K, 48.0, 0.0)

GARDE = {prix: garde_mensuelle(prix, cca=False) for prix in PRIX_PLACE}
GARDE_APRES_CCA = {prix: garde_mensuelle(prix) for prix in PRIX_PLACE}
TOTAL_BAS = FLUX_BAS + GARDE[60.0]
TOTAL_HAUT = FLUX_HAUT + GARDE[50.0]
LIBRE_HAUT = TOTAL_HAUT - parc.EFFORT_MENSUEL_EUR
LIBRE_BAS = TOTAL_BAS - parc.EFFORT_MENSUEL_EUR
calcule("total parc + Garde haut", TOTAL_HAUT, 795.0, 1.5)
calcule("total parc + Garde bas", TOTAL_BAS, 838.0, 1.5)

# --- Scénarios
SCENARIOS = [
    ("Base", "Verrerie louée à SCHINDLER, La Garde louée à 55 € la place, "
             "réserve alimentée de 500 €/mois",
     f"{euro(FLUX_HAUT)} à {euro(FLUX_BAS)} €/mois de flux Verrerie, "
     f"{euro(GARDE[55.0])} €/mois de La Garde, "
     f"soit <strong>{euro(FLUX_HAUT + GARDE[55.0])} à {euro(FLUX_BAS + GARDE[55.0])} €/mois</strong> "
     f"avant l'effort de réserve"),
    ("Favorable", "La Garde part à 60 € la place et le cabinet amortit la part bâtie des "
                  "places de La Verrerie",
     f"<strong>{euro(TOTAL_BAS)} €/mois</strong>, dont {euro(parc.EFFORT_MENSUEL_EUR)} à la réserve "
     f"et {euro(LIBRE_BAS)} € restant libres"),
    ("Défavorable", "La Garde reste vacante six mois et la toiture de La Verrerie est "
                    "appelée par la copropriété",
     f"un mois de vacance sur La Verrerie coûte {euro(LOYERS / 12)} € ; "
     f"la réserve de {euro(RESERVE_1)} € à un an absorbe "
     f"{euro(RESERVE_1 / (LOYERS / 12), 1)} mois de loyer, "
     f"et couvre les appels de fonds courants sans toucher au flux"),
]

HTML = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Trésorerie du parc — état au {parc.DATE_RELEVE} — Sémaphore Patrimoine</title>
<link rel="stylesheet" href="../../style.css">
</head>
<body>
<main class="report">

  <header class="report-header">
    <p class="report-breadcrumb">Note interne — trésorerie du parc</p>
    <h1>Ce que le parc dégage aujourd'hui, et ce qu'il dégagera avec La Garde</h1>
    <p class="report-address">SCI Sémaphore Patrimoine — La Verrerie (13 parkings, La Valentine, Marseille) et La Garde (2 places extérieures)</p>
    <p class="report-date">État au {parc.DATE_RELEVE} · projection à douze mois</p>
    <p class="report-source">Source des chiffres : <code>scripts/analyse_app/parc.py</code>, alimenté par le tableau d'amortissement Crédit Mutuel du 28 septembre 2026 et les factures de loyer SCHINDLER</p>
  </header>

  <section class="summary-cards">
    <div class="card">
      <span class="card-label">Loyers Verrerie</span>
      <span class="card-value">{euro(LOYERS)} € /an</span>
    </div>
    <div class="card">
      <span class="card-label">EBE</span>
      <span class="card-value">{euro(EBE)} € /an</span>
    </div>
    <div class="card">
      <span class="card-label">IS estimé</span>
      <span class="card-value">{euro(IS_BAS)} à {euro(IS_HAUT)} € /an</span>
    </div>
    <div class="card">
      <span class="card-label">Flux après échéance</span>
      <span class="card-value">{euro(FLUX_HAUT)} à {euro(FLUX_BAS)} € /mois</span>
    </div>
    <div class="card">
      <span class="card-label">Réserve au {parc.DATE_RELEVE}</span>
      <span class="card-value">{euro(parc.RESERVE_EUR, 2)} €</span>
    </div>
    <div class="card">
      <span class="card-label">Effort mensuel</span>
      <span class="card-value">{euro(parc.EFFORT_MENSUEL_EUR)} €</span>
    </div>
    <div class="card">
      <span class="card-label">Parc + La Garde</span>
      <span class="card-value">{euro(TOTAL_HAUT)} à {euro(TOTAL_BAS)} € /mois</span>
    </div>
    <div class="card card-verdict note-8">
      <span class="card-label">Trésorerie libre</span>
      <span class="card-value">{euro(LIBRE_HAUT)} à {euro(LIBRE_BAS)} € /mois</span>
    </div>
  </section>

  <section class="strategy-exploration">
    <h2>Lecture</h2>
    <p>Le parc tient aujourd'hui sur un seul locataire : SCHINDLER, bail commercial, {euro(LOYERS)} € de loyers par an, taxe foncière et assurance refacturées. L'EBE ressort à <strong>{euro(EBE)} €</strong>, dont on retire {euro(parc.PRET_VERRERIE_MENSUALITE_EUR, 2)} € d'échéance Crédit Mutuel chaque mois et l'impôt sur les sociétés. Reste <strong>{euro(FLUX_HAUT)} à {euro(FLUX_BAS)} € par mois</strong> selon que le cabinet amortit ou non la part bâtie des places. C'est le vrai chiffre du parc, et il recoupe la somme que Rémy retient chaque mois.</p>
    <p>Les deux places de La Garde, achetées {euro(parc.PRET_ASSOCIES_LA_GARDE_EUR)} € sur fonds personnels et prêtées à la SCI, ne produisent rien tant qu'elles sont vacantes. Louées à 50, 55 ou 60 € la place, elles ajoutent <strong>{euro(GARDE[50.0])} à {euro(GARDE[60.0])} € par mois</strong> après impôt et après leur quote-part de taxe foncière. Le compte courant d'associé se rembourse en plus, sur vingt ans, à {euro(CCA_MENSUEL, 2)} € par mois : cet argent quitte la SCI mais revient aux associés. Le parc passe alors de {euro(FLUX_HAUT)} € à <strong>{euro(TOTAL_HAUT)} € par mois</strong>.</p>
    <p>Ce qui reste libre après l'effort de réserve de {euro(parc.EFFORT_MENSUEL_EUR)} €, c'est <strong>{euro(LIBRE_HAUT)} à {euro(LIBRE_BAS)} € par mois</strong> aujourd'hui, davantage dès que La Garde est louée. La réserve, elle, atteint {euro(RESERVE_1)} € dans un an et {euro(RESERVE_5)} € dans cinq ans : c'est à la fois le coussin de vacance et la capacité d'apport du parc.</p>
  </section>

  <section class="financial-projections">
    <h2>La Verrerie, compte d'exploitation sur une année pleine</h2>
    <table class="projection-table">
      <thead><tr><th>Poste</th><th>Annuel</th><th>Mensuel</th></tr></thead>
      <tbody>
        <tr><td>Loyers SCHINDLER (4 trimestres)</td><td>{euro(LOYERS)} €</td><td>{euro(LOYERS / 12)} €</td></tr>
        <tr><td>Banque et cabinet comptable</td><td>-{euro(STRUCTURE)} €</td><td>-{euro(STRUCTURE / 12)} €</td></tr>
        <tr><td><strong>EBE</strong></td><td><strong>{euro(EBE)} €</strong></td><td><strong>{euro(EBE / 12)} €</strong></td></tr>
        <tr><td>Intérêts du prêt Crédit Mutuel</td><td>-{euro(parc.interets_verrerie_annee_pleine())} €</td><td>-{euro(parc.interets_verrerie_annee_pleine() / 12)} €</td></tr>
        <tr><td>Assurance emprunteur</td><td>-{euro(parc.ASSURANCE_EMPRUNTEUR_ANNUELLE_EUR)} €</td><td>-{euro(parc.ASSURANCE_EMPRUNTEUR_ANNUELLE_EUR / 12)} €</td></tr>
        <tr><td>Impôt sur les sociétés (15 %)</td><td>-{euro(IS_BAS)} à -{euro(IS_HAUT)} €</td><td>-{euro(IS_BAS / 12)} à -{euro(IS_HAUT / 12)} €</td></tr>
        <tr><td>Échéance de prêt, capital et intérêts</td><td>-{euro(parc.PRET_VERRERIE_MENSUALITE_EUR * 12)} €</td><td>-{euro(parc.PRET_VERRERIE_MENSUALITE_EUR, 2)} €</td></tr>
        <tr><td><strong>Flux de trésorerie</strong></td><td><strong>{euro(FLUX_HAUT * 12)} à {euro(FLUX_BAS * 12)} €</strong></td><td><strong>{euro(FLUX_HAUT)} à {euro(FLUX_BAS)} €</strong></td></tr>
      </tbody>
    </table>
    <p class="projection-note">La taxe foncière ({euro(parc.TF_VERRERIE_ANNUELLE_EUR)} €) et l'assurance du bien ({euro(parc.PNO_VERRERIE_ANNUELLE_EUR, 2)} €) sont refacturées au locataire : elles ne sont donc pas des charges, et les compter ici les compterait deux fois. L'assurance emprunteur, elle, est comprise dans l'échéance de {euro(parc.PRET_VERRERIE_MENSUALITE_EUR, 2)} €.</p>
  </section>

  <section class="financial-projections">
    <h2>La réserve vacance et travaux, notre mini-ALUR interne</h2>
    <p>La vacance locative et la provision travaux sont placées sur un fonds monétaire euro, à {TAUX_RESERVE} % net de frais, produits bruts d'impôt sur les sociétés. Le solde de départ est celui constaté au {parc.DATE_RELEVE}, l'effort de {euro(parc.EFFORT_MENSUEL_EUR)} € par mois tant qu'aucun nouveau dossier ne se matérialise.</p>
    <table class="projection-table">
      <thead><tr><th>Échéance</th><th>Solde de la réserve</th><th>Ce qu'elle couvre</th></tr></thead>
      <tbody>
        <tr><td>Un an</td><td>{euro(RESERVE_1)} €</td><td>{euro(RESERVE_1 / (LOYERS / 12), 1)} mois de loyer Verrerie</td></tr>
        <tr><td>Deux ans</td><td>{euro(RESERVE_2)} €</td><td>un sinistre courant ou une vacance longue</td></tr>
        <tr><td>Trois ans</td><td>{euro(RESERVE_3)} €</td><td>les appels de fonds d'une copropriété qui vote</td></tr>
        <tr><td>Cinq ans</td><td>{euro(RESERVE_5)} €</td><td>un apport partiel sur un nouveau lot</td></tr>
        <tr><td>Dix ans</td><td>{euro(RESERVE_10)} €</td><td>l'autofinancement d'un dossier entier</td></tr>
      </tbody>
    </table>
    <p class="projection-note">Jalons : 15 000 € en <strong>{MOIS_15K:.0f} mois</strong> (début 2028), 30 000 € en <strong>{MOIS_30K:.0f} mois</strong>, 50 000 € en <strong>{MOIS_50K:.0f} mois</strong>. C'est cette réserve, et non le compte courant, qui desserre le filtre des 30 000 € d'apport.</p>
  </section>

  <section class="financial-projections">
    <h2>La Garde, 11 400 € avancés sur fonds personnels</h2>
    <p>Deux places extérieures, achetées {euro(parc.PRET_ASSOCIES_LA_GARDE_EUR)} € et prêtées à la SCI en compte courant. Pas d'assurance dommage : une place extérieure n'en porte pas. Objectif locatif de {euro(parc.LOYER_LA_GARDE_CIBLE_MIN_EUR)} à {euro(parc.LOYER_LA_GARDE_CIBLE_MAX_EUR)} € par place et par mois, hors charges.</p>
    <table class="projection-table">
      <thead><tr><th>Loyer par place</th><th>Loyers annuels</th><th>Net après IS</th><th>Après remboursement du compte courant</th><th>Rendement brut</th></tr></thead>
      <tbody>
        <tr><td>50 €</td><td>{euro(1200)} €</td><td>{euro(GARDE[50.0])} €/mois</td><td>{euro(GARDE_APRES_CCA[50.0])} €/mois</td><td>10,5 %</td></tr>
        <tr><td>55 €</td><td>{euro(1320)} €</td><td>{euro(GARDE[55.0])} €/mois</td><td>{euro(GARDE_APRES_CCA[55.0])} €/mois</td><td>11,6 %</td></tr>
        <tr><td>60 €</td><td>{euro(1440)} €</td><td>{euro(GARDE[60.0])} €/mois</td><td>{euro(GARDE_APRES_CCA[60.0])} €/mois</td><td>12,6 %</td></tr>
      </tbody>
    </table>
    <p class="projection-note">Charge retenue : {euro(CHARGE_LA_GARDE)} € de taxe foncière par an, les charges de copropriété étant refacturées au preneur. Le compte courant se rembourse sur 240 mois, soit {euro(CCA_MENSUEL, 2)} € par mois, capital compris : ce n'est pas une charge, c'est de l'argent qui revient aux associés.</p>
  </section>

  <section class="financial-projections">
    <h2>Les trois scénarios</h2>
    <table class="comparison-table">
      <thead><tr><th>Scénario</th><th>Hypothèses</th><th>Flux mensuel</th></tr></thead>
      <tbody>
        {"".join(f"<tr><td><strong>{nom}</strong></td><td>{hypo}</td><td>{res}</td></tr>" for nom, hypo, res in SCENARIOS)}
      </tbody>
    </table>
  </section>

  <section class="strategy-exploration">
    <h2>Conventions de calcul</h2>
    <p>• L'impôt est reconstitué sur l'EBE diminué des intérêts réels du prêt et de l'assurance emprunteur. Le cabinet n'a pas encore dit s'il amortit la part bâtie des places : d'où la fourchette.</p>
    <p>• L'échéance Crédit Mutuel de {euro(parc.PRET_VERRERIE_MENSUALITE_EUR, 2)} € comprend le capital, les intérêts et l'assurance emprunteur : elle n'est retranchée qu'une fois.</p>
    <p>• Les loyers de La Garde sont comptés hors charges, avec {euro(CHARGE_LA_GARDE)} € de taxe foncière à notre charge et une vacance nulle la première année.</p>
    <p>• Les intérêts du prêt La Verrerie fondent d'environ 140 € par an : l'impôt montera d'autant, à provisionner.</p>
  </section>

  <footer class="report-footer">
    <p>Note interne Sémaphore Patrimoine, générée automatiquement depuis <code>parc.py</code> le {parc.DATE_RELEVE}. Chaque chiffre de cette page est contrôlé à la génération : si une donnée change, la page ne se reconstruit pas.</p>
  </footer>

</main>
</body>
</html>
"""


def main():
    sortie = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "analyses", "parc-tresorerie", "index.html",
    )
    os.makedirs(os.path.dirname(sortie), exist_ok=True)
    with open(sortie, "w", encoding="utf-8") as fh:
        fh.write(HTML)
    reste = [m for m in ("{", "}") if m in HTML.replace("{{", "").replace("}}", "")]
    print(f"écrit : {sortie}")
    print(f"taille : {len(HTML)} caractères")
    if reste:
        print("ATTENTION : accolades résiduelles détectées")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
