# -*- coding: utf-8 -*-
"""Fixtures de calibration — entrées reconstruites depuis les pages publiées.

But : vérifier que le moteur recalcule des notes cohérentes avec les notes
publiées de l'ère LLM (écart cible ≤ 0,2 sur entrées complètes ; sinon écart
documenté). Ces fiches servent aussi de tests de non-régression.

Source des entrées : pages analyses/YYYY-MM-DD-.../index.html (cartes de
synthèse, fiche d'identité, matrice de risques, scores d'attractivité).
Les valeurs publiées (note, rendements, revient) ne sont JAMAIS stockées ici —
elles ne servent qu'à mesurer l'écart en test.
"""

JEAN_ROSTAND = {
    "slug": "2026-09-03-11-parkings-jean-rostand-la-seyne",
    "date_analyse": "2026-09-03",
    "titre": "Bloc de 11 places de parking standard (sous-sol), résidence "
             "Jean Rostand, La Seyne-sur-Mer",
    "bien": {
        "type_bien": "parking",
        "sous_type": "sous-sol",
        "type_detail": "Bloc de 11 places de parking standard en sous-sol, "
                       "résidence neuve sécurisée — VEFA (livraison T2 2027)",
        "neuf": True,
        "adresse": {
            "texte": "Croisement bd Jean Rostand / av. Jean Vilar, quartier "
                     "Saint-Jean, La Seyne-sur-Mer (83500)",
            "ville": "La Seyne-sur-Mer", "code_postal": "83500",
            "quartier": "Saint-Jean",
        },
        "surfaces": {"texte": None},
        "lots": {"count": 11, "nature": "places standard sous-sol",
                 "surface_par_lot_m2": 12.0, "lots_distincts": True},
        "copro": {"charges_annuelles_euros": 1650.0,
                  "charges_source": "estimées 150 €/an/place — budget "
                                    "prévisionnel à obtenir par écrit"},
        "travaux": {"montant_euros": 0, "nature": None},
        "specificites": ["VEFA livraison T2 2027", "lots distincts cessibles"],
    },
    "annonce": {
        "plateforme": "seloger",
        "url": "https://www.seloger.com/annonce/achat/provence-alpes-cote-"
               "d-azur/var-83/la-seyne-sur-mer-83500/26ED31QDH4P8",
        "prix_affiche_euros": 88000.0,
        "prix_retenu_euros": 77000.0,
        "prix_statut": "offre",
        "vendeur": "Constructa Promotion",
        "prix_unitaire": {"valeur": 7000.0, "unite": "place"},
    },
    "marche": {
        "valeur": {"basse_euros": 110000.0, "haute_euros": 143000.0,
                   "retenue_euros": 125000.0,
                   "source": "revente unitaire lots distincts (10-13 k€/place)",
                   "confiance": "moyenne"},
        "loyers": [{"lot": "place standard sous-sol", "quantite": 11,
                    "loyer_mensuel_euros": 80.0, "occupe": False}],
        "notes": "Ancres locales 78-95 €/mois constatés (places sous-sol)",
    },
    "hypotheses": {
        "vacance_base_pct": 0.0,
        "vacance_best_pct": 0.0,
        "vacance_worst_pct": 25.0,
        "vacance_justification": "Vacance binaire neutralisée par le parc "
                                 "de 11 lots (point mort ~2 places louées)",
        "frais_acquisition_euros": 2600.0,
        "frais_acquisition_commentaire": "Acte unique 11 lots (barème réel)",
        "charges": {
            "taxe_fonciere_annuelle_euros": 0.0,
            "taxe_fonciere_commentaire": "Exonérée 2 ans (neuf), puis ~30 "
                                         "€/an/place",
            "charges_copro_annuelles_euros": 1650.0,
            "pno_annuelle_euros": 0.0,
            "entretien_annuel_euros": 0.0,
            "comptabilite_annuelle_euros": 0.0,
        },
        "duree_amortissement_ans": 30,
    },
    "analyse": {
        "branche": "parking",
        "type_operation": "locatif",
        "strategie_retenue": {
            "nom": "Location longue durée — bloc de 11 lots sous-sol",
            "code": "parking-ld", "lots": 11},
        "strategies_explorees": [
            {"nom": "Revente à l'unité (lots distincts)", "code": "mdb"}],
        "attractivite": [
            {"dimension": "tension_stationnement", "score": 6,
             "justification": "Tension réelle, inférieure au centre ancien"},
            {"dimension": "densite_residentielle", "score": 6,
             "justification": "Quartier en densification"},
            {"dimension": "accessibilite", "score": 7,
             "justification": "Croisement bd Jean Rostand / av. Jean Vilar"},
            {"dimension": "securite_acces", "score": 8,
             "justification": "Résidence neuve sécurisée, sous-sol fermé"},
            {"dimension": "protection", "score": 10,
             "justification": "Sous-sol : protection maximale, bâti amortissable"},
            {"dimension": "demande_locative", "score": 8,
             "justification": "78-95 €/mois constatés, offre limitée"},
        ],
        "risques": [
            {"facteur": "Charges copro inconnues (VEFA)", "severite": 4,
             "detail": "Budget prévisionnel non communiqué avant livraison"},
            {"facteur": "Relocation groupée post-livraison", "severite": 3,
             "detail": "Montée en charge 6-9 mois, couverte par la grille 0-11"},
            {"facteur": "Acte unique à confirmer", "severite": 3,
             "detail": "11 actes séparés ≈ 9 600 € de frais au lieu de 2 600 €"},
            {"facteur": "VEFA — délai de livraison", "severite": 3,
             "detail": "Livraison T2 2027, ~9 mois sans revenu"},
            {"facteur": "Concurrence locative intra-quartier", "severite": 2,
             "detail": "MILOS voisin — ne pas cumuler les deux programmes"},
            {"facteur": "Liquidité bloc avant livraison", "severite": 2,
             "detail": "Fonds immobilisés jusqu'à T2 2027"},
            {"facteur": "Taux d'occupation initial", "severite": 2,
             "detail": "Première année à 70-80 % d'occupation absorbée par la "
                      "trésorerie"},
        ],
    },
    "lien_annonce": "https://www.seloger.com/annonce/achat/provence-alpes-"
                    "cote-d-azur/var-83/la-seyne-sur-mer-83500/26ED31QDH4P8",
    # Valeurs publiées historiques — UTILISÉES UNIQUEMENT pour mesurer l'écart
    "note_publiee": 9.2,
    "rendement_publie": "8,5 % / 8,8 %",
}

MILOS = {
    "slug": "2026-09-03-place-classe-b-parking-milos-la-seyne",
    "date_analyse": "2026-09-03",
    "titre": "Place de parking catégorie B (sous-sol), VEFA résidence "
             "MILOS, La Seyne-sur-Mer",
    "bien": {
        "type_bien": "parking",
        "sous_type": "sous-sol",
        "type_detail": "Place catégorie B en sous-sol — résidence neuve "
                       "sécurisée MILOS, VEFA",
        "neuf": True,
        "adresse": {"texte": "Résidence MILOS, quartier Saint-Jean, "
                             "La Seyne-sur-Mer (83500)",
                    "ville": "La Seyne-sur-Mer", "code_postal": "83500",
                    "quartier": "Saint-Jean"},
        "lots": {"count": 1, "nature": "place catégorie B sous-sol",
                 "surface_par_lot_m2": 9.2, "lots_distincts": True},
        "copro": {"charges_annuelles_euros": 150.0,
                  "charges_source": "charges annuelles estimées (écrites)"},
        "travaux": {"montant_euros": 0, "nature": None},
    },
    "annonce": {
        "plateforme": "seloger",
        "url": "https://www.seloger.com/annonces/achat/parking/"
               "la-seyne-sur-mer-83/saint-jean/275220505.htm",
        "prix_affiche_euros": 7000.0,
        "prix_retenu_euros": 7000.0,
        "prix_statut": "affiche",
    },
    "marche": {
        "valeur": {"retenue_euros": 8000.0,
                   "source": "estimation revente place catégorie B secteur "
                             "Saint-Jean (ordre de grandeur)",
                   "confiance": "faible"},
        "loyers": [{"lot": "place sous-sol cat. B", "quantite": 1,
                    "loyer_mensuel_euros": 60.0, "occupe": False}],
        "notes": "Marché estimé 60-70 €/mois pour ce gabarit (borne basse "
                 "conservatrice retenue) — aucune ancre directe",
    },
    "hypotheses": {
        "vacance_base_pct": 0.0,
        "frais_acquisition_euros": 875.0,
        "frais_acquisition_commentaire": "Barème neuf 7 k€ (875 €)",
        "charges": {
            "taxe_fonciere_annuelle_euros": 0.0,
            "charges_copro_annuelles_euros": 150.0,
            "pno_annuelle_euros": 0.0,
            "entretien_annuel_euros": 0.0,
            "comptabilite_annuelle_euros": 0.0,
        },
    },
    "analyse": {
        "branche": "parking",
        "type_operation": "locatif",
        "strategie_retenue": {"nom": "Location longue durée",
                              "code": "parking-ld", "lots": 1},
        "attractivite": [
            {"dimension": "tension_stationnement", "score": 6},
            {"dimension": "densite_residentielle", "score": 6},
            {"dimension": "accessibilite", "score": 7},
            {"dimension": "securite_acces", "score": 8},
            {"dimension": "protection", "score": 10},
            {"dimension": "demande_locative", "score": 7},
        ],
        "risques": [
            {"facteur": "Place unique : vacance binaire", "severite": 4},
            {"facteur": "Charges annuelles à confirmer par écrit", "severite": 3},
            {"facteur": "Gabarit 9,2 m² sous le standard", "severite": 3},
            {"facteur": "VEFA délai de livraison", "severite": 3},
            {"facteur": "Adresse exacte du lot inconnue", "severite": 3},
            {"facteur": "Liquidité de revente", "severite": 2},
            {"facteur": "Grille promoteur concurrente", "severite": 2},
        ],
    },
    "note_publiee": 7.3,
    "rendement_publie": "6,1 % / 6,8 %",
}

VILLA_CUERS_MDB = {
    "slug": "2026-06-25-villa-137m2-a-terminer-cuers",
    "date_analyse": "2026-06-25",
    "titre": "Villa 137 m² à terminer, Cuers (83390)",
    "bien": {
        "type_bien": "maison",
        "type_detail": "Villa individuelle neuve — gros œuvre terminé, "
                       "second œuvre à faire",
        "neuf": False,
        "adresse": {"texte": "Cuers (83390)", "ville": "Cuers",
                    "code_postal": "83390"},
        "surfaces": {"carrez_m2": 137.0},
        "travaux": {"montant_euros": 164400.0,
                    "nature": "second œuvre (1 200 €/m² ≈ 164 k€)"},
    },
    "annonce": {
        "plateforme": "plusieurs (PP, SeLoger)",
        "url": None,
        "prix_affiche_euros": 270000.0,
        "prix_retenu_euros": 270000.0,
        "prix_statut": "affiche",
    },
    "marche": {
        "valeur": {"retenue_euros": 505530.0,
                   "source": "valeur revente retenue (fiche : 463-555 k€, "
                             "maison neuve 3 380-4 050 €/m²)",
                   "confiance": "moyenne"},
        "revente": {"prix_euros": 505530.0, "duree_mois": 12,
                    "portage_mensuel_euros": 0.0,
                    "frais_vente_euros": 12552.0},
        "loyers": None,
    },
    "hypotheses": {
        "frais_acquisition_euros": 20800.0,
        "frais_acquisition_commentaire": "≈ 20 800 € (fiche)",
        "charges": {},
    },
    "analyse": {
        "branche": "mdb",
        "type_operation": "mdb",
        "strategie_retenue": {"nom": "Achat – achèvement – revente",
                              "code": "mdb", "lots": 1},
        "attractivite": [
            {"dimension": "transports", "score": 5},
            {"dimension": "commerces", "score": 7},
            {"dimension": "ecoles", "score": 6},
            {"dimension": "securite", "score": 7},
            {"dimension": "demande_locative", "score": 5},
            {"dimension": "dynamisme", "score": 5},
        ],
        "risques": [
            {"facteur": "Construction à achever : risques cachés", "severite": 5,
             "bloquant": True,
             "detail": "Garantie décennale probablement absente sur le gros "
                       "œuvre d'origine inconnue — facteur bloquant"},
            {"facteur": "DPE inconnu / isolation", "severite": 3},
            {"facteur": "Liquidité revente", "severite": 3},
            {"facteur": "Portage pendant travaux", "severite": 3},
        ],
    },
    "note_publiee": 3.2,
    "rendement_publie": "—",
}
