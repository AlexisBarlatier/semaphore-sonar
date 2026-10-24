#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère la fiche du T3 de 68 m², centre-ville de Brignoles (83170).

analyses/2026-10-24-t3-brignoles-centre-68m2/index.html — SeLoger 26GCCUFIK3PP
(Elios Group, Cassilde Mattei, réf. 1372-ELIOSGROUP1).
Prix cible = solde nul, jamais le prix d'une note.
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
gen.SLUG = "2026-10-24-t3-brignoles-centre-68m2"
gen.SURFACE = 68.28
ANNUITE = 0.9 * (0.038 / 12) / (1 - (1 + 0.038 / 12) ** -240) + 0.9 * 0.0034 / 12
eur, nfr, pct, euro_signe = gen.eur, gen.nfr, gen.pct, gen.euro_signe
calcule = gen.calcule
releve_html = gen.releve_html

PRIX = 91000.0
TRAVAUX = 20000.0
VALEUR = 120000.0
LOYER = 750.0
TF = 700.0

GABARIT = gen.TEMPLATE
for _avant, _apres in [
    ("Analyse générée le 13 octobre 2026", "Analyse générée le 24 octobre 2026"),
    ("Sensibilité au loyer mensuel — prix affiché de {prix_affiche}",
     "Sensibilité au prix d'achat — loyer de marché {loyer} €/mois, travaux {travaux} compris"),
    ("<th>Loyer mensuel</th><th>EBE / an</th><th>Net après IS</th><th>Solde mensuel net</th>"
     "<th>Rendement net sur revient</th>",
     "<th>Prix d'achat</th><th>EBE / an</th><th>Net après IS</th><th>Solde mensuel net</th>"
     "<th>Rendement net sur revient</th>"),
    ("La dernière ligne montre la cible de colocation, hors bail en place.",
     "La ligne en surbrillance est le prix affiché."),
    ("solde du prix porté sur quinze ans", "solde du prix porté sur vingt ans"),
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
        rr["hypotheses"]["frais_acquisition_euros"] = round(prix * 0.08)
    return rr


def prix_cf_nul(lo=30000.0, hi=150000.0):
    def solde(p):
        cc = engine.compute(variante(rec(), prix=p))
        return cc["fiscal"]["net_apres_is"] / 12.0 - (p + TRAVAUX) * ANNUITE

    for _ in range(90):
        mid = (lo + hi) / 2
        if solde(mid) > 0:
            lo = mid
        else:
            hi = mid
    return round(lo / 500.0) * 500.0


def bloc_cartes(d):
    cartes = [
        ("Prix affiché", eur(d["prix"]) + f" ({eur(d['prix'] / gen.SURFACE)}/m²)"),
        ("Prix de revient", eur(d["revient"]) + f" travaux {eur(TRAVAUX)} compris"),
        ("Valeur retenue après travaux", eur(VALEUR)),
        ("Loyer de marché", eur(LOYER) + "/mois — bien libre, aucun bail"),
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
        ("Occupation", "Bien libre, aucun bail. Aucun loyer n'est encaissé aujourd'hui : les "
                       "750 €/mois sont une cible post-travaux"),
        ("Loyer retenu", f"{eur(LOYER)}/mois — médiane DHUP 2025 de Brignoles 13,1 €/m² (T3 de "
                         f"65 m² à 759 €), annonces actives de 630 € (T3 de 66 m² rue Petit "
                         f"Paradis) à 794 € CC (T3 de 68,65 m² boulevard Joseph Monnier, avec "
                         f"parking). Retenu sous les deux T3 avec ascenseur et parking, que ce lot "
                         f"n'a pas"),
        ("Charges de copropriété", eur(b["copro"]["charges_annuelles_euros"]) + "/an — "
         + b["copro"]["charges_source"]),
        ("Taxe foncière", eur(h["taxe_fonciere_annuelle_euros"]) + "/an — "
         + h["taxe_fonciere_commentaire"]),
        ("Entretien et gestion", eur(h["entretien_annuel_euros"]) + "/an — "
         + h["entretien_commentaire"]),
        ("Frais d'acquisition", eur(d["rec"]["hypotheses"]["frais_acquisition_euros"]) + " — "
         + d["rec"]["hypotheses"]["frais_acquisition_commentaire"]),
        ("Travaux", eur(TRAVAUX) + " — " + b["travaux"]["nature"]),
        ("Amortissement", eur(d["f"]["amortissement"]) + "/an — 90 % du prix de revient sur 30 ans"),
        ("DPE / GES", "C / A — double vitrage partout, chauffage individuel électrique. Aucune "
                      "échéance d'interdiction : le risque du dossier n'est pas énergétique"),
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


def bloc_strategie(d):
    lignes = []
    for st in d["strategies"]:
        ratio = st["ratio"]
        ratio_cls = "ratio-bon" if ratio < 0.95 else ("ratio-ok" if ratio <= 1.05 else "ratio-mauvais")
        badge = {"modéré": ("risque-modere", "Modéré"), "élevé": ("risque-eleve", "Élevé"),
                 "faible": ("risque-faible", "Faible")}.get(st["risque"], ("risque-modere", "Modéré"))
        fais = "faisabilite-haute" if "Immédiate" in st["faisabilite"] else "faisabilite-faible"
        sel = ' class="strategy-row selected"' if st["retenue"] else ' class="strategy-row"'
        rdt = "—" if st["rdt"] is None else pct(st["rdt"])
        lignes.append(
            f"        <tr{sel}>\n          <td>{st['strategie']}</td>\n          <td>{st['lots']}</td>\n"
            f"          <td>{rdt} ({st['loyer_label']})</td>\n"
            f"          <td>{eur(st['valeur'])}</td>\n"
            f"          <td><span class=\"ratio-badge {ratio_cls}\">{nfr(ratio, 3)}</span></td>\n"
            f"          <td><span class=\"badge-faisabilite {fais}\">{st['faisabilite']}</span></td>\n"
            f"          <td><span class=\"badge-risque {badge[0]}\">{badge[1]}</span></td>\n"
            f"          <td>{st['net_label']}</td>\n"
            "        </tr>")
    return ("    <table class=\"strategy-table\">\n      <thead>\n        <tr>\n"
            "          <th>Stratégie</th>\n          <th>Lots</th>\n          <th>Rendement net d'IS (revient)</th>\n"
            "          <th>Valeur revente</th>\n          <th>Ratio coût/valeur</th>\n          <th>Faisabilité</th>\n"
            "          <th>Risque</th>\n          <th>Résultat annuel</th>\n        </tr>\n      </thead>\n      <tbody>\n"
            + "\n".join(lignes) + "\n      </tbody>\n    </table>")


def main():
    r = rec()
    c = engine.compute(r)
    note, verdict, comp = scoring.note_et_verdict(r, c)
    f, rd = c["fiscal"], c["rendements"]
    prix = r["annonce"]["prix_retenu_euros"]
    plafond, contrainte = scoring.prix_plafond(r)
    cible = prix_cf_nul()

    c_12k = engine.compute(variante(r, travaux=12000.0))
    c_35k = engine.compute(variante(r, travaux=35000.0))
    c_650 = engine.compute(variante(r, loyer=650.0))

    scenarios = []
    for sc in (
        {"libelle": "Scénario Base", "classe": "scenario-base", "loyer": LOYER, "vacance": 5.0,
         "travaux": TRAVAUX,
         "sous_titre": f"Loyer {eur(LOYER)} — vacance 5 % — travaux {eur(TRAVAUX)} — prix affiché "
                       f"{eur(prix)}"},
        {"libelle": "Scénario Best", "classe": "scenario-best", "loyer": 800.0, "vacance": 3.0,
         "travaux": 12000.0,
         "sous_titre": "Loyer 800 € — vacance 3 % — travaux contenus à 12 000 €, devis favorable"},
        {"libelle": "Scénario Worst", "classe": "scenario-worst", "loyer": 650.0, "vacance": 12.0,
         "travaux": 35000.0,
         "sous_titre": "Loyer 650 € — vacance 12 % — travaux à 35 000 € si la cuisine, la salle de "
                       "bain et l'électricité sont à refaire"},
    ):
        rr = variante(r, loyer=sc["loyer"], vacance=sc["vacance"], travaux=sc["travaux"])
        cc = engine.compute(rr)
        assiette = prix + sc["travaux"]
        scenarios.append({"libelle": sc["libelle"], "classe": sc["classe"], "sous_titre": sc["sous_titre"],
                          "loyer": sc["loyer"], "vacance": sc["vacance"], "travaux": sc["travaux"],
                          "rec": rr, "c": cc,
                          "solde": cc["fiscal"]["net_apres_is"] / 12.0 - assiette * ANNUITE})

    grille = []
    for p in (PRIX, float(plafond), 85000.0, 80000.0, float(cible)):
        rr = variante(r, prix=p)
        cc = engine.compute(rr)
        grille.append({"prix": p, "ebe": cc["fiscal"]["ebe"], "net": cc["fiscal"]["net_apres_is"],
                       "solde": cc["fiscal"]["net_apres_is"] / 12.0 - (p + TRAVAUX) * ANNUITE,
                       "rdt": cc["rendements"]["net_sur_revient_pct"]})

    strategies = [
        {"strategie": "Rénovation puis location nue du T3", "lots": 1,
         "rdt": rd["net_sur_revient_pct"], "loyer_label": "750 €/mois",
         "ratio": c["ratio_cout_valeur"], "valeur": VALEUR,
         "net_label": eur(f["net_apres_is"]) + "/an",
         "faisabilite": "Immédiate : bien libre, aucun bail à attendre", "risque": "modéré",
         "retenue": True},
        {"strategie": "Achat, rénovation et revente", "lots": 1, "rdt": None,
         "loyer_label": "opération de revente",
         "ratio": c["prix_revient_total"] / VALEUR, "valeur": VALEUR,
         "net_label": euro_signe(VALEUR - c["prix_revient_total"]) + " de marge brute",
         "faisabilite": "Structure commerciale, portage 12 à 18 mois", "risque": "élevé",
         "retenue": False},
        {"strategie": "Location sans travaux", "lots": 1, "rdt": c_650["rendements"]["net_sur_revient_pct"],
         "loyer_label": "650 €/mois",
         "ratio": c_650["ratio_cout_valeur"], "valeur": 95000.0,
         "net_label": eur(c_650["fiscal"]["net_apres_is"]) + "/an",
         "faisabilite": "Immédiate mais relocation difficile", "risque": "élevé",
         "retenue": False},
    ]

    adresse = "Rue commerçante du centre-ville, Brignoles (83170) — adresse exacte non communiquée"
    lat, lon = "43.4058", "6.0615"

    d = {"slug": gen.SLUG, "adresse": adresse, "rec": r, "c": c, "note": note, "verdict": verdict,
         "comp": comp, "f": f, "rd": rd, "prix": prix, "loyer": LOYER,
         "revient": c["prix_revient_total"], "solde": f["net_apres_is"] / 12.0 - (prix + TRAVAUX) * ANNUITE,
         "classe": {"acheter": "buy", "negocier": "nego", "fuir": "pass"}[verdict],
         "classe_note": scoring.classe_note(note), "plafond": plafond, "contrainte": contrainte,
         "cible": cible, "scenarios": scenarios, "grille": grille, "strategies": strategies}

    releve = releve_html(
        ["Source", "Chiffre", "Lecture"],
        [["DVF Brignoles, appartements 45-80 m²", "13 ventes 2021-2025 — médiane 1 868 €/m², "
          "premier quartile 1 287, troisième 2 173, prix médian 93 000 €",
          "sur 68,28 m² : 88 000 € au premier quartile, 148 000 au troisième. Échantillon mince"],
         ["DVF Brignoles, appartements 60-75 m²", "9 ventes — médiane 1 409 €/m²",
          "la tranche exacte du bien : le prix affiché à 1 333 €/m² est au niveau du marché, "
          "pas en dessous"],
         ["DVF Brignoles, évolution 2021-2025", "1 550 à 2 000 €/m² de médiane annuelle",
          "prix stables, volumes faibles : pas de plus-value à attendre"],
         ["Médiane DHUP 2025, Brignoles", "13,1 €/m² (IC 95 % 10,1 à 16,9) — T3 de 65 m² à 759 €",
          "le repère communal, cohérent avec les annonces du centre"],
         ["Location relevée — T3 de 66 m², rue Petit Paradis, centre-ville", "630 €/mois",
          "le bas de la fourchette, sur une surface plus petite et sans parking"],
         ["Location relevée — T3 de 69 m², résidence avec ascenseur et parking", "786 €/mois",
          "le haut de la fourchette, avec des prestations que ce lot n'a pas"],
         ["Location relevée — T3 de 68,65 m², Pôle Liberté, 90 bd Joseph Monnier", "794 € CC "
          "(666 € HC), parking compris", "la référence la plus proche en surface"],
         ["Loyer retenu", f"{eur(LOYER)}/mois", "entre le T3 sans parking à 630 € et les T3 avec "
          "ascenseur et parking à 786-794 €"],
         ["Rendement selon le devis de travaux", f"{pct(c_12k['rendements']['net_sur_revient_pct'])} "
          f"à 12 000 € — {pct(rd['net_sur_revient_pct'])} à 20 000 € — "
          f"{pct(c_35k['rendements']['net_sur_revient_pct'])} à 35 000 €",
          "tout le dossier est dans ce devis, et il n'y en a pas"]])

    garde_fous = f"""        <li><strong>Prix plafond : {eur(plafond)}</strong> (contrainte du moteur : {contrainte}), soit {pct((prix - plafond) / prix * 100)} sous l'affichage. Au-dessus, le dossier ne peut plus atteindre le plancher de 5 %.</li>
        <li><strong>Prix cible : {eur(cible)}</strong>, soit {pct((prix - cible) / prix * 100)} sous l'affichage — le prix auquel le solde mensuel tombe à zéro, travaux compris. Il est sous la valeur du bien en l'état : autrement dit, il n'existe pas.</li>
        <li><strong>Le solde au prix affiché : {euro_signe(d['solde'])} par mois.</strong> Le dossier est proche de l'équilibre, mais il ne l'atteint pas, et l'écart tient à un devis qu'on n'a pas.</li>
        <li><strong>Tout dépend du devis de travaux :</strong> à 12 000 €, le rendement net monte à {pct(c_12k['rendements']['net_sur_revient_pct'])} ; à 20 000 €, {pct(rd['net_sur_revient_pct'])} ; à 35 000 €, {pct(c_35k['rendements']['net_sur_revient_pct'])}. C'est la première pièce à demander, avant la visite.</li>
        <li><strong>Le prix n'est pas une décote :</strong> 1 333 €/m² sur la tranche DVF des 60-75 m² (médiane 1 409 €/m²) et au niveau du premier quartile des 45-80 m² (1 287 €/m²). Le marché paie les travaux, il n'offre pas de marge.</li>
        <li><strong>Pièces à exiger :</strong> devis ou estimation des travaux de réagencement, plans et Carrez, trois derniers PV d'AG et carnet d'entretien de la copropriété de 4 lots, avis de taxe foncière, diagnostics électricité et plomb, et l'état réel de la cuisine, de la salle de bain et des tableaux électriques.</li>
        <li><strong>Point de méthode :</strong> le bien est libre. Les 750 €/mois sont une cible de marché : aucun loyer ne court avant le chantier et la signature d'un bail.</li>"""

    projections = "\n\n".join(gen.bloc_scenario(s) for s in scenarios)

    t = {
        "badge": "Petit ticket, devis manquant",
        "strategie": "rénovation puis location nue du T3",
        "adresse_courte": "Appartement T3 de 68 m², centre-ville — Brignoles (83170)",
        "quartier": "Centre-ville, Brignoles",
        "intro_attractivite": "Brignoles est le pôle administratif et scolaire du centre Var, 18 000 "
                             "habitants, sur l'A8 à trente kilomètres de Toulon. Le bien est dans une "
                             "rue commerçante du cœur de ville, à pied des commerces, des médecins, "
                             "des écoles et de l'hôpital : c'est l'emplacement qui tient la demande "
                             "locative de bourg.",
        "profil": "un ménage salarié du bassin brignolais, un couple avec un enfant, ou du personnel "
                  "hospitalier. Le T3 de 68 m² en centre est le format standard de cette demande, et "
                  "c'est aussi celui de l'offre : trois T3 concurrents sont en location au même "
                  "moment entre 630 et 794 €.",
        "intro_strategie": "Trois lectures : rénover puis louer, acheter-rénover-revendre, ou louer "
                          "sans travaux. La troisième est la plus mauvaise ; la deuxième ne survit "
                          "pas aux frais de vente sur un ticket de 91 000 €. Reste la première, et "
                          "elle dépend d'un devis.",
        "lecture": f"Le dossier est propre et petit : 91 000 € pour 68 m² dans une rue commerçante, "
                   f"soit {eur(prix / gen.SURFACE)}/m², un DPE C, un double vitrage récent et des "
                   f"charges de copropriété de 117 €/an. Il rend {pct(rd['net_sur_revient_pct'])} net "
                   f"après IS une fois les travaux budgétés, pour un solde de "
                   f"{euro_signe(d['solde'])} par mois : à un devis près, il passe. Mais l'annonce "
                   f"dit « rénovation nécessaire » sans avancer un chiffre, et c'est ce chiffre qui "
                   f"décide de tout, de 4,42 % à 5,24 %.",
        "conf": "Ce qui plaide pour le bien : un emplacement de centre-bourg commerçant, un DPE C avec "
                "double vitrage et GES A — donc pas de chantier énergétique —, une copropriété de "
                "quatre lots sans procédure et des charges négligeables, et un ticket qui tient dans "
                "la poche (18 000 € à sortir, frais compris). Ce qui le retient : 1 333 €/m² n'est "
                "pas une décote sur la tranche de surface, aucun garage ni balcon, et surtout une "
                "rénovation annoncée sans devis sur un bien qui ne produit rien tant qu'elle n'est "
                "pas faite.",
        "intro_projections": f"Les trois scénarios partent du même prix de {eur(prix)} et du même "
                             f"loyer de marché, et ne diffèrent que par le devis et la vacance : "
                             f"c'est exactement le choix qui se pose aujourd'hui.",
        "releve": releve,
        "garde_fous": garde_fous,
        "stance": f"On ne peut pas offrir au-dessus de {eur(plafond)}, et à ce prix le solde reste "
                  f"{euro_signe(engine.compute(variante(r, prix=plafond))['fiscal']['net_apres_is'] / 12.0 - (plafond + TRAVAUX) * ANNUITE)} "
                  f"par mois. Le prix qui l'annule, {eur(cible)}, est sous la valeur du bien en "
                  f"l'état : il n'existe pas. Donc on demande le devis avant tout. S'il tombe à "
                  f"12 000 €, on offre {eur(plafond)} et le dossier se fait ; s'il monte à 35 000 €, "
                  f"on passe.",
        "verdict_texte": f"À {eur(prix)}, l'appartement rend {pct(rd['net_sur_revient_pct'])} net "
                         f"après IS pour {eur(c['prix_revient_total'])} de prix de revient travaux "
                         f"compris, juste sous le plancher de 5 %, avec un solde de "
                         f"{euro_signe(d['solde'])} par mois. Le prix plafond est de {eur(plafond)}, "
                         f"soit {pct((prix - plafond) / prix * 100)} sous l'affichage : l'écart est "
                         f"modeste, du niveau d'une négociation ordinaire. Le prix cible — solde nul "
                         f"— ressort à {eur(cible)} et n'a pas de sens face à la valeur du bien. "
                         f"Autrement dit : ce n'est pas le prix qui bloque, c'est le devis de travaux. "
                         f"Un dossier à instruire en une pièce.",
        "performance": f"{pct(rd['net_sur_revient_pct'])} de rendement net après IS sur un prix de "
                       f"revient de {eur(c['prix_revient_total'])} travaux compris, pour un plancher "
                       f"de 5 % : performance {nfr(comp['s_performance'], 1)}/10. EBE avant IS : "
                       f"{eur(f['ebe'])}, amortissement {eur(f['amortissement'])}, IS "
                       f"{eur(f['is_annuel'])}. Ratio prix de revient sur valeur : "
                       f"{nfr(c['ratio_cout_valeur'], 2)} — on achète au niveau de la valeur, pas "
                       f"en dessous.",
        "prix_texte": f"Prix plafond {eur(plafond)} et prix cible {eur(cible)}, soit "
                      f"{pct((prix - plafond) / prix * 100)} et {pct((prix - cible) / prix * 100)} sous "
                      f"l'affichage. Le plafond est un prix de rendement, la cible un prix de "
                      f"trésorerie : sur ce dossier les deux sont sous la valeur du bien, ce qui dit "
                      f"que le problème n'est pas le prix mais le devis.",
    }

    calcule("EBE base", round(f["ebe"]), round(engine.compute(r)["fiscal"]["ebe"]))
    calcule("rendement net/revient", round(rd["net_sur_revient_pct"], 2),
            round(f["net_apres_is"] / c["prix_revient_total"] * 100, 2), tolerance=0.05)
    calcule("prix au m²", round(prix / gen.SURFACE), round(91000.0 / 68.28))
    calcule("ratio coût/valeur", round(c["ratio_cout_valeur"], 3),
            round(c["prix_revient_total"] / VALEUR, 3), tolerance=0.01)
    for s in scenarios:
        attendu = s["c"]["fiscal"]["net_apres_is"] / 12.0 - (prix + s["travaux"]) * ANNUITE
        calcule(f"solde scénario {s['libelle']}", round(s["solde"], 2), round(attendu, 2), tolerance=5.0)

    html = GABARIT.format(
        titre=r["titre"], adresse_courte=t["adresse_courte"], vendeur=r["annonce"]["vendeur"],
        url=r["annonce"]["url"], badge=t["badge"], strategie=t["strategie"],
        cartes=bloc_cartes(d), lat=lat, lon=lon, map_addr=adresse,
        quartier=t["quartier"], intro_attractivite=t["intro_attractivite"],
        attractivite=gen.bloc_attractivite({"rec": r}), profil=t["profil"], lecture=t["lecture"],
        intro_strategie=t["intro_strategie"], conf=t["conf"],
        strategie_html=bloc_strategie({"strategies": strategies}),
        releve=t["releve"], grille=bloc_grille(d), identite=bloc_identite(d),
        intro_projections=t["intro_projections"], projections=projections,
        risques=gen.bloc_risques({"rec": r}), verdict_cls=d["classe"], stance=t["stance"],
        verdict_texte=t["verdict_texte"], performance=t["performance"], prix_texte=t["prix_texte"],
        garde_fous=t["garde_fous"], amortissement=eur(f["amortissement"]),
        frais=eur(r["hypotheses"]["frais_acquisition_euros"]), loyer=nfr(LOYER),
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
          f"plafond {plafond} € | cible {cible} €")


if __name__ == "__main__":
    main()
