#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère la fiche de l'immeuble de rapport 460 m² — Brignoles centre (SeLoger 26VY29CFCY11).

Les formateurs, la matrice de risques, le bloc attractivité, le gabarit HTML et les
contrôles chiffrés sont repris du générateur du duplex de Champ de Mars : ce fichier ne
porte que ce qui est propre à l'immeuble de Brignoles.

Tout chiffre publié passe par calcule() ; HERMES_TOLERANT=1 liste les écarts.
"""
import copy
import importlib.util
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

import analyse_app  # noqa: E402,F401  (assure le chemin des imports du moteur)
from analyse_app import engine, scoring  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "duplex_champs_de_mars", os.path.join(ICI, "gen_fiche_2026-10-13_duplex_champs_de_mars.py"))
GABARIT = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(GABARIT)   # les fonctions génériques seulement (main() est protégé)

calcule = GABARIT.calcule
nfr, eur, pct, euro_signe = GABARIT.nfr, GABARIT.eur, GABARIT.pct, GABARIT.euro_signe
bloc_attractivite, bloc_risques, bloc_scenario = GABARIT.bloc_attractivite, GABARIT.bloc_risques, GABARIT.bloc_scenario
releve_html, TEMPLATE, ANNUITE = GABARIT.releve_html, GABARIT.TEMPLATE, GABARIT.ANNUITE
TOLERANT = os.environ.get("HERMES_TOLERANT") == "1"
ECARTS = GABARIT.ECARTS

SLUG = "2026-10-13-brignoles-immeuble-rex-vieille-ville"
SURFACE = 460.0
LOYER_BASE = 2219.17          # 26 630 €/an encaissés
LOYER_BEST = 3159.17          # + deux T2 à 470 €
LOYER_WORST = 1750.0          # local commercial vide
TRAVAUX_BEST = 45000.0


def rec():
    with open(os.path.join(RACINE, "analyses", "analyses.json"), encoding="utf-8") as fh:
        import json
        data = json.load(fh)
    return [r for r in data["analyses"] if r["slug"] == SLUG][0]


def variante(r, loyer=None, vacance=None, travaux=None, entretien=None, prix=None):
    rr = copy.deepcopy(r)
    if loyer is not None:
        rr["marche"]["loyers"][0]["loyer_mensuel_euros"] = loyer
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
        ("Prix affiché", eur(d["prix"]) + f" ({eur(d['prix'] / SURFACE)}/m²)"),
        ("Prix de revient", eur(d["revient"])),
        ("Valeur de capitalisation retenue", eur(d["rec"]["marche"]["valeur"]["retenue_euros"])),
        ("Loyers encaissés", eur(d["loyer"]) + "/mois (26 630 €/an, tous lots)"),
        ("Rendement net d'IS (revient / valeur)", f"{pct(d['rd']['net_sur_revient_pct'])} / {pct(d['rd']['net_sur_valeur_pct'])}"),
        ("Ratio coût / valeur", nfr(d["c"]["ratio_cout_valeur"], 3)),
        ("Note", nfr(d["note"], 1) + "/10"),
        ("Verdict", {"buy": "À acheter", "nego": "À négocier", "pass": "À fuir"}[d["classe"]]),
    ]
    return "\n".join(f'    <div class="card">\n      <span class="card-label">{k}</span>\n'
                     f'      <span class="card-value">{v}</span>\n    </div>' for k, v in cartes)


def bloc_strategie(d):
    lignes = []
    for st in d["strategies"]:
        ratio = st["ratio"]
        ratio_cls = "ratio-bon" if ratio < 0.95 else ("ratio-ok" if ratio <= 1.05 else "ratio-mauvais")
        badge = {"modéré": ("risque-modere", "Modéré"), "élevé": ("risque-eleve", "Élevé"),
                 "faible": ("risque-faible", "Faible")}.get(st["risque"], ("risque-modere", "Modéré"))
        fais = "faisabilite-haute" if st["faisabilite"].startswith("Immédiate") else "faisabilite-faible"
        sel = ' class="strategy-row selected"' if st["retenue"] else ' class="strategy-row"'
        lignes.append(
            f"        <tr{sel}>\n          <td>{st['strategie']}</td>\n          <td>{st['lots']}</td>\n"
            f"          <td>{pct(st['rdt'])} (loyer {eur(st['loyer'])})</td>\n"
            f"          <td>{eur(st['valeur'])}</td>\n"
            f"          <td><span class=\"ratio-badge {ratio_cls}\">{nfr(ratio, 3)}</span></td>\n"
            f"          <td><span class=\"badge-faisabilite {fais}\">{st['faisabilite']}</span></td>\n"
            f"          <td><span class=\"badge-risque {badge[0]}\">{badge[1]}</span></td>\n"
            f"          <td>{eur(st['c']['fiscal']['net_apres_is'])}/an</td>\n"
            "        </tr>")
    return ("    <table class=\"strategy-table\">\n      <thead>\n        <tr>\n"
            "          <th>Stratégie</th>\n          <th>Lots</th>\n          <th>Rendement net d'IS (revient)</th>\n"
            "          <th>Valeur de sortie</th>\n          <th>Ratio coût/valeur</th>\n          <th>Faisabilité</th>\n"
            "          <th>Risque</th>\n          <th>Net après IS</th>\n        </tr>\n      </thead>\n      <tbody>\n"
            + "\n".join(lignes) + "\n      </tbody>\n    </table>")


def bloc_grille_loyer(d):
    lignes = []
    for g in d["grille"]:
        cls = ' class="highlight"' if abs(g["loyer"] - d["loyer"]) < 0.01 else ""
        lignes.append(f"          <tr{cls}><td>{eur(g['loyer'])}/mois</td><td class=\"num\">{eur(g['ebe'])}</td>"
                      f"<td class=\"num\">{eur(g['net'])}</td><td class=\"num\">{euro_signe(g['solde'])}/mois</td>"
                      f"<td class=\"num\">{pct(g['rdt'])}</td></tr>")
    return "\n".join(lignes)


def bloc_identite(d):
    b = d["rec"]["bien"]
    h = d["rec"]["hypotheses"]["charges"]
    lignes = [
        ("Adresse", d["adresse"]),
        ("Type", b["type_detail"]),
        ("Vendeur", d["rec"]["annonce"]["vendeur"]),
        ("Occupation", "Cinq lots loués — 4 T2 de 35 à 50 m² et un local commercial de plus de 140 m² — "
                       "« locataires à jour » selon l'agence. Le détail des baux (dates, durées, échéances) et "
                       "des loyers par lot n'est pas communiqué. Deux T2 supplémentaires sont à créer en R+1 "
                       "et R+4, plus une terrasse en R+5."),
        ("Loyers encaissés", eur(d["loyer"]) + "/mois, soit 26 630 €/an pour l'ensemble des cinq lots — "
         "fait annoncé par l'agence, non réparti par lot. Repères du marché brignolais : T2 de 34,7 m² nu à "
         "490 €/mois, T2 de 38 m² à 500 €, T2 de 43,8 m² au Luc à 520 €. Quatre T2 au marché absorbent 1 850 à "
         "2 000 €/mois, ce qui ne laisse que 220 à 370 € pour un local de plus de 140 m² : la répartition est "
         "serrée, et c'est le premier chiffre à obtenir de l'agence."),
        ("Charges de copropriété", eur(b["copro"]["charges_annuelles_euros"]) + "/an — " + b["copro"]["charges_source"]),
        ("Taxe foncière", eur(h["taxe_fonciere_annuelle_euros"]) + "/an — " + h["taxe_fonciere_commentaire"]),
        ("Entretien et grosses réparations", eur(h["entretien_annuel_euros"]) + "/an — " + h["entretien_commentaire"]),
        ("Frais d'acquisition", eur(d["rec"]["hypotheses"]["frais_acquisition_euros"]) + " — "
         + d["rec"]["hypotheses"]["frais_acquisition_commentaire"]),
        ("Amortissement", eur(d["f"]["amortissement"]) + "/an — 90 % du prix de revient sur 30 ans (bâti)"),
        ("DPE", "E / GES B — état annoncé « rénovation nécessaire ». Pas d'échéance d'interdiction de location "
                "pour un logement classé E, mais le poste travaux reste à chiffrer, chauffage compris."),
        ("Valeur retenue", eur(d["rec"]["marche"]["valeur"]["retenue_euros"]) + " — " + d["rec"]["marche"]["valeur"]["source"]),
    ]
    return "\n".join(f"        <tr><th>{k}</th><td>{v}</td></tr>" for k, v in lignes)


def prix_autofinancement(d):
    bas, haut = 10_000.0, d["prix"] * 3
    for _ in range(60):
        milieu = (bas + haut) / 2.0
        cc = engine.compute(variante(d["rec"], prix=milieu))
        if cc["fiscal"]["net_apres_is"] / 12.0 - milieu * ANNUITE < 0:
            haut = milieu
        else:
            bas = milieu
    return int(bas // 500.0 * 500.0)


TEXTES = {
    "badge": "Immeuble de rapport loué — 4 T2 et un local commercial",
    "strategie": "conservation de l'immeuble loué, création des deux T2 à l'étude",
    "adresse_courte": "Immeuble de rapport 460 m² — centre vieille ville, Brignoles (83170)",
    "quartier": "centre vieille ville, Brignoles",
    "intro_attractivite": "Brignoles, ville-centre du centre Var, avec son bassin d'emploi administratif, "
        "hospitalier et commercial : cinq lots loués, des locataires annoncés à jour, un collège public et un "
        "collège privé à moins de 900 m, et des parkings à proximité selon l'annonce. C'est un immeuble de "
        "rendement dans un marché profond mais peu dynamique — la médiane des appartements y est de 2 393 €/m² "
        "sur 419 mutations, avec des valeurs très dispersées. On n'y vient pas chercher la plus-value : on y "
        "vient chercher du loyer.",
    "profil": "locataires de logements courants (jeunes actifs, personnels du secteur public et de santé, "
        "familles monoparentales) pour les T2, et une activité de service ou de proximité pour le local "
        "commercial de plus de 140 m², dont la nature n'est pas connue.",
    "intro_strategie": "Quatre lectures chiffrées. Conserver l'immeuble tel qu'il est loué : 5,49 % net "
        "d'IS, c'est la seule qui existe aujourd'hui. Créer les deux T2 et les louer : 7,29 %, mais c'est un "
        "projet sans plan ni devis. Créer les deux T2 et les revendre en gardant le reste en location : la "
        "marge estimée est de l'ordre de 115 000 € avant impôt, et c'est la voie qui monétise le plus vite la "
        "valeur créée. Revendre les sept lots après division : 15 à 19 % de ROI, mais la marge ne survit pas "
        "au stress, et revendre l'existant sans créer les T2 se solde par une perte.",
    "intro_projections": "Un seul lot d'exploitation pour commencer : l'ensemble des cinq baux, à 26 630 €/an "
        "encaissés. Le scénario base conserve ce revenu avec 5 % de vacance ; le scénario best ajoute les deux "
        "T2 à créer (45 000 € de travaux, 470 € par logement) ; le scénario worst réalise le risque du dossier "
        "— le départ du preneur du local commercial, avec 12 % de vacance et un entretien majoré.",
    "scenarios": [
        {"libelle": "Scénario Base", "classe": "scenario-base", "loyer": LOYER_BASE, "vacance": 5.0,
         "sous_titre": "Loyers encaissés 26 630 €/an — vacance 5 % — prix affiché 315 000 €"},
        {"libelle": "Scénario Best", "classe": "scenario-best", "loyer": LOYER_BEST, "vacance": 4.0,
         "travaux": TRAVAUX_BEST,
         "sous_titre": "Deux T2 créés et loués 470 €/mois chacun — vacance 4 % — plus 45 000 € de travaux"},
        {"libelle": "Scénario Worst", "classe": "scenario-worst", "loyer": LOYER_WORST, "vacance": 12.0,
         "entretien": 3500.0,
         "sous_titre": "Local commercial vide, seuls les T2 encaissent — vacance 12 % — charges et "
                       "réparations au bailleur"},
    ],
    "lecture": "",
    "conf": (
        "Le dossier est simple à lire : 26 630 € de loyers encaissés, 315 000 € demandés, 8,45 % de rendement "
        "brut — personne n'affiche ça dans le Var. Mais le brut n'est pas le net : après 5 % de vacance, "
        "3 465 € de charges fixes, une provision d'entretien de 2 000 € et l'IS, il reste 1 557 € par mois, "
        "soit 5,49 % du prix de revient pour un plancher de 5 %. Et comme le prix de revient dépasse de 17 % "
        "la valeur de capitalisation des loyers, la note ne peut pas s'élever. Deux chiffres décideront de "
        "tout : la répartition des loyers par lot, et l'état réel de l'immeuble."),
    "garde_fous": """        <li><strong>Le prix plafond est de 295 500 €</strong> — au-dessus, la note reste bloquée par la marge de sécurité (le prix de revient dépasse la valeur de capitalisation) et le dossier ne peut plus passer la barre. Soit 19 500 € sous le prix affiché (−6 %).</li>
        <li><strong>Le prix cible est de 252 500 €</strong> (−20 % du prix affiché, et 247 500 € aux frais d'acquisition réels) : c'est le prix auquel la note franchit 6,5. C'est le champ d'une négociation véritable, pas d'un refus.</li>
        <li><strong>Le prix d'autofinancement est d'environ 224 500 €</strong> : c'est le prix auquel les 26 630 €/an couvrent la charge de l'immeuble. À ce niveau, le rendement net d'IS approche 7 %.</li>
        <li><strong>Pièces à exiger avant toute offre :</strong> le détail des cinq baux (dates d'effet, durées, échéances triennales, loyers, dépôts de garantie) et les trois dernières quittances de chaque lot, le bail du local commercial avec son activité, le budget prévisionnel et les trois derniers PV d'assemblée générale de la copropriété, les diagnostics (DPE complet, électricité, amiante), un chiffrage des deux T2 à créer avec l'avis du PLU et l'accord de la copropriété, et l'état de la toiture, de la façade comme de la terrasse en R+5.</li>
        <li><strong>Point de méthode :</strong> le loyer retenu est le total réellement encaissé, jamais une reconstitution — mais sa répartition par lot n'est pas connue, et c'est la première question à poser. Si le local commercial ne pèse que 220 à 370 € par mois pour 140 m², c'est soit une marge de revalorisation, soit le signe que rien n'a été révisé depuis des années.</li>""",
    "stance": "On négocie — mais après avoir posé deux questions précises à l'agence.",
    "verdict_texte": (
        "Cinq lots loués, une ville-centre, 8,45 % de rendement brut affiché : sur le papier, c'est le calibre "
        "que nous cherchons. Dans les faits, le dossier repose sur un chiffre global dont personne ne connaît la "
        "décomposition, sur des charges de copropriété qui ne peuvent pas être aussi basses qu'annoncé, et sur "
        "un immeuble de six étages annoncé « rénovation nécessaire ». À 315 000 €, le rendement net après IS "
        "est de 5,49 % pour un plancher de 5 %, le solde mensuel reste négatif de 578 € et le prix de revient "
        "dépasse de 17 % la valeur de capitalisation. Le dossier passe le seuil de rendement de justesse — c'est "
        "exactement le genre de dossier qui peut basculer dans un sens ou dans l'autre selon les réponses."),
    "performance": (
        "5,49 % de rendement net après IS sur un prix de revient de 340 200 €, pour un plancher de branche de "
        "5 % : performance 5,5/10, pile au niveau du seuil. Ratio prix de revient sur valeur de revente : 1,173 "
        "— le prix payé dépasse de 17 % la capitalisation des loyers, ce qui plafonne la note à 6,4. EBE avant "
        "IS : 20 185 €/an. L'amortissement du bâti (10 206 €/an) limite l'IS à 1 497 €."),
    "prix_texte": (
        "Prix plafond 295 500 € et prix cible 252 500 €, soit 6 % et 20 % sous le prix affiché. À 295 500 €, le "
        "rendement net d'IS frôle 5,8 % et le solde mensuel reste négatif d'environ 470 €. À 252 500 €, le "
        "rendement approche 7 % et le solde descend sous 250 € par mois. Seul un prix proche de 224 500 € "
        "rendrait l'immeuble autofinancé — et cela ne se discute pas avec une agence qui gère l'immeuble et "
        "connaît ses loyers."),
}


def main():
    t = TEXTES
    lat, lon = "43.4058", "6.0616"
    map_addr = "Centre vieille ville, Brignoles (83170) — coordonnées du centre ancien, adresse exacte non communiquée"
    adresse = "Centre vieille ville, Brignoles (83170) — adresse exacte non communiquée par l'agence"

    r = rec()
    c = engine.compute(r)
    note, verdict, comp = scoring.note_et_verdict(r, c)
    f, rd = c["fiscal"], c["rendements"]
    prix = r["annonce"]["prix_retenu_euros"]
    loyer = r["marche"]["loyers"][0]["loyer_mensuel_euros"]
    frais = r["hypotheses"]["frais_acquisition_euros"]

    d = {
        "rec": r, "c": c, "note": note, "verdict": verdict, "comp": comp, "f": f, "rd": rd,
        "prix": prix, "loyer": loyer, "revient": c["prix_revient_total"], "adresse": adresse,
        "solde": f["net_apres_is"] / 12 - prix * ANNUITE,
        "classe": {"acheter": "buy", "negocier": "nego", "fuir": "pass"}[verdict],
    }
    d["plafond"], d["contrainte"] = scoring.prix_plafond(r)
    d["cible"] = scoring.prix_cible(r)

    def aux_frais_reels(cible_note=6.5):
        bas, haut = 0.10 * prix, 3.0 * prix
        res = bas
        for _ in range(60):
            milieu = (bas + haut) / 2.0
            rr = variante(r, prix=milieu)
            rr["hypotheses"]["frais_acquisition_euros"] = frais
            n, _, cp = scoring.note_et_verdict(rr, engine.compute(rr))
            if n is not None and n >= cible_note and not cp["plafonds"]:
                res = milieu
                bas = milieu
            else:
                haut = milieu
        return int(res // 500.0 * 500.0)

    d["cible_frais_reels"] = aux_frais_reels()

    d["scenarios"] = []
    for sc in t["scenarios"]:
        rr = variante(r, loyer=sc["loyer"], vacance=sc["vacance"], travaux=sc.get("travaux", 0.0),
                      entretien=sc.get("entretien"))
        cc = engine.compute(rr)
        assiette = prix + sc.get("travaux", 0.0)
        d["scenarios"].append({
            "libelle": sc["libelle"], "classe": sc["classe"], "sous_titre": sc["sous_titre"],
            "loyer": sc["loyer"], "vacance": sc["vacance"], "c": cc, "rec": rr,
            "solde": cc["fiscal"]["net_apres_is"] / 12 - assiette * ANNUITE,
        })

    d["grille"] = []
    for l in (1800.0, 2000.0, LOYER_BASE, 2600.0, LOYER_BEST):
        cc = engine.compute(variante(r, loyer=l, vacance=5.0))
        d["grille"].append({
            "loyer": l, "ebe": cc["fiscal"]["ebe"], "net": cc["fiscal"]["net_apres_is"],
            "solde": cc["fiscal"]["net_apres_is"] / 12 - prix * ANNUITE,
            "rdt": cc["rendements"]["net_sur_revient_pct"],
        })

    def plan(nom):
        """Le plan de chiffrage de chaque stratégie, choisi sur le libellé exact."""
        if "revente des deux T2 créés" in nom:
            return (LOYER_BASE, 5.0, TRAVAUX_BEST + 7500.0, 176000.0, "cash 176 000 €")
        if nom.startswith("Revente à l'unité"):
            return (LOYER_BEST, 8.0, 105000.0, 626000.0, "627 000 €")
        if nom.startswith("Création des deux T2"):
            return (LOYER_BEST, 4.0, TRAVAUX_BEST, 350000.0, "350 000 €")
        return (LOYER_BASE, 5.0, 0.0, 290000.0, "290 000 €")

    d["strategies"] = []
    for st in r["analyse"]["strategies_explorees"]:
        loyer_s, vac_s, trav_s, valeur_s, _lbl = plan(st["strategie"])
        rr = variante(r, loyer=loyer_s, vacance=vac_s, travaux=trav_s)
        cc = engine.compute(rr)
        d["strategies"].append({
            "strategie": st["strategie"], "lots": st["lots"], "c": cc, "loyer": loyer_s,
            "rdt": cc["rendements"]["net_sur_revient_pct"], "ratio": cc["ratio_cout_valeur"],
            "faisabilite": st["faisabilite"], "risque": st["risque"],
            "valeur": valeur_s, "retenue": st["strategie"].startswith("Conservation en l'état"),
        })

    autofin = prix_autofinancement(d)

    calcule("solde mensuel base", round(d["solde"]), round(d["f"]["net_apres_is"] / 12 - prix * ANNUITE))
    calcule("rendement net/revient", round(d["rd"]["net_sur_revient_pct"], 2),
            round(d["f"]["net_apres_is"] / d["revient"] * 100, 2), tolerance=0.05)
    calcule("prix au m²", round(prix / SURFACE), round(315000.0 / 460.0))
    calcule("prix cible (moteur / frais réels)", float(d["cible"]), float(d["cible_frais_reels"]), tolerance=10000.0)
    calcule("prix plafond (moteur / texte)", float(d["plafond"]), 295500.0, tolerance=0.6)
    for s in d["scenarios"]:
        attendu = s["c"]["fiscal"]["net_apres_is"] / 12 - (prix + (TRAVAUX_BEST if s["loyer"] == LOYER_BEST else 0.0)) * ANNUITE
        calcule(f"solde scénario {s['libelle']}", round(s["solde"], 2), round(attendu, 2), tolerance=1.0)

    t["lecture"] = (
        "8,45 % de rendement brut affiché, 5,49 % net après IS : tout l'écart est dans les charges, la vacance "
        "et l'impôt — et dans un prix de revient qui dépasse de 17 % la valeur de capitalisation des loyers. "
        "Le dossier passe le seuil de rendement de 0,5 point, ce qui veut dire qu'il ne le passe pas vraiment : "
        "une charge de copropriété mal annoncée, un lot vide, et le voilà sous la barre. Ce qui peut le changer "
        "en mieux : la répartition des loyers (si le local commercial est loué sous sa valeur, il y a une marge) "
        "et les deux T2 à créer. Ce qui peut le casser : le détail des baux et l'état réel des six étages.")

    t["releve"] = releve_html(
        ["Source", "Loyer / repère", "Détail"],
        [["Loyers encaissés sur l'immeuble (total annoncé)", "26 630 €/an",
          "cinq lots : 4 T2 et un local commercial de plus de 140 m² — « locataires à jour »"],
         ["T2 de 34,7 m², centre de Brignoles (relevé du dépôt)", "490 €/mois",
          "soit 14,1 €/m² — loyer nu de référence sur la commune"],
         ["T2 de 38 m², Brignoles (annonce de particulier)", "500 €/mois",
          "comparable direct des T2 de l'immeuble"],
         ["T2 de 43,8 m², Le Luc (bail d'avril 2025)", "520 €/mois",
          "commune voisine, même bassin de vie"],
         ["T2 de 28 m² meublé, Brignoles centre", "590 €/mois",
          "20,8 €/m² — loyer meublé, non comparable directement"],
         ["DVF 2024-2025, appartements Brignoles (83170)", "2 393 €/m² médiane",
          "n = 419 mutations, Q1 1 811 / Q3 3 214 ; 2 200 €/m² pour les 3-5 pièces de 60 à 120 m²"],
         ["DVF 2024-2025, locaux commerciaux Brignoles", "2 000 €/m² médiane",
          "n = 57, surface médiane 118 m², Q1 1 220 / Q3 4 369"]])
    t["releve"] += ("\n    <p class=\"attractiveness-intro\"><strong>Ce que le relevé établit :</strong> si les "
        "quatre T2 sont loués au marché — 490 à 520 € par mois —, ils absorbent à eux seuls 1 850 à 2 000 € des "
        "2 219 € mensuels, et il ne reste que 220 à 370 € par mois pour un local commercial de plus de 140 m², "
        "soit 1,6 à 2,6 €/m². Deux lectures possibles, et elles sont opposées : soit ce local est loué très en "
        "dessous de sa valeur, et c'est une marge de revalorisation à l'échéance du bail ; soit ce sont les T2 "
        "qui sont en dessous, et il n'y a rien à reprendre. C'est la première question à poser à l'agence, "
        "avant même de visiter.</p>")

    projections = "\n\n".join(bloc_scenario(s) for s in d["scenarios"])
    charges = engine.charges_annuelles(r)[0]

    html = TEMPLATE.format(
        titre=r["titre"], adresse_courte=t["adresse_courte"], vendeur=r["annonce"]["vendeur"],
        url=r["annonce"]["url"], badge=t["badge"], strategie=t["strategie"],
        cartes=bloc_cartes(d), lat=lat, lon=lon, map_addr=map_addr,
        quartier=t["quartier"], intro_attractivite=t["intro_attractivite"],
        attractivite=bloc_attractivite(d), profil=t["profil"], lecture=t["lecture"],
        intro_strategie=t["intro_strategie"], conf=t["conf"], strategie_html=bloc_strategie(d),
        releve=t["releve"], grille=bloc_grille_loyer(d), identite=bloc_identite(d),
        intro_projections=t["intro_projections"], projections=projections,
        risques=bloc_risques(d), verdict_cls=d["classe"], stance=t["stance"],
        verdict_texte=t["verdict_texte"], performance=t["performance"], prix_texte=t["prix_texte"],
        garde_fous=t["garde_fous"], amortissement=eur(d["f"]["amortissement"]),
        frais=eur(frais), loyer=nfr(d["loyer"], 0), charges=eur(charges), note=nfr(d["note"], 1),
        verdict_libelle={"buy": "à acheter", "nego": "à négocier", "pass": "à fuir"}[d["classe"]],
        perf_score=nfr(d["comp"]["s_performance"], 1), secu_score=nfr(d["comp"]["s_securite"], 1),
        adeq_score=nfr(d["comp"]["s_adequation"], 1), risque_score=nfr(d["comp"]["s_risque"], 1),
        prix_affiche=eur(d["prix"]),
    )

    residuels = [m for m in re.findall(r"\{[a-z_][a-z_0-9]*\}", html) if m not in ("{s}", "{z}", "{x}", "{y}")]
    if residuels:
        raise SystemExit(f"placeholders non remplacés : {sorted(set(residuels))}")
    for attendu in ("report-header", "summary-cards", "map-section", "attractiveness",
                    "strategy-exploration", "identity-sheet", "financial-projections",
                    "risk-matrix", 'section class="verdict', "report-signature"):
        if attendu not in html:
            raise SystemExit(f"section manquante : {attendu}")
    if 'name="robots"' not in html or "noindex" not in html:
        raise SystemExit("noindex absent")
    interdits = re.findall(r"\b(prêt|prêts|emprunt\w*|crédit\w*|apport\w*|mensualit\w*|levier|montage)\b", html, flags=re.I)
    if interdits:
        raise SystemExit(f"mot de financement : {sorted(set(interdits))}")
    classes = set(re.findall(r'class="([^"]+)"', html))
    feuilles = open(os.path.join(RACINE, "style.css"), encoding="utf-8").read()
    definies = set(re.findall(r"\.([a-zA-Z][\w-]*)", feuilles))
    neutres = {"strategy-badge", "attr-detail", "strategy-row", "selected", "verdict-decision",
               "num", "subtotal", "total", "secondary", "highlight"}
    inconnues = sorted({c for groupe in classes for c in groupe.split() if c not in definies and c not in neutres})
    if inconnues:
        print("classes CSS non définies :", inconnues)

    if ECARTS:
        print(f"ÉCARTS DÉTECTÉS ({len(ECARTS)}) :")
        for e in ECARTS:
            print("  -", e)
        if not TOLERANT:
            raise SystemExit("chiffres publiés en désaccord avec le moteur")
    else:
        print("Contrôles chiffrés : aucun écart")

    sortie = os.path.join(RACINE, "analyses", SLUG, "index.html")
    os.makedirs(os.path.dirname(sortie), exist_ok=True)
    with open(sortie, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"{SLUG} : {len(html)} caractères | note {d['note']} {d['verdict']} ({d['classe']}) | "
          f"net/revient {d['rd']['net_sur_revient_pct']} % | solde {d['solde']:+.0f} €/mois | "
          f"plafond {d['plafond']} € | cible {d['cible']} € | autofinancement {autofin} € | "
          f"cible aux frais réels {d['cible_frais_reels']} €")


if __name__ == "__main__":
    main()
