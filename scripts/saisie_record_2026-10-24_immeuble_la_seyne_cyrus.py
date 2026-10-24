#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saisie du record — Immeuble mixte commerce + habitation, rue Cyrus Hugues, La Seyne-sur-Mer.

SeLoger 267PVVC94GXQ — Agence Papazian-Chovelon Porte Marine (Orpi), réf. 38035 —
245 000 € — relevé le 24/10/2026. Fiche agence : réf. ROBGC, rue Cyrus Hugues.
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

SLUG = "2026-10-24-immeuble-mixte-cyrus-hugues-la-seyne"
BASE = os.path.join(RACINE, "analyses", "analyses.json")

PRIX = 245000.0
FRAIS = 19600.0          # 8 %, régime ancien, honoraires vendeur
TRAVAUX = 0.0
LOYER_LOGEMENT = 1050.0
LOYER_COMMERCE = 650.0
TF = 2034.0
SURFACE = 147.0
VALEUR = 225000.0


def eur(v):
    return f"{v:,.0f}".replace(",", " ") + " €"


def fiche():
    return {
        "slug": SLUG,
        "date_analyse": "2026-10-24",
        "date_maj": "2026-10-24",
        "titre": "Immeuble mixte commerce et habitation, rue Cyrus Hugues — La Seyne-sur-Mer (83500)",
        "bien": {
            "type_bien": "immeuble",
            "sous_type": "immeuble mixte",
            "type_detail": "Immeuble de ville de 1930 sur trois niveaux, à deux pas du port : un local "
                           "commercial en rez-de-chaussée actuellement exploité en boucherie-charcuterie, "
                           "et un logement de trois pièces et deux chambres réparti sur deux niveaux. "
                           "147 m² habitables annoncés, climatisation, cave. DPE D, GES B. Aucune "
                           "surface par lot, aucun loyer, aucun bail, aucun travaux chiffré dans "
                           "l'annonce.",
            "neuf": False,
            "adresse": {
                "texte": "Rue Cyrus Hugues, centre-ville, La Seyne-sur-Mer (83500) — adresse exacte non "
                         "communiquée dans l'annonce, rue donnée par la fiche de l'agence",
                "ville": "La Seyne-sur-Mer",
                "code_postal": "83500",
                "quartier": "Centre-ville",
            },
            "surfaces": {"texte": "147 m² habitables annoncés pour l'ensemble, sans ventilation entre "
                                  "le local commercial et le logement, sans Carrez et sans plan. "
                                  "Hypothèse de travail : environ 55 m² de local en rez-de-chaussée et "
                                  "92 m² de logement sur les deux niveaux. C'est une répartition "
                                  "supposée, pas un mesurage : elle déplace la valeur de 20 000 à "
                                  "30 000 € selon le partage réel"},
            "lots": {"count": 2,
                     "nature": "Un local commercial en rez-de-chaussée et un logement de trois pièces "
                               "à l'étage, sur deux niveaux. Immeuble entier, pas de copropriété "
                               "annoncée",
                     "lots_distincts": 2},
            "copro": {"charges_annuelles_euros": 0.0,
                      "charges_source": "Aucune copropriété annoncée : immeuble en monopropriété. "
                                        "L'assurance de l'immeuble et l'entretien des communs sont "
                                        "reconstitués dans les lignes correspondantes"},
            "travaux": {
                "montant_euros": TRAVAUX,
                "nature": "Aucun montant, aucun devis, aucune photo d'intérieur exploitable. "
                          "L'annonce vend des « possibilités d'aménagement selon vos projets », ce qui "
                          "est une façon de dire qu'il y a des travaux sans les chiffrer. Un immeuble "
                          "de 1930 en centre ancien porte toiture, façade, électricité et évacuations : "
                          "budget retenu à zéro dans le scénario central, 6 000 € en Worst. À vérifier "
                          "en visite technique avant toute offre",
            },
        },
        "annonce": {
            "plateforme": "seloger",
            "url": "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/la-seyne-sur-mer-83500/267PVVC94GXQ",
            "prix_affiche_euros": PRIX,
            "prix_retenu_euros": PRIX,
            "prix_statut": "affiche",
            "vendeur": "Agence Papazian-Chovelon Porte Marine (Orpi), réf. 38035 — honoraires à la "
                       "charge du vendeur. Fiche agence réf. ROBGC : rue Cyrus Hugues, 1930, taxe "
                       "foncière 2 034 €",
        },
        "marche": {
            "valeur": {
                "basse_euros": 245000.0,
                "haute_euros": 300000.0,
                "retenue_euros": VALEUR,
                "source": "La rue d'abord, la commune ensuite. DVF rue Cyrus Hugues : 326 m² en immeuble "
                          "entier (quatre appartements et un local de 108 m²) à 340 000 € en 2022, "
                          "soit 1 043 €/m² ; 74 m² en deux appartements à 85 000 € en 2024, soit "
                          "1 149 €/m² ; 88 m² et dépendance à 138 210 € en 2024, soit 1 571 €/m² ; "
                          "100 m² en deux appartements à 275 530 € en 2021, soit 2 755 €/m², la seule "
                          "mutation haute de la rue. Le niveau de la rue est donc 1 100 à 1 600 €/m², "
                          "pas 2 700. Les repères communaux — appartements 60-100 m² à 2 706 €/m² de "
                          "médiane sur 1 863 ventes, locaux commerciaux à 1 586 €/m², quartier "
                          "Centre Ville-Peyron à 2 098 €/m² — décrivent le reste de La Seyne, pas "
                          "cette rue. Retenu 225 000 € pour 147 m², soit 1 530 €/m², au milieu de la "
                          "fourchette réelle de la rue et au-dessus de l'immeuble entier de 2022 "
                          "parce que celui-ci était en bloc. Fourchette 200 000 à 250 000 €. "
                          "Conséquence directe : à 245 000 €, le prix affiché ressort à 1 667 €/m², "
                          "soit le haut de la rue, et non une décote",
                "confiance": "moyenne",
            },
            "loyers": [
                {"lot": "Logement de trois pièces et deux chambres, sur deux niveaux, loué nu",
                 "quantite": 1,
                 "loyer_mensuel_euros": LOYER_LOGEMENT,
                 "occupe": True,
                 "note": "Aucun loyer annoncé — estimation. Médiane DHUP 2025 de la commune : "
                         "14,8 €/m² (IC 95 % 11,5 à 19,2), soit 1 150 €/mois pour un T4 de 85 m² et "
                         "13,5 €/m² sur les T3 et plus. Le centre-ville se loue autour de 15 €/m² "
                         "(Lapporteurdimmo, quartier Centre-ville), mais c'est le quartier le moins "
                         "cher à l'achat de la commune. Baux en place comparables dans le centre : "
                         "T2 de 29 m² à 415 € et T2 de 35 m² à 510 € (Fnaim, 2026), soit 14,3 à "
                         "14,6 €/m². Retenu 1 050 €/mois sur 92 m², soit 11,4 €/m² : sous la médiane, "
                         "parce que le logement est sur deux niveaux, classé D, sans extérieur et dans "
                         "un bâti de 1930 dont l'état n'est pas documenté"},
                {"lot": "Local commercial en rez-de-chaussée, exploité en boucherie-charcuterie",
                 "quantite": 1,
                 "loyer_mensuel_euros": LOYER_COMMERCE,
                 "occupe": True,
                 "note": "Aucun loyer annoncé, et c'est le poste le plus incertain du dossier : "
                         "l'annonce dit « actuellement exploité », sans dire si le local est loué ou "
                         "exploité par le vendeur. Estimation au marché du 24/10/2026 sur le "
                         "Centre Ville-Peyron : boutique de 72 m² à 600 € hors charges (8,33 €/m²), "
                         "boutique de 38 m² à 500 € (13,16 €/m²), local de 70 m² à 1 200 €, local de "
                         "65 m² sur axe à 1 300 €. Retenu 650 €/mois pour 55 m², soit 11,8 €/m², dans "
                         "la moyenne de la fourchette. Un bail commercial ancien peut porter 350 à "
                         "450 €, et un local vide peut rester six à douze mois sans preneur dans un "
                         "centre ancien"},
            ],
            "notes": "Assiette : deux loyers estimés, aucun documenté. Le logement pèse 62 % des "
                     "revenus, le commerce 38 % — c'est la branche résidentielle qui gouverne la "
                     "fiche, avec le plancher de 5 %. Si le local est vide ou loué sous 450 €, "
                     "l'assiette perd 200 à 650 €/mois et le dossier change de nature. Les deux baux "
                     "sont la première pièce à exiger.",
        },
        "hypotheses": {
            "vacance_base_pct": 6.0,
            "vacance_best_pct": 3.0,
            "vacance_worst_pct": 15.0,
            "taux_placement_reserve_pct": 2.84,
            "quote_part_bati_pct": 90.0,
            "vacance_justification": "Immeuble mixte : vacance pondérée par les revenus de chaque "
                                     "composante, 5 % en habitation et 8 % en commerce, soit 6,1 % "
                                     "arrondis à 6 % en base. 3 % en best, 15 % en worst — un local "
                                     "commercial vide six mois et un logement vide trois mois la même "
                                     "année, configuration courante dans un centre ancien",
            "charges": {
                "charges_copro_annuelles_euros": 0.0,
                "charges_copro_commentaire": "Aucune copropriété : immeuble en monopropriété. "
                                             "L'assurance de l'immeuble est portée par la ligne PNO",
                "taxe_fonciere_annuelle_euros": TF,
                "taxe_fonciere_commentaire": "2 034 €/an, montant donné par la fiche de l'agence. La "
                                            "part du local commercial n'est refacturable au preneur "
                                            "que si le bail le prévoit expressément : à vérifier, "
                                            "sinon elle reste au bailleur",
                "entretien_annuel_euros": 2336.0,
                "entretien_commentaire": "2 336 €/an : gestion locative déléguée à 6 % des loyers "
                                         "(1 224 €), provision d'impayés à 3 % (612 €, distincte de "
                                         "la vacance) et 500 € d'entretien courant d'un bâti de 1930",
                "pno_annuelle_euros": 300.0,
                "comptabilite_annuelle_euros": 0.0,
            },
            "frais_acquisition_euros": FRAIS,
            "frais_acquisition_commentaire": "8 % du prix (19 600 €), régime ancien ; honoraires à la "
                                             "charge du vendeur, donc hors base de calcul",
        },
        "analyse": {
            "branche": "residentiel",
            "type_operation": "locatif",
            "strategie_retenue": {
                "nom": "Conservation en bloc : logement loué nu, local commercial loué sous bail",
                "code": "ld-nue",
                "lots": 2,
            },
            "strategies_explorees": [],
            "attractivite": [
                {"dimension": "transports", "score": 8,
                 "justification": "Centre-ville de La Seyne : réseau Mistral dense, embarcadère vers "
                                  "Toulon et Les Sables, gare de Toulon à quinze minutes, A50 à "
                                  "proximité. Le locataire vit ici sans voiture, ce qui élargit la "
                                  "demande."},
                {"dimension": "commerces", "score": 7,
                 "justification": "Cœur commerçant à deux pas du port, marché, services et "
                                  "restauration. La rue Cyrus Hugues est une rue du centre ancien, "
                                  "pas un axe passant : la visibilité commerciale annoncée par "
                                  "l'agence est à relativiser, et c'est le loyer du local qui la "
                                  "mesurera."},
                {"dimension": "ecoles", "score": 6,
                 "justification": "Collège Marie Curie à 874 m, collège privé Sainte-Marie à 303 m, "
                                  "école Sainte-Thérèse à 428 m. L'offre existe, mais le logement de "
                                  "trois pièces en centre ancien vise un couple ou une petite famille, "
                                  "pas le cœur de cible familial."},
                {"dimension": "securite", "score": 4,
                 "justification": "Commune de 64 000 habitants avec deux quartiers prioritaires "
                                  "(Berthe, La Coupiane), 15 % de chômage et 4,2 cambriolages pour "
                                  "1 000 habitants. Le centre ancien est hétérogène : rue par rue, "
                                  "l'ambiance change. C'est le point faible du dossier et il se "
                                  "vérifie sur place, à deux moments de la journée."},
                {"dimension": "demande_locative", "score": 7,
                 "justification": "Vacance communale estimée à 8,8 %, marché locatif profond — 64 000 "
                                  "habitants, parc privé important — et petites surfaces qui se "
                                  "relouent. Les T2 du centre se louent 415 à 510 €. La demande pour "
                                  "un trois pièces de 90 m² existe, à condition que le loyer reste "
                                  "sous 1 100 €."},
                {"dimension": "dynamisme", "score": 6,
                 "justification": "Deuxième ville du Var, économie tournée vers Toulon, la mer et le "
                                  "port. Prix en hausse de 5 % sur trois ans, 1 100 transactions par "
                                  "an : la liquidité est là. Mais 15 % de chômage et un parc HLM à "
                                  "15 % : c'est un marché de revenus modestes, pas de croissance."},
            ],
            "risques": [
                {"facteur": "Aucun loyer annoncé, et le local commercial est le poste décisif",
                 "severite": 5, "detail": ""},
                {"facteur": "Le local : loué ou exploité par le vendeur ?", "severite": 4,
                 "detail": "L'annonce dit « actuellement exploité en boucherie-charcuterie » sans "
                           "préciser si le local est loué ou si le vendeur y exploite son propre "
                           "fonds. Si c'est le vendeur, le local est vide à la vente, le fonds n'est "
                           "pas dans le prix, et il faut retrouver un preneur : six à douze mois de "
                           "vacance commerciale dans un centre ancien sont un ordre de grandeur "
                           "courant, soit 4 000 à 8 000 € de loyers perdus. Si c'est un bail, il faut "
                           "sa date, son terme, son loyer et sa clause de renouvellement — un bail "
                           "commercial donne au preneur un droit au renouvellement, et un refus se "
                           "paie d'une indemnité d'éviction."},
                {"facteur": "Aucune ventilation des surfaces entre local et logement", "severite": 4,
                 "detail": "147 m² pour l'ensemble, sans plan ni Carrez. La répartition conditionne "
                           "tout : un local de 40 m² et un logement de 107 m² ne produisent pas les "
                           "mêmes loyers qu'un local de 70 m² et un logement de 77 m², et la valeur "
                           "de revente se calcule lot par lot. Plans, mesurage et DDT à exiger avant "
                           "toute offre."},
                {"facteur": "Immeuble de 1930, DPE D, travaux non chiffrés", "severite": 3,
                 "detail": "L'annonce vend des « possibilités d'aménagement », ce qui signifie qu'il "
                           "y a des travaux. Toiture, façade, électricité et évacuations d'un immeuble "
                           "de 1930 se vérifient en visite technique, et sans copropriété il n'y a "
                           "aucune mutualisation possible : tout tombe sur le propriétaire."},
                {"facteur": "Deux lots seulement, dont un commerce", "severite": 3,
                 "detail": "Un logement vide, c'est 62 % des revenus qui s'arrêtent ; un local vide, "
                           "38 %, et pour plus longtemps. Le dossier n'a aucun lissage : deux baux, "
                           "deux risques binaires."},
                {"facteur": "Rue bon marché : la valeur de sortie est bornée", "severite": 3,
                 "detail": "Les mutations de la rue Cyrus Hugues vont de 1 043 à 1 571 €/m² pour des "
                           "immeubles entiers, quand les appartements de la commune se vendent 2 706 "
                           "€/m². La décote de la rue est réelle et le prix affiché de 1 667 €/m² en "
                           "tient compte : il ne faut pas attendre une revente au prix des "
                           "appartements du reste de la commune."},
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
        rr["hypotheses"]["frais_acquisition_euros"] = round(prix * 0.08)
    return rr


def annuite(assiette, taux=0.038, mois=240, ass=0.0034):
    i = taux / 12.0
    return assiette * 0.9 * i / (1 - (1 + i) ** -mois) + assiette * 0.9 * ass / 12.0


def main():
    r = fiche()
    c = engine.compute(r)

    c_local_vide = engine.compute(variante(r, loyer2=0.0))
    c_local_bas = engine.compute(variante(r, loyer2=450.0))
    c_haut = engine.compute(variante(r, loyer=1150.0, loyer2=750.0))

    revient_division = PRIX * 1.08 + 60000.0
    sortie_basse = 92 * 1571.0 + 55 * 1312.0
    sortie_haute = 92 * 2098.0 + 55 * 1586.0

    r["analyse"]["strategies_explorees"] = [
        {"strategie": "Conservation en bloc : logement loué nu et local commercial loué",
         "lots": 2,
         "performance": f"{eur(LOYER_LOGEMENT + LOYER_COMMERCE)}/mois de recettes estimées, soit un "
                        f"rendement net après IS de {c['rendements']['net_sur_revient_pct']:.2f} % "
                        f"sur un prix de revient de {eur(c['prix_revient_total'])}. Sans le local, "
                        f"l'assiette tombe à {eur(LOYER_LOGEMENT)} et le rendement à "
                        f"{(c_local_vide['rendements']['net_sur_revient_pct']):.2f} %",
         "valeur_sortie": f"Revente à l'unité au niveau de la rue : logement 92 m² à 1 571 €/m² "
                          f"et local 55 m² à 1 312 €/m², soit {eur(sortie_basse)} ; au haut de la "
                          f"fourchette communale, {eur(sortie_haute)}. Contre "
                          f"{eur(c['prix_revient_total'])} de revient, la sortie détruit du capital "
                          f"dans la lecture basse et ne crée rien dans la haute",
         "faisabilite": "Immédiate si les deux baux sont en cours : deux lots, deux baux, aucune "
                        "copropriété à créer",
         "risque": "modéré — la performance dépend du loyer du local, qui n'est pas documenté"},
        {"strategie": "Revente à la découpe après division en deux lots vendables",
         "lots": 2, "rdt": None,
         "performance": f"{eur(sortie_basse)} à {eur(sortie_haute)} de produit de revente contre "
                        f"{eur(revient_division)} de revient avec 60 000 € de travaux de mise en état "
                        f"et de division. L'opération perd de l'argent : la rue Cyrus Hugues ne paie "
                        f"pas le prix des appartements de la commune",
         "valeur_sortie": f"{eur(sortie_basse)} à {eur(sortie_haute)}",
         "faisabilite": "Division en lots ou en volumes à créer, plan de vente, portage de 18 à "
                        "24 mois, structure commerciale",
         "risque": "élevé et sans objet : la découpe détruit de la valeur dans cette rue"},
        {"strategie": "Transformation du local commercial en logement supplémentaire",
         "lots": 3,
         "performance": "Écartée faute de données : la surface du local, la hauteur sous plafond, "
                        "l'ouverture en façade et la servitude de linéaire commercial du PLU ne sont "
                        "pas connues. Un local de 55 m² transformé en T2 rapporterait environ 750 €, "
                        "soit 100 € de plus que le loyer commercial retenu, pour 60 000 à 80 000 € de "
                        "travaux : le gain ne couvre pas le capital engagé",
         "valeur_sortie": "Un T2 supplémentaire vaut environ 2 100 €/m² dans ce quartier, soit "
                          "115 000 € pour 55 m² — mais seulement après autorisation",
         "faisabilite": "Changement de destination, déclaration préalable, vérification de la "
                        "servitude de linéaire commercial sur la rue, ouverture, ventilation, "
                        "compteurs",
         "risque": "élevé — et le gain de loyer ne justifie pas le chantier"},
    ]

    r["analyse"]["risques"][0]["detail"] = (
        f"L'annonce ne donne aucun loyer. À l'assiette estimée de "
        f"{eur(LOYER_LOGEMENT + LOYER_COMMERCE)}/mois, le rendement net après IS ressort à "
        f"{c['rendements']['net_sur_revient_pct']:.2f} % pour un prix de revient de "
        f"{eur(c['prix_revient_total'])}. Avec un bail commercial ancien à 450 €, il tombe à "
        f"{(c_local_bas['rendements']['net_sur_revient_pct']):.2f} % ; avec le local vide, à "
        f"{(c_local_vide['rendements']['net_sur_revient_pct']):.2f} %. C'est le seul chiffre qui "
        f"compte et il n'est pas dans l'annonce : sans les deux baux, le prix ne se discute pas, il "
        f"se constate."
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
          f"{(LOYER_LOGEMENT + LOYER_COMMERCE) * 12 / PRIX * 100:.2f} % | ratio coût/valeur "
          f"{c['ratio_cout_valeur']:.3f}")
    print(f"  EBE {fmt(c['fiscal']['ebe'])} | net après IS {fmt(c['fiscal']['net_apres_is'])} | "
          f"revient {fmt(c['prix_revient_total'])}")
    print(f"  prix plafond {fmt(plafond)} € ({contrainte}) | prix cible {fmt(cible)} €")
    print(f"  solde mensuel standard : {c['fiscal']['net_apres_is'] / 12 - annuite(PRIX):+.0f} €/mois")
    print(f"  local vide {c_local_vide['rendements']['net_sur_revient_pct']:.2f} % | local 450 € "
          f"{c_local_bas['rendements']['net_sur_revient_pct']:.2f} % | haut "
          f"{c_haut['rendements']['net_sur_revient_pct']:.2f} %")


if __name__ == "__main__":
    main()
