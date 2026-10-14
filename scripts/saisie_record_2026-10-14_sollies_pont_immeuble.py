#!/usr/bin/env python3
"""Saisie de l'immeuble de village R+3 — 3 T2 et un ancien local commercial — Solliès-Pont (83210).

SeLoger 26CGGN6HMPH3 (IAD France, Christian Bergallo, réf. annonce 2136663), 139 000 €, 168 m².
Usage : python3 scripts/saisie_record_2026-10-14_sollies_pont_immeuble.py [--ecrire]
"""
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts"))
from analyse_app import engine, schema, scoring  # noqa: E402

BASE = RACINE / "analyses" / "analyses.json"
SLUG = "2026-10-14-sollies-pont-immeuble-village-3-t2-local"
PRIX = 139000.0
FRAIS = 11120.0              # 8 % (honoraires à la charge du vendeur)
TRAVAUX = 250000.0           # scénario central (annonce 220 000, barème 218 400-302 400)
LOYER_T2 = 520.0             # par T2 de 35 m²
LOYER_LOCAL = 480.0          # 40 m² à 12 €/m²/mois, bas de la fourchette relevée
ANNUITE = 0.9 * (0.037 / 12) / (1 - (1 + 0.037 / 12) ** -180) + 0.9 * 0.0034 / 12

RECORD = {
    "slug": SLUG,
    "date_analyse": "2026-10-14",
    "date_maj": "2026-10-14",
    "titre": "Immeuble de village R+3 à restaurer : 3 T2 de 35 m² et un ancien local commercial de 40 m² — Solliès-Pont centre",
    "bien": {
        "type_bien": "immeuble",
        "sous_type": None,
        "type_detail": "Immeuble de village en R+3, un T2 d'environ 35 m² par étage (R+1, R+2, R+3) "
                       "et, en rez-de-chaussée, la cage d'escalier et un ancien local commercial de 40 m² — "
                       "168 m² annoncés au total. Bâti de 1800, vendu libre, sans cave et sans ascenseur. "
                       "Restauration complète annoncée par l'agence : toiture, planchers, isolation, "
                       "électricité, plomberie, menuiseries, sols, peintures, sanitaires, cuisines",
        "neuf": False,
        "adresse": {
            "texte": "Centre, Solliès-Pont (83210) — adresse exacte non communiquée par le mandataire",
            "ville": "Solliès-Pont",
            "code_postal": "83210",
            "quartier": "Centre",
        },
        "surfaces": {
            "texte": "168 m² annoncés : 3 T2 d'environ 35 m² (105 m²), un ancien local commercial de 40 m² "
                     "en rez-de-chaussée, le solde en cage d'escalier et communs. Aucune surface Carrez par lot, "
                     "aucun plan",
        },
        "lots": {
            "count": 4,
            "nature": "Quatre unités louables : trois T2 d'environ 35 m² et un local commercial de 40 m². "
                      "Immeuble vendu entier, en monopropriété présumée (aucun syndic ni charge mentionnée) — "
                      "à confirmer",
            "lots_distincts": 4,
        },
        "copro": {
            "charges_annuelles_euros": 0.0,
            "charges_source": "Aucune charge de copropriété annoncée : immeuble présumé en monopropriété. "
                              "À confirmer par l'acte — si l'immeuble est en copropriété, compter 1 200 à "
                              "2 500 €/an de charges en plus",
        },
        "travaux": {
            "montant_euros": TRAVAUX,
            "nature": "L'agence annonce elle-même une « restauration totale » à environ 220 000 € : toiture, "
                      "planchers, isolation, électricité, plomberie, menuiseries, sols, peintures, sanitaires, "
                      "cuisines. Ce chiffre est le BAS de notre barème de rénovation lourde : 1 300 à "
                      "1 800 €/m² sur 168 m² donnent 218 400 à 302 400 €, et un bâti de 1800 dont la toiture "
                      "et les planchers sont à reprendre relève de la fourchette 1 500 à 2 500 €/m². "
                      "Scénario central retenu : 250 000 €, soit 1 488 €/m². Fourchette 220 000 à 300 000 €, "
                      "aucun devis communiqué",
        },
    },
    "annonce": {
        "plateforme": "seloger",
        "url": "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/sollies-pont-83210/26CGGN6HMPH3",
        "prix_affiche_euros": PRIX,
        "prix_retenu_euros": PRIX,
        "prix_statut": "affiche",
        "vendeur": "IAD France — Christian Bergallo, mandataire indépendant, agent commercial de la SAS I@D "
                   "France, RSAC Toulon 327188132, réf. annonce 2136663 — honoraires à la charge du vendeur "
                   "(annonce en exclusivité, présentée comme rare à la vente)",
    },
    "marche": {
        "valeur": {
            "basse_euros": 240000.0,
            "haute_euros": 330000.0,
            "retenue_euros": 280000.0,
            "source": "Immeuble rénové, valorisé lot par lot : trois T2 de 35 m² à 2 250 €/m² (236 000 €) plus "
                      "un local commercial de 40 m² à 1 000 €/m² (40 000 €), soit 276 000 € — retenue "
                      "280 000 €. Ancrages : DVF Solliès-Pont (83130), appartements médiane 2 820 €/m² "
                      "(n = 66 ventes en 2025) et tranche 30-45 m² à 2 293 €/m² (n = 11) — la médiane 2024 de "
                      "la même tranche ressort à 2 859 €/m² (n = 14) ; les transactions réellement constatées "
                      "dans le village portent sur des 56 m² à 2 098 €/m² et des 65 m² à 2 231 €/m² (dossier "
                      "Solliès-Pont du 20/09/2026), ce qui est la base retenue et non la moyenne communale. "
                      "Le local commercial est le poste le plus incertain : sa valeur de revente dépend de "
                      "l'activité, et 1 000 €/m² est une hypothèse prudente face à une médiane DVF communale "
                      "de 1 687 €/m² sur les locaux (n = 39 sur deux ans)",
            "confiance": "moyenne",
        },
        "loyers": [
            {
                "lot": "Trois T2 de 35 m² rénovés",
                "quantite": 3,
                "loyer_mensuel_euros": LOYER_T2,
                "occupe": False,
                "note": "Loyers APRÈS travaux, aucun lot n'étant louable en l'état (restauration complète). "
                        "Ancrage : 15,3 €/m²/mois en moyenne communale (dossier Solliès-Pont du 20/09/2026), "
                        "soit 535 € pour 35 m² ; un immeuble comparable du village (quatre T2 de 40 m²) est "
                        "loué 2 000 €/mois, soit 500 € par lot et 12,5 €/m² — un niveau lui-même annoncé "
                        "18 % sous le marché. 520 €/mois retenus, soit 14,9 €/m², entre le loyer en place du "
                        "comparable et la moyenne communale",
            },
            {
                "lot": "Ancien local commercial de 40 m² en rez-de-chaussée",
                "quantite": 1,
                "loyer_mensuel_euros": LOYER_LOCAL,
                "occupe": False,
                "note": "Loyer APRÈS travaux. Relevé de locaux commerciaux à Solliès-Pont au 14/10/2026 : "
                        "40 m² de surface de vente à 687 €/mois, 40 m² à 523 €/mois (157 €/m²/an), 25 m² à "
                        "400 €/mois et 75 m² à 900 €/mois — soit 12 à 16 €/m²/mois. Retenu : 480 €/mois, "
                        "soit 12 €/m²/mois, le bas de la fourchette relevée, un local de 40 m² en rez-de-"
                        "chaussée de village n'ayant ni la surface ni la visibilité des locaux de 75 m². "
                        "Hypothèse non confirmée par un bail : c'est un poste de revenu à valider, et un lot "
                        "qui peut rester vide plusieurs mois",
            },
        ],
        "notes": "L'assiette de revenus est entièrement POST-TRAVAUX : l'immeuble est vendu à restaurer "
                 "totalement, aucun lot ne produit aujourd'hui. Les 24 480 €/an retenus (2 040 €/mois) sont "
                 "donc une cible, pas un encaissement — et ils ne courent qu'après un chantier complet et "
                 "la relocation de quatre unités. C'est la différence de nature avec nos dossiers Brignoles : "
                 "ici le revenu n'existe pas encore.",
    },
    "hypotheses": {
        "vacance_base_pct": 5.0,
        "vacance_best_pct": 3.0,
        "vacance_worst_pct": 15.0,
        "taux_placement_reserve_pct": 2.84,
        "quote_part_bati_pct": 90.0,
        "vacance_justification": "Quatre unités dont un local commercial de 40 m², sur un marché locatif "
                                 "liquide mais une commune de 12 000 habitants : 5 % en base, 3 % en best "
                                 "(un T2 se reloue en quelques semaines avec la gare TER à douze minutes de "
                                 "Toulon), 15 % en worst — le local commercial vide pendant la relocation "
                                 "des logements.",
        "charges": {
            "charges_copro_annuelles_euros": 0.0,
            "charges_copro_commentaire": "Aucune charge annoncée : monopropriété présumée, à confirmer par "
                                         "l'acte. En copropriété, le poste coûterait 1 200 à 2 500 €/an et "
                                         "retirerait 0,3 à 0,6 point de rendement net",
            "taxe_fonciere_annuelle_euros": 2000.0,
            "taxe_fonciere_commentaire": "2 000 €/an ESTIMÉS — aucun avis communiqué. La commune applique un "
                                         "taux de taxe foncière sur le bâti de 49,51 % en 2025, l'un des plus "
                                         "élevés du Var (dossier Solliès-Pont du 20/09/2026) : l'avis réel est "
                                         "à exiger avant toute offre, le poste peut monter à 2 500-3 000 €",
            "entretien_annuel_euros": 1500.0,
            "entretien_commentaire": "1 500 €/an provisionnés pour un immeuble de village de 1800 sans "
                                     "extérieur : entretien courant et remise en état entre deux locataires. "
                                     "Après une restauration complète, ce poste est modéré au démarrage",
            "pno_annuelle_euros": 350.0,
            "comptabilite_annuelle_euros": 0.0,
        },
        "frais_acquisition_euros": FRAIS,
        "frais_acquisition_commentaire": "8 % du prix (11 120 €), régime ancien ; honoraires à la charge "
                                         "du vendeur",
    },
    "analyse": {
        "branche": "residentiel",
        "type_operation": "locatif",
        "strategie_retenue": {
            "nom": "Restauration complète puis location longue durée des trois T2 et du local commercial",
            "code": "ld-nue",
            "lots": 4,
        },
        "strategies_explorees": [
            {
                "strategie": "Restauration complète puis location longue durée (3 T2 + local commercial)",
                "lots": 4,
                "performance": "Le seul scénario qui crée un revenu, mais il part de 250 000 € de travaux "
                               "pour un actif de 280 000 € : le rendement net après IS reste sous le plancher "
                               "de 5 % au prix affiché",
                "valeur_sortie": "Valeur locative créée : 280 000 € (trois T2 à 2 250 €/m² et le local à "
                                 "1 000 €/m²), très en dessous du prix de revient",
                "faisabilite": "Douze à dix-huit mois de chantier complet, aucun devis, aucun plan, aucun "
                               "diagnostic : c'est un projet, pas une opération chiffrée",
                "risque": "élevé — toiture et planchers d'un bâti de 1800 à reprendre, structure inconnue, "
                          "budget travaux non devisé",
            },
            {
                "strategie": "Conversion du local commercial de 40 m² en quatrième logement",
                "lots": 4,
                "performance": "Substituer un studio loué 480-520 € au local revient au même loyer, avec des "
                               "travaux équivalents : aucun gain de revenu, une unité de plus à relouer",
                "valeur_sortie": "Valeur de revente d'un studio de 40 m² supérieure à celle d'un local de "
                                 "40 m² en village, mais la conversion suppose un changement de destination",
                "faisabilite": "Déclaration préalable et vérification du PLU ; le lot est déjà un local "
                               "commercial, la transformation est plausible",
                "risque": "faible sur le principe, mais elle ne corrige pas l'équation économique du dossier",
            },
            {
                "strategie": "Restauration puis revente à la découpe des quatre unités",
                "lots": 4,
                "performance": "Négative : 280 000 € de valeur de sortie pour 400 000 € de revient, "
                               "hors frais de vente et portage. Aucune marge de marchand de biens",
                "valeur_sortie": "280 000 € attendus des quatre unités, contre un revient de 400 000 € — la "
                                 "découpe ne crée pas la marge, elle l'ajoute aux frais",
                "faisabilite": "État descriptif de division à créer, portage de 24 à 30 mois",
                "risque": "élevé — et sans objet : l'opération est perdante avant même d'être risquée",
            },
        ],
        "attractivite": [
            {
                "dimension": "transports",
                "score": 8,
                "justification": "Solliès-Pont a sa gare TER — Toulon à une douzaine de minutes — et l'accès "
                                 "à l'A57 est immédiat : un atout rare pour une commune de 12 000 habitants, "
                                 "et le premier moteur de la demande locative du secteur.",
            },
            {
                "dimension": "commerces",
                "score": 7,
                "justification": "Bourg actif avec commerces de proximité, marché et services ; cœur de "
                                 "village, à pied de tout. C'est ce qui permet de louer le local commercial "
                                 "et les T2 sans voiture.",
            },
            {
                "dimension": "ecoles",
                "score": 7,
                "justification": "Groupes scolaires et collège sur la commune — le collège Vallée du Gapeau "
                                 "est à 649 m selon l'annonce — lycées à Toulon ou La Garde : secteur "
                                 "familial, ce qui soutient la demande sur des T2.",
            },
            {
                "dimension": "securite",
                "score": 7,
                "justification": "Commune résidentielle de la première couronne toulonnaise, sans quartier "
                                 "prioritaire, centre ancien entretenu. Un immeuble de village à restaurer "
                                 "intégralement reste toutefois un chantier en cœur de bourg.",
            },
            {
                "dimension": "demande_locative",
                "score": 7,
                "justification": "Marché liquide pour la taille de la commune : 50 à 66 ventes d'appartements "
                                 "par an, 28 annonces locatives relevées dans notre dossier du 20/09/2026, "
                                 "et quatre T2 loués dans un immeuble comparable du village. Le risque n'est "
                                 "pas la demande, c'est le loyer du local commercial.",
            },
            {
                "dimension": "dynamisme",
                "score": 6,
                "justification": "Économie agricole et résidentielle adossée à l'emploi toulonnais ; prix des "
                                 "appartements stables (médiane 2 820 €/m² en 2025 contre 2 824 €/m² en 2024) "
                                 "et construction neuve à l'arrêt. Marché sans fièvre : on n'y vient pas "
                                 "chercher de la plus-value, et un immeuble à restaurer s'y revend mal.",
            },
        ],
        "risques": [
            {
                "facteur": "Budget travaux : 220 000 € annoncés, aucun devis, structure inconnue",
                "detail": "L'agence annonce elle-même une restauration totale — toiture, planchers, "
                          "isolation, réseaux, menuiseries — pour environ 220 000 €, soit 1 310 €/m². C'est "
                          "le bas de notre barème : un immeuble ancien se chiffre entre 1 300 et 1 800 €/m², "
                          "et la reprise de la toiture et des planchers relève de la fourchette 1 500 à "
                          "2 500 €/m². À 300 000 € de travaux — le milieu de fourchette — le prix de "
                          "revient passe de 400 000 à 450 000 € et le rendement net tombe sous 4 %. "
                          "Aucun devis, aucun plan, aucun diagnostic structure : les 220 000 € sont un "
                          "argument de vente, pas un budget.",
                "severite": 5,
                "bloquant": True,
            },
            {
                "facteur": "Aucun diagnostic sur un bâti de 1800",
                "detail": "Ni DPE, ni électricité, ni amiante, ni plomb, ni plomb — l'annonce invite à "
                          "demander la performance énergétique, ce qui veut dire qu'elle n'existe pas. Sur "
                          "un bâti de 1800 avec restauration complète, le repérage amiante et l'état de "
                          "l'installation électrique conditionnent le budget : un désamiantage ou une reprise "
                          "de colonne déplace le chantier de plusieurs dizaines de milliers d'euros.",
                "severite": 4,
            },
            {
                "facteur": "Revenu inexistant au premier jour, chantier de douze à dix-huit mois",
                "detail": "L'immeuble est vendu à restaurer totalement : aucun lot ne produit, et la totalité "
                          "du revenu — 24 480 €/an retenus — n'arrive qu'après le chantier et la relocation "
                          "de quatre unités. Pendant ce temps, la taxe foncière, l'assurance et les intérêts "
                          "courent sur un actif qui ne rapporte rien.",
                "severite": 4,
            },
            {
                "facteur": "Rendement sous le plancher au prix affiché",
                "detail": "À 139 000 € d'achat et 250 000 € de travaux, le prix de revient atteint 400 000 € "
                          "pour 280 000 € de valeur locative créée : ratio coût/valeur de 1,43, et un "
                          "rendement net après IS inférieur au plancher de 5 % de la doctrine. Le dossier ne "
                          "tient pas sur le prix demandé, et il ne tient pas davantage sur les travaux "
                          "annoncés.",
                "severite": 4,
            },
            {
                "facteur": "Loyer du local commercial non établi",
                "detail": "Le loyer de 480 €/mois retenu est le bas d'un relevé d'annonces (12 à 16 €/m²/"
                          "mois sur des locaux de 25 à 75 m²) : aucun bail, aucun preneur, aucune activité "
                          "identifiée. Un local de 40 m² en rez-de-chaussée de village peut rester vacant "
                          "plusieurs mois, et c'est 24 % du revenu visé.",
                "severite": 3,
            },
            {
                "facteur": "Taxe foncière d'une commune au taux de 49,51 %",
                "detail": "Solliès-Pont applique l'un des taux de taxe foncière les plus élevés du Var. "
                          "2 000 €/an sont provisionnés sans avis : sur 168 m² restaurés, l'avis réel peut "
                          "dépasser 2 500 € et retirer un demi-point de rendement net.",
                "severite": 3,
            },
            {
                "facteur": "Statut de l'immeuble non confirmé",
                "detail": "Aucun syndic, aucune charge, aucun appel de fonds mentionnés : la monopropriété "
                          "est présumée. Si l'immeuble est en copropriété, les charges annuelles ajoutent "
                          "1 200 à 2 500 € et le ravalement ou la toiture peuvent faire l'objet d'un appel "
                          "de fonds voté pendant le chantier.",
                "severite": 3,
            },
            {
                "facteur": "Revente difficile en cas d'échec",
                "detail": "Un immeuble de village de 168 m² à 2 300 €/m² ne s'adresse qu'à des investisseurs "
                          "ou à des marchands de biens, sur un marché où la médiane des appartements "
                          "plafonne à 2 820 €/m² et où la construction neuve est à l'arrêt : le repli n'est "
                          "pas liquide, c'est le portage qui absorbe l'erreur.",
                "severite": 3,
            },
        ],
    },
}


def main():
    ecrire = "--ecrire" in sys.argv
    print("validation du record :", schema.validate_record(RECORD) or "aucune erreur")
    c = engine.compute(RECORD)
    n, v, comp = scoring.note_et_verdict(RECORD, c)
    plafond, detail = scoring.prix_plafond(RECORD)
    cible = scoring.prix_cible(RECORD)
    f, rd = c["fiscal"], c["rendements"]
    print(f"\nrevient {c['prix_revient_total']:.0f} € | revenus bruts {c['revenus_bruts_annuels']:.0f} €/an | "
          f"ratio coût/valeur {c['ratio_cout_valeur']:.3f}")
    print(f"EBE {f['ebe']:.0f} € | amortissement {f['amortissement']:.0f} € | IS {f['is_annuel']:.0f} € | "
          f"net après IS {f['net_apres_is']:.0f} €/an ({f['net_apres_is']/12:.0f} €/mois)")
    print(f"net sur revient {rd['net_sur_revient_pct']:.2f} % | net sur valeur {rd['net_sur_valeur_pct']:.2f} % | "
          f"brut sur revient {rd['brut_sur_revient_pct']:.2f} %")
    print(f"NOTE {n} — {v} | plafond {'aucun' if plafond is None else format(plafond, ',.0f') + ' €'}"
          f" | cible {'aucune' if cible is None else format(cible, ',.0f') + ' €'} | {detail}")
    print(f"composantes : {comp}")
    print(f"annuité {PRIX*ANNUITE:.0f} €/mois | solde {f['net_apres_is']/12 - PRIX*ANNUITE:+.0f} €/mois")
    if not ecrire:
        print("\n(base non modifiée — relancer avec --ecrire)")
        return
    data = json.loads(BASE.read_text(encoding="utf-8"))
    avant = len(data["analyses"])
    data["analyses"] = [a for a in data["analyses"] if a["slug"] != SLUG]
    data["analyses"].append(RECORD)
    BASE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nanalyses.json : {avant} -> {len(data['analyses'])} dossiers (slug {SLUG})")
    # sensibilité travaux (diagnostic)
    import copy
    for w in (220000.0, 250000.0, 300000.0):
        rr = copy.deepcopy(RECORD)
        rr["bien"]["travaux"]["montant_euros"] = w
        cc = engine.compute(rr)
        nn, vv, _ = scoring.note_et_verdict(rr, cc)
        pp = scoring.prix_plafond(rr)[0]
        net = cc["fiscal"]["net_apres_is"]
        rdt = cc["rendements"]["net_sur_revient_pct"]
        print(f"  travaux {w:>7,.0f} € : revient {cc['prix_revient_total']:>9,.0f} | "
              f"net {net if net is None else format(net, ',.0f')} € | "
              f"rdt {'n/d' if rdt is None else format(rdt, '.2f') + ' %'} | note {nn} | "
              f"plafond {'aucun' if pp is None else format(pp, ',.0f') + ' €'}")


if __name__ == "__main__":
    main()
