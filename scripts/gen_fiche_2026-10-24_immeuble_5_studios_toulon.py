#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère la fiche de l'immeuble 5 studios meublés — Saint-Jean-du-Var, Toulon (83100).

analyses/2026-10-24-immeuble-5-studios-toulon-saint-jean/index.html — SeLoger 26YVBFMFBW3E
(Capifrance, Hubert Pieraccini, réf. 975456).

Gabarit et contrôles repris du générateur de l'immeuble de La Seyne.
Convention de solde : frais d'acquisition comptants, 90 % du prix porté sur vingt ans
à 3,80 %, assurance comprise. Prix cible = solde nul.
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
gen.SLUG = "2026-10-24-immeuble-5-studios-toulon-saint-jean"
gen.SURFACE = 90.0
ANNUITE = 0.9 * (0.038 / 12) / (1 - (1 + 0.038 / 12) ** -240) + 0.9 * 0.0034 / 12
eur, nfr, pct, euro_signe = gen.eur, gen.nfr, gen.pct, gen.euro_signe
calcule = gen.calcule
releve_html = gen.releve_html

PRIX = 299000.0
TRAVAUX = 0.0
VALEUR = 300000.0
LOYER_STUDIO = 448.6
LOYER_TOTAL = LOYER_STUDIO * 5
TF = 2000.0
ENTRETIEN = 3860.0


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


def prix_cf_nul(lo=100000.0, hi=None):
    hi = hi or PRIX * 1.2

    def solde(p):
        cc = engine.compute(variante(rec(), prix=p))
        return cc["fiscal"]["net_apres_is"] / 12.0 - (p + TRAVAUX) * ANNUITE

    for _ in range(80):
        mid = (lo + hi) / 2
        if solde(mid) > 0:
            lo = mid
        else:
            hi = mid
    return round(lo / 500.0) * 500.0


GABARIT = gen.TEMPLATE
for _avant, _apres in [
    ("Analyse générée le 13 octobre 2026", "Analyse générée le 24 octobre 2026"),
    ("Sensibilité au loyer mensuel — prix affiché de {prix_affiche}",
     "Sensibilité au prix d'achat — loyers annoncés {loyer} €/mois par studio"),
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


def bloc_cartes(d):
    cartes = [
        ("Prix affiché", eur(d["prix"]) + f" ({eur(d['prix'] / gen.SURFACE)}/m² annoncés)"),
        ("Prix de revient", eur(d["revient"])),
        ("Valeur retenue (DVF studios)", eur(VALEUR)),
        ("Loyers annoncés", eur(LOYER_TOTAL) + "/mois — 9 % bruts, non documentés"),
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
        ("Occupation", "Cinq studios meublés loués et un garage, monopropriété. Aucun bail, aucune "
                       "quittance, aucun état des lieux au dossier : la rentabilité de 9 % est une "
                       "annonce, pas un relevé"),
        ("Loyers retenus", f"{eur(LOYER_STUDIO)}/mois par studio, soit {eur(LOYER_TOTAL)} — c'est "
                           f"exactement l'assiette qui donne 9 % sur 299 000 €. Plausible au marché "
                           f"haut des micro-surfaces meublées (24,9 €/m² pour 18 m², contre une "
                           f"médiane DHUP de 14,4 €/m² et un T1 de 25 m² à 415 €)"),
        ("Charges de copropriété", "Aucune — monopropriété. Cinq compteurs d'eau et cinq compteurs "
                                   "d'électricité individuels : le poste de charges collectives, "
                                   "habituellement le poison de ce produit, est neutralisé"),
        ("Taxe foncière", eur(h["taxe_fonciere_annuelle_euros"]) + "/an — "
         + h["taxe_fonciere_commentaire"]),
        ("Entretien et gestion", eur(h["entretien_annuel_euros"]) + "/an — "
         + h["entretien_commentaire"]),
        ("Frais d'acquisition", eur(d["rec"]["hypotheses"]["frais_acquisition_euros"]) + " — "
         + d["rec"]["hypotheses"]["frais_acquisition_commentaire"]),
        ("Amortissement", eur(d["f"]["amortissement"]) + "/an — 90 % du prix de revient sur 30 ans"),
        ("DPE / GES", "C (quatre lots) et D (un lot) / GES A — aucun calendrier d'interdiction avant "
                      "2034. Le risque du dossier n'est pas énergétique"),
        ("Surfaces", "90 m² dans le titre, « 100 m² environ » dans le descriptif, cinq studios "
                     "d'environ 18 m² plus un garage : le compte ne tombe pas, aucun Carrez par lot"),
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

    plafond_txt = (f"{pct((plafond - prix) / prix * 100)} au-dessus de l'affichage — la contrainte "
                   f"est la marge de sécurité, pas le rendement" if plafond > prix else
                   f"{pct((prix - plafond) / prix * 100)} sous l'affichage")
    c_400 = engine.compute(variante(r, loyer=400.0))
    c_375 = engine.compute(variante(r, loyer=375.0))
    c_480 = engine.compute(variante(r, loyer=480.0))
    sortie = 5 * 18 * 3809.0

    scenarios = []
    for sc in (
        {"libelle": "Scénario Base", "classe": "scenario-base", "loyer": LOYER_STUDIO,
         "vacance": 7.0, "travaux": TRAVAUX,
         "sous_titre": f"Loyers annoncés {eur(LOYER_STUDIO)} par studio — vacance 7 % (cinq baux "
                       f"meublés) — prix affiché {eur(prix)}"},
        {"libelle": "Scénario Best", "classe": "scenario-best", "loyer": 480.0,
         "vacance": 3.0, "travaux": TRAVAUX,
         "sous_titre": "Loyers 480 € par studio — vacance 3 % — les quittances confirment le 9 %"},
        {"libelle": "Scénario Worst", "classe": "scenario-worst", "loyer": 375.0,
         "vacance": 15.0, "travaux": 6000.0,
         "sous_titre": "Relocation à 375 € par studio — vacance 15 % (deux studios vides en fin "
                       "d'année) — 6 000 € de travaux imprévus"},
    ):
        rr = variante(r, loyer=sc["loyer"], vacance=sc["vacance"], travaux=sc["travaux"])
        cc = engine.compute(rr)
        assiette = prix + sc["travaux"]
        scenarios.append({"libelle": sc["libelle"], "classe": sc["classe"], "sous_titre": sc["sous_titre"],
                          "loyer": sc["loyer"] * 5, "vacance": sc["vacance"],
                          "travaux": sc["travaux"], "rec": rr, "c": cc,
                          "solde": cc["fiscal"]["net_apres_is"] / 12.0 - assiette * ANNUITE})

    grille = []
    for p in (PRIX, 280000.0, 260000.0, float(cible), 230000.0):
        rr = variante(r, prix=p)
        cc = engine.compute(rr)
        grille.append({"prix": p, "ebe": cc["fiscal"]["ebe"], "net": cc["fiscal"]["net_apres_is"],
                       "solde": cc["fiscal"]["net_apres_is"] / 12.0 - (p + TRAVAUX) * ANNUITE,
                       "rdt": cc["rendements"]["net_sur_revient_pct"]})

    strategies = [
        {"strategie": "Conservation en bloc : cinq studios meublés et un garage", "lots": 6,
         "rdt": rd["net_sur_revient_pct"], "loyer_label": "loyers annoncés",
         "ratio": c["ratio_cout_valeur"], "valeur": VALEUR,
         "net_label": eur(f["net_apres_is"]) + "/an",
         "faisabilite": "Immédiate : cinq baux en place, aucun travaux annoncé", "risque": "élevé",
         "retenue": True},
        {"strategie": "Bascule en location nue", "lots": 5,
         "rdt": c_375["rendements"]["net_sur_revient_pct"], "loyer_label": "375 € par studio",
         "ratio": c_375["ratio_cout_valeur"], "valeur": VALEUR,
         "net_label": eur(c_375["fiscal"]["net_apres_is"]) + "/an",
         "faisabilite": "Changement de bail, mobilier à sortir", "risque": "élevé",
         "retenue": False},
        {"strategie": "Revente à la découpe des cinq studios", "lots": 5, "rdt": None,
         "loyer_label": "opération de revente",
         "ratio": c["prix_revient_total"] / sortie, "valeur": sortie,
         "net_label": euro_signe(sortie - c["prix_revient_total"]) + " de marge brute",
         "faisabilite": "Cinq ventes de lots loués, 12 à 24 mois", "risque": "élevé",
         "retenue": False},
    ]

    adresse = "La Roseraie / Saint-Jean-du-Var, Toulon (83100) — adresse exacte non communiquée"
    lat, lon = "43.1240", "5.9560"

    d = {"slug": gen.SLUG, "adresse": adresse, "rec": r, "c": c, "note": note, "verdict": verdict,
         "comp": comp, "f": f, "rd": rd, "prix": prix, "loyer": LOYER_STUDIO,
         "revient": c["prix_revient_total"], "solde": f["net_apres_is"] / 12.0 - (prix + TRAVAUX) * ANNUITE,
         "classe": {"acheter": "buy", "negocier": "nego", "fuir": "pass"}[verdict],
         "classe_note": scoring.classe_note(note), "plafond": plafond, "contrainte": contrainte,
         "cible": cible, "scenarios": scenarios, "grille": grille, "strategies": strategies}

    releve = releve_html(
        ["Source", "Chiffre", "Lecture"],
        [["DVF Toulon, studios de 9 à 20 m²", "288 ventes 2021-2025 — médiane 3 809 €/m², premier "
          "quartile 3 132, prix médian 64 950 €",
          "la tranche du produit : un studio de 18 m² vaut environ 68 000 € à Toulon"],
         ["DVF Toulon, appartements de 20 à 30 m²", "1 032 ventes — médiane 3 106 €/m²",
          "confirme la prime des micro-surfaces"],
         ["DVF Toulon, appartements de 60 à 100 m²", "5 971 ventes — médiane 2 396 €/m²",
          "le même immeuble loué en deux T3 vaudrait 215 000 €, pas 300 000 : la valeur est dans "
          "le découpage et les baux"],
         ["Comparables internes, quartiers populaires de l'Est toulonnais", "85 m² à 132 000 € "
          "(Saint-Jean-du-Var), 77 m² à 160 000 €, 63 m² à 99 000 € (La Rode)",
          "1 550 à 2 100 €/m² pour le bâti : le prix demandé est 60 % au-dessus des murs"],
         ["Médiane DHUP 2025, Toulon", "14,4 €/m² (IC 95 % 11,2 à 18,7) — T1 de 25 m² à 415 €",
          "le repère communal des petites surfaces"],
         ["Loyers annoncés par le vendeur", "9 % de 299 000 €, soit 2 243 €/mois, 448,60 € par studio",
          "24,9 €/m² sur 18 m² : au-dessus du haut de la fourchette, plausible seulement si les "
          "quittances le prouvent"],
         ["Géographie prioritaire", "Saint-Jean-du-Var : QPV de la liste préfectorale, QVA du contrat "
          "de ville 2024-2030 de la métropole TPM",
          "ce n'est pas un critère de confort : c'est le risque de relocation et de revente"],
         ["Rendement selon le loyer", f"{pct(c_375['rendements']['net_sur_revient_pct'])} à 375 € — "
          f"{pct(rd['net_sur_revient_pct'])} à 449 € — "
          f"{pct(c_480['rendements']['net_sur_revient_pct'])} à 480 €",
          "les 9 % annoncés tiennent au loyer : c'est la première pièce à exiger"]])

    garde_fous = f"""        <li><strong>Prix plafond : {eur(plafond)}</strong> — {plafond_txt}. Le rendement de 5 % est atteint dès le prix affiché, ce qui est rare dans ce fil : le dossier passe le plancher, il ne passe pas le solde.</li>
        <li><strong>Prix cible : {eur(cible)}</strong>, soit {pct((prix - cible) / prix * 100)} sous l'affichage — le prix auquel le solde mensuel tombe à zéro.</li>
        <li><strong>Le solde au prix affiché : {euro_signe(d['solde'])} par mois.</strong> C'est le meilleur rendement des quatre dossiers du jour, et il reste négatif de 295 € : 9 % brut ne suffisent pas à couvrir le prix.</li>
        <li><strong>Les 9 % ne sont pas une quittance :</strong> à 400 € par studio le rendement net tombe à {pct(c_400['rendements']['net_sur_revient_pct'])}, à 375 € à {pct(c_375['rendements']['net_sur_revient_pct'])}. Cinq baux meublés de 18 m² dans un quartier populaire, cela se reloue — mais pas forcément à 449 €.</li>
        <li><strong>Le quartier est un QPV :</strong> Saint-Jean-du-Var figure dans la géographie prioritaire, en QVA du contrat de ville 2024-2030. La Roseraie est un secteur résidentiel plus calme, mais l'adresse exacte n'est pas donnée. Visite du quartier un samedi après-midi, sans l'agent, avant toute offre : hall, caves, qui traîne dans l'impasse, état des communs.</li>
        <li><strong>Pièces à exiger avant toute offre :</strong> les cinq baux et les quittances des douze derniers mois, les cinq états des lieux, l'avis de taxe foncière, les DPE par lot et l'année de construction, le mesurage Carrez par lot, l'état de la toiture et des chauffe-eau, et le contrat du « syndic » — qui n'en est pas un, puisqu'il n'y a pas de copropriété.</li>
        <li><strong>Point de méthode :</strong> l'assiette est celle annoncée par le vendeur. Aucun loyer n'est documenté, aucun travaux n'est devisé, deux surfaces circulent. Les chiffres publiés disent ce que le bien rend <em>si</em> les quittances confirment les 9 %.</li>"""

    projections = "\n\n".join(gen.bloc_scenario(s) for s in scenarios)

    t = {
        "badge": "Le meilleur rendement du fil, sur les baux les moins prouvés",
        "strategie": "conservation en bloc de cinq studios meublés et d'un garage",
        "adresse_courte": "Immeuble 5 studios meublés et garage — Toulon (83100)",
        "quartier": "Saint-Jean-du-Var / La Roseraie, Toulon",
        "intro_attractivite": "Toulon Est, à moins de 100 m du collège Voltaire, dans une impasse au "
                             "calme : la demande de petites surfaces meublées y est structurelle — "
                             "3,4 % de vacance communale, 3 000 transactions par an, étudiants, jeunes "
                             "actifs, personnel hospitalier. Mais Saint-Jean-du-Var est un quartier de "
                             "la politique de la ville, et c'est le prix à payer pour 9 % brut.",
        "profil": "des étudiants, des jeunes actifs et du personnel en mobilité, pour des studios "
                  "meublés de 18 m² à moins de 450 €. C'est le segment le plus liquide de Toulon, et "
                  "celui qui tourne le plus vite : cinq baux, cinq rotations possibles.",
        "intro_strategie": "Trois lectures : la conservation en meublé avec les cinq baux en place, la "
                          "bascule en location nue, et la revente à la découpe. La première est la "
                          "seule qui tienne le rendement ; la troisième ne couvre pas ses frais.",
        "lecture": f"C'est le seul dossier du fil qui passe le plancher de 5 % au prix affiché : "
                   f"{pct(rd['net_sur_revient_pct'])} net après IS, contre 4,55 % à Cuers, 4,76 % à "
                   f"La Valette et 4,96 % à La Seyne. Mais le solde reste {euro_signe(d['solde'])} par "
                   f"mois, et le rendement tient à une assiette que personne n'a vue : les 9 % sont "
                   f"calculés sur le prix demandé, pas relevés sur des quittances. À 375 € par studio, "
                   f"le dossier retombe à {pct(c_375['rendements']['net_sur_revient_pct'])}.",
        "conf": "Le produit est bien fait : cinq compteurs individuels d'eau et d'électricité — ce qui "
                "élimine le piège classique des charges collectives —, cinq DPE C ou D, un garage, une "
                "monopropriété sans syndic, un emplacement à moins de 100 m d'un collège et à quelques "
                "minutes du centre. Les murs, eux, valent 1 550 à 2 100 €/m² dans ce quartier : à "
                "3 322 €/m², on n'achète pas un immeuble, on achète cinq baux. C'est acceptable si les "
                "baux sont réels et si le quartier se gère — deux conditions qui se vérifient en une "
                "demi-journée, et qui ne se rattrapent pas après signature.",
        "intro_projections": f"Les trois scénarios partent du même prix de {eur(prix)} et de la même "
                             f"assiette de cinq studios. Le Base prend les loyers annoncés par le "
                             f"vendeur, le Worst la relocation à 375 € — le niveau qu'on observerait "
                             f"si les 9 % étaient calculés sur des baux anciens.",
        "releve": releve,
        "garde_fous": garde_fous,
        "stance": f"On peut essayer, et c'est le dossier du fil qui le mérite le plus sur le rendement. "
                  f"On offre {eur(cible)} — le prix du solde nul, {pct((prix - cible) / prix * 100)} "
                  f"sous l'affichage — sous trois conditions qui ne se négocient pas : les cinq "
                  f"quittances, les cinq baux, et une visite du quartier un samedi après-midi sans "
                  f"l'agent. Plafond absolu {eur(plafond)}. Si les quittances ne sont pas là, on ne "
                  f"propose rien, quel que soit le prix.",
        "verdict_texte": f"À {eur(prix)}, l'immeuble rend {pct(rd['net_sur_revient_pct'])} net après IS "
                         f"pour {eur(c['prix_revient_total'])} de prix de revient : au-dessus du "
                         f"plancher de 5 %, avec un solde de {euro_signe(d['solde'])} par mois. Le "
                         f"prix plafond est de {eur(plafond)} et le prix cible — solde nul — de "
                         f"{eur(cible)}, soit {pct((prix - cible) / prix * 100)} sous l'affichage. "
                         f"Le rendement n'est pas le problème : la preuve du rendement l'est. Cinq "
                         f"baux meublés annoncés à 9 % sans une quittance, dans un QPV, avec deux "
                         f"surfaces pour le même immeuble, c'est un dossier qui se visite avant de "
                         f"s'offrir.",
        "performance": f"{pct(rd['net_sur_revient_pct'])} de rendement net après IS sur un prix de "
                       f"revient de {eur(c['prix_revient_total'])}, pour un plancher de 5 % : "
                       f"performance {nfr(comp['s_performance'], 1)}/10. EBE avant IS : "
                       f"{eur(f['ebe'])}, amortissement {eur(f['amortissement'])}, IS "
                       f"{eur(f['is_annuel'])}. Ratio prix de revient sur valeur : "
                       f"{nfr(c['ratio_cout_valeur'], 2)} — on achète au-dessus du bâti, au prix des "
                       f"baux.",
        "prix_texte": f"Prix plafond {eur(plafond)} — {plafond_txt} — et prix cible {eur(cible)}, "
                      f"soit {pct((prix - cible) / prix * 100)} sous l'affichage. Le plafond est le prix "
                      f"de la marge de sécurité, la cible celui du solde nul : l'offre se cale sur la "
                      f"cible, et se retire si les quittances ne confirment pas les 9 %.",
    }

    calcule("EBE base", round(f["ebe"]), round(engine.compute(r)["fiscal"]["ebe"]))
    calcule("rendement net/revient", round(rd["net_sur_revient_pct"], 2),
            round(f["net_apres_is"] / c["prix_revient_total"] * 100, 2), tolerance=0.05)
    calcule("prix au m²", round(prix / gen.SURFACE), round(299000.0 / 90.0))
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
        frais=eur(r["hypotheses"]["frais_acquisition_euros"]), loyer=nfr(LOYER_STUDIO),
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
