from dataclasses import dataclass
import json
from pathlib import Path
import time

from jsonschema import Draft202012Validator

from .auditor import BACKOFF_DELAYS, parse_json_response
from .config import AUDITOR_IDS
from .llm_client import CallError, call_llm
from .schema import ALLOWED_LABELS, EVIDENCE_FIELDS, get_path
from .storage import atomic_write, fingerprint, load_json, save_json


@dataclass
class JudgeResult:
    status: str
    decisions: dict
    calls: int = 0
    error_type: str | None = None


def _opinion(audit, field):
    if audit is None:
        return None, {}
    if field == "paper_input_completeness":
        return audit.get(field), {}
    path = field.removeprefix("systems.*.")
    systems = audit.get("systems", [])
    if not systems:
        return None, {}
    label = get_path(systems[0], path)
    parent = get_path(systems[0], path.rsplit(".", 1)[0]) if "." in path else None
    evidence = {key: parent[key] for key in EVIDENCE_FIELDS if isinstance(parent, dict) and key in parent}
    return label, evidence


def collect_disputes(consensus, audits):
    """Collect no-majority fields with at least one legal first-stage vote."""
    fields = [("paper_input_completeness", consensus["paper_input_completeness"])]
    if consensus["systems"]:
        fields.extend(("systems.*." + path, value)
                      for path, value in consensus["systems"][0]["fields"].items())
    disputes = []
    for field, vote in fields:
        if vote["status"] != "no_majority":
            continue
        allowed = ALLOWED_LABELS[field]
        opinions = []
        legal_count = 0
        for auditor in AUDITOR_IDS:
            label, evidence = _opinion(audits.get(auditor), field)
            if label in allowed:
                legal_count += 1
            opinions.append({"auditor": auditor, "label": label if label in allowed else "INVALID", **evidence})
        if legal_count:
            disputes.append({"field": field, "allowed_labels": list(allowed), "opinions": opinions})
    return disputes


def build_judge_schema(disputes):
    evidence_item = {
        "type": "object",
        "properties": {
            "auditor": {"type": "string", "enum": list(AUDITOR_IDS)},
            "evidence": {"type": "string"},
            "location": {"type": "string"},
            "rationale": {"type": "string"},
        },
        "required": ["auditor", "evidence", "location", "rationale"],
        "additionalProperties": False,
    }
    decision_properties = {}
    for dispute in disputes:
        decision_properties[dispute["field"]] = {
            "type": "object",
            "properties": {
                "label": {"type": "string", "enum": dispute["allowed_labels"]},
                "evidence": {"type": "array", "items": evidence_item},
                "summary": {"type": "string"},
            },
            "required": ["label", "evidence", "summary"],
            "additionalProperties": False,
        }
    return {
        "type": "object",
        "properties": {
            "decisions": {
                "type": "object",
                "properties": decision_properties,
                "required": list(decision_properties),
                "additionalProperties": False,
            }
        },
        "required": ["decisions"],
        "additionalProperties": False,
    }


def build_judge_messages(protocol, paper_metadata, disputes):
    instructions = """You are the second-stage judge in a multi-agent paper audit.
Adjudicate only the disputed fields supplied below. Review every available auditor
label, evidence statement, location, rationale, and confidence. Choose exactly one
of the allowed labels for every field. Do not return null or INVALID. For S/F/P/E
function presence, the only legal labels are Present and Absent. Synthesize only
evidence already supplied by the auditors; do not invent quotations or locations.
Preserve disagreements in the summary and explain why the selected evidence meets
the protocol threshold. Return only JSON conforming to the judge schema."""
    protocol_without_output_template = protocol.split("# 16. REQUIRED OUTPUT SCHEMA", 1)[0]
    payload = json.dumps({"paper": paper_metadata, "disputes": disputes}, ensure_ascii=False, indent=2)
    return [
        {"role": "system", "content": instructions},
        {"role": "user", "content": "AUDIT PROTOCOL\n" + protocol_without_output_template +
         "\n\nDISPUTED FIRST-STAGE OPINIONS\n" + payload},
    ]


def load_saved_decisions(directory, disputes):
    try:
        data = load_json(Path(directory) / "decision.json")["decisions"]
        expected = {item["field"]: set(item["allowed_labels"]) for item in disputes}
        if set(data) != set(expected) or any(data[field]["label"] not in labels for field, labels in expected.items()):
            return {}
        return data
    except (OSError, ValueError, KeyError, TypeError):
        return {}


def run_judge(paper_metadata, disputes, config, *, protocol, output, overwrite=False,
              call=call_llm, sleep=time.sleep):
    if not disputes:
        return JudgeResult("not_needed", {})
    directory = Path(output) / paper_metadata["paper_id"] / "judge"
    schema = build_judge_schema(disputes)
    messages = build_judge_messages(protocol, paper_metadata, disputes)
    signature = fingerprint({"messages": messages, "schema": schema, "config": config.public()})
    if not overwrite:
        try:
            status = load_json(directory / "status.json")
            decisions = load_saved_decisions(directory, disputes)
            if status.get("status") == "success" and status.get("signature") == signature and decisions:
                return JudgeResult("loaded", decisions)
        except (OSError, ValueError):
            pass
    directory.mkdir(parents=True, exist_ok=True)
    save_json(directory / "input.json", {"paper": paper_metadata, "disputes": disputes})
    save_json(directory / "judge.schema.json", schema)
    save_json(directory / "status.json", {"status": "running", "signature": signature, "config": config.public()})
    attempts = directory / "attempts"
    previous = [int(path.name) for path in attempts.glob("*") if path.is_dir() and path.name.isdigit()]
    offset, calls = max(previous, default=0), 0
    validator = Draft202012Validator(schema)
    failure = None
    for attempt in range(config.max_retries + 1):
        attempt_dir = attempts / f"{offset + attempt + 1:04d}"
        attempt_dir.mkdir(parents=True, exist_ok=True)
        calls += 1
        try:
            response = call(messages, schema, config)
            atomic_write(attempt_dir / "raw_api_response.json", response.raw)
            atomic_write(attempt_dir / "raw_response.txt", response.content)
            atomic_write(directory / "raw_response.txt", response.content)
            data = parse_json_response(response.content)
            errors = list(validator.iter_errors(data))
            if errors:
                raise ValueError(errors[0].message)
            save_json(attempt_dir / "decision.json", data)
            save_json(directory / "decision.json", data)
            status = {"status": "success", "signature": signature, "config": config.public(),
                      "returned_model": response.model, "usage": response.usage,
                      "calls_this_run": calls, "last_attempt": attempt_dir.name}
            save_json(attempt_dir / "result.json", status)
            save_json(directory / "status.json", status)
            return JudgeResult("success", data["decisions"], calls)
        except (CallError, json.JSONDecodeError, ValueError) as exc:
            kind = exc.error_type if isinstance(exc, CallError) else "invalid_json" if isinstance(exc, json.JSONDecodeError) else "schema_invalid"
            message = str(exc).replace(config.api_key, "<redacted>") if config.api_key else str(exc)
            failure = {"status": "failed", "error_type": kind, "error_message": message,
                       "retry_count": calls, "signature": signature, "config": config.public(),
                       "calls_this_run": calls}
            if isinstance(exc, CallError) and exc.raw:
                atomic_write(attempt_dir / "raw_api_response.json", exc.raw)
            save_json(attempt_dir / "result.json", failure)
            if isinstance(exc, CallError) and not exc.retryable:
                break
            if attempt < config.max_retries:
                delay = exc.retry_after if isinstance(exc, CallError) and exc.retry_after is not None else BACKOFF_DELAYS[min(attempt, len(BACKOFF_DELAYS) - 1)]
                sleep(delay)
    save_json(directory / "status.json", failure)
    return JudgeResult("failed", {}, calls, failure["error_type"])
