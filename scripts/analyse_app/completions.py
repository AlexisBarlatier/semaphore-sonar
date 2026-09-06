# -*- coding: utf-8 -*-
"""Compléments de re-saisie appliqués par import_legacy après extraction.

Pourquoi : certaines entrées ne sont pas extractibles des pages (ex. taux de
vacance base choisi à l'époque) mais sont connues/justifiables. Elles sont
saisies ici une fois, puis réappliquées à chaque import (idempotent).

Règle : toute valeur ajoutée doit être justifiable par la page ou une
décision documentée (commentaire). Aucun résultat calculé n'est stocké.
"""

COMPLETIONS = {
    # Parc de 11 lots : la page justifie une vacance binaire négligeable en
    # base (point mort ~2 places louées, CF net positif dès 3/11)
    "2026-09-03-11-parkings-jean-rostand-la-seyne": {
        "hypotheses": {
            "vacance_base_pct": 0.0,
            "vacance_best_pct": 0.0,
            "vacance_worst_pct": 25.0,
            "vacance_justification": "Parc de 11 lots : vacance binaire "
                                     "statistiquement négligeable en base "
                                     "(grille 0-11, point mort ~2 places) — "
                                     "re-saisie 06/09/2026",
        },
    },
}


def apply(rec):
    """Applique les compléments éventuels à une fiche (en place)."""
    slug = rec.get("slug")
    comp = COMPLETIONS.get(slug)
    if not comp:
        return
    for section, values in comp.items():
        if not isinstance(values, dict):
            rec[section] = values
            continue
        target = rec.setdefault(section, {})
        if isinstance(target, dict):
            target.update(values)
        else:
            rec[section] = values
