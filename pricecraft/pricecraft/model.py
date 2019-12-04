"""Fit a regularized linear model on log-transformed prices."""

import math
import re
from dataclasses import dataclass
from statistics import median
from typing import Dict

WORDS = re.compile(r"[^\W_]+", re.UNICODE)


def features(listing):
    category = listing.category.casefold()
    tokens = sorted(set(WORDS.findall(listing.title.casefold())))[:12]
    text_scale = 1 / math.sqrt(len(tokens)) if tokens else 0.0
    values = {
        "category:" + category: 1.0,
        "condition:" + str(listing.condition): 1.0,
    }
    values.update(("word:" + token, text_scale) for token in tokens)
    return values


@dataclass
class Model:
    intercept: float
    ceiling: float
    weights: Dict[str, float]

    def predict(self, listing):
        estimate = self.intercept + sum(
            self.weights.get(key, 0.0) * value
            for key, value in features(listing).items()
        )
        return math.expm1(min(self.ceiling, max(0.0, estimate)))


def fit(listings):
    if not listings or any(row.price is None for row in listings):
        raise ValueError("training requires priced listings")

    targets = [math.log1p(row.price) for row in listings]
    training = [(features(row), target) for row, target in zip(listings, targets)]
    intercept = median(targets)
    weights = {}
    regularization = 0.008
    step = 0.25 / len(training)

    for _ in range(160):
        gradient = {}
        bias_gradient = 0.0
        for values, target in training:
            residual = intercept - target + sum(
                weights.get(key, 0.0) * value for key, value in values.items()
            )
            bias_gradient += residual
            for key, value in values.items():
                gradient[key] = gradient.get(key, 0.0) + residual * value

        intercept -= step * bias_gradient
        for key, value in gradient.items():
            previous = weights.get(key, 0.0)
            weights[key] = previous * (1 - 0.25 * regularization) - step * value

    return Model(intercept, max(targets), weights)
