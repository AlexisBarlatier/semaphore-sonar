#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saisie du record — Immeuble 5 studios meublés + garage, La Roseraie / Saint-Jean-du-Var, Toulon.

SeLoger 26YVBFMFBW3E — Capifrance, Hubert Pieraccini, réf. 975456 / 340931130931 —
299 000 € — relevé le 24/10/2026. Exclusivité, annonce neuve.
Idempotent : le slug est filtré avant append.
"""
import copy
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

from analyse_app import engine, schema, scoring  # noqa: E402

SLUG = "2026-10-24-immeuble-5-studios-toulon-saint-jean"
BASE = os.path.join(RACINE, "analyses", "analyses.json")

PRIX = 299000.0
FRAIS = 23920.0          # 8 %, régime ancien, honoraires vendeur
TRAVAUX = 0.0
LOYER_STUDIO = 410.0     # médiane des comparables du quartier, 18 m², hors charges (449 € annoncés = CC)
TF = 2000.0
SURFACE = 90.0
VALEUR = 300000.0


def eur(v):
    return f"{v:,.0f}".replace(",", " ") + " €"


def fiche():
    return {
        "slug": SLUG,
        "date_analyse": "2026-10-24",
        "date_maj": "2026-10-24",
        "titre": "Immeuble 5 studios meublés et garage — Saint-Jean-du-Var, Toulon (83100)",
        "bien": {
            "type_bien": "immeuble",
            "sous_type": "immeuble de rapport",
            "type_detail": "Immeuble sur trois niveaux dans une impasse au calme : garage et un studio "
                           "en rez-de-chaussée, deux studios au premier, deux studios au deuxième. Cinq "
                           "studios meublés d'environ 18 m², cinq compteurs électriques et cinq "
                           "compteurs d'eau individuels, un garage. Monopropriété. DPE C pour quatre "
                           "lots et D pour le cinquième, GES A.",
            "neuf": False,
            "adresse": {
                "texte": "La Roseraie / Saint-Jean-du-Var, Toulon (83100) — adresse exacte non "
                         "communiquée (petite impasse au calme)",
                "ville": "Toulon",
                "code_postal": "83100",
                "quartier": "Saint-Jean-du-Var / La Roseraie",
            },
            "surfaces": {"texte": "90 m² annoncés dans le titre, « 100 m² environ » dans le descriptif "
                                  "du même document : deux surfaces pour le même immeuble. Cinq studios "
                                  "d'environ 18 m² plus un garage, en monopropriété, sans mesurage "
                                  "Carrez par lot. Le prix au mètre carré varie de 2 990 € (sur 100 m²) "
                                  "à 3 322 € (sur 90 m²) selon le chiffre retenu"},
            "lots": {"count": 6,
                     "nature": "Cinq studios meublés et un garage. Monopropriété, cinq compteurs "
                               "électriques et cinq compteurs d'eau individuels. L'annonce parle aussi "
                               "d'un « syndic professionnel » alors qu'il n'y a pas de copropriété : "
                               "c'est un gestionnaire, pas un syndic, et le point est à clarifier",
                     "lots_distincts": 6},
            "copro": {"charges_annuelles_euros": 0.0,
                      "charges_source": "Aucune copropriété : monopropriété revendiquée deux fois dans "
                                        "l'annonce. Pas de charges de copropriété, pas de "
                                        "mutualisation des travaux"},
            "travaux": {
                "montant_euros": TRAVAUX,
                "nature": "« Aucun travaux à prévoir » et cinq DPE bons (quatre C, un D), sans devis ni "
                          "facture. Sur un immeuble dont l'année de construction n'est pas donnée, "
                          "c'est une déclaration du vendeur. Toiture, façade, électricité des communs "
                          "et chauffe-eau des cinq studios se vérifient : budget retenu à zéro, "
                          "6 000 € en Worst",
            },
        },
        "annonce": {
            "plateforme": "seloger",
            "url": "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/toulon-83000/26YVBFMFBW3E",
            "prix_affiche_euros": PRIX,
            "prix_retenu_euros": PRIX,
            "prix_statut": "affiche",
            "vendeur": "Capifrance, Hubert Pieraccini (SAS Pieraccini Hubert, RCS Montpellier 521753152), "
                       "réf. 975456 — honoraires à la charge du vendeur. Exclusivité",
        },
        "marche": {
            "valeur": {
                "basse_euros": 250000.0,
                "haute_euros": 340000.0,
                "retenue_euros": VALEUR,
                "source": "DVF Toulon (83137) 2021-2025 : studios de 9 à 20 m², 288 ventes, médiane "
                          "3 809 €/m², premier quartile 3 132, troisième 4 494, prix médian 64 950 € ; "
                          "appartements de 20 à 30 m², 1 032 ventes, médiane 3 106 €/m² ; 60 à 100 m², "
                          "5 971 ventes, médiane 2 396 €/m². Sur 90 m² de micro-lots, cela donne "
                          "280 000 à 343 000 € : 300 000 € retenus, au milieu. Le prix affiché à "
                          "3 322 €/m² est donc dans la fourchette des studios de la commune, mais "
                          "c'est le prix d'un produit d'investisseur, pas celui des murs : dans les "
                          "quartiers populaires de l'Est toulonnais, les appartements se vendent "
                          "1 550 à 2 100 €/m² (comparables internes : 85 m² à 132 000 € à "
                          "Saint-Jean-du-Var, 77 m² à 160 000 €, 63 m² à 99 000 € à La Rode). La "
                          "valeur est portée par les cinq baux, pas par le bâti",
                "confiance": "moyenne",
            },
            "loyers": [
                {"lot": "Cinq studios meublés d'environ 18 m²",
                 "quantite": 5,
                 "loyer_mensuel_euros": LOYER_STUDIO,
                 "occupe": True,
                 "note": "Aucun loyer à l'unité n'est donné : l'annonce affiche « une très belle "
                         "rentabilité (9 %) », soit 26 910 €/an et 448,60 € par studio, calculés sur "
                         "le prix demandé. Relevé de comparables du quartier, 18 à 22 m² meublés, au "
                         "24/10/2026 : 18 m² à Saint-Jean-du-Var, résidence de 2000, DPE C, ascenseur, "
                         "428 € CC (374 € HC, 20,8 €/m²) ; 20 m² à Saint-Jean-du-Var, copropriété de "
                         "1900, 440 € CC (410 € HC) ; 21,6 m² à Saint-Jean-du-Var, résidence fermée, "
                         "553 € CC (513 € HC, 23,8 €/m²) ; 21 m² à Toulon, 2008, 480 € CC (450 € HC) ; "
                         "20 m² à Toulon, 2006, DPE B, 550 € CC (520 € HC) ; 20 m² au Vert Coteau "
                         "rénové en 2026, 525 € CC (510 € HC). Médiane des comparables : 23,8 €/m² CC "
                         "et 22,6 €/m² HC, soit 407 € hors charges pour 18 m². Les 448,60 € font "
                         "24,9 €/m² : au-dessus du prix haut du quartier La Roseraie (23,3 €/m², "
                         "SeLoger). Et si ce loyer est charges comprises, comme tous les "
                         "comparables, l'assiette réelle tombe à 410-420 € par studio. Retenu "
                         "410 € hors charges : la médiane du quartier, pas l'annonce"},
            ],
            "notes": "Assiette : médiane des comparables du quartier hors charges, et non la rentabilité "
                     "annoncée. Le vendeur présente 9 % sur un loyer de 448,60 € qui n'est pas qualifié "
                     "charges comprises ou hors charges ; les comparables du quartier sont tous des "
                     "loyers CC, dont la conversion donne 374 à 520 € HC selon la surface. À 410 € le "
                     "brut tombe à 8,23 %, à 400 € à 8,03 %, à 375 € à 7,53 %. Aucune quittance, aucun "
                     "bail, aucun état des lieux au dossier.",
        },
        "hypotheses": {
            "vacance_base_pct": 7.0,
            "vacance_best_pct": 3.0,
            "vacance_worst_pct": 15.0,
            "taux_placement_reserve_pct": 2.84,
            "quote_part_bati_pct": 90.0,
            "vacance_justification": "Cinq studios meublés : rotation plus rapide que des baux nus, "
                                     "relocation entre deux locataires à chaque départ. 7 % en base "
                                     "(un studio vide un peu plus de quatre mois par an sur "
                                     "l'ensemble), 3 % en best, 15 % en worst (deux studios vides "
                                     "simultanément, ce qui arrive sur un produit étudiant en fin "
                                     "d'année universitaire)",
            "charges": {
                "charges_copro_annuelles_euros": 0.0,
                "charges_copro_commentaire": "Monopropriété, aucune charge de copropriété. Les cinq "
                                             "compteurs individuels d'eau et d'électricité évitent le "
                                             "poste le plus dangereux de ce type de produit : des "
                                             "charges collectives refacturées au forfait",
                "taxe_fonciere_annuelle_euros": TF,
                "taxe_fonciere_commentaire": "2 000 €/an ESTIMÉS — aucun avis communiqué. Six lots "
                                            "dont cinq loués, dans un immeuble de 90 à 100 m² : la "
                                            "fourchette communale pour ce format tourne autour de "
                                            "1 800 à 2 400 €. L'avis réel est à exiger",
                "entretien_annuel_euros": 3860.0,
                "entretien_commentaire": "3 860 €/an : gestion locative à 7 % des loyers (1 884 €, "
                                         "cinq baux meublés à renouveler), provision d'impayés à 4 % "
                                         "(1 076 €, distincte de la vacance) et 900 € d'entretien "
                                         "courant (cinq chauffe-eau, cinq salles d'eau, mobilier à "
                                         "remplacer)",
                "pno_annuelle_euros": 750.0,
                "comptabilite_annuelle_euros": 0.0,
            },
            "frais_acquisition_euros": FRAIS,
            "frais_acquisition_commentaire": "8 % du prix (23 920 €), régime ancien ; honoraires à la "
                                             "charge du vendeur, donc hors base de calcul",
        },
        "analyse": {
            "branche": "residentiel",
            "type_operation": "locatif",
            "strategie_retenue": {
                "nom": "Conservation en bloc : cinq studios meublés et un garage",
                "code": "ld-meuble",
                "lots": 6,
            },
            "strategies_explorees": [],
            "attractivite": [
                {"dimension": "transports", "score": 7,
                 "justification": "Toulon Est, réseau Mistral dense, accès rapide au centre et à la "
                                  "gare. Le locataire étudiant ou jeune actif vit sans voiture, ce "
                                  "qui est exactement la clientèle du produit."},
                {"dimension": "commerces", "score": 6,
                 "justification": "Commerces de proximité et services dans le quartier, centre-ville "
                                  "de Toulon à quelques minutes. Pas un emplacement touristique ni "
                                  "bourgeois : le commerce est fonctionnel, pas attractif."},
                {"dimension": "ecoles", "score": 7,
                 "justification": "Collège Voltaire à moins de 100 m, Institution Notre-Dame et "
                                  "établissements privés à 400 m, campus universitaire et hôpital "
                                  "Sainte-Musse à proximité. C'est la demande qui porte les studios."},
                {"dimension": "securite", "score": 3,
                 "justification": "Saint-Jean-du-Var est un quartier de la politique de la ville — QPV "
                                  "dans la géographie prioritaire, QVA dans le contrat de ville "
                                  "2024-2030 de la métropole. Chômage élevé, parc dégradé, trafics "
                                  "documentés sur une partie du secteur. La Roseraie est un secteur "
                                  "résidentiel plus calme, mais la réputation du quartier pèse sur la "
                                  "relocation et sur la revente."},
                {"dimension": "demande_locative", "score": 7,
                 "justification": "Toulon affiche 3,4 % de vacance et 3 000 transactions par an ; la "
                                  "demande de petites surfaces meublées y est structurelle — "
                                  "étudiants, jeunes actifs, mobilité professionnelle. C'est le point "
                                  "fort du produit, et il ne compense pas le point faible du quartier."},
                {"dimension": "dynamisme", "score": 5,
                 "justification": "Deuxième ville du Var, emploi métropolitain, mais 14 % de chômage "
                                  "et dix quartiers prioritaires. Le marché est profond et liquide, "
                                  "pas porteur : la plus-value n'est pas le moteur."},
            ],
            "risques": [
                {"facteur": "Rentabilité annoncée de 9 % sans une seule quittance", "severite": 5,
                 "detail": ""},
                {"facteur": "Quartier prioritaire : Saint-Jean-du-Var", "severite": 4,
                 "detail": "Saint-Jean-du-Var figure dans la géographie prioritaire de la ville (QPV "
                           "de la liste préfectorale, QVA du contrat de ville 2024-2030 de la "
                           "métropole). Ce n'est pas un critère de confort : c'est le risque de ne pas "
                           "pouvoir visiter, faire réparer ni relouer sans y aller, et de revendre "
                           "dans un marché étroit. La Roseraie est un secteur plus résidentiel que le "
                           "cœur du quartier, mais l'adresse exacte n'est pas donnée et la "
                           "qualification se fait rue par rue, sur place, un samedi après-midi."},
                {"facteur": "Cinq micro-lots meublés : gestion et rotation", "severite": 3,
                 "detail": "Cinq baux meublés de 18 m², cinq états des lieux par rotation, cinq "
                           "relocations potentielles par an. La vacance et les impayés ne se lissent "
                           "pas : un studio vide, c'est 9 % des revenus. Le produit exige un "
                           "gestionnaire, et la gestion déléguée coûte 7 à 9 % sur ce format."},
                {"facteur": "Prix au-dessus du bâti, valeur portée par les baux", "severite": 3,
                 "detail": "À 3 322 €/m², l'immeuble se paie au prix des studios de Toulon, quand les "
                           "appartements du même quartier se vendent 1 550 à 2 100 €/m². La valeur "
                           "tient aux cinq baux : si deux studios se relouent 100 € plus bas, la "
                           "valeur de l'actif baisse de 25 000 à 30 000 € par capitalisation. C'est un "
                           "actif de revenu, pas un actif de revente."},
                {"facteur": "Surfaces contradictoires et année de construction absente", "severite": 3,
                 "detail": "90 m² dans le titre, « 100 m² environ » dans le descriptif, cinq studios "
                           "d'environ 18 m² : le compte ne tombe pas et le garage n'est pas compté. "
                           "Plans, mesurage et DDT par lot à exiger, avec l'année de construction et "
                           "l'état de la toiture."},
                {"facteur": "« Syndic professionnel » sur une monopropriété", "severite": 2,
                 "detail": "L'annonce dit à la fois « monopropriété » et « géré par un syndic "
                           "professionnel ». Il n'y a pas de syndic sans copropriété : c'est un "
                           "gestionnaire, ou l'annonce se trompe. À clarifier, avec les contrats de "
                           "gestion et les cinq baux."},
            ],
        },
    }


def variante(r, loyer=None, vacance=None, travaux=None, prix=None, entretien=None):
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
        rr["hypotheses"]["frais_acquisition_euros"] = round(prix * 0.08)
    return rr


def annuite(assiette, taux=0.038, mois=240, ass=0.0034):
    i = taux / 12.0
    return assiette * 0.9 * i / (1 - (1 + i) ** -mois) + assiette * 0.9 * ass / 12.0


def main():
    r = fiche()
    c = engine.compute(r)

    c_400 = engine.compute(variante(r, loyer=400.0))
    c_375 = engine.compute(variante(r, loyer=375.0))
    c_480 = engine.compute(variante(r, loyer=480.0))

    r["analyse"]["strategies_explorees"] = [
        {"strategie": "Conservation en bloc : cinq studios meublés et un garage",
         "lots": 6,
         "performance": f"{eur(LOYER_STUDIO * 5)}/mois, soit 9 % brut sur le prix affiché, pour un "
                        f"rendement net après IS de {c['rendements']['net_sur_revient_pct']:.2f} % "
                        f"sur un prix de revient de {eur(c['prix_revient_total'])}. Le brut est réel "
                        f"si les baux le sont : c'est toute la question du dossier",
         "valeur_sortie": f"Revente à l'unité de cinq studios : 5 x 18 m² x 3 809 €/m² = "
                          f"{eur(5 * 18 * 3809)}, soit {eur(5 * 18 * 3809 - c['prix_revient_total'])} "
                          f"de mieux que le revient — mais à condition de vendre cinq lots meublés "
                          f"loués, ce qui prend du temps et se paie en frais",
         "faisabilite": "Immédiate : cinq baux en place, monopropriété, aucun travaux annoncé",
         "risque": "élevé — la rentabilité annoncée n'est pas documentée et le quartier est un QPV"},
        {"strategie": "Bascule en location nue des cinq studios",
         "lots": 5, "rdt": None,
         "performance": f"Assiette ramenée à environ 375 € par studio, soit "
                        f"{(c_375['rendements']['net_sur_revient_pct']):.2f} % net après IS : "
                        f"la location nue rapporte moins que le meublé, sans réduire la vacance dans "
                        f"un quartier où la demande est étudiante et meublée",
         "valeur_sortie": f"{eur(5 * 18 * 3809)} à la revente, comme en meublé",
         "faisabilite": "Changement de nature de bail, mobilier à sortir, relocation à faire",
         "risque": "élevé — on perd le loyer sans gagner en sécurité"},
        {"strategie": "Revente à la découpe des cinq studios",
         "lots": 5, "rdt": None,
         "performance": f"Produit de revente théorique {eur(5 * 18 * 3809)}, contre "
                        f"{eur(c['prix_revient_total'])} de revient : une marge apparente d'environ "
                        f"20 000 €, avant frais de vente, portage et vacance de commercialisation. "
                        f"Ce n'est pas une opération, c'est un lot de consolation",
         "valeur_sortie": f"{eur(5 * 18 * 3809)} au prix médian des studios de Toulon",
         "faisabilite": "Cinq ventes de lots meublés loués, 12 à 24 mois de portage, structure "
                        "commerciale",
         "risque": "élevé — la marge ne survit pas aux frais"},
    ]

    r["analyse"]["risques"][0]["detail"] = (
        f"Le vendeur annonce 9 % de rentabilité, soit 2 243 €/mois et 448,60 € par studio, calculés "
        f"sur le prix demandé, sans qu'aucune quittance ne soit au dossier. Or les comparables du "
        f"quartier, 18 à 22 m² meublés, se louent 428 à 553 € charges comprises, soit une médiane de "
        f"22,6 €/m² hors charges et environ 407 € pour 18 m². À l'assiette retenue de "
        f"{eur(LOYER_STUDIO)} par studio, le rendement net après IS ressort à "
        f"{c['rendements']['net_sur_revient_pct']:.2f} % pour un prix de revient de "
        f"{eur(c['prix_revient_total'])}. À 400 €, il tombe à "
        f"{(c_400['rendements']['net_sur_revient_pct']):.2f} %. Les 448,60 € font 24,9 €/m² : "
        f"au-dessus du prix haut du quartier La Roseraie (23,3 €/m², SeLoger). Le prix ne se paie que "
        f"sur les quittances, et elles ne sont pas là."
    )

    errs = schema.validate_record(r)
    if errs:
        raise SystemExit(f"record invalide : {errs}")
    print("champs_manquants :", schema.champs_manquants(r))

    note, verdict, comp = scoring.note_et_verdict(r, c)
    if note is None:
        raise SystemExit("note non calculable")
    plafond, contrainte = scoring.prix_plafond(r)

    with open(BASE, encoding="utf-8") as fh:
        data = json.load(fh)
    avant = len(data["analyses"])
    data["analyses"] = [a for a in data["analyses"] if a["slug"] != SLUG]
    data["analyses"].append(r)
    data["meta"]["count"] = len(data["analyses"])
    with open(BASE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"base : {avant} → {len(data['analyses'])} fiches")

    def fmt(x):
        return "aucun" if x is None else f"{x:,.0f}".replace(",", " ")

    print(f"note {note} / {verdict} ({comp.get('plafonds')})")
    print(f"  performance {c['rendements']['net_sur_revient_pct']:.2f} % | brut "
          f"{LOYER_STUDIO * 5 * 12 / PRIX * 100:.2f} % | ratio coût/valeur "
          f"{c['ratio_cout_valeur']:.3f}")
    print(f"  EBE {fmt(c['fiscal']['ebe'])} | net après IS {fmt(c['fiscal']['net_apres_is'])} | "
          f"revient {fmt(c['prix_revient_total'])}")
    print(f"  prix plafond {fmt(plafond)} € ({contrainte})")
    print(f"  solde mensuel standard : {c['fiscal']['net_apres_is'] / 12 - annuite(PRIX):+.0f} €/mois")
    print(f"  400 €/studio {c_400['rendements']['net_sur_revient_pct']:.2f} % | 375 € "
          f"{c_375['rendements']['net_sur_revient_pct']:.2f} % | 480 € "
          f"{c_480['rendements']['net_sur_revient_pct']:.2f} %")


if __name__ == "__main__":
    main()
