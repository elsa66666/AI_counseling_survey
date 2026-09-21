from dataclasses import dataclass
import json
from pathlib import Path
import time

from .llm_client import CallError, call_llm
from .prompt_builder import build_prompt
from .schema import AuditValidationError, validate_audit
from .storage import atomic_write, fingerprint, load_json, save_json

BACKOFF_DELAYS = (2, 5, 10, 20)


@dataclass
class AuditResult:
    auditor_id: str
    status: str
    audit: dict | None = None
    calls: int = 0
    error_type: str | None = None


def strip_json_code_fence(text: str) -> str:
    """Remove one complete ```json/``` wrapper; do not alter JSON content."""
    stripped = text.strip()
    lines = stripped.splitlines()
    if lines and lines[0].strip().casefold() in {"```", "```json"}:
        if len(lines) >= 2 and lines[-1].strip() == "```":
            return "\n".join(lines[1:-1]).strip()
    return stripped


def parse_json_response(text):
    return json.loads(strip_json_code_fence(text))


def drop_known_explanatory_extras(data):
    """Ignore only redundant E relational-adaptation evidence fields."""
    if not isinstance(data, dict):
        return data
    for system in data.get("systems", []):
        enactment = system.get("functions", {}).get("E", {}) if isinstance(system, dict) else {}
        if isinstance(enactment, dict):
            for key in ("confidence_ra", "evidence_ra", "location_ra", "rationale_ra"):
                enactment.pop(key, None)
        dependencies = system.get("dependencies", {}) if isinstance(system, dict) else {}
        if isinstance(dependencies, dict):
            for dependency in dependencies.values():
                if isinstance(dependency, dict):
                    dependency.pop("presence_note", None)
                    dependency.pop("validation_note", None)
    return data


def audit_signature(paper, protocol, schema, config):
    return fingerprint({"messages": build_prompt(paper, protocol), "schema": schema, "config": config.public()})


def load_existing(directory, schema, signature=None):
    try:
        status = load_json(directory / "status.json")
        if status["status"] != "success" or (signature is not None and status.get("signature") != signature):
            return None
        data = load_json(directory / "audit.json")
        validate_audit(data, schema)
        if status.get("audit_sha256") != fingerprint(data):
            return None
        return data
    except (OSError, ValueError, KeyError, TypeError):
        return None


def run_single_auditor(paper, auditor_id, config, *, protocol, schema, output,
                       overwrite=False, call=call_llm, sleep=time.sleep):
    directory = Path(output) / paper.paper_id / auditor_id
    messages = build_prompt(paper, protocol)
    signature = audit_signature(paper, protocol, schema, config)
    if not overwrite:
        existing = load_existing(directory, schema, signature)
        if existing is not None:
            return AuditResult(auditor_id, "loaded", existing)
        # A previous parser may have rejected an otherwise intact response.
        # Revalidate it before paying for another identical request.
        status_path, raw_path = directory / "status.json", directory / "raw_response.txt"
        if status_path.exists() and raw_path.exists():
            try:
                old_status = load_json(status_path)
                if old_status.get("signature") == signature:
                    recovered = drop_known_explanatory_extras(
                        parse_json_response(raw_path.read_text(encoding="utf-8")))
                    validate_audit(recovered, schema)
                    save_json(directory / "parsed_audit.json", recovered)
                    save_json(directory / "audit.json", recovered)
                    status = {"status": "success", "signature": signature, "audit_sha256": fingerprint(recovered),
                              "config": config.public(), "returned_model": old_status.get("returned_model"),
                              "usage": old_status.get("usage", {}), "calls_this_run": 0,
                              "recovered_from_saved_response": True}
                    save_json(status_path, status)
                    return AuditResult(auditor_id, "recovered", recovered)
            except (OSError, ValueError, AuditValidationError):
                pass
    directory.mkdir(parents=True, exist_ok=True)
    save_json(directory / "status.json", {"status": "running", "signature": signature, "config": config.public()})
    attempts = directory / "attempts"
    previous = [int(p.name) for p in attempts.glob("*") if p.is_dir() and p.name.isdigit()]
    offset, calls = max(previous, default=0), 0
    for attempt in range(config.max_retries + 1):
        attempt_dir = attempts / f"{offset + attempt + 1:04d}"
        attempt_dir.mkdir(parents=True, exist_ok=True)
        calls += 1
        try:
            response = call(messages, schema, config)
            atomic_write(attempt_dir / "raw_api_response.json", response.raw)
            atomic_write(attempt_dir / "raw_response.txt", response.content)
            atomic_write(directory / "raw_response.txt", response.content)
            data = drop_known_explanatory_extras(parse_json_response(response.content))
            validate_audit(data, schema)
            save_json(attempt_dir / "parsed_audit.json", data)
            save_json(directory / "parsed_audit.json", data)
            save_json(attempt_dir / "audit.json", data)
            save_json(directory / "audit.json", data)
            status = {"status": "success", "signature": signature, "audit_sha256": fingerprint(data),
                      "config": config.public(), "returned_model": response.model, "usage": response.usage,
                      "calls_this_run": calls, "last_attempt": attempt_dir.name}
            save_json(attempt_dir / "result.json", status)
            save_json(directory / "status.json", status)
            return AuditResult(auditor_id, "success", data, calls)
        except (CallError, json.JSONDecodeError, AuditValidationError) as exc:
            kind = "invalid_json" if isinstance(exc, json.JSONDecodeError) else exc.error_type
            message = str(exc).replace(config.api_key, "<redacted>") if config.api_key else str(exc)
            failure = {"status": "failed", "error_type": kind, "error_message": message,
                       "retry_count": calls, "signature": signature,
                       "config": config.public(), "calls_this_run": calls}
            if isinstance(exc, CallError) and exc.raw:
                atomic_write(attempt_dir / "raw_api_response.json", exc.raw)
                atomic_write(directory / "raw_response.txt", exc.raw)
            save_json(attempt_dir / "result.json", failure)
            if isinstance(exc, CallError) and not exc.retryable:
                break
            if attempt < config.max_retries:
                delay = exc.retry_after if isinstance(exc, CallError) and exc.retry_after is not None else BACKOFF_DELAYS[min(attempt, len(BACKOFF_DELAYS) - 1)]
                sleep(delay)
    save_json(directory / "status.json", failure)
    return AuditResult(auditor_id, "failed", calls=calls, error_type=failure["error_type"])
