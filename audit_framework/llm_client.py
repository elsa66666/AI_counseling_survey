"""Two HTTP formats, one fresh request; never another auditor's answer."""
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import re
import httpx


class CallError(Exception):
    def __init__(self, error_type, message, raw="", retryable=True, retry_after=None):
        super().__init__(message)
        self.error_type, self.raw, self.retryable = error_type, raw, retryable
        self.retry_after = retry_after


def parse_retry_after(value):
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=timezone.utc)
            return max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return None


@dataclass
class Response:
    raw: str
    content: str
    model: str | None
    usage: dict


def make_request(messages, schema, config):
    if not config.api_key or not config.base_url:
        raise CallError("configuration_error", "Missing API key or base URL", retryable=False)
    body = {"model": config.model, "stream": False}
    if config.api == "anthropic":
        url = config.base_url + "/messages"
        headers = {"x-api-key": config.api_key, "anthropic-version": "2023-06-01"}
        body.update(system=messages[0]["content"], messages=messages[1:], max_tokens=config.max_tokens)
        if config.output_mode == "json_schema":
            body["output_config"] = {"format": {"type": "json_schema", "schema": schema}}
    else:
        url = config.base_url + "/chat/completions"
        headers = {"Authorization": "Bearer " + config.api_key}
        token_key = "max_completion_tokens" if config.model.startswith(("gpt-", "o1", "o3", "o4")) else "max_tokens"
        body.update(messages=messages, **{token_key: config.max_tokens})
        if config.output_mode == "json_schema":
            body["response_format"] = {"type": "json_schema", "json_schema": {
                "name": "sfpe_audit", "strict": True, "schema": schema}}
        elif config.output_mode == "json_object":
            body["response_format"] = {"type": "json_object"}
    if config.temperature is not None:
        body["temperature"] = config.temperature
    return url, headers, body


def call_llm(messages, schema, config):
    url, headers, body = make_request(messages, schema, config)
    try:
        response = httpx.post(url, headers=headers, json=body, timeout=config.timeout)
    except httpx.TimeoutException:
        raise CallError("timeout", "API request timed out") from None
    except httpx.TransportError as exc:
        raise CallError("api_transport_error", type(exc).__name__) from None
    raw = response.content.decode("utf-8", errors="replace").replace(config.api_key, "<redacted>")
    if not response.is_success:
        code = response.status_code
        try:
            provider_error = response.json().get("error", {})
        except (ValueError, AttributeError):
            provider_error = {}
        if isinstance(provider_error, dict) and (provider_error.get("code") == "model_not_found" or
                "unknown provider for model" in str(provider_error.get("message", "")) or
                "无可用渠道" in str(provider_error.get("message", ""))):
            raise CallError("model_unavailable", "Requested model has no available route; check configured model ID", raw, False)
        provider_message = str(provider_error.get("message", "")) if isinstance(provider_error, dict) else ""
        overloaded = "overload" in provider_message.casefold() or "负载已饱和" in provider_message
        kind = "rate_limit" if code == 429 or overloaded else "authentication_error" if code in (401, 403) else "api_http_error"
        retryable = kind == "rate_limit" or code == 408 or code >= 500
        raise CallError(kind, f"HTTP {code}; see raw_api_response.json", raw, retryable,
                        parse_retry_after(response.headers.get("Retry-After")))
    if (config.api == "anthropic" and "data:" in raw and
            re.search(r'"(?:stop_reason|type)"\s*:\s*"refusal"', raw)):
        raise CallError("refusal", "Model refused the request", raw, False)
    try:
        data = response.json()
        if config.api == "anthropic":
            if data.get("stop_reason") == "max_tokens":
                raise CallError("output_truncated", "Increase max_tokens; output was truncated", raw)
            if data.get("stop_reason") == "refusal":
                raise CallError("refusal", "Model refused the request", raw, False)
            content = "".join(x.get("text", "") for x in data["content"] if x.get("type") == "text")
        else:
            choice = data["choices"][0]
            if choice.get("finish_reason") == "length":
                raise CallError("output_truncated", "Increase max_tokens; output was truncated", raw)
            if choice["message"].get("refusal") or choice.get("finish_reason") == "content_filter":
                raise CallError("refusal", "Model refused the request", raw, False)
            content = choice["message"].get("content") or ""
        if not isinstance(content, str) or not content.strip():
            raise CallError("empty_response", "No text returned", raw)
        return Response(raw, content, data.get("model"), data.get("usage", {}))
    except (KeyError, IndexError, TypeError, ValueError):
        raise CallError("invalid_api_response", "Unexpected API response envelope", raw) from None
