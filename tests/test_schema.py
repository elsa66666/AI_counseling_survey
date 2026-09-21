import unittest

from audit_framework.data_loader import load_papers
from audit_framework.config import ROOT
from audit_framework.schema import AuditValidationError, VOTABLE_FIELDS, build_schema, validate_audit
from tests.helpers import PROTOCOL, SCHEMA, audit


class SchemaTests(unittest.TestCase):
    def test_protocol_schema_and_actual_dataset(self):
        validate_audit(audit(), SCHEMA)
        self.assertEqual(len(VOTABLE_FIELDS), 22)
        papers = load_papers(ROOT / "data/papers/papers.json")
        self.assertEqual(len(papers), 47)
        self.assertEqual(len({p.paper_id for p in papers}), 47)
        self.assertIn("MIRROR", papers[23].title)
        self.assertEqual(papers[23].metadata["year"], "2025")

    def test_illegal_label(self):
        data = audit(); data["systems"][0]["functions"]["S"]["label"] = "full"
        with self.assertRaises(AuditValidationError) as ctx:
            validate_audit(data, SCHEMA)
        self.assertEqual(ctx.exception.error_type, "illegal_label")

    def test_extra_and_missing_fields_rejected(self):
        for mutate in (lambda x: x.update(invented="value"), lambda x: x.pop("systems")):
            data = audit(); mutate(data)
            with self.assertRaises(AuditValidationError):
                validate_audit(data, SCHEMA)

    def test_validation_requires_explicit_edge(self):
        data = audit(); data["systems"][0]["dependencies"]["S_to_F"]["presence"] = "Inferential"
        with self.assertRaises(AuditValidationError):
            validate_audit(data, SCHEMA)

    def test_positive_label_requires_evidence(self):
        data = audit(); data["systems"][0]["functions"]["F"]["evidence"] = ""
        with self.assertRaises(AuditValidationError):
            validate_audit(data, SCHEMA)

    def test_protocol_change_fails_fast(self):
        with self.assertRaises(ValueError):
            build_schema(PROTOCOL.replace('"Present|Absent|Unclear"', '"full|partial|none"'))


if __name__ == "__main__":
    unittest.main()
