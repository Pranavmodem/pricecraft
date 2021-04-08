"""Read and write the versioned JSON model format."""

import json
import math

from .model import Model

FORMAT = "pricecraft/v1"


def model_json(model):
    return json.dumps(
        {
            "format": FORMAT,
            "intercept": model.intercept,
            "ceiling": model.ceiling,
            "weights": model.weights,
        },
        allow_nan=False,
        indent=2,
        sort_keys=True,
    )


def read_model(path):
    with open(path, encoding="utf-8") as source:
        data = json.load(source)

    if not isinstance(data, dict) or data.get("format") != FORMAT:
        raise ValueError("unsupported Pricecraft model format")
    intercept = _coefficient(data.get("intercept"))
    ceiling = _coefficient(data.get("ceiling"))
    weights = data.get("weights")
    if not 0 <= ceiling <= math.log1p(1_000_000) or not isinstance(weights, dict):
        raise ValueError("invalid Pricecraft model")

    return Model(
        intercept,
        ceiling,
        {key: _coefficient(value) for key, value in weights.items()},
    )


def _coefficient(value):
    # Models trained on the supported price range produce small coefficients.
    # The limit also keeps inference arithmetic safe for untrusted model files.
    if type(value) not in (int, float) or not -1_000 <= value <= 1_000:
        raise ValueError("invalid model coefficient")
    return float(value)
