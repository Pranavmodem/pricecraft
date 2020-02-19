"""Measure held-out error against a training-median baseline."""

import math
import random
from statistics import median

from .model import fit


def rmsle(actual, predicted):
    if len(actual) != len(predicted) or not actual:
        raise ValueError("metrics require equally sized, nonempty inputs")
    error = sum(
        (math.log1p(value) - math.log1p(estimate)) ** 2
        for value, estimate in zip(actual, predicted)
    )
    return math.sqrt(error / len(actual))


def holdout(listings, seed):
    if len(listings) < 5:
        raise ValueError("evaluation requires at least five listings")
    shuffled = list(listings)
    random.Random(seed).shuffle(shuffled)
    cutoff = len(shuffled) - max(1, len(shuffled) // 5)
    return shuffled[:cutoff], shuffled[cutoff:]


def evaluate(listings, seed):
    train, test = holdout(listings, seed)
    model = fit(train)
    reference = median(row.price for row in train)
    actual = [row.price for row in test]
    return {
        "seed": seed,
        "train_rows": len(train),
        "test_rows": len(test),
        "training_median": reference,
        "baseline_rmsle": rmsle(actual, [reference] * len(test)),
        "model_rmsle": rmsle(actual, [model.predict(row) for row in test]),
    }
