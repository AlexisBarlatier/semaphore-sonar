"""Saisie du record — La Seyne-sur-Mer, hyper centre : 2 pièces loué 550 € + 5 boxes.

Source de vérité : `analyses/analyses.json` (entrées seulement, aucun résultat calculé).
Chiffres validés dans le fil du 2 octobre 2026 et recalculés par le moteur.

Usage :
    venv/bin/python3 scripts/saisie_record_la_seyne_hyper_centre_2p_bureau.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyse_app import schema  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEMIN = os.path.join(RACINE, "analyses", "analyses.json")
SLUG = "2026-10-02-la-seyne-hyper-centre-2p-bureau"

RECORD = {
    "slug": SLUG,
    "date_analyse": "2026-10-02",
    "date_maj": None,
    "titre": "2 pièces de 50 m² vendu loué et espace bureau de 30 m² à transformer en boxes — hyper centre, La Seyne-sur-Mer (83500)",
    "bien": {
        "type_bien": "appartement",
        "sous_type": None,
        "type_detail": (
            "Rez-de-chaussée d'un immeuble de 1950, dans l'hyper centre, copropriété de deux lots au total. "
            "Un 2 pièces de 50 m² (séjour 17,50 m², kitchenette équipée, une chambre, salle d'eau avec WC), vendu loué "
            "550 €/mois par bail en cours. Au rez-de-jardin, un espace bureau de 30 m² avec sa propre kitchenette et sa "
            "salle d'eau avec WC, vacant, desservi par une entrée distincte. Le bas dispose donc de son propre accès : "
            "il est louable, ou divisible en boxes, sans passer par le logement. Chauffage individuel électrique, "
            "85 €/mois estimés par le simulateur de l'annonce. Surface habitable annoncée 50 m², non confirmée en Carrez. "
            "Aucun DPE publié — l'annonce indique « DPE en cours ». Aucun stationnement. Copropriété de 2 lots, "
            "le second lot appartient à un tiers dont le statut d'occupation n'est pas connu. Vendeur : iad France, "
            "Sophia Benbella (06 27 16 98 52), référence 2126420, annonce Leboncoin 3280288123, honoraires à la charge du vendeur."
        ),
        "neuf": False,
        "adresse": {
            "texte": "Hyper centre, quartier Est — La Seyne-sur-Mer (83500)",
            "ville": "La Seyne-sur-Mer",
            "code_postal": "83500",
            "quartier": "Hyper centre",
        },
        "surfaces": {
            "texte": (
                "50 m² habitables annoncés (surface « habitable », non Carrez) pour le 2 pièces, auxquels s'ajoutent "
                "30 m² de rez-de-jardin décrits comme espace bureau avec kitchenette et salle d'eau. Sur les 80 m² "
                "cumulés, le prix demandé sort à 838 €/m². Aucune surface Carrez produite à ce stade."
            ),
            "carrez_m2": 50.0,
        },
        "lots": {
            "count": 6,
            "surface_par_lot_m2": None,
            "nature": (
                "Un logement (2 pièces, 50 m²) et cinq boxes à créer dans les 30 m² du rez-de-jardin par simple "
                "cloisonnement. Le bas est accessible indépendamment et destiné à être loué à des commerçants du "
                "centre-ville pour du stockage, ou à des particuliers. Le PLU répute les locaux accessoires avoir la "
                "destination du local principal : des boxes rattachés à un lot d'habitation ne créent pas de changement "
                "de destination, donc ni déclaration préalable, ni permis de diviser, ni place de stationnement exigée "
                "pour un logement créé. Confirmations à obtenir sur le règlement de copropriété et auprès du service "
                "de l'urbanisme."
            ),
            "lots_distincts": 6,
        },
        "copro": {
            "charges_annuelles_euros": 600.0,
            "charges_source": (
                "Non communiqué. Hypothèse de 300 €/lot/an sur une copropriété de deux lots sans ascenseur, soit "
                "600 €/an. Ni budget prévisionnel, ni appel de fonds, ni procès-verbaux, ni état daté ne nous ont été "
                "transmis. À obtenir avant toute signature."
            ),
        },
        "travaux": {
            "montant_euros": 10000.0,
            "nature": (
                "Division du rez-de-jardin en cinq boxes : cloisons, cinq portes, cinq points lumineux et interrupteurs, "
                "luminaires, reprise de sol et peinture. Aucune création de réseau ni de salle d'eau, l'espace en est déjà "
                "équipé. Aucun devis : montant arrêté avec Rémy sur la base d'une rénovation légère de cloisonnement. "
                "Le compteur individuel du bas reste à vérifier — s'il n'existe pas, c'est un poste supplémentaire. "
                "Aucune autorisation d'urbanisme attendue pour ce programme, la façade et la structure n'étant pas touchées."
            ),
        },
    },
    "annonce": {
        "plateforme": "Leboncoin",
        "url": "https://www.leboncoin.fr/ad/ventes_immobilieres/3280288123",
        "prix_affiche_euros": 67000.0,
        "prix_retenu_euros": 67000.0,
        "prix_statut": "affiche",
        "prix_commentaire": (
            "67 000 € honoraires à la charge du vendeur, soit 1 340 €/m² sur les 50 m² habitables annoncés et 838 €/m² "
            "sur les 80 m² du lot entier. Le même agent vend dans la même commune un local de 27 m² à 58 000 €, "
            "soit 2 148 €/m², et l'annonce voisine d'un T2 de 57 m² du quartier Est est affichée à 100 000 €. "
            "Le prix demandé est donc très inférieur au marché au mètre carré : c'est ce qui justifie de chercher la "
            "contrainte non écrite (qualification du local, copropriété, stationnement) plutôt qu'une remise. Offre de "
            "négociation à 61 000 €, qui reste le prix d'équilibre sur vingt ans du logement seul ; au-dessus, on paie le "
            "bas avant de l'avoir exploité."
        ),
    },
    "marche": {
        "valeur": {
            "basse_euros": 100000.0,
            "haute_euros": 135000.0,
            "retenue_euros": 117000.0,
            "source": (
                "Aucune mutation DVF exploitable : l'extraction locale du Var ne contient pas la commune, ni par le nom "
                "ni par le code INSEE. Valeur ancrée sur deux comparables directs de la même commune relevés sur le même "
                "portail : local de 27 m² au centre à 58 000 €, soit 2 148 €/m² (le même agent), et T2 de 57 m² quartier Est "
                "à 100 000 €, soit 1 754 €/m². Valeur retenue 117 000 €, soit 50 m² d'habitation autour de 1 750 €/m² "
                "(87 500 €) plus 30 m² de rez-de-chaussée valorisés 1 000 €/m² (30 000 €), le rez-de-chaussée boxable "
                "valant moins au mètre carré qu'un logement. Fourchette 100 000 à 135 000 €. Confiance faible : "
                "aucune transaction signée, seulement des prix affichés."
            ),
            "confiance": "faible",
        },
        "loyers": [
            {
                "lot": "2 pièces de 50 m² au rez-de-chaussée — vendu loué, bail en cours",
                "quantite": 1,
                "loyer_mensuel_euros": 550.0,
                "occupe": True,
                "note": (
                    "Loyer en place selon l'annonce, soit 11 €/m²/mois. Nos relevés de petites surfaces à La Seyne "
                    "montrent un studio de 19 m² au centre Peyron loué 420 €/mois, soit 22 €/m² : le bail du 2 pièces est "
                    "donc ancien. Date de prise d'effet, type de bail et indice de révision à demander. Aucune revalorisation "
                    "n'est intégrée au modèle."
                ),
            },
            {
                "lot": "Cinq boxes de 5 à 6 m² au rez-de-jardin — à créer et à louer",
                "quantite": 5,
                "loyer_mensuel_euros": 70.0,
                "occupe": False,
                "note": (
                    "Hypothèse de 70 €/mois par box. Relevés du marché local : cave de 3 m² chez un particulier à 40 et 60 €/mois "
                    "(13 à 20 €/m²), box de 4 à 6 m² en garde-meuble à 96 €/mois, box professionnel de 5 m² à 125 €/mois, "
                    "box de 14 m² chez un particulier à 150 €/mois, soit 11 €/m². Le loyer retenu se situe sous la moyenne "
                    "des box professionnels et à la hauteur des caves de particuliers. Ces boxes sont des accessoires d'un lot "
                    "d'habitation : ils ne changent pas la destination et ne comptent pas comme création de logement."
                ),
            },
        ],
        "notes": (
            "Le dossier tient entièrement à l'exploitation du rez-de-chaussée. Logement seul, le prix d'équilibre tombe "
            "à 49 700 € à quinze ans, très en dessous de ce que vaut le bien sur le marché : aucun vendeur ne signe là. "
            "Boxes loués, l'équilibre passe au-dessus du prix affiché."
        ),
    },
    "hypotheses": {
        "vacance_base_pct": 5.0,
        "vacance_best_pct": 2.0,
        "vacance_worst_pct": 20.0,
        "vacance_justification": (
            "Cinq pour cent en scénario central, comme sur les autres dossiers. Vingt pour cent en scénario pessimiste, "
            "soit plus d'un lot vide sur six : c'est le test qui compte ici, cinq boxes à remplir simultanément créant cinq "
            "occasions de vacance au lieu d'une. Le scénario pessimiste du dossier à 20 % de vacance laisse encore un "
            "cash-flow positif à quinze ans."
        ),
        "charges": {
            "charges_copro_annuelles_euros": 600.0,
            "charges_copro_commentaire": "Hypothèse 300 €/lot/an, copropriété de deux lots sans ascenseur. Non communiqué.",
            "taxe_fonciere_annuelle_euros": 800.0,
            "taxe_fonciere_commentaire": "Estimation pour un rez-de-chaussée de 80 m² à La Seyne. Avis de taxe foncière à demander.",
            "pno_annuelle_euros": 100.0,
            "pno_annuelle_commentaire": "Assurance propriétaire non occupant, montant symbolique : des boxes vides et cloisonnés ne contiennent rien de valeur.",
            "comptabilite_annuelle_euros": 900.0,
            "comptabilite_commentaire": "Coût marginal de tenue de comptes à 150 €/an par lot, soit six lots : le logement et les cinq boxes. Six baux, c'est six fois la gestion.",
        },
        "frais_acquisition_euros": 7000.0,
        "frais_acquisition_commentaire": (
            "Frais réels estimés à 7 000 € sur 67 000 €, soit 10,4 %. Le simulateur de l'annonce affiche 5 360 €, "
            "soit 8 % : sur un ticket de cette taille, les émoluments et débours fixes pèsent plus lourd que le taux."
        ),
        "quote_part_bati_pct": 90.0,
        "duree_amortissement_ans": 30,
        "taux_placement_reserve_pct": 2.84,
        "taux_placement_reserve_commentaire": "Taux du fonds monétaire au 28 septembre 2026, net de frais. Notre mini-ALUR interne, réserve de vacance et de travaux.",
    },
    "analyse": {
        "branche": "residentiel",
        "type_operation": "locatif",
        "strategie_retenue": {
            "nom": "Location nue du 2 pièces en place et de cinq boxes de stockage créés au rez-de-jardin",
            "code": "ld-nue",
            "lots": 6,
        },
        "strategies_explorees": [
            {
                "strategie": "Logement seul, rez-de-chaussée laissé vacant",
                "rendement": "5,6 % net d'IS sur prix de revient au prix affiché",
                "faisabilite": "Immédiate, un bail en cours",
                "risque": "Élevé — le prix d'équilibre tombe à 49 700 € à quinze ans, aucune négociation réaliste n'y mène",
            },
            {
                "strategie": "Création d'un studio dans les 30 m² du bas",
                "rendement": "supérieur aux boxes — environ 13 % net sur prix de revient avec 500 €/mois",
                "faisabilite": "Six mois d'autorisations, et rien n'est acquis",
                "risque": "Élevé — changement de destination, permis de diviser sous conditions de stationnement, unanimité de la copropriété pour changer l'affectation du lot, taxe d'aménagement. Aucun vendeur ne bloque un bien à 67 000 € pendant six mois",
            },
            {
                "strategie": "Rez-de-jardin loué en un seul lot à un commerçant, comme réserve",
                "rendement": "inférieur — environ 260 €/mois sur 30 m²",
                "faisabilite": "Immédiate, un seul bail",
                "risque": "Faible — moins de gestion, mais on renonce à 90 €/mois de loyer",
            },
            {
                "strategie": "Caves conservées en accessoires des deux logements",
                "rendement": "sans objet",
                "faisabilite": "Immédiate",
                "risque": "Aucun — argument de relocation, zéro gestion supplémentaire, mais aucun revenu direct",
            },
            {
                "strategie": "Location meublée ou colocation du 2 pièces",
                "rendement": "supérieur de 5 à 10 % sur le loyer",
                "faisabilite": "À la relocation seulement",
                "risque": "Moyen — le bail en cours est nu, et la fiscalité du meublé se durcit à compter de 2027",
            },
        ],
        "attractivite": [
            {
                "dimension": "transports",
                "score": 6,
                "justification": "L'annonce cite les lignes de bus et l'accès rapide vers Toulon et les plages. Pas de gare dans le quartier, la voiture reste utile, mais La Seyne est desservie par le réseau métropolitain et la RD559 vers Toulon est à proximité.",
            },
            {
                "dimension": "commerces",
                "score": 7,
                "justification": "Hyper centre : commerces de proximité immédiats, marché, services. C'est exactement le tissu qui fait vivre des boxes de stockage, les commerçants de centre-ville manquant de réserves.",
            },
            {
                "dimension": "ecoles",
                "score": 7,
                "justification": "Établissements scolaires de proximité cités par l'annonce — collège, écoles maternelle et primaire, lycée et enseignement supérieur recensés autour du bien. Le quartier est un quartier de vie, pas une zone d'activité.",
            },
            {
                "dimension": "securite",
                "score": 5,
                "justification": "Centre ancien dense de 1950, avec les nuisances habituelles de ce tissu : stationnement difficile, passages nocturnes. Le lot est un rez-de-chaussée sur rue, cinq boxes cloisonnés et fermés exposant moins qu'un logement vide au même endroit.",
            },
            {
                "dimension": "demande_locative",
                "score": 7,
                "justification": "La demande sur les deux créneaux est documentée : studios de 19 m² loués 420 € au centre Peyron, boxes de 5 m² à 125 €/mois chez un professionnel, 47 annonces de box et parkings sur le portail local, 26 à Toulon. Ce sont des relevés, pas des hypothèses. La réserve est la vitesse de commercialisation de cinq boxes à la fois.",
            },
            {
                "dimension": "dynamisme",
                "score": 6,
                "justification": "Commune de plus de 60 000 habitants dans la métropole toulonnaise, marché profond à l'échelle de la ville, mais aucune donnée de mutation exploitable dans notre extraction DVF pour chiffrer la profondeur de la tranche. Le même agent y commercialise plusieurs petits lots, signe d'un marché secondaire actif sur ces surfaces.",
            },
        ],
        "risques": [
            {
                "facteur": "Qualification juridique du local du rez-de-jardin",
                "severite": 3,
                "detail": "L'annonce le décrit comme un espace bureau. S'il est déclaré en local professionnel ou commercial, sa transformation en logement relève d'un changement de destination, et l'affectation du lot exige l'accord de l'assemblée des copropriétaires à l'unanimité — dans une copropriété de deux lots, l'autre propriétaire bloque seul. Notre programme de boxes écarte ce risque, les locaux accessoires étant réputés avoir la destination du local principal. Reste à vérifier au règlement de copropriété et à l'état descriptif de division.",
            },
            {
                "facteur": "Charges de copropriété inconnues",
                "severite": 3,
                "detail": "Aucun budget prévisionnel, aucun appel de fonds, aucun procès-verbal, aucun état daté. Le modèle retient 600 €/an d'hypothèse. Sur un immeuble de 1950, une assemblée qui vote un ravalement ou une toiture fait tomber plusieurs milliers d'euros sur notre quote-part, sans qu'aucun plafond n'ait été calculé pour l'absorber.",
            },
            {
                "facteur": "Cinq boxes à commercialiser simultanément",
                "severite": 3,
                "detail": "Les loyers unitaires sont documentés, mais la demande porte sur quatre petits lots ou moins à la fois dans ce quartier : deux annonces de box à 100 € dans le secteur. Un démarrage lent signifie plusieurs mois à zéro sur le bas, et cinq occasions de vacance au lieu d'une. Le scénario pessimiste à 20 % de vacance laisse néanmoins le dossier positif à quinze ans.",
            },
            {
                "facteur": "Aucun DPE ni diagnostic produit",
                "severite": 3,
                "detail": "L'annonce indique « DPE en cours » alors qu'un immeuble de 1950 doit déjà en disposer à la vente. Le chauffage est électrique : la classe conditionne les travaux d'ici 2034 et le confort de relocation du logement. Diagnostics électricité, amiante et plomb également à obtenir, le bâti étant antérieur à 1948.",
            },
            {
                "facteur": "Compteur individuel du rez-de-chaussée non vérifié",
                "severite": 2,
                "detail": "Rémy suppose que le bas dispose de son propre compteur puisqu'il est indépendant. Si ce n'est pas le cas, la pose est un poste supplémentaire non chiffré, et la refacturation d'électricité aux cinq locataires devient arbitraire sans comptage individuel.",
            },
            {
                "facteur": "Bail du 2 pièces sous le marché et sans pièce produite",
                "severite": 2,
                "detail": "550 € pour 50 m², soit 11 €/m²/mois, la moitié du loyer au mètre carré de nos relevés de petites surfaces à La Seyne. C'est un bail ancien : date de prise d'effet, indice de révision, type de bail et intention du locataire sont à demander, et aucune revalorisation n'est intégrée au modèle.",
            },
            {
                "facteur": "Vendeur peu enclin à une condition suspensive",
                "severite": 2,
                "detail": "Sur un bien de ce prix, un vendeur n'attendra pas six mois d'autorisations. C'est l'argument décisif en faveur du programme de boxes, qui ne demande aucune autorisation et permet de signer vite.",
            },
        ],
    },
}


def main():
    with open(CHEMIN, encoding="utf-8") as fh:
        base = json.load(fh)
    if list(base.keys()) != ["meta", "analyses"]:
        raise SystemExit("Structure inattendue, clés racine : %s" % list(base.keys()))
    avant = len(base["analyses"])
    base["analyses"] = [r for r in base["analyses"] if r.get("slug") != SLUG]
    base["analyses"].append(RECORD)
    base["meta"]["count"] = len(base["analyses"])

    record = next(r for r in base["analyses"] if r["slug"] == SLUG)
    record["champs_manquants"] = schema.champs_manquants(record)
    erreurs = schema.validate_record(record)
    if erreurs:
        print("RECORD INVALIDE :")
        for e in erreurs:
            print("  -", e)
        raise SystemExit(1)

    with open(CHEMIN, "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False, indent=2)

    with open(CHEMIN, encoding="utf-8") as fh:
        relu = json.load(fh)
    apres = len(relu["analyses"])
    slugs = [r["slug"] for r in relu["analyses"]]
    print("analyses : %d -> %d" % (avant, apres))
    print("cles racine relues :", list(relu.keys()))
    print("occurrences du slug :", slugs.count(SLUG))
    print("champs manquants :", record["champs_manquants"])


if __name__ == "__main__":
    main()
