from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from audit_framework.auditor import run_single_auditor
from audit_framework.config import AUDITOR_IDS
from audit_framework.llm_client import CallError, Response
from audit_framework.runner import run_batch, rebuild_consensus
from audit_framework.storage import load_json, save_json
from scripts.run_audit import main
from tests.helpers import PROTOCOL, audit, config


class RunnerTests(unittest.TestCase):
    def test_batch_survives_one_agent_failure_and_exports_all_papers(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            records = [{"bib": '@article{paper-' + str(i) + ', title={Test Paper}, year={2024}}',
                        "url": "https://example.org/" + str(i)} for i in range(2)]
            save_json(root / "papers.json", records)
            (root / "prompt.md").write_text(PROTOCOL, encoding="utf-8")

            def fetch(paper, *args):
                paper.content = "Shared evidence for " + paper.paper_id
                paper.source = {"source": paper.url}

            def single(paper, agent, cfg, **kwargs):
                def fake(*args):
                    if paper.paper_id == "paper-0" and agent == "auditor_2":
                        raise CallError("authentication_error", "HTTP 401", retryable=False)
                    return Response("synthetic envelope", json.dumps(audit()), "test-model", {})
                return run_single_auditor(paper, agent, cfg, **kwargs, call=fake, sleep=lambda _: None)

            kwargs = dict(papers_path=root / "papers.json", prompt_path=root / "prompt.md", output=root / "out",
                          cache=root / "cache", configs={a: config() for a in AUDITOR_IDS}, retrieve_fn=fetch,
                          auditor_fn=single, log=lambda _: None)
            summary = run_batch(**kwargs, limit=2, workers=3)
            self.assertEqual(summary["total_papers"], 2)
            self.assertEqual(summary["completed_papers"], 1)
            self.assertEqual(summary["auditor_failures"], 1)
            self.assertEqual(summary["total_auditor_calls"], 6)
            # Selecting one completed paper must not discard the other paper's exports.
            summary = run_batch(**kwargs, paper_id="paper-1")
            self.assertEqual(summary["total_papers"], 2)
            self.assertEqual(summary["auditor_calls_this_run"], 0)
            # Changing only one auditor config is safe: signatures rerun only it.
            changed = dict(kwargs["configs"])
            from dataclasses import replace
            changed["auditor_2"] = replace(config(), model="replacement-model")
            summary = run_batch(**{**kwargs, "configs": changed}, paper_id="paper-1")
            self.assertEqual(summary["auditor_calls_this_run"], 1)
            with patch("httpx.post", side_effect=AssertionError("offline")), redirect_stdout(StringIO()):
                code = main(["--rebuild-consensus", "--output", str(root / "out"), "--env", str(root / "missing.env")])
            self.assertEqual(code, 1)  # One intentionally failed paper remains.
            # An interrupted rerun with a changed input must not mix old audits.
            path = root / "out/paper-1/audit_signatures.json"
            signatures = load_json(path); signatures["auditor_3"] = "different-input"
            save_json(path, signatures)
            rebuild_consensus(root / "out", log=lambda _: None)
            result = load_json(root / "out/paper-1/consensus.json")
            self.assertEqual(result["failed_auditors"], ["auditor_3"])
            self.assertEqual(result["systems"][0]["fields"]["functions.S.label"]["status"], "majority")


if __name__ == "__main__":
    unittest.main()
