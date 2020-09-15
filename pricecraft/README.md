# Pricecraft

Pricecraft estimates resale listing prices from a title, category, and condition.

The project uses only Python's standard library.

## Evaluate a baseline

From the repository root, run:

```sh
python3 examples/make_listings.py > listings.csv
python3 -m pricecraft evaluate listings.csv --seed 19
python3 -m unittest discover -s tests -v
```

The evaluator holds out one fifth of the rows. It compares the model and a
training-set median using root mean squared logarithmic error (RMSLE).
