# -*- coding: utf-8 -*-
"""Moteur de calcul — conventions du skill analyse-annonce-immo (SCI à l'IS).

Tout est dérivé des ENTRÉES de la fiche ; rien n'est stocké en base.

Définitions retenues (alignées skill, version 2026-09) :
- revenus bruts annuels   = Σ (lots × loyer mensuel × 12)
- EBE = revenus bruts × (1 − vacance_base/100) − charges annuelles
        − provision rénovation (2,5 % × revenus bruts, règle interne)
- amortissement annuel    = quote_part_bati × prix retenu / durée
        (sous-sol/surélevé bâti amortissable ; extérieur non ; MDB : 0 ;
         résidentiel : quote-part bâti 90 %, durée 30 ans par défaut)
- IS = 15 % × max(0, EBE − amortissement)
- net après IS = EBE − IS   (c'est le CF que l'on compare à une mensualité)
- rendement net  = net après IS / valeur après travaux × 100,
        avec valeur après travaux = valeur marché retenue (input) ;
        rendements secondaires affichés : sur prix de revient et prix d'achat
- ratio coût/valeur = prix de revient / valeur marché retenue
- MDB : pas d'amortissement, IS sur la plus-value de cession, note sur ROI.

Le moteur ne produit JAMAIS une valeur si une entrée indispensable manque :
les fonctions retournent None et le listing affiche « — ».
"""

from .schema import champs_manquants

IS_RATE = 0.15
PROVISION_RENOVATION_PCT = 2.5      # cagnotte travaux (règle interne)
DUREE_AMORTISSEMENT_DEFAUT_ANS = 30
QUOTE_PART_BATI_DEFAUT = 90.0       # % du prix de revient (fiche MILOS 09/2026)

# Barèmes de frais par défaut (utilisés seulement si la fiche ne précise pas
# `hypotheses.frais_acquisition_euros` — toujours préférer le chiffre réel)
FRAIS_PCT_ANCIEN = 0.075
FRAIS_PCT_NEUF = 0.03
FRAIS_PCT_TERRAIN = 0.07
# Barème notaire parking constaté 09/2026 (Gilson) : 1 place 5 k€ → 675 €
# (neuf < 2 ans) ou 1 275 € (ancien) + 100 €/1 000 € au-delà.
PARKING_BASE_NEUF = 675.0
PARKING_BASE_ANCIEN = 1275.0
PARKING_PALIER_EUROS = 5000.0
PARKING_PAS_EUROS = 100.0
PARKING_LOTS_FORFAIT_PCT = 0.03    # lots multiples : défaut ≈ 3 % (approximatif)


def _g(record, *path, default=None):
    cur = record
    for p in path:
        if not isinstance(cur, dict) or p not in cur or cur[p] is None:
            return default
        cur = cur[p]
    return cur


def frais_acquisition_estimes(record):
    """Estimation des frais d'acquisition (émoluments notaire) quand la fiche
    ne donne pas le chiffre réel. Toujours documenté comme estimation."""
    explicite = _g(record, "hypotheses", "frais_acquisition_euros")
    if explicite:
        return explicite, "explicite (fiche)"
    bien = record.get("bien") or {}
    type_bien = bien.get("type_bien")
    prix = _g(record, "annonce", "prix_retenu_euros") \
        or _g(record, "annonce", "prix_affiche_euros")
    if not prix:
        return None, None
    neuf = bool(bien.get("neuf"))
    if type_bien == "terrain":
        return prix * FRAIS_PCT_TERRAIN, "estimation 7 % (terrain)"
    if type_bien == "parking":
        lots = (bien.get("lots") or {}).get("count") or 1
        if lots <= 1:
            base = PARKING_BASE_NEUF if neuf else PARKING_BASE_ANCIEN
            suppl = max(0.0, (prix - PARKING_PALIER_EUROS)
                        / 1000.0 * PARKING_PAS_EUROS)
            return base + suppl, "barème parking unitaire (estimation)"
        return prix * PARKING_LOTS_FORFAIT_PCT, "estimation 3 % (bloc lots)"
    pct = FRAIS_PCT_NEUF if neuf else FRAIS_PCT_ANCIEN
    return prix * pct, f"estimation {pct:.1%} (bien {'neuf' if neuf else 'ancien'})"


def _amortissable(record):
    bien = record.get("bien") or {}
    analyse = record.get("analyse") or {}
    if analyse.get("branche") == "mdb":
        return False
    if analyse.get("branche") == "promotion":
        return False
    if bien.get("type_bien") == "terrain":
        return False
    if bien.get("type_bien") == "parking":
        # sous-sol / surélevé = bâti amortissable ; extérieur = non
        return (bien.get("sous_type") or "") in ("sous-sol", "surélevé",
                                                 "surleve", "box", "ferme")
    return True


def amortissement_annuel(record):
    if not _amortissable(record):
        return 0.0
    bien = record.get("bien") or {}
    hyp = record.get("hypotheses") or {}
    # Conforme fiche MILOS 09/2026 : amortissement = 90 % du PRIX DE REVIENT
    # (frais inclus) sur 30 ans. Le prix de revient doit donc être calculé.
    rv = prix_revient(record)
    if not rv:
        return None
    duree = hyp.get("duree_amortissement_ans") or DUREE_AMORTISSEMENT_DEFAUT_ANS
    qp = hyp.get("quote_part_bati_pct")
    if qp is None:
        qp = QUOTE_PART_BATI_DEFAUT
    return rv["total"] * (qp / 100.0) / duree


def revenus_bruts_annuels(record):
    """Σ lots × loyer mensuel × 12. Null si un loyer manque."""
    loyers = _g(record, "marche", "loyers")
    if not loyers:
        return None
    total = 0.0
    for l in loyers:
        q = l.get("quantite") or 1
        lm = l.get("loyer_mensuel_euros")
        if lm is None:
            return None
        total += q * lm * 12
    return total


def charges_annuelles(record):
    """Somme des lignes de charges saisies + provision rénovation."""
    charges = _g(record, "hypotheses", "charges") or {}
    revenus = revenus_bruts_annuels(record)
    lignes = {
        "taxe_fonciere": charges.get("taxe_fonciere_annuelle_euros", 0.0) or 0.0,
        "copro": charges.get("charges_copro_annuelles_euros", 0.0) or 0.0,
        "pno": charges.get("pno_annuelle_euros", 0.0) or 0.0,
        "entretien": charges.get("entretien_annuel_euros", 0.0) or 0.0,
        "comptabilite": charges.get("comptabilite_annuelle_euros", 0.0) or 0.0,
    }
    provision = 0.0
    if revenus and not charges.get("provision_desactivee"):
        provision = revenus * PROVISION_RENOVATION_PCT / 100.0
    lignes["provision_renovation"] = round(provision, 2)
    total = sum(lignes.values())
    return total, lignes


def ebe(record):
    revenus = revenus_bruts_annuels(record)
    if revenus is None:
        return None
    vacance = _g(record, "hypotheses", "vacance_base_pct")
    if vacance is None:
        return None          # taux de vacance non renseigné : pas calculable
    charges, _ = charges_annuelles(record)
    return revenus * (1.0 - vacance / 100.0) - charges


def prix_revient(record):
    """Prix retenu + frais réels (ou estimés) + travaux immédiats."""
    prix = _g(record, "annonce", "prix_retenu_euros") \
        or _g(record, "annonce", "prix_affiche_euros")
    if not prix:
        return None
    frais, frais_label = frais_acquisition_estimes(record)
    travaux = _g(record, "bien", "travaux", "montant_euros", default=0.0) or 0.0
    divers = _g(record, "hypotheses", "frais_divers_euros", default=0.0) or 0.0
    if frais is None:
        return None
    return {
        "prix": prix,
        "frais_acquisition": round(frais, 2),
        "frais_label": frais_label,
        "travaux": travaux,
        "divers": divers,
        "total": round(prix + frais + travaux + divers, 2),
    }


def fiscal(record):
    """(EBE, amortissement, résultat fiscal, IS annuel, net après IS)."""
    e = ebe(record)
    if e is None:
        return None
    amort = amortissement_annuel(record)
    if amort is None:
        return None
    resultat = e - amort
    is_annuel = IS_RATE * max(0.0, resultat)
    return {
        "ebe": round(e, 2),
        "amortissement": round(amort, 2),
        "resultat_fiscal": round(resultat, 2),
        "is_annuel": round(is_annuel, 2),
        "net_apres_is": round(e - is_annuel, 2),
        "cf_mensuel_net": round((e - is_annuel) / 12.0, 2),
    }


def valeur_apres_travaux(record):
    """Valeur utilisée comme base du rendement net (skill : « valeur après
    travaux ») = valeur marché retenue, sinon milieu de fourchette."""
    v = _g(record, "marche", "valeur") or {}
    retenue = v.get("retenue_euros")
    if retenue:
        return retenue, "valeur marché retenue"
    if v.get("basse_euros") and v.get("haute_euros"):
        return (v["basse_euros"] + v["haute_euros"]) / 2.0, "milieu de fourchette"
    if v.get("basse_euros"):
        return v["basse_euros"], "fourchette basse (conservateur)"
    return None, None


def rendements(record):
    """Rendements en % — (net/valeur, net/revient, net/achat, brut/revient)."""
    fisc = fiscal(record)
    if fisc is None:
        return None
    net = fisc["net_apres_is"]
    valeur, vlabel = valeur_apres_travaux(record)
    rv = prix_revient(record)
    prix = _g(record, "annonce", "prix_retenu_euros") \
        or _g(record, "annonce", "prix_affiche_euros")
    out = {
        "net_apres_is_euros": round(net, 2),
        "valeur_base_euros": valeur,
        "valeur_base_label": vlabel,
    }
    if valeur:
        out["net_sur_valeur_pct"] = round(net / valeur * 100.0, 2)
    else:
        out["net_sur_valeur_pct"] = None
    if rv and rv["total"]:
        out["net_sur_revient_pct"] = round(net / rv["total"] * 100.0, 2)
        ebe_v = fisc["ebe"]
        out["brut_sur_revient_pct"] = round(ebe_v / rv["total"] * 100.0, 2)
    if prix:
        out["net_sur_achat_pct"] = round(net / prix * 100.0, 2)
    return out


def ratio_cout_valeur(record):
    rv = prix_revient(record)
    valeur, _ = valeur_apres_travaux(record)
    if not rv or not valeur:
        return None
    return round(rv["total"] / valeur, 3)


# ---------------------------------------------------------------------------
# Marchand de biens (MDB) — substitutions du skill (ROI au lieu du rendement)
# ---------------------------------------------------------------------------
def mdb_compte(record):
    """Compte d'exploitation MDB : PV nette après IS et ROI."""
    rv = prix_revient(record)
    revente = _g(record, "marche", "revente") or {}
    prix_revente = revente.get("prix_euros")
    if not rv or not prix_revente:
        return None
    frais_vente = revente.get("frais_vente_euros")
    if frais_vente is None:
        frais_vente = prix_revente * 0.05          # défaut documenté
    portage_mois = revente.get("duree_mois") or 0
    portage_mensuel = revente.get("portage_mensuel_euros") or 0.0
    portage_total = portage_mois * portage_mensuel
    pv_brute = prix_revente - frais_vente - rv["total"] - portage_total
    is_pv = IS_RATE * max(0.0, pv_brute)
    pv_nette = pv_brute - is_pv
    roi = pv_nette / rv["total"] * 100.0 if rv["total"] else None
    return {
        "prix_revient_total": rv["total"],
        "frais_vente": round(frais_vente, 2),
        "portage_total": round(portage_total, 2),
        "pv_brute": round(pv_brute, 2),
        "is_pv": round(is_pv, 2),
        "pv_nette": round(pv_nette, 2),
        "roi_pct": round(roi, 2) if roi is not None else None,
    }


def compute(record):
    """Point d'entrée : dictionnaire des résultats calculables (None si les
    entrées manquent). N'écrit jamais dans la fiche."""
    branche = _g(record, "analyse", "branche")
    result = {
        "calculable": False,
        "raison": [],
        "revenus_bruts_annuels": None,
        "frais_acquisition": None,
        "prix_revient_total": None,
        "fiscal": None,
        "rendements": None,
        "ratio_cout_valeur": None,
        "mdb": None,
    }
    if not branche:
        result["raison"].append("branche inconnue")
        return result

    if branche in ("promotion",):
        # Pas de formule de rendement/note formalisée pour la promotion :
        # la fiche reste descriptive (marge promoteur 12 % côté agent).
        result["calculable"] = True
        return result

    if branche == "mdb":
        result["revenus_bruts_annuels"] = None
        rv = prix_revient(record)
        if rv:
            result["frais_acquisition"] = rv["frais_acquisition"]
            result["prix_revient_total"] = rv["total"]
        m = mdb_compte(record)
        if m:
            result["calculable"] = True
            result["mdb"] = m
        else:
            result["raison"].append("revente ou revient manquant")
        return result

    # Branches locatives (residentiel / professionnel / parking)
    revenus = revenus_bruts_annuels(record)
    fisc = fiscal(record)
    rv = prix_revient(record)
    if rv:
        result["frais_acquisition"] = rv["frais_acquisition"]
        result["prix_revient_total"] = rv["total"]
    result["revenus_bruts_annuels"] = revenus
    if revenus is None:
        result["raison"].append("loyers manquants")
    if fisc is None:
        result["raison"].append("hypothèses de charges/vacance manquantes")
    if rv is None:
        result["raison"].append("prix manquant")
    if result["raison"]:
        return result
    result["fiscal"] = fisc
    result["rendements"] = rendements(record)
    result["ratio_cout_valeur"] = ratio_cout_valeur(record)
    result["calculable"] = True
    return result
