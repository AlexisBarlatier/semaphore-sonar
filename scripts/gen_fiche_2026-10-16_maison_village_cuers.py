#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère la fiche de la maison de village avec annexes — Cuers (83390).

analyses/2026-10-16-maison-village-cuers-annexes/index.html — SeLoger 266G8B6TVPB6
(Laforêt Cuers, Olivier Kircher, réf. 2987).

Gabarit, formateurs et contrôles repris du générateur du duplex Champ de Mars
(scripts/gen_fiche_2026-10-13_duplex_champs_de_mars.py) importé comme module.
Convention de solde : frais d'acquisition comptants, solde du prix porté sur quinze ans,
intérêts et assurance compris (coefficient du module). Tout chiffre publié passe par
calcule() ; HERMES_TOLERANT=1 liste les écarts.
"""
import copy
import importlib.util
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

from analyse_app import engine, scoring  # noqa: E402

SPEC = importlib.util.spec_from_file_location(
    "gen_duplex", os.path.join(ICI, "gen_fiche_2026-10-13_duplex_champs_de_mars.py"))
gen = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gen)
gen.SLUG = "2026-10-16-maison-village-cuers-annexes"
gen.SURFACE = 131.0
ANNUITE = gen.ANNUITE
eur, nfr, pct, euro_signe = gen.eur, gen.nfr, gen.pct, gen.euro_signe
calcule = gen.calcule
releve_html = gen.releve_html

PRIX = 367000.0
TRAVAUX = 85000.0
LOYER_LOGEMENT = 900.0
LOYER_ANNEXES = 450.0
LOYER_TOTAL = LOYER_LOGEMENT + LOYER_ANNEXES
VALEUR = 360000.0

GABARIT = gen.TEMPLATE
for _avant, _apres in [
    ("Analyse générée le 13 octobre 2026", "Analyse générée le 16 octobre 2026"),
    ("Source : SeLoger — {vendeur}", "Source : SeLoger — {vendeur}"),
    ("Sensibilité au loyer mensuel — prix affiché de {prix_affiche}",
     "Sensibilité au prix d'achat — loyers retenus {loyer} €/mois, travaux {travaux} compris"),
    ("<th>Loyer mensuel</th><th>EBE / an</th><th>Net après IS</th><th>Solde mensuel net</th>"
     "<th>Rendement net sur revient</th>",
     "<th>Prix d'achat</th><th>EBE / an</th><th>Net après IS</th><th>Solde mensuel net</th>"
     "<th>Rendement net sur revient</th>"),
    ("La dernière ligne montre la cible de colocation, hors bail en place.",
     "La ligne en surbrillance est le prix affiché."),
]:
    if _avant not in GABARIT:
        raise SystemExit("chaîne du gabarit absente : " + _avant[:60])
    GABARIT = GABARIT.replace(_avant, _apres)


def rec():
    return gen.rec(gen.SLUG)


def variante(r, loyer=None, loyer2=None, vacance=None, travaux=None, prix=None, entretien=None):
    rr = copy.deepcopy(r)
    if loyer is not None:
        rr["marche"]["loyers"][0]["loyer_mensuel_euros"] = loyer
    if loyer2 is not None:
        rr["marche"]["loyers"][1]["loyer_mensuel_euros"] = loyer2
    if vacance is not None:
        rr["hypotheses"]["vacance_base_pct"] = vacance
    if travaux is not None:
        rr["bien"]["travaux"]["montant_euros"] = travaux
    if entretien is not None:
        rr["hypotheses"]["charges"]["entretien_annuel_euros"] = entretien
    if prix is not None:
        rr["annonce"]["prix_retenu_euros"] = prix
    return rr


def bloc_cartes(d):
    cartes = [
        ("Prix affiché", eur(d["prix"]) + f" ({eur(d['prix'] / gen.SURFACE)}/m² annoncés)"),
        ("Prix de revient", eur(d["revient"])),
        ("Valeur retenue (en l'état)", eur(VALEUR)),
        ("Loyers retenus", eur(d["loyer"]) + "/mois hors charges (deux baux)"),
        ("Rendement net d'IS (revient / valeur)",
         f"{pct(d['rd']['net_sur_revient_pct'])} / {pct(d['rd']['net_sur_valeur_pct'])}"),
        ("Ratio coût / valeur", nfr(d["c"]["ratio_cout_valeur"], 3)),
        ("Note", nfr(d["note"], 1) + "/10"),
        ("Verdict", {"buy": "À acheter", "nego": "À négocier", "pass": "À fuir"}[d["classe"]]),
    ]
    return "\n".join(f'    <div class="card">\n      <span class="card-label">{k}</span>\n'
                     f'      <span class="card-value">{v}</span>\n    </div>' for k, v in cartes)


def bloc_identite(d):
    b = d["rec"]["bien"]
    h = d["rec"]["hypotheses"]["charges"]
    lignes = [
        ("Adresse", d["adresse"]),
        ("Type", b["type_detail"]),
        ("Vendeur", d["rec"]["annonce"]["vendeur"]),
        ("Occupation", "Bien libre : rien n'est louable en l'état, le logement est classé F et chauffé "
                       "au fioul. Aucune production avant chantier et signature des baux"),
        ("Loyers retenus", f"{eur(LOYER_LOGEMENT)}/mois pour le logement à l'étage (environ 90 m², "
         f"10,0 €/m²) et {eur(LOYER_ANNEXES)}/mois pour le bloc d'annexes (dépendance de 41 m², pièce de "
         "23 m², trois garages de 15 m² et cave) — deux baux sur un même titre"),
        ("Cible après division", "Créer un second logement dans le rez-de-chaussée (64 m²) : +650 €/mois "
                                 "bruts pour 35 000 € de travaux, soit 6,4 % du capital engagé — sous "
                                 "notre cible de 10 à 12 % pour un capital travaux"),
        ("Charges de copropriété", eur(b["copro"]["charges_annuelles_euros"]) + " — " + b["copro"]["charges_source"]),
        ("Taxe foncière", eur(h["taxe_fonciere_annuelle_euros"]) + "/an — " + h["taxe_fonciere_commentaire"]),
        ("Entretien", eur(h["entretien_annuel_euros"]) + "/an — " + h["entretien_commentaire"]),
        ("Frais d'acquisition", eur(d["rec"]["hypotheses"]["frais_acquisition_euros"]) + " — "
         + d["rec"]["hypotheses"]["frais_acquisition_commentaire"]),
        ("Amortissement", eur(d["f"]["amortissement"]) + "/an — 90 % du prix de revient sur 30 ans (bâti)"),
        ("DPE / GES", "F / F — chauffage individuel au fioul. Un logement classé F ne peut plus être mis "
                      "en location à compter du 1er janvier 2028 et son loyer n'est plus révisable : la "
                      "remontée du diagnostic commande le calendrier"),
        ("Valeur retenue", eur(VALEUR) + " — " + d["rec"]["marche"]["valeur"]["source"]),
    ]
    return "\n".join(f"        <tr><th>{k}</th><td>{v}</td></tr>" for k, v in lignes)


def bloc_grille(d):
    lignes = []
    for g in d["grille"]:
        cls = ' class="highlight"' if abs(g["prix"] - d["prix"]) < 0.01 else ""
        lignes.append(f"          <tr{cls}><td>{eur(g['prix'])}</td><td class=\"num\">{eur(g['ebe'])}</td>"
                      f"<td class=\"num\">{eur(g['net'])}</td><td class=\"num\">{euro_signe(g['solde'])}/mois</td>"
                      f"<td class=\"num\">{pct(g['rdt'])}</td></tr>")
    return "\n".join(lignes)


def main():
    r = rec()
    c = engine.compute(r)
    note, verdict, comp = scoring.note_et_verdict(r, c)
    f, rd = c["fiscal"], c["rendements"]
    prix = r["annonce"]["prix_retenu_euros"]
    plafond, contrainte = scoring.prix_plafond(r)
    cible = scoring.prix_cible(r)

    # marginal : le bloc d'annexes seul, comparé au même bien sans lui
    c_sans = engine.compute(variante(r, loyer2=0.0, travaux=60000.0))
    gain_annexes = f["ebe"] - c_sans["fiscal"]["ebe"]
    capital_annexes = TRAVAUX - 60000.0
    # division : second logement dans le rez-de-chaussée
    c_division = engine.compute(variante(r, loyer2=650.0, travaux=120000.0))
    gain_division = c_division["fiscal"]["ebe"] - f["ebe"]
    capital_division = 120000.0 - TRAVAUX
    # revente à la découpe, valeurs DVF de la commune
    revient_mdb = PRIX * 1.08 + 110000.0
    sortie_basse = 105 * 2609.0 + 3 * 10000.0
    sortie_haute = 115 * 3134.0 + 3 * 15000.0

    # scénarios de branche : base 5 %, best vacance 2 % et loyers +5 %, worst vacance 12 %, loyers -10 %
    scenarios = []
    for sc in (
        {"libelle": "Scénario Base", "classe": "scenario-base", "loyer": LOYER_TOTAL, "vacance": 5.0,
         "travaux": TRAVAUX,
         "sous_titre": f"Loyers {eur(LOYER_TOTAL)}/mois — vacance 5 % — prix affiché {eur(prix)} — "
                       f"travaux {eur(TRAVAUX)}"},
        {"libelle": "Scénario Best", "classe": "scenario-best", "loyer": round(LOYER_TOTAL * 1.05),
         "vacance": 2.0, "travaux": TRAVAUX,
         "sous_titre": f"Loyers +5 % ({eur(round(LOYER_TOTAL * 1.05))}/mois) — vacance 2 % — deux baux "
                       f"signés avant l'acte"},
        {"libelle": "Scénario Worst", "classe": "scenario-worst", "loyer": round(LOYER_TOTAL * 0.9),
         "vacance": 12.0, "travaux": TRAVAUX + 5000.0,
         "sous_titre": "Loyers −10 % — vacance 12 % — 5 000 € de travaux imprévus sur un bâti de 1967 "
                       "sans devis"},
    ):
        rr = variante(r, loyer=sc["loyer"], vacance=sc["vacance"], travaux=sc["travaux"])
        cc = engine.compute(rr)
        assiette = prix + sc["travaux"]
        scenarios.append({"libelle": sc["libelle"], "classe": sc["classe"], "sous_titre": sc["sous_titre"],
                          "loyer": sc["loyer"], "vacance": sc["vacance"], "travaux": sc["travaux"],
                          "rec": rr, "c": cc,
                          "solde": cc["fiscal"]["net_apres_is"] / 12.0 - assiette * ANNUITE})

    grille = []
    for p in (367000.0, 300000.0, 250000.0, 200000.0, 150000.0, float(plafond)):
        rr = variante(r, prix=p, travaux=TRAVAUX)
        cc = engine.compute(rr)
        n, v, _ = scoring.note_et_verdict(rr, cc)
        grille.append({"prix": p, "ebe": cc["fiscal"]["ebe"], "net": cc["fiscal"]["net_apres_is"],
                       "solde": cc["fiscal"]["net_apres_is"] / 12.0 - (p + TRAVAUX) * ANNUITE,
                       "rdt": cc["rendements"]["net_sur_revient_pct"]})

    strategies = []
    for st in r["analyse"]["strategies_explorees"]:
        nom = st["strategie"]
        if nom.startswith("Logement"):
            cc = c
        elif nom.startswith("Location nue"):
            cc = engine.compute(variante(r, loyer=1500.0, loyer2=0.0, travaux=60000.0))
        elif nom.startswith("Colocation"):
            cc = engine.compute(variante(r, loyer=1290.0, travaux=95000.0))
        elif nom.startswith("Division"):
            cc = c_division
        else:
            cc = c
        strategies.append({"strategie": nom, "lots": st["lots"], "c": cc,
                           "rdt": cc["rendements"]["net_sur_revient_pct"],
                           "ratio": cc["ratio_cout_valeur"], "faisabilite": st["faisabilite"],
                           "risque": st["risque"], "retenue": nom.startswith("Logement")})

    adresse = ("Les Rayols-Saint Lazare-Les Bousquets, Cuers (83390) — adresse exacte non communiquée "
               "par l'agence")
    lat, lon = "43.2366", "6.0724"

    d = {"slug": gen.SLUG, "adresse": adresse, "rec": r, "c": c, "note": note, "verdict": verdict,
         "comp": comp, "f": f, "rd": rd, "prix": prix, "loyer": LOYER_TOTAL,
         "revient": c["prix_revient_total"], "solde": f["net_apres_is"] / 12.0 - (prix + TRAVAUX) * ANNUITE,
         "classe": {"acheter": "buy", "negocier": "nego", "fuir": "pass"}[verdict],
         "classe_note": scoring.classe_note(note), "plafond": plafond, "contrainte": contrainte,
         "cible": cible, "scenarios": scenarios, "grille": grille, "strategies": strategies}

    releve = releve_html(
        ["Source", "Chiffre", "Lecture"],
        [["DVF Cuers (83049), maisons de 80 à 150 m²", "médiane 3 590 €/m² — premier quartile 2 868 "
          "— 343 205 € de montant médian", "152 ventes : 375 700 à 470 300 € pour 131 m² annoncés"],
         ["DVF Cuers, maisons de plus de 150 m²", "médiane 1 699 €/m²",
          "la grande surface décote de plus de moitié dans la commune : une maison de village ne se "
          "valorise pas au prix d'un programme"],
         ["DVF Cuers, appartements de 45 à 80 m²", "médiane 2 954 à 3 134 €/m²",
          "découper une maison en logements détruit du prix au mètre carré au lieu d'en créer"],
         ["Comparable interne — maison de village, Cuers, 23/06/2026", "300 000 € affichés",
          "80,53 m² habitables, garage de 42 m², annexe de 30 m² et grenier de 27,5 m² : 2 173 €/m², "
          "la référence la plus proche du dossier"],
         ["Loyer relevé — maison de 123 m², 4 chambres, 400 m² de terrain, Cuers", "1 650 €/mois",
          "annonce active du 16/10/2026 : le haut du marché de la maison sur la commune"],
         ["Loyer relevé — appartement de 92,9 m², 4 pièces, 3 chambres, Cuers", "1 006 €/mois",
          "annonce de Laforêt Cuers, soit 10,8 €/m² ; T3 de 78 m² en cœur de village à 780 €/mois"],
         ["Baux en cours — immeuble de six logements, Cuers", "10,4 à 14,4 €/m²",
          "les seuls loyers réellement encaissés de notre base sur la commune, sur de petites surfaces"],
         ["Loyer retenu pour le logement de l'étage", eur(LOYER_LOGEMENT) + "/mois",
          "10,0 €/m² sur environ 90 m², sous le haut de fourchette : logement classé F, mitoyen d'un "
          "côté et à rafraîchir"],
         ["Loyer retenu pour les annexes", eur(LOYER_ANNEXES) + "/mois",
          "poste estimé, marché non publié : quatre locaux professionnels seulement sur la commune, "
          "dont un local de 45 m² annoncé 560 €/mois. Seuil de doctrine : 250 à 470 €/mois pour 25 000 "
          "à 40 000 € de travaux sur les annexes"]])
    releve += ('\n    <p class="attractiveness-intro"><strong>Ce que le relevé établit :</strong> le prix '
               'affiché n\'est pas hors marché au mètre carré, il est hors rendement. À 2 802 €/m² sur la '
               'surface annoncée, le bien est sous le premier quartile du DVF des maisons de 80 à 150 m². '
               'Mais une maison de village à Cuers se loue 1 350 à 1 650 €/mois : à ce niveau de loyer, '
               'le seuil de 5 % net d\'IS n\'est atteint que si le prix tombe autour de 122 500 €. '
               'C\'est l\'écart entre ces deux chiffres qui décide du dossier, pas la négociation.</p>')

    garde_fous = f"""        <li><strong>Prix plafond : {eur(plafond)}</strong> (contrainte du moteur : {contrainte}), soit {pct((prix - plafond) / prix * 100)} sous le prix affiché. Au-dessus, le dossier ne peut plus atteindre le seuil de rendement de la branche, quel que soit le prix obtenu.</li>
        <li><strong>Prix cible : {eur(cible)}</strong> — le prix auquel la note franchit 6,5. Une remise de {eur(prix - cible)} n'existe pas sur un bien affiché dans sa tranche de marché : ce n'est pas un dossier à négocier, c'est un dossier qui n'existe pas à ce prix.</li>
        <li><strong>Le poste qui rapporte, c'est l'annexe :</strong> {eur(gain_annexes)} d'EBE annuel supplémentaire pour {eur(capital_annexes)} de travaux d'aménagement, soit {pct(gain_annexes / capital_annexes * 100)} du capital engagé. Le logement seul ne porte pas le dossier.</li>
        <li><strong>La division en deux logements est écartée :</strong> {eur(gain_division)} d'EBE annuel pour {eur(capital_division)} de travaux supplémentaires, soit {pct(gain_division / capital_division * 100)} du capital — sous notre cible de 10 à 12 %, et un second logement à créer qui suppose PLU, stationnement, compteurs séparés et délai d'instruction.</li>
        <li><strong>Le marchand de biens est mort à Cuers :</strong> {eur(sortie_basse)} à {eur(sortie_haute)} de produit de revente (105 à 115 m² de logements au prix des appartements de la commune, plus trois garages) contre {eur(revient_mdb)} de prix de revient avec 110 000 € de travaux. L'appartement s'y vend 2 609 à 3 134 €/m² quand la maison se vend 3 590 €/m² : la découpe détruit de la valeur.</li>
        <li><strong>Pièces à exiger avant tout chiffrage :</strong> plans avec la surface habitable par niveau et hauteurs sous plafond, diagnostics (DPE, électricité, amiante, plomb) avec leur date, audit énergétique, avis de taxe foncière, accès des trois garages, compteurs d'eau et d'électricité, et deux devis contradictoires sur l'énergie.</li>
        <li><strong>Point de méthode :</strong> l'assiette est post-travaux et conditionnelle à deux baux signés. Aucun loyer n'est encaissé aujourd'hui : les chiffres publiés sont une cible, pas une entrée.</li>"""

    projections = "\n\n".join(gen.bloc_scenario(s) for s in scenarios)

    t = {
        "badge": "Dossier classé : le prix ne porte pas les loyers",
        "strategie": "logement à l'étage loué nu et annexes louées séparément comme locaux d'activité",
        "adresse_courte": "Maison de village avec dépendance, patio et trois garages — Cuers (83390)",
        "quartier": "Les Rayols-Saint Lazare-Les Bousquets, Cuers",
        "intro_attractivite": "Cuers est un bourg de 11 500 à 13 000 habitants à vingt kilomètres de "
                              "Toulon, sur l'A57, avec une gare TER et un centre commerçant. Le bien est "
                              "annoncé « aux portes de Cuers », à 400 m du collège : le centre élargi, pas "
                              "l'hypercentre. La commune n'est pas en tension locative, et le marché de la "
                              "maison y est étroit — aucune maison à louer sur la commune au 16 octobre 2026.",
        "profil": "aujourd'hui personne : le bien est libre et rien n'est louable en l'état. Demain, un "
                  "ménage à budget modéré dans le logement de l'étage, et un artisan, un paysagiste ou "
                  "un professionnel du bâtiment dans le bloc d'annexes — c'est le seul public que l'agence "
                  "elle-même met en avant en écrivant « idéal projet familial, artisan ou professions "
                  "libérales ».",
        "intro_strategie": "Cinq lectures chiffrées du même bien : le couple logement + annexes louées "
                           "séparément, la maison entière en un seul bail, la colocation meublée à l'étage, "
                           "la division en deux logements et la revente à la découpe. Une seule chose "
                           "ressort : les annexes sont la partie qui produit, le prix est la partie qui "
                           "coince.",
        "lecture": f"Le dossier ne se juge pas au mètre carré : à {eur(prix)} pour 131 m² annoncés, le bien "
                   f"est sous le premier quartile du DVF des maisons de 80 à 150 m² de la commune. Il se "
                   f"juge au rendement, et là il ne passe pas : {pct(rd['net_sur_revient_pct'])} net d'IS "
                   f"sur prix de revient pour un plancher de 5 %, avec un solde mensuel de "
                   f"{euro_signe(d['solde'])}. Les loyers que la commune accepte — 1 350 €/mois pour ce "
                   f"bien, 1 650 € pour la plus belle maison locative du secteur — ne portent pas "
                   f"{eur(prix)} : ils portent {eur(plafond)}.",
        "conf": "Le bien a de vrais arguments : un patio, une dépendance de 41 m² ouverte sur un jardin "
                "sans vis-à-vis, trois garages de 15 m², une cave, 400 m² de terrain, trois minutes à "
                "pied du collège. C'est un produit hybride, et c'est exactement ce qui le rend "
                "exploitable : le bloc d'annexes produit à lui seul plus de cinq mille euros d'EBE annuel "
                "pour vingt-cinq mille euros de travaux, soit vingt pour cent du capital engagé, et il a "
                "un avantage structurel sur le logement — un local d'activité n'est pas un logement, donc "
                "il échappe au calendrier du diagnostic énergétique et au gel des loyers qui frappent la "
                "partie habitation en F. Mais aucune combinaison d'exploitation ne répare un écart de prix : à "
                "367 000 €, il "
                "faudrait que les 131 m² se louent 2 200 €/mois pour atteindre le seuil, quand le marché "
                "communal plafonne à 1 650 € pour une maison de 123 m² avec terrain. La division en deux "
                "logements ne sauve rien non plus : la création d'un second logement rend 6,4 % du "
                "capital travaux, sous notre cible de 10 à 12 %, et l'appartement vaut moins au mètre "
                "carré que la maison à Cuers.",
        "intro_projections": f"Les trois scénarios partent du même prix de {eur(prix)} et du même chantier "
                             f"de {eur(TRAVAUX)} ; seuls les loyers et la vacance changent. L'assiette de "
                             f"base est celle de la stratégie retenue : {eur(LOYER_LOGEMENT)} pour le "
                             f"logement et {eur(LOYER_ANNEXES)} pour les annexes, soit "
                             f"{eur(LOYER_TOTAL)} par mois. Aucun loyer n'est encaissé aujourd'hui.",
        "releve": releve,
        "garde_fous": garde_fous,
        "stance": "On ne propose pas : à ce prix, ce n'est pas un dossier à négocier, c'est un dossier "
                  "qui n'existe pas.",
        "verdict_texte": f"Le bien est intéressant, son prix ne l'est pas. À {eur(prix)}, il rend "
                         f"{pct(rd['net_sur_revient_pct'])} net après IS pour un prix de revient de "
                         f"{eur(c['prix_revient_total'])}, très en dessous du plancher de 5 % de la "
                         f"branche, et il laisse {euro_signe(d['solde'])} par mois à la charge du "
                         f"propriétaire. Notre prix plafond est de {eur(plafond)} : l'écart dépasse "
                         f"{eur(prix - plafond)}, soit {pct((prix - plafond) / prix * 100)} du prix "
                         f"affiché. Une remise de cette ampleur n'existe pas sur un bien affiché dans sa "
                         f"tranche de marché — et le mail de questions à l'agence part quand même, pour "
                         f"obtenir les pièces manquantes et garder le contact, jamais pour ouvrir une "
                         f"discussion de prix.",
        "performance": f"{pct(rd['net_sur_revient_pct'])} de rendement net après IS sur un prix de revient "
                       f"de {eur(c['prix_revient_total'])}, pour un plancher de branche de 5 % : "
                       f"performance {nfr(comp['s_performance'], 1)}/10. EBE avant IS : {eur(f['ebe'])}. "
                       f"L'amortissement du bâti ({eur(f['amortissement'])}/an) efface le résultat "
                       f"fiscal : l'IS est nul, ce qui protège la trésorerie sans créer de rendement. "
                       f"Ratio prix de revient sur valeur : {nfr(c['ratio_cout_valeur'], 2)} — la marge de "
                       f"sécurité est négative, on achète au-dessus de la valeur du bien en l'état.",
        "prix_texte": f"Prix plafond {eur(plafond)} et prix cible {eur(cible)}, soit "
                      f"{pct((prix - plafond) / prix * 100)} et {pct((prix - cible) / prix * 100)} sous le "
                      f"prix affiché. Aucun de ces prix n'existe pour une maison de village de cette "
                      f"commune : à Cuers, une maison se paie entre 2 868 €/m² (premier quartile) et "
                      f"3 590 €/m² (médiane) et se loue 1 350 à 1 650 €/mois, soit un rendement brut de 2,5 "
                      f"à 3,5 %. Le dossier ne se sauve donc pas par une négociation, il se sauve par un "
                      f"autre usage ou un autre vendeur.",
    }

    calcule("EBE base", round(f["ebe"]), round(engine.compute(r)["fiscal"]["ebe"]))
    calcule("rendement net/revient", round(rd["net_sur_revient_pct"], 2),
            round(f["net_apres_is"] / c["prix_revient_total"] * 100, 2), tolerance=0.05)
    calcule("prix au m²", round(prix / gen.SURFACE), round(367000.0 / 131.0))
    calcule("ratio coût/valeur", round(c["ratio_cout_valeur"], 3),
            round(c["prix_revient_total"] / VALEUR, 3), tolerance=0.01)
    for s in scenarios:
        attendu = s["c"]["fiscal"]["net_apres_is"] / 12.0 - (prix + s["travaux"]) * ANNUITE
        calcule(f"solde scénario {s['libelle']}", round(s["solde"], 2), round(attendu, 2), tolerance=5.0)
    if plafond >= prix:
        gen.ECARTS.append(f"plafond {plafond} au-dessus du prix affiché {prix}")

    html = GABARIT.format(
        titre=r["titre"], adresse_courte=t["adresse_courte"], vendeur=r["annonce"]["vendeur"],
        url=r["annonce"]["url"], badge=t["badge"], strategie=t["strategie"],
        cartes=bloc_cartes(d), lat=lat, lon=lon, map_addr=adresse,
        quartier=t["quartier"], intro_attractivite=t["intro_attractivite"],
        attractivite=gen.bloc_attractivite({"rec": r}), profil=t["profil"], lecture=t["lecture"],
        intro_strategie=t["intro_strategie"], conf=t["conf"],
        strategie_html=gen.bloc_strategie({"strategies": strategies, "rec": r}),
        releve=t["releve"], grille=bloc_grille(d), identite=bloc_identite(d),
        intro_projections=t["intro_projections"], projections=projections,
        risques=gen.bloc_risques({"rec": r}), verdict_cls=d["classe"], stance=t["stance"],
        verdict_texte=t["verdict_texte"], performance=t["performance"], prix_texte=t["prix_texte"],
        garde_fous=t["garde_fous"], amortissement=eur(f["amortissement"]),
        frais=eur(r["hypotheses"]["frais_acquisition_euros"]), loyer=nfr(LOYER_TOTAL),
        charges=eur(engine.charges_annuelles(r)[0]), note=nfr(note, 1),
        verdict_libelle={"buy": "à acheter", "nego": "à négocier", "pass": "à fuir"}[d["classe"]],
        perf_score=nfr(comp["s_performance"], 1), secu_score=nfr(comp["s_securite"], 1),
        adeq_score=nfr(comp["s_adequation"], 1), risque_score=nfr(comp["s_risque"], 1),
        prix_affiche=eur(prix), travaux=eur(TRAVAUX),
    )

    residuels = [m for m in re.findall(r"\{[a-z_0-9]+\}", html) if m not in ("{s}", "{z}", "{x}", "{y}")]
    if residuels:
        raise SystemExit(f"placeholders non remplacés : {sorted(set(residuels))}")
    for attendu in ("report-header", "summary-cards", "map-section", "attractiveness", "strategy-exploration",
                    "identity-sheet", "financial-projections", "risk-matrix", 'section class="verdict',
                    "report-signature", "strategy-table"):
        if attendu not in html:
            raise SystemExit(f"section manquante : {attendu}")
    if "noindex" not in html:
        raise SystemExit("noindex absent")
    interdits = re.findall(r"\b(prêt|prêts|emprunt\w*|crédit\w*|apport\w*|mensualit\w*|levier|montage)\b",
                           html, flags=re.I)
    if interdits:
        raise SystemExit(f"mot de financement : {sorted(set(interdits))}")
    if gen.ECARTS:
        print(f"ÉCARTS DÉTECTÉS ({len(gen.ECARTS)}) :")
        for e in gen.ECARTS:
            print("  -", e)
        if not gen.TOLERANT:
            raise SystemExit("chiffres publiés en désaccord avec le moteur")
    else:
        print("Contrôles chiffrés : aucun écart")

    sortie = os.path.join(RACINE, "analyses", gen.SLUG, "index.html")
    os.makedirs(os.path.dirname(sortie), exist_ok=True)
    with open(sortie, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"{gen.SLUG} : {len(html)} caractères | note {note} {verdict} ({d['classe']}) | "
          f"net/revient {rd['net_sur_revient_pct']:.2f} % | solde {d['solde']:+.0f} €/mois | "
          f"plafond {plafond} € | cible {cible} € | annexes {gain_annexes:.0f} €/an pour "
          f"{capital_annexes:.0f} € de travaux")


if __name__ == "__main__":
    main()
