# -*- coding: utf-8 -*-
"""Analyse_app — données et calculs du pipeline Sémaphore Sonar.

Principe (décision Alexis 06/09/2026) :
- `analyses/analyses.json` ne contient que des ENTRÉES (faits constatés,
  données marché sourcées, hypothèses, jugements qualitatifs chiffrés).
- AUCUN résultat de calcul n'y est stocké : prix de revient, rendements,
  ratio, note /10, verdict, classes CSS → calculés par engine/scoring au build.
"""

from .schema import (
    BRANCHES, TYPE_BIEN, STRATEGIE_CODES, DIMENSIONS,
    validate_record, RecordError,
)
from .engine import (
    compute, frais_acquisition_estimes,
)
from .scoring import (
    adequation_score, risque_moyen, note_globale, verdict, 
    note_et_verdict, RDT_POIDS, RATIO_POIDS, ADEQ_POIDS, RISQUE_POIDS,
)

__all__ = [
    "BRANCHES", "TYPE_BIEN", "STRATEGIE_CODES", "DIMENSIONS",
    "validate_record", "RecordError",
    "compute", "frais_acquisition_estimes",
    "adequation_score", "risque_moyen", "note_globale", "verdict",
    "note_et_verdict",
]
