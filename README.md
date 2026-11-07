# Pricecraft

Estimate resale listing prices from a title, category, and condition. Pricecraft
trains a regularized log-price model, compares it with a median-price baseline,
and writes predictions to CSV.

## Try it

Run from the repository root with Python 3.

```sh
cd pricecraft
python3 examples/make_listings.py > listings.csv
python3 -m pricecraft evaluate listings.csv --seed 19
python3 -m pricecraft evaluate listings.csv --seed 19 --by-product
python3 -m pricecraft train listings.csv > model.json
python3 -m pricecraft predict model.json listings.csv > predictions.csv
python3 -m unittest discover -s tests -v
```

The row split measures performance on held-out listings. The product split
keeps product families together, which tests generalization to groups the
model has not seen. On the included example, the median baseline performs
better on the product split.

See the [input format and evaluation details](pricecraft/README.md) and the
[original Mercari challenge notebook](Mercari_Challenge.ipynb).

## Credits

The original Mercari project is credited to Vijay Tulluri and Pranav Modem.
See the [MIT license](LICENSE.MD).
