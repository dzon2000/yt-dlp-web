import unittest
from html.parser import HTMLParser

from server import app


class DownloadErrorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.error_attributes: dict[str, str | None] | None = None

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        if attributes.get("id") == "download-error":
            self.error_attributes = attributes


class FrontendTests(unittest.TestCase):
    def test_homepage_renders_accessible_error_message_region(self) -> None:
        with app.test_client() as client:
            response = client.get("/")

        self.assertEqual(response.status_code, 200)
        parser = DownloadErrorParser()
        parser.feed(response.get_data(as_text=True))

        self.assertIsNotNone(parser.error_attributes)
        self.assertEqual(parser.error_attributes.get("role"), "alert")
        self.assertIn("hidden", parser.error_attributes)


if __name__ == "__main__":
    unittest.main()
