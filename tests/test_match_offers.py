import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from scripts import match_offers
from scripts.match_offers import score_offer


class ScoreOfferTests(unittest.TestCase):
    def setUp(self):
        self.profile = {"python": {"skill": "Python", "level": 4, "evidence": "Projet personnel"},
                        "sql": {"skill": "SQL", "level": 2, "evidence": ""}}

    def test_case_duplicates_and_unproven_skills(self):
        result = score_offer(self.profile, [" python ", "PYTHON", "SQL", "R"])
        self.assertEqual(result["matched"], ["Python"])
        self.assertEqual(result["gaps"], ["SQL", "R"])
        self.assertAlmostEqual(result["coverage"], 1 / 3, places=4)
        self.assertGreater(result["score"], 0)

    def test_empty_offer_has_no_false_match(self):
        self.assertEqual(score_offer(self.profile, []),
                         {"score": 0.0, "coverage": 0.0, "matched": [], "gaps": []})

    def test_public_output_excludes_nonofficial_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            profile = root / "profile.csv"
            source = root / "structured.json"
            local = root / "local.json"
            public = root / "public.json"
            profile.write_text("skill,level,evidence\nPython,4,Projet personnel\n", encoding="utf-8")
            source.write_text(json.dumps({"offers": [
                {"id": "ft_1", "source": "france_travail", "publishable": True,
                 "required_skills": ["python"]},
                {"id": "other_1", "source": "other", "publishable": False,
                 "required_skills": ["python"]},
            ]}), encoding="utf-8")
            original_load = match_offers.load_profile
            with patch.multiple(match_offers, PROFILE=profile, SOURCE=source, LOCAL=local, PUBLIC=public):
                with patch.object(match_offers, "load_profile", lambda: original_load(profile)):
                    match_offers.main()
            self.assertEqual(json.loads(local.read_text(encoding="utf-8"))["n_offers"], 2)
            self.assertEqual([o["id"] for o in json.loads(public.read_text(encoding="utf-8"))["offers"]], ["ft_1"])


if __name__ == "__main__":
    unittest.main()
