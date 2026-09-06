# -*- coding: utf-8 -*-
"""Scoring — note /10 et verdict (formule officielle du skill, § Note globale).

Note = 0,40 × min(10, rendement_net × 1,5)
     + 0,30 × max(0, 10 − (ratio_coût/valeur − 0,7) × 15)
     + 0,20 × adéquation quartier (moyenne pondérée des 6 scores)
     + 0,10 × (10 − moyenne des sévérités de risques)

Verdict : ≥ 6,5 « À acheter » ; 4,0–6,4 « À négocier » ; < 4,0 « À fuir ».
MDB : « rendement net » remplacé par le ROI net (même formule ×1,5).
Promotion : pas de formule formalisée → note None (affichage « — »).

Matrices de pondération de l'attractivité (ordre = DIMENSIONS_RESIDENTIEL) :
seules les stratégies documentées dans le skill ont une matrice ; les autres
(ld-nue, parking-ld, pro-bail, promotion) utilisent la moyenne simple —
écart documenté, à affiner si besoin.
"""

RDT_POIDS = 0.40
RATIO_POIDS = 0.30
ADEQ_POIDS = 0.20
RISQUE_POIDS = 0.10

MATRICES = {
    # (transports, commerces, ecoles, securite, demande, dynamisme)
    "ld-meuble": (20, 15, 20, 20, 20, 5),
    "airbnb": (20, 25, 0, 20, 15, 20),
    "colocation": (25, 10, 5, 15, 25, 20),
    "mdb": (15, 15, 5, 15, 10, 30),
}

SEUIL_ACHETER = 6.5
SEUIL_NEGOCIER = 4.0
# Un risque marqué « bloquant » (ex. absence de garantie décennale, PLU
# incompatible) plafonne la note sous le seuil « À fuir » : le deal est mort
# quel que soit le rendement. Valeur documentée — ajustable.
NOTE_CAP_BLOQUANT = 3.9


def adequation_score(record):
    """Moyenne pondérée des 6 scores d'attractivité (sinon None)."""
    analyse = record.get("analyse") or {}
    dims = analyse.get("attractivite")
    if not dims or len(dims) < 6:
        return None
    code = ((analyse.get("strategie_retenue") or {}).get("code") or "")
    poids = MATRICES.get(code)
    scores = [d.get("score") for d in dims[:6]]
    if any(s is None for s in scores):
        return None
    if poids and all(p >= 0 for p in poids):
        total = sum(s * p for s, p in zip(scores, poids))
        denom = sum(poids)
        return round(total / denom, 2) if denom else round(sum(scores) / 6.0, 2)
    return round(sum(scores) / 6.0, 2)


def risque_moyen(record):
    risques = (record.get("analyse") or {}).get("risques")
    if not risques:
        return None
    sev = [r.get("severite") for r in risques]
    if any(s is None for s in sev):
        return None
    return round(sum(sev) / len(sev), 2)


def note_globale(record, computed):
    """(note /10 arrondie à 1 décimale, composantes) ou (None, raisons)."""
    branche = (record.get("analyse") or {}).get("branche")
    if branche == "promotion":
        return None, ["branche promotion : pas de formule de note formalisée"]
    if not computed.get("calculable"):
        return None, computed.get("raison") or ["fiche non calculable"]

    analyse = record.get("analyse") or {}
    if branche == "mdb":
        m = computed.get("mdb") or {}
        if m.get("roi_pct") is None:
            return None, ["ROI MDB manquant"]
        s_rdt = min(10.0, m["roi_pct"] * 1.5)
        ratio = m["prix_revient_total"] / (
            (record.get("marche") or {}).get("revente", {}).get("prix_euros")
            or 1) if (record.get("marche") or {}).get("revente", {}).get(
            "prix_euros") else None
    else:
        rdt = (computed.get("rendements") or {}).get("net_sur_valeur_pct")
        ratio = computed.get("ratio_cout_valeur")
        if rdt is None or ratio is None:
            return None, ["rendement ou ratio manquant"]
        s_rdt = min(10.0, rdt * 1.5)

    if ratio is None:
        return None, ["ratio coût/valeur manquant"]
    s_ratio = max(0.0, 10.0 - (ratio - 0.7) * 15.0)

    adeq = adequation_score(record)
    risque = risque_moyen(record)
    if adeq is None:
        return None, ["scores attractivité manquants"]
    if risque is None:
        return None, ["risques manquants"]

    s_risque = 10.0 - risque
    note = (RDT_POIDS * s_rdt + RATIO_POIDS * s_ratio
            + ADEQ_POIDS * adeq + RISQUE_POIDS * s_risque)
    composantes = {
        "s_rendement": round(s_rdt, 2),
        "s_ratio": round(s_ratio, 2),
        "s_adequation": adeq,
        "s_risque": round(s_risque, 2),
        "note_brute": round(note, 2),
    }
    # Risque bloquant : la note est plafonnée sous le seuil « À fuir »
    if any(r.get("bloquant") for r in (record.get("analyse") or {}).get(
            "risques") or []):
        note = min(note, NOTE_CAP_BLOQUANT)
        composantes["bloquant"] = True
        composantes["note_plafonnee"] = NOTE_CAP_BLOQUANT
    return round(note, 1), composantes


def verdict(note):
    if note is None:
        return None
    if note >= SEUIL_ACHETER:
        return "acheter"
    if note >= SEUIL_NEGOCIER:
        return "negocier"
    return "fuir"


def note_et_verdict(record, computed):
    note, composantes = note_globale(record, computed)
    return note, verdict(note), composantes
