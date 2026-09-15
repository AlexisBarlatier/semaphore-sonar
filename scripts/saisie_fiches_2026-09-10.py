#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saisie des fiches du 10/09/2026 dans analyses/analyses.json (mode dry-run par defaut)."""
import json, sys, copy

sys.path.insert(0, '/home/alexis-barlatier/Documents/Semaphore-sonar/scripts')
from analyse_app import schema, engine, scoring

BASE = '/home/alexis-barlatier/Documents/Semaphore-sonar/analyses/analyses.json'

DIM = ("transports", "commerces", "ecoles", "securite", "demande_locative", "dynamisme")


def attract(notes):
    return [{"dimension": d, "score": notes[d][0], "justification": notes[d][1]} for d in DIM]


AGUILLON = {
    "slug": "2026-09-10-t4-73m2-aguillon-toulon",
    "date_analyse": "2026-09-10",
    "date_maj": None,
    "titre": "Toulon — T4 73 m², 1er étage avec ascenseur, quartier Aguillon (DPE E, salle de bain à moderniser)",
    "bien": {
        "type_bien": "appartement", "sous_type": None,
        "type_detail": "T4 traversant de 73 m² au 1er étage sur 7, ascenseur, 3 chambres, cuisine ouverte, salle de bain et WC séparés, 2 balcons (10 m²). Immeuble de 1980, chauffage individuel électrique. Pas de cave. Copropriété de 77 lots. Proche place du Mourillon et des commerces.",
        "neuf": False,
        "adresse": {"texte": "Quartier Aguillon, Toulon (83000) — adresse exacte non communiquée dans l'annonce", "ville": "Toulon", "code_postal": "83000"},
        "surfaces": {"texte": "73 m² annoncés (loi Carrez à confirmer)", "carrez_m2": 73.0},
        "lots": {"count": 1, "surface_par_lot_m2": 73.0, "nature": "1 appartement", "lots_distincts": 1},
        "copro": {"charges_annuelles_euros": 1400.0, "charges_source": "Estimation copropriété de 77 lots avec ascenseur, ~19 €/m²/an. À confirmer sur budget prévisionnel et avis de charges."},
        "travaux": {"montant_euros": 8000.0, "nature": "Modernisation de la salle de bain + rafraîchissement courant. Fourchette 6-12 k€, devis avant offre. Renovation energetique (isolation intérieure, menuiseries, chauffage) non incluse : 15-30 k€, chiffrée comme non rentable."},
    },
    "annonce": {
        "plateforme": "seloger", "url": "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/toulon-83000/26ZBKX4HBQAP",
        "prix_affiche_euros": 163500.0, "prix_retenu_euros": None, "prix_statut": "affiche",
        "prix_commentaire": "2 240 €/m² affichés. Honoraires à la charge du vendeur.",
    },
    "marche": {
        "valeur": {"basse_euros": 180000.0, "haute_euros": 200000.0, "retenue_euros": 190000.0,
                   "source": "Quartier Aguillon : 2 820 €/m² (offres en cours, efficity 08/2026) à 3 162 €/m² (ventes réelles DVF, Lestimo). Valeur en l'état retenue 2 600 €/m² : décote d'état (salle de bain vétuste) et de DPE E, plus absence de cave. Le prix/m² moyen n'est pas un prix de revente pour un bien en DPE E non traité.",
                   "confiance": "moyenne"},
        "loyers": [{"lot": "T4 73 m² (1er étage, ascenseur, 2 balcons)", "quantite": 1, "loyer_mensuel_euros": 950.0, "occupe": False,
                    "note": "Bien libre. Marché local : T4 102 m² Aguillon loué 1 255 € CC (12,3 €/m²), T4 rénové 760 € + 130 € de charges, T3 67 m² 900 € (13,4 €/m²). Retenu 950 € CC (13 €/m²), soit ~880 € hors charges. Fourchette 880-1 080."}],
        "notes": "Loyer retenu en bas de fourchette : DPE E avec facture énergétique annoncée de 1 465 à 1 981 €/an, ce qui pèse sur le loyer négociable. Le bien reste louable jusqu'en 2034 (interdiction DPE E).",
    },
    "hypotheses": {
        "vacance_base_pct": 5.0, "vacance_best_pct": 3.0, "vacance_worst_pct": 10.0,
        "vacance_justification": "Défaut résidentiel : locatif Toulon tendu, bien libre donc relocation rapide possible. Worst 10 % = DPE E mal accepté, délai de relocation allongé.",
        "frais_acquisition_euros": 13080.0,
        "charges": {
            "taxe_fonciere_annuelle_euros": 1250.0,
            "taxe_fonciere_commentaire": "Estimation 73 m² Toulon (commune à taux élevé), à vérifier sur avis réel. Alerte si > 15 % du brut.",
            "charges_copro_annuelles_euros": 1400.0,
            "charges_copro_commentaire": "Copropriété 77 lots avec ascenseur, ~19 €/m²/an. À confirmer.",
            "pno_annuelle_euros": 180.0, "pno_commentaire": "PNO appartement.",
            "entretien_annuel_euros": 300.0, "entretien_commentaire": "Entretien courant.",
            "comptabilite_annuelle_euros": 400.0, "comptabilite_commentaire": "Comptabilité SCI.",
        },
    },
    "analyse": {
        "branche": "residentiel", "type_operation": "locatif",
        "strategie_retenue": {"nom": "Location longue durée nue", "code": "ld-nue", "lots": 1},
        "strategies_explorees": [
            {"strategie": "Location nue longue durée", "lots": 1, "faisabilite": "immédiate après modernisation salle de bain", "risque": "faible"},
            {"strategie": "MDB : achat, remise en état, revente à un utilisateur", "lots": 1, "faisabilite": "12 mois", "risque": "moyen (marge uniquement si achat <= 137 k€)"},
        ],
        "attractivite": attract({
            "transports": (7, "Quartier bien desservi (bus, proximité Mourillon et centre-ville), stationnement en surface tendu."),
            "commerces": (7, "Commerces, écoles, administrations à proximité immédiate selon l'annonce ; place du Mourillon à quelques minutes."),
            "ecoles": (7, "Secteur scolaire toulonnais dense, écoles et collèges à pied."),
            "securite": (6, "Quartier résidentiel calme, résidence annoncée bien entretenue. Pas de QPV."),
            "demande_locative": (8, "Toulon : loyer moyen 16 €/m², demande familiale et active soutenue sur l'est toulonnais."),
            "dynamisme": (7, "Prix Toulon stables à orientés hausse, quartier recherché proche littoral."),
        }),
        "risques": [
            {"facteur": "DPE E — horizon réglementaire", "detail": "E interdit à la location en 2034. Le logement reste louable huit ans, mais la facture énergétique annoncée (1 465 à 1 981 €/an, chauffage électrique) pèse sur le loyer et sur la revente.", "severite": 3},
            {"facteur": "Charges fixes élevées", "detail": "Copropriété avec ascenseur + taxe foncière toulonnaise = 24 à 27 % du loyer brut. C'est le poste qui ramène le rendement sous le seuil, pas le prix d'achat.", "severite": 3},
            {"facteur": "Travaux non chiffrés par devis", "detail": "« Modernisation de la salle de bain » : fourchette 6-12 k€. Sur un immeuble de 1980, prévoir des surprises (électricité, plomberie).", "severite": 2},
            {"facteur": "Pas de cave", "detail": "Absence de cave annoncée : légère perte d'attractivité locative et de valeur à la revente.", "severite": 1},
        ],
    },
}

LOT3 = {
    "slug": "2026-09-10-lot-3-logements-rdc-toulon",
    "date_analyse": "2026-09-10",
    "date_maj": None,
    "titre": "Toulon — Lot de 3 logements en RDC (T2 32,76 m² + 2 studios), loués en 3/6/9",
    "bien": {
        "type_bien": "appartement", "sous_type": None,
        "type_detail": "Lot complet de 3 logements au rez-de-chaussée : T2 de 32,76 m², studio de 19,81 m², studio de 21,39 m². Immeuble de 1925, 6 étages, sans ascenseur, exposition sud, 3 WC séparés, pas de cave, pas de balcon. Copropriété de 22 lots. Travaux de rénovation à prévoir (non chiffrés). Les trois logements sont loués en 3/6/9.",
        "neuf": False,
        "adresse": {"texte": "Toulon (83000) — quartier non précisé dans l'annonce, secteur annoncé bien placé proche commodités et transports", "ville": "Toulon", "code_postal": "83000"},
        "surfaces": {"texte": "73,96 m² habitables (somme des trois lots) — l'annonce affiche 86,7 m², écart de 12,74 m² à justifier", "carrez_m2": 73.96},
        "lots": {"count": 3, "surface_par_lot_m2": None, "nature": "T2 32,76 m² + studio 19,81 m² + studio 21,39 m²", "lots_distincts": 3},
        "copro": {"charges_annuelles_euros": 1100.0, "charges_source": "Estimation pour 3 lots en copropriété de 22 lots de 1925 sans ascenseur (RDC). À confirmer sur budget prévisionnel."},
        "travaux": {"montant_euros": 45000.0, "nature": "Rénovation des trois logements ('travaux de rénovation à prévoir' — non chiffrés par le vendeur). Hypothèse 15 k€ par logement (second œuvre : réseaux, cloisons, sols, salle d'eau, cuisine). Fourchette 30-60 k€ selon l'état réel."},
    },
    "annonce": {
        "plateforme": "seloger", "url": "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/toulon-83000/26C7IRSUZ172",
        "prix_affiche_euros": 189000.0, "prix_retenu_euros": None, "prix_statut": "affiche",
        "prix_commentaire": "2 180 €/m² sur la surface affichée (86,7 m²), mais 2 555 €/m² sur la surface réelle des trois lots (73,96 m²). Honoraires à la charge du vendeur.",
    },
    "marche": {
        "valeur": {"basse_euros": 195000.0, "haute_euros": 225000.0, "retenue_euros": 210000.0,
                   "source": "Toulon : prix moyen appartements ~3 200 €/m² (MeilleursAgents 09/2026), 2 907 €/m² pour le bien médian SeLoger. Lots de petites surfaces en RDC d'immeuble ancien : valeur retenue 2 840 €/m² sur 73,96 m², décotée pour le RDC et l'état à rénover. Confiance faible : quartier non communiqué.",
                   "confiance": "faible"},
        "loyers": [
            {"lot": "T2 32,76 m²", "quantite": 1, "loyer_mensuel_euros": 524.0, "occupe": True, "note": "Hypothèse 16 €/m² — loyer réel non communiqué dans l'annonce."},
            {"lot": "Studio 19,81 m²", "quantite": 1, "loyer_mensuel_euros": 396.0, "occupe": True, "note": "Hypothèse 20 €/m² (petite surface) — loyer réel non communiqué."},
            {"lot": "Studio 21,39 m²", "quantite": 1, "loyer_mensuel_euros": 428.0, "occupe": True, "note": "Hypothèse 20 €/m² — loyer réel non communiqué."},
        ],
        "notes": "Loyers de marché estimés (1 348 €/mois au total) car l'annonce ne communique AUCUN loyer en place. Les baux 3/6/9 en cours peuvent être nettement inférieurs (baux anciens) : à exiger avant tout chiffrage définitif. Rendement brut estimé 7,9 % sur le revient, mais 4,5-5,5 % net après charges et fiscalité.",
    },
    "hypotheses": {
        "vacance_base_pct": 8.0, "vacance_best_pct": 5.0, "vacance_worst_pct": 14.0,
        "vacance_justification": "Trois logements = trois baux, donc rotation plus fréquente qu'un lot unique. Base 8 % (au-dessus du défaut résidentiel 5 %) pour tenir compte du turnover des petits logements et d'une relocation étalée. Worst 14 % = vacance simultanée de deux lots.",
        "frais_acquisition_euros": 15120.0,
        "charges": {
            "taxe_fonciere_annuelle_euros": 1800.0,
            "taxe_fonciere_commentaire": "Trois lots = trois impositions. Estimation 600 €/lot, à vérifier sur avis réels. Alerte si > 15 % du brut.",
            "charges_copro_annuelles_euros": 1100.0,
            "charges_copro_commentaire": "Copropriété de 22 lots, immeuble de 1925 sans ascenseur, RDC. À confirmer.",
            "pno_annuelle_euros": 250.0, "pno_commentaire": "PNO pour trois lots.",
            "entretien_annuel_euros": 500.0, "entretien_commentaire": "Entretien courant de trois logements (plus d'équipements qu'un lot unique).",
            "comptabilite_annuelle_euros": 400.0, "comptabilite_commentaire": "Comptabilité SCI.",
        },
    },
    "analyse": {
        "branche": "residentiel", "type_operation": "locatif",
        "strategie_retenue": {"nom": "Location longue durée nue — trois logements conservés", "code": "ld-nue", "lots": 3},
        "strategies_explorees": [
            {"strategie": "Location nue des trois lots", "lots": 3, "faisabilite": "immédiate, baux en cours", "risque": "faible"},
            {"strategie": "MDB : rénovation puis revente à la découpe des trois lots", "lots": 3, "faisabilite": "12-18 mois", "risque": "élevé — la revente à la découpe ne couvre pas le stock (marge -27 à -88 k€)"},
        ],
        "attractivite": attract({
            "transports": (7, "Secteur annoncé proche des transports, quartier non précisé dans l'annonce : note non vérifiable en l'état."),
            "commerces": (7, "Commodités annoncées à proximité immédiate. À confirmer par l'adresse exacte, non communiquée."),
            "ecoles": (6, "Toulon intra-muros disposant d'un maillage scolaire dense, sous réserve de l'implantation réelle."),
            "securite": (5, "Quartier non communiqué : note médiane par défaut. Un RDC d'immeuble de 1925 est plus exposé."),
            "demande_locative": (8, "Petites surfaces : la demande locative toulonnaise est structurellement forte sur les studios et T2, avec des loyers au m² supérieurs aux grandes surfaces."),
            "dynamisme": (7, "Marché toulonnais stable à haussier, forte demande locative estudiantine et active."),
        }),
        "risques": [
            {"facteur": "Loyers en place non communiqués", "detail": "L'annonce ne donne aucun loyer. Les baux 3/6/9 en cours peuvent être des baux anciens très en dessous du marché : impossible de valider le rendement sans les baux et les quittances. Première exigence avant toute offre.", "severite": 4},
            {"facteur": "Surfaces incohérentes", "detail": "Somme des trois lots : 73,96 m². Surface affichée : 86,7 m². Écart de 12,74 m² qui change le prix au m² (2 555 € au lieu de 2 180) et la valeur de revente. Exiger les surfaces Carrez de chaque lot.", "severite": 3},
            {"facteur": "Travaux non chiffrés", "detail": "« Travaux de rénovation à prévoir » sur trois logements : 30 à 60 k€ selon l'état. Aucun devis fourni, aucune visite technique possible avant offre sérieuse.", "severite": 3},
            {"facteur": "Rez-de-chaussée d'immeuble de 1925", "detail": "RDC ancien : vérifier humidité, remontées capillaires, ventilation et exposition du lot. Trois WC séparés et pas de cave laissent supposer des distributions étroites.", "severite": 3},
            {"facteur": "Gestion de trois baux", "detail": "Trois locataires, trois quittances, trois échéances : la charge de gestion et le risque d'impayé sont supérieurs à un lot unique.", "severite": 2},
        ],
    },
}

CHAMP = {
    "slug": "2026-09-10-t4-66m2-champ-de-mars-toulon",
    "date_analyse": "2026-09-10",
    "date_maj": None,
    "titre": "Toulon — T4 66 m², 2e étage sans ascenseur, quartier Champ de Mars (est toulonnais)",
    "bien": {
        "type_bien": "appartement", "sous_type": None,
        "type_detail": "T4 de 66 m² au 2e étage sur 4, sans ascenseur, 3 chambres, cuisine séparée, cellier, WC indépendant, salle de bain, pas de cave. Immeuble de copropriété de 20 lots, charges 960 €/an. Annoncé en bon état, sans travaux. DPE D, GES B, chauffage individuel électrique. Commercialisé comme idéal investisseur et colocation (proche universités).",
        "neuf": False,
        "adresse": {"texte": "Quartier Champ de Mars, Toulon Est (83000) — adresse exacte non communiquée", "ville": "Toulon", "code_postal": "83000"},
        "surfaces": {"texte": "66 m² annoncés", "carrez_m2": 66.0},
        "lots": {"count": 1, "surface_par_lot_m2": 66.0, "nature": "1 appartement", "lots_distincts": 1},
        "copro": {"charges_annuelles_euros": 960.0, "charges_source": "Charges annoncées dans l'annonce pour une copropriété de 20 lots — niveau faible, bon point du dossier."},
        "travaux": {"montant_euros": 0.0, "nature": "Aucun travaux annoncé. DPE D : pas de contrainte réglementaire avant 2034."},
    },
    "annonce": {
        "plateforme": "seloger", "url": "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/toulon-83000/26RTY777JQHN",
        "prix_affiche_euros": 158000.0, "prix_retenu_euros": None, "prix_statut": "affiche",
        "prix_commentaire": "2 394 €/m² affichés contre 2 228 €/m² de moyenne MeilleursAgents pour le secteur Jardin du Champ de Mars, soit environ 7 % au-dessus du marché. Honoraires à la charge du vendeur.",
    },
    "marche": {
        "valeur": {"basse_euros": 140000.0, "haute_euros": 154000.0, "retenue_euros": 147000.0,
                   "source": "MeilleursAgents secteur Jardin du Champ de Mars : 2 228 €/m² moyens (fourchette très large de 1 279 €/m² vers le haut). Valeur retenue 2 228 €/m² × 66 m². Le bien est affiché au-dessus de cette moyenne.",
                   "confiance": "moyenne"},
        "loyers": [{"lot": "T4 66 m² (2e étage, 3 chambres)", "quantite": 1, "loyer_mensuel_euros": 930.0, "occupe": False,
                    "note": "Location nue : marché local 860-950 € pour un T4 de ce type, retenu 930 € (14 €/m²). Colocation testée et écartée : 3 chambres de 9-11 m² plafonnent à 400-450 € (comparable direct : T4 meublé 67 m², 3 chambres, à partir de 450 € CC) et les charges de gestion (fluides, ménage, mobilier) rendent la colocation MOINS rentable que le nu : EBE 651 €/mois contre 698-708 €/mois en nu."}],
        "notes": "Étude colocation menée à la demande de Rémy : loyer brut +42 % mais charges +168 % — la colocation ne sauve pas ce dossier. Le nu reste le meilleur usage.",
    },
    "hypotheses": {
        "vacance_base_pct": 5.0, "vacance_best_pct": 3.0, "vacance_worst_pct": 10.0,
        "vacance_justification": "Défaut résidentiel : marché locatif toulonnais tendu, bien libre. Worst 10 % = délai de relocation et impayé couverts par provision.",
        "frais_acquisition_euros": 12640.0,
        "charges": {
            "taxe_fonciere_annuelle_euros": 950.0,
            "taxe_fonciere_commentaire": "Estimation 66 m² Toulon, à vérifier sur avis réel.",
            "charges_copro_annuelles_euros": 960.0,
            "charges_copro_commentaire": "Charges annoncées (20 lots) : 960 €/an, soit 80 €/mois.",
            "pno_annuelle_euros": 200.0, "pno_commentaire": "PNO appartement.",
            "entretien_annuel_euros": 300.0, "entretien_commentaire": "Entretien courant.",
            "comptabilite_annuelle_euros": 400.0, "comptabilite_commentaire": "Comptabilité SCI.",
        },
    },
    "analyse": {
        "branche": "residentiel", "type_operation": "locatif",
        "strategie_retenue": {"nom": "Location longue durée nue", "code": "ld-nue", "lots": 1},
        "strategies_explorees": [
            {"strategie": "Location nue", "lots": 1, "faisabilite": "immédiate", "risque": "faible"},
            {"strategie": "Colocation meublée 3 chambres", "lots": 3, "faisabilite": "immédiate après équipement", "risque": "moyen — écartée : charges de gestion supérieures au gain de loyer"},
        ],
        "attractivite": attract({
            "transports": (7, "Toulon Est, proche axes et transports urbains ; accès rapide au campus universitaire de La Garde."),
            "commerces": (7, "Secteur animé de l'est toulonnais, commerces de proximité."),
            "ecoles": (8, "Proximité immédiate des universités et écoles supérieures — argument central de l'annonce, cohérent avec la géographie."),
            "securite": (5, "Quartier populaire de l'est toulonnais, sans être un QPV. Notoriété locale moyenne."),
            "demande_locative": (8, "Demande étudiante et active soutenue ; le bassin universitaire de La Garde irrigue ce secteur."),
            "dynamisme": (6, "Prix stables sur Toulon Est, quartier sans moteur particulier de valorisation."),
        }),
        "risques": [
            {"facteur": "Prix affiché au-dessus du marché du secteur", "detail": "2 394 €/m² contre 2 228 €/m² de moyenne MeilleursAgents sur le secteur, soit +7 %. Il n'y a aucune décote d'entrée à capter : tout le rendement doit venir de la négociation.", "severite": 4},
            {"facteur": "Rendement sous le seuil", "detail": "En location nue avec provision d'impayés, le rendement net ressort à 4,8 % sur le revient, contre un seuil de parc de 6,5 %. Même au loyer haut de fourchette, le dossier ne passe pas.", "severite": 4},
            {"facteur": "2e étage sans ascenseur", "detail": "Deuxième étage sans ascenseur : pénalise la revente et une partie de la demande locative (familles, seniors).", "severite": 2},
            {"facteur": "Pas de cave", "detail": "Absence de cave : perte d'agrément et de valeur à la revente.", "severite": 2},
        ],
    },
}

NEW = [AGUILLON, LOT3, CHAMP]


def main(write=False):
    data = json.load(open(BASE))
    existing = {r["slug"] for r in data["analyses"]}
    out = []
    for rec in NEW:
        if rec["slug"] in existing:
            print(f"DEJA PRESENT : {rec['slug']}")
            continue
        errs = schema.validate_record(rec)
        rec["champs_manquants"] = schema.champs_manquants(rec)
        out.append(rec)
        print(f"\n=== {rec['slug']}")
        print(f"  validation : {errs if errs else 'OK'}")
        print(f"  champs manquants : {rec['champs_manquants']}")
        try:
            r = engine.compute(rec)
            note, verdict, comp = scoring.note_et_verdict(rec, r)
            print(f"  revient {r['prix_revient_total']:,.0f} € | revenus bruts {r['revenus_bruts_annuels']:,.0f} € | "
                  f"EBE {r['fiscal']['ebe']:,.0f} € | CF net {r['fiscal']['cf_mensuel_net']:,.0f} €/m")
            rd = r['rendements']
            print(f"  rendement net : revient {rd['net_sur_revient_pct']:.1f}% | achat {rd['net_sur_achat_pct']:.1f}% | "
                  f"valeur ({rd['valeur_base_label']}) {rd['net_sur_valeur_pct']:.1f}% | ratio cout/valeur {r['ratio_cout_valeur']:.2f}")
            print(f"  NOTE {note:.1f} → {verdict}")
            print(f"  composantes : {comp}")
        except Exception as e:
            print(f"  ERREUR MOTEUR : {type(e).__name__}: {e}")

    if write and out:
        data["analyses"].extend(out)
        data["meta"]["count"] = len(data["analyses"])
        data["meta"]["generated_at"] = "2026-09-10T00:00:00+00:00"
        data["meta"]["source"] = "saisie-agent"
        json.dump(data, open(BASE, "w"), ensure_ascii=False, indent=1)
        print(f"\nECRIT : {len(out)} fiches ajoutees, meta.count = {data['meta']['count']}")


if __name__ == "__main__":
    main(write="--write" in sys.argv)
