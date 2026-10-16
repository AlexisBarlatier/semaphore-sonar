#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saisie du record — Studio 26,64 m² loué sous bail commercial, Toulon Porte d'Italie.

LeBonCoin 3229330779 (Le Revenu Pierre, réf. 8238f-toulon-gsa) — 46 920 € — 16/10/2026.
Double diffusion relevée : gensdeconfiance, même référence, chiffres clés détaillés.

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

SLUG = "2026-10-16-studio-26m2-toulon-porte-italie-gere"
BASE = os.path.join(RACINE, "analyses", "analyses.json")

PRIX = 46920.0            # 45 600 € FAI HT + 1 320 € de TVA, affiché TTC
FRAIS = 3754.0            # frais annoncés par le vendeur
SURFACE = 26.64
LOYER_BAIL = 3420.0 / 12          # 285 €/mois HT, bail en cours
LOYER_MARCHE = 450.0              # relocation meublée directe après reprise
TRAVAUX_REPRISE = 4000.0          # remise en état après 10 ans d'exploitation étudiante


def eur(v):
    return f"{v:,.0f}".replace(",", " ") + " €"


def fiche():
    return {
        "slug": SLUG,
        "date_analyse": "2026-10-16",
        "date_maj": "2026-10-16",
        "titre": "Studio de 26,64 m² loué sous bail commercial à un exploitant — Campus Porte d'Italie, "
                 "Toulon (83000)",
        "bien": {
            "type_bien": "appartement",
            "sous_type": "studio",
            "type_detail": "T1 de 26,64 m² Carrez, meublé, dans une résidence étudiante exploitée par "
                           "GSA Résidences, quartier Porte d'Italie, à proximité du campus. DPE D, "
                           "GES B. Vendus meublés, occupés, sous bail commercial consenti à "
                           "l'exploitant : aucune occupation personnelle n'est possible, l'acquéreur "
                           "perçoit un loyer que le logement soit occupé ou non.",
            "neuf": False,
            "adresse": {
                "texte": "Quartier Porte d'Italie, Toulon (83000) — résidence étudiante, adresse "
                         "exacte non communiquée",
                "ville": "Toulon",
                "code_postal": "83000",
                "quartier": "Porte d'Italie",
            },
            "surfaces": {"texte": "26,64 m² Carrez (T1), 26 m² annoncés au portail"},
            "lots": {"count": 1,
                     "nature": "Un studio dans une résidence gérée : l'acquéreur devient bailleur de "
                               "locaux commerciaux vis-à-vis de l'exploitant, qui sous-loue aux "
                               "étudiants. Le lot est vendu meublé et occupé",
                     "lots_distincts": 1},
            "copro": {"charges_annuelles_euros": 380.0,
                      "charges_source": "380 € HT/an de charges non récupérables annoncées par le "
                                        "vendeur. Aucun budget prévisionnel ni PV d'assemblée "
                                        "générale communiqué : le poste est à vérifier sur les "
                                        "appels de fonds réels"},
            "travaux": {"montant_euros": TRAVAUX_REPRISE,
                        "nature": "Aucun travail à la charge de l'acquéreur tant que le bail court : "
                                  "l'entretien courant (article 605 du code civil) incombe à "
                                  "l'exploitant, les grosses réparations (606) au propriétaire. "
                                  "4 000 € provisionnés pour la remise en état du studio au départ de "
                                  "l'exploitant, après dix ans d'exploitation étudiante : peintures, "
                                  "sols, sanitaires, mobilier"},
        },
        "annonce": {
            "plateforme": "leboncoin",
            "url": "https://www.leboncoin.fr/ad/ventes_immobilieres/3229330779",
            "url_secondaire": "https://gensdeconfiance.com/fr/ui/post/realestate__sale/72b9b28e-5357-48c8-82d9-4b9c4c8d0f49",
            "prix_affiche_euros": PRIX,
            "prix_retenu_euros": PRIX,
            "prix_statut": "affiche",
            "vendeur": "Le Revenu Pierre (SIRET 49960425400031), spécialiste de la revente de LMNP en "
                       "résidences gérées, réf. 8238f-toulon-gsa — honoraires partagés entre l'acheteur "
                       "et le vendeur. Le bien est diffusé simultanément sur LeBonCoin et sur Gens de "
                       "Confiance, aux mêmes chiffres",
        },
        "marche": {
            "valeur": {
                "basse_euros": 58000.0,
                "haute_euros": 76000.0,
                "retenue_euros": 68000.0,
                "source": "DVF Toulon (83137) : appartements de moins de 30 m², médiane 3 351 €/m², "
                          "premier quartile 2 760, sur 737 ventes — soit 73 500 à 89 300 € pour "
                          "26,64 m². Comparables directs de la même famille, studios de résidences "
                          "gérées à Toulon : 21 m² annoncés 58 164 € (2 770 €/m²) et un studio GSA "
                          "Résidences Mayol à 57 500 € (2 875 €/m²). Retenue 68 000 €, soit 2 553 €/m², "
                          "sous le premier quartile communal : le studio porte un bail qui arrive à "
                          "terme le 31/12/2027 avec un loyer 40 % sous le marché, et le marché de "
                          "revente de ces lots est un marché d'investisseurs, étroit par construction",
                "confiance": "moyenne",
            },
            "loyers": [
                {"lot": "Studio meublé loué à l'exploitant par bail commercial",
                 "quantite": 1,
                 "loyer_mensuel_euros": 285.0,
                 "occupe": True,
                 "note": "Loyer en place : 3 420 € HT/an, soit 285 €/mois et 10,7 €/m², sous bail "
                         "commercial 3/6/9 du 01/01/2018 au 31/12/2027 avec GSA Résidences, indexé. "
                         "C'est un loyer très inférieur au marché du studio meublé à Toulon : relevé "
                         "du 16/10/2026 — studio meublé de 18 m² à Sainte-Anne à 589 € charges "
                         "comprises (33 €/m²), T2 meublé de 37 m² en basse ville à 680 € (18 €/m²), "
                         "soit une tranche de 15 à 20 €/m² pour un meublé de cette taille, donc 400 à "
                         "530 €/mois. Variante chiffrée hors assiette : reprise du studio et location "
                         f"meublée directe à {eur(LOYER_MARCHE)}/mois après le départ de l'exploitant, "
                         "avec 4 000 € de remise en état"},
            ],
            "notes": "Assiette EN PLACE : le loyer est garanti par le bail commercial tant que "
                     "l'exploitant paie, que le logement soit occupé ou non. Mais ce bail expire le "
                     "31/12/2027, soit dans quatorze mois : le dossier n'est pas un rendement long, "
                     "c'est un coupon court adossé à une option sur la reprise du studio. Aucune vacance "
                     "n'est retenue : un bail commercial fait payer le loyer que le logement soit "
                     "occupé ou non, et c'est la contrepartie du loyer bas consenti au preneur. Le "
                     "risque n'est donc pas l'absence de locataire, c'est la signature de "
                     "l'exploitant : il est traité au scénario Worst, pas en provision "
                     "systématique",
        },
        "hypotheses": {
            "vacance_base_pct": 0.0,
            "vacance_best_pct": 0.0,
            "vacance_worst_pct": 12.0,
            "taux_placement_reserve_pct": 2.84,
            "quote_part_bati_pct": 90.0,
            "vacance_justification": "Aucune vacance en base ni en best : un bail commercial fait "
                                     "payer le loyer que le logement soit occupé ou non, c'est la "
                                     "contrepartie du loyer bas. Le risque est la signature du "
                                     "preneur, pas l'occupation du lot, et il se traite en scénario "
                                     "Worst (12 % — défaillance en cours de bail, loyers suspendus "
                                     "pendant la procédure et studio à remettre en état)",
            "charges": {
                "charges_copro_annuelles_euros": 380.0,
                "charges_copro_commentaire": "380 € HT/an de charges non récupérables annoncées par le "
                                             "vendeur, à confirmer sur les appels de fonds",
                "taxe_fonciere_annuelle_euros": 642.0,
                "taxe_fonciere_commentaire": "642 €/an annoncés par le vendeur, aucun avis communiqué. "
                                            "C'est 18,8 % du loyer annuel : pour un studio occupé, le "
                                            "poste est lourd, et l'avis de taxe foncière est à exiger",
                "entretien_annuel_euros": 0.0,
                "entretien_commentaire": "Aucune gestion à notre charge : l'exploitant assure "
                                         "l'entretien courant (605) et la commercialisation. Le "
                                         "propriétaire garde les grosses réparations (606), qui ne se "
                                         "provisionnent pas dans le compte courant mais dans la "
                                         "réserve travaux du moteur",
                "pno_annuelle_euros": 150.0,
                "comptabilite_annuelle_euros": 0.0,
            },
            "frais_acquisition_euros": FRAIS,
            "frais_acquisition_commentaire": "3 754 € annoncés par le vendeur, soit 8,2 % du prix HT. "
                                             "Dans ce schéma d'acquisition, le 1 320 € de TVA affichée comme "
                                             "récupérable se récupère par l'acquéreur assujetti et se "
                                             "paie par l'acquéreur particulier : à faire trancher dans "
                                             "l'acte, la base HT ou TTC n'est pas indifférente",
        },
        "analyse": {
            "branche": "residentiel",
            "type_operation": "locatif",
            "strategie_retenue": {
                "nom": "Portage du bail commercial en place, puis reprise du studio et location "
                       "meublée directe à l'échéance",
                "code": "ld-meuble",
                "lots": 1,
            },
            "strategies_explorees": [],
            "attractivite": [
                {"dimension": "transports", "score": 8,
                 "justification": "Porte d'Italie est le secteur du campus toulonnais et le mieux "
                                  "desservi de la ville : gare de Toulon à quelques minutes, réseau "
                                  "de bus dense, accès direct aux axes vers l'est. Un studio destiné "
                                  "aux étudiants se loue sur cette desserte avant toute autre chose."},
                {"dimension": "commerces", "score": 7,
                 "justification": "Quartier du campus : commerces de proximité, restauration, "
                                  "supermarchés et services dans le périmètre piéton du campus. "
                                  "C'est ce qui permet de relouer un meublé sans voiture."},
                {"dimension": "ecoles", "score": 9,
                 "justification": "Le moteur de la demande est là : université de Toulon, IUT, "
                                  "écoles d'ingénieurs et de gestion regroupés sur le secteur Porte "
                                  "d'Italie et La Garde. La demande étudiante est structurelle, et "
                                  "c'est exactement la clientèle que vise ce studio."},
                {"dimension": "securite", "score": 5,
                 "justification": "Quartier animé et très passant, avec la délinquance d'un secteur "
                                  "étudiant la nuit. L'exploitation en résidence gérée limite le "
                                  "risque locatif, elle ne le supprime pas : la remise en état et les "
                                  "impayés étudiants restent chez l'exploitant tant que le bail court, "
                                  "et reviennent au propriétaire après."},
                {"dimension": "demande_locative", "score": 8,
                 "justification": "Demande étudiante soutenue et renouvelée chaque année, sur la "
                                  "seule ville du Var où elle est concentrée. Relevé du 16/10/2026 : "
                                  "31 studios meublés proposés à la location sur Toulon, de 18 à "
                                  "37 m², entre 18 et 33 €/m² : la demande est là, l'offre aussi, ce "
                                  "qui plafonne le loyer par le haut."},
                {"dimension": "dynamisme", "score": 6,
                 "justification": "Toulon reste une ville à revenu médian modeste, mais le secteur "
                                  "universitaire et militaire la soutient. Le marché n'est pas "
                                  "haussière : on n'achète pas ce studio pour la plus-value, on "
                                  "l'achète pour son prix d'entrée et son loyer."},
            ],
            "risques": [
                {"facteur": "Dépendance à l'exploitant : tout le loyer tient à sa signature",
                 "severite": 4,
                 "detail": "Le propriétaire ne choisit ni les locataires, ni les baux, ni les "
                           "réparations : c'est l'exploitant qui exploite. Un défaut de paiement ne "
                           "se voit qu'à l'échéance, et la clause résolutoire prend du temps. Les "
                           "comptes de GSA Résidences (exploitant du groupe Grand Sud Accueil, "
                           "SIRET 419 948 781) sont la première pièce à demander : c'est le locataire "
                           "unique, donc le dossier lui-même"},
                {"facteur": "Bail à quatorze mois du terme, avec droit au renouvellement de "
                            "l'exploitant", "severite": 4,
                 "detail": "Le bail commercial 3/6/9 court du 01/01/2018 au 31/12/2027. Un bail "
                           "commercial confère au preneur un droit au renouvellement : refuser le "
                           "renouvellement oblige le bailleur à une indemnité d'éviction que "
                           "l'intermédiaire lui-même chiffre à 12 000-15 000 € par studio en "
                           "résidence étudiante, soit le quart du prix payé. La reprise du studio "
                           "suppose donc une défaillance ou un départ de l'exploitant, pas un simple "
                           "refus de notre part : c'est la condition du scénario haut, et elle ne se "
                           "décide pas à la signature"},
                {"facteur": "Loyer 40 % sous le marché tant que le bail court", "severite": 3,
                 "detail": "285 €/mois pour 26,64 m² meublé, contre une tranche de 400 à 530 € pour "
                           "un meublé de cette taille dans la même ville. L'indexation du bail ne "
                           "comble pas cet écart : il n'y a aucun rattrapage à attendre avant le "
                           "terme, et c'est précisément ce qui explique la décote du prix"},
                {"facteur": "TVA et base de prix", "severite": 2,
                 "detail": "1 320 € de TVA présentée comme récupérable, sur un prix de 46 920 € "
                           "affiché TTC. La régularisation de TVA sur vingt ans est un poste classique "
                           "de ces reventes et l'acquéreur particulier ne récupère rien : à faire "
                           "écrire dans l'acte et dans la promesse, avec le montant de TVA déjà "
                           "régularisée par les propriétaires successifs"},
                {"facteur": "Remise en état après dix ans d'exploitation étudiante", "severite": 3,
                 "detail": "L'entretien courant est à l'exploitant, les grosses réparations au "
                           "propriétaire. Au départ de l'exploitant, le studio est rendu dans l'état "
                           "d'usure d'une exploitation intensive : 4 000 € provisionnés au barème, "
                           "davantage si les sanitaires et les sols sont repris. Aucun état des lieux "
                           "d'entrée ni diagnostic complet n'a été communiqué"},
                {"facteur": "Marché de revente étroit", "severite": 2,
                 "detail": "Un studio sous bail commercial ne s'adresse qu'à des investisseurs, et "
                           "accepte un seul profil d'acquéreur : celui qui veut le coupon. La sortie "
                           "la plus liquide est justement le scénario haut, studio libre et loué "
                           "meublé au marché — même logique que nos dossiers de petits lots : on "
                           "achète le prix, pas l'exploitation vendue par l'intermédiaire"},
            ],
        },
    }


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
    return rr


def main():
    r = fiche()
    c = engine.compute(r)
    f, rd = c["fiscal"], c["rendements"]

    c_haut = engine.compute(variante(r, loyer=LOYER_MARCHE, travaux=TRAVAUX_REPRISE))

    r["analyse"]["strategies_explorees"] = [
        {"strategie": "Portage du bail commercial en place jusqu'au terme du 31/12/2027",
         "lots": 1,
         "performance": f"{eur(LOYER_BAIL)}/mois encaissés sans gestion, indexés, pour un rendement "
                        f"net après IS de {rd['net_sur_revient_pct']:.2f} % sur un prix de revient de "
                        f"{eur(c['prix_revient_total'])}. Quatorze mois de coupon, puis la question "
                        f"se repose : renouvellement, défaillance ou reprise",
         "valeur_sortie": f"{eur(68000)} de valeur retenue pour un acte en main de "
                          f"{eur(PRIX + FRAIS)}, soit un ratio de {c['ratio_cout_valeur']:.2f} : la "
                          f"décote est la marge de sécurité du dossier",
         "faisabilite": "Immédiate : le bail est en place, le loyer court, rien à faire ni à gérer",
         "risque": "modéré à court terme, élevé au terme : tout dépend de ce que décide "
                   "l'exploitant au 31/12/2027"},
        {"strategie": "Reprise du studio et location meublée directe après le départ de l'exploitant",
         "lots": 1,
         "performance": f"{eur(LOYER_MARCHE)}/mois après {eur(TRAVAUX_REPRISE)} de remise en état, "
                        f"soit {eur(c_haut['fiscal']['ebe'])} d'EBE annuel et "
                        f"{c_haut['rendements']['net_sur_revient_pct']:.2f} % net après IS : le "
                        f"rendement double par rapport au coupon, au prix de la gestion",
         "valeur_sortie": f"Studio libre et loué meublé au marché : la valeur de revente remonte "
                          f"vers la médiane du DVF des moins de 30 m² (3 351 €/m²) au lieu de la "
                          f"décote de bail, soit plusieurs dizaines de milliers d'euros de plus que "
                          f"le prix payé",
         "faisabilite": "Subordonnée au départ ou à la défaillance de l'exploitant : un refus de "
                        "renouvellement de notre part coûte une indemnité d'éviction estimée à "
                        "12 000-15 000 €",
         "risque": "c'est le scénario qui fait le dossier, et il ne se commande pas : il s'attend"},
        {"strategie": "Revente en l'état, sous bail, au marché des studios gérés",
         "lots": 1,
         "performance": "Sortie de secours : les studios de résidences gérées comparables s'affichent "
                        "2 770 à 2 875 €/m², quand celui-ci est acheté autour de 1 800 €/m². La "
                        "revente rapporte si le bail est encore long ; à quatorze mois du terme, elle "
                        "ne rapporte rien de plus qu'aujourd'hui",
         "valeur_sortie": "Entre 58 000 et 76 000 € selon la durée de bail restante vendue avec le lot",
         "faisabilite": "Simple en apparence, mais le prix dépend entièrement de la durée du bail : "
                        "un bail à un an ne se vend pas",
         "risque": "faible, mais sans gain : c'est une porte de sortie, pas une stratégie"},
    ]

    errs = schema.validate_record(r)
    if errs:
        raise SystemExit(f"record invalide : {errs}")
    print("champs_manquants :", schema.champs_manquants(r))

    note, verdict, comp = scoring.note_et_verdict(r, c)
    plafond, contrainte = scoring.prix_plafond(r)
    cible = scoring.prix_cible(r)

    with open(BASE, encoding="utf-8") as fh:
        data = json.load(fh)
    avant = len(data["analyses"])
    data["analyses"] = [a for a in data["analyses"] if a["slug"] != SLUG]
    data["analyses"].append(r)
    data["meta"]["count"] = len(data["analyses"])
    with open(BASE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    with open(BASE, encoding="utf-8") as fh:
        relu = json.load(fh)
    print(f"base : {avant} → {len(relu['analyses'])} fiches | racine : {sorted(relu.keys())}")

    def fmt(x):
        return "aucun" if x is None else f"{x:,.0f}".replace(",", " ")

    print(f"note {note} / {verdict} {comp.get('plafonds')}")
    print(f"  EBE {fmt(f['ebe'])} | net après IS {fmt(f['net_apres_is'])} | IS {fmt(f['is_annuel'])} "
          f"| amort {fmt(f['amortissement'])}")
    print(f"  revient {fmt(c['prix_revient_total'])} | rdt revient {rd['net_sur_revient_pct']:.2f} % "
          f"| rdt valeur {rd['net_sur_valeur_pct']:.2f} % | ratio {c['ratio_cout_valeur']:.3f}")
    print(f"  plafond {fmt(plafond)} € ({contrainte}) | cible {fmt(cible)} €")
    print(f"  scénario haut (reprise, {eur(LOYER_MARCHE)}) : EBE {fmt(c_haut['fiscal']['ebe'])} | "
          f"net {fmt(c_haut['fiscal']['net_apres_is'])} | rdt {c_haut['rendements']['net_sur_revient_pct']:.2f} %")
    print(f"  composantes : perf {comp['s_performance']} | sécu {comp['s_securite']} | "
          f"adéquation {comp['s_adequation']} | risque {comp['s_risque']}")


if __name__ == "__main__":
    main()
