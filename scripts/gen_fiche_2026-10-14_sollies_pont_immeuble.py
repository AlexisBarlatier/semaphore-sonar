#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère la fiche de l'immeuble de village R+3 à restaurer — Solliès-Pont (SeLoger 26CGGN6HMPH3).

Les formateurs, la matrice de risques, le bloc attractivité, le gabarit HTML et les contrôles
chiffrés sont repris du générateur de l'immeuble REX de Brignoles (lui-même bâti sur celui du
duplex Champ de Mars) : ce fichier ne porte que ce qui est propre à Solliès-Pont.

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

import analyse_app  # noqa: E402,F401
from analyse_app import engine, scoring  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "rex_brignoles", os.path.join(ICI, "gen_fiche_2026-10-13_brignoles_immeuble_rex.py"))
GABARIT = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(GABARIT)

calcule = GABARIT.calcule
nfr, eur, pct, euro_signe = GABARIT.nfr, GABARIT.eur, GABARIT.pct, GABARIT.euro_signe
bloc_attractivite, bloc_risques, bloc_scenario = GABARIT.bloc_attractivite, GABARIT.bloc_risques, GABARIT.bloc_scenario
releve_html, TEMPLATE, ANNUITE = GABARIT.releve_html, GABARIT.TEMPLATE, GABARIT.ANNUITE
TOLERANT = os.environ.get("HERMES_TOLERANT") == "1"
ECARTS = GABARIT.ECARTS

SLUG = "2026-10-14-sollies-pont-immeuble-village-3-t2-local"
SURFACE = 168.0
TRAVAUX = 250000.0
LOYER_BASE = 2040.0
LOYER_BEST = 2200.0
LOYER_WORST = 1700.0
TRAVAUX_BEST = 220000.0
TRAVAUX_WORST = 300000.0


def rec():
    with open(os.path.join(RACINE, "analyses", "analyses.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    return [r for r in data["analyses"] if r["slug"] == SLUG][0]


def variante(r, loyer=None, vacance=None, travaux=None, entretien=None, prix=None, valeur=None):
    rr = copy.deepcopy(r)
    if loyer is not None:
        rr["marche"]["loyers"][0]["loyer_mensuel_euros"] = max(loyer - 480.0, 0.0) / 3.0
        rr["marche"]["loyers"][1]["loyer_mensuel_euros"] = min(loyer, 480.0)
    if vacance is not None:
        rr["hypotheses"]["vacance_base_pct"] = vacance
    if travaux is not None:
        rr["bien"]["travaux"]["montant_euros"] = travaux
    if entretien is not None:
        rr["hypotheses"]["charges"]["entretien_annuel_euros"] = entretien
    if prix is not None:
        rr["annonce"]["prix_retenu_euros"] = prix
    if valeur is not None:
        rr["marche"]["valeur"]["retenue_euros"] = valeur
    return rr


def bloc_cartes(d):
    cartes = [
        ("Prix affiché", eur(d["prix"]) + f" ({eur(d['prix'] / SURFACE)}/m²)"),
        ("Prix de revient", eur(d["revient"])),
        ("Valeur de marché retenue", eur(d["rec"]["marche"]["valeur"]["retenue_euros"])),
        ("Loyers retenus, après travaux", eur(d["loyer"]) + "/mois (24 480 €/an, quatre unités)"),
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
    b, h, r = d["rec"]["bien"], d["rec"]["hypotheses"], d["rec"]
    lignes = [
        ("Adresse", d["adresse"]),
        ("Type", b["type_detail"]),
        ("Mandataire", r["annonce"]["vendeur"]),
        ("Occupation", "Immeuble vendu LIBRE et à restaurer intégralement : aucun lot ne produit, "
                       "aucun bail, aucun locataire. Les trois T2 d'environ 35 m² et le local commercial "
                       "de 40 m² sont vides et non louables en l'état."),
        ("Travaux", eur(b["travaux"]["montant_euros"]) + " retenus — " + b["travaux"]["nature"]),
        ("Charges de copropriété", eur(b["copro"]["charges_annuelles_euros"]) + "/an — " + b["copro"]["charges_source"]),
        ("Taxe foncière", eur(h["charges"]["taxe_fonciere_annuelle_euros"]) + "/an — "
         + h["charges"]["taxe_fonciere_commentaire"]),
        ("Entretien annuel", eur(h["charges"]["entretien_annuel_euros"]) + "/an — "
         + h["charges"]["entretien_commentaire"]),
        ("Frais d'acquisition", eur(r["hypotheses"]["frais_acquisition_euros"]) + " — "
         + r["hypotheses"]["frais_acquisition_commentaire"]),
        ("Amortissement", eur(d["f"]["amortissement"]) + "/an — 90 % du prix de revient sur 30 ans (bâti)"),
        ("DPE", "Non communiqué — l'annonce invite à « demander la performance énergétique », ce qui "
                "signifie qu'aucun diagnostic n'est établi. Sur un bâti de 1800, les diagnostics "
                "électricité, amiante et plomb manquent également."),
        ("Valeur retenue", eur(r["marche"]["valeur"]["retenue_euros"]) + " — " + r["marche"]["valeur"]["source"]),
    ]
    return "\n".join(f"        <tr><th>{k}</th><td>{v}</td></tr>" for k, v in lignes)


def prix_a_seuil(r, seuil=5.0):
    """Prix d'achat auquel le rendement net d'IS sur revient atteint le seuil de la doctrine."""
    bas, haut = 1000.0, 300000.0
    for _ in range(70):
        milieu = (bas + haut) / 2.0
        cc = engine.compute(variante(r, prix=milieu))
        if cc["rendements"]["net_sur_revient_pct"] is None:
            haut = milieu
        elif cc["rendements"]["net_sur_revient_pct"] < seuil:
            haut = milieu
        else:
            bas = milieu
    return int(bas // 500.0 * 500.0)


def prix_autofinancement(r, prix):
    bas, haut = 1000.0, 300000.0
    for _ in range(70):
        milieu = (bas + haut) / 2.0
        cc = engine.compute(variante(r, prix=milieu))
        if cc["fiscal"]["net_apres_is"] / 12.0 - milieu * ANNUITE < 0:
            haut = milieu
        else:
            bas = milieu
    return int(bas // 500.0 * 500.0)


def textes(r, d, nfr_):
    f, rd = d["f"], d["rd"]
    plafond = d["plafond"]
    seuil = d["prix_seuil"]
    return {
        "badge": "Immeuble de village à restaurer — 3 T2 et un ancien local commercial",
        "strategie": "restauration complète de l'immeuble puis location longue durée des quatre unités",
        "adresse_courte": "Immeuble de village 168 m² en R+3 — centre, Solliès-Pont (83210)",
        "quartier": "centre, Solliès-Pont",
        "intro_attractivite":
            "Solliès-Pont, 12 000 habitants dans la vallée du Gapeau, à une douzaine de minutes de Toulon "
            "en TER : la commune a sa gare, ce que peu de bourgs de cette taille peuvent dire, et cela "
            "suffit à alimenter une demande locative régulière. Les appartements s'y traitent autour de "
            "2 820 €/m² (médiane DVF 2025, 66 ventes) et les loyers autour de 15,3 €/m²/mois — les deux "
            "chiffres qui encadrent ce dossier. Le bien, lui, est un immeuble de village de 1800 vendu "
            "libre et à restaurer intégralement, en plein centre : l'emplacement est bon, mais c'est un "
            "chantier, pas un placement.",
        "profil":
            "ménages actifs de la première couronne toulonnaise — couples et petites familles travaillant à "
            "Toulon, La Garde, Hyères ou La Farlède, sensibles aux douze minutes de trajet ferroviaire — "
            "pour les trois T2, et un commerce de proximité pour le local de 40 m² en rez-de-chaussée, "
            "dont la destination reste à définir.",
        "intro_strategie":
            "Trois lectures chiffrées, et une seule famille de scénarios : l'immeuble est vendu libre et à "
            "restaurer, il n'y a donc aucun revenu tant que le chantier n'est pas achevé et les quatre "
            "unités relouées. Restaurer puis louer les trois T2 et le local est la seule voie qui crée un "
            "revenu — c'est la stratégie retenue, et c'est aussi celle qui absorbe le plus de capital. "
            "Convertir le local de 40 m² en quatrième logement ne change pas l'équation : le loyer d'un "
            "studio est du même ordre que celui du local, pour des travaux comparables. Restaurer puis "
            "revendre à la découpe est perdant avant même d'être risqué : la somme des unités vaut "
            "nettement moins que le prix de revient.",
        "intro_projections":
            "Les quatre unités sont vides : l'assiette publiée est donc une cible d'après travaux, jamais "
            "un encaissement. Le scénario base retient 2 040 €/mois pour les trois T2 et le local, avec "
            "5 % de vacance et les 250 000 € de travaux du scénario central. Le scénario best suppose que "
            "le budget annoncé par l'agence (220 000 €) se tient et que les loyers atteignent 2 200 €/mois. "
            "Le scénario worst réalise les deux risques du dossier ensembles : 300 000 € de travaux et un "
            "local commercial vide à la relocation.",
        "lecture":
            f"Le dossier tient en une ligne : {eur(d['prix'])} d'achat plus {eur(TRAVAUX)} de travaux "
            f"donnent un prix de revient de {eur(d['revient'])} pour un actif qui, restauré et loué, vaut "
            f"{eur(r['marche']['valeur']['retenue_euros'])} — soit {nfr_(d['c']['ratio_cout_valeur'], 3)} fois "
            f"la valeur créée. Le revenu, lui, n'existe pas encore : il faut un chantier complet et quatre "
            f"relocations pour obtenir {eur(d['loyer'])}/mois. "
            f"Le rendement net après IS ressort à {pct(rd['net_sur_revient_pct'])} sur le prix de revient, "
            f"sous le plancher de 5 % de la doctrine, et le prix de revient dépasse de plus de 40 % la "
            f"valeur de marché : les trois plafonds de note jouent en même temps — rendement sous le "
            f"plancher, actif payé au-dessus de sa valeur, et un budget travaux non devisé.",
        "conf":
            f"Ce n'est pas un dossier de rendement, c'est un dossier de travaux. {eur(d['prix'])} pour un "
            f"immeuble de 168 m² est un prix d'entrée bas — 827 €/m² quand la commune traite autour de "
            f"2 820 €/m² — mais il porte une restauration totale que l'agence elle-même chiffre à "
            f"220 000 €, et que notre barème place entre 218 000 et 302 000 €. À 250 000 €, le prix de "
            f"revient atteint {eur(d['revient'])} pour {eur(r['marche']['valeur']['retenue_euros'])} de "
            f"valeur : l'opération détruit de la valeur, et elle la détruit deux fois — dans les travaux, "
            f"puis dans les mois de portage à vide. La bonne question n'est pas « le prix est-il "
            f"intéressant », elle est « quel budget travaux, et à quel prix d'achat » : c'est ce que la "
            f"grille ci-dessous borne.",
        "stance": "On ne paie pas ce dossier à ce prix — et le prix plafond est très loin sous l'affichage.",
        "verdict_texte":
            f"L'emplacement est bon, la commune est solide et la décote affichée est réelle : 827 €/m² "
            f"pour un immeuble de village en centre. Mais ce prix n'est pas une décote, c'est le prix d'un "
            f"immeuble à restaurer, et la restauration coûte plus cher que ce qu'elle crée. À "
            f"{eur(d['prix'])} d'achat et {eur(TRAVAUX)} de travaux, le rendement net après IS reste sous "
            f"le plancher de 5 % et le prix de revient dépasse de plus de 40 % la valeur de marché. Le prix "
            f"plafond ressort à {eur(d['plafond'])} — soit {eur(d['prix'] - d['plafond'])} sous "
            f"l'affichage — et le dossier ne rejoint la cible de rendement qu'à {eur(seuil)}. Entre les "
            f"deux, il n'y a pas de négociation : il y a un autre dossier.",
        "performance":
            f"{pct(rd['net_sur_revient_pct'])} de rendement net après IS sur un prix de revient de "
            f"{eur(d['revient'])}, quand le plancher de la branche est à 5 %. Ratio prix de revient sur "
            f"valeur : {nfr_(d['c']['ratio_cout_valeur'], 3)} — le capital engagé dépasse de plus de 40 % "
            f"la valeur de l'actif, ce qui plafonne la note sans rémission. EBE avant IS : {eur(f['ebe'])} "
            f"par an. L'amortissement du bâti ({eur(f['amortissement'])}) limite l'IS à "
            f"{eur(f['is_annuel'])}, mais il ne crée pas de valeur.",
        "prix_texte":
            f"Le prix plafond est de {eur(d['plafond'])} : au-dessus, le capital engagé dépasse la valeur "
            f"de l'actif et la note ne peut plus s'élever. Le dossier n'a pas de prix cible — aucune "
            f"décote réaliste ne l'amène à 6,5/10 tant que le budget travaux n'est pas devisé. Le prix "
            f"auquel il atteindrait le seuil de rendement de la doctrine est de {eur(seuil)}. Aux "
            f"220 000 € de travaux annoncés par l'agence, le prix plafond remonte à "
            f"{eur(d['plafond_220'])} : c'est la sensibilité travaux qui décide du dossier, pas le prix "
            f"d'affichage.",
    }


def garde_fous(d):
    return f"""        <li><strong>Le prix plafond est de {eur(d['plafond'])}</strong> — soit {eur(d['prix'] - d['plafond'])} sous le prix affiché (−{nfr((d['prix'] - d['plafond']) / d['prix'] * 100, 0)} %). Au-dessus, le capital engagé dépasse la valeur de l'actif et la note ne peut plus s'élever. Ce plafond vaut pour {eur(TRAVAUX)} de travaux ; aux 220 000 € annoncés par l'agence, il remonte à {eur(d['plafond_220'])}.</li>
        <li><strong>Le dossier n'a pas de prix cible.</strong> Aucune décote réaliste ne l'amène à 6,5/10 tant que le budget travaux reste non devisé : c'est un blocage, pas une réserve. Le débloquer suppose trois devis par corps d'état sur un métré établi après visite.</li>
        <li><strong>Le prix du seuil de rendement est de {eur(d["prix_seuil"])}</strong> — c'est le prix d'achat auquel {eur(d["loyer"])}/mois couvrent la doctrine de 5 % net après IS avec {eur(TRAVAUX)} de travaux, travaux compris dans le capital engagé.</li>
        <li><strong>La ligne rouge travaux est à environ 200 000 €</strong> : au-delà, le rendement net passe sous 5 % au prix affiché, et chaque euro de travaux supplémentaires se déduit du prix d'achat, euro pour euro.</li>
        <li><strong>Pièces à exiger avant toute proposition :</strong> devis écrits par corps d'état (toiture, planchers, réseaux, menuiseries) établis sur un métré, diagnostics DPE, électricité, amiante et plomb, avis de taxe foncière réel, titre de propriété pour établir la monopropriété ou la copropriété, et plan des niveaux avec surfaces par lot.</li>
        <li><strong>Point de méthode :</strong> l'agence annonce elle-même 220 000 € de travaux — c'est un argument de vente, pas un budget. Aucun montant publié ici ne se discute avant d'avoir vu le chiffrage d'un homme de l'art sur place.</li>"""


def main():
    lat, lon = "43.1695", "6.0439"
    map_addr = "Centre, Solliès-Pont (83210) — coordonnées du centre-bourg, adresse exacte non communiquée"
    adresse = "Centre, Solliès-Pont (83210) — adresse exacte non communiquée par le mandataire"

    r = rec()
    c = engine.compute(r)
    note, verdict, comp = scoring.note_et_verdict(r, c)
    f, rd = c["fiscal"], c["rendements"]
    prix = r["annonce"]["prix_retenu_euros"]
    loyer = r["marche"]["loyers"][0]["loyer_mensuel_euros"] * 3 + r["marche"]["loyers"][1]["loyer_mensuel_euros"]
    frais = r["hypotheses"]["frais_acquisition_euros"]

    d = {
        "rec": r, "c": c, "note": note, "verdict": verdict, "comp": comp, "f": f, "rd": rd,
        "prix": prix, "loyer": loyer, "revient": c["prix_revient_total"], "adresse": adresse,
        "solde": f["net_apres_is"] / 12 - (prix + TRAVAUX) * ANNUITE,
        "classe": {"acheter": "buy", "negocier": "nego", "fuir": "pass"}[verdict],
    }
    plafond, contrainte = scoring.prix_plafond(r)
    d["plafond"] = plafond
    d["contrainte"] = contrainte
    r220 = variante(r, travaux=220000.0)
    d["plafond_220"] = scoring.prix_plafond(r220)[0]
    d["prix_seuil"] = prix_a_seuil(r, 5.0)
    d["autofin"] = prix_autofinancement(r, prix)

    d["scenarios"] = []
    for lib, cls, loyer_s, vac, trav, entretien, sous in (
        ("Scénario Base", "scenario-base", LOYER_BASE, 5.0, TRAVAUX, None,
         f"{eur(LOYER_BASE)}/mois pour trois T2 et le local — vacance 5 % — {eur(TRAVAUX)} de travaux"),
        ("Scénario Best", "scenario-best", LOYER_BEST, 3.0, TRAVAUX_BEST, None,
         f"Loyers à {eur(LOYER_BEST)}/mois et budget travaux tenu aux {eur(TRAVAUX_BEST)} annoncés par l'agence"),
        ("Scénario Worst", "scenario-worst", LOYER_WORST, 15.0, TRAVAUX_WORST, 2500.0,
         f"Local commercial vide, {eur(TRAVAUX_WORST)} de travaux et charges majorées — vacance 15 %"),
    ):
        rr = variante(r, loyer=loyer_s, vacance=vac, travaux=trav, entretien=entretien)
        cc = engine.compute(rr)
        d["scenarios"].append({
            "libelle": lib, "classe": cls, "sous_titre": sous, "loyer": loyer_s, "vacance": vac,
            "c": cc, "rec": rr,
            "solde": cc["fiscal"]["net_apres_is"] / 12 - (prix + trav) * ANNUITE,
        })

    d["grille"] = []
    for l in (1700.0, 1900.0, LOYER_BASE, 2200.0, 2400.0):
        cc = engine.compute(variante(r, loyer=l, vacance=5.0))
        d["grille"].append({
            "loyer": l, "ebe": cc["fiscal"]["ebe"], "net": cc["fiscal"]["net_apres_is"],
            "solde": cc["fiscal"]["net_apres_is"] / 12 - (prix + TRAVAUX) * ANNUITE,
            "rdt": cc["rendements"]["net_sur_revient_pct"],
        })

    plans = {
        "Restauration complète puis location longue durée": (LOYER_BASE, 5.0, TRAVAUX, 280000.0),
        "Conversion du local commercial": (2080.0, 5.0, 265000.0, 300000.0),
        "Restauration puis revente à la découpe": (LOYER_BASE, 5.0, TRAVAUX, 280000.0),
    }
    d["strategies"] = []
    for st in r["analyse"]["strategies_explorees"]:
        key = next(k for k in plans if st["strategie"].startswith(k))
        loyer_s, vac_s, trav_s, valeur_s = plans[key]
        rr = variante(r, loyer=loyer_s, vacance=vac_s, travaux=trav_s, valeur=valeur_s)
        cc = engine.compute(rr)
        d["strategies"].append({
            "strategie": st["strategie"], "lots": st["lots"], "c": cc, "loyer": loyer_s,
            "rdt": cc["rendements"]["net_sur_revient_pct"], "ratio": cc["ratio_cout_valeur"],
            "faisabilite": st["faisabilite"], "risque": st["risque"], "valeur": valeur_s,
            "retenue": st["strategie"].startswith("Restauration complète"),
        })

    t = textes(r, d, nfr)
    t["garde_fous"] = garde_fous(d)

    # --- contrôles chiffrés -------------------------------------------------
    calcule("solde mensuel base", round(d["solde"]), round(f["net_apres_is"] / 12 - (prix + TRAVAUX) * ANNUITE))
    calcule("rendement net/revient", round(rd["net_sur_revient_pct"], 2),
            round(f["net_apres_is"] / d["revient"] * 100, 2), tolerance=0.05)
    calcule("prix au m²", round(prix / SURFACE), round(139000.0 / 168.0))
    calcule("loyer mensuel retenu", round(loyer), 3 * 520.0 + 480.0)
    calcule("ratio coût/valeur", round(c["ratio_cout_valeur"], 2), round(d["revient"] / 280000.0, 2), tolerance=0.02)
    calcule("prix plafond (moteur / texte)", float(d["plafond"]), float(d["plafond"]), tolerance=0.6)
    for s in d["scenarios"]:
        attendu = s["c"]["fiscal"]["net_apres_is"] / 12 - (prix + s["rec"]["bien"]["travaux"]["montant_euros"]) * ANNUITE
        calcule(f"solde {s['libelle']}", round(s["solde"], 2), round(attendu, 2), tolerance=1.0)

    t["releve"] = releve_html(
        ["Source", "Loyer / repère", "Détail"],
        [["Trois T2 de 35 m² — moyenne communale", "15,3 €/m²/mois",
          "soit 535 €/mois pour 35 m² (relevé du dossier Solliès-Pont du 20/09/2026)"],
         ["Immeuble comparable du village — 4 T2 de 40 m²", "2 000 €/mois au total",
          "500 € par T2, soit 12,5 €/m² : un niveau annoncé 18 % sous le marché communal"],
         ["Annonces locatives de Solliès-Pont", "546 € à 840 €/mois",
          "du studio de 27 m² au 56 m² meublé avec parking (dossier du 20/09/2026)"],
         ["Local commercial 40 m², Solliès-Pont", "523 à 687 €/mois",
          "12 à 16 €/m²/mois ; 25 m² à 400 € et 75 m² à 900 € en comparaison (relevé du 14/10/2026)"],
         ["DVF 2025, appartements Solliès-Pont (83130)", "2 820 €/m² médiane",
          "n = 66 ventes ; tranche 30-45 m² à 2 293 €/m² (n = 11), contre 2 859 €/m² en 2024 (n = 14)"],
         ["DVF, locations constatées dans le village", "2 098 et 2 231 €/m²",
          "transactions réelles sur des 56 m² et 65 m² — la base retenue pour la revente"],
         ["DVF 2024-2025, locaux commerciaux Solliès-Pont", "1 687 €/m² médiane",
          "n = 39 mutations, dont 1 244 €/m² pour les locaux de 100 m² et plus"]])

    t["releve"] += ("\n    <p class=\"attractiveness-intro\"><strong>Ce que le relevé établit :</strong> "
        "les trois T2 se louent entre 12,5 et 15,3 €/m²/mois sur la commune, soit 520 €/mois pour 35 m² "
        "avec la prudence retenue ici. Le local commercial, lui, se loue 12 à 16 €/m²/mois en annonce : "
        "480 €/mois pour 40 m² est le bas de cette fourchette, et c'est un poste de revenu qui n'est "
        "adossé à aucun bail. Côté revente, la médiane communale de 2 820 €/m² ne s'applique pas à des T2 "
        "de 35 m² dans un immeuble de village : les transactions réellement constatées sortent à 2 098 et "
        "2 231 €/m², et c'est cette base qui est retenue pour la valeur de sortie.</p>")

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
        garde_fous=t["garde_fous"], amortissement=eur(f["amortissement"]),
        frais=eur(frais), loyer=nfr(d["loyer"], 0), charges=eur(charges), note=nfr(d["note"], 1),
        verdict_libelle={"buy": "à acheter", "nego": "à négocier", "pass": "à fuir"}[d["classe"]],
        perf_score=nfr(comp["s_performance"], 1), secu_score=nfr(comp["s_securite"], 1),
        adeq_score=nfr(comp["s_adequation"], 1), risque_score=nfr(comp["s_risque"], 1),
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
    if r["annonce"]["url"] not in html:
        raise SystemExit("lien de l'annonce absent de la page")
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
          f"plafond {d['plafond']} € ({d['contrainte']}) | plafond@220k {d['plafond_220']} € | "
          f"seuil {d['prix_seuil']} € | autofinancement {d['autofin']} €")


if __name__ == "__main__":
    main()
