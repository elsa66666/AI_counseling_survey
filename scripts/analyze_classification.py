"""Recompute descriptive classification results from saved SFPE consensus records.

No LLM calls, manual relabeling, or modification of the input records is performed.
The unflagged subset is a sensitivity analysis, not a human-validated gold set.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

EDGES = ("S_to_F", "S_to_P", "F_to_P", "P_to_E", "E_to_S", "E_to_F", "E_to_P")


def label(record, field):
    return record["systems"][0]["fields"][field]["label"]


def analyze_subset(records):
    nodes = {f: sum(label(r, f"functions.{f}.label") == "Present" for r in records) for f in "SFPE"}
    edges = {}
    for edge in EDGES:
        a, b = edge.split("_to_")
        positive = [r for r in records if label(r, f"dependencies.{edge}.presence") == "Explicit"]
        edges[edge] = {
            "endpoint_cooccurrence": sum(all(label(r, f"functions.{f}.label") == "Present" for f in (a, b)) for r in records),
            "presence": dict(Counter(label(r, f"dependencies.{edge}.presence") for r in records)),
            "explicit_validation": dict(Counter(label(r, f"dependencies.{edge}.validation") for r in positive)),
            "explicit_ids": [r["paper_id"] for r in positive],
        }
    profiles = dict(Counter("".join(f for f in "SFPE" if label(r, f"functions.{f}.label") == "Present") or "None" for r in records))
    forward = [r for r in records if all(label(r, f"dependencies.{e}.presence") == "Explicit" for e in ("S_to_F", "F_to_P", "P_to_E"))]
    return {
        "n": len(records), "nodes": nodes, "profiles": profiles, "edges": edges,
        "F_modes": dict(Counter(label(r, "functions.F.mode") for r in records)),
        "E_relational_adaptation": dict(Counter(label(r, "functions.E.relational_adaptation") for r in records)),
        "forward_pipeline_ids": [r["paper_id"] for r in forward],
        "V1_pairs": [{"paper_id": r["paper_id"], "edge": e} for r in records for e in EDGES if label(r, f"dependencies.{e}.validation") == "V1"],
    }


def analyze(path):
    schema = json.loads((path.parent / "audit.schema.json").read_text())
    data = path.read_bytes()
    records = [json.loads(line) for line in data.decode().splitlines() if line.strip()]
    assert len({r["paper_id"] for r in records}) == len(records)
    assert all(len(r["systems"]) == 1 for r in records)
    entries = [(r["paper_id"], "paper_input_completeness", r["paper_input_completeness"]) for r in records]
    entries += [(r["paper_id"], "systems.*." + key, f) for r in records for key, f in r["systems"][0]["fields"].items()]
    fields = [f for _, _, f in entries]
    raw_vote_counts = Counter()
    legacy_adjudications = []
    illegal_votes = []
    for paper_id, key, field in entries:
        node = schema
        for part in key.split("."):
            node = node["items"] if part == "*" else node["properties"][part]
        allowed = node["enum"]
        valid = [value for value in field["agent_labels"].values() if value in allowed]
        illegal_votes.extend({"paper_id": paper_id, "field": key, "auditor": a, "label": value} for a, value in field["agent_labels"].items() if value is not None and value not in allowed)
        votes = Counter(valid)
        assert dict(votes) == field["votes"]
        top = max(votes.values(), default=0)
        expected = "unanimous" if top == 3 else "majority" if top == 2 else "no_majority"
        if field["status"] != "adjudicated":
            assert field["status"] == expected
            assert top >= 2 and field["label"] == votes.most_common(1)[0][0]
        else:
            if top >= 2:
                legacy_adjudications.append({"paper_id": paper_id, "field": key, "original_majority": votes.most_common(1)[0][0], "released_judge_label": field["label"]})
        raw_vote_counts[expected] += 1
    consistency = [r for r in records if r["systems"][0]["consistency_issues"]]
    completeness = [r for r in records if r["paper_input_completeness"]["label"] == "PossiblyTruncated" or label(r, "system_input_completeness") == "PossiblyTruncated"]
    flagged = [r for r in records if r["needs_review"]]
    return {
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "unit": "one canonical audited configuration per paper folder; no counselor-role eligibility filter",
        "field_total": len(fields),
        "final_field_status": dict(Counter(f["status"] for f in fields)),
        "first_stage_vote_status": dict(raw_vote_counts),
        "legacy_majority_adjudications": legacy_adjudications,
        "illegal_saved_function_votes": illegal_votes,
        "adjudicated_papers": sum(bool(r["adjudication"]["resolved_fields"]) for r in records),
        "papers_with_full_agreement": sum(r["full_agreement"] for r in records),
        "flagged_ids": [r["paper_id"] for r in flagged],
        "consistency_issues": {r["paper_id"]: r["systems"][0]["consistency_issues"] for r in consistency},
        "incomplete_ids": [r["paper_id"] for r in completeness],
        "all_records": analyze_subset(records),
        "unflagged_records": analyze_subset([r for r in records if not r["needs_review"]]),
        "notes": ["Agreement does not establish accuracy.", "Exclude flagged records only for sensitivity analysis; retain raw released labels.", "No manual gold standard is available.", "A record without a mechanical flag can still have audited-unit or semantic errors."],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("field_total", "first_stage_vote_status", "final_field_status", "adjudicated_papers")}, indent=2))
