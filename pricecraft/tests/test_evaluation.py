import unittest

from pricecraft.evaluation import holdout, rmsle


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
