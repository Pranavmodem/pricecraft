import tempfile
import unittest
from pathlib import Path

from pricecraft.listings import Listing, read_listings


class ListingTests(unittest.TestCase):
    def read(self, content, *, priced):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "listings.csv")
            path.write_text(content, encoding="utf-8")
            return read_listings(path, priced=priced)

    def test_unpriced_csv_accepts_quoted_fields_and_trims_spaces(self):
        actual = self.read(
            '\ufefftitle,category,condition\n"lamp, small", home ,4\n', priced=False
        )
        self.assertEqual(actual, [Listing("lamp, small", "home", 4)])

    def test_zero_price_is_valid(self):
        actual = self.read("title,category,condition,price\nlamp,home,4,0\n", priced=True)
        self.assertEqual(actual[0].price, 0.0)

    def test_reports_row_for_invalid_condition_or_price(self):
        header = "title,category,condition,price\n"
        for row, message in (
            ("lamp,home,6,3\n", "condition must be"),
            ("lamp,home,3,nan\n", "price must be between"),
            ("lamp,home,3\n", "wrong number of columns"),
        ):
            with self.subTest(row=row):
                with self.assertRaisesRegex(ValueError, "line 2: " + message):
                    self.read(header + row, priced=True)

    def test_rejects_duplicate_headers_and_empty_files(self):
        with self.assertRaisesRegex(ValueError, "duplicate column"):
            self.read("title,category,condition,title\n", priced=False)
        with self.assertRaisesRegex(ValueError, "no listings found"):
            self.read("title,category,condition\n", priced=False)

    def test_rejects_unterminated_quotes(self):
        with self.assertRaisesRegex(ValueError, "malformed CSV"):
            self.read('title,category,condition\n"lamp,home,4\n', priced=False)
