"""Command-line interface for Pricecraft."""

import argparse
import csv
import json
import sys

from .artifacts import model_json, read_model
from .evaluation import evaluate
from .listings import read_listings
from .model import fit


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m pricecraft")
    commands = parser.add_subparsers(dest="command", required=True)

    evaluate_parser = commands.add_parser("evaluate", help="score a held-out split")
    evaluate_parser.add_argument("listings")
    evaluate_parser.add_argument("--seed", type=int, default=19)

    train_parser = commands.add_parser("train", help="write a JSON model to stdout")
    train_parser.add_argument("listings")

    predict_parser = commands.add_parser("predict", help="write CSV prices to stdout")
    predict_parser.add_argument("model")
    predict_parser.add_argument("listings")

    args = parser.parse_args(argv)
    try:
        if args.command == "predict":
            model = read_model(args.model)
            listings = read_listings(args.listings, priced=False)
            writer = csv.writer(sys.stdout, lineterminator="\n")
            writer.writerow(("listing_row", "predicted_price"))
            for row, listing in enumerate(listings, start=1):
                writer.writerow((row, "{:.2f}".format(model.predict(listing))))
        else:
            listings = read_listings(args.listings, priced=True)
            if args.command == "train":
                print(model_json(fit(listings)))
            else:
                report = evaluate(listings, args.seed)
                print(json.dumps(report, indent=2, sort_keys=True))
    except (OSError, ValueError, csv.Error) as exc:
        parser.exit(2, "pricecraft: {}\n".format(exc))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
