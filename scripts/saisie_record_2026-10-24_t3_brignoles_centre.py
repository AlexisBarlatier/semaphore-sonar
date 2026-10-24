#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saisie du record — T3 68 m², rue commerçante du centre, Brignoles (83170).

SeLoger 26GCCUFIK3PP — Elios Group, Cassilde Mattei, réf. 1372-ELIOSGROUP1 — 91 000 € —
relevé le 24/10/2026. Idempotent : le slug est filtré avant append.
"""
import copy
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

from analyse_app import engine, schema, scoring  # noqa: E402

SLUG = "2026-10-24-t3-brignoles-centre-68m2"
BASE = os.path.join(RACINE, "analyses", "analyses.json")

PRIX = 91000.0
FRAIS = 7280.0
TRAVAUX = 20000.0
LOYER = 750.0
TF = 700.0
CHARGES = 117.0
SURFACE = 68.28
VALEUR = 120000.0


def eur(v):
    return f"{v:,.0f}".replace(",", " ") + " €"


def fiche():
    return {
        "slug": SLUG,
        "date_analyse": "2026-10-24",
        "date_maj": "2026-10-24",
        "titre": "Appartement T3 de 68 m², rue commerçante du centre — Brignoles (83170)",
        "bien": {
            "type_bien": "appartement",
            "sous_type": "T3",
            "type_detail": "Appartement de type 3 au premier étage d'un petit immeuble en "
                           "copropriété, dans une rue commerçante du cœur de ville : entrée, "
                           "dégagement, trois pièces, deux chambres, deux WC et une salle de bain. "
                           "Belles hauteurs sous plafond, double vitrage partout, parking à "
                           "proximité. État déclaré : rénovation nécessaire. DPE C, GES A, chauffage "
                           "individuel électrique.",
            "neuf": False,
            "adresse": {
                "texte": "Rue commerçante du centre-ville, Brignoles (83170) — adresse exacte non "
                         "communiquée",
                "ville": "Brignoles",
                "code_postal": "83170",
                "quartier": "Centre-ville",
            },
            "surfaces": {"texte": "68,28 m² annoncés, 68,20 m² dans le descriptif du même document : "
                                  "l'écart est négligeable. Aucun Carrez au dossier, aucun plan"},
            "lots": {"count": 1,
                     "nature": "Un appartement dans une copropriété de 4 lots, sans ascenseur, sans "
                               "balcon, sans garage. Parking public à proximité",
                     "lots_distincts": 1},
            "copro": {"charges_annuelles_euros": CHARGES,
                      "charges_source": "117 €/an de quote-part de budget prévisionnel, annoncés par "
                                        "l'annonce pour une copropriété de 4 lots. Aucune procédure "
                                        "en cours. Le montant est crédible pour une petite copro sans "
                                        "ascenseur ni chauffage collectif, mais il ne couvre pas les "
                                        "travaux : il faut les PV d'AG des trois dernières années"},
            "travaux": {
                "montant_euros": TRAVAUX,
                "nature": "« Travaux de réagencement et rénovation à prévoir », sans montant ni devis. "
                          "Le DPE C et le double vitrage partout indiquent que l'enveloppe et les "
                          "menuiseries sont faites : le poste est intérieur (cuisine, salle de bain, "
                          "électricité, peintures, sols). Barème retenu : 300 €/m² pour un "
                          "réagencement, soit 20 000 € sur 68 m². Fourchette 12 000 à 35 000 € selon "
                          "l'état réel de la cuisine, de la salle de bain et des tableaux électriques",
            },
        },
        "annonce": {
            "plateforme": "seloger",
            "url": "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/brignoles-83170/26GCCUFIK3PP",
            "prix_affiche_euros": PRIX,
            "prix_retenu_euros": PRIX,
            "prix_statut": "affiche",
            "vendeur": "Elios Group France — Cassilde Mattei (SAS Cassilde Mattei, RCS 753494228), "
                       "réf. 1372-ELIOSGROUP1 — honoraires à la charge du vendeur",
        },
        "marche": {
            "valeur": {
                "basse_euros": 95000.0,
                "haute_euros": 145000.0,
                "retenue_euros": VALEUR,
                "source": "DVF Brignoles (83018), appartements de 45 à 80 m² : 13 ventes 2021-2025, "
                          "médiane 1 868 €/m², premier quartile 1 287, troisième quartile 2 173, prix "
                          "médian 93 000 € ; sur la tranche 60-75 m², 9 ventes, médiane 1 409 €/m². "
                          "Échantillon mince, marché étroit : c'est un repère, pas une distribution. "
                          "Sur 68,28 m², la fourchette va de 88 000 € (premier quartile) à 148 000 € "
                          "(troisième quartile). Valeur retenue 120 000 €, après travaux, entre le "
                          "prix médian et le troisième quartile, pour un T3 de centre-ville rénové, "
                          "avec double vitrage et DPE C. En l'état, avant travaux, la valeur est plus "
                          "proche de 95 000 €, ce qui situe le prix affiché au niveau du bien à "
                          "rénover, pas en dessous",
                "confiance": "faible",
            },
            "loyers": [
                {"lot": "T3 de 68 m², premier étage, centre-ville",
                 "quantite": 1,
                 "loyer_mensuel_euros": LOYER,
                 "occupe": False,
                 "note": "Bien libre, aucun bail. Estimation au marché du 24/10/2026 : médiane DHUP "
                         "2025 de Brignoles 13,1 €/m² (IC 95 % 10,1 à 16,9), T3 de 65 m² à 759 €. "
                         "Annonces actives : T3 de 66 m² rue Petit Paradis, centre-ville, à 630 € ; "
                         "T3 de 69 m² en résidence avec ascenseur et parking à 786 € ; T3 de 68,65 m² "
                         "au 90 boulevard Joseph Monnier (Pôle Liberté) à 794 € charges comprises, "
                         "dont 666 € hors charges. Retenu 750 €/mois : dans la fourchette, sous les "
                         "deux T3 avec ascenseur et parking, ce que ce lot n'a pas, et au-dessus du "
                         "T3 de la rue Petit Paradis, qui est plus petit"},
            ],
            "notes": "Bien libre : l'assiette est une cible post-travaux, pas un encaissement. Aucun "
                     "loyer ne court avant le chantier et la signature d'un bail. C'est la lecture de "
                     "dette du dossier : à 91 000 €, on paie un appartement qui ne produit rien "
                     "aujourd'hui.",
        },
        "hypotheses": {
            "vacance_base_pct": 5.0,
            "vacance_best_pct": 2.0,
            "vacance_worst_pct": 12.0,
            "taux_placement_reserve_pct": 2.84,
            "quote_part_bati_pct": 90.0,
            "vacance_justification": "Un seul lot : 5 % en base (trois semaines de vacance par an), "
                                     "2 % en best, 12 % en worst (un mois et demi entre deux "
                                     "locataires sur un marché de bourg où l'offre de T3 est "
                                     "abondante)",
            "charges": {
                "charges_copro_annuelles_euros": CHARGES,
                "charges_copro_commentaire": "117 €/an, quote-part de budget prévisionnel annoncée, "
                                             "sur une copropriété de 4 lots. Aucune procédure en "
                                             "cours. Le poste est marginal ; ce sont les travaux votés "
                                             "qui comptent, et ils ne sont pas au dossier",
                "taxe_fonciere_annuelle_euros": TF,
                "taxe_fonciere_commentaire": "700 €/an ESTIMÉS — aucun avis communiqué. Repères "
                                            "internes à Brignoles : 900 à 1 300 €/an pour un T3 de "
                                            "60 à 70 m² dans le centre. L'avis réel est à exiger",
                "entretien_annuel_euros": 1110.0,
                "entretien_commentaire": "1 110 €/an : gestion locative déléguée à 6 % des loyers "
                                         "(540 €), provision d'impayés à 3 % (270 €, distincte de la "
                                         "vacance) et 300 € d'entretien courant",
                "pno_annuelle_euros": 200.0,
                "comptabilite_annuelle_euros": 0.0,
            },
            "frais_acquisition_euros": FRAIS,
            "frais_acquisition_commentaire": "8 % du prix (7 280 €), régime ancien ; honoraires à la "
                                             "charge du vendeur, donc hors base de calcul",
        },
        "analyse": {
            "branche": "residentiel",
            "type_operation": "locatif",
            "strategie_retenue": {
                "nom": "Rénovation puis location nue du T3",
                "code": "ld-nue",
                "lots": 1,
            },
            "strategies_explorees": [],
            "attractivite": [
                {"dimension": "transports", "score": 6,
                 "justification": "Brignoles est sur l'A8, à 30 km de Toulon et 50 de Marseille, "
                                  "avec une gare routière et un accès autoroutier immédiat. Pas de "
                                  "train de voyageurs : la commune vit de la voiture et de l'emploi "
                                  "local."},
                {"dimension": "commerces", "score": 8,
                 "justification": "Rue commerçante du cœur de ville, commerces, médecins, écoles et "
                                  "hôpital à pied. C'est le meilleur argument du bien et ce qui tient "
                                  "la demande locative sur le centre."},
                {"dimension": "ecoles", "score": 7,
                 "justification": "Écoles, collèges et lycées sur la commune, hôpital à proximité. "
                                  "Brignoles est le pôle administratif et scolaire du centre Var."},
                {"dimension": "securite", "score": 4,
                 "justification": "Centre ancien du Var avec ses zones d'incivilité ; nos dossiers "
                                  "antérieurs sur Brignoles relevaient des problèmes de stationnement "
                                  "et de propreté en vieille ville. Rue commerçante passante : à "
                                  "vérifier le soir."},
                {"dimension": "demande_locative", "score": 6,
                 "justification": "Marché de bourg : locataires salariés, personnel hospitalier, "
                                  "familles modestes. La demande existe sur les T3 de centre, mais "
                                  "l'offre aussi — trois T3 de 66 à 69 m² sont en concurrence au "
                                  "même moment entre 630 et 794 €."},
                {"dimension": "dynamisme", "score": 5,
                 "justification": "18 000 habitants, économie administrative et de services, "
                                  "démographie stable. Marché sans fièvre : les prix DVF sont passés "
                                  "de 1 550 à 2 000 €/m² en cinq ans, mais sur des volumes très "
                                  "faibles."},
            ],
            "risques": [
                {"facteur": "Travaux de rénovation non chiffrés sur un bien vendu « à réagencer »",
                 "severite": 4, "detail": ""},
                {"facteur": "Aucun loyer encaissé : assiette post-travaux", "severite": 3,
                 "detail": "Le bien est libre. Les 750 €/mois sont une cible de marché, pas un "
                           "encaissement : ils ne courent qu'après le chantier et la signature d'un "
                           "bail. Sur douze mois, cela veut dire six à dix mois sans revenu si les "
                           "travaux prennent du temps — et une relocation à un niveau qu'on ne "
                           "connaît pas encore."},
                {"facteur": "Marché DVF très mince : 13 ventes de 45 à 80 m² en cinq ans",
                 "severite": 3,
                 "detail": "La valeur de 120 000 € repose sur 13 mutations, dont le premier quartile "
                           "est à 1 287 €/m² : la fourchette réelle va de 88 000 à 148 000 €. Une "
                           "revente se juge sur ce que paiera un acheteur de bourg, pas sur une "
                           "médiane fragile. Le prix affiché est d'ailleurs au niveau du premier "
                           "quartile : le marché dit que la décote paie les travaux, pas qu'elle "
                           "offre une marge."},
                {"facteur": "Copropriété de 4 lots sans historique", "severite": 3,
                 "detail": "117 €/an de charges est très bas, ce qui est bon signe pour la gestion "
                           "courante et mauvais signe pour l'entretien : sur un immeuble de 4 lots, "
                           "une toiture ou une façade se vote à quatre et se paie comptant. Les trois "
                           "derniers PV d'AG et le carnet d'entretien sont à exiger avant l'offre."},
                {"facteur": "Stationnement absent", "severite": 2,
                 "detail": "Aucun garage, aucun balcon, parking public à proximité seulement. Dans un "
                           "bourg où la voiture est indispensable, c'est un frein à la relocation et "
                           "un argument de prix à la baisse face aux T3 en résidence qui en ont un."},
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
        rr["hypotheses"]["frais_acquisition_euros"] = round(prix * 0.08)
    return rr


def annuite(assiette, taux=0.038, mois=240, ass=0.0034):
    i = taux / 12.0
    return assiette * 0.9 * i / (1 - (1 + i) ** -mois) + assiette * 0.9 * ass / 12.0


def main():
    r = fiche()
    c = engine.compute(r)

    c_12k = engine.compute(variante(r, travaux=12000.0))
    c_35k = engine.compute(variante(r, travaux=35000.0))
    c_650 = engine.compute(variante(r, loyer=650.0))
    c_820 = engine.compute(variante(r, loyer=820.0))

    r["analyse"]["strategies_explorees"] = [
        {"strategie": "Rénovation puis location nue du T3",
         "lots": 1,
         "performance": f"{eur(LOYER)}/mois après travaux, soit un rendement net après IS de "
                        f"{c['rendements']['net_sur_revient_pct']:.2f} % sur un prix de revient de "
                        f"{eur(c['prix_revient_total'])} travaux compris. C'est le seul montage qui "
                        f"tienne sur ce bien, et il dépend entièrement du devis",
         "valeur_sortie": f"Revente après travaux : 120 000 € retenus, 148 000 € au troisième "
                          f"quartile DVF, contre {eur(c['prix_revient_total'])} de revient. La marge "
                          f"existe, elle est mince et elle paie le chantier, pas l'achat",
         "faisabilite": "Libre, aucun bail à attendre : travaux de deux à quatre mois, puis "
                        "relocation. Copropriété de 4 lots, aucune autorisation particulière",
         "risque": "modéré — le risque est le devis, pas l'exploitation"},
        {"strategie": "Achat, rénovation et revente (marchand de biens)",
         "lots": 1, "rdt": None,
         "performance": f"{eur(120000 - 118280)} de marge à la valeur retenue et "
                        f"{eur(148000 - 118280)} au troisième quartile, avant frais de vente et "
                        f"portage. Sur un ticket de 91 000 €, les frais de vente (6 %, soit 7 200 à "
                        f"8 900 €) mangent la moitié de la marge : ce n'est pas une opération",
         "valeur_sortie": "120 000 à 148 000 € selon la qualité du chantier",
         "faisabilite": "Structure commerciale, TVA, portage de 12 à 18 mois",
         "risque": "élevé — la marge ne survit pas aux frais"},
        {"strategie": "Conservation en l'état, location sans travaux",
         "lots": 1,
         "rdt": None,
         "performance": "Écartée : l'annonce dit elle-même « rénovation nécessaire », et un T3 de "
                        "68 m² non rénové dans une rue commerçante se loue 150 à 200 € sous le "
                        "marché, avec une relocation difficile. Louer sans travaux, c'est acheter "
                        "un rendement de 3,5 % et une vacance",
         "valeur_sortie": "95 000 € en l'état",
         "faisabilite": "Immédiate, mais à quel loyer",
         "risque": "élevé — c'est le scénario qui transforme un dossier correct en dossier mort"},
    ]

    r["analyse"]["risques"][0]["detail"] = (
        f"« Travaux de réagencement et rénovation à prévoir », sans montant ni devis. Le budget retenu "
        f"est de {eur(TRAVAUX)} (300 €/m²), mais la fourchette va de 12 000 à 35 000 € selon l'état de "
        f"la cuisine, de la salle de bain et des tableaux électriques. À 12 000 €, le rendement net "
        f"après IS monte à {c_12k['rendements']['net_sur_revient_pct']:.2f} % ; à 35 000 €, il tombe à "
        f"{c_35k['rendements']['net_sur_revient_pct']:.2f} %. Tout le dossier tient dans ce devis : "
        f"c'est la première pièce à demander, avant même la visite."
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
          f"{LOYER * 12 / PRIX * 100:.2f} % | ratio coût/valeur {c['ratio_cout_valeur']:.3f}")
    print(f"  EBE {fmt(c['fiscal']['ebe'])} | net après IS {fmt(c['fiscal']['net_apres_is'])} | "
          f"revient {fmt(c['prix_revient_total'])}")
    print(f"  prix plafond {fmt(plafond)} € ({contrainte})")
    print(f"  solde mensuel standard : {c['fiscal']['net_apres_is'] / 12 - annuite(PRIX + TRAVAUX):+.0f} €/mois")
    print(f"  travaux 12k {c_12k['rendements']['net_sur_revient_pct']:.2f} % | 35k "
          f"{c_35k['rendements']['net_sur_revient_pct']:.2f} % | loyer 650 "
          f"{c_650['rendements']['net_sur_revient_pct']:.2f} % | 820 "
          f"{c_820['rendements']['net_sur_revient_pct']:.2f} %")


if __name__ == "__main__":
    main()
