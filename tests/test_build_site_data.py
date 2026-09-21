from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.build_site_data import ROOT, build


class SiteDataTests(unittest.TestCase):
    def test_public_export_matches_consensus_dataset(self):
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            result = build(
                ROOT / "data/audit_results/all_consensus.jsonl",
                ROOT / "data/audit_results/audit_summary.json",
                directory / "audits.json",
                directory / "audits.csv",
                directory / "site/audits.json",
                ROOT / "prompts/sfpe_protocol.md",
                directory / "site/protocol.md",
            )
            payload = json.loads((directory / "audits.json").read_text(encoding="utf-8"))
            self.assertEqual(result["papers"], 47)
            self.assertEqual(len(payload["papers"]), 47)
            self.assertTrue(all(paper["title"] and paper["paper_url"] and paper["year"] for paper in payload["papers"]))
            self.assertTrue(all(len(paper["dependencies"]) == 7 for paper in payload["papers"]))
            self.assertTrue(all(paper["sfpe"][key] in {"Present", "Absent"}
                                for paper in payload["papers"] for key in "SFPE"))
            self.assertEqual(payload["summary"]["no_majority_fields"], 0)
            self.assertEqual(payload["summary"]["adjudicated_fields"], 19)
            by_id = {paper["paper_id"]: paper for paper in payload["papers"]}
            self.assertEqual(by_id["heinz2025therabot"]["sfpe"]["S"], "Present")
            self.assertEqual(by_id["gratch2014distress"]["sfpe"]["P"], "Absent")


if __name__ == "__main__":
    unittest.main()
