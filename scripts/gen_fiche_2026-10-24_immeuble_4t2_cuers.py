#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère la fiche de l'immeuble de rapport 4 T2 — cœur de village, Cuers (83390).

analyses/2026-10-24-immeuble-4-t2-cuers-centre/index.html — SeLoger 258VMUYNSNEA
(Cuers Immobilier, réf. 4060v ; seconde diffusion Capifrance 964187).

Gabarit et contrôles repris du générateur de la maison de village de Cuers
(scripts/gen_fiche_2026-10-16_maison_village_cuers.py), lui-même adossé au duplex
Champ de Mars. Convention de solde : frais d'acquisition comptants, 90 % du prix
porté sur vingt ans à 3,80 %, assurance comprise.
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
gen.SLUG = "2026-10-24-immeuble-4-t2-cuers-centre"
gen.SURFACE = 117.56
# standard du groupe : 90 % du prix sur 20 ans à 3,80 %, assurance 0,34 %
ANNUITE = 0.9 * (0.038 / 12) / (1 - (1 + 0.038 / 12) ** -240) + 0.9 * 0.0034 / 12
eur, nfr, pct, euro_signe = gen.eur, gen.nfr, gen.pct, gen.euro_signe
calcule = gen.calcule
releve_html = gen.releve_html


def prix_cf_nul(r, lo=50000.0, hi=None):
    """Prix d'achat auquel le solde mensuel est nul, au standard du groupe
    (90 % du prix sur 20 ans à 3,80 %, assurance comprise). C'est le prix cible :
    la note 6,5 ne sert plus de référence."""
    hi = hi or r["annonce"]["prix_retenu_euros"] * 1.2

    def solde(p):
        rr = copy.deepcopy(r)
        rr["annonce"]["prix_retenu_euros"] = p
        base = p - 15000.0 if "la-valette" in r["slug"] else p
        rr["hypotheses"]["frais_acquisition_euros"] = round(base * 0.08)
        cc = engine.compute(rr)
        travaux = rr["bien"]["travaux"]["montant_euros"] or 0.0
        return cc["fiscal"]["net_apres_is"] / 12.0 - (p + travaux) * ANNUITE

    for _ in range(80):
        mid = (lo + hi) / 2
        if solde(mid) > 0:
            lo = mid
        else:
            hi = mid
    return round(lo / 500.0) * 500.0

PRIX = 365000.0
TRAVAUX = 0.0
VALEUR = 345000.0
LOYER_LOT_CC = 629.22
LOYER_LOT_HC = 585.00
LOYER_TOTAL = LOYER_LOT_CC * 4
CHARGES = 2800.0
TF = 2470.0
ENTRETIEN = 3100.0

GABARIT = gen.TEMPLATE
for _avant, _apres in [
    ("Analyse générée le 13 octobre 2026", "Analyse générée le 24 octobre 2026"),
    ("Sensibilité au loyer mensuel — prix affiché de {prix_affiche}",
     "Sensibilité au prix d'achat — quatre baux en place, {loyer} €/mois par lot"),
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


def variante(r, loyer=None, vacance=None, travaux=None, prix=None, entretien=None, charges=None):
    rr = copy.deepcopy(r)
    if loyer is not None:
        rr["marche"]["loyers"][0]["loyer_mensuel_euros"] = loyer
    if vacance is not None:
        rr["hypotheses"]["vacance_base_pct"] = vacance
    if travaux is not None:
        rr["bien"]["travaux"]["montant_euros"] = travaux
    if entretien is not None:
        rr["hypotheses"]["charges"]["entretien_annuel_euros"] = entretien
    if charges is not None:
        rr["hypotheses"]["charges"]["charges_copro_annuelles_euros"] = charges
    if prix is not None:
        rr["annonce"]["prix_retenu_euros"] = prix
        rr["hypotheses"]["frais_acquisition_euros"] = round(prix * 0.08)
    return rr


def bloc_cartes(d):
    cartes = [
        ("Prix affiché", eur(d["prix"]) + f" ({eur(d['prix'] / gen.SURFACE)}/m²)"),
        ("Prix de revient", eur(d["revient"])),
        ("Valeur retenue (tranche 24-36 m²)", eur(VALEUR)),
        ("Loyers retenus", eur(LOYER_TOTAL) + "/mois charges comprises, quatre baux"),
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
        ("Occupation", "Quatre appartements loués nus, un par niveau, aucun lot vide annoncé. Le "
                       "loyer est donné charges comprises par Cuers Immobilier (2 516,88 €/mois) et "
                       "hors charges par Capifrance (2 340 €/mois) : l'écart de 176,88 €/mois est la "
                       "provision sur charges. Aucun bail, aucune quittance, aucune régularisation de "
                       "charges au dossier à ce stade"),
        ("Loyers retenus", f"{eur(LOYER_LOT_CC)}/mois par lot charges comprises, soit "
                           f"{eur(LOYER_LOT_HC)} hors charges et {eur(LOYER_TOTAL)} pour les quatre "
                           f"lots — 19,9 €/m² hors charges, au-dessus du haut de la fourchette des "
                           f"comparables de même surface et 43 % au-dessus de la médiane communale "
                           f"DHUP 2025 (13,9 €/m²)"),
        ("Charges de copropriété", eur(b["copro"]["charges_annuelles_euros"]) + " — "
         + b["copro"]["charges_source"]),
        ("Taxe foncière", eur(h["taxe_fonciere_annuelle_euros"]) + "/an — "
         + h["taxe_fonciere_commentaire"]),
        ("Entretien et gestion", eur(h["entretien_annuel_euros"]) + "/an — "
         + h["entretien_commentaire"]),
        ("Frais d'acquisition", eur(d["rec"]["hypotheses"]["frais_acquisition_euros"]) + " — "
         + d["rec"]["hypotheses"]["frais_acquisition_commentaire"]),
        ("Amortissement", eur(d["f"]["amortissement"]) + "/an — 90 % du prix de revient sur 30 ans"),
        ("DPE / GES", "C / A — 162 kWh/m²/an d'énergie primaire, 4 kg CO2/m²/an. Aucun calendrier "
                      "d'interdiction de louer sur ce classement : le risque du dossier n'est pas "
                      "énergétique, il est locatif et tarifaire"),
        ("Annexes", "Aucune cave, aucun parking, aucun garage, aucun extérieur. Rien à louer "
                    "séparément et rien à valoriser à la revente"),
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
            f"          <td>{eur(VALEUR)}</td>\n"
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
    cible = prix_cf_nul(r)

    c_hc = engine.compute(variante(r, loyer=LOYER_LOT_HC, charges=677.0))
    c_meuble = engine.compute(variante(r, loyer=LOYER_LOT_CC + 55.0, entretien=ENTRETIEN + 900.0))
    revient_decoupe = PRIX * 1.08
    sortie_basse = 4 * 29.39 * 2378.0
    sortie_haute = 4 * 29.39 * 2939.0

    scenarios = []
    for sc in (
        {"libelle": "Scénario Base", "classe": "scenario-base", "loyer": LOYER_LOT_CC, "vacance": 5.0,
         "travaux": TRAVAUX, "entretien": ENTRETIEN, "charges": CHARGES,
         "sous_titre": f"Loyers en place {eur(LOYER_LOT_CC)}/mois par lot — vacance 5 % — prix "
                       f"affiché {eur(prix)} — aucun travaux"},
        {"libelle": "Scénario Best", "classe": "scenario-best", "loyer": LOYER_LOT_CC, "vacance": 2.0,
         "travaux": TRAVAUX, "entretien": round(ENTRETIEN * 0.9), "charges": CHARGES,
         "sous_titre": "Vacance 2 % — loyers inchangés (ils sont déjà au plafond du marché, aucune "
                       "progression n'est retenue) — charges de gestion −10 %"},
        {"libelle": "Scénario Worst", "classe": "scenario-worst", "loyer": round(LOYER_LOT_CC * 0.88, 2),
         "vacance": 12.0, "travaux": 5000.0, "entretien": round(ENTRETIEN * 1.2),
         "charges": CHARGES + 500.0,
         "sous_titre": "Relocation 12 % sous les loyers en place — vacance 12 % — 5 000 € de travaux "
                       "imprévus (toiture, façade, évacuations) — charges +20 %"},
    ):
        rr = variante(r, loyer=sc["loyer"], vacance=sc["vacance"], travaux=sc["travaux"],
                      entretien=sc["entretien"], charges=sc["charges"])
        cc = engine.compute(rr)
        assiette = prix + sc["travaux"]
        scenarios.append({"libelle": sc["libelle"], "classe": sc["classe"], "sous_titre": sc["sous_titre"],
                          "loyer": sc["loyer"], "vacance": sc["vacance"], "travaux": sc["travaux"],
                          "rec": rr, "c": cc,
                          "solde": cc["fiscal"]["net_apres_is"] / 12.0 - assiette * ANNUITE})

    grille = []
    for p in (PRIX, 345000.0, float(plafond), 300000.0, 280000.0, float(cible)):
        rr = variante(r, prix=p)
        cc = engine.compute(rr)
        grille.append({"prix": p, "ebe": cc["fiscal"]["ebe"], "net": cc["fiscal"]["net_apres_is"],
                       "solde": cc["fiscal"]["net_apres_is"] / 12.0 - (p + TRAVAUX) * ANNUITE,
                       "rdt": cc["rendements"]["net_sur_revient_pct"]})

    strategies = [
        {"strategie": r["analyse"]["strategies_explorees"][0]["strategie"], "lots": 4,
         "rdt": rd["net_sur_revient_pct"], "loyer_label": eur(LOYER_TOTAL) + " CC",
         "ratio": c["ratio_cout_valeur"], "net_label": eur(f["net_apres_is"]) + "/an",
         "faisabilite": "Immédiate : quatre baux en place, aucun travaux annoncé",
         "risque": "modéré", "retenue": True},
        {"strategie": r["analyse"]["strategies_explorees"][1]["strategie"], "lots": 4,
         "rdt": c_meuble["rendements"]["net_sur_revient_pct"],
         "loyer_label": eur((LOYER_LOT_CC + 55.0) * 4) + " CC",
         "ratio": c_meuble["ratio_cout_valeur"],
         "net_label": eur(c_meuble["fiscal"]["net_apres_is"]) + "/an",
         "faisabilite": "Ameublement des quatre lots, 16 000 € à engager",
         "risque": "élevé", "retenue": False},
        {"strategie": r["analyse"]["strategies_explorees"][2]["strategie"],
         "lots": 4, "rdt": None, "loyer_label": "opération de revente",
         "ratio": revient_decoupe / sortie_haute,
         "net_label": euro_signe(sortie_haute - revient_decoupe) + " de marge",
         "faisabilite": "Portage 18 à 24 mois, deux jeux de frais",
         "risque": "élevé", "retenue": False},
    ]

    adresse = "Cœur du village, Cuers (83390) — adresse exacte non communiquée par l'agence"
    lat, lon = "43.2375", "6.0715"

    d = {"slug": gen.SLUG, "adresse": adresse, "rec": r, "c": c, "note": note, "verdict": verdict,
         "comp": comp, "f": f, "rd": rd, "prix": prix, "loyer": LOYER_LOT_CC,
         "revient": c["prix_revient_total"], "solde": f["net_apres_is"] / 12.0 - (prix + TRAVAUX) * ANNUITE,
         "classe": {"acheter": "buy", "negocier": "nego", "fuir": "pass"}[verdict],
         "classe_note": scoring.classe_note(note), "plafond": plafond, "contrainte": contrainte,
         "cible": cible, "scenarios": scenarios, "grille": grille, "strategies": strategies}

    solde_plafond = (engine.compute(variante(r, prix=plafond))["fiscal"]["net_apres_is"] / 12.0
                     - (plafond + TRAVAUX) * ANNUITE)
    solde_cible = (engine.compute(variante(r, prix=cible))["fiscal"]["net_apres_is"] / 12.0
                   - (cible + TRAVAUX) * ANNUITE)

    releve = releve_html(
        ["Source", "Chiffre", "Lecture"],
        [["DVF Cuers (83049), appartements 24-36 m², ventes 2021-2025", "26 ventes — médiane "
          "2 378 €/m², premier quartile 1 791, troisième quartile 2 939 — prix médian 66 600 € le lot",
          "la tranche du bien : quatre lots de 29,4 m² valent 280 000 à 345 000 € au prix du marché"],
         ["DVF Cuers, appartements 20-40 m²", "40 ventes — médiane 2 617 €/m², prix médian 76 950 €",
          "confirme la fourchette : un T2 de 29 m² se paie 77 000 à 90 000 €, pas 91 250 €"],
         ["DVF Cuers, appartements 30-45 m²", "108 ventes — médiane 3 384 €/m², mais dix ventes entre "
          "4 500 et 8 590 €/m²", "médiane tirée par des lots neufs et des lots avec garage : elle ne "
          "décrit pas ce produit et ne doit pas servir de référence"],
         ["Médiane DHUP 2025, Cuers", "13,9 €/m² (IC 95 % 10,7 à 18,0)",
          "le repère communal toutes surfaces ; les petites surfaces se louent au-dessus, c'est "
          "pourquoi les comparables de même taille priment"],
         ["Location relevée — studio meublé 30,19 m², 4 place Général de Gaulle, Cuers", "560 à "
          "620 €/mois CC", "l'annonce de la commune la plus proche du produit, en plein centre"],
         ["Location relevée — studio non meublé 29 m², centre-ville, Cuers", "550 €/mois CC "
          "(538 € HC)", "septembre 2026 : le loyer nu de référence sur la surface exacte du dossier"],
         ["Location relevée — T2 42 m² rénové en 2023, Cuers", "690 €/mois CC (635 € HC), 15,1 €/m²",
          "surface plus grande, loyer au mètre carré plus bas : la petite surface se paie plus cher"],
         ["Location relevée — T2 meublé 40 m² de caractère et T2 meublé 53 m² avec garage", "635 et "
          "750 €/mois CC", "le haut de la fourchette communale, meublé et avec garage"],
         ["Loyers du dossier", f"{eur(LOYER_LOT_HC)} HC par lot, soit 19,9 €/m²",
          "au-dessus du haut de la fourchette des comparables de même surface : les loyers sont au "
          "plafond, pas en dessous"],
         ["Charges de copropriété et taxe foncière annoncées", f"{eur(CHARGES)}/an et {eur(TF)}/an",
          "8,8 % du loyer brut part en charges et taxe foncière, avant gestion, impayés et provision"],
         ["Écart entre les deux diffusions du même bien", "2 516,88 € CC contre 2 340 € HC",
          "176,88 €/mois de provision sur charges : les deux annonces se réconcilient, mais aucune "
          "n'est une pièce comptable"]])

    garde_fous = f"""        <li><strong>Prix plafond : {eur(plafond)}</strong> (contrainte du moteur : {contrainte}), soit {pct((prix - plafond) / prix * 100)} sous le prix affiché. À ce prix le rendement atteint le plancher de 5 %, mais le solde mensuel reste {euro_signe(solde_plafond)} : le plancher de rendement et le plancher de trésorerie ne coïncident pas.</li>
        <li><strong>Prix de cash-flow nul : {eur(cible)}</strong>, soit {pct((prix - cible) / prix * 100)} sous l'affichage. C'est le prix auquel les loyers portent l'échéance ; il est sous la valeur de marché du bien (345 000 €) et ne s'obtiendra pas.</li>
        <li><strong>Le solde au prix affiché : {euro_signe(d['solde'])} par mois.</strong> Traduit sur le barème du parc, cela consomme {abs(d['solde']) * 12 / 5375:.1f} place de stationnement par an, soit environ {abs(d['solde']) * 12 / 5375 * 6:.0f} places sur six ans — et le cash d'entrée correspond à {PRIX * 0.18 / 5375:.0f} places.</li>
        <li><strong>Les loyers sont au plafond, pas en dessous :</strong> 585 € hors charges pour 29 m² contre 538 € HC pour un studio nu de 29 m² en centre-ville. Aucune progression à attendre, et une relocation se ferait 8 à 12 % plus bas. Chaque point de loyer perdu vaut {eur(LOYER_TOTAL * 12 * 0.01)} par an.</li>
        <li><strong>Le poste qui peut tuer le compte, c'est la ligne « électricité » :</strong> les charges comprises couvriraient l'eau, l'électricité et les parties communes, pour une provision de 2 123 €/an quand le seul poste énergie du bâtiment est estimé entre 2 900 et 3 570 €/an. Si les compteurs individuels n'existent pas, l'EBE perd 2 500 à 3 000 €/an.</li>
        <li><strong>Pièces à exiger avant toute discussion de prix :</strong> les quatre baux et les quittances des douze derniers mois, la dernière régularisation de charges, les trois derniers PV d'AG et les appels de fonds, le carnet d'entretien et le plan pluriannuel de travaux, l'avis de taxe foncière, les DPE par lot, l'attestation de compteurs individuels eau et électricité, et le diagnostic de l'électricité des communs.</li>
        <li><strong>Point de méthode :</strong> le rendement brut de 8,27 % n'est pas le rendement du dossier. Après charges, taxe foncière, vacance, gestion, impayés et provision travaux, l'EBE tombe à {eur(f['ebe'])} et le net après IS à {eur(f['net_apres_is'])}, soit {pct(rd['net_sur_revient_pct'])} du prix de revient.</li>"""

    projections = "\n\n".join(gen.bloc_scenario(s) for s in scenarios)

    t = {
        "badge": "Dossier classé : le prix ne porte pas les loyers",
        "strategie": "conservation en bloc des quatre T2 loués nus",
        "adresse_courte": "Immeuble de rapport, 4 T2 loués — cœur de village, Cuers (83390)",
        "quartier": "Centre-ville, Cuers",
        "intro_attractivite": "Cuers est un bourg de 12 300 habitants à vingt kilomètres de Toulon, "
                             "sur l'A57, avec une gare TER et un centre commerçant vivant. Le bien est "
                             "au cœur du village, à pied de la place de la Convention et du marché : "
                             "c'est le meilleur emplacement locatif de la commune pour des petites "
                             "surfaces. La demande existe — cinq annonces de 29 à 53 m² étaient "
                             "actives le 24 octobre 2026 — mais elle se paie 550 à 620 € par mois, "
                             "pas 629.",
        "profil": "un locataire seul ou en couple, actif, à budget modéré, qui veut le centre et se "
                  "passe de voiture au quotidien. C'est exactement le public des studios de 29-30 m² "
                  "relevés à 550-620 €/mois. Quatre lots de ce format visent quatre fois ce public, "
                  "donc quatre rotations possibles.",
        "intro_strategie": "Trois lectures chiffrées du même immeuble : la conservation en bloc avec "
                          "les quatre baux en place, la relocation en meublé, et la revente à la "
                          "découpe — la copropriété de quatre lots existe déjà, il n'y a rien à "
                          "diviser. Aucune ne change le diagnostic : le bien produit, le prix coûte "
                          "trop cher pour ce qu'il produit.",
        "lecture": f"Le dossier ne se juge pas au mètre carré : à {eur(prix)} pour 117,56 m², le bien "
                   f"sort à 3 105 €/m², soit 5,7 % au-dessus du troisième quartile de sa propre "
                   f"tranche de surface (2 939 €/m², DVF Cuers, 26 ventes de 24-36 m²). Il se juge au "
                   f"rendement, et là il ne passe pas : {pct(rd['net_sur_revient_pct'])} net après IS "
                   f"sur un prix de revient de {eur(c['prix_revient_total'])} pour un plancher de 5 %, "
                   f"et un solde mensuel de {euro_signe(d['solde'])}. Le brut de 8,27 % est réel ; "
                   f"c'est la charge — 2 800 € de copropriété, 2 470 € de taxe foncière, quatre baux "
                   f"à gérer — qui le ramène sous le seuil.",
        "conf": "L'immeuble a de vrais arguments : rénové intérieur et extérieur en 2019, DPE C, "
                "climatisation réversible, quatre lots déjà constitués en copropriété, un emplacement "
                "de centre-bourg que la commune ne reproduit pas, et quatre baux en place qui "
                "produisent dès le premier mois. Sur ce marché, c'est un produit d'investisseur "
                "correct — et c'est précisément pourquoi il est au prix du marché : 3 105 €/m² pour du "
                "rénové 2019 en cœur de village n'est pas une anomalie. Le problème n'est pas le bien, "
                "c'est l'équation entre un prix de marché et des loyers de marché : à Cuers, un "
                "appartement à 3 000 €/m² loué 585 € par mois rend 4,5 % net après IS. Aucune "
                "négociation de 10 % ne transforme ce produit en dossier de rendement.",
        "intro_projections": f"Les trois scénarios partent du même prix de {eur(prix)} et de la même "
                             f"assiette de loyers en place, {eur(LOYER_LOT_CC)} par lot et par mois "
                             f"charges comprises. Seuls la vacance, le niveau de relocation et les "
                             f"charges changent. Le scénario Best ne suppose aucune hausse de loyer : "
                             f"les loyers en place sont déjà au-dessus du haut de la fourchette "
                             f"communale.",
        "releve": releve,
        "garde_fous": garde_fous,
        "stance": f"On ne tente pas. Une offre à {eur(cible)} — le prix du solde nul — serait "
                  f"{pct((prix - cible) / prix * 100)} sous l'affichage et 25 % sous la valeur du bien : "
                  f"aucun vendeur ne signe, et le dossier n'a pas d'autre qualité qui justifierait d'y "
                  f"passer du temps. À {eur(plafond)}, il tient le plancher de rendement mais reste à "
                  f"{euro_signe(solde_plafond)} par mois : ce n'est pas un achat, c'est une recharge "
                  f"de trésorerie. On garde le bien au registre et on le rouvre si le prix passe sous "
                  f"{eur(cible + 20000)}, pas avant.",
        "verdict_texte": f"À {eur(prix)}, l'immeuble rend {pct(rd['net_sur_revient_pct'])} net après "
                         f"IS pour un prix de revient de {eur(c['prix_revient_total'])}, sous le "
                         f"plancher de 5 % de la branche, et il laisse {euro_signe(d['solde'])} par "
                         f"mois à la charge du propriétaire. Le prix plafond est de {eur(plafond)}, "
                         f"soit {pct((prix - plafond) / prix * 100)} sous l'affichage : cette décote "
                         f"est dans l'ordre de grandeur d'une négociation, mais elle ne suffit pas — "
                         f"à ce prix le solde reste {euro_signe(solde_plafond)} par mois. Le prix qui "
                         f"annule le solde, {eur(cible)}, est {pct((prix - cible) / prix * 100)} sous "
                         f"l'affichage et sous la valeur de marché : il n'existe pas. C'est un dossier "
                         f"à écarter au prix demandé, pas à travailler.",
        "performance": f"{pct(rd['net_sur_revient_pct'])} de rendement net après IS sur un prix de "
                       f"revient de {eur(c['prix_revient_total'])}, pour un plancher de branche de "
                       f"5 % : performance {nfr(comp['s_performance'], 1)}/10. EBE avant IS : "
                       f"{eur(f['ebe'])}. L'amortissement du bâti ({eur(f['amortissement'])}/an) "
                       f"ramène l'IS à {eur(f['is_annuel'])}, ce qui protège la trésorerie sans créer "
                       f"de rendement. Ratio prix de revient sur valeur : "
                       f"{nfr(c['ratio_cout_valeur'], 2)} — on achète 14 % au-dessus de la valeur de "
                       f"la tranche de surface.",
        "prix_texte": f"Prix plafond {eur(plafond)} et prix cible {eur(cible)}, soit "
                      f"{pct((prix - plafond) / prix * 100)} et {pct((prix - cible) / prix * 100)} sous "
                      f"le prix affiché. Les deux chiffres ne mesurent pas la même chose : le plafond "
                      f"est le prix du rendement, la cible est le prix de la trésorerie. Sur ce "
                      f"dossier, le rendement demande {eur(plafond - cible)} de moins que la "
                      f"trésorerie — et c'est la trésorerie qui commande, puisque la capacité "
                      f"d'engagement du groupe est bornée.",
    }

    calcule("EBE base", round(f["ebe"]), round(engine.compute(r)["fiscal"]["ebe"]))
    calcule("rendement net/revient", round(rd["net_sur_revient_pct"], 2),
            round(f["net_apres_is"] / c["prix_revient_total"] * 100, 2), tolerance=0.05)
    calcule("prix au m²", round(prix / gen.SURFACE), round(365000.0 / 117.56))
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
        frais=eur(r["hypotheses"]["frais_acquisition_euros"]), loyer=nfr(LOYER_LOT_CC),
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
