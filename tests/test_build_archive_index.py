import csv
import io
import unittest

from scripts.build_archive_index import render_page_index


class PageIndexTests(unittest.TestCase):
    def test_indexes_archived_and_missing_pages_but_not_assets(self):
        manifest = {
            "records": [
                {
                    "url": "https://www.livingneighborhoods.org/",
                    "final_url": "https://www.livingneighborhoods.org/",
                    "status": 200,
                    "content_type": "text/html",
                    "error": None,
                    "discovered_from": None,
                    "bytes": 303,
                    "sha256": "abc",
                    "local_path": "archive/www.livingneighborhoods.org/index.html",
                },
                {
                    "url": "https://www.livingneighborhoods.org/missing.htm",
                    "final_url": "https://www.livingneighborhoods.org/missing.htm",
                    "status": 404,
                    "content_type": "text/html",
                    "error": "HTTP Error 404: Not Found",
                    "discovered_from": "https://www.livingneighborhoods.org/",
                    "bytes": 0,
                    "sha256": None,
                    "local_path": None,
                },
                {
                    "url": "https://www.livingneighborhoods.org/old-section/",
                    "final_url": "https://www.livingneighborhoods.org/old-section/",
                    "status": 404,
                    "content_type": "text/html",
                    "error": "HTTP Error 404: Not Found",
                    "discovered_from": "https://www.livingneighborhoods.org/menu.htm",
                    "bytes": 0,
                    "sha256": None,
                    "local_path": None,
                },
                {
                    "url": "https://www.livingneighborhoods.org/missing.jpg",
                    "final_url": "https://www.livingneighborhoods.org/missing.jpg",
                    "status": 404,
                    "content_type": "text/html",
                    "error": "HTTP Error 404: Not Found",
                    "discovered_from": "https://www.livingneighborhoods.org/",
                    "bytes": 0,
                    "sha256": None,
                    "local_path": None,
                },
            ]
        }

        rows = list(csv.DictReader(io.StringIO(render_page_index(manifest))))

        self.assertEqual(
            [row["source_url"] for row in rows],
            [
                "https://www.livingneighborhoods.org/",
                "https://www.livingneighborhoods.org/missing.htm",
                "https://www.livingneighborhoods.org/old-section/",
            ],
        )
        self.assertEqual(rows[0]["result"], "archived")
        self.assertEqual(rows[0]["archive_link"], "www.livingneighborhoods.org/index.html")
        self.assertEqual(rows[0]["byte_size"], "303")
        self.assertEqual(rows[1]["result"], "http_error")
        self.assertEqual(rows[1]["status"], "404")
        self.assertEqual(rows[1]["notes"], "HTTP Error 404: Not Found")
        self.assertEqual(rows[1]["archive_link"], "")

    def test_reports_unclassified_failures_as_transient_errors(self):
        manifest = {
            "records": [
                {
                    "url": "https://www.livingneighborhoods.org/timeout.html",
                    "final_url": "https://www.livingneighborhoods.org/timeout.html",
                    "status": None,
                    "content_type": None,
                    "error": "timed out",
                    "discovered_from": None,
                    "bytes": 0,
                    "sha256": None,
                    "local_path": None,
                }
            ]
        }

        row = next(csv.DictReader(io.StringIO(render_page_index(manifest))))

        self.assertEqual(row["result"], "transient_error")
        self.assertEqual(row["status"], "")
        self.assertEqual(row["notes"], "timed out")


if __name__ == "__main__":
    unittest.main()
