import csv
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "pricecraft", *map(str, args)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    def test_example_evaluate_train_and_predict(self):
        with tempfile.TemporaryDirectory() as directory:
            dataset = Path(directory, "listings.csv")
            model = Path(directory, "model.json")
            unseen = Path(directory, "unseen.csv")
            with dataset.open("w", encoding="utf-8") as output:
                subprocess.run(
                    [sys.executable, "examples/make_listings.py"],
                    cwd=ROOT,
                    stdout=output,
                    check=True,
                )

            result = self.run_cli("evaluate", dataset)
            self.assertEqual(result.returncode, 0, result.stderr)
            scores = json.loads(result.stdout)
            self.assertEqual((scores["train_rows"], scores["test_rows"]), (216, 54))
            self.assertLess(scores["model_rmsle"], scores["baseline_rmsle"])

            result = self.run_cli("train", dataset)
            self.assertEqual(result.returncode, 0, result.stderr)
            model.write_text(result.stdout, encoding="utf-8")
            unseen.write_text(
                "title,category,condition\nceramic lamp,home,4\n",
                encoding="utf-8",
            )
            result = self.run_cli("predict", model, unseen)
            self.assertEqual(result.returncode, 0, result.stderr)
            rows = list(csv.DictReader(io.StringIO(result.stdout)))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["listing_row"], "1")
            self.assertGreater(float(rows[0]["predicted_price"]), 0)

    def test_bad_input_returns_error_without_partial_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "bad.csv")
            path.write_text("title,category\nlamp,home\n", encoding="utf-8")
            result = self.run_cli("evaluate", path)
            self.assertEqual(result.returncode, 2)
            self.assertIn("missing columns: condition, price", result.stderr)
            self.assertEqual(result.stdout, "")
