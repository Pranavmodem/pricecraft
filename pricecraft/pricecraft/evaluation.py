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


def _product_holdout(listings, seed):
    if len(listings) < 5:
        raise ValueError("evaluation requires at least five listings")
    groups = {}
    for row in listings:
        if row.group is None:
            raise ValueError("grouped evaluation requires a product_group on every row")
        groups.setdefault(row.group, []).append(row)
    if len(groups) < 2:
        raise ValueError("grouped evaluation requires at least two product groups")

    names = sorted(groups)
    random.Random(seed).shuffle(names)
    cutoff = len(names) - max(1, len(names) // 5)
    train = [row for name in names[:cutoff] for row in groups[name]]
    test = [row for name in names[cutoff:] for row in groups[name]]
    return train, test


def evaluate(listings, seed, *, by_product=False):
    split = _product_holdout if by_product else holdout
    train, test = split(listings, seed)
    model = fit(train)
    reference = median(row.price for row in train)
    actual = [row.price for row in test]
    return {
        "seed": seed,
        "split": "product_group" if by_product else "row",
        "train_rows": len(train),
        "test_rows": len(test),
        "training_median": reference,
        "baseline_rmsle": rmsle(actual, [reference] * len(test)),
        "model_rmsle": rmsle(actual, [model.predict(row) for row in test]),
    }
