# -*- coding: utf-8 -*-
"""Écrit (ou met à jour) l'enregistrement Saint-Maximin dans analyses/analyses.json.

Un seul point d'écriture : le script relit le fichier, remplace l'enregistrement
de même slug s'il existe, et réécrit en conservant l'ordre. Relancer est sans
effet de bord.
"""
import json
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "scripts"))

from analyse_app.schema import validate_record, champs_manquants

SLUG = "2026-09-28-immeuble-saint-maximin-9-rue-daguerre"
ANNONCE = "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/saint-maximin-la-sainte-baume-83470/261QSCIG43MJ"

RECORD = {
    "slug": SLUG,
    "date_analyse": "2026-09-28",
    "date_maj": None,
    "titre": "Immeuble de rapport de 2 logements meublés (47,14 m² habitables) — 9 rue Daguerre, centre, Saint-Maximin-la-Sainte-Baume (83470)",
    "bien": {
        "type_bien": "immeuble",
        "sous_type": None,
        "type_detail": (
            "Immeuble de rapport construit avant 1948, au cœur du centre ancien, "
            "composé de deux logements meublés et d'annexes en rez-de-chaussée. "
            "T2 en duplex sur les 1er et 2e étages : 29,72 m² habitables, reloué meublé "
            "à partir du 7 octobre 2026 pour 600 € + 30 € de provisions. Studio au 3e étage "
            "avec mezzanine : 17,42 m² habitables, loué meublé depuis le 11 août 2026 pour "
            "430 € + 20 € de provisions. Rez-de-chaussée non habitable : hall, deux caves et "
            "une buanderie, 16,18 m² au total, exclus de la surface Carrez. "
            "Surface habitable totale 47,14 m², surface au sol 54,03 m² (attestation de "
            "mesurage n° 6418/EFA). Chauffage électrique individuel par panneaux rayonnants, "
            "eau chaude sur ballon électrique, ventilation par ouverture des fenêtres. "
            "Fenêtres bois double vitrage au T2, une partie en métal simple vitrage au studio. "
            "Taxe foncière 1 041 €/an annoncée par l'agence. Baux meublés d'un an renouvelables, "
            "dépôts de garantie de 1 200 € et 900 €. Honoraires d'agence à la charge du vendeur. "
            "Mandat n° 119, référence annonce 252, agence Nestenn Saint-Maximin."
        ),
        "neuf": False,
        "adresse": {
            "texte": "9 rue Daguerre, centre — Saint-Maximin-la-Sainte-Baume (83470)",
            "ville": "Saint-Maximin-la-Sainte-Baume",
            "code_postal": "83470",
            "quartier": "Centre ancien",
        },
        "surfaces": {
            "texte": (
                "47,14 m² habitables (29,72 + 17,42), 54,03 m² au sol, auxquels s'ajoutent "
                "16,18 m² de rez-de-chaussée non habitable (hall, deux caves, buanderie). "
                "L'annonce affiche 70 m² et calcule son prix au m² sur cette base, qui additionne "
                "l'habitable, les annexes et la mezzanine. Le prix au m² habitable réel à "
                "160 000 € est de 3 394 €, contre 2 286 € affichés."
            ),
            "carrez_m2": 47.14,
        },
        "lots": {
            "count": 2,
            "surface_par_lot_m2": None,
            "nature": (
                "Deux lots d'habitation meublés, plus des annexes en rez-de-chaussée dont le "
                "rattachement reste à confirmer : lots privés attachés aux logements ou parties "
                "communes. Chaque logement dispose d'un accès et de sanitaires indépendants."
            ),
            "lots_distincts": 2,
        },
        "copro": {
            "charges_annuelles_euros": 0.0,
            "charges_source": (
                "NON COMMUNIQUÉ à ce jour. Les deux logements sont loués avec 50 €/mois de "
                "provisions couvrant les charges générales et l'eau, mais ni le budget "
                "prévisionnel, ni les appels de fonds, ni les procès-verbaux d'assemblée, ni "
                "l'état daté ne nous ont été transmis. Le DPE relève une toiture non isolée. "
                "En attendant ces pièces, le moteur applique sa provision de 2,5 % des loyers "
                "(309 €/an), qui tient lieu de charge de copropriété et de risque travaux."
            ),
        },
        "travaux": {
            "montant_euros": 0.0,
            "nature": (
                "Aucun travaux engagé à l'acquisition, mais un passif prévisible que l'annonce "
                "ne mentionne pas : le DPE recommande l'isolation des murs et de la toiture, "
                "relève une toiture non isolée et des fenêtres métal simple vitrage au studio. "
                "Si le studio est classé E (320 kWh/m²/an), la location reste possible jusqu'en "
                "2034, ce qui fixe l'échéance des travaux au milieu de la vie d'un prêt de vingt "
                "ans. Les diagnostics électricité et plomb, obligatoires sur un bâti d'avant 1948, "
                "ne sont pas encore produits."
            ),
        },
    },
    "annonce": {
        "plateforme": "SeLoger",
        "url": ANNONCE,
        "prix_affiche_euros": 160000.0,
        "prix_retenu_euros": 122500.0,
        "prix_statut": "cible",
        "prix_commentaire": (
            "160 000 € affichés par l'agence Nestenn, honoraires à la charge du vendeur, soit "
            "3 394 €/m² habitable. Cible de négociation à 122 500 €, soit 2 599 €/m² : "
            "-23,4 % sous l'affichage et légèrement sous la médiane DVF de la commune pour "
            "cette tranche de surface (2 738 €/m², 41 mutations entre 25 et 60 m² en 2024-2025). "
            "Le prix affiché ne couvre pas sa mensualité sur quinze ans : le ratio EBE sur "
            "annuité tombe à 1,03 pour un seuil bancaire de 1,20, et le cash-flow est à "
            "-233 €/mois. C'est ce qui justifie la décote demandée, pas notre rendement."
        ),
    },
    "marche": {
        "valeur": {
            "basse_euros": 111600.0,
            "haute_euros": 163200.0,
            "retenue_euros": 127400.0,
            "source": (
                "DVF 2024-2025, mutations de 25 à 60 m² comportant au moins un appartement à "
                "Saint-Maximin-la-Sainte-Baume : 41 mutations. Prix au m² de 1 846 à 5 000, "
                "premier quartile 2 367, médiane 2 738, troisième quartile 3 462. Au m² médian, "
                "47,14 m² valent 129 000 € ; la valeur retenue de 127 400 € correspond à la "
                "médiane de la tranche. Comparables proches : 119 200 € pour 43 m², 107 000 € "
                "pour 44 m², 97 000 € pour 49 m², 151 000 € pour 60 m². Chiffres extraits des "
                "fichiers DVF 2024 et 2025 du Var, agrégés par mutation pour neutraliser les "
                "ventes multi-lots."
            ),
            "confiance": "moyenne",
        },
        "loyers": [
            {
                "lot": "T2 en duplex, 1er et 2e étages — bail meublé reloué au 7 octobre 2026",
                "quantite": 1,
                "loyer_mensuel_euros": 600.0,
                "occupe": True,
                "note": (
                    "600 €/mois hors charges, plus 30 € de provisions sur charges générales et "
                    "eau. Soit 20,2 €/m² pour 29,72 m². L'agent annonce un bail reloué au "
                    "7 octobre : la signature reste à confirmer, c'est une question posée. "
                    "Bail meublé d'un an renouvelable, dépôt de 1 200 €."
                ),
            },
            {
                "lot": "Studio au 3e étage avec mezzanine — bail meublé en cours depuis le 11 août 2026",
                "quantite": 1,
                "loyer_mensuel_euros": 430.0,
                "occupe": True,
                "note": (
                    "430 €/mois hors charges, plus 20 € de provisions. 24,7 €/m² pour 17,42 m² : "
                    "le loyer au mètre carré d'un studio meublé, à la limite haute du marché "
                    "local. Bail meublé d'un an renouvelable, dépôt de 900 €."
                ),
            },
        ],
        "notes": (
            "Deux baux meublés d'un an renouvelables, soit 1 030 €/mois hors charges et "
            "12 360 €/an, pour 47,14 m² habitables. Les loyers au mètre carré (20,2 et "
            "24,7 €/m²) sont élevés pour une commune de cette taille : c'est la prime du meublé "
            "et des petites surfaces. Elle protège le dossier aujourd'hui, elle le fragilise si "
            "l'un des deux logements se reloue en nu ou après un long délai."
        ),
    },
    "hypotheses": {
        "vacance_base_pct": 5.0,
        "vacance_best_pct": 2.0,
        "vacance_worst_pct": 20.0,
        "vacance_justification": (
            "5 % en base : deux baux meublés, donc un préavis d'un mois seulement, sur deux "
            "logements dont un vient d'être reloué. Scénario favorable 2 % (les deux locataires "
            "restent), scénario défavorable 20 % (un départ, quatre mois de vacance et une "
            "relocation sous le loyer en place)."
        ),
        "charges": {
            "charges_copro_annuelles_euros": 0.0,
            "charges_copro_commentaire": (
                "Aucune charge de copropriété annoncée : ni budget prévisionnel, ni appels de "
                "fonds. Les 50 €/mois payés par les locataires sont des provisions, pas une "
                "charge certaine. Le moteur applique donc sa provision de 2,5 % des loyers "
                "(309 €/an) en attendant les pièces."
            ),
            "taxe_fonciere_annuelle_euros": 1041.0,
            "taxe_fonciere_commentaire": (
                "1 041 €/an annoncés par l'agence le 28 septembre 2026, pour l'immeuble entier. "
                "Chiffre déclaratif : l'avis de taxe foncière et le montant de la TEOM sont "
                "demandés, pour vérifier ce qui est refacturable aux locataires."
            ),
            "pno_annuelle_euros": 200.0,
            "comptabilite_annuelle_euros": 300.0,
            "comptabilite_commentaire": (
                "300 €/an, soit 150 € par lot : coût marginal de deux logements dans une "
                "comptabilité de SCI déjà portée par le parc. Deux opérations mensuelles et "
                "deux annuelles par lot."
            ),
            "provision_desactivee": False,
            "provision_commentaire": (
                "Provision maintenue à 2,5 % des loyers (309 €/an) : elle couvre l'absence "
                "d'information sur la copropriété et le passif travaux que le DPE laisse voir. "
                "C'est la seule prudence qu'on peut s'offrir tant que l'état daté et les "
                "procès-verbaux ne sont pas là."
            ),
        },
        "frais_acquisition_euros": 9188.0,
        "frais_acquisition_commentaire": (
            "7,5 % du prix, soit 9 188 € pour un immeuble ancien. Barème constaté sur le "
            "secteur, à confirmer par le devis du notaire."
        ),
        "quote_part_bati_pct": 75.0,
        "duree_amortissement_ans": 35,
        "taux_placement_reserve_pct": 2.84,
        "taux_placement_reserve_commentaire": (
            "La vacance et la provision travaux ne sont pas perdues : elles forment notre "
            "mini-ALUR interne, placé sur un fonds monétaire en euros à 2,84 % net de frais "
            "relevé le 28 septembre 2026. Produits bruts d'IS, la SCI étant à l'impôt sur les "
            "sociétés."
        ),
    },
    "analyse": {
        "branche": "residentiel",
        "type_operation": "locatif",
        "strategie_retenue": {
            "nom": "Deux logements meublés en location longue durée, locataires en place",
            "code": "ld-meuble",
            "lots": 2,
        },
        "strategies_explorees": [
            {
                "strategie": "Deux meublés longue durée — locataires en place",
                "rendement": "6,7 % net d'IS sur prix de revient à 122 500 €",
                "faisabilite": "Immédiate, deux baux en cours",
                "risque": "faible",
            },
            {
                "strategie": "Location nue des deux lots",
                "rendement": "inférieur",
                "faisabilite": "À la relocation seulement",
                "risque": "élevé — on perd la prime du meublé et le mobilier cesse d'être amorti",
            },
            {
                "strategie": "Location courte durée",
                "rendement": "non retenu",
                "faisabilite": "Réglementation et registre en commune touristique",
                "risque": "élevé — rotation, gestion, deux petits lots à équiper",
            },
            {
                "strategie": "Rémembrement des deux lots en un logement unique",
                "rendement": "sans objet",
                "faisabilite": "À vérifier au règlement de copropriété",
                "risque": "on divise le revenu par deux pour un seul bail",
            },
        ],
        "attractivite": [
            {
                "dimension": "transports",
                "score": 5,
                "justification": (
                    "Pas de gare sur la commune : le réseau régional passe par Aix ou Marseille, "
                    "et la voiture reste indispensable. En revanche l'autoroute A8 et la N7 "
                    "irriguent la ville, avec un bassin d'emploi qui va d'Aix à Saint-Maximin."
                ),
            },
            {
                "dimension": "commerces",
                "score": 7,
                "justification": (
                    "Centre ancien commerçant, marchés provençaux, zones commerciales en "
                    "périphérie : Saint-Maximin est la ville-centre d'un bassin d'environ "
                    "17 000 habitants, à 40 km d'Aix-en-Provence."
                ),
            },
            {
                "dimension": "ecoles",
                "score": 7,
                "justification": (
                    "Écoles, collèges et lycée sur la commune : l'offre scolaire complète "
                    "soutient la demande des jeunes ménages, qui manque pourtant de petits "
                    "logements à loyer modéré."
                ),
            },
            {
                "dimension": "securite",
                "score": 5,
                "justification": (
                    "Centre ancien dense, avec les nuisances habituelles de ce tissu "
                    "(stationnement, incivilités nocturnes). Les deux logements sont en étage, "
                    "avec caves et buanderie en rez-de-chaussée."
                ),
            },
            {
                "dimension": "demande_locative",
                "score": 7,
                "justification": (
                    "Le studio a été reloué en août et le T2 se reloue début octobre : les deux "
                    "lots trouvent preneur rapidement, ce qui valide la demande et le niveau de "
                    "loyer sur ce créneau de petites surfaces meublées."
                ),
            },
            {
                "dimension": "dynamisme",
                "score": 5,
                "justification": (
                    "100 mutations comportant au moins un appartement en deux ans sur la "
                    "commune : le marché existe mais reste étroit, et la profondeur de revente "
                    "d'un petit immeuble de rapport se compte en trimestres."
                ),
            },
        ],
        "risques": [
            {
                "facteur": "Copropriété entièrement inconnue",
                "severite": 4,
                "detail": (
                    "Ni budget prévisionnel, ni appels de fonds, ni procès-verbaux, ni état "
                    "daté, ni charges annoncées. Or le DPE relève une toiture non isolée : une "
                    "assemblée qui vote un ravalement ou une réfection de toiture fait tomber "
                    "plusieurs milliers d'euros sur notre quote-part, sans qu'aucun plafond "
                    "n'ait été calculé pour l'absorber. C'est la première pièce à obtenir."
                ),
            },
            {
                "facteur": "Diagnostics électricité et plomb non produits",
                "severite": 4,
                "detail": (
                    "Le bâti date d'avant 1948 : le diagnostic électricité et le constat de "
                    "risque d'exposition au plomb sont obligatoires à la vente et peuvent "
                    "chacun déclencher une mise en sécurité ou un traitement lourd. Sur un "
                    "immeuble de deux logements, ces deux postes se chiffrent en milliers "
                    "d'euros, à ajouter au prix s'ils ressortent défavorables."
                ),
            },
            {
                "facteur": "Classe DPE E et échéance 2034",
                "severite": 3,
                "detail": (
                    "Le studio consomme 320 kWh/m²/an, en limite de la classe E, et une partie "
                    "de ses fenêtres est en métal simple vitrage. Si la classe E est confirmée, "
                    "les travaux deviennent obligatoires avant 2034, en pleine vie d'un prêt de "
                    "vingt ans. L'annonce, elle, n'affiche que la meilleure des deux étiquettes."
                ),
            },
            {
                "facteur": "Le dossier ne passe qu'à vingt ans",
                "severite": 3,
                "detail": (
                    "À 122 500 €, le ratio EBE sur annuité est de 1,03 sur quinze ans, contre "
                    "1,20 exigé par la banque, et le cash-flow est nul. Il faut allonger à vingt "
                    "ans pour atteindre 1,27 et +132 €/mois. Un prêteur qui refuse les vingt "
                    "ans rend le dossier intenable au prix cible."
                ),
            },
            {
                "facteur": "Charges d'eau en provisions, sans comptage",
                "severite": 2,
                "detail": (
                    "Les 20 et 30 € de provisions couvrent l'eau. Sans compteur divisionnaire, "
                    "une surconsommation se régularise sur le propriétaire, et la répartition "
                    "entre les deux lots devient arbitraire. À clarifier avant le compromis."
                ),
            },
            {
                "facteur": "Deux baux meublés d'un an",
                "severite": 2,
                "detail": (
                    "Deux préavis d'un mois suffisent à vider l'immeuble. La vacance "
                    "structurelle du meublé est plus élevée que celle du nu, et le mobilier se "
                    "dégrade : il faudra prévoir son renouvellement, sans base d'inventaire."
                ),
            },
        ],
    },
    "champs_manquants": [
        "Copropriété : budget prévisionnel, deux derniers appels de fonds, procès-verbaux, "
        "carnet d'entretien, état daté",
        "Diagnostics électricité et plomb, et la classe DPE de chaque logement",
        "Avis de taxe foncière complet et montant de la TEOM",
        "Travaux votés ou à l'étude sur la toiture et les parties communes",
        "Rattachement des caves et de la buanderie : lots privés ou parties communes",
        "Confirmation de la signature du bail du T2 au 7 octobre",
        "Inventaire du mobilier des deux meublés",
        "Compteurs d'eau divisionnaires et mode de régularisation",
    ],
}


def main():
    chemin = os.path.join(RACINE, "analyses", "analyses.json")
    data = json.load(open(chemin, encoding="utf-8"))
    erreurs = validate_record(RECORD)
    if erreurs:
        print("ERREURS DE SCHÉMA :")
        for e in erreurs:
            print(" -", e)
        return 1
    manquants = champs_manquants(RECORD)
    if manquants:
        print("Champs manquants :", manquants)
    analyses = data["analyses"]
    avant = len(analyses)
    analyses = [a for a in analyses if a.get("slug") != SLUG]
    analyses.append(RECORD)
    analyses.sort(key=lambda a: (a.get("date_analyse") or "", a.get("slug") or ""), reverse=True)
    data["analyses"] = analyses
    with open(chemin, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(f"enregistrements : {avant} -> {len(analyses)}")
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
