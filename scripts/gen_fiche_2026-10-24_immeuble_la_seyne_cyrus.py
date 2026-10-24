#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère la fiche de l'immeuble mixte rue Cyrus Hugues — La Seyne-sur-Mer (83500).

analyses/2026-10-24-immeuble-mixte-cyrus-hugues-la-seyne/index.html — SeLoger 267PVVC94GXQ
(Agence Papazian-Chovelon Porte Marine, réf. 38035).

Gabarit et contrôles repris du générateur de l'immeuble de La Valette.
Convention de solde : frais d'acquisition comptants, 90 % du prix porté sur vingt ans
à 3,80 %, assurance comprise. Prix cible = solde nul, jamais le prix d'une note.
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
gen.SLUG = "2026-10-24-immeuble-mixte-cyrus-hugues-la-seyne"
gen.SURFACE = 147.0
ANNUITE = 0.9 * (0.038 / 12) / (1 - (1 + 0.038 / 12) ** -240) + 0.9 * 0.0034 / 12
eur, nfr, pct, euro_signe = gen.eur, gen.nfr, gen.pct, gen.euro_signe
calcule = gen.calcule
releve_html = gen.releve_html

PRIX = 245000.0
TRAVAUX = 0.0
VALEUR = 225000.0
LOYER_LOGEMENT = 1050.0
LOYER_COMMERCE = 650.0
LOYER_TOTAL = LOYER_LOGEMENT + LOYER_COMMERCE
TF = 2034.0
ENTRETIEN = 2336.0


def prix_cf_nul(lo=50000.0, hi=None):
    hi = hi or PRIX * 1.2

    def solde(p):
        rr = variante(rec(), prix=p)
        cc = engine.compute(rr)
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
     "Sensibilité au prix d'achat — loyers estimés {loyer} €/mois pour le logement, 650 € pour le local"),
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
        rr["hypotheses"]["frais_acquisition_euros"] = round(prix * 0.08)
    return rr


def bloc_cartes(d):
    cartes = [
        ("Prix affiché", eur(d["prix"]) + f" ({eur(d['prix'] / gen.SURFACE)}/m² annoncés)"),
        ("Prix de revient", eur(d["revient"])),
        ("Valeur retenue (niveau de la rue)", eur(VALEUR)),
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
        ("Occupation", "Local commercial « actuellement exploité en boucherie-charcuterie » et "
                       "logement à l'étage. L'annonce ne dit pas si le local est loué ou exploité par "
                       "le vendeur, ne donne ni loyer, ni bail, ni date : c'est l'inconnue majeure du "
                       "dossier"),
        ("Loyers retenus", f"{eur(LOYER_LOGEMENT)}/mois pour le logement (11,4 €/m² sur 92 m²) et "
                           f"{eur(LOYER_COMMERCE)}/mois pour le local (11,8 €/m² sur 55 m²), soit "
                           f"{eur(LOYER_TOTAL)} — ESTIMÉS au marché du 24/10/2026, à confirmer avec "
                           f"les deux baux"),
        ("Charges de copropriété", "Aucune — immeuble en monopropriété, pas de syndic"),
        ("Taxe foncière", eur(h["taxe_fonciere_annuelle_euros"]) + "/an — "
         + h["taxe_fonciere_commentaire"]),
        ("Entretien et gestion", eur(h["entretien_annuel_euros"]) + "/an — "
         + h["entretien_commentaire"]),
        ("Frais d'acquisition", eur(d["rec"]["hypotheses"]["frais_acquisition_euros"]) + " — "
         + d["rec"]["hypotheses"]["frais_acquisition_commentaire"]),
        ("Amortissement", eur(d["f"]["amortissement"]) + "/an — 90 % du prix de revient sur 30 ans"),
        ("DPE / GES", "D / B — aucun calendrier d'interdiction de louer avant 2034. Le risque du "
                      "dossier n'est pas énergétique, il est locatif et commercial"),
        ("Surface", "147 m² annoncés pour l'ensemble, sans ventilation entre le local et le "
                    "logement : répartition supposée 55 m² / 92 m², à faire mesurer"),
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

    c_local_vide = engine.compute(variante(r, loyer2=0.0))
    c_local_bas = engine.compute(variante(r, loyer2=450.0))
    c_haut = engine.compute(variante(r, loyer=1150.0, loyer2=750.0))
    revient_division = PRIX * 1.08 + 60000.0
    sortie_basse = 92 * 1571.0 + 55 * 1312.0
    sortie_haute = 92 * 2098.0 + 55 * 1586.0

    scenarios = []
    for sc in (
        {"libelle": "Scénario Base", "classe": "scenario-base", "loyer": LOYER_LOGEMENT,
         "loyer2": LOYER_COMMERCE, "vacance": 6.0, "travaux": TRAVAUX,
         "sous_titre": f"Logement {eur(LOYER_LOGEMENT)} et local {eur(LOYER_COMMERCE)} — vacance "
                       f"6 % (5 % habitation, 8 % commerce) — prix affiché {eur(prix)}"},
        {"libelle": "Scénario Best", "classe": "scenario-best", "loyer": 1150.0, "loyer2": 750.0,
         "vacance": 3.0, "travaux": TRAVAUX,
         "sous_titre": "Logement 1 150 € et local 750 € — vacance 3 % — les deux baux sont au-dessus "
                       "de l'estimation"},
        {"libelle": "Scénario Worst", "classe": "scenario-worst", "loyer": 950.0, "loyer2": 450.0,
         "vacance": 15.0, "travaux": 6000.0,
         "sous_titre": "Bail commercial ancien à 450 € — vacance 15 % (local vide six mois) — "
                       "6 000 € de travaux sur un bâti de 1930"},
    ):
        rr = variante(r, loyer=sc["loyer"], loyer2=sc["loyer2"], vacance=sc["vacance"],
                      travaux=sc["travaux"])
        cc = engine.compute(rr)
        assiette = prix + sc["travaux"]
        scenarios.append({"libelle": sc["libelle"], "classe": sc["classe"], "sous_titre": sc["sous_titre"],
                          "loyer": sc["loyer"] + sc["loyer2"], "vacance": sc["vacance"],
                          "travaux": sc["travaux"], "rec": rr, "c": cc,
                          "solde": cc["fiscal"]["net_apres_is"] / 12.0 - assiette * ANNUITE})

    grille = []
    for p in (PRIX, 230000.0, float(plafond), 210000.0, float(cible)):
        rr = variante(r, prix=p)
        cc = engine.compute(rr)
        grille.append({"prix": p, "ebe": cc["fiscal"]["ebe"], "net": cc["fiscal"]["net_apres_is"],
                       "solde": cc["fiscal"]["net_apres_is"] / 12.0 - (p + TRAVAUX) * ANNUITE,
                       "rdt": cc["rendements"]["net_sur_revient_pct"]})

    strategies = [
        {"strategie": "Conservation en bloc : logement loué nu et local commercial loué", "lots": 2,
         "rdt": rd["net_sur_revient_pct"], "loyer_label": "loyers estimés",
         "ratio": c["ratio_cout_valeur"], "valeur": VALEUR,
         "net_label": eur(f["net_apres_is"]) + "/an",
         "faisabilite": "Immédiate si les deux baux sont en cours", "risque": "modéré",
         "retenue": True},
        {"strategie": "Revente à la découpe après mise en état", "lots": 2, "rdt": None,
         "loyer_label": "opération de revente",
         "ratio": revient_division / sortie_haute, "valeur": sortie_haute,
         "net_label": euro_signe(sortie_haute - revient_division) + " de marge",
         "faisabilite": "Division en lots, portage 18 à 24 mois", "risque": "élevé",
         "retenue": False},
        {"strategie": "Transformation du local commercial en logement", "lots": 3, "rdt": None,
         "loyer_label": "gain de 100 €/mois",
         "ratio": (revient_division + 70000.0) / (VALEUR + 115000.0), "valeur": VALEUR + 115000.0,
         "net_label": "gain insuffisant",
         "faisabilite": "Changement de destination, PLU, servitude commerciale", "risque": "élevé",
         "retenue": False},
    ]

    adresse = "Rue Cyrus Hugues, centre-ville, La Seyne-sur-Mer (83500) — adresse exacte non communiquée"
    lat, lon = "43.1010", "5.8845"

    d = {"slug": gen.SLUG, "adresse": adresse, "rec": r, "c": c, "note": note, "verdict": verdict,
         "comp": comp, "f": f, "rd": rd, "prix": prix, "loyer": LOYER_LOGEMENT,
         "revient": c["prix_revient_total"], "solde": f["net_apres_is"] / 12.0 - (prix + TRAVAUX) * ANNUITE,
         "classe": {"acheter": "buy", "negocier": "nego", "fuir": "pass"}[verdict],
         "classe_note": scoring.classe_note(note), "plafond": plafond, "contrainte": contrainte,
         "cible": cible, "scenarios": scenarios, "grille": grille, "strategies": strategies}

    releve = releve_html(
        ["Source", "Chiffre", "Lecture"],
        [["DVF rue Cyrus Hugues, 326 m² en immeuble entier (4 appartements + local de 108 m²), "
          "2022", "340 000 €, soit 1 043 €/m²",
          "la mutation la plus comparable : un immeuble entier de la même rue, à 1 043 €/m²"],
         ["DVF rue Cyrus Hugues, 74 m² en deux appartements, 2024", "85 000 €, soit 1 149 €/m²",
          "deuxième point bas de la rue"],
         ["DVF rue Cyrus Hugues, 88 m² et dépendance, 2024", "138 210 €, soit 1 571 €/m²",
          "le haut réaliste de la rue sur un logement"],
         ["DVF rue Cyrus Hugues, 100 m² en deux appartements, 2021", "275 530 €, soit 2 755 €/m²",
          "seule mutation haute de la rue : elle ne suffit pas à faire un marché"],
         ["DVF La Seyne-sur-Mer, appartements 60-100 m²", "1 863 ventes 2021-2025 — médiane "
          "2 706 €/m², premier quartile 2 157, troisième 3 463",
          "le repère de la commune, pas celui de la rue : c'est le piège de ce dossier"],
         ["DVF La Seyne-sur-Mer, locaux commerciaux 30-120 m²", "133 ventes — médiane 1 586 €/m²",
          "la valeur d'un local de 55 m² tourne autour de 87 000 €"],
         ["Prix au m² par quartier — Centre Ville-Peyron", "2 098 €/m² (DVF par quartier IRIS)",
          "le quartier le moins cher de la commune, celui du bien"],
         ["Médiane DHUP 2025, La Seyne-sur-Mer", "14,8 €/m² (IC 95 % 11,5 à 19,2) — T4 de 85 m² à "
          "1 150 €", "le repère locatif communal"],
         ["Baux du centre-ville — T2 de 29 m² et T2 de 35 m²", "415 € et 510 €/mois",
          "14,3 à 14,6 €/m² : le niveau réel des baux en place dans le centre ancien"],
         ["Locations commerciales relevées — 72, 38, 70 et 65 m²", "600 €, 500 €, 1 200 € et "
          "1 300 €/mois", "8,3 à 13,2 €/m² : la fourchette du local commercial dans le quartier"],
         ["Loyers retenus", f"{eur(LOYER_LOGEMENT)} pour le logement, {eur(LOYER_COMMERCE)} pour le "
          "local", "estimations au marché, aucune des deux n'est documentée par un bail"],
         ["Rendement selon le loyer du local", f"{pct(c_local_vide['rendements']['net_sur_revient_pct'])} "
          f"local vide — {pct(c_local_bas['rendements']['net_sur_revient_pct'])} à 450 € — "
          f"{pct(rd['net_sur_revient_pct'])} à 650 €",
          "le local fait basculer le dossier de 2,6 % à 5 % : c'est la seule question à poser"]])

    garde_fous = f"""        <li><strong>Prix plafond : {eur(plafond)}</strong> (contrainte du moteur : {contrainte}), soit {pct((prix - plafond) / prix * 100)} sous le prix affiché. Au-delà, le dossier ne peut plus atteindre le plancher de 5 % ni tenir sa valeur.</li>
        <li><strong>Prix cible : {eur(cible)}</strong>, soit {pct((prix - cible) / prix * 100)} sous l'affichage — le prix auquel le solde mensuel tombe à zéro. C'est ce prix qui fixe une offre, jamais celui d'une note.</li>
        <li><strong>Le solde au prix affiché : {euro_signe(d['solde'])} par mois.</strong> Et le chiffre est instable : {euro_signe(c_local_bas['fiscal']['net_apres_is'] / 12.0 - prix * ANNUITE)} si le bail commercial est à 450 €, {euro_signe(c_local_vide['fiscal']['net_apres_is'] / 12.0 - prix * ANNUITE)} si le local est vide.</li>
        <li><strong>Le local est le dossier.</strong> À 650 €/mois, l'immeuble rend {pct(rd['net_sur_revient_pct'])} net après IS ; à 450 €, {pct(c_local_bas['rendements']['net_sur_revient_pct'])} ; vide, {pct(c_local_vide['rendements']['net_sur_revient_pct'])}. L'annonce dit « actuellement exploité en boucherie-charcuterie » sans préciser si c'est un bail ou le fonds du vendeur : la première question à poser, avant la visite.</li>
        <li><strong>La rue est bon marché, et le prix affiché n'y est pas une décote :</strong> 1 667 €/m² demandés contre 1 043 à 1 571 €/m² pour les immeubles et appartements de la même rue (DVF 2021-2025). C'est le repère de la rue qui compte, pas les 2 706 €/m² de la commune.</li>
        <li><strong>Pièces à exiger avant toute offre :</strong> le bail commercial (date, terme, loyer, charges, clause de renouvellement, décomposition 605/606) ou l'acte qui établit que le local est libre, le bail du logement et les quittances, la ventilation des surfaces et le Carrez, l'avis de taxe foncière (2 034 € annoncés), les DPE par lot, l'état de la toiture, de la façade et de l'électricité, et le règlement de copropriété s'il en existe un.</li>
        <li><strong>Point de méthode :</strong> aucun loyer, aucun travaux devisé, aucune surface par lot. Les chiffres publiés décrivent ce que le bien vaut <em>si</em> les deux baux sont au marché — pas ce qu'il rapporte aujourd'hui.</li>"""

    projections = "\n\n".join(gen.bloc_scenario(s) for s in scenarios)

    t = {
        "badge": "Dossier conditionnel : le local décide de tout",
        "strategie": "conservation en bloc, logement loué nu et local commercial loué",
        "adresse_courte": "Immeuble mixte commerce et habitation — La Seyne-sur-Mer (83500)",
        "quartier": "Centre-ville, La Seyne-sur-Mer",
        "intro_attractivite": "La Seyne-sur-Mer est la deuxième ville du Var, 64 000 habitants, "
                             "centre ancien à deux pas du port, réseau Mistral dense et gare de Toulon "
                             "à quinze minutes. Le marché est profond — plus de 1 100 transactions par "
                             "an — et les prix ont progressé de 5 % sur trois ans. Mais c'est aussi "
                             "15 % de chômage, deux quartiers prioritaires et un centre ancien "
                             "hétérogène : la rue fait le dossier.",
        "profil": "un couple ou une petite famille pour le logement de trois pièces, et un commerçant "
                  "de proximité pour le local. Deux clientèles différentes, deux baux, deux risques : "
                  "c'est la nature du produit mixte.",
        "intro_strategie": "Trois lectures : la conservation en bloc avec les deux baux, la revente à "
                          "la découpe après mise en état, et la transformation du local en logement. "
                          "Les deux dernières ne tiennent pas les chiffres, et c'est le loyer du local "
                          "qui décide de la première.",
        "lecture": f"Le dossier se joue sur un seul chiffre, et il n'est pas dans l'annonce : le loyer "
                   f"du local commercial. À {eur(LOYER_COMMERCE)}/mois, l'immeuble rend "
                   f"{pct(rd['net_sur_revient_pct'])} net après IS pour {eur(c['prix_revient_total'])} "
                   f"de prix de revient ; à 450 €, il tombe à "
                   f"{pct(c_local_bas['rendements']['net_sur_revient_pct'])} ; local vide, à "
                   f"{pct(c_local_vide['rendements']['net_sur_revient_pct'])}. Le logement seul ne "
                   f"porte pas l'immeuble. Et le prix affiché — {eur(prix / gen.SURFACE)}/m² — est au "
                   f"haut de ce que la rue Cyrus Hugues a payé ces cinq dernières années.",
        "conf": "Ce qui plaide pour le bien : un emplacement de centre-ville à deux pas du port, un "
                "DPE D sans échéance, une climatisation, un local déjà en activité qui amène du "
                "passage, un logement de trois pièces sur deux niveaux qui se reloue, et une taxe "
                "foncière documentée à 2 034 €. Ce qui le disqualifie à ce prix : la rue elle-même. "
                "Un immeuble entier de 326 m² s'y est vendu 340 000 € en 2022, soit 1 043 €/m² ; ici "
                "on demande 1 667 €/m² pour 147 m² avec des travaux non chiffrés et des loyers "
                "inconnus. L'écart n'est pas une opportunité, c'est une question.",
        "intro_projections": f"Les trois scénarios partent du même prix de {eur(prix)} et de la même "
                             f"répartition supposée — logement de 92 m², local de 55 m². Seuls le "
                             f"niveau des baux et la vacance changent. Le Worst n'est pas théorique : "
                             f"un bail commercial signé il y a quinze ans à 450 € est la configuration "
                             f"la plus fréquente dans un centre ancien.",
        "releve": releve,
        "garde_fous": garde_fous,
        "stance": f"On ne propose pas {eur(prix)}. Le prix qui annule le solde est {eur(cible)}, soit "
                  f"{pct((prix - cible) / prix * 100)} sous l'affichage et sous la valeur de la rue : "
                  f"aucun vendeur ne signe à ce niveau. On demande donc les deux baux avant toute "
                  f"discussion ; si le local est loué 650 € et le logement 1 050 €, on offre "
                  f"{eur(plafond)}, pas au-delà. Sinon le dossier s'écarte.",
        "verdict_texte": f"À {eur(prix)}, l'immeuble rend {pct(rd['net_sur_revient_pct'])} net après "
                         f"IS pour {eur(c['prix_revient_total'])} de prix de revient, sous le "
                         f"plancher de 5 %, avec un solde de {euro_signe(d['solde'])} par mois. Le "
                         f"prix plafond est de {eur(plafond)} et le prix cible — solde nul — de "
                         f"{eur(cible)}, soit {pct((prix - cible) / prix * 100)} sous l'affichage. "
                         f"L'écart au plafond est modeste, mais l'incertitude sur le loyer du local "
                         f"vaut 200 à 650 €/mois, soit l'équivalent de 40 000 à 80 000 € de prix. "
                         f"C'est un dossier à instruire avant d'être un dossier à négocier.",
        "performance": f"{pct(rd['net_sur_revient_pct'])} de rendement net après IS sur un prix de "
                       f"revient de {eur(c['prix_revient_total'])}, pour un plancher de 5 % : "
                       f"performance {nfr(comp['s_performance'], 1)}/10. EBE avant IS : "
                       f"{eur(f['ebe'])}, amortissement {eur(f['amortissement'])}, IS "
                       f"{eur(f['is_annuel'])}. Ratio prix de revient sur valeur : "
                       f"{nfr(c['ratio_cout_valeur'], 2)} — on achète au-dessus du niveau de la rue.",
        "prix_texte": f"Prix plafond {eur(plafond)} et prix cible {eur(cible)}, soit "
                      f"{pct((prix - plafond) / prix * 100)} et {pct((prix - cible) / prix * 100)} sous "
                      f"l'affichage. Le plafond est le prix du rendement, la cible est celui du solde "
                      f"nul : les deux sont sous la valeur de la rue, ce qui dit le dossier mieux "
                      f"qu'un commentaire.",
    }

    calcule("EBE base", round(f["ebe"]), round(engine.compute(r)["fiscal"]["ebe"]))
    calcule("rendement net/revient", round(rd["net_sur_revient_pct"], 2),
            round(f["net_apres_is"] / c["prix_revient_total"] * 100, 2), tolerance=0.05)
    calcule("prix au m²", round(prix / gen.SURFACE), round(245000.0 / 147.0))
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
        frais=eur(r["hypotheses"]["frais_acquisition_euros"]), loyer=nfr(LOYER_LOGEMENT),
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
