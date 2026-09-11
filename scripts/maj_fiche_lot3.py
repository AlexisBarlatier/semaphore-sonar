#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Met a jour la fiche du lot de 3 logements (2 rue Vincent Allegre) avec les donnees reelles."""
import importlib.util, os, sys

ROOT = '/home/alexis-barlatier/Documents/Semaphore-sonar'
spec = importlib.util.spec_from_file_location("gen", os.path.join(ROOT, 'scripts', 'gen_fiches_2026-09-10.py'))
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

SLUG = "2026-09-10-lot-3-logements-rdc-toulon"

gen.LECTURE[SLUG] = (
    "Trois logements loués 1 400 € par mois charges comprises pour 86,7 m², soit 16,1 €/m² : c'est le rendement d'une colocation, "
    "pas celui d'un T4 nu qui se louerait 1 000 à 1 100 €. Mais trois faits cadrent le dossier. D'abord le prix : la rue Vincent Allègre "
    "cote 2 206 €/m² sur une vente réelle de 2025 (81 m² à 178 650 €), quand le bien est affiché 2 180 €/m² — il n'y a aucune décote d'entrée "
    "à capter. Ensuite le rendement : après charges réelles (900 € de copropriété, 1 900 € de taxe foncière), vacance de 8 % et provision "
    "d'impayés, l'EBE ressort à 804 €/mois et le rendement net à 3,7 % sur le prix de revient, très loin du seuil de 6,5 %. Enfin les travaux : "
    "l'agent annonce un rafraîchissement sans le chiffrer ni le qualifier, et le bien loue en l'état. La durée est la clé du montage — sur 20 ans "
    "le cash flow neutre s'obtient à 132 400 €, sur 18 ans seulement à 122 800 €, et chaque tranche de travaux financée coûte environ 1,1 € de prix. "
    "Prix cible : 130 000 € si le rafraîchissement est différé à la rotation, 98 600 € s'il est financé dès l'acquisition."
)

gen.CONF[SLUG] = dict(
    titre_court="Lot de 3 logements, 2 rue Vincent Allegre, Toulon",
    adresse="2, rue Vincent Allègre, Toulon (83000) - secteur Saint-Roch / Claret, proche du tribunal judiciaire - T4 coupé en trois logements loués séparément (colocation de fait)",
    date_fr="10 septembre 2026",
    source="SeLoger - annonce 26C7IRSUZ172 (agence Illiz) - données de loyer, charges et taxe foncière transmises par l'agent le 10/09/2026",
    url="https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/toulon-83000/26C7IRSUZ172",
    badge="Investissement locatif",
    strategie="Location longue durée - trois logements conservés (colocation de fait)",
    fiscal_note="SCI à l'IS (15 %), amortissement sur 90 % du prix de revient sur 30 ans, provision d'impayés 1 % (pas de GLI)",
    lat="43.1277", lon="5.9245",
    quartier="secteur Saint-Roch / Claret, 2 rue Vincent Allègre, Toulon (83000)",
    intro_attr="Le 2 rue Vincent Allègre se situe dans le quartier Claret, au nord du centre de Toulon : un secteur résidentiel ancien, correctement desservi, sans être un quartier prisé. Le secteur est central : le tribunal judiciaire (place Gabriel Péri) est à quelques centaines de mètres, le centre-ville et ses administrations à pied — un emplacement plus favorable que la moyenne communale ne le suggère. Information décisive pour ce dossier : la rue cote <strong>2 299 €/m²</strong> en moyenne (MeilleursAgents 09/2026, fourchette 1 192-3 020), 2 390 €/m² selon efficity et 2 313 €/m² au n°4. Le bien est affiché à 2 180 €/m² : il est donc <strong>au prix du marché de la rue</strong>, légèrement en dessous même, et non 29 % sous les moyennes toulonnaises comme le laissait croire le calcul initial sur la surface affichée.",
    profil="jeunes actifs et étudiants - trois logements séparés de petite surface, le segment le plus demandé du marché toulonnais",
    concl_attr="Adéquation correcte (7,0/10) : l'emplacement central, la proximité du tribunal et du centre soutiennent la demande locative sur des petites surfaces. Mais l'économie du dossier reste défavorable : le quartier est un emplacement locatif honnête, la rue est dans la moyenne basse de Toulon, et le prix demandé correspond à sa valeur. Le seul moteur possible du rendement est le prix d'achat, pas l'exploitation.",
    intro_strat="Deux lectures testées : la conservation en location (colocation de fait, loyer réel 1 400 €/mois) et la sortie. Le découpage en trois lots est autorisé par l'assemblée générale : la revente à la découpe est donc une option ouverte, la revente en bloc en est une autre.",
    rationale=(
        "La location est retenue, et le loyer réel justifie cette stratégie : 1 400 €/mois charges comprises pour 86,7 m², soit 16,1 €/m², "
        "le rendement d'une colocation. Les trois logements sont loués en 3/6/9 et la taxe foncière est connue (1 900 €/an, soit 22 €/m² — "
        "élevée, à faire confirmer sur l'avis réel). Mais l'exploitation ne peut pas porter le dossier seule : avec les charges réelles, une vacance "
        "de 8 % justifiée par la rotation de trois baux et la provision d'impayés, l'EBE ressort à <strong>804 €/mois</strong> et le rendement net "
        "à <strong>3,7 %</strong> sur le prix de revient au prix affiché. Le seuil de 6,5 % exige un prix d'entrée très inférieur.<br><br>"
        "La durée du crédit est le paramètre décisif, et elle a été chiffrée : sur <strong>20 ans</strong>, le cash flow devient neutre à "
        "<strong>132 400 €</strong> ; sur 18 ans, il faut descendre à 122 800 € ; sur 15 ans, le plafond tombe sous 110 000 €. À 130 000 €, "
        "le dossier dégage +12 €/mois sur 20 ans et −40 €/mois sur 18 ans : <strong>vingt ans n'est pas un confort, c'est la condition du "
        "cash flow neutre</strong>.<br><br>"
        "Reste le poste travaux. L'agent annonce un rafraîchissement nécessaire sans le chiffrer, alors que le bien est loué en l'état : les travaux "
        "ne sont donc pas urgents, et la stratégie retenue est de les différer à la rotation des locataires. Si le rafraîchissement est réalisé et "
        "financé dès l'acquisition, chaque tranche coûte environ 1,1 € de prix d'achat pour rester à cash flow neutre : 20 k€ de travaux ramènent le "
        "prix cible à 110 000 €, 30 k€ à 98 600 €, 45 k€ à 81 700 €. <strong>Qualifier ce poste avant tout engagement est aussi important que "
        "négocier le prix.</strong><br><br>"
        "Le découpage en trois lots, autorisé par l'assemblée générale, reste un levier de sortie documenté : la technique du lot couloir en indivision "
        "préserve les tantièmes généraux et la surface Carrez (37,01 + 24,06 + 25,64 = 86,70 m², aucune perte). Le différentiel de prix au m² entre "
        "petites surfaces et monobloc est confirmé par les ventes réelles (médiane de 3 889 €/m² sous 25 m² contre 2 612 €/m² de 50 à 70 m², soit "
        "+49 %). Mais les baux étant récents, une revente immédiate se ferait louée, avec une décote d'occupation de l'ordre de 15 % qui annule "
        "l'essentiel du gain : c'est un projet à l'échéance des baux, pas une sortie immédiate."
    ),
    identite=[
        ("Adresse", "<strong>2, rue Vincent Allègre, Toulon (83000)</strong> - secteur Saint-Roch / Claret, à quelques centaines de mètres du tribunal judiciaire (place Gabriel Péri). Source : agent, 10/09/2026 ; localisation confirmée par géocodage"),
        ("Composition", "T4 <strong>coupé en trois</strong>, loué comme trois logements séparés (colocation de fait) : T2 de 32,76 m², studio de 19,81 m², studio de 21,39 m² - immeuble de 1925, 6 étages, sans ascenseur, exposition sud, 3 WC séparés, pas de cave, pas de balcon"),
        ("Surfaces", "<strong>86,7 m²</strong> = 73,96 m² de lots + <strong>12,74 m² de couloir en indivision</strong> pour les trois lots. L'écart entre la somme des lots et la surface de l'annonce est donc expliqué"),
        ("Occupation", "Les trois logements sont <strong>loués en 3/6/9</strong> - loyer global réel 1 400 €/mois charges comprises"),
        ("Prix affiché", "189 000 € soit 2 180 €/m² - honoraires à la charge du vendeur"),
        ("Valeur de marché retenue", "180 000 à 210 000 €, retenue <strong>195 000 €</strong> (2 250 €/m² sur 86,7 m²) - rue Vincent Allègre : 2 299 €/m² (MeilleursAgents 09/2026), 2 390 €/m² (efficity), 2 313 €/m² au n°4. <strong>Le bien est au prix du marché de la rue</strong>"),
        ("Loyers réels", "<strong>1 400 €/mois charges comprises pour les trois lots</strong>, dont 120 € de provisions sur charges payées par les locataires (3 × 40 €/lot/mois), soit <strong>1 280 € hors charges</strong>. Le loyer ressort à 16,1 €/m² CC sur 86,7 m² : niveau d'une colocation, très supérieur à un T4 nu (1 000-1 100 €). La répartition entre les trois lots n'a pas été communiquée : elle est reconstituée au prorata des surfaces"),
        ("Travaux", "« Travaux de rénovation à prévoir » selon l'agent, <strong>ni chiffrés ni qualifiés</strong> — alors que le bien est loué en l'état à 1 400 €/mois, donc sans urgence. Enveloppe retenue <strong>45 000 €</strong> (15 k€ par logement) si le rafraîchissement complet est réalisé, à engager à la rotation des locataires. <strong>Qualification à obtenir avant tout engagement</strong> : nature des travaux, logements concernés, devis — l'écart entre 20 k€ et 45 k€ vaut 30 000 € sur le prix"),
        ("Charges annuelles", "Copropriété <strong>900 €/an</strong> (75 €/mois réels pour les trois lots) + taxe foncière <strong>1 900 €/an</strong> (montant réel, soit 22 €/m² — élevée) + PNO 250 € + entretien 500 € + <strong>provision d'impayés 1 %</strong> (~154 €, auto-assurance, pas de GLI) + comptabilité 400 €"),
        ("Fiscalité", "SCI à l'IS : IS 15 % sur le résultat, amortissement de 90 % du prix de revient sur 30 ans. Pas de GLI : provision d'auto-assurance de 1 % du loyer annuel"),
        ("Prix de revient", "<strong>204 120 €</strong> = prix 189 000 € + frais d'acquisition ~15 120 € (8 %), travaux différés — ou <strong>249 120 €</strong> si le rafraîchissement de 45 000 € est réalisé dès l'acquisition"),
    ],
    stance=(
        "<strong>À négocier — 130 000 € sur vingt ans si le rafraîchissement est différé, 98 600 € s'il est financé dès l'acquisition.</strong> "
        "Le produit est bon : trois logements loués 1 400 € par mois pour 86,7 m², soit 16,1 €/m² — le rendement d'une colocation — avec des charges "
        "réelles modérées (75 €/mois de copropriété, 1 900 € de taxe foncière). Mais le prix affiché est au niveau du marché de la rue (2 180 €/m² "
        "contre 2 206 €/m² sur une vente réelle de 2025) : aucune décote d'entrée, et le rendement net plafonne à 3,7 % sur le prix de revient. "
        "Deux conditions font le dossier : <strong>la durée de vingt ans</strong> — sur 18 ans le cash flow neutre exige 122 800 €, pas 132 400 € — "
        "et <strong>la qualification des travaux</strong>, dont chaque tranche financée coûte environ 1,1 € de prix d'achat. À 130 000 € sur 20 ans, "
        "le cash flow est neutre (+12 €/mois) avec 23 400 € d'apport. À 189 000 €, on paie le prix du marché pour un rendement de 3,7 %."
    ),
    prix_plafond="132 400 € sur 20 ans, 122 800 € sur 18 ans (travaux différés à la rotation des locataires). Si le rafraîchissement est financé dès l'acquisition : 110 000 € pour 20 k€ de travaux, 98 600 € pour 30 k€, 81 700 € pour 45 k€. Chaque tranche de travaux financée coûte environ 1,1 € de prix d'achat. En dessous de 120 000 €, le dossier tient dans toutes les hypothèses.",
    leviers=[
        "La durée est le premier levier, et il est chiffré : vingt ans porte le prix neutre à 132 400 € contre 122 800 € sur 18 ans et moins de 110 000 € sur 15 ans. Demander 20 ans n'est pas une commodité de trésorerie, c'est la condition du cash flow neutre — et Rémy a raison de vouloir la garder comme paramètre de la clause de prêt",
        "Les travaux « à prévoir » ne sont ni chiffrés ni qualifiés : les faire préciser (nature, logements concernés, devis) est aussi important que négocier le prix, puisque chaque 10 000 € de travaux financé retire environ 11 000 € au prix d'achat viable. C'est un argument direct : soit ils sont réels et le prix baisse, soit ils ne le sont pas et le vendeur ne peut pas les invoquer",
        "Le bien loue en l'état 1 400 € par mois : les travaux ne sont pas urgents, ce qui autorise à les différer à la rotation des locataires et à préserver le prix. C'est la position la plus défendable, et elle laisse la main sur le calendrier",
        "La taxe foncière de 1 900 €/an pour 86,7 m² est élevée : 22 €/m², contre une moyenne toulonnaise plus proche de 15-18 €/m². À faire confirmer sur l'avis réel et à intégrer à part entière — un écart de 400 €/an fait basculer le verdict",
        "Trois baux en 3/6/9 : demander les échéances réelles. Une rotation simultanée représenterait plusieurs mois de vacance cumulée sur un bien dont le rendement repose sur l'occupation complète",
        "Le découpage en trois lots est autorisé par l'AG et le différentiel petites surfaces / monobloc est confirmé par les ventes réelles (+49 %). Mais il ne se monétise qu'à l'échéance des baux : vendu loué, la décote d'occupation annule le gain. C'est un levier de sortie à trois ans, pas un argument de négociation immédiat",
    ],
    meta=[
        "<strong>Régime fiscal retenu :</strong> SCI à l'IS (15 %) — amortissement sur 90 % du prix de revient sur 30 ans — provision d'impayés 1 % du loyer annuel (auto-assurance, pas de GLI)",
        "<strong>Frais d'acquisition estimés :</strong> ~15 120 € (8 % du prix affiché)",
        "<strong>Durée de financement de référence : 20 ans.</strong> Sur 18 ans, le cash flow neutre exige 122 800 € et non 132 400 € ; sur 15 ans, le plafond tombe sous 110 000 €",
        "<strong>Enveloppe travaux :</strong> 45 000 € si le rafraîchissement complet est réalisé (15 k€ par logement), à différer à la rotation des locataires. Chaque tranche financée coûte environ 1,1 € de prix d'achat",
        "<strong>Contrôle à faire avant toute offre :</strong> qualification et devis du rafraîchissement (nature, logements, montant), échéances des trois baux, avis de taxe foncière de 1 900 €, PV d'AG et budget de copropriété, surfaces Carrez par lot et acte de division (couloir indivis), état technique du rez-de-chaussée",
    ],
)

gen.main()
