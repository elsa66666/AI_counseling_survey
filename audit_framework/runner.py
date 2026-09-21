from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

from .auditor import AuditResult, audit_signature, load_existing, run_single_auditor
from .config import AUDITOR_IDS, JUDGE_ID
from .data_loader import load_papers, load_prompt
from .fulltext import retrieve
from .judge import JudgeResult, collect_disputes, load_saved_decisions, run_judge
from .schema import build_schema
from .stats import export_batch
from .storage import OutputLock, fingerprint, load_json, save_json, atomic_write
from .voting import build_consensus


def select_papers(papers, paper_id, limit):
    if paper_id:
        papers = [p for p in papers if p.paper_id == paper_id]
        if not papers:
            raise ValueError(f"Unknown paper ID: {paper_id}")
    return papers[:limit] if limit is not None else papers


def run_batch(*, papers_path, prompt_path, output, cache, configs, limit=1, paper_id=None,
              overwrite=False, workers=1, sources_path=None, auditor_fn=run_single_auditor,
              judge_fn=run_judge, retrieve_fn=retrieve, log=print):
    protocol = load_prompt(prompt_path)
    schema = build_schema(protocol)
    papers = select_papers(load_papers(papers_path), paper_id, limit)
    sources = load_json(sources_path) if sources_path else {}
    manifest = {"protocol_sha256": fingerprint(protocol), "schema": schema,
                "auditors": {a: configs[a].public() for a in AUDITOR_IDS},
                "judge": configs[JUDGE_ID].public() if JUDGE_ID in configs else None,
                "input_dataset": str(Path(papers_path).resolve())}
    with OutputLock(output):
        manifest_path = output / "experiment.json"
        if manifest_path.exists():
            old_manifest = load_json(manifest_path)
            immutable = ("protocol_sha256", "schema", "input_dataset")
            if any(old_manifest.get(k) != manifest.get(k) for k in immutable):
                raise ValueError("Protocol/schema/dataset changed. Use a new --output directory to avoid mixing experiments.")
            # Model/config changes are allowed: per-auditor signatures ensure
            # only matching results remain eligible, while attempt history stays.
        save_json(manifest_path, manifest)
        atomic_write(output / "protocol.md", protocol)
        save_json(output / "audit.schema.json", schema)
        calls = judge_calls = 0
        for index, paper in enumerate(papers, 1):
            log(f"[paper {index}/{len(papers)}] paper_id={paper.paper_id}")
            directory = output / paper.paper_id
            save_json(directory / "metadata.json", paper.metadata)
            try:
                source = sources.get(paper.paper_id)
                if source and not source.startswith(("http://", "https://")):
                    source = str((Path(sources_path).parent / source).resolve())
                retrieve_fn(paper, cache, source)
                save_json(directory / "source.json", paper.source)
            except Exception as exc:
                save_json(directory / "input_error.json", {"status": "failed", "error_type": "fulltext_error", "error_message": str(exc)})
                log(f"  input: failed ({type(exc).__name__}); no API calls")
                results = [AuditResult(a, "failed", error_type="fulltext_error") for a in AUDITOR_IDS]
            else:
                (directory / "input_error.json").unlink(missing_ok=True)
                save_json(directory / "audit_signatures.json", {
                    a: audit_signature(paper, protocol, schema, configs[a]) for a in AUDITOR_IDS})

                def run(agent):
                    return auditor_fn(paper, agent, configs[agent], protocol=protocol, schema=schema,
                                      output=output, overwrite=overwrite)

                if workers == 1:
                    results = []
                    for agent in AUDITOR_IDS:
                        result = run(agent)
                        results.append(result)
                        log(f"  {agent}: {result.status}" + (f" ({result.error_type})" if result.error_type else ""))
                else:
                    with ThreadPoolExecutor(max_workers=min(workers, 3)) as executor:
                        results = list(executor.map(run, AUDITOR_IDS))
                    for result in results:
                        log(f"  {result.auditor_id}: {result.status}" + (f" ({result.error_type})" if result.error_type else ""))
            calls += sum(r.calls for r in results)
            audits = {r.auditor_id: r.audit for r in results}
            initial = build_consensus(paper.metadata, audits)
            disputes = collect_disputes(initial, audits)
            judge_config = configs.get(JUDGE_ID)
            if disputes and judge_config is not None:
                judged = judge_fn(paper.metadata, disputes, judge_config, protocol=protocol,
                                  output=output, overwrite=overwrite)
            elif disputes:
                judged = JudgeResult("configuration_missing", {})
            else:
                judged = JudgeResult("not_needed", {})
            judge_calls += judged.calls
            judge_meta = {"status": judged.status,
                          "model": judge_config.model if judge_config else None,
                          "disputed_fields": [item["field"] for item in disputes],
                          "resolved_fields": list(judged.decisions)}
            if judged.error_type:
                judge_meta["error_type"] = judged.error_type
            consensus = build_consensus(paper.metadata, audits, judged.decisions, judge_meta)
            save_json(directory / "consensus.json", consensus)
            log(f"  judge: {judged.status}" if disputes else "  judge: not_needed")
            log(f"  consensus: {consensus['status']}")
        return export_batch(output, schema, calls, judge_calls)


def rebuild_consensus(output, *, paper_id=None, limit=None, log=print):
    """Offline: no config, dotenv, paper retrieval, prompt file, or LLM required."""
    with OutputLock(output):
        schema = load_json(output / "audit.schema.json")
        paths = sorted(output.glob("*/metadata.json"))
        if paper_id:
            paths = [p for p in paths if p.parent.name == paper_id]
        if not paths:
            raise ValueError("No saved paper metadata found")
        if limit is not None:
            paths = paths[:limit]
        for path in paths:
            metadata = load_json(path)
            signatures_path = path.parent / "audit_signatures.json"
            signatures = load_json(signatures_path) if signatures_path.exists() else {}
            audits = {a: load_existing(path.parent / a, schema, signatures.get(a, "missing-input-signature")) for a in AUDITOR_IDS}
            # A failed/new input must not resurrect stale audits of a previous input.
            if (path.parent / "input_error.json").exists():
                audits = dict.fromkeys(AUDITOR_IDS)
            initial = build_consensus(metadata, audits)
            disputes = collect_disputes(initial, audits)
            decisions = load_saved_decisions(path.parent / "judge", disputes) if disputes else {}
            judge_meta = {"status": "loaded" if decisions else "not_needed" if not disputes else "not_run",
                          "model": None, "disputed_fields": [item["field"] for item in disputes],
                          "resolved_fields": list(decisions)}
            result = build_consensus(metadata, audits, decisions, judge_meta)
            save_json(path.parent / "consensus.json", result)
            log(f"{metadata['paper_id']}: {result['status']} (offline)")
        return export_batch(output, schema, 0, 0)
