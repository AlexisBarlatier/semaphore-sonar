#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche Cuers — ensemble atypique deux niveaux, 115 m2, 199 000 EUR.

Saisit l'entree dans analyses.json puis genere la fiche HTML avec les chiffres du moteur.
"""
import copy, importlib.util, json, os, sys

ROOT = '/home/alexis-barlatier/Documents/Semaphore-sonar'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from analyse_app import schema, engine

BASE = os.path.join(ROOT, 'analyses', 'analyses.json')
SLUG = "2026-09-21-maison-cuers-les-bousquets"
URL = ("https://www.seloger.com/annonces/achat/maison/cuers-83/"
       "les-rayols-saint-lazare-les-bousquets/259991513.htm")

RECORD = {
    "slug": SLUG,
    "date_analyse": "2026-09-21",
    "date_maj": None,
    "titre": "Cuers — ensemble atypique deux niveaux (115 m²), 199 000 €",
    "bien": {
        "type_bien": "maison",
        "sous_type": None,
        "type_detail": (
            "Ensemble atypique dans une copropriété de 4 lots, à l'entrée de Cuers, au calme d'une impasse. "
            "Deux niveaux de vie : au premier, une entrée desservant une pièce pouvant servir de chambre ou de bureau, "
            "un salon, deux chambres et une salle d'eau avec WC ; un escalier intérieur mène à une vaste remise. "
            "Au niveau supérieur, accessible par les parties communes, un second espace de vie complet avec salon, "
            "salle à manger, cuisine et salle d'eau avec WC. Des combles aménageables complètent l'ensemble. "
            "115 m² annoncés au total, 5 pièces, 3 chambres. « Des travaux de rénovation sont à prévoir » selon "
            "l'annonce, sans montant. Les photographies montrent des intérieurs habitables mais d'états inégaux : "
            "un séjour refait (parquet chevron, murs blancs) dont l'image porte la mention « photographie retouchée », "
            "une salle à manger rustique en tomettes de terre cuite avec poutre apparente, et une chambre carrelée "
            "avec fenêtre à petits bois et persiennes. Aucun DPE n'est publié : l'agence le déclare « non soumis »."
        ),
        "neuf": False,
        "adresse": {
            "texte": "Cuers (83390), quartier Les Rayols - Saint Lazare - Les Bousquets, à l'entrée de la commune — adresse exacte non communiquée",
            "ville": "Cuers",
            "code_postal": "83390"
        },
        "surfaces": {
            "texte": ("115 m² annoncés pour l'ensemble, sans ventilation par niveau ni surface Carrez : la part "
                      "habitable, celle de la remise et celle des combles ne sont pas distinguées"),
            "carrez_m2": 115.0
        },
        "lots": {
            "count": 2,
            "surface_par_lot_m2": None,
            "nature": ("Deux espaces de vie indépendants sur deux niveaux, chacun avec ses sanitaires, reliés par "
                       "l'escalier intérieur et par les parties communes"),
            "lots_distincts": 2
        },
        "copro": {
            "charges_annuelles_euros": 700.0,
            "charges_source": (
                "Copropriété de 4 lots, tous d'habitation, sans procédure en cours (annonce SeLoger et fiche Laforêt). "
                "Aucun montant de charges n'est communiqué. Provision retenue 700 €/an pour le ou les lots vendus, sur "
                "la base d'une copropriété de quatre lots avec parties communes et cage d'escalier : à CONFIRMER sur "
                "le budget prévisionnel et les appels de fonds. La copropriété existe : c'est une charge certaine, "
                "à la différence d'une monopropriété"
            )
        },
        "travaux": {
            "montant_euros": 35000.0,
            "nature": (
                "« Des travaux de rénovation sont à prévoir » (annonce), non chiffrés, sans devis ni diagnostic "
                "technique. Provision retenue 35 000 €, soit environ 300 €/m², pour remettre l'ensemble en état de "
                "location sur deux logements : reprise de l'électricité, chauffage ou production d'eau chaude, "
                "peintures et sols, cuisine à créer au premier niveau, salles d'eau à moderniser. Fourchette 20 000 à "
                "60 000 € selon la profondeur. À ajouter si le DPE s'avère F ou G : 25 000 à 40 000 € de rénovation "
                "énergétique, avec interdiction de louer dès 2028 pour un F et depuis 2025 pour un G. L'aménagement "
                "des combles, qui est le vrai levier de valorisation, est un chantier distinct à chiffrer à part"
            )
        }
    },
    "annonce": {
        "plateforme": "seloger",
        "url": URL,
        "prix_affiche_euros": 199000.0,
        "prix_retenu_euros": None,
        "prix_statut": "affiche",
        "prix_commentaire": (
            "199 000 €, honoraires à la charge du vendeur, soit 1 730 €/m² sur les 115 m² annoncés. Le chiffre "
            "paraît spectaculairement bas : la moyenne communale des maisons ressort à 3 477 €/m² (MeilleursAgents "
            "01/09/2026) et 3 576 €/m² en moyenne DVF 2025. Mais cette moyenne est tirée par les petites surfaces et "
            "les villas récentes. La transaction réellement comparable, une maison de 115 m² et 4 pièces vendue "
            "le 19 décembre 2025, s'est traitée à 182 000 €, soit 1 583 €/m². À 1 730 €/m², le bien est donc AU "
            "NIVEAU du marché de sa catégorie, pas 50 % en dessous. C'est le premier point que l'annonce fait "
            "mal lire, et il change tout le raisonnement"
        )
    },
    "marche": {
        "valeur": {
            "basse_euros": 180000.0,
            "haute_euros": 230000.0,
            "retenue_euros": 200000.0,
            "source": (
                "Comparaison directe d'abord, c'est la seule méthode solide ici : 115 m² à 1 583 €/m² en décembre "
                "2025 (Rue Raoul Dufy, même surface), 127 m² à 1 941 €/m² (Rue de Verdun), 71 m² à 2 746 €/m² "
                "(Le Village). Le prix au m² décroît fortement avec la surface à Cuers : la médiane communale, "
                "autour de 3 600 €/m², est calculée sur des lots bien plus petits. Pour 115 m² anciens avec travaux, "
                "la fourchette pertinente est 1 600 à 2 000 €/m², soit 180 000 à 230 000 €. Valeur retenue "
                "200 000 € (1 739 €/m²). À ce niveau, le prix affiché est donc exactement à la valeur : ni décote, "
                "ni prime. Le seul élément qui pourrait justifier une valeur supérieure est l'aménagement des "
                "combles, dont la surface n'est pas communiquée : chaque m² aménagé coûte de l'ordre de 1 000 à "
                "1 400 € et vaut 1 700 à 2 000 € au m², mais c'est un chantier à financer et à autoriser"
            ),
            "confiance": "moyenne"
        },
        "loyers": [
            {"lot": "Logement inférieur (entrée, salon, deux chambres, bureau, salle d'eau)", "quantite": 1,
             "loyer_mensuel_euros": 850.0, "occupe": False,
             "note": ("Le bien est vendu libre, aucun loyer n'est encaissé aujourd'hui : ces loyers sont des loyers "
                      "retenus, pas des loyers en place. 850 € pour un logement de type T3/T4 d'un niveau, sur la base "
                      "des maisons relouées à Cuers (1 180 € pour 90 m², 1 250 € CC pour 85 m², 1 050 € pour 76 m²). "
                      "Attention : le premier niveau n'a pas de cuisine décrite, il faut en créer une pour le louer "
                      "en logement autonome")},
            {"lot": "Logement supérieur (salon, salle à manger, cuisine, salle d'eau)", "quantite": 1,
             "loyer_mensuel_euros": 600.0, "occupe": False,
             "note": ("600 € pour un T2/T3 complet, dont le loyer au m² est mécaniquement plus élevé que celui d'une "
                      "maison entière (14,7 €/m² de moyenne communale pour les appartements). Ce niveau a sa propre "
                      "cuisine et ses sanitaires, et son accès se fait par les parties communes : la division en deux "
                      "logements est structurellement possible, c'est l'argument de vente de l'annonce")}
        ],
        "notes": (
            "Aucun loyer en place : le vendeur ne loue pas, ou vend libre. Les loyers retenus totalisent "
            "1 450 €/mois, soit 17 400 €/an et 8,7 % brut sur le prix affiché, 12,6 €/m² sur les 115 m² annoncés. "
            "Le point critique est que ce total suppose DEUX logements loués séparément : en un seul bail, le marché "
            "local d'une maison de village de ce type ressort plutôt autour de 1 250 à 1 300 €/mois, soit 8 à 12 % "
            "de moins. Toute la rentabilité du dossier tient donc à la faisabilité de la division, et elle dépend de "
            "trois inconnues : la création d'une cuisine au premier niveau, l'accord que le règlement de copropriété "
            "donne à deux locations distinctes, et l'autorisation d'urbanisme si des travaux modifient les accès. "
            "Faute de l'une des trois, le dossier retombe sur le scénario pessimiste"
        )
    },
    "hypotheses": {
        "vacance_base_pct": 6.0,
        "vacance_best_pct": 3.0,
        "vacance_worst_pct": 12.0,
        "vacance_justification": (
            "Taux un peu au-dessus du défaut résidentiel (5 %) parce qu'il s'agit d'une maison et non d'un immeuble "
            "de rapport : le marché de la location de maisons à Cuers est étroit (136 ventes de maisons par an, mais "
            "peu d'annonces locatives de cette taille), et un logement qui se libère met plus longtemps à retrouver "
            "preneur qu'un T2. La vacance pessimiste à 12 % correspond au basculement en un seul bail, avec un "
            "changement de locataire par an sur un parc d'un seul logement"
        ),
        "frais_acquisition_euros": 15920.0,
        "frais_divers_euros": 0.0,
        "charges": {
            "taxe_fonciere_annuelle_euros": 1400.0,
            "taxe_fonciere_commentaire": (
                "ESTIMATION 1 400 €/an, la taxe n'est pas communiquée. Cuers pratique un taux de taxe foncière sur "
                "le bâti de 53,63 % en 2025 (plus 12,29 % de TEOM), en hausse de 1,9 point depuis 2021 : c'est l'un "
                "des taux les plus élevés du Var. Le calcul part d'une valeur locative cadastrale de l'ordre de "
                "2 600 € pour 115 m² anciens, ce qui reste à confirmer sur l'avis réel. Fourchette 1 200 à 1 900 €/an "
                "selon la valeur locative : chaque 500 € d'écart vaut 42 €/mois de cash flow"
            ),
            "charges_copro_annuelles_euros": 700.0,
            "charges_copro_commentaire": (
                "Copropriété de 4 lots, aucun montant communiqué, aucun procès-verbal d'assemblée, aucun budget "
                "prévisionnel. Provision 700 €/an pour quatre lots anciens avec parties communes et cage d'escalier, "
                "à confirmer. C'est une charge certaine puisqu'il y a bien une copropriété, contrairement au dossier "
                "de Solliès-Pont : elle est à vérifier avant toute offre, en même temps que les travaux votés et les "
                "appels de fonds à venir"
            ),
            "pno_annuelle_euros": 450.0,
            "pno_commentaire": "Assurance du logement, à ajuster si deux locations distinctes.",
            "entretien_annuel_euros": 900.0,
            "entretien_commentaire": (
                "Entretien d'une maison ancienne de village : couverture, façade, évacuations, menuiseries. "
                "Pas de jardin mentionné, donc pas de charge d'extérieur"
            ),
            "comptabilite_annuelle_euros": 0.0,
            "comptabilite_commentaire": "Aucune ligne de comptabilité : le poste est mutualisé sur la SCI existante (convention du groupe)."
        }
    },
    "analyse": {
        "branche": "residentiel",
        "type_operation": "locatif",
        "strategie_retenue": {
            "nom": "Location nue sur deux logements indépendants, après remise en état",
            "code": "ld-nue",
            "lots": 2
        },
        "strategies_explorees": [
            {"strategie": "Location nue sur deux logements indépendants", "lots": 2,
             "rendement": "4,7 % net sur le prix de revient (9,3 % brut sur le prix affiché)",
             "faisabilite": "immédiate après 35 000 € de travaux, dont une cuisine à créer au premier niveau",
             "risque": "moyen — structurellement possible (deux sanitaires, deux accès), mais dépend du règlement de copropriété et du budget travaux"},
            {"strategie": "Location nue en un seul bail familial", "lots": 1,
             "rendement": "3,7 % net sur le prix de revient (1 250 à 1 300 €/mois, soit 8 à 12 % de moins)",
             "faisabilite": "immédiate, sans travaux de division",
             "risque": "faible sur l'exécution, mais c'est le scénario qui ne couvre plus l'échéance bancaire"},
            {"strategie": "Aménagement des combles puis location d'un troisième logement", "lots": 3,
             "rendement": "loyer supplémentaire de 600 à 700 €/mois pour 1 000 à 1 400 €/m² de travaux",
             "faisabilite": "2 à 3 ans, permis ou déclaration préalable selon la nature des travaux",
             "risque": "élevé — surface des combles non communiquée, hauteur sous plafond, structure et accès à vérifier, et accord de la copropriété nécessaire"},
            {"strategie": "Revente après rénovation complète", "lots": 2,
             "rendement": "création de valeur de l'ordre de 15 à 25 % si travaux maîtrisés, à condition d'acheter autour de 155 000 €",
             "faisabilite": "12 à 24 mois avec un artisan suivi",
             "risque": "élevé — le prix au m² de revente pour 115 m² anciens à Cuers est établi à 1 583-1 941 €/m², la marge se joue donc entièrement sur le prix d'achat et sur le coût réel des travaux"}
        ],
        "attractivite": [
            {"dimension": "transports", "score": 7,
             "justification": "Cuers dispose de sa <strong>gare TER (Cuers-Pierrefeu)</strong> sur la ligne de Toulon, avec des trajets directs de 20 à 30 minutes, et se situe à 17 km de Toulon par l'A57, soit une vingtaine de minutes. Pour un village de 9 000 à 10 000 habitants, c'est une desserte solide, qui alimente la demande des actifs travaillant dans l'agglomération toulonnaise."},
            {"dimension": "commerces", "score": 7,
             "justification": "La commune compte un noyau commercial actif : commerces de proximité, restaurants, hypermarché et marchés (plus de 200 commerces recensés par l'agence). Cuers joue le rôle de bourg-centre pour la vallée du Gapeau et la plaine des Maures."},
            {"dimension": "ecoles", "score": 7,
             "justification": "Une dizaine d'établissements et structures d'accueil, avec collège sur la commune et lycées à Toulon, La Garde ou La Farlède. Le profil attendu du locataire de ce bien est justement une famille, ou deux foyers distincts sur le même ensemble."},
            {"dimension": "securite", "score": 7,
             "justification": "Commune résidentielle de 65 % de propriétaires, sans quartier prioritaire, avec un bâti de village et des lotissements récents. L'annonce situe le bien dans une impasse à l'entrée de la commune : c'est un argument de calme réel, à l'écart des axes."},
            {"dimension": "demande_locative", "score": 6,
             "justification": "Le marché de la vente est liquide (136 ventes de maisons et 120 d'appartements en un an) mais celui de la location de maisons est étroit : les annonces de maisons se comptent en dizaines et les loyers constatés vont de 1 050 € (76 m²) à 1 250 € CC (85 m²), avec un point haut à 1 940 € CC (93 m²). C'est un marché de deux foyers modestes, pas de cadres."},
            {"dimension": "dynamisme", "score": 6,
             "justification": "Économie résidentielle et agricole adossée à l'emploi toulonnais, avec un solde démographique positif. Mais les prix des maisons reculent de 3,4 % sur un an et la construction neuve est à l'arrêt (1 logement autorisé en 2026, contre 536 depuis 2021) : marché stable, sans tension, ce qui protège la revente mais limite la plus-value."}
        ],
        "risques": [
            {"facteur": "Aucun DPE publié, annonce et agence le déclarent « non soumis »", "severite": 3,
             "detail": "Le DPE est obligatoire pour toute vente d'un logement, et son absence dans l'annonce comme sa mention « non soumis » sur le site de l'agence sont anormales. C'est l'information la plus lourde du dossier : à Cuers, 3 % des logements diagnostiqués sont des passoires F ou G, mais la classe C y est la plus représentée et la construction médiane date de 1976, sur un bâti dont l'ancienneté n'est pas connue ici. Si le bien sort en F, la location devient interdite à compter de 2028 et il faut 25 000 à 40 000 € de rénovation énergétique : cela suffit à annuler la totalité de la marge. À exiger avant toute offre, avec la facture énergétique par logement."},
            {"facteur": "Prix au m² illusoire : le bien est à sa valeur, pas en dessous", "severite": 3,
             "detail": "L'annonce s'affiche à 1 730 €/m² quand la moyenne communale des maisons est de 3 477 €/m² (MeilleursAgents) et la moyenne DVF 2025 de 3 576 €/m². La comparaison est trompeuse : le prix au m² s'effondre avec la surface dans cette commune, et la seule transaction comparable (115 m², quatre pièces, vendue en décembre 2025) s'est traitée à 182 000 €, soit 1 583 €/m². Le prix affiché est donc exactement à la valeur du marché de sa catégorie. Toute la négociation doit se construire là-dessus, et non sur une prétendue décote de 50 %."},
            {"facteur": "Travaux de rénovation annoncés sans le moindre chiffre", "severite": 3,
             "detail": "« Des travaux de rénovation sont à prévoir », sans nature, sans devis, sans diagnostic technique. Les photographies montrent des intérieurs habitables mais datés par endroits (tomettes de terre cuite, carrelage, menuiseries), et l'une d'elles est explicitement retouchée. La fourchette 20 000 à 60 000 € vaut 40 000 € de prix d'achat : c'est la deuxième variable du dossier après le loyer."},
            {"facteur": "Division en deux logements non validée", "severite": 3,
             "detail": "Le total de loyers retenu (1 450 €/mois) suppose deux locations distinctes. Or le premier niveau n'a pas de cuisine décrite (il faut la créer), et l'accès du niveau supérieur se fait par les parties communes : cela signifie que le règlement de copropriété et l'état descriptif de division doivent autoriser cette exploitation, sinon il faut y revenir par une assemblée. En un seul bail, le loyer retombe à 1 250-1 300 €/mois et le cash flow passe sous zéro."},
            {"facteur": "Copropriété de 4 lots : charges, travaux votés et budget inconnus", "severite": 2,
             "detail": "La copropriété existe (4 lots, tous d'habitation, aucune procédure en cours), mais aucun montant de charges, aucun budget prévisionnel, aucun carnet d'entretien, aucun procès-verbal d'assemblée n'est communiqué. Sur un bâti ancien de village, un ravalement, une couverture ou une colonne d'évacuation se votent et se paient en quote-part. C'est le seul poste du dossier dont le montant ne se négocie pas après l'achat."},
            {"facteur": "Surface habitable réelle inconnue", "severite": 2,
             "detail": "115 m² annoncés sans ventilation : ni surface par niveau, ni surface Carrez, ni plan. La part de la remise et celle des combles ne sont pas distinguées. Si l'habitable réel n'est que de 85 à 95 m², le loyer au m² des deux logements devient nettement supérieur à ce que le marché local paie, et la valeur de revente au m² se recalcule à la hausse sur une surface plus faible."},
            {"facteur": "Taxe foncière inconnue dans une commune au taux parmi les plus élevés du Var", "severite": 3,
             "detail": "Aucune taxe foncière n'est communiquée. Cuers applique un taux communal sur le bâti de 53,63 % en 2025, en hausse de 1,9 point depuis 2021, et 12,29 % de TEOM. Sur 115 m² anciens, la fourchette réaliste va de 1 200 à 1 900 €/an, soit jusqu'à 11 % des loyers bruts. Chaque 500 € d'écart vaut 42 €/mois de cash flow : c'est la première pièce à obtenir."},
            {"facteur": "Marché du locatif familial étroit pour un loyer de 1 450 €/mois", "severite": 2,
             "detail": "Les maisons relouées à Cuers se situent entre 1 050 € (76 m²) et 1 250 € CC (85 m²), avec un point haut isolé à 1 940 € CC. Un ensemble à 1 450 €/mois en deux logements doit trouver deux preneurs plutôt qu'un seul, ce qui double la vacance possible et exige des logements complets : cuisines, sanitaires, chauffage, à des niveaux de finition cohérents avec ces loyers."},
            {"facteur": "Combles aménageables : le levier, mais aussi l'inconnue", "severite": 2,
             "detail": "L'annonce met en avant des combles aménageables, sans en donner la surface ni les contraintes. Hauteur sous plafond, structure, charpente, trémies et accès déterminent si le chantier coûte 800 ou 1 600 €/m² créé. C'est un vrai potentiel de valorisation (un troisième logement à 600-700 €/mois), mais il est interdit de l'intégrer au prix d'offre avant d'avoir vu les lieux et chiffré le chantier."},
            {"facteur": "Annonce dont une photographie est retouchée", "severite": 1,
             "detail": "L'image du séjour porte la mention « photographie retouchée » : le rendu annoncé n'est pas l'état réel de la pièce. Ni la nature ni l'ampleur de la retouche ne sont précisées. Ce n'est pas un vice, mais cela impose de vérifier l'état réel de chaque pièce en visite, et de ne fonder aucun chiffrage sur les photographies."}
        ]
    },
    "champs_manquants": []
}


def main():
    data = json.load(open(BASE))
    data['analyses'] = [r for r in data['analyses'] if r['slug'] != SLUG]
    RECORD['champs_manquants'] = schema.champs_manquants(RECORD)
    errs = schema.validate_record(RECORD)
    if errs:
        raise SystemExit(f"fiche invalide : {errs}")
    data['analyses'].append(RECORD)
    data['meta']['count'] = len(data['analyses'])
    json.dump(data, open(BASE, 'w'), ensure_ascii=False, indent=2)
    print(f"record ajoute : {SLUG} | total {data['meta']['count']} fiches")

    spec = importlib.util.spec_from_file_location("gen", os.path.join(ROOT, 'scripts', 'gen_fiches_2026-09-10.py'))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)

    def eur(v):
        return f"{v:,.0f}".replace(',', ' ')

    def fr(v, dec=1):
        return f"{v:.{dec}f}".replace('.', ',')

    def ligne(label, val, cls=""):
        c = f' class="{cls}"' if cls else ''
        return f'            <tr{c}><td>{label}</td><td class="num">{val}</td></tr>'

    def scenario_html(rec, vac, loyers=None):
        v = copy.deepcopy(rec)
        v['hypotheses']['vacance_base_pct'] = vac
        if loyers:
            for l, m in zip(v['marche']['loyers'], loyers):
                l['loyer_mensuel_euros'] = m
        r = engine.compute(v)
        f = r['fiscal']
        rev = r['revenus_bruts_annuels']
        ch = rec['hypotheses']['charges']
        prov = round(rev * 0.025, 2)
        vac_eur = round(rev * vac / 100.0, 2)
        cf_reint = (f['ebe'] - f['is_annuel'] + f['amortissement']) / 12.0
        rows = [
            ligne("Revenu brut annuel (deux loyers retenus)", f"{eur(rev)} €"),
            ligne(f"Vacance locative ({vac:.0f} %)", f"-{eur(vac_eur)} €"),
            ligne("Taxe foncière (estimée — à vérifier)", f"-{eur(ch['taxe_fonciere_annuelle_euros'])} €"),
            ligne("Charges de copropriété (4 lots — à vérifier)", f"-{eur(ch['charges_copro_annuelles_euros'])} €"),
            ligne("Entretien de la maison", f"-{eur(ch['entretien_annuel_euros'])} €"),
            ligne("Assurance PNO", f"-{eur(ch['pno_annuelle_euros'])} €"),
            ligne("Provision travaux 2,5 % (règle interne)", f"-{eur(prov)} €"),
            ligne("EBE avant IS", f"{eur(f['ebe'])} €", "subtotal"),
            ligne("Amortissement du bâti (90 % du revient / 30 ans)", f"{eur(f['amortissement'])} €"),
            ligne("Résultat fiscal", f"{eur(f['resultat_fiscal'])} €"),
            ligne("IS (15 %)", f"-{eur(f['is_annuel'])} €"),
            ligne("CF net mensuel après IS", f"{eur(f['cf_mensuel_net'])} €", "highlight"),
            ligne("CF amort. réintégré (mensuel)", f"{eur(cf_reint)} €"),
            ligne("Rendement net sur prix de revient", f"{fr(r['rendements']['net_sur_revient_pct'])} %"),
            ligne("Rendement net sur valeur de marché", f"{fr(r['rendements']['net_sur_valeur_pct'])} %"),
        ]
        return r, "\n".join(rows)

    def bloc_scenarios(rec, titre, intro, loyers_base=None):
        rb, rows_b = scenario_html(rec, rec['hypotheses']['vacance_base_pct'])
        ro, rows_o = scenario_html(rec, rec['hypotheses']['vacance_best_pct'], loyers=[1000.0, 700.0])
        rp, rows_p = scenario_html(rec, rec['hypotheses']['vacance_worst_pct'], loyers=[700.0, 500.0])
        rd = lambda r: fr(r['rendements']['net_sur_revient_pct'])
        rv = lambda r: fr(r['rendements']['net_sur_valeur_pct'])
        cf = lambda r: eur(r['fiscal']['cf_mensuel_net'])
        ci = lambda r: eur((r['fiscal']['ebe'] - r['fiscal']['is_annuel'] + r['fiscal']['amortissement']) / 12)
        return f"""  <section class="financial-projections">
    <h2>Projections financières — prix affiché {eur(rec['annonce']['prix_affiche_euros'])} €, SCI à l'IS</h2>
    <p class="attractiveness-intro">{intro}</p>
    <div class="projections-grid">
      <div class="projection-card scenario-base">
        <h3>Scénario Base</h3>
        <p class="scenario-subtitle">Vacance {rec['hypotheses']['vacance_base_pct']:.0f} % — deux logements loués séparément (850 € + 600 €), 35 000 € de travaux</p>
        <table class="projection-table"><tbody>
{rows_b}
        </tbody></table>
      </div>
      <div class="projection-card scenario-optimiste">
        <h3>Scénario Optimiste</h3>
        <p class="scenario-subtitle">Vacance {rec['hypotheses']['vacance_best_pct']:.0f} % — deux logements à 1 000 € et 700 € après travaux complets</p>
        <table class="projection-table"><tbody>
{rows_o}
        </tbody></table>
      </div>
      <div class="projection-card scenario-pessimiste">
        <h3>Scénario Pessimiste</h3>
        <p class="scenario-subtitle">Vacance {rec['hypotheses']['vacance_worst_pct']:.0f} % — un seul bail familial réalisable, 1 200 €/mois</p>
        <table class="projection-table"><tbody>
{rows_p}
        </tbody></table>
      </div>
    </div>
    <table class="projection-table compare">
      <thead><tr><th>Indicateur</th><th class="num">Base</th><th class="num">Optimiste</th><th class="num">Pessimiste</th></tr></thead>
      <tbody>
        <tr><td>Revenu brut annuel</td><td class="num">{eur(rb['revenus_bruts_annuels'])} €</td><td class="num">{eur(ro['revenus_bruts_annuels'])} €</td><td class="num">{eur(rp['revenus_bruts_annuels'])} €</td></tr>
        <tr><td>EBE avant IS</td><td class="num">{eur(rb['fiscal']['ebe'])} €</td><td class="num">{eur(ro['fiscal']['ebe'])} €</td><td class="num">{eur(rp['fiscal']['ebe'])} €</td></tr>
        <tr><td>CF net mensuel après IS</td><td class="num">{cf(rb)} €</td><td class="num">{cf(ro)} €</td><td class="num">{cf(rp)} €</td></tr>
        <tr><td>CF amort. réintégré (mensuel)</td><td class="num">{ci(rb)} €</td><td class="num">{ci(ro)} €</td><td class="num">{ci(rp)} €</td></tr>
        <tr><td>Rendement net (prix de revient)</td><td class="num">{rd(rb)} %</td><td class="num">{rd(ro)} %</td><td class="num">{rd(rp)} %</td></tr>
        <tr><td>Rendement net (valeur de marché)</td><td class="num">{rv(rb)} %</td><td class="num">{rv(ro)} %</td><td class="num">{rv(rp)} %</td></tr>
        <tr><td>Ratio coût / valeur</td><td class="num">{fr(rb['ratio_cout_valeur'], 2)}</td><td class="num">{fr(ro['ratio_cout_valeur'], 2)}</td><td class="num">{fr(rp['ratio_cout_valeur'], 2)}</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix"><p class="attractiveness-intro">{gen.LECTURE[rec['slug']]}</p></div>
    <p class="attractiveness-intro"><strong>Sensibilité du prix</strong> — frais d'acquisition 8 %, valeur de marché retenue 200 000 €.
    Prix où l'opération crée de la valeur (ratio coût/valeur de 1,00) : <strong>152 800 €</strong> avec 35 000 € de travaux, 166 700 € avec 20 000 €, 129 600 € avec 50 000 €.
    Prix où le bien couvre son échéance bancaire (apport de 10 %, crédit sur 20 ans) : <strong>185 000 €</strong> environ au loyer de base, <strong>216 000 €</strong> si les deux logements se louent aux loyers hauts, <strong>150 000 €</strong> en un seul bail familial.
    À 199 000 €, le prix de revient de 249 920 € dépasse la valeur de 25 % et le cash flow ne couvre pas la mensualité. Toute offre doit être conditionnée à l'avis de taxe foncière, au DPE, aux surfaces et au règlement de copropriété.</p>
  </section>"""

    gen.bloc_scenarios = bloc_scenarios

    gen.LECTURE[SLUG] = (
        "Le dossier le plus trompeur des quatre : il s'affiche à 1 730 €/m² quand la commune affiche 3 477 €/m² "
        "pour les maisons, et il faut dix minutes pour comprendre que la comparaison ne vaut rien. Le prix au m² "
        "s'effondre avec la surface à Cuers, et la transaction comparable (115 m², quatre pièces, décembre 2025) "
        "s'est traitée à 1 583 €/m². Autrement dit, à 199 000 €, l'ensemble est exactement à sa valeur, ni décote "
        "ni prime. Le reste du dossier est un vrai potentiel et une vraie facture : deux niveaux de vie déjà "
        "indépendants, chacun avec ses sanitaires, dont l'un complet avec cuisine, et l'accès du niveau supérieur "
        "par les parties communes qui rend la division en deux logements crédible. C'est ce qui justifie un loyer "
        "total de 1 450 €/mois et 8,7 % brut. Mais il y a 35 000 € de remise en état non chiffrée, une taxe "
        "foncière inconnue dans une commune au taux de 53,63 %, une copropriété dont on ne connaît ni les charges "
        "ni les travaux votés, et surtout aucun DPE : l'agence le déclare « non soumis », ce qui est anormal pour "
        "une vente. Avec 35 000 € de travaux, le prix de revient atteint 249 920 € pour 200 000 € de valeur. "
        "Autrement dit, acheter à ce prix détruit de la valeur, et seule une négociation franche rétablit "
        "l'opération."
    )

    gen.CONF = {SLUG: dict(
        titre_court="Ensemble deux niveaux, Cuers (83390)",
        adresse="Cuers (83390), quartier Les Rayols - Saint Lazare - Les Bousquets — ensemble de 115 m² sur deux niveaux, dans une copropriété de 4 lots",
        date_fr="21 septembre 2026",
        source="SeLoger — annonce 259991513 (Laforêt Cuers, EK Conseil — Olivier Kircher, réf. agence 2318)",
        url=URL,
        badge="Investissement locatif",
        strategie="Location nue sur deux logements indépendants, après remise en état",
        fiscal_note="SCI à l'IS (15 %), amortissement sur 90 % du prix de revient sur 30 ans",
        lat="43.2375", lon="6.0677",
        quartier="Cuers (83390), vallée du Gapeau et plaine des Maures — 17 km de Toulon, gare TER sur la commune",
        intro_attr=(
            "Cuers est une commune de 9 000 à 10 000 habitants à 17 km de Toulon, desservie par sa "
            "<strong>gare TER (Cuers-Pierrefeu)</strong> qui met l'agglomération à 20 à 30 minutes, et adossée à "
            "l'emploi toulonnais. Le marché de la vente y est liquide (136 ventes de maisons et 120 d'appartements "
            "sur un an), l'immobilier résidentiel y est majoritaire (69 % de maisons, 65 % de propriétaires) et la "
            "construction neuve est à l'arrêt : 1 logement autorisé en 2026 contre 536 depuis 2021. C'est un marché "
            "stable, sans fièvre, où les maisons se traitent autour de <strong>3 577 €/m² en moyenne DVF</strong> "
            "et 3 477 €/m² selon MeilleursAgents. Attention toutefois : cette moyenne porte sur des surfaces bien "
            "plus petites. Pour 115 m², le prix au m² réel tombe à <strong>1 583 à 1 941 €/m²</strong>."
        ),
        profil="deux foyers modestes ou une famille avec un espace indépendant : actifs de la vallée du Gapeau travaillant à Toulon, La Garde ou Hyères, sensibles au trajet ferroviaire de 20 minutes et au calme d'une impasse, avec un budget de 600 à 900 € par logement",
        concl_attr=(
            "Adéquation correcte (6,6/10). Le trio de base est là : une commune qui tient son marché, une gare TER "
            "à 20 minutes de Toulon, et un bien qui offre deux espaces de vie déjà indépendants, donc deux loyers "
            "possibles sur un même achat. Mais le dossier porte une anomalie qu'aucun des trois autres n'avait : "
            "<strong>aucun DPE publié</strong>, l'agence le déclare « non soumis », ce qui est contraire à "
            "l'obligation de diagnostic à la vente. Ajoutez une taxe foncière inconnue sur une commune au taux de "
            "53,63 %, une copropriété de quatre lots dont on ne connaît ni les charges ni les travaux votés, et "
            "35 000 € de travaux annoncés sans un seul devis. Ce n'est pas un dossier de marché, c'est un dossier "
            "de pièces à réunir avant de parler prix."
        ),
        intro_strat=(
            "Quatre lectures ont été testées : la location nue sur deux logements indépendants, la location en un "
            "seul bail familial, l'aménagement des combles pour créer un troisième logement, et la revente après "
            "rénovation. La première est retenue, parce que la configuration du bien la rend structurellement "
            "possible : chaque niveau a ses sanitaires et l'accès du niveau supérieur se fait par les parties "
            "communes."
        ),
        rationale=(
            "La configuration vend le dossier. Deux espaces de vie déjà constitués, chacun avec sa salle d'eau et "
            "ses WC, et un niveau supérieur complet avec cuisine : la location séparée n'est pas un projet, c'est "
            "l'état du bien, à une cuisine près au premier niveau. C'est ce qui permet de retenir "
            "<strong>1 450 €/mois</strong> (850 € + 600 €), soit 17 400 €/an et <strong>8,7 % brut</strong> sur le "
            "prix affiché, pour un rendement net de 4,7 % sur le prix de revient.<br><br>"
            "Mais trois constats empêchent d'acheter à ce prix. D'abord <strong>le prix au m² ne veut rien dire</strong> : "
            "1 730 €/m² contre 3 477 €/m² de moyenne communale ressemble à une aubaine, et n'en est pas une. Le prix "
            "au m² décroît très fortement avec la surface à Cuers, et la transaction réellement comparable, une "
            "maison de 115 m² et quatre pièces vendue en décembre 2025, s'est traitée à 182 000 €, soit "
            "1 583 €/m². La valeur retenue ici, <strong>200 000 €</strong>, place donc l'annonce exactement à sa "
            "valeur.<br><br>"
            "Ensuite <strong>les travaux sont annoncés sans un chiffre</strong>. Il faut 35 000 € pour remettre "
            "l'ensemble en état de location sur deux logements, et la fourchette va de 20 000 à 60 000 €. Avec "
            "35 000 €, le prix de revient atteint 249 920 €, soit <strong>25 % au-dessus de la valeur</strong> : "
            "l'opération détruit de la valeur au prix demandé. Le seuil où elle en crée est à "
            "<strong>152 800 €</strong>.<br><br>"
            "Enfin <strong>le DPE manque</strong>, et c'est le risque qui peut annuler tout le reste. Le vendeur et "
            "l'agence le déclarent « non soumis » : à la vente, c'est anormal. Si le bien sort en F ou en G, la "
            "location devient interdite en 2028 pour un F (déjà depuis 2025 pour un G) et il faut 25 000 à 40 000 € "
            "de rénovation énergétique. Ce seul poste vaut plus que toute la marge du dossier.<br><br>"
            "Reste l'option à instruire, et elle est sérieuse : les <strong>combles aménageables</strong>. Un "
            "troisième logement, soit 600 à 700 €/mois de loyer supplémentaire, pour un coût de 1 000 à 1 400 €/m² "
            "créé contre une valeur de 1 700 à 2 000 €/m². C'est le vrai levier de valorisation du bien. Mais ni "
            "la surface ni la faisabilité ne sont documentées : à intégrer au prix d'offre après visite, jamais "
            "avant."
        ),
        identite=[
            ("Adresse", "Cuers (83390), quartier Les Rayols - Saint Lazare - Les Bousquets, à l'entrée de la commune, dans une impasse — adresse exacte non communiquée"),
            ("Vendeur / intermédiaire", "Laforêt Cuers, EK Conseil (1 place Pasteur, 83390 Cuers, RCS 899934822) — Olivier Kircher. Références : SeLoger 264ZZ9GP6QGJ, agence 2318, Laforêt 52466432"),
            ("Composition", "Ensemble sur <strong>deux niveaux</strong> : au premier, entrée, une pièce (chambre ou bureau), salon, deux chambres, salle d'eau avec WC, plus une <strong>vaste remise</strong> par escalier intérieur ; au niveau supérieur, accessible par les parties communes, salon, salle à manger, cuisine, salle d'eau avec WC. <strong>Combles aménageables</strong>"),
            ("Statut", "<strong>Copropriété de 4 lots, tous d'habitation</strong>, aucune procédure en cours (annonce et fiche agence). Charges, budget prévisionnel, carnet d'entretien et travaux votés <strong>non communiqués</strong>"),
            ("Surfaces", "<strong>115 m² annoncés</strong>, 5 pièces, 3 chambres — <strong>aucune ventilation par niveau, aucune surface Carrez, aucun plan</strong>. La part habitable, celle de la remise et celle des combles ne sont pas distinguées"),
            ("DPE / GES", "<strong>Aucun DPE publié.</strong> L'annonce invite à le demander à l'agence, et le site de l'agence indique « DPE NON SOUMIS ». C'est anormal pour une vente. Aucune facture énergétique communiquée"),
            ("Prix affiché", "<strong>199 000 €</strong>, honoraires à la charge du vendeur, soit <strong>1 730 €/m²</strong> sur les 115 m² annoncés"),
            ("Valeur de marché retenue", "180 000 à 230 000 €, retenue <strong>200 000 €</strong> (1 739 €/m²) : comparables DVF de décembre 2025 à 1 583 €/m² (115 m²) et 1 941 €/m² (127 m²). <strong>Le prix affiché est exactement à la valeur</strong>, contrairement à ce que suggère la moyenne communale de 3 477 €/m² des maisons"),
            ("Loyers retenus", "<strong>1 450 €/mois</strong> (850 € + 600 €) = 17 400 €/an = <strong>8,7 % brut</strong> sur le prix affiché, soit 12,6 €/m². Aucun loyer en place : le bien est vendu libre. En un seul bail, compter 1 250 à 1 300 €/mois"),
            ("Travaux", "<strong>35 000 € provisionnés</strong> (≈ 300 €/m²), fourchette 20 000 à 60 000 € : électricité, chauffage ou eau chaude, peintures et sols, cuisine à créer au premier niveau, salles d'eau. Plus 25 000 à 40 000 € si le DPE s'avère F ou G"),
            ("Taxe foncière", "<strong>Estimée 1 400 €/an</strong> — non communiquée. Taux communal sur le bâti de <strong>53,63 %</strong> en 2025 (+1,9 point depuis 2021), plus 12,29 % de TEOM : l'un des plus élevés du Var. Fourchette 1 200 à 1 900 €/an"),
            ("Charges annuelles", "Taxe foncière estimée 1 400 € + charges de copropriété 700 € + entretien 900 € + assurance 450 € + provision travaux 2,5 % = <strong>3 885 €/an</strong> hors vacance"),
            ("Fiscalité", "SCI à l'IS : IS 15 % sur le résultat, amortissement de 90 % du prix de revient sur 30 ans"),
            ("Prix de revient à l'affichage", "<strong>249 920 €</strong> = prix 199 000 € + frais d'acquisition 15 920 € (8 %) + travaux 35 000 €"),
        ],
        stance=(
            "<strong>On négocie, et bas : offre 160 000 €, plafond 170 000 €. Au-delà, on passe.</strong> "
            "Le dossier a de vrais atouts : deux espaces de vie déjà indépendants avec deux loyers possibles, "
            "8,7 % brut sur le prix affiché, des combles aménageables comme réserve de valorisation, et une "
            "commune qui tient son marché avec une gare TER à 20 minutes de Toulon. Mais rien de tout cela ne "
            "justifie le prix demandé.<br><br>"
            "<strong>Trois chiffres commandent la décision.</strong> À 199 000 € avec 35 000 € de travaux, le prix "
            "de revient de 249 920 € dépasse la valeur retenue de 25 %, et le ratio coût/valeur de 1,25 signifie "
            "qu'on achète plus cher que ce que le bien vaut. Le seuil où l'opération crée de la valeur est à "
            "<strong>152 800 €</strong>, celui où le bien couvre encore sa mensualité bancaire autour de "
            "<strong>185 000 €</strong>. Et à l'annonce, l'écart entre 199 000 € et ce seuil de couverture est de "
            "14 000 € : c'est précisément la marge de négociation à prendre.<br><br>"
            "<strong>Le grand argument de l'annonce est faux, et c'est une bonne nouvelle pour la négociation.</strong> "
            "Afficher 1 730 €/m² quand la commune est à 3 477 €/m² fait croire à 50 % de décote. Or la transaction "
            "comparable, une maison de 115 m² vendue en décembre 2025, s'est traitée à 1 583 €/m² : le bien est à "
            "sa valeur. Personne ne brade, et il n'y a donc aucune raison de payer le prix demandé pour un bien "
            "dont les travaux ne sont pas chiffrés.<br><br>"
            "<strong>Quatre pièces à obtenir avant d'écrire quoi que ce soit</strong> : le DPE et la facture "
            "énergétique par logement (le risque qui peut annuler la marge), l'avis de taxe foncière réel (chaque "
            "500 € d'écart vaut 42 €/mois), un devis de remise en état par corps d'état, et le règlement de "
            "copropriété avec le budget prévisionnel et les travaux votés, pour vérifier que deux locations "
            "distinctes sont bien autorisées. Une visite avec un artisan est indispensable, et l'aménagement des "
            "combles se chiffre après, pas avant."
        ),
        prix_plafond=(
            "<strong>170 000 €</strong> net vendeur avec 35 000 € de travaux. Repères chiffrés : "
            "<strong>152 800 €</strong> pour que le prix de revient égale la valeur de marché (166 700 € avec "
            "20 000 € de travaux, 129 600 € avec 50 000 €), et <strong>185 000 €</strong> pour que le bien couvre "
            "encore son échéance bancaire au loyer de base, avec 10 % d'apport et un crédit sur 20 ans. "
            "À 199 000 €, le ratio coût/valeur est de 1,25 et le cash flow est négatif avant même l'imprévu. "
            "Si le DPE sort en F ou en G, retirer 25 000 à 40 000 € de la capacité de prix, soit un plafond "
            "ramené autour de 135 000 € : dans ce cas, le dossier ne se fait pas. "
            "Inversement, si la division en deux logements est confirmée par le règlement de copropriété et si "
            "l'artisan chiffre les travaux sous 25 000 €, le plafond monte à 186 000 €."
        ),
        leviers=[
            "Le prétexte de la décote doit être démonté avant de négocier : 1 730 €/m² contre 3 477 €/m² de moyenne communale laisse croire à 50 % sous le marché, alors que la transaction comparable (115 m², décembre 2025) est à 1 583 €/m². Le bien est à sa valeur ; le vendeur n'a donc aucun avantage à défendre et aucune raison d'ignorer une offre argumentée",
            "Exiger le DPE avant tout : l'absence de diagnostic publié à la vente est anormale, et un classement F ou G vaut 25 000 à 40 000 € de travaux avec interdiction de louer à horizon 2028. C'est le seul poste capable d'annuler la totalité de la marge : il commande le prix",
            "La taxe foncière n'est pas communiquée dans une commune au taux de 53,63 %, en hausse de 1,9 point depuis 2021 : exiger l'avis réel. Chaque 500 € d'écart vaut 42 €/mois de cash flow, soit environ 6 000 € de capacité de prix",
            "Faire chiffrer la rénovation par corps d'état (électricité, chauffage, eau chaude, cuisine, salles d'eau, peintures) avant de proposer un prix : la fourchette 20 000 à 60 000 € vaut 40 000 € de prix d'achat, soit 20 % du montant affiché",
            "Vérifier dans le règlement de copropriété que deux locations distinctes sont autorisées, et obtenir le budget prévisionnel, le carnet d'entretien et les travaux votés : sur un bâti ancien de village, une couverture ou une colonne d'évacuation se paient en quote-part et ne se négocient plus après l'achat",
            "Exiger la surface habitable réelle par niveau et les plans : les 115 m² annoncés mêlent logements, remise et combles. Si l'habitable tombe à 90 m², les loyers retenus sont hors marché et la valeur de revente se recalcule sur une surface plus faible",
            "Chiffrer l'aménagement des combles séparément, avec un artisan, après visite : c'est le vrai levier de valorisation du bien (un troisième logement à 600-700 €/mois pour 1 000 à 1 400 €/m² créé, contre une valeur de 1 700 à 2 000 €/m²), mais rien ne doit en entrer dans l'offre avant d'avoir vu la charpente et l'accès",
            "Prévoir la visite avec un artisan dès maintenant, et pas après l'accord sur le prix : sur ce dossier, l'état réel est la seule inconnue que l'annonce ne documente pas du tout, et l'une des photographies est explicitement retouchée",
        ],
        meta=[
            "<strong>Régime fiscal retenu :</strong> SCI à l'IS (15 %) — amortissement sur 90 % du prix de revient sur 30 ans — provision travaux de 2,5 % des revenus (règle interne)",
            "<strong>Frais d'acquisition :</strong> 15 920 € (8 % du prix affiché, barème de l'ancien)",
            "<strong>Enveloppe travaux :</strong> 35 000 € provisionnés (≈ 300 €/m²), fourchette 20 000 à 60 000 €. Aucun devis, aucun diagnostic technique. À ajouter si DPE F ou G : 25 000 à 40 000 €",
            "<strong>Loyers :</strong> aucun loyer en place, le bien est vendu libre. Les 1 450 €/mois sont des loyers retenus sur comparables locaux (1 050 € pour 76 m², 1 180 € pour 90 m², 1 250 € CC pour 85 m², point haut à 1 940 € CC pour 93 m²) et supposent deux logements loués séparément",
            "<strong>Contrôles à faire avant toute offre :</strong> DPE et facture énergétique par logement ; avis de taxe foncière réel (taux bâti communal de 53,63 %) ; surfaces et plans par niveau ; devis de remise en état par corps d'état ; règlement de copropriété, budget prévisionnel, travaux votés et procès-verbaux d'assemblée ; diagnostics techniques (électricité, gaz, amiante, plomb, termites) ; état de la charpente et de la couverture ; surface et hauteur des combles",
            "<strong>Option de sortie à instruire :</strong> l'aménagement des combles pour créer un troisième logement, ou la revente après rénovation complète. Les deux supposent d'acheter autour de 155 000 € et de maîtriser le coût réel des travaux : ce sont des décisions de seconde étape, après la visite",
            "<strong>Points de méthode :</strong> le prix d'offre se cale sur les loyers retenus, jamais sur le potentiel des combles non chiffré. Le marché local du locatif familial est étroit : le risque de vacance d'un ensemble à 1 450 €/mois est double de celui d'un T2",
            "<strong>Rappel de marché (sources au 21/09/2026) :</strong> MeilleursAgents Cuers 3 477 €/m² pour les maisons (1 743 à 5 588) et 3 576 €/m² en moyenne DVF 2025 ; loyers 15,0 €/m²/mois pour les maisons et 14,7 €/m²/mois pour les appartements ; transactions DVF comparables : 115 m² à 1 583 €/m² (décembre 2025), 127 m² à 1 941 €/m², 71 m² à 2 746 €/m² ; taxe foncière bâtie 53,63 % et TEOM 12,29 % ; 3 % de passoires thermiques, classe C majoritaire, année médiane de construction 1976 ; 136 ventes de maisons et 120 d'appartements sur un an",
        ],
    )}

    gen.main()

    # Le generateur partage code la classe de verdict 'nego' : c'est le verdict retenu ici.
    chemin = os.path.join(ROOT, 'analyses', SLUG, 'index.html')
    html = open(chemin, encoding='utf-8').read()
    n = html.count('<section class="verdict nego">')
    print(f'verdict nego : {n} occurrence(s)')
    if n == 0:
        html = html.replace('<section class="verdict buy">', '<section class="verdict nego">')
        open(chemin, 'w', encoding='utf-8').write(html)
        print('classe nego appliquee')


if __name__ == '__main__':
    main()
