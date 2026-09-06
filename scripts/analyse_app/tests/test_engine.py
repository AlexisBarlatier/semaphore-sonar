# -*- coding: utf-8 -*-
"""Tests moteur + scoring (fixtures calibrées sur les pages publiées).

Écarts documentés vs notes publiées de l'ère LLM :
- JEAN_ROSTAND : écart 0,0 (9,2 == 9,2) — référence exacte
- MILOS        : +0,4 (7,7 vs 7,3) — la fiche publiée intégrait ~45 €/an de
                 charges supplémentaires non documentées ; verdict identique
- CUERS_MDB    : +0,7 (3,9 vs 3,2) — note publiée plafonnée par jugement ;
                 le moteur applique désormais la règle « risque bloquant »
                 (plafond 3,9, verdict fuir) à valider par Alexis/Rémy

Exécution : /home/alexis-barlatier/.hermes/hermes-agent/venv/bin/python3 \
    -m unittest discover -s scripts/analyse_app/tests -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from analyse_app import engine as E        # noqa: E402
from analyse_app import scoring as S        # noqa: E402
from analyse_app import schema              # noqa: E402
from analyse_app.fixtures import (          # noqa: E402
    JEAN_ROSTAND, MILOS, VILLA_CUERS_MDB)


class TestEngine(unittest.TestCase):

    def test_revient_jean_rostand(self):
        c = E.compute(JEAN_ROSTAND)
        self.assertTrue(c["calculable"])
        self.assertEqual(c["frais_acquisition"], 2600.0)
        self.assertEqual(c["prix_revient_total"], 79600.0)

    def test_amortissement_milos_conforme_fiche(self):
        # Fiche MILOS : « 90 % du prix de revient sur 30 ans (~236 €/an) »
        c = E.compute(MILOS)
        self.assertEqual(c["fiscal"]["amortissement"], 236.25)

    def test_rendement_double_jean_rostand(self):
        c = E.compute(JEAN_ROSTAND)
        r = c["rendements"]
        self.assertAlmostEqual(r["net_sur_achat_pct"], 10.01, places=2)
        self.assertAlmostEqual(r["net_sur_revient_pct"], 9.68, places=2)

    def test_ratio_cout_valeur(self):
        c = E.compute(JEAN_ROSTAND)
        self.assertAlmostEqual(c["ratio_cout_valeur"], 0.637, places=3)

    def test_frais_parking_unitaire_neuf(self):
        # Barème : 1 place 7 k€ neuf → 675 + 2 × 100 = 875 €
        rec = {
            "bien": {"type_bien": "parking", "neuf": True, "lots": {"count": 1}},
            "annonce": {"prix_retenu_euros": 7000.0},
            "hypotheses": {},
        }
        frais, _ = E.frais_acquisition_estimes(rec)
        self.assertEqual(frais, 875.0)

    def test_pas_calculable_sans_loyers(self):
        rec = dict(JEAN_ROSTAND)
        rec["marche"] = {"valeur": {"retenue_euros": 125000.0}, "loyers": None}
        c = E.compute(rec)
        self.assertFalse(c["calculable"])
        self.assertIn("loyers manquants", c["raison"])


class TestScoring(unittest.TestCase):

    def test_note_jean_rostand_exacte(self):
        c = E.compute(JEAN_ROSTAND)
        note, verdict, comp = S.note_et_verdict(JEAN_ROSTAND, c)
        self.assertEqual(note, 9.2)
        self.assertEqual(verdict, "acheter")
        self.assertIsInstance(comp, dict)
        self.assertAlmostEqual(comp["s_adequation"], 7.5, places=1)

    def test_note_milos_ecart_documente(self):
        c = E.compute(MILOS)
        note, verdict, _ = S.note_et_verdict(MILOS, c)
        self.assertEqual(note, 7.7)
        self.assertEqual(verdict, "acheter")

    def test_risque_bloquant_plafonne(self):
        c = E.compute(VILLA_CUERS_MDB)
        note, verdict, comp = S.note_et_verdict(VILLA_CUERS_MDB, c)
        self.assertEqual(note, 3.9)
        self.assertEqual(verdict, "fuir")
        self.assertIsInstance(comp, dict)
        self.assertTrue(comp.get("bloquant"))

    def test_note_promotion_aucune_formule(self):
        rec = {"analyse": {"branche": "promotion"}, "bien": {},
               "annonce": {}, "marche": {}, "hypotheses": {}}
        note, _, comp = S.note_et_verdict(rec, E.compute(rec))
        self.assertIsNone(note)
        self.assertIsNotNone(comp)

    def test_seuils_verdict(self):
        self.assertEqual(S.verdict(7.0), "acheter")
        self.assertEqual(S.verdict(6.5), "acheter")
        self.assertEqual(S.verdict(6.4), "negocier")
        self.assertEqual(S.verdict(4.0), "negocier")
        self.assertEqual(S.verdict(3.9), "fuir")
        self.assertIsNone(S.verdict(None))


class TestSchema(unittest.TestCase):

    def test_fixtures_valides(self):
        for rec in (JEAN_ROSTAND, MILOS, VILLA_CUERS_MDB):
            self.assertEqual(schema.validate_record(rec), [], rec["slug"])
            self.assertEqual(schema.champs_manquants(rec), [], rec["slug"])

    def test_missing_list(self):
        rec = {"bien": {"type_bien": "parking", "sous_type": "sous-sol"},
               "annonce": {}, "marche": {}, "hypotheses": {},
               "analyse": {"branche": "parking"}}
        m = schema.champs_manquants(rec)
        self.assertIn("marche.loyers", m)
        self.assertIn("analyse.attractivite", m)

    def test_validation_prix_negatif(self):
        rec = dict(JEAN_ROSTAND)
        rec["annonce"] = {"prix_affiche_euros": -5.0}
        self.assertTrue(any("prix" in e for e in schema.validate_record(rec)))


if __name__ == "__main__":
    unittest.main()
