#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Promotion — terrain d'activité ZAC des Florides, Marignane (13700).

Annonce BureauxLocaux « Vente Entrepôt Marignane 13700 » (réf. 21382150-0001V,
agence IMMPROVE Industrie & Logistique) : foncier divisible de 12 834 m² à
94 238 m², « à partir de 1 219 230 € », soit 95 €/m² HD (hors droits), avec
5 % HT du prix de vente d'honoraires à la charge de l'acquéreur (mention de
l'annonce sœur réf. 21864230-0009V).

Lecture PURE PROMOTION : acheter le foncier, construire des locaux d'activité,
revendre. Aucun revenu locatif n'est modélisé : la branche promotion du moteur
n'a pas de formule de rendement, et la décision se juge sur la marge nette sur
prix de revient, après frais d'acquisition, travaux, VRD, honoraires, taxes,
portage, commercialisation et fiscalité.

Sources des hypothèses :
- prix du foncier : annonce (95 €/m² HD + 5 % HT d'honoraires acquéreur) ;
- ancrages foncier DVF 2025 à Marignane : 83,0 €/m² sur 46 865 m² (17/04/2025)
  et 125,0 €/m² sur 21 233 m² (11/06/2025), 69,6 €/m² sur 16 782 m² (19/12/2025) ;
- prix de sortie : DVF 2025 ventes de locaux industriels et commerciaux —
  Marignane 23 ventes, médiane 1 520 €/m² (531 €/m² pour 3 011 m², 781 €/m²
  pour 15 300 m², 1 411 €/m² pour 1 042 m², 2 647 €/m² pour 680 m²) ; zone
  aéroportuaire (Marignane, Vitrolles, Saint-Victoret, Les Pennes-Mirabeau,
  Marseille) 114 ventes, médiane 1 621 €/m². Demandés constatés dans la ZAC des
  Florides : 1 800 €/m² pour un bâtiment neuf de 1 886 m² (3 395 000 €).
- coût de construction : 400 à 800 €/m² pour un entrepôt et 600 à 1 000 €/m²
  pour un site de production (Axis MO), ~500 €/m² en moyenne (Thibault Bâtiment
  Industriel), 300 à 1 500 €/m² selon spécifications (Selectra), 550 à 700 €/m²
  pour de la logistique de grande taille (Le Moniteur, 2021-2023).
"""
import statistics as st

# --- Le foncier proposé ------------------------------------------------------
SURF_LOT = 12834.0                 # plus petit lot proposé
PRIX_M2_HD = 95.0                  # €/m² hors droits, prix affiché
HONORAIRES_PCT = 0.05              # 5 % HT du prix de vente, charge acquéreur
DROITS_PCT = 0.07                  # droits d'enregistrement + émoluments notaire
PRIX_FONCIER_HD = SURF_LOT * PRIX_M2_HD
HONORAIRES = PRIX_FONCIER_HD * HONORAIRES_PCT
DROITS = (PRIX_FONCIER_HD + HONORAIRES) * DROITS_PCT
FONCIER_CHARGE = PRIX_FONCIER_HD + HONORAIRES + DROITS
FONCIER_M2_TERRAIN = FONCIER_CHARGE / SURF_LOT

# --- Coûts de construction et d'opération (par m² construit, HT) -------------
TRAVAUX_BAS, TRAVAUX_BASE, TRAVAUX_HAUT = 600.0, 700.0, 900.0
VRD_PCT_TRAVAUX = 0.13             # voiries, réseaux, espaces verts, clôtures
HONORAIRES_TRAVAUX_PCT = 0.09      # architecte, BET, AMO, géomètre, CT, SPS
ASSURANCES_PCT = 0.03              # dommages-ouvrage, tous risques chantier
TAXE_AMENAGEMENT_M2 = 40.0         # ESTIMEE : taux communal non obtenu (voir note)
PRIX_SORTIE_BAS, PRIX_SORTIE_BASE, PRIX_SORTIE_HAUT = 1200.0, 1500.0, 1800.0
COMMERCIALISATION_PCT = 0.04       # honoraires de vente HT, sur le CA
IMPRÉVUS_PCT_TRAVAUX = 0.05
PORTAGE_MOIS = 18
PORTAGE_TAUX = 0.045               # part financée : 70 % du besoin
PORTAGE_PART_FINANCEE = 0.70
IS_TAUX = 0.25

# --- Emprises testées (la SHON autorisée est l'inconnue n° 1) ----------------
EMPRISES = ((0.30, "30 % — hypothèse basse"), (0.40, "40 % — médiane"),
            (0.50, "50 % — hypothèse haute"))


def cout_hors_foncier(surf_construite, travaux):
    vrd = travaux * VRD_PCT_TRAVAUX
    hono = travaux * HONORAIRES_TRAVAUX_PCT
    assu = travaux * ASSURANCES_PCT
    imprevus = travaux * IMPRÉVUS_PCT_TRAVAUX
    ta = TAXE_AMENAGEMENT_M2 * surf_construite
    besoin = (travaux + vrd + hono + assu + imprevus) * surf_construite + ta
    portage = besoin * PORTAGE_PART_FINANCEE * PORTAGE_TAUX * PORTAGE_MOIS / 12.0
    return dict(travaux=travaux * surf_construite, vrd=vrd * surf_construite,
                honoraires=hono * surf_construite, assurances=assu * surf_construite,
                imprevus=imprevus * surf_construite, taxe=ta, portage=portage,
                total=besoin + portage)


def operation(emprise_pct, prix_sortie, travaux=TRAVAUX_BASE):
    surf = SURF_LOT * emprise_pct
    ch = cout_hors_foncier(surf, travaux)
    ca = surf * prix_sortie
    com = ca * COMMERCIALISATION_PCT
    cout_total = ch['total'] + FONCIER_CHARGE + com
    marge = ca - cout_total
    is_ = max(0.0, marge) * IS_TAUX
    return dict(emprise=emprise_pct, surf=surf, ca=ca, com=com,
                cout_hors_foncier=ch['total'], foncier=FONCIER_CHARGE,
                cout_total=cout_total, revient_m2=cout_total / surf,
                marge=marge, marge_pct_ca=marge / ca * 100.0,
                roi_pct=marge / cout_total * 100.0, is_=is_,
                net=marge - is_, net_pct_ca=(marge - is_) / ca * 100.0)


def prix_foncier_max(cible_pct_ca, emprise_pct, prix_sortie,
                     travaux=TRAVAUX_BASE):
    """Prix de foncier chargé qui laisse la marge cible en % du CA."""
    surf = SURF_LOT * emprise_pct
    ch = cout_hors_foncier(surf, travaux)
    ca = surf * prix_sortie
    com = ca * COMMERCIALISATION_PCT
    marge_cible = ca * cible_pct_ca
    return ca - ch['total'] - com - marge_cible


def prix_sortie_necessaire(cible_pct_ca, emprise_pct, travaux=TRAVAUX_BASE):
    surf = SURF_LOT * emprise_pct
    ch = cout_hors_foncier(surf, travaux)
    # ca - ca*com% - couts - foncier = cible*ca  ->  ca = (couts+foncier)/(1-com%-cible)
    return ((ch['total'] + FONCIER_CHARGE)
            / (1 - COMMERCIALISATION_PCT - cible_pct_ca) / surf)


if __name__ == '__main__':
    print("=" * 78)
    print("FONCIER — ce que coûte réellement le lot de 12 834 m²")
    print("=" * 78)
    print(f"  prix affiché HD                  {PRIX_M2_HD:>10.2f} €/m²   "
          f"{PRIX_FONCIER_HD:>12,.0f} €")
    print(f"  honoraires 5 % HT acquéreur      {HONORAIRES:>12,.0f} €")
    print(f"  droits + émoluments ~7 %         {DROITS:>12,.0f} €")
    print(f"  FONCIER CHARGÉ                   {FONCIER_M2_TERRAIN:>10.2f} €/m²   "
          f"{FONCIER_CHARGE:>12,.0f} €")
    print(f"  soit +{FONCIER_M2_TERRAIN - PRIX_M2_HD:.1f} €/m² sur le prix affiché "
          f"({(FONCIER_M2_TERRAIN / PRIX_M2_HD - 1) * 100:.1f} %)")
    print()
    print("  Ancrages DVF 2025 du foncier nu à Marignane (terrains > 1 000 m²) :")
    for s, v, m2, d in ((46865, 3889795, 83.0, "17/04/2025"),
                        (21233, 2655000, 125.0, "11/06/2025"),
                        (16782, 1168370, 69.6, "19/12/2025")):
        print(f"    {d}  {s:>6,} m²  {v:>10,.0f} €  {m2:>5.1f} €/m²".replace(',', ' '))
    print(f"    annonce   {SURF_LOT:>6,.0f} m²  {PRIX_FONCIER_HD:>10,.0f} €  "
          f"{PRIX_M2_HD:>5.1f} €/m²".replace(',', ' '))
    print()
    print("=" * 78)
    print("OPÉRATION — marge de promotion selon l'emprise et le prix de sortie")
    print("=" * 78)
    for pct, lib in EMPRISES:
        for sortie in (PRIX_SORTIE_BAS, PRIX_SORTIE_BASE, PRIX_SORTIE_HAUT):
            o = operation(pct, sortie)
            print(f"  emprise {lib:<18} sortie {sortie:>6.0f} €/m²  "
                  f"{o['surf']:>7,.0f} m² bâtis  CA {o['ca']:>12,.0f} €  "
                  f"revient {o['revient_m2']:>7.0f} €/m²  "
                  f"marge {o['marge']:>11,.0f} € ({o['marge_pct_ca']:>5.1f} % CA, "
                  f"ROI {o['roi_pct']:>5.1f} %, net {o['net']:>11,.0f} €)".replace(',', ' '))
        print()
    print("=" * 78)
    print("PRIX DE FONCIER MAX acceptable selon l'emprise (marge cible 15 % du CA)")
    print("=" * 78)
    for pct, lib in EMPRISES:
        for sortie in (PRIX_SORTIE_BAS, PRIX_SORTIE_BASE, PRIX_SORTIE_HAUT):
            mx = prix_foncier_max(0.15, pct, sortie)
            print(f"  {lib:<18} sortie {sortie:>6.0f} €/m²  →  foncier chargé max "
                  f"{mx:>12,.0f} €  soit {mx / SURF_LOT:>7.1f} €/m² de terrain "
                  f"({'au-dessus' if mx > FONCIER_CHARGE else 'SOUS'} du prix affiché)")
        print()
    print("=" * 78)
    print("PRIX DE SORTIE NÉCESSAIRE pour 15 % de marge (au prix affiché)")
    print("=" * 78)
    for pct, lib in EMPRISES:
        for trav in (TRAVAUX_BAS, TRAVAUX_BASE, TRAVAUX_HAUT):
            n = prix_sortie_necessaire(0.15, pct, trav)
            print(f"  {lib:<18} travaux {trav:>5.0f} €/m²  →  sortie nécessaire "
                  f"{n:>7.0f} €/m²")
        print()
    print("=" * 78)
    print("BESOIN DE FINANCEMENT (apport bancaire usuel : 20 %)")
    print("=" * 78)
    for pct, lib in EMPRISES:
        o = operation(pct, PRIX_SORTIE_BASE)
        print(f"  {lib:<18} coût total {o['cout_total']:>12,.0f} €   "
              f"apport 20 % {o['cout_total'] * 0.2:>11,.0f} €".replace(',', ' '))
