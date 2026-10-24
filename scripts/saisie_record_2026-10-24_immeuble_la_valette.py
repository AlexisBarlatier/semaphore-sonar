#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saisie du record — Immeuble de rapport 2 T2 + 2 remises, cœur historique, La Valette-du-Var.

SeLoger 26V1QCQPE2DT — AMV Immobilier (L'Agence du Moulin Vieux), réf. CD05082026 —
265 000 € honoraires inclus (250 000 € net vendeur + 15 000 € acquéreur) — relevé le 24/10/2026.
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

SLUG = "2026-10-24-immeuble-2t2-remises-la-valette"
BASE = os.path.join(RACINE, "analyses", "analyses.json")

PRIX = 265000.0          # honoraires inclus
NET_VENDEUR = 250000.0
HONORAIRES = 15000.0
FRAIS = 20000.0          # droits et émoluments, 8 % du prix net vendeur
TRAVAUX = 0.0
LOYER_T2 = 800.0
LOYER_REMISE = 60.0
TF = 2034.0
SURFACE = 127.0
VALEUR = 320000.0


def eur(v):
    return f"{v:,.0f}".replace(",", " ") + " €"


def fiche():
    return {
        "slug": SLUG,
        "date_analyse": "2026-10-24",
        "date_maj": "2026-10-24",
        "titre": "Immeuble de rapport, 2 T2 et 2 remises — cœur historique, La Valette-du-Var (83160)",
        "bien": {
            "type_bien": "immeuble",
            "sous_type": "immeuble de rapport",
            "type_detail": "Immeuble de rapport dans le cœur historique du village, au calme : deux "
                           "appartements de type 2 à l'étage, deux remises en rez-de-chaussée et une "
                           "cave. Immeuble de 1930. Surface annoncée : 127 m² sur SeLoger, 147 m² sur la fiche "
                           "de l'agence — deux chiffres pour le même bien. DPE E, GES B, facture "
                           "énergétique estimée entre 653 et 883 €/an. Aucun plan, aucun mesurage "
                           "par lot.",
            "neuf": False,
            "adresse": {
                "texte": "Cœur historique du village, La Valette-du-Var (83160) — adresse exacte non "
                         "communiquée par l'agence",
                "ville": "La Valette-du-Var",
                "code_postal": "83160",
                "quartier": "Centre historique",
            },
            "surfaces": {"texte": "Deux surfaces pour le même bien : 127 m² sur SeLoger, 147 m² sur la fiche "
                                  "de l'agence (qui parle de « surface habitable »), soit 20 m² d'écart "
                                  "et 16 % de valeur. Aucun Carrez, aucun mesurage par lot. La "
                                  "répartition entre les deux T2 et les deux remises n'est pas donnée : "
                                  "deux T2 de 55 à 63 m² et des remises de 8 à 15 m² sont l'hypothèse "
                                  "la plus probable, mais elle n'est pas documentée. Toute la valeur "
                                  "au mètre carré dépend de ce chiffre"},
            "lots": {"count": 4,
                     "nature": "Deux appartements T2 à l'étage, deux remises en rez-de-chaussée, une "
                               "cave. Aucune copropriété : un seul propriétaire, charges à "
                               "reconstituer",
                     "lots_distincts": 4},
            "copro": {"charges_annuelles_euros": 0.0,
                      "charges_source": "Aucune copropriété : immeuble en monopropriété. L'assurance "
                                        "de l'immeuble, l'entretien des communs et la provision gros "
                                        "travaux sont reconstitués dans les lignes d'entretien et "
                                        "d'assurance de la fiche"},
            "travaux": {
                "montant_euros": TRAVAUX,
                "nature": "Aucun montant annoncé, aucun devis, aucune photo d'intérieur exploitable "
                          "dans l'annonce. Le bien est classé E, ce qui n'impose aucune échéance "
                          "avant 2034, mais un immeuble ancien en cœur de village porte toujours un "
                          "poste toiture, façade et électricité que l'annonce tait. Budget retenu à "
                          "zéro dans le scénario central, 5 000 € en Worst : c'est une hypothèse de "
                          "lecture, pas un constat. Le DPE E et l'absence de tout devis sont les deux "
                          "raisons de ne pas signer sans visite technique",
            },
        },
        "annonce": {
            "plateforme": "seloger",
            "url": "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/la-valette-du-var-83160/26V1QCQPE2DT",
            "prix_affiche_euros": PRIX,
            "prix_retenu_euros": PRIX,
            "prix_statut": "affiche",
            "vendeur": "AMV Immobilier — L'Agence du Moulin Vieux (Christian Dupuy), réf. CD05082026. "
                       "265 000 € honoraires inclus : 250 000 € net vendeur et 15 000 € d'honoraires à "
                       "la charge de l'acquéreur (6 %), les droits calculés sur le net vendeur",
        },
        "marche": {
            "valeur": {
                "basse_euros": 280000.0,
                "haute_euros": 350000.0,
                "retenue_euros": VALEUR,
                "source": "DVF La Valette-du-Var (83144), appartements de 40 à 70 m² : 742 ventes "
                          "2021-2025, médiane 2 888 €/m², premier quartile 2 477, troisième quartile "
                          "3 835, prix médian 175 000 €. Sur 127 m² annoncés, deux T2 de 60 m² valent "
                          "346 560 €, auxquels s'ajoutent les deux remises. Décote de bloc de 12 % "
                          "appliquée (un immeuble se vend sous la somme de ses lots), puis 16 000 € "
                          "de remises : 320 000 € retenus, fourchette 280 000 à 400 000 € selon que "
                          "la surface réelle est de 127 ou de 147 m² — la fiche de l'agence annonce "
                          "147 m² quand SeLoger en annonce 127, et c'est le premier point à trancher. "
                          "Contrôle par les immeubles vendus en bloc dans la commune : 154 m² à "
                          "2 922 €/m² et 156 m² à 2 949 €/m² en décembre 2025, ce qui situe un "
                          "immeuble de ce format autour de 3 000 €/m² sur la surface réelle. Prix "
                          "affiché : 2 087 €/m² sur 127 m², ou 1 803 €/m² sur 147 m², contre 2 888 "
                          "€/m² de médiane des appartements de la commune ; l'écart s'explique par la "
                          "décote de bloc et par un état que l'annonce ne documente pas",
                "confiance": "moyenne",
            },
            "loyers": [
                {"lot": "Deux appartements T2 à l'étage, loués nus",
                 "quantite": 2,
                 "loyer_mensuel_euros": LOYER_T2,
                 "occupe": True,
                 "note": "AUCUN LOYER N'EST DONNÉ PAR L'ANNONCE — elle parle d'un « rapport locatif "
                         "correct » sans avancer un chiffre : c'est le trou du dossier. Estimation "
                         "au marché du 24/10/2026, à confirmer avec les baux : médiane DHUP 2025 de la "
                         "commune 15,5 €/m² (IC 95 % 12,15 à 19,77), T3 de 65 m² à 898 €/mois. "
                         "Annonces actives : 57 m² à 894 €, 55 m² à 770 €, 61 m² à 1 000 €, 48 m² à "
                         "915 €, 46 m² à 695 €. Retenu 800 € par T2, soit 12,7 à 14,5 €/m² selon que "
                         "le lot fait 55 ou 63 m² : sous la médiane communale, parce que le bien est "
                         "classé E, sans extérieur et dans un bâti ancien dont l'état n'est pas "
                         "documenté. Le loyer réel des baux en place peut être très différent, dans "
                         "les deux sens"},
                {"lot": "Deux remises en rez-de-chaussée",
                 "quantite": 2,
                 "loyer_mensuel_euros": LOYER_REMISE,
                 "occupe": True,
                 "note": "Poste estimé, aucun loyer annoncé : 60 €/mois par remise, ordre de grandeur "
                         "d'un local de stockage ou d'un garage en centre ancien. Si les remises font "
                         "au moins 9 m² et 20 m³ et que le PLU le permet, leur transformation en "
                         "studios serait un autre dossier — elle suppose déclaration préalable, "
                         "ouverture, ventilation et compteurs, et n'entre dans aucun calcul de prix "
                         "tant qu'elle n'est pas autorisée"},
            ],
            "notes": "Assiette : loyers de marché estimés, faute de tout chiffre dans l'annonce. Si les "
                     "baux en place portent 900 € par T2, le dossier change de nature ; s'ils portent "
                     "650 €, il ne passe pas. Les deux baux et les quittances sont la première pièce à "
                     "exiger, avant même la visite.",
        },
        "hypotheses": {
            "vacance_base_pct": 5.0,
            "vacance_best_pct": 2.0,
            "vacance_worst_pct": 12.0,
            "taux_placement_reserve_pct": 2.84,
            "quote_part_bati_pct": 90.0,
            "vacance_justification": "Deux logements seulement : un T2 vide représente la moitié de "
                                     "l'assiette. 5 % en base (un lot vide trois semaines par an), "
                                     "2 % en best, 12 % en worst (un T2 vide un mois et demi, ou les "
                                     "deux remises vides en même temps)",
            "charges": {
                "charges_copro_annuelles_euros": 0.0,
                "charges_copro_commentaire": "Aucune copropriété. L'assurance de l'immeuble est portée "
                                             "par la ligne PNO, l'entretien des communs par la ligne "
                                             "d'entretien",
                "taxe_fonciere_annuelle_euros": TF,
                "taxe_fonciere_commentaire": "2 034 €/an, montant donné par la fiche de l'agence. Repère "
                                            "communal : la taxe foncière sur le bâti de La "
                                            "Valette-du-Var est parmi les plus lourdes de l'aire "
                                            "toulonnaise, et un immeuble de 127 m² en centre ancien "
                                            "avec deux lots loués se situe dans cette fourchette. "
                                            "L'avis réel est à exiger avant toute offre",
                "entretien_annuel_euros": 2357.0,
                "entretien_commentaire": "2 357 €/an : gestion locative déléguée à 6 % des loyers "
                                         "(1 238 €), provision d'impayés à 3 % (619 €, distincte de "
                                         "la vacance) et 500 € d'entretien courant d'un bâti ancien "
                                         "sans parties communes",
                "pno_annuelle_euros": 300.0,
                "comptabilite_annuelle_euros": 0.0,
            },
            "frais_acquisition_euros": FRAIS,
            "frais_acquisition_commentaire": "20 000 € de droits et émoluments, calculés à 8 % du prix "
                                             "net vendeur de 250 000 €. Les 15 000 € d'honoraires sont "
                                             "déjà compris dans le prix affiché de 265 000 € : les "
                                             "ajouter aux frais les compterait deux fois",
        },
        "analyse": {
            "branche": "residentiel",
            "type_operation": "locatif",
            "strategie_retenue": {
                "nom": "Conservation en bloc : deux T2 loués nus, remises louées séparément",
                "code": "ld-nue",
                "lots": 4,
            },
            "strategies_explorees": [],
            "attractivite": [
                {"dimension": "transports", "score": 8,
                 "justification": "Réseau Mistral dense vers Toulon, accès direct A57 et A570, gare "
                                  "de Toulon à une dizaine de minutes. C'est une commune de première "
                                  "couronne, pas un village isolé : le locataire peut y vivre sans "
                                  "voiture pour aller travailler à Toulon."},
                {"dimension": "commerces", "score": 8,
                 "justification": "Cœur historique avec marché, commerces de proximité et services, "
                                  "et à quelques minutes les zones Grand Var et L'Avenue 83. Le "
                                  "centre ancien est vivant : c'est ce qui tient la demande locative "
                                  "sur ce type de produit."},
                {"dimension": "ecoles", "score": 7,
                 "justification": "Dix-sept établissements scolaires sur la commune, du primaire au "
                                  "lycée, et un tissu associatif dense. La clientèle familiale existe, "
                                  "mais deux T2 en centre ancien visent plutôt des actifs seuls ou en "
                                  "couple."},
                {"dimension": "securite", "score": 5,
                 "justification": "Commune globalement calme, mais le centre ancien concentre les "
                                  "logements dégradés et la vacance ; deux quartiers prioritaires "
                                  "existent ailleurs dans la commune (Berthe, La Coupiane). À "
                                  "vérifier rue par rue : un cœur historique peut être très calme ou "
                                  "très passant selon la position exacte."},
                {"dimension": "demande_locative", "score": 7,
                 "justification": "Vacance communale estimée à 8,8 %, plus de 1 100 transactions par "
                                  "an, loyers médians à 15,5 €/m² et un parc locatif privé important. "
                                  "Les petites surfaces se relouent vite : cinq annonces de 46 à 61 m² "
                                  "entre 695 et 1 000 € au 24/10/2026."},
                {"dimension": "dynamisme", "score": 7,
                 "justification": "23 700 habitants, première couronne toulonnaise, bassin d'emploi "
                                  "métropolitain, prix en hausse de 9 % entre 2021 et 2025. C'est le "
                                  "type de commune où la valeur de revente tient, à condition "
                                  "d'acheter sous le marché — ce qui est le cas ici."},
            ],
            "risques": [
                {"facteur": "Aucun loyer annoncé : le prix n'est pas vérifiable", "severite": 5,
                 "detail": ""},
                {"facteur": "Surface habitable non mesurée et non ventilée par lot", "severite": 4,
                 "detail": "127 m² annoncés, sans Carrez, sans plan, sans répartition entre les deux "
                           "T2 et les deux remises, et deux surfaces différentes pour le même bien — 127 m² sur "
                           "SeLoger, 147 m² sur la fiche de l'agence. À 2 087 €/m² annoncés, la valeur "
                           "change de plus de 50 000 € selon la surface retenue. Diagnostic de "
                           "surface, plans et mesurage par lot à exiger avant toute offre : c'est le "
                           "premier chiffre à faire confirmer."},
                {"facteur": "DPE E sur un bâti ancien sans devis ni année de construction",
                 "severite": 3,
                 "detail": "Le classement E n'impose rien avant 2034 et les loyers ne sont pas gelés, "
                           "mais il signale un bâti mal isolé, probablement chauffé à l'électrique. "
                           "Aucun devis, aucune photo d'intérieur exploitable, aucune année de "
                           "construction : toiture, façade, électricité et évacuations sont les "
                           "postes que l'annonce tait, et ils se paient comptant dans un immeuble "
                           "sans copropriété pour les mutualiser."},
                {"facteur": "Deux logements seulement : la vacance coûte la moitié de l'assiette",
                 "severite": 3,
                 "detail": "Un T2 vide, et c'est 800 €/mois qui disparaissent, soit la moitié des "
                           "loyers. La granularité du risque est mauvaise : pas de lissage possible "
                           "entre dix lots, et une relocation ratée se voit immédiatement en "
                           "trésorerie."},
                {"facteur": "Prix affiché honoraires inclus avec 6 % à la charge de l'acquéreur",
                 "severite": 2,
                 "detail": "15 000 € d'honoraires s'ajoutent au prix net vendeur de 250 000 €, et les "
                           "droits se calculent sur le seul net vendeur. Le coût complet ressort à "
                           "285 000 €, soit 7,5 % au-dessus du prix affiché : c'est le chiffre à "
                           "avoir en tête avant de raisonner en rendement."},
                {"facteur": "Deux remises en rez-de-chaussée à l'usage incertain", "severite": 2,
                 "detail": "Leur surface n'est pas donnée. Si elles font moins de 9 m² ou moins de "
                           "20 m³, elles ne peuvent pas devenir des logements et ne valent que leur "
                           "revente ou leur usage de stockage. Les compter comme un revenu "
                           "supplémentaire avant de connaître leur surface serait une erreur."},
            ],
        },
    }


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
        rr["hypotheses"]["frais_acquisition_euros"] = round((prix - HONORAIRES) * 0.08)
    return rr


def annuite(assiette, taux=0.038, mois=240, ass=0.0034):
    i = taux / 12.0
    return assiette * 0.9 * i / (1 - (1 + i) ** -mois) + assiette * 0.9 * ass / 12.0


def main():
    r = fiche()
    c = engine.compute(r)

    c_baux_hauts = engine.compute(variante(r, loyer=900.0))
    c_baux_bas = engine.compute(variante(r, loyer=650.0))
    c_meuble = engine.compute(variante(r, loyer=950.0, entretien=2357.0 + 900.0))
    c_division = engine.compute(variante(r, loyer=LOYER_T2, loyer2=1110.0, travaux=45000.0))

    r["analyse"]["strategies_explorees"] = [
        {"strategie": "Conservation en bloc : deux T2 loués nus, remises louées séparément",
         "lots": 4,
         "performance": f"{eur(LOYER_T2 * 2 + LOYER_REMISE * 2)}/mois de recettes estimées, soit un "
                        f"rendement net après IS de {c['rendements']['net_sur_revient_pct']:.2f} % "
                        f"sur un prix de revient de {eur(c['prix_revient_total'])}. Sans les remises, "
                        f"l'assiette tombe à {eur(LOYER_T2 * 2)} et le rendement à "
                        f"{(engine.compute(variante(r, loyer2=0.0))['rendements']['net_sur_revient_pct']):.2f} %",
         "valeur_sortie": f"Revente à la découpe des deux T2 : 2 x 60 m² x 2 888 €/m² = 346 560 €, "
                          f"moins les frais de vente, contre {eur(c['prix_revient_total'])} de revient. "
                          f"C'est la voie de sortie qui porte la valeur du dossier",
         "faisabilite": "Immédiate : deux baux en place, remises louées séparément, aucune "
                        "copropriété à créer si l'immeuble est déjà en monopropriété",
         "risque": "modéré — le rendement dépend entièrement de loyers que l'annonce ne donne pas"},
        {"strategie": "Relocation des deux T2 en meublé",
         "lots": 2,
         "performance": f"2 x 950 €/mois, soit +300 €/mois de recettes brutes, pour l'ameublement des "
                        f"deux lots (environ 8 000 €) et une rotation plus rapide. Rendement net "
                        f"après IS de {c_meuble['rendements']['net_sur_revient_pct']:.2f} % : le gain "
                        f"de loyer ne couvre pas le surcoût de gestion et d'ameublement",
         "valeur_sortie": "Aucune prime de valeur à la revente : le meublé se paie au loyer, pas au "
                          "mètre carré",
         "faisabilite": "Changement de nature de bail, mobilier complet, gestion des entrées et "
                        "sorties sur deux lots",
         "risque": "modéré — le meublé de centre ancien à La Valette vise une clientèle mobile, "
                   "celle qui part le plus vite"},
        {"strategie": "Transformation des deux remises en studios",
         "lots": 4,
         "performance": f"Scénario conditionnel : +1 110 €/mois (2 x 555 €) pour 45 000 € de travaux "
                        f"de transformation, soit 29,6 % du capital engagé. Rendement net après IS de "
                        f"{c_division['rendements']['net_sur_revient_pct']:.2f} % si et seulement si "
                        f"les remises font au moins 9 m² et 20 m³, que le PLU autorise la création de "
                        f"logements et que le règlement sanitaire est respecté. Aucune de ces trois "
                        f"conditions n'est vérifiée à ce stade",
         "valeur_sortie": "Deux studios de 15 à 20 m² valent 60 000 à 80 000 € à la revente dans la "
                          "commune, soit une création de valeur réelle — mais elle n'existe qu'après "
                          "autorisation",
         "faisabilite": "Déclaration préalable, vérification de la zone du PLU et de la servitude de "
                        "linéaire commercial, ouverture en façade, ventilation, compteurs séparés",
         "risque": "élevé — c'est un projet, pas une exploitation : il ne doit pas entrer dans le prix"},
    ]

    r["analyse"]["risques"][0]["detail"] = (
        f"L'annonce annonce un « rapport locatif correct » et ne donne aucun loyer. À l'assiette "
        f"estimée de {eur(LOYER_T2 * 2 + LOYER_REMISE * 2)}/mois, le rendement net après IS ressort à "
        f"{c['rendements']['net_sur_revient_pct']:.2f} % pour un prix de revient de "
        f"{eur(c['prix_revient_total'])}. Avec des baux à 650 € par T2, il tombe à "
        f"{(c_baux_bas['rendements']['net_sur_revient_pct']):.2f} % ; avec des baux à 900 €, il monte à "
        f"{(c_baux_hauts['rendements']['net_sur_revient_pct']):.2f} %. L'écart entre les deux lectures "
        f"vaut plus de 60 000 € de prix. Tant que les baux ne sont pas au dossier, le prix n'est pas "
        f"une donnée, c'est une fourchette."
    )

    errs = schema.validate_record(r)
    if errs:
        raise SystemExit(f"record invalide : {errs}")
    print("champs_manquants :", schema.champs_manquants(r))

    note, verdict, comp = scoring.note_et_verdict(r, c)
    if note is None:
        raise SystemExit("note non calculable")
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
    print(f"base : {avant} → {len(relu['analyses'])} fiches")

    def fmt(x):
        return "aucun" if x is None else f"{x:,.0f}".replace(",", " ")

    print(f"note {note} / {verdict} ({comp.get('plafonds')})")
    print(f"  performance {c['rendements']['net_sur_revient_pct']:.2f} % | brut "
          f"{(LOYER_T2 * 2 + LOYER_REMISE * 2) * 12 / PRIX * 100:.2f} % | ratio coût/valeur "
          f"{c['ratio_cout_valeur']:.3f}")
    print(f"  EBE {fmt(c['fiscal']['ebe'])} | net après IS {fmt(c['fiscal']['net_apres_is'])} | "
          f"revient {fmt(c['prix_revient_total'])}")
    print(f"  prix plafond {fmt(plafond)} € ({contrainte}) | prix cible {fmt(cible)} €")
    print(f"  solde mensuel standard : {c['fiscal']['net_apres_is'] / 12 - annuite(PRIX):+.0f} €/mois")
    print(f"  baux 900 : {c_baux_hauts['rendements']['net_sur_revient_pct']:.2f} % | baux 650 : "
          f"{c_baux_bas['rendements']['net_sur_revient_pct']:.2f} % | meublé : "
          f"{c_meuble['rendements']['net_sur_revient_pct']:.2f} % | studios : "
          f"{c_division['rendements']['net_sur_revient_pct']:.2f} %")


if __name__ == "__main__":
    main()
