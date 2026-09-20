#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche Brignoles — immeuble de rapport 3 T3, centre ancien (SPR), 230 000 €.

Saisit l'entrée dans analyses.json puis genere la fiche HTML avec les chiffres
du moteur (analyse-annonce-immo : SCI a l'IS, 3 scenarios, note 40/30/20/10).
"""
import copy, importlib.util, json, os, sys

ROOT = '/home/alexis-barlatier/Documents/Semaphore-sonar'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from analyse_app import schema, engine

BASE = os.path.join(ROOT, 'analyses', 'analyses.json')
SLUG = "2026-09-20-immeuble-rapport-brignoles-centre-ancien"
URL = ("https://www.seloger.com/annonce/achat/provence-alpes-cote-d-azur/var-83/"
       "brignoles-83170/26GX1JRW1GBC")

RECORD = {
    "slug": SLUG,
    "date_analyse": "2026-09-20",
    "date_maj": None,
    "titre": "Brignoles — immeuble de rapport 3 T3 (196 m²) en centre ancien, Site Patrimonial Remarquable",
    "bien": {
        "type_bien": "immeuble",
        "sous_type": None,
        "type_detail": (
            "Immeuble de rapport en R+3 sur quatre niveaux, dans l'hyper-centre de Brignoles, à l'intérieur du "
            "périmètre du Site Patrimonial Remarquable classé par arrêté ministériel du 15 juin 2020. "
            "Trois T3 en étages : 64,06 m² au R+1, 67,84 m² au R+2, 64,57 m² au R+3 — soit 196,47 m² habitables — "
            "et des combles aménageables au quatrième niveau, d'une surface non communiquée. "
            "Immeuble sans ascenseur. Bâti ancien (pierres apparentes, tomettes d'origine, poutres). "
            "AUCUN DPE N'EST FOURNI : la fiche vendeur indique « diagnostic de performance énergétique vierge ». "
            "Aucun locataire n'est mentionné dans l'annonce : les trois logements sont présumés vacants. "
            "Les photographies de l'annonce montrent des logements « dans leur jus » : peintures écaillées, "
            "plomberie et électricité apparentes, chauffe-eau vétuste, traces d'humidité en plafond, "
            "menuiseries simple vitrage — alors que la fiche vendeur déclare « travaux à prévoir : aucun »."
        ),
        "neuf": False,
        "adresse": {
            "texte": "Centre ancien (périmètre SPR), Brignoles (83170) — adresse exacte non communiquée par le vendeur",
            "ville": "Brignoles",
            "code_postal": "83170"
        },
        "surfaces": {
            "texte": ("196,47 m² habitables (3 T3 : 64,06 + 67,84 + 64,57) — 197 m² annoncés. "
                      "Combles aménageables au 4e niveau : surface non communiquée"),
            "carrez_m2": 196.47
        },
        "lots": {
            "count": 3,
            "surface_par_lot_m2": None,
            "nature": "3 T3 en étages (64,06 / 67,84 / 64,57 m²) + combles aménageables au 4e niveau — sans ascenseur",
            "lots_distincts": 3
        },
        "copro": {
            "charges_annuelles_euros": 0.0,
            "charges_source": (
                "Aucune copropriété ni aucun syndic n'est mentionné : immeuble présumé en MONOPROPRIÉTÉ, donc sans charges "
                "de copropriété. À CONFIRMER : si l'immeuble est en copropriété, les charges et le budget prévisionnel "
                "doivent être obtenus, ce qui réduirait d'autant le cash flow (ordre de grandeur 8 à 12 €/m²/an pour un "
                "immeuble de centre ancien sans ascenseur, soit 1 600 à 2 400 €/an)."
            )
        },
        "travaux": {
            "montant_euros": 120000.0,
            "nature": (
                "RÉNOVATION COMPLÈTE des trois logements, provisionnée 120 000 € (≈ 610 €/m² habitable) : reprise de "
                "l'électricité et de la plomberie (apparentes sur les photos), salles de bains et cuisines, sols, "
                "peintures, traitement de l'humidité en plafond, menuiseries en double vitrage conformes au SPR et "
                "chauffage. FOURCHETTE 80 000 à 200 000 € selon le devis : 80 000 € (≈ 400 €/m²) pour une remise en "
                "état locative minimale — électricité, salles de bains, peintures — et 200 000 € (≈ 1 000 €/m²) si la "
                "toiture, la structure ou les réseaux sont à reprendre. Dans un SPR, les menuiseries et les façades "
                "relèvent de l'accord de l'Architecte des bâtiments de France : délais et surcoûts à prévoir. "
                "AUCUN DEVIS N'A ÉTÉ ÉTABLI : c'est le premier point bloquant du dossier."
            )
        }
    },
    "annonce": {
        "plateforme": "seloger",
        "url": URL,
        "prix_affiche_euros": 230000.0,
        "prix_retenu_euros": None,
        "prix_statut": "affiche",
        "prix_commentaire": (
            "230 000 €, honoraires à la charge du vendeur, soit 1 168 €/m² sur les 197 m² annoncés (1 171 €/m² sur les "
            "196,47 m² réellement habitables). Le vendeur est CASAVO (SAS PROPRIOO, RCS 824117345) : un intermédiaire "
            "qui achète pour revendre, ce qui explique un dossier sans DPE et sans locataire. "
            "Le même bien est diffusé sur LeBonCoin (réf. 3222843686), Logic-Immo (réf. 273406483) et Figaro Immo "
            "(réf. 62075) — pas d'enchère croisée, un seul vendeur."
        )
    },
    "marche": {
        "valeur": {
            "basse_euros": 250000.0,
            "haute_euros": 330000.0,
            "retenue_euros": 285000.0,
            "source": (
                "Trois sources convergentes. (1) MeilleursAgents au 01/09/2026 : 2 250 €/m² en moyenne communale et "
                "1 865 €/m² sur le quartier Centre / Vieille-Ville — c'est cette dernière qui compte. (2) DVF 2025 : "
                "2 388 €/m² en moyenne communale sur 189 ventes d'appartements (Immovrai), moyenne tirée vers le haut "
                "par le neuf et les quartiers récents. (3) Les immeubles entiers effectivement en vente dans le centre "
                "de Brignoles le 20/09/2026 se traitent entre 1 168 et 1 467 €/m² (176 m² à 210 000 €, 220 m² à "
                "275 000 €, 300 m² à 440 000 €, 525 m² à 627 000 €). Valeur retenue après travaux 285 000 €, soit "
                "1 450 €/m² : une décote de 22 % sur le prix/m² du quartier, justifiée par l'absence d'ascenseur, "
                "l'absence de parking, l'obligation de vente en bloc et la profondeur du marché local. "
                "Fourchette 250 000 à 330 000 €. À noter : la valeur ne doit pas être majorée des combles, dont la "
                "surface n'est même pas communiquée."
            ),
            "confiance": "moyenne"
        },
        "loyers": [
            {"lot": "T3 de 64,06 m² (R+1)", "quantite": 1, "loyer_mensuel_euros": 660.0, "occupe": False,
             "note": ("10,3 €/m². Retenu sous la médiane des annonces relevées à Brignoles le 20/09/2026 pour des T3 "
                      "de 60 à 75 m² (550, 615, 720, 750, 820, 827, 880 et 910 €/mois selon état et meublement), et "
                      "nettement sous la moyenne MeilleursAgents de 13,2 €/m². Lot présumé vacant.")},
            {"lot": "T3 de 67,84 m² (R+2)", "quantite": 1, "loyer_mensuel_euros": 660.0, "occupe": False,
             "note": ("9,7 €/m². Deuxième étage sans ascenseur : c'est la décote qui explique le loyer retenu, "
                      "inférieur au prix au m² du R+1. Lot présumé vacant.")},
            {"lot": "T3 de 64,57 m² (R+3)", "quantite": 1, "loyer_mensuel_euros": 660.0, "occupe": False,
             "note": ("10,2 €/m². Dernier étage sous toiture, exposé aux déperditions : loyer retenu identique, à "
                      "confirmer après diagnostic de couverture. Lot présumé vacant.")},
        ],
        "notes": (
            "Loyers retenus 3 × 660 € = 1 980 €/mois, soit 23 760 €/an et 10,2 €/m² — le bas de la fourchette "
            "constatée, conformément à la règle du groupe : on ne construit pas un prix sur la borne haute des "
            "loyers. RENDU APRÈS RÉNOVATION seulement : l'immeuble est en mauvais état et aucun des trois logements "
            "ne peut être loué en l'état (voir le risque « permis de louer »). Le parc locatif de Brignoles compte "
            "33 appartements en annonce le 20/09/2026 : la relocation de trois lots simultanés n'est pas un marché "
            "de pénurie, elle prendra plusieurs mois."
        )
    },
    "hypotheses": {
        "vacance_base_pct": 8.0,
        "vacance_best_pct": 5.0,
        "vacance_worst_pct": 15.0,
        "vacance_justification": (
            "ÉCART ASSUMÉ AU DÉFAUT RÉSIDENTIEL (5 %). Trois raisons : (1) l'immeuble est vendu SANS locataire — les "
            "trois logements sont à relouer en même temps, ce qui n'est pas de la vacance statistique mais un revenu "
            "absent le premier jour ; (2) chaque relocation exige une autorisation préalable de mise en location "
            "(permis de louer, dispositif en vigueur à Brignoles et renouvelé pour 2026), avec visite de conformité "
            "et délai d'un mois ; (3) l'offre locative locale est abondante (33 appartements en annonce), donc les "
            "délais s'allongent. Worst 15 % : deux lots vides en simultané et un impayé."
        ),
        "frais_acquisition_euros": 18400.0,
        "frais_divers_euros": 0.0,
        "charges": {
            "taxe_fonciere_annuelle_euros": 2619.0,
            "taxe_fonciere_commentaire": (
                "Chiffre du vendeur (fiche Casavo et LeBonCoin : « taxe foncière 2 619 €/an »), soit 11 % du loyer "
                "brut retenu — sous le seuil d'alerte de 15 %, mais élevé pour un immeuble sans ascenseur et sans "
                "parties communes développées : à vérifier sur l'avis réel avant toute offre."
            ),
            "charges_copro_annuelles_euros": 0.0,
            "charges_copro_commentaire": (
                "Immeuble présumé en monopropriété (aucun syndic ni aucune copropriété mentionnés) : pas de charges "
                "de copropriété. À CONFIRMER — si l'immeuble est en copropriété, compter 1 600 à 2 400 €/an."
            ),
            "pno_annuelle_euros": 400.0,
            "pno_commentaire": "Assurance de l'immeuble (trois logements et parties communes).",
            "entretien_annuel_euros": 1200.0,
            "entretien_commentaire": (
                "Entretien courant de l'immeuble : cage d'escalier, façade, couverture, évacuations. Sans syndic, "
                "le propriétaire porte tout."
            ),
            "comptabilite_annuelle_euros": 0.0,
            "comptabilite_commentaire": (
                "Aucune ligne de comptabilité : la SCI porte déjà d'autres biens, le poste est mutualisé "
                "(convention du groupe)."
            )
        }
    },
    "analyse": {
        "branche": "residentiel",
        "type_operation": "locatif",
        "strategie_retenue": {
            "nom": "Rénovation complète des trois logements puis location nue",
            "code": "ld-nue",
            "lots": 3
        },
        "strategies_explorees": [
            {"strategie": "Rénovation complète puis location nue des trois T3", "lots": 3,
             "rendement": "4,4 % net sur le revient / 5,7 % sur la valeur",
             "faisabilite": "3 à 6 mois de travaux, 3 logements à relouer",
             "risque": "élevé — 120 000 € de travaux provisionnés et un DPE inconnu"},
            {"strategie": "Aménagement des combles en quatrième logement", "lots": 4,
             "rendement": "potentiel non chiffrable",
             "faisabilite": "soumise à l'accord de l'Architecte des bâtiments de France (SPR)",
             "risque": "élevé — surface du comble non communiquée, règles de hauteur et de création de surface"},
            {"strategie": "Mise en location en l'état, sans travaux", "lots": 3,
             "rendement": "non calculable",
             "faisabilite": "bloquée par le permis de louer",
             "risque": "élevé — logements non conformes à la décence et sans DPE : la mairie peut refuser la mise en location"},
            {"strategie": "Marchand de biens : rénovation puis revente à l'unité", "lots": 3,
             "rendement": "-88 000 € de plus-value nette",
             "faisabilite": "division en copropriété à créer",
             "risque": "rédhibitoire — le prix de revente au détail ne couvre pas la rénovation"}
        ],
        "attractivite": [
            {"dimension": "transports", "score": 5,
             "justification": "Brignoles n'a pas de gare voyageurs : la desserte repose sur l'autocar (réseau régional) et sur l'accès A8 par la sortie de Saint-Maximin. Toulon et Aix sont à 45 minutes, Marseille à une heure. Centre-ville tout à pied."},
            {"dimension": "commerces", "score": 8,
             "justification": "Hyper-centre commerçant : marché hebdomadaire, administrations, sous-préfecture, santé, deux supermarchés à moins de 500 m. Le point fort réel du dossier, et la raison pour laquelle les logements d'hyper-centre se relouent."},
            {"dimension": "ecoles", "score": 7,
             "justification": "Commune de 15 000 habitants dotée de plusieurs groupes scolaires, d'un collège et du lycée Raynouard ; alimentation en personnel administratif et enseignant, profil de locataire recherché."},
            {"dimension": "securite", "score": 5,
             "justification": "Pas de quartier prioritaire, centre ancien animé le jour. Mais la vieille ville concentre des logements vacants et dégradés — le dispositif de permis de louer de la commune en est le symptôme. Immobilier de centre ancien pénalisé à la revente."},
            {"dimension": "demande_locative", "score": 6,
             "justification": "Demande réelle portée par les actifs, les professions libérales et les fonctionnaires, mais offre abondante : 33 appartements en location à Brignoles le 20/09/2026, dont une majorité de T2 et T3. Ce n'est pas un marché de pénurie ; les délais de relocation y sont moyens."},
            {"dimension": "dynamisme", "score": 5,
             "justification": "Sous-préfecture du centre Var, agglomération de la Provence Verte. Prix stables (+0,8 % sur un an pour les appartements, -3,0 % sur trois mois selon MeilleursAgents), 189 ventes d'appartements en 2025. Marché peu liquide : les immeubles entiers s'y revendent en un à deux ans."}
        ],
        "risques": [
            {"facteur": "Aucun DPE fourni — location possiblement interdite", "severite": 5,
             "detail": "La fiche vendeur indique « diagnostic de performance énergétique vierge » : il n'y a pas d'évaluation énergétique. Un DPE est obligatoire pour vendre et pour louer ; son absence n'est pas un oubli, c'est un évitement. Si le bâti ancien (simple vitrage visible sur les photos, chauffage inconnu, pierres apparentes non isolées) ressort en F ou G, la mise en location est interdite — G depuis le 1er janvier 2025 pour les nouveaux baux, F à partir de 2028, E en 2034. Or dans un SPR, la rénovation énergétique est la plus contrainte qui existe : pas d'isolation thermique par l'extérieur possible, menuiseries à valider par l'Architecte des bâtiments de France. CONDITION SUSPENSIVE N°1 : obtenir les trois DPE avant toute offre."},
            {"facteur": "Travaux très lourds contredits par la fiche vendeur", "severite": 5,
             "detail": "Le vendeur déclare « travaux à prévoir : aucun ». Les photographies de l'annonce montrent trois logements dans leur jus : peintures écaillées et cloques, plomberie et électricité apparentes hors normes, chauffe-eau vétuste, traces d'humidité en plafond, carrelages usés, cuisine réduite à un évier et des placards. Une rénovation complète de trois logements de 65 m², c'est 80 000 à 200 000 € selon la profondeur. L'écart entre les deux hypothèses vaut 120 000 € de prix d'achat : c'est le cœur du dossier, et il n'est pas tranché."},
            {"facteur": "Permis de louer — autorisation préalable obligatoire", "severite": 4,
             "detail": "Brignoles applique le permis de louer, renouvelé pour 2026 : chaque mise en location exige une autorisation préalable, délivrée après visite de conformité, pour deux ans. Trois logements à relouer, c'est trois dossiers et trois visites. Un logement déclaré non conforme (humidité, électricité, ventilation) ne peut pas être loué, et l'autorisation prend un mois. Le dispositif verrouille la montée en loyer d'un immeuble acheté en mauvais état : la trésorerie doit tenir la période."},
            {"facteur": "Argument Malraux inopérant", "severite": 4,
             "detail": "L'annonce vend le classement en SPR comme « un levier fiscal exceptionnel » via le dispositif Malraux. Double problème. (1) Depuis 2025, Malraux n'existe plus que dans les SPR dotés d'un plan de sauvegarde et de mise en valeur approuvé (30 %) ou d'un plan de valorisation de l'architecture et du patrimoine (22 %) ; les quartiers anciens dégradés sont sortis du dispositif au 31/12/2024. À Brignoles, seuls l'arrêté de classement du 15 juin 2020 et l'étude préalable de 2018 sont publiés — aucune trace d'un PSMV ou d'un PVAP approuvé, à vérifier en mairie. (2) La réduction Malraux s'impute sur l'impôt sur le revenu des personnes physiques : elle est incompatible avec une détention en SCI à l'IS. L'argument fiscal de l'annonce ne vaut donc rien dans notre montage — et ne doit pas se payer dans le prix."},
            {"facteur": "Marché de revente encombré", "severite": 4,
             "detail": "22 immeubles sont en vente à Brignoles le 20/09/2026, dont sept dans le seul centre ancien, entre 1 168 et 1 467 €/m². L'affirmation de l'annonce — « la rareté de ce type de bien en centre historique en renforce durablement la valeur » — est démentie par l'offre disponible. La sortie d'un immeuble entier à Brignoles se compte en années, pas en mois : c'est un actif de rendement, pas de plus-value."},
            {"facteur": "Bâti ancien : couverture, structure, humidité", "severite": 4,
             "detail": "Les traces d'humidité visibles en plafond, un troisième étage sous toiture et l'absence de tout diagnostic technique (structure, couverture, amiante, plomb, termites) laissent ouverte la seule dépense qui ne se négocie pas : la toiture. Aucun plan, aucun diagnostic, aucune facture d'entretien n'accompagne l'annonce."},
            {"facteur": "Contraintes du Site Patrimonial Remarquable", "severite": 3,
             "detail": "Toute intervention sur les façades, les menuiseries, la couverture ou une création de surface en combles relève de l'Architecte des bâtiments de France. Cela signifie des menuiseries bois sur mesure plutôt que du PVC de série, des délais d'instruction allongés et des arbitrages esthétiques imposés. Dans un immeuble dont tout le sujet est la facture de rénovation, ce n'est pas un détail : c'est un surcoût structurel de 10 à 20 %."},
            {"facteur": "Statut de copropriété non communiqué", "severite": 2,
             "detail": "L'annonce ne dit ni si l'immeuble est en copropriété, ni s'il existe un syndic, ni s'il y a des lots annexes. La fiche vendeur mentionne seulement « procédure en cours : non, travaux votés : aucun ». Un budget prévisionnel écrit doit être obtenu avant toute offre : si l'immeuble est en copropriété, c'est 1 600 à 2 400 €/an de charges en plus."},
            {"facteur": "Taxe foncière élevée au regard du loyer", "severite": 2,
             "detail": "2 619 €/an annoncés, soit 11 % des loyers bruts retenus, pour un immeuble de 196 m² sans ascenseur. C'est sous le seuil d'alerte de 15 %, mais l'avis réel doit être produit : une valeur locative cadastrale surévaluée sur un immeuble ancien se conteste, elle ne se subit pas."}
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
    json.dump(data, open(BASE, 'w'), ensure_ascii=False, indent=1)
    print(f"record ajoute : {SLUG} | total {data['meta']['count']} fiches")

    spec = importlib.util.spec_from_file_location("gen", os.path.join(ROOT, 'scripts', 'gen_fiches_2026-09-10.py'))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)

    def eur(v):
        return f"{v:,.0f}".replace(',', ' ')

    def ligne(label, val, cls=""):
        c = f' class="{cls}"' if cls else ''
        return f'            <tr{c}><td>{label}</td><td class="num">{val}</td></tr>'

    def scenario_html(rec, vac):
        v = copy.deepcopy(rec)
        v['hypotheses']['vacance_base_pct'] = vac
        r = engine.compute(v)
        f = r['fiscal']
        rev = r['revenus_bruts_annuels']
        ch = rec['hypotheses']['charges']
        prov = round(rev * 0.025, 2)
        vac_eur = round(rev * vac / 100.0, 2)
        cf_reint = (f['ebe'] - f['is_annuel'] + f['amortissement']) / 12.0
        rows = [
            ligne("Revenu brut annuel", f"{eur(rev)} €"),
            ligne(f"Vacance locative ({vac:.0f} %)", f"-{eur(vac_eur)} €"),
            ligne("Taxe foncière (chiffre vendeur)", f"-{eur(ch['taxe_fonciere_annuelle_euros'])} €"),
            ligne("Entretien de l'immeuble", f"-{eur(ch['entretien_annuel_euros'])} €"),
            ligne("Assurance PNO", f"-{eur(ch['pno_annuelle_euros'])} €"),
            ligne("Charges de copropriété", "néant (monopropriété présumée)", ""),
            ligne("Provision travaux 2,5 % (règle interne)", f"-{eur(prov)} €"),
            ligne("EBE avant IS", f"{eur(f['ebe'])} €", "subtotal"),
            ligne("Amortissement du bâti (90 % du revient / 30 ans)", f"{eur(f['amortissement'])} €"),
            ligne("Résultat fiscal", f"{eur(f['resultat_fiscal'])} €"),
            ligne("IS (15 %)", f"-{eur(f['is_annuel'])} €"),
            ligne("CF net mensuel après IS", f"{eur(f['cf_mensuel_net'])} €", "highlight"),
            ligne("CF amort. réintégré (mensuel)", f"{eur(cf_reint)} €"),
            ligne("Rendement net sur prix de revient", f"{r['rendements']['net_sur_revient_pct']:.1f} %".replace('.', ',')),
            ligne("Rendement net sur valeur de marché", f"{r['rendements']['net_sur_valeur_pct']:.1f} %".replace('.', ',')),
        ]
        return r, "\n".join(rows)

    def bloc_scenarios(rec, titre, intro, loyers_base=None):
        rb, rows_b = scenario_html(rec, rec['hypotheses']['vacance_base_pct'])
        ro, rows_o = scenario_html(rec, rec['hypotheses']['vacance_best_pct'])
        rp, rows_p = scenario_html(rec, rec['hypotheses']['vacance_worst_pct'])
        rd = lambda r: f"{r['rendements']['net_sur_revient_pct']:.1f}".replace('.', ',')
        rv = lambda r: f"{r['rendements']['net_sur_valeur_pct']:.1f}".replace('.', ',')
        cf = lambda r: eur(r['fiscal']['cf_mensuel_net'])
        return f"""  <section class="financial-projections">
    <h2>Projections financières — prix affiché {eur(rec['annonce']['prix_affiche_euros'])} €, SCI à l'IS</h2>
    <p class="attractiveness-intro">{intro}</p>
    <div class="projections-grid">
      <div class="projection-card scenario-base">
        <h3>Scénario Base</h3>
        <p class="scenario-subtitle">Vacance {rec['hypotheses']['vacance_base_pct']:.0f} % — trois logements à relouer, 120 000 € de travaux provisionnés</p>
        <table class="projection-table"><tbody>
{rows_b}
        </tbody></table>
      </div>
      <div class="projection-card scenario-optimiste">
        <h3>Scénario Optimiste</h3>
        <p class="scenario-subtitle">Vacance {rec['hypotheses']['vacance_best_pct']:.0f} % — relocation rapide des trois lots, travaux tenus à 120 000 €</p>
        <table class="projection-table"><tbody>
{rows_o}
        </tbody></table>
      </div>
      <div class="projection-card scenario-pessimiste">
        <h3>Scénario Pessimiste</h3>
        <p class="scenario-subtitle">Vacance {rec['hypotheses']['vacance_worst_pct']:.0f} % — deux lots vides en simultané, un impayé, travaux dérivés</p>
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
        <tr><td>CF amort. réintégré (mensuel)</td><td class="num">{eur((rb['fiscal']['ebe'] - rb['fiscal']['is_annuel'] + rb['fiscal']['amortissement']) / 12)} €</td><td class="num">{eur((ro['fiscal']['ebe'] - ro['fiscal']['is_annuel'] + ro['fiscal']['amortissement']) / 12)} €</td><td class="num">{eur((rp['fiscal']['ebe'] - rp['fiscal']['is_annuel'] + rp['fiscal']['amortissement']) / 12)} €</td></tr>
        <tr><td>Rendement net (prix de revient)</td><td class="num">{rd(rb)} %</td><td class="num">{rd(ro)} %</td><td class="num">{rd(rp)} %</td></tr>
        <tr><td>Rendement net (valeur de marché)</td><td class="num">{rv(rb)} %</td><td class="num">{rv(ro)} %</td><td class="num">{rv(rp)} %</td></tr>
        <tr><td>Ratio coût / valeur</td><td class="num">{rb['ratio_cout_valeur']:.2f}</td><td class="num">{ro['ratio_cout_valeur']:.2f}</td><td class="num">{rp['ratio_cout_valeur']:.2f}</td></tr>
      </tbody>
    </table>
    <div class="risk-matrix"><p class="attractiveness-intro">{gen.LECTURE[rec['slug']]}</p></div>
    <p class="attractiveness-intro"><strong>Sensibilité du prix plafond à l'enveloppe de travaux</strong> (ratio coût/valeur = 1,00, valeur retenue 285 000 €, frais d'acquisition 8 %) : 80 000 € de travaux → plafond 190 000 € ; 100 000 € → 171 000 € ; 120 000 € → 153 000 € ; 160 000 € → 116 000 €. À 230 000 €, il faudrait que la rénovation complète des trois logements tienne dans 22 000 € — soit 112 €/m², l'équivalent d'un rafraîchissement de peinture, et rien d'autre.</p>
  </section>"""

    gen.bloc_scenarios = bloc_scenarios

    gen.LECTURE[SLUG] = (
        "Ici, le prix n'est pas le problème : 1 168 €/m², c'est le bas du marché des immeubles du centre de Brignoles, "
        "et c'est 37 % sous le prix au m² du quartier Centre / Vieille-Ville. Le problème, c'est ce que le vendeur ne dit pas. "
        "Pas de DPE — obligatoire pour vendre et pour louer. Pas de locataire — trois logements à relouer en même temps. "
        "Et une fiche qui déclare « aucun travaux à prévoir » quand les photographies montrent trois appartements dans leur "
        "jus : plomberie et électricité apparentes, peintures écaillées, traces d'humidité, simple vitrage. "
        "Une rénovation complète de 196 m², c'est 80 000 à 200 000 € dans un bâti ancien d'un Site Patrimonial Remarquable, "
        "où les menuiseries et les façades passent par l'Architecte des bâtiments de France. Le dossier ne se juge donc pas "
        "sur le prix affiché mais sur le prix affiché PLUS les travaux : 368 400 € de revient pour 285 000 € de valeur, "
        "un ratio de 1,29. À ce niveau, chaque euro investi crée moins d'un euro de valeur."
    )

    gen.CONF = {SLUG: dict(
        titre_court="Immeuble 3 T3, centre ancien, Brignoles",
        adresse="Centre ancien (Site Patrimonial Remarquable), Brignoles (83170) — immeuble de 196 m², 3 T3 + combles",
        date_fr="20 septembre 2026",
        source="SeLoger — annonce 26GX1JRW1GBC (CASAVO, SAS PROPRIOO) — également diffusée sur LeBonCoin, Logic-Immo et Figaro Immo (réf. 62075)",
        url=URL,
        badge="Investissement locatif",
        strategie="Rénovation complète des trois logements puis location nue",
        fiscal_note="SCI à l'IS (15 %), amortissement sur 90 % du prix de revient sur 30 ans",
        lat="43.4058", lon="6.0617",
        quartier="centre ancien de Brignoles (83170), périmètre du Site Patrimonial Remarquable",
        intro_attr=(
            "Le bien est situé dans l'hyper-centre de Brignoles (15 000 habitants, sous-préfecture du Var), à l'intérieur du "
            "périmètre du Site Patrimonial Remarquable classé en 2020. Les prix du quartier Centre / Vieille-Ville ressortent à "
            "<strong>1 865 €/m²</strong> selon MeilleursAgents au 01/09/2026, contre 2 250 €/m² en moyenne communale : la vieille "
            "ville se traite 17 % sous le reste de Brignoles, et les immeubles entiers entre 1 168 et 1 467 €/m². "
            "Les loyers des T3 de 60 à 75 m² effectivement affichés à Brignoles le 20/09/2026 vont de 550 à 830 €/mois "
            "(9 à 12 €/m²), pour une moyenne MeilleursAgents de 13,2 €/m². Le prix demandé, <strong>1 168 €/m²</strong>, "
            "est donc bas pour un immeuble — mais il porte sur 196 m² qui n'ont pas été rénovés depuis des décennies."
        ),
        profil="actifs, professions libérales et fonctionnaires travaillant à Brignoles ou dans la Provence Verte, couples sans enfant et petits ménages à la recherche d'un T3 de centre-ville avec du cachet",
        concl_attr=(
            "Adéquation moyenne (6,0/10). L'emplacement est le vrai atout : hyper-centre commerçant, marché, administrations, "
            "tout à pied — c'est exactement le profil de bien qui se reloue à Brignoles, et le format T3 correspond à la demande "
            "locale. Mais deux réserves pèsent sur l'adéquation. D'abord le centre ancien lui-même : la commune applique le permis "
            "de louer, signe d'un parc dégradé qui se reloue mal et se revend plus mal encore. Ensuite le marché : 33 appartements "
            "en location et 22 immeubles en vente à Brignoles le 20/09/2026 — la rareté annoncée par le vendeur n'existe pas."
        ),
        intro_strat=(
            "Quatre lectures ont été testées : la rénovation complète suivie d'une location nue, l'aménagement des combles en "
            "quatrième logement, la mise en location sans travaux, et l'achat-rénovation-revente à l'unité. "
            "La troisième est écartée d'emblée — sans DPE et sans conformité à la décence, la commune peut refuser la mise en "
            "location. La quatrième est chiffrée et perd de l'argent. Reste la rénovation, avec un prix d'entrée à renégocier."
        ),
        rationale=(
            "La rénovation complète est la seule stratégie qui a un sens ici, parce que rien d'autre n'est louable en l'état : "
            "ni le permis de louer, ni la décence, ni l'absence de DPE ne permettent de mettre les trois logements sur le marché "
            "tels quels. Elle est chiffrée avec <strong>120 000 € de travaux</strong> (≈ 610 €/m²), fourchette 80 000 à 200 000 €.<br><br>"
            "À 230 000 € affichés, le prix de revient atteint <strong>368 400 €</strong> — 230 000 € de prix, 18 400 € de frais "
            "d'acquisition, 120 000 € de travaux — pour une valeur après travaux de <strong>285 000 €</strong> : un ratio coût/valeur "
            "de <strong>1,29</strong>. Autrement dit, l'opération détruit 83 000 € de valeur. Le rendement net ressort à 4,4 % sur le "
            "prix de revient et 5,7 % sur la valeur de marché, et le scénario pessimiste tombe à 2,9 %. Le prix qui rétablit "
            "l'équilibre est de <strong>153 000 €</strong> avec 120 000 € de travaux, ou de <strong>190 000 €</strong> si un devis "
            "ramène la rénovation à 80 000 €.<br><br>"
            "Deux autres pistes ont été testées sérieusement. Les <strong>combles aménageables</strong>, d'abord : leur surface n'est "
            "même pas communiquée, et dans un SPR toute création de surface habitable en dernier niveau passe par l'Architecte des "
            "bâtiments de France. C'est un bonus éventuel, jamais un élément de prix. La <strong>revente à l'unité</strong>, ensuite : "
            "les trois T3 représentent 196 m², qui valent environ 366 000 € au prix du quartier (1 865 €/m²), soit 344 000 € nets "
            "d'honoraires. Face à un revient de 368 400 €, plus les frais de division et le portage, la plus-value nette est négative "
            "d'environ 88 000 €. Le détail ne justifie pas le bloc : il faut soit louer, soit renoncer.<br><br>"
            "Reste la question qui décide de tout : <strong>de combien sont réellement les travaux ?</strong> Le vendeur répond "
            "« aucun », ses propres photographies répondent le contraire. L'écart entre 80 000 € et 200 000 € vaut 120 000 € de prix "
            "d'achat : rien ne se décide avant un devis."
        ),
        identite=[
            ("Adresse", "Centre ancien de Brignoles (83170), dans le périmètre du Site Patrimonial Remarquable — adresse exacte non communiquée par le vendeur"),
            ("Composition", "R+3 sur quatre niveaux : <strong>trois T3 de 64,06 / 67,84 et 64,57 m²</strong> aux 1er, 2e et 3e étages, soit 196,47 m² habitables, et <strong>combles aménageables</strong> au 4e niveau (surface non communiquée)"),
            ("Bâti", "Immeuble ancien : pierres apparentes, tomettes d'origine, poutres. <strong>Sans ascenseur</strong>"),
            ("Occupation", "<strong>Aucun locataire mentionné</strong> : les trois logements sont présumés vacants. Pas de bail, pas de quittance, pas de loyer d'exploitation"),
            ("DPE / GES", "<strong>AUCUN DPE FOURNI</strong> — la fiche vendeur indique « diagnostic de performance énergétique vierge ». Un DPE est obligatoire pour vendre et pour louer : sans lui, ni la relocation ni la vérification de la conformité ne sont possibles"),
            ("Prix affiché", "<strong>230 000 €</strong>, honoraires à la charge du vendeur, soit <strong>1 168 €/m²</strong> (1 171 €/m² sur les 196,47 m² habitables)"),
            ("Valeur de marché retenue", "250 000 à 330 000 €, retenue <strong>285 000 €</strong> (1 450 €/m²) : prix/m² du quartier Centre / Vieille-Ville à 1 865 €, décote de bloc de 22 %"),
            ("Loyers retenus", "<strong>3 × 660 € = 1 980 €/mois</strong>, soit 10,2 €/m² — annonces constatées à Brignoles : 550, 615, 720, 750, 820, 827 et 880 €/mois pour des T3 de 60 à 75 m²"),
            ("Travaux", "<strong>120 000 € provisionnés</strong> (≈ 610 €/m²) : électricité, plomberie, salles de bains, cuisines, sols, peintures, humidité, menuiseries, chauffage. <strong>Fourchette 80 000 à 200 000 €</strong> — aucun devis établi"),
            ("Charges annuelles", "Taxe foncière <strong>2 619 €</strong> (chiffre vendeur) + entretien immeuble 1 200 € + assurance PNO 400 € + provision travaux 2,5 % = <strong>4 813 €/an</strong> hors vacance. Charges de copropriété : néant, immeuble présumé en monopropriété (à confirmer)"),
            ("Fiscalité", "SCI à l'IS : IS 15 % sur le résultat, amortissement de 90 % du prix de revient sur 30 ans. Le dispositif Malraux invoqué par l'annonce est sans effet dans une SCI à l'IS"),
            ("Prix de revient à l'affichage", "<strong>368 400 €</strong> = prix 230 000 € + frais d'acquisition 18 400 € (8 %) + travaux 120 000 €"),
        ],
        stance=(
            "<strong>À négocier — et la négociation commence 35 % sous l'affichage : 153 000 € avec 120 000 € de travaux, "
            "190 000 € si un devis ramène la rénovation à 80 000 €.</strong> Le dossier n'est pas absurde : le prix au m² est bas "
            "(1 168 €/m², contre 1 865 €/m² pour le quartier), l'emplacement d'hyper-centre est le bon pour du locatif à Brignoles, "
            "et trois T3 de 65 m² constituent un format qui se reloue. Mais tel qu'il est présenté, il ne passe pas. "
            "À 230 000 €, le prix de revient monte à <strong>368 400 €</strong> pour une valeur après travaux de <strong>285 000 €</strong> : "
            "un ratio coût/valeur de 1,29, qui signifie que l'euro investi crée 0,77 € de valeur. Le rendement net ressort à 4,4 % "
            "sur le revient et 5,7 % sur la valeur, quand notre seuil est à 6,5 %. Le scénario pessimiste tombe à 2,9 % et 490 €/mois "
            "de cash flow.<br><br>"
            "Trois faits commandent la décote, et deux d'entre eux sont écrits noir sur blanc dans le dossier du vendeur. "
            "Le <strong>DPE est « vierge »</strong> : un F ou un G interdirait purement et simplement la mise en location, et la "
            "rénovation énergétique d'un bâti en pierre dans un site patrimonial est la plus chère et la plus contrainte qui existe. "
            "Les <strong>photographies contredisent la fiche</strong> : « travaux à prévoir : aucun », alors que les pièces montrent "
            "des réseaux apparents, des peintures écaillées, un chauffe-eau vétuste et des traces d'humidité. "
            "Enfin l'argument <strong>Malraux est inopérant</strong> : depuis 2025, le dispositif suppose un plan de sauvegarde et "
            "de mise en valeur approuvé, dont nous ne trouvons aucune trace à Brignoles — et il s'impute sur l'impôt sur le revenu, "
            "pas sur une SCI à l'IS. Rien de tout cela ne se paie dans le prix.<br><br>"
            "<strong>La décision se prend donc en deux temps.</strong> Avant toute offre, deux pièces sont indispensables et "
            "elles ne coûtent rien : les trois DPE et un devis de rénovation. Avec un devis à 120 000 €, le plafond est de 153 000 € "
            "et le dossier redevient cohérent — rendement net de 4,5 % sur le revient, 5,5 % sur la valeur, 1 316 €/mois de cash flow. "
            "Si le devis ressort à 200 000 €, le plafond tombe à 79 000 € : le dossier est mort, il n'y a rien à négocier. "
            "Si, à l'inverse, la visite révèle trois logements en meilleur état que les photos — 60 000 € de travaux — le plafond "
            "remonte à 208 000 € et le bien devient un vrai dossier de parc. <strong>Tant que l'état n'est pas chiffré, aucun prix "
            "n'est défendable : cette analyse fixe la méthode et les bornes, pas un engagement.</strong>"
        ),
        prix_plafond=(
            "<strong>153 000 €</strong> net vendeur avec 120 000 € de travaux (ratio coût/valeur de 1,00, valeur retenue 285 000 €, "
            "frais d'acquisition 8 %) ; <strong>139 000 €</strong> pour créer réellement de la valeur (ratio 0,95). "
            "Grille de sensibilité : 80 000 € de travaux → 190 000 € ; 100 000 € → 171 000 € ; 120 000 € → 153 000 € ; "
            "160 000 € → 116 000 € ; 200 000 € → 79 000 €. À 230 000 €, il faudrait que la rénovation complète des trois "
            "logements tienne dans 22 000 €, soit 112 €/m² : une couche de peinture, rien de plus. "
            "Toute offre doit être conditionnée à la production des trois DPE et d'un devis de rénovation par corps d'état."
        ),
        leviers=[
            "Le DPE absent est le premier levier, et il est incontestable : la vente d'un bien sans DPE est irrégulière, et la location l'est aussi. Demander les trois diagnostics avant toute discussion de prix renverse le rapport de force — le vendeur sait ce que ces diagnostics vont dire, sinon il les aurait produits",
            "La contradiction entre la fiche et les photographies est le levier chiffrable : « travaux à prévoir : aucun » d'un côté, plomberie et électricité apparentes, peintures écaillées, traces d'humidité et simple vitrage de l'autre. Un devis d'artisan transforme cette contradiction en montant opposable",
            "L'argument Malraux de l'annonce ne tient pas : depuis 2025 le dispositif exige un PSMV ou un PVAP approuvé (aucune trace à Brignoles, seuls l'arrêté de classement de 2020 et l'étude préalable de 2018 sont publiés), et il s'impute sur l'impôt sur le revenu, donc hors SCI à l'IS. Aucune « prime de défiscalisation » ne se justifie dans le prix",
            "La rareté annoncée est démentie par le marché : 22 immeubles en vente à Brignoles le 20/09/2026, dont sept dans le centre ancien, entre 1 168 et 1 467 €/m². L'offre abondante et la lenteur des ventes d'immeubles entiers sont des arguments de décote, pas de rareté",
            "Le permis de louer de Brignoles verrouille la montée en loyer : trois logements à faire autoriser, une visite de conformité chacun, un mois de délai par dossier, et aucun revenu tant que les travaux ne sont pas conformes. C'est une charge de trésorerie à faire porter au vendeur",
            "Les combles aménageables ne doivent jamais entrer dans le prix : surface non communiquée, faisabilité soumise à l'Architecte des bâtiments de France et règles de hauteur. À traiter comme un bonus à documenter, ou comme un argument de vente du vendeur — pas comme une valeur",
            "La taxe foncière annoncée, 2 619 €/an, représente 11 % des loyers bruts pour un immeuble sans ascenseur : demander l'avis réel et vérifier la valeur locative cadastrale, qui se conteste si elle est surévaluée",
            "Le vendeur est un intermédiaire (CASAVO, SAS PROPRIOO) qui achète pour revendre : il a un prix d'entrée, un coût de portage et une date de sortie. C'est le seul profil de vendeur avec lequel une décote forte se discute sur des devis, pas sur des impressions",
        ],
        meta=[
            "<strong>Régime fiscal retenu :</strong> SCI à l'IS (15 %) — amortissement sur 90 % du prix de revient sur 30 ans — provision travaux de 2,5 % des revenus (règle interne). Le dispositif Malraux est écarté : inapplicable en SCI à l'IS et subordonné à un PSMV/PVAP approuvé",
            "<strong>Frais d'acquisition :</strong> 18 400 € (8 % du prix affiché, barème de l'ancien)",
            "<strong>Enveloppe travaux :</strong> 120 000 € provisionnés (≈ 610 €/m²), fourchette 80 000 à 200 000 €. Aucun devis n'a été établi — c'est le premier point bloquant, l'écart vaut 120 000 € de prix",
            "<strong>Contrôles à faire avant toute offre :</strong> les trois DPE (condition suspensive n°1, le F/G interdisant la location), un devis de rénovation par corps d'état, le statut de copropriété et le budget prévisionnel s'il en existe un, l'avis de taxe foncière, la procédure et les délais du permis de louer en mairie, la faisabilité ABF pour les menuiseries et l'aménagement des combles, les plans et surfaces Carrez lot par lot, la confirmation écrite de l'absence de locataire, les diagnostics techniques (amiante, plomb, termites, électricité, gaz) et l'état de la couverture",
            "<strong>Documents à obtenir en mairie :</strong> le règlement du Site Patrimonial Remarquable et l'existence éventuelle d'un PSMV ou d'un PVAP approuvé — c'est cette pièce qui détermine l'éligibilité Malraux, et donc l'intérêt du bien pour un investisseur fortement imposé",
            "<strong>Point de méthode :</strong> le prix plafond n'est pas un chiffre unique mais une fonction de l'enveloppe travaux (190 000 € à 80 000 € de travaux, 153 000 € à 120 000 €, 79 000 € à 200 000 €). Aucun prix n'est défendable avant devis",
            "<strong>Rappel de marché (sources au 20/09/2026) :</strong> MeilleursAgents quartier Centre / Vieille-Ville 1 865 €/m² et 13,2 €/m²/mois ; DVF 2025 2 388 €/m² sur 189 ventes d'appartements ; immeubles entiers du centre entre 1 168 et 1 467 €/m² ; annonces de T3 de 550 à 880 €/mois",
        ],
    )}

    gen.main()


if __name__ == '__main__':
    main()
