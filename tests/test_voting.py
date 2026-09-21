import copy
import unittest

from audit_framework.config import AUDITOR_IDS
from audit_framework.voting import build_consensus, majority_vote
from tests.helpers import audit, paper


class VotingTests(unittest.TestCase):
    def test_strict_two_of_three(self):
        for votes, winner, status in [
            (["A", "A", "A"], "A", "unanimous"),
            (["A", "A", "B"], "A", "majority"),
            (["A", "B", "C"], None, "no_majority"),
            (["A", "A", "INVALID"], "A", "majority"),
            (["A", "B", "INVALID"], None, "no_majority"),
            (["A", None, None], None, "no_majority"),
            ([None, None, None], None, "no_majority"),
        ]:
            with self.subTest(votes=votes):
                result = majority_vote(votes, {"A", "B", "C"})
                self.assertEqual((result["label"], result["status"]), (winner, status))
                self.assertEqual(result["needs_review"], winner is None)
                if votes == ["A", "A", "INVALID"]:
                    self.assertEqual(result["agreement"], 0.6667)

    def test_nested_fields_and_evidence(self):
        records = {a: audit() for a in AUDITOR_IDS}
        for agent, s, f, v in zip(AUDITOR_IDS, ["Present", "Present", "Absent"],
                                 ["Absent", "Present", "INVALID"], ["V0", "V1", "V2"]):
            system = records[agent]["systems"][0]
            system["functions"]["S"].update(label=s, evidence=agent)
            system["functions"]["F"]["label"] = f
            system["dependencies"]["P_to_E"]["validation"] = v
        before = copy.deepcopy(records)
        result = build_consensus(paper().metadata, records)
        fields = result["systems"][0]["fields"]
        self.assertEqual(fields["functions.S.label"]["label"], "Present")
        self.assertIsNone(fields["functions.F.label"]["label"])
        self.assertIsNone(fields["dependencies.P_to_E.validation"]["label"])
        self.assertEqual([e["evidence"] for e in fields["functions.S.label"]["supporting_evidence"]], ["auditor_1", "auditor_2"])
        self.assertEqual(records, before)
        self.assertFalse(any("confidence" in p for p in fields))

    def test_system_names_do_not_affect_paper_folder_alignment(self):
        records = {a: audit() for a in AUDITOR_IDS}
        records["auditor_1"]["systems"][0]["system_name"] = "GPT-4o-based PST pipeline"
        records["auditor_2"]["systems"][0]["system_name"] = "LLM-based PST Annotation Framework"
        records["auditor_3"]["systems"][0]["system_name"] = "Alternative name"
        result = build_consensus(paper().metadata, records)
        system = result["systems"][0]
        self.assertEqual(len(result["systems"]), 1)
        self.assertEqual(system["system_key"], "test-paper")
        self.assertEqual(system["system_names"], {a: records[a]["systems"][0]["system_name"] for a in AUDITOR_IDS})
        self.assertEqual(system["fields"]["functions.S.label"]["invalid_agents"], [])
        self.assertTrue(result["full_agreement"])

    def test_no_eligible_systems_is_not_failed(self):
        records = {a: {**audit(), "systems": []} for a in AUDITOR_IDS}
        result = build_consensus(paper().metadata, records)
        self.assertTrue(result["completed"])
        self.assertEqual(result["systems"], [])
        self.assertTrue(result["full_agreement"])

    def test_independent_majorities_can_conflict(self):
        records = {a: audit() for a in AUDITOR_IDS}
        # All three individual records obey F absent -> dependency absent.
        records["auditor_1"]["systems"][0]["functions"]["F"].update(label="Absent", mode="NA")
        for edge in ("S_to_F", "F_to_P", "E_to_F"):
            records["auditor_1"]["systems"][0]["dependencies"][edge].update(presence="Absent", validation="NA")
        records["auditor_2"]["systems"][0]["functions"]["F"].update(label="INVALID", mode="NA")
        fields = build_consensus(paper().metadata, records)["systems"][0]
        self.assertIsNone(fields["fields"]["functions.F.label"]["label"])
        self.assertTrue(fields["needs_review"])

    def test_judge_adjudication_preserves_first_stage_votes_and_adds_evidence(self):
        records = {a: audit() for a in AUDITOR_IDS}
        records["auditor_1"]["systems"][0]["functions"]["S"].update(label="Present", evidence="positive")
        records["auditor_2"]["systems"][0]["functions"]["S"].update(label="Absent", evidence="negative")
        records["auditor_3"]["systems"][0]["functions"]["S"]["label"] = "INVALID"
        decision = {"label": "Present", "evidence": [{"auditor": "auditor_1", "evidence": "positive",
                    "location": "Methods", "rationale": "Implements state inference"}],
                    "summary": "The positive evidence satisfies S."}
        result = build_consensus(paper().metadata, records,
                                 {"systems.*.functions.S.label": decision},
                                 {"status": "success", "model": "gpt-5.5"})
        field = result["systems"][0]["fields"]["functions.S.label"]
        self.assertEqual(field["label"], "Present")
        self.assertEqual(field["status"], "adjudicated")
        self.assertEqual(field["agent_labels"], {"auditor_1": "Present", "auditor_2": "Absent",
                                                  "auditor_3": "INVALID"})
        self.assertEqual(field["supporting_evidence"], decision["evidence"])
        self.assertEqual(field["pre_adjudication"]["status"], "no_majority")


if __name__ == "__main__":
    unittest.main()
