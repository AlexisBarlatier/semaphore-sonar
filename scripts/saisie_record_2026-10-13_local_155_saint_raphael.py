#!/usr/bin/env python3
"""Saisie du local de 155 m² (74 garage + 81 cave) — Saint-Raphaël centre (SeLoger 26TX63BF4NPD).

Usage : python3 scripts/saisie_record_2026-10-13_local_155_saint_raphael.py [--ecrire]
"""
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts"))
from analyse_app import engine, schema, scoring  # noqa: E402

BASE = RACINE / "analyses" / "analyses.json"
SLUG = "2026-10-13-local-155m2-saint-raphael-centre"
PRIX_HAI = 155000.0        # honoraires inclus (150 000 € hors honoraires + 5 000 € à l'acquéreur)
FRAIS = 12000.0            # 8 % du prix hors honoraires

RECORD = {
    "slug": SLUG,
    "date_analyse": "2026-10-13",
    "date_maj": "2026-10-13",
    "titre": "Local de 155 m² en rez-de-chaussée (74 m² garage + 81 m² cave) — Saint-Raphaël centre",
    "bien": {
        "type_bien": "local-pro",
        "sous_type": None,
        "type_detail": "Local en rez-de-chaussée de 155 m² en plein cœur de Saint-Raphaël : une partie garage "
                       "d'environ 74 m² et une partie cave/stockage d'environ 81 m², dans une copropriété de "
                       "50 lots — ni DPE ni GES (lot sans bâti chauffé)",
        "neuf": False,
        "adresse": {
            "texte": "Plateau Notre-Dame Sud / Bord de mer / Beaurivage, Saint-Raphaël (83700) — "
                     "adresse exacte non communiquée par l'agence",
            "ville": "Saint-Raphaël",
            "code_postal": "83700",
            "quartier": "Beaurivage",
        },
        "surfaces": {
            "texte": "155 m² au total : 74 m² de garage au rez-de-chaussée + 81 m² de cave/stockage — "
                     "surfaces annoncées, non mesurées",
        },
        "lots": {
            "count": 2,
            "nature": "Un seul lot en vente, mais deux volumes distincts (garage et cave) susceptibles de deux "
                      "usages et, sous réserve du règlement, de deux preneurs",
            "lots_distincts": None,
        },
        "copro": {
            "charges_annuelles_euros": 480.0,
            "charges_source": "480 €/an annoncés, copropriété de 50 lots gérée par un syndic professionnel, "
                              "aucune procédure en cours",
        },
        "travaux": {
            "montant_euros": 0.0,
            "nature": "Aucun travaux annoncé. Le local est vendu vide, sans bail et sans preneur : "
                      "l'aménagement éventuel (portes, électricité, cloisonnement) n'est pas chiffré par le vendeur",
        },
    },
    "annonce": {
        "plateforme": "seloger",
        "url": "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/saint-raphael-83700/26TX63BF4NPD",
        "prix_affiche_euros": PRIX_HAI,
        "prix_retenu_euros": PRIX_HAI,
        "prix_statut": "affiche",
        "vendeur": "Arnaud Stoclet, agent commercial (SAS Propriétés Privées, mandat réf. 448481) — "
                   "honoraires 3,33 % à la charge de l'acquéreur, soit 5 000 € : prix affiché 155 000 € "
                   "honoraires inclus, 150 000 € hors honoraires",
    },
    "marche": {
        "valeur": {
            "basse_euros": 135000.0,
            "haute_euros": 168000.0,
            "retenue_euros": 150000.0,
            "source": "Local vacant : valorisé au prix du mètre carré constaté, pas en capitalisant un loyer espéré. "
                      "Comparables de vente à Saint-Raphaël : local commercial de 150 m² à 174 000 € (1 160 €/m²), "
                      "local de 91 m² en rue n° 1 à 80 000 € (879 €/m²) ; moyenne des murs d'entrepôts de la commune "
                      "à 2 625 €/m² (Unemplacement, 24 annonces) — non comparable, il s'agit de locaux de zone. "
                      "Valeur retenue 968 €/m², soit 150 000 € pour 155 m².",
            "confiance": "faible",
        },
        "loyers": [
            {
                "lot": "Local entier — un seul preneur",
                "quantite": 1,
                "loyer_mensuel_euros": 1225.0,
                "occupe": False,
                "note": "Loyer de marché reconstitué, faute de loyer constaté : 74 m² de garage au rez-de-chaussée à "
                        "10 €/m²/mois (740 €) et 81 m² de cave/stockage à 6 €/m²/mois (486 €), soit 1 225 €/mois. "
                        "Références locales relevées le 13/10/2026 : locaux d'activités à Saint-Raphaël entre 8,3 et "
                        "14,7 €/m²/mois (entrepôt de 5 398 m² à 8,3 €/m², local d'activités de 476 m² sur axe passant "
                        "à 10,1 €/m², entrepôt de 204 m² à 14,7 €/m², local de 325 m² à 13,8 €/m²), tous avec accès "
                        "véhicule, hauteur et rideau métallique, ce que la cave n'a pas.",
            },
        ],
        "notes": "Le loyer de 1 225 €/mois n'est pas constaté : aucun bail, aucun preneur, aucune quittance. "
                 "C'est une valeur locative reconstituée à partir du relevé local — elle doit être confirmée par une "
                 "agence de gestion avant toute offre. Les deux box du dossier Saint-Raphaël du 4 octobre donnent "
                 "l'ordre de grandeur du petit lot (12,5 à 13,2 €/m²/mois), mais la prime de rareté du petit lot "
                 "ne se transpose pas à 155 m².",
    },
    "hypotheses": {
        "vacance_base_pct": 10.0,
        "vacance_best_pct": 5.0,
        "vacance_worst_pct": 20.0,
        "taux_placement_reserve_pct": 2.84,
        "quote_part_bati_pct": 90.0,
        "vacance_justification": "Un seul preneur pour 155 m², aucun bail en place : la vacance n'est pas une "
                                 "statistique, c'est un état de départ. 10 % en base (un mois de vide par an en "
                                 "moyenne sur la durée), 20 % en worst (un an sans preneur, toutes charges au "
                                 "bailleur), 5 % en best si un artisan signe un bail 3-6-9 dès l'acquisition.",
        "charges": {
            "charges_copro_annuelles_euros": 480.0,
            "charges_copro_commentaire": "480 €/an annoncés (0,26 €/m²/mois) : très faibles, ce qui est cohérent "
                                         "avec un lot sans bâti — budget prévisionnel et dernière AG à exiger",
            "taxe_fonciere_annuelle_euros": 900.0,
            "taxe_fonciere_commentaire": "900 €/an estimés pour un local de 155 m² à Saint-Raphaël (aucun avis "
                                         "communiqué) — hypothèse, à remplacer par l'avis réel. En bail commercial, "
                                         "la taxe foncière est refacturable au preneur si le bail le prévoit : "
                                         "aucun bail n'existe ici, elle reste donc au bailleur",
            "entretien_annuel_euros": 400.0,
            "entretien_commentaire": "400 €/an estimés : entretien courant et provision pour grosses réparations de "
                                     "l'article 606 (toiture, façade, structure), qui restent au bailleur par "
                                     "nature. La provision travaux du moteur (2,5 % des loyers) s'y ajoute",
            "pno_annuelle_euros": 180.0,
            "comptabilite_annuelle_euros": 0.0,
        },
        "frais_acquisition_euros": FRAIS,
        "frais_acquisition_commentaire": "8 % du prix hors honoraires (12 000 €) ; les 5 000 € d'honoraires "
                                         "d'agence sont à la charge de l'acquéreur et déjà portés par le prix affiché",
    },
    "analyse": {
        "branche": "professionnel",
        "type_operation": "locatif",
        "strategie_retenue": {
            "nom": "Bail commercial du local entier à un artisan ou une activité de stockage",
            "code": "pro-bail",
            "lots": 1,
        },
        "strategies_explorees": [
            {
                "strategie": "Bail commercial 3-6-9 du local entier à un seul preneur",
                "lots": 1,
                "performance": "5,5 % net après IS sur le prix de revient avec le loyer de 1 225 €/mois, "
                               "pour un plancher de branche de 7 % — sous le seuil avec le loyer le plus probable",
                "valeur_sortie": "Valeur de capitalisation au taux du profil : 150 000 € environ à 9 %, "
                                 "soit le prix affiché",
                "faisabilite": "Le local est vide : le délai de relocation se compte en trimestres, et "
                               "l'aménagement (électricité, portes, sanitaires) n'est pas chiffré",
                "risque": "élevé — un seul preneur, aucun bail, et une activité que le règlement de copropriété "
                          "n'a pas encore autorisée",
            },
            {
                "strategie": "Deux preneurs — garage et cave loués séparément",
                "lots": 2,
                "performance": "Améliore le rendement de 0,3 à 0,8 point en répartissant le risque, à condition "
                               "de créer un accès indépendant pour la cave",
                "valeur_sortie": "Valeur inchangée, mais liquidité meilleure à la revente",
                "faisabilite": "Les deux volumes existent déjà séparément ; le cloisonnement, l'accès et "
                               "l'électricité ne sont ni chiffrés ni autorisés par écrit",
                "risque": "modéré — deux preneurs, deux baux, deux risques de vacance, plus de gestion",
            },
            {
                "strategie": "Division en boxes de stockage ou en caves",
                "lots": 4,
                "performance": "Le loyer au mètre carré d'un box est le double de celui d'un plateau, mais le "
                               "coût d'aménagement et le permis éventuel n'ont pas de devis : non chiffrable en l'état",
                "valeur_sortie": "Aucune valeur créée tant que la division n'est pas autorisée et chiffrée",
                "faisabilite": "À vérifier au règlement de copropriété et au PLU avant tout engagement",
                "risque": "élevé — division non documentée, travaux non chiffrés, autorisations non obtenues",
            },
            {
                "strategie": "Changement de destination vers l'habitation",
                "lots": 1,
                "performance": "Hors sujet en l'état : la cave n'a pas de jour sur l'extérieur et le garage "
                               "devrait être restructuré",
                "valeur_sortie": "Fort potentiel théorique en centre-ville de Saint-Raphaël, mais soumis au PLU "
                                 "et à une structure à reprendre",
                "faisabilite": "À vérifier d'abord au PLU (linéaire commercial protégé) et sur un devis de "
                               "restructuration",
                "risque": "élevé — cette voie ne se juge pas sans les deux pièces qui manquent",
            },
        ],
        "attractivite": [
            {
                "dimension": "accessibilite",
                "score": 7,
                "justification": "Plein cœur de Saint-Raphaël, accès rez-de-chaussée direct depuis la rue, "
                                 "à quelques minutes de la gare et des axes du centre. Pas d'aire de manœuvre "
                                 "pour un poids lourd, ce qui écarte la logistique.",
            },
            {
                "dimension": "visibilite_flux",
                "score": 5,
                "justification": "Le produit n'est pas un commerce : pas de vitrine décrite, pas de linéaire. "
                                 "La visibilité ne vaut que pour une activité artisanale de proximité, pas pour "
                                 "un usage de vente au détail.",
            },
            {
                "dimension": "bassin_emploi",
                "score": 7,
                "justification": "Saint-Raphaël, 36 000 habitants, commune de la corniche varoise : tissu "
                                 "d'artisans, de services et de commerces dense, plus l'activité touristique. "
                                 "La demande de surfaces de stockage y est alimentée par les professionnels du "
                                 "bâtiment et du paysage.",
            },
            {
                "dimension": "concurrence",
                "score": 6,
                "justification": "Six annonces d'entrepôts ou de locaux d'activités à louer sur la commune, plus "
                                 "les locaux commerciaux : l'offre n'est pas saturée, mais les concurrents ont "
                                 "rideaux métalliques, hauteur et accès poids lourds. Les petits box de stockage "
                                 "de la commune se louent 16 à 18 €/m²/mois — c'est la référence qui compte pour "
                                 "un produit de 10 à 40 m², pas pour 155.",
            },
            {
                "dimension": "dynamisme",
                "score": 6,
                "justification": "Commune littorale à économie mixte, tourisme et services : pas de zone "
                                 "industrialo-logistique structurante, mais une demande artisanale continue.",
            },
            {
                "dimension": "reglementaire",
                "score": 4,
                "justification": "Point critique du dossier : ni la destination du lot au règlement de "
                                 "copropriété, ni l'usage autorisé (stockage professionnel, atelier, activité "
                                 "recevant du public) ne sont documentés. Copropriété de 50 lots, centre-ville, "
                                 "partie enterrée : les règles de sécurité et l'accessibilité doivent être "
                                 "vérifiées avant l'offre, pas après.",
            },
        ],
        "risques": [
            {
                "facteur": "Usage autorisé par le règlement de copropriété : la question est ouverte",
                "detail": "L'annonce vend « garage, cave, stockage, activité professionnelle » sans jamais citer "
                          "la désignation du lot ni l'usage que le règlement autorise. C'est exactement la "
                          "question restée sans réponse sur les deux box du dossier du 4 octobre, où l'agence a "
                          "répondu par la désignation « garage » et rien sur le stockage professionnel. Dans une "
                          "copropriété de 50 lots en centre-ville, un stockage professionnel ou une activité "
                          "recevant du public peut être interdit au règlement ou soumis à l'accord du syndic. "
                          "Tant que la réponse n'est pas écrite, le dossier n'a pas de projet.",
                "severite": 5,
            },
            {
                "facteur": "Aucun preneur, aucun bail, aucun loyer constaté",
                "detail": "Le local est vide et le loyer de 1 225 €/mois est une reconstitution de marché, pas un "
                          "revenu. Sur 155 m² d'un seul tenant, la relocation se compte en trimestres et la "
                          "marge d'erreur sur le loyer est de plusieurs centaines d'euros par mois : à "
                          "1 000 €/mois, le dossier rend 4,6 % et ne couvre pas sa charge ; à 1 450 €/mois, il "
                          "atteint 7 % et l'équilibre.",
                "severite": 4,
            },
            {
                "facteur": "Partie cave de 81 m² : accès, hauteur et sécurité",
                "detail": "La moitié du lot est en cave, c'est-à-dire sans accès véhicule, sans jour, sans "
                          "ventilation décrite. Le prix de 1 000 €/m² du lot entier repose sur l'hypothèse que "
                          "ces 81 m² valent du stockage louable. Sans plan, sans coupe et sans hauteur sous "
                          "plafond, on ne sait pas ce qu'on achète réellement — ni si un preneur la voudra.",
                "severite": 4,
            },
            {
                "facteur": "Écart au plancher de rendement de la branche",
                "detail": "À 1 225 €/mois de loyer et 155 000 € affichés, le rendement net après IS sur prix de "
                          "revient ressort à 5,5 % pour un plancher de 7 % : le dossier est sous son seuil de "
                          "1,5 point au loyer le plus probable, et il ne le franchit qu'à partir d'environ "
                          "1 450 € par mois, soit 9,4 €/m² — le haut de la fourchette des locaux d'activités "
                          "municipaux, pour un produit qui n'a ni rideau métallique ni hauteur.",
                "severite": 4,
            },
            {
                "facteur": "Honoraires à la charge de l'acquéreur",
                "detail": "5 000 € d'honoraires pèsent sur l'acquéreur (3,33 %), sans marge de négociation de ce "
                          "côté : ce sont 4 % du prix net qui s'ajoutent aux droits et émoluments.",
                "severite": 2,
            },
            {
                "facteur": "Copropriété de 50 lots : travaux et appels de fonds non documentés",
                "detail": "480 €/an de charges annoncées, mais aucun budget prévisionnel, aucun PV d'assemblée, "
                          "aucun plan pluriannuel de travaux. Sur un immeuble de centre-ville qui porte une cave, "
                          "les postes qui coûtent ne se voient pas dans les charges courantes : étanchéité, "
                          "descentes d'eaux, structure.",
                "severite": 3,
            },
            {
                "facteur": "Destination et cadre réglementaire",
                "detail": "Aucune information sur la zone du PLU, sur un éventuel linéaire commercial protégé, "
                          "ni sur les risques (Géorisques) — le bien est en secteur urbain ancien. La voie du "
                          "changement de destination vers l'habitation, théoriquement la plus créatrice de "
                          "valeur en centre-ville, dépend entièrement de ces documents.",
                "severite": 3,
            },
        ],
    },
}


def main():
    ecrire = "--ecrire" in sys.argv
    print("validation du record :", schema.validate_record(RECORD) or "aucune erreur")
    c = engine.compute(RECORD)
    n, v, comp = scoring.note_et_verdict(RECORD, c)
    plafond, detail = scoring.prix_plafond(RECORD)
    cible = scoring.prix_cible(RECORD)
    f, rd = c["fiscal"], c["rendements"]
    print(f"\nrevient {c['prix_revient_total']:.0f} € | revenus bruts {c['revenus_bruts_annuels']:.0f} €/an | "
          f"ratio coût/valeur {c['ratio_cout_valeur']:.3f}")
    print(f"EBE {f['ebe']:.0f} € | amortissement {f['amortissement']:.0f} € | IS {f['is_annuel']:.0f} € | "
          f"net après IS {f['net_apres_is']:.0f} €/an ({f['net_apres_is']/12:.0f} €/mois)")
    print(f"net sur revient {rd['net_sur_revient_pct']:.2f} % | net sur valeur {rd['net_sur_valeur_pct']:.2f} %")
    print(f"NOTE {n} — {v} | plafond {plafond:.0f} € | cible {cible:.0f} € | contrainte {detail}")
    ANNUITE = 0.9 * (0.037 / 12) / (1 - (1 + 0.037 / 12) ** -180) + 0.9 * 0.0034 / 12
    print(f"annuité {PRIX_HAI*ANNUITE:.0f} €/mois | solde {f['net_apres_is']/12 - PRIX_HAI*ANNUITE:+.0f} €/mois | "
          f"autofinancement {(f['net_apres_is']/12)/ANNUITE:.0f} €")
    if not ecrire:
        print("\n(base non modifiée — relancer avec --ecrire)")
        return
    data = json.loads(BASE.read_text(encoding="utf-8"))
    avant = len(data["analyses"])
    data["analyses"] = [a for a in data["analyses"] if a["slug"] != SLUG]
    data["analyses"].append(RECORD)
    BASE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nanalyses.json : {avant} -> {len(data['analyses'])} dossiers (slug {SLUG})")


if __name__ == "__main__":
    main()
