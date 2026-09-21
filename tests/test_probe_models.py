import json
import unittest

from audit_framework.llm_client import CallError, Response
from scripts.probe_models import probe_model


class ProbeModelsTests(unittest.TestCase):
    def test_success_and_fenced_json(self):
        for content in ('{"ok":true}', '```json\n{"ok":true}\n```'):
            result = probe_model("deepseek-v3", "key", "https://example/v1", call=lambda *a: Response("raw", content, "returned", {}))
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["returned_model"], "returned")

    def test_failures_are_classified_without_retry(self):
        def failed(*args):
            raise CallError("rate_limit", "HTTP 429", retry_after=7)
        result = probe_model("claude-sonnet-5", "key", "https://example/v1", call=failed)
        self.assertEqual(result["status"], "rate_limit")
        self.assertEqual(result["retry_after"], 7)

    def test_invalid_json_is_not_repaired(self):
        result = probe_model("test", "key", "https://example/v1",
                             call=lambda *a: Response("raw", "Here is JSON: {'ok': True}", None, {}))
        self.assertEqual(result["status"], "invalid_json")


if __name__ == "__main__":
    unittest.main()
