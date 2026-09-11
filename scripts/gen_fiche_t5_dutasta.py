#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cree la fiche du T5 86 m2 quartier Dutasta-Mayol (Toulon) et la genere.

Usage : PY scripts/gen_fiche_t5_dutasta.py
"""
import importlib.util, json, os, sys

ROOT = '/home/alexis-barlatier/Documents/Semaphore-sonar'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from analyse_app import schema

BASE = os.path.join(ROOT, 'analyses', 'analyses.json')
SLUG = "2026-09-11-t5-86m2-dutasta-mayol-toulon"
URL = "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/toulon-83000/26AUE1NNJC3Q"

RECORD = {
    "slug": SLUG,
    "date_analyse": "2026-09-11",
    "date_maj": None,
    "titre": "Toulon — T5 de 86 m² au 5e étage avec ascenseur, quartier Dutasta-Mayol, 4 chambres",
    "bien": {
        "type_bien": "appartement",
        "sous_type": None,
        "type_detail": (
            "T5 de 86,05 m² au 5e étage sur 8, ascenseur, 4 chambres, séjour-salon au sud donnant sur balcon de 7 m², "
            "cuisine indépendante à aménager avec cellier/loggia, salle de bain avec baignoire et fenêtre, WC indépendant, "
            "cave de 4 m², exposition sud-ouest, double vitrage, chauffage et eau chaude individuels au gaz. "
            "Immeuble de 1940, bien entretenu, copropriété de 53 lots, sans procédure syndicale en cours. "
            "Bien LIBRE (non loué) : aucun bail en place, aucune contrainte d'occupation. Honoraires à la charge du vendeur."
        ),
        "neuf": False,
        "adresse": {
            "texte": "Quartier Dutasta-Mayol, Toulon (83000) — adresse exacte non communiquée dans l'annonce, proche de Mayol et du port",
            "ville": "Toulon",
            "code_postal": "83000"
        },
        "surfaces": {
            "texte": "86,05 m² annoncés (loi Carrez à confirmer par le diagnostic du vendeur)",
            "carrez_m2": 86.05
        },
        "lots": {
            "count": 1,
            "surface_par_lot_m2": 86.05,
            "nature": "1 appartement, convertible en colocation de 4 chambres (3 chambres + séjour transformable)",
            "lots_distincts": 1
        },
        "copro": {
            "charges_annuelles_euros": 1173.0,
            "charges_source": "Charges de copropriété réelles annoncées par l'annonce : 1 173 €/an (14 €/m²/an), copropriété de 53 lots, aucune procédure syndicale en cours."
        },
        "travaux": {
            "montant_euros": 35000.0,
            "nature": (
                "« Prévoir travaux de modernité » : cuisine à aménager, rafraîchissement général, sols, peintures. "
                "Enveloppe retenue 35 000 € en colocation, dont l'équipement mobilier (15-25 k€ si l'on se limite à la modernisation "
                "sans passage en meublé). Une deuxième salle d'eau serait le poste qui change la valeur du bien : à chiffrer en visite "
                "(contrainte d'évacuation à vérifier)."
            )
        }
    },
    "annonce": {
        "plateforme": "seloger",
        "url": URL,
        "prix_affiche_euros": 155000.0,
        "prix_retenu_euros": None,
        "prix_statut": "affiche",
        "prix_commentaire": "1 801 €/m² sur 86,05 m². Honoraires d'agence à la charge du vendeur. Décote affichée de 29 % sur le prix moyen du quartier Dutasta-Mayol (2 522 €/m² retenus)."
    },
    "marche": {
        "valeur": {
            "basse_euros": 207000.0,
            "haute_euros": 225000.0,
            "retenue_euros": 217000.0,
            "source": (
                "Quartier Dutasta-Mayol : 2 433 €/m² (SeLoger, rue des Remparts, quartier Dutasta-Mayol — bas 1 878, haut 3 043), "
                "2 612 €/m² (RealAdvisor, août 2026), 2 500 €/m² (efficity, rue Dutasta). Retenue 2 522 €/m² sur 86,05 m² = 217 000 €, "
                "avec fourchette 207 000 à 225 000 €. L'avenue de la République cote 3 048 €/m² (MeilleursAgents), mais c'est une avenue "
                "plus cotée que la moyenne du quartier. Aucune vente DVF exploitable sur ce bien : le chiffrage repose sur les estimations d'annonces."
            ),
            "confiance": "moyenne"
        },
        "loyers": [
            {
                "lot": "Chambre 1 (colocation, meublée)",
                "quantite": 1,
                "loyer_mensuel_euros": 420.0,
                "occupe": False,
                "note": "Hypothèse de marché toulonnais, aucun bail en place. Les annonces locales de colocation à Toulon s'étalent de 320 € CC (étudiant, entrée de gamme) à 530 € CC."
            },
            {
                "lot": "Chambre 2 (colocation, meublée)",
                "quantite": 1,
                "loyer_mensuel_euros": 420.0,
                "occupe": False,
                "note": "Hypothèse de marché, aucun bail en place."
            },
            {
                "lot": "Chambre 3 (colocation, meublée)",
                "quantite": 1,
                "loyer_mensuel_euros": 420.0,
                "occupe": False,
                "note": "Hypothèse de marché, aucun bail en place."
            },
            {
                "lot": "Chambre 4 (séjour transformé, colocation meublée)",
                "quantite": 1,
                "loyer_mensuel_euros": 420.0,
                "occupe": False,
                "note": "Le séjour-salon du sud peut devenir une quatrième chambre (l'annonce propose déjà « salon ou une chambre »). Hypothèse de marché."
            }
        ],
        "notes": (
            "Aucun loyer en place : le bien est libre, tout le chiffrage repose sur une hypothèse de colocation à 420 €/chambre, "
            "cohérente avec le marché toulonnais (annonces de 320 à 530 € charges comprises) sans être vérifiée par un bail. "
            "Test de sensibilité : à 350 €/chambre le rendement net tombe à 3,7 % et le CF à −306 €/mois ; à 460 €/chambre il monte à 6,2 % "
            "et le CF devient positif (+112 €/mois sur 18 ans). En location nue, le même bien plafonne à 3,8-4,9 % net selon un loyer de 950 à 1 150 €/mois : "
            "le nu ne fait pas vivre ce bien. En achat-rénovation-revente, avec 30 k€ de travaux, la marge nette va de 2,3 % (revente à 2 600 €/m²) "
            "à 10,3 % (2 900 €/m²) : trop dépendant du prix de sortie pour être la voie principale."
        )
    },
    "hypotheses": {
        "vacance_base_pct": 10.0,
        "vacance_best_pct": 8.0,
        "vacance_worst_pct": 15.0,
        "vacance_justification": (
            "Colocation = chambres qui tournent individuellement, donc vacance structurellement plus élevée qu'un logement loué en bloc. "
            "Base 10 %, best 8 % (quatre chambres, ville étudiante), worst 15 % (une chambre vacante trois mois sur l'année)."
        ),
        "frais_acquisition_euros": 12400.0,
        "frais_divers_euros": 0.0,
        "charges": {
            "taxe_fonciere_annuelle_euros": 1300.0,
            "taxe_fonciere_commentaire": "Estimation 86 m² à Toulon (~15 €/m²/an), à vérifier sur l'avis réel. Alerte si > 15 % du brut.",
            "charges_copro_annuelles_euros": 1173.0,
            "charges_copro_commentaire": "Montant réel annoncé : 1 173 €/an, soit 14 €/m²/an — trois fois moins que le T4 de Champ de Mars. Point positif du dossier.",
            "pno_annuelle_euros": 250.0,
            "pno_commentaire": "PNO appartement avec cave et balcon.",
            "entretien_annuel_euros": 2900.0,
            "entretien_commentaire": (
                "Entretien courant 800 € + ménage et fournitures 700 € + provision de renouvellement du mobilier 700 € "
                "+ provision d'impayés 3,5 % du loyer (~700 €, colocation : provision renforcée, doctrine du groupe, pas de GLI)."
            ),
            "comptabilite_annuelle_euros": 600.0,
            "comptabilite_commentaire": "Comptabilité SCI, majorée pour une exploitation en colocation meublée (4 baux, quittances, mobilier)."
        }
    },
    "analyse": {
        "branche": "residentiel",
        "type_operation": "locatif",
        "strategie_retenue": {"nom": "Colocation meublée 4 chambres", "code": "colocation", "lots": 4},
        "strategies_explorees": [
            {"strategie": "Colocation meublée 4 chambres", "lots": 4, "faisabilite": "après travaux de modernité et équipement (4-6 mois)", "risque": "moyen (rotation, impayés, gestion)"},
            {"strategie": "Location nue longue durée", "lots": 1, "faisabilite": "immédiate", "risque": "faible — mais rendement net plafonné à 3,8-4,9 %"},
            {"strategie": "MDB : achat, modernisation, revente", "lots": 1, "faisabilite": "9-12 mois", "risque": "élevé (marge de 2 à 10 % selon le prix de revente)"}
        ],
        "attractivite": [
            {"dimension": "transports", "score": 8, "justification": "Quartier Dutasta-Mayol : proche du port, de Mayol et des axes centraux, desserte bus dense, gare de Toulon à distance de marche."},
            {"dimension": "commerces", "score": 8, "justification": "« Proche de toutes les commodités à pied » selon l'annonce : centre-ville, commerces et services à proximité immédiate."},
            {"dimension": "ecoles", "score": 7, "justification": "Secteur scolaire toulonnais dense ; bassin étudiant (université, écoles) qui soutient la demande de colocation."},
            {"dimension": "securite", "score": 6, "justification": "Quartier central résidentiel, immeuble annoncé bien entretenu, aucune procédure syndicale. Pas de QPV."},
            {"dimension": "demande_locative", "score": 8, "justification": "Toulon : demande structurellement forte sur les petites surfaces et la colocation étudiante ; quartier recherché pour sa centralité."},
            {"dimension": "dynamisme", "score": 7, "justification": "Prix Toulon stables à orientés hausse sur le centre, quartier port-Mayol en amélioration continue."}
        ],
        "risques": [
            {"facteur": "Une seule salle de bain et un WC pour quatre chambres", "detail": "C'est le vrai plafond commercial du bien : à 420 € la chambre, on est proche du haut de ce que ce format accepte. Créer une seconde salle d'eau changerait l'équation, mais la contrainte d'évacuation doit être vérifiée en visite.", "severite": 3},
            {"facteur": "Aucun loyer en place", "detail": "Le bien est libre : tout le chiffrage repose sur une hypothèse de colocation à 420 €/chambre, non vérifiée par un bail. À 350 €, le dossier tombe à 3,7 % net et −306 €/mois de trésorerie.", "severite": 3},
            {"facteur": "Colocation : rotation et impayés", "detail": "Quatre baux, quatre rotations possibles, un profil locataire plus mobile et des impayés plus fréquents. Provision portée à 3,5 % du loyer, vacance de base à 10 %.", "severite": 2},
            {"facteur": "Travaux de modernité non chiffrés", "detail": "« Prévoir travaux de modernité » : cuisine à aménager, rafraîchissement. Enveloppe retenue 35 k€ en colocation (dont mobilier) ; 15-25 k€ si l'on se limite à la modernisation sans meublé. Devis avant offre.", "severite": 2},
            {"facteur": "Immeuble de 1940", "detail": "Parties communes, toiture et colonnes à examiner. Charges de copropriété faibles (1 173 €/an) mais un immeuble de cet âge peut réserver des appels de fonds. Exiger les trois derniers PV d'AG et le budget prévisionnel.", "severite": 2}
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
    print(f"record ajoute : {SLUG} | total {data['meta']['count']} fiches | champs manquants : {RECORD['champs_manquants'] or 'aucun'}")

    spec = importlib.util.spec_from_file_location("gen", os.path.join(ROOT, 'scripts', 'gen_fiches_2026-09-10.py'))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)

    gen.LECTURE[SLUG] = (
        "Le dossier a un vrai atout que les autres annonces toulonnaises n'avaient pas : une décote affichée de 29 % sur son propre quartier "
        "(1 801 €/m² contre 2 522 €/m² pour Dutasta-Mayol). Un T5 de 86 m² avec ascenseur au 5e étage, balcon, cave, DPE D et des charges de "
        "copropriété à 14 €/m²/an, ce n'est pas un bien courant à ce prix. Mais la décote paie les travaux de modernité, et surtout le bien ne "
        "vit que par un seul usage : la colocation. À 4 chambres et 420 € la chambre, le rendement net ressort à 5,2 % avec un cash flow quasi "
        "neutre sur 20 ans ; en location nue, il s'effondre à 3,8-4,9 % et la trésorerie devient franchement négative. Le plafond du bien n'est "
        "pas son emplacement, c'est sa salle de bain unique pour quatre chambres. Prix qui tiendrait le seuil de parc de 6,5 % : 116 000 € à "
        "420 €/chambre, 144 000 € à 460 €. L'affichage est à 155 000 €, mais il est déjà au niveau du cash flow neutre : ce qui manque ici, "
        "c'est le rendement, pas la trésorerie."
    )

    gen.CONF[SLUG] = dict(
        titre_court="T5 86 m2, Dutasta-Mayol, Toulon",
        adresse="Quartier Dutasta-Mayol, Toulon (83000) — T5 de 86 m² au 5e étage sur 8 avec ascenseur, 4 chambres, balcon et cave",
        date_fr="11 septembre 2026",
        source="SeLoger - annonce 26AUE1NNJC3Q (La maison de l'immobilier IBOX Transac, 21 rue Peiresc, Toulon)",
        url=URL,
        badge="Investissement locatif",
        strategie="Colocation meublée 4 chambres",
        fiscal_note="SCI à l'IS (15 %), amortissement sur 90 % du prix de revient sur 30 ans, provision d'impayés 3,5 % (colocation, pas de GLI)",
        lat="43.1208", lon="5.9300",
        quartier="quartier Dutasta-Mayol, Toulon (83000), proche de Mayol et du port",
        intro_attr=(
            "Le quartier Dutasta-Mayol occupe le centre toulonnais, entre le port et le stade Mayol : c'est un emplacement de centralité, "
            "avec commerces, administrations et transports accessibles à pied. Les estimations y ressortent à <strong>2 433 €/m²</strong> "
            "(SeLoger, rue des Remparts — bas 1 878, haut 3 043), <strong>2 612 €/m²</strong> (RealAdvisor, août 2026) et 2 500 €/m² "
            "(efficity, rue Dutasta), l'avenue de la République montant à 3 048 €/m². Le bien est affiché à <strong>1 801 €/m²</strong>, "
            "soit 29 % sous la moyenne du quartier : c'est la première annonce récente qui présente une décote affichée sur son propre secteur. "
            "Cette décote paie les travaux de modernité annoncés et le 5e étage — pas un défaut de localisation."
        ),
        profil="jeunes actifs, étudiants et jeunes professionnels — la colocation est le segment le plus tendu du marché toulonnais",
        concl_attr=(
            "Adéquation bonne (7,4/10). L'emplacement central, la proximité du centre-ville et du port, l'ascenseur et le DPE D soutiennent "
            "la demande locative sur les deux usages testés. Le facteur limitant n'est ni le quartier ni le prix d'entrée, mais la configuration "
            "interne : une salle de bain unique pour quatre chambres plafonne mécaniquement le loyer par chambre."
        ),
        intro_strat=(
            "Trois usages ont été chiffrés : la colocation meublée en quatre chambres (retenue), la location nue et l'achat-rénovation-revente. "
            "Le bien étant libre, aucun loyer en place ne vient contraindre le choix."
        ),
        rationale=(
            "La colocation est la seule lecture qui fait vivre ce bien. À quatre chambres de 420 €, le loyer brut atteint 1 680 €/mois pour "
            "86 m², soit 19,5 €/m² — le niveau qu'un T5 nu de cette surface ne peut pas atteindre (950 à 1 150 €/mois, soit 3,8 à 4,9 % net). "
            "En colocation, le rendement net ressort à <strong>5,2 %</strong> sur le prix de revient avec un cash flow de −41 €/mois sur 18 ans "
            "et +21 €/mois sur 20 ans. À 460 € la chambre, il monte à <strong>6,2 %</strong> et le cash flow devient positif dès 18 ans (+112 €/mois).<br><br>"
            "La location nue est écartée : elle ne passe pas le seuil de parc, et son cash flow est négatif de 250 à 400 €/mois. Le MDB a été "
            "chiffré puis écarté comme voie principale : avec 30 k€ de travaux, la marge nette va de +4 700 € (revente à 2 600 €/m²) à "
            "+20 800 € (2 900 €/m²), soit 2,3 % à 10,3 % — entièrement dépendante du prix de sortie, et la TVA sur marge mange la majeure partie "
            "du différentiel dès que la revente reste dans la fourchette basse du quartier.<br><br>"
            "Le vrai plafond du dossier est ailleurs : <strong>une seule salle de bain et un WC pour quatre chambres</strong>. C'est ce qui borne "
            "le loyer par chambre, et donc le rendement. Si la visite confirme qu'une deuxième salle d'eau est faisable à coût raisonnable, "
            "l'équation s'améliore sensiblement ; si elle ne l'est pas, le bien restera sur un palier de 5 à 6 % net."
        ),
        identite=[
            ("Adresse", "Quartier Dutasta-Mayol, Toulon (83000) — adresse exacte non communiquée dans l'annonce, proche de Mayol et du port"),
            ("Composition", "T5 de <strong>86,05 m²</strong> au <strong>5e étage sur 8 avec ascenseur</strong> : 4 chambres, séjour-salon au sud (ou salon et une chambre) donnant sur un balcon de 7 m², cuisine indépendante à aménager avec cellier/loggia, salle de bain avec baignoire et fenêtre, WC indépendant, cave de 4 m²"),
            ("Immeuble", "Construit en <strong>1940</strong>, annoncé bien entretenu — copropriété de <strong>53 lots</strong>, <strong>aucune procédure syndicale en cours</strong>. Double vitrage, exposition sud-ouest, chauffage et eau chaude individuels au gaz"),
            ("DPE / GES", "<strong>DPE D</strong> / GES D — pas de contrainte réglementaire de location avant 2034 — facture énergétique annoncée 1 715 à 2 321 €/an"),
            ("Occupation", "<strong>Bien libre</strong> : aucun bail en place, aucune contrainte d'occupation. Honoraires d'agence à la charge du vendeur"),
            ("Prix affiché", "155 000 € soit <strong>1 801 €/m²</strong>"),
            ("Valeur de marché retenue", "207 000 à 225 000 €, retenue <strong>217 000 €</strong> (2 522 €/m²) — quartier Dutasta-Mayol : 2 433 €/m² (SeLoger), 2 612 €/m² (RealAdvisor), 2 500 €/m² (efficity). <strong>La décote affichée est de 29 %</strong>"),
            ("Loyers retenus", "<strong>Aucun loyer en place.</strong> Hypothèse de colocation : 4 chambres à <strong>420 €/mois</strong> = 1 680 €/mois (19,5 €/m²), marché local de 320 à 530 € CC par chambre. Sensibilité : 350 €/chambre → 3,7 % net et −306 €/mois ; 460 €/chambre → 6,2 % net et +112 €/mois"),
            ("Travaux", "« Prévoir travaux de modernité » : cuisine à aménager, rafraîchissement. Enveloppe <strong>35 000 €</strong> en colocation (dont équipement mobilier) ; 15-25 k€ si modernisation seule sans meublé. Deuxième salle d'eau à chiffrer en visite"),
            ("Charges annuelles", "Copropriété <strong>1 173 €/an (montant réel)</strong> + taxe foncière ~1 300 € + PNO 250 € + entretien et ménage 2 200 € + provision d'impayés 700 € + comptabilité 600 €"),
            ("Fiscalité", "SCI à l'IS : IS 15 % sur le résultat, amortissement de 90 % du prix de revient sur 30 ans. Pas de GLI : provision d'auto-assurance renforcée à 3,5 % du loyer (colocation)"),
            ("Prix de revient", "<strong>202 400 €</strong> = prix 155 000 € + frais d'acquisition ~12 400 € (8 %) + travaux 35 000 €"),
        ],
        stance=(
            "<strong>À négocier — 138 000 à 145 000 € maximum.</strong> Le bien a de vraies qualités : un 5e étage avec ascenseur à "
            "1 800 €/m² dans un quartier qui cote 2 500, un DPE D qui ne sera pas interdit à la location en 2034, un immeuble sans procédure "
            "et des charges de copropriété trois fois inférieures à la moyenne toulonnaise. Mais il ne fonctionne que sur un usage — la "
            "colocation — et son rendement net y plafonne à 5,2 % à 420 € la chambre, avec un cash flow à peine neutre sur vingt ans. "
            "La salle de bain unique pour quatre chambres borne le potentiel : c'est elle qui empêche d'aller chercher 460-480 € par chambre. "
            "À 138 000-145 000 €, le rendement net passe à 6 % et la trésorerie devient franchement positive sur 18 ans. "
            "À 155 000 €, on paie le cash flow neutre sans rendement : ce n'est pas un dossier de parc, c'est un dossier de portage."
        ),
        prix_plafond=(
            "138 000 à 145 000 €, soit 7 à 11 % sous l'affichage. À ce prix, le rendement net en colocation ressort autour de 6 % et le cash flow "
            "devient positif sur 18 ans. Hors colocation, en location nue, le prix qui tiendrait le seuil de parc serait de 116 000 € : "
            "c'est la mesure de l'écart entre les deux usages."
        ),
        leviers=[
            "La salle de bain unique est le premier levier de négociation et d'instruction : c'est elle qui plafonne le loyer par chambre. Faire chiffrer en visite la faisabilité d'une deuxième salle d'eau — si elle passe, le bien change de catégorie ; si elle ne passe pas, c'est un argument direct sur le prix",
            "Les « travaux de modernité » ne sont pas chiffrés : exiger un devis détaillé (cuisine, électricité, plomberie, sols) avant toute offre. Sur un immeuble de 1940, l'électricité et la plomberie sont les postes qui dérapent, et ils ne se voient pas sur les photos",
            "La décote affichée de 29 % est réelle mais elle paie les travaux : ne pas laisser le vendeur la présenter comme une aubaine, c'est le prix d'un bien à moderniser, pas d'un bien prêt à louer",
            "Le bien est libre : c'est un avantage pour la colocation (aucun bail à attendre), mais aussi un manque à gagner pour le vendeur. Un bien libre depuis plusieurs mois est un vendeur qui commence à compter les charges — c'est le moment de discuter",
            "Les charges de copropriété à 14 €/m²/an et l'absence de procédure sont deux points à faire figurer noir sur blanc dans l'offre : ils verrouillent le principal poste de risque fixe du dossier",
            "La colocation en SCI à l'IS mérite un cadrage : amortissement du mobilier sur 5 à 10 ans selon les équipements, TVA sur les loyers meublés à anticiper si elle est un jour optionnelle. À valider avec le comptable avant l'acquisition",
        ],
        meta=[
            "<strong>Régime fiscal retenu :</strong> SCI à l'IS (15 %) — amortissement sur 90 % du prix de revient sur 30 ans — provision d'impayés renforcée à 3,5 % du loyer (colocation, pas de GLI)",
            "<strong>Frais d'acquisition estimés :</strong> ~12 400 € (8 % du prix affiché)",
            "<strong>Enveloppe travaux :</strong> 35 000 € en colocation (modernisation, cuisine, équipement mobilier) — 15-25 k€ si modernisation seule. Deuxième salle d'eau à chiffrer",
            "<strong>Contrôle à faire avant toute offre :</strong> devis de travaux détaillé et faisabilité d'une seconde salle d'eau, budget prévisionnel de copropriété et PV d'AG des trois derniers exercices, avis de taxe foncière, diagnostics complets (électricité, gaz, amiante, plomb), Carrez, plan du logement pour valider la dimension des quatre chambres",
            "<strong>Point de méthode :</strong> le rendement du dossier dépend entièrement d'un loyer de colocation qui n'existe pas encore. À 350 € la chambre, le dossier tombe à 3,7 % net et la trésorerie passe à −306 €/mois. La visite et deux ou trois comparables signés sont indispensables avant l'offre",
        ],
    )

    gen.main()


if __name__ == '__main__':
    main()
