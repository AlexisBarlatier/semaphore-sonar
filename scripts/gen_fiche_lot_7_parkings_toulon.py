#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche du lot de 7 emplacements de stationnement — Toulon Les Routes.

Réutilise le gabarit et les briques du générateur `gen_fiches_2026-10-13_toulon.py`
(importé comme module) ; seuls les blocs propres au produit parking sont réécrits ici.
Sortie : analyses/2026-10-13-lot-7-parkings-toulon-les-routes/index.html
"""
import copy
import importlib.util
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)

spec = importlib.util.spec_from_file_location(
    "gen_toulon", os.path.join(ICI, "gen_fiches_2026-10-13_toulon.py"))
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

SLUG = "2026-10-13-lot-7-parkings-toulon-les-routes"
SORTIE = os.path.join(RACINE, "analyses", SLUG, "index.html")
N = 7
LOYER = 620.0            # 2 × 60 (extérieur) + 4 × 100 (sous-sol) + 1 × 100 (double)
FRAIS = 7125.0
PRIX = 95000.0

LECTURE = (
    "Sept emplacements dans une résidence de 2022, dont cinq en sous-sol sécurisé : le produit est le "
    "meilleur de la gamme stationnement, et le secteur est dense. Ce qui bloque, c'est le prix. À 95 000 €, "
    "le lot revient à 13 571 € par emplacement, au-dessus du plafond de doctrine d'une place en sous-sol "
    "(10 800 €) avant même de calculer le rendement, et il rend 4,86 % net d'IS pour un plancher de branche "
    "de 8 %. Au loyer de marché relevé (620 €/mois pour les sept), il faudrait 56 000 € pour que le lot "
    "couvre sa charge, et environ 50 000 € pour atteindre le plancher de rendement. Aucune place n'étant "
    "louée aujourd'hui, le dossier part de zéro revenu : c'est une offre basse ou rien."
)

CONF = (
    "Le lot se juge sur le loyer qu'il produit, pas sur le prix au m² — un stationnement n'en a pas. Les "
    "loyers sont relevés dans la même copropriété et dans le même secteur : 100 €/mois pour la place double "
    "en enfilade, 112 € charges comprises pour un garage de 12 m² aux Routes, 85 € pour un garage en "
    "sous-sol sécurisé à Saint-Roch, 60 € pour une place extérieure. La place double ne se loue pas deux "
    "fois le prix d'une place : la seconde voiture est bloquée par la première, et la compter à 200 € "
    "gonflerait le loyer du lot de 16 %."
)

GARDE_FOUS = """        <li><strong>Plafond de doctrine : 67 000 € acte en main</strong> (2 extérieures à 6 500 € + 5 emplacements de sous-sol à 10 800 €). Le prix affiché — 95 000 € hors frais, soit 13 571 € par emplacement — est au-dessus de la ligne de son produit avant tout calcul.</li>
        <li><strong>Prix d'autofinancement : 58 500 € net vendeur</strong> — le prix auquel les 620 €/mois couvrent la charge du lot. C'est le plafond dur de l'offre.</li>
        <li><strong>Plancher de rendement (8 % net d'IS) : 50 000 €</strong>, et 56 000 € pour la note du moteur. Le repère des 100 mois de loyer donne 62 000 € — les trois ancres encadrent la même zone.</li>
        <li><strong>À exiger avant toute offre :</strong> statut des lots (sept lots distincts ou lot unique) et numéros de lots, appel de charges et budget prévisionnel, avis de taxe foncière, PV des assemblées depuis la livraison, règlement de copropriété (location à un non-résident), ancienneté du titre du vendeur pour le droit de mutation.</li>"""

STANCE = "On offre bas, une seule fois, et on ne poursuit pas."
VERDICT_TEXTE = (
    "Le dossier ne mérite pas d'être travaillé au prix demandé : sept emplacements vides à commercialiser "
    "d'un coup, aucun bail en place, un prix par emplacement supérieur au plafond de doctrine, et un solde "
    "mensuel négatif de 230 € au prix affiché. Mais il ne coûte rien de le tester : une offre basse ferme, "
    "sans réserve, sur un lot qui traîne depuis longtemps, se refuse ou se saisit — elle ne se négocie pas."
)
PERFORMANCE = (
    "4,86 % de rendement net après IS sur un prix de revient de 102 125 € (95 000 € + 7 125 € de frais) "
    "pour un plancher de branche de 8 % — performance 0,9/10. EBE avant IS : 5 416 €/an. Ratio prix de "
    "revient sur valeur retenue : 1,46."
)
PRIX_TEXTE = (
    "Prix plafond du moteur : 56 000 € (contrainte de plancher de performance), prix cible 54 000 €. "
    "L'offre retenue est de 55 000 € net vendeur — environ 59 700 € acte en main avec les frais réels, "
    "soit 8 530 € par emplacement — et elle ne se poursuit pas : au-dessus de 58 500 €, le lot ne couvre "
    "plus sa charge au loyer relevé, et au-dessus de 67 000 € acte en main il sort de la doctrine du groupe."
)

RELEVE = gen.releve_html(
    ["Source", "Loyer", "Détail"],
    [["Double place en enfilade, sous-sol sécurisé, Toulon Les Routes", "100 €", "même produit, même secteur que le lot — loyer relevé sur le portail"],
     ["Garage de 12 m², Toulon Les Routes", "112 € CC", "dont 2 € de provisions pour charges, dépôt de garantie 110 €"],
     ["Garage en sous-sol sécurisé, Saint-Roch (Foncia)", "85 €", "annonce d'agence, 20 avenue du Général Nogues"],
     ["Place ou box de 17 m², Pont du Las", "115 € CC", "Bien'ici, annonce de particulier"],
     ["Place extérieure, Toulon 83200", "60 €", "leboncoin, 20 annonces de places dans la ville"],
     ["Place en sous-sol, Mourillon", "100 €", "portail spécialisé du stationnement"]]
) + ("\n    <p class=\"attractiveness-intro\"><strong>Ce que le relevé établit :</strong> la fourchette utile "
     "à Toulon est de 85 à 115 €/mois pour un emplacement couvert ou en sous-sol sécurisé, et de 50 à 70 € "
     "pour une place extérieure. Le lot est retenu à 2 × 60 € + 4 × 100 € + 1 × 100 €, soit 620 €/mois. "
     "Aucune place n'est louée aujourd'hui : ce chiffre est un potentiel de marché, pas un revenu en place — "
     "et c'est précisément ce qui justifie une offre basse plutôt qu'un prix de marché.</p>")

SCENARIOS = [
    ("Scénario Base", (620.0, 10.0, PRIX), "scenario-base", "Loyer 620 €/mois (relevé) — vacance 10 % — prix affiché 95 000 €"),
    ("Scénario Best", (682.0, 5.0, PRIX), "scenario-best", "Loyer 682 €/mois (+10 %, sept emplacements loués vite) — vacance 5 % — prix affiché 95 000 €"),
    ("Scénario Worst", (496.0, 25.0, PRIX), "scenario-worst", "Loyer 496 €/mois (−20 %) — vacance 25 % (trois mois de vide par an) — prix affiché 95 000 €"),
]


def bloc_cartes_parking(d):
    cartes = [
        ("Prix affiché", gen.eur(PRIX)),
        ("Emplacements", "7 (2 extérieurs, 4 en sous-sol, 1 double)"),
        ("Prix demandé par emplacement", gen.eur(PRIX / N)),
        ("Prix de revient affiché", gen.eur(d["revient"])),
        ("Loyer retenu", gen.eur(LOYER) + "/mois pour les 7"),
        ("Prix en mois de loyer", gen.nfr(PRIX / LOYER) + " mois — repère du groupe : 100"),
        ("Rendement net d'IS (revient / valeur)", f"{gen.pct(d['rd']['net_sur_revient_pct'])} / {gen.pct(d['rd']['net_sur_valeur_pct'])}"),
        ("Note", gen.nfr(d["note"], 1) + "/10"),
    ]
    return "\n".join(f'    <div class="card">\n      <span class="card-label">{k}</span>\n'
                     f'      <span class="card-value">{v}</span>\n    </div>' for k, v in cartes)


def bloc_identite_parking(d):
    r = d["rec"]
    lignes = [
        ("Adresse", r["bien"]["adresse"]["texte"]),
        ("Type", r["bien"]["type_detail"]),
        ("Vendeur", r["annonce"]["vendeur"]),
        ("Occupation", "Aucune place louée : les sept emplacements sont libres, aucun bail ni quittance produit"),
        ("Loyer de marché retenu", gen.eur(LOYER) + "/mois — 2 × 60 € (extérieur) + 4 × 100 € (sous-sol) + 1 × 100 € (double en enfilade)"),
        ("Charges de copropriété", gen.eur(r["bien"]["copro"]["charges_annuelles_euros"]) + "/an — " + r["bien"]["copro"]["charges_source"]),
        ("Taxe foncière", gen.eur(r["hypotheses"]["charges"]["taxe_fonciere_annuelle_euros"]) + "/an — " + r["hypotheses"]["charges"]["taxe_fonciere_commentaire"]),
        ("Frais d'acquisition", gen.eur(FRAIS) + " — " + r["hypotheses"]["frais_acquisition_commentaire"]),
        ("Amortissement", gen.eur(d["f"]["amortissement"]) + "/an — cinq emplacements sur sept sont bâtis (quote-part 71 % du prix de revient, sur 30 ans)"),
        ("Structure du lot", "Non communiquée : sept lots distincts ou lot unique. La revente à l'unité en dépend."),
        ("Valeur retenue", gen.eur(r["marche"]["valeur"]["retenue_euros"]) + " — " + r["marche"]["valeur"]["source"]),
    ]
    return "\n".join(f"        <tr><th>{k}</th><td>{v}</td></tr>" for k, v in lignes)


def main():
    d = gen.prepare(SLUG, "43.1237", "5.9110",
                    "Secteur Les Routes, Toulon (83200) — coordonnées du secteur, adresse exacte non communiquée",
                    "Secteur Les Routes, Toulon (83200) — adresse exacte non communiquée",
                    LECTURE, CONF, RELEVE, SCENARIOS, GARDE_FOUS)
    # grille de loyer adaptée au lot entier
    r = d["rec"]
    d["grille"] = []
    for L in (LOYER - 100, LOYER - 50, LOYER, LOYER + 50, LOYER + 100, LOYER + 150):
        rr = copy.deepcopy(r)
        for ligne in rr["marche"]["loyers"]:
            ligne["loyer_mensuel_euros"] = ligne["loyer_mensuel_euros"] / LOYER * L
        for ligne in rr["marche"]["loyers"]:
            ligne["loyer_mensuel_euros"] = round(ligne["loyer_mensuel_euros"], 2)
        cc = gen.engine.compute(rr)
        d["grille"].append({"loyer": L, "ebe": cc["fiscal"]["ebe"], "net": cc["fiscal"]["net_apres_is"],
                            "solde": cc["fiscal"]["net_apres_is"] / 12 - PRIX * gen.ANNUITE,
                            "rdt": cc["rendements"]["net_sur_revient_pct"]})

    scenarios = []
    for libelle, (loyer_s, vac_s, prix_s), classe, st in SCENARIOS:
        rr = copy.deepcopy(r)
        for ligne in rr["marche"]["loyers"]:
            ligne["loyer_mensuel_euros"] = round(ligne["loyer_mensuel_euros"] / LOYER * loyer_s, 2)
        rr["hypotheses"]["vacance_base_pct"] = vac_s
        cc = gen.engine.compute(rr)
        scenarios.append({"libelle": libelle, "classe": classe, "sous_titre": st, "loyer": loyer_s,
                          "vacance": vac_s, "c": cc, "rec": rr,
                          "solde": cc["fiscal"]["net_apres_is"] / 12 - prix_s * gen.ANNUITE})
    projections = "\n\n".join(gen.bloc_scenario(s, PRIX) for s in scenarios)

    html = gen.TEMPLATE.format(
        titre=r["titre"],
        adresse_courte="Lot de 7 emplacements de stationnement — Les Routes, Toulon (83200)",
        vendeur=r["annonce"]["vendeur"], url=r["annonce"]["url"],
        badge="Placement parking — lot de sept emplacements",
        strategie="location longue durée du lot, à un prix qui couvre sa charge",
        cartes=bloc_cartes_parking(d), lat="43.1237", lon="5.9110",
        map_addr="Secteur Les Routes, Toulon (83200) — coordonnées du secteur, adresse exacte non communiquée",
        quartier="Les Routes, Toulon Ouest",
        intro_attractivite=("Secteur résidentiel dense de Toulon Ouest, où se garer est difficile et où les "
            "résidences récentes ont leur propre parking. Le lot est dans une copropriété livrée en 2022, "
            "sécurisée : cinq emplacements sur sept sont en sous-sol, deux en extérieur. Le produit est bon, "
            "la concurrence immédiate est l'offre des autres propriétaires de la même résidence."),
        attractivite=gen.bloc_attractivite(d),
        profil=("résidents des 77 lots de la copropriété et des résidences voisines cherchant une seconde "
            "place ou un emplacement abrité ; riverains du secteur sans garage."),
        lecture=LECTURE,
        intro_strategie=("Trois lectures : louer le lot entier au loyer de marché, acheter à la découpe pour "
            "revendre à l'unité (le statut des lots n'est pas communiqué), ou tester le vendeur par une offre "
            "basse unique. C'est la troisième qui est retenue, sans renoncer à la location."),
        strategie_html="", conf=CONF, releve=RELEVE, grille=gen.bloc_grille_loyer(d),
        identite=bloc_identite_parking(d),
        intro_projections=("Lot de sept emplacements, aucun bail en place : le revenu part de zéro. Charges "
            "700 €/an de copropriété estimées et 420 €/an de taxe foncière, provision travaux 2,5 % des "
            "loyers. Cinq emplacements sur sept sont bâtis : la quote-part amortissable est fixée à 71 % du "
            "prix de revient."),
        projections=projections, risques=gen.bloc_risques(d), verdict_cls=d["classe"],
        stance=STANCE, verdict_texte=VERDICT_TEXTE, performance=PERFORMANCE, prix_texte=PRIX_TEXTE,
        garde_fous=GARDE_FOUS, amortissement=gen.eur(d["f"]["amortissement"]), frais=gen.eur(FRAIS),
        loyer=gen.nfr(LOYER), charges=gen.eur(gen.engine.charges_annuelles(r)[0]),
        note=gen.nfr(d["note"], 1),
        verdict_libelle={"acheter": "à acheter", "negocier": "à négocier", "fuir": "à fuir"}[d["verdict"]],
        perf_score=gen.nfr(d["comp"]["s_performance"], 1), secu_score=gen.nfr(d["comp"]["s_securite"], 1),
        adeq_score=gen.nfr(d["comp"]["s_adequation"], 1), risque_score=gen.nfr(d["comp"]["s_risque"], 1),
        prix_affiche=gen.eur(PRIX),
    ).replace("{strategie}", gen.bloc_strategie(d))

    residuels = [m for m in re.findall(r"\{[a-z_][a-z_0-9]*\}", html) if m not in ("{s}", "{z}", "{x}", "{y}")]
    if residuels:
        raise SystemExit(f"placeholders non remplacés : {sorted(set(residuels))}")
    for attendu in ("report-header", "summary-cards", "map-section", "attractiveness", "identity-sheet",
                    "financial-projections", "risk-matrix", 'section class="verdict', "report-signature"):
        if attendu not in html:
            raise SystemExit(f"section manquante : {attendu}")
    interdits = re.findall(r"\b(prêt|prêts|emprunt\w*|crédit\w*|apport\w*|mensualit\w*|levier|montage)\b", html, flags=re.I)
    if interdits:
        raise SystemExit(f"mot de financement : {sorted(set(interdits))}")

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"Fiche écrite : {SORTIE} ({len(html)} caractères)")
    print(f"note={d['note']} {d['verdict']} ({d['classe']}) | net/revient={d['rd']['net_sur_revient_pct']} % | "
          f"solde={d['solde']:+.0f} €/mois | plafond={d['plafond']} € | cible={d['cible']} €")
    if gen.ECARTS:
        print("ÉCARTS :", gen.ECARTS)


if __name__ == "__main__":
    main()
