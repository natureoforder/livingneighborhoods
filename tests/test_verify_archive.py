from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from scripts.verify_archive import verify_manifest


class ArchiveManifestVerificationTests(unittest.TestCase):
    def write_manifest(self, directory, records):
        path = Path(directory) / "manifest.json"
        path.write_text(json.dumps({"records": records}), encoding="utf-8")
        return path

    def success_record(self, url, path, content_type="text/html"):
        content = Path(path).read_bytes()
        return {
            "url": url,
            "final_url": url,
            "status": 200,
            "content_type": content_type,
            "bytes": len(content),
            "sha256": sha256(content).hexdigest(),
            "local_path": str(path),
        }

    def test_accepts_checksums_and_closed_link_graph(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "index.html"
            image = root / "image.jpg"
            page.write_text('<img src="image.jpg">', encoding="utf-8")
            image.write_bytes(b"image")
            records = [
                self.success_record("https://www.livingneighborhoods.org/", page),
                self.success_record(
                    "https://www.livingneighborhoods.org/image.jpg",
                    image,
                    "image/jpeg",
                ),
            ]

            errors = verify_manifest(self.write_manifest(root, records))

            self.assertEqual(errors, [])

    def test_rejects_checksum_mismatch_and_transient_failures(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "index.html"
            page.write_text("hello", encoding="utf-8")
            record = self.success_record("https://www.livingneighborhoods.org/", page)
            record["sha256"] = "bad"
            transient = {
                "url": "https://www.livingneighborhoods.org/missing.htm",
                "final_url": "https://www.livingneighborhoods.org/missing.htm",
                "status": None,
                "content_type": None,
                "bytes": 0,
                "sha256": None,
                "local_path": None,
            }

            errors = verify_manifest(self.write_manifest(root, [record, transient]))

            self.assertTrue(any("checksum" in error for error in errors))
            self.assertTrue(any("transient" in error for error in errors))

    def test_rejects_referenced_url_missing_from_manifest(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "index.html"
            page.write_text('<a href="missing.htm">Missing</a>', encoding="utf-8")
            record = self.success_record("https://www.livingneighborhoods.org/", page)

            errors = verify_manifest(self.write_manifest(root, [record]))

            self.assertTrue(any("not represented" in error for error in errors))

    def test_cli_runs_from_repository_root(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "index.html"
            page.write_text("hello", encoding="utf-8")
            manifest = self.write_manifest(
                root,
                [self.success_record("https://www.livingneighborhoods.org/", page)],
            )
            script = Path(__file__).parents[1] / "scripts" / "verify_archive.py"

            result = subprocess.run(
                [sys.executable, str(script), str(manifest)],
                cwd=Path(__file__).parents[1],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
