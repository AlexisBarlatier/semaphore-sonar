#!/usr/bin/env python3
"""Saisie du duplex 3 pièces de 63 m² — Champ de Mars, Toulon (annonce SeLoger 26SXIFKHH1R3).

Usage : python3 scripts/saisie_record_2026-10-13_duplex_champs_de_mars.py [--ecrire]

Sans --ecrire, le script calcule et affiche sans toucher à analyses/analyses.json.
"""
import copy
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts"))
from analyse_app import engine, schema, scoring  # noqa: E402

BASE = RACINE / "analyses" / "analyses.json"
SLUG = "2026-10-13-duplex-3p-63m2-champs-de-mars-toulon"

PRIX = 140000.0
FRAIS = 11200.0
ANNUITE = 0.9 * (0.037 / 12) / (1 - (1 + 0.037 / 12) ** -180) + 0.9 * 0.0034 / 12

RECORD = {
    "slug": SLUG,
    "date_analyse": "2026-10-13",
    "date_maj": "2026-10-13",
    "titre": "Duplex 3 pièces de 63 m² avec chambre mansardée — Champ de Mars, Toulon",
    "bien": {
        "type_bien": "appartement",
        "sous_type": None,
        "type_detail": "3 pièces de 63 m² Carrez (89 m² au sol) en 8e étage sur 9 avec ascenseur, "
                       "chambre mansardée en duplex au dernier niveau, véranda fermée de 11 m², "
                       "balcon de 12 m² à l'ouest, cave de 6 m² en sous-sol",
        "neuf": False,
        "adresse": {
            "texte": "Quartier Champ de Mars II, Toulon (83000) — adresse exacte non communiquée par l'agence",
            "ville": "Toulon",
            "code_postal": "83000",
            "quartier": "Champ de Mars",
        },
        "surfaces": {
            "texte": "63 m² loi Carrez annoncés, 89 m² au sol, véranda fermée 11 m², balcon 12 m², cave 6 m²",
        },
        "lots": {
            "count": 1,
            "nature": "1 appartement avec chambre mansardée en duplex au dernier niveau de l'immeuble — "
                      "le rattachement de cette chambre au lot principal n'est pas établi",
            "lots_distincts": None,
        },
        "copro": {
            "charges_annuelles_euros": 1176.0,
            "charges_source": "1 176 €/an annoncés par l'agence (SeLoger, 18,7 €/m²/an) — budget prévisionnel à exiger",
        },
        "travaux": {
            "montant_euros": 0.0,
            "nature": "Aucun travaux annoncé, l'ensemble est présenté comme refait à neuf — estimation du vendeur, "
                      "sans devis, sans facture, sans date",
        },
    },
    "annonce": {
        "plateforme": "seloger",
        "url": "https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/toulon-83000/26SXIFKHH1R3",
        "prix_affiche_euros": PRIX,
        "prix_retenu_euros": PRIX,
        "prix_statut": "affiche",
        "vendeur": "ISABELLE ROVIRA — DR HOUSE IMMO (entreprise individuelle, RSAC Toulon 480539923) — "
                   "honoraires à la charge du vendeur, prix ramené de 160 000 € à 140 000 €",
    },
    "marche": {
        "valeur": {
            "basse_euros": 132000.0,
            "haute_euros": 165000.0,
            "retenue_euros": 150000.0,
            "source": "DVF 2024-2025, Toulon (83137) : appartements 4 pièces, médiane 2 458 €/m² (n = 1 053) ; "
                      "tranche 60-80 m², médiane 2 448 €/m² (n = 1 542). Valeur retenue 2 380 €/m² pour un "
                      "3 pièces de 63 m² Carrez en étage élevé avec ascenseur, véranda, balcon et cave, "
                      "soit 150 000 €.",
            "confiance": "moyenne",
        },
        "loyers": [
            {
                "lot": "Appartement loué nu — locataire en place depuis septembre 2020",
                "quantite": 1,
                "loyer_mensuel_euros": 800.0,
                "occupe": True,
                "note": "Loyer encaissé 800 € hors charges (830 € charges comprises), bail 3/6/9 du 15/09/2020 : "
                        "seule assiette réelle, elle alimente l'EBE, les plafonds et le cash-flow. Relevés de "
                        "location à Toulon pour la surface : 58 m² à 900 €/mois (Champ de Mars), 63 m² à 840 € "
                        "charges comprises, T4 de 67 m² à 1 020 €, moyenne communale FNAIM 12,02 €/m² (soit 757 € "
                        "pour 63 m²). Le loyer en place est dans le marché : le potentiel du dossier est en "
                        "colocation, pas dans une revalorisation du loyer nu.",
            },
        ],
        "notes": "Deux assiettes, et une seule compte aujourd'hui. Ce qui rentre : 800 € hors charges par mois, "
                 "bail en place, locataire depuis septembre 2020. Ce qui est visé : 3 chambres meublées à 450 €, "
                 "soit 1 350 €/mois, médiane du relevé de colocation toulonnais du 28/09/2026 (masse principale "
                 "420 à 520 € charges comprises par chambre ; Champ de Mars 480 € pour une chambre de 11 m², "
                 "chambre mansardée à décoter). Cette cible ne rentre dans aucun calcul de prix : elle suppose le "
                 "départ du locataire. "
                 "Le bail porte par ailleurs 30 €/mois de provisions sur charges quand la copropriété coûte "
                 "98 €/mois : le bailleur porte la différence (68 €/mois, 816 €/an) hors taxe foncière.",
    },
    "hypotheses": {
        "vacance_base_pct": 5.0,
        "vacance_best_pct": 2.0,
        "vacance_worst_pct": 15.0,
        "taux_placement_reserve_pct": 2.84,
        "quote_part_bati_pct": 90.0,
        "vacance_justification": "Bien vendu occupé : aucune vacance en cours, mais rotation à prévoir. 5 % en base, "
                                 "15 % en worst (un appartement de 1935 sans parking se reloue lentement hors rentrée).",
        "charges": {
            "charges_copro_annuelles_euros": 1176.0,
            "charges_copro_commentaire": "1 176 €/an annoncés (18,7 €/m²/an, dans le barème d'attente pour un "
                                         "immeuble de 1935 avec ascenseur) — budget prévisionnel et trois derniers "
                                         "appels de fonds à exiger",
            "taxe_fonciere_annuelle_euros": 1050.0,
            "taxe_fonciere_commentaire": "1 050 €/an estimés (taux global de Toulon 49,76 % en 2025) — avis de "
                                         "taxe foncière à exiger, c'est la seule base fiable",
            "entretien_annuel_euros": 400.0,
            "entretien_commentaire": "400 €/an estimés : entretien courant et petits travaux de bailleur. La "
                                     "provision travaux du moteur (2,5 % des loyers) s'y ajoute.",
            "pno_annuelle_euros": 130.0,
            "comptabilite_annuelle_euros": 0.0,
        },
        "frais_acquisition_euros": FRAIS,
        "frais_acquisition_commentaire": "8 % du prix, estimation du portail (11 200 €) ; honoraires à la charge du vendeur",
    },
    "analyse": {
        "branche": "residentiel",
        "type_operation": "locatif",
        "strategie_retenue": {
            "nom": "Portage du bail en place, bascule en colocation à l'échéance du bail",
            "code": "colocation",
            "lots": 1,
        },
        "strategies_explorees": [
            {
                "strategie": "Portage du bail en place — location nue, locataire depuis septembre 2020",
                "lots": 1,
                "performance": "3,90 % net après IS sur le prix de revient, pour un plancher de branche de 5 % : "
                               "le bien ne couvre pas son coût de détention au prix affiché",
                "valeur_sortie": "Valeur vénale retenue 150 000 € pour un prix de revient de 151 200 € : "
                                 "aucune marge de sortie à court terme",
                "faisabilite": "Immédiate, sans travaux ni relocation : le loyer rentre dès la signature",
                "risque": "faible — le risque est celui du locataire en place, de son impayé éventuel et de "
                          "l'état du logement à la sortie",
            },
            {
                "strategie": "Colocation meublée à trois chambres, après le départ du locataire",
                "lots": 3,
                "performance": "5,98 % net après IS avec la cible de 1 350 €/mois, au-dessus du plancher — c'est la "
                               "seule thèse qui fait vivre le dossier",
                "valeur_sortie": "Un 3 pièces aménagé en colocation se revend au prix du logement nu à Toulon : "
                                 "la valeur créée est dans le revenu, pas dans la revente",
                "faisabilite": "Verrouillée par le bail jusqu'à la prochaine échéance triennale : aucune reprise "
                               "n'est possible avant 2029, puis ameublement à provisionner",
                "risque": "élevé sur l'horizon — trois chambres à relouer, une chambre mansardée à décoter, et "
                          "un locataire en place dont la sortie n'est pas maîtrisée",
            },
            {
                "strategie": "Location nue au marché après départ du locataire",
                "lots": 1,
                "performance": "4,2 % net après IS sur la base d'un loyer de relocation à 850 €/mois : la "
                               "revalorisation du loyer nu ne suffit pas à atteindre le plancher",
                "valeur_sortie": "Valeur vénale inchangée, le bien n'ayant pas changé",
                "faisabilite": "Même verrou que la colocation : il faut attendre la sortie du locataire",
                "risque": "modéré — un loyer de 850 € pour 63 m² se défend, mais il reste dans le marché "
                          "et ne crée aucun effet de levier",
            },
        ],
        "attractivite": [
            {
                "dimension": "transports",
                "score": 8,
                "justification": "Six arrêts de bus dans un rayon de 200 m (Amigas 40 m, Bir Hakeim 100 m, "
                                 "Av. François Cuzin 100 m, Champ de Mars 150 m, Poste la Rode 200 m, Pie X 200 m) "
                                 "et accès rapide aux axes du centre.",
            },
            {
                "dimension": "commerces",
                "score": 8,
                "justification": "Quartier Champ de Mars, à la lisière du centre-ville : commerces, marché, "
                                 "services et santé à pied.",
            },
            {
                "dimension": "ecoles",
                "score": 8,
                "justification": "École maternelle Claude Debussy à 100 m, collège Peiresc à 700 m, et secteur "
                                 "étudiant toulonnais (droit, Chalucet, paramédical) à quelques minutes : c'est "
                                 "ce qui fonde la thèse colocation.",
            },
            {
                "dimension": "securite",
                "score": 6,
                "justification": "Centre dense, bâti hétérogène et copropriété de 1935 : cadre de vie correct "
                                 "mais sans marque de standing, la valeur du quartier se joue rue par rue.",
            },
            {
                "dimension": "demande_locative",
                "score": 8,
                "justification": "Le logement est déjà loué et le loyer en place est au niveau du marché au mètre "
                                 "carré : la demande existe, elle est constatée et non espérée. L'offre de "
                                 "colocation toulonnaise reste abondante (66 à 183 annonces selon les portails).",
            },
            {
                "dimension": "dynamisme",
                "score": 7,
                "justification": "Toulon, préfecture du Var, métropole Toulon Provence Méditerranée : marché "
                                 "profond (5 095 ventes d'appartements en 24 mois), liquide à la revente.",
            },
        ],
        "risques": [
            {
                "facteur": "Bail reconduit : aucune reprise possible avant 2029",
                "detail": "Bail 3/6/9 du 15 septembre 2020, dernière échéance triennale passée le 15 septembre 2026 : "
                          "le bail court désormais jusqu'au 14 septembre 2029. La colocation, seule thèse rentable "
                          "du dossier, est donc hors d'atteinte pendant trois ans, et aucune reprise pour habiter "
                          "n'est ouverte à l'acquéreur. Tout le dossier repose sur le comportement d'un locataire "
                          "dont on ne connaît ni l'historique de paiement ni son projet.",
                "severite": 5,
            },
            {
                "facteur": "Écart au plancher de rendement au prix affiché",
                "detail": "Le loyer encaissé de 800 €/mois donne 3,90 % net après IS sur le prix de revient, pour un "
                          "plancher de branche de 5 % : le dossier ne s'autofinance pas et ne couvre pas son coût de "
                          "détention tel qu'affiché.",
                "severite": 4,
            },
            {
                "facteur": "Statut de la chambre mansardée non établi",
                "detail": "La troisième chambre est un ancien grenier mansardé au 9e niveau. Trois inconnues : est-ce "
                          "un lot de copropriété rattaché à l'appartement ou un lot distinct ? Quelle est sa surface "
                          "Carrez réelle ? Quelle est la hauteur sous plafond (au-dessous de 1,80 m, elle ne se loue "
                          "pas en colocation) ? Si cette chambre tombe, la cible de 1 350 €/mois tombe avec elle.",
                "severite": 4,
            },
            {
                "facteur": "Provisions sur charges du bail très en dessous du coût réel",
                "detail": "Le bail porte 830 € charges comprises, soit 30 €/mois de provisions, quand la copropriété "
                          "coûte 98 €/mois : 68 €/mois restent au bailleur (816 €/an) avant taxe foncière. Une "
                          "régularisation annuelle peut aussi se heurter à un locataire en place depuis 2020.",
                "severite": 3,
            },
            {
                "facteur": "Copropriété de 1935, 9 étages avec ascenseur",
                "detail": "À 90 ans, l'immeuble porte les postes que l'annonce tait : façade, toiture, colonnes, "
                          "électricité des communs, ascenseur en fin de vie. Le budget prévisionnel et les trois "
                          "derniers appels de fonds ne sont pas communiqués, aucun diagnostic technique global n'est "
                          "annoncé. Un appel de fonds voté efface un à deux ans de loyer.",
                "severite": 3,
            },
            {
                "facteur": "DPE D — facture énergétique à la charge du locataire",
                "detail": "DPE D (180 kWh/m²/an) et GES B, chauffage individuel, menuiseries PVC double vitrage : "
                          "aucune échéance d'interdiction de location, mais une facture annoncée entre 1 090 et "
                          "1 510 €/an qui pèsera sur la relocation d'un appartement du 8e étage.",
                "severite": 2,
            },
            {
                "facteur": "« Refait à neuf » sans pièce",
                "detail": "L'annonce présente le logement comme entièrement rénové, sans devis, sans facture et sans "
                          "date. Sur un immeuble de 1935, les postes qui ne se voient pas sur les photos sont "
                          "l'électricité, la plomberie et l'étanchéité de la véranda : trois postes qui coûtent "
                          "chacun plusieurs milliers d'euros.",
                "severite": 3,
            },
        ],
    },
}


def maj_scenarios():
    """Les trois scénarios, calculés depuis le record par le moteur."""
    out = []
    for nom, loyer, vac, travaux, entretien in [
        ("base", 800.0, 5.0, 0.0, 400.0),
        ("best", 1350.0, 2.0, 8000.0, 2200.0),
        ("worst", 800.0, 15.0, 0.0, 900.0),
    ]:
        r = copy.deepcopy(RECORD)
        r["bien"]["travaux"]["montant_euros"] = travaux
        r["hypotheses"]["charges"]["entretien_annuel_euros"] = entretien
        r["hypotheses"]["vacance_base_pct"] = vac
        r["marche"]["loyers"] = [{
            "lot": nom, "quantite": 1, "loyer_mensuel_euros": loyer, "occupe": True, "note": nom,
        }]
        c = engine.compute(r)
        n, v, comp = scoring.note_et_verdict(r, c)
        out.append((nom, loyer, vac, c, n, v))
    return out


def main():
    ecrire = "--ecrire" in sys.argv
    print("validation du record :", schema.validate_record(RECORD) or "aucune erreur")
    c = engine.compute(RECORD)
    n, v, comp = scoring.note_et_verdict(RECORD, c)
    plafond, plafond_detail = scoring.prix_plafond(RECORD)
    cible = scoring.prix_cible(RECORD)
    print(f"\nrevenus bruts {c['revenus_bruts_annuels']:.0f} €/an | revient {c['prix_revient_total']:.0f} € "
          f"| ratio coût/valeur {c['ratio_cout_valeur']:.3f}")
    f, rd = c["fiscal"], c["rendements"]
    print(f"EBE {f['ebe']:.0f} € | amortissement {f['amortissement']:.0f} € | IS {f['is_annuel']:.0f} € "
          f"| net après IS {f['net_apres_is']:.0f} €/an ({f['net_apres_is']/12:.0f} €/mois)")
    print(f"net sur revient {rd['net_sur_revient_pct']:.2f} % | net sur valeur {rd['net_sur_valeur_pct']:.2f} % "
          f"| net sur achat {rd['net_sur_achat_pct']:.2f} %")
    print(f"NOTE {n} — {v} | plafond {plafond:.0f} € | cible {cible:.0f} € | annuité {PRIX*ANNUITE:.0f} €/mois "
          f"| solde {f['net_apres_is']/12 - PRIX*ANNUITE:+.0f} €/mois")
    print(f"autofinancement {(f['net_apres_is']/12)/ANNUITE:.0f} € | repère 100 mois {800*100:.0f} €")
    print("\nscénarios :")
    for nom, loyer, vac, cs, ns, vs in maj_scenarios():
        ff, rr = cs["fiscal"], cs["rendements"]
        print(f"  {nom:<6} loyer {loyer:>6.0f} € vac {vac:>4.1f} % | revient {cs['prix_revient_total']:>8.0f} € "
              f"| EBE {ff['ebe']:>7.0f} € | net IS {ff['net_apres_is']:>7.0f} € | net/rev {rr['net_sur_revient_pct']:>5.2f} % "
              f"| note {ns} {vs}")
    if not ecrire:
        print("\n(base non modifiée — relancer avec --ecrire pour saisir)")
        return
    data = json.loads(BASE.read_text(encoding="utf-8"))
    avant = len(data["analyses"])
    data["analyses"] = [a for a in data["analyses"] if a["slug"] != SLUG]
    data["analyses"].append(RECORD)
    BASE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nanalyses.json : {avant} -> {len(data['analyses'])} dossiers (slug {SLUG})")


if __name__ == "__main__":
    main()
