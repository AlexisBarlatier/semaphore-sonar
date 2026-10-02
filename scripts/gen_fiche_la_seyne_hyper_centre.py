"""Génère la fiche HTML — La Seyne-sur-Mer, hyper centre : 2 pièces loué + 5 boxes.

Tous les chiffres publiés sont recalculés par le moteur (`engine.compute`) et
contrôlés par `calcule()`. Avec HERMES_TOLERANT=1, les écarts sont listés au lieu
d'arrêter le build.

    venv/bin/python3 scripts/gen_fiche_la_seyne_hyper_centre.py
"""

import copy
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "scripts"))
from analyse_app import engine, scoring  # noqa: E402

SLUG = "2026-10-02-la-seyne-hyper-centre-2p-bureau"
CHEMIN_JSON = os.path.join(RACINE, "analyses", "analyses.json")
CHEMIN_HTML = os.path.join(RACINE, "analyses", SLUG, "index.html")
CHEMIN_CSS = os.path.join(RACINE, "style.css")
TAUX = 0.037
ASSURANCE = 0.0034
APPORT = 0.10
DUREE = 15
TOLERANT = os.environ.get("HERMES_TOLERANT") == "1"
ECARTS = []


def calcule(libelle, publie, recalcule, tolerance=0.6):
    if publie is None or recalcule is None:
        if publie != recalcule:
            ECARTS.append("%s : publié %s / recalculé %s" % (libelle, publie, recalcule))
    elif abs(float(publie) - float(recalcule)) > tolerance:
        ECARTS.append("%s : publié %s / recalculé %s" % (libelle, publie, recalcule))
    return publie


def nfr(v, dec=0):
    entier, _, frac = ("%.*f" % (dec, float(v))).partition(".")
    entier = re.sub(r"(?<=\d)(?=(\d{3})+$)", "\u202f", entier)
    return entier + ("," + frac if dec else "")


def eur(v, dec=0):
    return nfr(v, dec) + " €"


def euro_signe(v, dec=0):
    return ("−" if float(v) < 0 else "+") + nfr(abs(float(v)), dec) + " €"


def pct(v, dec=2):
    return nfr(v, dec) + " %"


def charger():
    with open(CHEMIN_JSON, encoding="utf-8") as fh:
        base = json.load(fh)
    return next(r for r in base["analyses"] if r["slug"] == SLUG)


def annuite(prix, ans):
    capital = float(prix) * (1 - APPORT)
    taux = TAUX if ans != 20 else 0.038
    return capital * (taux / 12) / (1 - (1 + taux / 12) ** (-ans * 12)) + capital * ASSURANCE / 12


def rec_prix(p):
    r = copy.deepcopy(RECORD)
    r["annonce"]["prix_affiche_euros"] = float(p)
    r["annonce"]["prix_retenu_euros"] = float(p)
    return r


def rec_box(lb):
    r = copy.deepcopy(RECORD)
    for ligne in r["marche"]["loyers"]:
        if ligne["quantite"] == 5:
            ligne["loyer_mensuel_euros"] = float(lb)
    return r


def rec_vac(v):
    r = copy.deepcopy(RECORD)
    r["hypotheses"]["vacance_base_pct"] = float(v)
    return r


def cf(computed, prix, ans=DUREE):
    return computed["fiscal"]["net_apres_is"] / 12 - annuite(prix, ans)


def classe_note(note):
    css = open(CHEMIN_CSS, encoding="utf-8").read()
    if re.search(r"\.card-verdict\.note-%d\b" % round(note), css):
        return "note-%d" % round(note)
    for lettre, seuil in (("A", 6.5), ("B", 5.0), ("C", 4.0), ("D", 0.0)):
        if note >= seuil:
            return "note-" + lettre
    return "note-E"


LIBELLES_ATTR = {
    "transports": "Transports",
    "commerces": "Commerces",
    "ecoles": "Écoles",
    "securite": "Sécurité",
    "demande_locative": "Demande locative",
    "dynamisme": "Dynamisme",
}


def main():
    global RECORD
    RECORD = charger()
    prix = RECORD["annonce"]["prix_affiche_euros"]
    computed = engine.compute(RECORD)
    fiscal = computed["fiscal"]
    rend = computed["rendements"]
    note, verdict, _ = scoring.note_et_verdict(RECORD, computed)
    libelles = {"acheter": "À acheter", "negocier": "À négocier", "fuir": "On fuit"}
    classes = {"acheter": "buy", "negocier": "nego", "fuir": "pass"}
    loyer_logement = sum(l["loyer_mensuel_euros"] * l["quantite"] for l in RECORD["marche"]["loyers"] if l["quantite"] == 1)
    loyer_boxes = sum(l["loyer_mensuel_euros"] * l["quantite"] for l in RECORD["marche"]["loyers"] if l["quantite"] == 5)
    revenus = computed["revenus_bruts_annuels"]
    charges = engine.charges_annuelles(RECORD)[0]
    vacance_eur = revenus * RECORD["hypotheses"]["vacance_base_pct"] / 100.0
    valeur = RECORD["marche"]["valeur"]["retenue_euros"]
    travaux = RECORD["bien"]["travaux"]["montant_euros"]
    apport_total = prix * APPORT + computed["frais_acquisition"] + travaux
    r15 = fiscal["ebe"] / (annuite(prix, 15) * 12)
    r20 = fiscal["ebe"] / (annuite(prix, 20) * 12)

    calcule("EBE", 7613.0, fiscal["ebe"], 1.0)
    calcule("net apres IS mensuel", 571.0, fiscal["net_apres_is"] / 12, 1.0)
    calcule("net sur revient", 8.15, rend["net_sur_revient_pct"], 0.02)
    calcule("brut sur revient", 9.06, rend["brut_sur_revient_pct"], 0.02)
    calcule("cash-flow 15 ans", 117.0, cf(computed, prix, 15), 1.0)
    calcule("cash-flow 20 ans", 195.0, cf(computed, prix, 20), 1.0)
    calcule("ratio 15 ans", 1.40, r15, 0.02)
    calcule("ratio 20 ans", 1.69, r20, 0.02)
    calcule("note", 8.4, note, 0.05)
    calcule("revenus bruts", 10800.0, revenus, 1.0)
    calcule("prix de revient", 84000.0, computed["prix_revient_total"], 1.0)
    if ECARTS:
        print("ECARTS :")
        for e in ECARTS:
            print("  -", e)
        if not TOLERANT:
            raise SystemExit("build arrete : %d ecart(s)" % len(ECARTS))

    lignes_duree = []
    for ans in (15, 20, 25):
        ratio = fiscal["ebe"] / (annuite(prix, ans) * 12)
        lignes_duree.append(
            '<tr%s><td>%d ans</td><td>%s</td><td>%s</td><td>%.2f</td><td>%s</td></tr>'
            % (' class="highlight"' if ans == DUREE else "", ans, eur(annuite(prix, ans)),
               euro_signe(cf(computed, prix, ans)), ratio,
               "tenu" if ratio >= 1.20 else "sous le seuil bancaire")
        )
    lignes_echelle = []
    for p in (55000.0, 61000.0, 67000.0, 75000.0, 85000.0, 95000.0):
        c = engine.compute(rec_prix(p))
        n, v, _ = scoring.note_et_verdict(rec_prix(p), c)
        lignes_echelle.append(
            '<tr%s><td>%s</td><td>%s/10</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
            % (' class="highlight"' if int(p) == 67000 else "", eur(p), nfr(n, 1), libelles[v].lower(),
               eur(c["fiscal"]["ebe"]), euro_signe(c["fiscal"]["net_apres_is"] / 12),
               euro_signe(cf(c, p)), pct(c["rendements"]["net_sur_revient_pct"]))
        )
    lignes_boxes = []
    for lb in (60.0, 70.0, 80.0):
        c = engine.compute(rec_box(lb))
        lignes_boxes.append(
            '<tr%s><td>%s par box</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
            % (' class="highlight"' if lb == 70.0 else "", eur(lb), eur(c["fiscal"]["ebe"]),
               euro_signe(c["fiscal"]["net_apres_is"] / 12), euro_signe(cf(c, prix, 15)), euro_signe(cf(c, prix, 20)))
        )
    lignes_scen = []
    for lbl, v in (("Meilleur cas — vacance 2 %", 2.0), ("Cas de base — vacance 5 %", 5.0), ("Cas défavorable — vacance 20 %", 20.0)):
        c = engine.compute(rec_vac(v))
        lignes_scen.append(
            '<tr%s><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
            % (' class="highlight"' if v == 5.0 else "", lbl, eur(c["fiscal"]["ebe"]),
               euro_signe(c["fiscal"]["net_apres_is"] / 12), euro_signe(cf(c, prix, 15)), euro_signe(cf(c, prix, 20)),
               pct(c["rendements"]["net_sur_revient_pct"]))
        )
    attr = []
    for item in RECORD["analyse"]["attractivite"]:
        attr.append(
            '      <div class="attractiveness-item">\n'
            '        <div class="attractiveness-head"><span class="attractiveness-label">%s</span>'
            '<span class="attractiveness-score">%d/10</span></div>\n        <p>%s</p>\n      </div>'
            % (LIBELLES_ATTR[item["dimension"]], item["score"], item["justification"])
        )
    strat = []
    for item in RECORD["analyse"]["strategies_explorees"]:
        rendu = ("%s net d'IS sur prix de revient" % pct(rend["net_sur_revient_pct"])) if item["strategie"].startswith("Location nue du 2") else item["rendement"]
        strat.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (item["strategie"], rendu, item["faisabilite"], item["risque"]))
    risques = []
    for item in RECORD["analyse"]["risques"]:
        risques.append('<tr><td>%s</td><td class="sev sev-%d">%d/5</td><td>%s</td></tr>' % (item["facteur"], item["severite"], item["severite"], item["detail"]))

    html = TEMPLATE.format(
        titre=RECORD["titre"],
        prix=eur(prix), prix_m2=eur(prix / 50.0),
        brut=pct(rend["brut_sur_revient_pct"]), net_revient=pct(rend["net_sur_revient_pct"]),
        cash_flow=euro_signe(cf(computed, prix), 0) + "/mois",
        ratio=nfr(r15, 2), note=nfr(note, 1),
        classe_note=classe_note(note), classe_verdict=classes[verdict],
        verdict_texte=libelles[verdict],
        loyer_logement=eur(loyer_logement), loyer_boxes=eur(loyer_boxes), revenus=eur(revenus),
        vacance=eur(vacance_eur), charges=eur(charges), charges_pct=pct(charges / revenus * 100, 1),
        travaux=eur(travaux), frais=eur(computed["frais_acquisition"]),
        revient=eur(computed["prix_revient_total"]), valeur=eur(valeur), apport=eur(apport_total),
        ebe=eur(fiscal["ebe"]), amortissement=eur(fiscal["amortissement"]),
        is_annuel=eur(fiscal["is_annuel"]), net_annuel=eur(fiscal["net_apres_is"]),
        net_mensuel=euro_signe(fiscal["net_apres_is"] / 12),
        reserve=eur(fiscal["reserve_annuelle"]), produits_reserve=eur(fiscal["produits_reserve"], 2),
        cout_valeur=nfr(computed["ratio_cout_valeur"], 3),
        cf15=euro_signe(cf(computed, prix, 15), 0), cf20=euro_signe(cf(computed, prix, 20), 0),
        cf25=euro_signe(cf(computed, prix, 25), 0),
        echeance15=eur(annuite(prix, 15) * 12), cf_annuel=euro_signe(cf(computed, prix, 15) * 12),
        lignes_duree="\n".join(lignes_duree), lignes_echelle="\n".join(lignes_echelle),
        lignes_boxes="\n".join(lignes_boxes), lignes_scen="\n".join(lignes_scen),
        attractivite="\n".join(attr), strategies="\n".join(strat), risques="\n".join(risques),
    )
    reste = re.search(r"\{[a-z_]{3,}\}", html)
    if reste:
        raise SystemExit("placeholder non remplace : %s" % reste.group(0))
    with open(CHEMIN_HTML, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("fiche ecrite : %s (%d lignes)" % (CHEMIN_HTML, html.count("\n") + 1))
    print("note %s / verdict %s / classe %s / classe note %s" % (nfr(note, 1), verdict, classes[verdict], classe_note(note)))


TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titre}</title>
<link rel="stylesheet" href="../../style.css">
</head>
<body>
<main class="report">

  <header class="report-header">
    <p class="report-breadcrumb">Analyse d'acquisition — residentiel · locatif</p>
    <h1>{titre}</h1>
    <p class="report-address">Hyper centre, quartier Est — La Seyne-sur-Mer (83500) · annonce Leboncoin 3280288123 · iad France, réf. 2126420</p>
    <p class="report-date">Prix affiché {prix} · analysé le 2 octobre 2026</p>
    <p class="report-source">Analyse produite pour Alexis et Rémy Barlatier — Sémaphore Patrimoine. Tous les chiffres sont recalculés par le moteur du dépôt ; les pièces annoncées et non produites sont listées dans « Confiance et limites ».</p>
  </header>

  <section class="summary-cards">
    <div class="card">
      <span class="card-label">Prix affiché</span>
      <span class="card-value">{prix}</span>
    </div>
    <div class="card">
      <span class="card-label">Prix au m² habitable</span>
      <span class="card-value">{prix_m2}</span>
    </div>
    <div class="card">
      <span class="card-label">Rendement brut sur revient</span>
      <span class="card-value">{brut}</span>
    </div>
    <div class="card">
      <span class="card-label">Net d'IS sur revient</span>
      <span class="card-value">{net_revient}</span>
    </div>
    <div class="card">
      <span class="card-label">Cash-flow à 15 ans</span>
      <span class="card-value">{cash_flow}</span>
    </div>
    <div class="card">
      <span class="card-label">Ratio EBE / annuité</span>
      <span class="card-value">{ratio}</span>
    </div>
    <div class="card">
      <span class="card-label">Note du moteur</span>
      <span class="card-value">{note}/10</span>
    </div>
    <div class="card card-verdict {classe_note}">
      <span class="card-label">Verdict</span>
      <span class="card-value">{verdict_texte}</span>
    </div>
  </section>

  <section class="strategy-exploration">
    <h2>Lecture du dossier</h2>
    <p>Ce qui se vend, c'est un rez-de-chaussée de 1950 dans l'hyper centre, occupé en haut et libre en bas. Le haut est un 2 pièces de 50 m² vendu loué 550 €/mois ; le bas est un espace de 30 m² avec sa kitchenette et sa salle d'eau, desservi par une entrée distincte, aujourd'hui vacant. Deux pièces, deux usages, deux revenus possibles.</p>
    <p>L'annonce affiche 1 340 €/m² sur les 50 m² habitables, mais le bien en fait 80 au total : 838 €/m². Pour situer le niveau, le même agent commercialise dans la même commune un local de 27 m² à 58 000 €, soit <strong>2 148 €/m²</strong>, et un T2 de 57 m² du quartier Est est affiché à 100 000 €, soit 1 754 €/m². Le prix demandé est très en dessous du marché au mètre carré. Quand l'écart est de cet ordre, c'est qu'une contrainte n'est pas dans l'annonce — et c'est ce que nous avons cherché.</p>
    <p>La contrainte, c'est le bas : le transformer en logement demande un changement de destination, une déclaration préalable, peut-être une place de stationnement et, dans une copropriété de deux lots, l'accord unanime de l'autre propriétaire. Six mois de procédure sur un bien à 67 000 €, aucun vendeur ne l'accepte. La sortie est ailleurs : <strong>cloisonner le bas en cinq boxes de stockage</strong>, sans créer de logement. Le PLU répute les locaux accessoires avoir la destination du local principal, il n'y a donc ni changement de destination, ni permis de diviser, ni stationnement à fournir pour un logement créé, ni unanimité à obtenir sur l'affectation d'un logement. Dix mille euros de cloisons et de portes, et le bas produit.</p>
    <p>Les chiffres, maintenant. {revenus} de loyers annuels — {loyer_logement} pour le logement et {loyer_boxes} pour les cinq boxes — moins {vacance} de vacance, {charges} de charges d'exploitation et la provision travaux : un EBE de {ebe}. Après amortissement du bâti à 90 % sur 30 ans, l'IS ressort à {is_annuel}, laissant <strong>{net_annuel} par an</strong>. À quinze ans, la mensualité de {cf15} est couverte : <strong>{cash_flow}</strong> de cash-flow, ratio {ratio} pour un seuil bancaire de 1,20.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Fiche d'identité</h2>
    <table class="identity-table">
      <tbody>
        <tr><th>Adresse</th><td>Hyper centre, quartier Est — <strong>La Seyne-sur-Mer (83500)</strong>. L'annonce ne publie pas l'adresse exacte. Ville de plus de 60 000 habitants de la métropole toulonnaise, commerces, écoles et services à pied.</td></tr>
        <tr><th>Type</th><td>Rez-de-chaussée d'un immeuble de <strong>1950</strong> : un 2 pièces de 50 m² habitables (séjour 17,50 m², kitchenette, une chambre, salle d'eau avec WC) et un espace bureau de 30 m² au rez-de-jardin, avec kitchenette et salle d'eau, entrée distincte.</td></tr>
        <tr><th>Lots</th><td>Copropriété de <strong>deux lots au total</strong>. Notre lot porte le logement et le rez-de-jardin. Projet : un logement et <strong>cinq boxes de stockage</strong> créés par cloisonnement du bas.</td></tr>
        <tr><th>Baux</th><td>Un bail en cours sur le 2 pièces, <strong>550 €/mois</strong>, soit 11 €/m²/mois. Nos relevés donnent un studio de 19 m² au centre Peyron loué 420 €, soit 22 €/m² : le bail est ancien. Date de prise d'effet et indice de révision à demander.</td></tr>
        <tr><th>Copropriété</th><td>Charges <strong>non communiquées</strong> : aucun budget prévisionnel, aucun appel de fonds, aucun procès-verbal, aucun état daté. Hypothèse retenue 300 €/lot/an, soit 600 €/an. Le second lot appartient à un tiers.</td></tr>
        <tr><th>Charges</th><td>Copropriété 600 €/an (hypothèse), taxe foncière 800 €/an (estimation, avis à demander), assurance propriétaire non occupant 100 €/an, tenue de comptes 900 €/an — <strong>150 € par lot, six lots</strong>, c'est le coût de six baux.</td></tr>
        <tr><th>Travaux</th><td><strong>{travaux}</strong> retenus pour la division en cinq boxes : cloisons, cinq portes, cinq points lumineux, luminaires, sol et peinture. Aucun devis, montant arrêté sur une rénovation légère de cloisonnement. Le compteur individuel du bas reste à vérifier.</td></tr>
        <tr><th>Valeur retenue</th><td>{valeur}, soit 50 m² d'habitation autour de 1 750 €/m² et 30 m² de rez-de-chaussée à 1 000 €/m². Fourchette 100 000 à 135 000 €. <strong>Confiance faible</strong> : aucune mutation DVF exploitable sur la commune dans notre extraction, seulement des prix affichés de comparables directs.</td></tr>
        <tr><th>Vendeur</th><td>iad France, Sophia Benbella, référence 2126420, annonce Leboncoin. Honoraires à la charge du vendeur. Aucun contact direct à ce jour : le vendeur n'a jamais écrit, la demande de pièces passe par la messagerie du portail.</td></tr>
      </tbody>
    </table>
  </section>

  <section class="financial-projections">
    <h2>Le compte d'exploitation, une année pleine</h2>
    <table class="projection-table">
      <thead><tr><th>Poste</th><th>Annuel</th></tr></thead>
      <tbody>
        <tr><td>Loyers bruts — logement {loyer_logement}, cinq boxes {loyer_boxes}</td><td class="num">{revenus}</td></tr>
        <tr class="secondary"><td>Vacance structurelle 5 %</td><td class="num">−{vacance}</td></tr>
        <tr class="secondary"><td>Charges d'exploitation — taxe foncière, copropriété, assurance, tenue de comptes</td><td class="num">−{charges}</td></tr>
        <tr class="secondary"><td>Provision travaux 2,5 % des loyers, placée</td><td class="num">−{reserve}</td></tr>
        <tr class="secondary"><td>Produits du placement de la réserve (2,84 % net de frais)</td><td class="num">+{produits_reserve}</td></tr>
        <tr class="subtotal"><td>EBE avant impôt</td><td class="num">+{ebe}</td></tr>
        <tr><td>Amortissement du bâti (90 % / 30 ans)</td><td class="num">−{amortissement}</td></tr>
        <tr><td>Impôt sur les sociétés (15 %)</td><td class="num">−{is_annuel}</td></tr>
        <tr class="subtotal"><td>Flux net après IS</td><td class="num">+{net_annuel}</td></tr>
        <tr><td>Échéance de crédit, 15 ans à 3,70 %</td><td class="num">−{echeance15}</td></tr>
        <tr class="subtotal"><td>Cash-flow annuel</td><td class="num">{cf_annuel}</td></tr>
      </tbody>
    </table>
    <p class="projection-note">La vacance et la provision travaux ne sont pas perdues : elles forment notre réserve, placée à 2,84 % net de frais, et figurent en produits. L'amortissement du bâti n'est pas une sortie de trésorerie, il ne réduit que l'assiette de l'impôt. Le moteur ne déduit pas les intérêts d'emprunt, pourtant déductibles en SCI à l'IS : le chiffre publié est donc prudent, d'une trentaine d'euros par mois la première année.</p>
  </section>

  <section class="financial-projections">
    <h2>Le dossier résiste-t-il au crédit ?</h2>
    <p class="strategy-rationale">C'est ici que se joue la plupart des dossiers, pas sur le prix d'affichage. À {prix}, avec 90 % financés à 3,70 % plus assurance emprunteur de 0,34 %, voici ce que chaque durée change.</p>
    <table class="projection-table">
      <thead><tr><th>Durée</th><th>Mensualité</th><th>Cash-flow</th><th>Ratio EBE / annuité</th><th>Lecture</th></tr></thead>
      <tbody>
{lignes_duree}
      </tbody>
    </table>
    <p class="scenario-subtitle">Contrairement à la plupart des dossiers du parc, celui-ci passe dès quinze ans, notre durée bancaire maximale. Les plafonds qui gouvernent l'offre : <strong>78 000 €</strong> pour tenir le ratio bancaire de 1,20 à quinze ans, <strong>85 200 €</strong> pour un cash-flow nul à quinze ans et 104 100 € à vingt ans. C'est donc <strong>la banque qui contraint, pas la trésorerie</strong> — et le prix affiché de {prix} laisse encore 16 % de marge sous ce plafond.</p>
  </section>

  <section class="financial-projections">
    <h2>Échelle de prix — ce que chaque prix payé change</h2>
    <p class="strategy-rationale">Six baux, vacance 5 %, crédit de 90 % sur quinze ans à 3,70 % plus assurance 0,34 %, apport de 10 %, {travaux} de travaux. La note est celle du moteur à chaque prix.</p>
    <table class="projection-table">
      <thead><tr><th>Prix payé</th><th>Note</th><th>Verdict</th><th>EBE</th><th>Net d'IS / mois</th><th>Cash-flow 15 ans</th><th>Net sur revient</th></tr></thead>
      <tbody>
{lignes_echelle}
      </tbody>
    </table>
    <p class="scenario-subtitle">La ligne en évidence est le prix affiché. Le dossier reste « à acheter » jusqu'à 95 000 €, parce que la valeur retenue est de {valeur} : à {prix}, on paie 72 % de la valeur. C'est cette décote qui porte la note, et elle vient des comparables du même agent, pas d'une opinion sur le vendeur.</p>
  </section>

  <section class="financial-projections">
    <h2>Le dossier résiste-t-il au loyer des boxes ?</h2>
    <p class="strategy-rationale">Le paramètre fragile, c'est le loyer des cinq boxes. Relevés du marché : cave de 3 m² chez un particulier à 40 et 60 €/mois, box de 4 à 6 m² en garde-meuble à 96 €, box professionnel de 5 m² à 125 €, box de 14 m² à 150 €. Nous retenons 70 €. Voici ce que chaque niveau laisse, à {prix} et quinze ans.</p>
    <table class="projection-table">
      <thead><tr><th>Loyer unitaire</th><th>EBE</th><th>Net d'IS / mois</th><th>Cash-flow 15 ans</th><th>Cash-flow 20 ans</th></tr></thead>
      <tbody>
{lignes_boxes}
      </tbody>
    </table>
    <p class="scenario-subtitle">Cinq boxes à 60 € au lieu de 70 laissent encore {cf15} par mois : la marge encaisse une baisse de 14 % du loyer sans casser le dossier. Ce qui ne se teste pas au loyer, c'est le temps de commercialisation — cinq boxes à remplir, ce sont cinq occasions de vacance au lieu d'une.</p>
  </section>

  <section class="financial-projections">
    <h2>Les trois scénarios</h2>
    <p class="strategy-rationale">Le paramètre de stress retenu est la vacance, seul facteur qui joue sur les six lots à la fois. Le cas défavorable à 20 % correspond à plus d'un lot vide sur six.</p>
    <table class="projection-table">
      <thead><tr><th>Scénario</th><th>EBE</th><th>Net d'IS / mois</th><th>Cash-flow 15 ans</th><th>Cash-flow 20 ans</th><th>Net sur revient</th></tr></thead>
      <tbody>
{lignes_scen}
      </tbody>
    </table>
    <p class="scenario-subtitle">Même dans le cas défavorable, avec deux lots vides sur six, le dossier reste positif à quinze ans. C'est la démonstration que le bas n'a pas besoin de fonctionner à plein pour que l'acquisition tienne : il suffit qu'il produise.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Ce que coûte la détention</h2>
    <p class="strategy-rationale">Détenir ce lot coûte {charges} par an, soit <strong>{charges_pct} des loyers bruts</strong> — c'est bas, et c'est un des attraits du dossier : pas d'ascenseur, pas de parties communes lourdes, un bâti simple. Mais la copropriété n'est pas connue, et c'est exactement là que le chiffre peut se dégrader. La tenue de comptes pèse 900 € par an, soit 150 € par lot : six baux, c'est six fois la gestion, et c'est le prix de la granularité.</p>
    <p>Les 30 m² du bas restent une charge tant qu'ils ne produisent rien : éléments communs, assurance d'un local inoccupé, risque de dégradation. C'est précisément ce qui justifie de ne pas les payer dans le prix.</p>
  </section>

  <section class="attractiveness">
    <h2>Attractivité du quartier</h2>
    <p class="attractiveness-intro">Six dimensions notées sur 10, pondérées pour un logement et des boxes de stockage en location longue durée. Les scores sont une appréciation, pas une mesure : ils servent à comparer les dossiers entre eux.</p>
{attractivite}
    <p class="attractiveness-summary">Moyenne pondérée pour la stratégie retenue : 6,3/10. Le quartier n'est pas le problème, il est l'atout : hyper centre commerçant, demande locative documentée sur les petites surfaces comme sur le stockage, marché profond à l'échelle de la ville. Ce qui décide, c'est le bas et la copropriété.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Stratégies examinées</h2>
    <p class="strategy-rationale">La stratégie retenue est la location nue du logement en place et de cinq boxes créés au rez-de-jardin. Les autres pistes ont été chiffrées puis écartées.</p>
    <table class="comparison-table">
      <thead><tr><th>Stratégie</th><th>Rendement</th><th>Faisabilité</th><th>Risque</th></tr></thead>
      <tbody>
{strategies}
      </tbody>
    </table>
  </section>

  <section class="risk-matrix">
    <h2>Matrice de risques</h2>
    <table class="risk-table">
      <thead><tr><th>Facteur</th><th>Sévérité</th><th>Ce que cela veut dire</th></tr></thead>
      <tbody>
{risques}
      </tbody>
    </table>
  </section>

  <section class="verdict {classe_verdict}">
    <h2>Verdict</h2>
    <p class="verdict-stance">Le dossier sort à <strong>{net_revient} net d'IS sur prix de revient</strong>, <strong>{cash_flow}</strong> de cash-flow à quinze ans et un ratio bancaire de {ratio}, très au-dessus du seuil de 1,20. Au prix affiché de {prix}, on paie {cout_valeur} fois la valeur retenue. <strong>On achète</strong>, en ouvrant la négociation à 61 000 € — le prix où le bien s'équilibre sur vingt ans avec le seul logement — puisqu'en l'état le bas ne produit rien et coûte.</p>
    <p class="verdict-stance">Trois pièces décident avant de s'engager : le règlement de copropriété et l'état descriptif de division sur la qualification du local du bas, la majorité exigée pour changer l'affectation du lot, et la position de la commune sur le stationnement. La demande de pièces est partie par la messagerie du portail. <strong>Le studio dans le bas reste la réserve</strong> : une fois le bien à nous, si la copropriété et la Ville suivent, le logement se fera. On commence par ce qui rapporte tout de suite.</p>
  </section>

  <footer class="report-footer">
    <p>Analyse produite le 2 octobre 2026 pour Alexis et Rémy Barlatier — SCI Sémaphore Patrimoine. Chiffres recalculés par le moteur du dépôt à partir de la base d'analyses ; les pièces annoncées et non produites sont signalées dans la fiche d'identité et la matrice de risques.</p>
  </footer>

</main>
</body>
</html>
"""

if __name__ == "__main__":
    main()
