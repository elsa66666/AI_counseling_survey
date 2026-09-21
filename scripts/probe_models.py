"""Probe which gateway models are usable for this audit's JSON workflow."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import dotenv_values
import httpx

from audit_framework.auditor import parse_json_response
from audit_framework.config import AuditorConfig, ROOT
from audit_framework.llm_client import CallError, call_llm
from audit_framework.storage import save_json


DEFAULT_MODELS = (
    "gpt-5.4-mini",
    "gpt-5.4-nano",
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-5-20250929",
    "claude-sonnet-5",
    "deepseek-v3",
    "deepseek-v3.2",
    "deepseek-v4-flash",
    "deepseek-v4-pro",
    "qwen3.5-flash",
    "qwen3.6-35b-a3b",
    "qwen3.6-flash",
    "glm-5.1",
    "kimi-k2.5",
    "grok-4-fast-non-reasoning",
    "minimax-m2.5",
)

PROBE_SCHEMA = {
    "type": "object",
    "properties": {"ok": {"type": "boolean"}},
    "required": ["ok"],
    "additionalProperties": False,
}
PROBE_MESSAGES = [
    {"role": "system", "content": "Return only valid JSON matching the requested schema."},
    {"role": "user", "content": 'Return exactly this JSON object: {"ok":true}'},
]


def load_gateway(env_path):
    env = {**os.environ, **dotenv_values(env_path)}
    key, base = env.get("OPENAI_API_KEY", ""), env.get("OPENAI_BASE_URL", "").rstrip("/")
    if not key or not base:
        raise ValueError("OPENAI_API_KEY and OPENAI_BASE_URL are required")
    return key, base


def listed_models(key, base):
    response = httpx.get(base + "/models", headers={"Authorization": "Bearer " + key}, timeout=60)
    response.raise_for_status()
    return {item["id"] for item in response.json().get("data", []) if item.get("id")}


def probe_model(model, key, base, timeout=30, call=call_llm):
    started = time.monotonic()
    api = "anthropic" if model.startswith("claude-") else "openai"
    config = AuditorConfig(
        model=model,
        api=api,
        output_mode="json_schema",
        base_url=base,
        api_key=key,
        max_tokens=64,
        timeout=timeout,
        max_retries=0,
    )
    result = {"model": model, "api": api, "status": None}
    try:
        response = call(PROBE_MESSAGES, PROBE_SCHEMA, config)
        parsed = parse_json_response(response.content)
        if parsed != {"ok": True}:
            result.update(status="schema_invalid", error_message="Response did not equal {\"ok\": true}")
        else:
            result.update(status="ok", returned_model=response.model, usage=response.usage)
    except CallError as exc:
        result.update(status=exc.error_type, error_message=str(exc), retry_after=exc.retry_after)
    except json.JSONDecodeError as exc:
        result.update(status="invalid_json", error_message=str(exc))
    except (KeyError, TypeError, ValueError) as exc:
        result.update(status="schema_invalid", error_message=str(exc))
    result["latency_seconds"] = round(time.monotonic() - started, 3)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Probe gateway model availability with one tiny JSON request per model.")
    parser.add_argument("--env", type=Path, default=ROOT / ".env")
    parser.add_argument("--models", nargs="+", default=list(DEFAULT_MODELS))
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/model_probe_results.json")
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    try:
        key, base = load_gateway(args.env)
        visible = listed_models(key, base)
        results = []
        for model in dict.fromkeys(args.models):
            if model not in visible:
                result = {"model": model, "status": "not_listed", "latency_seconds": 0.0}
            else:
                result = probe_model(model, key, base, args.timeout)
            results.append(result)
            print(f"{model}: {result['status']} ({result['latency_seconds']}s)", flush=True)
        report = {
            "gateway": base,
            "probe_type": "single native JSON-schema request; no retries",
            "timeout_seconds": args.timeout,
            "visible_model_count": len(visible),
            "results": results,
            "working_models": [r["model"] for r in results if r["status"] == "ok"],
        }
        save_json(args.output, report)
        print(f"Saved: {args.output.resolve()}")
        return 0 if report["working_models"] else 1
    except (OSError, ValueError, KeyError, httpx.HTTPError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
