import unittest

from scripts.archive_site import ROOT, is_html_record, links_from, local_path, normalize


class ArchiveDiscoveryTests(unittest.TestCase):
    def test_root_document_counts_as_html_by_content_type(self):
        self.assertTrue(
            is_html_record(
                {
                    "final_url": ROOT,
                    "content_type": "text/html",
                    "local_path": "archive/www.livingneighborhoods.org/index.html",
                }
            )
        )

    def test_discovers_links_hidden_in_legacy_javascript_and_meta_refresh(self):
        page = b"""
        <html>
          <meta http-equiv="refresh" content="0;URL=/ht-0/home.htm">
          <body onload="goToInFrame('../ht-0/menu-exp.htm', '../ht-0/action.htm')">
            <a href="javascript:clickWindow('../clickagreement/terms.htm','window2')">Terms</a>
            <script>var library = '../library/generativecodesv10.pdf';</script>
            <img src="../pics/example.jpg">
          </body>
        </html>
        """

        links = links_from(page, "text/html", ROOT + "ht-0/bln-exp.htm")

        self.assertIn(ROOT + "ht-0/home.htm", links)
        self.assertIn(ROOT + "ht-0/menu-exp.htm", links)
        self.assertIn(ROOT + "ht-0/action.htm", links)
        self.assertIn(ROOT + "clickagreement/terms.htm", links)
        self.assertIn(ROOT + "library/generativecodesv10.pdf", links)
        self.assertIn(ROOT + "pics/example.jpg", links)

    def test_discovers_css_and_javascript_asset_references(self):
        content = b"""
        body { background: url('../images/paper.gif'); }
        var movie = '../movies/example.mov';
        var helper = '../scripts/helper.js';
        """

        links = links_from(content, "text/css", ROOT + "styles/main.css")

        self.assertEqual(
            links,
            {
                ROOT + "images/paper.gif",
                ROOT + "movies/example.mov",
                ROOT + "scripts/helper.js",
            },
        )

    def test_normalizes_windows_paths_without_matching_partial_extensions(self):
        content = rb"""
        <img src="..\images\photo.jpg">
        <object classid="Word.Document"></object>
        """

        links = links_from(content, "text/html", ROOT + "workpackets/packet1.htm")

        self.assertIn(ROOT + "images/photo.jpg", links)
        self.assertNotIn(ROOT + "workpackets/Word.Doc", links)

    def test_normalize_canonicalizes_host_and_removes_fragments_and_queries(self):
        url = normalize(
            ROOT + "ht-0/menu-exp.htm",
            "https://livingneighborhoods.org/ht-0/archive.htm?old=1#papers",
        )

        self.assertEqual(url, ROOT + "ht-0/archive.htm")

    def test_normalize_percent_encodes_spaces(self):
        url = normalize(
            ROOT + "library/article.htm",
            "Part 1 - Article_files/style.css",
        )

        self.assertEqual(
            url,
            ROOT + "library/Part%201%20-%20Article_files/style.css",
        )

    def test_local_path_preserves_source_tree(self):
        self.assertEqual(
            local_path(ROOT + "ht-0/archive.htm").as_posix(),
            "archive/www.livingneighborhoods.org/ht-0/archive.htm",
        )


if __name__ == "__main__":
    unittest.main()
