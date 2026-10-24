#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère la fiche de l'immeuble 2 T2 + 2 remises — La Valette-du-Var (83160).

analyses/2026-10-24-immeuble-2t2-remises-la-valette/index.html — SeLoger 26V1QCQPE2DT
(AMV Immobilier / L'Agence du Moulin Vieux, réf. CD05082026).

Gabarit et contrôles repris du générateur de l'immeuble 4 T2 de Cuers.
Convention de solde : frais d'acquisition comptants, 90 % du prix porté sur vingt ans
à 3,80 %, assurance comprise.
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
gen.SLUG = "2026-10-24-immeuble-2t2-remises-la-valette"
gen.SURFACE = 127.0
ANNUITE = 0.9 * (0.038 / 12) / (1 - (1 + 0.038 / 12) ** -240) + 0.9 * 0.0034 / 12
eur, nfr, pct, euro_signe = gen.eur, gen.nfr, gen.pct, gen.euro_signe
calcule = gen.calcule
releve_html = gen.releve_html

PRIX = 265000.0
NET_VENDEUR = 250000.0
TRAVAUX = 0.0
VALEUR = 320000.0
LOYER_T2 = 800.0
LOYER_REMISE = 60.0
LOYER_TOTAL = 2 * LOYER_T2 + 2 * LOYER_REMISE
TF = 1800.0
ENTRETIEN = 2357.0

GABARIT = gen.TEMPLATE
for _avant, _apres in [
    ("Analyse générée le 13 octobre 2026", "Analyse générée le 24 octobre 2026"),
    ("Sensibilité au loyer mensuel — prix affiché de {prix_affiche}",
     "Sensibilité au prix d'achat — loyers estimés {loyer} €/mois par T2, remises 60 €"),
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
        rr["hypotheses"]["frais_acquisition_euros"] = round((prix - 15000.0) * 0.08)
    return rr


def bloc_cartes(d):
    cartes = [
        ("Prix affiché", eur(d["prix"]) + f" ({eur(d['prix'] / gen.SURFACE)}/m² annoncés)"),
        ("Prix de revient", eur(d["revient"])),
        ("Valeur retenue (décote de bloc)", eur(VALEUR)),
        ("Loyers retenus", eur(LOYER_TOTAL) + "/mois estimés — aucun loyer annoncé"),
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
        ("Occupation", "Deux appartements T2 loués nus à l'étage, deux remises en rez-de-chaussée, "
                       "une cave. Aucun loyer, aucune date de bail, aucune quittance au dossier : "
                       "l'annonce parle d'un « rapport locatif correct » sans avancer un chiffre"),
        ("Loyers retenus", f"{eur(LOYER_T2)}/mois par T2 et {eur(LOYER_REMISE)}/mois par remise, soit "
                           f"{eur(LOYER_TOTAL)} — ESTIMÉS au marché du 24/10/2026 (médiane DHUP 2025 "
                           f"15,5 €/m² ; annonces de 55 à 61 m² entre 770 et 1 000 €), à confirmer "
                           f"avec les deux baux"),
        ("Charges de copropriété", "Aucune — immeuble en monopropriété, pas de syndic, pas de "
                                   "mutualisation possible des travaux"),
        ("Taxe foncière", eur(h["taxe_fonciere_annuelle_euros"]) + "/an — "
         + h["taxe_fonciere_commentaire"]),
        ("Entretien et gestion", eur(h["entretien_annuel_euros"]) + "/an — "
         + h["entretien_commentaire"]),
        ("Frais d'acquisition", eur(d["rec"]["hypotheses"]["frais_acquisition_euros"]) + " — "
         + d["rec"]["hypotheses"]["frais_acquisition_commentaire"]),
        ("Amortissement", eur(d["f"]["amortissement"]) + "/an — 90 % du prix de revient sur 30 ans"),
        ("DPE / GES", "E / B — facture énergétique estimée entre 653 et 883 €/an. Aucune échéance "
                      "d'interdiction de louer avant 2034, mais un bâti mal isolé dont l'année de "
                      "construction n'est même pas donnée"),
        ("Annexes", "Deux remises en rez-de-chaussée et une cave. Surface des remises non donnée : "
                    "ni leur location, ni leur transformation en studios ne peut être chiffrée "
                    "avant mesurage"),
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
    cible = scoring.prix_cible(r)

    c_meuble = engine.compute(variante(r, loyer=950.0, entretien=ENTRETIEN + 900.0))
    c_studios = engine.compute(variante(r, loyer2=1110.0, travaux=45000.0))
    c_900 = engine.compute(variante(r, loyer=900.0))
    c_650 = engine.compute(variante(r, loyer=650.0))

    scenarios = []
    for sc in (
        {"libelle": "Scénario Base", "classe": "scenario-base", "loyer": LOYER_T2, "loyer2": LOYER_REMISE,
         "vacance": 5.0, "travaux": TRAVAUX,
         "sous_titre": f"Loyers estimés {eur(LOYER_T2)} par T2 et {eur(LOYER_REMISE)} par remise — "
                       f"vacance 5 % — prix affiché {eur(prix)} — aucun travaux"},
        {"libelle": "Scénario Best", "classe": "scenario-best", "loyer": 870.0, "loyer2": 60.0,
         "vacance": 2.0, "travaux": TRAVAUX,
         "sous_titre": "Loyers portés à 870 € par T2 — vacance 2 % — les baux en place sont au "
                       "niveau du marché haut"},
        {"libelle": "Scénario Worst", "classe": "scenario-worst", "loyer": 690.0, "loyer2": 50.0,
         "vacance": 12.0, "travaux": 5000.0,
         "sous_titre": "Baux en place 14 % sous le marché — vacance 12 % (un T2 vide un mois et "
                       "demi) — 5 000 € de travaux imprévus sur un bâti sans devis"},
    ):
        rr = variante(r, loyer=sc["loyer"], loyer2=sc["loyer2"], vacance=sc["vacance"],
                      travaux=sc["travaux"])
        cc = engine.compute(rr)
        assiette = prix + sc["travaux"]
        scenarios.append({"libelle": sc["libelle"], "classe": sc["classe"], "sous_titre": sc["sous_titre"],
                          "loyer": sc["loyer"] * 2 + sc["loyer2"] * 2, "vacance": sc["vacance"],
                          "travaux": sc["travaux"], "rec": rr, "c": cc,
                          "solde": cc["fiscal"]["net_apres_is"] / 12.0 - assiette * ANNUITE})

    grille = []
    for p in (PRIX, 255000.0, 240000.0, float(cible), 200000.0):
        rr = variante(r, prix=p)
        cc = engine.compute(rr)
        grille.append({"prix": p, "ebe": cc["fiscal"]["ebe"], "net": cc["fiscal"]["net_apres_is"],
                       "solde": cc["fiscal"]["net_apres_is"] / 12.0 - (p + TRAVAUX) * ANNUITE,
                       "rdt": cc["rendements"]["net_sur_revient_pct"]})

    strategies = [
        {"strategie": "Conservation en bloc : deux T2 loués nus, remises louées séparément", "lots": 4,
         "rdt": rd["net_sur_revient_pct"], "loyer_label": "loyers estimés",
         "ratio": c["ratio_cout_valeur"], "valeur": VALEUR,
         "net_label": eur(f["net_apres_is"]) + "/an",
         "faisabilite": "Immédiate : deux baux en place, remises louées à part",
         "risque": "modéré", "retenue": True},
        {"strategie": "Relocation des deux T2 en meublé", "lots": 2,
         "rdt": c_meuble["rendements"]["net_sur_revient_pct"], "loyer_label": "950 € par T2",
         "ratio": c_meuble["ratio_cout_valeur"], "valeur": VALEUR,
         "net_label": eur(c_meuble["fiscal"]["net_apres_is"]) + "/an",
         "faisabilite": "Mobilier des deux lots, 8 000 € à engager", "risque": "modéré",
         "retenue": False},
        {"strategie": "Transformation des deux remises en studios", "lots": 4,
         "rdt": c_studios["rendements"]["net_sur_revient_pct"], "loyer_label": "2 x 555 € + T2",
         "ratio": c_studios["ratio_cout_valeur"], "valeur": 380000.0,
         "net_label": eur(c_studios["fiscal"]["net_apres_is"]) + "/an",
         "faisabilite": "Déclaration préalable, PLU, 9 m² et 20 m³ minimum", "risque": "élevé",
         "retenue": False},
    ]

    adresse = "Cœur historique du village, La Valette-du-Var (83160) — adresse exacte non communiquée"
    lat, lon = "43.1375", "5.9830"

    d = {"slug": gen.SLUG, "adresse": adresse, "rec": r, "c": c, "note": note, "verdict": verdict,
         "comp": comp, "f": f, "rd": rd, "prix": prix, "loyer": LOYER_TOTAL,
         "revient": c["prix_revient_total"], "solde": f["net_apres_is"] / 12.0 - (prix + TRAVAUX) * ANNUITE,
         "classe": {"acheter": "buy", "negocier": "nego", "fuir": "pass"}[verdict],
         "classe_note": scoring.classe_note(note), "plafond": plafond, "contrainte": contrainte,
         "cible": cible, "scenarios": scenarios, "grille": grille, "strategies": strategies}

    solde_plafond = (engine.compute(variante(r, prix=plafond))["fiscal"]["net_apres_is"] / 12.0
                     - (plafond + TRAVAUX) * ANNUITE)

    releve = releve_html(
        ["Source", "Chiffre", "Lecture"],
        [["DVF La Valette-du-Var (83144), appartements 40-70 m²", "742 ventes 2021-2025 — médiane "
          "2 888 €/m², premier quartile 2 477, troisième quartile 3 835, prix médian 175 000 €",
          "deux T2 de 60 m² valent 346 560 € à la médiane : c'est la base de la valeur, avant "
          "décote de bloc"],
         ["DVF La Valette-du-Var, appartements 70-110 m²", "527 ventes — médiane 2 499 €/m²",
          "la grande surface décote de 13 % : les deux T2 se situent dans la tranche la plus chère "
          "au mètre carré"],
         ["DVF La Valette-du-Var, immeubles vendus en bloc", "154 m² à 2 922 €/m² et 156 m² à "
          "2 949 €/m² (décembre 2025)", "un immeuble de ce format se traite autour de 3 000 €/m² "
          "sur la surface réelle, soit 15 à 20 % sous la somme de ses lots"],
         ["Médiane DHUP 2025, La Valette-du-Var", "15,5 €/m² (IC 95 % 12,15 à 19,77) — T3 de 65 m² "
          "à 898 €/mois", "le repère communal ; un T2 de 60 m² au loyer médian vaudrait 930 €"],
         ["Annonce relevée — 57 m², La Valette-du-Var, octobre 2026", "894 €/mois",
          "l'annonce active la plus proche du produit par la surface"],
         ["Annonces relevées — 55, 61, 48 et 46 m²", "770 €, 1 000 €, 915 € et 695 €/mois",
          "la fourchette réelle du marché sur les T2 de la commune : 695 à 1 000 €"],
         ["Loyer retenu pour chaque T2", eur(LOYER_T2) + "/mois",
          "soit 12,7 à 14,5 €/m² selon que le lot fait 55 ou 63 m² : sous la médiane, pour un "
          "classement E sans extérieur et un état non documenté"],
         ["Loyer retenu pour les remises", eur(LOYER_REMISE) + "/mois chacune",
          "poste estimé, surface inconnue : ordre de grandeur d'un local de stockage en centre ancien"],
         ["Rendement du dossier selon les baux",
          f"{pct(c_650['rendements']['net_sur_revient_pct'])} à 650 € — "
          f"{pct(rd['net_sur_revient_pct'])} à 800 € — "
          f"{pct(c_900['rendements']['net_sur_revient_pct'])} à 900 €",
          "l'écart entre les deux hypothèses vaut plus de 60 000 € de prix : c'est le seul chiffre "
          "qui compte, et il n'est pas dans l'annonce"]])

    garde_fous = f"""        <li><strong>Prix plafond : {eur(plafond)}</strong> (contrainte du moteur : {contrainte}), soit {pct((prix - plafond) / prix * 100)} sous le prix affiché. La négociation nécessaire pour atteindre le plancher de 5 % est de {eur(prix - plafond)} : c'est l'ordre de grandeur d'une discussion ordinaire, pas d'une décote hors marché.</li>
        <li><strong>Prix cible : {eur(cible)}</strong>, soit {pct((prix - cible) / prix * 100)} sous l'affichage — le prix auquel la note franchit 6,5 et le solde se rapproche de zéro.</li>
        <li><strong>Le solde au prix affiché : {euro_signe(d['solde'])} par mois</strong>, avec des loyers estimés au marché. Sans les baux, ce chiffre peut varier de {euro_signe(c_650['fiscal']['net_apres_is'] / 12.0 - prix * ANNUITE)} à {euro_signe(c_900['fiscal']['net_apres_is'] / 12.0 - prix * ANNUITE)}.</li>
        <li><strong>Le prix au mètre carré est bas, et c'est l'argument du dossier :</strong> {eur(prix / gen.SURFACE)}/m² annoncés contre 2 888 €/m² de médiane DVF sur les appartements de 40 à 70 m². Ratio coût sur valeur : {nfr(c['ratio_cout_valeur'], 2)}. On achète 11 % sous la valeur de la somme des lots, ce qui laisse une vraie sortie par revente à la découpe.</li>
        <li><strong>Mais cette décote a une explication à obtenir :</strong> un immeuble de deux T2 en centre ancien qui se vend 28 % sous le prix des appartements de la commune, sans travaux annoncés, cache soit un état, soit une surface surestimée, soit des baux sous-évalués. Les trois se vérifient avec les mêmes pièces.</li>
        <li><strong>Pièces à exiger avant toute offre :</strong> les deux baux et les quittances des douze derniers mois, la taxe foncière, le mesurage Carrez par lot et les plans, le DPE par lot, l'année de construction, les surfaces des deux remises, l'état de la toiture et de la façade, et le règlement de copropriété s'il en existe un.</li>
        <li><strong>Point de méthode :</strong> aucun loyer n'est publié, aucun travaux n'est devisé. Les chiffres de cette fiche reposent sur des loyers de marché estimés et un budget travaux à zéro : ils disent ce que le bien vaut <em>si</em> les baux sont au marché, pas ce qu'il rapporte aujourd'hui.</li>"""

    projections = "\n\n".join(gen.bloc_scenario(s) for s in scenarios)

    t = {
        "badge": "Dossier conditionnel : le prix est bon, les loyers ne sont pas donnés",
        "strategie": "conservation en bloc, deux T2 loués nus et deux remises louées séparément",
        "adresse_courte": "Immeuble de rapport, 2 T2 et 2 remises — La Valette-du-Var (83160)",
        "quartier": "Centre historique, La Valette-du-Var",
        "intro_attractivite": "La Valette-du-Var est une commune de 23 700 habitants en première "
                             "couronne de Toulon, desservie par le réseau Mistral, l'A57 et l'A570, "
                             "avec un centre ancien vivant, un marché et 17 établissements scolaires. "
                             "Le marché y est liquide — plus de 1 100 transactions par an — et les "
                             "prix ont progressé de 9 % entre 2021 et 2025. C'est exactement le type "
                             "de commune où un immeuble acheté sous le prix des appartements se "
                             "revend bien.",
        "profil": "des actifs seuls ou en couple, à quinze minutes de Toulon, qui veulent le centre "
                  "et les commerces à pied. Deux T2 de 55 à 63 m² visent ce public, avec une "
                  "rotation modérée : c'est le segment le plus demandé de la commune.",
        "intro_strategie": "Trois lectures du même immeuble : la conservation en bloc avec les deux "
                          "baux en place, la relocation en meublé, et la transformation des deux "
                          "remises en studios. La troisième est la seule qui change l'échelle du "
                          "dossier — mais elle est conditionnelle à trois vérifications qui ne sont "
                          "pas faites.",
        "lecture": f"Le dossier se lit à l'envers de l'habitude : le prix est bon, le revenu n'est "
                   f"pas documenté. À {eur(prix)} honoraires inclus, soit {eur(prix / gen.SURFACE)}/m² "
                   f"sur 127 m² annoncés, l'immeuble s'achète 11 % sous la valeur de la somme de ses "
                   f"lots (ratio coût/valeur {nfr(c['ratio_cout_valeur'], 2)}). Mais l'annonce ne "
                   f"donne aucun loyer, et c'est lui qui décide : à 800 € par T2, le rendement net "
                   f"après IS ressort à {pct(rd['net_sur_revient_pct'])} ; à 650 €, il tombe à "
                   f"{pct(c_650['rendements']['net_sur_revient_pct'])} ; à 900 €, il monte à "
                   f"{pct(c_900['rendements']['net_sur_revient_pct'])}. Trois dossiers différents "
                   f"pour le même prix.",
        "conf": "Les arguments sont réels : cœur historique au calme, deux T2 loués, deux remises "
                "exploitables séparément, une cave, un DPE E qui n'impose rien avant 2034, et surtout "
                "un prix au mètre carré très en dessous de la commune. La sortie est identifiable — "
                "revendre les deux T2 à l'unité, ce que le marché paye 2 888 €/m² sur cette tranche "
                "de surface. Mais rien de tout cela ne se valide sans trois pièces : les baux, le "
                "mesurage, et la taxe foncière. L'annonce elle-même les remplace par une phrase — "
                "« rapport locatif correct » — qui n'est pas un chiffre.",
        "intro_projections": f"Les trois scénarios partent du même prix de {eur(prix)} honoraires "
                             f"inclus et de la même assiette de loyers estimée à {eur(LOYER_TOTAL)} "
                             f"par mois. Seuls la vacance, le niveau des baux et les travaux changent. "
                             f"Le scénario Worst n'est pas une hypothèse d'école : des baux signés il "
                             f"y a six ou huit ans à 650 € sont la configuration la plus courante "
                             f"dans un immeuble vendu « avec rapport locatif correct ».",
        "releve": releve,
        "garde_fous": garde_fous,
        "stance": f"On ne fait pas d'offre avant d'avoir lu les deux baux. Si les loyers sont au "
                  f"niveau du marché (800 € et plus par T2), on propose {eur(plafond)} honoraires "
                  f"inclus, pas un euro de plus, et le dossier tient. Si les baux sont à 650 €, le "
                  f"prix qui tient le plancher tombe sous 220 000 € et il n'y a pas de discussion "
                  f"possible sur un bien affiché 265 000 €.",
        "verdict_texte": f"À {eur(prix)} honoraires inclus, le prix de revient ressort à "
                         f"{eur(c['prix_revient_total'])} et le rendement net après IS à "
                         f"{pct(rd['net_sur_revient_pct'])} avec des loyers estimés au marché, sous "
                         f"le plancher de 5 % de la branche. Le solde mensuel est de "
                         f"{euro_signe(d['solde'])}. Le prix plafond est de {eur(plafond)}, soit "
                         f"{pct((prix - plafond) / prix * 100)} sous l'affichage : l'écart est dans "
                         f"l'ordre du négociable. Mais la vraie réserve n'est pas le prix, c'est "
                         f"l'absence de loyers : aucune conclusion solide ne peut être tirée d'une "
                         f"annonce qui annonce un « rapport correct » sans le chiffrer. C'est un "
                         f"dossier à instruire, pas un dossier à écarter.",
        "performance": f"{pct(rd['net_sur_revient_pct'])} de rendement net après IS sur un prix de "
                       f"revient de {eur(c['prix_revient_total'])}, pour un plancher de 5 % : "
                       f"performance {nfr(comp['s_performance'], 1)}/10. EBE avant IS : "
                       f"{eur(f['ebe'])}, amortissement {eur(f['amortissement'])}, IS "
                       f"{eur(f['is_annuel'])}. Ratio prix de revient sur valeur : "
                       f"{nfr(c['ratio_cout_valeur'], 2)} — l'achat se fait sous la valeur, ce qui "
                       f"est la principale qualité du dossier.",
        "prix_texte": f"Prix plafond {eur(plafond)} et prix cible {eur(cible)}, soit "
                      f"{pct((prix - plafond) / prix * 100)} et {pct((prix - cible) / prix * 100)} sous "
                      f"le prix affiché. L'offre se cale sur le plafond — {eur(plafond)} honoraires "
                      f"inclus, soit {eur(plafond - 15000.0)} net vendeur — et se justifie par les "
                      f"loyers, jamais par le seul rendement cible.",
    }

    calcule("EBE base", round(f["ebe"]), round(engine.compute(r)["fiscal"]["ebe"]))
    calcule("rendement net/revient", round(rd["net_sur_revient_pct"], 2),
            round(f["net_apres_is"] / c["prix_revient_total"] * 100, 2), tolerance=0.05)
    calcule("prix au m²", round(prix / gen.SURFACE), round(265000.0 / 127.0))
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
        strategie_html=bloc_strategie({"strategies": strategies}),
        releve=t["releve"], grille=bloc_grille(d), identite=bloc_identite(d),
        intro_projections=t["intro_projections"], projections=projections,
        risques=gen.bloc_risques({"rec": r}), verdict_cls=d["classe"], stance=t["stance"],
        verdict_texte=t["verdict_texte"], performance=t["performance"], prix_texte=t["prix_texte"],
        garde_fous=t["garde_fous"], amortissement=eur(f["amortissement"]),
        frais=eur(r["hypotheses"]["frais_acquisition_euros"]), loyer=nfr(LOYER_T2),
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
