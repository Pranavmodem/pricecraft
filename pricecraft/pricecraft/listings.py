"""Read and validate listing CSV files."""

import csv
import math
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Listing:
    title: str
    category: str
    condition: int
    price: Optional[float] = None


def read_listings(path, *, priced):
    required = {"title", "category", "condition"}
    if priced:
        required.add("price")

    with open(path, encoding="utf-8-sig", newline="") as source:
        rows = csv.DictReader(source, strict=True)
        try:
            headers = rows.fieldnames or []
        except csv.Error as exc:
            raise ValueError("malformed CSV header: {}".format(exc)) from exc
        missing = required.difference(headers)
        if missing:
            raise ValueError("missing columns: " + ", ".join(sorted(missing)))
        if len(headers) != len(set(headers)):
            raise ValueError("duplicate column names")

        listings = []
        try:
            for row in rows:
                try:
                    listings.append(_parse_row(row, priced=priced))
                except ValueError as exc:
                    raise ValueError("line {}: {}".format(rows.line_num, exc)) from exc
        except csv.Error as exc:
            raise ValueError("malformed CSV: {}".format(exc)) from exc

    if not listings:
        raise ValueError("no listings found")
    return listings


def _parse_row(row, *, priced):
    if None in row or any(value is None for value in row.values()):
        raise ValueError("wrong number of columns")

    title = row["title"].strip()
    category = row["category"].strip()
    if not title or not category:
        raise ValueError("title and category are required")

    condition = row["condition"].strip()
    if condition not in {"1", "2", "3", "4", "5"}:
        raise ValueError("condition must be an integer from 1 to 5")

    price = None
    if priced:
        try:
            price = float(row["price"])
        except ValueError as exc:
            raise ValueError("price must be a number") from exc
        if not math.isfinite(price) or not 0 <= price <= 1_000_000:
            raise ValueError("price must be between 0 and 1000000")

    return Listing(title, category, int(condition), price)
