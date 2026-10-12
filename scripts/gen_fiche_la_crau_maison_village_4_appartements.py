# -*- coding: utf-8 -*-
"""Fiche « La Crau — maison de village, 4 appartements indépendants ».

Réponse de l'agence du 12 octobre 2026 : loyers en place des trois baux
(somme 3 050 €/mois), immeuble en un seul lot sans division juridique,
compteurs individuels, T1 libre en attente de travaux couverts par
l'assurance, façade à reprendre (14 000 € annoncés) plus les volets.

Sortie : analyses/2026-10-12-la-crau-maison-village-4-appartements/index.html
"""
import os
import re

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "analyses", "2026-10-12-la-crau-maison-village-4-appartements",
                      "index.html")
URL_ANNONCE = ("https://www.logic-immo.com/detail-annonce/vente/provence-alpes-cote-d-azur/"
               "var-83/la-crau-83260/26V49XQZ4PZT")
URL_IAD = "https://www.iadfrance.fr/annonce/immeuble-vente-la-crau-240m2/r2131728"

PRIX = 500000.0
SURF_ANNONCEE = 240.0          # surface globale annoncée
SURF_LOTS_ANNONCE = 222.0      # somme des surfaces « environ » de l'annonce, lot par lot
CARREZ = 240.94                # certificat de superficie NOSTIKA, 27 janvier 2022
ANNEXES = 53.16                # deux caves, deux terrasses et cage d'escalier, hors Carrez
# Loyer en place (baux communiqués par l'agence le 12/10/2026). Le T1 est libre.
LOTS = [("T1 — RDC Sud, mezzanine et dressing (libre)", 44.19, 590.0),
        ("T2 — RDC Est", 37.96, 640.0),
        ("T3 — 1er étage, trois chambres et terrasse", 77.30, 890.0),
        ("T4 — 2e étage, trois chambres et terrasse", 81.48, 930.0)]
SURF_REELLE = sum(l[1] for l in LOTS)
LOYER_MARCHE = sum(l[2] for l in LOTS)          # quatre lots loués : la cible après travaux du T1
LOYER_EN_PLACE = LOYER_MARCHE - LOTS[0][2]      # trois baux en cours, T1 vide : ce qui rentre aujourd'hui

FRAIS = 0.08
TRAVAUX = 30000.0          # provision : « quelques travaux de rafraîchissement », aucun devis
TF = 3115.0                # avis communiqué le 12 octobre 2026 (Rémy)
CHARGES = 1500.0           # monopropriété : aucun syndic, aucune charge de copropriété — entretien et assurance de l'immeuble
PNO = 400.0
VACANCE = 0.95
IS = 0.15                  # convention prudente : IS sur l'EBE, intérêts non déduits
COEF20 = 0.006238          # mensualité par euro emprunté : 20 ans à 3,80 %, assurance comprise
APPORT = 0.10

# --- Vision marchand de biens : revente à la découpe -------------------------
# Quartiles des ventes d'APPARTEMENTS à La Crau (INSEE 83047) : extraction
# geo-DVF du 12 octobre 2026, millésimes 2024 et 2025, 129 ventes retenues.
# Chaque lot est valorisé sur la tranche de surface qui le contient.
DVF = [("T2 — RDC Sud", 44.19, 3347.0, 4009.0, 5362.0),
       ("T2 — RDC Est", 37.96, 3286.0, 3890.0, 4184.0),
       ("T4 — 1er étage", 77.30, 2778.0, 3282.0, 3707.0),
       ("T4 — 2e étage", 81.48, 2778.0, 3282.0, 3707.0)]
MDB_FACADE = 14000.0       # réfection de la façade, estimation du maçon rapportée par l'agence
MDB_VOLETS = 6000.0        # volets à repeindre ou remplacer, non chiffrés par l'agence
MDB_TRAVAUX = 90000.0 + MDB_FACADE + MDB_VOLETS   # remise en état des lots plus façade et volets
MDB_EDD = 8000.0           # division à créer : un seul lot aujourd'hui (plancher, 8 000 à 15 000 €)
MDB_MOIS = 24              # portage allongé : la division juridique s'instruit avant la première vente
MDB_PORTAGE_TAUX = 0.042   # coût du portage annuel sur le capital engagé
MDB_HONORAIRES = 0.05      # frais de commercialisation des lots
VA_TRAVAUX_M2 = 400.0      # convention maison : simple rafraîchissement


def ca_decoupe(idx):
    """Chiffre d'affaires de la revente à la découpe, au quantile demandé (2 = Q1, 3 = médiane, 4 = Q3)."""
    return sum(e[idx] * e[1] for e in DVF)


def impot_societes(resultat):
    """IS : 15 % jusqu'à 42 500 €, 25 % au-delà (barème du moteur)."""
    if resultat <= 0:
        return 0.0
    if resultat <= 42500.0:
        return 0.15 * resultat
    return 0.15 * 42500.0 + 0.25 * (resultat - 42500.0)


def mdb_compte(prix, ca, travaux=MDB_TRAVAUX):
    acte = prix * (1 + FRAIS)
    portage = MDB_PORTAGE_TAUX * (acte + travaux * 0.6) * (MDB_MOIS / 12)
    revient = acte + travaux + MDB_EDD + portage
    honoraires = ca * MDB_HONORAIRES
    pv = ca - honoraires - revient
    impot = impot_societes(pv)
    nette = pv - impot
    roi = nette / revient * 100
    return dict(prix=prix, acte=acte, portage=portage, revient=revient, honoraires=honoraires,
                pv=pv, impot=impot, nette=nette, roi=roi,
                roi_an=((1 + nette / revient) ** (12.0 / MDB_MOIS) - 1) * 100)


def mdb_prix_roi_exact(ca, cible=0.15, travaux=MDB_TRAVAUX):
    """Prix tel que la plus-value nette d'IS égale la cible × prix de revient."""
    lo, hi = 10000.0, 2000000.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if mdb_compte(mid, ca, travaux)["nette"] > cible * mdb_compte(mid, ca, travaux)["revient"]:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def mdb_prix_pour(ca, cible=0.15, travaux=MDB_TRAVAUX):
    """Prix pour une cible de ROI net d'impôt : revient_max = 0,85 × net de revente / (1 + cible).

    La formule est conservatrice : elle laisse en réalité 20 % de ROI net, notre cible
    marchand de biens. Le prix correspondant à un ROI net strictement égal à la cible se
    calcule par itération, avec mdb_prix_roi_exact().
    """
    net_revente = ca * (1 - MDB_HONORAIRES)
    revient_max = 0.85 * net_revente / (1 + cible)
    portage_hors_acte = MDB_PORTAGE_TAUX * (travaux * 0.6) * (MDB_MOIS / 12)
    return (revient_max - travaux - MDB_EDD - portage_hors_acte) / ((1 + FRAIS) + MDB_PORTAGE_TAUX * (MDB_MOIS / 12))

ACTE = PRIX * (1 + FRAIS)
REVIENT = ACTE + TRAVAUX
CAPITAL = ACTE * (1 - APPORT)
MENSU = CAPITAL * COEF20

ECARTS = []


def calcule(libelle, publie, attendu, tolerance):
    if abs(float(publie) - float(attendu)) > tolerance:
        ECARTS.append("%s : publie %s, attendu %s" % (libelle, publie, attendu))
    return publie


def nfr(v, dec=0):
    ent, _, frac = ("%.*f" % (dec, float(v))).partition(".")
    return re.sub(r"(?<=\d)(?=(\d{3})+$)", "\u202f", ent) + (("," + frac) if dec else "")


def eur(v, dec=0):
    return nfr(v, dec) + " €"


def signe(v):
    return ("−" if v < 0 else "+") + nfr(abs(v)) + " €"


def exploitation(loyer):
    ebe = loyer * 12 * VACANCE - TF - CHARGES - PNO
    net = ebe * (1 - IS)
    return dict(loyer=loyer, ebe=ebe, net=net, net_m=net / 12,
                net_revient=net / REVIENT * 100, net_acte=net / ACTE * 100,
                cf=net / 12 - MENSU, ratio=ebe / (MENSU * 12),
                brut=loyer * 12 / PRIX * 100)


def plafond_ratio(loyer, cible=1.20):
    """Prix tel que EBE / annuité = cible ; capital = acte × 0,9, donc prix = capital / 0,972."""
    ebe = loyer * 12 * VACANCE - TF - CHARGES - PNO
    return (ebe / 12 / cible) / COEF20 / (1 - APPORT) / (1 + FRAIS)


def plafond_cf_nul(loyer):
    net = (loyer * 12 * VACANCE - TF - CHARGES - PNO) * (1 - IS)
    return (net / 12) / COEF20 / (1 - APPORT) / (1 + FRAIS)


def plafond_rendement(loyer, cible=0.05):
    """Prix tel que net / (prix × 1,08 + travaux) = cible."""
    net = (loyer * 12 * VACANCE - TF - CHARGES - PNO) * (1 - IS)
    return (net / cible - TRAVAUX) / (1 + FRAIS)


def main():
    base = exploitation(LOYER_EN_PLACE)
    basses = exploitation(LOYER_EN_PLACE * 0.90)
    hautes = exploitation(LOYER_MARCHE)

    lignes_lots = "\n".join(
        "        <tr><td>%s</td><td class=\"num\">%s m²</td><td>%s</td><td class=\"num\">%s</td>"
        "<td class=\"num\">%s</td><td>%s</td></tr>"
        % (nom, nfr(surf, 2), ann, eur(loyer), eur(loyer / surf), source)
        for nom, surf, loyer, ann, source in (
            ("T1 — RDC Sud, mezzanine et dressing", 44.19, 0.0, "T1 ≈ 45 m²",
             "vide : sinistre, travaux couverts par l'assurance, relouage attendu à 590 €"),
            ("T2 — RDC Est", 37.96, 640.0, "T2 ≈ 38 m²",
             "loué, 16,9 €/m² : au-dessus de la fourchette relevée"),
            ("T3 — 1er étage, trois chambres", 77.30, 890.0, "T3 ≈ 80 m²",
             "loué, 11,5 €/m² : la décote des grandes surfaces"),
            ("T4 — 2e étage, trois chambres", 81.48, 930.0, "T4 ≈ 85 m²",
             "loué, 11,4 €/m² : la décote des grandes surfaces"),
        ))

    grille = [(LOYER_EN_PLACE * f, plafond_cf_nul(LOYER_EN_PLACE * f),
               plafond_ratio(LOYER_EN_PLACE * f), plafond_rendement(LOYER_EN_PLACE * f))
              for f in (0.90, 1.00, 1.12, 1.24)]
    lignes_grille = "\n".join(
        "        <tr><td>%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
        "<td class=\"num\">%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td></tr>"
        % (eur(rev), eur(cf_nul), eur(ratio_p), eur(rdt_p), eur(min(ratio_p, rdt_p)),
           nfr((min(ratio_p, rdt_p) / PRIX - 1) * 100, 0))
        for rev, cf_nul, ratio_p, rdt_p in grille)

    calcule("loyers des baux en place", LOYER_EN_PLACE, 2460.0, 1.0)
    calcule("loyers à quatre lots loués", LOYER_MARCHE, 3050.0, 1.0)

    # --- lecture marchand de biens ---
    ca_q1, ca_med, ca_q3 = (ca_decoupe(i) for i in (2, 3, 4))
    expl65, expl70 = (LOYER_EN_PLACE * 12 / 0.065, LOYER_EN_PLACE * 12 / 0.07)
    expl65_stab = LOYER_MARCHE * 12 / 0.065
    comptes = [mdb_compte(PRIX, ca) for ca in (ca_q1, ca_med, ca_q3)]
    prix15 = [mdb_prix_pour(ca) for ca in (ca_q1, ca_med, ca_q3)]      # cible 20 % net
    prix_roi15 = mdb_prix_roi_exact(ca_med)                            # cible 15 % net exacte
    ca_carrez = ca_med * 0.92
    carrez_compte = mdb_compte(PRIX, ca_carrez)
    carrez_prix = mdb_prix_pour(ca_carrez)
    calcule("CA découpe à la médiane", ca_med, 845938.0, 500.0)
    calcule("prix d'achat pour 20 % de ROI net à la médiane", prix15[1], 404168.0, 2000.0)
    calcule("prix d'achat pour 15 % de ROI net à la médiane", prix_roi15, 470547.0, 2000.0)
    lignes_dvf = "\n".join(
        "        <tr><td>%s</td><td class=\"num\">%s m²</td><td class=\"num\">%s à %s</td>"
        "<td class=\"num\">%s</td><td class=\"num\">%s</td></tr>"
        % (nom, nfr(surf, 0), eur(q1), eur(q3), eur((q1 + q3) / 2),
           eur(surf * med))
        for nom, surf, q1, med, q3 in DVF)
    postes = [("Prix d'achat (net vendeur)", "prix"), ("Frais d'acquisition 8 %", None),
              ("Travaux de remise en état", None), ("Division et frais annexes", None),
              ("Portage %d mois" % MDB_MOIS, "portage"), ("Commercialisation des lots", "honoraires"),
              ("Prix de revient total", "revient"), ("Chiffre d'affaires de la découpe", None),
              ("Plus-value brute", "pv"), ("Impôt sur les sociétés", "impot"),
              ("Plus-value nette", "nette")]
    lignes_mdb = []
    for lab, key in postes:
        if key is None:
            vals = {"Frais d'acquisition 8 %": [c["acte"] - c["prix"] for c in comptes],
                    "Travaux de remise en état": [MDB_TRAVAUX] * 3,
                    "Division et frais annexes": [MDB_EDD] * 3,
                    "Chiffre d'affaires de la découpe": [ca_q1, ca_med, ca_q3]}[lab]
        else:
            vals = [c[key] for c in comptes]
        lignes_mdb.append("        <tr><td>%s</td>%s</tr>"
                          % (lab, "".join("<td class=\"num\">%s</td>" % eur(v) for v in vals)))
    lignes_mdb.append("        <tr><td><strong>ROI de l'opération</strong></td>%s</tr>"
                      % "".join("<td class=\"num\"><strong>%s %%</strong></td>" % nfr(c["roi"], 1)
                                for c in comptes))
    lignes_mdb.append("        <tr><td><strong>ROI annualisé</strong></td>%s</tr>"
                      % "".join("<td class=\"num\"><strong>%s %%</strong></td>" % nfr(c["roi_an"], 1)
                                for c in comptes))
    lignes_mdb = "\n".join(lignes_mdb)
    lignes_prix15 = "\n".join(
        "        <tr><td>%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td>"
        "<td class=\"num\">%s</td><td class=\"num\">%s</td></tr>"
        % (lab, eur(ca), eur(mdb_prix_pour(ca, travaux=40000.0)),
           eur(mdb_prix_pour(ca, travaux=MDB_TRAVAUX)), eur(mdb_prix_pour(ca, travaux=133000.0)))
        for lab, ca in (("Revente au Q1 des comparables", ca_q1),
                        ("Revente à la médiane", ca_med),
                        ("Revente au Q3", ca_q3)))
    calcule("surface Carrez des quatre lots", SURF_REELLE, 240.93, 0.05)
    # --- plan phasé : un lot à la fois, au rythme des baux ---
    acq_m2 = PRIX * (1 + FRAIS) / SURF_REELLE
    phas = [(l[0], l[1], l[1] * d[3], l[1] * (acq_m2 + VA_TRAVAUX_M2)) for l, d in zip(LOTS, DVF)]
    marge_phasee = sum(r - c for _, _, r, c in phas)
    revient_phase = PRIX * (1 + FRAIS) + SURF_REELLE * VA_TRAVAUX_M2 + MDB_EDD
    ca_net_phase = ca_med * (1 - MDB_HONORAIRES)
    sortie_initiale = PRIX * (1 + FRAIS) * APPORT + LOTS[0][1] * VA_TRAVAUX_M2 + MDB_EDD
    sortie_totale = PRIX * (1 + FRAIS) * APPORT + SURF_REELLE * VA_TRAVAUX_M2 + MDB_EDD
    mens_phase = PRIX * (1 + FRAIS) * (1 - APPORT) * COEF20
    ebe3 = ((LOYER_MARCHE - LOTS[0][2]) * 12 * VACANCE - TF - CHARGES - PNO) / 12
    ebe4 = (LOYER_MARCHE * 12 * VACANCE - TF - CHARGES - PNO) / 12
    lignes_phase = "\n".join(
        "        <tr><td>%s</td><td class=\"num\">%s m²</td><td class=\"num\">%s</td>"
        "<td class=\"num\">%s</td><td class=\"num\">%s</td></tr>"
        % (nom, nfr(s, 2), eur(r), eur(c), eur(r - c))
        for nom, s, r, c in phas)
    calcule("marge brute du plan phasé", marge_phasee, 209566.0, 500.0)
    calcule("EBE au loyer en place", base["ebe"], 23029.0, 2.0)
    calcule("plafond du ratio 1,20 au loyer en place", plafond_ratio(LOYER_EN_PLACE), 263755.0, 1500.0)

    html = TEMPLATE.format(
        url=URL_ANNONCE, url_iad=URL_IAD, prix=eur(PRIX), surf_annoncee=nfr(SURF_ANNONCEE, 0),
        surf=nfr(SURF_REELLE, 2), pm2=eur(PRIX / SURF_ANNONCEE),
        carrez=nfr(CARREZ, 2), annexes=nfr(ANNEXES, 2),
        ecart_lots=nfr(SURF_REELLE - SURF_LOTS_ANNONCE, 0),
        pm2_reel=eur(PRIX / SURF_REELLE), loyer_marche=eur(LOYER_MARCHE),
        loyer_en_place=eur(LOYER_EN_PLACE), loyers_an=eur(LOYER_EN_PLACE * 12),
        loyer_m2=nfr(LOYER_EN_PLACE / (SURF_REELLE - LOTS[0][1]), 2),
        surf_louee=nfr(SURF_REELLE - LOTS[0][1], 2),
        acte=eur(ACTE), travaux=eur(TRAVAUX), revient=eur(REVIENT), capital=eur(CAPITAL),
        mens=eur(MENSU), tf=eur(TF), charges=eur(CHARGES), pno=eur(PNO),
        frais_fixes=eur(TF + CHARGES + PNO), appar=eur(ACTE * APPORT),
        brut=nfr(base["brut"], 2), ebe=eur(base["ebe"]), net_an=eur(base["net"]),
        net_m=eur(base["net_m"]), net_revient=nfr(base["net_revient"], 2),
        net_acte=nfr(base["net_acte"], 2), cf=signe(base["cf"]), ratio=nfr(base["ratio"], 2),
        ch_pct=nfr((TF + CHARGES + PNO) / (LOYER_EN_PLACE * 12) * 100, 1),
        basse_net=nfr(basses["net_revient"], 2), basse_cf=signe(basses["cf"]),
        haute_net=nfr(hautes["net_revient"], 2), haute_cf=signe(hautes["cf"]),
        plafond=eur(plafond_ratio(LOYER_EN_PLACE)),
        plafond_bas=eur(plafond_ratio(LOYER_EN_PLACE * 0.90)),
        plafond_haut=eur(plafond_ratio(LOYER_MARCHE)),
        plafond_rdt=eur(plafond_rendement(LOYER_EN_PLACE)),
        plafond_ecart=nfr((1 - plafond_ratio(LOYER_EN_PLACE) / PRIX) * 100, 0),
        ecart_rdt=nfr(plafond_rendement(LOYER_EN_PLACE) - PRIX, 0),
        lignes_lots=lignes_lots, lignes_grille=lignes_grille,
        lignes_dvf=lignes_dvf, lignes_mdb=lignes_mdb, lignes_prix15=lignes_prix15,
        lignes_phase=lignes_phase,
        marge_phasee=eur(marge_phasee), revient_phase=eur(revient_phase),
        ca_net_phase=eur(ca_net_phase), sortie_initiale=eur(sortie_initiale),
        sortie_totale=eur(sortie_totale), mens_phase=eur(mens_phase),
        ebe3=eur(ebe3), ebe4=eur(ebe4), cf3=signe(ebe3 - mens_phase), cf4=signe(ebe4 - mens_phase),
        marge_phasee_pct=nfr(marge_phasee / revient_phase * 100, 0),
        acq_m2=eur(acq_m2), va_m2=eur(VA_TRAVAUX_M2),
        loyer_vacant=eur(LOTS[0][2]), loyers3=eur(LOYER_MARCHE - LOTS[0][2]),
        ca_q1=eur(ca_q1), ca_med=eur(ca_med), ca_q3=eur(ca_q3),
        ca_med_m2=nfr(ca_med / SURF_REELLE, 0),
        expl65=eur(expl65), expl70=eur(expl70), expl65_stab=eur(expl65_stab),
        mdb_travaux=eur(MDB_TRAVAUX), mdb_travaux_m2=nfr(MDB_TRAVAUX / SURF_REELLE, 0),
        mdb_facade=eur(MDB_FACADE), mdb_volets=eur(MDB_VOLETS),
        mdb_edd=eur(MDB_EDD), mdb_mois=MDB_MOIS, mdb_portage=eur(comptes[1]["portage"]),
        mdb_revient=eur(comptes[1]["revient"]), mdb_honoraires=eur(comptes[1]["honoraires"]),
        mdb_is=eur(comptes[1]["impot"]), mdb_nette=eur(comptes[1]["nette"]),
        mdb_roi=nfr(comptes[1]["roi"], 1), mdb_roi_an=nfr(comptes[1]["roi_an"], 1),
        mdb_roi_q1=nfr(comptes[0]["roi"], 1), mdb_roi_q3=nfr(comptes[2]["roi"], 1),
        mdb_cible=nfr(20, 0), prix_roi15=eur(prix_roi15),
        roi_affiche=nfr(comptes[1]["roi"], 1), roi_affiche_an=nfr(comptes[1]["roi_an"], 1),
        prix15_q1=eur(prix15[0]), prix15_med=eur(prix15[1]), prix15_q3=eur(prix15[2]),
        prix15_med_carrez=eur(carrez_prix), ca_carrez=eur(ca_carrez),
        roi_carrez=nfr(carrez_compte["roi"], 1),
        prix15_med_ecart=nfr((1 - prix15[1] / PRIX) * 100, 0),
        vacance=nfr((1 - VACANCE) * 100, 0), taux_is=nfr(IS * 100, 0),
        n_lots=len(LOTS),
    )
    reste = re.search(r"\{[a-z_0-9]{3,}\}", html)
    if reste:
        raise SystemExit("placeholder non remplacé : %s" % reste.group(0))
    if "26V49XQZ4PZT" not in html or "noindex" not in html:
        raise SystemExit("lien annonce ou balise noindex manquante")
    if ECARTS and not os.environ.get("HERMES_TOLERANT"):
        raise SystemExit("écarts de contrôle :\n  " + "\n  ".join(ECARTS))

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("fiche écrite : %s (%d lignes)" % (SORTIE, html.count("\n") + 1))
    print("  loyers retenus %s / mois | EBE %s | net %s/an | %s %% net/revient | CF %s | ratio %.2f"
          % (eur(LOYER_MARCHE), eur(base["ebe"]), eur(base["net"]),
             nfr(base["net_revient"], 2), signe(base["cf"]), base["ratio"]))
    for rev, cf_nul, ratio_p, rdt_p in grille:
        print("  revenus %s -> plafond CF nul %s | ratio 1,20 %s | 5 %% net %s"
              % (eur(rev), eur(cf_nul), eur(ratio_p), eur(rdt_p)))
    print("  écarts : %s" % (ECARTS or "aucun"))


TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>La Crau — maison de village, 4 appartements</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<main class="report">

  <header class="report-header">
    <p class="report-breadcrumb">Analyse — Sémaphore Patrimoine</p>
    <h1>La Crau — maison de village, {n_lots} appartements indépendants</h1>
    <p class="report-address">La Crau (83260), quartier Centre Ville Sud · {surf_annoncee} m² annoncés, {surf} m² sur les quatre lots · 3 des 4 logements loués · bâti de 1930 · DPE D</p>
    <p class="report-source">Sources : <a href="{url}">l'annonce Logic-Immo, réf. 26V49XQZ4PZT</a> (iad France, Brice Lacordaire, réf. 2131728) et <a href="{url_iad}">la fiche iad du même bien</a>, complétées le 12 octobre 2026 par le dossier envoyé par l'agence — plans des quatre lots et diagnostics techniques. <strong>L'agence a répondu le 12 octobre 2026</strong> : loyers en place des trois baux (3 050 €/mois au total), immeuble en <strong>un seul lot</strong> sans division juridique, compteurs d'eau et d'électricité individuels, T1 libre en attente de travaux couverts par l'assurance, façade à reprendre pour environ 14 000 € plus les volets. La <strong>taxe foncière est connue : 3 115 €</strong> pour 2026, contre 2 500 € provisionnés. L'état des risques du 14 avenue de la Libération, lui, n'a jamais été transmis : celui du dossier porte sur une autre maison, au 745 chemin de Peiracous à Forcalqueiret.</p>
  </header>

  <section class="strategy-exploration">
    <h2>Le bien</h2>
    <p>Maison de village sur deux étages, découpée en <strong>{n_lots} appartements indépendants</strong>, chacun avec son entrée : un T2 au rez-de-chaussée sud avec mezzanine et dressing, un T2 au rez-de-chaussée est, et deux T4 de trois chambres aux 1er et 2e étages, chacun avec sa terrasse. Deux caves, cage d'escalier commune : <strong>{annexes} m² hors Carrez</strong> au total. <strong>Immeuble en monopropriété</strong> — aucun syndic, aucune charge de copropriété : l'entretien de la maison est entièrement à notre charge, et il n'existe aucun fonds travaux mutualisé. C'est un poste à provisionner, pas une économie.</p>
    <p class="projection-note"><strong>Le certificat de superficie du 27 janvier 2022 donne {carrez} m² Carrez</strong>, détaillés pièce par pièce — exactement la surface globale annoncée, mais <strong>{ecart_lots} m² de plus que la somme des surfaces « environ » de l'annonce, qui minore chaque lot</strong>. Le tableau ci-dessous confronte les deux. DPE de 2022, bâti de 1930, chauffage électrique, facture théorique de 3 335 à 4 513 €/an ; état déclaré « rénovation nécessaire », sans devis.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Ce que dit le dossier technique reçu le 12 octobre</h2>
    <ul>
      <li><strong>Surfaces.</strong> Certificat de superficie NOSTIKA du 27 janvier 2022 : {carrez} m² Carrez au total, dont {annexes} m² d'annexes hors Carrez. Le détail pièce par pièce permet de reconstituer les quatre lots — c'est la seule base fiable pour une revente à la découpe.</li>
      <li><strong>Amiante : présence confirmée.</strong> Conduits de fluides en fibres-ciment dans les combles, en bon état, amiante fortement lié. Aucun danger en l'état, mais <strong>tout percement ou dépose impose un repérage complémentaire et une entreprise certifiée</strong> — c'est un poste à chiffrer dans les travaux, pas une clause de style.</li>
      <li><strong>Électricité : anomalies relevées.</strong> Le rapport de 2022 relève des anomalies au titre de la sécurité des personnes, dont l'absence de protection adaptée par les dispositifs différentiels et des observations sur les socles de prises. À intégrer au budget de remise en état.</li>
      <li><strong>Termites.</strong> Le bourg est en zone délimitée par arrêté préfectoral ; les parties visitées ne montrent pas d'indice, mais des éléments restent inaccessibles (plénum, poutres anciennes conservées).</li>
      <li><strong>Diagnostics du mauvais immeuble.</strong> L'agence a joint un second dossier, référence 598, daté de mars 2016 : il porte sur une maison au 745 chemin du Peiracous à Forcalqueiret, propriété d'un tiers. C'est l'adresse du vendeur, pas celle du bien — à écarter, mais cela dit le sérieux du dossier transmis.</li>
      <li><strong>Ce qui manque toujours.</strong> Les trois baux et leurs loyers, l'avis de taxe foncière, le chiffrage des travaux, l'état des risques — et la réponse à la question qui commande tout le reste : <strong>la division en quatre est-elle juridique, ou seulement physique ?</strong> Un état descriptif de division et un règlement de copropriété se créent avant de vendre lot par lot, et cela prend trois à six mois. Deux autres points à obtenir dans le même envoi : les compteurs d'électricité et d'eau sont-ils individuels par logement, et la taxe foncière porte-t-elle sur un seul avis pour l'immeuble entier.</li>
    </ul>
  </section>

  <section class="financial-projections">
    <h2>Les chiffres d'entrée</h2>
    <p>Prix affiché <strong>{prix}</strong>, soit {pm2} au m² annoncé et <strong>{pm2_reel} au m² réellement louable</strong>. Frais d'acquisition à 8 % : acte en main <strong>{acte}</strong>. Enveloppe de rafraîchissement provisionnée à <strong>{travaux}</strong>, faute de devis : <strong>prix de revient {revient}</strong>.</p>
    <p class="strategy-rationale">Apport de 10 % ({appar}) et mensualité sur 20 ans à 3,80 % assurance comprise : <strong>{mens}</strong>, calculée sur la seule quotité empruntée ({capital}).</p>
  </section>

  <section class="financial-projections">
    <h2>La grille des loyers, lot par lot</h2>
    <table class="projection-table">
      <thead><tr><th>Lot</th><th>Surface Carrez</th><th>Sur l'annonce</th><th>Loyer en place</th><th>Au m²</th><th>Renseignements de l'agence, 12 octobre 2026</th></tr></thead>
      <tbody>
{lignes_lots}
      </tbody>
    </table>
    <p class="scenario-subtitle"><strong>Ce qui rentre aujourd'hui : {loyer_en_place} par mois, soit {loyers_an} par an et {loyer_m2} au m² des {surf_louee} m² loués</strong> — les trois baux en cours, communiqués par l'agence le 12 octobre 2026. Le T1 ne produit rien : il est vide depuis un sinistre, et sa remise en état par l'assurance n'est pas datée. Remis en état et reloué à 590 €, l'immeuble encaisserait {loyer_marche} par mois : <strong>c'est une cible, pas un revenu.</strong></p>
  </section>

  <section class="financial-projections">
    <h2>Le compte au prix affiché</h2>
    <table class="projection-table">
      <thead><tr><th>Poste</th><th>Annuel</th><th>Commentaire</th></tr></thead>
      <tbody>
        <tr><td>Loyers bruts</td><td class="num">{loyers_an}</td><td>hypothèse de marché, baux non communiqués</td></tr>
        <tr><td>Vacance {vacance} %</td><td class="num">déduite</td><td>provision statistique, aucune vacance structurelle identifiée</td></tr>
        <tr><td>Charges, taxe foncière, assurance</td><td class="num">{frais_fixes}</td><td>{ch_pct} % des loyers bruts, sur provisions</td></tr>
        <tr><td>EBE</td><td class="num">{ebe}</td><td>excédent brut d'exploitation</td></tr>
        <tr><td>Impôt sur les sociétés {taux_is} %</td><td class="num">{net_an} net</td><td>convention prudente : IS sur l'EBE, intérêts non déduits</td></tr>
        <tr><td>Mensualité de crédit</td><td class="num">{mens} / mois</td><td>20 ans à 3,80 % sur {capital}</td></tr>
      </tbody>
    </table>
    <p class="scenario-subtitle">Au prix affiché : <strong>{brut} % brut</strong>, EBE {ebe}, net après IS <strong>{net_m} par mois</strong> — soit <strong>{net_revient} %</strong> du prix de revient ({net_acte} % de l'acte en main) — et un cash-flow de <strong>{cf} par mois</strong>, pour un rapport EBE / annuité de <strong>{ratio}</strong>. <strong>Le bien ne remplit aucune des deux conditions : ni le seuil de rendement, ni la couverture de sa mensualité.</strong></p>
  </section>

  <section class="financial-projections">
    <h2>Les prix qui tiendraient, selon l'assiette de loyers</h2>
    <p class="attractiveness-intro">Trois plafonds se calculent séparément — celui où le cash-flow devient nul, celui où le rapport EBE / annuité atteint 1,20 (seuil de confort du prêteur, à 20 ans) et celui du rendement cible de 5 % net sur le prix de revient. <strong>C'est le plus bas qui gouverne.</strong></p>
    <table class="projection-table">
      <thead><tr><th>Loyers annuels</th><th>Cash-flow nul</th><th>Ratio 1,20</th><th>5 % net</th><th>Plafond retenu</th><th>Sous l'affichage</th></tr></thead>
      <tbody>
{lignes_grille}
      </tbody>
    </table>
    <p class="scenario-subtitle">À l'assiette réellement encaissée ({loyer_en_place} par mois), le plafond du prêteur ressort à <strong>{plafond}</strong> — <strong>{plafond_ecart} % sous le prix affiché</strong> — tandis que le rendement de 5 % ne serait atteint qu'à <strong>{plafond_rdt}</strong>, soit {ecart_rdt} sous la demande. Les deux ancres sont donc sous le prix : ce n'est pas le loyer qui bloque, c'est le prix.</p>
    <p class="scenario-subtitle">Sensibilité : à 10 % de loyers en moins, le plafond du prêteur tombe à {plafond_bas} ; au T1 reloué à 590 € — l'hypothèse la plus favorable, celle des quatre lots loués — il monte à {plafond_haut} — <strong>toujours sous les {prix} demandés</strong>. Aucune hypothèse de loyer plausible dans ce bourg ne fait passer le prix affiché.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Ce qui décide, et ce qui inquiète</h2>
    <ul>
      <li><strong>Ce qui rentre, c'est 2 460 €/mois, pas 3 050.</strong> Le T1 est vide depuis un sinistre et ne produit rien : seuls les trois baux payent, sur une assiette 20 % plus basse que celle du potentiel. Chaque mois de vacance du T1 coûte environ 560 € de trésorerie au propriétaire — c'est précisément ce que l'assurance indemnise aujourd'hui, et l'indemnité s'arrête à la vente. Dater la remise en état est la première chose à faire écrire.</li>
      <li><strong>Le T1 est libre à cause d'un sinistre, et les travaux sont couverts par l'assurance.</strong> C'est le lot qu'on referait en premier dans le plan phasé, et une partie de la dépense est déjà prise en charge. Deux points à faire écrire : <strong>qui réalise les travaux, dans quel délai</strong>, et <strong>à qui revient l'indemnité si la vente intervient avant qu'ils soient faits</strong> — sur un achat-revente, elle doit nous être transférée ou déduite du prix.</li>
      <li><strong>La mairie financerait une partie de la façade.</strong> L'agence l'annonce sans montant ni accord : « après dépôt de dossier, la mairie finance une partie ». C'est un gain non chiffré, à ne pas inscrire au compte d'opération avant d'avoir la délibération, mais qui peut absorber une partie des {mdb_facade}.</li>
      <li><strong>Le vendeur est une SCI, pas un particulier.</strong> SCI COPA DE ROSA, propriétaire du 14 avenue de la Libération. Une cession de parts éviterait les droits de mutation — de l'ordre de 7 à 8 % du prix, soit 30 à 40 000 € à ce niveau — mais elle suppose d'auditer les comptes et les dettes de la société. C'est la seule piste qui puisse améliorer le prix sans toucher au vendeur.</li>
      <li><strong>Le prix au m² est bas — mais au m² des logements, pas des murs.</strong> {pm2_reel} au m² Carrez contre {ca_med_m2} €/m² pour la revente des logements du bourg : la décote apparente vient de ce que l'immeuble s'achète au prix d'une exploitation locative et se revend au prix d'acquéreurs occupants. C'est là, et nulle part ailleurs, qu'est la marge.</li>
      <li><strong>Le rafraîchissement n'est pas chiffré.</strong> « Quelques travaux » sur du 1930 : l'enveloppe retenue ici est une provision de {travaux} pour la location nue, et chaque 10 000 € en plus retire environ 10 000 € du plafond de prix. Le chiffrage de découpe, lui, intègre la façade à {mdb_facade} annoncés par le maçon, plus {mdb_volets} de volets provisionnés : ce sont des travaux de copropriété au sens où ils portent sur les murs, pas sur un lot.</li>
      <li><strong>Taxe foncière et charges inconnues.</strong> Provisionnées ensemble à {frais_fixes} par an, soit {ch_pct} % des loyers bruts. Sur un immeuble de quatre logements en village, ce poste peut être le double — et il se déduit directement du prix.</li>
      <li><strong>La partie de rez-de-chaussée non exploitée.</strong> Elle sert de cave aux locataires. Sa surface, ses accès et son usage possible ne sont pas communiqués : c'est le seul levier de valeur du lot, et il n'est ni chiffré ni même décrit.</li>
      <li><strong>La concentration géographique.</strong> Ce serait le troisième dossier vivant de notre pile dans le même secteur (Pignans, Gonfaron, Brignoles) : ces bourgs partagent le même marché locatif mince et la même liquidité étroite à la revente.</li>
      <li><strong>Un immeuble entier se gère.</strong> Quatre lots, quatre baux, des rotations à couvrir : la gestion se provisionne dans les charges, elle n'est pas gratuite.</li>
    </ul>
  </section>

  <section class="financial-projections">
    <h2>Lecture 3, vision marchand de biens — la valeur est dans la découpe</h2>
    <p class="attractiveness-intro">Les <strong>129 ventes d'appartements</strong> enregistrées à La Crau en 2024 et 2025 (extraction geo-DVF du 12 octobre 2026, commune 83047) donnent le prix au m² par tranche de surface. Chaque lot est valorisé sur la tranche qui le contient, entre le premier et le troisième quartile.</p>
    <table class="projection-table">
      <thead><tr><th>Lot</th><th>Surface</th><th>Fourchette DVF</th><th>Milieu de fourchette</th><th>Valeur à la médiane</th></tr></thead>
      <tbody>
{lignes_dvf}
      </tbody>
    </table>
    <p class="scenario-subtitle">Revendus à la découpe, les quatre lots représentent <strong>{ca_q1} au premier quartile, {ca_med} à la médiane et {ca_q3} au troisième quartile</strong>, soit {ca_med_m2} €/m² à la médiane. Le prix affiché ressort à <strong>{pm2_reel}</strong> : très en dessous du marché de la revente.</p>
    <p class="strategy-rationale">Mais la comparaison qui compte est ailleurs. <strong>En bloc, pour un investisseur locatif, le bien vaut ce que rapporte son exploitation</strong> — {loyers_an} par an encaissés capitalisés à 6,5 à 7 %, soit entre {expl70} et {expl65}. <strong>Le prix demandé est au-dessus</strong> : il faudrait les quatre lots loués, T1 compris, pour approcher {expl65_stab}. Il n'y a donc aucune marge en achat-revente en bloc, et même une perte : la marge entière est dans l'exécution de la découpe, et c'est une opération de marchand de biens, pas un achat de parc.</p>
  </section>

  <section class="financial-projections">
    <h2>Le compte de l'opération de découpe, au prix affiché</h2>
    <p class="attractiveness-intro">Travaux de remise en état des quatre lots provisionnés à 90 000 € (la convention maison de 400 €/m²), <strong>plus la façade à {mdb_facade} annoncés par le maçon et {mdb_volets} de volets provisionnés</strong> — des travaux qui portent sur les murs et non sur un lot, donc dus par le propriétaire quel que soit le scénario. Division et frais annexes {mdb_edd} : c'est un plancher, l'immeuble est aujourd'hui un seul lot. Portage {mdb_mois} mois à 4,2 % l'an, commercialisation des lots à 5 % du chiffre d'affaires, impôt sur les sociétés à 15 % puis 25 %.</p>
    <table class="projection-table">
      <thead><tr><th>Poste</th><th>Revente au Q1</th><th>Revente à la médiane</th><th>Revente au Q3</th></tr></thead>
      <tbody>
{lignes_mdb}
      </tbody>
    </table>
    <p class="scenario-subtitle">Prix de revient <strong>{mdb_revient}</strong> ; à la médiane des comparables, plus-value nette <strong>{mdb_nette}</strong> après {mdb_is} d'impôt, soit un ROI de <strong>{mdb_roi} %</strong> sur {mdb_mois} mois — {mdb_roi_an} % en rythme annuel. Au premier quartile, l'opération <strong>perd de l'argent</strong> ({mdb_roi_q1} %) ; au troisième, elle dégage {mdb_roi_q3} %.</p>
    <table class="projection-table">
      <thead><tr><th>Hypothèse de revente</th><th>Chiffre d'affaires</th><th>Travaux 40 k€</th><th>Travaux {mdb_travaux}</th><th>Travaux 133 k€</th></tr></thead>
      <tbody>
{lignes_prix15}
      </tbody>
    </table>
    <p class="scenario-subtitle">Prix d'achat qui laisse <strong>{mdb_cible} % de ROI net d'impôt</strong> sur {mdb_mois} mois : à la médiane et pour {mdb_travaux} de travaux, c'est <strong>{prix15_med}</strong>, soit {prix15_med_ecart} % sous le prix affiché. Pour un ROI net de 15 % seulement, le prix monterait à <strong>{prix_roi15}</strong> — et au prix affiché, le compte ressort à {roi_affiche} % de ROI, soit environ {roi_affiche_an} % par an : mieux qu'un placement sans risque, très loin de notre cible. Deux réserves : si les 222 m² annoncés sont des surfaces habitables et que le Carrez ressort 8 % en dessous, la revente médiane tombe à {ca_carrez}, le ROI au prix affiché à {roi_carrez} % et le prix cible à <strong>{prix15_med_carrez}</strong> ; et <strong>l'immeuble est un seul lot : la division juridique est à créer avant toute vente à la découpe</strong>, ce qui ajoute trois à six mois et un coût qui n'est ici provisionné qu'au plancher.</p>
  </section>

  <section class="financial-projections">
    <h2>Lecture 4 — le plan phasé, un lot à la fois</h2>
    <p class="attractiveness-intro">Trois des quatre logements sont loués : on ne peut de toute façon pas livrer des lots libres sans congé pour vendre — préavis de six mois, à l'échéance du bail. <strong>Le phasage n'est donc pas un confort, c'est la seule exécution possible</strong> — et c'est aussi la plus rentable, parce qu'on ne mobilise pas l'enveloppe de travaux d'un coup et que les loyers continuent de payer le crédit pendant l'opération.</p>
    <p class="scenario-subtitle"><strong>Le préalable est la division.</strong> Si les quatre logements ne sont séparés que physiquement, il faut d'abord créer l'état descriptif de division et le règlement de copropriété — trois à six mois, et un coût retenu ici au plancher de {mdb_edd} : une division à instruire de zéro coûte plutôt 8 000 à 15 000 €. Chaque millier d'euros au-dessus se déduit du prix d'achat au même montant. Et tant que la copropriété n'existe pas, on ne peut vendre que l'immeuble entier — c'est-à-dire au prix d'exploitation, pas à celui de la découpe.</p>
    <table class="projection-table">
      <thead><tr><th>Lot</th><th>Surface Carrez</th><th>Revente à la médiane</th><th>Coût acquisition + travaux</th><th>Marge brute</th></tr></thead>
      <tbody>
{lignes_phase}
      </tbody>
    </table>
    <p class="scenario-subtitle">Coût de revient par lot : {acq_m2} d'acquisition frais compris, plus {va_m2} de remise en état. <strong>Marge brute de l'opération phasée : {marge_phasee}</strong>, soit {marge_phasee_pct} % du prix de revient — avant portage, intérêts et impôt, mais aussi avant les loyers encaissés pendant l'opération.</p>
    <p class="strategy-rationale"><strong>Ce que le phasage change, c'est la trésorerie.</strong> Sortie au démarrage : apport plus les travaux du premier lot et la division, soit <strong>{sortie_initiale}</strong> — au lieu de <strong>{sortie_totale}</strong> si les quatre lots étaient refaits d'un coup. Le reste s'autofinance par les ventes successives.</p>
    <p class="scenario-subtitle"><strong>Le point de vigilance est la période de vacance.</strong> Tant que le lot libre ne produit rien, l'immeuble tourne en déficit : {loyers3} de loyers pour {mens_phase} de mensualité, soit {cf3} par mois. Les quatre lots loués ramènent la trésorerie à {cf4}. <strong>La première étape n'est donc pas de vendre le lot libre, mais de le remettre en état et de le louer</strong> — il stabilise le crédit, et les ventes se font ensuite au rythme des départs.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Verdict</h2>
    <p><strong>Deux lectures, et c'est la seconde qui porte le dossier.</strong> En location au prix affiché : {net_revient} % net sur le prix de revient à l'assiette réellement encaissée, cash-flow de {cf} par mois, rapport EBE / annuité de {ratio} — le bien ne tient pas, et les deux plafonds de financement ({plafond} pour la banque, {plafond_rdt} pour le rendement de 5 %) sont très loin sous la demande. <strong>En achat de parc, l'immeuble vaut {expl70} à {expl65} capitalisé sur les loyers encaissés</strong> — {expl65_stab} au plus si les quatre lots étaient loués. Le prix demandé n'est donc défendable que dans cette seconde hypothèse, et sans aucune marge pour nous.</p>
    <p class="strategy-rationale">En marchand de biens, le constat s'inverse, mais le prix a bougé. Avec les loyers réels, la façade à {mdb_facade}, {mdb_volets} de volets, la division à créer et {mdb_mois} mois de portage, le compte d'opération au prix affiché ressort à <strong>{mdb_roi} % de ROI à la médiane</strong> des comparables. <strong>Le prix qui laisse {mdb_cible} % net est désormais {prix15_med}</strong> — et {prix_roi15} pour un simple 15 % net — contre 431 000 € tant que la façade, les volets et la division n'étaient pas connus. Au prix affiché, le compte ressort à {roi_affiche} % net sur {mdb_mois} mois, soit {roi_affiche_an} % par an. C'est le prix de référence, et il ne remonte pas tant que le devis du maçon n'est pas remis et l'indemnité d'assurance du T1 arbitrée.<br><strong>L'exécution retenue reste le plan phasé</strong> : le T1 remis en état et reloué pour stabiliser le crédit ({cf4} par mois de trésorerie), puis une vente à chaque fin de bail, pour une sortie de trésorerie initiale de {sortie_initiale} au lieu de {sortie_totale}. Trois conditions restent ouvertes : la taxe foncière, le devis de la façade, et le rattachement de l'indemnité d'assurance — sans elle, le premier lot du phasage se paie deux fois.</p>
  </section>

  <footer class="report-footer">
    <p>Fiche produite pour Alexis et Rémy Barlatier — Sémaphore Patrimoine, 12 octobre 2026. Chiffres recalculés par <code>scripts/gen_fiche_la_crau_maison_village_4_appartements.py</code> ; modifier un prix, un loyer ou une charge régénère la page.</p>
  </footer>

</main>
</body>
</html>
"""

if __name__ == "__main__":
    main()
