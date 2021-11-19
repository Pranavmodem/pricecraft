import tempfile
import unittest
from pathlib import Path

from pricecraft.artifacts import model_json, read_model
from pricecraft.listings import Listing
from pricecraft.model import fit


class ModelArtifactTests(unittest.TestCase):
    def load(self, content):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "model.json")
            path.write_text(content, encoding="utf-8")
            return read_model(path)

    def test_round_trip_and_unseen_listing(self):
        rows = [
            Listing("desk lamp", "home", 2, 12.0),
            Listing("camera body", "electronics", 5, 100.0),
        ]
        model = fit(rows)
        restored = self.load(model_json(model))
        unseen = Listing("tripod", "photography", 4)
        self.assertEqual(model, restored)
        self.assertAlmostEqual(model.predict(unseen), restored.predict(unseen))
        self.assertGreaterEqual(restored.predict(unseen), 0.0)
        self.assertLessEqual(restored.predict(unseen), 100.0 + 1e-10)

    def test_rejects_unsupported_version_and_invalid_coefficients(self):
        with self.assertRaisesRegex(ValueError, "unsupported"):
            self.load('{"format":"pricecraft/v2"}')
        for coefficient in ("true", "null", "NaN", "1e999"):
            with self.subTest(coefficient=coefficient):
                with self.assertRaisesRegex(ValueError, "coefficient"):
                    self.load(
                        '{"format":"pricecraft/v1","intercept":0,"ceiling":1,'
                        '"weights":{"word:lamp":' + coefficient + '}}'
                    )
