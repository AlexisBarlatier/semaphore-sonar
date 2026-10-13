#!/usr/bin/env python3
"""Saisie de l'immeuble de rapport 460 m² — Centre vieille ville, Brignoles (SeLoger 26VY29CFCY11).

Usage : python3 scripts/saisie_record_2026-10-13_brignoles_immeuble_rex.py [--ecrire]
"""
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts"))
from analyse_app import engine, schema, scoring  # noqa: E402

BASE = RACINE / "analyses" / "analyses.json"
SLUG = "2026-10-13-brignoles-immeuble-rex-vieille-ville"
PRIX = 315000.0
FRAIS = 25200.0              # 8 % (honoraires à la charge du vendeur)
LOYER_TOTAL = 2219.17        # 26 630 €/an encaissés, tous lots confondus
ANNUITE = 0.9 * (0.037 / 12) / (1 - (1 + 0.037 / 12) ** -180) + 0.9 * 0.0034 / 12

RECORD = {
    "slug": SLUG,
    "date_analyse": "2026-10-13",
    "date_maj": "2026-10-13",
    "titre": "Immeuble de rapport 460 m² : 4 T2 loués, local commercial de 140 m² et deux T2 à créer — Brignoles centre",
    "bien": {
        "type_bien": "immeuble",
        "sous_type": None,
        "type_detail": "Immeuble de 6 étages en centre ancien de Brignoles, en copropriété avec l'immeuble "
                       "accolé : un local commercial de plus de 140 m² en rez-de-chaussée, 4 T2 loués de 35 à "
                       "50 m² aux étages, deux T2 supplémentaires à créer (R+1 et R+4) et une terrasse en R+5 — "
                       "460 m² annoncés au total. DPE E / GES B, état « rénovation nécessaire »",
        "neuf": False,
        "adresse": {
            "texte": "Centre vieille ville, Brignoles (83170) — adresse exacte non communiquée par l'agence",
            "ville": "Brignoles",
            "code_postal": "83170",
            "quartier": "Centre vieille ville",
        },
        "surfaces": {
            "texte": "460 m² annoncés au total : local commercial > 140 m², 4 T2 de 35 à 50 m² (soit environ "
                     "170 m²), surfaces à aménager et terrasse en R+5",
        },
        "lots": {
            "count": 5,
            "nature": "5 lots loués (4 T2 et 1 local commercial) plus deux logements à créer — immeuble en "
                      "copropriété avec l'immeuble accolé",
            "lots_distincts": None,
        },
        "copro": {
            "charges_annuelles_euros": 492.0,
            "charges_source": "Charges trimestrielles annoncées à 123 €, soit 492 €/an — le montant est présenté "
                              "sans préciser s'il s'entend pour l'immeuble ou par lot. À vérifier : s'il s'agit "
                              "de 123 € par trimestre et par lot, la charge annuelle approche 2 500 € et le "
                              "rendement perd plus d'un demi-point",
        },
        "travaux": {
            "montant_euros": 0.0,
            "nature": "Aucun travaux chiffré dans l'annonce, qui porte pourtant la mention « rénovation "
                      "nécessaire ». Le poste des deux T2 à créer n'est pas devisé par le vendeur",
        },
    },
    "annonce": {
        "plateforme": "seloger",
        "url": "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/brignoles-83170/26VY29CFCY11",
        "prix_affiche_euros": PRIX,
        "prix_retenu_euros": PRIX,
        "prix_statut": "affiche",
        "vendeur": "AGENCE REX, Brignoles (37 square Saint-Louis, RCS 502760127) — mandat réf. 2189P, "
                   "honoraires à la charge du vendeur. L'immeuble est géré par l'agence, ce qui explique la "
                   "qualité du suivi locatif annoncé (« locataires à jour »)",
    },
    "marche": {
        "valeur": {
            "basse_euros": 265000.0,
            "haute_euros": 330000.0,
            "retenue_euros": 290000.0,
            "source": "Un immeuble de rapport se valorise par capitalisation du revenu : loyers encaissés "
                      "26 630 €/an moins charges non refacturables (TF 1 663 € et copropriété 492 €), soit "
                      "24 475 € nets. Retenue : 290 000 € au taux de 8,4 %, cohérent avec un immeuble de centre "
                      "ancien à rafraîchir, en copropriété, dont quatre des cinq baux ne sont pas détaillés. "
                      "Contrôle par le marché : DVF 2024-2025 à Brignoles (83170), appartements médiane "
                      "2 393 €/m² (n = 419) et 2 200 €/m² pour les 3-5 pièces de 60 à 120 m² (n = 177), locaux "
                      "commerciaux médiane 2 000 €/m² (n = 57) — le prix demandé (685 €/m² sur 460 m²) est très "
                      "en dessous, ce qui est normal pour un immeuble de rapport vendu sur ses loyers et non "
                      "sur ses mètres carrés.",
            "confiance": "moyenne",
        },
        "loyers": [
            {
                "lot": "Immeuble loué — 4 T2 et 1 local commercial (total encaissé annoncé)",
                "quantite": 1,
                "loyer_mensuel_euros": LOYER_TOTAL,
                "occupe": True,
                "note": "26 630 €/an encaissés, tous lots confondus, « locataires à jour » selon l'agence — le "
                        "détail par lot n'est pas communiqué. Repères du marché brignolais relevés dans nos "
                        "dossiers : T2 de 34,7 m² nu à 490 €/mois (14,1 €/m²), T2 de 38 m² à 500 €, T2 de "
                        "43,8 m² au Luc à 520 €, T2 de 28 m² meublé à 590 €. Quatre T2 au marché représentent "
                        "environ 1 850 à 2 000 €/mois : il ne resterait donc que 220 à 370 €/mois pour un local "
                        "commercial de plus de 140 m², soit 1,6 à 2,6 €/m²/mois. C'est le point central du "
                        "dossier : soit un bail ancien est très en dessous de sa valeur — et il y a une marge —, "
                        "soit les loyers des T2 sont eux-mêmes bas, et il n'y a rien à reprendre.",
            },
        ],
        "notes": "Le fait solide du dossier, c'est le total encaissé ; le détail par lot est l'inconnue. "
                 "Le loyer retenu ici est donc le total réel, jamais une reconstitution : c'est lui qui alimente "
                 "l'EBE, les plafonds et le solde mensuel.",
    },
    "hypotheses": {
        "vacance_base_pct": 5.0,
        "vacance_best_pct": 2.0,
        "vacance_worst_pct": 12.0,
        "taux_placement_reserve_pct": 2.84,
        "quote_part_bati_pct": 90.0,
        "vacance_justification": "Cinq lots loués, dont un local commercial : la rotation est plus fréquente que "
                                 "sur un logement unique, mais chaque départ coûte un lot entier. 5 % en base, "
                                 "2 % en best (baux en place et locataires à jour), 12 % en worst avec le départ "
                                 "du preneur du local commercial.",
        "charges": {
            "charges_copro_annuelles_euros": 492.0,
            "charges_copro_commentaire": "492 €/an annoncés (123 € par trimestre), montant à vérifier lot par lot : "
                                         "pour un immeuble de six étages, avec un local commercial en rez-de-chaussée, "
                                         "une charge de 41 € par mois pour l'ensemble est inhabituellement basse",
            "taxe_fonciere_annuelle_euros": 1663.0,
            "taxe_fonciere_commentaire": "1 663 €/an annoncés — c'est le seul poste de charges documenté du dossier, "
                                         "avis à exiger pour confirmation",
            "entretien_annuel_euros": 2000.0,
            "entretien_commentaire": "2 000 €/an provisionnés : immeuble de six étages en centre ancien, "
                                     "« rénovation nécessaire », en copropriété avec l'immeuble accolé. Ce poste "
                                     "couvre l'entretien courant, les parties communes et la remise en état entre "
                                     "deux locataires. La provision travaux du moteur (2,5 % des loyers) s'y ajoute",
            "pno_annuelle_euros": 350.0,
            "comptabilite_annuelle_euros": 0.0,
        },
        "frais_acquisition_euros": FRAIS,
        "frais_acquisition_commentaire": "8 % du prix (25 200 €), dans le régime ancien ; honoraires à la charge "
                                         "du vendeur",
    },
    "analyse": {
        "branche": "residentiel",
        "type_operation": "locatif",
        "strategie_retenue": {
            "nom": "Immeuble de rapport conservé en l'état, création des deux T2 à l'étude",
            "code": "ld-nue",
            "lots": 5,
        },
        "strategies_explorees": [
            {
                "strategie": "Conservation en l'état — quatre T2 et le local commercial loués",
                "lots": 5,
                "performance": "5,6 % net après IS sur le prix de revient, au-dessus du plancher de 5 % mais "
                               "sans couvrir la charge du lot",
                "valeur_sortie": "Valeur de capitalisation 290 000 € au taux de 8,4 % : le prix affiché est "
                                 "au-dessus de cette valeur",
                "faisabilite": "Immédiate : les cinq lots sont loués, les loyers rentrent dès la signature",
                "risque": "modéré — le risque est celui des baux, dont quatre ne sont pas détaillés, et celui "
                          "d'un immeuble de six étages à rafraîchir",
            },
            {
                "strategie": "Création des deux T2 supplémentaires (R+1 et R+4)",
                "lots": 7,
                "performance": "Fait passer le rendement net d'IS de 5,6 % à environ 7,3 % si les travaux "
                               "tiennent dans 45 000 € et si les deux logements se louent 470 €",
                "valeur_sortie": "Deux lots de plus à la revente, sur un marché où le mètre carré d'appartement "
                                 "se négocie 2 200 à 2 400 €",
                "faisabilite": "Aucun devis, aucun plan, aucune autorisation : c'est un projet, pas une "
                               "opération chiffrée",
                "risque": "élevé sur les travaux (création de logements dans l'ancien, réseaux, évacuations, "
                          "isolation) et sur le délai de relocation",
            },
            {
                "strategie": "Revente à l'unité des cinq lots après division",
                "lots": 5,
                "performance": "Le mètre carré d'appartement se négocie 2 200 à 2 400 € à Brignoles contre "
                               "685 €/m² payés pour l'ensemble : la marge théorique est là, la faisabilité n'y est pas",
                "valeur_sortie": "Dépend d'une division en lots de copropriété, qui suppose l'accord de la "
                                 "copropriété et un géomètre",
                "faisabilite": "Longue et incertaine : l'immeuble est en copropriété avec l'immeuble accolé",
                "risque": "élevé — c'est une opération de marchand de biens déguisée en immeuble de rapport",
            },
        ],
        "attractivite": [
            {
                "dimension": "transports",
                "score": 5,
                "justification": "Centre de Brignoles : la commune est traversée par la nationale 7 et desservie "
                                 "par les cars régionaux ; pas de gare, les déplacements se font en voiture.",
            },
            {
                "dimension": "commerces",
                "score": 7,
                "justification": "Cœur de la vieille ville, proche des parkings et des écoles selon l'annonce : "
                                 "commerces et services à pied, ce qui porte la demande locative des T2.",
            },
            {
                "dimension": "ecoles",
                "score": 7,
                "justification": "Collège public Jean Moulin à 870 m et collège privé Sainte-Jeanne-d'Arc à "
                                 "409 m, écoles primaires publiques et privées dans le même rayon : c'est un "
                                 "secteur pavé pour les familles, mais aussi pour les personnels.",
            },
            {
                "dimension": "securite",
                "score": 5,
                "justification": "Vieille ville ancienne, bâti dense et hétérogène : cadre de vie correct mais "
                                 "sans marque de standing, et un immeuble de six étages à rafraîchir.",
            },
            {
                "dimension": "demande_locative",
                "score": 7,
                "justification": "Les cinq lots sont loués et les locataires à jour : la demande existe et elle "
                                 "est constatée sur ce bien. Brignoles est la ville-centre du centre Var, avec "
                                 "un bassin d'emploi administratif, hospitalier et commercial qui alimente le "
                                 "locatif courant.",
            },
            {
                "dimension": "dynamisme",
                "score": 5,
                "justification": "Marché profond mais peu dynamique : médiane DVF 2 393 €/m² pour les "
                                 "appartements sur 419 mutations, avec des valeurs hétérogènes (Q1 1 811 / "
                                 "Q3 3 214). C'est un marché de rendement, pas de plus-value rapide.",
            },
        ],
        "risques": [
            {
                "facteur": "Le détail des loyers par lot n'est pas communiqué",
                "detail": "L'agence annonce 26 630 €/an pour cinq lots, sans dire ce que paie chacun. Or les "
                          "repères du marché brignolais (T2 de 35 à 50 m² loués 490 à 520 €) rendent le total "
                          "difficile à répartir : quatre T2 au marché absorbent 1 850 à 2 000 € par mois, "
                          "laissant 220 à 370 € pour un local commercial de plus de 140 m². Tout le dossier "
                          "dépend de la lecture de cette répartition — marge de revalorisation d'un côté, "
                          "loyers sous le marché de l'autre.",
                "severite": 4,
            },
            {
                "facteur": "« Rénovation nécessaire » sur un immeuble de six étages",
                "detail": "Le DPE est classé E et l'état intérieur est annoncé « rénovation nécessaire ». Dans un "
                          "immeuble de centre ancien en copropriété avec un immeuble accolé, les postes qui "
                          "coûtent (toiture, façade, colonnes, électricité des communs, étanchéité de la "
                          "terrasse) ne se voient pas dans 492 € de charges annuelles. Un appel de fonds voté "
                          "efface deux ans de loyer net.",
                "severite": 4,
            },
            {
                "facteur": "Charges annoncées invraisemblablement basses",
                "detail": "123 € par trimestre pour six étages, un local commercial et une copropriété partagée "
                          "ne peut pas être la charge de l'ensemble. Si ce montant s'entend par lot, la charge "
                          "réelle approche 2 500 €/an, soit 0,6 point de rendement net en moins. À faire "
                          "confirmer écrit par écrit, avec le budget prévisionnel et les trois derniers PV.",
                "severite": 3,
            },
            {
                "facteur": "Local commercial : bail, preneur et destination",
                "detail": "Un local de plus de 140 m² en rez-de-chaussée de vieille ville est le lot qui peut le "
                          "plus facilement rester vide, et le seul dont la valeur dépend d'une activité. Ni "
                          "l'activité, ni la durée du bail, ni l'échéance, ni la destination au règlement ne sont "
                          "données. En cas de départ, la relocation d'une telle surface prend des mois.",
                "severite": 4,
            },
            {
                "facteur": "Copropriété avec l'immeuble accolé",
                "detail": "L'immeuble n'est pas autonome : les décisions de travaux, le ravalement, la toiture et "
                          "l'étanchéité se prennent avec les copropriétaires voisins. C'est une contrainte de "
                          "gouvernance qui pèse sur le calendrier des travaux et sur la capacité à décider seul.",
                "severite": 3,
            },
            {
                "facteur": "Écart au plafond de rendement",
                "detail": "Au prix affiché, le rendement net après IS sur prix de revient ressort à 5,6 % pour un "
                          "plancher de 5 % : le dossier passe tout juste le seuil, et il le repasse sous la barre "
                          "dès que les charges de copropriété sont corrigées à la hausse ou qu'un lot se vide.",
                "severite": 3,
            },
            {
                "facteur": "Création de deux logements : autorisations et devis",
                "detail": "L'annonce valorise la « possibilité de faire deux appartements T2 de plus en R+1 et "
                          "R+4 » sans plan, sans devis et sans vérification du PLU ni du règlement de "
                          "copropriété. Tant que ces trois pièces manquent, cette valeur ne peut pas être payée.",
                "severite": 3,
            },
            {
                "facteur": "Non accessible aux personnes à mobilité réduite",
                "detail": "Mentionné dans les caractéristiques : le rez-de-chaussée commercial n'est pas "
                          "accessible PMR. Pour une activité de service recevant du public, c'est un obstacle "
                          "réglementaire à instruire avant de compter sur ce lot comme locatif de longue durée.",
                "severite": 2,
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
    print(f"NOTE {n} — {v} | plafond {plafond:.0f} € | cible {cible:.0f} € | {detail}")
    print(f"annuité {PRIX*ANNUITE:.0f} €/mois | solde {f['net_apres_is']/12 - PRIX*ANNUITE:+.0f} €/mois | "
          f"autofinancement {(f['net_apres_is']/12)/ANNUITE:.0f} €")
    if not ecrire:
        print("\n(base non modifiée — relancer avec --ecrire)")
        return
    data = json.loads(BASE.read_text(encoding="utf-8"))
    avant = len(data["analyses"])
    data["analyses"] = [a for a in data["analyses"] if a["slug"] != SLUG]
    data["analyses"].append(RECORD)
    BASE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nanalyses.json : {avant} -> {len(data['analyses'])} dossiers (slug {SLUG})")


if __name__ == "__main__":
    main()
