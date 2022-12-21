import unittest

from pricecraft.evaluation import _product_holdout, evaluate, holdout, rmsle
from pricecraft.listings import Listing


class EvaluationTests(unittest.TestCase):
    def test_holdout_is_repeatable_and_disjoint(self):
        rows = list(range(25))
        train, test = holdout(rows, seed=31)
        self.assertEqual((train, test), holdout(rows, seed=31))
        self.assertEqual((len(train), len(test)), (20, 5))
        self.assertEqual(set(train).intersection(test), set())
        self.assertEqual(sorted(train + test), rows)

    def test_small_dataset_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least five"):
            holdout(list(range(4)), seed=31)

    def test_rmsle_is_zero_for_exact_predictions(self):
        self.assertEqual(rmsle([0, 12], [0, 12]), 0.0)
        self.assertGreater(rmsle([0, 12], [0, 18]), 0.0)

    def test_grouped_split_never_shares_a_product_group(self):
        rows = [
            Listing("listing", "home", 4, float(index), str(index % 5))
            for index in range(20)
        ]
        train, test = _product_holdout(rows, seed=19)
        self.assertEqual(len(train) + len(test), len(rows))
        self.assertTrue({row.group for row in train}.isdisjoint(row.group for row in test))
        self.assertEqual(evaluate(rows, 19, by_product=True)["split"], "product_group")

    def test_grouped_split_requires_groups(self):
        rows = [Listing("listing", "home", 4, 1.0)] * 5
        with self.assertRaisesRegex(ValueError, "product_group"):
            evaluate(rows, 19, by_product=True)
