#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cree la fiche de l'immeuble de rapport de Vidauban (4 lots, centre-ville) et la genere."""
import importlib.util, json, os, sys

ROOT = '/home/alexis-barlatier/Documents/Semaphore-sonar'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from analyse_app import schema

BASE = os.path.join(ROOT, 'analyses', 'analyses.json')
SLUG = "2026-09-15-immeuble-rapport-vidauban-centre"
URL = "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/vidauban-83550/26UCYRMCT738"

RECORD = {
    "slug": SLUG,
    "date_analyse": "2026-09-15",
    "date_maj": None,
    "titre": "Vidauban — immeuble de rapport 4 lots en centre-ville (local commercial + 3 T2)",
    "bien": {
        "type_bien": "immeuble",
        "sous_type": None,
        "type_detail": (
            "Immeuble de rapport en R+3, 230 m² annoncés, construit en 1900, entièrement loué. "
            "Rez-de-chaussée : local commercial de 47 m² en activité, complété par 3 réserves de 35 m². "
            "1er, 2e et 3e étages : trois T2 de 50 m² d'agencement identique (entrée, cuisine, séjour, 1 chambre, salle d'eau, WC séparé). "
            "Dernier niveau : 3 greniers (potentiel de stockage ou valorisation). Annexes : 4 caves, 1 débarras, jardin, parties communes. "
            "MONOPROPRIÉTÉ : aucune charge de copropriété. Compteurs électriques indépendants. "
            "Emplacement n°1 en plein cœur du centre-ville, à proximité immédiate des commerces et des parkings. "
            "Travaux de rafraîchissement à prévoir dans les appartements (annoncés par l'agence), aucune urgence puisque tous les lots sont loués."
        ),
        "neuf": False,
        "adresse": {
            "texte": "Centre-ville de Vidauban (83550) — adresse exacte non communiquée dans l'annonce",
            "ville": "Vidauban",
            "code_postal": "83550"
        },
        "surfaces": {
            "texte": "230 m² annoncés, incluant le local commercial (47 m²), ses réserves (35 m²), les trois T2 (150 m²) et les greniers",
            "carrez_m2": 230.0
        },
        "lots": {
            "count": 4,
            "surface_par_lot_m2": None,
            "nature": "1 local commercial de 47 m² (+ 35 m² de réserves) + 3 T2 de 50 m² + 3 greniers + 4 caves + débarras",
            "lots_distincts": 4
        },
        "copro": {
            "charges_annuelles_euros": 0.0,
            "charges_source": "Monopropriété : aucune charge de copropriété. Les seules charges sont la taxe foncière, l'assurance, l'entretien et la comptabilité."
        },
        "travaux": {
            "montant_euros": 40000.0,
            "nature": (
                "Rafraîchissement des trois T2 annoncé par l'agence (peintures, sols, remise en état des salles d'eau et des cuisines). "
                "Enveloppe retenue 40 000 € (environ 470 €/m² sur les 150 m² de logements), à engager À LA ROTATION des locataires et non à l'acquisition : "
                "les trois appartements sont loués et le local commercial est en activité, il n'y a donc aucune urgence et rien à faire à court terme. "
                "Hypothèse haute 90 000 € (1 200 €/m², réseaux refaits) si la visite révèle des réseaux vétustes — l'écart vaut 50 000 € de prix. "
                "À ajouter en différé : la rénovation énergétique (DPE D, facture annoncée 3 280 à 4 470 €/an pour l'immeuble)."
            )
        }
    },
    "annonce": {
        "plateforme": "seloger",
        "url": URL,
        "prix_affiche_euros": 288000.0,
        "prix_retenu_euros": None,
        "prix_statut": "affiche",
        "prix_commentaire": (
            "1 252 €/m² sur les 230 m² annoncés (1 462 €/m² sur la seule surface louable de 197 m²). "
            "INCOHÉRENCE : le texte de l'annonce annonce une rentabilité de 7,24 % « sur la base d'un prix de 319 000 € HAI », "
            "alors que le bien est affiché 288 000 €. À 288 000 €, le rendement brut est de 8,02 %. "
            "Le texte n'a pas été mis à jour après une baisse de 31 000 € — indice d'un vendeur déjà en mouvement."
        )
    },
    "marche": {
        "valeur": {
            "basse_euros": 320000.0,
            "haute_euros": 360000.0,
            "retenue_euros": 340000.0,
            "source": (
                "Deux méthodes convergentes. (1) Capitalisation : loyers en place 23 100 €/an rapportés à un taux de rendement de marché de 6,5 à 7 % "
                "pour un immeuble de rapport entièrement loué → 330 000 à 355 000 €. "
                "(2) Comparaison : les appartements se traitent à 2 459-2 607 €/m² à Vidauban (Immovrai DVF, Orpi 09/2026), les maisons à 3 500-3 617 €/m² ; "
                "les 150 m² de logements valorisés à 2 200 €/m² (décote d'ancien sans travaux) et le local commercial à 1 500 €/m² donnent environ 330 000 €. "
                "Valeur retenue 340 000 €, donc LE BIEN EST AFFICHÉ 15 % SOUS SA VALEUR DE MARCHÉ — décote qui paie les travaux de rafraîchissement."
            ),
            "confiance": "moyenne"
        },
        "loyers": [
            {"lot": "Local commercial 47 m² + 35 m² de réserves", "quantite": 1, "loyer_mensuel_euros": 780.0, "occupe": True,
             "note": "Bail en activité. 9,5 €/m² sur 82 m², soit le bas de fourchette pour un emplacement n°1 en centre-ville : marge de revalorisation au renouvellement."},
            {"lot": "T2 de 50 m² (1er étage)", "quantite": 1, "loyer_mensuel_euros": 370.0, "occupe": True,
             "note": "Bail en place. 7,4 €/m² : le marché de Vidauban est à 11-13 €/m², soit 35 à 40 % au-dessus. Revalorisation possible à la rotation."},
            {"lot": "T2 de 50 m² (2e étage)", "quantite": 1, "loyer_mensuel_euros": 395.0, "occupe": True,
             "note": "Bail en place. 7,9 €/m², même constat."},
            {"lot": "T2 de 50 m² (3e étage)", "quantite": 1, "loyer_mensuel_euros": 380.0, "occupe": True,
             "note": "Bail en place. 7,6 €/m², même constat."}
        ],
        "notes": (
            "Loyers en place 1 925 €/mois hors charges, soit 23 100 €/an et 8,02 % brut sur le prix affiché. "
            "POTENTIEL DE REVALORISATION DOCUMENTÉ : les trois T2 se louent 7,4 à 7,9 €/m² quand le marché de Vidauban est à 11-13 €/m² "
            "(comparables relevés : T2 49 m² à 683 € soit 14 €/m², T3 63 m² à 814 € soit 12,7 €/m², 60 m² à 580 €). "
            "Si les trois T2 passent à 600 € à la rotation, le revenu atteint 2 580 €/mois, soit 30 960 €/an (+34 %). "
            "Le local commercial, à 9,5 €/m², dispose aussi d'une marge au renouvellement du bail. "
            "RÉSERVE : la revalorisation ne s'obtient qu'à la rotation des locataires — elle n'est pas encaissable le jour de l'acquisition, "
            "et le prix d'offre doit donc se caler sur les baux signés, pas sur le potentiel."
        )
    },
    "hypotheses": {
        "vacance_base_pct": 8.0,
        "vacance_best_pct": 5.0,
        "vacance_worst_pct": 15.0,
        "vacance_justification": (
            "Immeuble entièrement loué, 4 baux dont un bail commercial. Base 8 % (au-dessus du défaut résidentiel) pour tenir compte du lot commercial, "
            "dont la relocation est plus longue qu'un logement. Worst 15 % : vacance simultanée d'un T2 et du local."
        ),
        "frais_acquisition_euros": 23040.0,
        "frais_divers_euros": 0.0,
        "charges": {
            "taxe_fonciere_annuelle_euros": 2500.0,
            "taxe_fonciere_commentaire": "Estimation pour un immeuble de 4 lots dont un local commercial à Vidauban, à confirmer sur l'avis réel. Alerte si > 15 % du brut.",
            "charges_copro_annuelles_euros": 0.0,
            "charges_copro_commentaire": "MONOPROPRIÉTÉ : aucune charge de copropriété, aucun syndic, aucune assemblée générale. C'est un avantage structurel du dossier.",
            "pno_annuelle_euros": 400.0,
            "pno_commentaire": "Assurance immeuble en monopropriété (logements + local commercial).",
            "entretien_annuel_euros": 1000.0,
            "entretien_commentaire": "Entretien courant d'un immeuble de 1900 et des parties communes (jardin, cages d'escalier).",
            "comptabilite_annuelle_euros": 600.0,
            "comptabilite_commentaire": "Comptabilité SCI, avec un bail commercial à suivre."
        }
    },
    "analyse": {
        "branche": "residentiel",
        "type_operation": "mixte",
        "strategie_retenue": {"nom": "Conservation en l'état puis revalorisation à la rotation", "code": "ld-nue", "lots": 4},
        "strategies_explorees": [
            {"strategie": "Conservation en l'état avec loyers actuels", "lots": 4, "faisabilite": "immédiate", "risque": "faible — mais rendement net 4,8 %"},
            {"strategie": "Conservation + rafraîchissement à la rotation et revalorisation des T2 à 600 €", "lots": 4, "faisabilite": "étalée sur 3 à 5 ans", "risque": "moyen (calendrier des rotations inconnu)"},
            {"strategie": "MDB : revente à la découpe des trois T2 après rénovation", "lots": 4, "faisabilite": "bloquée — tous les lots sont loués", "risque": "élevé (baux en cours, pas d'EDD)"}
        ],
        "attractivite": [
            {"dimension": "transports", "score": 6, "justification": "Vidauban dispose d'une gare SNCF (ligne Marseille-Nice), d'un accès autoroutier immédiat (A57) et d'un réseau de bus. Centre-ville tout à pied."},
            {"dimension": "commerces", "score": 8, "justification": "Emplacement n°1 en plein cœur du centre-ville, à proximité immédiate des commerces et des parkings. C'est l'argument principal du bien pour le lot commercial comme pour les logements."},
            {"dimension": "ecoles", "score": 7, "justification": "Vidauban (environ 12 000 habitants) dispose de groupes scolaires et d'un collège ; lycées à Draguignan et Le Luc."},
            {"dimension": "securite", "score": 6, "justification": "Commune résidentielle du centre Var, pas de QPV. Centre-ville animé en journée."},
            {"dimension": "demande_locative", "score": 7, "justification": "Marché locatif tendu sur les petites surfaces : les comparables relevés affichent 11 à 14 €/m² pour des T2 et T3, ce qui traduit une demande réelle et une offre limitée."},
            {"dimension": "dynamisme", "score": 6, "justification": "Vidauban bénéficie de sa position entre Draguignan, Le Luc et la plaine des Maures ; prix en hausse de l'ordre de 5 à 7 % sur un an selon les sources."}
        ],
        "risques": [
            {"facteur": "Revalorisation des loyers différée", "detail": "Les trois T2 sont 35 à 40 % sous le marché, mais les locataires sont en place. On ne peut pas augmenter un loyer en cours de bail au-delà de l'IRL : le potentiel ne se réalise qu'à la rotation, dont le calendrier est inconnu. Le prix d'offre doit donc se caler sur les baux signés.", "severite": 3},
            {"facteur": "Travaux non chiffrés", "detail": "L'agence annonce un « rafraîchissement » sans le chiffrer : 40 000 € si les réseaux sont sains, jusqu'à 90 000 € s'ils sont à refaire. L'écart vaut 50 000 € de prix d'achat.", "severite": 3},
            {"facteur": "Facture énergétique élevée", "detail": "DPE D avec une facture annoncée de 3 280 à 4 470 €/an pour l'immeuble, sur un bâti de 1900. La rénovation énergétique devra être provisionnée, sans contrainte réglementaire avant 2034.", "severite": 2},
            {"facteur": "Bail commercial non détaillé", "detail": "Le local est « en activité » mais ni la nature du bail, ni son échéance, ni sa clause de révision ne sont communiquées. Un bail ancien sous le marché est un potentiel ; un bail précaire est un risque.", "severite": 2},
            {"facteur": "Greniers et combles", "detail": "Trois greniers au dernier niveau : potentiel de valorisation annoncé mais aucune surface habitable ne peut y être créée sans autorisation. À traiter comme un bonus, jamais comme une valeur acquise.", "severite": 1}
        ]
    },
    "champs_manquants": []
}


def main():
    data = json.load(open(BASE))
    data['analyses'] = [r for r in data['analyses'] if r['slug'] != SLUG]
    RECORD['champs_manquants'] = schema.champs_manquants(RECORD)
    data['analyses'].append(RECORD)
    data['meta']['count'] = len(data['analyses'])
    json.dump(data, open(BASE, 'w'), ensure_ascii=False, indent=1)
    print(f"record ajoute : {SLUG} | total {data['meta']['count']} fiches")

    spec = importlib.util.spec_from_file_location("gen", os.path.join(ROOT, 'scripts', 'gen_fiches_2026-09-10.py'))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)

    gen.LECTURE[SLUG] = (
        "Le dossier inverse le schéma habituel : ici, ce n'est pas le prix qui bloque, c'est le calendrier. L'immeuble est entièrement loué, "
        "et ses loyers sont 35 à 40 % sous le marché — les trois T2 se louent 7,4 à 7,9 €/m² quand Vidauban vaut 11 à 13 €/m². "
        "Le potentiel est donc considérable mais il ne s'encaisse qu'à la rotation des locataires, dont personne ne connaît la date. "
        "En l'état, le rendement net ressort à 4,8 % sur le prix affiché et le cash flow est négatif de 357 €/mois sur vingt ans. "
        "Le prix qui produit un cash flow positif avec les baux signés est de 219 000 € pour un équilibre, 199 000 € pour dégager 100 €/mois — "
        "soit 24 à 31 % sous l'affichage. Mais le bien est déjà vendu 15 % sous sa valeur de marché, et le texte de l'annonce trahit une baisse "
        "de 31 000 € non répercutée. La vraie question n'est donc pas « combien vaut-il » mais « quel prix payer pour un potentiel qu'on ne peut pas exploiter tout de suite »."
    )

    gen.CONF[SLUG] = dict(
        titre_court="Immeuble 4 lots, centre-ville Vidauban",
        adresse="Centre-ville de Vidauban (83550) — local commercial + 3 T2, monopropriété",
        date_fr="15 septembre 2026",
        source="SeLoger - annonce 26UCYRMCT738 (NESTENN Draguignan, Stéphane Scarpitta)",
        url=URL,
        badge="Investissement locatif",
        strategie="Conservation en l'état, rafraîchissement et revalorisation à la rotation",
        fiscal_note="SCI à l'IS (15 %), amortissement sur 90 % du prix de revient sur 30 ans, provision d'impayés 1 % (pas de GLI)",
        lat="43.4277", lon="6.4320",
        quartier="centre-ville de Vidauban (83550), emplacement n°1",
        intro_attr=(
            "Le bien occupe un emplacement n°1 en plein cœur du centre-ville de Vidauban, à proximité immédiate des commerces et des parkings. "
            "La commune, située entre Draguignan, Le Luc et la plaine des Maures, dispose d'une gare SNCF sur la ligne Marseille-Nice et d'un accès "
            "autoroutier direct par l'A57. Le marché local est solide sur les locations : les T2 et T3 s'y traitent entre 11 et 14 €/m², "
            "ce qui traduit une demande réelle sur des surfaces limitées. Les appartements se vendent entre "
            "<strong>2 459 et 2 607 €/m²</strong> (Immovrai DVF, Orpi 09/2026), les maisons entre 3 500 et 3 617 €/m². "
            "Le bien est affiché à <strong>1 252 €/m²</strong> — mais cette moyenne porte sur 230 m² qui incluent les greniers, les réserves et le local : "
            "ramené aux 197 m² réellement louables, le prix ressort à 1 462 €/m²."
        ),
        profil="locataires de longue durée à budget modeste dans les T2, commerce de proximité au rez-de-chaussée — le profil que produit un emplacement de centre-ville",
        concl_attr=(
            "Adéquation bonne (7,3/10). L'emplacement de centre-ville et la monopropriété sont deux atouts structurels : aucun syndic, aucune charge "
            "de copropriété, aucune assemblée générale. La demande locative est réelle et les loyers en place sont nettement sous le marché, "
            "ce qui documente un potentiel de revalorisation. Le facteur limitant n'est ni l'emplacement ni le rendement brut de 8 % — "
            "c'est le calendrier : les loyers bas sont protégés par des baux en cours."
        ),
        intro_strat=(
            "Trois lectures ont été testées : la conservation en l'état avec les loyers actuels, la conservation avec rafraîchissement et "
            "revalorisation à la rotation, et l'achat-rénovation-revente. La troisième est écartée d'emblée, tous les lots étant loués."
        ),
        rationale=(
            "La conservation est la seule stratégie possible, mais elle se scinde en deux temps qu'il faut chiffrer séparément. "
            "<strong>Premier temps, les baux signés</strong> : 1 925 €/mois de loyers, 8,02 % brut, un mono-propriétaire sans charges de copropriété. "
            "Après taxe foncière, assurance, entretien, comptabilité, vacance de 8 % et provisions, l'EBE ressort à 1 329 €/mois et le rendement net "
            "à <strong>4,8 %</strong> — le cash flow est négatif de 357 €/mois sur vingt ans.<br><br>"
            "<strong>Deuxième temps, le potentiel</strong> : les trois T2 se louent 7,4 à 7,9 €/m² quand le marché local vaut 11 à 13 €/m², et le local "
            "commercial est à 9,5 €/m² pour un emplacement n°1. Si les trois appartements passent à 600 € à la rotation, le revenu grimpe à "
            "2 580 €/mois, soit +34 %. Avec 40 000 € de rafraîchissement financés, un prix de 240 000 € dégagerait alors "
            "+151 €/mois de cash flow et 7,0 % de rendement net.<br><br>"
            "Le problème est que ce deuxième temps n'est pas encaissable le jour de l'acquisition. Les loyers bas sont protégés par des baux en cours : "
            "on ne les relève qu'à la rotation, et un bail commercial de longue date ne se renégocie qu'à son échéance. "
            "D'où la règle appliquée ici : <strong>le prix d'offre se cale sur les baux signés, jamais sur le potentiel</strong>. "
            "Sur cette base, l'équilibre s'obtient à 219 000 € et un cash flow de +100 €/mois à 199 000 €.<br><br>"
            "Une réserve favorable, cependant : le bien est affiché 15 % sous sa valeur de marché (340 000 €), et le texte de l'annonce mentionne encore "
            "un prix de 319 000 € — le vendeur a déjà baissé de 31 000 € sans mettre son texte à jour. C'est le signe d'un vendeur en mouvement, "
            "et c'est la meilleure raison de travailler ce dossier."
        ),
        identite=[
            ("Adresse", "Centre-ville de Vidauban (83550) — adresse exacte non communiquée, emplacement n°1 proche des commerces et parkings"),
            ("Composition", "R+3 de 230 m² : <strong>local commercial de 47 m²</strong> + 3 réserves de 35 m² au rez-de-chaussée, <strong>trois T2 de 50 m²</strong> d'agencement identique (entrée, cuisine, séjour, 1 chambre, salle d'eau, WC séparé) aux 1er, 2e et 3e étages, <strong>3 greniers</strong> au dernier niveau"),
            ("Annexes", "4 caves, 1 débarras, jardin, parties communes desservantes"),
            ("Statut", "<strong>MONOPROPRIÉTÉ</strong> : aucune charge de copropriété, aucun syndic, aucune assemblée générale. Compteurs électriques indépendants"),
            ("Occupation", "<strong>Tous les lots sont loués</strong> : local 780 €, T2 370 €, 395 € et 380 € — soit 1 925 €/mois hors charges"),
            ("DPE / GES", "DPE D / GES B — bâti de 1900 — facture énergétique annoncée 3 280 à 4 470 €/an pour l'immeuble"),
            ("Prix affiché", "288 000 € soit 1 252 €/m² sur 230 m², ou 1 462 €/m² sur les 197 m² louables"),
            ("Valeur de marché retenue", "320 000 à 360 000 €, retenue <strong>340 000 €</strong> — capitalisation des loyers à 6,5-7 % et comparaison avec les 2 459-2 607 €/m² des appartements de Vidauban. <strong>Le bien est affiché 15 % sous sa valeur</strong>"),
            ("Loyers en place", "<strong>1 925 €/mois</strong> hors charges = 23 100 €/an = 8,02 % brut. Les trois T2 sont à 7,4-7,9 €/m² contre 11-13 €/m² de marché"),
            ("Potentiel de revalorisation", "Si les trois T2 passent à 600 € à la rotation : <strong>2 580 €/mois</strong>, soit 30 960 €/an (+34 %) et 10,75 % brut"),
            ("Travaux", "<strong>40 000 €</strong> de rafraîchissement des trois T2 (environ 470 €/m²), à engager à la rotation et non à l'acquisition. Hypothèse haute 90 000 € si les réseaux sont à refaire"),
            ("Charges annuelles", "<strong>Zéro charge de coproprieté</strong> + taxe foncière ~2 500 € + assurance immeuble 400 € + entretien 1 000 € + comptabilité 600 € = <strong>4 500 €/an</strong>"),
            ("Fiscalité", "SCI à l'IS : IS 15 % sur le résultat, amortissement de 90 % du prix de revient sur 30 ans. Pas de GLI : provision d'auto-assurance de 1 % du loyer annuel"),
            ("Prix de revient", "<strong>311 040 €</strong> = prix 288 000 € + frais d'acquisition ~23 040 € (8 %), travaux différés"),
        ],
        stance=(
            "<strong>À négocier — 240 000 € pour un cash flow positif après revalorisation, 219 000 € pour l'équilibre avec les baux signés.</strong> "
            "Le dossier a tout pour plaire : emplacement n°1 en centre-ville, monopropriété sans aucune charge de copropriété, immeuble entièrement loué, "
            "8,02 % de rendement brut, et des loyers 35 à 40 % sous un marché locatif réellement tendu. C'est un actif de capitalisation solide. "
            "Mais deux réserves commandent la négociation. D'abord le calendrier : les loyers bas sont protégés par des baux en cours, "
            "et rien ne dit quand les T2 se libéreront — le potentiel de +600 €/mois n'est pas encaissable aujourd'hui. Ensuite les travaux : "
            "l'agence annonce un rafraîchissement sans le chiffrer, et l'écart entre 40 000 € et 90 000 € vaut 50 000 € de prix. "
            "À 288 000 €, le cash flow est négatif de 357 €/mois et le rendement net de 4,8 % : ce n'est pas un dossier de parc. "
            "À 240 000 € avec les travaux financés, il dégage +151 €/mois après revalorisation et 7,0 % net. "
            "L'argument décisif face au vendeur : son propre texte annonce encore 319 000 €, il a donc déjà consenti 31 000 €."
        ),
        prix_plafond=(
            "219 000 € pour un cash flow neutre sur 20 ans avec les baux signés, 199 000 € pour dégager +100 €/mois. "
            "240 000 € si l'on accepte de payer le potentiel de revalorisation, sous condition de financer les 40 000 € de travaux : "
            "le cash flow ressort alors à +151 €/mois et le rendement à 7,0 %. Au-delà de 260 000 €, le dossier ne couvre plus rien, "
            "même avec les loyers revalorisés."
        ),
        leviers=[
            "L'incohérence de prix est le premier levier : le texte de l'annonce annonce encore une rentabilité de 7,24 % « sur la base d'un prix de 319 000 € HAI » alors que le bien est affiché 288 000 €. Le vendeur a donc déjà baissé de 31 000 € — c'est écrit noir sur blanc, et ça se rappelle sans agressivité",
            "Les loyers des T2 sont 35 à 40 % sous le marché : c'est l'argument massue pour justifier une décote. Le bien ne produit pas ce qu'il pourrait produire, et cette sous-performance durera aussi longtemps que les baux en cours. Capitaliser ce manque à gagner plutôt que le promettre",
            "L'écart entre 40 000 € et 90 000 € de travaux vaut 50 000 € de prix : faire chiffrer le rafraîchissement par un artisan avant l'offre, et faire constater l'état des réseaux (électricité, plomberie) sur un bâti de 1900",
            "Le bail commercial doit être lu pièce en pièce : nature, échéance, clause de révision, répartition des charges. Un bail ancien sous le marché est un potentiel de revalorisation ; un bail précaire est un risque de vacance longue sur 780 €/mois",
            "La monopropriété est un atout à faire valoir dans la durée : aucun appel de fonds de copropriété, aucun syndic, aucune assemblée. Sur un immeuble de centre-ville de 1900, c'est la meilleure protection contre les dépenses imposées",
            "Les trois greniers sont un bonus, pas une valeur : ne jamais les compter dans le prix. En revanche, leur aménagement éventuel (bureau, stockage) peut améliorer l'attractivité sans toucher aux baux",
        ],
        meta=[
            "<strong>Régime fiscal retenu :</strong> SCI à l'IS (15 %) — amortissement sur 90 % du prix de revient sur 30 ans — provision d'impayés 1 % (pas de GLI)",
            "<strong>Frais d'acquisition estimés :</strong> ~23 040 € (8 % du prix affiché)",
            "<strong>Enveloppe travaux :</strong> 40 000 € de rafraîchissement des trois T2 (à la rotation), hypothèse haute 90 000 € si les réseaux sont à refaire. Rénovation énergétique à provisionner séparément",
            "<strong>Contrôle à faire avant toute offre :</strong> devis de rafraîchissement et état des réseaux (électricité, plomberie, toiture), bail commercial complet et échéance, avis de taxe foncière, diagnostics complets, surfaces exactes par lot, échéances des trois baux d'habitation, titre de propriété et absence de servitude",
            "<strong>Point de méthode :</strong> le prix d'offre se cale sur les baux signés (1 925 €/mois), jamais sur le potentiel de revalorisation. Le potentiel est un levier de négociation, pas une base de prix",
        ],
    )

    gen.main()


if __name__ == '__main__':
    main()
