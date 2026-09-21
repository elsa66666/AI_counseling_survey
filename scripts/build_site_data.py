"""Build the public audit dataset and GitHub Pages data from consensus JSONL."""

import argparse
import csv
import json
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
EDGES = ("S_to_F", "S_to_P", "F_to_P", "P_to_E", "E_to_S", "E_to_F", "E_to_P")


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def label(fields, name):
    value = fields.get(name, {})
    return value.get("label")


def paper_record(record):
    metadata = record["metadata"]
    paper_url = metadata.get("paper_url") or metadata.get("url")
    parsed = urlparse(paper_url or "")
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or "scholar.google" in parsed.netloc:
        raise ValueError(f"{record['paper_id']}: invalid public paper URL")
    systems = record.get("systems", [])
    if len(systems) != 1:
        raise ValueError(f"{record['paper_id']}: expected one canonical consensus system")
    system = systems[0]
    fields = system["fields"]
    required = [
        "functions.S.label", "functions.F.label", "functions.F.mode", "functions.P.label",
        "functions.E.label", "functions.E.relational_adaptation",
        *[f"dependencies.{edge}.{item}" for edge in EDGES for item in ("presence", "validation")],
    ]
    missing = [name for name in required if name not in fields]
    if missing:
        raise ValueError(f"{record['paper_id']}: missing consensus fields: {', '.join(missing)}")
    return {
        "paper_id": record["paper_id"],
        "title": metadata["title"],
        "paper_url": paper_url,
        "year": int(metadata["year"]),
        "authors": metadata.get("authors", ""),
        "status": record["status"],
        "needs_review": record["needs_review"],
        "full_agreement": record["full_agreement"],
        "paper_input_completeness": record["paper_input_completeness"],
        "system_names": system.get("system_names", {}),
        "sfpe": {
            "S": label(fields, "functions.S.label"),
            "F": label(fields, "functions.F.label"),
            "F_mode": label(fields, "functions.F.mode"),
            "P": label(fields, "functions.P.label"),
            "E": label(fields, "functions.E.label"),
            "E_relational_adaptation": label(fields, "functions.E.relational_adaptation"),
        },
        "dependencies": {
            edge.replace("_to_", "→"): {
                "presence": label(fields, f"dependencies.{edge}.presence"),
                "validation": label(fields, f"dependencies.{edge}.validation"),
            }
            for edge in EDGES
        },
        "fields": fields,
        "consistency_issues": system.get("consistency_issues", []),
    }


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path, papers):
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        "paper_id", "title", "paper_url", "year", "authors", "status", "needs_review",
        "S", "F", "F_mode", "P", "E", "E_relational_adaptation",
        *[f"{edge}_{item}" for edge in EDGES for item in ("presence", "validation")],
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for paper in papers:
            row = {key: paper.get(key, "") for key in headers}
            row.update(paper["sfpe"])
            for edge in EDGES:
                display = edge.replace("_to_", "→")
                row[f"{edge}_presence"] = paper["dependencies"][display]["presence"]
                row[f"{edge}_validation"] = paper["dependencies"][display]["validation"]
            writer.writerow(row)


def build(input_path, summary_path, public_json, public_csv, site_json, protocol_path, site_protocol):
    records = read_jsonl(input_path)
    papers = sorted((paper_record(record) for record in records), key=lambda p: (p["year"], p["title"]), reverse=True)
    if len({paper["paper_id"] for paper in papers}) != len(papers):
        raise ValueError("Duplicate paper_id in consensus data")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary["total_papers"] != len(papers):
        raise ValueError("Summary paper count does not match consensus data")
    payload = {
        "schema_version": "1.0",
        "source": "data/audit_results/all_consensus.jsonl",
        "summary": summary,
        "papers": papers,
    }
    write_json(public_json, payload)
    write_json(site_json, payload)
    write_csv(public_csv, papers)
    site_protocol.write_text(protocol_path.read_text(encoding="utf-8-sig"), encoding="utf-8")
    return {"papers": len(papers), "json": str(public_json), "csv": str(public_csv), "site": str(site_json)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/audit_results/all_consensus.jsonl")
    parser.add_argument("--summary", type=Path, default=ROOT / "data/audit_results/audit_summary.json")
    parser.add_argument("--json", type=Path, default=ROOT / "data/audit_results/audits.json")
    parser.add_argument("--csv", type=Path, default=ROOT / "data/audit_results/audits.csv")
    parser.add_argument("--site-json", type=Path, default=ROOT / "docs/data/audits.json")
    parser.add_argument("--protocol", type=Path, default=ROOT / "prompts/sfpe_protocol.md")
    parser.add_argument("--site-protocol", type=Path, default=ROOT / "docs/protocol.md")
    args = parser.parse_args(argv)
    result = build(args.input, args.summary, args.json, args.csv, args.site_json, args.protocol, args.site_protocol)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
