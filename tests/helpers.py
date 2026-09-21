import copy
from pathlib import Path

from audit_framework.config import ROOT, AuditorConfig
from audit_framework.data_loader import Paper, load_prompt
from audit_framework.schema import build_schema, extract_template

PROTOCOL = load_prompt(ROOT / "prompts/sfpe_protocol.md")
SCHEMA = build_schema(PROTOCOL)


def audit():
    def fill(value):
        if isinstance(value, dict):
            return {k: fill(v) for k, v in value.items()}
        if isinstance(value, list):
            return [fill(value[0])]
        return value.split("|")[0] if "|" in value else "Synthetic unit-test evidence"
    data = fill(extract_template(PROTOCOL))
    data["systems"][0]["system_name"] = "Test System"
    data["systems"][0]["borderline_cases"] = []
    return copy.deepcopy(data)


def paper():
    return Paper("test-paper", "Test paper", "https://example.org/paper", {"paper_id": "test-paper", "title": "Test paper"},
                 "Synthetic paper text", {"source": "https://example.org/paper", "extraction_warnings": []})


def config():
    return AuditorConfig("test-model", "openai", "json_schema", "https://example.org/v1", "test-secret", max_retries=1)
