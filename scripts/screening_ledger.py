"""Freeze candidate records and recompute evidence-backed eligibility counts.

This script performs no literature retrieval or LLM calls. Pending publication
or scope decisions remain pending; bibliographic metadata alone is not proof.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROLES = {"COUNSELOR", "CLIENT", "BOTH", "SUPPORT", "OUTSIDE", "UNRESOLVED"}
PUBLICATION = {"Published", "NotPublished", "Pending"}

def normalized_title(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())

def initialize(papers_path, output_dir, publication_checks=None, snapshot_date="2026-10-13"):
    raw = papers_path.read_bytes()
    papers = json.loads(raw)
    checks = {} if publication_checks is None else {x["paper_id"]: x for x in json.loads(publication_checks.read_text())}
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for p in papers:
        c = checks.get(p["paper_id"], {})
        rows.append({
            "paper_id": p["paper_id"], "title": p["title"], "year": p["year"],
            "source_url": p["url"], "discovery_source": "GPT-assisted legacy candidate list",
            "discovery_query": None, "discovery_date": None,
            "publication": c.get("publication_decision", "Pending"),
            "publication_evidence": c.get("publication_evidence", ""),
            "publication_evidence_url": c.get("additional_evidence_url", c.get("crossref_source", p["url"])),
            "publication_checked_at": c.get("checked_at"),
            "publication_response_sha256": c.get("additional_evidence_sha256", c.get("crossref_response_sha256", c.get("response_sha256"))),
            "role": "UNRESOLVED", "role_evidence": "", "role_evidence_location": "",
            "role_evidence_url": "", "duplicate_of": None,
            "screening_method": None, "screening_votes": [], "screening_model_versions": [],
            "technology": "Unverified", "protocol_version": "selection-v1.0",
        })
    (output_dir / "candidates.json").write_bytes(raw)
    ledger = output_dir / "screening.json"
    ledger.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    manifest = {
        "snapshot_date": snapshot_date, "protocol_version": "selection-v1.0",
        "candidate_sha256": hashlib.sha256(raw).hexdigest(),
        "input_n": len(papers), "candidate_origin": "GPT-assisted legacy discovery; original discovery prompts and queries unavailable",
        "scope": "Published counselor/mental-health-support modeling or client simulation; standalone resources counted separately",
        "retrieval_runs": [],
        "note": "This is a retrospective screening input snapshot, not a completed systematic search. No initial database hit count is inferred from the 47 candidates.",
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return ledger

def summarize(ledger_path):
    rows = json.loads(ledger_path.read_text())
    ids = [r["paper_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Repeated paper_id; use duplicate_of for a second version")
    outcomes = Counter()
    reasons = Counter()
    roles = Counter()
    for r in rows:
        if r["publication"] not in PUBLICATION or r["role"] not in ROLES:
            raise ValueError(f"Illegal decision for {r['paper_id']}")
        if r["publication"] != "Pending" and not all(r.get(k, "").strip() for k in ("publication_evidence", "publication_evidence_url")):
            raise ValueError(f"Publication decision lacks evidence: {r['paper_id']}")
        if r["role"] != "UNRESOLVED" and not all(r[k].strip() for k in ("role_evidence", "role_evidence_location", "role_evidence_url")):
            raise ValueError(f"Scope decision lacks traceable evidence: {r['paper_id']}")
        if r.get("duplicate_of"):
            if r["duplicate_of"] not in ids or r["duplicate_of"] == r["paper_id"]:
                raise ValueError("duplicate_of must point to another frozen candidate")
            target = next(x for x in rows if x["paper_id"] == r["duplicate_of"])
            if target.get("duplicate_of"):
                raise ValueError("duplicate_of must point to a canonical candidate")
            outcome, reason = "Duplicate", "Duplicate version"
        elif r["publication"] == "NotPublished":
            outcome, reason = "Excluded", "Not formally published"
        elif r["publication"] == "Pending":
            outcome, reason = "Pending", "Publication not verified"
        elif r["role"] == "OUTSIDE":
            outcome, reason = "Excluded", "Outside counseling/support or client-simulation scope"
        elif r["role"] == "SUPPORT":
            outcome, reason = "Supporting", "Supporting dataset, detection, evaluation, or foundational resource"
        elif r["role"] == "UNRESOLVED":
            outcome, reason = "Pending", "Scope evidence not finalized"
        else:
            outcome, reason = "Included", "Eligible modeled role"
            roles[r["role"]] += 1
        outcomes[outcome] += 1; reasons[reason] += 1
    for k in ("Included", "Supporting", "Excluded", "Pending", "Duplicate"):
        outcomes[k] += 0
    for k in ("COUNSELOR", "CLIENT", "BOTH"):
        roles[k] += 0
    assert sum(outcomes.values()) == len(rows)
    return {
        "candidate_n": len(rows), "unique_ids": len(set(ids)),
        "unique_normalized_titles": len({normalized_title(r["title"]) for r in rows}),
        "unique_current_urls": len({r["source_url"].rstrip('/') for r in rows}),
        "publication_states": dict(Counter(r["publication"] for r in rows)),
        "record_outcomes": dict(outcomes), "primary_reason_counts": dict(reasons),
        "included_exclusive_roles": dict(roles),
        "counselor_or_support_model_n": roles["COUNSELOR"] + roles["BOTH"],
        "client_simulation_n": roles["CLIENT"] + roles["BOTH"],
        "final_screening_complete": outcomes["Pending"] == 0,
        "ledger_sha256": hashlib.sha256(ledger_path.read_bytes()).hexdigest(),
        "counting_note": "Included + Supporting + Excluded + Pending + Duplicate = candidate_n. BOTH contributes once to Included and once to each role-specific count. Zero Included while decisions are pending is not a final inclusion result.",
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("--papers", type=Path, required=True)
    init.add_argument("--output-dir", type=Path, required=True)
    init.add_argument("--publication-checks", type=Path)
    init.add_argument("--snapshot-date", required=True, help="Explicit YYYY-MM-DD cutoff for the frozen input")
    summary = commands.add_parser("summarize")
    summary.add_argument("ledger", type=Path)
    summary.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "init":
        print(initialize(args.papers, args.output_dir, args.publication_checks, args.snapshot_date))
    else:
        result = summarize(args.ledger)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
