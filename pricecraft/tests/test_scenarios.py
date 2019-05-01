import csv
import json
import tempfile
import unittest
from pathlib import Path

from pricecraft.listings import read_listings

CASES = Path(__file__).parent.parent / "fixtures"


class ListingScenarioTests(unittest.TestCase):
    def test_listing_contract(self):
        count = 0
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "listing.csv")
            for file in sorted(CASES.glob("*.jsonl")):
                for line in file.read_text(encoding="utf-8").splitlines():
                    case = json.loads(line)
                    count += 1
                    with self.subTest(case=case["id"]):
                        with path.open("w", encoding="utf-8", newline="") as output:
                            writer = csv.writer(output)
                            writer.writerow(("title", "category", "condition", "price"))
                            writer.writerow(case["input"])
                        if "error" in case:
                            with self.assertRaisesRegex(ValueError, case["error"]):
                                read_listings(path, priced=True)
                        else:
                            listing, = read_listings(path, priced=True)
                            self.assertEqual(
                                [listing.title, listing.category, listing.condition, listing.price],
                                case["expected"],
                            )
        self.assertGreater(count, 0)
