"""Exercise the static-site checker through its public CLI."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('check-static-site.py')
REPO = Path(__file__).resolve().parents[2]


class StaticSiteContract(unittest.TestCase):
    def run_check(self, root):
        return subprocess.run(
            [sys.executable, str(SCRIPT), '--root', str(root)],
            capture_output=True, text=True, check=False,
        )

    def test_current_site_is_well_formed_and_links_resolve(self):
        result = self.run_check(REPO)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_local_asset_and_page_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'index.html').write_text(
                '<!DOCTYPE html><html><head><title>Test</title></head><body>'
                '<a href="/missing/">Missing page</a><img src="logo.png" alt="Logo">'
                '<a href="https://example.org">External</a><a href="#top">Fragment</a>'
                '</body></html>'
            )
            result = self.run_check(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('/missing/', result.stdout + result.stderr)
            self.assertIn('logo.png', result.stdout + result.stderr)

    def test_missing_basic_structure_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'index.html').write_text('<html><body>No head or title</body></html>')
            result = self.run_check(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('structure', result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
