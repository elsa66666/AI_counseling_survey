import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from jsonschema import Draft202012Validator

from audit_framework.config import AUDITOR_IDS
from audit_framework.judge import build_judge_schema, collect_disputes, run_judge
from audit_framework.llm_client import Response
from audit_framework.voting import build_consensus
from tests.helpers import PROTOCOL, audit, config, paper


class JudgeTests(unittest.TestCase):
    def test_collects_each_supported_no_majority_pattern_but_not_all_invalid(self):
        records = {agent: audit() for agent in AUDITOR_IDS}
        systems = {agent: records[agent]["systems"][0] for agent in AUDITOR_IDS}
        for agent, label in zip(AUDITOR_IDS, ["Present", "Absent", "INVALID"]):
            systems[agent]["functions"]["S"]["label"] = label
        for agent, mode in zip(AUDITOR_IDS, ["Static", "Dynamic", "Unclear"]):
            systems[agent]["functions"]["F"]["mode"] = mode
        for agent, label in zip(AUDITOR_IDS, ["Present", "INVALID", "INVALID"]):
            systems[agent]["functions"]["P"]["label"] = label
        for agent in AUDITOR_IDS:
            systems[agent]["functions"]["E"]["label"] = "INVALID"
        disputes = collect_disputes(build_consensus(paper().metadata, records), records)
        fields = {item["field"] for item in disputes}
        self.assertIn("systems.*.functions.S.label", fields)       # A/B/INVALID
        self.assertIn("systems.*.functions.F.mode", fields)        # A/B/C
        self.assertIn("systems.*.functions.P.label", fields)       # A/INVALID/INVALID
        self.assertNotIn("systems.*.functions.E.label", fields)    # no usable opinion

    def test_f_mode_excludes_na_when_final_f_is_present(self):
        records = {agent: audit() for agent in AUDITOR_IDS}
        systems = {agent: records[agent]["systems"][0] for agent in AUDITOR_IDS}
        for agent, label, mode in zip(
            AUDITOR_IDS,
            ["Present", "Absent", "Present"],
            ["Dynamic", "NA", "Static"],
        ):
            systems[agent]["functions"]["F"].update(label=label, mode=mode)
        disputes = collect_disputes(build_consensus(paper().metadata, records), records)
        dispute = next(item for item in disputes if item["field"] == "systems.*.functions.F.mode")
        self.assertEqual(dispute["allowed_labels"], ["Static", "Dynamic", "Unclear"])
        self.assertEqual([opinion["label"] for opinion in dispute["opinions"]],
                         ["Dynamic", "INVALID", "Static"])
        enum = build_judge_schema([dispute])["properties"]["decisions"]["properties"] \
            ["systems.*.functions.F.mode"]["properties"]["label"]["enum"]
        self.assertNotIn("NA", enum)

    def test_schema_links_disputed_f_presence_to_f_mode(self):
        records = {agent: audit() for agent in AUDITOR_IDS}
        systems = {agent: records[agent]["systems"][0] for agent in AUDITOR_IDS}
        for agent, label, mode in zip(
            AUDITOR_IDS,
            ["Present", "Absent", "INVALID"],
            ["Dynamic", "Static", "NA"],
        ):
            systems[agent]["functions"]["F"].update(label=label, mode=mode)
        disputes = collect_disputes(build_consensus(paper().metadata, records), records)
        schema = build_judge_schema(disputes)
        decision = lambda label, mode: {"decisions": {
            "systems.*.functions.F.label": {"label": label, "evidence": [], "summary": "summary"},
            "systems.*.functions.F.mode": {"label": mode, "evidence": [], "summary": "summary"},
        }}
        validator = Draft202012Validator(schema)
        self.assertFalse(list(validator.iter_errors(decision("Present", "Static"))))
        self.assertTrue(list(validator.iter_errors(decision("Present", "NA"))))
        self.assertFalse(list(validator.iter_errors(decision("Absent", "NA"))))
        self.assertTrue(list(validator.iter_errors(decision("Absent", "Static"))))

    def test_judge_saves_raw_response_and_structured_evidence(self):
        records = {agent: audit() for agent in AUDITOR_IDS}
        for agent, label in zip(AUDITOR_IDS, ["Present", "Absent", "INVALID"]):
            item = records[agent]["systems"][0]["functions"]["S"]
            item.update(label=label, evidence=agent + " evidence", location="Methods", rationale=agent + " rationale")
        disputes = collect_disputes(build_consensus(paper().metadata, records), records)
        self.assertEqual([item["field"] for item in disputes], ["systems.*.functions.S.label"])
        schema = build_judge_schema(disputes)
        decision = {"decisions": {"systems.*.functions.S.label": {
            "label": "Present",
            "evidence": [{"auditor": "auditor_1", "evidence": "auditor_1 evidence",
                          "location": "Methods", "rationale": "auditor_1 rationale"}],
            "summary": "The cited implementation meets S."
        }}}
        self.assertEqual(schema["properties"]["decisions"]["properties"]
                         ["systems.*.functions.S.label"]["properties"]["label"]["enum"],
                         ["Present", "Absent"])
        with TemporaryDirectory() as tmp:
            result = run_judge(
                paper().metadata, disputes, config(), protocol=PROTOCOL, output=Path(tmp),
                call=lambda *args: Response("raw envelope", "```json\n" + json.dumps(decision) + "\n```",
                                            "gpt-5.5", {}),
            )
            directory = Path(tmp) / "test-paper/judge"
            self.assertEqual(result.status, "success")
            self.assertEqual(result.decisions, decision["decisions"])
            self.assertTrue((directory / "raw_response.txt").read_text(encoding="utf-8").startswith("```json"))
            self.assertEqual(json.loads((directory / "decision.json").read_text(encoding="utf-8")), decision)


if __name__ == "__main__":
    unittest.main()
