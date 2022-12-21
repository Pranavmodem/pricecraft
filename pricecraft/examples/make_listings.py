"""Write a deterministic, example listing dataset to standard output."""

import csv
import random
import sys


def main():
    rng = random.Random(610)
    products = (
        ("electronics", "digital camera", 115),
        ("electronics", "compact speaker", 42),
        ("electronics", "wireless headphones", 70),
        ("home", "ceramic mug", 10),
        ("home", "desk lamp", 34),
        ("home", "cast iron skillet", 55),
        ("clothing", "wool coat", 80),
        ("clothing", "cotton shirt", 22),
        ("clothing", "running shoes", 56),
    )

    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(("title", "category", "condition", "price", "product_group"))
    for category, title, base in products:
        for condition in range(1, 6):
            for variant in range(6):
                color = ("red", "blue", "black")[variant % 3]
                price = base * (0.44 + 0.13 * condition) * rng.uniform(0.90, 1.10)
                writer.writerow((
                    "{} {}".format(color, title),
                    category,
                    condition,
                    "{:.2f}".format(price),
                    title,
                ))


if __name__ == "__main__":
    main()
