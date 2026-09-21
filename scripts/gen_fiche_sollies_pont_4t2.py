#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche Sollies-Pont — immeuble de rapport 4 T2 loues, 160 m2, 262 000 EUR.

Saisit l'entree dans analyses.json puis genere la fiche HTML avec les chiffres du moteur.
"""
import copy, importlib.util, json, os, sys

ROOT = '/home/alexis-barlatier/Documents/Semaphore-sonar'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from analyse_app import schema, engine

BASE = os.path.join(ROOT, 'analyses', 'analyses.json')
SLUG = "2026-09-20-immeuble-rapport-4-t2-sollies-pont"
URL = ("https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/"
       "sollies-pont-83210/262WZHWZ28Z8")

RECORD = {
    "slug": SLUG,
    "date_analyse": "2026-09-20",
    "date_maj": None,
    "titre": "Solliès-Pont — immeuble de rapport 4 T2 loués (160 m²), 262 000 €",
    "bien": {
        "type_bien": "immeuble",
        "sous_type": None,
        "type_detail": (
            "Immeuble de rapport de 1900 en R+3, un appartement par palier, quatre T2 loués pour un revenu annoncé de "
            "2 000 €/mois. 160 m² annoncés (aucune surface Carrez par lot, aucun plan). DPE D / GES B, facture "
            "énergétique annoncée entre 3 030 et 4 130 €/an. « Rafraîchissement à prévoir » selon l'annonce. "
            "Les photographies montrent deux logements d'états différents : l'un avec cuisine américaine refaite, "
            "comptoir-bar, menuiseries PVC double vitrage et carrelage récent — un convecteur électrique ancien sous la "
            "fenêtre ; l'autre avec tomettes hexagonales d'origine, menuiseries bois simple vitrage, câblage apparent et "
            "mobilier ancien. Aucune charge de copropriété, aucune taxe foncière, aucun bail et aucun diagnostic "
            "technique ne sont communiqués : le dossier est mince."
        ),
        "neuf": False,
        "adresse": {
            "texte": "Solliès-Pont (83210) — adresse exacte non communiquée. Emprise déclarée dans le village, à proximité de la gare",
            "ville": "Solliès-Pont",
            "code_postal": "83210"
        },
        "surfaces": {
            "texte": ("160 m² annoncés pour l'immeuble, soit 40 m² par T2 en moyenne — aucune surface Carrez par lot, "
                      "aucun plan communiqué"),
            "carrez_m2": 160.0
        },
        "lots": {
            "count": 4,
            "surface_par_lot_m2": None,
            "nature": "4 T2, un par palier, sur 4 niveaux (R+3) — sans ascenseur",
            "lots_distincts": 4
        },
        "copro": {
            "charges_annuelles_euros": 0.0,
            "charges_source": (
                "Aucune copropriété, aucun syndic et aucune charge ne sont mentionnés : immeuble présumé en MONOPROPRIÉTÉ, "
                "donc sans charges de copropriété. Avec quatre lots et un appartement par palier, c'est la configuration "
                "la plus probable. À CONFIRMER : si l'immeuble est en copropriété, compter 1 800 à 2 800 €/an de charges, "
                "ce qui amputerait directement le cash flow."
            )
        },
        "travaux": {
            "montant_euros": 30000.0,
            "nature": (
                "« Rafraîchissement à prévoir » (annonce), non chiffré. Provision retenue 30 000 €, soit environ 187 €/m², "
                "à engager à la ROTATION des locataires et non à l'acquisition : les quatre appartements sont loués, il n'y "
                "a donc aucune urgence. Les photographies justifient l'enveloppe : dans le logement le plus daté, "
                "menuiseries bois simple vitrage, câblage apparent, tomettes usées et convecteurs anciens. "
                "Fourchette 20 000 à 60 000 € selon la profondeur (simple peinture et sols contre reprise des réseaux et "
                "des menuiseries). À provisionner séparément : la rénovation énergétique, sans contrainte réglementaire "
                "avant 2034 puisque le bien est en DPE D."
            )
        }
    },
    "annonce": {
        "plateforme": "seloger",
        "url": URL,
        "prix_affiche_euros": 262000.0,
        "prix_retenu_euros": None,
        "prix_statut": "affiche",
        "prix_commentaire": (
            "262 000 €, honoraires à la charge du vendeur, soit 1 638 €/m² sur les 160 m² annoncés. "
            "C'est 43 % sous le prix/m² moyen des appartements de la commune (2 852 €/m², MeilleursAgents 01/09/2026) "
            "et 44 % sous la moyenne DVF 2025 des appartements (3 654 €/m² sur 88 ventes). Même en appliquant une décote "
            "de bloc de 30 %, le prix affiché reste sous la valeur. C'est le premier des trois dossiers du week-end à être "
            "affiché sous sa valeur."
        )
    },
    "marche": {
        "valeur": {
            "basse_euros": 285000.0,
            "haute_euros": 350000.0,
            "retenue_euros": 315000.0,
            "source": (
                "Deux méthodes convergent vers le haut. (1) Capitalisation : les 24 000 € de loyers annuels, après 5 % de "
                "vacance, 3 000 € de taxe foncière estimée, entretien, assurance et provision travaux, laissent 17 250 € de "
                "revenu net avant impôt — soit un rendement brut de marché de 7,5 à 8 % pour un immeuble de rapport de "
                "quatre lots, ce qui vaut 300 000 à 320 000 €. (2) Comparaison : les appartements de Solliès-Pont se "
                "traitent à 2 852 €/m² (MeilleursAgents), 2 950 €/m² en médiane DVF et 3 654 €/m² en moyenne 2025 sur "
                "88 ventes ; les 160 m² valorisés à 2 852 €/m² donnent 456 000 € en vente à l'unité, soit environ 320 000 € "
                "après une décote de bloc de 30 %. Valeur retenue 315 000 € (1 969 €/m²), fourchette 285 000 à 350 000 €. "
                "Le prix affiché (1 638 €/m²) est donc 17 % SOUS la valeur retenue."
            ),
            "confiance": "moyenne"
        },
        "loyers": [
            {"lot": "T2 n° 1", "quantite": 1, "loyer_mensuel_euros": 500.0, "occupe": True,
             "note": "Répartition par lot non communiquée : l'annonce donne un total de 2 000 €/mois pour quatre T2, soit 500 € en moyenne. Bail en cours."},
            {"lot": "T2 n° 2", "quantite": 1, "loyer_mensuel_euros": 500.0, "occupe": True,
             "note": "Idem — 500 €/mois en moyenne. 12,5 €/m² sur les 160 m² annoncés, contre 15,3 €/m² de moyenne communale : c'est 18 % sous le marché, et c'est au moins autant un potentiel qu'un signal d'alerte sur l'état réel des lots."},
            {"lot": "T2 n° 3", "quantite": 1, "loyer_mensuel_euros": 500.0, "occupe": True,
             "note": "Idem. Comparables locatifs relevés le 20/09/2026 à Solliès-Pont : 546 € (27 m²), 659 € CC, 682 € CC, 685 € CC, 730 € (43 m² meublé), 840 € (56 m² meublé avec parking). Un T2 de 40 m² à 500 € est en bas de fourchette."},
            {"lot": "T2 n° 4", "quantite": 1, "loyer_mensuel_euros": 500.0, "occupe": True,
             "note": "Idem. Baux non communiqués : dates, échéances, type et dépôts à obtenir avant toute offre."}
        ],
        "notes": (
            "Loyers en place 2 000 €/mois, soit 24 000 €/an et 9,16 % brut sur le prix affiché — le meilleur rendement "
            "brut des trois dossiers du week-end (7,46 % à Pignans, 5,2 % sur les loyers retenus à Brignoles). "
            "Les quatre logements sont loués : le revenu est acquis au premier jour. Le loyer affiché ressort à "
            "12,5 €/m² sur les 160 m² annoncés, contre 15,3 €/m² de moyenne communale (MeilleursAgents) : il y a donc "
            "un potentiel de revalorisation d'environ 18 % — soit 360 €/mois, 4 320 €/an et une soixantaine de milliers "
            "d'euros de capacité de prix à 8 % — mais il n'est encaissable qu'à la rotation, bail par bail, et il peut "
            "aussi signifier que les lots sont en dessous du marché pour de bonnes raisons (petites surfaces, état). "
            "Le prix d'offre se cale sur les 2 000 € encaissés, jamais sur le potentiel."
        )
    },
    "hypotheses": {
        "vacance_base_pct": 5.0,
        "vacance_best_pct": 2.0,
        "vacance_worst_pct": 12.0,
        "vacance_justification": (
            "Taux par défaut de la branche résidentielle (5 % / 2 % / 12 %) : les quatre logements sont loués et le marché "
            "locatif local est liquide (28 annonces en ligne, 88 ventes d'appartements par an, 12 000 habitants, gare à "
            "12 minutes de Toulon). La vacance worst à 12 % tient compte du turnover d'un immeuble de quatre lots — "
            "quatre baux, donc quatre occasions de vacance — et non d'un marché déprimé."
        ),
        "frais_acquisition_euros": 20960.0,
        "frais_divers_euros": 0.0,
        "charges": {
            "taxe_fonciere_annuelle_euros": 3000.0,
            "taxe_fonciere_commentaire": (
                "ESTIMATION 3 000 €/an — aucune taxe foncière n'est communiquée. Solliès-Pont pratique un taux de taxe "
                "foncière sur le bâti de 49,51 % en 2025, l'un des plus élevés du Var : le poste doit être vérifié sur "
                "l'avis réel avant toute offre. Si la valeur locative cadastrale de l'immeuble est élevée, la taxe peut "
                "atteindre 4 000 à 5 000 €/an, soit jusqu'à 20 % des loyers bruts : ce serait le premier poste de charge."
            ),
            "charges_copro_annuelles_euros": 0.0,
            "charges_copro_commentaire": (
                "Immeuble présumé en monopropriété (aucun syndic, aucune copropriété, aucun appel de fonds mentionné) : "
                "pas de charges de copropriété. À CONFIRMER — si l'immeuble est en copropriété, compter 1 800 à 2 800 €/an."
            ),
            "pno_annuelle_euros": 450.0,
            "pno_commentaire": "Assurance de l'immeuble et de ses quatre logements.",
            "entretien_annuel_euros": 1500.0,
            "entretien_commentaire": (
                "Entretien d'un bâti de 1900 sur quatre niveaux : cage d'escalier, façade, couverture, évacuations. "
                "En monopropriété, le propriétaire porte tout."
            ),
            "comptabilite_annuelle_euros": 0.0,
            "comptabilite_commentaire": "Aucune ligne de comptabilité : le poste est mutualisé sur la SCI existante (convention du groupe)."
        }
    },
    "analyse": {
        "branche": "residentiel",
        "type_operation": "locatif",
        "strategie_retenue": {
            "nom": "Conservation avec les quatre baux en place, rafraîchissement à la rotation",
            "code": "ld-nue",
            "lots": 4
        },
        "strategies_explorees": [
            {"strategie": "Conservation avec les quatre baux en place", "lots": 4,
             "rendement": "5,1 % net sur le revient / 5,1 % sur la valeur",
             "faisabilite": "immédiate — revenus acquis au premier jour, travaux étalés à la rotation",
             "risque": "faible — le prix affiché est 17 % sous la valeur retenue"},
            {"strategie": "Conservation avec revalorisation des loyers à la rotation", "lots": 4,
             "rendement": "5,5 % net sur le revient avec +18 % de loyer",
             "faisabilite": "étalée sur 2 à 4 ans, bail par bail",
             "risque": "moyen — les baux en cours ne se révèlent qu'à l'IRL jusqu'à leur terme"},
            {"strategie": "Revente à la découpe des quatre T2", "lots": 4,
             "rendement": "ROI 19,8 % sur le revient à 2 600 €/m² (62 750 € net d'IS), 28,8 % à 2 852 €/m² (91 478 €)",
             "faisabilite": "état descriptif de division à créer, calendrier commandé par la vacance des quatre baux",
             "risque": "moyen — opération rentable, mais elle échange une rente perpétuelle contre une marge unique et la date de vacance de chaque lot est inconnue"},
            {"strategie": "Location meublée des quatre T2", "lots": 4,
             "rendement": "+10 à 15 % de loyer, charges de gestion en hausse",
             "faisabilite": "immédiate",
             "risque": "moyen — le marché local compte des meublés (annonces à 730 et 840 € pour 43 et 56 m²) mais le turnover et la gestion quadruplent"}
        ],
        "attractivite": [
            {"dimension": "transports", "score": 8,
             "justification": "Double atout rare : Solliès-Pont a sa <strong>gare TER</strong> (trajets directs vers Toulon en une douzaine de minutes, vers Hyères et Carnoules) et se trouve à quelques minutes de l'A57. Beaucoup de communes de la vallée du Gapeau n'ont ni l'un ni l'autre. C'est ce qui alimente la demande locative."},
            {"dimension": "commerces", "score": 7,
             "justification": "Bourg actif de 12 000 habitants avec commerces de proximité, marché, services de santé et administrations ; grande distribution à La Farlède et La Garde à moins de 10 minutes."},
            {"dimension": "ecoles", "score": 7,
             "justification": "Groupes scolaires, collège sur la commune et lycées à Toulon ou La Garde ; la vallée du Gapeau est un secteur familial, ce qui soutient la demande sur des T2 comme sur des maisons."},
            {"dimension": "securite", "score": 7,
             "justification": "Commune résidentielle de la première couronne toulonnaise, sans quartier prioritaire, avec un centre ancien entretenu — la rue photographiée dans l'annonce présente des façades propres et des volets repeints."},
            {"dimension": "demande_locative", "score": 7,
             "justification": "Marché liquide pour une commune de cette taille : 88 ventes d'appartements en 2025, 28 annonces locatives en ligne, 12 000 habitants et la gare à 12 minutes de Toulon. Les T2 se relouent, avec des loyers constatés entre 546 et 840 € CC."},
            {"dimension": "dynamisme", "score": 6,
             "justification": "Économie agricole (plaine des Solliès, cerises) et résidentielle, adossée à l'emploi toulonnais. Prix des appartements en hausse sur dix ans (+28 %) mais repli de 0,6 % sur un an et construction neuve à l'arrêt (1 logement autorisé en 2026) : marché stable, sans fièvre."}
        ],
        "risques": [
            {"facteur": "Rafraîchissement non chiffré — deux logements d'états très différents", "severite": 3,
             "detail": "L'annonce annonce un « rafraîchissement à prévoir », sans montant. Les photographies montrent un logement déjà refait (cuisine américaine, comptoir-bar, menuiseries PVC double vitrage, carrelage récent) et un autre resté dans son jus (tomettes d'origine, menuiseries bois simple vitrage, câblage apparent, convecteurs anciens). Provision retenue 30 000 €, fourchette 20 000 à 60 000 € : l'écart vaut 40 000 € de prix. À engager à la rotation, donc étalé — c'est le point favorable du dossier."},
            {"facteur": "Aucune surface par lot, aucun plan", "severite": 2,
             "detail": "Les 160 m² annoncés n'ont pas de ventilation Carrez : on ne sait pas si les quatre T2 font 30, 40 ou 45 m² chacun. Cela change le loyer au m² réel (12,5 €/m² sur 160 m², mais 16,7 €/m² si la surface habitable n'est que de 120 m²) et la valeur de revente à l'unité. À exiger avant toute offre."},
            {"facteur": "Taxe foncière inconnue dans une commune à taux élevé", "severite": 3,
             "detail": "Aucune taxe foncière n'est annoncée. Solliès-Pont applique un taux sur le bâti de 49,51 % en 2025, parmi les plus élevés du Var. Sur l'ordre de grandeur d'un immeuble de 160 m² loué 24 000 €/an, le poste peut aller de 3 000 à 5 000 €/an selon la valeur locative cadastrale — soit jusqu'à 20 % des loyers bruts. C'est la première ligne à vérifier : chaque 1 000 € d'écart vaut 80 €/mois de cash flow."},
            {"facteur": "Facture énergétique annoncée de 3 030 à 4 130 €/an", "severite": 3,
             "detail": "Chauffage par convecteurs électriques anciens sur un bâti de 1900 (visibles sur deux photographies), pour une facture annoncée de 3 030 à 4 130 €/an pour l'immeuble — soit environ 750 à 1 030 € par logement. Le DPE D n'impose aucune contrainte avant 2034, mais ce niveau de charge pèse sur l'attractivité locative et sur la rotation : c'est un argument de rénovation, donc une dépense à provisionner."},
            {"facteur": "Baux non communiqués", "severite": 2,
             "detail": "Quatre baux en cours, aucun détail : ni dates, ni échéances, ni type, ni dépôts de garantie, ni répartition des loyers entre les lots. L'annonce ne donne qu'un total de 2 000 €/mois. Or tout le dossier repose sur ces baux, et la revalorisation de 18 % identifiée ne s'encaissera qu'à leur terme."},
            {"facteur": "Bâti de 1900 : aucun diagnostic structure ni couverture", "severite": 3,
             "detail": "Aucun diagnostic technique (structure, couverture, charpente, amiante, plomb, termites, électricité, gaz) n'accompagne l'annonce, alors que le bâti est de 1900 et sur quatre niveaux. Le DPE seul ne dit rien de la toiture, qui est la dépense qui ne se négocie pas. À faire vérifier lors de la visite des combles ou du dernier niveau."},
            {"facteur": "Loyer inférieur de 18 % au marché : potentiel ou signal", "severite": 2,
             "detail": "2 000 €/mois pour 160 m², soit 12,5 €/m², contre 15,3 €/m² de moyenne communale. Deux lectures : soit les loyers ont été fixés il y a plusieurs années et il y a 4 000 à 5 000 €/an à récupérer à la rotation, soit les logements sont petits et en état moyen, et le loyer reflète leur valeur. Les deux lectures ne donnent pas le même prix."},
            {"facteur": "Dossier d'information très mince", "severite": 1,
             "detail": "Quatre photographies, aucune charge, aucune taxe foncière, aucun bail, aucun diagnostic, aucune surface par lot, et un intermédiaire qui est un agent commercial isolé (eXp Realty, RSAC Toulon 791 286 644). La qualité du dossier ne préjuge pas de celle du bien, mais elle impose de tout vérifier avant de s'engager."},
            {"facteur": "Statut de copropriété non confirmé", "severite": 1,
             "detail": "L'annonce ne dit pas si l'immeuble est en monopropriété ou en copropriété. Quatre lots et un appartement par palier plaident pour la monopropriété, donc pour l'absence de charges et d'appels de fonds. À confirmer : si une copropriété existe, c'est 1 800 à 2 800 €/an de charges en plus et un syndic à subir."}
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
            ligne("Revenu brut annuel (4 baux en place)", f"{eur(rev)} €"),
            ligne(f"Vacance locative ({vac:.0f} %)", f"-{eur(vac_eur)} €"),
            ligne("Taxe foncière (estimée — à vérifier)", f"-{eur(ch['taxe_fonciere_annuelle_euros'])} €"),
            ligne("Charges de copropriété", "néant (monopropriété présumée)"),
            ligne("Entretien de l'immeuble", f"-{eur(ch['entretien_annuel_euros'])} €"),
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
        ro, rows_o = scenario_html(rec, rec['hypotheses']['vacance_best_pct'], loyers=[550.0, 550.0, 550.0, 550.0])
        rp, rows_p = scenario_html(rec, rec['hypotheses']['vacance_worst_pct'])
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
        <p class="scenario-subtitle">Vacance {rec['hypotheses']['vacance_base_pct']:.0f} % — les quatre baux en place, rafraîchissement étalé à la rotation (30 000 €)</p>
        <table class="projection-table"><tbody>
{rows_b}
        </tbody></table>
      </div>
      <div class="projection-card scenario-optimiste">
        <h3>Scénario Optimiste</h3>
        <p class="scenario-subtitle">Vacance {rec['hypotheses']['vacance_best_pct']:.0f} % — loyers réalignés à 550 €/lot à la rotation (13,8 €/m²)</p>
        <table class="projection-table"><tbody>
{rows_o}
        </tbody></table>
      </div>
      <div class="projection-card scenario-pessimiste">
        <h3>Scénario Pessimiste</h3>
        <p class="scenario-subtitle">Vacance {rec['hypotheses']['vacance_worst_pct']:.0f} % — deux départs dans l'année, relocation lente sur un marché de 28 annonces</p>
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
    <p class="attractiveness-intro"><strong>Sensibilité du prix plafond</strong> — frais d'acquisition 8 %, valeur de marché retenue 315 000 €.
    Création de valeur (ratio coût/valeur de 0,95) : <strong>249 000 €</strong> avec 30 000 € de travaux — 264 000 € pour un ratio de 1,00, soit le point où le prix de revient égale la valeur.
    Seuil de 6,5 % de rendement net sur le prix de revient : <strong>192 000 €</strong> avec 30 000 € de travaux (202 000 € avec 20 000 €, 172 000 € avec 50 000 €).
    À 262 000 €, le ratio coût/valeur est de 0,99 et le rendement net de 5,1 % sur le prix de revient comme sur la valeur : le dossier s'achète à sa valeur, pas en dessous.</p>
  </section>"""

    gen.bloc_scenarios = bloc_scenarios

    gen.LECTURE[SLUG] = (
        "Enfin un dossier où le prix n'est pas le problème. 1 638 €/m² pour un immeuble de 160 m² loué 2 000 €/mois, "
        "quand les appartements de Solliès-Pont se traitent à 2 852 €/m² en moyenne et 3 654 €/m² en moyenne DVF 2025 : "
        "l'affichage est 17 % sous la valeur retenue, et même une décote de bloc de 30 % ne suffit pas à ramener la "
        "valeur au niveau du prix demandé. Les quatre logements sont loués, le DPE est D, la gare TER met Toulon à "
        "douze minutes. Les deux inconnues sont dans la colonne des charges et non dans celle du prix : la taxe "
        "foncière, dans une commune dont le taux communal atteint 49,51 %, et le rafraîchissement annoncé sans montant. "
        "Le prix de revient ressort à 312 960 € pour 315 000 € de valeur : le dossier s'achète à sa valeur, la marge "
        "se joue sur le prix payé."
    )

    gen.CONF = {SLUG: dict(
        titre_court="Immeuble 4 T2 loués, Solliès-Pont (83210)",
        adresse="Solliès-Pont (83210) — immeuble de 160 m² en R+3, quatre T2 loués, un par palier",
        date_fr="20 septembre 2026",
        source="SeLoger — annonce 262WZHWZ28Z8 (eXp Realty, Team Morena — Grégory Schwan, agent commercial, RSAC Toulon 791 286 644, réf. VI1041-EXPFRANCE)",
        url=URL,
        badge="Investissement locatif",
        strategie="Conservation avec les quatre baux en place, rafraîchissement étalé à la rotation",
        fiscal_note="SCI à l'IS (15 %), amortissement sur 90 % du prix de revient sur 30 ans",
        lat="43.1901", lon="6.0412",
        quartier="Solliès-Pont (83210), vallée du Gapeau — première couronne toulonnaise",
        intro_attr=(
            "Solliès-Pont est une commune de 12 000 habitants de la vallée du Gapeau, à douze minutes de Toulon en TER, "
            "avec un <strong>atout rare pour cette taille de commune : sa gare</strong>, et un accès direct à l'A57. "
            "Les appartements s'y traitent à <strong>2 852 €/m²</strong> en moyenne (MeilleursAgents 01/09/2026), "
            "2 950 €/m² en médiane DVF et 3 654 €/m² en moyenne 2025 sur 88 ventes ; les loyers ressortent à "
            "<strong>15,3 €/m²/mois</strong> en moyenne, avec des annonces constatées entre 546 € (27 m²) et 840 € "
            "(56 m² meublé avec parking). Le prix demandé, <strong>1 638 €/m²</strong>, est 43 % sous le prix/m² moyen "
            "des appartements de la commune — et il porte sur un immeuble dont les quatre logements sont loués 2 000 €/mois."
        ),
        profil="ménages actifs de la première couronne toulonnaise : couples et petites familles travaillant à Toulon, La Garde, Hyères ou La Farlède, sensibles au trajet ferroviaire de douze minutes et au cadre semi-rural de la vallée du Gapeau",
        concl_attr=(
            "Adéquation bonne (7,0/10), la meilleure des trois dossiers du week-end. Le trio gagnant est là : un marché "
            "locatif liquide pour une commune de 12 000 habitants (28 annonces, 88 ventes d'appartements par an), une "
            "gare TER qui met Toulon à douze minutes, et des appartements qui se revendent à 2 852 €/m² quand l'immeuble "
            "est acheté à 1 638 €/m². Les réserves sont ailleurs : la commune applique un taux de taxe foncière de "
            "49,51 %, la facture énergétique annoncée atteint 3 030 à 4 130 €/an pour l'immeuble, et le rafraîchissement "
            "reste à chiffrer. Ce n'est pas un dossier de quartier, c'est un dossier de charges à verrouiller."
        ),
        intro_strat=(
            "Quatre lectures ont été testées : la conservation avec les quatre baux en place, la même conservation avec "
            "revalorisation des loyers à la rotation, la revente à la découpe des quatre T2 et la location meublée. "
            "La conservation est retenue : les revenus sont acquis au premier jour et le rafraîchissement s'étale sans "
            "toucher aux baux en cours."
        ),
        rationale=(
            "La conservation s'impose, et c'est rare : elle ne demande aucun redressement. Les quatre logements sont loués, "
            "2 000 €/mois rentrent dès le premier jour, l'EBE ressort à <strong>17 250 €/an</strong> et le cash flow net "
            "après IS à <strong>1 339 €/mois</strong> pour un prix affiché de 262 000 €. Le rafraîchissement de 30 000 € "
            "n'est pas une urgence : il s'engage à la rotation, logement par logement.<br><br>"
            "Les deux autres pistes méritaient d'être chiffrées. La <strong>revente à la découpe</strong> n'est pas à "
            "écarter sur les chiffres : les 160 m² sortent entre 368 000 € (2 300 €/m²), 416 000 € (2 600 €/m²) et "
            "456 320 € (2 852 €/m², la moyenne communale), soit 349 600 € à 433 500 € nets d'honoraires. Le revient de "
            "l'opération de découpe — prix 240 000 €, frais 19 200 €, remise au standard de vente 48 000 € (12 000 € par "
            "logement, et non 7 500 € de rafraîchissement locatif) et état descriptif de division 10 000 € — ressort à "
            "<strong>317 200 €</strong>. La marge avant impôt va donc de <strong>32 400 €</strong> à 2 300 €/m² à "
            "<strong>116 300 €</strong> à 2 852 €/m², soit après IS (15 % puis 25 %) <strong>27 500 € à 91 500 €</strong>, "
            "un ROI de 8,7 % à 28,8 % sur le revient. C'est une vraie opération, pas un mirage.<br><br>"
            "Trois choses la séparent pourtant de la conservation, et ce sont elles qui commandent le choix. "
            "D'abord le <strong>calendrier n'est pas à nous</strong> : les quatre logements sont loués, un lot ne se vend "
            "bien que vacant et rénové, et les baux ne sont pas communiqués — l'opération peut prendre quatre ans comme "
            "huit. Ensuite le <strong>prix de sortie au m² n'est pas établi</strong> : 2 852 €/m² est la moyenne communale, "
            "mais les transactions réelles du village portent sur des 56 m² à 2 098 €/m² et des 65 m² à 2 231 €/m² — "
            "à 2 300 €/m² la marge nette tombe à 27 500 €. L'écart vaut 64 000 € de résultat. Enfin, et c'est le point "
            "décisif, la découpe <strong>échange une rente contre une marge</strong> : 2 000 €/mois à perpétuité contre "
            "60 000 à 90 000 € une fois, et un immeuble vide au bout du compte.<br><br>"
            "La bonne façon de traiter la découpe n'est donc pas de la rejeter mais de la <strong>garder en option</strong> : "
            "le bien s'achète 17 % sous sa valeur, la rente court dès le premier mois, et chaque logement peut se vendre "
            "au fil des vacances, sans calendrier imposé et avec un prix de sortie qui monte. On ne décide pas aujourd'hui "
            "entre louer et vendre — on achète le droit de décider plus tard. "
            "La <strong>location meublée</strong> ajouterait 10 à 15 % de loyers — le marché local en compte (730 € pour "
            "43 m² meublé, 840 € pour 56 m²) — mais quadruplerait la gestion et le turnover sur quatre lots.<br><br>"
            "Reste le vrai sujet : à 262 000 €, le prix de revient de 312 960 € égale la valeur de marché retenue "
            "(315 000 €), ratio de 0,99. Le dossier n'est pas cher — 17 % sous la valeur — mais il ne crée pas de valeur "
            "au prix demandé. La marge se joue donc sur la négociation : à 249 000 €, le ratio descend à 0,95 et "
            "l'opération commence à créer du patrimoine ; à 240 000 €, le rendement net remonte à 5,5 % sur le revient "
            "et le cash flow à 1 331 €/mois."
        ),
        identite=[
            ("Adresse", "Solliès-Pont (83210), vallée du Gapeau — adresse exacte non communiquée ; emprise déclarée dans le village, à proximité de la gare"),
            ("Vendeur / intermédiaire", "eXp Realty (Team Morena) — Grégory Schwan, agent commercial, RSAC Toulon 791 286 644 — réf. VI1041-EXPFRANCE"),
            ("Composition", "Immeuble de <strong>1900</strong> en R+3, <strong>un appartement par palier</strong> : quatre T2, 160 m² annoncés au total (40 m² en moyenne par lot — <strong>aucune surface Carrez par lot, aucun plan</strong>). Sans ascenseur"),
            ("Occupation", "<strong>Vendu loué</strong> : quatre baux en cours, <strong>2 000 €/mois</strong> annoncés. Ni dates, ni échéances, ni type, ni répartition par lot"),
            ("DPE / GES", "<strong>DPE D / GES B</strong>, bâti de 1900. Facture énergétique annoncée entre <strong>3 030 et 4 130 €/an</strong> pour l'immeuble, chauffage par convecteurs électriques anciens"),
            ("Statut", "Immeuble présumé en <strong>monopropriété</strong> (aucun syndic, aucune charge, aucun appel de fonds mentionnés) — à confirmer. Si copropriété : 1 800 à 2 800 €/an de charges en plus"),
            ("Prix affiché", "<strong>262 000 €</strong>, honoraires à la charge du vendeur, soit <strong>1 638 €/m²</strong> sur les 160 m² annoncés"),
            ("Valeur de marché retenue", "285 000 à 350 000 €, retenue <strong>315 000 €</strong> (1 969 €/m²) : 2 852 €/m² de moyenne communale, 2 950 €/m² en médiane DVF, 3 654 €/m² en moyenne 2025 — décote de bloc de 30 % appliquée. <strong>Le prix affiché est 17 % sous la valeur</strong>"),
            ("Loyers en place", "<strong>2 000 €/mois</strong> = 24 000 €/an = <strong>9,16 % brut</strong> sur le prix affiché = 12,5 €/m², contre <strong>15,3 €/m²</strong> de moyenne communale : potentiel de revalorisation d'environ 18 % (≈ 360 €/mois) à la rotation"),
            ("Travaux", "<strong>30 000 €</strong> provisionnés (≈ 187 €/m²) pour le rafraîchissement des quatre logements, étalé à la rotation (fourchette 20 000 à 60 000 €). Les photographies montrent un logement déjà refait et un autre resté dans son jus"),
            ("Taxe foncière", "<strong>Estimée 3 000 €/an</strong> — non communiquée. Taux communal de taxe foncière sur le bâti : <strong>49,51 %</strong> en 2025, l'un des plus élevés du Var. À vérifier sur l'avis réel : le poste peut monter à 4 000-5 000 €/an"),
            ("Charges annuelles", "Taxe foncière estimée 3 000 € + entretien immeuble 1 500 € + assurance PNO 450 € + provision travaux 2,5 % = <strong>5 550 €/an</strong> hors vacance. Charges de copropriété : néant (monopropriété présumée)"),
            ("Fiscalité", "SCI à l'IS : IS 15 % sur le résultat, amortissement de 90 % du prix de revient sur 30 ans"),
            ("Prix de revient à l'affichage", "<strong>312 960 €</strong> = prix 262 000 € + frais d'acquisition 20 960 € (8 %) + travaux 30 000 €"),
        ],
        stance=(
            "<strong>À acheter — en offrant 240 000 €, avec un plafond à 250 000 €.</strong> C'est le premier dossier du "
            "week-end qui mérite un chèque. Le rendement brut de <strong>9,16 %</strong> sur le prix affiché n'est pas un "
            "artefact : il découle d'un prix de 1 638 €/m² quand les appartements de Solliès-Pont se traitent à "
            "2 852 €/m² en moyenne et 3 654 €/m² en moyenne DVF 2025. Même en appliquant une décote de bloc de 30 % — "
            "ce qui est sévère pour un immeuble dont les quatre lots sont loués — la valeur ressort à 315 000 €, soit "
            "17 % au-dessus du prix demandé. Les quatre baux produisent 2 000 €/mois dès le premier jour, le cash flow "
            "net après IS est de <strong>1 339 €/mois</strong>, et le rafraîchissement annoncé n'est pas une urgence : "
            "il s'étale à la rotation, logement par logement.<br><br>"
            "<strong>Deux réserves, et elles ne portent pas sur le prix.</strong> D'abord la taxe foncière : elle n'est "
            "pas communiquée et Solliès-Pont applique un taux sur le bâti de <strong>49,51 %</strong>, parmi les plus "
            "élevés du Var — la fourchette va de 3 000 à 5 000 €/an, soit jusqu'à 20 % des loyers bruts. Chaque "
            "1 000 € d'écart vaut 80 €/mois de cash flow : c'est la première pièce à obtenir. Ensuite le "
            "rafraîchissement, annoncé sans montant : les photographies montrent deux logements d'états très différents, "
            "l'un déjà refait avec cuisine américaine et menuiseries PVC double vitrage, l'autre resté en menuiseries "
            "bois simple vitrage avec câblage apparent. L'écart entre 20 000 et 60 000 € vaut 40 000 € de prix.<br><br>"
            "<strong>La marge se joue donc sur le prix payé, pas sur l'exploitation.</strong> À 262 000 €, le prix de "
            "revient égale la valeur (ratio 0,99) : on n'achète pas mal, mais on n'achète pas de marge non plus. "
            "À <strong>249 000 €</strong>, le ratio descend à 0,95 et l'opération commence à créer du patrimoine ; "
            "à <strong>240 000 €</strong>, le rendement net remonte à 5,5 % sur le prix de revient, le cash flow reste "
            "à 1 331 €/mois et la décote négociée absorbe l'intégralité de l'aléa travaux. C'est le prix à proposer. "
            "Foncier à 49,51 % et loyers 18 % sous le marché travaillent dans le même sens : il y a de la matière pour "
            "discuter, et le vendeur affiche déjà 17 % sous la valeur."
        ),
        prix_plafond=(
            "<strong>250 000 €</strong> net vendeur avec 30 000 € de travaux : c'est le maximum où l'opération crée encore "
            "de la valeur (ratio coût/valeur de 0,95). Repères : 240 000 € pour un rendement net de 5,5 % sur le prix de "
            "revient, 264 000 € pour un ratio de 1,00 — le point où le prix de revient égale la valeur de marché — et "
            "192 000 € pour atteindre le seuil de 6,5 % de rendement net sur le prix de revient. "
            "Grille de sensibilité aux travaux : 20 000 € → 202 000 € de prix pour le seuil de 6,5 % ; 30 000 € → 192 000 € ; "
            "50 000 € → 172 000 €. Au-delà de 264 000 €, le dossier s'achète au-dessus de sa valeur. "
            "Toute offre doit être conditionnée à l'avis de taxe foncière, aux quatre baux, aux surfaces Carrez par lot "
            "et à un devis de rafraîchissement."
        ),
        leviers=[
            "Le prix au m² est le levier le plus solide jamais présenté dans un dossier : 1 638 €/m² contre 2 852 €/m² de moyenne communale et 3 654 €/m² en moyenne DVF 2025. Même en concédant une décote de bloc de 30 %, la valeur reste au-dessus du prix demandé — un acheteur qui négocie sur ces bases part avec un avantage réel",
            "La taxe foncière n'est pas communiquée dans une commune dont le taux sur le bâti atteint 49,51 % : exiger l'avis réel avant toute offre. Si la valeur locative cadastrale est élevée, la taxe peut absorber jusqu'à 20 % des loyers bruts, et c'est 1 000 € d'écart par an pour chaque tranche de 80 €/mois de cash flow",
            "Le rafraîchissement est annoncé sans montant : faire chiffrer par corps d'état (peintures, sols, électricité, menuiseries, salles d'eau). Les photographies documentent deux logements d'états très différents — l'écart entre 20 000 et 60 000 € vaut 40 000 € de prix",
            "Les quatre baux doivent être produits : dates, échéances, types, dépôts et répartition des loyers par lot. Le potentiel de revalorisation de 18 % (2 000 € → 2 360 €/mois) ne s'encaisse qu'à leur terme, bail par bail",
            "Les surfaces Carrez par lot et les plans doivent être exigés : 160 m² annoncés pour quatre T2, soit 40 m² en moyenne, mais aucune ventilation. Si la surface habitable réelle n'est que de 120 m², le loyer au m² passe de 12,5 à 16,7 € et la revente à l'unité est moins attractive",
            "La facture énergétique annoncée (3 030 à 4 130 €/an pour l'immeuble) et les convecteurs électriques anciens sont des arguments de négociation à double titre : ils pèsent sur l'attractivité locative et annoncent une rénovation énergétique à provisionner, sans contrainte réglementaire avant 2034 puisqu'on est en DPE D",
            "Le dossier est mince — quatre photographies, aucun diagnostic technique, aucun plan : faire jouer le principe de précaution sur la couverture et la structure d'un bâti de 1900 sur quatre niveaux, dépenses qui ne se négocient pas après coup",
            "Le statut de copropriété doit être clarifié : quatre lots et un appartement par palier plaident pour la monopropriété, donc zéro charge et zéro appel de fonds. Si une copropriété existe, c'est 1 800 à 2 800 €/an de charges et un syndic en plus — de quoi revoir le prix à la baisse",
        ],
        meta=[
            "<strong>Régime fiscal retenu :</strong> SCI à l'IS (15 %) — amortissement sur 90 % du prix de revient sur 30 ans — provision travaux de 2,5 % des revenus (règle interne)",
            "<strong>Frais d'acquisition :</strong> 20 960 € (8 % du prix affiché, barème de l'ancien)",
            "<strong>Enveloppe travaux :</strong> 30 000 € provisionnés (≈ 187 €/m²), fourchette 20 000 à 60 000 €, étalés à la rotation des locataires. Aucun devis établi",
            "<strong>Contrôles à faire avant toute offre :</strong> avis de taxe foncière réel (taux communal de 49,51 %) ; les quatre baux en cours ; surfaces Carrez et plans par lot ; devis de rafraîchissement par corps d'état ; diagnostics techniques complets (électricité, gaz, amiante, plomb, termites) ; état de la couverture et de la charpente ; confirmation du statut de monopropriété ou de copropriété et, le cas échéant, budget prévisionnel ; attestation de la facture énergétique par logement",
            "<strong>Option de sortie à instruire :</strong> la revente à la découpe reste ouverte lot par lot (ROI de 8,7 à 28,8 % sur le revient selon le prix de sortie au m²), mais elle suppose un état descriptif de division et des logements vacants. Elle se décide à la vacance de chaque bail, jamais contre un calendrier de marché — d'où l'intérêt d'acheter d'abord et de trancher ensuite",
            "<strong>Points de méthode :</strong> le prix d'offre se cale sur les 2 000 € encaissés et non sur le potentiel de revalorisation (18 %), inencaissable avant les termes des baux. Le rafraîchissement s'étale à la rotation : il ne bloque aucun revenu",
            "<strong>Rappel de marché (sources au 20/09/2026) :</strong> MeilleursAgents 2 852 €/m² pour les appartements et 15,3 €/m²/mois de loyer à Solliès-Pont ; DVF 2025 : moyenne 3 654 €/m² sur 88 ventes d'appartements, médiane 2 950 €/m² ; maisons entre 3 709 €/m² (MeilleursAgents) et 4 026 €/m² (DVF). Annonces locatives relevées entre 546 € (27 m²) et 840 € (56 m² meublé)",
        ],
    )}

    gen.main()

    # Le generateur partage (gen_fiches_2026-09-10.py) code en dur la classe
    # de verdict 'nego' : pour un verdict d'achat, on reprend la classe 'buy'
    # du CSS dans la fiche de ce slug uniquement, apres ecriture.
    chemin = os.path.join(ROOT, 'analyses', SLUG, 'index.html')
    html = open(chemin, encoding='utf-8').read()
    html = html.replace('<section class="verdict nego">', '<section class="verdict buy">')
    open(chemin, 'w', encoding='utf-8').write(html)
    print('verdict : classe buy appliquee')


if __name__ == '__main__':
    main()
