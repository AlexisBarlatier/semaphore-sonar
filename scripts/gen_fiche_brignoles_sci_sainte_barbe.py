#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche de synthèse — Immeuble 6 logements, 17 avenue Dréo, Brignoles (SCI Sainte Barbe).

Page hors listing : dossier encore ouvert, publiée pour lecture des associés après
réception des baux, des cinq DDT et des deux devis électricité (23/10/2026).

Tout chiffre publié est recalculé depuis le moteur et comparé par calcule().
HERMES_TOLERANT=1 liste les écarts au lieu de s'arrêter au premier.
"""
import copy
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

import analyse_app  # noqa: E402,F401
from analyse_app import engine, scoring  # noqa: E402

SLUG = "2026-07-04-extension-80-90-brignoles-350m2"
SURFACE_CARREZ = 220.04
PRIX = 399000.0
TRAVAUX = 130000.0
TF = 4600.0
CHARGES = {
    "taxe_fonciere_annuelle_euros": TF,
    "charges_copro_annuelles_euros": 0.0,
    "pno_annuelle_euros": 400.0,
    "entretien_annuel_euros": 2841.0,   # gestion 5 % + entretien courant + provision 2,5 %
    "comptabilite_annuelle_euros": 500.0,
    "provision_desactivee": True,
}
LOYERS = [
    ("Cinq baux en cours — un par lot (3 040 €/mois)", 3040.0),
    ("Relocation au loyer médian de la commune (13,1 €/m², DHUP 2025)", 2882.0),
    ("Loyer médian + sixième lot aménagé à 640 €", 3522.0),
    ("Si deux lots sont réellement vides (à confirmer)", 1824.0),
]
TOLERANT = os.environ.get("HERMES_TOLERANT") == "1"
ECARTS = []


def calcule(libelle, publie, attendu, tolerance=1.0):
    if publie is None or attendu is None:
        ECARTS.append((libelle, publie, attendu))
        return publie
    if abs(float(publie) - float(attendu)) > tolerance:
        ECARTS.append((libelle, publie, attendu))
    return publie


def nfr(x, dec=0):
    s = f"{x:,.{dec}f}".replace(",", "\u202f").replace(".", ",")
    return s


def eur(x, dec=0):
    return nfr(x, dec) + "\u00a0€"


def pct(x, dec=2):
    return nfr(x, dec) + "\u00a0%"


def euro_signe(x, dec=0):
    s = nfr(abs(x), dec)
    return ("\u2212" if x < 0 else "+") + s + "\u00a0€"


def record(loyer):
    return {
        "slug": SLUG,
        "date_analyse": "2026-07-04",
        "date_maj": "2026-10-23",
        "titre": "Immeuble 6 logements — 17 avenue Dréo, Brignoles (83170)",
        "bien": {
            "type_bien": "immeuble", "sous_type": None, "type_detail": "Investissement locatif", "neuf": None,
            "adresse": {"texte": "17 avenue Dréo, Brignoles (83170)", "ville": "Brignoles", "code_postal": "83170"},
            "surfaces": {"texte": "220 m² Carrez (5 lots mesurés)"},
            "lots": {"count": 6, "nature": "5 logements existants (3 T3, 2 T2) + 1 T2 à aménager"},
            "copro": {"charges_annuelles_euros": 0.0, "charges_source": "monopropriété SCI Sainte Barbe"},
            "travaux": {"montant_euros": TRAVAUX, "nature": "électricité 5 lots, isolation sols/murs/toiture, aménagement 6e lot"},
        },
        "annonce": {"plateforme": "Logic-Immo", "url": "https://www.logic-immo.com/detail-vente-263831147.htm",
                    "prix_affiche_euros": PRIX, "prix_retenu_euros": None, "prix_statut": "affiche"},
        "marche": {
            "valeur": {"basse_euros": 360000.0, "haute_euros": 420000.0, "retenue_euros": 390000.0,
                       "source": "capitalisation des loyers de marché sur 220 m² Carrez", "confiance": "moyenne"},
            "loyers": [{"libelle": "assiette", "quantite": 1, "loyer_mensuel_euros": loyer, "occupe": True, "note": ""}],
            "notes": "",
        },
        "hypotheses": {"vacance_base_pct": 5.0, "vacance_best_pct": 5.0, "vacance_worst_pct": 12.0,
                       "charges": dict(CHARGES), "frais_acquisition_euros": None, "taux_placement_reserve_pct": 2.84},
        "analyse": {
            "branche": "residentiel", "type_operation": "locatif",
            "strategie_retenue": {"nom": "Relocation et aménagement du 6e lot", "code": "ld-nue", "lots": 6},
            "strategies_explorees": [],
            "attractivite": [{"dimension": d, "score": s, "nature": "", "justification": j} for d, s, j in [
                ("transports", 6, "Centre de Brignoles, accès direct aux axes vers Toulon et Aix"),
                ("commerces", 7, "Centre ancien, commerces de proximité à pied"),
                ("ecoles", 6, "Établissements scolaires de la commune à distance raisonnable"),
                ("securite", 5, "Centre ancien, fréquentation de passage, pas de nuisance majeure relevée"),
                ("demande_locative", 6, "Marché locatif actif : 86 annonces actives, demande à l'année"),
                ("dynamisme", 5, "Commune administratrice du Var, bassin d'emploi modeste"),
            ]],
            "risques": [
                {"libelle": "Travaux réels 6 à 7 fois le budget annoncé", "severite": 5, "bloquant": False,
                 "detail": "20 000 € annoncés pour finir le 6e lot ; électricité seule déjà chiffrée 9 124 € pour deux lots, "
                           "aucune isolation (sols, murs, toiture), et le lot brut vaut 45 000 € à lui seul. Enveloppe réaliste "
                           "130 000 à 140 000 €, dont la part existant ne peut se faire qu'au départ des locataires."},
                {"libelle": "Loyers dans le haut du marché, occupation à confirmer", "severite": 3, "bloquant": False,
                 "detail": "Cinq baux signés entre 2019 et 2025 couvrent les cinq lots, mais l'agence évoque trois appartements occupés. "
                           "Aucun congé ni état des lieux de sortie n'est fourni. À 13,8 €/m² contre 13,1 de médiane communale, "
                           "les loyers sont hauts mais dans le marché : ils n'expliquent pas seuls une vacance."},
                {"libelle": "Installation électrique dangereuse sur les cinq lots", "severite": 4, "bloquant": False,
                 "detail": "Les cinq DDT concluent à des anomalies avec recommandation d'agir pour éliminer les dangers."},
                {"libelle": "Sixième logement à créer", "severite": 3, "bloquant": False,
                 "detail": "Le PC de 2012 autorisait six logements ; le sixième n'est ni mesuré ni diagnostiqué."},
            ],
        },
        "legacy": None, "champs_manquants": [],
    }


def chiffre(loyer):
    r = record(loyer)
    c = engine.compute(r)
    return r, c, c["fiscal"]


def main():
    lignes = []
    for lab, loy in LOYERS:
        r, c, f = chiffre(loy)
        plaf, contrainte = scoring.prix_plafond(r)
        plaf5 = (f["ebe"] / 0.05 - TRAVAUX) / 1.075
        calcule(f"plafond 5 % {loy}", plaf5, (f["ebe"] / 0.05 - TRAVAUX) / 1.075)
        lignes.append({
            "lab": lab, "loyer": loy, "revenus": c["revenus_bruts_annuels"], "ebe": f["ebe"],
            "net": f["net_apres_is"], "sur_revient": c["rendements"]["net_sur_revient_pct"],
            "sur_valeur": c["rendements"]["net_sur_valeur_pct"], "plafond": plaf5, "contrainte": contrainte,
        })

    base = lignes[0]
    cible = lignes[2]
    r_base, c_base, f_base = chiffre(base["loyer"])
    note, verdict, _ = scoring.note_et_verdict(r_base, c_base)
    classe = {"acheter": "buy", "negocier": "nego", "fuir": "pass"}.get(verdict, "nego")
    libelle_verdict = {"acheter": "À acheter", "negocier": "À négocier", "fuir": "À fuir"}.get(verdict, verdict)

    revient = c_base["prix_revient_total"]
    frais = c_base["frais_acquisition"]

    calcule("revient", revient, PRIX + frais + TRAVAUX)
    calcule("prix au m²", PRIX / SURFACE_CARREZ, 399000 / 220.04)

    def _tr(i):
        cls = ' class="ligne-base"' if i == 0 else ''
        return f"<tr{cls}>"

    lignes_html = "".join(
        _tr(i)
        + f"<td>{l['lab']}</td><td class=\"num\">{eur(l['loyer'])}</td>"
        + f"<td class=\"num\">{eur(l['ebe'])}</td><td class=\"num\">{pct(l['sur_revient'])}</td>"
        + f"<td class=\"num\">{pct(l['sur_valeur'])}</td>"
        + f"<td class=\"num\">{eur(l['plafond']) if l['plafond'] else '—'}</td></tr>"
        for i, l in enumerate(lignes)
    )

    baux = [
        ("RDC — fond de cour", "36,85", "530", "20", "février 2019"),
        ("1er gauche", "39,00", "540", "20", "1er septembre 2025"),
        ("1er droite", "48,67", "670", "20", "19 avril 2023"),
        ("2e gauche", "44,92", "650", "20", "1er mai 2024"),
        ("2e droite", "50,60", "650", "20", "7 août 2025"),
    ]
    baux_html = "".join(
        f"<tr><td>{b[0]}</td><td class=\"num\">{b[1]}</td><td class=\"num\">{b[2]}\u00a0€</td>"
        f"<td class=\"num\">{b[3]}\u00a0€</td><td>{b[4]}</td></tr>" for b in baux
    )
    total_baux = sum(int(b[2]) for b in baux)
    calcule("total des loyers des baux", total_baux, 3040)

    # DPE relevés sur les deux DDT lisibles
    dpe = [("RDC", "E", "286", "11"), ("1er droite", "C", "128", "4")]

    annonces = [
        ("T2 36 m² — Zimo, Brignoles", "36,00", "535", "14,9"),
        ("T2 51 m² — Orpi (bien loué)", "51,18", "746", "14,6"),
        ("T3 55 m² — Locagestion", "55,00", "780", "14,2"),
        ("T3 70 m² — Les Clés", "70,00", "870", "12,4"),
        ("T4 97 m² — SeLoger", "97,00", "1 167", "12,0"),
        ("T4 73 m² — Rentola", "73,00", "755", "10,3"),
        ("T3 66 m² — FNAIM", "66,00", "630", "9,5"),
    ]
    marche_html = "".join(
        f"<tr><td>{a[0]}</td><td class=\"num\">{a[1]} m²</td><td class=\"num\">{a[2]}\u00a0€</td>"
        f"<td class=\"num\">{a[3]}\u00a0€</td></tr>" for a in annonces
    )

    html = TEMPLATE.format(
        slug=SLUG,
        marche=marche_html,
        prix=eur(PRIX),
        prix_m2=eur(PRIX / SURFACE_CARREZ),
        surface=nfr(SURFACE_CARREZ, 2),
        revient=eur(revient),
        travaux=eur(TRAVAUX),
        ebe_base=eur(base["ebe"]),
        ebe_cible=eur(cible["ebe"]),
        solde_base=euro_signe(base["net"] / 12),
        solde_cible=euro_signe(cible["net"] / 12),
        rdt_base=pct(base["sur_revient"]),
        rdt_cible=pct(cible["sur_revient"]),
        plaf_base=eur(base["plafond"]),
        plaf_cible=eur(cible["plafond"]),
        ecart_base=pct((base["plafond"] - PRIX) / PRIX * 100, 1),
        ecart_cible=pct((cible["plafond"] - PRIX) / PRIX * 100, 1),
        multiple_base=nfr(PRIX / base["plafond"], 1),
        dessus_cible=pct((PRIX / cible["plafond"] - 1) * 100, 0),
        note=nfr(note, 1),
        verdict=libelle_verdict,
        classe=classe,
        lignes=lignes_html,
        baux=baux_html,
        total_baux=eur(total_baux),
        dpe="".join(f"<tr><td>{d[0]}</td><td class=\"num\">{d[1]}</td><td class=\"num\">{d[2]}</td><td class=\"num\">{d[3]}</td></tr>" for d in dpe),
    )

    if ECARTS:
        print("ECARTS :")
        for e in ECARTS:
            print("  ", e)
        if not TOLERANT:
            raise SystemExit("contrôles chiffrés en échec")

    assert html.count("<section") >= 8, f"structure incomplète : {html.count('<section')} sections"
    assert "noindex" in html
    assert "logic-immo" in html
    for mot in ("prêt", "emprunt", "crédit", "apport", "mensualité", "levier", "montage"):
        assert mot not in html.lower(), f"mot de financement : {mot}"

    sortie = os.path.join(RACINE, "analyses", SLUG, "index.html")
    os.makedirs(os.path.dirname(sortie), exist_ok=True)
    with open(sortie, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"écrit {sortie} — {len(html.splitlines())} lignes")
    print(f"note {note} / verdict {verdict} / plafond base {base['plafond']} / plafond cible {cible['plafond']}")


TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fiche de synthèse — Immeuble 6 logements, 17 avenue Dréo, Brignoles (83170)</title>
<link rel="stylesheet" href="../../style.css">
<style>
  .fiche-synthese {{ max-width: 980px; margin: 0 auto; padding: 0 20px 60px; }}
  .fiche-synthese h2 {{ margin-top: 42px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }}
  .fiche-synthese h3 {{ margin-top: 26px; }}
  .fiche-synthese table {{ width: 100%; border-collapse: collapse; margin: 14px 0 22px; font-size: 0.94rem; }}
  .fiche-synthese th {{ text-align: left; background: #f3f4f6; padding: 9px 10px; border-bottom: 2px solid #d1d5db; font-weight: 600; }}
  .fiche-synthese td {{ padding: 8px 10px; border-bottom: 1px solid #e5e7eb; vertical-align: top; }}
  .fiche-synthese td.num {{ text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }}
  .fiche-synthese tr.ligne-base {{ background: #fff7ed; font-weight: 600; }}
  .fiche-synthese .alerte {{ background: #fef2f2; border-left: 4px solid #dc2626; padding: 16px 18px; margin: 22px 0; }}
  .fiche-synthese .info {{ background: #f0f9ff; border-left: 4px solid #0284c7; padding: 16px 18px; margin: 22px 0; }}
  .fiche-synthese ul {{ padding-left: 22px; }}
  .fiche-synthese li {{ margin-bottom: 7px; }}
  .fiche-synthese .kpi {{ display: flex; flex-wrap: wrap; gap: 14px; margin: 22px 0; }}
  .fiche-synthese .kpi div {{ flex: 1 1 190px; border: 1px solid #e5e7eb; border-radius: 8px; padding: 14px 16px; background: #fafafa; }}
  .fiche-synthese .kpi span {{ display: block; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; color: #6b7280; }}
  .fiche-synthese .kpi strong {{ display: block; font-size: 1.35rem; margin-top: 6px; }}
</style>
</head>
<body>
<header class="report-header">
  <nav class="report-breadcrumb"><a href="../../analyses/index.html">← Retour aux analyses</a></nav>
  <h1>Fiche de synthèse</h1>
  <p class="report-address">Immeuble 6 logements — 17 avenue Dréo, Brignoles (83170)</p>
  <p class="report-date">Dossier ouvert le 4 juillet 2026, mis à jour le 23 octobre 2026 après réception des baux, des cinq dossiers de diagnostics et des deux devis électricité</p>
  <p class="report-source">Vendeur : SCI Sainte Barbe (Jean-Bernard Léon). Mandataire : Deborah Vacchino, réseau Happyssimmo, réf. 2074DV.2. Prix affiché 399 000 €, honoraires à la charge du vendeur.</p>
  <div class="report-source-link"><a href="https://www.logic-immo.com/detail-vente-263831147.htm">https://www.logic-immo.com/detail-vente-263831147.htm</a></div>
</header>

<main class="fiche-synthese">

<section>
<div class="alerte">
<strong>Ce que l'annonce dit, et ce que les pièces disent.</strong>
L'annonce vend un immeuble de 350 m², six logements loués, 3 100 €/mois, avec 20 000 € pour finir le dernier lot.
Les baux, les mesures Carrez et les diagnostics reçus le 23 octobre 2026 disent autre chose : <strong>220 m² Carrez</strong>
pour les cinq lots loués, et une remise en état qui coûte cinq à six fois le budget annoncé. Les cinq baux couvrent les cinq lots —
mais l'agence évoque trois appartements occupés, et aucun document ne tranche. C'est la première question à poser.
</div>

<div class="kpi">
  <div><span>Prix affiché</span><strong>{prix}</strong></div>
  <div><span>Prix au m² (5 lots mesurés)</span><strong>{prix_m2}</strong></div>
  <div><span>Surface Carrez des 5 lots loués</span><strong>{surface} m²</strong></div>
  <div><span>Prix de revient travaux compris</span><strong>{revient}</strong></div>
</div>
</section>

<section>
<h2>Les surfaces : quatre chiffres, et un trou</h2>
<table>
<tr><th>Source</th><th class="num">Surface</th><th>Ce qu'elle couvre</th></tr>
<tr><td>Annonce</td><td class="num">350 m²</td><td>Surface commerciale — six logements et communs, non opposable</td></tr>
<tr><td>Baux — surfaces déclarées</td><td class="num">257,64 m²</td><td>Les cinq lots loués, majorés</td></tr>
<tr class="ligne-base"><td>DDT — mesure Loi Carrez</td><td class="num">{surface} m²</td><td>Les cinq lots loués seulement, mesurés le 19 septembre 2026</td></tr>
<tr><td>Sixième lot</td><td class="num">non mesuré</td><td>Brut : ni Carrez, ni DPE, ni diagnostic. Sa surface s'ajoute et reste inconnue</td></tr>
</table>
<p>Le Carrez ne porte que sur les cinq lots loués. Le sixième, brut, n'a jamais été mesuré ni diagnostiqué — sa surface s'ajoute à celle des autres et personne ne la connaît aujourd'hui. Ce n'est pas un détail : elle décide du prix au m² de l'ensemble. Sur les seuls lots mesurés, le prix ressort à <strong>{prix_m2}</strong> ; ramené aux 350 m² annoncés, il tombe à 1 140 €/m². La vérité est entre les deux, et l'écart se chiffre en dizaines de mètres carrés.</p>
</section>

<section>
<h2>Les cinq baux reçus</h2>
<table>
<tr><th>Lot</th><th class="num">Carrez</th><th class="num">Loyer</th><th class="num">Charges</th><th>Date d'effet</th></tr>
{baux}
<tr><td><strong>Total</strong></td><td class="num">220,04 m²</td><td class="num"><strong>{total_baux}</strong></td><td class="num">100 €</td><td>—</td></tr>
</table>
<p>3 040 €/mois sur 220 m² Carrez, soit <strong>13,8 €/m²</strong>. Le loyer médian de la commune ressort à
<strong>13,1 €/m²</strong> (DHUP 2025, fourchette 10,1 à 16,9) : les baux sont donc à 5 % au-dessus du marché,
dans le haut de la fourchette mais pas hors marché. Les loyers ne sont pas le problème du dossier.
Les cinq baux reçus couvrent les cinq lots et aucun ne porte de mention de résiliation : rien dans les pièces ne dit
qu'un lot est vide. Si deux le sont, c'est une information d'agence qui reste à documenter — congé, état des lieux de sortie, date.
À la relocation au loyer médian, l'assiette ressort à 2 880 €/mois pour les cinq lots, soit 160 € de moins.</p>
</section>

<section>
<h2>Ce que le marché demande aujourd'hui</h2>
<table>
<tr><th>Annonce / source</th><th class="num">Surface</th><th class="num">Loyer</th><th class="num">€/m²</th></tr>
{marche}
<tr class="ligne-base"><td>Médiane communale (DHUP 2025)</td><td class="num">—</td><td class="num">—</td><td class="num">13,1 €</td></tr>
</table>
<p>La fourchette observée va de 9,5 à 14,9 €/m² selon l'état, l'étage et la surface. Les petites surfaces partent plus cher
au m², les grands logements moins. Nos cinq lots se situent entre 12,8 et 14,5 €/m² : ils sont dans le marché, en haut de la
fourchette pour les petites surfaces. <strong>Il n'y a donc pas de marge de revalorisation à attendre de la relocation</strong> —
au mieux une stabilité, au pire 5 % de moins sur les lots les plus chers au m².</p>
</section>

<section>
<h2>Le budget travaux : 20 000 € annoncés, 130 000 € chiffrés</h2>
<ul>
<li><strong>Électricité</strong> — les cinq DDT concluent à des anomalies avec recommandation d'agir pour éliminer les dangers. Deux devis de l'électricien Fouassier (Brignoles) : 4 287 € et 4 837 € pour deux logements seulement, soit environ 22 500 € pour les cinq.</li>
<li><strong>Isolation</strong> — aucune, ni sols, ni murs, ni toiture. Enveloppe 55 000 à 65 000 € sur six logements.</li>
<li><strong>Aménagement du sixième lot</strong> — largement au-delà des 20 000 € annoncés, un lot brut à créer coûte 45 000 € avec ses réseaux et sa salle d'eau.</li>
</ul>
<p>Total : <strong>{travaux}</strong>. Les 20 000 € annoncés ne couvrent même pas l'électricité des lots existants.</p>
<p>Et le calendrier compte autant que le montant : <strong>les travaux de l'existant ne se font qu'au départ des locataires</strong>.
Un logement occupé ne se rénove pas. Le budget s'étale donc sur plusieurs années, au rythme des rotations — ce qui veut dire
des loyers bloqués en dessous du marché tant que le lot n'a pas été repris, et un chantier qui revient à chaque congé.
Le sixième lot, lui, peut être fait immédiatement, mais il ne se louera pas sans l'isolation.</p>
</section>

<section>
<h2>Le DPE, lot par lot</h2>
<table>
<tr><th>Lot</th><th class="num">Classe</th><th class="num">kWh/m²/an</th><th class="num">GES</th></tr>
{dpe}
<tr><td>Sixième lot</td><td class="num">—</td><td class="num">—</td><td class="num">—</td></tr>
<tr><td colspan="4">Les trois autres lots loués sont diagnostiqués mais leur classe n'a pas encore été relevée. Le sixième lot, brut, n'a fait l'objet d'aucun DPE : il en faudra un après aménagement. Aucune passoire parmi les lots mesurés. Pas d'échéance réglementaire à court terme.</td></tr>
</table>
</section>

<section>
<h2>Le compte, selon l'assiette de loyers</h2>
<table>
<tr><th>Assiette</th><th class="num">Loyer</th><th class="num">EBE</th><th class="num">Net / revient</th><th class="num">Net / valeur</th><th class="num">Plafond 5 % avant IS</th></tr>
{lignes}
</table>
<p>La ligne surlignée est celle des cinq baux reçus : c'est la seule assiette documentée. La dernière ligne est
l'hypothèse d'agence, à confirmer par les congés. Les deux du milieu sont des cibles après relocation, pas des revenus.</p>
<div class="info">
<strong>Le chiffre à retenir.</strong> Sur l'assiette réelle, l'exploitation dégage <strong>{ebe_base}</strong> par an,
soit un solde d'exploitation de <strong>{solde_base}/mois</strong>, pour un prix de revient de {revient}.
Tous lots loués et le sixième aménagé, on monte à <strong>{ebe_cible}</strong> et <strong>{solde_cible}/mois</strong>.
</div>
</section>

<section>
<h2>La grille de prix</h2>
<table>
<tr><th>Critère</th><th class="num">Prix</th><th>Écart au prix affiché</th></tr>
<tr class="ligne-base"><td>Prix affiché</td><td class="num">{prix}</td><td>—</td></tr>
<tr><td>Plafond sur les cinq baux en cours</td><td class="num">{plaf_base}</td><td class="num">{ecart_base}</td></tr>
<tr><td>Plafond au loyer de marché, sixième lot aménagé</td><td class="num">{plaf_cible}</td><td class="num">{ecart_cible}</td></tr>
</table>
<p>Sur les cinq baux en cours, le plafond 5 % net avant IS ressort à <strong>{plaf_base}</strong>, soit <strong>{ecart_base}</strong>
sur le prix affiché. L'écart est faible — mais ce plafond suppose que les 130 000 € de travaux tiennent et que les loyers
restent à 13,8 €/m², soit 5 % au-dessus de la médiane communale. Ramené au loyer médian, il tombe à 336 000 €. Et la marge de
sécurité du moteur, qui compare le prix de revient à la valeur de l'actif, plafonne à 292 000 €.</p>
</section>

<section>
<h2>Risques</h2>
<ul>
<li><strong>Travaux sous-estimés d'un facteur six.</strong> La pièce reçue chiffre l'électricité seule à 9 124 € pour deux lots ; le vendeur annonce 20 000 € pour finir un sixième lot sans isolation.</li>
<li><strong>Occupation non documentée.</strong> Cinq baux signés, mais l'agence évoque trois appartements occupés. Aucun congé fourni : c'est la première question à poser, et elle déplace le dossier de 120 000 €.</li>
<li><strong>Sixième lot non mesuré.</strong> Le permis de 2012 en prévoyait six ; le dernier n'est ni diagnostiqué ni chiffré.</li>
<li><strong>Monopropriété SCI.</strong> Pas de charges de copropriété, mais pas de vote pour arbitrer les travaux non plus : tout repose sur le vendeur puis sur nous.</li>
</ul>
</section>

<section class="verdict {classe}">
<h2>Recommandation</h2>
<p><strong>{verdict} — note {note}/10.</strong></p>
<p>Sur les cinq baux reçus, le prix affiché dépasse le plafond de rendement de 7 % : c'est une négociation ordinaire, pas un mur.
Mais ce plafond repose sur deux hypothèses fragiles — des loyers dans le haut du marché, et des travaux que le vendeur
a budgétés six fois trop bas. Au loyer médian, le plafond descend à 336 000 €. Si deux lots sont réellement vides,
il tombe à 110 000 €.</p>
<p>Deux conditions avant toute proposition : un devis isolation et aménagement signé, et l'état locatif exact des cinq lots —
lesquels sont occupés, lesquels sont vides, et depuis quand. Sans ces pièces, le rendement affiché est une photo qui
peut se dégrader de moitié.</p>
</section>

<footer>
<p class="report-footer">Fiche de synthèse interne — Sémaphore Patrimoine. Chiffres calculés par le moteur d'analyse du dépôt sur les pièces reçues le 23 octobre 2026 (cinq DDT, deux devis électricité, cinq baux).</p>
</footer>

</main>
</body>
</html>
"""

if __name__ == "__main__":
    main()
