import json

from .config import AUDITOR_IDS
from .auditor import load_existing
from .storage import atomic_write, load_json, save_json


def export_batch(output, schema, calls_this_run=0, judge_calls_this_run=0):
    """Rebuild exports from every paper on disk, not only the current --limit."""
    consensus, raw = [], []
    total_calls = total_judge_calls = 0
    for path in sorted(output.glob("*/consensus.json")):
        record = load_json(path)
        consensus.append(record)
        signatures_path = path.parent / "audit_signatures.json"
        signatures = load_json(signatures_path) if signatures_path.exists() else {}
        for agent in AUDITOR_IDS:
            directory = path.parent / agent
            data = load_existing(directory, schema, signatures.get(agent, "missing-input-signature"))
            status = load_json(directory / "status.json") if (directory / "status.json").exists() else {"status": "missing"}
            raw.append({"paper_id": record["paper_id"], "auditor_id": agent, "audit": data, "provenance": status,
                        "eligible_for_current_consensus": data is not None and not (path.parent / "input_error.json").exists()})
            total_calls += len(list((directory / "attempts").glob("*/result.json")))
        total_judge_calls += len(list((path.parent / "judge/attempts").glob("*/result.json")))
    fields = [c["paper_input_completeness"] for c in consensus] + [f for c in consensus for s in c["systems"] for f in s["fields"].values()]
    summary = {"total_papers": len(consensus), "completed_papers": sum(c["completed"] for c in consensus),
               "failed_papers": sum(not c["completed"] for c in consensus),
               "total_auditor_calls": total_calls, "auditor_calls_this_run": calls_this_run,
               "total_judge_calls": total_judge_calls, "judge_calls_this_run": judge_calls_this_run,
               "auditor_failures": sum(len(c["failed_auditors"]) for c in consensus),
               "unanimous_fields": sum(f["status"] == "unanimous" for f in fields),
               "majority_fields": sum(f["status"] == "majority" for f in fields),
               "no_majority_fields": sum(f["status"] == "no_majority" for f in fields),
               "adjudicated_fields": sum(f["status"] == "adjudicated" for f in fields),
               "papers_with_full_agreement": sum(c["full_agreement"] for c in consensus),
               "papers_with_at_least_one_disagreement": sum(not c["full_agreement"] for c in consensus),
               "papers_requiring_manual_review": sum(c["needs_review"] for c in consensus),
               "field_count_scope": "Core audit fields plus paper/system completeness; confidence is not voted",
               "disagreement_count_includes_missing_votes": True}
    for name, rows in (("all_consensus.jsonl", consensus), ("all_raw_audits.jsonl", raw)):
        atomic_write(output / name, "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))
    save_json(output / "audit_summary.json", summary)
    return summary
