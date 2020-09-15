"""Command-line interface for Pricecraft."""

import argparse
import json

from .evaluation import evaluate
from .listings import read_listings


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m pricecraft")
    commands = parser.add_subparsers(dest="command", required=True)
    evaluate_parser = commands.add_parser("evaluate", help="score a held-out split")
    evaluate_parser.add_argument("listings")
    evaluate_parser.add_argument("--seed", type=int, default=19)
    args = parser.parse_args(argv)

    try:
        listings = read_listings(args.listings, priced=True)
        print(json.dumps(evaluate(listings, args.seed), indent=2, sort_keys=True))
    except (OSError, ValueError) as exc:
        parser.exit(2, "pricecraft: {}\n".format(exc))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
