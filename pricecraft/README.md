# Pricecraft

Pricecraft estimates resale listing prices from a title, category, and condition.

## Run locally

The project uses the Python standard library and has no third-party
dependencies. Historical reference runtimes are
[Python 3.7.3](https://www.python.org/downloads/release/python-373/) and
[Python 3.7.5](https://www.python.org/downloads/release/python-375/).
Use a supported Python release for ordinary use. Run the historical
interpreter offline with the example fixture if you need to replay it.

From the repository root:

```sh
python3 examples/make_listings.py > listings.csv
python3 -m pricecraft evaluate listings.csv --seed 19
python3 -m pricecraft train listings.csv > model.json
python3 -m pricecraft predict model.json listings.csv > predictions.csv
python3 -m unittest discover -s tests -v
```

## Inputs and outputs

Training and evaluation read a UTF-8 CSV with columns `title`, `category`,
`condition`, and `price`. Condition is an integer from 1 to 5, where 5
indicates better condition. Prices must be between 0 and 1,000,000 in a
consistent currency. Prediction requires only the first three fields.

Training writes a versioned JSON model to standard output. Prediction writes
a CSV with one-based listing row numbers and prices rounded to two decimal
places. The commands above reuse the example CSV to demonstrate the file
formats. Pass a separate CSV of unseen listings for inference.

## Model and evaluation

The model fits a regularized linear regression to `log1p(price)`. It uses
title tokens, category, and condition as features. Predictions are capped at
the highest training price. Evaluation shuffles the input rows with a seeded
generator and reserves one fifth of the rows before fitting. It scores the
model and the training-set median using root mean squared logarithmic error
(RMSLE). Lower is better.

On the included generator with evaluation seed 19, the split contains
216 training rows and 54 held-out rows. The training-median baseline scores
**0.7640 RMSLE** and the model scores **0.1096 RMSLE**. Related product
variants can appear on both sides of the split. These scores verify the
example pipeline and do not estimate accuracy on unseen product families or
real marketplace listings.

For a stricter comparison, add a `product_group` to every input row and run:

```sh
python3 -m pricecraft evaluate listings.csv --seed 19 --by-product
```

The grouped split holds out entire product groups so that variants of a held-out
product cannot leak into training. Treat the two split modes as different
evaluation questions and report which one produced each result.

The validation corpus in `fixtures/` exercises the listing format across
conditions, categories, Unicode text, numeric price boundaries, and invalid
values. The tests read the same CSV interface used by the CLI.

With seed 19, the grouped split holds out 30 rows from one complete group.
The model scores **0.8355 RMSLE** and the median baseline scores **0.2830**.
The median wins on this split. Use the grouped result when considering
generalization to a new product family.
