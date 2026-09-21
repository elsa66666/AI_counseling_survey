from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.build_site_data import ROOT, build, paper_record, read_jsonl


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
            self.assertEqual(payload["summary"]["adjudicated_fields"], 21)
            by_id = {paper["paper_id"]: paper for paper in payload["papers"]}
            self.assertEqual(by_id["heinz2025therabot"]["sfpe"]["S"], "Present")
            self.assertEqual(by_id["heinz2025therabot"]["sfpe"]["E_relational_adaptation"], "No")
            self.assertEqual(by_id["heinz2025therabot"]["dependencies"]["E→S"]["presence"], "Absent")
            self.assertEqual(by_id["gratch2014distress"]["sfpe"]["P"], "Absent")

    def test_rejects_f_mode_that_conflicts_with_f_presence(self):
        record = read_jsonl(ROOT / "data/audit_results/all_consensus.jsonl")[0]
        fields = record["systems"][0]["fields"]
        fields["functions.F.label"]["label"] = "Present"
        fields["functions.F.mode"]["label"] = "NA"
        with self.assertRaisesRegex(ValueError, "F=Present conflicts with F_mode=NA"):
            paper_record(record)


if __name__ == "__main__":
    unittest.main()
