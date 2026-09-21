import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from audit_framework.auditor import audit_signature, parse_json_response, run_single_auditor, strip_json_code_fence
from audit_framework.config import AUDITOR_IDS, load_configs
from audit_framework.llm_client import CallError, Response, make_request, call_llm
import httpx
from audit_framework.prompt_builder import build_prompt
from audit_framework.runner import rebuild_consensus
from audit_framework.storage import load_json, save_json
from tests.helpers import PROTOCOL, SCHEMA, audit, config, paper


class ResumeTests(unittest.TestCase):
    def test_explicit_env_overrides_hosting_app_environment(self):
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            entries = {a: {"model": "test", "api": "openai", "output_mode": "json_schema",
                           "api_key_env": "OPENAI_API_KEY", "base_url_env": "OPENAI_BASE_URL"}
                       for a in (*AUDITOR_IDS, "judge")}
            save_json(directory / "auditors.json", entries)
            (directory / ".env").write_text("OPENAI_API_KEY=local-key\nOPENAI_BASE_URL=https://local.example/v1\n")
            with patch.dict("os.environ", {"OPENAI_API_KEY": "hosting-key", "OPENAI_BASE_URL": "https://hosting.example/v1"}):
                configs = load_configs(directory / "auditors.json", directory / ".env")
            self.assertEqual(configs["auditor_1"].api_key, "local-key")
            self.assertEqual(configs["auditor_1"].base_url, "https://local.example/v1")

    def test_model_not_found_is_not_a_transient_rate_limit(self):
        response = httpx.Response(429, json={"error": {"code": "model_not_found", "message": "unknown provider for model test"}})
        with patch("httpx.post", return_value=response), self.assertRaises(CallError) as ctx:
            call_llm(build_prompt(paper(), PROTOCOL), SCHEMA, config())
        self.assertEqual(ctx.exception.error_type, "model_unavailable")
        self.assertFalse(ctx.exception.retryable)

    def test_retry_after_header_and_upstream_overload_are_retryable(self):
        response = httpx.Response(503, headers={"Retry-After": "9"},
                                  json={"error": {"message": "upstream overloaded"}})
        with patch("httpx.post", return_value=response), self.assertRaises(CallError) as ctx:
            call_llm(build_prompt(paper(), PROTOCOL), SCHEMA, config())
        self.assertEqual(ctx.exception.error_type, "rate_limit")
        self.assertTrue(ctx.exception.retryable)
        self.assertEqual(ctx.exception.retry_after, 9)

    def test_anthropic_sse_refusal_is_not_retried(self):
        from dataclasses import replace
        cfg = replace(config(), api="anthropic")
        response = httpx.Response(200, text=(
            'event: message_delta\n'
            'data: {"type":"message_delta","delta":{"stop_reason":"refusal",'
            '"stop_details":{"type":"refusal"}}}\n\n'))
        with patch("httpx.post", return_value=response), self.assertRaises(CallError) as ctx:
            call_llm(build_prompt(paper(), PROTOCOL), SCHEMA, cfg)
        self.assertEqual(ctx.exception.error_type, "refusal")
        self.assertFalse(ctx.exception.retryable)

    def test_resume_partial_missing_auditor_and_rebuild_are_offline(self):
        calls, messages_seen = [], []

        def fake(messages, schema, cfg):
            calls.append(cfg.model); messages_seen.append(messages)
            return Response('{"synthetic":true}', json.dumps(audit()), "test-model", {})

        with TemporaryDirectory() as tmp:
            output = Path(tmp)
            save_json(output / "audit.schema.json", SCHEMA)
            save_json(output / "test-paper/metadata.json", paper().metadata)
            save_json(output / "test-paper/audit_signatures.json", {
                a: audit_signature(paper(), PROTOCOL, SCHEMA, config()) for a in AUDITOR_IDS})
            kwargs = dict(protocol=PROTOCOL, schema=SCHEMA, output=output, call=fake)
            for agent in AUDITOR_IDS[:2]:
                run_single_auditor(paper(), agent, config(), **kwargs)
            statuses = [run_single_auditor(paper(), a, config(), **kwargs).status for a in AUDITOR_IDS]
            self.assertEqual(statuses, ["loaded", "loaded", "success"])
            self.assertEqual(len(calls), 3)
            self.assertTrue(all(m == messages_seen[0] for m in messages_seen))
            self.assertEqual(messages_seen[0][1]["content"].split("\n\n", 1)[1], PROTOCOL.replace("{{FULL_PAPER}}", paper().content))
            with patch("httpx.post", side_effect=AssertionError("No API during rebuild")), patch("httpx.Client.get", side_effect=AssertionError("No retrieval")):
                summary = rebuild_consensus(output, log=lambda _: None)
            self.assertEqual(summary["completed_papers"], 1)
            self.assertEqual(summary["auditor_calls_this_run"], 0)
            self.assertEqual(summary["total_auditor_calls"], 3)
            self.assertEqual(summary["unanimous_fields"], 22)
            self.assertTrue((output / "test-paper/auditor_1/raw_response.txt").exists())

    def test_invalid_json_retried_and_raw_preserved(self):
        responses = iter([Response("bad-envelope", "not JSON", None, {}), Response("ok-envelope", json.dumps(audit()), None, {})])
        with TemporaryDirectory() as tmp:
            output = Path(tmp)
            result = run_single_auditor(paper(), "auditor_1", config(), protocol=PROTOCOL, schema=SCHEMA,
                                       output=output, call=lambda *a: next(responses), sleep=lambda _: None)
            self.assertEqual(result.status, "success")
            self.assertEqual(result.calls, 2)
            self.assertEqual((output / "test-paper/auditor_1/attempts/0001/raw_response.txt").read_text(), "not JSON")
            self.assertEqual(load_json(output / "test-paper/auditor_1/parsed_audit.json"), audit())

    def test_backoff_and_retry_after(self):
        failures = iter([
            CallError("rate_limit", "busy", retry_after=7),
            CallError("rate_limit", "busy"),
            Response("ok", json.dumps(audit()), None, {}),
        ])
        delays = []
        from dataclasses import replace
        cfg = replace(config(), max_retries=2)
        def fake_call(*args):
            item = next(failures)
            if isinstance(item, Exception):
                raise item
            return item
        with TemporaryDirectory() as tmp:
            result = run_single_auditor(paper(), "auditor_1", cfg, protocol=PROTOCOL, schema=SCHEMA,
                                       output=Path(tmp), call=fake_call, sleep=delays.append)
        self.assertEqual(result.status, "success")
        self.assertEqual(delays, [7, 5])

    def test_final_rate_limit_records_retry_count(self):
        delays = []
        with TemporaryDirectory() as tmp:
            output = Path(tmp)
            result = run_single_auditor(
                paper(), "auditor_1", config(), protocol=PROTOCOL, schema=SCHEMA, output=output,
                call=lambda *a: (_ for _ in ()).throw(CallError("rate_limit", "busy")),
                sleep=delays.append,
            )
            status = load_json(output / "test-paper/auditor_1/status.json")
        self.assertEqual(result.status, "failed")
        self.assertEqual(status["error_type"], "rate_limit")
        self.assertEqual(status["retry_count"], 2)
        self.assertEqual(delays, [2])

    def test_json_transport_normalization_only(self):
        # Cases 1-3: plain JSON, ```json, and bare ``` all parse.
        for source in ('{"label":"V1"}', '```json\n{"label":"V1"}\n```', '```\n\n{"label":"V1"}\n```'):
            with self.subTest(source=source):
                self.assertEqual(parse_json_response(source), {"label": "V1"})
        # Cases 4-5: prose prefixes and Python dict syntax remain invalid.
        for bad in ('Here is the JSON:\n{"label":"V1"}', "```json\n{'label': 'V1'}\n```"):
            with self.subTest(bad=bad), self.assertRaises(json.JSONDecodeError):
                parse_json_response(bad)
        self.assertEqual(strip_json_code_fence('  {"label":"V1"}\n'), '{"label":"V1"}')

    def test_saved_fenced_response_can_be_recovered_without_api(self):
        with TemporaryDirectory() as tmp:
            output = Path(tmp); directory = output / "test-paper/auditor_1"
            signature = audit_signature(paper(), PROTOCOL, SCHEMA, config())
            directory.mkdir(parents=True)
            save_json(directory / "status.json", {"status": "failed", "signature": signature})
            (directory / "raw_response.txt").write_text("```json\n" + json.dumps(audit()) + "\n```", encoding="utf-8")
            result = run_single_auditor(paper(), "auditor_1", config(), protocol=PROTOCOL, schema=SCHEMA,
                                       output=output, call=lambda *a: (_ for _ in ()).throw(AssertionError("no API")))
            self.assertEqual(result.status, "recovered")
            self.assertEqual(result.calls, 0)
            self.assertTrue((directory / "raw_response.txt").read_text(encoding="utf-8").startswith("```json"))
            self.assertEqual(load_json(directory / "parsed_audit.json"), audit())

    def test_known_relational_evidence_extras_are_ignored_without_retry(self):
        data = audit()
        data["systems"][0]["functions"]["E"].update({
            "confidence_ra": "High", "evidence_ra": "extra explanation",
            "location_ra": "Section 3", "rationale_ra": "extra rationale",
        })
        data["systems"][0]["dependencies"]["S_to_P"].update({
            "presence_note": "extra explanation", "validation_note": "extra explanation",
        })
        raw = "```json\n" + json.dumps(data) + "\n```"
        with TemporaryDirectory() as tmp:
            output = Path(tmp)
            result = run_single_auditor(
                paper(), "auditor_1", config(), protocol=PROTOCOL, schema=SCHEMA,
                output=output, call=lambda *a: Response("envelope", raw, None, {}),
            )
            saved = load_json(output / "test-paper/auditor_1/audit.json")
            original = (output / "test-paper/auditor_1/raw_response.txt").read_text(encoding="utf-8")
        self.assertEqual(result.status, "success")
        self.assertEqual(result.calls, 1)
        self.assertNotIn("confidence_ra", saved["systems"][0]["functions"]["E"])
        self.assertNotIn("presence_note", saved["systems"][0]["dependencies"]["S_to_P"])
        self.assertIn("confidence_ra", original)

    def test_failed_auth_not_retried(self):
        def bad(*args):
            raise CallError("authentication_error", "HTTP 401", '{"error":"denied"}', False)
        with TemporaryDirectory() as tmp:
            result = run_single_auditor(paper(), "auditor_1", config(), protocol=PROTOCOL, schema=SCHEMA,
                                       output=Path(tmp), call=bad, sleep=lambda _: None)
            self.assertEqual(result.calls, 1)
            self.assertEqual(result.status, "failed")

    def test_changed_content_and_corrupt_audit_are_not_reused(self):
        def fake(*args):
            return Response("raw", json.dumps(audit()), None, {})
        with TemporaryDirectory() as tmp:
            output = Path(tmp)
            kwargs = dict(protocol=PROTOCOL, schema=SCHEMA, output=output, call=fake)
            run_single_auditor(paper(), "auditor_1", config(), **kwargs)
            changed = paper(); changed.content += " new evidence"
            self.assertEqual(run_single_auditor(changed, "auditor_1", config(), **kwargs).status, "success")
            (output / "test-paper/auditor_1/audit.json").write_text("{}")
            self.assertEqual(run_single_auditor(changed, "auditor_1", config(), **kwargs).status, "recovered")

    def test_schema_is_sent_natively_without_other_answers(self):
        _, _, body = make_request(build_prompt(paper(), PROTOCOL), SCHEMA, config())
        self.assertEqual(body["response_format"]["json_schema"]["schema"], SCHEMA)
        self.assertTrue(body["response_format"]["json_schema"]["strict"])
        self.assertEqual(len(body["messages"]), 2)


if __name__ == "__main__":
    unittest.main()
