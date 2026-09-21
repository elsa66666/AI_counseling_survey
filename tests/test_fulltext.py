from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import httpx

from audit_framework.fulltext import FulltextError, check_identity, extract_html, retrieve
from tests.helpers import paper


class FulltextTests(unittest.TestCase):
    def test_abstract_and_wrong_paper_rejected(self):
        with self.assertRaises(FulltextError):
            extract_html("<article><h1>Abstract</h1>Short abstract</article>")
        with self.assertRaises(FulltextError):
            check_identity("Cognitive Reframing Psychotherapy", "Unrelated astronomy manuscript")

    def test_cache_reuse_no_network(self):
        html = '<article><h1>Test paper</h1><h2>Introduction</h2>' + "Scientific content. " * 400 + '<h2>Methods</h2></article>'
        requests = []
        def handler(request):
            requests.append(request.url)
            return httpx.Response(200, text=html)
        with TemporaryDirectory() as tmp, httpx.Client(transport=httpx.MockTransport(handler)) as client:
            first = retrieve(paper(), Path(tmp), client=client)
            second = retrieve(paper(), Path(tmp), client=client)
            self.assertEqual(first.content, second.content)
            self.assertEqual(len(requests), 1)


if __name__ == "__main__":
    unittest.main()
