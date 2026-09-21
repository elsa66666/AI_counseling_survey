import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import dotenv_values

AUDITOR_IDS = ("auditor_1", "auditor_2", "auditor_3")
ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class AuditorConfig:
    model: str
    api: str
    output_mode: str
    base_url: str
    api_key: str = field(repr=False)
    temperature: float | None = None
    max_tokens: int = 16384
    timeout: float = 180
    max_retries: int = 3  # Initial request + at most three retries.

    def public(self):
        return {k: v for k, v in vars(self).items() if k != "api_key"}


def load_configs(path: Path, env_path: Path):
    # The explicitly selected local .env is authoritative. The hosting app may
    # itself export OPENAI_* variables for an unrelated API/account.
    env = {**os.environ, **dotenv_values(env_path)}
    entries = json.loads(path.read_text(encoding="utf-8"))
    if set(entries) != set(AUDITOR_IDS):
        raise ValueError("Configuration must define exactly auditor_1, auditor_2, auditor_3")
    result = {}
    for agent, entry in entries.items():
        entry = dict(entry)
        key = env.get(entry.pop("api_key_env"), "") or ""
        base = env.get(entry.pop("base_url_env"), "") or ""
        config = AuditorConfig(api_key=key, base_url=base.rstrip("/"), **entry)
        if config.api not in {"openai", "anthropic"}:
            raise ValueError(f"{agent}: unsupported API")
        if config.output_mode not in {"json_schema", "json_object", "prompt_json"}:
            raise ValueError(f"{agent}: unsupported output mode")
        if config.api == "anthropic" and config.output_mode == "json_object":
            raise ValueError("Anthropic requires json_schema or prompt_json")
        if config.max_retries < 0 or config.max_tokens < 1 or config.timeout <= 0:
            raise ValueError(f"{agent}: invalid limits")
        result[agent] = config
    return result
