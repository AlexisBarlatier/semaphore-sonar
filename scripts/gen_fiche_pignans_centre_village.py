#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche Pignans — immeuble de rapport 3 T2 vendu loué, coeur de village, 280 000 EUR.

Saisit l'entree dans analyses.json puis genere la fiche HTML avec les chiffres du moteur.
"""
import copy, importlib.util, json, os, sys

ROOT = '/home/alexis-barlatier/Documents/Semaphore-sonar'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from analyse_app import schema, engine

BASE = os.path.join(ROOT, 'analyses', 'analyses.json')
SLUG = "2026-09-20-immeuble-rapport-pignans-centre-village"
URL = ("https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/"
       "pignans-83790/26KYRRDV2G3R")

RECORD = {
    "slug": SLUG,
    "date_analyse": "2026-09-20",
    "date_maj": None,
    "titre": "Pignans — immeuble de rapport 3 T2 (147 m² Carrez) vendu loué, cœur du village",
    "bien": {
        "type_bien": "immeuble",
        "sous_type": None,
        "type_detail": (
            "Immeuble de rapport R+3 au cœur du village de Pignans, vendu LOUÉ, commercialisé par une étude notariale "
            "(LMVE 16 NOTAIRES, SELARL Ioos Solomon & Associés, Lagny-sur-Marne — réf. 77073-51). "
            "Trois T2 en étages, superficie Carrez totale 147,08 m² : logement 1 au 1er étage (48,6 m² — séjour-cuisine, "
            "une chambre, salle d'eau avec WC) ; logement 2 au 2e étage (49,82 m² — séjour-cuisine, deux chambres, WC, "
            "salle d'eau) ; logement 3 au 3e étage (48,66 m² — séjour-cuisine, une chambre, salle d'eau avec WC, "
            "terrasse tropézienne). DPE D / GES B. "
            "L'immeuble est en copropriété SANS SYNDIC : les parties communes sont gérées directement, et « quelques "
            "travaux sont en prévision sur les parties communes » selon l'étude notariale — sans montant. "
            "Une partie du rez-de-chaussée n'est pas exploitée et sert de cave aux locataires. "
            "Les trois lots sont loués (baux en cours, non communiqués) : 630 € + 550 € + 560 € = 1 740 €/mois charges "
            "comprises. SeLoger affiche par ailleurs un champ automatique « état : rénovation nécessaire », en "
            "contradiction avec la mention « logements en bon état général » de l'étude notariale."
        ),
        "neuf": False,
        "adresse": {
            "texte": "Cœur du village, Pignans (83790) — adresse exacte non communiquée",
            "ville": "Pignans",
            "code_postal": "83790"
        },
        "surfaces": {
            "texte": ("147,08 m² Carrez (48,6 + 49,82 + 48,66) — 150 m² annoncés. Partie de rez-de-chaussée non "
                      "exploitée : surface non communiquée"),
            "carrez_m2": 147.08
        },
        "lots": {
            "count": 3,
            "surface_par_lot_m2": None,
            "nature": "3 T2 en étages (48,6 / 49,82 / 48,66 m²) + terrasse tropézienne au 3e + partie de RDC non exploitée",
            "lots_distincts": 3
        },
        "copro": {
            "charges_annuelles_euros": 900.0,
            "charges_source": (
                "ESTIMATION, aucune charge n'est communiquée dans l'annonce. L'immeuble est en copropriété sans syndic : "
                "sont à budgéter l'assurance des parties communes, l'électricité, le nettoyage de la cage d'escalier et "
                "l'entretien courant, soit 900 €/an pour trois lots (300 €/lot/an). Si la quote-part des trois lots est de "
                "100 % des millièmes, l'intégralité des travaux sur parties communes nous revient — ce que la provision de "
                "travaux ci-dessous suppose. À faire préciser par l'état descriptif de division et les derniers comptes."
            )
        },
        "travaux": {
            "montant_euros": 20000.0,
            "nature": (
                "« Quelques travaux en prévision sur les parties communes » (étude notariale), sans montant ni nature. "
                "Les photographies montrent une façade marquée (crépi noirci et salpêtre en pied de façade autour des "
                "portes, volets écaillés, câbles apparents) et les murs de la terrasse tropézienne très dégradés au-dessus "
                "d'un sol refait : ravalement, traitement des remontées d'humidité en pied de façade, réfection de la cage "
                "d'escalier et provision pour la couverture. Enveloppe retenue 20 000 € pour l'ensemble de l'immeuble "
                "(≈ 136 €/m² Carrez), fourchette 15 000 à 40 000 €. À l'intérieur, un des logements photographiés montre "
                "des réseaux apparents, un convecteur vétuste et des traces d'humidité : ces reprises relèvent de la rotation "
                "des locataires et ne sont pas budgétées ici — elles sont provisionnées par le poste « provision travaux » "
                "récurrent du compte d'exploitation."
            )
        }
    },
    "annonce": {
        "plateforme": "seloger",
        "url": URL,
        "prix_affiche_euros": 280000.0,
        "prix_retenu_euros": None,
        "prix_statut": "affiche",
        "prix_commentaire": (
            "280 000 €, honoraires à la charge du vendeur, soit 1 867 €/m² sur les 150 m² annoncés ou 1 904 €/m² sur les "
            "147,08 m² Carrez. Vente notariale (Immobilier.notaires®, étude LMVE 16 NOTAIRES à Lagny-sur-Marne) : le "
            "vendeur est probablement une indivision ou une succession, géré depuis l'Île-de-France, sur un bien situé "
            "dans le Var — configuration qui laisse généralement de la place à une négociation chiffrée, mais aussi qui "
            "signifie que le vendeur ne connaît pas les travaux des parties communes."
        )
    },
    "marche": {
        "valeur": {
            "basse_euros": 240000.0,
            "haute_euros": 290000.0,
            "retenue_euros": 260000.0,
            "source": (
                "Trois sources convergentes. (1) MeilleursAgents au 01/09/2026 : 2 020 €/m² en moyenne communale pour les "
                "appartements et 12,4 €/m²/mois de loyer. (2) DVF 2025 : 2 264 €/m² en moyenne (18 ventes d'appartements "
                "sur un an — marché très étroit), avec des transactions réelles à 2 098 €/m² (56 m², Grande Rue), "
                "2 907 €/m² (21 m², place Mazel) et 3 464 €/m² (78 m², Saint-Esprit) ; PAP retient 2 150 €/m². "
                "(3) Par capitalisation : les 20 880 € de loyers annuels, chargés et pondérés d'une vacance de 5 %, laissent "
                "un revenu net avant impôt de 16 439 € ; à 6,3 % de rendement net avant impôt, cela vaut 260 000 €. "
                "Valeur retenue 260 000 €, soit 1 768 €/m² Carrez : une décote de 12 % sur le prix/m² des appartements de "
                "la commune, qui paie l'absence de décote de bloc réelle et la profondeur du marché local. "
                "Fourchette 240 000 à 290 000 €. Le prix affiché (1 904 €/m²) est donc AU NIVEAU du marché — pas au-dessus, "
                "mais sans marge."
            ),
            "confiance": "moyenne"
        },
        "loyers": [
            {"lot": "T2 de 48,6 m² (1er étage)", "quantite": 1, "loyer_mensuel_euros": 630.0, "occupe": True,
             "note": ("12,96 €/m² CC — au-dessus de la moyenne communale de 12,4 €/m². Bail en cours (non communiqué). "
                      "Peu de revalorisation à espérer à court terme : révision à l'IRL uniquement.")},
            {"lot": "T2 de 49,82 m² (2e étage, deux chambres)", "quantite": 1, "loyer_mensuel_euros": 550.0, "occupe": True,
             "note": ("11,04 €/m² CC — le lot le moins cher au m² alors qu'il compte deux chambres, format rare dans le "
                      "village. C'est ici que se situe la seule revalorisation documentée : à 12,4 €/m², il vaut 618 €, "
                      "soit +68 €/mois. Inencaissable avant la rotation : bail en cours.")},
            {"lot": "T2 de 48,66 m² (3e étage, terrasse tropézienne)", "quantite": 1, "loyer_mensuel_euros": 560.0, "occupe": True,
             "note": ("11,51 €/m² CC. Terrasse tropézienne : argument de relocation réel, mais aussi le lot le plus exposé "
                      "(dernier étage, étanchéité et couverture à vérifier). Bail en cours.")}
        ],
        "notes": (
            "Loyers en place 1 740 €/mois charges comprises, soit 20 880 €/an et 7,46 % brut sur le prix affiché — "
            "11,83 €/m², contre 12,4 €/m² de moyenne communale (MeilleursAgents 09/2026). Les trois lots sont loués : "
            "le revenu est acquis au premier jour, ce qui est l'atout principal du dossier, mais il n'y a pas de marge "
            "immédiate — les loyers sont DÉJÀ au prix du marché, et un bail en cours ne se révise qu'à l'IRL. Potentiel "
            "identifiable à la rotation : +68 €/mois sur le T2 de 49,82 m² (550 € → 618 € au prix du marché), soit "
            "816 €/an et environ 8 000 € de capacité de prix. Annonces locatives relevées le 20/09/2026 dans le secteur : "
            "560 € (33 m²), 615 € (31 m² à Gonfaron), 650 € (T3 66 m²), 680 €, 708 € (63 m²), 820 € (T3) — "
            "seulement 9 à 12 annonces en ligne à Pignans : le marché locatif est réel mais peu profond."
        )
    },
    "hypotheses": {
        "vacance_base_pct": 5.0,
        "vacance_best_pct": 2.0,
        "vacance_worst_pct": 12.0,
        "vacance_justification": (
            "Taux par défaut de la branche résidentielle (5 % / 2 % / 12 %), sans écart : les trois logements sont loués, "
            "les loyers sont au prix du marché et les baux sont en cours. Le Worst à 12 % correspond à un départ suivi d'une "
            "relocation lente — le marché local ne compte que 9 à 12 annonces de location et 18 ventes d'appartements par an, "
            "donc une relocation de T2 peut prendre plusieurs mois. Le risque n'est pas la vacance structurelle, c'est la "
            "profondeur du marché."
        ),
        "frais_acquisition_euros": 22400.0,
        "frais_divers_euros": 0.0,
        "charges": {
            "taxe_fonciere_annuelle_euros": 1075.0,
            "taxe_fonciere_commentaire": (
                "Montant annoncé par l'étude notariale : 1 075 €/an, soit 5,1 % des loyers bruts — très raisonnable, "
                "bien en dessous du seuil d'alerte de 15 %. À confirmer sur l'avis réel."
            ),
            "charges_copro_annuelles_euros": 900.0,
            "charges_copro_commentaire": (
                "ESTIMATION 900 €/an (300 €/lot/an) : assurance des parties communes, électricité, nettoyage et entretien "
                "courant d'une copropriété sans syndic. Aucun chiffre n'est communiqué dans l'annonce — à obtenir avec "
                "l'état descriptif de division et les derniers appels de fonds."
            ),
            "pno_annuelle_euros": 300.0,
            "pno_commentaire": "Assurance propriétaire non occupant pour trois lots (100 €/lot).",
            "entretien_annuel_euros": 600.0,
            "entretien_commentaire": "Entretien courant : cage d'escalier, désenfumage, petites reprises sur les parties communes.",
            "comptabilite_annuelle_euros": 0.0,
            "comptabilite_commentaire": (
                "Aucune ligne de comptabilité : la SCI porte déjà d'autres biens, le poste est mutualisé (convention du groupe)."
            )
        }
    },
    "analyse": {
        "branche": "residentiel",
        "type_operation": "locatif",
        "strategie_retenue": {
            "nom": "Conservation avec les trois baux en place, revalorisation du lot sous-loué à la rotation",
            "code": "ld-nue",
            "lots": 3
        },
        "strategies_explorees": [
            {"strategie": "Conservation avec les trois baux en place", "lots": 3,
             "rendement": "4,8 % net sur le revient / 5,9 % sur la valeur",
             "faisabilite": "immédiate, revenus acquis au premier jour",
             "risque": "faible — mais aucune marge : loyers déjà au prix du marché"},
            {"strategie": "Exploitation de la partie de rez-de-chaussée non utilisée", "lots": 4,
             "rendement": "potentiel non chiffrable",
             "faisabilite": "à instruire (surface inconnue, accès, PLU)",
             "risque": "moyen — surface non communiquée, usage à valider ; ne doit pas entrer dans le prix"},
            {"strategie": "Revente à la découpe des trois T2", "lots": 3,
             "rendement": "marge négative d'environ 32 000 €",
             "faisabilite": "simple : les lots sont déjà distincts en copropriété",
             "risque": "rédhibitoire — les 309 000 € de revente au détail ne couvrent pas le prix de revient"},
            {"strategie": "Location meublée des trois T2", "lots": 3,
             "rendement": "+10 à 15 % de loyer, mais vacance et turnover accrus",
             "faisabilite": "immédiate",
             "risque": "élevé — le profil locataire local (actifs, familles) n'est pas un profil meublé, et le village ne compte que 9 à 12 annonces locatives"}
        ],
        "attractivite": [
            {"dimension": "transports", "score": 7,
             "justification": "Atout réel et rare pour un village de 3 000 habitants : Pignans a sa gare, desservie par le TER sur l'axe Toulon–Carnoules–Saint-Raphaël. Accès A57 par Carnoules et Le Luc. Toulon et Saint-Raphaël à moins d'une heure, Hyères à 35 minutes."},
            {"dimension": "commerces", "score": 6,
             "justification": "Cœur de village commerçant (commerces de proximité, marché, école, services publics) — le bien est « au cœur du village », ce qui est exactement l'emplacement qui se reloue. Moins dense toutefois qu'une sous-préfecture."},
            {"dimension": "ecoles", "score": 5,
             "justification": "École primaire sur la commune ; collèges et lycées à Gonfaron, Besse-sur-Issole ou Le Luc. Demande familiale réelle mais modeste pour des T2."},
            {"dimension": "securite", "score": 6,
             "justification": "Village rural du pied des Maures, pas de quartier prioritaire. 12 % de logements vacants sur la commune : le centre ancien se dégrade lentement, sans tension particulière."},
            {"dimension": "demande_locative", "score": 6,
             "justification": "Demande locative réelle (27 % de locataires, 81 % de résidences principales, desserte ferroviaire attractive pour les actifs), mais marché étroit : 9 à 12 annonces à louer et 19 % seulement de logements collectifs sur 2 247 logements."},
            {"dimension": "dynamisme", "score": 5,
             "justification": "Prix en progression sur la commune (+12,4 % sur un an selon PAP, appartements +9,6 % sur un an en DVF) dans un secteur en croissance résidentielle ; mais 18 ventes d'appartements par an seulement et une construction neuve à l'arrêt (3 logements autorisés en 2026). Marché peu liquide."}
        ],
        "risques": [
            {"facteur": "Loyers déjà au prix du marché — aucune marge d'entrée", "severite": 3,
             "detail": "1 740 €/mois pour 147,08 m² Carrez, soit 11,83 €/m² contre 12,4 €/m² de moyenne communale. Le dossier s'achète donc en capitalisant le loyer existant : il n'y a pas de valeur locative cachée à révéler, seulement 68 €/mois à récupérer sur un lot à la rotation (soit environ 8 000 € de capacité de prix). C'est une opération de rendement, pas de redressement."},
            {"facteur": "Copropriété sans syndic et travaux sur parties communes non chiffrés", "severite": 3,
             "detail": "L'étude notariale annonce « quelques travaux en prévision sur les parties communes » sans montant, et la copropriété n'a pas de syndic : personne n'a voté de budget, personne ne porte la dépense, et il n'y a pas de procès-verbal d'assemblée générale à consulter. Les photos montrent une façade marquée (salpêtre en pied de mur, volets écaillés, câbles apparents) et des murs de terrasse dégradés. Provision retenue 20 000 € (fourchette 15 000 à 40 000 €) : c'est le principal aléa chiffrable du dossier."},
            {"facteur": "Marché local très étroit", "severite": 4,
             "detail": "18 ventes d'appartements par an à Pignans, 9 à 12 annonces de location en ligne, 2 247 logements dont 19 % seulement d'appartements : la liquidité est faible des deux côtés. Un lot vide peut mettre plusieurs mois à se relouer, et la revente d'un immeuble entier dans un village de 3 000 habitants se compte en trimestres, voire en années. C'est ce qui justifie la vacance pessimiste à 12 % et la décote de valeur retenue."},
            {"facteur": "Baux non communiqués", "severite": 2,
             "detail": "L'annonce donne les loyers mais aucune date de bail, aucune échéance, aucun type (nu/meublé), aucune clause de révision et aucun dépôt de garantie. Or tout le prix repose sur ces baux : un bail précaire ou une échéance imminente change la nature du dossier, notamment pour le lot à 550 € dont la revalorisation est le seul potentiel."},
            {"facteur": "Façade et pied de mur — humidité ascensionnelle", "severite": 3,
             "detail": "Les photographies montrent des traces de salpêtre et un crépi décollé autour des portes du rez-de-chaussée, ainsi que des coulures sous les fenêtres. Sur un bâti ancien de village, ce type de désordre remonte souvent à l'absence de coupure de capillarité : le traitement est coûteux et n'est pas une simple peinture. À faire chiffrer par un maçon avant toute offre."},
            {"facteur": "Risque inondation — porter à connaissance du 15 avril 2025", "severite": 2,
             "detail": "La préfecture du Var a notifié à Pignans un porter à connaissance inondation du 15 avril 2025 sur le bassin versant du Gapeau : un plan de prévention du risque inondation est en préparation, sans être approuvé à ce jour. Aucune contrainte immédiate sur un bâtiment existant, mais un PPRi approuvé peut modifier les règles d'urbanisme et l'assurabilité. À suivre."},
            {"facteur": "Lot du 3e étage sous toiture, avec terrasse", "severite": 2,
             "detail": "Le logement 3 est au dernier étage, sous une terrasse tropézienne dont le sol a été refait mais dont les murs périphériques sont très dégradés. L'étanchéité et la couverture conditionnent la valeur du lot le plus cher à relouer : à vérifier impérativement (relevés, traces d'infiltration)."},
            {"facteur": "Contradiction sur l'état du bien", "severite": 2,
             "detail": "L'étude notariale écrit « logements en bon état général » ; la fiche SeLoger affiche un champ automatique « état : rénovation nécessaire » et l'une des photographies montre des réseaux apparents, un convecteur électrique vétuste et des traces d'humidité dans une pièce d'eau. La réalité est probablement intermédiaire — bon état locatif, finitions anciennes — mais elle doit être vue, lot par lot."}
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
            ligne("Revenu brut annuel (3 baux en place)", f"{eur(rev)} €"),
            ligne(f"Vacance locative ({vac:.0f} %)", f"-{eur(vac_eur)} €"),
            ligne("Taxe foncière (montant notarié)", f"-{eur(ch['taxe_fonciere_annuelle_euros'])} €"),
            ligne("Charges de copropriété (estimées, sans syndic)", f"-{eur(ch['charges_copro_annuelles_euros'])} €"),
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
        ro, rows_o = scenario_html(rec, rec['hypotheses']['vacance_best_pct'], loyers=[630.0, 618.0, 560.0])
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
        <p class="scenario-subtitle">Vacance {rec['hypotheses']['vacance_base_pct']:.0f} % — les trois baux en place, 20 000 € de travaux sur parties communes</p>
        <table class="projection-table"><tbody>
{rows_b}
        </tbody></table>
      </div>
      <div class="projection-card scenario-optimiste">
        <h3>Scénario Optimiste</h3>
        <p class="scenario-subtitle">Vacance {rec['hypotheses']['vacance_best_pct']:.0f} % — reconduction des trois baux et T2 de 49,82 m² réaligné à 618 € (12,4 €/m²) à la rotation</p>
        <table class="projection-table"><tbody>
{rows_o}
        </tbody></table>
      </div>
      <div class="projection-card scenario-pessimiste">
        <h3>Scénario Pessimiste</h3>
        <p class="scenario-subtitle">Vacance {rec['hypotheses']['vacance_worst_pct']:.0f} % — un départ, relocation lente sur un marché étroit, travaux dérivés</p>
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
    <p class="attractiveness-intro"><strong>Sensibilité du prix plafond</strong> — frais d'acquisition 8 %, valeur de marché retenue 260 000 €. Seuil de 6,5 % de rendement net sur le prix de revient : <strong>190 000 €</strong> avec 20 000 € de travaux (194 000 € avec 15 000 €, 184 000 € avec 25 000 €, 169 000 € avec 40 000 €). Ratio coût/valeur de 0,95 : <strong>210 000 €</strong> avec 20 000 € de travaux. À 280 000 €, le rendement net sur le prix de revient ressort à 4,8 % et le ratio coût/valeur à 1,24 : l'opération détruit 62 400 € de valeur avant même de compter les travaux réellement votés.</p>
  </section>"""

    gen.bloc_scenarios = bloc_scenarios

    gen.LECTURE[SLUG] = (
        "C'est le dossier le plus propre des deux : l'immeuble est vendu loué, les trois baux produisent 1 740 €/mois, "
        "le DPE D ne pose aucune contrainte, la taxe foncière est faible (1 075 €) et le village a une gare TER. "
        "Le problème est ailleurs : le prix est exactement au niveau du marché. 1 904 €/m² Carrez contre 2 020 €/m² de "
        "moyenne communale (MeilleursAgents) et 2 150 €/m² selon PAP — soit 7 à 12 % de décote seulement, pour un immeuble "
        "entier, illiquide, avec des travaux de parties communes non chiffrés et des loyers déjà au prix. "
        "À 280 000 €, les 20 880 € de loyers annuels rapportent 4,8 % net après IS sur un prix de revient de 322 400 €, "
        "quand notre seuil est de 6,5 %. Tout le rendement manquant doit venir du prix : il faut 189 000 € pour que le "
        "dossier redevienne un dossier de parc."
    )

    gen.CONF = {SLUG: dict(
        titre_court="Immeuble 3 T2 vendu loué, cœur du village de Pignans",
        adresse="Cœur du village, Pignans (83790) — immeuble de 147 m² Carrez, 3 T2 loués + terrasse tropézienne",
        date_fr="20 septembre 2026",
        source="SeLoger — annonce 26KYRRDV2G3R (Immobilier.notaires®, étude LMVE 16 NOTAIRES — SELARL Ioos Solomon & Associés, réf. 77073-51)",
        url=URL,
        badge="Investissement locatif",
        strategie="Conservation avec les trois baux en place, revalorisation du lot sous-loué à la rotation",
        fiscal_note="SCI à l'IS (15 %), amortissement sur 90 % du prix de revient sur 30 ans",
        lat="43.3007", lon="6.2265",
        quartier="cœur du village de Pignans (83790)",
        intro_attr=(
            "Pignans est un village de 3 000 habitants au pied des Maures, entre Le Luc et Carnoules, avec un atout que "
            "peu de communes de cette taille peuvent revendiquer : <strong>sa gare</strong>, desservie par le TER sur l'axe "
            "Toulon–Carnoules–Saint-Raphaël, et un accès autoroutier rapide par l'A57. Les appartements de la commune se "
            "traitent à <strong>2 020 €/m²</strong> (MeilleursAgents 01/09/2026), 2 150 €/m² selon PAP et 2 264 €/m² en "
            "moyenne DVF 2025 — 18 ventes seulement sur l'année. Les loyers s'établissent à 12,4 €/m²/mois en moyenne, avec "
            "des annonces relevées entre 560 et 820 € pour des T2 et T3. Le bien est affiché <strong>1 904 €/m² Carrez</strong> : "
            "7 à 12 % sous le prix/m² des appartements de la commune, mais sans aucune décote de bloc."
        ),
        profil="actifs travaillant à Toulon, Hyères, Le Luc ou dans la plaine des Maures, ménages modestes et familles à la recherche d'un T2 de village avec commerces à pied et gare à proximité",
        concl_attr=(
            "Adéquation correcte (5,8/10). L'emplacement est bon — cœur de village, commerces et services à pied, gare TER "
            "à quelques minutes — et le format T2 correspond à la demande. Trois réserves toutefois : le marché est étroit "
            "(9 à 12 annonces locatives, 18 ventes d'appartements par an, 19 % seulement de logements collectifs), le "
            "village compte 12 % de logements vacants, et les loyers en place sont déjà au prix du marché : il n'y a pas de "
            "valeur locative à révéler. C'est un dossier d'emplacement, pas de redressement."
        ),
        intro_strat=(
            "Quatre lectures ont été testées : la conservation avec les trois baux en place, l'exploitation de la partie de "
            "rez-de-chaussée non utilisée, la revente à la découpe des trois T2 (facilitée par des lots déjà distincts en "
            "copropriété) et la location meublée. La conservation est retenue : c'est la seule qui soit immédiatement "
            "encaissable et chiffrable."
        ),
        rationale=(
            "La conservation est la stratégie de bon sens : les trois logements sont loués, le revenu est acquis au premier "
            "jour, et les charges sont légères (taxe foncière 1 075 €, soit 5,1 % des loyers bruts — c'est peu). "
            "Après vacance de 5 %, charges, assurance et provision travaux, l'EBE ressort à <strong>16 439 €/an</strong>, "
            "le cash flow net après IS à <strong>1 285 €/mois</strong> et le rendement net à <strong>4,8 % sur le prix de "
            "revient</strong> (5,9 % sur la valeur de marché). Le ratio coût/valeur est de 1,24 : à 280 000 €, l'opération "
            "détruit 62 400 € de valeur, frais d'acquisition et travaux inclus.<br><br>"
            "La <strong>revente à la découpe</strong> méritait un examen sérieux, puisque les trois lots sont déjà distincts "
            "en copropriété et qu'il n'y a donc aucun état descriptif de division à créer. Le calcul est sans appel : "
            "147,08 m² au prix du marché communal (2 100 €/m², moyenne des trois sources) valent 309 000 €, soit environ "
            "290 000 € nets d'honoraires, contre un prix de revient de 322 400 € avant portage et frais de vente. "
            "La marge est négative d'environ 32 000 € : l'arbitrage n'existe pas.<br><br>"
            "L'<strong>exploitation de la partie de rez-de-chaussée</strong> non utilisée est le seul vrai potentiel "
            "non chiffré du dossier : elle sert aujourd'hui de cave aux locataires. Sa surface n'est pas communiquée, son "
            "usage futur non plus (cave, garage, local, studio ?). À traiter comme un bonus : on ne paie pas pour une "
            "surface qu'on n'a pas mesurée, mais c'est un argument à faire préciser avant l'offre.<br><br>"
            "Reste la réalité du prix. Les loyers sont au niveau du marché (11,83 €/m² contre 12,4 €/m²), il n'y a donc "
            "qu'une seule source de rendement : la négociation. Le seuil de 6,5 % de rendement net que s'impose la SCI "
            "n'est atteint qu'à <strong>189 000 €</strong> avec 20 000 € de travaux."
        ),
        identite=[
            ("Adresse", "Cœur du village de Pignans (83790) — adresse exacte non communiquée"),
            ("Vendeur / intermédiaire", "Vente notariale — Immobilier.notaires®, étude <strong>LMVE 16 NOTAIRES</strong> (SELARL Ioos Solomon & Associés), 16 avenue du Général Leclerc, 77400 Lagny-sur-Marne — réf. 77073-51. Configuration type indivision ou succession"),
            ("Composition", "R+3 : <strong>trois T2</strong> de 48,6 m² (1er étage), 49,82 m² (2e étage, deux chambres) et 48,66 m² (3e étage, <strong>terrasse tropézienne</strong>) — 147,08 m² Carrez. <strong>Partie de rez-de-chaussée non exploitée</strong> servant de cave aux locataires (surface non communiquée)"),
            ("Occupation", "<strong>Vendu loué</strong> : trois baux en cours, 630 € + 550 € + 560 € = <strong>1 740 €/mois charges comprises</strong> (baux non communiqués : dates, échéances, type, dépôts à obtenir)"),
            ("DPE / GES", "<strong>DPE D / GES B</strong> — aucune contrainte réglementaire de location avant 2034. SeLoger affiche en parallèle un champ automatique « état : rénovation nécessaire », en contradiction avec la mention « bon état général » de l'étude notariale"),
            ("Statut", "Immeuble en <strong>copropriété sans syndic</strong> — trois lots distincts. Charges estimées 900 €/an (aucun chiffre communiqué) : à confirmer par l'état descriptif de division et les derniers appels de fonds"),
            ("Prix affiché", "<strong>280 000 €</strong>, honoraires à la charge du vendeur, soit 1 867 €/m² sur 150 m² annoncés ou <strong>1 904 €/m² Carrez</strong>"),
            ("Valeur de marché retenue", "240 000 à 290 000 €, retenue <strong>260 000 €</strong> (1 768 €/m² Carrez) : 2 020 €/m² de moyenne communale (MeilleursAgents), 2 150 €/m² (PAP), 2 264 €/m² en DVF 2025"),
            ("Loyers en place", "<strong>1 740 €/mois</strong> charges comprises = 20 880 €/an = <strong>7,46 % brut</strong> sur le prix affiché = 11,83 €/m², contre 12,4 €/m² de marché. Seul potentiel identifié : le T2 de 49,82 m², loué 550 € (11,04 €/m²) au lieu de 618 € au prix du marché — <strong>+68 €/mois à la rotation</strong>"),
            ("Taxe foncière", "<strong>1 075 €/an</strong> (montant annoncé), soit 5,1 % des loyers bruts — très raisonnable"),
            ("Travaux", "<strong>20 000 € provisionnés</strong> pour les parties communes (ravalement, pied de façade et humidité, cage d'escalier, provision couverture — fourchette 15 000 à 40 000 €) : « quelques travaux en prévision » annoncés sans montant"),
            ("Charges annuelles", "Taxe foncière 1 075 € + charges de copropriété estimées 900 € + assurance PNO 300 € + entretien 600 € + provision travaux 2,5 % = <strong>3 397 €/an</strong> hors vacance"),
            ("Fiscalité", "SCI à l'IS : IS 15 % sur le résultat, amortissement de 90 % du prix de revient sur 30 ans"),
            ("Prix de revient à l'affichage", "<strong>322 400 €</strong> = prix 280 000 € + frais d'acquisition 22 400 € (8 %) + travaux 20 000 €"),
        ],
        stance=(
            "<strong>À négocier — 190 000 € pour tenir le seuil de 6,5 % de rendement net, contre 280 000 € affichés.</strong> "
            "Le dossier est bon sur le fond : immeuble <strong>vendu loué</strong> (1 740 €/mois acquis dès le premier jour), "
            "<strong>DPE D</strong>, taxe foncière faible à 5,1 % des loyers, village avec gare TER, cœur de bourg commerçant, "
            "terrasse tropézienne au dernier étage et trois lots déjà distincts en copropriété. C'est propre, louable, et "
            "sans travaux lourds.<br><br>"
            "Mais le prix est exactement celui du marché, et c'est tout le problème. Sur 147,08 m² Carrez, 280 000 € "
            "représentent 1 904 €/m², soit 7 à 12 % seulement sous le prix/m² des appartements de la commune — pour un "
            "immeuble entier, dans un village qui ne compte que 18 ventes d'appartements par an et 9 à 12 annonces "
            "locatives. À ce prix, le prix de revient atteint <strong>322 400 €</strong> (frais de 8 % et 20 000 € de "
            "travaux sur les parties communes inclus) pour une valeur de marché retenue de <strong>260 000 €</strong> : "
            "un ratio coût/valeur de 1,24, soit 62 400 € de valeur détruite. Le rendement net ressort à <strong>4,8 % "
            "sur le prix de revient</strong> et 5,9 % sur la valeur, contre un seuil de 6,5 %.<br><br>"
            "Et il n'y a pas de rattrapage possible par l'exploitation : les loyers en place sont <strong>déjà au niveau du "
            "marché</strong> (11,83 €/m² contre 12,4 €/m²), et un bail en cours ne se révise qu'à l'IRL. Le seul gisement "
            "identifiable est de <strong>68 €/mois</strong> sur le T2 de 49,82 m², loué 550 € alors qu'il vaut 618 € au "
            "prix du marché — inencaissable avant la rotation, et il ne pèse que 8 000 € de capacité de prix. "
            "La revente à la découpe, tentante puisque les lots sont déjà distincts, a été chiffrée : "
            "309 000 € de valeur au détail, 290 000 € nets d'honoraires, contre 322 400 € de prix de revient — "
            "marge négative de 32 000 €, dossier écarté.<br><br>"
            "<strong>Deux aléas restent à lever avant toute offre.</strong> D'abord les travaux de parties communes : "
            "« quelques travaux en prévision » sans montant, dans une copropriété sans syndic, donc sans budget voté ni "
            "procès-verbal à consulter — les photographies montrent une façade avec salpêtre en pied de mur et des volets "
            "écaillés. L'écart entre 15 000 et 40 000 € vaut 25 000 € de prix. Ensuite les baux : dates, échéances, type "
            "et dépôts ne sont pas communiqués, alors que tout le prix repose sur eux. "
            "<strong>À 260 000 €, l'équilibre approche sans être atteint ; à 190 000 €, le dossier devient un vrai dossier "
            "de parc, à 6,5 % net et 1 252 €/mois de cash flow.</strong> C'est le prix à proposer — en sachant que le vendeur "
            "est une étude notariale, donc un interlocuteur qui chiffre, pas un particulier qui s'attache."
        ),
        prix_plafond=(
            "<strong>189 000 €</strong> (arrondi 190 000 €) net vendeur avec 20 000 € de travaux : c'est le prix où le rendement net atteint "
            "6,5 % sur le prix de revient (cash flow de 1 252 €/mois après IS). Grille de sensibilité : 15 000 € de travaux "
            "→ 194 000 € ; 20 000 € → 189 000 € ; 25 000 € → 184 000 € ; 40 000 € → 169 000 €. "
            "Second repère, côté marché : <strong>210 000 €</strong> pour rester sous la valeur retenue avec un ratio "
            "coût/valeur de 0,95 — c'est le maximum qu'un acheteur rationnel devrait payer sans exiger de rendement "
            "supplémentaire. Au-delà de 210 000 €, le bien s'achète au-dessus de sa valeur ; à 280 000 €, il détruit "
            "62 400 € de valeur. Toute offre doit être conditionnée à la communication des baux, de l'état descriptif de "
            "division et du chiffrage des travaux de parties communes."
        ),
        leviers=[
            "Le rendement est le levier central, et il se démontre : 7,46 % brut ne veut pas dire grand-chose, mais 4,8 % net après IS sur un prix de revient de 322 400 €, contre un seuil de 6,5 %, se présente chiffres en main. C'est la discussion la plus honnête à avoir avec une étude notariale",
            "Les travaux de parties communes sont annoncés sans montant, dans une copropriété sans syndic : ni budget voté, ni procès-verbal d'assemblée générale, ni devis. Faire chiffrer le ravalement et le traitement des remontées d'humidité (salpêtre visible en pied de façade sur les photographies) avant toute offre — l'écart entre 15 000 et 40 000 € vaut 25 000 € de prix",
            "Les baux doivent être produits : dates et échéances, type (nu ou meublé), clause de révision, dépôts de garantie. Un bail précaire ou une échéance imminente sur le lot le plus rentable change la nature du dossier, et une revalorisation est le seul potentiel identifié (+68 €/mois sur le T2 de 49,82 m²)",
            "La partie de rez-de-chaussée non exploitée doit être mesurée et son usage précisé : aujourd'hui simple cave des locataires, elle peut valoir un garage, un local ou un studio. Surface non communiquée à ce stade — on ne paie que ce qui est mesuré, mais c'est un argument de négociation à instruire",
            "La liquidité du marché est un argument de décote, pas de vente : 18 ventes d'appartements par an, 9 à 12 annonces locatives, 12 % de logements vacants dans la commune et 19 % seulement de logements collectifs. Un immeuble entier s'y revend en trimestres, pas en semaines — c'est ce que paie la décote de bloc, qui n'existe pas dans le prix demandé",
            "Le vendeur est une étude notariale de Lagny-sur-Marne (77) gérant un bien du Var : très probablement une indivision ou une succession. Ces dossiers se traitent sur des chiffres, pas sur l'affect, et le notaire a intérêt à une vente rapide et propre : c'est le contexte le plus favorable pour une offre basse documentée",
            "La terrasse tropézienne est un argument de relocation réel à mettre en avant auprès du lot du 3e étage — mais elle s'accompagne d'une exposition à l'étanchéité et à la couverture : à vérifier, et à faire jouer en décote si des reprises sont nécessaires",
            "Le repère de prix à opposer : 1 904 €/m² Carrez, contre 2 020 €/m² de moyenne communale et 2 150 €/m² selon PAP. Un immeuble entier, illiquide et avec travaux annoncés devrait se traiter 15 à 20 % sous le prix/m² des appartements vendus à l'unité — pas 7 à 12 %",
        ],
        meta=[
            "<strong>Régime fiscal retenu :</strong> SCI à l'IS (15 %) — amortissement sur 90 % du prix de revient sur 30 ans — provision travaux de 2,5 % des revenus (règle interne)",
            "<strong>Frais d'acquisition :</strong> 22 400 € (8 % du prix affiché, barème de l'ancien)",
            "<strong>Enveloppe travaux :</strong> 20 000 € provisionnés pour les parties communes (ravalement, humidité en pied de façade, cage d'escalier, provision couverture), fourchette 15 000 à 40 000 €. Aucun montant ni devis communiqué par l'étude notariale",
            "<strong>Contrôles à faire avant toute offre :</strong> les trois baux (dates, échéances, type, révision, dépôts), l'état descriptif de division et le règlement de copropriété, les derniers appels de fonds et l'existence d'un carnet d'entretien, le chiffrage des travaux de parties communes (façade, humidité, couverture, cage d'escalier), l'avis de taxe foncière réel, les diagnostics techniques complets (électricité, gaz, amiante, plomb, termites), l'état de l'étanchéité de la terrasse tropézienne, la surface et le statut de la partie de rez-de-chaussée non exploitée, et l'avancement du porter à connaissance inondation du 15 avril 2025 (bassin du Gapeau)",
            "<strong>Point de méthode :</strong> les loyers en place sont déjà au prix du marché — le prix d'offre ne peut donc pas s'appuyer sur un potentiel de revalorisation. Le seul gisement identifié (68 €/mois sur un lot) pèse 8 000 € de capacité de prix, et il n'est encaissable qu'à la rotation",
            "<strong>Rappel de marché (sources au 20/09/2026) :</strong> MeilleursAgents 2 020 €/m² pour les appartements et 12,4 €/m²/mois de loyer à Pignans ; DVF 2025 2 264 €/m² (18 ventes) ; PAP 2 150 €/m² ; annonces locatives relevées entre 560 € (33 m²) et 820 € (T3) ; 9 à 12 annonces en ligne sur la commune",
        ],
    )}

    gen.main()


if __name__ == '__main__':
    main()
