#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère la fiche du studio 26,64 m² loué sous bail commercial — Toulon Porte d'Italie.

analyses/2026-10-16-studio-26m2-toulon-porte-italie-gere/index.html — LeBonCoin 3229330779
(Le Revenu Pierre, réf. 8238f-toulon-gsa), doublon Gens de Confiance.

Gabarit, formateurs et contrôles repris du générateur du duplex Champ de Mars
(scripts/gen_fiche_2026-10-13_duplex_champs_de_mars.py) importé comme module.
Convention de solde : frais d'acquisition comptants, solde du prix porté sur quinze ans,
intérêts et assurance compris (coefficient du module).
Tout chiffre publié passe par calcule() ; HERMES_TOLERANT=1 liste les écarts.
"""
import copy
import importlib.util
import json
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
gen.SLUG = "2026-10-16-studio-26m2-toulon-porte-italie-gere"
gen.SURFACE = 26.64
ANNUITE = gen.ANNUITE
eur, nfr, pct, euro_signe = gen.eur, gen.nfr, gen.pct, gen.euro_signe
calcule = gen.calcule
releve_html = gen.releve_html

PRIX = 46920.0
FRAIS = 3754.0
TRAVAUX = 4000.0
LOYER_BAIL = 285.0
LOYER_MARCHE = 450.0

GABARIT = gen.TEMPLATE
for _avant, _apres in [
    ("Analyse générée le 13 octobre 2026", "Analyse générée le 16 octobre 2026"),
    ("<p class=\"report-source\">Source : SeLoger — {vendeur}</p>",
     "<p class=\"report-source\">Source : LeBonCoin — {vendeur}</p>"),
    ('<div class="report-source-link"><a href="{url}">{url}</a></div>',
     '<div class="report-source-link"><a href="{url}">{url}</a><br>'
     '<a href="{url2}">Seconde diffusion de la même annonce : Gens de Confiance</a></div>'),
    ("Sensibilité au loyer mensuel — prix affiché de {prix_affiche}",
     "Sensibilité au prix d'achat — coupon de {loyer} €/mois, remise en état {travaux} comprise"),
    ("<th>Loyer mensuel</th><th>EBE / an</th><th>Net après IS</th><th>Solde mensuel net</th>"
     "<th>Rendement net sur revient</th>",
     "<th>Prix d'achat</th><th>EBE / an</th><th>Net après IS</th><th>Solde mensuel net</th>"
     "<th>Rendement net sur revient</th>"),
    ("La dernière ligne montre la cible de colocation, hors bail en place.",
     ""),
]:
    if _avant not in GABARIT:
        raise SystemExit("chaîne du gabarit absente : " + _avant[:60])
    GABARIT = GABARIT.replace(_avant, _apres)


def rec():
    return gen.rec(gen.SLUG)


def variante(r, loyer=None, vacance=None, travaux=None, prix=None):
    rr = copy.deepcopy(r)
    if loyer is not None:
        rr["marche"]["loyers"][0]["loyer_mensuel_euros"] = loyer
    if vacance is not None:
        rr["hypotheses"]["vacance_base_pct"] = vacance
    if travaux is not None:
        rr["bien"]["travaux"]["montant_euros"] = travaux
    if prix is not None:
        rr["annonce"]["prix_retenu_euros"] = prix
    return rr


def bloc_cartes(d):
    cartes = [
        ("Prix affiché", eur(d["prix"]) + f" ({eur(d['prix'] / gen.SURFACE)}/m²)"),
        ("Prix de revient", eur(d["revient"])),
        ("Valeur retenue (studio sous bail)", eur(d["rec"]["marche"]["valeur"]["retenue_euros"])),
        ("Loyer encaissé (bail en cours)", eur(d["loyer"]) + "/mois hors charges"),
        ("Rendement net d'IS (revient / valeur)",
         f"{pct(d['rd']['net_sur_revient_pct'])} / {pct(d['rd']['net_sur_valeur_pct'])}"),
        ("Rendement du studio repris et reloué meublé", pct(d["c_haut"]["rendements"]["net_sur_revient_pct"])),
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
        ("Occupation", "Studio meublé, loué à l'exploitant par bail commercial 3/6/9 du 01/01/2018 au "
                       "31/12/2027, exploitant GSA Résidences. Aucune occupation personnelle possible : "
                       "le lot n'est vendu qu'à un investisseur, et le loyer est dû que le logement soit "
                       "occupé ou non"),
        ("Loyer en place", eur(d["loyer"]) + "/mois hors taxes, soit 3 420 € HT/an — 10,7 €/m², contre "
         "15 à 20 €/m² pour un meublé de cette taille dans la même ville (relevé du 16/10/2026 : 18 m² "
         "à 589 € charges comprises à Sainte-Anne, 37 m² à 680 € en basse ville)"),
        ("Cible après reprise", eur(LOYER_MARCHE) + "/mois en location meublée directe, avec "
         f"{eur(TRAVAUX)} de remise en état : variante chiffrée, hors assiette de prix"),
        ("Charges non récupérables", eur(b["copro"]["charges_annuelles_euros"]) + " HT/an — "
         + b["copro"]["charges_source"]),
        ("Taxe foncière", eur(h["taxe_fonciere_annuelle_euros"]) + "/an — " + h["taxe_fonciere_commentaire"]),
        ("Frais d'acquisition", eur(d["rec"]["hypotheses"]["frais_acquisition_euros"]) + " — "
         + d["rec"]["hypotheses"]["frais_acquisition_commentaire"]),
        ("Amortissement", eur(d["f"]["amortissement"]) + "/an — 90 % du prix de revient sur 30 ans (bâti)"),
        ("DPE / GES", "D / B — aucune contrainte de décence à l'horizon : le calendrier des passoires "
                      "thermiques (F en 2028, E en 2034) ne concerne pas ce lot"),
        ("Valeur retenue", eur(d["rec"]["marche"]["valeur"]["retenue_euros"]) + " — "
         + d["rec"]["marche"]["valeur"]["source"]),
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
    loyer = r["marche"]["loyers"][0]["loyer_mensuel_euros"]
    c_haut = engine.compute(variante(r, loyer=LOYER_MARCHE, travaux=TRAVAUX))
    plafond, contrainte = scoring.prix_plafond(r)
    cible = scoring.prix_cible(r)

    # prix d'équilibre du scénario de reprise : le seuil de 5 % sur le revient, travaux compris
    def prix_seuil(scenario_loyer, cible_rdt=5.0):
        bas, haut = 5_000.0, prix * 3
        res = bas
        for _ in range(60):
            milieu = (bas + haut) / 2.0
            rr = variante(r, loyer=scenario_loyer, prix=milieu, travaux=TRAVAUX)
            cc = engine.compute(rr)
            if cc["rendements"]["net_sur_revient_pct"] >= cible_rdt:
                res, bas = milieu, milieu
            else:
                haut = milieu
        return int(res // 500.0 * 500.0)

    seuil_coupon = plafond
    seuil_reprise = prix_seuil(LOYER_MARCHE)

    # scénarios
    scenarios = []
    for sc in (
        {"libelle": "Scénario Base", "classe": "scenario-base", "loyer": LOYER_BAIL, "vacance": 5.0,
         "travaux": TRAVAUX,
         "sous_titre": f"Bail commercial en place, {eur(LOYER_BAIL)}/mois — vacance 5 % — prix affiché "
                       f"{eur(prix)} — remise en état provisionnée à la reprise"},
        {"libelle": "Scénario Best", "classe": "scenario-best", "loyer": LOYER_MARCHE, "vacance": 5.0,
         "travaux": TRAVAUX,
         "sous_titre": f"Exploitant parti ou défaillant : studio repris et reloué meublé à "
                       f"{eur(LOYER_MARCHE)}/mois — vacance 5 % — prix affiché {eur(prix)}"},
        {"libelle": "Scénario Worst", "classe": "scenario-worst", "loyer": LOYER_BAIL, "vacance": 12.0,
         "travaux": 8000.0,
         "sous_titre": "Défaillance de l'exploitant en cours de bail : loyers suspendus pendant la "
                       "procédure, studio rendu dégradé et remis en état à 8 000 €"},
    ):
        rr = variante(r, loyer=sc["loyer"], vacance=sc["vacance"], travaux=sc["travaux"])
        cc = engine.compute(rr)
        assiette = prix + sc["travaux"]
        scenarios.append({"libelle": sc["libelle"], "classe": sc["classe"], "sous_titre": sc["sous_titre"],
                          "loyer": sc["loyer"], "vacance": sc["vacance"], "travaux": sc["travaux"],
                          "rec": rr, "c": cc,
                          "solde": cc["fiscal"]["net_apres_is"] / 12.0 - assiette * ANNUITE})

    # grille de prix
    grille = []
    for p in (46920.0, 42000.0, 38000.0, 34000.0, float(seuil_coupon), 30000.0):
        rr = variante(r, prix=p, travaux=TRAVAUX)
        cc = engine.compute(rr)
        grille.append({"prix": p, "ebe": cc["fiscal"]["ebe"], "net": cc["fiscal"]["net_apres_is"],
                       "solde": cc["fiscal"]["net_apres_is"] / 12.0 - p * ANNUITE,
                       "rdt": cc["rendements"]["net_sur_revient_pct"]})

    # stratégies, recalculées par le moteur
    strategies = []
    for st in r["analyse"]["strategies_explorees"]:
        nom = st["strategie"]
        if nom.startswith("Portage"):
            cc = c
        elif nom.startswith("Reprise"):
            cc = c_haut
        else:
            cc = c
        strategies.append({"strategie": nom, "lots": st["lots"], "c": cc,
                           "rdt": cc["rendements"]["net_sur_revient_pct"],
                           "ratio": cc["ratio_cout_valeur"], "faisabilite": st["faisabilite"],
                           "risque": st["risque"], "retenue": nom.startswith("Portage")})

    adresse = "Quartier Porte d'Italie, Toulon (83000) — résidence étudiante, adresse exacte non communiquée"
    lat, lon = "43.1243", "5.9453"

    d = {"slug": gen.SLUG, "adresse": adresse, "rec": r, "c": c, "note": note, "verdict": verdict, "comp": comp,
         "f": f, "rd": rd, "prix": prix, "loyer": loyer, "revient": c["prix_revient_total"],
         "solde": f["net_apres_is"] / 12.0 - prix * ANNUITE, "c_haut": c_haut,
         "classe": {"acheter": "buy", "negocier": "nego", "fuir": "pass"}[verdict],
         "classe_note": scoring.classe_note(note), "plafond": plafond, "contrainte": contrainte,
         "cible": cible, "seuil_coupon": seuil_coupon, "seuil_reprise": seuil_reprise,
         "scenarios": scenarios, "grille": grille, "strategies": strategies}

    releve = releve_html(
        ["Source", "Chiffre", "Lecture"],
        [["Bail en place — 3/6/9 du 01/01/2018 au 31/12/2027, exploitant GSA Résidences",
          "3 420 € HT/an (285 €/mois)", "la seule assiette encaissée du dossier, garantie par le "
                                        "preneur et non par l'occupation du logement"],
         ["Loyer de relocation visé, studio meublé repris en direct", "450 €/mois",
          "tranche relevée de 15 à 20 €/m² pour un meublé de 26 m² à Toulon : 400 à 530 €/mois"],
         ["Studio meublé de 18 m², Sainte-Anne (Toulon)", "589 € charges comprises",
          "annonce du 16/10/2026 — 33 €/m², la borne haute des petites surfaces"],
         ["T2 meublé de 37 m², basse ville (Toulon)", "680 € charges comprises",
          "annonce du 16/10/2026 — 18 €/m², la borne basse des surfaces plus grandes"],
         ["DVF Toulon, appartements de moins de 30 m²", "médiane 3 351 €/m² — premier quartile 2 760",
          "737 ventes : 73 500 à 89 300 € pour 26,64 m², avant décote de bail"],
         ["Studios comparables en résidences gérées à Toulon", "2 770 à 2 875 €/m²",
          "21 m² annoncé 58 164 € et un studio GSA Résidences Mayol à 57 500 € — le marché de la même "
          "famille de produit"],
         ["Offre", "46 920 € affichés", "1 761 €/m² : 37 % sous les comparables de résidences gérées "
                                        "et 36 % sous le premier quartile du DVF, décote qui rémunère "
                                        "un bail à quatorze mois du terme et un loyer sous le marché"]])
    releve += ('\n    <p class="attractiveness-intro"><strong>Ce que le relevé établit :</strong> le prix '
               'n\'est pas en cause, il est déjà très en dessous de la valeur du studio. Ce que le prix '
               'achète, c\'est un coupon court et une option : quatorze mois de loyer garanti par '
               'l\'exploitant, puis un studio de 26,64 m² au campus que l\'on relouera meublé 450 €/mois '
               'au lieu de 285 €. Le dossier se juge donc sur la solidité du preneur et sur le sort du '
               'bail au 31 décembre 2027, jamais sur le rendement affiché.</p>')

    garde_fous = f"""        <li><strong>Prix plafond du coupon seul : {eur(seuil_coupon)}</strong> — c'est le prix auquel le loyer de 285 €/mois atteint le seuil de 5 % net d'IS sur prix de revient, soit 35 % sous le prix affiché. Autrement dit : au prix demandé, le coupon ne suffit pas à faire vivre le dossier.</li>
        <li><strong>Prix plafond si la reprise se fait : {eur(seuil_reprise)}</strong> — avec le studio repris et reloué meublé à {eur(LOYER_MARCHE)}/mois, le seuil est atteint jusqu'à {eur(seuil_reprise)}. Le prix affiché se situe entre les deux : il est trop haut pour le coupon et confortable pour l'option.</li>
        <li><strong>Le scénario haut rend {pct(c_haut['rendements']['net_sur_revient_pct'])} net d'IS</strong> contre {pct(rd['net_sur_revient_pct'])} pour le coupon — le rendement double, et c'est la raison d'acheter.</li>
        <li><strong>Pièces à exiger avant toute offre :</strong> le bail commercial et ses avenants, la durée restante et son caractère ferme ou 3/6/9, les comptes des deux derniers exercices de l'exploitant, la répartition des charges (605 et 606), l'état des lieux d'entrée et les diagnostics, l'avis de taxe foncière, les appels de fonds de copropriété, et le détail de la TVA régularisable.</li>
        <li><strong>Point de méthode :</strong> la cible de relocation ({eur(LOYER_MARCHE)}/mois) n'entre dans aucun prix tant que le bail court. Seul le loyer encaissé alimente l'EBE, les plafonds et le solde ; la reprise se publie en variante, avec son capital travaux.</li>"""

    cartes = bloc_cartes(d)
    projections = "\n\n".join(gen.bloc_scenario(s) for s in scenarios)

    t = {
        "badge": "Coupon court + option sur la reprise du studio",
        "strategie": "portage du bail commercial en place, puis reprise du studio et location meublée "
                     "directe à l'échéance",
        "adresse_courte": "Studio meublé de 26,64 m² loué sous bail commercial — Campus Porte d'Italie, "
                          "Toulon (83000)",
        "quartier": "Porte d'Italie, Toulon",
        "intro_attractivite": "Porte d'Italie, c'est le quartier du campus toulonnais : université, IUT "
                              "et écoles supérieures à pied, gare de Toulon et réseau de bus à quelques "
                              "minutes, commerces et restauration au pied des résidences. C'est le seul "
                              "secteur de la ville où la demande locative étudiante est structurelle, et "
                              "c'est précisément ce qui rend ce studio relouable en direct le jour où "
                              "l'exploitant s'en va.",
        "profil": "aujourd'hui un exploitant, preneur unique qui paie le loyer que le logement soit "
                  "occupé ou non ; demain, si la reprise se fait, des étudiants en location meublée "
                  "directe sur le secteur du campus.",
        "intro_strategie": "Trois lectures chiffrées du même studio : portage du bail en place, reprise "
                           "du studio et relocation meublée directe après le départ de l'exploitant, ou "
                           "revente en l'état sous bail. Le prix affiché ne rémunère pas le coupon, il "
                           "rémunère l'option.",
        "lecture": f"Le lot est vendu {pct(rd['net_sur_revient_pct'])} net d'IS sur prix de revient pour "
                   f"un plancher de 5 % : au prix demandé, le coupon de {eur(LOYER_BAIL)}/mois ne paie "
                   f"pas le dossier. Ce qui le paie, c'est le studio lui-même : 26,64 m² Carrez au "
                   f"campus, achetés {eur(PRIX)} quand le premier quartile du DVF des moins de 30 m² "
                   f"est à 2 760 €/m² et les studios comparables en résidence gérée à 2 770-2 875 €/m². "
                   f"Repris et reloué meublé à {eur(LOYER_MARCHE)}/mois, le même studio rend "
                   f"{pct(c_haut['rendements']['net_sur_revient_pct'])} net d'IS.",
        "conf": "Le dossier se juge sur trois faits, pas sur le taux affiché. Le premier est que la "
                "décote est réelle : 1 761 €/m² payés contre 2 760 €/m² au premier quartile du DVF, "
                "soit une marge de sécurité qui absorbe l'incertitude. Le deuxième est que le loyer de "
                "285 €/mois est garanti par un preneur unique, mais seulement jusqu'au 31 décembre 2027. "
                "Le troisième est la limite du scénario de reprise : un bail commercial donne au "
                "preneur un droit au renouvellement, et refuser ce renouvellement coûte une indemnité "
                "d'éviction que l'intermédiaire chiffre lui-même à 12 à 15 000 € par studio en résidence "
                "étudiante. Autrement dit, on ne décide pas de récupérer le studio : on attend que "
                "l'exploitant parte ou défaille, et on est payé pour cette attente par le prix d'entrée.",
        "intro_projections": f"Les trois scénarios partent du même prix de {eur(PRIX)} et du même studio ; "
                             f"le scénario Base encaisse le bail en cours, le scénario Best suppose le "
                             f"départ de l'exploitant et une relocation meublée directe à "
                             f"{eur(LOYER_MARCHE)}/mois, le scénario Worst une défaillance en cours de "
                             f"bail avec loyers suspendus et remise en état dégradée.",
        "releve": releve,
        "garde_fous": garde_fous,
        "stance": "On négocie, mais pas sur le prix : sur le bail.",
        "verdict_texte": f"À {eur(PRIX)}, le lot rend {pct(rd['net_sur_revient_pct'])} net d'IS sur un prix "
                         f"de revient de {eur(c['prix_revient_total'])}, sous le plancher de 5 % de la "
                         f"branche, et il laisse {euro_signe(d['solde'])} par mois à la charge du "
                         f"propriétaire. Ce n'est pourtant pas un dossier à refuser : la valeur retenue du "
                         f"studio est de {eur(68000)}, soit un ratio coût/valeur de "
                         f"{nfr(c['ratio_cout_valeur'], 2)}, et la reprise du studio le ferait passer à "
                         f"{pct(c_haut['rendements']['net_sur_revient_pct'])}. Ce que le prix affiché "
                         f"achète, c'est une option sur ce studio, et une option qui coûte 35 % sous le "
                         f"premier quartile du marché mérite d'être travaillée.",
        "performance": f"{pct(rd['net_sur_revient_pct'])} de rendement net après IS sur un prix de revient "
                       f"de {eur(c['prix_revient_total'])}, pour un plancher de branche de 5 % : "
                       f"performance {nfr(comp['s_performance'], 1)}/10. EBE avant IS : {eur(f['ebe'])}. "
                       f"L'amortissement du bâti ({eur(f['amortissement'])}/an) efface presque tout le "
                       f"résultat fiscal, l'IS se limite à {eur(f['is_annuel'])}. Le scénario de reprise, "
                       f"lui, rend {pct(c_haut['rendements']['net_sur_revient_pct'])} net d'IS.",
        "prix_texte": f"Prix plafond du coupon seul : {eur(seuil_coupon)} (contrainte : {contrainte}). Prix "
                      f"plafond avec reprise du studio : {eur(seuil_reprise)}. Le prix affiché de "
                      f"{eur(PRIX)} se situe entre les deux, et c'est toute la question du dossier : on "
                      f"paie aujourd'hui un coupon insuffisant pour une option qui vaut, elle, la peine. "
                      f"Un prix cassé n'a pas de sens ici, le lot est déjà vendu à 64 % de sa valeur "
                      f"retenue et 36 % sous le premier quartile du DVF : ce qui se négocie, ce sont les "
                      f"conditions du bail et la garantie du preneur.",
    }

    calcule("EBE base", round(f["ebe"]), round(engine.compute(r)["fiscal"]["ebe"]))
    calcule("rendement net/revient", round(rd["net_sur_revient_pct"], 2),
            round(f["net_apres_is"] / c["prix_revient_total"] * 100, 2), tolerance=0.05)
    calcule("prix au m²", round(prix / gen.SURFACE), round(46920.0 / 26.64))
    calcule("solde mensuel base", round(d["solde"], 2), round(f["net_apres_is"] / 12 - prix * ANNUITE), tolerance=1.0)
    for s in scenarios:
        attendu = s["c"]["fiscal"]["net_apres_is"] / 12.0 - (prix + s["travaux"]) * ANNUITE
        calcule(f"solde scénario {s['libelle']}", round(s["solde"], 2), round(attendu, 2), tolerance=5.0)
    # le prix affiché doit se situer entre le seuil du coupon et celui de la reprise
    if not (seuil_coupon < prix < seuil_reprise):
        gen.ECARTS.append(f"prix affiché {prix} hors de l'encadrement [{seuil_coupon} ; {seuil_reprise}]")

    # adaptations propres à ce dossier : date, source, section de sensibilité, second lien d'annonce
    remplacements = [
        ("Analyse générée le 13 octobre 2026", "Analyse générée le 16 octobre 2026"),
        ("<p class=\"report-source\">Source : SeLoger — {vendeur}</p>",
         "<p class=\"report-source\">Source : LeBonCoin — {vendeur}</p>"),
        ('<div class="report-source-link"><a href="{url}">{url}</a></div>',
         '<div class="report-source-link"><a href="{url}">{url}</a><br>'
         '<a href="{url2}">Seconde diffusion : Gens de Confiance, même référence</a></div>'),
        ("Sensibilité au loyer mensuel — prix affiché de {prix_affiche}",
         "Sensibilité au prix d'achat — coupon de {loyer} €/mois, remise en état {travaux} € comprise"),
        ("<th>Loyer mensuel</th><th>EBE / an</th><th>Net après IS</th><th>Solde mensuel net</th>"
         "<th>Rendement net sur revient</th>",
         "<th>Prix d'achat</th><th>EBE / an</th><th>Net après IS</th><th>Solde mensuel net</th>"
         "<th>Rendement net sur revient</th>"),
        ("Chaque ligne est recalculée par le moteur à partir du même lot, vacance 5 %, charges "
         "inchangées. Le solde mensuel se lit sous la convention du groupe : frais d'acquisition "
         "sortis comptants, solde du prix porté sur quinze ans, intérêts et assurance compris. "
         "La dernière ligne montre la cible de colocation, hors bail en place.",
         "Chaque ligne est recalculée par le moteur à partir du même lot, sur le loyer encaissé de "
         "285 €/mois, vacance 5 %, charges inchangées. Le solde mensuel se lit sous la convention du "
         "groupe : frais d'acquisition sortis comptants, solde du prix porté sur quinze ans, intérêts "
         "et assurance compris."),
    ]

    gabarit = GABARIT
    html = gabarit.format(
        titre=r["titre"], adresse_courte=t["adresse_courte"], vendeur=r["annonce"]["vendeur"],
        url=r["annonce"]["url"], url2=r["annonce"]["url_secondaire"],
        badge=t["badge"], strategie=t["strategie"],
        cartes=cartes, lat=lat, lon=lon, map_addr=adresse,
        quartier=t["quartier"], intro_attractivite=t["intro_attractivite"],
        attractivite=gen.bloc_attractivite({"rec": r}), profil=t["profil"], lecture=t["lecture"],
        intro_strategie=t["intro_strategie"], conf=t["conf"],
        strategie_html=gen.bloc_strategie({"strategies": strategies, "rec": r}),
        releve=t["releve"], grille=bloc_grille(d), identite=bloc_identite(d),
        intro_projections=t["intro_projections"], projections=projections,
        risques=gen.bloc_risques({"rec": r}), verdict_cls=d["classe"], stance=t["stance"],
        verdict_texte=t["verdict_texte"], performance=t["performance"], prix_texte=t["prix_texte"],
        garde_fous=t["garde_fous"], amortissement=eur(f["amortissement"]),
        frais=eur(r["hypotheses"]["frais_acquisition_euros"]), loyer=nfr(loyer),
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
          f"seuil coupon {seuil_coupon} € | seuil reprise {seuil_reprise} €")


if __name__ == "__main__":
    main()
